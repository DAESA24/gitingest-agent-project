"""
Unit tests for storage module.

Tests cover:
- URL parsing and repo name extraction
- Directory creation for data and analyze paths
- Path sanitization and validation
- Error handling for invalid inputs
"""

import pytest
from pathlib import Path
from unittest.mock import patch
from exceptions import ValidationError, StorageError
from storage import (
    parse_repo_name,
    ensure_data_directory,
    ensure_analyze_directory,
    save_analysis,
)


class TestParseRepoName:
    """Tests for parse_repo_name() function."""

    def test_parse_repo_name_basic(self):
        """Test extracting repo name from standard GitHub URL."""
        assert parse_repo_name("https://github.com/tiangolo/fastapi") == "fastapi"
        assert parse_repo_name("https://github.com/pallets/click") == "click"
        assert parse_repo_name("https://github.com/user/my-repo") == "my-repo"

    def test_parse_repo_name_with_git_suffix(self):
        """Test handling .git suffix removal."""
        assert parse_repo_name("https://github.com/tiangolo/fastapi.git") == "fastapi"
        assert parse_repo_name("https://github.com/user/repo.git") == "repo"

    def test_parse_repo_name_with_trailing_slash(self):
        """Test handling trailing slash."""
        assert parse_repo_name("https://github.com/tiangolo/fastapi/") == "fastapi"
        assert parse_repo_name("https://github.com/user/repo/") == "repo"

    def test_parse_repo_name_with_trailing_slash_and_git(self):
        """Test handling both trailing slash and .git suffix."""
        # Edge case: .git with trailing slash
        assert parse_repo_name("https://github.com/user/repo.git/") == "repo"

    def test_parse_repo_name_sanitization(self):
        """Test removal of special characters."""
        # Note: GitHub doesn't allow most special chars, but we sanitize defensively
        result = parse_repo_name("https://github.com/user/repo-name_123")
        assert result == "repo-name_123"

    def test_parse_repo_name_with_underscore(self):
        """Test repo names with underscores are preserved."""
        assert parse_repo_name("https://github.com/user/my_repo") == "my_repo"

    def test_parse_repo_name_with_numbers(self):
        """Test repo names with numbers are preserved."""
        assert parse_repo_name("https://github.com/user/repo123") == "repo123"
        assert parse_repo_name("https://github.com/user/123repo") == "123repo"

    def test_parse_repo_name_invalid_empty_url(self):
        """Test empty URL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            parse_repo_name("")
        assert "non-empty string" in str(exc_info.value)

    def test_parse_repo_name_invalid_none(self):
        """Test None URL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            parse_repo_name(None)
        assert "non-empty string" in str(exc_info.value)

    def test_parse_repo_name_invalid_format(self):
        """Test invalid URL format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            parse_repo_name("invalid")
        assert "Invalid" in str(exc_info.value)

    def test_parse_repo_name_http_protocol(self):
        """Test HTTP protocol (not just HTTPS) works."""
        assert parse_repo_name("http://github.com/user/repo") == "repo"

    def test_parse_repo_name_github_enterprise(self):
        """Test GitHub Enterprise-style URLs work."""
        # Works because we extract last component regardless of domain
        assert parse_repo_name("https://github.company.com/user/repo") == "repo"


class TestEnsureDataDirectory:
    """Tests for ensure_data_directory() function."""

    def test_ensure_data_directory_creates_path(self, tmp_path, monkeypatch):
        """Test directory creation for data path."""
        # Change to temp directory for isolated testing
        monkeypatch.chdir(tmp_path)

        data_dir = ensure_data_directory("test-repo")

        assert data_dir.exists()
        assert data_dir.is_dir()
        assert data_dir.name == "test-repo"
        # Phase 1.5: context/related-repos/[repo]/ structure
        assert data_dir.parent.name == "related-repos"
        assert data_dir.parent.parent.name == "context"

    def test_ensure_data_directory_returns_absolute(self, tmp_path, monkeypatch):
        """Test absolute path is returned."""
        monkeypatch.chdir(tmp_path)

        data_dir = ensure_data_directory("test-repo")

        assert data_dir.is_absolute()

    def test_ensure_data_directory_idempotent(self, tmp_path, monkeypatch):
        """Test calling twice doesn't error (exist_ok=True)."""
        monkeypatch.chdir(tmp_path)

        # Create once
        data_dir1 = ensure_data_directory("test-repo")
        # Create again
        data_dir2 = ensure_data_directory("test-repo")

        assert data_dir1 == data_dir2
        assert data_dir1.exists()

    def test_ensure_data_directory_multiple_repos(self, tmp_path, monkeypatch):
        """Test creating directories for multiple repositories."""
        monkeypatch.chdir(tmp_path)

        fastapi_dir = ensure_data_directory("fastapi")
        click_dir = ensure_data_directory("click")

        assert fastapi_dir.exists()
        assert click_dir.exists()
        assert fastapi_dir != click_dir

    def test_ensure_data_directory_with_hyphen(self, tmp_path, monkeypatch):
        """Test repo names with hyphens work correctly."""
        monkeypatch.chdir(tmp_path)

        data_dir = ensure_data_directory("my-test-repo")

        assert data_dir.exists()
        assert data_dir.name == "my-test-repo"

    def test_ensure_data_directory_with_underscore(self, tmp_path, monkeypatch):
        """Test repo names with underscores work correctly."""
        monkeypatch.chdir(tmp_path)

        data_dir = ensure_data_directory("my_test_repo")

        assert data_dir.exists()
        assert data_dir.name == "my_test_repo"


class TestEnsureAnalyzeDirectory:
    """Tests for ensure_analyze_directory() function."""

    def test_ensure_analyze_directory_installation(self, tmp_path, monkeypatch):
        """Test creation for installation analysis type."""
        monkeypatch.chdir(tmp_path)

        analyze_dir = ensure_analyze_directory("installation")

        assert analyze_dir.exists()
        assert analyze_dir.is_dir()
        assert analyze_dir.name == "installation"
        assert analyze_dir.parent.name == "analyze"

    def test_ensure_analyze_directory_workflow(self, tmp_path, monkeypatch):
        """Test creation for workflow analysis type."""
        monkeypatch.chdir(tmp_path)

        analyze_dir = ensure_analyze_directory("workflow")

        assert analyze_dir.exists()
        assert analyze_dir.name == "workflow"

    def test_ensure_analyze_directory_architecture(self, tmp_path, monkeypatch):
        """Test creation for architecture analysis type."""
        monkeypatch.chdir(tmp_path)

        analyze_dir = ensure_analyze_directory("architecture")

        assert analyze_dir.exists()
        assert analyze_dir.name == "architecture"

    def test_ensure_analyze_directory_custom(self, tmp_path, monkeypatch):
        """Test creation for custom analysis type."""
        monkeypatch.chdir(tmp_path)

        analyze_dir = ensure_analyze_directory("custom")

        assert analyze_dir.exists()
        assert analyze_dir.name == "custom"

    def test_ensure_analyze_directory_all_types(self, tmp_path, monkeypatch):
        """Test creation for all analysis types."""
        monkeypatch.chdir(tmp_path)

        types = ["installation", "workflow", "architecture", "custom"]
        dirs = [ensure_analyze_directory(t) for t in types]

        # All directories should exist
        for d in dirs:
            assert d.exists()
            assert d.is_dir()

        # All directories should be distinct
        assert len(set(dirs)) == len(dirs)

    def test_ensure_analyze_directory_returns_absolute(self, tmp_path, monkeypatch):
        """Test absolute path is returned."""
        monkeypatch.chdir(tmp_path)

        analyze_dir = ensure_analyze_directory("installation")

        assert analyze_dir.is_absolute()

    def test_ensure_analyze_directory_idempotent(self, tmp_path, monkeypatch):
        """Test calling twice doesn't error (exist_ok=True)."""
        monkeypatch.chdir(tmp_path)

        # Create once
        analyze_dir1 = ensure_analyze_directory("installation")
        # Create again
        analyze_dir2 = ensure_analyze_directory("installation")

        assert analyze_dir1 == analyze_dir2
        assert analyze_dir1.exists()


class TestErrorHandling:
    """Tests for error handling in storage module."""

    def test_ensure_data_directory_permission_error(self, tmp_path, monkeypatch):
        """Test StorageError raised on permission errors."""
        monkeypatch.chdir(tmp_path)

        # Mock Path.mkdir to raise PermissionError
        from unittest.mock import Mock, patch
        with patch('storage.Path.mkdir', side_effect=PermissionError("Access denied")):
            with pytest.raises(StorageError) as exc_info:
                ensure_data_directory("test-repo")
            assert "Permission denied" in str(exc_info.value)

    def test_ensure_data_directory_os_error(self, tmp_path, monkeypatch):
        """Test StorageError raised on OS errors."""
        monkeypatch.chdir(tmp_path)

        # Mock Path.mkdir to raise OSError
        from unittest.mock import Mock, patch
        with patch('storage.Path.mkdir', side_effect=OSError("Disk full")):
            with pytest.raises(StorageError) as exc_info:
                ensure_data_directory("test-repo")
            assert "Failed to create directory" in str(exc_info.value)

    def test_ensure_analyze_directory_permission_error(self, tmp_path, monkeypatch):
        """Test StorageError raised on permission errors for analyze dir."""
        monkeypatch.chdir(tmp_path)

        # Mock Path.mkdir to raise PermissionError
        from unittest.mock import Mock, patch
        with patch('storage.Path.mkdir', side_effect=PermissionError("Access denied")):
            with pytest.raises(StorageError) as exc_info:
                ensure_analyze_directory("installation")
            assert "Permission denied" in str(exc_info.value)

    def test_ensure_analyze_directory_os_error(self, tmp_path, monkeypatch):
        """Test StorageError raised on OS errors for analyze dir."""
        monkeypatch.chdir(tmp_path)

        # Mock Path.mkdir to raise OSError
        from unittest.mock import Mock, patch
        with patch('storage.Path.mkdir', side_effect=OSError("Disk full")):
            with pytest.raises(StorageError) as exc_info:
                ensure_analyze_directory("installation")
            assert "Failed to create directory" in str(exc_info.value)


class TestIntegration:
    """Integration tests for storage module."""

    def test_full_workflow_data_then_analyze(self, tmp_path, monkeypatch):
        """Test creating data directory then analyze directory."""
        monkeypatch.chdir(tmp_path)

        # Parse repo name from URL
        repo_name = parse_repo_name("https://github.com/tiangolo/fastapi")

        # Create data directory
        data_dir = ensure_data_directory(repo_name)

        # Create analyze directory
        analyze_dir = ensure_analyze_directory("installation")

        # Both should exist
        assert data_dir.exists()
        assert analyze_dir.exists()

        # Verify structure (Phase 1.5: context/related-repos/)
        assert (tmp_path / "context" / "related-repos" / "fastapi").exists()
        assert (tmp_path / "analyze" / "installation").exists()

    def test_multiple_repos_multiple_analyses(self, tmp_path, monkeypatch):
        """Test complex scenario with multiple repos and analysis types."""
        monkeypatch.chdir(tmp_path)

        # Parse multiple repos
        repos = [
            "https://github.com/tiangolo/fastapi",
            "https://github.com/pallets/click",
            "https://github.com/psf/requests",
        ]
        repo_names = [parse_repo_name(url) for url in repos]

        # Create data directories for all
        data_dirs = [ensure_data_directory(name) for name in repo_names]

        # Create multiple analysis types
        analysis_types = ["installation", "workflow", "architecture"]
        analyze_dirs = [ensure_analyze_directory(t) for t in analysis_types]

        # Verify all exist
        assert len(data_dirs) == 3
        assert len(analyze_dirs) == 3
        for d in data_dirs + analyze_dirs:
            assert d.exists()

    def test_parse_and_ensure_combined(self, tmp_path, monkeypatch):
        """Test parsing URL and ensuring directory in one flow."""
        monkeypatch.chdir(tmp_path)

        url = "https://github.com/user/my-awesome-repo.git"
        repo_name = parse_repo_name(url)
        data_dir = ensure_data_directory(repo_name)

        assert repo_name == "my-awesome-repo"
        assert data_dir.exists()
        assert data_dir.name == "my-awesome-repo"


class TestSaveAnalysis:
    """Test save_analysis function."""

    def test_save_analysis_creates_file(self, tmp_path):
        """Test save_analysis creates analysis file."""
        analyze_dir = tmp_path / "analyze" / "installation"
        analyze_dir.mkdir(parents=True)

        with patch('storage.ensure_analyze_directory', return_value=analyze_dir):
            content = "# Analysis\n\nDetailed analysis content..."
            output_path = save_analysis(content, "fastapi", "installation")

            assert Path(output_path).exists()
            assert "fastapi.md" in output_path
            assert analyze_dir / "fastapi.md" == Path(output_path)

    def test_save_analysis_includes_metadata(self, tmp_path):
        """Test saved file includes metadata header."""
        analyze_dir = tmp_path / "analyze" / "workflow"
        analyze_dir.mkdir(parents=True)

        with patch('storage.ensure_analyze_directory', return_value=analyze_dir):
            content = "# Analysis content\n\nThis is the main analysis..."
            output_path = save_analysis(content, "django", "workflow")

            saved_content = Path(output_path).read_text(encoding='utf-8')
            assert "# django - Workflow Analysis" in saved_content
            assert "**Analyzed:**" in saved_content
            assert "**Analysis Type:** workflow" in saved_content
            assert "---" in saved_content
            assert "# Analysis content" in saved_content

    def test_save_analysis_all_types(self, tmp_path):
        """Test save_analysis with all analysis types."""
        for analysis_type in ['installation', 'workflow', 'architecture', 'custom']:
            analyze_dir = tmp_path / "analyze" / analysis_type
            analyze_dir.mkdir(parents=True, exist_ok=True)

            with patch('storage.ensure_analyze_directory', return_value=analyze_dir):
                output_path = save_analysis("Test content", "test-repo", analysis_type)

                assert analyze_dir / "test-repo.md" == Path(output_path)
                assert Path(output_path).exists()

                saved_content = Path(output_path).read_text(encoding='utf-8')
                assert f"**Analysis Type:** {analysis_type}" in saved_content

    def test_save_analysis_returns_absolute_path(self, tmp_path):
        """Test absolute path is returned."""
        analyze_dir = tmp_path / "analyze" / "installation"
        analyze_dir.mkdir(parents=True)

        with patch('storage.ensure_analyze_directory', return_value=analyze_dir):
            output_path = save_analysis("Content", "repo", "installation")

            assert Path(output_path).is_absolute()

    def test_save_analysis_overwrites_existing(self, tmp_path):
        """Test existing file is overwritten with new analysis."""
        analyze_dir = tmp_path / "analyze" / "installation"
        analyze_dir.mkdir(parents=True)
        existing_file = analyze_dir / "repo.md"
        existing_file.write_text("Old content that should be replaced")

        with patch('storage.ensure_analyze_directory', return_value=analyze_dir):
            output_path = save_analysis("New analysis content", "repo", "installation")

            saved_content = Path(output_path).read_text(encoding='utf-8')
            assert "New analysis content" in saved_content
            assert "Old content that should be replaced" not in saved_content

    def test_save_analysis_metadata_format(self, tmp_path):
        """Test metadata header format is correct."""
        analyze_dir = tmp_path / "analyze" / "architecture"
        analyze_dir.mkdir(parents=True)

        with patch('storage.ensure_analyze_directory', return_value=analyze_dir):
            content = "## System Design\n\nThe system consists of..."
            output_path = save_analysis(content, "fastapi", "architecture")

            saved_content = Path(output_path).read_text(encoding='utf-8')

            # Check metadata structure
            lines = saved_content.split('\n')
            assert lines[0] == "# fastapi - Architecture Analysis"
            assert lines[1] == ""
            assert "**Repository:**" in lines[2]
            assert "**Analyzed:**" in lines[3]
            assert "**Analysis Type:** architecture" in lines[4]
            assert lines[5] == ""
            assert lines[6] == "---"
            assert lines[7] == ""
            # Content starts after metadata
            assert "## System Design" in saved_content

    def test_save_analysis_date_included(self, tmp_path):
        """Test analysis includes current date."""
        analyze_dir = tmp_path / "analyze" / "workflow"
        analyze_dir.mkdir(parents=True)

        with patch('storage.ensure_analyze_directory', return_value=analyze_dir):
            from datetime import datetime
            expected_date = datetime.now().strftime("%Y-%m-%d")

            output_path = save_analysis("Content", "test-repo", "workflow")
            saved_content = Path(output_path).read_text(encoding='utf-8')

            assert f"**Analyzed:** {expected_date}" in saved_content

    def test_save_analysis_storage_error_directory_creation(self, tmp_path):
        """Test StorageError raised when directory creation fails."""
        with patch('storage.ensure_analyze_directory', side_effect=PermissionError("Permission denied")):
            with pytest.raises(StorageError) as exc_info:
                save_analysis("Content", "repo", "installation")

            assert "Failed to create analyze directory" in str(exc_info.value)

    def test_save_analysis_storage_error_file_write(self, tmp_path):
        """Test StorageError raised when file write fails."""
        analyze_dir = tmp_path / "analyze" / "installation"
        analyze_dir.mkdir(parents=True)

        with patch('storage.ensure_analyze_directory', return_value=analyze_dir):
            # Make the file read-only to cause write failure
            output_file = analyze_dir / "repo.md"
            output_file.write_text("test")
            output_file.chmod(0o444)  # Read-only

            try:
                with pytest.raises(StorageError) as exc_info:
                    save_analysis("Content", "repo", "installation")

                assert "Failed to write analysis file" in str(exc_info.value)
            finally:
                # Restore permissions for cleanup
                output_file.chmod(0o644)