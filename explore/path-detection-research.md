# Path Detection Research (Phase 1.5 Enhancement)

**Date:** 2025-09-29
**Purpose:** Research path detection strategies for multi-location output capability
**Phase:** 1.5 Enhancement (Requirements Addendum)

---

## Overview

This research supports the Phase 1.5 enhancement that enables GitIngest Agent to save analysis outputs to any BMAD project directory, not just gitingest-agent-project.

**Core Requirement:** Detect current working directory, identify if it's a BMAD project, and route outputs appropriately.

---

## Python Path Detection Methods

### Method 1: pathlib.Path (Recommended)

**Modern, cross-platform path handling**

```python
from pathlib import Path

# Get current working directory
cwd = Path.cwd()
print(cwd)  # PosixPath('/path/to/project') or WindowsPath('C:\\path\\to\\project')

# Get absolute path
absolute_path = Path('relative/path').resolve()

# Check if file/directory exists
if cwd.exists():
    print("Path exists")

# Check if path is directory
if cwd.is_dir():
    print("Is a directory")

# Check if path is file
some_file = Path('file.txt')
if some_file.is_file():
    print("Is a file")
```

**Advantages:**
- ✅ Cross-platform (Windows/Unix paths handled automatically)
- ✅ Object-oriented interface
- ✅ Built-in Python 3.4+
- ✅ Rich path manipulation methods

### Method 2: os.getcwd() (Legacy)

**Traditional approach**

```python
import os

# Get current working directory
cwd = os.getcwd()
print(cwd)  # String: '/path/to/project'

# Join paths
data_path = os.path.join(cwd, 'data', 'repo')

# Check existence
if os.path.exists(data_path):
    print("Path exists")

# Check if directory
if os.path.isdir(data_path):
    print("Is directory")
```

**Use Case:** Legacy code compatibility only. Prefer pathlib for new code.

### Method 3: __file__ for Script Location

**Get location of current script**

```python
from pathlib import Path

# Get script's directory
script_dir = Path(__file__).parent.resolve()

# Get project root (assuming script is in src/)
project_root = script_dir.parent

# Construct paths relative to project
data_dir = project_root / 'data'
```

**Use Case:** When you need paths relative to script location, not CWD.

---

## Detecting BMAD Projects

### Strategy: Check for .bmad-core/ Directory

**Implementation:**

```python
from pathlib import Path

def is_bmad_project(directory: Path = None) -> bool:
    """
    Check if directory contains BMAD framework

    Args:
        directory: Path to check (default: current working directory)

    Returns:
        True if .bmad-core/ exists in directory
    """
    if directory is None:
        directory = Path.cwd()

    bmad_core = directory / '.bmad-core'
    return bmad_core.exists() and bmad_core.is_dir()

# Usage
if is_bmad_project():
    print("Current directory is a BMAD project")
```

### Getting Project Name

```python
def get_project_name(directory: Path = None) -> str:
    """
    Extract project name from directory

    Args:
        directory: Project directory (default: current working directory)

    Returns:
        Project directory name
    """
    if directory is None:
        directory = Path.cwd()

    return directory.name

# Usage
project_name = get_project_name()
# If in /path/to/my-project/ → returns "my-project"
```

### Detecting Specific Project (GitIngest Agent)

```python
def is_gitingest_agent_project(directory: Path = None) -> bool:
    """
    Check if current directory is gitingest-agent-project

    Returns:
        True if directory name is "gitingest-agent-project"
    """
    if directory is None:
        directory = Path.cwd()

    return directory.name == "gitingest-agent-project"

# Usage
if is_gitingest_agent_project():
    # Use V2 default behavior
    output_dir = Path('data')
else:
    # Use enhanced behavior
    output_dir = Path('context/related-repos')
```

---

## Path Resolution Strategies

### Strategy 1: Current Working Directory

**When to use:** Most common case - user runs command from project directory

```python
def resolve_output_location() -> Path:
    """
    Determine where to save analysis based on current directory

    Returns:
        Path to output directory
    """
    cwd = Path.cwd()

    # Check if in gitingest-agent-project
    if cwd.name == "gitingest-agent-project":
        # V2 behavior: save to data/ and analyze/
        return cwd

    # Check if in another BMAD project
    if is_bmad_project(cwd):
        # Enhanced behavior: save to context/related-repos/
        context_dir = cwd / 'context' / 'related-repos'
        context_dir.mkdir(parents=True, exist_ok=True)
        return context_dir

    # Unknown location: prompt user
    return prompt_for_output_location()
```

### Strategy 2: Explicit Path Parameter

**When to use:** User specifies exact output location via CLI flag

```python
def resolve_explicit_path(user_path: str) -> Path:
    """
    Resolve user-provided path

    Args:
        user_path: Path string from user (absolute or relative)

    Returns:
        Resolved absolute Path object
    """
    path = Path(user_path)

    # Convert to absolute if relative
    if not path.is_absolute():
        path = path.resolve()

    # Validate path exists or can be created
    if not path.exists():
        # Try to create
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise ValueError(f"Cannot create directory: {path}")

    # Validate it's a directory
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    return path
```

### Strategy 3: Relative Path Navigation

**When to use:** Finding gitingest-agent-project from other locations

```python
def find_gitingest_agent_project() -> Path | None:
    """
    Search for gitingest-agent-project in workspace

    Assumes structure: Claude Code Workspace/Software Projects/gitingest-agent-project/

    Returns:
        Path to gitingest-agent-project if found, else None
    """
    cwd = Path.cwd()

    # Strategy 1: Check if we're already in it
    if cwd.name == "gitingest-agent-project":
        return cwd

    # Strategy 2: Check parent directories
    for parent in cwd.parents:
        if parent.name == "Software Projects":
            gitingest_dir = parent / "gitingest-agent-project"
            if gitingest_dir.exists():
                return gitingest_dir

    # Strategy 3: Check sibling directories
    if cwd.parent.name == "Software Projects":
        gitingest_dir = cwd.parent / "gitingest-agent-project"
        if gitingest_dir.exists():
            return gitingest_dir

    return None
```

---

## Storage Manager Implementation

### Complete StorageManager Class

```python
from pathlib import Path
from typing import Optional
import click

class StorageManager:
    """
    Manages output location detection and path resolution
    for GitIngest Agent with multi-location support
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize storage manager

        Args:
            output_dir: Explicit output directory (overrides detection)
        """
        if output_dir:
            self.output_dir = Path(output_dir).resolve()
        else:
            self.output_dir = self._detect_output_location()

        self.is_gitingest_project = self._check_if_gitingest_project()

    def _detect_output_location(self) -> Path:
        """Detect appropriate save location based on context"""
        cwd = Path.cwd()

        # Check if in gitingest-agent-project
        if cwd.name == "gitingest-agent-project":
            return cwd  # Use V2 default structure

        # Check if in another BMAD project
        if self._is_bmad_project(cwd):
            # Offer to save to context/related-repos/
            if click.confirm(
                f"Detected BMAD project: {cwd.name}. "
                f"Save to this project's context folder?",
                default=True
            ):
                context_dir = cwd / "context" / "related-repos"
                context_dir.mkdir(parents=True, exist_ok=True)
                return context_dir
            else:
                # User declined, try to find gitingest-agent-project
                gitingest_dir = self._find_gitingest_agent_project()
                if gitingest_dir:
                    return gitingest_dir

        # Unknown location - ask user
        return self._prompt_for_location(cwd)

    def _is_bmad_project(self, directory: Path) -> bool:
        """Check if directory contains BMAD framework"""
        bmad_core = directory / '.bmad-core'
        return bmad_core.exists() and bmad_core.is_dir()

    def _check_if_gitingest_project(self) -> bool:
        """Check if output directory is gitingest-agent-project"""
        return self.output_dir.name == "gitingest-agent-project" or \
               (self.output_dir.parent.name == "gitingest-agent-project")

    def _find_gitingest_agent_project(self) -> Optional[Path]:
        """Search for gitingest-agent-project in workspace"""
        cwd = Path.cwd()

        # Check parent directories for Software Projects
        for parent in cwd.parents:
            if parent.name == "Software Projects":
                gitingest_dir = parent / "gitingest-agent-project"
                if gitingest_dir.exists():
                    return gitingest_dir

        return None

    def _prompt_for_location(self, current_dir: Path) -> Path:
        """Prompt user for output location"""
        click.echo(f"Current directory: {current_dir}")
        click.echo()
        click.echo("Where should analysis be saved?")
        click.echo("1. Current directory")
        click.echo("2. GitIngest Agent project (if found)")
        click.echo("3. Custom location (specify path)")

        choice = click.prompt("Select option", type=int, default=1)

        if choice == 1:
            output = current_dir / "gitingest-analysis"
            output.mkdir(parents=True, exist_ok=True)
            return output
        elif choice == 2:
            gitingest_dir = self._find_gitingest_agent_project()
            if gitingest_dir:
                return gitingest_dir
            else:
                click.echo("GitIngest Agent project not found")
                return self._prompt_for_location(current_dir)
        else:
            custom_path = click.prompt("Enter path", type=str)
            return Path(custom_path).resolve()

    def get_data_path(self, repo_name: str, filename: str) -> Path:
        """
        Get path for extraction data

        Args:
            repo_name: Repository name
            filename: File name (e.g., 'digest.txt', 'tree.txt')

        Returns:
            Full path for data file
        """
        if self.is_gitingest_project:
            # V2 behavior: data/[repo]/[file]
            path = self.output_dir / 'data' / repo_name / filename
        else:
            # Enhanced behavior: context/related-repos/[repo]-[file]
            base_name = filename.rsplit('.', 1)[0]  # Remove extension
            path = self.output_dir / f"{repo_name}-{base_name}.txt"

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def get_analysis_path(self, repo_name: str, analysis_type: str) -> Path:
        """
        Get path for analysis output

        Args:
            repo_name: Repository name
            analysis_type: Type of analysis (installation, architecture, etc.)

        Returns:
            Full path for analysis file
        """
        if self.is_gitingest_project:
            # V2 behavior: analyze/[type]/[repo].md
            path = self.output_dir / 'analyze' / analysis_type / f"{repo_name}.md"
        else:
            # Enhanced behavior: [repo]-[type].md in output directory
            path = self.output_dir / f"{repo_name}-{analysis_type}.md"

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
```

### Usage in CLI Commands

```python
import click
from storage import StorageManager

@click.command()
@click.argument('url')
@click.option('--output-dir', default=None, help='Custom output directory')
def extract_full(url, output_dir):
    """Extract full repository content"""

    # Initialize storage manager
    storage = StorageManager(output_dir=output_dir)

    # Parse repo name
    repo_name = parse_repo_name(url)

    # Get output path
    output_path = storage.get_data_path(repo_name, 'digest.txt')

    # Call GitIngest
    subprocess.run(['gitingest', url, '-o', str(output_path)], check=True)

    click.echo(f"✓ Extracted to: {output_path}")
```

---

## Cross-Platform Path Handling

### Windows vs Unix Paths

**Pathlib handles this automatically:**

```python
from pathlib import Path

# Unix
path = Path('/home/user/project/data')
# str(path) → '/home/user/project/data'

# Windows
path = Path('C:\\Users\\user\\project\\data')
# str(path) → 'C:\\Users\\user\\project\\data'

# Cross-platform construction
path = Path.home() / 'project' / 'data'
# Works on both platforms
```

### Path Separators

```python
# NEVER hardcode separators
bad = 'path/to/file'  # ❌ Unix only
bad = 'path\\to\\file'  # ❌ Windows only

# ALWAYS use Path
good = Path('path') / 'to' / 'file'  # ✅ Cross-platform
```

### Home Directory

```python
# Get user home directory (cross-platform)
home = Path.home()
# Unix: /home/username
# Windows: C:\Users\username

# Expand ~ in paths
path = Path('~/project/data').expanduser()
# Resolves to actual home directory
```

---

## Error Handling

### Path Validation

```python
def validate_output_path(path: Path) -> bool:
    """
    Validate output path is usable

    Args:
        path: Path to validate

    Returns:
        True if valid, raises exception if not
    """
    # Check if path exists
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise click.ClickException(
                f"Permission denied creating directory: {path}"
            )
        except Exception as e:
            raise click.ClickException(
                f"Cannot create directory {path}: {e}"
            )

    # Check if it's a directory
    if not path.is_dir():
        raise click.ClickException(
            f"Path is not a directory: {path}"
        )

    # Check write permissions
    test_file = path / '.write_test'
    try:
        test_file.touch()
        test_file.unlink()
    except PermissionError:
        raise click.ClickException(
            f"No write permission for directory: {path}"
        )

    return True
```

### Handling Non-Existent Paths

```python
def ensure_directory_exists(path: Path) -> Path:
    """
    Create directory if it doesn't exist

    Args:
        path: Directory path

    Returns:
        Path object (confirmed to exist)

    Raises:
        click.ClickException: If directory cannot be created
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError:
        raise click.ClickException(
            f"❌ Permission denied: Cannot create {path}\n"
            f"   Try running: mkdir -p {path}"
        )
    except Exception as e:
        raise click.ClickException(
            f"❌ Error creating directory: {e}"
        )
```

---

## Testing Path Detection

### Unit Tests

```python
import pytest
from pathlib import Path
from storage import StorageManager

def test_is_bmad_project(tmp_path):
    """Test BMAD project detection"""
    # Create fake BMAD project
    bmad_core = tmp_path / '.bmad-core'
    bmad_core.mkdir()

    storage = StorageManager()
    assert storage._is_bmad_project(tmp_path) is True

def test_not_bmad_project(tmp_path):
    """Test non-BMAD directory"""
    storage = StorageManager()
    assert storage._is_bmad_project(tmp_path) is False

def test_gitingest_project_detection(tmp_path):
    """Test gitingest-agent-project detection"""
    gitingest_dir = tmp_path / 'gitingest-agent-project'
    gitingest_dir.mkdir()

    # Change to that directory
    import os
    original_cwd = os.getcwd()
    os.chdir(gitingest_dir)

    try:
        storage = StorageManager()
        assert storage.is_gitingest_project is True
    finally:
        os.chdir(original_cwd)

def test_custom_output_dir():
    """Test explicit output directory"""
    custom_dir = "/tmp/custom"
    storage = StorageManager(output_dir=custom_dir)
    assert str(storage.output_dir) == custom_dir
```

### Integration Tests

```python
def test_path_resolution_in_bmad_project(tmp_path):
    """Test path resolution when in BMAD project"""
    # Setup fake BMAD project
    project = tmp_path / 'test-project'
    project.mkdir()
    (project / '.bmad-core').mkdir()

    import os
    original_cwd = os.getcwd()
    os.chdir(project)

    try:
        storage = StorageManager()
        path = storage.get_analysis_path('react', 'architecture')

        # Should save to context/related-repos/
        assert 'context' in str(path)
        assert 'related-repos' in str(path)
    finally:
        os.chdir(original_cwd)
```

---

## Summary: Best Practices

1. **Use pathlib.Path** - Modern, cross-platform path handling
2. **Detect BMAD projects** - Check for `.bmad-core/` directory
3. **Support explicit paths** - Allow `--output-dir` CLI parameter
4. **Validate paths** - Check existence, permissions before use
5. **Create directories safely** - Use `mkdir(parents=True, exist_ok=True)`
6. **Handle errors gracefully** - Clear messages, recovery options
7. **Test across platforms** - Verify Windows and Unix paths work
8. **Never hardcode separators** - Use Path operations (/)

---

## Key Patterns for GitIngest Agent

### 1. Storage Manager Initialization
```python
storage = StorageManager(output_dir=user_provided_path)
```

### 2. BMAD Project Detection
```python
if (Path.cwd() / '.bmad-core').exists():
    # Is BMAD project
```

### 3. Path Resolution
```python
if cwd.name == "gitingest-agent-project":
    # V2 behavior
else if is_bmad_project(cwd):
    # Enhanced behavior
else:
    # Prompt user
```

### 4. Directory Creation
```python
output_path.parent.mkdir(parents=True, exist_ok=True)
```

### 5. Cross-Platform Paths
```python
path = Path('data') / repo_name / 'digest.txt'
```

---

**Status:** ✅ Research complete
**Next:** Integrate path detection into PRD and Architecture documents