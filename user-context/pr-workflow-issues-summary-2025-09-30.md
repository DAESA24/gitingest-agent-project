# Pull Request Workflow - GitHub Issues Summary

**Date:** 2025-09-30
**Target Repository:** Claude-Code-Workspace
**Purpose:** Add PR workflow automation to workspace

---

## Issue #1: Add PR Workflow Automation to Workspace CLAUDE.md

### Issue Type
Feature Request

### Title
```
Feature: Add PR workflow automation to workspace CLAUDE.md
```

### Labels
- `enhancement`
- `documentation`
- `workspace-config`

### Priority
**High** - Core functionality for automated PR creation and management

### Description

Add comprehensive Pull Request workflow instructions to workspace-level CLAUDE.md file to enable Claude Code to automatically create, manage, and merge PRs in GitHub-integrated BMAD projects.

This enhancement adds two key capabilities:
1. **PR Execution Workflow** - Instructions for Claude to create and manage PRs during development
2. **Project Setup Enhancement** - Instructions for Claude to auto-create PR documentation when setting up new GitHub-integrated projects

---

### Part 1: PR Execution Workflow (New Section)

**Location:** Insert at line 289 in `CLAUDE.md` (between "Sub-Project Workflow Integration" and "ADHD Support Framework")

**Section Header:**
```markdown
### Pull Request (PR) Workflow with BMAD Integration
```

**Content:** [See full section text below - approximately 500 lines]

**What This Adds:**
- Step-by-step PR creation process with explicit commands
- Pre-PR verification checklist (tests, git status, commits)
- PR merge process with strategy guidelines (squash/merge/rebase)
- PR review process for reviewers
- Troubleshooting common PR issues
- Integration with BMAD phases (Explore/Plan/Execute)
- Best practices and anti-patterns
- Decision trees for when to create PRs and which merge strategy to use

**Audience:** Claude Code Agent (written explicitly for AI interpretation)

**Key Features:**
- `VERIFY:` markers after commands showing expected output
- `INTERPRET OUTPUT:` sections explaining how to read results
- `IMPORTANT:` flags for critical steps
- `DO/DON'T` lists for clear guidance
- Explicit placeholder replacement instructions
- Error recovery procedures with exact commands

---

### Part 2: Project Setup Enhancement (Modify Existing Section)

**Location:** Modify existing section at lines 70-127 ("BMAD Installation Process - GitHub-Integrated")

**Insert New Step After Line 88 (after "Create BMAD Phase Directories"):**

```markdown
**Step 2.6: Create PR Documentation Files (GitHub-Integrated Only)**
- **CRITICAL:** Only execute this step if GitHub integration confirmed in Step 1
- Copy PR documentation templates from workspace templates directory
- Create three files in the new project from templates:

**Execute these commands:**
```bash
# Ensure .github directory exists
mkdir -p .github

# Copy CONTRIBUTING.md template to docs/
cp "../.templates/github-pr-workflow/CONTRIBUTING.md.template" \
   "docs/CONTRIBUTING.md"

# VERIFY: File exists
ls -la docs/CONTRIBUTING.md

# Copy pull_request_template.md to .github/
cp "../.templates/github-pr-workflow/pull_request_template.md.template" \
   ".github/pull_request_template.md"

# VERIFY: File exists
ls -la .github/pull_request_template.md

# Copy github-pr-workflow.md to user-context/
cp "../.templates/github-pr-workflow/github-pr-workflow.md.template" \
   "user-context/github-pr-workflow.md"

# VERIFY: File exists
ls -la user-context/github-pr-workflow.md
```

**Verify all three files created:**
- `docs/CONTRIBUTING.md` - Public contribution guidelines
- `.github/pull_request_template.md` - Auto-populating PR template
- `user-context/github-pr-workflow.md` - Claude's quick reference

**If any file missing:** Stop and report error to user before proceeding.

**Customize template placeholders:**
After copying templates, replace these placeholders in all three files:
- `[Project Name]` → Actual project name
- `[project-name]` → Kebab-case project name
- `[owner]` → GitHub username/org name
- `[project-root]` → Actual project root path

**Note:** Templates contain generic content. User may want to customize further after project creation.
```

---

### Full PR Workflow Section Content

**Complete text to insert at line 289:**

[FULL 500-LINE SECTION CONTENT HERE - Including all the content from the recommendations document:
- When to Create a Pull Request
- PR Creation Process - Step by Step (Steps 1-6)
- PR Merge Process - Step by Step (Steps 1-4)
- PR Review Process (For Reviewers)
- Troubleshooting Common PR Issues
- PR Best Practices (DO/DON'T lists)
- Integration with BMAD Workflow
]

*(Full content available in pr-workflow-recommendations-2025-09-30.md)*

---

### Acceptance Criteria

**Part 1: PR Workflow Section**
- [ ] New section "Pull Request (PR) Workflow with BMAD Integration" added at line 289
- [ ] Section includes all 7 subsections (When to Create, Creation Process, Merge Process, Review Process, Troubleshooting, Best Practices, BMAD Integration)
- [ ] All commands include VERIFY markers
- [ ] All placeholders clearly marked with [brackets]
- [ ] No conflicts with existing sections
- [ ] Markdown formatting correct (headers, code blocks, lists)

**Part 2: Project Setup Enhancement**
- [ ] New Step 2.6 added after "Create BMAD Phase Directories"
- [ ] Step only executes for GitHub-integrated projects
- [ ] All three file copy commands included
- [ ] Verification commands after each copy
- [ ] Placeholder replacement instructions clear
- [ ] Error handling instructions included

**Testing:**
- [ ] Claude can read and understand the new instructions
- [ ] Instructions are clear enough for autonomous execution
- [ ] No ambiguity in command sequences
- [ ] Decision points have clear logic

---

### Implementation Notes

**File to Modify:** `C:\Users\drewa\My Drive\Claude Code Workspace\CLAUDE.md`

**Backup First:**
```bash
cd "C:\Users\drewa\My Drive\Claude Code Workspace"
cp CLAUDE.md CLAUDE-backup-$(date +%Y-%m-%d).md
```

**Line Numbers:**
- Insert Part 1 at line 289
- Modify Part 2 between lines 70-127 (add Step 2.6 after line 88)

**Testing After Implementation:**
1. Create a test GitHub-integrated project
2. Verify Claude auto-creates the three PR documentation files
3. Verify Claude can create a PR using the new workflow instructions
4. Verify Claude can merge a PR using the instructions

---

### Related Documentation

- **Full recommendations:** `Software Projects/gitingest-agent-project/user-context/pr-workflow-recommendations-2025-09-30.md`
- **Templates created in:** Issue #2 (dependency)

---

### Dependencies

**Requires:** Issue #2 (PR Documentation Templates) completed first

**Why:** Step 2.6 copies templates from `.templates/github-pr-workflow/` directory which is created in Issue #2.

**Implementation Order:**
1. Complete Issue #2 (create templates)
2. Complete Issue #1 Part 1 (add PR workflow section)
3. Complete Issue #1 Part 2 (add project setup step)
4. Test with a new project creation

---

---

## Issue #2: Create PR Documentation Templates in Workspace

### Issue Type
Feature Request

### Title
```
Feature: Create PR documentation templates in workspace
```

### Labels
- `enhancement`
- `documentation`
- `templates`

### Priority
**Medium** - Required for Issue #1 but doesn't block current projects

### Description

Create reusable PR documentation templates in workspace that get automatically copied into new GitHub-integrated BMAD projects during setup.

These templates provide consistent PR workflow documentation across all projects and serve as the source for auto-generated documentation when Claude creates new projects.

---

### Directory Structure to Create

```
Claude Code Workspace/                              # Workspace root
├── .templates/                                     # NEW - Template storage directory
│   └── github-pr-workflow/                        # NEW - PR workflow templates
│       ├── CONTRIBUTING.md.template               # NEW - Contribution guidelines
│       ├── pull_request_template.md.template      # NEW - PR template for GitHub
│       └── github-pr-workflow.md.template         # NEW - Quick reference for Claude
```

**Location:** `C:\Users\drewa\My Drive\Claude Code Workspace\.templates\github-pr-workflow\`

---

### Template Files to Create

#### File 1: CONTRIBUTING.md.template

**Purpose:** Public-facing contribution guidelines for GitHub projects
**Copied to:** `[project-root]/docs/CONTRIBUTING.md` during project setup
**Size:** ~200 lines

**Content:** [See full template below]

**Placeholders to Replace on Copy:**
- `[Project Name]` - User-facing project name
- `[owner]` - GitHub username or organization
- `[project-name]` - Kebab-case project name

**Sections Included:**
- Getting Started
- Development Setup (Prerequisites, Installation, Running Tests)
- Pull Request Process
- Coding Standards (Python/Node.js specific)
- Testing Guidelines
- Documentation Standards
- Issue Reporting (Bug Reports, Feature Requests)
- BMAD-Specific Guidelines
- Questions/Contact Info

---

#### File 2: pull_request_template.md.template

**Purpose:** Auto-populating PR description template for GitHub UI
**Copied to:** `[project-root]/.github/pull_request_template.md` during project setup
**Size:** ~80 lines

**Content:** [See full template below]

**Placeholders to Replace on Copy:**
- None (template is generic and works for all projects)

**Sections Included:**
- Summary (text input)
- Changes Made (bullet list)
- Type of Change (checkboxes)
- Testing section (test results, how to test)
- Related Issues (GitHub keyword links)
- BMAD Phase (checkboxes)
- Checklist (verification items)
- Breaking Changes (if applicable)
- Screenshots (if applicable)
- Additional Notes

**GitHub Integration:**
- When user clicks "Create Pull Request" on GitHub, this template auto-fills the description box
- User fills in the bracketed sections
- Checkboxes provide structured verification

---

#### File 3: github-pr-workflow.md.template

**Purpose:** Quick reference guide for Claude Code during PR operations
**Copied to:** `[project-root]/user-context/github-pr-workflow.md` during project setup
**Size:** ~350 lines

**Content:** [See full template below]

**Placeholders to Replace on Copy:**
- `[project-name]` - Used in example commands

**Sections Included:**
- Quick Reference Commands (common operations)
- Common Workflows (4 scenarios with step-by-step)
  - Scenario 1: Feature Complete - Ready for PR
  - Scenario 2: Bug Fix - Quick PR
  - Scenario 3: Refactoring - Large PR
  - Scenario 4: Documentation Only
- Decision Trees (when to create PR, which merge strategy)
- Error Recovery (common issues and fixes)
- BMAD Integration Notes (phase-specific guidance)
- When to Skip PR Process
- User Communication (what to tell user)
- Automation Opportunities

**Audience:** Claude Code Agent (quick lookup during PR operations)

---

### Full Template File Contents

#### CONTRIBUTING.md.template

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

#### pull_request_template.md.template

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

#### github-pr-workflow.md.template

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
   - All tests passing
   - Coverage maintained
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

## Remember

- ✅ PRs create formal record for future reference
- ✅ PRs enable GitHub features (comments, reviews, checks)
- ✅ PRs make collaboration easier
- ✅ PRs don't slow down solo development (quick to merge)
- ❌ Don't skip PRs "to save time" (they save time later)
```

---

### Acceptance Criteria

**Directory Structure:**
- [ ] `.templates/` directory created in workspace root
- [ ] `github-pr-workflow/` subdirectory created inside `.templates/`
- [ ] All three template files created with `.template` extension

**Template Files:**
- [ ] `CONTRIBUTING.md.template` created (~200 lines)
- [ ] `pull_request_template.md.template` created (~80 lines)
- [ ] `github-pr-workflow.md.template` created (~350 lines)

**Content Quality:**
- [ ] All placeholders clearly marked with [brackets]
- [ ] Markdown formatting correct in all templates
- [ ] Code blocks properly formatted
- [ ] No broken links or references
- [ ] Templates are generic enough for any project

**Git Tracking:**
- [ ] `.templates/` directory added to workspace git repo
- [ ] All three template files committed
- [ ] Templates pushed to remote

**Testing:**
- [ ] Can copy templates to a test project
- [ ] Placeholder replacement works correctly
- [ ] Templates render correctly on GitHub

---

### Implementation Commands

```bash
# Navigate to workspace root
cd "C:\Users\drewa\My Drive\Claude Code Workspace"

# Create directory structure
mkdir -p .templates/github-pr-workflow

# Create template files (content from above)
# File 1: CONTRIBUTING.md.template
cat > .templates/github-pr-workflow/CONTRIBUTING.md.template <<'EOF'
[Full CONTRIBUTING.md.template content here]
EOF

# File 2: pull_request_template.md.template
cat > .templates/github-pr-workflow/pull_request_template.md.template <<'EOF'
[Full pull_request_template.md.template content here]
EOF

# File 3: github-pr-workflow.md.template
cat > .templates/github-pr-workflow/github-pr-workflow.md.template <<'EOF'
[Full github-pr-workflow.md.template content here]
EOF

# Verify all files created
ls -la .templates/github-pr-workflow/

# Add to git
git add .templates/
git commit -m "Add PR workflow documentation templates"
git push origin main
```

---

### Usage After Implementation

**Automatic Usage (via Issue #1):**
When Claude creates a new GitHub-integrated project, Step 2.6 will automatically copy these templates to the project.

**Manual Usage:**
User can manually copy templates to existing projects:
```bash
# From any project directory
cp "../.templates/github-pr-workflow/CONTRIBUTING.md.template" \
   "docs/CONTRIBUTING.md"

cp "../.templates/github-pr-workflow/pull_request_template.md.template" \
   ".github/pull_request_template.md"

cp "../.templates/github-pr-workflow/github-pr-workflow.md.template" \
   "user-context/github-pr-workflow.md"

# Customize placeholders in the copied files
```

---

### Related Documentation

- **Full recommendations:** `Software Projects/gitingest-agent-project/user-context/pr-workflow-recommendations-2025-09-30.md`
- **Dependent issue:** Issue #1 (uses these templates)

---

### Implementation Order

**Must complete this issue BEFORE Issue #1** because Issue #1's Step 2.6 references these template files.

**Recommended approach:**
1. Create Issue #2 (this issue)
2. Implement Issue #2 (create templates)
3. Test templates by manually copying to test project
4. Create Issue #1
5. Implement Issue #1 (add workflow to CLAUDE.md)
6. Test full workflow with new project creation

---

---

## Summary

### Two Issues Created

**Issue #1: Add PR Workflow Automation to Workspace CLAUDE.md**
- Priority: High
- Adds ~500 lines of PR workflow instructions
- Adds Step 2.6 to project setup (auto-create PR docs)
- Depends on: Issue #2

**Issue #2: Create PR Documentation Templates in Workspace**
- Priority: Medium (but implement first)
- Creates `.templates/github-pr-workflow/` directory
- Creates 3 template files (~630 lines total)
- No dependencies

### Implementation Order

1. ✅ Create Issue #2 first
2. ✅ Implement Issue #2 (create templates)
3. ✅ Create Issue #1 second
4. ✅ Implement Issue #1 (add to CLAUDE.md)
5. ✅ Test with new project creation

---

**End of Issues Summary**
