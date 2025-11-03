"""
File system operations and path management.

This module provides utilities for managing file system operations,
including path resolution, directory creation, and file naming conventions.
"""

import re
from pathlib import Path
from exceptions import ValidationError, StorageError


def parse_repo_name(url: str) -> str:
    """
    Extract repository name from GitHub URL.

    Args:
        url: GitHub URL (e.g., https://github.com/owner/repo or https://github.com/owner/repo.git)

    Returns:
        Repository name (e.g., "repo" from "https://github.com/owner/repo")

    Raises:
        ValidationError: If URL format is invalid or repo name is empty

    Examples:
        >>> parse_repo_name("https://github.com/tiangolo/fastapi")
        'fastapi'
        >>> parse_repo_name("https://github.com/tiangolo/fastapi.git")
        'fastapi'
        >>> parse_repo_name("https://github.com/tiangolo/fastapi/")
        'fastapi'
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")

    # Extract last path component
    parts = url.rstrip('/').split('/')
    if len(parts) < 2:
        raise ValidationError(f"Invalid GitHub URL format: {url}")

    repo_name = parts[-1]

    # Remove .git suffix if present
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]

    # Sanitize: keep only alphanumeric, hyphens, underscores
    safe_name = re.sub(r'[^\w-]', '', repo_name)

    if not safe_name:
        raise ValidationError(f"Invalid repository name extracted from URL: {url}")

    return safe_name


def ensure_data_directory(repo_name: str) -> Path:
    """
    Ensure data directory exists for repository.

    Creates data/ directory at project root (parent of execute/),
    not within execute/ directory. This keeps extracted repository
    content separate from code execution artifacts.

    Args:
        repo_name: Repository name (sanitized)

    Returns:
        Absolute Path to data/[repo-name]/

    Raises:
        StorageError: If directory creation fails

    Examples:
        >>> data_dir = ensure_data_directory("fastapi")
        >>> data_dir.exists()
        True
        >>> data_dir.name
        'fastapi'
    """
    try:
        # Navigate to project root (parent of execute/)
        project_root = Path(__file__).parent.parent
        data_dir = project_root / "data" / repo_name
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir.resolve()
    except PermissionError:
        raise StorageError(f"Permission denied creating directory: {data_dir}")
    except OSError as e:
        raise StorageError(f"Failed to create directory {data_dir}: {e}")


def ensure_analyze_directory(analysis_type: str) -> Path:
    """
    Ensure analyze directory exists for analysis type.

    Creates analyze/ directory at project root (parent of execute/),
    not within execute/ directory. This keeps user-facing analysis
    outputs separate from code execution artifacts.

    Args:
        analysis_type: Type of analysis (installation, workflow, architecture, custom)

    Returns:
        Absolute Path to analyze/[type]/

    Raises:
        StorageError: If directory creation fails

    Examples:
        >>> analyze_dir = ensure_analyze_directory("installation")
        >>> analyze_dir.exists()
        True
        >>> analyze_dir.name
        'installation'
    """
    try:
        # Navigate to project root (parent of execute/)
        project_root = Path(__file__).parent.parent
        analyze_dir = project_root / "analyze" / analysis_type
        analyze_dir.mkdir(parents=True, exist_ok=True)
        return analyze_dir.resolve()
    except PermissionError:
        raise StorageError(f"Permission denied creating directory: {analyze_dir}")
    except OSError as e:
        raise StorageError(f"Failed to create directory {analyze_dir}: {e}")


def save_analysis(content: str, repo_name: str, analysis_type: str) -> str:
    """
    Save analysis to analyze/ folder with metadata header.

    Creates a markdown file containing the analysis with metadata including
    repository name, analysis date, and analysis type.

    Args:
        content: Analysis content (markdown format)
        repo_name: Repository name (used as filename)
        analysis_type: Type of analysis (installation, workflow, architecture, custom)

    Returns:
        Absolute path to saved analysis file

    Raises:
        StorageError: If directory creation or file write fails

    Examples:
        >>> save_analysis("# Analysis\\n...", "fastapi", "installation")
        '/path/to/analyze/installation/fastapi.md'
    """
    from datetime import datetime

    # Ensure analyze directory exists
    try:
        analyze_dir = ensure_analyze_directory(analysis_type)
    except Exception as e:
        raise StorageError(f"Failed to create analyze directory: {e}")

    output_file = analyze_dir / f"{repo_name}.md"

    # Generate metadata header
    current_date = datetime.now().strftime("%Y-%m-%d")
    metadata = f"""# {repo_name} - {analysis_type.title()} Analysis

**Repository:** https://github.com/{repo_name}
**Analyzed:** {current_date}
**Analysis Type:** {analysis_type}

---

"""

    # Combine metadata + content
    full_content = metadata + content

    # Write to file
    try:
        output_file.write_text(full_content, encoding='utf-8')
    except Exception as e:
        raise StorageError(f"Failed to write analysis file: {e}")

    return str(output_file.resolve())