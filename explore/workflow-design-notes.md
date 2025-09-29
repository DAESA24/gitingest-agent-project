# Workflow Design Notes

**Date:** 2025-09-29
**Purpose:** Design GitIngest Agent workflow logic and decision trees

---

## Core Workflow Overview

GitIngest Agent automates the process of analyzing GitHub repositories by intelligently routing based on token size and user needs.

**Key Decision Point:** 200,000 token threshold

---

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────┐
│ USER INPUT: GitHub URL                          │
│ Format: https://github.com/user/repo           │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ CLAUDE.MD TRIGGER                               │
│ - Pattern match: GitHub URL                     │
│ - Automatic workflow activation                 │
│ - No user confirmation needed                   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ STEP 1: TOKEN SIZE CHECK                        │
│ Command: gitingest-agent check-size <url>      │
│ Action: Call GitIngest to count tokens          │
│ Output: "Token count: NNNNNN"                   │
│ Store: TOKEN_COUNT variable                     │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ STEP 2: WORKFLOW ROUTING DECISION               │
│ Decision: TOKEN_COUNT < 200,000?                │
└──────┬──────────────────────────────┬───────────┘
       │                              │
       ▼ YES                          ▼ NO
┌──────────────────┐           ┌─────────────────────┐
│ ROUTE A:         │           │ ROUTE B:            │
│ Full Extraction  │           │ Selective Extract   │
└──────┬───────────┘           └─────┬───────────────┘
       │                             │
       │                             │
       ▼                             ▼
┌──────────────────────────┐  ┌────────────────────────────┐
│ STEP 3A: FULL EXTRACT    │  │ STEP 3B: TREE EXTRACTION   │
│ Command: extract-full    │  │ Command: extract-tree      │
│ Save to: data/repo/      │  │ Save to: data/repo/        │
│         digest.txt       │  │         tree.txt           │
│ No user prompts          │  │ Display tree to user       │
└──────┬───────────────────┘  └────┬───────────────────────┘
       │                           │
       │                           ▼
       │                    ┌────────────────────────────┐
       │                    │ STEP 4: USER SELECTION     │
       │                    │ Prompt: "What to analyze?" │
       │                    │ Options:                   │
       │                    │ - Documentation            │
       │                    │ - Installation             │
       │                    │ - Specific files           │
       │                    └────┬───────────────────────┘
       │                         │
       │                         ▼
       │                    ┌────────────────────────────┐
       │                    │ STEP 5: SPECIFIC EXTRACT   │
       │                    │ Command: extract-specific  │
       │                    │          --type [choice]   │
       │                    │ Save to: data/repo/        │
       │                    │         [type]-content.txt │
       │                    └────┬───────────────────────┘
       │                         │
       │                         ▼
       │                    ┌────────────────────────────┐
       │                    │ STEP 6: SIZE RE-CHECK      │
       │                    │ ⚠️  CRITICAL BUG FIX       │
       │                    │ Verify < 200k after fetch  │
       │                    │ If still too large:        │
       │                    │   → Prompt narrower select │
       │                    └────┬───────────────────────┘
       │                         │
       └─────────────────────────┴───────────────┐
                                                  │
                                                  ▼
                              ┌───────────────────────────────────┐
                              │ STEP 7: ANALYSIS GENERATION       │
                              │ Claude Code analyzes content      │
                              │ Prompt: "What type of analysis?"  │
                              │ Options:                          │
                              │ - Installation guide              │
                              │ - Architecture overview           │
                              │ - Workflow documentation          │
                              │ - Custom analysis                 │
                              └────────────┬──────────────────────┘
                                           │
                                           ▼
                              ┌───────────────────────────────────┐
                              │ STEP 8: SAVE PROMPT               │
                              │ Ask: "Save analysis?"             │
                              │ If YES:                           │
                              │   → Save to analyze/[type]/       │
                              │            [repo].md              │
                              │ If NO:                            │
                              │   → Display only                  │
                              └────────────┬──────────────────────┘
                                           │
                                           ▼
                              ┌───────────────────────────────────┐
                              │ STEP 9: COMPLETION                │
                              │ Display summary:                  │
                              │ ✓ Repository analyzed             │
                              │ ✓ Files saved to: [paths]         │
                              │ ✓ Token count: [count]            │
                              └───────────────────────────────────┘
```

---

## Workflow Routes Detailed

### Route A: Full Extraction (< 200k tokens)

**Characteristics:**
- Fastest path (fewest steps)
- No user interaction until analysis
- Suitable for small-to-medium repos

**Steps:**
1. Size check confirms < 200k
2. Extract entire repository
3. Save to `data/[repo]/digest.txt`
4. Proceed directly to analysis

**Advantages:**
- Simple, linear workflow
- No decision-making overhead
- Complete context available

**Use Cases:**
- Small utility libraries
- Documentation sites
- Individual project components
- Well-scoped repositories

### Route B: Selective Extraction (≥ 200k tokens)

**Characteristics:**
- More complex (requires user input)
- Multiple sub-workflows possible
- Prevents context overflow

**Steps:**
1. Size check confirms ≥ 200k
2. Extract tree structure
3. Display tree to user
4. User selects content type
5. Extract specific content
6. **Re-check size** (critical)
7. Proceed to analysis

**Advantages:**
- Stays within token limits
- User controls what's analyzed
- Focused analysis on relevant parts

**Use Cases:**
- Large frameworks (React, Django)
- Monorepos
- Comprehensive documentation
- Enterprise codebases

---

## Content Type Options (Route B)

### Option 1: Documentation Only

**Pattern:**
```bash
gitingest-agent extract-specific <url> --type docs
```

**Include Patterns:**
- `docs/**/*`
- `*.md`
- `README*`
- `*.rst`

**Typical Token Range:** 20k-100k

**Best For:**
- Understanding project purpose
- Learning how to use library
- Finding installation instructions

### Option 2: Installation Guide

**Pattern:**
```bash
gitingest-agent extract-specific <url> --type installation
```

**Include Patterns:**
- `README*`
- `INSTALL*`
- `setup.py`
- `pyproject.toml`
- `package.json`
- `docs/installation*`
- `docs/getting-started*`

**Typical Token Range:** 5k-30k

**Best For:**
- Setting up project locally
- Understanding dependencies
- Configuration requirements

### Option 3: Core Implementation

**Pattern:**
```bash
gitingest-agent extract-specific <url> --type code
```

**Include Patterns:**
- `src/**/*.py` (or relevant language)
- `lib/**/*`
- Exclude: `tests/*`, `examples/*`

**Typical Token Range:** Varies widely

**Best For:**
- Understanding architecture
- Learning implementation patterns
- Finding specific functionality

### Option 4: Automatic Fallback (README + Docs)

**When to Use:** User unsure or doesn't specify

**Pattern:**
```bash
# Automatic selection
gitingest-agent extract-specific <url> --type auto
```

**Include Patterns:**
- `README*`
- `docs/**/*.md`
- Top-level configuration files

**Typical Token Range:** 30k-80k

**Best For:**
- General understanding
- Safe default choice
- Time-constrained analysis

---

## Critical: Size Re-Check Logic

### The Problem

**From V2 Spec:**
> "After retrieving the tree and documentation, I need another check to ensure the combined content doesn't exceed the limit again. Currently, it can overshoot."

### The Solution

**Implementation:**
```python
def extract_with_validation(url, content_type, max_tokens=200_000):
    """Extract content with iterative size validation"""

    # First extraction attempt
    output_path = extract_specific(url, content_type)
    token_count = count_tokens_from_file(output_path)

    # Check if still over limit
    if token_count <= max_tokens:
        click.echo(f"✓ Extraction successful: {token_count} tokens")
        return output_path, token_count

    # Content still too large - prompt for refinement
    click.echo(f"⚠️  Content still exceeds limit: {token_count} tokens")
    click.echo(f"   Target: {max_tokens} tokens")
    click.echo()
    click.echo("Options:")
    click.echo("1. Narrow content selection further")
    click.echo("2. Analyze in chunks")
    click.echo("3. Proceed with partial content (truncate)")

    choice = click.prompt("Select option", type=int)

    if choice == 1:
        # Recursive refinement
        refined_type = prompt_for_narrower_selection()
        return extract_with_validation(url, refined_type, max_tokens)
    elif choice == 2:
        # Chunk strategy
        return extract_in_chunks(url, content_type, max_tokens)
    else:
        # Truncate and proceed
        return truncate_content(output_path, max_tokens)
```

**Workflow Integration:**
```
Extract specific content
   ↓
Count tokens in result
   ↓
If > 200k:
   ↓
Prompt user for refinement
   ↓
Repeat until < 200k
```

---

## Command Specifications

### Command: check-size

**Purpose:** Count tokens without full extraction

**Implementation Strategy:**
```python
def check_size(url):
    """
    Fast token counting using GitIngest to stdout
    Avoids disk writes until necessary
    """
    result = subprocess.run(
        ['gitingest', url, '-o', '-'],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Estimate tokens (4 chars ≈ 1 token)
    token_count = len(result.stdout) // 4

    return token_count
```

**Output Format:**
```
Token count: 150000
Route: full extraction
```

### Command: extract-full

**Purpose:** Extract entire repository

**Implementation:**
```python
def extract_full(url):
    """Extract complete repository to digest.txt"""
    repo_name = parse_repo_name(url)
    output_dir = Path(f"data/{repo_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "digest.txt"

    subprocess.run([
        'gitingest',
        url,
        '-o', str(output_file)
    ], check=True)

    return output_file
```

**Output:**
```
Extracting repository...
✓ Saved to: data/repo-name/digest.txt
Token count: 145000
```

### Command: extract-tree

**Purpose:** Get repository structure only

**Implementation Strategy:**
```python
def extract_tree(url):
    """
    Extract minimal content to visualize structure
    Alternative: Use git ls-tree if GitIngest doesn't support tree-only
    """
    repo_name = parse_repo_name(url)
    output_dir = Path(f"data/{repo_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "tree.txt"

    # Strategy: Extract with severe filtering to get structure
    subprocess.run([
        'gitingest',
        url,
        '-i', 'README.md',  # Minimal content
        '-s', '1024',       # 1KB max file size
        '-o', str(output_file)
    ], check=True)

    # Display tree to terminal
    with open(output_file) as f:
        tree_content = f.read()
    click.echo(tree_content)

    return output_file
```

**Alternative: Direct Git Approach**
```python
def extract_tree_alt(url):
    """Use git directly for tree structure"""
    # Clone shallow
    subprocess.run(['git', 'clone', '--depth=1', url, 'temp_repo'])

    # Get file list
    result = subprocess.run(
        ['git', '-C', 'temp_repo', 'ls-tree', '-r', '--name-only', 'HEAD'],
        capture_output=True,
        text=True
    )

    # Clean up
    shutil.rmtree('temp_repo')

    return result.stdout
```

### Command: extract-specific

**Purpose:** Extract targeted content based on type

**Implementation:**
```python
def extract_specific(url, content_type):
    """Extract specific content with type-based filtering"""
    repo_name = parse_repo_name(url)
    output_dir = Path(f"data/{repo_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{content_type}-content.txt"

    # Map content types to filter patterns
    filters = get_filters_for_type(content_type)

    cmd = ['gitingest', url, '-o', str(output_file)]

    if filters['include']:
        cmd.extend(['-i', ','.join(filters['include'])])
    if filters['exclude']:
        cmd.extend(['-e', ','.join(filters['exclude'])])

    subprocess.run(cmd, check=True)

    return output_file

def get_filters_for_type(content_type):
    """Define filter patterns for each content type"""
    patterns = {
        'docs': {
            'include': ['docs/**/*', '*.md', 'README*', '*.rst'],
            'exclude': ['docs/examples/*']
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
            'exclude': ['tests/*', '*_test.py', 'test_*.py']
        },
        'auto': {
            'include': ['README*', 'docs/**/*.md'],
            'exclude': ['docs/examples/*', 'docs/archive/*']
        }
    }
    return patterns.get(content_type, patterns['auto'])
```

---

## Error Handling Strategies

### Network Errors

**Symptom:** GitIngest fails to clone repository

**Response:**
```python
try:
    result = subprocess.run(cmd, check=True, capture_output=True)
except subprocess.CalledProcessError as e:
    if "could not resolve host" in e.stderr.lower():
        click.echo("❌ Network error: Unable to reach GitHub")
        click.echo("   Check your internet connection")
    elif "repository not found" in e.stderr.lower():
        click.echo("❌ Repository not found")
        click.echo("   Verify URL is correct and repo is public")
    else:
        click.echo(f"❌ GitIngest error: {e.stderr}")

    if click.confirm("Retry?"):
        return extract_full(url)  # Retry
    else:
        raise click.Abort()
```

### Permission Errors

**Symptom:** Cannot create data/ directories

**Response:**
```python
try:
    output_dir.mkdir(parents=True, exist_ok=True)
except PermissionError:
    click.echo("❌ Permission denied creating directory")
    click.echo(f"   Path: {output_dir}")
    click.echo()
    click.echo("Manual fix:")
    click.echo(f"   mkdir -p {output_dir}")
    raise click.Abort()
```

### Token Overflow

**Symptom:** Content exceeds limit after extraction

**Response:** (See "Size Re-Check Logic" above)

### Invalid URL

**Symptom:** URL doesn't match GitHub format

**Response:**
```python
def validate_github_url(url):
    """Validate GitHub URL format"""
    pattern = r'https?://github\.com/[\w-]+/[\w-]+'
    if not re.match(pattern, url):
        click.echo("❌ Invalid GitHub URL")
        click.echo("   Expected: https://github.com/user/repo")
        click.echo(f"   Received: {url}")
        raise click.BadParameter("Invalid GitHub URL format")
```

---

## Context Tracking

### Variables to Maintain

Throughout workflow execution:

```python
context = {
    'repo_url': 'https://github.com/user/repo',
    'repo_name': 'repo',
    'token_count': 150000,
    'workflow_type': 'full',  # or 'selective'
    'extraction_path': 'data/repo/digest.txt',
    'analysis_type': 'installation',  # if requested
    'save_path': 'analyze/installation/repo.md'  # if saved
}
```

### Progress Display

```python
def display_progress(context):
    """Show workflow progress to user"""
    click.echo("─" * 50)
    click.echo(f"Repository: {context['repo_name']}")
    click.echo(f"Token count: {context['token_count']:,}")
    click.echo(f"Workflow: {context['workflow_type']}")
    click.echo(f"Extraction: {context['extraction_path']}")
    click.echo("─" * 50)
```

---

## Workflow Optimization Opportunities

### 1. Parallel Processing

**Opportunity:** When analyzing multiple repos

**Implementation:**
```python
# Future enhancement
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(analyze_repo, url) for url in urls]
    results = [f.result() for f in futures]
```

### 2. Caching

**Opportunity:** Re-analyzing same repo

**Implementation:**
```python
def check_cache(url):
    """Check if recent analysis exists"""
    cache_file = Path(f"data/{repo_name}/.cache.json")
    if cache_file.exists():
        cache = json.loads(cache_file.read_text())
        if is_cache_fresh(cache):  # Check age, commit hash
            return cache['extraction_path']
    return None
```

### 3. Smart Content Selection

**Opportunity:** Predict best content type based on analysis goal

**Implementation:**
```python
def suggest_content_type(analysis_goal):
    """Suggest extraction type based on analysis goal"""
    mapping = {
        'installation': 'installation',
        'setup': 'installation',
        'architecture': 'code',
        'implementation': 'code',
        'usage': 'docs',
        'tutorial': 'docs'
    }
    return mapping.get(analysis_goal.lower(), 'auto')
```

---

## Summary: Key Design Decisions

1. **200k token threshold** - Based on Claude Code context limit
2. **Two-route workflow** - Full vs. selective based on size
3. **Size re-check critical** - Prevent overflow after selective extraction
4. **User prompts strategic** - Only when decision required
5. **Automatic by default** - GitHub URL triggers entire workflow
6. **Error handling graceful** - Clear messages, retry options
7. **Context displayed** - User always knows workflow state
8. **File-based storage** - Persistent, structured data

---

**Status:** ✅ Workflow design complete
**Next:** Translate design into BMAD planning documents (PRD, architecture)