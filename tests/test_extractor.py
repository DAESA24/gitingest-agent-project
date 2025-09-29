"""
Unit tests for extractor module.

Tests cover:
- Full repository extraction
- Tree structure extraction
- Selective content extraction
- GitIngest subprocess execution
- Error handling for network, timeout, and filesystem errors
"""

import pytest
import subprocess
from unittest.mock import Mock, patch, call
from pathlib import Path
from exceptions import GitIngestError, StorageError, ValidationError
from extractor import (
    _run_gitingest,
    extract_full,
    extract_tree,
    extract_specific,
)


class TestRunGitingest:
    """Tests for _run_gitingest() helper function."""

    @patch('extractor.subprocess.run')
    def test_run_gitingest_success(self, mock_run):
        """Test successful GitIngest execution."""
        mock_run.return_value = Mock(
            stdout="Repository extracted successfully",
            stderr="",
            returncode=0
        )

        result = _run_gitingest(['https://github.com/user/repo', '-o', 'output.txt'])

        assert result.returncode == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ['gitingest', 'https://github.com/user/repo', '-o', 'output.txt']

    @patch('extractor.subprocess.run')
    def test_run_gitingest_timeout(self, mock_run):
        """Test timeout handling."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=['gitingest'],
            timeout=300
        )

        with pytest.raises(TimeoutError) as exc_info:
            _run_gitingest(['https://github.com/user/repo', '-o', 'output.txt'])

        assert "timed out after 300s" in str(exc_info.value)

    @patch('extractor.subprocess.run')
    def test_run_gitingest_custom_timeout(self, mock_run):
        """Test custom timeout parameter."""
        mock_run.return_value = Mock(returncode=0)

        _run_gitingest(['url', '-o', 'file'], timeout=120)

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs['timeout'] == 120

    @patch('extractor.subprocess.run')
    def test_run_gitingest_repository_not_found(self, mock_run):
        """Test repository not found error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['gitingest'],
            stderr="fatal: repository 'https://github.com/user/notfound' not found"
        )

        with pytest.raises(GitIngestError) as exc_info:
            _run_gitingest(['https://github.com/user/notfound', '-o', 'output.txt'])

        error_msg = str(exc_info.value)
        assert "Repository not found" in error_msg
        assert "https://github.com/user/notfound" in error_msg

    @patch('extractor.subprocess.run')
    def test_run_gitingest_authentication_error(self, mock_run):
        """Test authentication error for private repositories."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['gitingest'],
            stderr="fatal: bad credentials - authentication failed"
        )

        with pytest.raises(GitIngestError) as exc_info:
            _run_gitingest(['https://github.com/user/private', '-o', 'output.txt'])

        error_msg = str(exc_info.value)
        assert "Authentication failed" in error_msg
        assert "private repository?" in error_msg

    @patch('extractor.subprocess.run')
    def test_run_gitingest_network_error(self, mock_run):
        """Test network error handling."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['gitingest'],
            stderr="fatal: could not resolve host: github.com"
        )

        with pytest.raises(GitIngestError) as exc_info:
            _run_gitingest(['https://github.com/user/repo', '-o', 'output.txt'])

        error_msg = str(exc_info.value)
        assert "Network error" in error_msg
        assert "Unable to reach GitHub" in error_msg

    @patch('extractor.subprocess.run')
    def test_run_gitingest_generic_error(self, mock_run):
        """Test generic GitIngest error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['gitingest'],
            stderr="Unknown error occurred"
        )

        with pytest.raises(GitIngestError) as exc_info:
            _run_gitingest(['url', '-o', 'output.txt'])

        assert "GitIngest error" in str(exc_info.value)
        assert "Unknown error occurred" in str(exc_info.value)


class TestExtractFull:
    """Tests for extract_full() function."""

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    def test_extract_full_success(self, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test successful full extraction."""
        # Setup mocks
        data_dir = tmp_path / "data" / "test-repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_run_gitingest.return_value = Mock(returncode=0)

        # Create the file that GitIngest would create
        digest_file = data_dir / "digest.txt"
        digest_file.write_text("Repository content", encoding='utf-8')

        # Execute
        result_path = extract_full("https://github.com/user/test-repo", "test-repo")

        # Verify
        assert Path(result_path).exists()
        assert Path(result_path).name == "digest.txt"
        assert Path(result_path).is_absolute()
        mock_ensure_dir.assert_called_once_with("test-repo")
        mock_run_gitingest.assert_called_once()

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    def test_extract_full_gitingest_args(self, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test GitIngest command arguments."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_run_gitingest.return_value = Mock(returncode=0)

        # Create digest file
        (data_dir / "digest.txt").write_text("content", encoding='utf-8')

        extract_full("https://github.com/user/repo", "repo")

        # Verify GitIngest was called with correct arguments
        call_args = mock_run_gitingest.call_args[0][0]
        assert call_args[0] == "https://github.com/user/repo"
        assert call_args[1] == '-o'
        assert 'digest.txt' in call_args[2]

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    def test_extract_full_timeout_value(self, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test full extraction uses 300-second timeout."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_run_gitingest.return_value = Mock(returncode=0)
        (data_dir / "digest.txt").write_text("content", encoding='utf-8')

        extract_full("https://github.com/user/repo", "repo")

        # Verify timeout parameter
        call_kwargs = mock_run_gitingest.call_args[1]
        assert call_kwargs['timeout'] == 300

    @patch('extractor.ensure_data_directory')
    def test_extract_full_storage_error(self, mock_ensure_dir):
        """Test StorageError raised when directory creation fails."""
        mock_ensure_dir.side_effect = PermissionError("Permission denied")

        with pytest.raises(StorageError) as exc_info:
            extract_full("https://github.com/user/repo", "repo")

        assert "Failed to create directory" in str(exc_info.value)


class TestExtractTree:
    """Tests for extract_tree() function."""

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    def test_extract_tree_success(self, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test successful tree extraction."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_run_gitingest.return_value = Mock(returncode=0)

        # Create tree file with content
        tree_file = data_dir / "tree.txt"
        tree_content = "README.md\nsrc/\n  main.py\n  utils.py\n"
        tree_file.write_text(tree_content, encoding='utf-8')

        # Execute
        result_path, content = extract_tree("https://github.com/user/repo", "repo")

        # Verify
        assert Path(result_path).exists()
        assert Path(result_path).name == "tree.txt"
        assert Path(result_path).is_absolute()
        assert content == tree_content
        mock_ensure_dir.assert_called_once_with("repo")

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    def test_extract_tree_gitingest_args(self, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test GitIngest command arguments for tree extraction."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_run_gitingest.return_value = Mock(returncode=0)
        (data_dir / "tree.txt").write_text("tree", encoding='utf-8')

        extract_tree("https://github.com/user/repo", "repo")

        # Verify GitIngest arguments include filtering
        call_args = mock_run_gitingest.call_args[0][0]
        assert '-i' in call_args
        assert 'README.md' in call_args
        assert '-s' in call_args
        assert '1024' in call_args

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    def test_extract_tree_timeout_value(self, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test tree extraction uses shorter timeout (120s)."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_run_gitingest.return_value = Mock(returncode=0)
        (data_dir / "tree.txt").write_text("tree", encoding='utf-8')

        extract_tree("https://github.com/user/repo", "repo")

        # Verify timeout parameter
        call_kwargs = mock_run_gitingest.call_args[1]
        assert call_kwargs['timeout'] == 120


class TestExtractSpecific:
    """Tests for extract_specific() function."""

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    @patch('extractor.get_filters_for_type')
    def test_extract_specific_docs(self, mock_get_filters, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test selective extraction with 'docs' content type."""
        # Setup mocks
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_get_filters.return_value = {
            'include': ['docs/**/*', '*.md'],
            'exclude': ['docs/examples/*']
        }
        mock_run_gitingest.return_value = Mock(returncode=0)

        # Create output file
        docs_file = data_dir / "docs-content.txt"
        docs_file.write_text("Documentation content", encoding='utf-8')

        # Execute
        result_path = extract_specific("https://github.com/user/repo", "repo", "docs")

        # Verify
        assert Path(result_path).exists()
        assert Path(result_path).name == "docs-content.txt"
        assert Path(result_path).is_absolute()
        mock_get_filters.assert_called_once_with("docs")

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    @patch('extractor.get_filters_for_type')
    def test_extract_specific_installation(self, mock_get_filters, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test selective extraction with 'installation' content type."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_get_filters.return_value = {
            'include': ['README*', 'setup.py', 'pyproject.toml'],
            'exclude': []
        }
        mock_run_gitingest.return_value = Mock(returncode=0)
        (data_dir / "installation-content.txt").write_text("Install instructions", encoding='utf-8')

        result_path = extract_specific("https://github.com/user/repo", "repo", "installation")

        assert "installation-content.txt" in result_path
        mock_get_filters.assert_called_once_with("installation")

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    @patch('extractor.get_filters_for_type')
    def test_extract_specific_code(self, mock_get_filters, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test selective extraction with 'code' content type."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_get_filters.return_value = {
            'include': ['src/**/*.py'],
            'exclude': ['tests/*']
        }
        mock_run_gitingest.return_value = Mock(returncode=0)
        (data_dir / "code-content.txt").write_text("Source code", encoding='utf-8')

        result_path = extract_specific("https://github.com/user/repo", "repo", "code")

        assert "code-content.txt" in result_path
        mock_get_filters.assert_called_once_with("code")

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    @patch('extractor.get_filters_for_type')
    def test_extract_specific_auto(self, mock_get_filters, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test selective extraction with 'auto' content type."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_get_filters.return_value = {
            'include': ['README*', 'docs/**/*.md'],
            'exclude': ['docs/archive/*']
        }
        mock_run_gitingest.return_value = Mock(returncode=0)
        (data_dir / "auto-content.txt").write_text("Auto selected content", encoding='utf-8')

        result_path = extract_specific("https://github.com/user/repo", "repo", "auto")

        assert "auto-content.txt" in result_path
        mock_get_filters.assert_called_once_with("auto")

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    @patch('extractor.get_filters_for_type')
    def test_extract_specific_filter_args(self, mock_get_filters, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test GitIngest command includes filter patterns."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_get_filters.return_value = {
            'include': ['*.md', 'docs/**/*'],
            'exclude': ['docs/examples/*']
        }
        mock_run_gitingest.return_value = Mock(returncode=0)
        (data_dir / "docs-content.txt").write_text("content", encoding='utf-8')

        extract_specific("https://github.com/user/repo", "repo", "docs")

        # Verify include and exclude patterns in GitIngest args
        call_args = mock_run_gitingest.call_args[0][0]
        assert '-i' in call_args
        assert '*.md' in call_args
        assert 'docs/**/*' in call_args
        assert '-e' in call_args
        assert 'docs/examples/*' in call_args

    @patch('extractor.get_filters_for_type')
    def test_extract_specific_invalid_type(self, mock_get_filters):
        """Test ValidationError raised for invalid content type."""
        mock_get_filters.side_effect = ValidationError("Invalid content type: invalid")

        with pytest.raises(ValidationError) as exc_info:
            extract_specific("https://github.com/user/repo", "repo", "invalid")

        assert "Invalid content type" in str(exc_info.value)


class TestIntegration:
    """Integration tests for extractor module."""

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    def test_full_extraction_workflow(self, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test complete full extraction workflow."""
        data_dir = tmp_path / "data" / "fastapi"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_run_gitingest.return_value = Mock(returncode=0)

        # Create expected output
        (data_dir / "digest.txt").write_text("Repository content", encoding='utf-8')

        # Extract
        result_path = extract_full("https://github.com/tiangolo/fastapi", "fastapi")

        # Verify
        assert Path(result_path).exists()
        assert "fastapi" in result_path
        assert "digest.txt" in result_path

    @patch('extractor._run_gitingest')
    @patch('extractor.ensure_data_directory')
    @patch('extractor.get_filters_for_type')
    def test_selective_extraction_workflow(self, mock_get_filters, mock_ensure_dir, mock_run_gitingest, tmp_path):
        """Test complete selective extraction workflow."""
        data_dir = tmp_path / "data" / "repo"
        data_dir.mkdir(parents=True)
        mock_ensure_dir.return_value = data_dir
        mock_get_filters.return_value = {
            'include': ['docs/**/*'],
            'exclude': ['docs/examples/*']
        }
        mock_run_gitingest.return_value = Mock(returncode=0)

        # Create expected outputs for multiple extractions
        (data_dir / "tree.txt").write_text("Tree structure", encoding='utf-8')
        (data_dir / "docs-content.txt").write_text("Docs content", encoding='utf-8')

        # Extract tree first
        tree_path, tree_content = extract_tree("https://github.com/user/repo", "repo")

        # Then extract specific content
        docs_path = extract_specific("https://github.com/user/repo", "repo", "docs")

        # Verify both extractions
        assert Path(tree_path).exists()
        assert tree_content == "Tree structure"
        assert Path(docs_path).exists()
        assert "docs-content.txt" in docs_path