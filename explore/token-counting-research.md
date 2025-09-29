# Token Counting Research

**Date:** 2025-09-29
**Purpose:** Research token counting strategies for GitIngest Agent

---

## Overview

Token counting is critical for GitIngest Agent's routing logic. The 200,000 token threshold determines whether to extract the full repository or use selective extraction.

---

## Token Estimation Methods

### Method 1: GitIngest Built-in Estimation

**How it works:**
- GitIngest includes token count in output metadata
- Based on standard LLM tokenization
- Approximately accurate for routing decisions

**Implementation:**
```python
def count_tokens_gitingest(url):
    """Use GitIngest to estimate tokens"""
    result = subprocess.run(
        ['gitingest', url, '-o', '-'],  # Output to stdout
        capture_output=True,
        text=True,
        timeout=120
    )

    # Look for token count in output
    match = re.search(r'Estimated tokens:\s*(\d+)', result.stdout)
    if match:
        return int(match.group(1))

    # Fallback: estimate from character count
    return len(result.stdout) // 4
```

**Accuracy:** ±10% typically sufficient for routing

### Method 2: Character-Based Estimation

**Rule of Thumb:** 1 token ≈ 4 characters (English text)

**Implementation:**
```python
def estimate_tokens_from_chars(text):
    """Rough estimation: 4 chars per token"""
    return len(text) // 4
```

**Accuracy:**
- Good for English prose: ±15%
- Less accurate for code (varies by language)
- Python: ~3.5 chars/token
- JavaScript: ~3.8 chars/token
- JSON: ~5 chars/token

### Method 3: Tiktoken Library (Precise)

**Most accurate:** Uses actual tokenizer from OpenAI

**Installation:**
```bash
uv add tiktoken
```

**Implementation:**
```python
import tiktoken

def count_tokens_precise(text, model="gpt-4"):
    """Precise token counting using tiktoken"""
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)
```

**Accuracy:** Exact for GPT models, ~95% for Claude

**Trade-off:**
- ✅ Most accurate
- ❌ Adds dependency
- ❌ Slower (encoding overhead)

### Method 4: File Size Heuristic (Pre-check)

**Fastest:** Check without downloading content

**Implementation:**
```python
def estimate_tokens_from_repo_size(url):
    """
    Estimate tokens from GitHub API repository size
    Useful for pre-filtering very large repos
    """
    # Parse owner/repo from URL
    owner, repo = parse_github_url(url)

    # GitHub API call
    response = requests.get(f'https://api.github.com/repos/{owner}/{repo}')
    data = response.json()

    # Size in KB
    size_kb = data.get('size', 0)

    # Rough estimate: 1KB ≈ 250 tokens (code)
    return size_kb * 250
```

**Accuracy:** Very rough, but fast
- Good for early filtering (> 1MB = definitely too large)
- Not reliable for routing decision

---

## Recommended Strategy for GitIngest Agent

### Phase 1: Use GitIngest Built-in

**Rationale:**
- No additional dependencies
- Fast enough for workflow
- Accuracy sufficient for 200k threshold
- Already have GitIngest installed

**Implementation:**
```python
def check_size(url):
    """Token counting using GitIngest"""
    try:
        result = subprocess.run(
            ['gitingest', url, '-o', '-'],
            capture_output=True,
            text=True,
            timeout=120,
            check=True
        )

        # Try to parse token count from output
        match = re.search(r'Estimated tokens:\s*(\d+)', result.stdout)
        if match:
            token_count = int(match.group(1))
        else:
            # Fallback: character-based estimation
            token_count = len(result.stdout) // 4

        return token_count

    except subprocess.TimeoutExpired:
        raise click.ClickException("Token counting timed out (repo too large?)")
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f"GitIngest error: {e.stderr}")
```

### Phase 2 (Optional): Add Tiktoken for Re-check

**When:** Validating extracted content size

**Why:** More precise for secondary checks

**Implementation:**
```python
def count_tokens_from_file(file_path, use_tiktoken=False):
    """Count tokens in extracted file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if use_tiktoken:
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model("gpt-4")
            return len(encoding.encode(content))
        except ImportError:
            pass  # Fall back to estimation

    # Default: character-based estimation
    return len(content) // 4
```

---

## Token Threshold Analysis

### Why 200,000 Tokens?

**Context Limits:**
- Claude 3.5 Sonnet: 200k tokens
- GPT-4 Turbo: 128k tokens
- Gemini 1.5: 1M tokens (outlier)

**Practical Considerations:**
- 200k allows full context for analysis
- Leaves room for conversation history
- Matches video creator's threshold
- Conservative, safe choice

### Buffer Strategy

**Recommendation:** Use 180k as practical threshold

```python
HARD_LIMIT = 200_000      # Absolute max
PRACTICAL_LIMIT = 180_000  # Target threshold (90%)
WARNING_THRESHOLD = 150_000  # Start warning user

def check_size_with_buffer(url):
    """Size check with safety buffer"""
    token_count = count_tokens(url)

    if token_count < PRACTICAL_LIMIT:
        status = "full"
    elif token_count < HARD_LIMIT:
        status = "warning"  # Can do full but warn
        click.echo(f"⚠️  Close to limit: {token_count:,} tokens")
    else:
        status = "selective"

    return token_count, status
```

---

## Token Counting for Different Content Types

### Documentation

**Characteristics:**
- High text density
- ~4 chars/token typical
- Markdown formatting adds tokens

**Example:**
```
10,000 characters of docs ≈ 2,500 tokens
```

### Source Code

**Characteristics:**
- Variable by language
- Python/Ruby: ~3.5 chars/token
- JavaScript/Java: ~3.8 chars/token
- Whitespace affects count

**Example:**
```python
# Python code
def hello():
    print("Hello")

# Approx 30 chars, ~8-9 tokens
```

### Configuration Files

**Characteristics:**
- JSON/YAML: More tokens per char
- Structured format overhead
- ~5 chars/token

**Example:**
```json
{"key": "value", "nested": {"data": 123}}

# 40 chars, ~8 tokens
```

---

## Optimization Strategies

### Strategy 1: Early Exit for Large Repos

**Implementation:**
```python
def quick_size_check(url):
    """Fast pre-check using GitHub API"""
    owner, repo = parse_github_url(url)

    response = requests.get(f'https://api.github.com/repos/{owner}/{repo}')
    size_kb = response.json().get('size', 0)

    if size_kb > 5000:  # > 5MB
        # Definitely needs selective extraction
        return float('inf'), "selective"

    # Otherwise, do full token count
    return check_size(url)
```

### Strategy 2: Incremental Counting

**For very large repos:**
```python
def incremental_size_check(url, threshold=200_000):
    """
    Stop counting once threshold exceeded
    Saves time for obviously large repos
    """
    # Start GitIngest process
    proc = subprocess.Popen(
        ['gitingest', url, '-o', '-'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    accumulated_chars = 0
    for line in proc.stdout:
        accumulated_chars += len(line)
        estimated_tokens = accumulated_chars // 4

        if estimated_tokens > threshold:
            proc.kill()
            return estimated_tokens, "selective"

    proc.wait()
    final_tokens = accumulated_chars // 4
    return final_tokens, "full"
```

### Strategy 3: Caching Token Counts

**For repeated analysis:**
```python
def get_cached_token_count(url):
    """Check cache before counting"""
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cache_file = Path(f".cache/tokens/{cache_key}.json")

    if cache_file.exists():
        cache = json.loads(cache_file.read_text())

        # Check if cache is fresh (< 1 day old)
        cache_age = time.time() - cache['timestamp']
        if cache_age < 86400:
            return cache['token_count']

    # Cache miss or stale - recount
    token_count = count_tokens(url)

    # Store in cache
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps({
        'token_count': token_count,
        'timestamp': time.time()
    }))

    return token_count
```

---

## Error Handling

### Timeout Handling

```python
try:
    token_count = count_tokens(url)
except subprocess.TimeoutExpired:
    click.echo("⚠️  Token counting timed out")
    click.echo("   Repository is likely very large")
    click.echo()

    if click.confirm("Proceed with selective extraction?"):
        return float('inf'), "selective"
    else:
        raise click.Abort()
```

### Network Errors

```python
try:
    token_count = count_tokens(url)
except subprocess.CalledProcessError as e:
    if "could not resolve" in e.stderr.lower():
        click.echo("❌ Network error during size check")
        if click.confirm("Retry?"):
            return count_tokens(url)  # Retry
    raise
```

---

## Display Formatting

### User-Friendly Token Display

```python
def format_token_count(count):
    """Format token count for display"""
    if count < 1_000:
        return f"{count} tokens"
    elif count < 1_000_000:
        return f"{count:,} tokens ({count/1000:.1f}k)"
    else:
        return f"{count:,} tokens ({count/1_000_000:.1f}M)"

# Examples:
# 850 → "850 tokens"
# 45000 → "45,000 tokens (45.0k)"
# 1500000 → "1,500,000 tokens (1.5M)"
```

### Progress Indication

```python
def show_token_check_progress(url):
    """Show progress during token counting"""
    with click.progressbar(
        length=100,
        label='Counting tokens'
    ) as bar:
        # Simulate progress (GitIngest doesn't provide real progress)
        token_count = count_tokens(url)
        bar.update(100)

    click.echo(f"Token count: {format_token_count(token_count)}")
    return token_count
```

---

## Testing Token Counting

### Test Cases

```python
def test_token_counting():
    """Test token counting accuracy"""

    # Test 1: Known small repo
    count1 = count_tokens("https://github.com/octocat/Hello-World")
    assert count1 < 10_000, "Hello-World should be < 10k tokens"

    # Test 2: Character estimation
    test_text = "a" * 4000  # 4000 characters
    estimated = estimate_tokens_from_chars(test_text)
    assert 900 < estimated < 1100, "Should estimate ~1000 tokens"

    # Test 3: Threshold routing
    _, route = check_size_with_buffer("https://github.com/facebook/react")
    assert route == "selective", "React repo should trigger selective"
```

### Accuracy Verification

```python
def verify_token_accuracy(url, expected_range):
    """Verify token count is within expected range"""
    token_count = count_tokens(url)
    min_tokens, max_tokens = expected_range

    if min_tokens <= token_count <= max_tokens:
        click.echo(f"✓ Token count verified: {token_count}")
    else:
        click.echo(f"⚠️  Token count outside expected range")
        click.echo(f"   Got: {token_count}")
        click.echo(f"   Expected: {min_tokens}-{max_tokens}")
```

---

## Summary: Best Practices

1. **Use GitIngest built-in** - Sufficient for routing decisions
2. **Character estimation fallback** - When parsing fails
3. **Add 10% buffer** - Use 180k instead of 200k for safety
4. **Cache results** - Avoid recounting same repos
5. **Timeout protection** - Assume selective for timeouts
6. **Display clearly** - Show token count with formatting
7. **Test with known repos** - Validate accuracy
8. **Consider tiktoken** - For precise secondary checks

---

## Token Count Reference Table

| Repository Type | Typical Size | Tokens | Route |
|----------------|--------------|--------|-------|
| Small utility | 50-200 files | 10k-50k | Full |
| Medium library | 200-500 files | 50k-150k | Full |
| Large framework | 500-2000 files | 150k-500k | Selective |
| Monorepo | 2000+ files | 500k+ | Selective |

---

**Status:** ✅ Research complete
**Recommendation:** Use GitIngest built-in with character fallback