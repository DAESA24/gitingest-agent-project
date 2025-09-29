# Claude Code Agent Patterns Research

**Date:** 2025-09-29
**Purpose:** Research CLAUDE.md automation for GitIngest Agent workflow

---

## Overview

CLAUDE.md files provide project-specific instructions that Claude Code automatically loads into context. They define workflows, commands, conventions, and automation patterns that guide Claude's behavior when working in a project.

---

## CLAUDE.md File Purpose

### What Gets Included

**Core Documentation:**
- Project overview and purpose
- Main technologies and frameworks
- Development guidelines and conventions
- File structure preferences
- Testing approaches

**Command Reference:**
- Build commands
- Test commands
- Development server commands
- Custom project-specific commands

**Workflow Instructions:**
- Step-by-step procedures
- Conditional logic patterns
- Error handling strategies
- Common task automation

---

## CLAUDE.md Location and Loading

### File Placement

**Project-Level:**
```
project-root/
├── CLAUDE.md           # Main project instructions
├── .claude/
│   └── commands/       # Custom slash commands
│       ├── command1.md
│       └── command2.md
```

**Personal-Level:**
```
~/.claude/commands/     # Personal commands (all projects)
```

### Auto-Loading Behavior

- Claude automatically loads CLAUDE.md on chat start
- Pulls into context window automatically
- No explicit trigger needed
- Updates reflected in new chat sessions

---

## Workflow Automation Patterns

### Pattern 1: Automatic Workflow Trigger

**Use Case:** Execute multi-step workflow when specific input detected

**Structure:**
```markdown
## Workflow Trigger

When user provides [PATTERN], automatically execute the following workflow:

### Step 1: [Action Name]
Execute: [command or action]
Expected output: [description]

### Step 2: [Action Name]
If [condition]:
  Execute: [command A]
Else:
  Execute: [command B]

### Step 3: [Action Name]
[Continue workflow...]
```

**GitIngest Agent Example:**
```markdown
## GitHub Repository Analysis Workflow

When user provides a GitHub URL (format: https://github.com/user/repo):

### Step 1: Extract URL
Parse the GitHub URL from user message.
Store as: REPO_URL

### Step 2: Check Repository Size
Execute: `gitingest-agent check-size $REPO_URL`
Store token count as: TOKEN_COUNT

### Step 3: Route Based on Size
If TOKEN_COUNT < 200000:
  Execute: `gitingest-agent extract-full $REPO_URL`
  Proceed to Step 5
Else:
  Execute: `gitingest-agent extract-tree $REPO_URL`
  Proceed to Step 4

### Step 4: User Selection (Large Repos Only)
Display tree to user
Ask: "What would you like to analyze?"
Execute: `gitingest-agent extract-specific $REPO_URL --type [user-choice]`

### Step 5: Generate Analysis
Ask user: "What type of analysis?"
Generate analysis based on request

### Step 6: Save Results
Ask: "Save analysis to analyze/ folder?"
If yes: Save to appropriate location
```

### Pattern 2: Conditional Logic Handling

**Use Case:** Different workflows based on conditions

**Structure:**
```markdown
## Conditional Workflow

IF [condition]:
  - Action A
  - Action B
ELSE IF [condition2]:
  - Action C
  - Action D
ELSE:
  - Action E

Reference: Check [variable] from previous step
```

**Example:**
```markdown
## Size-Based Routing

After checking token count:

IF token_count < 200000:
  Workflow: Full Extraction
  - Extract entire repository
  - Save to data/[repo]/digest.txt
  - No user prompts needed
  - Proceed directly to analysis

ELSE IF token_count >= 200000:
  Workflow: Selective Extraction
  - Extract tree structure
  - Display to user
  - Prompt for content selection
  - Extract selected content only
  - Re-check size after extraction
```

### Pattern 3: Step-by-Step Command Execution

**Use Case:** Sequential command execution with validation

**Structure:**
```markdown
## Sequential Workflow

Execute these steps in order. Wait for each to complete before proceeding.

**Step 1: [Name]**
Command: `[command]`
Validation: [expected output]
On success: Proceed to Step 2
On failure: [error handling]

**Step 2: [Name]**
Command: `[command]`
[Continue...]
```

**Example:**
```markdown
## Repository Extraction Workflow

Execute commands sequentially:

**Step 1: Size Check**
Command: `gitingest-agent check-size <url>`
Validation: Output contains "Token count: [number]"
Store: Parse number and save as TOKEN_COUNT
On failure: Inform user of network/URL error

**Step 2: Directory Setup**
Command: Create data/[repo-name]/ directory
Validation: Directory exists
On failure: Check permissions

**Step 3: Extraction**
Command: Based on TOKEN_COUNT (see conditional routing)
Validation: File created in expected location
Display: Confirm path to user
```

### Pattern 4: User Interaction Points

**Use Case:** Define when to prompt user vs. proceed automatically

**Structure:**
```markdown
## User Interaction Guidelines

### When to Ask User:
1. [Scenario A] - Ask: "[Question]"
2. [Scenario B] - Ask: "[Question]"

### When NOT to Ask:
1. [Scenario X] - Proceed automatically
2. [Scenario Y] - Proceed automatically

### Response Handling:
- Parse user input
- Map to appropriate action
- Execute corresponding command
```

**Example:**
```markdown
## GitIngest Agent Interaction Points

### When to Ask User:
1. After tree extraction (repos > 200k): "What would you like to analyze?"
   Options: documentation, installation, specific files
2. After analysis generation: "Save this analysis to analyze/ folder?"
   Options: yes (specify path), no
3. On errors: Present issue, ask how to proceed

### When NOT to Ask:
1. Starting workflow - Automatically begin on GitHub URL detection
2. Size checking - Automatically execute check-size command
3. Creating data/ folders - Automatically create as needed
4. Full extraction (small repos) - Automatically extract without prompts

### Response Handling:
- "documentation" → Execute: gitingest-agent extract-specific --type docs
- "installation" → Extract README + setup files
- "yes" → Save to analyze/[type]/[repo].md
- "no" → Display analysis only, do not save
```

### Pattern 5: Context Maintenance

**Use Case:** Track state across multi-step workflow

**Structure:**
```markdown
## Context Variables

Maintain awareness of these throughout workflow:
- VARIABLE_1: [description]
- VARIABLE_2: [description]

Reference these variables in later steps.
Display context when helpful to user.
```

**Example:**
```markdown
## Workflow Context

Track these variables throughout the session:

- REPO_URL: GitHub repository URL being analyzed
- REPO_NAME: Extracted repository name (user/repo)
- TOKEN_COUNT: Token count from size check
- WORKFLOW_TYPE: "full" or "tree" (based on size)
- EXTRACTION_PATH: Where content was saved
- ANALYSIS_TYPE: Type of analysis requested

Display Progress:
"Processing: [REPO_NAME]"
"Token count: [TOKEN_COUNT]"
"Extraction saved to: [EXTRACTION_PATH]"
```

### Pattern 6: Error Handling

**Use Case:** Graceful error recovery

**Structure:**
```markdown
## Error Handling

### Error Type 1: [Error Name]
Symptom: [description]
Response: [action]
Ask user: [question]

### Error Type 2: [Error Name]
Symptom: [description]
Response: [action]
Fallback: [alternative approach]
```

**Example:**
```markdown
## GitIngest Agent Error Handling

### Network Errors
Symptom: gitingest command fails, "unable to clone"
Response: Inform user "Unable to access repository"
Provide: Check URL format, network connection
Ask: "Retry or cancel workflow?"

### Size Overflow
Symptom: Extracted content still exceeds 200k after filtering
Response: Inform user "Content still exceeds limit"
Display: Current token count
Ask: "Narrow selection further or proceed with partial content?"

### Invalid URL
Symptom: URL not matching GitHub format
Response: Inform user "Invalid GitHub URL format"
Provide: Expected format examples
Ask: "Provide corrected URL or cancel?"

### Permission Errors
Symptom: Cannot create data/ directories
Response: Inform user of permission issue
Provide: Manual mkdir commands
Ask: "Run commands manually or specify different location?"
```

---

## Custom Slash Commands

### Creating Custom Commands

**Location:** `.claude/commands/[command-name].md`

**Format:**
```markdown
# Command Name

Description of what this command does.

## Arguments

$ARGUMENTS - Dynamic arguments passed to command

## Steps

1. Step one
2. Step two
3. etc.

## Example Usage

/project:command-name arg1 arg2
```

**GitIngest Agent Example:**

**File:** `.claude/commands/analyze-repo.md`
```markdown
# Analyze Repository

Automatically analyze a GitHub repository using GitIngest Agent.

## Arguments

$ARGUMENTS - GitHub repository URL

## Workflow

1. Extract URL from arguments
2. Execute check-size command
3. Route to appropriate extraction workflow
4. Generate analysis based on size/content
5. Offer to save results

## Usage

/project:analyze-repo https://github.com/user/repo
```

---

## Best Practices from Research

### 1. Explore, Plan, Code Workflow

**Pattern:**
```markdown
## Development Workflow

When implementing new features:

### Phase 1: Explore
- Read relevant files (DO NOT code yet)
- Understand existing patterns
- Identify integration points

### Phase 2: Plan
- Create implementation plan
- Verify plan with user
- Use "think" keyword to trigger extended thinking

### Phase 3: Code
- Implement based on plan
- Write tests
- Verify solution
```

### 2. Specificity in Instructions

**Good:**
```markdown
Execute: `gitingest-agent check-size <url>`
Expected output: "Token count: 150000"
Store as: TOKEN_COUNT
```

**Bad:**
```markdown
Check the size of the repo
```

### 3. Thinking Modes

**Trigger extended reasoning:**
```markdown
When analyzing complex repo structure:
- Use "think" for standard analysis
- Use "think hard" for architectural decisions
- Use "ultrathink" for optimization strategies
```

### 4. Verification Steps

**Pattern:**
```markdown
After extraction:
1. Verify file exists at expected path
2. Confirm file size is non-zero
3. Display path to user: "Saved to: [path]"
4. On verification failure: [error handling]
```

---

## GitIngest Agent CLAUDE.md Structure

### Recommended Organization

```markdown
# GitIngest Agent

[Brief description of agent purpose]

## Agent Identity
[Define agent role and behavior]

## Workflow Activation
[Define trigger patterns - GitHub URLs]

## Workflow Steps
[Detailed step-by-step instructions]

### Step 1: URL Detection
[Instructions...]

### Step 2: Size Checking
[Instructions...]

### Step 3: Workflow Routing
[Conditional logic...]

### Step 4a: Full Extraction (Small Repos)
[Instructions...]

### Step 4b: Tree + Selective (Large Repos)
[Instructions...]

### Step 5: Analysis Generation
[Instructions...]

### Step 6: Results Storage
[Instructions...]

## Context Management
[Variables to track]

## User Interaction Guidelines
[When to prompt, when to proceed]

## Command Reference
[All available commands with usage]

## Error Handling
[Error scenarios and responses]

## Important Notes
[Edge cases, reminders, gotchas]
```

---

## Automation Trigger Mechanisms

### Pattern Recognition

**Input Patterns:**
- GitHub URL: `https://github.com/...`
- Slash command: `/project:command`
- Keyword: specific phrases that trigger workflows

**Example:**
```markdown
## Trigger Patterns

Workflow activates when user input matches:
1. GitHub URL regex: `https?://github\.com/[\w-]+/[\w-]+`
2. Direct command: "analyze repository [url]"
3. Alias: "ingest [url]"

On match: Begin automatic workflow execution
```

### State Machine Pattern

**Defining States:**
```markdown
## Workflow States

State: IDLE
- Waiting for GitHub URL
- On URL received → Transition to SIZE_CHECKING

State: SIZE_CHECKING
- Executing check-size command
- On completion → Store token_count
- If < 200k → FULL_EXTRACTION
- If >= 200k → TREE_EXTRACTION

State: FULL_EXTRACTION
- Executing extract-full
- On completion → ANALYSIS_PROMPT

[Continue defining states...]
```

---

## Answers to Research Questions

**Q1: How to trigger automatic command execution?**
- Define trigger patterns in CLAUDE.md (e.g., GitHub URL regex)
- Use "When user provides [pattern]" language
- Specify "automatically execute" without confirmation
- Claude recognizes patterns and initiates workflow

**Q2: How to structure step-by-step workflow instructions?**
- Use numbered or named steps
- Specify exact commands to execute
- Define expected outputs
- Include validation checks
- Handle error scenarios explicitly

**Q3: How to handle conditional logic?**
- Use IF/ELSE structures explicitly
- Reference variables from previous steps
- Define clear conditions (e.g., token_count < 200000)
- Specify different workflows for each branch

**Q4: How to prompt for user input mid-workflow?**
- Define "User Interaction Points" section
- Specify exact questions to ask
- List expected response options
- Map responses to actions/commands

**Q5: Best practices for bash command documentation?**
- Show exact command syntax
- Include expected output
- Provide validation steps
- Document error conditions
- Reference where output is stored

---

## Key Patterns for GitIngest Agent

### 1. Workflow Trigger
```markdown
When user provides GitHub URL:
Automatically execute workflow (no confirmation)
```

### 2. Sequential Steps
```markdown
Execute Step 1
Wait for completion
Validate output
Proceed to Step 2
```

### 3. Conditional Routing
```markdown
IF token_count < 200000:
  Full extraction workflow
ELSE:
  Tree + selective workflow
```

### 4. Context Tracking
```markdown
Maintain variables:
- REPO_URL
- TOKEN_COUNT
- WORKFLOW_TYPE
```

### 5. User Prompts
```markdown
Ask user only when decision needed:
- Content selection (large repos)
- Analysis type preference
- Save location confirmation
```

---

## Resources

- **Claude Code Docs:** https://docs.claude.com/en/docs/claude-code/
- **Best Practices:** https://www.anthropic.com/engineering/claude-code-best-practices
- **Common Workflows:** https://docs.claude.com/en/docs/claude-code/common-workflows
- **Awesome Claude Code:** https://github.com/hesreallyhim/awesome-claude-code

---

**Status:** ✅ Research complete
**Next:** Apply patterns to GitIngest Agent CLAUDE.md draft