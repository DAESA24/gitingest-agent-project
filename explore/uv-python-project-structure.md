# UV Python Project Structure Research

**Date:** 2025-09-29
**Purpose:** Research UV package manager for GitIngest Agent project setup

---

## Overview

UV is an extremely fast Python package and project manager written in Rust. It provides 10-100x faster dependency management than pip, with built-in support for virtual environments, project scaffolding, and CLI tool development.

**Installation:** Already installed in user environment ✅

---

## UV Project Initialization

### Creating New Projects

```bash
# Initialize in current directory
uv init

# Initialize with project name
uv init gitingest-agent

# Initialize with specific Python version
uv init --python 3.12 gitingest-agent
```

### Generated Structure

```
gitingest-agent/
├── .gitignore          # Git ignore patterns
├── .python-version     # Python version specification
├── README.md           # Project documentation
├── pyproject.toml      # Project configuration
├── main.py            # Entry point (generated)
├── .venv/             # Virtual environment (created on first run)
└── uv.lock            # Dependency lockfile
```

---

## pyproject.toml Structure

### Basic CLI Tool Configuration

```toml
[project]
name = "gitingest-agent"
version = "0.1.0"
description = "Automated GitHub repository analysis tool"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1.0",
]

[project.scripts]
gitingest-agent = "cli:gitingest_agent"
# Format: command-name = "module:function"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Project Scripts Explained

**Format:** `command-name = "module:function"`

**Example:**
```toml
[project.scripts]
gitingest-agent = "cli:gitingest_agent"
# Creates global command 'gitingest-agent'
# Executes function 'gitingest_agent' from module 'cli.py'
```

**Resulting Usage:**
```bash
gitingest-agent check-size <url>
gitingest-agent extract-full <url>
```

### Dependencies Section

```toml
[project]
dependencies = [
    "click>=8.1.0",           # CLI framework
    "requests>=2.31.0",       # HTTP requests (if needed)
]
```

### Optional Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]
test = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
]
```

**Installing Optional Dependencies:**
```bash
uv sync --extra dev      # Install dev dependencies
uv sync --extra test     # Install test dependencies
uv sync --all-extras     # Install all optional dependencies
```

---

## UV Project Structure for GitIngest Agent

### Recommended Layout

```
gitingest-agent-project/
├── .bmad-core/              # BMAD framework
├── .venv/                   # UV virtual environment
├── data/                    # Repository extractions (runtime)
├── analyze/                 # Analysis outputs (runtime)
├── explore/                 # BMAD exploration phase
├── plan/                    # BMAD planning phase
├── execute/                 # BMAD execution phase
│   ├── src/                # Source code
│   │   ├── __init__.py
│   │   ├── cli.py          # Main CLI entry point
│   │   ├── commands/       # Command modules
│   │   │   ├── __init__.py
│   │   │   ├── check.py
│   │   │   ├── extract.py
│   │   │   └── analyze.py
│   │   ├── core/           # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── token_counter.py
│   │   │   ├── workflow.py
│   │   │   └── storage.py
│   │   └── utils/          # Utilities
│   │       ├── __init__.py
│   │       └── git_utils.py
│   └── tests/              # Test suite
│       ├── __init__.py
│       ├── test_cli.py
│       └── test_workflow.py
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lockfile
├── CLAUDE.md               # Agent instructions
└── README.md               # User documentation
```

### Alternative: Flat Structure

```
gitingest-agent-project/
├── .bmad-core/
├── .venv/
├── cli.py                  # Main CLI (at root)
├── token_counter.py        # Modules at root
├── workflow.py
├── storage.py
├── tests/
├── pyproject.toml
└── README.md
```

**Note:** Flat structure simpler for small projects, src/ structure better for growth.

---

## Dependency Management with UV

### Adding Dependencies

```bash
# Add runtime dependency
uv add click

# Add with version constraint
uv add "click>=8.1.0"

# Add development dependency
uv add --dev pytest

# Add optional dependency
uv add --optional dev ruff
```

**Result:** Automatically updates `pyproject.toml` and `uv.lock`

### Removing Dependencies

```bash
uv remove requests
```

### Upgrading Dependencies

```bash
# Upgrade specific package
uv lock --upgrade-package click

# Upgrade all packages
uv lock --upgrade
```

### Syncing Environment

```bash
# Sync environment with lockfile
uv sync

# Sync with optional dependencies
uv sync --extra dev
```

---

## Running the Project

### Development Execution

```bash
# Run Python script in project environment
uv run main.py

# Run CLI command (after defining in pyproject.toml)
uv run gitingest-agent check-size <url>

# Run with arguments
uv run -- gitingest-agent extract-full <url>
```

### Making CLI Globally Accessible

**Option 1: Install in Development Mode**
```bash
# From project directory
uv pip install -e .

# Now available globally
gitingest-agent check-size <url>
```

**Option 2: UV Tool Install**
```bash
# Install as tool (future UV feature)
uv tool install .

# Or from PyPI after publishing
uv tool install gitingest-agent
```

**Option 3: Add to PATH**
```bash
# After building
uv build
pip install dist/gitingest_agent-*.whl

# Now globally accessible
gitingest-agent check-size <url>
```

---

## Testing Integration

### pyproject.toml Test Configuration

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
]
```

### Running Tests

```bash
# Install test dependencies
uv sync --extra test

# Run tests with UV
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_cli.py

# Run with verbose output
uv run pytest -v
```

---

## Building and Publishing

### Building Distributions

```bash
# Build source distribution and wheel
uv build

# Output:
# dist/
#   gitingest_agent-0.1.0.tar.gz
#   gitingest_agent-0.1.0-py3-none-any.whl
```

### Publishing to PyPI

```bash
# Build first
uv build

# Publish (requires UV 0.4+)
uv publish

# Or use twine
pip install twine
twine upload dist/*
```

---

## Complete pyproject.toml Example for GitIngest Agent

```toml
[project]
name = "gitingest-agent"
version = "0.1.0"
description = "Automated GitHub repository analysis using GitIngest and Claude Code"
readme = "README.md"
requires-python = ">=3.12"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
license = { text = "MIT" }
keywords = ["github", "repository", "analysis", "llm", "gitingest"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.1.0",
]

[project.scripts]
gitingest-agent = "cli:gitingest_agent"

[project.urls]
Homepage = "https://github.com/yourusername/gitingest-agent-project"
Repository = "https://github.com/yourusername/gitingest-agent-project"
Issues = "https://github.com/yourusername/gitingest-agent-project/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = [
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = []
```

---

## CLI Entry Point Structure

### cli.py (Main Entry Point)

```python
"""GitIngest Agent CLI entry point."""
import click

@click.group()
def gitingest_agent():
    """GitIngest Agent - Automated GitHub repository analysis."""
    pass

@gitingest_agent.command()
@click.argument('url')
def check_size(url):
    """Check token count of repository."""
    from core.token_counter import count_tokens
    count = count_tokens(url)
    click.echo(f"Token count: {count}")

@gitingest_agent.command()
@click.argument('url')
def extract_full(url):
    """Extract full repository content."""
    from core.workflow import extract_full_repository
    path = extract_full_repository(url)
    click.echo(f"Extracted to: {path}")

if __name__ == '__main__':
    gitingest_agent()
```

### Making Entry Point Work

**pyproject.toml:**
```toml
[project.scripts]
gitingest-agent = "cli:gitingest_agent"
```

**Directory Structure:**
```
project/
├── cli.py              # Contains gitingest_agent function
├── pyproject.toml      # Defines script entry point
```

**After Installation:**
```bash
uv pip install -e .     # Install in development mode
gitingest-agent --help  # Command now globally available
```

---

## UV vs. pip/Poetry Comparison

### UV Advantages

**Speed:**
- 10-100x faster than pip
- Parallel dependency resolution
- Rust-based implementation

**Features:**
- Built-in project scaffolding
- Lockfile generation (uv.lock)
- Virtual environment management
- Tool installation support

**Compatibility:**
- pip-compatible interface (uv pip)
- pyproject.toml standard
- Works with existing Python packages

### Command Equivalents

| Task | pip/venv | UV |
|------|----------|-----|
| Create venv | `python -m venv .venv` | `uv venv` |
| Activate | `source .venv/bin/activate` | Not needed with `uv run` |
| Install package | `pip install click` | `uv add click` |
| Install dev deps | `pip install -e .[dev]` | `uv sync --extra dev` |
| Run script | `python script.py` | `uv run script.py` |
| Freeze deps | `pip freeze > requirements.txt` | `uv lock` |

---

## Best Practices for GitIngest Agent

### 1. Use UV for Everything

```bash
# Initialize project
uv init

# Add dependencies
uv add click

# Run commands
uv run gitingest-agent check-size <url>

# Run tests
uv run pytest
```

### 2. Pin Python Version

```toml
[project]
requires-python = ">=3.12"
```

### 3. Use Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",  # Linter/formatter
]
```

### 4. Leverage uv run

```bash
# No need to activate venv
uv run python script.py
uv run pytest
uv run gitingest-agent check-size <url>
```

### 5. Keep Dependencies Minimal

```toml
dependencies = [
    "click>=8.1.0",  # Only runtime dependency
]
# GitIngest installed as tool, not project dependency
```

---

## Answers to Research Questions

**Q1: How to structure pyproject.toml for CLI tool?**
- Use `[project.scripts]` section
- Format: `command-name = "module:function"`
- Example: `gitingest-agent = "cli:gitingest_agent"`

**Q2: How to make CLI command globally accessible?**
- Define in `[project.scripts]`
- Install with `uv pip install -e .` (dev mode)
- Or build and install: `uv build && pip install dist/*.whl`

**Q3: UV best practices for development dependencies?**
- Use `[project.optional-dependencies]` section
- Common groups: `dev`, `test`, `docs`
- Install with: `uv sync --extra dev`

**Q4: How to integrate tests with UV?**
- Add pytest to optional dependencies
- Configure in `[tool.pytest.ini_options]`
- Run with: `uv run pytest`
- No venv activation needed

---

## Key Patterns for GitIngest Agent

### 1. Project Initialization
```bash
uv init gitingest-agent
cd gitingest-agent
```

### 2. Add Dependencies
```bash
uv add click
uv add --dev pytest
```

### 3. Define Entry Point
```toml
[project.scripts]
gitingest-agent = "cli:gitingest_agent"
```

### 4. Development Workflow
```bash
uv pip install -e .
gitingest-agent --help
```

### 5. Testing
```bash
uv run pytest
```

---

## Resources

- **UV Documentation:** https://docs.astral.sh/uv/
- **Projects Guide:** https://docs.astral.sh/uv/guides/projects/
- **Configuration:** https://docs.astral.sh/uv/concepts/projects/config/
- **Real Python Tutorial:** https://realpython.com/python-uv/

---

**Status:** ✅ Research complete
**Next:** Apply UV project structure to GitIngest Agent implementation