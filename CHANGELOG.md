# Changelog

All notable changes to GitIngest Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-location output capability with StorageManager (Phase 1.5)
- `--output-dir` option for custom output directory specification
- Automatic detection of project type (gitingest-agent-project vs. other directories)
- Universal `context/related-repos/` output location for non-project directories
- StorageManager class for dynamic path resolution

### Changed
- Storage layer refactored to use StorageManager abstraction
- CLI commands enhanced with output directory configuration (check-size, extract-full)
- Updated storage.py to integrate with new StorageManager architecture

## [1.0.0] - 2025-10-03

### Added
- Initial release with core GitIngest Agent functionality
- CLI framework with check-size, extract-full, extract-tree, extract-specific commands
- Token-based routing for large repositories (200k token threshold)
- Analysis generation with multiple types (installation, workflow, architecture, custom)
- Local storage in data/ and analyze/ directories
- Repository extraction using gitingest
- Automatic repository size checking and routing decisions
- Interactive content selection for large repositories
- Comprehensive test suite
