"""
Unit tests for workflow module.

Tests cover:
- GitHub URL validation and parsing
- Token count formatting
- Content type filter mapping
- Edge cases and error handling
"""

import pytest
from exceptions import ValidationError
from workflow import (
    validate_github_url,
    format_token_count,
    get_filters_for_type,
    FILTER_PATTERNS,
)


class TestValidateGithubUrl:
    """Tests for validate_github_url() function."""

    def test_validate_github_url_valid_https(self):
        """Test URL validation with standard HTTPS GitHub URL."""
        owner, repo = validate_github_url("https://github.com/tiangolo/fastapi")
        assert owner == "tiangolo"
        assert repo == "fastapi"

    def test_validate_github_url_valid_http(self):
        """Test URL validation with HTTP protocol."""
        owner, repo = validate_github_url("http://github.com/pallets/click")
        assert owner == "pallets"
        assert repo == "click"

    def test_validate_github_url_with_trailing_slash(self):
        """Test handling of trailing slash."""
        owner, repo = validate_github_url("https://github.com/user/repo/")
        assert owner == "user"
        assert repo == "repo"

    def test_validate_github_url_with_git_suffix(self):
        """Test handling of .git suffix."""
        owner, repo = validate_github_url("https://github.com/user/repo.git")
        assert owner == "user"
        assert repo == "repo"

    def test_validate_github_url_with_trailing_slash_and_git(self):
        """Test handling both trailing slash and .git suffix."""
        owner, repo = validate_github_url("https://github.com/user/repo.git/")
        assert owner == "user"
        assert repo == "repo"

    def test_validate_github_url_with_hyphens(self):
        """Test owner/repo names with hyphens."""
        owner, repo = validate_github_url("https://github.com/my-org/my-repo")
        assert owner == "my-org"
        assert repo == "my-repo"

    def test_validate_github_url_with_underscores(self):
        """Test owner/repo names with underscores."""
        owner, repo = validate_github_url("https://github.com/my_org/my_repo")
        assert owner == "my_org"
        assert repo == "my_repo"

    def test_validate_github_url_with_numbers(self):
        """Test owner/repo names with numbers."""
        owner, repo = validate_github_url("https://github.com/user123/repo456")
        assert owner == "user123"
        assert repo == "repo456"

    def test_validate_github_url_invalid_empty(self):
        """Test ValidationError raised for empty URL."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("")
        assert "non-empty string" in str(exc_info.value)

    def test_validate_github_url_invalid_none(self):
        """Test ValidationError raised for None URL."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url(None)
        assert "non-empty string" in str(exc_info.value)

    def test_validate_github_url_invalid_format(self):
        """Test ValidationError raised for invalid URL format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("not-a-url")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_validate_github_url_non_github_domain(self):
        """Test ValidationError for non-GitHub URLs."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://gitlab.com/user/repo")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_validate_github_url_missing_repo(self):
        """Test ValidationError for URL without repository name."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/user")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_validate_github_url_missing_owner(self):
        """Test ValidationError for URL without owner."""
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_validate_github_url_extra_path_components(self):
        """Test URL with extra path components (e.g., /tree/main)."""
        # Note: regex.match() only matches from start, so extra paths cause no match
        # The URL doesn't match the pattern because it has extra components
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/user/repo/tree/main")
        assert "Invalid GitHub URL format" in str(exc_info.value)

    def test_validate_github_url_special_characters(self):
        """Test ValidationError for special characters in owner/repo."""
        # Regex only allows \w (alphanumeric + underscore) and hyphens
        with pytest.raises(ValidationError) as exc_info:
            validate_github_url("https://github.com/user@org/repo")
        assert "Invalid GitHub URL format" in str(exc_info.value)


class TestFormatTokenCount:
    """Tests for format_token_count() function."""

    def test_format_token_count_small(self):
        """Test formatting of small token counts."""
        assert format_token_count(999) == "999 tokens"
        assert format_token_count(100) == "100 tokens"
        assert format_token_count(1) == "1 tokens"

    def test_format_token_count_thousands(self):
        """Test formatting with thousand separators."""
        assert format_token_count(1000) == "1,000 tokens"
        assert format_token_count(145000) == "145,000 tokens"
        assert format_token_count(999999) == "999,999 tokens"

    def test_format_token_count_millions(self):
        """Test formatting of large token counts."""
        assert format_token_count(1000000) == "1,000,000 tokens"
        assert format_token_count(1234567) == "1,234,567 tokens"

    def test_format_token_count_zero(self):
        """Test formatting of zero tokens."""
        assert format_token_count(0) == "0 tokens"

    def test_format_token_count_threshold(self):
        """Test formatting around the 200k threshold."""
        assert format_token_count(200000) == "200,000 tokens"
        assert format_token_count(199999) == "199,999 tokens"
        assert format_token_count(200001) == "200,001 tokens"


class TestGetFiltersForType:
    """Tests for get_filters_for_type() function."""

    def test_get_filters_for_type_docs(self):
        """Test filter patterns for docs type."""
        filters = get_filters_for_type('docs')

        assert 'include' in filters
        assert 'exclude' in filters
        assert isinstance(filters['include'], list)
        assert isinstance(filters['exclude'], list)

        # Check specific patterns
        assert 'docs/**/*' in filters['include']
        assert '*.md' in filters['include']
        assert 'README*' in filters['include']
        assert '*.rst' in filters['include']
        assert 'docs/examples/*' in filters['exclude']
        assert 'docs/archive/*' in filters['exclude']

    def test_get_filters_for_type_installation(self):
        """Test filter patterns for installation type."""
        filters = get_filters_for_type('installation')

        assert 'include' in filters
        assert 'exclude' in filters

        # Check specific patterns
        assert 'README*' in filters['include']
        assert 'INSTALL*' in filters['include']
        assert 'setup.py' in filters['include']
        assert 'pyproject.toml' in filters['include']
        assert 'package.json' in filters['include']
        assert 'docs/installation*' in filters['include']
        assert 'docs/getting-started*' in filters['include']
        assert filters['exclude'] == []  # No exclusions for installation

    def test_get_filters_for_type_code(self):
        """Test filter patterns for code type."""
        filters = get_filters_for_type('code')

        assert 'include' in filters
        assert 'exclude' in filters

        # Check specific patterns
        assert 'src/**/*.py' in filters['include']
        assert 'lib/**/*.py' in filters['include']
        assert 'tests/*' in filters['exclude']
        assert '*_test.py' in filters['exclude']
        assert 'test_*.py' in filters['exclude']
        assert 'examples/*' in filters['exclude']

    def test_get_filters_for_type_auto(self):
        """Test filter patterns for auto type."""
        filters = get_filters_for_type('auto')

        assert 'include' in filters
        assert 'exclude' in filters

        # Check specific patterns
        assert 'README*' in filters['include']
        assert 'docs/**/*.md' in filters['include']
        assert 'docs/examples/*' in filters['exclude']
        assert 'docs/archive/*' in filters['exclude']

    def test_get_filters_for_type_invalid(self):
        """Test ValidationError for invalid content type."""
        with pytest.raises(ValidationError) as exc_info:
            get_filters_for_type('invalid-type')

        error_msg = str(exc_info.value)
        assert "Invalid content type: invalid-type" in error_msg
        assert "Valid types:" in error_msg
        # Check all valid types mentioned
        assert "docs" in error_msg
        assert "installation" in error_msg
        assert "code" in error_msg
        assert "auto" in error_msg

    def test_get_filters_for_type_case_sensitive(self):
        """Test content type is case-sensitive."""
        with pytest.raises(ValidationError):
            get_filters_for_type('DOCS')  # uppercase should fail

        with pytest.raises(ValidationError):
            get_filters_for_type('Docs')  # title case should fail

    def test_get_filters_for_type_returns_copy(self):
        """Test function returns the actual dictionary (not a copy in this impl)."""
        filters1 = get_filters_for_type('docs')
        filters2 = get_filters_for_type('docs')

        # Both should have same content
        assert filters1 == filters2
        # In this implementation, they reference the same dict (optimization)
        assert filters1 is filters2


class TestFilterPatternsStructure:
    """Tests for FILTER_PATTERNS constant structure."""

    def test_filter_patterns_all_types_present(self):
        """Test all expected content types are in FILTER_PATTERNS."""
        expected_types = ['docs', 'installation', 'code', 'auto']
        for content_type in expected_types:
            assert content_type in FILTER_PATTERNS

    def test_filter_patterns_all_have_include_exclude(self):
        """Test all filter patterns have include/exclude keys."""
        for content_type, patterns in FILTER_PATTERNS.items():
            assert 'include' in patterns, f"{content_type} missing 'include'"
            assert 'exclude' in patterns, f"{content_type} missing 'exclude'"
            assert isinstance(patterns['include'], list)
            assert isinstance(patterns['exclude'], list)

    def test_filter_patterns_include_not_empty(self):
        """Test all filter patterns have at least one include pattern."""
        for content_type, patterns in FILTER_PATTERNS.items():
            assert len(patterns['include']) > 0, f"{content_type} has no include patterns"

    def test_filter_patterns_installation_no_exclude(self):
        """Test installation type has no exclusions (by design)."""
        assert FILTER_PATTERNS['installation']['exclude'] == []


class TestIntegration:
    """Integration tests for workflow module."""

    def test_full_workflow_url_to_filters(self):
        """Test complete workflow: URL validation + filter selection."""
        # Validate URL
        owner, repo = validate_github_url("https://github.com/tiangolo/fastapi")

        # Get filters for docs
        filters = get_filters_for_type('docs')

        # Format token count
        formatted = format_token_count(145000)

        # Verify results
        assert owner == "tiangolo"
        assert repo == "fastapi"
        assert '*.md' in filters['include']
        assert formatted == "145,000 tokens"

    def test_all_content_types_accessible(self):
        """Test all content types can be retrieved without errors."""
        for content_type in ['docs', 'installation', 'code', 'auto']:
            filters = get_filters_for_type(content_type)
            assert 'include' in filters
            assert 'exclude' in filters