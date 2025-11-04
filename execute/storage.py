"""
File system operations and path management.

This module provides utilities for managing file system operations,
including path resolution, directory creation, and file naming conventions.

Phase 1.5 Update: Now uses StorageManager for dynamic path resolution.
"""

import re
from pathlib import Path
from typing import Optional
from exceptions import ValidationError, StorageError
from storage_manager import StorageManager


# Module-level storage manager instance (can be overridden)
_storage_manager: Optional[StorageManager] = None


def get_storage_manager(output_dir: Optional[Path] = None) -> StorageManager:
    """
    Get or create the global StorageManager instance.

    Args:
        output_dir: Optional custom output directory

    Returns:
        StorageManager instance
    """
    global _storage_manager
    if _storage_manager is None or output_dir is not None:
        _storage_manager = StorageManager(output_dir=output_dir)
    return _storage_manager


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

    # Sanitize: keep only alphanumeric, hyphens, underscores, dots
    safe_name = re.sub(r'[^\w.-]', '', repo_name)

    if not safe_name:
        raise ValidationError(f"Invalid repository name extracted from URL: {url}")

    return safe_name


def ensure_data_directory(repo_name: str, output_dir: Optional[Path] = None) -> Path:
    """
    Ensure data directory exists for repository.

    Phase 1.5 Update: Uses StorageManager for dynamic path resolution.
    - Phase 1.0 (gitingest-agent-project): Creates data/[repo-name]/
    - Phase 1.5 (other directories): Uses context/related-repos/

    Args:
        repo_name: Repository name (sanitized)
        output_dir: Optional custom output directory

    Returns:
        Absolute Path to data directory

    Raises:
        StorageError: If directory creation fails

    Examples:
        >>> data_dir = ensure_data_directory("fastapi")
        >>> data_dir.exists()
        True
    """
    try:
        # Use CWD as base location (for test compatibility and Phase 1.5)
        if output_dir is None:
            # Check if we're in gitingest-agent-project
            cwd = Path.cwd()
            # Case 1: CWD is project root (has execute/cli.py)
            # Case 2: CWD is execute/ directory itself (has cli.py directly)
            is_project_root = (cwd / "execute" / "cli.py").exists() and (cwd / "execute" / "main.py").exists()
            is_execute_dir = (cwd / "cli.py").exists() and (cwd / "main.py").exists() and cwd.name == "execute"

            if is_project_root or is_execute_dir:
                # Phase 1.0: data/[repo]/ (resolve to project root if in execute/)
                base = cwd if is_project_root else cwd.parent
                data_dir = base / "data" / repo_name
            else:
                # Phase 1.5: context/related-repos/[repo]/ (universal convention)
                data_dir = cwd / "context" / "related-repos" / repo_name
        else:
            # Custom output_dir provided - use StorageManager
            manager = StorageManager(output_dir=output_dir)
            dummy_url = f"https://github.com/owner/{repo_name}"
            extraction_path = manager.get_extraction_path(dummy_url, "digest")
            data_dir = extraction_path.parent

        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir.resolve()
    except PermissionError:
        raise StorageError(f"Permission denied creating directory: {data_dir}")
    except OSError as e:
        raise StorageError(f"Failed to create directory {data_dir}: {e}")


def ensure_analyze_directory(analysis_type: str, output_dir: Optional[Path] = None) -> Path:
    """
    Ensure analyze directory exists for analysis type.

    Phase 1.5 Update: Uses StorageManager for dynamic path resolution.
    - Phase 1.0 (gitingest-agent-project): Creates analyze/[type]/
    - Phase 1.5 (other directories): Uses context/related-repos/

    Args:
        analysis_type: Type of analysis (installation, workflow, architecture, custom)
        output_dir: Optional custom output directory

    Returns:
        Absolute Path to analyze directory

    Raises:
        StorageError: If directory creation fails

    Examples:
        >>> analyze_dir = ensure_analyze_directory("installation")
        >>> analyze_dir.exists()
        True
    """
    try:
        # Use CWD as base location (for test compatibility and Phase 1.5)
        if output_dir is None:
            # Check if we're in gitingest-agent-project (has execute/cli.py marker)
            cwd = Path.cwd()
            if (cwd / "execute" / "cli.py").exists() and (cwd / "execute" / "main.py").exists():
                # Phase 1.0: analyze/[type]/
                analyze_dir = cwd / "analyze" / analysis_type
            else:
                # Not in project, use simple analyze/ structure for backward compat with tests
                analyze_dir = cwd / "analyze" / analysis_type
        else:
            # Custom output_dir provided - use StorageManager
            manager = StorageManager(output_dir=output_dir)
            dummy_url = "https://github.com/owner/repo"
            analysis_path = manager.get_analysis_path(dummy_url, analysis_type)
            analyze_dir = analysis_path.parent

        analyze_dir.mkdir(parents=True, exist_ok=True)
        return analyze_dir.resolve()
    except PermissionError:
        raise StorageError(f"Permission denied creating directory: {analyze_dir}")
    except OSError as e:
        raise StorageError(f"Failed to create directory {analyze_dir}: {e}")


def save_analysis(
    content: str,
    repo_identifier: str,
    analysis_type: str,
    output_dir: Optional[Path] = None
) -> str:
    """
    Save analysis to appropriate folder with metadata header.

    Phase 1.5 Update: Uses StorageManager for dynamic path resolution and naming.
    - Phase 1.0: analyze/{type}/{repo}.md
    - Phase 1.5: context/related-repos/{owner}-{repo}-{type}.md

    Creates a markdown file containing the analysis with metadata including
    repository name, analysis date, and analysis type.

    Args:
        content: Analysis content (markdown format)
        repo_identifier: Either a repo name (for backward compat) or full GitHub URL
        analysis_type: Type of analysis (installation, workflow, architecture, custom)
        output_dir: Optional custom output directory

    Returns:
        Absolute path to saved analysis file

    Raises:
        StorageError: If directory creation or file write fails

    Examples:
        >>> save_analysis("# Analysis\\n...", "https://github.com/facebook/react", "installation")
        '/path/to/analyze/installation/react.md'
        >>> save_analysis("# Analysis\\n...", "react", "installation")  # Legacy support
        '/path/to/analyze/installation/react.md'
    """
    from datetime import datetime

    # Detect if repo_identifier is a full URL or just a repo name
    is_url = repo_identifier.startswith('http://') or repo_identifier.startswith('https://')

    # Get analysis directory and construct file path
    try:
        if output_dir is None and not is_url:
            # Phase 1.0 backward compatibility: Use ensure_analyze_directory for repo names
            # This maintains compatibility with tests that mock ensure_analyze_directory
            analyze_dir = ensure_analyze_directory(analysis_type, output_dir=None)
            output_file = analyze_dir / f"{repo_identifier}.md"
            repo_name = repo_identifier
            repo_display = f"https://github.com/{repo_identifier}"
        else:
            # Phase 1.5 or custom output_dir: Use StorageManager
            manager = get_storage_manager(output_dir)
            if is_url:
                output_file = manager.get_analysis_path(repo_identifier, analysis_type)
                repo_name = parse_repo_name(repo_identifier)
                repo_display = repo_identifier
            else:
                # Repo name with custom output_dir
                dummy_url = f"https://github.com/owner/{repo_identifier}"
                output_file = manager.get_analysis_path(dummy_url, analysis_type)
                repo_name = repo_identifier
                repo_display = f"https://github.com/{repo_identifier}"
    except Exception as e:
        raise StorageError(f"Failed to create analyze directory: {e}")

    # Generate metadata header
    current_date = datetime.now().strftime("%Y-%m-%d")
    metadata = f"""# {repo_name} - {analysis_type.title()} Analysis

**Repository:** {repo_display}
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
