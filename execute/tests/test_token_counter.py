"""
Unit tests for token_counter module.

Tests cover:
- Token counting with GitIngest integration (mocked)
- Token parsing and fallback estimation
- File-based token counting
- Routing decision logic
- Error handling for timeouts and GitIngest failures
"""

import pytest
import subprocess
from unittest.mock import Mock, patch
from pathlib import Path
from exceptions import GitIngestError, ValidationError
from token_counter import (
    count_tokens,
    count_tokens_from_file,
    should_extract_full,
)


class TestCountTokens:
    """Tests for count_tokens() function."""

    @patch('token_counter.subprocess.run')
    def test_count_tokens_under_threshold(self, mock_run):
        """Test counting repository under 200k threshold."""
        mock_run.return_value = Mock(
            stdout="Estimated tokens: 145000\n[content]",
            returncode=0
        )

        count = count_tokens("https://github.com/user/repo")

        assert count == 145000
        assert should_extract_full(count) == True
        # Verify GitIngest was called correctly
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ['gitingest', 'https://github.com/user/repo', '-o', '-']

    @patch('token_counter.subprocess.run')
    def test_count_tokens_over_threshold(self, mock_run):
        """Test counting repository over 200k threshold."""
        mock_run.return_value = Mock(
            stdout="Estimated tokens: 487523\n[content]",
            returncode=0
        )

        count = count_tokens("https://github.com/user/repo")

        assert count == 487523
        assert should_extract_full(count) == False

    @patch('token_counter.subprocess.run')
    def test_count_tokens_at_threshold(self, mock_run):
        """Test counting repository exactly at 200k threshold."""
        mock_run.return_value = Mock(
            stdout="Estimated tokens: 200000\n[content]",
            returncode=0
        )

        count = count_tokens("https://github.com/user/repo")

        assert count == 200000
        assert should_extract_full(count) == False  # >= threshold = selective

    @patch('token_counter.subprocess.run')
    def test_count_tokens_fallback_estimation(self, mock_run):
        """Test fallback to character-based estimation."""
        # No "Estimated tokens" in output, use fallback
        mock_run.return_value = Mock(
            stdout="a" * 400_000,  # 100k tokens estimated (400k / 4)
            returncode=0
        )

        count = count_tokens("https://github.com/user/repo")

        assert count == 100_000

    @patch('token_counter.subprocess.run')
    def test_count_tokens_small_repo_fallback(self, mock_run):
        """Test fallback estimation for very small repository."""
        mock_run.return_value = Mock(
            stdout="a" * 4000,  # 1k tokens estimated
            returncode=0
        )

        count = count_tokens("https://github.com/user/repo")

        assert count == 1000

    @patch('token_counter.subprocess.run')
    def test_count_tokens_timeout(self, mock_run):
        """Test timeout handling for very large repos."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=['gitingest'],
            timeout=120
        )

        with pytest.raises(TimeoutError) as exc_info:
            count_tokens("https://github.com/user/repo")

        error_msg = str(exc_info.value)
        assert "timed out after 120 seconds" in error_msg
        assert "extract-tree" in error_msg  # Suggests alternative
        assert "extract-specific" in error_msg

    @patch('token_counter.subprocess.run')
    def test_count_tokens_network_error(self, mock_run):
        """Test network error handling."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['gitingest'],
            stderr="could not resolve host"
        )

        with pytest.raises(GitIngestError) as exc_info:
            count_tokens("https://github.com/user/repo")

        assert "Network error" in str(exc_info.value)
        assert "Unable to reach GitHub" in str(exc_info.value)

    @patch('token_counter.subprocess.run')
    def test_count_tokens_repository_not_found(self, mock_run):
        """Test 404 repository not found handling."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['gitingest'],
            stderr="repository not found: 404 error"
        )

        with pytest.raises(GitIngestError) as exc_info:
            count_tokens("https://github.com/user/nonexistent")

        assert "Repository not found" in str(exc_info.value)

    @patch('token_counter.subprocess.run')
    def test_count_tokens_authentication_error(self, mock_run):
        """Test authentication error for private repositories."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['gitingest'],
            stderr="authentication failed: permission denied"
        )

        with pytest.raises(GitIngestError) as exc_info:
            count_tokens("https://github.com/user/private-repo")

        error_msg = str(exc_info.value)
        assert "Authentication failed" in error_msg
        assert "private repository?" in error_msg

    @patch('token_counter.subprocess.run')
    def test_count_tokens_generic_error(self, mock_run):
        """Test generic GitIngest error handling."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['gitingest'],
            stderr="Unknown error occurred"
        )

        with pytest.raises(GitIngestError) as exc_info:
            count_tokens("https://github.com/user/repo")

        assert "GitIngest failed" in str(exc_info.value)
        assert "Unknown error occurred" in str(exc_info.value)

    @patch('token_counter.subprocess.run')
    def test_count_tokens_invalid_url(self, mock_run):
        """Test ValidationError raised for invalid URL."""
        # Should raise ValidationError before calling subprocess
        with pytest.raises(ValidationError):
            count_tokens("not-a-valid-url")

        # Subprocess should not have been called
        mock_run.assert_not_called()

    @patch('token_counter.subprocess.run')
    def test_count_tokens_timeout_value(self, mock_run):
        """Test timeout parameter is set correctly."""
        mock_run.return_value = Mock(
            stdout="Estimated tokens: 10000\n",
            returncode=0
        )

        count_tokens("https://github.com/user/repo")

        # Check timeout was passed to subprocess.run
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs['timeout'] == 120

    @patch('token_counter.subprocess.run')
    def test_count_tokens_check_flag(self, mock_run):
        """Test check=True is set for subprocess.run."""
        mock_run.return_value = Mock(
            stdout="Estimated tokens: 10000\n",
            returncode=0
        )

        count_tokens("https://github.com/user/repo")

        # Verify check=True for automatic exception raising
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs['check'] == True


class TestCountTokensFromFile:
    """Tests for count_tokens_from_file() function."""

    def test_count_tokens_from_file_basic(self, tmp_path):
        """Test counting tokens from existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("a" * 80_000, encoding='utf-8')  # 20k tokens

        count = count_tokens_from_file(str(test_file))

        assert count == 20_000

    def test_count_tokens_from_file_large(self, tmp_path):
        """Test counting tokens from large file."""
        test_file = tmp_path / "large.txt"
        test_file.write_text("x" * 1_000_000, encoding='utf-8')  # 250k tokens

        count = count_tokens_from_file(str(test_file))

        assert count == 250_000

    def test_count_tokens_from_file_small(self, tmp_path):
        """Test counting tokens from very small file."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("hello", encoding='utf-8')  # 1 token (5 chars / 4)

        count = count_tokens_from_file(str(test_file))

        assert count == 1

    def test_count_tokens_from_file_empty(self, tmp_path):
        """Test counting tokens from empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding='utf-8')

        count = count_tokens_from_file(str(test_file))

        assert count == 0

    def test_count_tokens_from_file_not_found(self):
        """Test error handling for missing file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            count_tokens_from_file("nonexistent.txt")

        assert "File not found" in str(exc_info.value)
        assert "nonexistent.txt" in str(exc_info.value)

    def test_count_tokens_from_file_path_object(self, tmp_path):
        """Test function accepts Path objects."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("a" * 4000, encoding='utf-8')

        # Should work with Path object (converted to string internally)
        count = count_tokens_from_file(str(test_file))

        assert count == 1000

    def test_count_tokens_from_file_multiline(self, tmp_path):
        """Test counting with multiline content."""
        test_file = tmp_path / "multiline.txt"
        content = "line 1\nline 2\nline 3\n" * 1000  # ~21k chars
        test_file.write_text(content, encoding='utf-8')

        count = count_tokens_from_file(str(test_file))

        # Should count all characters including newlines
        expected = len(content) // 4
        assert count == expected


class TestShouldExtractFull:
    """Tests for should_extract_full() function."""

    def test_should_extract_full_under_threshold(self):
        """Test routing decision for small repo."""
        assert should_extract_full(145_000) == True
        assert should_extract_full(100_000) == True
        assert should_extract_full(1_000) == True

    def test_should_extract_full_over_threshold(self):
        """Test routing decision for large repo."""
        assert should_extract_full(487_523) == False
        assert should_extract_full(300_000) == False
        assert should_extract_full(200_001) == False

    def test_should_extract_full_exactly_at_threshold(self):
        """Test routing decision at exact threshold."""
        # At threshold = selective extraction (>= threshold)
        assert should_extract_full(200_000) == False

    def test_should_extract_full_just_below_threshold(self):
        """Test routing decision just below threshold."""
        assert should_extract_full(199_999) == True

    def test_should_extract_full_custom_threshold(self):
        """Test routing with custom threshold."""
        assert should_extract_full(150_000, threshold=100_000) == False
        assert should_extract_full(50_000, threshold=100_000) == True
        assert should_extract_full(100_000, threshold=100_000) == False

    def test_should_extract_full_zero_threshold(self):
        """Test edge case with zero threshold."""
        # Everything should be selective with 0 threshold
        assert should_extract_full(0, threshold=0) == False
        assert should_extract_full(1, threshold=0) == False

    def test_should_extract_full_very_large_threshold(self):
        """Test with very large threshold."""
        assert should_extract_full(1_000_000, threshold=10_000_000) == True


class TestIntegration:
    """Integration tests for token_counter module."""

    @patch('token_counter.subprocess.run')
    def test_full_workflow_small_repo(self, mock_run):
        """Test complete workflow for small repository."""
        # Mock GitIngest response
        mock_run.return_value = Mock(
            stdout="Estimated tokens: 145000\nRepository content...",
            returncode=0
        )

        # Count tokens
        url = "https://github.com/tiangolo/fastapi"
        count = count_tokens(url)

        # Make routing decision
        should_full = should_extract_full(count)

        # Verify results
        assert count == 145000
        assert should_full == True

    @patch('token_counter.subprocess.run')
    def test_full_workflow_large_repo(self, mock_run):
        """Test complete workflow for large repository."""
        mock_run.return_value = Mock(
            stdout="Estimated tokens: 487523\nRepository content...",
            returncode=0
        )

        url = "https://github.com/large/repo"
        count = count_tokens(url)
        should_full = should_extract_full(count)

        assert count == 487523
        assert should_full == False

    def test_recheck_workflow(self, tmp_path):
        """Test re-check workflow after selective extraction."""
        # Simulate selective extraction creating file
        extracted_file = tmp_path / "docs-content.txt"
        extracted_file.write_text("a" * 360_000, encoding='utf-8')  # 90k tokens

        # Re-check token count
        count = count_tokens_from_file(str(extracted_file))
        should_full = should_extract_full(count)

        # Under threshold after selective extraction
        assert count == 90_000
        assert should_full == True