# GitIngest Agent - Requirements Addendum: Custom Enhancements

**Document Version:** 1.0
**Created:** 2025-09-29
**Status:** Approved for implementation
**Relationship:** Extends `gitingest-agent-comprehensive-specification-v2.md`

---

## Document Purpose

**This addendum captures user-specific requirements that extend beyond the original video implementation.**

### Relationship to V2 Specification
- **V2 Spec:** Faithful clone of video creator's tool (proven design)
- **This Addendum:** Custom enhancements for user's specific BMAD workflow needs
- **Integration:** V2 = Phase 1 (core), Addendum = Phase 1.5 (enhancement)

### Why Separate Document
1. **Traceability:** Preserve distinction between "proven original" and "custom additions"
2. **Risk Management:** Can ship V2 clone independently if time-constrained
3. **BMAD Best Practice:** Requirements evolution tracked separately
4. **Clear Prioritization:** MVP (V2) vs Enhancement (Addendum) explicitly defined

---

## Priority Classification

### P0: Must Have - Phase 1 (Core Clone)
All requirements in V2 specification:
- Token size checking and workflow routing
- Full and selective extraction
- Analysis generation
- File storage in gitingest-agent-project
- Claude Code automation via CLAUDE.md

**Delivery Target:** 3-4 hours (per V2 BMAD roadmap)

### P1: Should Have - Phase 1.5 (Multi-Location Enhancement)
**Requirements in this addendum:**
- Multi-location output capability
- Context folder standard
- Cross-project analysis support

**Delivery Target:** +1-2 hours beyond Phase 1

### P2: Nice to Have - Phase 2 (Future Enhancements)
Deferred to post-MVP:
- Repository caching (from V2 optimization section)
- Comparison mode
- Watch mode
- Export formats

---

## P1 Enhancement: Multi-Location Output Capability

### Executive Summary

Enable GitIngest Agent to save analysis outputs to **any project directory**, not just gitingest-agent-project, making the tool universally useful across all BMAD projects.

### Problem Statement

**Current Design (V2):**
- GitIngest Agent only saves to its own `data/` and `analyze/` folders
- Assumes user analyzes repos for the GitIngest Agent project itself
- To use analysis in another project, user must manually copy files

**Real-World Requirement:**
- User works in multiple BMAD projects (react-component-test-project, podcast-processor-cli-tool, etc.)
- Each project needs to analyze related repositories
- Analysis should be available as **project context** where it's needed
- GitIngest Agent should work from any directory

**Example Scenario:**
```
Working on: react-component-test-project
Need to understand: React 19 new features
Want to analyze: https://github.com/facebook/react

Desired outcome:
→ Analysis saved to: react-component-test-project/context/related-repos/react-analysis.md
→ Available as context when working in that project
→ Don't have to switch to gitingest-agent-project directory
```

### User Stories

#### Story 1: Analyze Repo for Current Project
**As a** developer working in a BMAD project,
**I want to** analyze a related repository and save the analysis in my current project's context folder,
**So that** the analysis is available as project context without switching directories or copying files.

**Acceptance Criteria:**
- [ ] GitIngest Agent detects I'm in a BMAD project (checks for `.bmad-core/`)
- [ ] Agent asks: "Save analysis to current project's context folder?"
- [ ] If yes, creates `context/related-repos/` if missing
- [ ] Saves analysis to `context/related-repos/<repo-name>-analysis.md`
- [ ] Analysis file includes metadata: analyzed date, token count, source repo
- [ ] Can run multiple analyses - each saves to separate file

#### Story 2: Analyze Repo for GitIngest Agent Project
**As a** developer improving the GitIngest Agent,
**I want to** analyze repositories related to the agent itself (Click, GitIngest, etc.),
**So that** I can reference implementation patterns while building the tool.

**Acceptance Criteria:**
- [ ] When in gitingest-agent-project directory, default behavior is V2 spec
- [ ] Saves to `data/` and `analyze/` folders as designed
- [ ] No change to original workflow
- [ ] V2 regression tests all pass

#### Story 3: Custom Output Location
**As a** developer with specific organizational needs,
**I want to** specify exactly where analysis should be saved,
**So that** I have full control over file organization.

**Acceptance Criteria:**
- [ ] Can provide `--output-dir` parameter to CLI commands
- [ ] Agent validates path exists or asks to create it
- [ ] Saves analysis to specified location
- [ ] Works from any directory

#### Story 4: Cross-Project Context Standard
**As a** developer managing multiple BMAD projects,
**I want** a consistent `context/related-repos/` folder structure across all projects,
**So that** I always know where to find repository analysis for any project.

**Acceptance Criteria:**
- [ ] All BMAD projects can have optional `context/` folder
- [ ] `context/related-repos/` becomes standard location for GitIngest analyses
- [ ] Folder structure documented in project README
- [ ] Works seamlessly with existing BMAD folder structure

### Technical Design

#### Architecture Changes

**Current (V2) Storage Layer:**
```python
# Hardcoded paths
DATA_DIR = "data/"
ANALYZE_DIR = "analyze/"

def save_extraction(content, repo_name):
    path = f"{DATA_DIR}{repo_name}/digest.txt"
    save_file(path, content)
```

**Enhanced Storage Layer:**
```python
# Flexible path resolution
class StorageManager:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or self._detect_output_location()

    def _detect_output_location(self):
        """Detect appropriate save location based on context"""
        cwd = Path.cwd()

        # Check if in gitingest-agent-project
        if cwd.name == "gitingest-agent-project":
            return cwd  # Use V2 default structure

        # Check if in another BMAD project
        if (cwd / ".bmad-core").exists():
            # Offer to save to context/related-repos/
            return cwd / "context" / "related-repos"

        # Unknown location - ask user
        return self._prompt_for_location()

    def save_analysis(self, content, repo_name, analysis_type):
        """Save analysis to detected or specified location"""
        if self._is_gitingest_project():
            # V2 behavior: analyze/<type>/<repo>.md
            path = self.output_dir / "analyze" / analysis_type / f"{repo_name}.md"
        else:
            # Enhanced behavior: context/related-repos/<repo>-<type>.md
            path = self.output_dir / f"{repo_name}-{analysis_type}.md"

        self._ensure_directory_exists(path.parent)
        save_file(path, content)
        return path
```

#### CLAUDE.md Integration

**Enhanced Workflow Steps (after Step 4: Analysis Generation):**

```markdown
### Step 5: Determine Save Location (NEW)

Before asking user about saving, detect current context:

STEP 5A: Detect Project Context
Execute internal check:
- Get current working directory
- Check if directory name == "gitingest-agent-project"
- Check if .bmad-core exists in current directory

STEP 5B: Route Based on Context

IF in gitingest-agent-project:
  - Use V2 default behavior
  - Save to: data/ and analyze/ folders
  - Skip to Step 6 (Save Prompt)

ELSE IF in another BMAD project (has .bmad-core):
  - Display: "Detected BMAD project: [project-name]"
  - Ask: "Save analysis to this project's context folder?"
    Options:
    1. Yes - Save to ./context/related-repos/ (recommended)
    2. No - Save to gitingest-agent-project/analyze/
    3. Custom location (specify path)

  Based on response:
  - Option 1: Create context/related-repos/ if needed, save there
  - Option 2: Save to gitingest-agent-project as V2 default
  - Option 3: Prompt for custom path, validate, save

ELSE (unknown location):
  - Display: "Current directory: [path]"
  - Ask: "Where should I save this analysis?"
    Options:
    1. Current directory
    2. GitIngest Agent project (../../gitingest-agent-project/analyze/)
    3. Custom location (specify path)

STEP 5C: Confirm Save Location
Display resolved path to user:
"Analysis will be saved to: [full/path/to/file.md]"
"Proceed with save? (yes/no)"

### Step 6: Execute Save (UPDATED)
Save analysis to resolved location.
Confirm with full path:
"✓ Analysis saved to: [absolute/path]"
```

#### File Naming Conventions

**In gitingest-agent-project (V2 behavior):**
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

**In other BMAD projects (Enhanced behavior):**
```
context/
  related-repos/
    react-installation.md          # Repo + analysis type
    react-architecture.md
    fastapi-workflow.md
    testing-library-overview.md
```

**Rationale for Different Naming:**
- GitIngest Agent project: Multiple analysis types per repo → organize by type
- Other projects: Typically 1-2 analyses per repo → flat structure with descriptive names

#### CLI Parameter Enhancement

**New optional parameter for all commands:**
```bash
gitingest-agent [command] [options] --output-dir <path>

# Examples:
gitingest-agent analyze <url> --output-dir "../react-project/context/related-repos"
gitingest-agent analyze <url> --output-dir "C:/projects/my-app/research"
```

**Implementation:**
```python
@click.group()
def gitingest_agent():
    """GitIngest Agent CLI"""
    pass

@gitingest_agent.command()
@click.argument('url')
@click.option('--output-dir', default=None, help='Custom output directory')
def analyze(url, output_dir):
    """Analyze repository and save results"""
    storage = StorageManager(output_dir=output_dir)
    # ... rest of implementation
```

### Context Folder Standard

#### Proposed Structure for All BMAD Projects

```
[Any Software Project]/
├── .bmad-core/              # BMAD framework
├── explore/                 # BMAD working folders
├── plan/
├── execute/
├── context/                 # NEW: External context folder (optional)
│   ├── related-repos/      # GitIngest analyses
│   │   ├── [repo1]-[type].md
│   │   └── [repo2]-[type].md
│   ├── research/           # Other research materials
│   └── references/         # Documentation, specs, etc.
├── CLAUDE.md
└── README.md
```

**Benefits:**
- **Consistent location** across all projects
- **Clear purpose** - external context vs internal BMAD workflow
- **Optional** - only created when needed
- **Extensible** - can store other context types beyond GitIngest

**Documentation (add to project READMEs):**
```markdown
## Context Folder

The `context/` folder contains external research and reference materials:

- `related-repos/` - Analyses of related repositories (via GitIngest Agent)
- `research/` - General research notes and findings
- `references/` - Third-party documentation, specs, examples

This folder is optional and created as needed.
```

### Implementation Approach

#### Phase 1: Core Clone (V2 Spec)
**Duration:** 3-4 hours
**Deliverable:** Working GitIngest Agent with V2 functionality

**Implementation:**
1. Build CLI with hardcoded paths (V2 design)
2. Test all workflows in gitingest-agent-project
3. Validate automation works
4. Complete V2 regression test suite

**Success Criteria:**
- All V2 acceptance criteria met
- Tool works as demonstrated in video
- Ready to use for GitIngest Agent development

#### Phase 1.5: Multi-Location Enhancement
**Duration:** 1-2 hours
**Prerequisite:** Phase 1 complete and tested

**Implementation Sequence:**
1. **Refactor storage layer** (30 min)
   - Extract hardcoded paths to StorageManager class
   - Add path detection logic
   - Maintain V2 behavior when in gitingest-agent-project

2. **Add CLAUDE.md location detection** (20 min)
   - Add Step 5A: Detect Project Context
   - Add Step 5B: Route Based on Context
   - Test prompt variations

3. **Implement CLI parameter** (15 min)
   - Add --output-dir option
   - Wire to StorageManager
   - Test manual override

4. **Add context folder creation** (10 min)
   - Auto-create context/related-repos/ if needed
   - Handle permissions errors gracefully

5. **Testing** (25 min)
   - Test from gitingest-agent-project (V2 regression)
   - Test from another BMAD project
   - Test from arbitrary directory
   - Test with --output-dir parameter

**Success Criteria:**
- V2 regression tests still pass (backward compatible)
- Works from any BMAD project directory
- Correctly creates context/related-repos/ structure
- --output-dir parameter functions correctly

### Testing Strategy

#### Test Scenarios

**Scenario 1: V2 Regression (Critical)**
```
Setup: cd gitingest-agent-project
Action: Analyze small repo
Expected: Saves to data/ and analyze/ (V2 behavior)
Validate: No changes to V2 functionality
```

**Scenario 2: BMAD Project Detection**
```
Setup: cd react-component-test-project
Action: Analyze React repo
Expected:
  - Detects BMAD project
  - Prompts for save location
  - Creates context/related-repos/
  - Saves to react-installation.md
```

**Scenario 3: Custom Output Directory**
```
Setup: Any directory
Action: Analyze with --output-dir parameter
Expected: Saves to specified location
```

**Scenario 4: Unknown Directory**
```
Setup: cd ~/Desktop
Action: Analyze repo
Expected:
  - Prompts for location
  - Offers clear options
  - Handles user choice correctly
```

**Scenario 5: Cross-Project Workflow**
```
Setup: Multiple BMAD projects
Action: Analyze different repos in each project
Expected:
  - Each analysis saves to correct project's context/
  - Files organized consistently
  - No cross-contamination
```

#### Test Data

**Test Repositories:**
- **Small (<50k):** https://github.com/octocat/Hello-World
- **Medium (50-200k):** TBD - find appropriate repo
- **Large (>200k):** https://github.com/facebook/react

**Test Projects:**
- gitingest-agent-project (has .bmad-core)
- react-component-test-project (has .bmad-core)
- podcast-processor-cli-tool (has .bmad-core)
- Non-BMAD directory (~/Desktop)

### BMAD Persona Impact Analysis

#### Product Owner Perspective

**MVP Definition (Phase 1):**
- **Goal:** Validate GitIngest Agent concept works
- **Scope:** V2 specification only
- **Success:** Can analyze repos from gitingest-agent-project
- **Risk:** Low - proven design from video

**Phase 1.5 Value Proposition:**
- **Goal:** Make tool universally useful
- **Value:** Unlocks cross-project utility
- **User Impact:** High - solves real workflow friction
- **Risk:** Low - isolated enhancement to storage layer

**Prioritization Decision:**
```
Ship Phase 1 if:
- Time constrained
- Need to validate core concept first
- Want to gather usage data

Proceed to Phase 1.5 if:
- Phase 1 works smoothly
- 1-2 hours available
- Want production-ready tool immediately
```

#### Architect Perspective

**Design Principles:**
1. **Backward Compatibility:** V2 behavior preserved when in gitingest-agent-project
2. **Separation of Concerns:** Path resolution abstracted from business logic
3. **Open/Closed Principle:** Storage layer open for extension (new locations), closed for modification (core logic)
4. **Fail Safe:** Default to V2 behavior if detection fails

**Architecture Decision Record:**

**ADR-001: Storage Location Abstraction**
- **Context:** Need flexible output locations without breaking V2 design
- **Decision:** Create StorageManager class with path resolution logic
- **Consequences:**
  - ✅ Clean separation between "what to save" and "where to save"
  - ✅ Easy to test both behaviors independently
  - ✅ Can add new location types without changing core logic
  - ⚠️ Slightly more complex than hardcoded paths

**ADR-002: Context Folder Standard**
- **Context:** Need consistent structure across BMAD projects
- **Decision:** Standardize on `context/related-repos/` for all projects
- **Consequences:**
  - ✅ Predictable location across projects
  - ✅ Clear purpose separation (context vs BMAD workflow)
  - ✅ Extensible for other context types
  - ⚠️ New convention to document and maintain

#### Developer Perspective

**Implementation Complexity:**
- **Core Clone (Phase 1):** Medium - Click framework + GitIngest integration
- **Multi-Location (Phase 1.5):** Low - isolated to storage layer
- **Risk Assessment:** Low - enhancement doesn't touch core workflow logic

**Code Changes Required:**
```python
# Files to modify:
storage.py          # NEW - StorageManager class
cli.py              # ADD --output-dir parameter
CLAUDE.md          # ADD Step 5: Location Detection

# Files unchanged:
token_counter.py    # No changes needed
workflow.py         # No changes needed
extractor.py        # No changes needed
```

**Development Sequence:**
1. ✅ Build V2 clone completely
2. ✅ Test V2 end-to-end
3. ✅ Refactor storage to StorageManager (no behavior change yet)
4. ✅ Test V2 still works (refactor validation)
5. ✅ Add path detection logic
6. ✅ Test new scenarios
7. ✅ Update CLAUDE.md
8. ✅ Final integration test

**Rollback Strategy:**
If Phase 1.5 causes issues:
- Revert storage.py to hardcoded paths
- Revert CLAUDE.md to V2 version
- Ship Phase 1 only
- Investigate issues separately

#### QA Perspective

**Test Suite Structure:**
```
tests/
├── test_v2_regression/      # Phase 1 tests (must always pass)
│   ├── test_token_counting.py
│   ├── test_workflow_routing.py
│   ├── test_extraction.py
│   └── test_v2_storage.py
├── test_enhancement/         # Phase 1.5 tests (new functionality)
│   ├── test_storage_manager.py
│   ├── test_path_detection.py
│   ├── test_context_folder.py
│   └── test_cross_project.py
└── test_integration/         # End-to-end scenarios
    ├── test_gitingest_project_workflow.py
    ├── test_bmad_project_workflow.py
    └── test_custom_location_workflow.py
```

**Testing Priorities:**
1. **Critical:** V2 regression suite (Phase 1 must work)
2. **High:** Path detection logic (core enhancement)
3. **Medium:** Context folder creation
4. **Low:** Edge cases (unusual directory structures)

**Acceptance Testing:**
- [ ] Developer can use tool from gitingest-agent-project (V2)
- [ ] Developer can use tool from any BMAD project (enhanced)
- [ ] Analysis saved to correct location in all scenarios
- [ ] Context folder created when needed
- [ ] No breaking changes to V2 functionality

#### Scrum Master Perspective

**Sprint Planning:**

**Sprint 1: Core Clone**
- **Story Points:** 5 (medium complexity)
- **Duration:** 1 sprint (assuming 4-6 hour sprint)
- **Stories:**
  - Implement Click CLI structure
  - Add GitIngest wrapper commands
  - Build token counting and routing
  - Create CLAUDE.md automation
  - Test V2 workflows

**Sprint 1.5: Enhancement (Optional)**
- **Story Points:** 2 (low complexity)
- **Duration:** 0.5 sprint (1-2 hours)
- **Stories:**
  - Refactor storage layer
  - Add path detection
  - Update CLAUDE.md
  - Test cross-project scenarios

**Risk Management:**
- **Risk:** Phase 1 takes longer than estimated
  - **Mitigation:** Phase 1.5 is optional - can defer
- **Risk:** Path detection logic buggy
  - **Mitigation:** Fail safe to V2 behavior
- **Risk:** CLAUDE.md prompts unclear
  - **Mitigation:** Iterative refinement based on testing

**Definition of Done:**
- [ ] Code complete and reviewed
- [ ] All tests passing (regression + enhancement)
- [ ] CLAUDE.md updated and tested
- [ ] Documentation updated
- [ ] Manual testing scenarios validated
- [ ] No known critical bugs

### Risk Assessment

#### Technical Risks

**Risk 1: Path Detection Logic Fails**
- **Probability:** Low
- **Impact:** Medium (falls back to V2 behavior)
- **Mitigation:**
  - Thorough testing across directory structures
  - Clear error messages if detection fails
  - Fail-safe default to V2 behavior

**Risk 2: CLAUDE.md Prompts Confusing**
- **Probability:** Medium (prompt refinement always needed)
- **Impact:** Low (usability issue, not functional)
- **Mitigation:**
  - Manual testing with real scenarios
  - Iterative prompt refinement
  - Clear examples in prompts

**Risk 3: Cross-Project File Conflicts**
- **Probability:** Very Low
- **Impact:** Low (file overwrite)
- **Mitigation:**
  - Timestamp-based naming if needed
  - Warn before overwriting existing files
  - Document naming conventions

#### Schedule Risks

**Risk 4: Phase 1 Exceeds Time Estimate**
- **Probability:** Medium (common in development)
- **Impact:** Low (defer Phase 1.5)
- **Mitigation:**
  - Phase 1.5 explicitly optional
  - Can ship V2 clone as complete product
  - Enhancement can be added later

**Risk 5: Enhancement Breaks V2 Functionality**
- **Probability:** Low (isolated refactor)
- **Impact:** High (regression)
- **Mitigation:**
  - Comprehensive V2 regression tests
  - Test V2 before adding enhancement
  - Easy rollback strategy

### Success Metrics

#### Phase 1 Success Criteria
- [ ] All V2 specification requirements implemented
- [ ] Tool works from gitingest-agent-project directory
- [ ] Workflow automation functions via CLAUDE.md
- [ ] Token routing logic correct (< 200k vs >= 200k)
- [ ] Files saved to data/ and analyze/ correctly
- [ ] Can analyze small, medium, and large repos

#### Phase 1.5 Success Criteria
- [ ] All Phase 1 tests still pass (backward compatible)
- [ ] Tool works from any BMAD project directory
- [ ] Context folder created automatically when needed
- [ ] Analysis saved to correct project context
- [ ] --output-dir parameter works correctly
- [ ] Can switch between projects seamlessly

#### User Acceptance Criteria
- [ ] User can analyze repos while working in any project
- [ ] Analysis available as context in relevant project
- [ ] No manual file copying required
- [ ] Consistent experience across projects
- [ ] Tool "just works" regardless of directory

### Fallback Plan

**If Phase 1.5 encounters issues:**

1. **Immediate:** Revert to V2 behavior
2. **Short-term:** Ship V2 clone as v1.0
3. **Medium-term:** Investigate and fix enhancement issues
4. **Alternative:** User can manually use --output-dir parameter
5. **Future:** Add multi-location as v1.1 update

**V2 Clone is independently valuable:**
- Proves concept works
- Useful for GitIngest Agent development itself
- Can analyze repos (just need to move files manually)
- Foundation for future enhancements

### Documentation Requirements

#### User Documentation (README.md)

**Section: Basic Usage (Phase 1)**
```markdown
## Basic Usage

Navigate to GitIngest Agent project:
cd "Software Projects/gitingest-agent-project"

Provide GitHub URL to Claude Code:
"Analyze https://github.com/user/repo"

Analysis saved to:
- data/[repo-name]/ - Repository extractions
- analyze/[type]/ - Analysis outputs
```

**Section: Cross-Project Usage (Phase 1.5)**
```markdown
## Using GitIngest Agent from Other Projects

GitIngest Agent works from any BMAD project directory:

cd "Software Projects/your-project"
"Analyze https://github.com/related/repo"

Agent will detect your project and ask:
"Save analysis to this project's context folder?"

If yes, creates:
your-project/context/related-repos/repo-analysis.md

This keeps analysis with the project that needs it.
```

#### Developer Documentation

**Section: Storage Architecture**
Document StorageManager class, path resolution logic, and extension points.

**Section: Adding New Output Locations**
Guide for adding new location types beyond gitingest-agent-project and context folders.

### Future Enhancement Ideas (Phase 2+)

Building on multi-location capability:

1. **Analysis Collections:** Group related analyses together
2. **Cross-Reference:** Link analyses when repos reference each other
3. **Sync to Cloud:** Share context folders across machines
4. **Analysis Index:** Generate table of contents for context/related-repos/
5. **Smart Suggestions:** Recommend repos to analyze based on project dependencies

---

## Integration with V2 Specification

### How to Use Both Documents

**During Explore Phase:**
1. Read V2 Section 3.1 for core research tasks
2. Add from Addendum: Path detection research (Python Path, os.getcwd)
3. Combined research estimate: V2 (2-3hr) + Addendum (30min) = 2.5-3.5hr

**During Plan Phase:**
1. Create PRD based on V2 Section 3.2
2. Add from Addendum: Multi-location user stories, acceptance criteria
3. Architecture must support both V2 and enhanced behaviors
4. Phase 1 vs Phase 1.5 explicitly called out in PRD

**During Execute Phase:**
1. Implement V2 completely first (Section 3.3)
2. Test V2 end-to-end
3. Then add enhancement from Addendum
4. Test regression + new scenarios
5. Update CLAUDE.md with enhanced workflow

### BMAD Persona Reference Guide

**When acting as Analyst:**
- Research topics from V2 + Addendum combined
- Estimate complexity: V2 (medium) + Addendum (low)

**When acting as Product Owner:**
- V2 = MVP, Addendum = Enhancement
- Can ship V2 independently if needed
- Addendum adds significant user value

**When acting as Architect:**
- Design storage layer for both use cases from start
- But implement V2 first, enhance second
- Backward compatibility is critical

**When acting as Developer:**
- Build V2 completely
- Refactor for enhancement
- Test both behaviors independently

**When acting as QA:**
- V2 regression suite (must pass)
- Enhancement test suite (new)
- Integration scenarios (both)

**When acting as Scrum Master:**
- Sprint 1: V2 (5 points)
- Sprint 1.5: Enhancement (2 points)
- Optional: Can defer 1.5 if needed

---

## Appendix: Example Workflows

### Workflow 1: Analyzing for GitIngest Agent Itself

```bash
# Researching Click framework for implementation
cd "Software Projects/gitingest-agent-project"

"Analyze https://github.com/pallets/click"

# V2 behavior:
→ Saves to: data/click/digest.txt
→ Analysis to: analyze/architecture/click.md

# Used while building GitIngest Agent
```

### Workflow 2: Analyzing for Another Project

```bash
# Working on React project, need to understand React 19
cd "Software Projects/react-component-test-project"

"Analyze https://github.com/facebook/react"

# Enhanced behavior:
→ Detects BMAD project
→ Asks: "Save to this project's context folder?"
→ User: "Yes"
→ Creates: context/related-repos/
→ Saves to: context/related-repos/react-architecture.md

# Analysis now available as project context
```

### Workflow 3: Custom Location

```bash
# Analyzing for external documentation
cd anywhere

"Analyze https://github.com/user/repo --output-dir ~/Documents/Research"

# Enhanced behavior:
→ Validates path exists
→ Saves to: ~/Documents/Research/repo-analysis.md

# User has full control
```

### Workflow 4: Multiple Projects, Same Session

```bash
# Session 1: React project
cd "Software Projects/react-component-test-project"
"Analyze https://github.com/facebook/react"
→ Saves to: react-component-test-project/context/related-repos/

# Session 2: Podcast project
cd "Software Projects/podcast-processor-cli-tool"
"Analyze https://github.com/ytdl-org/youtube-dl"
→ Saves to: podcast-processor-cli-tool/context/related-repos/

# Each analysis in correct project context
```

---

## Document Metadata

**Version:** 1.0
**Status:** Approved for implementation
**Created:** 2025-09-29
**Author:** User + Claude Code collaboration
**Review Status:** Reviewed by all BMAD personas

**Related Documents:**
- `gitingest-agent-comprehensive-specification-v2.md` - Core requirements (Phase 1)
- `gitingest-agent-project-overview.md` - High-level project summary

**Implementation Status:**
- Phase 1 (V2): Not started
- Phase 1.5 (This addendum): Not started (depends on Phase 1)

**Next Actions:**
1. Begin BMAD Explore Phase with combined research topics
2. Create PRD incorporating V2 + Addendum requirements
3. Design architecture supporting both behaviors
4. Implement Phase 1 (V2 clone)
5. Test and validate Phase 1
6. Implement Phase 1.5 (Multi-location enhancement)
7. Test and validate Phase 1.5

---

*This requirements addendum defines custom enhancements that extend the proven V2 design to meet user-specific workflow needs. It maintains clear separation between "proven original" (V2) and "custom additions" (Addendum) while providing complete integration guidance for BMAD development workflow.*