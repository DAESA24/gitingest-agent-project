"""
Tests for storage_manager module.

Verifies StorageManager path detection, file naming conventions,
and Phase 1.0/1.5 mode switching.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from storage_manager import StorageManager


class TestStorageManagerDetection:
    """Test automatic location detection logic."""

    @patch('storage_manager.Path.cwd')
    def test_detect_location_gitingest_project(self, mock_cwd, tmp_path):
        """Should detect gitingest-agent-project and return cwd."""
        # Setup: Create marker files
        project_dir = tmp_path / "gitingest-agent-project"
        project_dir.mkdir()
        execute_dir = project_dir / "execute"
        execute_dir.mkdir()
        (execute_dir / "cli.py").touch()
        (execute_dir / "main.py").touch()

        mock_cwd.return_value = project_dir

        manager = StorageManager()

        assert manager.output_dir == project_dir
        assert manager._is_phase_1_0_mode() is True

    @patch('storage_manager.Path.cwd')
    def test_detect_location_other_directory(self, mock_cwd, tmp_path):
        """Should detect non-gitingest directory and return context/related-repos/."""
        other_dir = tmp_path / "my-react-app"
        other_dir.mkdir()

        mock_cwd.return_value = other_dir

        manager = StorageManager()

        expected_context = other_dir / "context" / "related-repos"
        assert manager.output_dir == expected_context
        assert expected_context.exists()
        assert manager._is_phase_1_0_mode() is False

    @patch('storage_manager.Path.cwd')
    def test_auto_create_context_folder(self, mock_cwd, tmp_path, capsys):
        """Should auto-create context/related-repos/ and notify user."""
        project_dir = tmp_path / "some-project"
        project_dir.mkdir()

        mock_cwd.return_value = project_dir

        manager = StorageManager()

        context_dir = project_dir / "context" / "related-repos"
        assert context_dir.exists()

        # Check user notification
        captured = capsys.readouterr()
        assert "Creating context/related-repos/" in captured.out

    def test_manual_output_dir(self, tmp_path):
        """Should use provided output_dir instead of auto-detection."""
        custom_dir = tmp_path / "custom-output"
        custom_dir.mkdir()

        manager = StorageManager(output_dir=custom_dir)

        assert manager.output_dir == custom_dir


class TestStorageManagerPaths:
    """Test path generation for different modes."""

    def test_extraction_path_phase_1_0(self, tmp_path):
        """Phase 1.0: data/{repo}/{content_type}.txt"""
        # Setup Phase 1.0 environment
        project_dir = tmp_path / "gitingest-agent-project"
        project_dir.mkdir()
        execute_dir = project_dir / "execute"
        execute_dir.mkdir()
        (execute_dir / "cli.py").touch()
        (execute_dir / "main.py").touch()

        manager = StorageManager(output_dir=project_dir)

        path = manager.get_extraction_path(
            "https://github.com/facebook/react",
            "digest"
        )

        expected = project_dir / "data" / "react" / "digest.txt"
        assert path == expected

    def test_extraction_path_phase_1_5(self, tmp_path):
        """Phase 1.5: context/related-repos/{owner}-{repo}-{content_type}.txt"""
        context_dir = tmp_path / "context" / "related-repos"
        context_dir.mkdir(parents=True)

        manager = StorageManager(output_dir=context_dir)

        path = manager.get_extraction_path(
            "https://github.com/facebook/react",
            "digest"
        )

        expected = context_dir / "facebook-react-digest.txt"
        assert path == expected

    def test_analysis_path_phase_1_0(self, tmp_path):
        """Phase 1.0: analyze/{type}/{repo}.md"""
        project_dir = tmp_path / "gitingest-agent-project"
        project_dir.mkdir()
        execute_dir = project_dir / "execute"
        execute_dir.mkdir()
        (execute_dir / "cli.py").touch()
        (execute_dir / "main.py").touch()

        manager = StorageManager(output_dir=project_dir)

        path = manager.get_analysis_path(
            "https://github.com/facebook/react",
            "installation"
        )

        expected = project_dir / "analyze" / "installation" / "react.md"
        assert path == expected

    def test_analysis_path_phase_1_5(self, tmp_path):
        """Phase 1.5: context/related-repos/{owner}-{repo}-{type}.md"""
        context_dir = tmp_path / "context" / "related-repos"
        context_dir.mkdir(parents=True)

        manager = StorageManager(output_dir=context_dir)

        path = manager.get_analysis_path(
            "https://github.com/facebook/react",
            "installation"
        )

        expected = context_dir / "facebook-react-installation.md"
        assert path == expected

    def test_analysis_path_with_git_suffix(self, tmp_path):
        """Should handle .git suffix in URLs correctly."""
        context_dir = tmp_path / "context" / "related-repos"
        context_dir.mkdir(parents=True)

        manager = StorageManager(output_dir=context_dir)

        path = manager.get_analysis_path(
            "https://github.com/vercel/next.js.git",
            "workflow"
        )

        expected = context_dir / "vercel-next.js-workflow.md"
        assert path == expected


class TestStorageManagerRepoNameParsing:
    """Test GitHub URL parsing logic."""

    def test_parse_standard_url(self, tmp_path):
        """Should parse standard GitHub URL."""
        manager = StorageManager(output_dir=tmp_path)
        owner, repo = manager._parse_repo_full_name("https://github.com/facebook/react")

        assert owner == "facebook"
        assert repo == "react"

    def test_parse_url_with_git_suffix(self, tmp_path):
        """Should remove .git suffix."""
        manager = StorageManager(output_dir=tmp_path)
        owner, repo = manager._parse_repo_full_name("https://github.com/vercel/next.js.git")

        assert owner == "vercel"
        assert repo == "next.js"

    def test_parse_url_with_trailing_slash(self, tmp_path):
        """Should handle trailing slash."""
        manager = StorageManager(output_dir=tmp_path)
        owner, repo = manager._parse_repo_full_name("https://github.com/tiangolo/fastapi/")

        assert owner == "tiangolo"
        assert repo == "fastapi"

    def test_parse_maintains_special_chars_in_repo_name(self, tmp_path):
        """Should preserve dots and hyphens in repo names."""
        manager = StorageManager(output_dir=tmp_path)
        owner, repo = manager._parse_repo_full_name("https://github.com/vuejs/vue-next")

        assert owner == "vuejs"
        assert repo == "vue-next"


class TestStorageManagerPhaseDetection:
    """Test Phase 1.0 vs 1.5 mode detection."""

    def test_is_phase_1_0_mode_true(self, tmp_path):
        """Should return True when execute/cli.py exists."""
        project_dir = tmp_path / "gitingest-agent-project"
        project_dir.mkdir()
        execute_dir = project_dir / "execute"
        execute_dir.mkdir()
        (execute_dir / "cli.py").touch()

        manager = StorageManager(output_dir=project_dir)

        assert manager._is_phase_1_0_mode() is True

    def test_is_phase_1_0_mode_false(self, tmp_path):
        """Should return False when execute/cli.py doesn't exist."""
        other_dir = tmp_path / "other-project"
        other_dir.mkdir()

        manager = StorageManager(output_dir=other_dir)

        assert manager._is_phase_1_0_mode() is False


class TestStorageManagerEdgeCases:
    """Test edge cases and error conditions."""

    @patch('storage_manager.Path.cwd')
    def test_context_folder_already_exists(self, mock_cwd, tmp_path, capsys):
        """Should not print message if context folder already exists."""
        project_dir = tmp_path / "existing-project"
        project_dir.mkdir()
        context_dir = project_dir / "context" / "related-repos"
        context_dir.mkdir(parents=True)

        mock_cwd.return_value = project_dir

        manager = StorageManager()

        # Should NOT print creation message
        captured = capsys.readouterr()
        assert "Creating context/related-repos/" not in captured.out
        assert manager.output_dir == context_dir

    def test_multiple_path_generations(self, tmp_path):
        """Should generate consistent paths across multiple calls."""
        context_dir = tmp_path / "context" / "related-repos"
        context_dir.mkdir(parents=True)

        manager = StorageManager(output_dir=context_dir)

        path1 = manager.get_analysis_path("https://github.com/facebook/react", "installation")
        path2 = manager.get_analysis_path("https://github.com/facebook/react", "installation")

        assert path1 == path2
