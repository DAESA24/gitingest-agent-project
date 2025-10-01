# Pull Request Workflow Documentation Recommendations

**Date:** 2025-09-30
**Purpose:** Propose additions to workspace-level CLAUDE.md for GitHub PR workflow with BMAD integration

---

## Analysis of Current CLAUDE.md Structure

### Existing Sections (Relevant to PR Workflow)
1. **Project Creation Protocol** (Lines 5-219) - How projects are created
2. **Sub-Project (Feature Development) Workflow** (Lines 221-288) - Feature branches and worktrees
3. **BMAD-GitHub Integration Patterns** (Lines 324-397) - GitHub operations per BMAD phase
4. **Package Management Standards** (Lines 399-416) - Tool-specific instructions

### Identified Gap
**Missing:** Explicit PR creation and review workflow that bridges feature development (line 277-288) and GitHub integration (line 324-346).

**Current State:**
- Line 281-282 mentions "Pull requests created from feature branches"
- Line 343 mentions "Create pull requests for feature integration"
- **But no explicit step-by-step PR workflow for Claude to execute**

### Recommended Insertion Point
**Insert new section AFTER line 288 (end of Sub-Project Workflow Integration) and BEFORE line 290 (ADHD Support Framework)**

**Reasoning:**
1. Follows natural workflow progression (create feature → develop → PR → merge)
2. Keeps GitHub integration patterns together
3. Doesn't interrupt existing logical groupings
4. Separates from support frameworks (ADHD, Documentation)

---

## Proposed Addition to Workspace CLAUDE.md

### Section Title and Location
**Insert at Line 289** (new section between Sub-Project Workflow and ADHD Support)

**Section Header:**
```markdown
### Pull Request (PR) Workflow with BMAD Integration
```

---

### Proposed Complete Section Text

```markdown
### Pull Request (PR) Workflow with BMAD Integration
**Prerequisites:** Feature branch with completed work, all tests passing
**Purpose:** Formal code review and merge process for GitHub-integrated BMAD projects

#### When to Create a Pull Request
Create a PR when ANY of these conditions are met:
- Feature development is complete and ready for review
- Refactoring work is finished with all tests passing
- Bug fix is complete and verified
- Documentation updates are ready for main branch

**DO NOT create PR for:**
- Work in progress (WIP) - unless explicitly creating draft PR
- Failing tests or broken builds
- Incomplete features without user approval

#### PR Creation Process - Step by Step

**Step 1: Pre-PR Verification Checklist**
Execute these commands in sequence. Stop and fix issues before proceeding:

```bash
# Navigate to project (if not already there)
cd "Software Projects/[project-name]"

# Ensure you're on the feature branch
git branch --show-current
# VERIFY: Output should be your feature branch name (e.g., "feature/add-pr-workflow")

# Check for uncommitted changes
git status
# VERIFY: Either "nothing to commit, working tree clean" OR stage changes first

# Run all tests (Python example)
cd execute && uv run pytest
# VERIFY: All tests passing. If tests fail, fix before proceeding.

# Run all tests (Node.js example)
npm test
# VERIFY: All tests passing. If tests fail, fix before proceeding.

# Return to project root
cd ..
```

**If any verification fails:** Stop, fix the issue, commit the fix, then restart Step 1.

**Step 2: Review Recent Commits**
```bash
# View commits that will be in the PR
git log origin/main..HEAD --oneline

# INTERPRET OUTPUT:
# - Each line is one commit that will be included in the PR
# - Verify commit messages are clear and descriptive
# - If commit messages are poor, consider interactive rebase (advanced)
```

**Step 3: Push Feature Branch to Remote**
```bash
# Push your feature branch to GitHub
git push origin [feature-branch-name]

# Example: git push origin feature/add-pr-workflow

# VERIFY: Command completes without errors
# VERIFY: Output shows "remote: Create a pull request for '[branch-name]'"
```

**Step 4: Gather PR Context Information**
Collect this information before creating the PR:

```bash
# Get commit summary
git log origin/main..HEAD --oneline > /tmp/pr-commits.txt

# Get changed files
git diff origin/main..HEAD --name-only > /tmp/pr-files.txt

# Get detailed changes
git diff origin/main..HEAD --stat > /tmp/pr-stats.txt

# Read the summaries
cat /tmp/pr-commits.txt
cat /tmp/pr-files.txt
cat /tmp/pr-stats.txt
```

**Step 5: Create Pull Request with GitHub CLI**
```bash
# Create PR with title and body
gh pr create \
  --title "[Type]: Brief description of changes" \
  --body "$(cat <<'EOF'
## Summary
[Brief description of what this PR does - 1-2 sentences]

## Changes Made
[Bullet list of specific changes]
- Change 1
- Change 2
- Change 3

## Testing
[How you verified these changes work]
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] No regressions found

## Related Issues
Closes #[issue-number] (if applicable)
Fixes #[issue-number] (if applicable)
Relates to #[issue-number] (if applicable)

## BMAD Phase
[Which BMAD phase does this relate to?]
- [ ] Explore - Research and discovery
- [ ] Plan - Planning and design
- [ ] Execute - Implementation

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated for new functionality
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or breaking changes documented)
- [ ] Commit messages are clear and descriptive

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base main \
  --head [feature-branch-name]

# IMPORTANT PLACEHOLDERS TO REPLACE:
# - [Type]: bug-fix, feature, refactor, docs, test, etc.
# - [feature-branch-name]: Your actual branch name
# - [issue-number]: GitHub issue number (if applicable)
# - Fill in all [bracketed] sections with actual content

# VERIFY: Command outputs a GitHub PR URL
# SAVE: Copy the PR URL for reference
```

**PR Title Format Guidelines:**
- **bug-fix:** "Fix: Brief description" (e.g., "Fix: Windows encoding error in CLI")
- **feature:** "Feature: Brief description" (e.g., "Feature: Add PR workflow documentation")
- **refactor:** "Refactor: Brief description" (e.g., "Refactor: Move files to execute directory")
- **docs:** "Docs: Brief description" (e.g., "Docs: Update README installation steps")
- **test:** "Test: Brief description" (e.g., "Test: Add integration test suite")

**Step 6: Self-Review the PR**
```bash
# View the PR in your browser
gh pr view --web

# OR view in terminal
gh pr view

# VERIFY CHECKLIST:
# - [ ] Title is clear and descriptive
# - [ ] Description explains the WHY, not just WHAT
# - [ ] All commits are included
# - [ ] No unexpected files in "Files changed" tab
# - [ ] Tests are visible in PR checks (if CI/CD configured)
```

**Step 7: Wait for Review or Merge**
- If solo developer: Review thoroughly, then merge
- If team project: Wait for review, address feedback, then merge

#### PR Merge Process - Step by Step

**Step 1: Final Pre-Merge Verification**
```bash
# Ensure PR is up to date with main
gh pr view [pr-number] --json mergeable --jq '.mergeable'

# INTERPRET OUTPUT:
# - "MERGEABLE" = Good to merge
# - "CONFLICTING" = Resolve conflicts first
# - "UNKNOWN" = GitHub still checking

# If conflicts exist, resolve them:
git checkout [feature-branch]
git pull origin main
# Resolve conflicts in your editor
git add .
git commit -m "Resolve merge conflicts"
git push origin [feature-branch]
```

**Step 2: Merge the PR**
```bash
# Merge with squash (recommended for clean history)
gh pr merge [pr-number] --squash --delete-branch

# OR merge with merge commit (preserves all commits)
gh pr merge [pr-number] --merge --delete-branch

# OR merge with rebase (linear history)
gh pr merge [pr-number] --rebase --delete-branch

# RECOMMENDED: Use --squash for most cases
# VERIFY: Command outputs "Merged pull request #[number]"
```

**Merge Strategy Guidelines:**
- **--squash** (Recommended): Combines all commits into one clean commit on main
- **--merge**: Preserves all commits and creates merge commit (use for major features)
- **--rebase**: Linear history without merge commit (use if you want linear git log)

**Step 3: Post-Merge Cleanup**
```bash
# Pull latest main with merged changes
git checkout main
git pull origin main

# Verify merge was successful
git log --oneline -5
# VERIFY: Your PR changes appear in recent commits

# Delete local feature branch (if not auto-deleted)
git branch -d [feature-branch-name]

# Verify branch is deleted
git branch -a
# VERIFY: Feature branch no longer appears in local branches
```

**Step 4: Verify Deployment (if applicable)**
If project has CI/CD:
```bash
# Check GitHub Actions status
gh run list --limit 5

# View specific run details
gh run view [run-id]

# VERIFY: Deployment successful or in progress
```

#### PR Review Process (For Reviewers)

**If user asks you to review a PR:**

**Step 1: Checkout PR Locally**
```bash
# Checkout the PR branch
gh pr checkout [pr-number]

# VERIFY: You're now on the PR branch
git branch --show-current
```

**Step 2: Run Tests Locally**
```bash
# Run full test suite
cd execute && uv run pytest  # Python
# OR
npm test  # Node.js

# VERIFY: All tests pass
# If tests fail, note failures for review comment
```

**Step 3: Review Code Changes**
```bash
# View all changes
git diff main..HEAD

# View specific file
git diff main..HEAD -- path/to/file.py

# ANALYZE:
# - Code quality and clarity
# - Test coverage for new code
# - Potential bugs or edge cases
# - Documentation completeness
```

**Step 4: Provide Review Feedback**
```bash
# Add review comment via CLI
gh pr review [pr-number] --comment --body "Review feedback here"

# Request changes
gh pr review [pr-number] --request-changes --body "Changes needed: ..."

# Approve PR
gh pr review [pr-number] --approve --body "LGTM! Great work."

# LGTM = "Looks Good To Me" (standard approval phrase)
```

#### Troubleshooting Common PR Issues

**Issue: "Your branch is behind main"**
```bash
# Update your feature branch with latest main
git checkout [feature-branch]
git pull origin main
# Resolve any conflicts
git push origin [feature-branch]
```

**Issue: "Tests failing on PR but pass locally"**
```bash
# Check if you committed all necessary files
git status

# Check CI/CD logs
gh run list --branch [feature-branch]
gh run view [run-id]

# Common causes:
# - Missing dependency in package.json or pyproject.toml
# - Environment variable not set in CI/CD
# - Database migration not included
```

**Issue: "Merge conflicts"**
```bash
# Update your branch with main
git checkout [feature-branch]
git pull origin main

# Git will show conflict markers in files
# Open conflicted files and resolve manually
# Look for <<<<<<, ======, >>>>>> markers

# After resolving conflicts:
git add .
git commit -m "Resolve merge conflicts with main"
git push origin [feature-branch]
```

**Issue: "Cannot delete branch - PR not merged"**
```bash
# Force delete local branch (use with caution)
git branch -D [feature-branch-name]

# Delete remote branch manually
git push origin --delete [feature-branch-name]

# ONLY do this if you're certain the PR is abandoned
```

#### PR Best Practices

**DO:**
- ✅ Create PRs for all non-trivial changes
- ✅ Keep PRs focused on single feature/fix
- ✅ Write clear PR descriptions with context
- ✅ Link related issues with "Closes #", "Fixes #", "Relates to #"
- ✅ Ensure all tests pass before creating PR
- ✅ Review your own PR before asking others
- ✅ Respond promptly to review feedback
- ✅ Use draft PRs for work-in-progress if feedback needed early

**DON'T:**
- ❌ Create massive PRs with multiple unrelated changes
- ❌ Merge without testing
- ❌ Ignore failing tests or CI/CD checks
- ❌ Force push to main branch
- ❌ Delete branches before verifying merge
- ❌ Skip PR process for "quick fixes" (they often aren't quick)
- ❌ Merge your own PRs without review (if team project)

#### Integration with BMAD Workflow

**Explore Phase PRs:**
- Type: `docs` or `research`
- Content: Research findings, exploratory code, proof of concepts
- Merge to: `develop` or feature-specific branch (not directly to `main`)

**Plan Phase PRs:**
- Type: `docs` or `plan`
- Content: PRD updates, architecture changes, story refinements
- Merge to: `main` (documentation changes) or `develop`

**Execute Phase PRs:**
- Type: `feature`, `bug-fix`, or `refactor`
- Content: Implementation code, tests, configuration
- Merge to: `develop` first, then `main` after verification

**Multi-Phase PRs:**
- For refactoring that spans phases (like execute/ directory move)
- Include comprehensive verification checklist in PR
- Document phase impact in PR description
```

---

## Proposed Documentation Files

### 1. docs/CONTRIBUTING.md (New File)

**Purpose:** Public-facing contribution guidelines for GitHub
**Location in project:** `[project-root]/docs/CONTRIBUTING.md`

**Full Content:**

```markdown
# Contributing to [Project Name]

Thank you for considering contributing to this project! This document provides guidelines for contributing code, documentation, and other improvements.

## Getting Started

1. **Fork the repository** (if external contributor)
2. **Clone your fork** or the main repository
3. **Create a feature branch** from `main` or `develop`
4. **Make your changes** following our coding standards
5. **Test your changes** thoroughly
6. **Submit a pull request**

## Development Setup

### Prerequisites
- Python 3.12+ (for Python projects) OR Node.js 18+ (for Node.js projects)
- UV package manager (Python) OR npm (Node.js)
- Git
- GitHub CLI (`gh`) recommended

### Installation
```bash
# Clone the repository
gh repo clone [owner]/[project-name]
cd [project-name]

# Python projects:
cd execute
uv sync

# Node.js projects:
npm install
```

### Running Tests
```bash
# Python projects:
cd execute
uv run pytest

# Node.js projects:
npm test
```

## Pull Request Process

### Before Creating a PR

1. **Ensure all tests pass** locally
2. **Update documentation** if you changed functionality
3. **Add tests** for new features
4. **Follow coding style** of the project
5. **Commit with clear messages** describing your changes

### Creating a PR

1. **Push your branch** to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR** using GitHub CLI:
   ```bash
   gh pr create --title "Type: Brief description" --body "Detailed description"
   ```

3. **Fill out PR template** completely (auto-populated)

4. **Link related issues** using "Closes #123" or "Fixes #123"

### PR Title Format

Use conventional commit format for PR titles:

- `Feature: Add user authentication`
- `Fix: Resolve database connection timeout`
- `Refactor: Reorganize utility functions`
- `Docs: Update API documentation`
- `Test: Add integration tests for auth module`

### Code Review Process

1. **Wait for automated checks** (if CI/CD configured)
2. **Respond to reviewer feedback** promptly
3. **Make requested changes** in new commits
4. **Re-request review** after addressing feedback
5. **Squash commits** before merge (optional)

## Coding Standards

### Python Projects
- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings for public functions/classes
- Aim for 90%+ test coverage
- Use `black` for formatting (if configured)

### Node.js Projects
- Follow Airbnb JavaScript Style Guide
- Use ES6+ features
- Write JSDoc comments for complex functions
- Aim for 80%+ test coverage
- Use `prettier` for formatting (if configured)

## Testing Guidelines

### Writing Tests
- **Unit tests:** Test individual functions/classes in isolation
- **Integration tests:** Test module interactions
- **End-to-end tests:** Test full user workflows (if applicable)

### Test Naming
- Use descriptive test names: `test_user_login_with_invalid_password`
- Group related tests in test classes or describe blocks
- Test both happy path and edge cases

### Test Coverage
- Aim for high coverage but prioritize meaningful tests
- Don't test third-party libraries
- Focus on business logic and critical paths

## Documentation

### Code Comments
- Comment WHY, not WHAT
- Use docstrings for functions, classes, modules
- Keep comments up-to-date with code changes

### Markdown Documentation
- Update README.md for user-facing changes
- Update docs/ folder for technical documentation
- Use clear headings and examples

## Issue Reporting

### Bug Reports
Use the bug report template and include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node version, etc.)
- Screenshots (if applicable)

### Feature Requests
Use the feature request template and include:
- Problem you're trying to solve
- Proposed solution
- Alternative solutions considered
- Additional context

## BMAD-Specific Guidelines

This project follows the BMAD (Breakthrough Method for AI-driven Agile Development) methodology:

### Project Structure
- `explore/` - Research and discovery (not in git)
- `plan/` - Planning documents (not in git)
- `execute/` - Implementation code (in git)
- `docs/` - PRD and architecture (in git)

### Development Workflow
1. **Explore phase:** Research and prototype
2. **Plan phase:** Define requirements and architecture
3. **Execute phase:** Implement with tests

### Story Development
- Stories documented in `docs/stories/`
- Each story has clear acceptance criteria
- Implementation in `execute/` directory

## Questions?

- Check existing issues and PRs first
- Ask in discussions or issue comments
- Contact maintainers via email (see README)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).
```

---

### 2. .github/pull_request_template.md (New File)

**Purpose:** Auto-populates PR description when creating PRs on GitHub
**Location in project:** `[project-root]/.github/pull_request_template.md`

**Full Content:**

```markdown
## Summary
<!-- Briefly describe what this PR does in 1-2 sentences -->


## Changes Made
<!-- Detailed list of changes -->
-
-
-

## Type of Change
<!-- Check all that apply -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (code change that neither fixes a bug nor adds a feature)
- [ ] Documentation update
- [ ] Test addition or modification
- [ ] Configuration change

## Testing
<!-- Describe the tests you ran and how to reproduce them -->

### Test Results
- [ ] All unit tests passing (`pytest` or `npm test`)
- [ ] All integration tests passing
- [ ] Manual testing completed
- [ ] No regressions found

### How to Test
<!-- Provide steps for reviewers to test your changes -->
1.
2.
3.

## Related Issues
<!-- Link related issues using GitHub keywords -->
Closes #
Fixes #
Relates to #

## BMAD Phase
<!-- Which BMAD phase does this PR relate to? -->
- [ ] Explore - Research and discovery
- [ ] Plan - Planning and design
- [ ] Execute - Implementation

## Checklist
<!-- Check all that apply -->
- [ ] My code follows the project's coding standards
- [ ] I have added tests that prove my fix/feature works
- [ ] All new and existing tests pass
- [ ] I have updated the documentation accordingly
- [ ] My changes generate no new warnings
- [ ] I have added/updated comments for complex logic
- [ ] Any dependent changes have been merged and published

## Breaking Changes
<!-- If this introduces breaking changes, describe them and migration path -->


## Screenshots
<!-- If applicable, add screenshots to help explain your changes -->


## Additional Notes
<!-- Any additional information reviewers should know -->


---
🤖 PR created with [Claude Code](https://claude.com/claude-code)
```

---

### 3. user-context/github-pr-workflow.md (New File)

**Purpose:** Personal reference for Claude Code BMAD workflow integration
**Location in project:** `[project-root]/user-context/github-pr-workflow.md`

**Full Content:**

```markdown
# GitHub PR Workflow - Personal BMAD Reference

**Purpose:** Step-by-step PR workflow for Claude Code sessions
**Audience:** Claude Code Agent (me!)
**Context:** BMAD projects with GitHub integration

---

## Quick Reference Commands

### Create PR
```bash
gh pr create --title "Type: Description" --body "..." --base main --head feature-branch
```

### Merge PR
```bash
gh pr merge [number] --squash --delete-branch
```

### Review PR
```bash
gh pr checkout [number]  # Test locally
gh pr review [number] --approve --body "LGTM"
```

---

## Common Workflows

### Scenario 1: Feature Complete - Ready for PR

**Context:** User says "Feature is complete, create a PR"

**Execute these steps:**

1. **Verify tests pass:**
   ```bash
   cd execute && uv run pytest
   ```

2. **Check git status:**
   ```bash
   git status
   # If uncommitted changes, commit them first
   ```

3. **Push to remote:**
   ```bash
   git push origin $(git branch --show-current)
   ```

4. **Create PR:**
   ```bash
   gh pr create --title "Feature: [description]" --body "$(cat <<'EOF'
   ## Summary
   [Auto-generate from commits]

   ## Testing
   - All tests passing
   - Manual verification completed

   Closes #[issue-number]
   EOF
   )"
   ```

5. **Show PR URL to user:**
   ```bash
   gh pr view --web
   ```

---

### Scenario 2: Bug Fix - Quick PR

**Context:** User found and fixed a bug

**Execute these steps:**

1. **Ensure on feature branch:**
   ```bash
   git checkout -b fix/bug-description  # If not already on branch
   ```

2. **Commit fix:**
   ```bash
   git add .
   git commit -m "Fix: [description]"
   ```

3. **Run tests:**
   ```bash
   cd execute && uv run pytest
   ```

4. **Push and create PR:**
   ```bash
   git push origin fix/bug-description
   gh pr create --title "Fix: [description]" --body "Fixes #[issue]"
   ```

---

### Scenario 3: Refactoring - Large PR

**Context:** Major refactoring with multiple commits

**Execute these steps:**

1. **Review all commits:**
   ```bash
   git log origin/main..HEAD --oneline
   ```

2. **Ensure documentation updated:**
   - Check if README needs updates
   - Check if docs/ files need updates

3. **Run full test suite:**
   ```bash
   cd execute
   uv run pytest --cov
   # Verify coverage maintained or improved
   ```

4. **Create comprehensive PR:**
   ```bash
   gh pr create --title "Refactor: [description]" --body "$(cat <<'EOF'
   ## Summary
   [Explain WHY refactoring was needed]

   ## Changes Made
   [List major changes from git log]

   ## Testing
   - All 190 tests passing
   - 99% coverage maintained
   - CLI tested manually

   ## Verification
   [List verification steps completed]
   EOF
   )"
   ```

---

### Scenario 4: Documentation Only

**Context:** Only docs changed, no code

**Execute these steps:**

1. **Verify only docs changed:**
   ```bash
   git diff origin/main..HEAD --name-only
   # Should only show .md files or docs/ folder
   ```

2. **Create docs PR:**
   ```bash
   gh pr create --title "Docs: [description]" --body "Documentation update only, no code changes"
   ```

3. **Merge immediately (if solo project):**
   ```bash
   gh pr merge --squash --delete-branch
   ```

---

## Decision Trees

### Should I Create a PR?

```
Is this a software project with GitHub integration?
  NO → Don't create PR, just commit to main
  YES ↓

Is the change trivial (typo fix, comment update)?
  YES → Commit directly to main (user preference dependent)
  NO ↓

Are all tests passing?
  NO → Fix tests first, then revisit
  YES ↓

Is the work complete or is this WIP?
  WIP → Ask user if they want draft PR
  COMPLETE ↓

CREATE PR ✓
```

### Which Merge Strategy?

```
Is this multiple related commits that tell a story?
  YES → Use --merge (preserve history)
  NO ↓

Is this many small commits with messy messages?
  YES → Use --squash (clean history)
  NO ↓

Is this a single commit already?
  YES → Use --rebase (linear history)
  NO ↓

DEFAULT: Use --squash (safest choice)
```

---

## Error Recovery

### "Your branch is behind main"
```bash
git pull origin main
# Resolve conflicts if any
git push origin feature-branch
```

### "Tests failing on CI but pass locally"
```bash
# Check CI logs
gh run list --branch feature-branch
gh run view [run-id]

# Common fixes:
# 1. Missing dependency in package.json/pyproject.toml
# 2. Environment variable not set in CI
# 3. File paths wrong for CI environment
```

### "Merge conflicts"
```bash
git pull origin main
# Fix conflicts in editor
git add .
git commit -m "Resolve merge conflicts"
git push origin feature-branch
```

---

## BMAD Integration Notes

### Explore Phase
- PRs are rare (mostly local experimentation)
- If PR needed: Type = `docs` or `research`
- Merge to: `develop` branch (not main)

### Plan Phase
- PRs for: Documentation updates, architecture changes
- Type = `docs` or `plan`
- Merge to: `main` (docs are stable)

### Execute Phase
- PRs for: All code changes
- Type = `feature`, `fix`, `refactor`, `test`
- Merge to: `develop` → test → `main`

---

## When to Skip PR Process

**Skip PRs when:**
1. Solo project AND user explicitly says "just merge to main"
2. Typo fixes in documentation (user preference)
3. Project doesn't have GitHub integration
4. Working in thought project (no code)

**Always use PRs when:**
1. Team project (even if just 2 people)
2. User asks for "review" or "feedback"
3. Breaking changes or risky refactoring
4. Unsure if changes are correct
5. User says "create a PR"

---

## User Communication

### When Creating PR
**Tell user:**
- "I've created PR #[number] for [feature/fix]"
- "PR URL: [url]"
- "Would you like me to merge it or would you prefer to review first?"

### After Merging PR
**Tell user:**
- "PR #[number] merged successfully"
- "Changes are now on main branch"
- "Feature branch deleted"

### If Tests Fail
**Tell user:**
- "Tests are failing: [brief description]"
- "Should I fix the issues or would you like to investigate?"

---

## Automation Opportunities

### Auto-merge for docs-only PRs
```bash
# Check if only docs changed
if git diff origin/main..HEAD --name-only | grep -qv '\.md$\|^docs/'; then
  echo "Code changes detected, needs review"
else
  gh pr merge --squash --delete-branch
  echo "Docs-only PR auto-merged"
fi
```

### Auto-create PR after commit
```bash
# After committing a fix/feature
git push origin $(git branch --show-current)
gh pr create --fill  # Uses commit message as PR description
```

---

## Remember

- ✅ PRs create formal record for future reference
- ✅ PRs enable GitHub features (comments, reviews, checks)
- ✅ PRs make collaboration easier
- ✅ PRs don't slow down solo development (quick to merge)
- ❌ Don't skip PRs "to save time" (they save time later)
```

---

## Summary

### What Gets Added Where

1. **Workspace CLAUDE.md (Line 289):** New section "Pull Request (PR) Workflow with BMAD Integration"
   - Complete step-by-step PR process for Claude to execute
   - Integration with BMAD phases
   - Troubleshooting common issues

2. **Project docs/CONTRIBUTING.md:** Public contribution guide
   - For external contributors and team members
   - Technical setup and coding standards

3. **Project .github/pull_request_template.md:** Auto-populating PR template
   - Ensures consistent PR descriptions
   - Checklists for verification

4. **Project user-context/github-pr-workflow.md:** Claude's personal reference
   - Quick commands
   - Decision trees
   - BMAD-specific guidance

### Implementation Plan

1. Create feature request issue in Claude-Code-Workspace repo
2. Include all four proposed additions in issue body
3. Specify exact insertion points for each
4. User (or Claude in future session) implements from issue

---

**End of Recommendations Document**
