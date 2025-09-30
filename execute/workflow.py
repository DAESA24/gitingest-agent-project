"""
Workflow routing and content type mapping.

This module provides utility functions for URL validation, content type filtering,
and user-friendly formatting. These utilities maintain consistent validation and
display logic across the application.
"""

import re
from exceptions import ValidationError


# Filter patterns for content type mapping
FILTER_PATTERNS = {
    'docs': {
        'include': ['docs/**/*', '*.md', 'README*', '*.rst'],
        'exclude': ['docs/examples/*', 'docs/archive/*']
    },
    'installation': {
        'include': [
            'README*', 'INSTALL*', 'setup.py', 'pyproject.toml',
            'package.json', 'docs/installation*', 'docs/getting-started*'
        ],
        'exclude': []
    },
    'code': {
        'include': ['src/**/*.py', 'lib/**/*.py'],
        'exclude': ['tests/*', '*_test.py', 'test_*.py', 'examples/*']
    },
    'auto': {
        'include': ['README*', 'docs/**/*.md'],
        'exclude': ['docs/examples/*', 'docs/archive/*']
    }
}


def validate_github_url(url: str) -> tuple[str, str]:
    """
    Validate GitHub URL and extract owner/repo.

    Args:
        url: GitHub repository URL

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        ValidationError: If URL format is invalid

    Examples:
        >>> validate_github_url("https://github.com/tiangolo/fastapi")
        ('tiangolo', 'fastapi')
        >>> validate_github_url("https://github.com/tiangolo/fastapi.git")
        ('tiangolo', 'fastapi')
        >>> validate_github_url("https://github.com/tiangolo/fastapi/")
        ('tiangolo', 'fastapi')
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")

    # Remove trailing slashes and .git suffix
    clean_url = url.rstrip('/')
    if clean_url.endswith('.git'):
        clean_url = clean_url[:-4]

    # Strict regex pattern: https?://github.com/owner/repo
    # Only allows alphanumeric, hyphens, underscores in owner/repo names
    # $ ensures we match the entire URL (no extra path components)
    pattern = r'https?://github\.com/([\w-]+)/([\w-]+)$'

    match = re.match(pattern, clean_url)
    if not match:
        raise ValidationError(f"Invalid GitHub URL format: {url}")

    owner = match.group(1)
    repo = match.group(2)

    return owner, repo


def format_token_count(count: int) -> str:
    """
    Format token count for user display.

    Args:
        count: Token count

    Returns:
        Formatted string (e.g., "145,000 tokens")

    Examples:
        >>> format_token_count(145000)
        '145,000 tokens'
        >>> format_token_count(1234567)
        '1,234,567 tokens'
        >>> format_token_count(999)
        '999 tokens'
    """
    return f"{count:,} tokens"


def get_filters_for_type(content_type: str) -> dict[str, list[str]]:
    """
    Map content type to GitIngest filter patterns.

    Args:
        content_type: Type of content to extract (docs, installation, code, auto)

    Returns:
        Dict with 'include' and 'exclude' pattern lists

    Raises:
        ValidationError: If content_type is invalid

    Examples:
        >>> filters = get_filters_for_type('docs')
        >>> 'include' in filters
        True
        >>> 'exclude' in filters
        True
        >>> filters = get_filters_for_type('installation')
        >>> 'README*' in filters['include']
        True
    """
    if content_type not in FILTER_PATTERNS:
        valid_types = ', '.join(FILTER_PATTERNS.keys())
        raise ValidationError(
            f"Invalid content type: {content_type}. "
            f"Valid types: {valid_types}"
        )

    return FILTER_PATTERNS[content_type]