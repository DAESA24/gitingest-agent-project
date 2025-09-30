"""
Custom exception hierarchy for GitIngest Agent.

This module defines all application-specific exceptions used across the codebase.
All exceptions inherit from GitIngestAgentError for consistent error handling.
"""


class GitIngestAgentError(Exception):
    """
    Base exception for all GitIngest Agent errors.

    Use this to catch any application-specific error:
        try:
            # some operation
        except GitIngestAgentError as e:
            # handle any application error
    """
    pass


class GitIngestError(GitIngestAgentError):
    """
    Raised when GitIngest CLI execution fails.

    Common causes:
    - Network errors
    - Invalid repository URLs
    - Repository not found (404)
    - Authentication failures for private repositories
    - GitIngest CLI timeout

    Example:
        raise GitIngestError(f"Repository not found: {url}")
    """
    pass


class ValidationError(GitIngestAgentError):
    """
    Raised when input validation fails.

    Common causes:
    - Invalid GitHub URL format
    - Invalid content type selection
    - Malformed path patterns

    Example:
        raise ValidationError(f"Invalid GitHub URL: {url}")
    """
    pass


class StorageError(GitIngestAgentError):
    """
    Raised when file system operations fail.

    Common causes:
    - Permission denied when creating directories
    - Disk full when writing files
    - Invalid path characters
    - File already exists (when not expected)

    Example:
        raise StorageError(f"Cannot create directory: {path}")
    """
    pass


class WorkflowError(GitIngestAgentError):
    """
    Raised when workflow logic encounters unexpected state.

    Common causes:
    - Invalid routing decision
    - Missing required context variables
    - Configuration errors
    - Unexpected workflow state transitions

    Example:
        raise WorkflowError("Token count unavailable for routing decision")
    """
    pass