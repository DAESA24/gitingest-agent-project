"""CLI framework and commands for GitIngest Agent."""

import sys
import io
import os
from pathlib import Path
import click

from token_counter import count_tokens, should_extract_full, count_tokens_from_file
from workflow import format_token_count
from storage import parse_repo_name
import extractor
from exceptions import GitIngestError, ValidationError, StorageError


def ensure_execute_directory():
    """
    Ensure we're running from the execute/ directory.

    Auto-detects project structure and changes to execute/ if needed.
    This allows commands to work from both project root and execute/ directory.
    """
    cwd = Path.cwd()

    # Check if we're in execute/ already
    if cwd.name == "execute":
        return

    # Check if execute/ exists as subdirectory (we're in project root)
    execute_dir = cwd / "execute"
    if execute_dir.exists() and execute_dir.is_dir():
        os.chdir(execute_dir)
        return

    # Check if we're in a subdirectory of the project and need to navigate to execute/
    # Look for pyproject.toml as marker
    current = cwd
    for _ in range(3):  # Search up to 3 levels
        if (current / "pyproject.toml").exists():
            # Found project root, check for execute/
            execute_dir = current / "execute"
            if execute_dir.exists():
                os.chdir(execute_dir)
                return
        current = current.parent


@click.group()
def gitingest_agent():
    """
    GitIngest Agent - Automated GitHub repository analysis.

    Analyzes GitHub repositories using GitIngest with intelligent
    token-aware routing for Claude Code workflows.
    """
    pass


@gitingest_agent.command()
@click.argument('url')
def check_size(url: str):
    """
    Check token count and determine extraction strategy.

    Args:
        url: GitHub repository URL

    Example:
        gitingest-agent check-size https://github.com/user/repo
    """
    ensure_execute_directory()
    try:
        click.echo("Checking repository size...")

        # Count tokens
        token_count = count_tokens(url)

        # Format and display
        formatted = format_token_count(token_count)
        click.echo(f"Token count: {formatted}")

        # Determine route
        route = "full extraction" if should_extract_full(token_count) else "selective extraction"
        click.echo(f"Route: {route}")

    except ValidationError as e:
        click.echo(f"[ERROR] Invalid URL: {e}", err=True)
        raise click.Abort()
    except GitIngestError as e:
        click.echo(f"[ERROR] {e}", err=True)
        raise click.Abort()


@gitingest_agent.command()
@click.argument('url')
def extract_full(url: str):
    """
    Extract entire repository to data/ directory.

    Used for repositories under 200k tokens. Extracts complete
    repository content including all files and code.

    Args:
        url: GitHub repository URL

    Example:
        gitingest-agent extract-full https://github.com/octocat/Hello-World
    """
    ensure_execute_directory()
    try:
        # Parse repository name
        repo_name = parse_repo_name(url)

        click.echo("Extracting full repository...")

        # Extract (returns path and encoding errors)
        output_path, encoding_errors = extractor.extract_full(url, repo_name)

        # Count tokens in result
        token_count = count_tokens_from_file(output_path)
        formatted = format_token_count(token_count)

        # Display confirmation
        click.echo(f"[OK] Saved to: {output_path}")
        click.echo(f"Token count: {formatted}")

        # Display encoding warnings if present
        if encoding_errors:
            click.echo(f"\n[WARNING] Encoding errors detected in {len(encoding_errors)} file(s):", err=True)
            for file in encoding_errors[:5]:  # Show first 5
                click.echo(f"  - {file}", err=True)
            if len(encoding_errors) > 5:
                click.echo(f"  ... and {len(encoding_errors) - 5} more", err=True)
            click.echo("\nThis is a known GitIngest issue on Windows with UTF-8 files.", err=True)
            click.echo("See README.md 'Known Issues' for workarounds.", err=True)

    except ValidationError as e:
        click.echo(f"[ERROR] Invalid URL: {e}", err=True)
        raise click.Abort()
    except StorageError as e:
        click.echo(f"[ERROR] Storage error: {e}", err=True)
        raise click.Abort()
    except GitIngestError as e:
        click.echo(f"[ERROR] Extraction failed: {e}", err=True)
        raise click.Abort()


@gitingest_agent.command()
@click.argument('url')
def extract_tree(url: str):
    """
    Extract repository tree structure.

    Displays file/directory structure without full content.
    Used for large repositories (>= 200k tokens) to understand
    structure before selective extraction.

    Args:
        url: GitHub repository URL

    Example:
        gitingest-agent extract-tree https://github.com/fastapi/fastapi
    """
    ensure_execute_directory()
    try:
        repo_name = parse_repo_name(url)

        click.echo("Extracting tree structure...")

        # Extract tree (returns path, content, and encoding errors)
        output_path, tree_content, encoding_errors = extractor.extract_tree(url, repo_name)

        # Display success and path (tree content saved to file due to encoding issues on Windows)
        click.echo(f"\n[OK] Tree structure extracted")
        click.echo(f"[OK] Saved to: {output_path}")
        click.echo(f"\nView the tree structure in the file above.")

        # Display encoding warnings if present
        if encoding_errors:
            click.echo(f"\n[WARNING] Encoding errors detected in {len(encoding_errors)} file(s).", err=True)
            click.echo("This is a known GitIngest issue on Windows with UTF-8 files.", err=True)
            click.echo("See README.md 'Known Issues' for workarounds.", err=True)

    except ValidationError as e:
        click.echo(f"[ERROR] Invalid URL: {e}", err=True)
        raise click.Abort()
    except StorageError as e:
        click.echo(f"[ERROR] Storage error: {e}", err=True)
        raise click.Abort()
    except GitIngestError as e:
        click.echo(f"[ERROR] Extraction failed: {e}", err=True)
        raise click.Abort()


@gitingest_agent.command()
@click.argument('url')
@click.option('--type', 'content_type', required=True,
              type=click.Choice(['docs', 'installation', 'code', 'auto']),
              help='Type of content to extract')
def extract_specific(url: str, content_type: str):
    """
    Extract specific content from repository using filters with overflow prevention.

    Uses content type filters to extract targeted sections:
    - docs: Documentation files (*.md, docs/**, README)
    - installation: Installation files (README, setup.py, package.json)
    - code: Source code (src/**/*.py, lib/**/*.py)
    - auto: Automatic (README + docs)

    Includes token overflow prevention: if extracted content exceeds 200k tokens,
    prompts user to narrow selection or proceed with partial content.

    Args:
        url: GitHub repository URL
        content_type: Type of content to extract

    Example:
        gitingest-agent extract-specific https://github.com/fastapi/fastapi --type docs
    """
    ensure_execute_directory()
    try:
        repo_name = parse_repo_name(url)

        # Initial extraction
        click.echo(f"Extracting {content_type} content...")
        output_path, encoding_errors = extractor.extract_specific(url, repo_name, content_type)

        # Token re-check loop for overflow prevention
        while True:
            # Count tokens in extracted content
            token_count = count_tokens_from_file(output_path)
            formatted = format_token_count(token_count)

            # Display confirmation
            click.echo(f"[OK] Saved to: {output_path}")
            click.echo(f"Token count: {formatted}")

            # Display encoding warnings if present
            if encoding_errors:
                click.echo(f"\n[WARNING] Encoding errors detected in {len(encoding_errors)} file(s):", err=True)
                for file in encoding_errors[:3]:  # Show first 3
                    click.echo(f"  - {file}", err=True)
                if len(encoding_errors) > 3:
                    click.echo(f"  ... and {len(encoding_errors) - 3} more", err=True)
                click.echo("\nThis is a known GitIngest issue on Windows with UTF-8 files.", err=True)
                click.echo("See README.md 'Known Issues' for workarounds.", err=True)

            # Check for overflow (threshold: 200k tokens)
            if token_count < 200_000:
                # Success - content is under threshold
                break

            # Overflow detected - warn user and prompt for action
            overflow = token_count - 200_000
            click.echo(f"\n[WARNING] Content exceeds token limit!")
            click.echo(f"   Current: {formatted}")
            click.echo(f"   Target: 200,000 tokens")
            click.echo(f"   Overflow: {overflow:,} tokens")
            click.echo("\nOptions:")
            click.echo("  1) Narrow selection further")
            click.echo("  2) Proceed with partial content")

            choice = click.prompt("Select option", type=int, default=1)

            if choice == 2:
                # User chooses to proceed despite overflow
                click.echo("\n[WARNING] Proceeding with content exceeding token limit")
                click.echo("   Analysis may be truncated")
                break
            elif choice == 1:
                # Re-extract with narrower selection
                click.echo("\nWhat would you like to extract instead?")
                click.echo("Suggestion: Try a more specific filter:")
                click.echo("  - installation: Just setup files")
                click.echo("  - auto: README + minimal docs")

                new_type = click.prompt(
                    "Content type",
                    type=click.Choice(['docs', 'installation', 'code', 'auto']),
                    default='installation'
                )

                # Re-extract with new content type
                click.echo(f"\nExtracting {new_type} content...")
                output_path, encoding_errors = extractor.extract_specific(url, repo_name, new_type)
                content_type = new_type  # Update for next iteration
            else:
                # Invalid choice - continue loop to re-prompt
                click.echo("Invalid choice. Please select 1 or 2.")

    except ValidationError as e:
        click.echo(f"[ERROR] Invalid input: {e}", err=True)
        raise click.Abort()
    except StorageError as e:
        click.echo(f"[ERROR] Storage error: {e}", err=True)
        raise click.Abort()
    except GitIngestError as e:
        click.echo(f"[ERROR] Extraction failed: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    gitingest_agent()