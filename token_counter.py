"""
Token counting and routing logic.

This module wraps GitIngest CLI to estimate repository token counts and makes
routing decisions for full vs selective extraction based on the 200k token threshold.
"""

import re
import subprocess
from pathlib import Path
from exceptions import GitIngestError
from workflow import validate_github_url


def count_tokens(url: str) -> int:
    """
    Count tokens in repository using GitIngest.

    Args:
        url: GitHub repository URL

    Returns:
        Estimated token count

    Raises:
        ValidationError: If URL format is invalid
        GitIngestError: If GitIngest execution fails
        TimeoutError: If counting takes too long (>120s)

    Examples:
        >>> count_tokens("https://github.com/octocat/Hello-World")
        8500
    """
    # Validate URL format before attempting GitIngest call
    validate_github_url(url)

    try:
        result = subprocess.run(
            ['gitingest', url, '-o', '-'],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutes
            check=True
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError(
            f"Token counting timed out after 120 seconds. "
            f"Repository may be very large. Retry with 'extract-tree' command first, "
            f"then use 'extract-specific --type installation' for minimal content."
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.lower() if e.stderr else ""

        # Provide specific error messages based on GitIngest output
        if "could not resolve host" in stderr:
            raise GitIngestError("Network error: Unable to reach GitHub")
        elif "repository not found" in stderr or "404" in stderr:
            raise GitIngestError(f"Repository not found: {url}")
        elif "authentication" in stderr or "permission denied" in stderr:
            raise GitIngestError(f"Authentication failed: {url} (private repository?)")
        else:
            raise GitIngestError(f"GitIngest failed: {e.stderr}")

    # Try to parse "Estimated tokens: NNNN" from GitIngest output
    match = re.search(r'Estimated tokens:\s*(\d+)', result.stdout)
    if match:
        return int(match.group(1))

    # Fallback: Character-based estimation (4 chars ≈ 1 token)
    return len(result.stdout) // 4


def count_tokens_from_file(file_path: str) -> int:
    """
    Count tokens in already-extracted file.

    Used for size re-check after selective extraction.

    Args:
        file_path: Path to extracted content file

    Returns:
        Estimated token count

    Raises:
        FileNotFoundError: If file doesn't exist

    Examples:
        >>> count_tokens_from_file("data/fastapi/docs-content.txt")
        89450
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding='utf-8')

    # Character-based estimation: 4 chars ≈ 1 token
    return len(content) // 4


def should_extract_full(token_count: int, threshold: int = 200_000) -> bool:
    """
    Determine if full extraction is appropriate.

    Args:
        token_count: Repository token count
        threshold: Decision threshold (default 200k)

    Returns:
        True if should extract full, False if selective

    Examples:
        >>> should_extract_full(145000)
        True
        >>> should_extract_full(487523)
        False
        >>> should_extract_full(200000)
        False
    """
    return token_count < threshold