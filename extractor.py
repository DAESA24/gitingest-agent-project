"""
GitIngest CLI wrapper functions.

This module wraps GitIngest CLI with subprocess calls, handling full and selective
repository extraction with comprehensive error handling and timeout protection.
"""

import subprocess
from pathlib import Path
from exceptions import GitIngestError, StorageError
from storage import ensure_data_directory
from workflow import get_filters_for_type


def _run_gitingest(args: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    """
    Execute gitingest with standard error handling.

    Args:
        args: Command arguments (after 'gitingest')
        timeout: Maximum execution time in seconds (default 300)

    Returns:
        CompletedProcess object

    Raises:
        GitIngestError: If command fails
        TimeoutError: If execution exceeds timeout

    Examples:
        >>> _run_gitingest(['https://github.com/user/repo', '-o', 'output.txt'])
        CompletedProcess(...)
    """
    cmd = ['gitingest'] + args

    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"GitIngest timed out after {timeout}s")
    except subprocess.CalledProcessError as e:
        # Parse GitIngest error messages for user-friendly output
        stderr = e.stderr.lower() if e.stderr else ""

        if "not found" in stderr or "404" in stderr:
            # Extract URL from args if present
            url = args[0] if args else "repository"
            raise GitIngestError(f"Repository not found: {url}")
        elif "bad credentials" in stderr or "authentication" in stderr or "permission denied" in stderr:
            raise GitIngestError("Authentication failed (private repository?)")
        elif "could not resolve host" in stderr:
            raise GitIngestError("Network error: Unable to reach GitHub")
        else:
            raise GitIngestError(f"GitIngest error: {e.stderr}")


def extract_full(url: str, repo_name: str) -> str:
    """
    Extract entire repository.

    Args:
        url: GitHub repository URL
        repo_name: Repository name for storage

    Returns:
        Absolute path to digest.txt file

    Raises:
        GitIngestError: If extraction fails
        StorageError: If directory creation fails
        TimeoutError: If extraction exceeds timeout

    Examples:
        >>> extract_full("https://github.com/octocat/Hello-World", "Hello-World")
        '/path/to/data/Hello-World/digest.txt'
    """
    # Ensure directory exists (uses storage module)
    try:
        data_dir = ensure_data_directory(repo_name)
    except Exception as e:
        raise StorageError(f"Failed to create directory: {e}")

    output_file = data_dir / "digest.txt"

    # Build GitIngest command
    args = [url, '-o', str(output_file)]

    # Execute extraction
    _run_gitingest(args, timeout=300)

    # Return absolute path
    return str(output_file.resolve())


def extract_tree(url: str, repo_name: str) -> tuple[str, str]:
    """
    Extract minimal tree structure.

    Args:
        url: GitHub repository URL
        repo_name: Repository name for storage

    Returns:
        Tuple of (absolute_path, tree_content)

    Raises:
        GitIngestError: If extraction fails
        StorageError: If directory creation fails
        TimeoutError: If extraction exceeds timeout

    Examples:
        >>> path, tree = extract_tree("https://github.com/user/repo", "repo")
        >>> print(tree)
        README.md
        src/
          main.py
          utils.py
    """
    # Ensure directory exists
    try:
        data_dir = ensure_data_directory(repo_name)
    except Exception as e:
        raise StorageError(f"Failed to create directory: {e}")

    output_file = data_dir / "tree.txt"

    # Strategy: Extract with severe filtering to get structure only
    # -i README.md: Include at least one file (GitIngest requires content)
    # -s 1024: Maximum 1KB per file (forces truncation, shows structure)
    args = [
        url,
        '-i', 'README.md',
        '-s', '1024',
        '-o', str(output_file)
    ]

    # Tree extraction is faster than full, use shorter timeout
    _run_gitingest(args, timeout=120)

    # Read and return tree content
    tree_content = output_file.read_text(encoding='utf-8')

    return str(output_file.resolve()), tree_content


def extract_specific(url: str, repo_name: str, content_type: str) -> str:
    """
    Extract targeted content with filtering.

    Args:
        url: GitHub repository URL
        repo_name: Repository name for storage
        content_type: Type of content (docs, installation, code, auto)

    Returns:
        Absolute path to [type]-content.txt file

    Raises:
        GitIngestError: If extraction fails
        StorageError: If directory creation fails
        ValidationError: If content_type is invalid
        TimeoutError: If extraction exceeds timeout

    Examples:
        >>> extract_specific("https://github.com/user/repo", "repo", "docs")
        '/path/to/data/repo/docs-content.txt'
    """
    # Get filter patterns for content type (raises ValidationError if invalid)
    filters = get_filters_for_type(content_type)

    # Ensure directory exists
    try:
        data_dir = ensure_data_directory(repo_name)
    except Exception as e:
        raise StorageError(f"Failed to create directory: {e}")

    output_file = data_dir / f"{content_type}-content.txt"

    # Build GitIngest command with include/exclude patterns
    args = [url]

    # Add include patterns (-i flag for each pattern)
    for pattern in filters['include']:
        args.extend(['-i', pattern])

    # Add exclude patterns (-e flag for each pattern)
    for pattern in filters['exclude']:
        args.extend(['-e', pattern])

    # Add output file
    args.extend(['-o', str(output_file)])

    # Execute extraction (use full timeout since filtering can take time)
    _run_gitingest(args, timeout=300)

    # Return absolute path
    return str(output_file.resolve())