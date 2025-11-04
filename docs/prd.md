# GitIngest Agent - Product Requirements Document

- **Version:** 1.3
- **Date:** 2025-11-04
- **Status:** v1.0.0 Complete ✅ | v1.1.0 Complete ✅ | v2.0.0 Proposed 📋
- **Current Release:** v1.1.0 (Multi-Location Output)
- **Next Release:** v2.0.0 (TOON Format + Multi-Agent Architecture)
- **Document Owner:** Product Manager

---

## Executive Summary

GitIngest Agent is an automated CLI tool that eliminates manual friction in GitHub repository analysis by intelligently routing extraction workflows based on token size limits. This Phase 1 implementation is a **high-fidelity clone** of a proven design demonstrated in the AI LABS video "Bash Apps Are INSANE... A New Way To Use Claude Code," where the creator built a similar tool in approximately 2 hours.

**Core Value Proposition:** Replace manual workflow (GitIngest → token checking → Claude Desktop) with automated Claude Code agent that handles entire process from GitHub URL to analyzed output.

**Key Innovation:** Token-aware routing that automatically extracts full content for small repositories (< 200k tokens) or intelligently prompts for selective extraction on large repositories (≥ 200k tokens).

---

## 1. Vision & Problem Statement

### 1.1 The Problem

The video creator's original workflow for analyzing GitHub repositories had significant friction:

1. Use GitIngest CLI to convert repositories into LLM-readable text
2. **Manually check** if repository exceeds 200,000 token limit
3. If too large, **manually determine** which parts to extract (README, docs, specific code)
4. **Manually run** GitIngest again with filtering parameters
5. Paste result into Claude Desktop for analysis
6. Repeat entire process for each new repository

**Impact:** This manual workflow slows down content creation, research, and library integration workflows. The token checking step is particularly tedious and error-prone.

### 1.2 The Solution

GitIngest Agent automates the complete workflow through Claude Code integration:

- **Automatic token size checking** - No manual token counting required
- **Intelligent workflow routing** - Automatically chooses full vs. selective extraction
- **Interactive content selection** - For large repos, guides user through targeted extraction
- **Integrated analysis** - Claude Code analyzes content directly from extracted files
- **Persistent storage** - All data saved as structured files for future reference

### 1.3 Success Metrics

**Efficiency Gains:**
- Eliminate 100% of manual token checking
- Reduce repository analysis workflow from 5+ steps to 1 step (provide URL)
- Enable analysis of multiple repositories in a single Claude Code session

**Quality Improvements:**
- Prevent context overflow (token limit exceeded)
- Ensure relevant content extracted for large repositories
- Maintain complete extraction history in structured format

---

## 2. Target Users

### 2.1 Primary User Persona

**Developer/Content Creator:**
- Analyzing open-source repositories for understanding
- Researching implementation patterns for content creation
- Evaluating libraries for potential project integration
- Creating documentation about repository architecture/workflows

**Technical Profile:**
- Comfortable with command-line tools
- Works with GitHub repositories regularly
- Uses Claude Code for development workflows
- Values automation and efficiency

**Workflow Context:**
- Works within gitingest-agent-project directory
- Analyzes 3-10 repositories per work session
- Needs quick answers about installation, architecture, or usage
- Stores analysis results for future reference

### 2.2 Use Cases

**UC1: Quick Installation Guide Extraction**
- User needs to understand how to install/setup a library
- Provides GitHub URL to GitIngest Agent
- Agent extracts installation-relevant content
- Claude Code generates step-by-step installation guide

**UC2: Architecture Analysis for Large Framework**
- User analyzing a major framework (React, FastAPI, etc.)
- Repository exceeds 200k token limit
- Agent prompts for content type (architecture/core implementation)
- Extracts only relevant sections
- Claude Code explains architectural patterns

**UC3: Documentation Research for Content Creation**
- Content creator researching repository for video/article
- Agent extracts documentation and key code samples
- Analysis saved for reference during content creation
- Can re-run with different focus areas as needed

**UC4: Repeated Analysis of Same Repository**
- User analyzing repository multiple times with different focuses
- First pass: Installation guide
- Second pass: Architecture overview
- Third pass: Specific feature implementation
- All extractions stored in data/ folder for reference

---

## 3. User Stories

### Phase 1: Core Clone User Stories

**US1: Automatic Token Size Checking**
As a developer analyzing a GitHub repository,
I want the agent to automatically check token size without manual commands,
So that I don't waste time manually counting tokens or guessing repository size.

**Acceptance Criteria:**
- Agent executes check-size automatically on GitHub URL detection
- Token count displayed clearly (formatted with commas)
- Decision made automatically: "full extraction" or "selective extraction"
- No user confirmation required for size check

---

**US2: Seamless Full Extraction for Small Repos**
As a developer analyzing a small-to-medium repository (< 200k tokens),
I want the entire repository extracted automatically without prompts,
So that I can immediately proceed to analysis without friction.

**Acceptance Criteria:**
- Full extraction triggered automatically when token_count < 200,000
- Repository saved to data/[repo-name]/digest.txt
- Path confirmed to user after extraction
- No intermediate prompts before analysis stage

---

**US3: Guided Selective Extraction for Large Repos**
As a developer analyzing a large repository (≥ 200k tokens),
I want to see the repository structure and select specific content to extract,
So that I stay within token limits while getting relevant information.

**Acceptance Criteria:**
- Tree structure extracted and displayed when token_count ≥ 200,000
- User prompted: "What would you like to analyze?"
- Clear options provided: documentation, installation, code, auto
- Selected content extracted with appropriate filtering
- Extraction path confirmed to user

---

**US4: Token Overflow Prevention**
As a developer who selected "documentation" for a large repository,
I want the agent to verify the extracted content is still under the token limit,
So that I don't experience context overflow during analysis.

**Acceptance Criteria:**
- Token count checked after selective extraction
- If still > 200k: User prompted to narrow selection further
- Options provided: more specific filters, chunk strategy, or truncate
- Process repeats until content < 200k tokens
- Final token count displayed before analysis

---

**US5: Analysis Generation**
As a developer with extracted repository content,
I want Claude Code to analyze the content based on my specific needs,
So that I get actionable insights about installation, architecture, or implementation.

**Acceptance Criteria:**
- User prompted: "What type of analysis would you like?"
- Options: installation, workflow, architecture, custom
- Claude Code analyzes extracted content
- Analysis quality appropriate for selected type
- Results displayed in readable format

---

**US6: Optional Analysis Storage**
As a developer who generated valuable analysis,
I want to optionally save the analysis for future reference,
So that I don't lose insights when the conversation ends.

**Acceptance Criteria:**
- After analysis, user prompted: "Save this analysis?"
- If yes: Saved to analyze/[analysis-type]/[repo-name].md
- If no: Analysis displayed only (not persisted)
- Save path confirmed with full absolute path
- Saved files include metadata (date, token count, source)

---

**US7: Claude Code Workflow Automation**
As a developer using Claude Code,
I want to simply provide a GitHub URL and have the entire workflow execute automatically,
So that I don't need to remember or manually invoke each command.

**Acceptance Criteria:**
- GitHub URL pattern triggers workflow automatically
- No initial confirmation prompt ("Starting workflow...")
- Commands execute sequentially with context maintained
- Progress displayed at each step
- User prompted only at decision points (content selection, save confirmation)
- Workflow completes with summary of actions taken

---

## 4. Functional Requirements

### FR1: Token Size Checking

**Description:** Automatically count tokens in target repository to determine extraction strategy.

**Implementation:**
- Wrap GitIngest CLI with stdout output
- Parse token count from output or estimate from character count
- Apply decision logic: < 200k = full, ≥ 200k = selective
- Display formatted token count to user

**Command:** `gitingest-agent check-size <github-url>`

**Output Format:**
```
Checking repository size...
Token count: 145,000
Route: full extraction
```

**Error Handling:**
- Network errors: Inform user, offer retry
- Invalid URL: Display expected format
- Timeout: Inform user (likely very large repo)

**Dependencies:** GitIngest CLI (already installed)

**Priority:** P0 (Critical - determines all subsequent workflow)

---

### FR2: Full Extraction Workflow

**Description:** Extract entire repository content for repositories under token limit.

**Trigger:** token_count < 200,000

**Process:**
1. Create data/[repo-name]/ directory if needed
2. Execute: `gitingest <url> -o data/[repo-name]/digest.txt`
3. Confirm file saved with path
4. Display token count and file location
5. Proceed directly to analysis prompt

**Command:** `gitingest-agent extract-full <github-url>`

**Output Format:**
```
Extracting full repository...
✓ Saved to: data/fastapi/digest.txt
Token count: 145,000 tokens
```

**Storage Schema:**
```
data/
  [repo-name]/
    digest.txt          # Full repository content
    .metadata.json      # Extraction metadata (optional)
```

**Error Handling:**
- Directory creation failure: Display permission error, provide manual mkdir command
- GitIngest failure: Display error message, check network/URL
- Disk space: Check available space, warn if insufficient

**Priority:** P0 (Critical path for small repos)

---

### FR3: Selective Extraction Workflow

**Description:** Extract targeted repository content when full extraction exceeds token limit.

**Trigger:** token_count ≥ 200,000

**Process:**
1. Extract tree structure (minimal content, just file paths)
2. Save to data/[repo-name]/tree.txt
3. Display tree to user
4. Prompt: "What would you like to analyze?"
5. Map user choice to filter patterns
6. Execute selective extraction
7. **Critical:** Re-check token count
8. If still > 200k: Prompt for narrower selection (iterate)
9. Proceed to analysis when under limit

**Commands:**
- `gitingest-agent extract-tree <github-url>`
- `gitingest-agent extract-specific <github-url> --type <type>`

**Output Format:**
```
Repository exceeds token limit: 487,523 tokens
Extracting tree structure...

[Tree display]

What would you like to analyze?
1. Documentation only
2. Installation guide
3. Core implementation
4. README + key docs (auto)

Your choice: 1

Extracting documentation...
✓ Saved to: data/fastapi/docs-content.txt
Token count: 89,450 tokens
```

**Priority:** P0 (Critical path for large repos)

---

### FR4: Content Type Filtering

**Description:** Map user-friendly content types to GitIngest filter patterns.

**Supported Types:**

**Type: `docs`**
- Include: `docs/**/*`, `*.md`, `README*`, `*.rst`
- Exclude: `docs/examples/*`, `docs/archive/*`
- Use case: Understanding project documentation

**Type: `installation`**
- Include: `README*`, `INSTALL*`, `setup.py`, `pyproject.toml`, `package.json`, `docs/installation*`, `docs/getting-started*`
- Exclude: None
- Use case: Setting up project locally

**Type: `code`**
- Include: `src/**/*.py`, `lib/**/*` (adjust for language)
- Exclude: `tests/*`, `*_test.py`, `test_*.py`, `examples/*`
- Use case: Understanding implementation

**Type: `auto` (fallback)**
- Include: `README*`, `docs/**/*.md`
- Exclude: `docs/examples/*`
- Use case: General overview when user unsure

**Implementation:** Mapping function in storage module

**Priority:** P0 (Essential for selective extraction)

---

### FR5: Size Re-Check After Extraction

**Description:** Validate extracted content is under token limit to prevent overflow.

**Critical Issue (from V2 Spec):**
> "After retrieving the tree and documentation, I need another check to ensure the combined content doesn't exceed the limit again. Currently, it can overshoot."

**Implementation:**
```
Extract specific content
  ↓
Count tokens in result file
  ↓
If > 200k:
  - Display: "Content still exceeds limit: [count] tokens"
  - Display: "Target: 200,000 tokens"
  - Prompt: "Options: 1) Narrow selection, 2) Chunk strategy, 3) Proceed with partial"
  - Based on choice: Re-extract or proceed
```

**Priority:** P0 (Critical - prevents analysis failures)

**Test Cases:**
- Large documentation set that combined still exceeds 200k
- Multiple docs folders selected
- Code extraction with many large files

---

### FR6: Analysis Generation

**Description:** Generate analysis of extracted content based on user-specified type.

**Process:**
1. Read extracted content from data/[repo-name]/[file].txt
2. Prompt user: "What type of analysis would you like?"
3. Claude Code analyzes with focus on selected type
4. Display analysis results
5. Proceed to save prompt

**Analysis Types:**
- **Installation:** Step-by-step setup instructions, dependencies, configuration
- **Workflow:** How to use the library/tool, common patterns, examples
- **Architecture:** System design, component relationships, data flow
- **Custom:** User-specified analysis focus

**Quality Criteria:**
- Analysis addresses user's selected type
- Uses specific details from extracted content
- Actionable and concise
- Includes code examples where relevant

**Priority:** P1 (Important, but extraction more critical)

---

### FR7: Storage Management

**Description:** Manage file storage for extractions and analyses with clear organization.

**Directory Structure:**
```
gitingest-agent-project/
├── data/                          # Repository extractions
│   └── [repo-name]/              # One folder per repository
│       ├── digest.txt            # Full extraction (< 200k)
│       ├── tree.txt              # Tree structure (≥ 200k)
│       ├── docs-content.txt      # Selective: docs
│       ├── installation-content.txt  # Selective: installation
│       └── code-content.txt      # Selective: code
├── analyze/                       # Analysis outputs
│   ├── installation/             # Installation guides
│   │   └── [repo-name].md
│   ├── workflow/                 # Workflow documentation
│   │   └── [repo-name].md
│   ├── architecture/             # Architecture analyses
│   │   └── [repo-name].md
│   └── custom/                   # Custom analyses
│       └── [repo-name].md
```

**Features:**
- Automatic directory creation (mkdir -p behavior)
- Path validation before saves
- Absolute path confirmation to user
- Graceful handling of existing files (no overwrite without confirmation)

**Priority:** P0 (Critical for core functionality)

---

### FR8: CLAUDE.md Workflow Automation

**Description:** Define complete agent behavior in CLAUDE.md for automatic Claude Code execution.

**Trigger Pattern:** GitHub URL in user message (`https://github.com/...`)

**Workflow Steps:**
1. **Step 1:** Extract URL from message
2. **Step 2:** Execute check-size command
3. **Step 3:** Route based on token count
4. **Step 4a:** Full extraction (if < 200k) → Skip to Step 6
5. **Step 4b:** Tree extraction (if ≥ 200k) → Continue to Step 5
6. **Step 5:** User content selection → Specific extraction → Size re-check
7. **Step 6:** Analysis generation prompt
8. **Step 7:** Optional save to analyze/
9. **Step 8:** Completion summary

**Context Maintenance:**
- REPO_URL: GitHub URL being analyzed
- REPO_NAME: Extracted repository name
- TOKEN_COUNT: Current token count
- WORKFLOW_TYPE: "full" or "selective"
- EXTRACTION_PATH: Where content was saved
- ANALYSIS_TYPE: Type of analysis requested (if applicable)

**User Interaction Points:**
- **When to prompt:** Content selection (large repos), analysis type, save confirmation
- **When NOT to prompt:** Starting workflow, size checking, creating directories, extracting full repo

**Priority:** P0 (Essential for automation value proposition)

---

## 5. Technical Requirements

### TR1: Technology Stack

**Programming Language:** Python 3.12+

**Package Manager:** UV (10-100x faster than pip)
- Handles virtual environments automatically
- Project scaffolding
- Dependency management

**CLI Framework:** Click (≥8.1.0)
- Command grouping (parent command with subcommands)
- Argument and option parsing
- Error handling and user prompts
- Testing support via CliRunner

**External Tool:** GitIngest CLI
- Already installed via `uv tool install gitingest`
- Wrapped via subprocess calls
- No direct dependency in pyproject.toml

**Priority:** P0 (Foundation for all implementation)

---

### TR2: CLI Command Structure

**Parent Command:** `gitingest-agent`

**Subcommands:**

```bash
gitingest-agent check-size <github-url>
# Purpose: Count tokens, determine routing
# Output: Token count and route decision

gitingest-agent extract-full <github-url>
# Purpose: Extract entire repository
# Output: Path to digest.txt

gitingest-agent extract-tree <github-url>
# Purpose: Extract tree structure only
# Output: Path to tree.txt, displays tree

gitingest-agent extract-specific <github-url> --type <type>
# Purpose: Extract targeted content
# Options: --type [docs|installation|code|auto]
# Output: Path to [type]-content.txt
```

**Global Options (future consideration):**
- `--verbose`: Detailed output
- `--quiet`: Minimal output
- `--output-dir`: Custom output location (Phase 1.5)

**Entry Point Configuration:**
```toml
[project.scripts]
gitingest-agent = "cli:gitingest_agent"
```

**Priority:** P0 (User-facing interface)

---

### TR3: Project Structure

```
gitingest-agent-project/
├── .bmad-core/                    # BMAD framework (don't modify)
├── .venv/                         # UV virtual environment
├── .gitignore                     # Git ignore patterns
├── .python-version                # Python version (3.12)
├── data/                          # Repository extractions (created at runtime)
├── analyze/                       # Analysis outputs (created at runtime)
├── explore/                       # BMAD exploration (completed)
├── plan/                          # BMAD planning (in progress)
├── user-context/                  # Project requirements
├── cli.py                         # Main CLI entry point
├── token_counter.py              # Token counting logic
├── workflow.py                    # Workflow routing logic
├── storage.py                     # File storage management
├── extractor.py                   # GitIngest wrapper functions
├── tests/                         # Test suite
│   ├── test_cli.py
│   ├── test_token_counter.py
│   ├── test_workflow.py
│   └── test_storage.py
├── pyproject.toml                 # Project configuration
├── uv.lock                        # Dependency lockfile
├── CLAUDE.md                      # Agent automation instructions
└── README.md                      # User documentation
```

**Design Decision:** Flat structure (modules at root) for Phase 1 simplicity. Can refactor to src/ structure in future if project grows.

**Priority:** P0 (Required for implementation)

---

### TR4: Error Handling Strategy

**Network Errors:**
- GitIngest clone failures
- GitHub API rate limits
- Timeout on large repositories

**Response:**
- Clear error message
- Suggest corrective action
- Offer retry option
- Graceful workflow abort

**File System Errors:**
- Permission denied (directory creation)
- Disk space insufficient
- Path too long (Windows limitation)

**Response:**
- Explain issue in user-friendly terms
- Provide manual fix commands
- Exit cleanly

**Logic Errors:**
- Invalid GitHub URL format
- Token count still exceeds limit after multiple refinements
- Empty extraction result

**Response:**
- Validate inputs early
- Set maximum retry attempts
- Provide escape hatch (proceed anyway with warning)

**Priority:** P1 (Important for production quality)

---

### TR5: Testing Requirements

**Unit Tests:**
- Token counting accuracy (±10% tolerance)
- URL parsing and validation
- Filter pattern generation
- File path management

**Integration Tests:**
- Full workflow (small repo)
- Selective workflow (large repo)
- Size re-check iteration
- Error recovery scenarios

**Manual Tests:**
- Claude Code automation (CLAUDE.md triggers)
- User interaction flow (prompts and responses)
- Real repository analysis (Hello-World, FastAPI, React)

**Test Repositories:**
- Small: https://github.com/octocat/Hello-World (< 10k tokens)
- Medium: TBD (50-150k tokens)
- Large: https://github.com/fastapi/fastapi (> 400k tokens)

**Coverage Target:** 80%+ for core logic (token_counter, workflow, storage)

**Priority:** P1 (Essential for reliability)

---

## 6. Success Criteria

### 6.1 Functional Completeness

**Phase 1 is complete when:**

- [ ] All seven user stories have passing acceptance criteria
- [ ] All eight functional requirements implemented
- [ ] All five technical requirements met
- [ ] CLI commands work as specified
- [ ] CLAUDE.md automation triggers correctly
- [ ] Error handling covers major failure scenarios

### 6.2 Quality Gates

**Accuracy:**
- [ ] Token counting within ±10% of actual
- [ ] Workflow routing 100% correct at 200k threshold
- [ ] File saves to correct locations 100% of the time

**Reliability:**
- [ ] Handles network errors gracefully
- [ ] Recovers from token overflow correctly
- [ ] No crashes on invalid inputs

**Usability:**
- [ ] GitHub URL triggers workflow automatically
- [ ] User prompts clear and actionable
- [ ] Progress displayed at each step
- [ ] Paths confirmed with absolute paths

### 6.3 Validation Testing

**Test Scenario 1: Small Repository**
```
Input: https://github.com/octocat/Hello-World
Expected: Full extraction, no prompts until analysis
Verify: File saved to data/Hello-World/digest.txt
Result: Analysis generated successfully
```

**Test Scenario 2: Large Repository**
```
Input: https://github.com/fastapi/fastapi
Expected: Tree extraction, user prompted for content type
User selects: Documentation
Verify: Size re-check passes (< 200k)
Result: Analysis generated from docs only
```

**Test Scenario 3: Token Overflow Recovery**
```
Input: Large repo with extensive documentation
User selects: Documentation
Size check: Still > 200k after extraction
Expected: Agent prompts for narrower selection
User narrows: Installation docs only
Result: Under 200k, proceeds to analysis
```

**Test Scenario 4: Claude Code Automation**
```
User message: "Analyze https://github.com/user/repo"
Expected: No confirmation prompt, workflow begins immediately
Verify: Each command executes sequentially
Verify: Context maintained (token_count, repo_name)
Result: Complete workflow without manual intervention
```

### 6.4 Performance Benchmarks

**Token Counting:**
- Small repos (< 50k): < 15 seconds
- Medium repos (50-200k): < 60 seconds
- Large repos (> 200k): < 2 minutes

**Full Extraction:**
- Depends on repository size
- Network bound (clone time)
- Should complete within GitIngest's normal time

**Workflow Completion:**
- Small repo (no prompts): < 30 seconds total
- Large repo (with selection): < 3 minutes total

---

## 7. Known Limitations

### 7.1 Critical Issues (from V2 Spec)

**Issue 1: Token Overshoot After Selective Extraction**

**Description:** After extracting README + docs for large repo, combined content may still exceed 200k limit.

**Impact:** High - Can cause context overflow during analysis

**Mitigation:** Implement size re-check (FR5) with iterative refinement

**Status:** Identified in V2 spec, mitigation included in Phase 1 requirements

---

**Issue 2: Manual Testing Required for Workflow**

**Description:** Claude Code automation behavior cannot be fully unit tested; requires manual validation.

**Impact:** Medium - More time needed for testing phase

**Mitigation:**
- Create detailed manual test protocol
- Test with multiple real repositories
- Document breaking points discovered
- Iterate on CLAUDE.md prompts

**Status:** Expected, time allocated in development estimates

---

**Issue 3: CLAUDE.md Prompt Refinement**

**Description:** Workflow instructions may not be followed correctly on first attempt; requires iteration.

**Impact:** Medium - Extended testing/refinement phase

**Mitigation:**
- Use proven patterns from exploration research
- Test incremental workflow steps
- Maintain refinement log
- Start with specific, explicit instructions

**Status:** Expected, documented in V2 spec as largest time investment

---

### 7.2 GitIngest Constraints

**Constraint 1: File Processing Limit**
- GitIngest processes first 1000 files only
- No explicit warning when limit hit
- Impact: Very large repos may have incomplete content
- Mitigation: Document limitation, rarely affects targeted extraction

**Constraint 2: GitHub API Rate Limits**
- Without token: 60 requests/hour
- With token: 5000 requests/hour
- Impact: Repeated analysis of private repos may hit limit
- Mitigation: Consider adding GitHub token support (future enhancement)

**Constraint 3: Network Dependency**
- Requires internet connection
- Clone time varies by repo size
- Large repos (> 500 MB) may timeout
- Mitigation: Implement timeout handling, suggest selective extraction

---

## 8. Out of Scope (Phase 1.5 - Future)

### Explicitly NOT in Phase 1

These features are documented in the Requirements Addendum and planned for Phase 1.5:

**Multi-Location Output:**
- Saving analyses to other BMAD project directories
- BMAD project detection (checking for .bmad-core/)
- context/related-repos/ folder structure
- --output-dir CLI parameter

**Cross-Project Usage:**
- Working from directories other than gitingest-agent-project
- Dynamic path resolution based on current working directory
- Offering save location options

**Reason for Deferral:** Phase 1 focuses on replicating the proven video design. Multi-location features add complexity and should be validated after core functionality is solid.

**Architecture Note:** Storage layer should be designed to allow Phase 1.5 enhancement without major refactoring, but implementation is explicitly deferred.

---

## 9. Development Timeline

### 9.1 Estimates

**Original (Video Creator):** 2 hours total

**BMAD Approach (Phase 1):**
- Explore Phase: ✅ Complete (6 research documents)
- Plan Phase: 2 hours (PRD + Architecture)
- Execute Phase: 3-4 hours (Implementation + Testing)
- **Total Phase 1: 5-6 hours**

### 9.2 Phase Breakdown

**Plan Phase (Current):**
- [x] Exploration research complete
- [ ] PRD complete (this document)
- [ ] Architecture document
- [ ] CLAUDE.md draft

**Execute Phase:**
- [ ] Project setup (UV init, pyproject.toml)
- [ ] Core CLI structure (Click commands)
- [ ] Token counting implementation
- [ ] Workflow routing logic
- [ ] Storage management
- [ ] GitIngest wrapper functions
- [ ] CLAUDE.md finalization
- [ ] Testing and refinement

**Validation:**
- [ ] Manual test protocol execution
- [ ] V2 specification compliance check
- [ ] Breaking point documentation
- [ ] CLAUDE.md prompt refinement

### 9.3 Risk Factors

**Schedule Risks:**
- CLAUDE.md refinement may take longer than estimated
- Manual testing uncovers unexpected breaking points
- GitIngest behavior quirks require workarounds

**Mitigation:**
- Use exploration research patterns (proven)
- Start with explicit, specific CLAUDE.md instructions
- Test incrementally, not end-to-end first

---

## 10. Reference Documents

### Primary Requirements Source

**V2 Specification:** gitingest-agent-comprehensive-specification-v2.md
- Sections 1-7 (Phase 1 definition)
- Video transcript quotes
- Known issues and refinements
- BMAD development roadmap

### Exploration Research

**Technical Research:**
- click-framework-research.md - CLI patterns and examples
- gitingest-cli-capabilities.md - GitIngest usage and filtering
- token-counting-research.md - Token estimation methods
- uv-python-project-structure.md - Project setup and configuration

**Design Research:**
- workflow-design-notes.md - Workflow logic and decision trees
- claude-code-automation-patterns.md - CLAUDE.md best practices

### Future Phase Reference

**Phase 1.5 Requirements:** gitingest-agent-requirements-addendum-custom-enhancements.md
- Multi-location output capability
- Universal context folder standard
- Cross-project usage patterns

**Note:** Addendum features integrated into Phase 1.5 (Section 11.5 below) with simplified universal approach (no project-type detection needed).

---

## 11.5 v1.1.0 Release: Multi-Location Output

### 11.5.1 Overview

**Status:** ✅ Complete (Released 2025-11-04)

Version 1.1.0 extends GitIngest Agent with **universal multi-location output capability**, enabling the tool to save analysis outputs to any directory, not just gitingest-agent-project. This enhancement makes GitIngest Agent universally useful across all project types and workflows.

**Problem Statement:**

Phase 1.0 design saves extractions and analyses exclusively to:
- `gitingest-agent-project/data/` - Repository extractions
- `gitingest-agent-project/analyze/` - Analysis outputs

This limits utility to analyzing repositories for the GitIngest Agent project itself. To use analyses in another project, users must manually copy files between directories.

**Real-World Requirement:**

Users work across diverse project types:
- Software development (React apps, Python tools, BMAD projects)
- Knowledge management (Research, writing, Obsidian vaults)
- Learning and exploration (Tutorials, experiments, comparisons)
- Ad-hoc analysis (Temporary directories, quick investigations)

Each project needs analyzed repositories available as **local context** without manual file management.

**Value Proposition:**

- **Work from anywhere** - Analyze repos from any directory
- **Context where needed** - Analyses saved in the current project automatically
- **Universal standard** - `context/related-repos/` works everywhere (no configuration)
- **Zero manual file copying** - Tool handles everything automatically
- **One convention to learn** - Same structure across all project types
- **Backward compatible** - Phase 1.0 behavior preserved in gitingest-agent-project

**Example Scenario:**

```
Working on: react-component-test-project
Need to understand: React 19 new features
Want to analyze: https://github.com/facebook/react

Desired outcome:
→ Analysis saved to: react-component-test-project/context/related-repos/react-analysis.md
→ Available as context when working in that project
→ No directory switching or file copying required
```

### 11.5.2 User Stories

**User Story 11.5.1: Analyze Repo from Any Directory**

As a developer working in any project directory,
I want to analyze a related repository and save the analysis in my current directory's context folder,
So that the analysis is available as project context without switching directories or copying files.

**Acceptance Criteria:**
- [ ] GitIngest Agent works from ANY directory (not just BMAD projects)
- [ ] Automatically creates `context/related-repos/` in current directory if missing
- [ ] Saves analysis to `context/related-repos/<repo-name>-<analysis-type>.md`
- [ ] Analysis file includes metadata: analyzed date, token count, source repo
- [ ] Can run multiple analyses - each saves to separate file
- [ ] Universal convention works across software projects, knowledge projects, and ad-hoc directories

---

**User Story 11.5.2: Analyze Repo for GitIngest Agent Project**

As a developer improving the GitIngest Agent,
I want to analyze repositories related to the agent itself (Click, GitIngest, etc.),
So that I can reference implementation patterns while building the tool.

**Acceptance Criteria:**
- [ ] When in gitingest-agent-project directory, default behavior is Phase 1.0 spec
- [ ] Saves to `data/` and `analyze/` folders as designed
- [ ] No change to original workflow
- [ ] Phase 1.0 regression tests all pass

---

**User Story 11.5.3: Custom Output Location**

As a developer with specific organizational needs,
I want to specify exactly where analysis should be saved,
So that I have full control over file organization.

**Acceptance Criteria:**
- [ ] Can provide `--output-dir` parameter to CLI commands
- [ ] Agent validates path exists or asks to create it
- [ ] Saves analysis to specified location
- [ ] Works from any directory

---

**User Story 11.5.4: Universal Context Folder Standard**

As a developer managing multiple projects,
I want a consistent `context/related-repos/` folder structure across all my projects,
So that I always know where to find repository analysis regardless of project type.

**Acceptance Criteria:**
- [ ] Any project can have a `context/` folder (created automatically)
- [ ] `context/related-repos/` becomes universal standard for GitIngest analyses
- [ ] Works consistently across software projects, knowledge projects, and ad-hoc directories
- [ ] Folder structure documented in project README
- [ ] One convention to learn, works everywhere

### 11.5.3 Scope: What Phase 1.5 Changes (and What It Doesn't)

**IMPORTANT CLARIFICATION:**

Phase 1.5 is **ONLY** about changing where analysis files are saved. All Phase 1.0 workflow behavior remains completely unchanged.

**What Phase 1.5 Changes:**

- ✅ **Storage location detection** - Where to save output files
- ✅ **Folder creation** - Auto-create `context/related-repos/` if needed
- ✅ **File naming** - Adapt naming convention based on location
- ✅ **CLI parameter** - Add `--output-dir` option

**What Phase 1.5 Does NOT Change:**

- ❌ **Token size checking** - Still automatic, still uses 200k threshold
- ❌ **Workflow routing** - Still routes to full vs selective based on token count
- ❌ **Content selection** - For large repos, still prompts user for content type (docs/installation/code/auto)
- ❌ **Analysis type selection** - **ALWAYS prompts: "What type of analysis would you like?"** (installation/workflow/architecture/custom)
- ❌ **Analysis generation** - Same quality and depth regardless of directory
- ❌ **Extraction process** - GitIngest wrapping unchanged

**Critical User Experience Guarantee:**

Whether you run GitIngest Agent from:
- `gitingest-agent-project` directory
- Another BMAD project
- Any arbitrary directory
- With `--output-dir` parameter

**You will ALWAYS get:**
1. Token size check → routing decision
2. Full or selective extraction (based on size)
3. **"What type of analysis would you like?"** prompt ← UNIVERSAL
4. Claude Code analyzes with selected focus
5. Storage location prompt (Phase 1.5 addition)
6. Analysis saved to appropriate location

**The only difference is WHERE the analysis is saved at the end, not HOW it's generated.**

### 11.5.4 Technical Requirements

**TR6: Storage Location Abstraction**

**Current Architecture (Phase 1.0):**
```python
# Hardcoded paths
DATA_DIR = "data/"
ANALYZE_DIR = "analyze/"

def save_extraction(content, repo_name):
    path = f"{DATA_DIR}{repo_name}/digest.txt"
    save_file(path, content)
```

**Enhanced Architecture (Phase 1.5):**
```python
# Flexible path resolution - SIMPLIFIED UNIVERSAL APPROACH
class StorageManager:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or self._detect_output_location()

    def _detect_output_location(self):
        """Detect appropriate save location based on context"""
        cwd = Path.cwd()

        # Exception: If in gitingest-agent-project itself
        if cwd.name == "gitingest-agent-project":
            return cwd  # Use Phase 1.0 default structure (data/, analyze/)

        # Universal default: context/related-repos/ for ALL other directories
        context_dir = cwd / "context" / "related-repos"

        # Auto-create if doesn't exist
        if not context_dir.exists():
            print(f"Creating context/related-repos/ in current directory...")
            context_dir.mkdir(parents=True, exist_ok=True)

        return context_dir
```

**Key Technical Changes:**

- **StorageManager Class** - Abstraction layer for path resolution
- **Universal Default** - `./context/related-repos/` for ANY directory (except gitingest-agent-project)
- **No Project Detection** - No `.bmad-core/` checking needed (simpler logic)
- **Auto-Create Context Folder** - Always creates `context/related-repos/` if missing
- **Backward Compatibility** - Phase 1.0 behavior preserved ONLY in gitingest-agent-project
- **CLI Parameter** - `--output-dir` option for manual override always available

**Design Rationale:**

This simplified approach makes `context/related-repos/` a **universal best practice** across:
- BMAD projects (software development)
- Knowledge projects (research, writing)
- Personal projects (any use case)
- Ad-hoc directories (temporary analysis)

One convention, zero configuration, consistent everywhere.

**File Naming Conventions:**

**In gitingest-agent-project (Phase 1.0 behavior):**
```
analyze/
  installation/
    react.md
    fastapi.md
  workflow/
    react.md
  architecture/
    react.md
```

**In other BMAD projects (Phase 1.5 behavior):**
```
context/
  related-repos/
    react-installation.md          # Repo + analysis type
    react-architecture.md
    fastapi-workflow.md
    testing-library-overview.md
```

**Rationale:** GitIngest Agent project needs multiple analysis types organized by type. Other projects typically have 1-2 analyses per repo, so flat structure with descriptive names is more practical.

**Context Folder Standard:**

Proposed universal structure for ALL projects:
```
[Any Project Directory]/
├── context/                 # Universal context folder (auto-created)
│   ├── related-repos/      # GitIngest analyses (auto-created)
│   │   ├── [repo1]-[type].md
│   │   └── [repo2]-[type].md
│   ├── research/           # Other research materials (optional)
│   └── references/         # Documentation, specs, etc. (optional)
├── [your project files]
└── [your project structure]
```

**Universal Applicability:**

This structure works for:
- **Software projects** (BMAD, React, Python, etc.)
- **Knowledge projects** (Research, writing, Obsidian vaults)
- **Personal projects** (Learning, experiments, tutorials)
- **Ad-hoc directories** (Temporary analysis, comparisons)

**Benefits:**
- **Universal convention** - Same structure everywhere
- **Zero configuration** - Auto-creates on first use
- **One habit to learn** - Always check `context/related-repos/`
- **Extensible** - Can add other context subdirectories as needed
- **Predictable** - No project type detection required

### 11.5.4 Implementation Phases

Phase 1.5 implementation is estimated at **1-2 hours total** and breaks down into focused increments:

**Phase 1.5.1: Refactor Storage Layer (30 min)**

- Extract hardcoded paths to StorageManager class
- Add path detection logic
- Maintain Phase 1.0 behavior when in gitingest-agent-project
- Test Phase 1.0 regression (no behavior change yet)

**Phase 1.5.2: Add CLAUDE.md Location Detection (15 min)**

- Add storage location step to CLAUDE.md workflow
- Universal default: `./context/related-repos/` for all non-gitingest-agent-project directories
- No project type detection needed (simpler logic)
- Test folder creation and save workflow

**Phase 1.5.3: Implement CLI Parameter (15 min)**

- Add `--output-dir` option to CLI commands
- Wire parameter to StorageManager
- Test manual override functionality
- Validate path handling (relative/absolute)

**Phase 1.5.4: Add Context Folder Creation (10 min)**

- Auto-create `context/related-repos/` if needed
- Handle permissions errors gracefully
- Add user confirmation before creation
- Test folder creation on multiple projects

**Phase 1.5.5: Testing (20 min)**

- Test from gitingest-agent-project (Phase 1.0 regression)
- Test from software development project
- Test from knowledge management directory
- Test from arbitrary/temporary directory
- Test with `--output-dir` parameter
- Validate all acceptance criteria

**Total Implementation Time:** 1 hour 30 minutes

**Time Savings:** Simpler logic (no BMAD detection) reduces implementation and testing time by ~10 minutes.

**Prerequisites:**
- Phase 1.0 complete and tested ✅
- No new external dependencies required
- No blockers identified

### 11.5.6 Success Metrics

**Functional Success Criteria:**

- [ ] All Phase 1.0 tests still pass (backward compatible)
- [ ] Tool works from ANY directory (software, knowledge, ad-hoc)
- [ ] Context folder created automatically in current directory
- [ ] Analysis saved to `./context/related-repos/` universally
- [ ] `--output-dir` parameter functions correctly
- [ ] Can switch between different project types seamlessly

**User Acceptance Criteria:**

- [ ] User can analyze repos while working in any directory
- [ ] Analysis available as local context automatically
- [ ] No manual file copying or configuration required
- [ ] Consistent experience across all project types
- [ ] Tool "just works" - zero learning curve for location behavior
- [ ] Universal convention (`context/related-repos/`) becomes habit

**Quality Metrics:**

- [ ] 100% Phase 1.0 regression test pass rate
- [ ] 95%+ test coverage on StorageManager module
- [ ] Zero breaking changes to existing Phase 1.0 API
- [ ] Error handling covers all location detection scenarios
- [ ] User prompts are clear and actionable

### 11.5.6 Dependencies and Prerequisites

**Prerequisites:**

- **Phase 1.0 Complete:** ✅ All core functionality implemented and tested
- **Python 3.12+:** Already established in Phase 1.0
- **Click Framework:** Supports `--output-dir` option pattern
- **UV Package Manager:** No changes needed

**External Dependencies:**

- **None** - Phase 1.5 uses only Python standard library features (Path, os)
- No additional packages required in pyproject.toml

**Blockers:**

- **None identified** - Can implement immediately after Phase 1.0

**Architecture Dependencies:**

- Phase 1.5 builds on storage layer from Phase 1.0
- CLAUDE.md workflow extensions are additive (no conflicts)
- CLI commands extended, not replaced

### 11.5.7 Risks and Mitigations

**Risk 1: Path Detection Logic Fails**

- **Probability:** Low
- **Impact:** Medium (falls back to Phase 1.0 behavior)
- **Mitigation:**
  - Thorough testing across directory structures
  - Clear error messages if detection fails
  - Fail-safe default to Phase 1.0 behavior
  - Manual override via `--output-dir` always available

**Risk 2: CLAUDE.md Prompts Confusing**

- **Probability:** Medium (prompt refinement always needed)
- **Impact:** Low (usability issue, not functional)
- **Mitigation:**
  - Manual testing with real scenarios
  - Iterative prompt refinement
  - Clear examples in prompts
  - User can always specify `--output-dir` to bypass prompts

**Risk 3: Phase 1.5 Breaks Phase 1.0 Functionality**

- **Probability:** Low (isolated refactor)
- **Impact:** High (regression)
- **Mitigation:**
  - Comprehensive Phase 1.0 regression tests run first
  - Test Phase 1.0 behavior before adding Phase 1.5 features
  - Easy rollback strategy (revert storage.py changes)
  - Refactor validation step before enhancement

**Risk 4: Cross-Project File Conflicts**

- **Probability:** Very Low
- **Impact:** Low (file overwrite)
- **Mitigation:**
  - Timestamp-based naming if needed
  - Warn before overwriting existing files
  - Document naming conventions clearly
  - Analysis type in filename prevents most conflicts

**Risk 5: Phase 1.0 Exceeds Time Estimate (Blocking Phase 1.5)**

- **Probability:** Medium (common in development)
- **Impact:** Low (defer Phase 1.5)
- **Mitigation:**
  - Phase 1.5 explicitly optional
  - Can ship Phase 1.0 as complete product
  - Phase 1.5 can be added later as v1.1 update
  - No technical debt from deferring Phase 1.5

**Overall Risk Assessment:** **Low Risk, High Value**

Phase 1.5 is an isolated enhancement to the storage layer with clear rollback path and significant user value. The 1-2 hour implementation window and comprehensive testing strategy make this a low-risk, high-reward enhancement.

---

## 12. v2.0.0 Roadmap

### 12.1 Overview

**Status:** ✅ v1.0.0 Complete | ✅ v1.1.0 Complete | 📋 v2.0.0 Proposed

**📋 For Complete V2.0 Specification:** See [prd-v2.0-roadmap.md](prd-v2.0-roadmap.md)

Version 2.0.0 will extend GitIngest Agent with three major enhancements:

1. **Context-Efficient Agent Architecture** - Reduce CLAUDE.md overhead from 3.2k → 300 tokens (90% reduction)
2. **TOON Format Integration** - Token-Oriented Object Notation for 15-25% token reduction on GitHub API data
3. **Multi-Agent Architecture** - Parallel repository processing with sub-agent orchestration

**Key Features:**

- **Progressive Disclosure** - Move workflow orchestration from documentation to executable code
- **CLI Analyze Command** - `gitingest-agent analyze <url>` handles full workflow automatically
- **Plugin Architecture** - Extensible analysis types without modifying core code
- **TOON Output Format** - `--format toon` for optimized token usage
- **Multi-Repo Comparison** - Synthesized analysis workflows (e.g., "Compare FastAPI, Flask, Django")
- **GitHub API Integration** - Commit history, issues, PRs with TOON optimization

**Detailed Specifications:**

- **V2.0 Roadmap:** [prd-v2.0-roadmap.md](prd-v2.0-roadmap.md) - Complete feature specs and user stories
- **TOON Feature Request:** [user-context/v2-toon-multiagent-feature-request.md](../user-context/v2-toon-multiagent-feature-request.md) - Original proposal

### 12.2 Validation Completed

**Docker Testing Infrastructure:**

- TOON format validated with real GitHub API data
- 15-25% token savings verified (not marketing claims - real testing)
- Test results: [docker/toon-test/RESULTS.md](../docker/toon-test/RESULTS.md)
- Environment: Node.js 20 + TOON CLI v0.7.3+

**Real-World Test Cases:**

- Repository metadata: 4,044 → 3,374 tokens (16.6% savings)
- Commit history (30 commits): 76,348 → 58,906 tokens (22.8% savings)
- Conclusion: TOON delivers consistent 15-25% savings on GitHub API responses

### 12.3 Multiplicative Effect: TOON + Multi-Agent

**The Innovation:**

TOON and multi-agent architecture create a **multiplicative benefit**:

- **TOON alone:** 15-25% token savings per repository
- **Multi-agents alone:** 5× context windows through parallelization
- **Combined:** 5 repositories × 40% deeper analysis in same infrastructure

**Example Scenario:**

```
Without optimization (current):
5 repos × 76k tokens (JSON commits) = 380k tokens
❌ Exceeds 200k context limit

With TOON + Sub-Agents:
5 agents × 59k tokens (TOON commits) = 295k total
✅ Each agent: 200k window
✅ 141k left per agent for deep analysis
✅ 17k × 5 = 85k extra tokens for intelligence
```

### 12.4 Implementation Phases

**Phase 2.1: TOON Foundation (2-4 hours)**

- Add `--format toon` flag to CLI commands
- Implement TOON conversion in extractor module
- Test with docker/toon-test/ container
- Update storage for .toon file handling

**Phase 2.2: Multi-Repo Sequential (4-6 hours)**

- Add `compare` subcommand to CLI
- Implement sequential repo analysis
- Store intermediate summaries
- Generate comparison report

**Phase 2.3: Parallel Sub-Agents (6-8 hours)**

- Add `--parallel` flag to compare command
- Implement Task tool sub-agent launching
- Handle parallel completion and aggregation
- Validate results vs sequential mode

**Phase 2.4: GitHub API Integration (4-6 hours)**

- Add `extract-api` subcommand
- Implement GitHub API client
- Convert API responses to TOON
- Store alongside repository files

**Total Estimated Effort:** 16-24 hours across 4 phases

### 12.5 Success Metrics

**Token Efficiency:**

- Target: 15-25% token savings on GitHub API data (already verified)
- Measure: Compare JSON vs TOON token counts
- Success: Consistent savings across 10+ repositories

**Multi-Repo Capacity:**

- Target: Analyze 5+ repositories in single session
- Baseline: v1.0 can handle 1-2 repos
- Success: 5 repos with deep analysis (not shallow summaries)

**Performance:**

- Parallel speedup: 3-5× faster than sequential
- Success: Parallel takes ~1.2 × analysis_time (slight overhead acceptable)

### 12.6 Architecture Preview

**Integration Points in Current Architecture:**

- **Extractor Module:** Add TOON conversion after GitIngest extraction
- **Storage Module:** Support .toon file format alongside .txt
- **Token Counter:** Account for TOON token savings in routing logic
- **CLI Layer:** Add `compare` and `extract-api` commands

**No Breaking Changes:**

- Phase 1 functionality remains unchanged
- TOON is opt-in via `--format` flag
- Multi-repo comparison is new command (doesn't affect existing)
- All Phase 1 tests continue to pass

**External Dependencies:**

- TOON CLI: `@toon-format/cli` (Node.js package, already tested)
- Claude Code Task tool: For parallel sub-agent orchestration

### 12.7 Context-Efficient Architecture (Priority Enhancement)

**Problem:**

CLAUDE.md currently consumes **3,200 tokens** on every session load, regardless of whether repository analysis is occurring. This represents ~1.6% of the 200k context window consumed before any productive work begins.

**Proposed Solution:**

Move workflow orchestration from documentation to executable code using progressive disclosure. This architectural shift is detailed in **Section 2.1** of the [V2.0 Roadmap](prd-v2.0-roadmap.md).

**Key Approach:**

- **CLI Orchestration:** Create `gitingest-agent analyze <url>` command that handles full workflow internally
- **Minimal CLAUDE.md:** Reduce to ~300 tokens (90% reduction) - just URL detection and command execution
- **On-Demand Help:** Optional `/analyze-help` slash command for detailed docs (loaded only when requested)
- **Plugin Foundation:** Extensibility without modifying core instructions

**Benefits:**

- 90% context reduction (3.2k → 300 tokens when idle)
- Testable workflow logic (code vs. documentation)
- Direct CLI usage (CI/CD integration, scripting)
- Foundation for plugin architecture

**Priority:** This should be implemented **before** multi-repo/TOON features to prevent further context bloat.

**Full Specification:** See [prd-v2.0-roadmap.md - Section 2.1](prd-v2.0-roadmap.md#21-context-efficient-agent-architecture)

### 12.8 Next Steps

**Before V2.0 Development:**

1. ✅ **Feature Request Complete** - Comprehensive V2.0 specification documented
2. ✅ **Validation Complete** - TOON testing verified with real data
3. ✅ **Architecture Updated** - Integration points identified
4. 🎯 **CLAUDE.md Optimization** - Address context overhead (Section 12.7)
5. 🎯 **Story Creation Ready** - Use BMAD workflow to create V2.0 stories

**BMAD V2.0 Workflow:**

1. Use @sm to create V2.0 stories from feature request
2. Let detailed docs evolve with implementation
3. Iterate on architecture as needed
4. Maintain test coverage (96%+ target)
5. **New:** Implement CLAUDE.md optimization before scaling to multi-repo

---

## 13. Approval & Sign-off

### Document Status

- **Version:** 1.3
- **Product Version:** v1.0.0 Complete ✅ | v1.1.0 Complete ✅ | v2.0.0 Proposed 📋
- **Scope:** v1.0.0 (Released) + v1.1.0 (Released) + v2.0.0 Roadmap (Proposed)
- **Last Updated:** 2025-11-04

### Next Steps

1. **Architect:** Review PRD and create architecture.md
2. **Product Owner:** Review user stories for business value alignment
3. **Developer:** Review technical requirements for feasibility
4. **QA:** Review success criteria and test requirements

### Changes from Original

This PRD represents a **high-fidelity clone** of the video creator's proven design, with the following additions from V2 specification:

- **Size re-check implementation** (critical bug fix identified in video)
- **Explicit error handling requirements** (production quality)
- **Comprehensive testing strategy** (BMAD methodology)
- **Architecture notes for Phase 1.5 extensibility** (future-proofing)

---

**Document End**

*This PRD documents v1.0.0 (Core Clone) and v1.1.0 (Multi-Location Output) releases, both complete as of 2025-11-04. Version 2.0.0 roadmap is proposed for future development.*