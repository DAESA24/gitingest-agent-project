# GitIngest Agent

Automated GitHub repository analysis tool using GitIngest CLI and Claude Code.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status: Active](https://img.shields.io/badge/status-active-success.svg)

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [How It Works](#how-it-works)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)
- [Developer Setup](#developer-setup)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Phase Roadmap](#phase-roadmap)

## Installation

### Prerequisites

- **Python 3.12 or higher** - [Download Python](https://www.python.org/downloads/)
- **uv package manager** - [Install uv](https://github.com/astral-sh/uv)
- **GitIngest CLI** - Install with: `uv tool install gitingest`
- **Git** - For cloning the repository

### Install from GitHub

```bash
# Clone the repository
git clone https://github.com/DAESA24/gitingest-agent-project.git
cd gitingest-agent-project/execute

# Sync environment and install dependencies
uv sync

# Install in development mode
uv pip install -e .

# Verify installation
uv run gitingest-agent --help
```

**Note:** This tool is currently distributed via GitHub only. Installation from PyPI will be available in a future release.

## Quick Start

Get started with GitIngest Agent in 3 simple steps:

### 1. Check Repository Size

```bash
# From the execute/ directory
uv run gitingest-agent check-size https://github.com/octocat/Hello-World
```

**Output:**

```text
Checking repository size...
Token count: 47 tokens
Route: full extraction
```

### 2. Extract Repository

```bash
# From the execute/ directory
uv run gitingest-agent extract-full https://github.com/octocat/Hello-World
```

**Output:**

```text
Extracting full repository...
[OK] Saved to: /home/user/my-project/context/related-repos/Hello-World/digest.txt
Token count: 47 tokens
```

### 3. Analyze the Content

The extracted content is saved to:

- **When in gitingest-agent-project**: `data/[repo-name]/digest.txt`
- **When in other directories**: `context/related-repos/[repo-name]/digest.txt`

You can now read and analyze the extracted content with your preferred tool or AI assistant!

## Commands

GitIngest Agent provides four main commands for repository analysis:

### `check-size` - Check Token Count

Check repository token count and determine extraction strategy.

```bash
uv run gitingest-agent check-size <github-url> [--output-dir PATH]
```

**Examples:**

```bash
# Basic usage
uv run gitingest-agent check-size https://github.com/fastapi/fastapi

# With custom output directory
uv run gitingest-agent check-size https://github.com/fastapi/fastapi --output-dir ./my-analyses
```

**Output:**

```text
Checking repository size...
Token count: 487,523 tokens
Route: selective extraction
```

### `extract-full` - Extract Complete Repository

Extract entire repository content (recommended for repos < 200k tokens).

```bash
uv run gitingest-agent extract-full <github-url> [--output-dir PATH]
```

**Examples:**

```bash
# Basic usage
uv run gitingest-agent extract-full https://github.com/octocat/Hello-World

# With custom output directory
uv run gitingest-agent extract-full https://github.com/octocat/Hello-World --output-dir ./my-analyses
```

**Output:**

```text
Extracting full repository...
[OK] Saved to: /home/user/project/context/related-repos/Hello-World/digest.txt
Token count: 47 tokens
```

### `extract-tree` - Extract Repository Structure

Extract repository tree structure without full content (for large repos >= 200k tokens).

```bash
uv run gitingest-agent extract-tree <github-url> [--output-dir PATH]
```

**Examples:**

```bash
# Basic usage
uv run gitingest-agent extract-tree https://github.com/fastapi/fastapi

# With custom output directory
uv run gitingest-agent extract-tree https://github.com/fastapi/fastapi --output-dir ./my-analyses
```

**Output:**

```text
Extracting tree structure...
[OK] Saved to: /home/user/project/context/related-repos/fastapi/tree.txt
Token count: 8,234 tokens

Repository structure:
README.md
fastapi/
  __init__.py
  applications.py
  routing.py
  ...
docs/
  tutorial/
  ...
```

### `extract-specific` - Extract Targeted Content

Extract specific content using filters with automatic overflow prevention.

```bash
uv run gitingest-agent extract-specific <github-url> --type <content-type> [--output-dir PATH]
```

**Content Types:**

- `docs` - Documentation files (*.md, docs/**, README)
- `installation` - Setup files (README, setup.py, package.json, requirements.txt)
- `code` - Source code (src/**/*.py, lib/**/*.py)
- `auto` - Automatic selection (README + key docs)

**Examples:**

```bash
# Extract only documentation
uv run gitingest-agent extract-specific https://github.com/fastapi/fastapi --type docs

# Extract installation files
uv run gitingest-agent extract-specific https://github.com/fastapi/fastapi --type installation

# Extract source code
uv run gitingest-agent extract-specific https://github.com/fastapi/fastapi --type code

# Automatic selection with custom output
uv run gitingest-agent extract-specific https://github.com/fastapi/fastapi --type auto --output-dir ./analyses
```

**Output:**

```text
Extracting specific content (type: docs)...
[OK] Saved to: /home/user/project/context/related-repos/fastapi/docs-content.txt
Token count: 125,430 tokens
```

### Global Option: `--output-dir`

All commands support the `--output-dir` parameter to specify a custom output location:

```bash
# Save to custom directory
uv run gitingest-agent extract-full https://github.com/user/repo --output-dir ./my-custom-folder

# Use absolute path
uv run gitingest-agent extract-full https://github.com/user/repo --output-dir /home/user/analyses
```

**Default Behavior (without --output-dir):**

- **In gitingest-agent-project**: Saves to `data/[repo-name]/`
- **In other directories**: Saves to `context/related-repos/[repo-name]/`

### Get Help

```bash
# Show all commands
uv run gitingest-agent --help

# Get help for specific command
uv run gitingest-agent check-size --help
uv run gitingest-agent extract-full --help
uv run gitingest-agent extract-tree --help
uv run gitingest-agent extract-specific --help
```

## How It Works

GitIngest Agent uses intelligent location detection to determine where to save extracted repository content.

### Phase 1.0: GitIngest Agent Project (Backward Compatible)

When running from the `gitingest-agent-project` directory, the tool uses the original Phase 1.0 behavior:

**Detection Logic:**

- Checks if current directory contains `execute/cli.py` and `execute/main.py`
- OR if current directory is the `execute/` subdirectory itself

**Output Location:** `data/[repo-name]/`

**Example:**

```bash
cd ~/work/dev/gitingest-agent-project/execute
uv run gitingest-agent extract-full https://github.com/octocat/Hello-World

# Creates: ~/work/dev/gitingest-agent-project/data/Hello-World/digest.txt
```

**Folder Structure:**

```text
gitingest-agent-project/
├── execute/
│   ├── cli.py
│   └── main.py
├── data/                          # Phase 1.0 output location
│   └── Hello-World/
│       └── digest.txt
```

### Phase 1.5: Universal Context Convention (NEW in v1.1.0)

When running from ANY other directory (React projects, Vue projects, Node.js apps, etc.), the tool uses Phase 1.5:

**Output Location:** `context/related-repos/[repo-name]/`

**Benefits:**

- **Clear purpose**: "context" folder indicates external reference materials
- **No pollution**: Avoids creating random `data/` folders in your projects
- **Universal standard**: Same convention works across all project types
- **Auto-creation**: Automatically creates `context/` and `related-repos/` if they don't exist

**Example:**

```bash
cd ~/work/dev/my-react-app
uv run ~/work/dev/gitingest-agent-project/execute/gitingest-agent extract-full https://github.com/facebook/react

# Creates: ~/work/dev/my-react-app/context/related-repos/react/digest.txt
```

**Folder Structure:**

```text
my-react-app/
├── src/
├── public/
├── package.json
└── context/                       # Phase 1.5 universal convention
    └── related-repos/
        └── react/
            └── digest.txt
```

### Custom Output Directory Override

You can always override the automatic detection with `--output-dir`:

```bash
# Save to completely custom location
uv run gitingest-agent extract-full https://github.com/user/repo --output-dir ./my-analyses

# Creates: ./my-analyses/digest.txt
```

**Path Validation:**

- Creates directory if it doesn't exist (with confirmation prompt)
- Supports both relative and absolute paths
- Validates write permissions

## Common Use Cases

### Use Case 1: Analyze a Small Repository

For repositories under 200k tokens, use full extraction:

```bash
# Check size first
uv run gitingest-agent check-size https://github.com/octocat/Hello-World
# Output: Token count: 47 tokens
# Route: full extraction

# Extract full content
uv run gitingest-agent extract-full https://github.com/octocat/Hello-World
# Output: [OK] Saved to: /current/directory/context/related-repos/Hello-World/digest.txt
```

**When to use:** READMEs, small utilities, simple examples, config files

### Use Case 2: Analyze a Large Repository

For repositories >= 200k tokens, use selective extraction:

```bash
# Check size first
uv run gitingest-agent check-size https://github.com/fastapi/fastapi
# Output: Token count: 487,523 tokens
# Route: selective extraction

# Extract tree structure to understand layout
uv run gitingest-agent extract-tree https://github.com/fastapi/fastapi

# Extract only what you need
uv run gitingest-agent extract-specific https://github.com/fastapi/fastapi --type installation
# Output: [OK] Saved to: /current/directory/context/related-repos/fastapi/installation-content.txt
```

**When to use:** Large frameworks, complex applications, extensive documentation

### Use Case 3: Custom Output Location

Save analyses to a dedicated folder outside your project:

```bash
# Create dedicated analyses directory
mkdir -p ~/repo-analyses

# Extract to custom location
uv run gitingest-agent extract-full https://github.com/user/repo --output-dir ~/repo-analyses

# Result: ~/repo-analyses/digest.txt
```

**When to use:** Centralized analysis storage, shared team folder, backup location

### Use Case 4: Working in React/Vue/Next.js Projects

Analyze related repositories while working in your frontend project:

```bash
# In your React project
cd ~/work/dev/my-react-app

# Analyze React source for reference
uv run ~/work/dev/gitingest-agent-project/execute/gitingest-agent extract-specific https://github.com/facebook/react --type docs

# Analyze related libraries
uv run ~/work/dev/gitingest-agent-project/execute/gitingest-agent extract-full https://github.com/reduxjs/redux

# All saved to: my-react-app/context/related-repos/
```

**Folder structure:**

```text
my-react-app/
├── src/
├── public/
├── package.json
└── context/
    └── related-repos/
        ├── react/
        │   └── docs-content.txt
        └── redux/
            └── digest.txt
```

**Benefits:**

- Reference materials organized alongside your code
- No pollution of project root
- Easy to .gitignore (add `context/` to `.gitignore`)

## Troubleshooting

### Issue: "gitingest-agent: command not found"

**Cause:** Repository not cloned or not running from execute/ directory.

**Solutions:**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/DAESA24/gitingest-agent-project.git
   cd gitingest-agent-project/execute
   uv sync
   ```

2. **Run from execute/ directory:**

   ```bash
   cd gitingest-agent-project/execute
   uv run gitingest-agent --help
   ```

3. **Use absolute path from anywhere:**

   ```bash
   uv run ~/path/to/gitingest-agent-project/execute/gitingest-agent --help
   ```

### Issue: "Repository not found" errors

**Cause:** Invalid repository URL or repository is private/doesn't exist.

**Solutions:**

1. **Verify the URL format:**

   ```bash
   # Correct format:
   https://github.com/owner/repository

   # Examples:
   https://github.com/facebook/react  ✓
   https://github.com/octocat/Hello-World  ✓

   # Incorrect:
   github.com/owner/repo  ✗
   http://github.com/owner/repo  ✗
   ```

2. **Check repository exists:**

   - Visit the URL in your browser
   - Ensure repository is public (private repos not supported)

3. **Check your internet connection:**

   ```bash
   # Test GitHub connectivity
   curl -I https://github.com
   ```

### Issue: "Invalid GitHub URL format"

**Cause:** URL doesn't match expected GitHub format.

**Solution:**

Ensure URL follows the pattern: `https://github.com/{owner}/{repository}`

```bash
# Correct format
gitingest-agent extract-full https://github.com/octocat/Hello-World

# Incorrect formats (will fail)
gitingest-agent extract-full github.com/octocat/Hello-World
gitingest-agent extract-full www.github.com/octocat/Hello-World
gitingest-agent extract-full https://github.com/octocat
```

### Issue: Token overflow after selective extraction

**Cause:** Even after filtering, extracted content still exceeds 200k token limit.

**Solution:**

Narrow your selection further:

```bash
# If 'docs' is too large, try 'installation' (more specific)
uv run gitingest-agent extract-specific https://github.com/large-repo --type installation

# Or use 'auto' for minimal content (README + key docs)
uv run gitingest-agent extract-specific https://github.com/large-repo --type auto
```

**Overflow Prevention:**

- The tool will warn you if content exceeds limits
- You'll be prompted to narrow selection or proceed with partial content
- Use more specific content types for better control

### Issue: Permission errors creating directories

**Cause:** Insufficient write permissions in target directory.

**Solutions:**

1. **Check directory permissions:**

   ```bash
   # Check current directory permissions
   ls -ld .

   # Ensure you have write access
   ```

2. **Use --output-dir to specify writable location:**

   ```bash
   uv run gitingest-agent extract-full https://github.com/user/repo --output-dir ~/my-analyses
   ```

3. **Create directory manually first:**

   ```bash
   mkdir -p context/related-repos
   chmod 755 context/related-repos
   uv run gitingest-agent extract-full https://github.com/user/repo
   ```

### Issue: Windows UTF-8 encoding errors

**Cause:** GitIngest (external dependency) may fail on Windows with UTF-8 files.

**Symptoms:**

```text
Error reading file with 'cp1252': 'charmap' codec can't decode byte...
```

**Solutions:**

1. **Set Python encoding environment variable:**

   ```bash
   # PowerShell
   $env:PYTHONIOENCODING = "utf-8"
   uv run gitingest-agent extract-full https://github.com/user/repo

   # CMD
   set PYTHONIOENCODING=utf-8
   uv run gitingest-agent extract-full https://github.com/user/repo
   ```

2. **Use WSL (Windows Subsystem for Linux):**

   ```bash
   wsl
   cd gitingest-agent-project/execute
   uv run gitingest-agent extract-full https://github.com/user/repo
   ```

3. **Try selective extraction (fewer files = fewer encoding issues):**

   ```bash
   uv run gitingest-agent extract-specific https://github.com/user/repo --type installation
   ```

**Note:** This is a known issue with the external GitIngest library on Windows. The tool will detect and warn about encoding errors, but extraction will continue with available content.

## Developer Setup

This section is for developers contributing to GitIngest Agent.

### Dev Prerequisites

- Python 3.12 or higher
- UV package manager installed
- GitIngest CLI installed globally (`uv tool install gitingest`)
- Git for version control

### Dev Installation

```bash
# Clone the repository
git clone https://github.com/your-username/gitingest-agent-project.git
cd gitingest-agent-project

# Navigate to implementation directory
cd execute

# Sync environment (creates .venv and installs dependencies)
uv sync

# Install in development mode
uv pip install -e .

# Verify installation
uv run gitingest-agent --help
uv run pytest --version
```

**Important:** All development commands must be run from the `execute/` directory.

### Development Workflow

This project follows the **BMAD (Breakthrough Method for AI-driven Agile Development)** methodology with integrated QA.

**Workflow:**

- **Story Creation**: `@sm *draft`
- **Story Implementation**: `@dev *develop-story {story}`
- **Story Review**: `@qa *review {story}`
- **Risk Assessment**: `@qa *risk {story}`

See `.bmad-core/enhanced-ide-development-workflow.md` for complete workflow details.

### Running Development Commands

```bash
# Navigate to execute directory
cd execute

# Run CLI in development mode
uv run gitingest-agent --help
uv run gitingest-agent check-size https://github.com/user/repo

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

## Testing

All test commands must be run from the `execute/` directory:

```bash
# Navigate to execute directory
cd execute

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_token_counter.py

# Run with verbose output
uv run pytest -v

# Run tests matching pattern
uv run pytest -k "test_check_size"
```

**Test Suite Stats:**

- 190+ tests across all modules
- 96%+ code coverage
- Integration tests for CLI commands
- Unit tests for core functionality

**Test Structure:**

```text
execute/tests/
├── test_cli.py              # CLI command tests
├── test_token_counter.py    # Token counting logic tests
├── test_workflow.py         # Display formatting tests
├── test_storage.py          # Storage layer tests
├── test_extractor.py        # GitIngest integration tests
└── test_exceptions.py       # Exception handling tests
```

## Project Structure

```text
gitingest-agent-project/
├── .bmad-core/              # BMAD framework
├── docs/                    # Planning & story documents
│   ├── prd.md              # Product requirements
│   ├── architecture.md     # System design
│   ├── stories/            # Implementation stories
│   └── handoffs/           # QA handoff documents
├── explore/                 # Research documents
├── plan/                    # Planning work
├── user-context/            # User-provided contextual files
├── docker/                  # Development tools
│   └── toon-test/          # TOON format testing environment
├── execute/                 # Implementation directory (all Python code)
│   ├── .venv/              # UV virtual environment
│   ├── tests/              # Test suite (190 tests, 96%+ coverage)
│   ├── cli.py              # CLI entry point (Click framework)
│   ├── token_counter.py    # Token counting & routing logic
│   ├── workflow.py         # Display formatting utilities
│   ├── storage.py          # File management & analysis storage
│   ├── storage_manager.py  # Dynamic path resolution (Phase 1.5)
│   ├── extractor.py        # GitIngest API wrapper
│   ├── exceptions.py       # Custom exception classes
│   ├── pyproject.toml      # Python project configuration
│   └── uv.lock             # Dependency lock file
├── analyze/                 # Generated analyses storage (runtime)
├── data/                    # Repository extraction storage (runtime)
├── CLAUDE.md                # Agent configuration (Claude Code behavior)
├── CLAUDE_ANALYSIS_GUIDE.md # Analysis generation specifications
├── CHANGELOG.md             # Version history
└── README.md                # This file
```

### Structure Explanation

**Root Level:**

- **BMAD Framework:** `.bmad-core/`, `docs/`, `explore/`, `plan/`, `user-context/`
- **Agent Configuration:** `CLAUDE.md`, `CLAUDE_ANALYSIS_GUIDE.md` (Claude Code runtime config)
- **Project Documentation:** `README.md`, `CHANGELOG.md`

**execute/ Directory:**

- **All Python Implementation:** Source code, tests, and Python environment
- **Self-Contained:** Complete Python project with its own pyproject.toml and .venv
- **Working Directory:** All development commands run from execute/

## Phase Roadmap

### Phase 1.0: Core Clone ✅ **COMPLETE**

High-fidelity replication of proven design from AI LABS video.

**Implemented Features:**

- ✅ Token size checking and routing (200k threshold)
- ✅ Full and selective extraction workflows
- ✅ Claude Code automation via CLAUDE.md
- ✅ Analysis generation (4 types: installation, workflow, architecture, custom)
- ✅ Analysis storage with metadata headers
- ✅ Token overflow prevention with iterative refinement
- ✅ CLI with 4 commands (check-size, extract-full, extract-tree, extract-specific)
- ✅ 190 tests passing, 96%+ coverage

**Implementation Stats:**

- 13 stories completed (1.2-1.14)
- 5 core modules (cli, token_counter, workflow, storage, extractor)
- 15 files changed, 4,926+ lines added
- Complete documentation and workflow automation

### Phase 1.5: Multi-Location Output ✅ **COMPLETE** (v1.1.0)

Enhanced storage capabilities for cross-project usage.

**Implemented Features:**

- ✅ BMAD project detection (gitingest-agent-project vs. other directories)
- ✅ context/related-repos/ universal convention
- ✅ --output-dir parameter on all commands
- ✅ Work from any directory without project pollution
- ✅ Automatic directory creation with validation
- ✅ StorageManager abstraction for dynamic path resolution

**Status:** Released in v1.1.0

### Phase 2.0: TOON Format + Multi-Agent Architecture (Proposed)

Multi-repository analysis at scale through token optimization and parallel processing.

**Key Features:**

- **TOON Format Integration** - 15-25% token savings on GitHub API data (validated)
- **Multi-Agent Architecture** - Parallel sub-agent processing for 5+ repositories
- **Multi-Repo Comparison** - Synthesized analysis across multiple codebases
- **GitHub API Integration** - Commit history, issues, PRs with TOON optimization

**Validation Completed:**

- ✅ Docker testing infrastructure ([docker/toon-test/](docker/toon-test/))
- ✅ Real token savings verified (15-25% on API data)
- ✅ TOON CLI integration tested and working

**Status:** Feature request complete, ready for story creation

See [user-context/v2-toon-multiagent-feature-request.md](user-context/v2-toon-multiagent-feature-request.md) for complete V2.0 specification.

## Documentation

- **[PRD](docs/prd.md)** - Product requirements and user stories
- **[Architecture](docs/architecture.md)** - System design and technical details
- **[CLAUDE.md](CLAUDE.md)** - Complete workflow automation guide
- **[CLAUDE_ANALYSIS_GUIDE.md](CLAUDE_ANALYSIS_GUIDE.md)** - Analysis generation specifications
- **[Stories](docs/stories/)** - Implementation stories
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[Research](explore/)** - Exploration phase research documents

## Contributing

This is a personal development project following BMAD methodology. Development is tracked through:

- User stories in `docs/stories/`
- Quality gates via Test Architect (`@qa`)
- Git commits with co-authorship by Claude

## License

MIT License (To be finalized)

---

**Current Version:** v1.1.0

**Development Status:** Phase 1.5 Complete ✅ - Fully functional CLI tool with universal context convention.

**Next Steps:**

- ✅ Phase 1.0 Complete - All 13 stories implemented and tested
- ✅ Phase 1.5 Complete - Multi-location output and --output-dir parameter
- ✅ V2.0 Research Complete - TOON format validated
- 🎯 **Ready for V2.0 Story Creation** - BMAD workflow planning phase

---

> Built with [Claude Code](https://claude.com/claude-code) using BMAD methodology
