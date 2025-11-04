"""
Storage location detection and path management.

This module provides the StorageManager class which abstracts storage location
detection, supporting both Phase 1.0 (gitingest-agent-project) and Phase 1.5
(universal context/related-repos/) behaviors.
"""

from pathlib import Path
from typing import Optional, Tuple


class StorageManager:
    """
    Manages storage locations for repository data and analysis outputs.

    Automatically detects the appropriate save location based on the current
    working directory and project context. Supports two modes:

    - Phase 1.0: When in gitingest-agent-project, uses data/ and analyze/ folders
    - Phase 1.5: When in any other directory, uses context/related-repos/ folder

    Attributes:
        output_dir: The base directory for all storage operations
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize StorageManager with automatic or manual location detection.

        Args:
            output_dir: Optional custom output directory. If None, auto-detects
                       based on current working directory.
        """
        self.output_dir = output_dir or self._detect_output_location()

    def _detect_output_location(self) -> Path:
        """
        Detect appropriate save location based on current directory.

        Uses marker files (execute/cli.py and execute/main.py) to determine
        if we're in the gitingest-agent-project. This is more robust than
        checking directory names.

        Returns:
            Path to use as base output directory:
            - Current directory if in gitingest-agent-project
            - context/related-repos/ subdirectory otherwise
        """
        cwd = Path.cwd()

        # Check for marker files (more robust than directory name)
        # We're in gitingest-agent-project if execute/cli.py and execute/main.py exist
        if (cwd / "execute" / "cli.py").exists() and (cwd / "execute" / "main.py").exists():
            # Phase 1.0 behavior: Use current directory as base
            return cwd

        # Universal default: context/related-repos/ for ALL other directories
        context_dir = cwd / "context" / "related-repos"

        # Auto-create if doesn't exist
        if not context_dir.exists():
            print(f"Creating context/related-repos/ in current directory...")
            context_dir.mkdir(parents=True, exist_ok=True)

        return context_dir

    def get_extraction_path(self, repo_url: str, content_type: str) -> Path:
        """
        Get path for extraction file based on location and naming convention.

        Args:
            repo_url: GitHub repository URL
            content_type: Type of content (digest, tree, installation, etc.)

        Returns:
            Path object for where extraction should be saved
        """
        owner, repo = self._parse_repo_full_name(repo_url)

        if self._is_phase_1_0_mode():
            # Phase 1.0: data/{repo}/{content_type}.txt
            return self.output_dir / "data" / repo / f"{content_type}.txt"
        else:
            # Phase 1.5: context/related-repos/{owner}-{repo}-{content_type}.txt
            return self.output_dir / f"{owner}-{repo}-{content_type}.txt"

    def get_analysis_path(self, repo_url: str, analysis_type: str) -> Path:
        """
        Get path for analysis file with proper naming convention.

        Args:
            repo_url: GitHub repository URL
            analysis_type: Type of analysis (installation, workflow, architecture, custom)

        Returns:
            Path object for where analysis should be saved
        """
        owner, repo = self._parse_repo_full_name(repo_url)

        if self._is_phase_1_0_mode():
            # Phase 1.0: analyze/{type}/{repo}.md
            return self.output_dir / "analyze" / analysis_type / f"{repo}.md"
        else:
            # Phase 1.5: context/related-repos/{owner}-{repo}-{type}.md
            return self.output_dir / f"{owner}-{repo}-{analysis_type}.md"

    def _is_phase_1_0_mode(self) -> bool:
        """
        Check if we're operating in Phase 1.0 mode (gitingest-agent-project).

        Returns:
            True if in gitingest-agent-project, False otherwise
        """
        return (self.output_dir / "execute" / "cli.py").exists()

    def _parse_repo_full_name(self, url: str) -> Tuple[str, str]:
        """
        Extract (owner, repo) from GitHub URL.

        Args:
            url: GitHub URL (e.g., https://github.com/owner/repo)

        Returns:
            Tuple of (owner, repo) strings

        Examples:
            >>> _parse_repo_full_name("https://github.com/facebook/react")
            ('facebook', 'react')
            >>> _parse_repo_full_name("https://github.com/vercel/next.js.git")
            ('vercel', 'next.js')
        """
        parts = url.rstrip('/').split('/')
        owner = parts[-2]
        repo = parts[-1].replace('.git', '')
        return (owner, repo)
