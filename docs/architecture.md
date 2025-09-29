# GitIngest Agent - System Architecture

**Version:** 1.0 - Phase 1 (Core Clone)
**Date:** 2025-09-29
**Status:** Planning
**Document Owner:** System Architect

---

## Executive Summary

This document defines the system architecture for GitIngest Agent Phase 1, a high-fidelity clone of the proven design from the AI LABS video. The architecture prioritizes **simplicity** (2-hour implementation target), **reliability** (proven workflow patterns), and **extensibility** (support Phase 1.5 enhancements without major refactoring).

**Key Architectural Decisions:**
- **Flat module structure** - Simple, fast to implement
- **CLI-first design** - Click framework with command grouping
- **Subprocess integration** - Wrap GitIngest CLI without dependencies
- **File-based persistence** - Structured storage in data/ and analyze/
- **Declarative automation** - CLAUDE.md drives workflow execution

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code (LLM)                       │
│  - Reads CLAUDE.md                                          │
│  - Executes workflow automatically                          │
│  - Analyzes extracted content                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Invokes CLI commands
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              GitIngest Agent (Python CLI)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CLI Layer (Click Framework)                        │   │
│  │  - check-size, extract-full, extract-tree           │   │
│  │  - extract-specific, analyze                        │   │
│  └────────────┬────────────────────────────────────────┘   │
│               │                                             │
│  ┌────────────┴────────────────────────────────────────┐   │
│  │  Core Logic Layer                                   │   │
│  │  - token_counter: Size checking                     │   │
│  │  - workflow: Routing logic                          │   │
│  │  - storage: File management                         │   │
│  │  - extractor: GitIngest wrapper                     │   │
│  └────────────┬────────────────────────────────────────┘   │
│               │                                             │
│               │ subprocess.run()                            │
└───────────────┼─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              GitIngest CLI (External Tool)                  │
│  - Repository cloning                                       │
│  - Content extraction                                       │
│  - Filtering and formatting                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                File System (Persistence)                    │
│  data/[repo-name]/    - Repository extractions              │
│  analyze/[type]/      - Analysis outputs                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

**Scenario 1: Small Repository (< 200k tokens)**

```
User provides GitHub URL
    ↓
Claude Code reads CLAUDE.md → Workflow activated
    ↓
CLI: gitingest-agent check-size <url>
    ↓
token_counter.count_tokens() → subprocess → GitIngest
    ↓
Decision: 145,000 < 200,000 → "full"
    ↓
CLI: gitingest-agent extract-full <url>
    ↓
extractor.extract_full() → subprocess → GitIngest
    ↓
storage.save_extraction() → data/repo/digest.txt
    ↓
Claude Code analyzes content from file
    ↓
User prompted: Save analysis?
    ↓
storage.save_analysis() → analyze/[type]/repo.md
```

**Scenario 2: Large Repository (≥ 200k tokens)**

```
User provides GitHub URL
    ↓
Claude Code reads CLAUDE.md → Workflow activated
    ↓
CLI: gitingest-agent check-size <url>
    ↓
token_counter.count_tokens() → subprocess → GitIngest
    ↓
Decision: 487,523 ≥ 200,000 → "selective"
    ↓
CLI: gitingest-agent extract-tree <url>
    ↓
extractor.extract_tree() → subprocess → GitIngest (minimal)
    ↓
storage.save_extraction() → data/repo/tree.txt
    ↓
Display tree to user
    ↓
User selects content type: "docs"
    ↓
CLI: gitingest-agent extract-specific <url> --type docs
    ↓
workflow.get_filters_for_type("docs") → include/exclude patterns
    ↓
extractor.extract_specific() → subprocess → GitIngest (filtered)
    ↓
storage.save_extraction() → data/repo/docs-content.txt
    ↓
token_counter.count_tokens_from_file() → Size re-check
    ↓
Decision: 89,450 < 200,000 → Proceed
    ↓
Claude Code analyzes content from file
    ↓
storage.save_analysis() → analyze/[type]/repo.md
```

---

## 2. Component Architecture

### 2.1 CLI Layer (cli.py)

**Responsibility:** User-facing command interface using Click framework

**Design Pattern:** Command Group with Subcommands

**Structure:**
```python
@click.group()
def gitingest_agent():
    """Parent command group"""
    pass

@gitingest_agent.command()
@click.argument('url')
def check_size(url):
    """Token size checking command"""
    # Call token_counter.count_tokens()
    # Display result
    pass

@gitingest_agent.command()
@click.argument('url')
def extract_full(url):
    """Full extraction command"""
    # Call extractor.extract_full()
    # Display confirmation
    pass

@gitingest_agent.command()
@click.argument('url')
def extract_tree(url):
    """Tree extraction command"""
    # Call extractor.extract_tree()
    # Display tree
    pass

@gitingest_agent.command()
@click.argument('url')
@click.option('--type', type=click.Choice(['docs', 'installation', 'code', 'auto']))
def extract_specific(url, type):
    """Selective extraction command"""
    # Call extractor.extract_specific()
    # Size re-check
    # Display confirmation
    pass
```

**Key Responsibilities:**
- Argument parsing and validation
- User interaction (prompts, confirmations)
- Progress display
- Error message formatting
- Delegation to core logic modules

**Dependencies:**
- Click framework (≥8.1.0)
- Core logic modules (token_counter, workflow, extractor, storage)

**Testing Strategy:**
- Use Click's CliRunner for unit tests
- Test each command independently
- Mock core logic modules for isolation

---

### 2.2 Token Counter Module (token_counter.py)

**Responsibility:** Token counting and workflow routing decisions

**Public Interface:**
```python
def count_tokens(url: str) -> int:
    """
    Count tokens in repository using GitIngest.

    Args:
        url: GitHub repository URL

    Returns:
        Estimated token count

    Raises:
        GitIngestError: If extraction fails
        TimeoutError: If counting takes too long
    """
    pass

def count_tokens_from_file(file_path: str) -> int:
    """
    Count tokens in already-extracted file.
    Used for size re-check after selective extraction.

    Args:
        file_path: Path to extracted content file

    Returns:
        Estimated token count
    """
    pass

def should_extract_full(token_count: int, threshold: int = 200_000) -> bool:
    """
    Determine if full extraction is appropriate.

    Args:
        token_count: Repository token count
        threshold: Decision threshold (default 200k)

    Returns:
        True if should extract full, False if selective
    """
    pass
```

**Implementation Strategy:**
```python
def count_tokens(url: str) -> int:
    # Strategy: Use GitIngest to stdout, estimate from output
    result = subprocess.run(
        ['gitingest', url, '-o', '-'],
        capture_output=True,
        text=True,
        timeout=120
    )

    # Try to parse "Estimated tokens: NNNN" from output
    match = re.search(r'Estimated tokens:\s*(\d+)', result.stdout)
    if match:
        return int(match.group(1))

    # Fallback: Character-based estimation (4 chars ≈ 1 token)
    return len(result.stdout) // 4
```

**Design Decisions:**
- **No external dependencies** - Uses GitIngest built-in estimation
- **Character fallback** - If parsing fails, estimate from length
- **Configurable threshold** - Default 200k, but parameterized for testing
- **File-based recounting** - Separate function for re-check workflow

**Error Handling:**
- Timeout → Raise TimeoutError (assume very large repo)
- Network error → Raise GitIngestError with descriptive message
- Invalid URL → Raise ValueError

---

### 2.3 Workflow Module (workflow.py)

**Responsibility:** Workflow routing logic and content type mapping

**Public Interface:**
```python
def get_filters_for_type(content_type: str) -> dict[str, list[str]]:
    """
    Map content type to GitIngest filter patterns.

    Args:
        content_type: Type of content to extract
                     (docs, installation, code, auto)

    Returns:
        Dict with 'include' and 'exclude' pattern lists
    """
    pass

def validate_github_url(url: str) -> tuple[str, str]:
    """
    Validate GitHub URL and extract owner/repo.

    Args:
        url: GitHub URL to validate

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        ValueError: If URL invalid
    """
    pass

def format_token_count(count: int) -> str:
    """
    Format token count for user display.

    Args:
        count: Token count

    Returns:
        Formatted string (e.g., "145,000 tokens (145.0k)")
    """
    pass
```

**Content Type Filter Mapping:**
```python
FILTER_PATTERNS = {
    'docs': {
        'include': ['docs/**/*', '*.md', 'README*', '*.rst'],
        'exclude': ['docs/examples/*', 'docs/archive/*']
    },
    'installation': {
        'include': [
            'README*', 'INSTALL*', 'setup.py', 'pyproject.toml',
            'package.json', 'docs/installation*', 'docs/getting-started*'
        ],
        'exclude': []
    },
    'code': {
        'include': ['src/**/*.py', 'lib/**/*.py'],
        'exclude': ['tests/*', '*_test.py', 'test_*.py', 'examples/*']
    },
    'auto': {
        'include': ['README*', 'docs/**/*.md'],
        'exclude': ['docs/examples/*', 'docs/archive/*']
    }
}
```

**Design Decisions:**
- **Declarative filter mapping** - Easy to extend with new types
- **Language-agnostic auto fallback** - Uses markdown documentation
- **Conservative exclusions** - Exclude examples/tests to reduce noise

---

### 2.4 Extractor Module (extractor.py)

**Responsibility:** Wrap GitIngest CLI with subprocess calls

**Public Interface:**
```python
def extract_full(url: str, repo_name: str) -> str:
    """
    Extract entire repository.

    Args:
        url: GitHub repository URL
        repo_name: Repository name for storage

    Returns:
        Path to digest.txt file

    Raises:
        GitIngestError: If extraction fails
    """
    pass

def extract_tree(url: str, repo_name: str) -> str:
    """
    Extract minimal tree structure.

    Args:
        url: GitHub repository URL
        repo_name: Repository name for storage

    Returns:
        Path to tree.txt file
    """
    pass

def extract_specific(url: str, repo_name: str, content_type: str) -> str:
    """
    Extract targeted content with filtering.

    Args:
        url: GitHub repository URL
        repo_name: Repository name for storage
        content_type: Type of content (docs, installation, code, auto)

    Returns:
        Path to [type]-content.txt file

    Raises:
        GitIngestError: If extraction fails
    """
    pass
```

**Implementation Pattern:**
```python
def extract_full(url: str, repo_name: str) -> str:
    output_dir = Path(f"data/{repo_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "digest.txt"

    cmd = ['gitingest', url, '-o', str(output_file)]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
            check=True
        )
        return str(output_file)
    except subprocess.CalledProcessError as e:
        raise GitIngestError(f"Extraction failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Extraction timed out after 5 minutes")
```

**Design Decisions:**
- **Timeout protection** - 5 minutes max per extraction
- **Automatic directory creation** - No manual mkdir required
- **Absolute path returns** - Clear about where files are saved
- **Descriptive errors** - Include GitIngest stderr in exceptions

**Tree Extraction Strategy:**
```python
def extract_tree(url: str, repo_name: str) -> str:
    # Strategy: Extract with severe filtering to get structure only
    # Alternative: Could use git ls-tree, but this maintains consistency

    cmd = [
        'gitingest', url,
        '-i', 'README.md',  # Minimal content trigger
        '-s', '1024',       # Max 1KB files
        '-o', str(output_file)
    ]

    # Extract, then display tree to terminal
    subprocess.run(cmd, check=True)

    with open(output_file, 'r', encoding='utf-8') as f:
        tree_content = f.read()

    click.echo(tree_content)  # Display to user

    return str(output_file)
```

---

### 2.5 Storage Module (storage.py)

**Responsibility:** File system operations and path management

**Public Interface:**
```python
def parse_repo_name(url: str) -> str:
    """
    Extract repository name from GitHub URL.

    Args:
        url: GitHub URL

    Returns:
        Repository name (e.g., "fastapi" from github.com/tiangolo/fastapi)
    """
    pass

def ensure_data_directory(repo_name: str) -> Path:
    """
    Ensure data directory exists for repository.

    Args:
        repo_name: Repository name

    Returns:
        Path to data/[repo-name]/
    """
    pass

def ensure_analyze_directory(analysis_type: str) -> Path:
    """
    Ensure analyze directory exists for analysis type.

    Args:
        analysis_type: Type of analysis (installation, workflow, etc.)

    Returns:
        Path to analyze/[type]/
    """
    pass

def save_analysis(content: str, repo_name: str, analysis_type: str) -> str:
    """
    Save analysis to analyze/ folder.

    Args:
        content: Analysis content (markdown)
        repo_name: Repository name
        analysis_type: Type of analysis

    Returns:
        Absolute path to saved file
    """
    pass
```

**File Naming Conventions:**
```python
# Extraction files
data/{repo_name}/digest.txt              # Full extraction
data/{repo_name}/tree.txt                # Tree structure
data/{repo_name}/docs-content.txt        # Selective: docs
data/{repo_name}/installation-content.txt # Selective: installation
data/{repo_name}/code-content.txt        # Selective: code

# Analysis files
analyze/{analysis_type}/{repo_name}.md   # Organized by type
```

**Design Decisions:**
- **Automatic directory creation** - mkdir -p behavior (parents=True, exist_ok=True)
- **Absolute path returns** - Always return full paths for clarity
- **Descriptive file names** - Content type prefix for selective extractions
- **Type-based organization** - Analyze folder organized by analysis type

**Phase 1.5 Extensibility:**
```python
# Phase 1: Hardcoded paths
def ensure_data_directory(repo_name: str) -> Path:
    return Path(f"data/{repo_name}")

# Phase 1.5: Will become
def ensure_data_directory(repo_name: str, base_dir: Path = None) -> Path:
    if base_dir is None:
        base_dir = detect_output_location()  # BMAD project detection
    return base_dir / "data" / repo_name
```

**Note:** Phase 1 uses hardcoded "data/" and "analyze/" paths. Architecture supports future parameterization for Phase 1.5 multi-location feature.

---

## 3. Integration Architecture

### 3.1 GitIngest CLI Integration

**Integration Pattern:** Subprocess Wrapper

```python
# Low-level wrapper
def _run_gitingest(args: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    """
    Execute gitingest with standard error handling.

    Args:
        args: Command arguments (after 'gitingest')
        timeout: Maximum execution time in seconds

    Returns:
        CompletedProcess object

    Raises:
        GitIngestError: If command fails
        TimeoutError: If execution exceeds timeout
    """
    cmd = ['gitingest'] + args

    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
    except subprocess.CalledProcessError as e:
        # Parse GitIngest error messages
        if "not found" in e.stderr.lower():
            raise GitIngestError(f"Repository not found: {url}")
        elif "bad credentials" in e.stderr.lower():
            raise GitIngestError("Authentication failed (private repo?)")
        else:
            raise GitIngestError(f"GitIngest error: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"GitIngest timed out after {timeout}s")
```

**Design Decisions:**
- **No direct dependency** - GitIngest not in pyproject.toml (installed as tool)
- **Subprocess isolation** - GitIngest failures don't crash Python process
- **Error parsing** - Translate GitIngest errors to user-friendly messages
- **Timeout protection** - Prevent infinite hangs on large repos

---

### 3.2 Claude Code Integration

**Integration Pattern:** Declarative Workflow (CLAUDE.md)

**CLAUDE.md Structure:**
```markdown
# GitIngest Agent

You are the GitIngest Agent for analyzing GitHub repositories.

## Workflow Trigger
When user provides GitHub URL: https://github.com/...
Execute workflow automatically (no confirmation).

## Workflow Steps

### Step 1: Token Size Check
Execute: gitingest-agent check-size <url>
Store: TOKEN_COUNT

### Step 2: Route Based on Size
IF TOKEN_COUNT < 200000:
  Execute: gitingest-agent extract-full <url>
  Go to Step 4
ELSE:
  Execute: gitingest-agent extract-tree <url>
  Go to Step 3

### Step 3: Selective Extraction
Display tree to user
Ask: "What would you like to analyze?"
Execute: gitingest-agent extract-specific <url> --type <choice>
Re-check size (if > 200k, iterate)

### Step 4: Analysis
Generate analysis based on extracted content
Ask: "What type of analysis?"
Generate based on user request

### Step 5: Save
Ask: "Save analysis to analyze/ folder?"
If yes: Save with confirmation
If no: Display only

## Context Variables
- REPO_URL
- TOKEN_COUNT
- WORKFLOW_TYPE
- EXTRACTION_PATH
```

**Design Decisions:**
- **Pattern-triggered** - GitHub URL activates workflow automatically
- **Step-by-step explicit** - Clear command execution sequence
- **Context maintenance** - Variables tracked across steps
- **Conditional logic** - IF/ELSE branching based on token count
- **User interaction points** - Prompts only at decision points

---

## 4. Data Model

### 4.1 File System Schema

```
gitingest-agent-project/
│
├── data/                              # Repository extractions
│   ├── fastapi/                       # Example: FastAPI repo
│   │   ├── digest.txt                # Full extraction (if < 200k)
│   │   ├── tree.txt                  # Tree structure (if ≥ 200k)
│   │   ├── docs-content.txt          # Selective extraction: docs
│   │   └── installation-content.txt  # Selective extraction: installation
│   │
│   └── click/                         # Example: Click repo
│       └── digest.txt                # Full extraction
│
└── analyze/                           # Analysis outputs
    ├── installation/                  # Installation guides
    │   ├── fastapi.md
    │   └── click.md
    │
    ├── workflow/                      # Workflow documentation
    │   └── fastapi.md
    │
    ├── architecture/                  # Architecture analyses
    │   └── click.md
    │
    └── custom/                        # Custom analyses
        └── fastapi.md
```

### 4.2 File Content Formats

**Extraction Files (data/):**
```
# Repository: user/repo
# Branch: main
# Files: 42
# Estimated Tokens: 150,000
# Generated: 2025-09-29T10:30:00

================================================================================
FILE: src/main.py
================================================================================

[File content]

================================================================================
FILE: src/utils.py
================================================================================

[File content]
```

**Analysis Files (analyze/):**
```markdown
# [Repository Name] - [Analysis Type]

**Repository:** https://github.com/user/repo
**Analyzed:** 2025-09-29
**Token Count:** 150,000
**Extraction:** data/repo/digest.txt

## [Analysis Content]

...

---

*Generated by GitIngest Agent*
```

---

## 5. Error Handling Architecture

### 5.1 Error Hierarchy

```python
class GitIngestAgentError(Exception):
    """Base exception for GitIngest Agent"""
    pass

class GitIngestError(GitIngestAgentError):
    """GitIngest CLI execution failed"""
    pass

class ValidationError(GitIngestAgentError):
    """Input validation failed"""
    pass

class StorageError(GitIngestAgentError):
    """File system operation failed"""
    pass

class WorkflowError(GitIngestAgentError):
    """Workflow logic error"""
    pass
```

### 5.2 Error Handling Strategy

**Network Errors:**
```python
try:
    result = subprocess.run(['gitingest', url, '-o', '-'])
except subprocess.CalledProcessError as e:
    if "could not resolve host" in e.stderr.lower():
        click.echo("❌ Network error: Unable to reach GitHub")
        click.echo("   Check your internet connection")
        if click.confirm("Retry?"):
            return extract_full(url, repo_name)  # Retry
        raise click.Abort()
```

**File System Errors:**
```python
try:
    output_dir.mkdir(parents=True, exist_ok=True)
except PermissionError:
    click.echo("❌ Permission denied creating directory")
    click.echo(f"   Path: {output_dir}")
    click.echo("   Manual fix: mkdir -p data/repo-name")
    raise click.Abort()
```

**Token Overflow:**
```python
# After selective extraction
token_count = count_tokens_from_file(output_file)
if token_count > 200_000:
    click.echo(f"⚠️  Content still exceeds limit: {token_count:,} tokens")
    click.echo("   Options:")
    click.echo("   1. Narrow selection further")
    click.echo("   2. Proceed with partial content")

    choice = click.prompt("Select option", type=int)
    if choice == 1:
        # Re-prompt for content type, iterate
        pass
```

---

## 6. Testing Architecture

### 6.1 Test Structure

```
tests/
├── test_cli.py                    # CLI command tests
├── test_token_counter.py          # Token counting logic
├── test_workflow.py               # Routing and filtering
├── test_storage.py                # File operations
├── test_extractor.py              # GitIngest wrapper
├── test_integration.py            # End-to-end workflows
└── fixtures/
    ├── small_repo_output.txt      # Mock GitIngest output (< 200k)
    ├── large_repo_output.txt      # Mock GitIngest output (≥ 200k)
    └── test_repos.json            # Real repo URLs for integration tests
```

### 6.2 Testing Strategy

**Unit Tests (Isolated):**
```python
# Test token counting with mocked GitIngest
@patch('subprocess.run')
def test_count_tokens_under_limit(mock_run):
    mock_run.return_value.stdout = "a" * 400_000  # 100k tokens
    count = count_tokens("https://github.com/user/repo")
    assert count == 100_000
    assert should_extract_full(count) == True

# Test CLI with Click's CliRunner
def test_check_size_command():
    runner = CliRunner()
    with patch('token_counter.count_tokens', return_value=150_000):
        result = runner.invoke(check_size, ['https://github.com/user/repo'])
        assert result.exit_code == 0
        assert "150,000" in result.output
```

**Integration Tests (Real GitIngest):**
```python
# Test with actual small repository
def test_full_extraction_hello_world():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            extract_full,
            ['https://github.com/octocat/Hello-World']
        )
        assert result.exit_code == 0
        assert Path('data/Hello-World/digest.txt').exists()
```

**Manual Tests (Claude Code):**
- Workflow trigger on GitHub URL
- Sequential command execution
- Context maintenance across steps
- User prompt handling
- Error recovery

---

## 7. Performance Considerations

### 7.1 Bottlenecks

**Network I/O:**
- GitIngest clones repositories (network bound)
- Large repos (> 100 MB) take minutes
- Mitigation: Timeout protection, progress indication

**Token Counting:**
- Requires full content download to stdout
- Same as extraction time
- Mitigation: Could cache results, but Phase 1 skips for simplicity

**File I/O:**
- Disk writes for extractions
- Negligible compared to network time
- Mitigation: None needed

### 7.2 Optimization Opportunities (Future)

**Caching:**
```python
# Future: Cache token counts
def get_cached_token_count(url: str) -> Optional[int]:
    cache_file = Path(f".cache/{hash(url)}.json")
    if cache_file.exists():
        data = json.loads(cache_file.read_text())
        if time.time() - data['timestamp'] < 86400:  # 24 hours
            return data['token_count']
    return None
```

**Parallel Processing:**
```python
# Future: Analyze multiple repos concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(analyze_repo, url) for url in urls]
    results = [f.result() for f in futures]
```

**Note:** Phase 1 prioritizes simplicity over optimization. Proven design doesn't include caching/parallelization.

---

## 8. Security Considerations

### 8.1 Input Validation

**URL Validation:**
```python
def validate_github_url(url: str) -> tuple[str, str]:
    """Validate GitHub URL and extract owner/repo"""
    pattern = r'https?://github\.com/([\w-]+)/([\w-]+)'
    match = re.match(pattern, url)
    if not match:
        raise ValidationError(f"Invalid GitHub URL: {url}")
    return match.group(1), match.group(2)
```

**Path Traversal Prevention:**
```python
def parse_repo_name(url: str) -> str:
    """Extract repository name with sanitization"""
    owner, repo = validate_github_url(url)
    # Remove dangerous characters
    safe_repo = re.sub(r'[^\w-]', '', repo)
    return safe_repo
```

### 8.2 Subprocess Safety

**Command Injection Prevention:**
```python
# ✅ Good: Use list arguments
subprocess.run(['gitingest', url, '-o', output_file])

# ❌ Bad: Use shell=True with string
subprocess.run(f"gitingest {url} -o {output_file}", shell=True)
```

**Path Safety:**
```python
# Ensure paths stay within project directory
output_file = Path('data') / safe_repo_name / 'digest.txt'
assert output_file.resolve().is_relative_to(Path.cwd())
```

### 8.3 Resource Limits

**Timeout Protection:**
- All subprocess calls have timeout (default 300s)
- Prevents infinite hangs on problematic repos

**Disk Space:**
- No explicit checks in Phase 1 (assume sufficient space)
- GitIngest has 10MB file size limit (built-in protection)

---

## 9. Deployment Architecture

### 9.1 Installation

**User Installation:**
```bash
# Navigate to project
cd "Software Projects/gitingest-agent-project"

# Initialize UV project (if not already done)
uv init

# Install dependencies
uv add click

# Install in development mode
uv pip install -e .

# Verify installation
gitingest-agent --help
```

**File Structure After Installation:**
```
gitingest-agent-project/
├── .venv/                    # UV virtual environment
├── cli.py                    # Source files
├── token_counter.py
├── workflow.py
├── storage.py
├── extractor.py
├── pyproject.toml            # Project config
├── uv.lock                   # Dependency lockfile
├── CLAUDE.md                 # Agent instructions
└── README.md                 # User documentation
```

### 9.2 Configuration

**pyproject.toml:**
```toml
[project]
name = "gitingest-agent"
version = "0.1.0"
description = "Automated GitHub repository analysis using GitIngest"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1.0",
]

[project.scripts]
gitingest-agent = "cli:gitingest_agent"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**No Additional Configuration:**
- No config files needed
- No environment variables required
- GitIngest already installed globally via UV tool

---

## 10. Phase 1.5 Extensibility

### 10.1 Architecture Decisions Supporting Phase 1.5

**Modular Storage Layer:**
```python
# Phase 1: Hardcoded
def ensure_data_directory(repo_name: str) -> Path:
    return Path(f"data/{repo_name}")

# Phase 1.5: Parameterized (minimal change)
def ensure_data_directory(repo_name: str, base_dir: Path = None) -> Path:
    if base_dir is None:
        base_dir = Path(".")  # Default to current (Phase 1 behavior)
    return base_dir / "data" / repo_name
```

**CLI Extensibility:**
```python
# Phase 1: No --output-dir
@gitingest_agent.command()
@click.argument('url')
def extract_full(url):
    pass

# Phase 1.5: Add optional parameter (backward compatible)
@gitingest_agent.command()
@click.argument('url')
@click.option('--output-dir', default=None, help='Custom output directory')
def extract_full(url, output_dir):
    base = Path(output_dir) if output_dir else Path(".")
    # Rest of logic unchanged
```

### 10.2 Refactoring Requirements for Phase 1.5

**Minimal Changes Needed:**
1. Add `StorageManager` class to encapsulate path resolution
2. Add `--output-dir` parameter to CLI commands
3. Add BMAD project detection logic (.bmad-core check)
4. Update CLAUDE.md with location detection steps

**No Breaking Changes:**
- Phase 1 tests continue to pass
- Default behavior unchanged (data/ and analyze/ in current directory)
- Enhancement is additive, not replacement

---

## 11. Architectural Principles

### 11.1 Design Principles Applied

**Simplicity First:**
- Flat module structure (not src/ package)
- Direct subprocess calls (no abstraction layers)
- File-based persistence (no database)
- Minimal dependencies (only Click)

**Proven Pattern Replication:**
- Architecture matches video creator's 2-hour implementation
- No speculative features
- Known workflow, known design

**Extensibility Without Complexity:**
- Modular functions support future enhancement
- But no abstraction until needed (YAGNI)
- Phase 1.5 extensions require minimal refactoring

**Error Handling:**
- Fail fast with clear messages
- User-friendly error output
- Graceful degradation where possible

**Testing:**
- Unit tests for logic isolation
- Integration tests with real GitIngest
- Manual tests for Claude Code automation

### 11.2 Trade-offs

**Simplicity vs. Features:**
- ✅ Chose: Simple flat structure
- ❌ Deferred: src/ package organization
- Rationale: 2-hour implementation target, proven design

**Direct Integration vs. Abstraction:**
- ✅ Chose: Direct subprocess calls to GitIngest
- ❌ Deferred: GitIngest Python API wrapper
- Rationale: Tool already installed, subprocess simpler

**File-based vs. Database:**
- ✅ Chose: Structured file storage
- ❌ Deferred: SQLite or JSON database
- Rationale: Video design uses files, sufficient for Phase 1

---

## 12. Success Metrics

### 12.1 Architecture Quality Gates

**Modularity:**
- [ ] Each module has single clear responsibility
- [ ] Modules can be tested independently
- [ ] Dependencies flow in one direction (CLI → Core → GitIngest)

**Maintainability:**
- [ ] Code follows Python conventions (PEP 8)
- [ ] Functions have clear type hints
- [ ] Complex logic has inline comments

**Extensibility:**
- [ ] Phase 1.5 enhancement requires < 2 hours refactoring
- [ ] Storage layer supports multi-location with minimal changes
- [ ] CLI accepts new parameters without breaking existing commands

**Reliability:**
- [ ] Error handling covers all subprocess failure modes
- [ ] Timeout protection prevents infinite hangs
- [ ] File operations handle permission/space errors

---

## 13. Conclusion

This architecture replicates the proven design from the AI LABS video with enhancements for production quality (error handling, testing strategy, Phase 1.5 extensibility).

**Key Strengths:**
- **Simplicity** - Flat structure, minimal dependencies, direct integration
- **Reliability** - Comprehensive error handling, timeout protection
- **Proven** - Based on demonstrated 2-hour implementation
- **Extensible** - Supports Phase 1.5 without major refactoring

**Next Steps:**
1. Draft CLAUDE.md workflow specification
2. Begin Execute Phase implementation
3. Test with real repositories

---

**Document Status:** Complete - Ready for Implementation

**Related Documents:**
- [prd.md](prd.md) - Product Requirements
- CLAUDE.md - Workflow automation (next document)

**Version History:**
- 1.0 - Initial architecture for Phase 1 (Core Clone)