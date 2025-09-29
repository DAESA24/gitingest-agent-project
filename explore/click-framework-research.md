# Click Framework Research

**Date:** 2025-09-29
**Purpose:** Research Click framework for building GitIngest Agent CLI

---

## Overview

Click is a Python package for creating command-line interfaces with minimal code. It's designed to make writing CLI applications quick, intuitive, and composable.

**Installation:** `pip install click` or `uv add click`

---

## Core Concepts

### 1. Commands and Groups

**Command:** Wraps a Python function to make it a CLI command
```python
import click

@click.command()
@click.argument('name')
def hello(name):
    click.echo(f'Hello {name}!')
```

**Group:** Container for multiple commands (parent command)
```python
@click.group()
def cli():
    """Parent command for GitIngest Agent"""
    pass

@cli.command()
def check_size():
    """Check repository token size"""
    click.echo("Checking size...")
```

### 2. Command Groups Pattern for GitIngest Agent

```python
@click.group()
def gitingest_agent():
    """GitIngest Agent CLI tool"""
    pass

@gitingest_agent.command()
@click.argument('url')
def check_size(url):
    """Check token count of repository"""
    # Implementation here
    pass

@gitingest_agent.command()
@click.argument('url')
def extract_full(url):
    """Extract full repository content"""
    # Implementation here
    pass

@gitingest_agent.command()
@click.argument('url')
@click.option('--type', type=click.Choice(['docs', 'readme', 'code']))
def extract_specific(url, type):
    """Extract specific content from repository"""
    # Implementation here
    pass
```

**Usage:**
- `gitingest-agent check-size <url>`
- `gitingest-agent extract-full <url>`
- `gitingest-agent extract-specific <url> --type docs`

---

## Passing Context Between Commands

### Using Context Objects

Click provides `@click.pass_context` to share data between commands:

```python
@click.group()
@click.pass_context
def cli(ctx):
    """Initialize shared context"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config()

@cli.command()
@click.pass_context
def subcommand(ctx):
    """Access shared context"""
    config = ctx.obj['config']
    # Use config
```

### For GitIngest Agent Workflow

```python
@click.group()
@click.pass_context
def gitingest_agent(ctx):
    """GitIngest Agent with shared context"""
    ctx.ensure_object(dict)
    ctx.obj['data_dir'] = 'data/'
    ctx.obj['analyze_dir'] = 'analyze/'

@gitingest_agent.command()
@click.argument('url')
@click.pass_context
def check_size(ctx, url):
    """Check size and store in context"""
    token_count = count_tokens(url)
    ctx.obj['token_count'] = token_count
    ctx.obj['repo_url'] = url
    click.echo(f"Token count: {token_count}")
    return token_count
```

---

## Wrapping External CLI Tools (GitIngest)

### Best Practice Pattern

Click provides special options for wrapping external commands:

```python
import subprocess

@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def wrapper(args):
    """Wrapper around external CLI"""
    cmdline = ['external-tool'] + list(args)
    result = subprocess.run(cmdline, capture_output=True, text=True)
    return result.stdout
```

### GitIngest Wrapper Pattern

```python
import subprocess
import click

def run_gitingest(url, output_path, include_pattern=None, exclude_pattern=None):
    """Wrapper function for GitIngest CLI"""
    cmd = ['gitingest', url, '-o', output_path]

    if include_pattern:
        cmd.extend(['-i', include_pattern])
    if exclude_pattern:
        cmd.extend(['-e', exclude_pattern])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise click.ClickException(f"GitIngest failed: {result.stderr}")

    return result.stdout

@click.command()
@click.argument('url')
def extract_full(url):
    """Extract full repository using GitIngest"""
    repo_name = extract_repo_name(url)
    output_path = f"data/{repo_name}/digest.txt"

    # Ensure directory exists
    os.makedirs(f"data/{repo_name}", exist_ok=True)

    # Call GitIngest
    output = run_gitingest(url, output_path)
    click.echo(f"Extracted to: {output_path}")
```

---

## File Handling Best Practices

### Creating Output Directories

```python
import os
from pathlib import Path

@click.command()
@click.argument('url')
def extract(url):
    """Extract with automatic directory creation"""
    repo_name = extract_repo_name(url)
    output_dir = Path(f"data/{repo_name}")

    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "digest.txt"
    # Process...
```

### Error Handling

```python
@click.command()
def process():
    """Command with error handling"""
    try:
        # Processing logic
        result = risky_operation()
    except FileNotFoundError as e:
        raise click.ClickException(f"File not found: {e}")
    except Exception as e:
        raise click.UsageError(f"Operation failed: {e}")
```

---

## Testing Click Applications

### Using CliRunner

```python
from click.testing import CliRunner
import pytest

def test_check_size():
    """Test check-size command"""
    runner = CliRunner()
    result = runner.invoke(check_size, ['https://github.com/user/repo'])

    assert result.exit_code == 0
    assert "Token count:" in result.output

def test_extract_full():
    """Test extract-full command"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(extract_full, ['https://github.com/user/repo'])

        assert result.exit_code == 0
        assert os.path.exists('data/repo/digest.txt')
```

### Isolated Filesystem for Testing

```python
def test_with_files():
    """Test with isolated filesystem"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create test files
        with open('config.txt', 'w') as f:
            f.write('test config')

        # Run command
        result = runner.invoke(my_command)

        # Verify results
        assert result.exit_code == 0
```

---

## Organizing Commands in Multiple Files

### Modular Structure

```
gitingest-agent-project/
├── cli.py                 # Main entry point
├── commands/
│   ├── __init__.py
│   ├── check.py          # Size checking commands
│   ├── extract.py        # Extraction commands
│   └── analyze.py        # Analysis commands
```

### Main Entry Point (cli.py)

```python
import click
from commands import check, extract, analyze

@click.group()
def gitingest_agent():
    """GitIngest Agent CLI"""
    pass

# Register command modules
gitingest_agent.add_command(check.check_size)
gitingest_agent.add_command(extract.extract_full)
gitingest_agent.add_command(extract.extract_tree)
gitingest_agent.add_command(analyze.analyze)

if __name__ == '__main__':
    gitingest_agent()
```

### Command Module (commands/check.py)

```python
import click

@click.command()
@click.argument('url')
def check_size(url):
    """Check repository token size"""
    # Implementation
    pass
```

---

## Making CLI Globally Accessible

### pyproject.toml Configuration

```toml
[project.scripts]
gitingest-agent = "cli:gitingest_agent"
```

### Alternative: setup.py Entry Points

```python
setup(
    name='gitingest-agent',
    entry_points={
        'console_scripts': [
            'gitingest-agent=cli:gitingest_agent',
        ],
    },
)
```

After installation: `gitingest-agent <command>` available globally

---

## Key Patterns for GitIngest Agent

### 1. Parent Group with Subcommands
```python
@click.group()
def gitingest_agent():
    pass

@gitingest_agent.command()
def check_size():
    pass

@gitingest_agent.command()
def extract_full():
    pass
```

### 2. Subprocess Integration for GitIngest
```python
def run_gitingest(url, options):
    cmd = ['gitingest', url] + options
    result = subprocess.run(cmd, capture_output=True)
    return result
```

### 3. Context Sharing
```python
@click.pass_context
def command(ctx):
    token_count = ctx.obj['token_count']
```

### 4. File Management
```python
Path(output_dir).mkdir(parents=True, exist_ok=True)
```

### 5. Testing with CliRunner
```python
runner = CliRunner()
result = runner.invoke(command, args)
assert result.exit_code == 0
```

---

## Resources

- **Official Docs:** https://click.palletsprojects.com/
- **Commands & Groups:** https://click.palletsprojects.com/en/stable/commands/
- **Advanced Patterns:** https://click.palletsprojects.com/en/stable/advanced/
- **Real Python Tutorial:** https://realpython.com/python-click/
- **Better Stack Guide:** https://betterstack.com/community/guides/scaling-python/click-explained/

---

## Answers to Research Questions

**Q1: How do Click groups work?**
- Use `@click.group()` decorator to create parent command
- Add subcommands with `@group.command()` or `group.add_command()`
- Groups can be nested for hierarchical CLI structures

**Q2: How to pass arguments between commands?**
- Use Context objects with `@click.pass_context`
- Store shared data in `ctx.obj` dictionary
- Access in subcommands via `@click.pass_context` decorator

**Q3: How to integrate Click with external CLI tools?**
- Use `subprocess.run()` within Click commands
- Build command arrays dynamically based on options
- Handle errors with `raise click.ClickException()`

**Q4: Best practices for file handling?**
- Use `pathlib.Path` for cross-platform compatibility
- Create directories with `mkdir(parents=True, exist_ok=True)`
- Validate paths and handle errors explicitly

**Q5: How to structure tests?**
- Use `click.testing.CliRunner` for command testing
- Use `isolated_filesystem()` for file operation tests
- Test exit codes, output content, and side effects

---

**Status:** ✅ Research complete
**Next:** Apply patterns to GitIngest Agent implementation