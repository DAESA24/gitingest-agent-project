"""CLI framework and commands for GitIngest Agent."""

import click

from token_counter import count_tokens, should_extract_full
from workflow import format_token_count
from exceptions import GitIngestError, ValidationError


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


if __name__ == "__main__":
    gitingest_agent()