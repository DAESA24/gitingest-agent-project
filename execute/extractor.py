"""
GitIngest CLI wrapper functions.

This module wraps GitIngest CLI with subprocess calls, handling full and selective
repository extraction with comprehensive error handling and timeout protection.
"""

import re
import subprocess
from pathlib import Path
from exceptions import GitIngestError, StorageError
from storage import ensure_data_directory
from workflow import get_filters_for_type


def _check_encoding_errors(file_path: Path) -> list[str]:
    """
    Check extracted file for encoding errors from GitIngest.

    GitIngest may fail to read UTF-8 files on Windows, leaving error messages
    in the output file instead of the actual content. This function detects
    such errors.

    Args:
        file_path: Path to extracted file

    Returns:
        List of files with encoding errors (empty if none)

    Examples:
        >>> errors = _check_encoding_errors(Path("data/repo/digest.txt"))
        >>> if errors:
        ...     print(f"Encoding errors in: {', '.join(errors)}")
    """
    encoding_errors = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Pattern: "Error reading file with 'cp1252': 'charmap' codec can't decode"
        # or similar encoding error messages from GitIngest
        error_pattern = r"Error reading file with '[^']+': '(?:charmap|codec).*?(?:can't decode|character maps to)"
        
        # Find all file sections with encoding errors
        # Format: FILE: path\n====\nError reading file...
        file_sections = re.split(r'={80,}', content)
        
        for section in file_sections:
            if re.search(error_pattern, section, re.IGNORECASE):
                # Extract filename from "FILE: path" at start of section
                file_match = re.search(r'FILE:\s*(.+?)$', section, re.MULTILINE)
                if file_match:
                    encoding_errors.append(file_match.group(1).strip())
    
    except Exception:
        # If we can't read the file, don't fail - just return no errors
        pass
    
    return encoding_errors


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


def extract_full(url: str, repo_name: str) -> tuple[str, list[str]]:
    """
    Extract entire repository.

    Args:
        url: GitHub repository URL
        repo_name: Repository name for storage

    Returns:
        Tuple of (absolute_path, encoding_errors):
        - absolute_path: Path to digest.txt file
        - encoding_errors: List of files with encoding errors (empty if none)

    Raises:
        GitIngestError: If extraction fails
        StorageError: If directory creation fails
        TimeoutError: If extraction exceeds timeout

    Examples:
        >>> path, errors = extract_full("https://github.com/octocat/Hello-World", "Hello-World")
        >>> print(path)
        '/path/to/data/Hello-World/digest.txt'
        >>> if errors:
        ...     print(f"Encoding errors in: {', '.join(errors)}")
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

    # Check for encoding errors (Windows cp1252 issues)
    encoding_errors = _check_encoding_errors(output_file)

    # Return absolute path and any encoding errors
    return str(output_file.resolve()), encoding_errors


def extract_tree(url: str, repo_name: str) -> tuple[str, str, list[str]]:
    """
    Extract minimal tree structure.

    Args:
        url: GitHub repository URL
        repo_name: Repository name for storage

    Returns:
        Tuple of (absolute_path, tree_content, encoding_errors):
        - absolute_path: Path to tree.txt file
        - tree_content: Tree structure as string
        - encoding_errors: List of files with encoding errors (empty if none)

    Raises:
        GitIngestError: If extraction fails
        StorageError: If directory creation fails
        TimeoutError: If extraction exceeds timeout

    Examples:
        >>> path, tree, errors = extract_tree("https://github.com/user/repo", "repo")
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

    # Read tree content
    tree_content = output_file.read_text(encoding='utf-8')

    # Check for encoding errors (Windows cp1252 issues)
    encoding_errors = _check_encoding_errors(output_file)

    return str(output_file.resolve()), tree_content, encoding_errors


def extract_specific(url: str, repo_name: str, content_type: str) -> tuple[str, list[str]]:
    """
    Extract targeted content with filtering.

    Args:
        url: GitHub repository URL
        repo_name: Repository name for storage
        content_type: Type of content (docs, installation, code, auto)

    Returns:
        Tuple of (absolute_path, encoding_errors):
        - absolute_path: Path to [type]-content.txt file
        - encoding_errors: List of files with encoding errors (empty if none)

    Raises:
        GitIngestError: If extraction fails
        StorageError: If directory creation fails
        ValidationError: If content_type is invalid
        TimeoutError: If extraction exceeds timeout

    Examples:
        >>> path, errors = extract_specific("https://github.com/user/repo", "repo", "docs")
        >>> print(path)
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

    # Check for encoding errors (Windows cp1252 issues)
    encoding_errors = _check_encoding_errors(output_file)

    # Return absolute path and any encoding errors
    return str(output_file.resolve()), encoding_errors