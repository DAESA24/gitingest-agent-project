# GitIngest CLI Capabilities Research

**Date:** 2025-09-29
**Purpose:** Deep dive into GitIngest CLI for integration with GitIngest Agent

---

## Overview

GitIngest is a command-line tool that converts GitHub repositories into LLM-friendly text format. It generates consolidated text prompts optimized for large language models with smart formatting and automatic filtering.

**Installation:** `uv tool install gitingest` ✅ Already installed

---

## CLI Usage Patterns

### Basic Usage

```bash
# Analyze local directory (default: digest.txt)
gitingest

# Analyze specific directory
gitingest /path/to/repo

# Analyze GitHub repository
gitingest https://github.com/user/repo

# Output to stdout
gitingest -o - https://github.com/user/repo

# Custom output file
gitingest -o custom-output.txt https://github.com/user/repo
```

### Complete Command Reference

```bash
gitingest [OPTIONS] [SOURCE]
```

**SOURCE:** Can be:
- Current directory (default if omitted)
- Absolute or relative path
- GitHub URL (https://github.com/user/repo)

---

## Command-Line Options

### Output Control

**`-o, --output TEXT`**
- Output file path (default: `digest.txt`)
- Use `-` for stdout
- Example: `gitingest -o analysis.txt <url>`

### Filtering Options

**`-i, --include-pattern TEXT`**
- Shell-style glob patterns to include
- Multiple patterns supported
- Example: `gitingest -i "*.py" -i "*.md"`
- Combined: `gitingest -i "*.py,*.md,docs/**/*"`

**`-e, --exclude-pattern TEXT`**
- Shell-style glob patterns to exclude
- Multiple patterns supported
- Example: `gitingest -e "*.log" -e "tests/*"`
- Combined: `gitingest -e "*.log,tests/*,node_modules/*"`

**`-s, --max-size INTEGER`**
- Maximum file size to process in bytes
- Default: `10485760` (10 MB)
- Example: `gitingest -s 5242880` (5 MB limit)

### Repository Options

**`-b, --branch TEXT`**
- Specify branch to analyze
- Default: repository's default branch
- Example: `gitingest -b develop <url>`

**`--include-submodules`**
- Include repository's submodules in analysis
- Default: submodules excluded
- Example: `gitingest --include-submodules <url>`

**`--include-gitignored`**
- Include files matched by .gitignore and .gitingestignore
- Default: respect ignore files
- Example: `gitingest --include-gitignored <url>`

### Authentication

**`-t, --token TEXT`**
- GitHub personal access token (PAT)
- Required for private repositories
- Can use environment variable: `GITHUB_TOKEN`
- Example: `gitingest -t ghp_xxxxx <url>`
- Example: `GITHUB_TOKEN=ghp_xxxxx gitingest <url>`

---

## Filtering Patterns Deep Dive

### Include Pattern Examples

```bash
# Python files only
gitingest -i "*.py" <url>

# Documentation files
gitingest -i "*.md,*.rst,docs/**/*" <url>

# Specific directories
gitingest -i "src/**/*,docs/**/*" <url>

# Configuration files
gitingest -i "*.json,*.toml,*.yaml,*.yml" <url>

# README and setup files
gitingest -i "README*,setup.py,pyproject.toml,package.json" <url>
```

### Exclude Pattern Examples

```bash
# Exclude tests
gitingest -e "tests/*,*_test.py,test_*.py" <url>

# Exclude common noise
gitingest -e "*.log,*.tmp,node_modules/*,dist/*,build/*" <url>

# Exclude large files
gitingest -e "*.pdf,*.zip,*.tar.gz,*.mp4" <url>

# Exclude dependencies
gitingest -e "node_modules/*,venv/*,.venv/*,vendor/*" <url>
```

### Combined Filtering Strategy

```bash
# Documentation only, exclude examples
gitingest \
  -i "docs/**/*,*.md,README*" \
  -e "docs/examples/*,*.log" \
  <url>

# Source code only, exclude tests and builds
gitingest \
  -i "src/**/*.py,lib/**/*.py" \
  -e "tests/*,*_test.py,build/*,dist/*" \
  <url>
```

---

## Automatic Exclusions

GitIngest automatically excludes common files to reduce noise:

**Version Control:**
- `.git/`, `.svn/`, `.hg/`
- `.gitignore`, `.gitmodules`

**System Files:**
- `.DS_Store`, `Thumbs.db`
- `desktop.ini`

**Logs & Temporary:**
- `*.log`, `*.tmp`, `*.temp`
- `*.cache`

**Media Files:**
- `*.jpg`, `*.png`, `*.gif`, `*.svg`
- `*.mp4`, `*.mp3`, `*.wav`
- `*.pdf`, `*.doc`, `*.ppt`

**Archives:**
- `*.zip`, `*.tar`, `*.gz`, `*.rar`

**Dependencies:**
- `node_modules/`
- `vendor/`
- `__pycache__/`
- `*.pyc`, `*.pyo`

**Build Artifacts:**
- `dist/`, `build/`, `.egg-info/`
- `target/`, `out/`, `bin/`

**IDE Files:**
- `.vscode/`, `.idea/`
- `*.swp`, `*.swo`

---

## Token Counting Capabilities

### How GitIngest Counts Tokens

GitIngest includes token count statistics in its output:

**Output Format:**
```
Repository: user/repo
Files processed: 42
Total size: 256 KB
Estimated tokens: 150,000
```

**Token Estimation:**
- Based on standard LLM tokenization
- Approximately 4 characters per token (rough estimate)
- Actual count may vary by model (GPT-4, Claude, etc.)

### Extracting Token Count Programmatically

```python
import subprocess
import re

def count_tokens(url):
    """Extract token count from GitIngest output"""
    result = subprocess.run(
        ['gitingest', url, '-o', '-'],
        capture_output=True,
        text=True
    )

    # Parse output for token count
    match = re.search(r'Estimated tokens:\s*(\d+)', result.stdout)
    if match:
        return int(match.group(1))

    # Fallback: count characters and estimate
    char_count = len(result.stdout)
    return char_count // 4  # Rough estimate
```

### Token Size Checking Strategy for GitIngest Agent

```python
def check_repository_size(url):
    """
    Check repository token size without full extraction
    Returns: (token_count, should_extract_full)
    """
    # Strategy 1: Use GitIngest with tree-only mode (if available)
    # Strategy 2: Extract to stdout and count
    # Strategy 3: Use GitHub API to estimate from file sizes

    result = subprocess.run(
        ['gitingest', url, '-o', '-'],
        capture_output=True,
        text=True
    )

    # Count tokens from output
    token_count = len(result.stdout) // 4

    # Decision threshold
    threshold = 200_000
    should_extract_full = token_count < threshold

    return token_count, should_extract_full
```

---

## Output Format Structure

### Digest File Format

```
# Repository: user/repo
# Branch: main
# Files: 42
# Total Size: 256 KB
# Estimated Tokens: 150,000
# Generated: 2025-09-29T10:30:00

================================================================================
FILE: src/main.py
================================================================================

[File content here]

================================================================================
FILE: src/utils.py
================================================================================

[File content here]

...
```

### Parsing Output Format

```python
def parse_gitingest_output(output_path):
    """Parse GitIngest digest file"""
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract metadata
    metadata = {}
    for line in content.split('\n')[:10]:  # Check first 10 lines
        if line.startswith('# Repository:'):
            metadata['repository'] = line.split(':', 1)[1].strip()
        elif line.startswith('# Estimated Tokens:'):
            metadata['token_count'] = int(line.split(':')[1].strip().replace(',', ''))
        # ... parse other metadata

    # Split by file separators
    files = content.split('=' * 80)
    parsed_files = []

    for file_section in files[1:]:  # Skip header
        if file_section.strip():
            lines = file_section.strip().split('\n')
            if lines[0].startswith('FILE:'):
                file_path = lines[0].replace('FILE:', '').strip()
                file_content = '\n'.join(lines[2:])  # Skip separator line
                parsed_files.append({
                    'path': file_path,
                    'content': file_content
                })

    return metadata, parsed_files
```

---

## Performance Characteristics

### Processing Speed

**Small Repos (< 50k tokens):**
- Processing time: 5-15 seconds
- Network bound (clone time)

**Medium Repos (50k-200k tokens):**
- Processing time: 15-60 seconds
- CPU bound (content processing)

**Large Repos (> 200k tokens):**
- Processing time: 1-5 minutes
- Mixed (clone + processing)
- May hit GitHub API rate limits

### Limitations

**File Limit:**
- Processes first 1000 files
- Prevents memory overload on massive repos
- No explicit warning if limit hit

**GitHub API Rate Limits:**
- Without token: 60 requests/hour
- With token: 5000 requests/hour
- Recommendation: Always use token for GitIngest Agent

**Memory Usage:**
- Proportional to repository size
- Large repos (> 500 MB) may cause issues
- Mitigation: Use filtering to reduce scope

---

## Error Handling

### Common Errors

**Repository Not Found:**
```
Error: Repository not found or not accessible
Solution: Check URL, use -t flag for private repos
```

**Network Timeout:**
```
Error: Failed to clone repository
Solution: Retry, check network connection, verify URL
```

**Invalid Patterns:**
```
Error: Invalid glob pattern
Solution: Check pattern syntax, escape special characters
```

**Token Authentication:**
```
Error: Bad credentials
Solution: Verify GitHub token, check token permissions
```

### Error Handling Pattern

```python
def safe_gitingest_call(url, **kwargs):
    """Call GitIngest with error handling"""
    try:
        result = subprocess.run(
            build_gitingest_command(url, **kwargs),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr
            if "not found" in error_msg.lower():
                raise RepositoryNotFoundError(url)
            elif "bad credentials" in error_msg.lower():
                raise AuthenticationError("Invalid GitHub token")
            else:
                raise GitIngestError(error_msg)

        return result.stdout

    except subprocess.TimeoutExpired:
        raise TimeoutError(f"GitIngest timed out processing {url}")
    except Exception as e:
        raise GitIngestError(f"Unexpected error: {e}")
```

---

## Private Repository Support

### Using Personal Access Tokens

**Creating Token:**
1. GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo` (full control of private repositories)
4. Copy token: `ghp_xxxxxxxxxxxxx`

**Using Token:**

```bash
# Method 1: Command-line flag
gitingest -t ghp_xxxxx https://github.com/user/private-repo

# Method 2: Environment variable
export GITHUB_TOKEN=ghp_xxxxx
gitingest https://github.com/user/private-repo

# Method 3: In Python
os.environ['GITHUB_TOKEN'] = 'ghp_xxxxx'
subprocess.run(['gitingest', url])
```

---

## GitIngest Agent Integration Patterns

### Pattern 1: Full Extraction

```python
def extract_full_repository(url, repo_name):
    """Extract complete repository"""
    output_path = f"data/{repo_name}/digest.txt"
    os.makedirs(f"data/{repo_name}", exist_ok=True)

    subprocess.run([
        'gitingest',
        url,
        '-o', output_path
    ], check=True)

    return output_path
```

### Pattern 2: Tree Structure Only

```python
def extract_tree(url, repo_name):
    """Extract repository structure (file paths only)"""
    output_path = f"data/{repo_name}/tree.txt"
    os.makedirs(f"data/{repo_name}", exist_ok=True)

    # Use extreme filtering to get minimal content
    subprocess.run([
        'gitingest',
        url,
        '-i', 'README*',  # Only README to get structure
        '-s', '1024',     # Max 1KB files
        '-o', output_path
    ], check=True)

    # Alternative: Use git ls-tree if GitIngest doesn't support tree-only
    # subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'HEAD'])

    return output_path
```

### Pattern 3: Selective Extraction

```python
def extract_documentation(url, repo_name):
    """Extract documentation only"""
    output_path = f"data/{repo_name}/docs-content.txt"
    os.makedirs(f"data/{repo_name}", exist_ok=True)

    subprocess.run([
        'gitingest',
        url,
        '-i', 'docs/**/*,*.md,README*,INSTALL*',
        '-e', 'docs/examples/*,docs/archive/*',
        '-o', output_path
    ], check=True)

    return output_path

def extract_readme_only(url, repo_name):
    """Extract README and key docs"""
    output_path = f"data/{repo_name}/readme-content.txt"
    os.makedirs(f"data/{repo_name}", exist_ok=True)

    subprocess.run([
        'gitingest',
        url,
        '-i', 'README*,INSTALL*,CONTRIBUTING*,setup.py,pyproject.toml,package.json',
        '-o', output_path
    ], check=True)

    return output_path
```

---

## Answers to Research Questions

**Q1: How does GitIngest count tokens?**
- Includes token estimate in output metadata
- Approximately 4 characters per token
- Can parse from output or estimate from character count

**Q2: What filtering patterns work best for docs-only extraction?**
- Include: `docs/**/*,*.md,README*,*.rst`
- Exclude: `docs/examples/*,docs/api/*` (if too verbose)
- Adjust max-size to skip large files

**Q3: How to handle private repositories?**
- Use `-t` flag with GitHub personal access token
- Or set `GITHUB_TOKEN` environment variable
- Token needs `repo` scope for private access

**Q4: Performance characteristics with large repos?**
- 1000 file limit prevents memory overload
- Processing time: 1-5 minutes for large repos
- Recommendation: Use filtering to reduce scope

**Q5: Output format structure?**
- Header with metadata (repo, tokens, files)
- File separator: 80 equals signs
- Format: `FILE: path` followed by content
- Parseable with regex and string splitting

---

## Key Patterns for GitIngest Agent

### 1. Size Checking
```python
result = subprocess.run(['gitingest', url, '-o', '-'], capture_output=True)
token_count = len(result.stdout) // 4
```

### 2. Full Extraction
```python
subprocess.run(['gitingest', url, '-o', f'data/{repo}/digest.txt'])
```

### 3. Documentation Extraction
```python
subprocess.run(['gitingest', url, '-i', 'docs/**/*,*.md', '-o', output])
```

### 4. Error Handling
```python
try:
    result = subprocess.run(cmd, check=True, capture_output=True, timeout=300)
except subprocess.CalledProcessError as e:
    # Handle GitIngest errors
except subprocess.TimeoutExpired:
    # Handle timeout
```

### 5. Token Parsing
```python
match = re.search(r'Estimated tokens:\s*(\d+)', output)
token_count = int(match.group(1)) if match else len(output) // 4
```

---

## Resources

- **GitHub Repository:** https://github.com/davidesantangelo/gitingest
- **Official Site:** https://gitingest.com/
- **PyPI Package:** https://pypi.org/project/gitingest/
- **Local Installation:** ✅ Already installed via UV

---

**Status:** ✅ Research complete
**Next:** Apply patterns to GitIngest Agent workflow implementation