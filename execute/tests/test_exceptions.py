"""
Unit tests for custom exception classes.

Tests verify:
- Exception instantiation with messages
- Inheritance hierarchy
- Exception raising and catching
- Base exception can catch all specialized exceptions
"""

import pytest
from exceptions import (
    GitIngestAgentError,
    GitIngestError,
    ValidationError,
    StorageError,
    WorkflowError,
)


class TestBaseException:
    """Tests for GitIngestAgentError base exception."""

    def test_base_exception_instantiation(self):
        """Test GitIngestAgentError can be created with message."""
        error = GitIngestAgentError("Test error message")
        assert str(error) == "Test error message"

    def test_base_exception_can_be_raised(self):
        """Test GitIngestAgentError can be raised and caught."""
        with pytest.raises(GitIngestAgentError) as exc_info:
            raise GitIngestAgentError("Base error")
        assert "Base error" in str(exc_info.value)

    def test_base_exception_inherits_from_exception(self):
        """Test GitIngestAgentError inherits from built-in Exception."""
        error = GitIngestAgentError("Test")
        assert isinstance(error, Exception)


class TestGitIngestError:
    """Tests for GitIngestError exception."""

    def test_git_ingest_error_inheritance(self):
        """Test GitIngestError inherits from GitIngestAgentError."""
        error = GitIngestError("GitIngest failed")
        assert isinstance(error, GitIngestAgentError)
        assert isinstance(error, GitIngestError)

    def test_git_ingest_error_message_preserved(self):
        """Test GitIngestError preserves error message."""
        message = "Repository not found: https://github.com/invalid/repo"
        error = GitIngestError(message)
        assert str(error) == message

    def test_git_ingest_error_can_be_caught(self):
        """Test GitIngestError can be raised and caught."""
        with pytest.raises(GitIngestError) as exc_info:
            raise GitIngestError("Network timeout")
        assert "Network timeout" in str(exc_info.value)


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from GitIngestAgentError."""
        error = ValidationError("Invalid URL")
        assert isinstance(error, GitIngestAgentError)
        assert isinstance(error, ValidationError)

    def test_validation_error_message_preserved(self):
        """Test ValidationError preserves error message."""
        message = "Invalid GitHub URL: not-a-url"
        error = ValidationError(message)
        assert str(error) == message

    def test_validation_error_can_be_caught(self):
        """Test ValidationError can be raised and caught."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Invalid content type")
        assert "Invalid content type" in str(exc_info.value)


class TestStorageError:
    """Tests for StorageError exception."""

    def test_storage_error_inheritance(self):
        """Test StorageError inherits from GitIngestAgentError."""
        error = StorageError("Permission denied")
        assert isinstance(error, GitIngestAgentError)
        assert isinstance(error, StorageError)

    def test_storage_error_message_preserved(self):
        """Test StorageError preserves error message."""
        message = "Cannot create directory: /protected/path"
        error = StorageError(message)
        assert str(error) == message

    def test_storage_error_can_be_caught(self):
        """Test StorageError can be raised and caught."""
        with pytest.raises(StorageError) as exc_info:
            raise StorageError("Disk full")
        assert "Disk full" in str(exc_info.value)


class TestWorkflowError:
    """Tests for WorkflowError exception."""

    def test_workflow_error_inheritance(self):
        """Test WorkflowError inherits from GitIngestAgentError."""
        error = WorkflowError("Invalid state")
        assert isinstance(error, GitIngestAgentError)
        assert isinstance(error, WorkflowError)

    def test_workflow_error_message_preserved(self):
        """Test WorkflowError preserves error message."""
        message = "Token count unavailable for routing decision"
        error = WorkflowError(message)
        assert str(error) == message

    def test_workflow_error_can_be_caught(self):
        """Test WorkflowError can be raised and caught."""
        with pytest.raises(WorkflowError) as exc_info:
            raise WorkflowError("Configuration error")
        assert "Configuration error" in str(exc_info.value)


class TestExceptionHierarchy:
    """Tests for exception hierarchy and polymorphism."""

    def test_catch_base_catches_all_specialized(self):
        """Test catching GitIngestAgentError catches all specialized exceptions."""
        exceptions_to_test = [
            GitIngestError("GitIngest failed"),
            ValidationError("Invalid input"),
            StorageError("File error"),
            WorkflowError("Logic error"),
        ]

        for error in exceptions_to_test:
            with pytest.raises(GitIngestAgentError):
                raise error

    def test_specialized_exceptions_distinct(self):
        """Test specialized exceptions are distinct types."""
        git_error = GitIngestError("Git error")
        validation_error = ValidationError("Validation error")

        assert isinstance(git_error, GitIngestError)
        assert not isinstance(git_error, ValidationError)
        assert isinstance(validation_error, ValidationError)
        assert not isinstance(validation_error, GitIngestError)

    def test_exception_isinstance_checks(self):
        """Test isinstance checks work correctly for exception hierarchy."""
        error = GitIngestError("Test")

        # Should match base class
        assert isinstance(error, GitIngestAgentError)
        # Should match specific class
        assert isinstance(error, GitIngestError)
        # Should match built-in Exception
        assert isinstance(error, Exception)
        # Should not match sibling classes
        assert not isinstance(error, ValidationError)
        assert not isinstance(error, StorageError)
        assert not isinstance(error, WorkflowError)


class TestExceptionUsagePatterns:
    """Tests for common exception usage patterns."""

    def test_exception_with_empty_message(self):
        """Test exceptions work with empty messages."""
        error = GitIngestAgentError()
        assert isinstance(error, GitIngestAgentError)

    def test_exception_with_multiline_message(self):
        """Test exceptions preserve multiline messages."""
        message = "Error occurred:\n  Line 1\n  Line 2"
        error = WorkflowError(message)
        assert str(error) == message

    def test_exception_with_formatted_message(self):
        """Test exceptions work with formatted messages."""
        url = "https://github.com/user/repo"
        error = ValidationError(f"Invalid URL: {url}")
        assert "Invalid URL" in str(error)
        assert url in str(error)

    def test_re_raising_exception(self):
        """Test exceptions can be caught and re-raised."""
        with pytest.raises(GitIngestError):
            try:
                raise GitIngestError("Original error")
            except GitIngestAgentError:
                # Can catch with base class and re-raise
                raise