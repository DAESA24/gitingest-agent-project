"""CLI framework and commands for GitIngest Agent."""

import click

from token_counter import count_tokens, should_extract_full, count_tokens_from_file
from workflow import format_token_count
from storage import parse_repo_name
import extractor
from exceptions import GitIngestError, ValidationError, StorageError


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
        click.echo(f"❌ Invalid URL: {e}", err=True)
        raise click.Abort()
    except GitIngestError as e:
        click.echo(f"❌ Error: {e}", err=True)
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
    try:
        # Parse repository name
        repo_name = parse_repo_name(url)

        click.echo("Extracting full repository...")

        # Extract
        output_path = extractor.extract_full(url, repo_name)

        # Count tokens in result
        token_count = count_tokens_from_file(output_path)
        formatted = format_token_count(token_count)

        # Display confirmation
        click.echo(f"✓ Saved to: {output_path}")
        click.echo(f"Token count: {formatted}")

    except ValidationError as e:
        click.echo(f"❌ Invalid URL: {e}", err=True)
        raise click.Abort()
    except StorageError as e:
        click.echo(f"❌ Storage error: {e}", err=True)
        raise click.Abort()
    except GitIngestError as e:
        click.echo(f"❌ Extraction failed: {e}", err=True)
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
    try:
        repo_name = parse_repo_name(url)

        click.echo("Extracting tree structure...")

        # Extract tree (returns path and content)
        output_path, tree_content = extractor.extract_tree(url, repo_name)

        # Display tree to user
        click.echo("\nRepository structure:")
        click.echo(tree_content)

        click.echo(f"\n✓ Saved to: {output_path}")

    except ValidationError as e:
        click.echo(f"❌ Invalid URL: {e}", err=True)
        raise click.Abort()
    except StorageError as e:
        click.echo(f"❌ Storage error: {e}", err=True)
        raise click.Abort()
    except GitIngestError as e:
        click.echo(f"❌ Extraction failed: {e}", err=True)
        raise click.Abort()


@gitingest_agent.command()
@click.argument('url')
@click.option('--type', 'content_type', required=True,
              type=click.Choice(['docs', 'installation', 'code', 'auto']),
              help='Type of content to extract')
def extract_specific(url: str, content_type: str):
    """
    Extract specific content from repository using filters.

    Uses content type filters to extract targeted sections:
    - docs: Documentation files (*.md, docs/**, README)
    - installation: Installation files (README, setup.py, package.json)
    - code: Source code (src/**/*.py, lib/**/*.py)
    - auto: Automatic (README + docs)

    Args:
        url: GitHub repository URL
        content_type: Type of content to extract

    Example:
        gitingest-agent extract-specific https://github.com/fastapi/fastapi --type docs
    """
    try:
        repo_name = parse_repo_name(url)

        click.echo(f"Extracting {content_type} content...")

        # Extract specific content
        output_path = extractor.extract_specific(url, repo_name, content_type)

        # Count tokens in result
        token_count = count_tokens_from_file(output_path)
        formatted = format_token_count(token_count)

        # Display confirmation
        click.echo(f"✓ Saved to: {output_path}")
        click.echo(f"Token count: {formatted}")

    except ValidationError as e:
        click.echo(f"❌ Invalid input: {e}", err=True)
        raise click.Abort()
    except StorageError as e:
        click.echo(f"❌ Storage error: {e}", err=True)
        raise click.Abort()
    except GitIngestError as e:
        click.echo(f"❌ Extraction failed: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    gitingest_agent()