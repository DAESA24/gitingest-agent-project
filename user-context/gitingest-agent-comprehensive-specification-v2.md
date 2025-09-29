# GitIngest Agent - Comprehensive Technical Specification V2

**Project:** GitIngest Agent (clone of "git agent" from AI LABS video)
**Source Video:** "Bash Apps Are INSANE… A New Way To Use Claude Code" (https://www.youtube.com/watch?v=1_twhMU9AxM)
**Audience:** Claude Code LLM for BMAD-based development
**Purpose:** Complete technical specification for building GitIngest Agent with maximum detail from source material

---

## Part 1: Executive Summary

### Project Mission
Build the **GitIngest Agent** - an automated Claude Code agent that eliminates manual friction in analyzing GitHub repositories by automatically checking token sizes and routing to appropriate workflows.

### Core Value Proposition
**Replaces:** Manual workflow requiring Claude Desktop + manual token checking + manual content extraction
**With:** Automated Claude Code agent that handles entire workflow from GitHub URL to analyzed output

### Key Metrics
- **Development Time (Original):** 2 hours total
- **Token Threshold:** 200,000 tokens (Claude Code model restriction)
- **Automation Trigger:** GitHub URL provided to Claude Code
- **Storage:** All data persisted as structured files (not chat context)

---

## Related Requirements Documents

**⚠️ IMPORTANT: This V2 specification defines Phase 1 only (Core Clone)**

### This Document (V2)
- **Scope:** Phase 1 - Faithful replication of video creator's tool
- **Source:** Proven design from AI LABS video
- **Target:** 3-4 hours implementation
- **Deliverable:** Working GitIngest Agent with V2 functionality
- **Purpose:** Validate core concept and establish foundation

### Requirements Addendum (Phase 1.5)
- **File:** `gitingest-agent-requirements-addendum-custom-enhancements.md`
- **Scope:** Phase 1.5 - Multi-location output capability
- **Purpose:** Custom enhancements for user's BMAD workflow needs
- **Target:** +1-2 hours beyond Phase 1
- **Key Feature:** Save analyses to any BMAD project's context folder

### Development Sequence
1. **Explore Phase:** Research topics from BOTH V2 and Addendum
2. **Plan Phase:** Create PRD incorporating V2 (MVP) + Addendum (Enhancement)
3. **Execute Phase 1:** Implement V2 completely, test thoroughly
4. **Execute Phase 1.5:** Add multi-location enhancement from Addendum
5. **Final Validation:** Ensure both V2 regression and enhancement tests pass

### When to Read Each Document
- **V2 (This Document):**
  - During Explore: Core technical research
  - During Plan: MVP feature set and architecture
  - During Execute Phase 1: Implementation details
- **Addendum:**
  - During Explore: Additional research topics (path detection)
  - During Plan: Enhancement requirements and user stories
  - During Execute Phase 1.5: Multi-location implementation

**📋 Both documents required for complete requirements picture.**

---

## Part 2: Technical Deep Dive

### 2.1 Exact Workflow Logic Tree

```
┌─────────────────────────────────────┐
│ User provides GitHub URL to         │
│ Claude Code in GitIngest Agent      │
│ project directory                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Claude Code automatically executes  │
│ "gitingest-agent check-size [URL]"  │
│ (triggered by CLAUDE.md context)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Check size function counts tokens   │
│ in repository                       │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
┌──────────┐    ┌──────────────┐
│< 200k    │    │>= 200k       │
│tokens    │    │tokens        │
└────┬─────┘    └──────┬───────┘
     │                 │
     ▼                 ▼
┌─────────────┐  ┌──────────────────────┐
│Extract full │  │1. Extract repo tree  │
│repository   │  │2. Save tree to data/ │
│             │  │3. Print tree         │
│Save to:     │  │4. Ask user: "What    │
│data/        │  │   type of analysis?" │
│[repo-name]/ │  └──────┬───────────────┘
│digest.txt   │         │
└─────┬───────┘         ▼
      │          ┌────────────────────────┐
      │          │Fallback: Auto-fetch    │
      │          │README + docs/          │
      │          │                        │
      │          │⚠️ KNOWN BUG: May still│
      │          │exceed limit - needs   │
      │          │second size check      │
      │          └──────┬─────────────────┘
      │                 │
      │          ┌──────┴──────────┐
      │          │User specifies:  │
      │          │- Documentation  │
      │          │- Installation   │
      │          │- Implementation │
      │          │- etc.           │
      │          └──────┬──────────┘
      │                 │
      │          ┌──────▼──────────┐
      │          │Extract specific │
      │          │content based on │
      │          │request          │
      │          │                 │
      │          │Save to: data/   │
      │          │[repo-name]/     │
      │          │[specific].txt   │
      │          └──────┬──────────┘
      │                 │
      └─────────┬───────┘
                │
                ▼
┌───────────────────────────────────────┐
│Claude Code's LLM analyzes content     │
│(automatic from CLAUDE.md instructions)│
└──────────────┬────────────────────────┘
               │
               ▼
┌───────────────────────────────────────┐
│Ask user: "Save analysis to            │
│analyze/ folder?"                      │
└──────────────┬────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   ┌────────┐    ┌─────────────┐
   │Yes     │    │No           │
   │        │    │             │
   │Save to:│    │Display only │
   │analyze/│    │(no storage) │
   │[type]/ │    └─────────────┘
   │*.md    │
   └────────┘
```

### 2.2 CLI Command Specifications

#### Parent Command Structure
```bash
# Parent command group
gitingest-agent [subcommand] [options]
```

#### Specific Subcommands (Extracted from Transcript)

**1. Check Size**
```bash
gitingest-agent check-size <github-url>
```
- **Purpose:** Count tokens in repository
- **Output:** Token count number
- **Decision:** Routes to full extraction or tree analysis
- **Storage:** None (decision-making only)

**2. Extract Full**
```bash
gitingest-agent extract-full <github-url>
```
- **Purpose:** Extract entire repository content
- **Trigger:** Token count < 200k
- **Output File:** `data/[repo-name]/digest.txt`
- **GitIngest Wrapper:** Calls `gitingest <url> -o data/[repo-name]/digest.txt`

**3. Extract Tree**
```bash
gitingest-agent extract-tree <github-url>
```
- **Purpose:** Get repository directory structure only
- **Trigger:** Token count >= 200k
- **Output File:** `data/[repo-name]/tree.txt`
- **Display:** Prints tree to terminal for user review

**4. Extract Specific**
```bash
gitingest-agent extract-specific <github-url> --type [docs|code|readme]
```
- **Purpose:** Extract targeted content based on analysis needs
- **Trigger:** User specification after tree review
- **Options:**
  - `--type docs`: Documentation folders only
  - `--type readme`: README files only
  - `--type code`: Specific code files (user specifies)
- **Output File:** `data/[repo-name]/[type]-content.txt`
- **GitIngest Wrapper:** Uses `-i` and `-e` flags for filtering

**5. Analyze**
```bash
gitingest-agent analyze <content-file> --analysis-type [installation|workflow|architecture]
```
- **Purpose:** Trigger Claude Code analysis with specific template
- **Input:** Path to extracted content file
- **Output:** Analysis results (display or save)
- **Storage:** Optional save to `analyze/[analysis-type]/[repo-name].md`

#### GitIngest CLI Parameters (Underlying Tool)

From transcript and GitIngest documentation:
```bash
gitingest [SOURCE] [OPTIONS]

Key options used in GitIngest Agent:
-o, --output TEXT           # Output file path ('-' for stdout)
-i, --include-pattern TEXT  # Include specific file patterns
-e, --exclude-pattern TEXT  # Exclude specific file patterns
-s, --max-size INTEGER      # Max file size in bytes (default: 10485760)
-b, --branch TEXT           # Specific branch to analyze
```

### 2.3 File Structure Requirements

**IMPORTANT CLARIFICATION:**
- `.bmad-core/` = BMAD methodology framework (DO NOT MODIFY)
- `data/` = GitIngest Agent's application data (CREATE DURING EXECUTE PHASE)
- `analyze/` = GitIngest Agent's analysis outputs (CREATE DURING EXECUTE PHASE)

These are **separate concerns**. The `data/` and `analyze/` folders are custom to our application, NOT part of BMAD framework.

```
gitingest-agent-project/
├── .bmad-core/                    # BMAD framework (installed)
│   └── [BMAD templates - do not modify]
├── user-context/                  # Project documentation
│   ├── gitingest-agent-project-overview.md
│   └── gitingest-agent-comprehensive-specification-v2.md (this file)
├── data/                          # Repository extractions (CREATE THIS)
│   └── [repo-name]/              # One folder per analyzed repo
│       ├── digest.txt            # Full extraction (< 200k tokens)
│       ├── tree.txt              # Tree structure (>= 200k tokens)
│       ├── docs-content.txt      # Specific extractions
│       ├── readme-content.txt    #
│       └── code-content.txt      #
├── analyze/                       # Analysis outputs
│   ├── installation/             # Installation guides
│   │   └── [repo-name].md
│   ├── workflow/                 # Workflow documentation
│   │   └── [repo-name].md
│   ├── architecture/             # Architecture analysis
│   │   └── [repo-name].md
│   └── [custom-type]/            # User-defined analysis types
│       └── [repo-name].md
├── cli.py                         # Click-based CLI implementation
├── CLAUDE.md                      # Claude Code agent instructions
├── pyproject.toml                 # UV/Python project configuration
├── tests/                         # Test suite
│   ├── test_check_size.py
│   ├── test_extract.py
│   └── test_workflow.py
└── README.md                      # Project documentation
```

### 2.4 Data Structures and Schemas

#### Repository Metadata Schema
```json
{
  "repo_url": "https://github.com/user/repo",
  "repo_name": "repo",
  "extraction_date": "2025-09-29",
  "token_count": 150000,
  "extraction_type": "full|tree|specific",
  "files_analyzed": 42,
  "extraction_file": "data/repo/digest.txt"
}
```

#### Analysis Output Schema
```markdown
# [Repository Name] - [Analysis Type]

**Repository:** [URL]
**Analyzed:** [Date]
**Token Count:** [Number]

## [Analysis Content]
...

## Source Data
- Extraction: data/[repo-name]/[file].txt
- Token Count: [number]
```

### 2.5 Known Issues and Required Refinements

#### Issue 1: Token Overshoot After Documentation Fetch
**Description (from transcript):**
> "After retrieving the tree and documentation, I need another check to ensure the combined content doesn't exceed the limit again. Currently, it can overshoot."

**Solution Required:**
- Add secondary token check after fetching README + docs
- If still exceeds 200k, prompt user to select specific docs folders
- Implement iterative refinement: tree → docs list → user selects subset

**Implementation Priority:** High (mentioned as active bug)

#### Issue 2: Workflow Testing Limitations
**Description (from transcript):**
> "You'll need to test the workflow manually as Claude won't be able to fully test everything on its own."

**Solution Approach:**
- Create test suite with known repos of various sizes
- Small repo (< 50k tokens): Full extraction test
- Medium repo (50k-200k tokens): Full extraction test
- Large repo (> 200k tokens): Tree + selective extraction test
- Document expected outcomes for manual verification

#### Issue 3: Prompt Refinement Iteration
**Description (from transcript):**
> "During testing, you'll discover various breaking points where parts of the workflow aren't followed correctly. These refinements take the most time."

**Solution Approach:**
- Maintain CLAUDE.md version history
- Document each breaking point discovered
- Track prompt adjustments that fixed issues
- Build up robust instruction set iteratively

---

## Part 3: BMAD Development Roadmap

### 3.1 Explore Phase

#### Research Tasks

**A. Click Framework Deep Dive**
- **What:** Python CLI framework for building command-line interfaces
- **Why:** Core framework wrapping GitIngest commands
- **Resources:**
  - Click documentation: https://click.palletsprojects.com/
  - Focus on: Command groups, subcommands, options, arguments
  - Example patterns: How to wrap existing CLI tools

**Research Questions:**
1. How do Click groups work? (Parent command with subcommands)
2. How to pass arguments between commands?
3. How to integrate Click with external CLI tools (GitIngest)?
4. Best practices for file handling in Click commands?
5. How to structure tests for Click applications?

**B. GitIngest CLI Mastery**
- **What:** Repository-to-text conversion tool
- **Installation:** Already completed via `uv tool install gitingest`
- **Documentation Review:**
  - File in workspace: `Context Research/gitingest_repo_analysis/youtube-transcript-mcp-repo-analysis.txt`
  - Focus sections: CLI usage, filtering options, token estimation

**Research Questions:**
1. How does GitIngest count tokens?
2. What filtering patterns work best for docs-only extraction?
3. How to handle private repositories (if needed)?
4. Performance characteristics with large repos?
5. Output format structure - how to parse?

**C. Claude Code Agent Patterns**
- **What:** How Claude Code responds to CLAUDE.md instructions
- **Study:** Existing CLAUDE.md in workspace root
- **Focus:** Workflow automation patterns

**Research Questions:**
1. How to trigger automatic command execution?
2. How to structure step-by-step workflow instructions?
3. How to handle conditional logic (if/then scenarios)?
4. How to prompt for user input mid-workflow?
5. Best practices for bash command documentation?

**D. UV/Python Project Structure**
- **What:** Modern Python project setup with UV
- **Why:** Project uses Python (Click) + UV package manager
- **Reference:** User's setup guide shows UV preference

**Research Questions:**
1. How to structure pyproject.toml for CLI tool?
2. How to make CLI command globally accessible?
3. UV best practices for development dependencies?
4. How to integrate tests with UV?

#### Exploration Deliverables

Create in `explore/` folder:
1. `click-framework-research.md` - Click patterns and examples
2. `gitingest-cli-capabilities.md` - Detailed CLI documentation
3. `workflow-design-notes.md` - Workflow logic design
4. `token-counting-research.md` - Token estimation methods
5. `claude-code-automation-patterns.md` - CLAUDE.md best practices

### 3.2 Plan Phase

#### PRD Development

**PRD Template Structure:**
```markdown
# GitIngest Agent - Product Requirements Document

## Vision
[Based on Part 1 Executive Summary]

## User Stories
1. As a developer, I want to analyze GitHub repos without manual token checking
2. As a developer, I want automatic workflow routing based on repo size
3. As a developer, I want to store analysis results for future reference
4. As a developer, I want Claude Code to handle the entire workflow automatically

## Functional Requirements
FR1: Token Size Checking
FR2: Workflow Routing Logic
FR3: Data Storage Management
FR4: Analysis Template Generation
FR5: Claude Code Integration

## Technical Requirements
TR1: Click CLI Framework
TR2: GitIngest Wrapper Commands
TR3: File I/O for data/ and analyze/
TR4: CLAUDE.md Workflow Specification
TR5: Python 3.12+ with UV package manager

## Success Criteria
[Based on Version 1 success criteria]

## Known Limitations
[From 2.5 Known Issues]
```

**Key PRD Elements (from transcript):**
- **Development Time Target:** 2 hours (achieved in original)
- **Primary User:** Developer analyzing open-source repos
- **Core Workflow:** URL → size check → branch → extract → analyze → store
- **Storage Philosophy:** Structured data files, not chat context
- **Integration:** Seamless Claude Code automation via CLAUDE.md

#### Architecture Design

**Architecture Document Structure:**
```markdown
# GitIngest Agent - System Architecture

## Component Diagram
[CLI Layer] → [GitIngest Wrapper] → [Storage Layer]
     ↓              ↓                      ↓
[Click Commands] [Token Counter]    [data/ analyze/]
     ↓
[Claude Code Integration via CLAUDE.md]

## Data Flow
[Detailed workflow from 2.1]

## Module Specifications
- cli.py: Command definitions
- token_counter.py: Size checking logic
- extractor.py: GitIngest wrapper functions
- analyzer.py: Analysis template handling
- storage.py: File management utilities

## Integration Points
- Claude Code: CLAUDE.md instructions
- GitIngest: CLI subprocess calls
- File System: data/ and analyze/ folders
```

**Architecture Decisions:**
1. **Click Group Pattern:** Parent command `gitingest-agent` with subcommands
2. **GitIngest Wrapping:** Subprocess calls with custom pre/post processing
3. **Storage Strategy:** File-based persistence in structured folders
4. **Workflow Automation:** CLAUDE.md defines complete workflow logic
5. **Token Counting:** Leverage GitIngest's built-in estimation

#### CLAUDE.md Specification

**Purpose:** Define complete agent behavior for Claude Code

**Structure (based on transcript description):**
```markdown
# GitIngest Agent - Claude Code Instructions

## Agent Purpose
You are the GitIngest Agent. When user provides a GitHub URL, automatically execute the complete repository analysis workflow.

## Workflow Trigger
When user messages contains a GitHub URL (https://github.com/...), immediately begin workflow.

## Workflow Steps

### Step 1: Size Check
Execute: `gitingest-agent check-size <github-url>`
Wait for token count result.

### Step 2: Route Based on Size
IF token_count < 200000:
  Execute: `gitingest-agent extract-full <github-url>`
  Proceed to Step 4
ELSE:
  Execute: `gitingest-agent extract-tree <github-url>`
  Proceed to Step 3

### Step 3: Selective Extraction (Large Repos)
Display tree to user.
Ask: "This repository exceeds 200k tokens. What would you like to analyze?"
Options:
- Documentation only
- Installation guide
- Specific implementation files
- README + key docs (automatic fallback)

Based on response, execute:
`gitingest-agent extract-specific <github-url> --type <user-choice>`

⚠️ IMPORTANT: After extraction, check size again. If still > 200k, ask user to narrow selection further.

### Step 4: Analysis
Review extracted content.
Ask: "What type of analysis would you like?"
Options:
- Installation steps
- Workflow understanding
- Architecture overview
- Custom analysis

Generate analysis based on request.

### Step 5: Storage
Ask: "Save this analysis to analyze/ folder?"
IF yes:
  Save to: analyze/<analysis-type>/<repo-name>.md
  Confirm: "Analysis saved to <path>"
ELSE:
  Confirm: "Analysis complete (not saved)"

## Command Reference
[Document all gitingest-agent commands here]

## Important Notes
- Always execute commands step-by-step with full context
- Display progress at each step
- Handle errors gracefully
- Confirm file saves with exact paths
```

#### Planning Deliverables

Create in `plan/` folder:
1. `prd.md` - Complete product requirements
2. `architecture.md` - System architecture and design
3. `CLAUDE.md` - Draft agent instructions (will move to root in Execute)
4. `data-schema.md` - File formats and data structures
5. `test-plan.md` - Testing strategy and test cases

### 3.3 Execute Phase

#### Implementation Sequence

**Phase 1: Project Setup**
1. ✅ Create GitHub repository (completed)
2. ✅ Install BMAD framework (completed)
3. Initialize UV project: `uv init`
4. Configure pyproject.toml with dependencies
5. Create folder structure: data/, analyze/

**Phase 2: Core CLI Implementation**
1. Create `cli.py` with Click group
2. Implement `check-size` command
   - Call gitingest with size estimation
   - Parse token count from output
   - Return decision: full | tree
3. Implement `extract-full` command
   - Call: `gitingest <url> -o data/<repo>/digest.txt`
   - Handle errors (network, permissions)
4. Implement `extract-tree` command
   - Call gitingest to get directory structure
   - Save to: `data/<repo>/tree.txt`
   - Display tree to terminal
5. Implement `extract-specific` command
   - Accept --type parameter
   - Map types to GitIngest filter patterns
   - Call with -i and -e flags appropriately

**Phase 3: Token Counting & Routing Logic**
1. Create `token_counter.py` module
   - Function: `count_tokens(url) -> int`
   - Uses GitIngest estimation capability
2. Create `workflow.py` module
   - Function: `route_extraction(token_count) -> str`
   - Returns: "full" | "tree"
   - Threshold: 200,000 tokens

**Phase 4: Storage Management**
1. Create `storage.py` module
   - Function: `save_extraction(content, repo, type)`
   - Function: `save_analysis(content, repo, analysis_type)`
   - Create directories if missing
   - Handle file naming conflicts

**Phase 5: CLAUDE.md Integration**
1. Move draft CLAUDE.md from plan/ to root
2. Test workflow trigger with GitHub URL
3. Refine instructions based on testing
4. Document all commands with examples
5. Iterate on prompt effectiveness

**Phase 6: Testing & Validation**
1. Unit tests for each CLI command
2. Integration tests for complete workflow
3. Manual testing with repos of various sizes:
   - Small: < 50k tokens
   - Medium: 50k-200k tokens
   - Large: > 200k tokens
4. Test error handling and edge cases
5. Validate CLAUDE.md automation works correctly

**Phase 7: Bug Fixes & Refinements**
1. Implement secondary size check (Issue 1 from 2.5)
2. Refine workflow based on breaking points discovered
3. Improve CLAUDE.md instructions
4. Add user guidance and error messages
5. Document refinements made

#### Testing Approach

**Test Repository Selection:**
- **Small (< 50k):** https://github.com/octocat/Hello-World
- **Medium (50k-200k):** Find example repository
- **Large (> 200k):** https://github.com/fastapi/fastapi (or similar)

**Test Scenarios:**
1. Full extraction workflow (small repo)
2. Tree + selective extraction (large repo)
3. Size check accuracy validation
4. File storage verification
5. Claude Code automation testing
6. Error handling (invalid URL, network issues)

**Manual Test Checklist:**
```
[ ] Provide GitHub URL to Claude Code
[ ] Verify size check runs automatically
[ ] Confirm correct workflow routing
[ ] Check data/ folder structure created
[ ] Validate content extracted correctly
[ ] Test analysis generation
[ ] Verify optional saving to analyze/
[ ] Confirm complete workflow automation
```

#### Execute Phase Deliverables

Create in `execute/` folder:
1. `src/` - Source code
   - cli.py
   - token_counter.py
   - workflow.py
   - storage.py
   - extractor.py
2. `tests/` - Test suite
   - test_cli.py
   - test_token_counter.py
   - test_workflow.py
   - test_storage.py
3. `docs/` - Implementation documentation
   - api-reference.md
   - testing-results.md
   - refinements-log.md
4. CLAUDE.md (in root) - Final agent instructions
5. README.md - User-facing documentation

---

## Part 4: Claude Code Integration Specification

### 4.1 CLAUDE.md Structure Deep Dive

#### Section 1: Agent Identity
```markdown
# GitIngest Agent

You are the GitIngest Agent, an automated tool for analyzing GitHub repositories.
Your purpose is to eliminate manual token checking and streamline repository analysis.
```

**Purpose:** Establishes agent role and context

#### Section 2: Automatic Workflow Trigger
```markdown
## Workflow Activation

When the user provides a GitHub repository URL in the format:
- https://github.com/<user>/<repo>
- https://github.com/<user>/<repo>/tree/<branch>

Immediately begin the GitIngest Agent workflow without asking for confirmation.
```

**Purpose:** Defines trigger condition for automation

**Key Pattern (from transcript):**
> "Every time I provide a repository URL, it executes the complete bakedin workflow automatically."

#### Section 3: Step-by-Step Command Execution
```markdown
## Workflow Execution

Execute these steps sequentially. Wait for each command to complete before proceeding.

### Step 1: Extract URL
Parse the GitHub URL from user message.
Store as variable: REPO_URL

### Step 2: Check Token Size
Execute command: `gitingest-agent check-size $REPO_URL`
Output format: "Token count: <number>"
Store token count as variable: TOKEN_COUNT

### Step 3: Route Workflow
IF TOKEN_COUNT < 200000:
  Set WORKFLOW_TYPE = "full"
  Proceed to Step 4a
ELSE:
  Set WORKFLOW_TYPE = "tree"
  Proceed to Step 4b

[Continue with detailed steps...]
```

**Purpose:** Provides explicit execution sequence

**Key Pattern (from transcript):**
> "Claude code simply runs the git agent command and knows exactly when and where to execute each step."

#### Section 4: Context Maintenance
```markdown
## Context Management

Maintain awareness of:
- Current step in workflow
- REPO_URL being analyzed
- TOKEN_COUNT of repository
- WORKFLOW_TYPE (full | tree)
- Files created in data/ folder
- Analysis type requested by user

Reference these variables throughout the workflow.
```

**Purpose:** Ensures workflow continuity across multiple commands

**Key Pattern (from transcript):**
> "When I include claude.md in any claude code instance, it automatically picks up this context and behaves accordingly."

#### Section 5: User Interaction Points
```markdown
## User Interaction Guidelines

### When to Ask User
1. After tree extraction (repos > 200k): "What would you like to analyze?"
2. After analysis generation: "Save this analysis?"
3. On errors: Present issue and ask how to proceed

### When NOT to Ask User
1. Don't ask to confirm starting workflow (automatic on URL)
2. Don't ask to confirm size checking (automatic)
3. Don't ask to confirm file saves to data/ (automatic)

### Response Handling
Wait for user input when prompted.
Parse response and map to appropriate command/action.
```

**Purpose:** Defines interaction patterns

**Key Pattern (from transcript):**
> "Based on this tree, it asks what type of analysis I need."

#### Section 6: Command Reference
```markdown
## Available Commands

### gitingest-agent check-size
**Usage:** `gitingest-agent check-size <github-url>`
**Purpose:** Count tokens in repository
**Output:** "Token count: <number>"
**When:** First step of every workflow

### gitingest-agent extract-full
**Usage:** `gitingest-agent extract-full <github-url>`
**Purpose:** Extract complete repository
**Output:** File saved to data/<repo>/digest.txt
**When:** Token count < 200k

[Continue with all commands...]
```

**Purpose:** Reference documentation for Claude Code

#### Section 7: Error Handling
```markdown
## Error Handling

### Network Errors
If gitingest command fails with network error:
- Inform user: "Unable to access repository. Check URL and network connection."
- Ask: "Retry or cancel?"

### Size Errors
If extraction still exceeds limit after filtering:
- Inform user: "Selected content still exceeds 200k tokens."
- Show current token count
- Ask: "Narrow selection further or proceed with partial content?"

[Continue with other error scenarios...]
```

**Purpose:** Graceful error handling

### 4.2 Automation Triggers and Workflow

#### Trigger Mechanism

**Input Pattern Recognition:**
```
User message contains: "https://github.com/..."
↓
CLAUDE.md matches pattern
↓
Claude Code activates GitIngest Agent workflow
↓
Executes Step 1 automatically (no confirmation)
```

**Key Implementation Detail (from transcript):**
> "The claud file instructs Cloud Code how to respond when given a GitHub link."

#### Workflow State Machine

```
State: IDLE
  → User provides GitHub URL
  → Transition to: SIZE_CHECKING

State: SIZE_CHECKING
  → Execute: check-size command
  → On completion: Store token_count
  → IF token_count < 200k:
      Transition to: FULL_EXTRACTION
    ELSE:
      Transition to: TREE_EXTRACTION

State: FULL_EXTRACTION
  → Execute: extract-full command
  → On completion: File saved to data/
  → Transition to: ANALYSIS_PROMPT

State: TREE_EXTRACTION
  → Execute: extract-tree command
  → On completion: Display tree
  → Transition to: USER_SELECTION

State: USER_SELECTION
  → Prompt user for analysis type
  → Wait for user response
  → Execute: extract-specific command
  → Transition to: ANALYSIS_PROMPT

State: ANALYSIS_PROMPT
  → Ask user: "What analysis would you like?"
  → Wait for user response
  → Generate analysis based on request
  → Transition to: SAVE_PROMPT

State: SAVE_PROMPT
  → Ask user: "Save analysis?"
  → IF yes: Save to analyze/ folder
  → Transition to: COMPLETE

State: COMPLETE
  → Display summary of actions taken
  → Transition to: IDLE
```

#### Context Persistence

**How Claude Code Maintains Context:**
1. CLAUDE.md loaded at start of each interaction
2. Workflow state tracked via explicit step references
3. Variables stored in conversation context
4. File paths confirmed after each save
5. Token count remembered throughout workflow

**Key Pattern (from transcript):**
> "It extracts the URL, performs the extraction, and runs a checking function to count tokens. Then it generates analysis templates based on what needs to be analyzed."

### 4.3 Step-by-Step Command Flow Example

**Scenario:** User provides URL to large repository

```
User: "Analyze https://github.com/fastapi/fastapi"

Claude Code (internal):
  - CLAUDE.md loaded
  - Pattern match: GitHub URL detected
  - Activate GitIngest Agent workflow

Claude Code (executes):
  > gitingest-agent check-size https://github.com/fastapi/fastapi

Output:
  Token count: 487,523

Claude Code (decision):
  - 487,523 > 200,000
  - Route to: tree extraction

Claude Code (executes):
  > gitingest-agent extract-tree https://github.com/fastapi/fastapi

Output:
  Tree structure saved to: data/fastapi/tree.txt
  [Tree displayed to user]

Claude Code (prompts user):
  "This repository exceeds 200k tokens (487k). What would you like to analyze?
  Options:
  1. Documentation only
  2. Installation guide
  3. Core implementation files
  4. README + key docs (automatic)"

User: "Documentation only"

Claude Code (executes):
  > gitingest-agent extract-specific https://github.com/fastapi/fastapi --type docs

Output:
  Documentation extracted to: data/fastapi/docs-content.txt
  Token count: 156,234

Claude Code (analyzes):
  [Reads docs-content.txt]
  [Generates analysis based on content]

Claude Code (prompts user):
  "Analysis complete. Would you like to save this to analyze/ folder?
  Suggested path: analyze/documentation/fastapi.md"

User: "Yes"

Claude Code (executes):
  [Saves analysis to analyze/documentation/fastapi.md]

Claude Code (confirms):
  "✓ Analysis saved to: analyze/documentation/fastapi.md
  ✓ Extraction data: data/fastapi/docs-content.txt
  ✓ Repository tree: data/fastapi/tree.txt

  Workflow complete. Provide another GitHub URL to analyze additional repositories."
```

**Key Characteristics (from transcript):**
- "Executing step by step with full context"
- "Immediately runs the check size tool through terminal commands"
- "Based on this tree, it asks what type of analysis I need"
- "I can optionally store this in the analyze folder"

### 4.4 Testing Approach for Claude Code Integration

#### Test 1: URL Recognition
```
Test: Provide GitHub URL
Expected: Workflow starts automatically (no confirmation prompt)
Verify: First command executed is check-size
```

#### Test 2: Small Repo Workflow
```
Test: Provide URL to repo < 200k tokens
Expected: Full extraction without prompts
Verify:
  - check-size executed
  - extract-full executed
  - File saved to data/
  - Analysis prompt appears
```

#### Test 3: Large Repo Workflow
```
Test: Provide URL to repo > 200k tokens
Expected: Tree extraction with user selection
Verify:
  - check-size executed
  - extract-tree executed
  - Tree displayed
  - User prompted for selection
  - extract-specific executed based on response
```

#### Test 4: Context Maintenance
```
Test: Interrupt workflow mid-execution
Action: Ask unrelated question
Expected: Claude Code maintains workflow state
Verify: Can resume workflow after interruption
```

#### Test 5: Error Recovery
```
Test: Provide invalid GitHub URL
Expected: Error message with recovery options
Verify: Workflow doesn't crash, prompts for correction
```

---

## Part 5: Known Issues, Refinements, and Optimization Opportunities

### 5.1 Critical Issues from Source Material

#### Issue A: Token Overshoot in Large Repo Fallback

**Source Quote (from transcript):**
> "After retrieving the tree and documentation, I need another check to ensure the combined content doesn't exceed the limit again. Currently, it can overshoot."

**Problem:**
When repo > 200k tokens, automatic fallback fetches README + docs. Combined content may still exceed 200k limit.

**Impact:**
- Claude Code may receive content exceeding context window
- Analysis may fail or be incomplete
- User experience degraded

**Solution Design:**
```python
def extract_with_size_validation(url, content_type, max_tokens=200000):
    """Extract content with iterative size checking"""

    # First extraction attempt
    content = extract_specific(url, content_type)
    token_count = count_tokens_in_content(content)

    if token_count <= max_tokens:
        return content

    # Content too large - prompt for refinement
    print(f"Content still exceeds limit: {token_count} tokens")
    print("Options:")
    print("1. Further narrow selection")
    print("2. Extract in chunks")
    print("3. Summarize large files")

    user_choice = get_user_input()

    # Recursive refinement until under limit
    return refine_extraction(url, content_type, user_choice, max_tokens)
```

**Implementation Priority:** High (affects core functionality)

**Testing:**
- Test with FastAPI repo (487k tokens)
- Test with React repo (large documentation)
- Verify iterative refinement works

#### Issue B: Workflow Breaking Points During Testing

**Source Quote (from transcript):**
> "During testing, you'll discover various breaking points where parts of the workflow aren't followed correctly. These refinements take the most time."

**Potential Breaking Points:**
1. **URL Parsing:** Different GitHub URL formats
   - Standard: https://github.com/user/repo
   - Branch: https://github.com/user/repo/tree/main
   - Subdirectory: https://github.com/user/repo/tree/main/src
2. **Network Timeouts:** Large repo cloning
3. **File System:** Permission issues creating folders
4. **Token Counting:** Edge cases in estimation
5. **Claude Code:** Prompt ambiguity causing wrong command execution

**Solution Approach:**
- Document each breaking point as discovered
- Create test case for each issue
- Refine CLAUDE.md instructions
- Add error handling in CLI commands
- Maintain refinement log in docs/

**Refinement Log Template:**
```markdown
## Refinement Log

### Issue 1: Branch-specific URLs not parsed correctly
- **Discovered:** 2025-09-29 during FastAPI testing
- **Symptom:** extract-full command failed with "repository not found"
- **Root Cause:** URL parser didn't handle /tree/ in path
- **Fix:** Updated URL parsing regex in cli.py
- **CLAUDE.md Change:** Added URL format examples
- **Test Added:** test_url_parsing.py

[Continue for each issue...]
```

#### Issue C: Manual Testing Requirements

**Source Quote (from transcript):**
> "You'll need to test the workflow manually as Claude won't be able to fully test everything on its own."

**Areas Requiring Manual Testing:**
1. **Claude Code Automation:** Verify CLAUDE.md triggers work
2. **User Interaction Flow:** Test prompt clarity and response handling
3. **File Output Verification:** Confirm correct content saved
4. **End-to-End Workflow:** Complete scenarios with real repos
5. **Error Recovery:** Test graceful failure handling

**Manual Test Protocol:**
```markdown
## Manual Test Session Template

**Date:** 2025-09-29
**Tester:** [Name]
**Test Scenario:** Large repo analysis (FastAPI)

### Pre-Test Setup
- [ ] GitIngest Agent project directory active
- [ ] CLAUDE.md in place
- [ ] data/ and analyze/ folders empty
- [ ] Claude Code instance fresh

### Test Steps
1. Provide URL: "Analyze https://github.com/fastapi/fastapi"
2. Observe: Does workflow start automatically?
3. Verify: check-size command executed
4. Record: Token count displayed
5. Verify: Correct routing (tree extraction)
6. Observe: Tree displayed to user
7. Respond: "Documentation only"
8. Verify: extract-specific executed
9. Check: File saved to correct location
10. Review: Analysis generated
11. Respond: "Yes" to save prompt
12. Verify: Analysis saved correctly

### Results
- [ ] Workflow triggered automatically: PASS/FAIL
- [ ] Commands executed in order: PASS/FAIL
- [ ] Token counting accurate: PASS/FAIL
- [ ] Routing logic correct: PASS/FAIL
- [ ] Files saved to correct paths: PASS/FAIL
- [ ] Analysis quality acceptable: PASS/FAIL
- [ ] User interaction smooth: PASS/FAIL

### Issues Discovered
[Document any problems encountered]

### CLAUDE.md Refinements Made
[List prompt adjustments]
```

### 5.2 Optimization Opportunities

#### Optimization 1: Caching Repository Metadata

**Opportunity:**
Repeated analysis of same repository requires re-fetching and token counting.

**Solution:**
```python
# Add metadata caching
cache_structure = {
    "repo_url": "https://github.com/user/repo",
    "last_checked": "2025-09-29T10:30:00",
    "token_count": 150000,
    "last_commit": "abc123",
    "cached_extraction": "data/repo/digest.txt"
}

# Check cache before extraction
def check_cache(repo_url):
    if cache_exists(repo_url):
        if cache_is_fresh(repo_url):  # Check last commit
            return load_from_cache(repo_url)
    return None
```

**Impact:** Faster repeated analysis, reduced GitIngest calls

#### Optimization 2: Parallel Analysis Types

**Opportunity:**
User might want multiple analysis types (installation + workflow).

**Solution:**
```markdown
# In CLAUDE.md, add:
"Would you like multiple analysis types?
1. Single analysis
2. Multiple analyses (specify which ones)"

# If multiple selected:
for analysis_type in user_selections:
    generate_analysis(analysis_type)
    save_to_analyze(analysis_type)
```

**Impact:** More efficient workflow for comprehensive repository understanding

#### Optimization 3: Smart Content Filtering

**Opportunity:**
For large repos, predictively select most relevant content.

**Solution:**
```python
# Intelligent content selection
def smart_filter_for_analysis_type(tree, analysis_type):
    if analysis_type == "installation":
        return filter_patterns([
            "README*",
            "INSTALL*",
            "docs/installation*",
            "docs/getting-started*",
            "setup.py",
            "pyproject.toml",
            "package.json"
        ])
    elif analysis_type == "architecture":
        return filter_patterns([
            "docs/architecture*",
            "docs/design*",
            "ARCHITECTURE*",
            "src/*/README*"
        ])
    # etc.
```

**Impact:** Reduced user prompting, faster analysis

### 5.3 Future Enhancement Ideas

#### Enhancement 1: Comparison Mode
```
Command: gitingest-agent compare <repo1-url> <repo2-url>
Purpose: Compare architecture/patterns between similar repositories
Output: Comparison analysis in analyze/comparisons/
```

#### Enhancement 2: Watch Mode
```
Command: gitingest-agent watch <repo-url>
Purpose: Monitor repository for changes, re-analyze when updated
Output: Change summaries in analyze/changes/
```

#### Enhancement 3: Export Formats
```
Command: gitingest-agent export <analysis-path> --format [pdf|html|markdown]
Purpose: Export analysis in different formats
Output: Formatted documents for sharing
```

#### Enhancement 4: Team Collaboration
```
Feature: Shared analyze/ folder via cloud storage
Purpose: Team members access same analysis repository
Implementation: Configurable storage backend
```

---

## Part 6: Quick Reference Guide

### 6.1 Command Cheat Sheet

```bash
# Start workflow (automatic when URL provided to Claude Code)
"Analyze https://github.com/user/repo"

# Manual command execution (if needed)
gitingest-agent check-size <url>
gitingest-agent extract-full <url>
gitingest-agent extract-tree <url>
gitingest-agent extract-specific <url> --type <docs|readme|code>
gitingest-agent analyze <content-file> --analysis-type <type>
```

### 6.2 File Location Reference

```
Project Root: Software Projects/gitingest-agent-project/

Data Storage:
  data/<repo-name>/digest.txt         (full extraction)
  data/<repo-name>/tree.txt           (tree structure)
  data/<repo-name>/docs-content.txt   (specific extraction)

Analysis Storage:
  analyze/installation/<repo-name>.md
  analyze/workflow/<repo-name>.md
  analyze/architecture/<repo-name>.md

Configuration:
  CLAUDE.md                           (agent instructions)
  cli.py                              (CLI implementation)
  pyproject.toml                      (project config)
```

### 6.3 Token Threshold Reference

```
Decision Threshold: 200,000 tokens
  < 200k: Full extraction
  >= 200k: Tree + selective extraction

Claude Code Context Limit: ~200k tokens
Warning Threshold: 180k tokens (90% of limit)
```

### 6.4 Development Time Estimates

```
Based on original creator's experience:
- Total Development Time: 2 hours
  - Workflow Design: 30 minutes
  - CLI Implementation: 45 minutes
  - CLAUDE.md Writing: 15 minutes
  - Testing & Refinement: 30 minutes

Expected for BMAD approach:
- Explore Phase: 2-3 hours (deeper research)
- Plan Phase: 1-2 hours (formal PRD/architecture)
- Execute Phase: 2-3 hours (implementation + testing)
- Total: 5-8 hours (more thorough than original)
```

---

## Part 7: Success Criteria and Definition of Done

### 7.1 Core Functionality Checklist

```
[ ] Token size checking works reliably for all repo sizes
[ ] Workflow routes correctly based on token threshold
[ ] Full extraction saves to data/<repo>/digest.txt
[ ] Tree extraction saves to data/<repo>/tree.txt
[ ] Selective extraction works with --type parameter
[ ] Analysis generation produces quality output
[ ] Optional saving to analyze/ folder works
[ ] File naming conventions followed consistently
```

### 7.2 Claude Code Integration Checklist

```
[ ] CLAUDE.md triggers workflow on GitHub URL
[ ] Commands execute automatically in sequence
[ ] Workflow maintains context across steps
[ ] User prompts appear at correct decision points
[ ] Error handling prevents workflow crashes
[ ] Completion message summarizes actions taken
```

### 7.3 Testing Validation Checklist

```
[ ] Small repo (< 50k tokens) workflow tested
[ ] Medium repo (50k-200k tokens) workflow tested
[ ] Large repo (> 200k tokens) workflow tested
[ ] Edge cases tested (invalid URL, network errors)
[ ] Manual testing protocol executed
[ ] All breaking points documented
[ ] Refinement log maintained
```

### 7.4 Documentation Completeness Checklist

```
[ ] README.md with user instructions
[ ] CLAUDE.md with complete agent specification
[ ] API reference for CLI commands
[ ] Testing results documented
[ ] Refinement log updated
[ ] Known issues documented with workarounds
```

### 7.5 Definition of Done

**Project is considered complete when:**
1. All core functionality checklist items pass
2. All Claude Code integration checklist items pass
3. All testing validation checklist items pass
4. All documentation completeness checklist items pass
5. Tool successfully replicates video creator's git agent functionality
6. Manual testing confirms 2-hour use case workflow works end-to-end

---

## Appendix A: Video Creator's Key Quotes

**On Development Speed:**
> "This entire workflow integration with Claude Code took about 2 hours to build."

**On Complexity:**
> "Building this was surprisingly straightforward. It's a compact tool."

**On CLAUDE.md Importance:**
> "Most of your effort will go into refining the claude.md file. Prompting agents properly requires significant tweaking."

**On Testing:**
> "You'll need to test the workflow manually as Claude won't be able to fully test everything on its own."

**On Automation:**
> "When I include claude.md in any claude code instance, it automatically picks up this context and behaves accordingly."

**On Core Mechanism:**
> "When we run git agent, it's essentially calling the git ingest CLI underneath. That's the core mechanism."

**On Click Framework:**
> "Click allows you to define new commands and run them seamlessly."

**On Workflow Trigger:**
> "Every time I provide a repository URL, it executes the complete bakedin workflow automatically."

**On Storage Philosophy:**
> "Claude code becomes the actual agent and instead of just maintaining context, it stores everything as structured data within the repository."

---

## Appendix B: GitIngest CLI Reference

### Installation
```bash
uv tool install gitingest  # ✅ Already completed
```

### Basic Usage
```bash
gitingest <github-url>                    # Default: saves to digest.txt
gitingest <github-url> -o <output-file>   # Custom output location
gitingest -o - <github-url>               # Output to stdout
```

### Filtering Options
```bash
-i, --include-pattern TEXT   # Include specific patterns
-e, --exclude-pattern TEXT   # Exclude specific patterns
-s, --max-size INTEGER       # Max file size (default: 10MB)
-b, --branch TEXT            # Specific branch
```

### Examples
```bash
# Documentation only
gitingest <url> -i "*.md,docs/**/*" -o docs.txt

# Python files only
gitingest <url> -i "*.py" -e "tests/*,*_test.py" -o code.txt

# README and key config files
gitingest <url> -i "README*,package.json,pyproject.toml" -o readme.txt
```

### Token Estimation
GitIngest provides token count in output. Parse with:
```bash
gitingest <url> | grep "Estimated tokens"
```

---

## Document Metadata

**Version:** 2.0
**Created:** 2025-09-29
**Purpose:** Comprehensive technical specification for GitIngest Agent development
**Audience:** Claude Code LLM for BMAD workflow execution
**Status:** Ready for Explore Phase
**Next Action:** Begin research tasks from Section 3.1

**Related Documents:**
- `gitingest-agent-project-overview.md` (Version 1, high-level summary)
- YouTube Transcript: `Context Research/youtube_transcript_analysis/bash-apps-are-insane-a-new-way-to-use-claude-code.md`
- GitIngest Analysis: `Context Research/gitingest_repo_analysis/youtube-transcript-mcp-repo-analysis.txt`

**Update History:**
- V1.0: Initial overview (high-level summary)
- V2.0: Comprehensive technical specification with BMAD roadmap, implementation details, and Claude Code integration specification

---

*This document provides complete technical context for building GitIngest Agent using the BMAD methodology. All details extracted from source video transcript and optimized for LLM consumption during development workflow.*