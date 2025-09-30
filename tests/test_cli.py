"""Tests for CLI framework and commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from cli import gitingest_agent, check_size, extract_full, extract_tree, extract_specific
from exceptions import GitIngestError, ValidationError, StorageError


class TestCheckSizeCommand:
    """Test check-size command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_check_size_command_under_threshold(self):
        """Test check-size with repository under 200k tokens."""
        with patch('cli.count_tokens', return_value=145_000):
            with patch('cli.format_token_count', return_value='145,000 tokens'):
                result = self.runner.invoke(check_size, ['https://github.com/user/repo'])

                assert result.exit_code == 0
                assert "Checking repository size..." in result.output
                assert "Token count: 145,000 tokens" in result.output
                assert "Route: full extraction" in result.output

    def test_check_size_command_over_threshold(self):
        """Test check-size with repository over 200k tokens."""
        with patch('cli.count_tokens', return_value=487_523):
            with patch('cli.format_token_count', return_value='487,523 tokens'):
                result = self.runner.invoke(check_size, ['https://github.com/fastapi/fastapi'])

                assert result.exit_code == 0
                assert "Checking repository size..." in result.output
                assert "Token count: 487,523 tokens" in result.output
                assert "Route: selective extraction" in result.output

    def test_check_size_command_at_threshold(self):
        """Test check-size with repository exactly at 200k tokens."""
        with patch('cli.count_tokens', return_value=200_000):
            with patch('cli.format_token_count', return_value='200,000 tokens'):
                result = self.runner.invoke(check_size, ['https://github.com/user/repo'])

                assert result.exit_code == 0
                assert "200,000 tokens" in result.output
                assert "Route: selective extraction" in result.output

    def test_check_size_invalid_url(self):
        """Test check-size with invalid GitHub URL."""
        with patch('cli.count_tokens', side_effect=ValidationError("Invalid GitHub URL format")):
            result = self.runner.invoke(check_size, ['https://invalid-url'])

            assert result.exit_code == 1
            assert "❌ Invalid URL:" in result.output
            assert "Invalid GitHub URL format" in result.output

    def test_check_size_network_error(self):
        """Test check-size with network error."""
        with patch('cli.count_tokens', side_effect=GitIngestError("Network error: Connection timeout")):
            result = self.runner.invoke(check_size, ['https://github.com/user/repo'])

            assert result.exit_code == 1
            assert "❌ Error:" in result.output
            assert "Network error: Connection timeout" in result.output

    def test_check_size_gitingest_timeout(self):
        """Test check-size with GitIngest timeout error."""
        with patch('cli.count_tokens', side_effect=GitIngestError("GitIngest request timed out")):
            result = self.runner.invoke(check_size, ['https://github.com/huge/repo'])

            assert result.exit_code == 1
            assert "❌ Error:" in result.output
            assert "GitIngest request timed out" in result.output

    def test_check_size_missing_url(self):
        """Test check-size without URL argument."""
        result = self.runner.invoke(check_size, [])

        assert result.exit_code == 2  # Click error code for missing argument
        assert "Missing argument" in result.output

    def test_check_size_help(self):
        """Test check-size command help output."""
        result = self.runner.invoke(check_size, ['--help'])

        assert result.exit_code == 0
        assert "Check token count and determine extraction strategy" in result.output
        assert "URL" in result.output


class TestGitingestAgentGroup:
    """Test parent command group."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_gitingest_agent_help(self):
        """Test parent command help output."""
        result = self.runner.invoke(gitingest_agent, ['--help'])

        assert result.exit_code == 0
        assert "GitIngest Agent" in result.output
        assert "Automated GitHub repository analysis" in result.output
        assert "check-size" in result.output

    def test_gitingest_agent_no_command(self):
        """Test parent command without subcommand shows usage."""
        result = self.runner.invoke(gitingest_agent, [])

        # Click returns exit code 0 when group is invoked without command (shows help)
        # If no help is auto-shown, it may return exit code 0 with usage info
        assert result.exit_code in [0, 2]
        # Should show usage or commands when no command provided
        assert "Usage:" in result.output or "Commands:" in result.output or "GitIngest Agent" in result.output


class TestCLIIntegration:
    """Integration tests for CLI."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_check_size_full_flow_small_repo(self):
        """Test complete flow for small repository."""
        with patch('cli.count_tokens', return_value=50_000):
            with patch('cli.format_token_count', return_value='50,000 tokens'):
                result = self.runner.invoke(
                    gitingest_agent,
                    ['check-size', 'https://github.com/octocat/Hello-World']
                )

                assert result.exit_code == 0
                assert "50,000 tokens" in result.output
                assert "full extraction" in result.output

    def test_check_size_full_flow_large_repo(self):
        """Test complete flow for large repository."""
        with patch('cli.count_tokens', return_value=750_000):
            with patch('cli.format_token_count', return_value='750,000 tokens'):
                result = self.runner.invoke(
                    gitingest_agent,
                    ['check-size', 'https://github.com/torvalds/linux']
                )

                assert result.exit_code == 0
                assert "750,000 tokens" in result.output
                assert "selective extraction" in result.output

    def test_check_size_full_flow_error(self):
        """Test complete flow with error."""
        with patch('cli.count_tokens', side_effect=ValidationError("Repository not found")):
            result = self.runner.invoke(
                gitingest_agent,
                ['check-size', 'https://github.com/nonexistent/repo']
            )

            assert result.exit_code == 1
            assert "❌ Invalid URL:" in result.output
            assert "Repository not found" in result.output


class TestExtractFullCommand:
    """Test extract-full command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_extract_full_command_success(self):
        """Test successful full extraction."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_full', return_value='/path/to/data/test-repo/digest.txt'):
                with patch('cli.count_tokens_from_file', return_value=145_000):
                    with patch('cli.format_token_count', return_value='145,000 tokens'):
                        result = self.runner.invoke(extract_full, ['https://github.com/user/test-repo'])

                        assert result.exit_code == 0
                        assert "Extracting full repository..." in result.output
                        assert "✓ Saved to:" in result.output
                        assert "/path/to/data/test-repo/digest.txt" in result.output
                        assert "Token count: 145,000 tokens" in result.output

    def test_extract_full_displays_output_path(self):
        """Test that output path is displayed."""
        with patch('cli.parse_repo_name', return_value='Hello-World'):
            with patch('cli.extractor.extract_full', return_value='/absolute/path/data/Hello-World/digest.txt'):
                with patch('cli.count_tokens_from_file', return_value=8_500):
                    with patch('cli.format_token_count', return_value='8,500 tokens'):
                        result = self.runner.invoke(extract_full, ['https://github.com/octocat/Hello-World'])

                        assert result.exit_code == 0
                        assert "/absolute/path/data/Hello-World/digest.txt" in result.output

    def test_extract_full_gitingest_error(self):
        """Test error handling for GitIngest failure."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_full', side_effect=GitIngestError("Repository not found")):
                result = self.runner.invoke(extract_full, ['https://github.com/user/notfound'])

                assert result.exit_code == 1
                assert "❌ Extraction failed:" in result.output
                assert "Repository not found" in result.output

    def test_extract_full_storage_error(self):
        """Test error handling for storage failure."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_full', side_effect=StorageError("Permission denied")):
                result = self.runner.invoke(extract_full, ['https://github.com/user/repo'])

                assert result.exit_code == 1
                assert "❌ Storage error:" in result.output
                assert "Permission denied" in result.output

    def test_extract_full_validation_error(self):
        """Test error handling for invalid URL."""
        with patch('cli.parse_repo_name', side_effect=ValidationError("Invalid GitHub URL format")):
            result = self.runner.invoke(extract_full, ['https://invalid-url'])

            assert result.exit_code == 1
            assert "❌ Invalid URL:" in result.output

    def test_extract_full_missing_url(self):
        """Test extract-full without URL argument."""
        result = self.runner.invoke(extract_full, [])

        assert result.exit_code == 2
        assert "Missing argument" in result.output

    def test_extract_full_help(self):
        """Test extract-full command help output."""
        result = self.runner.invoke(extract_full, ['--help'])

        assert result.exit_code == 0
        assert "Extract entire repository" in result.output
        assert "URL" in result.output


class TestExtractTreeCommand:
    """Test extract-tree command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_extract_tree_command_success(self):
        """Test successful tree extraction."""
        tree_content = "README.md\nsrc/\n  main.py\n  utils.py\ndocs/"
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_tree', return_value=('/path/to/data/test-repo/tree.txt', tree_content)):
                result = self.runner.invoke(extract_tree, ['https://github.com/user/test-repo'])

                assert result.exit_code == 0
                assert "Extracting tree structure..." in result.output
                assert "Repository structure:" in result.output
                assert "README.md" in result.output
                assert "src/" in result.output
                assert "✓ Saved to:" in result.output
                assert "/path/to/data/test-repo/tree.txt" in result.output

    def test_extract_tree_displays_tree_content(self):
        """Test that tree content is displayed to user."""
        tree_content = "setup.py\nfastapi/\n  __init__.py\n  routing.py"
        with patch('cli.parse_repo_name', return_value='fastapi'):
            with patch('cli.extractor.extract_tree', return_value=('/path/tree.txt', tree_content)):
                result = self.runner.invoke(extract_tree, ['https://github.com/fastapi/fastapi'])

                assert result.exit_code == 0
                assert "setup.py" in result.output
                assert "fastapi/" in result.output
                assert "__init__.py" in result.output

    def test_extract_tree_gitingest_error(self):
        """Test error handling for GitIngest failure."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_tree', side_effect=GitIngestError("Connection timeout")):
                result = self.runner.invoke(extract_tree, ['https://github.com/user/repo'])

                assert result.exit_code == 1
                assert "❌ Extraction failed:" in result.output
                assert "Connection timeout" in result.output

    def test_extract_tree_storage_error(self):
        """Test error handling for storage failure."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_tree', side_effect=StorageError("Cannot create directory")):
                result = self.runner.invoke(extract_tree, ['https://github.com/user/repo'])

                assert result.exit_code == 1
                assert "❌ Storage error:" in result.output

    def test_extract_tree_help(self):
        """Test extract-tree command help output."""
        result = self.runner.invoke(extract_tree, ['--help'])

        assert result.exit_code == 0
        assert "Extract repository tree structure" in result.output


class TestExtractSpecificCommand:
    """Test extract-specific command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_extract_specific_docs_type(self):
        """Test selective extraction with docs type."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', return_value='/path/to/data/test-repo/docs-content.txt'):
                with patch('cli.count_tokens_from_file', return_value=89_450):
                    with patch('cli.format_token_count', return_value='89,450 tokens'):
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'docs']
                        )

                        assert result.exit_code == 0
                        assert "Extracting docs content..." in result.output
                        assert "✓ Saved to:" in result.output
                        assert "Token count: 89,450 tokens" in result.output

    def test_extract_specific_installation_type(self):
        """Test selective extraction with installation type."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', return_value='/path/installation-content.txt'):
                with patch('cli.count_tokens_from_file', return_value=12_000):
                    with patch('cli.format_token_count', return_value='12,000 tokens'):
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'installation']
                        )

                        assert result.exit_code == 0
                        assert "Extracting installation content..." in result.output

    def test_extract_specific_code_type(self):
        """Test selective extraction with code type."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', return_value='/path/code-content.txt'):
                with patch('cli.count_tokens_from_file', return_value=156_000):
                    with patch('cli.format_token_count', return_value='156,000 tokens'):
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'code']
                        )

                        assert result.exit_code == 0
                        assert "Extracting code content..." in result.output

    def test_extract_specific_auto_type(self):
        """Test selective extraction with auto type."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', return_value='/path/auto-content.txt'):
                with patch('cli.count_tokens_from_file', return_value=45_000):
                    with patch('cli.format_token_count', return_value='45,000 tokens'):
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'auto']
                        )

                        assert result.exit_code == 0
                        assert "Extracting auto content..." in result.output

    def test_extract_specific_missing_type_option(self):
        """Test error when --type option is missing."""
        result = self.runner.invoke(extract_specific, ['https://github.com/user/repo'])

        assert result.exit_code == 2
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_extract_specific_invalid_type_value(self):
        """Test error with invalid content type."""
        result = self.runner.invoke(
            extract_specific,
            ['https://github.com/user/repo', '--type', 'invalid']
        )

        assert result.exit_code == 2
        assert "Invalid value" in result.output or "choice" in result.output.lower()

    def test_extract_specific_gitingest_error(self):
        """Test error handling for GitIngest failure."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', side_effect=GitIngestError("Rate limit exceeded")):
                result = self.runner.invoke(
                    extract_specific,
                    ['https://github.com/user/repo', '--type', 'docs']
                )

                assert result.exit_code == 1
                assert "❌ Extraction failed:" in result.output

    def test_extract_specific_storage_error(self):
        """Test error handling for storage failure."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', side_effect=StorageError("Disk full")):
                result = self.runner.invoke(
                    extract_specific,
                    ['https://github.com/user/repo', '--type', 'docs']
                )

                assert result.exit_code == 1
                assert "❌ Storage error:" in result.output

    def test_extract_specific_help(self):
        """Test extract-specific command help output."""
        result = self.runner.invoke(extract_specific, ['--help'])

        assert result.exit_code == 0
        assert "Extract specific content" in result.output
        assert "--type" in result.output
        assert "docs" in result.output or "installation" in result.output


class TestTokenOverflowPrevention:
    """Test token overflow prevention and re-check logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_extract_specific_under_threshold_no_prompt(self):
        """Test no prompting when content is under 200k tokens."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', return_value='/path/installation-content.txt'):
                with patch('cli.count_tokens_from_file', return_value=12_450):
                    with patch('cli.format_token_count', return_value='12,450 tokens'):
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'installation']
                        )

                        assert result.exit_code == 0
                        assert "Token count: 12,450 tokens" in result.output
                        assert "Content exceeds" not in result.output
                        assert "Options:" not in result.output

    def test_extract_specific_overflow_detected_proceed(self):
        """Test overflow warning displayed when content exceeds 200k and user proceeds."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', return_value='/path/docs-content.txt'):
                with patch('cli.count_tokens_from_file', return_value=287_523):
                    with patch('cli.format_token_count', return_value='287,523 tokens'):
                        # Simulate user choosing to proceed (option 2)
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'docs'],
                            input='2\n'
                        )

                        assert result.exit_code == 0
                        assert "Content exceeds token limit" in result.output
                        assert "287,523 tokens" in result.output
                        assert "Target: 200,000 tokens" in result.output
                        assert "Overflow:" in result.output
                        assert "87,523 tokens" in result.output
                        assert "Options:" in result.output
                        assert "1) Narrow selection further" in result.output
                        assert "2) Proceed with partial content" in result.output
                        assert "Warning: Proceeding with content exceeding token limit" in result.output

    def test_extract_specific_overflow_narrow_once(self):
        """Test iterative refinement with one narrowing iteration."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific') as mock_extract:
                # First extraction: overflow, second extraction: success
                mock_extract.side_effect = [
                    '/path/docs-content.txt',
                    '/path/installation-content.txt'
                ]

                with patch('cli.count_tokens_from_file') as mock_count:
                    with patch('cli.format_token_count') as mock_format:
                        # First check: overflow, second check: under threshold
                        mock_count.side_effect = [287_523, 12_450]
                        mock_format.side_effect = ['287,523 tokens', '12,450 tokens']

                        # User input: 1 (narrow), then 'installation' as new type
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'docs'],
                            input='1\ninstallation\n'
                        )

                        assert result.exit_code == 0
                        assert "Content exceeds token limit" in result.output
                        assert "Narrow selection further" in result.output
                        assert "Extracting installation content" in result.output
                        assert "12,450 tokens" in result.output
                        assert mock_extract.call_count == 2

    def test_extract_specific_overflow_narrow_multiple_times(self):
        """Test iterative refinement with multiple narrowing iterations."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific') as mock_extract:
                # Three extractions: docs (overflow), code (still overflow), installation (success)
                mock_extract.side_effect = [
                    '/path/docs-content.txt',
                    '/path/code-content.txt',
                    '/path/installation-content.txt'
                ]

                with patch('cli.count_tokens_from_file') as mock_count:
                    with patch('cli.format_token_count') as mock_format:
                        # Three checks: overflow, overflow, success
                        mock_count.side_effect = [287_523, 215_000, 8_500]
                        mock_format.side_effect = ['287,523 tokens', '215,000 tokens', '8,500 tokens']

                        # User input: 1 (narrow) -> code, 1 (narrow again) -> installation
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'docs'],
                            input='1\ncode\n1\ninstallation\n'
                        )

                        assert result.exit_code == 0
                        assert "Content exceeds token limit" in result.output
                        assert "Extracting code content" in result.output
                        assert "Extracting installation content" in result.output
                        assert "8,500 tokens" in result.output
                        assert mock_extract.call_count == 3

    def test_extract_specific_at_threshold_no_prompt(self):
        """Test exact threshold (200k) does not trigger overflow warning."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', return_value='/path/docs-content.txt'):
                with patch('cli.count_tokens_from_file', return_value=199_999):
                    with patch('cli.format_token_count', return_value='199,999 tokens'):
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'docs']
                        )

                        assert result.exit_code == 0
                        assert "199,999 tokens" in result.output
                        assert "Content exceeds" not in result.output

    def test_extract_specific_just_over_threshold(self):
        """Test just over threshold (200k) triggers overflow warning."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', return_value='/path/docs-content.txt'):
                with patch('cli.count_tokens_from_file', return_value=200_001):
                    with patch('cli.format_token_count', return_value='200,001 tokens'):
                        # User chooses to proceed
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'docs'],
                            input='2\n'
                        )

                        assert result.exit_code == 0
                        assert "Content exceeds token limit" in result.output
                        assert "Overflow: 1 tokens" in result.output

    def test_extract_specific_overflow_invalid_choice_then_proceed(self):
        """Test handling invalid user choice, then proceeding."""
        with patch('cli.parse_repo_name', return_value='test-repo'):
            with patch('cli.extractor.extract_specific', return_value='/path/docs-content.txt'):
                with patch('cli.count_tokens_from_file', return_value=250_000):
                    with patch('cli.format_token_count', return_value='250,000 tokens'):
                        # User input: invalid choice (3), then valid (2)
                        result = self.runner.invoke(
                            extract_specific,
                            ['https://github.com/user/repo', '--type', 'docs'],
                            input='3\n2\n'
                        )

                        assert result.exit_code == 0
                        assert "Content exceeds token limit" in result.output