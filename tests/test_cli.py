"""Tests for CLI framework and commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from cli import gitingest_agent, check_size
from exceptions import GitIngestError, ValidationError


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