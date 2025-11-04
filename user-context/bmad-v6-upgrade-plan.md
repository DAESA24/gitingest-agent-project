# BMAD v4 to v6 Alpha5 Upgrade Plan

## Executive Summary

This document outlines the upgrade path from BMAD METHOD v4 to v6.0.0-alpha5 for the gitingest-agent project, specifically targeting the v2.0 development phase.

- **Current State:** BMAD v4 (`.bmad-core/`) with completed v1.1.0
- **Target State:** BMAD v6 alpha5 (`bmad/`) for v2.0 development
- **Upgrade Type:** Major version upgrade with architectural changes
- **Risk Level:** Medium (automatic backup, non-destructive)
- **Estimated Time:** 1-2 hours

---

## Table of Contents

1. [What's Changing](#whats-changing)
2. [Pre-Upgrade Assessment](#pre-upgrade-assessment)
3. [Breaking Changes Impact](#breaking-changes-impact)
4. [Upgrade Strategy](#upgrade-strategy)
5. [Step-by-Step Upgrade Process](#step-by-step-upgrade-process)
6. [Post-Upgrade Configuration](#post-upgrade-configuration)
7. [V2.0 Initialization](#v20-initialization)
8. [Rollback Plan](#rollback-plan)
9. [Validation Checklist](#validation-checklist)

---

## 1. What's Changing

### 1.1 BMAD v6 Alpha5 Key Features

**3-Track Scale System (Revolutionary)**
- **Old (v4):** 5-level hierarchy (confusing, artificial)
- **New (v6):** 3 intuitive tracks (Quick Flow, BMad Method, Enterprise Method)
- **Impact:** Simplifies project classification and workflow selection

**Workflow Modernization**
- Replaced legacy XML elicit tags with explicit `invoke-task` patterns
- Streamlined input document discovery (114 lines of repeated content eliminated)
- Standardized epic/story templates with BDD-style acceptance criteria
- Improved workflow.yaml consistency

**Documentation Accuracy**
- Agent YAML files now authoritative source
- Fixed agent ownership attributions
- Capability descriptions match actual configurations

**Brownfield Development Guidance**
- Phase 0 rewritten for real-world scenarios
- Projects without documentation: `document-project` workflow option
- Massive existing files: Shard before indexing

**PM/UX Evolution**
- Product leaders as "code orchestrators"
- AI-optimized requirements directly into agentic pipelines

### 1.2 Breaking Changes Summary

- **Variable Rename:** `project_level` → `project_track`
- **Variable Removed:** `target_scale` (no longer used)
- **Workflow Paths:** 9 level-based → 6 track-based alternatives
- **Agent File Rename:** `paige.agent.yaml` → `tech-writer.agent.yaml`

### 1.3 Architecture Transformation

**v4 "Expansion Packs" Model:**
```
your-project/
├── .bmad-core/          # Was the "BMad Method"
├── .bmad-game-dev/      # Game development module
├── .bmad-creative-writing/  # Creative module
└── .bmad-infrastructure-devops/  # Infrastructure module
```

**v6 Unified Structure:**
```
your-project/
└── bmad/
    ├── core/            # Real core framework (universal)
    ├── bmm/             # BMad Method (software development)
    ├── bmb/             # BMad Builder (coming soon)
    ├── cis/             # Creative Intelligence Suite (coming soon)
    └── _cfg/
        └── agents/      # Customizations (.customize.yaml files)
```

**Key Insight:** v4's `.bmad-core` was actually the BMad Method. v6's `bmad/core/` is the true universal framework.

---

## 2. Pre-Upgrade Assessment

### 2.1 Current Project State

**Project:** gitingest-agent-project
- **Version:** v1.1.0 (complete)
- **Status:** Phase 1.5 complete, ready for v2.0
- **BMAD Version:** v4
- **BMAD Location:** `.bmad-core/`
- **Documentation:**
  - PRD: `docs/prd.md` (unsharded)
  - Architecture: `docs/architecture.md` (sharded to `docs/architecture/`)
  - Stories: `docs/stories/`
  - QA: `docs/qa/`

**BMAD v4 Configuration:**
```yaml
# .bmad-core/core-config.yaml
markdownExploder: true
prd:
  prdFile: docs/prd.md
  prdVersion: v4
  prdSharded: false
architecture:
  architectureFile: docs/architecture.md
  architectureVersion: v4
  architectureSharded: true
  architectureShardedLocation: docs/architecture
devStoryLocation: docs/stories
```

### 2.2 Upgrade Readiness

**✅ Ready for Upgrade:**
- Planning phase complete (PRD + Architecture)
- v1.1.0 fully implemented and tested
- Documentation structure established
- No active development in progress
- Clean git status (all committed)

**⚠️ Considerations:**
- Custom agent configurations (if any) need migration
- IDE command cleanup recommended (optional)
- Story templates may change (BDD-style in v6)

### 2.3 Files to be Backed Up

The installer will automatically back up:
- `.bmad-core/` → `v4-backup/.bmad-core/`
- Any legacy IDE commands in `.claude/commands/` (optional manual cleanup)

**Backup Location:** `v4-backup/` in project root

---

## 3. Breaking Changes Impact

### 3.1 Variable Name Changes

**`project_level` → `project_track`**

**Impact:** Low (installer handles automatically)
- v6 auto-detects track from context
- No manual configuration required
- Workflows reference new variable name internally

**Action Required:** None (automatic)

### 3.2 Workflow Path Changes

**9 Level-Based Paths → 6 Track-Based Paths**

**Old (v4):**
- `brownfield-service` (L1)
- `brownfield-ui` (L1)
- `brownfield-fullstack` (L1)
- `greenfield-service` (L2-L5)
- `greenfield-ui` (L2-L5)
- `greenfield-fullstack` (L2-L5)
- Plus 3 more specialized paths

**New (v6):**
- `quick-flow-service`
- `quick-flow-ui`
- `bmad-method-service`
- `bmad-method-ui`
- `enterprise-method-service`
- `enterprise-method-ui`

**Impact for gitingest-agent:** Medium
- **Current Track:** BMad Method (we have PRD, Architecture, Stories)
- **Workflow Type:** Service/CLI (no UI component)
- **New Workflow:** `bmad-method-service`

**Action Required:** Reference new workflow name in v6

### 3.3 Agent File Changes

**`paige.agent.yaml` → `tech-writer.agent.yaml`**

**Impact:** Low (we haven't used Paige agent)
- Only affects documentation generation workflows
- New name reflects role consistency

**Action Required:** None (we don't reference this agent)

### 3.4 Template Changes

**Story Templates: Traditional → BDD-Style**

**Old (v4):**
```markdown
## Acceptance Criteria
- Criterion 1
- Criterion 2
```

**New (v6):**
```markdown
## Acceptance Criteria

**Given** [context/preconditions]
**When** [action/event]
**Then** [expected outcome]
```

**Impact:** Low (v2.0 stories not yet created)
- v1.x stories remain unchanged (historical record)
- v2.0 stories will use BDD format
- More rigorous acceptance criteria

**Action Required:** Adapt to BDD format for v2.0 stories

---

## 4. Upgrade Strategy

### 4.1 Upgrade Approach

**Philosophy:** Non-Destructive, Backward Compatible

1. **Automatic Backup:** v4 files moved to `v4-backup/`
2. **Clean Installation:** v6 installed to `bmad/`
3. **Document Compatibility:** Existing docs work as-is (unsharded/sharded both supported)
4. **Progressive Adoption:** Use v4 backup as reference during transition

### 4.2 Timing Recommendation

**Ideal Timing:** NOW (Before v2.0 development starts)

**Reasons:**
- v1.1.0 complete and stable
- No active story implementation
- v2.0 planning not yet started
- Clean slate for new track-based workflows
- Alpha5 is latest stable preview
- Avoid mid-development migration

**Risk Mitigation:**
- v4 backup available for reference
- v1.x work unaffected (historical)
- v2.0 starts fresh with v6

### 4.3 Migration vs. Fresh Start

**For v1.x (Completed Work):**
- **Keep as-is:** No migration needed
- v1.x stories are historical record
- v1.x documentation remains valid
- Git history preserved

**For v2.0 (New Development):**
- **Fresh start with v6**
- Use new track system (BMad Method)
- Use new BDD story templates
- Use new workflow paths
- Benefit from alpha5 improvements

---

## 5. Step-by-Step Upgrade Process

### 5.1 Prerequisites

**Environment Check:**
```bash
# Verify Node.js and npm installed (for BMAD installer)
node --version   # Should be v18+ or v20+
npm --version    # Should be v9+ or v10+

# Verify git status clean
cd c:\Users\drewa\work\dev\gitingest-agent-project
git status       # Should show "working tree clean"

# Create a git checkpoint (optional but recommended)
git tag v1.1.0-bmad-v4-checkpoint
git push origin v1.1.0-bmad-v4-checkpoint
```

**Download BMAD-METHOD v6:**
```bash
# Navigate to a temporary location (NOT your project root)
cd c:\Users\drewa\work\dev
git clone https://github.com/bmad-code-org/BMAD-METHOD
cd BMAD-METHOD

# Verify version
git log --oneline -1
# Should show commit related to v6.0.0-alpha5 or later

# Install installer dependencies
npm install
```

### 5.2 Run Installer

**Launch Interactive Installer:**
```bash
# From BMAD-METHOD directory
npx bmad-method install

# When prompted for project path:
C:\Users\drewa\work\dev\gitingest-agent-project
```

### 5.3 Installer Prompts & Responses

**Prompt 1: V4 Detection**
```
✓ Detected BMAD v4 installation (.bmad-core/)
? Back up v4 files to v4-backup/? (Y/n)
```
**Response:** Y (Yes - automatic backup)

**Prompt 2: IDE Command Cleanup**
```
✓ Found legacy IDE commands in .claude/commands/
  These may conflict with v6 agent system.
? Remove legacy v4 IDE commands? (Y/n)
```
**Response:** Y (Yes - clean slate for v6)

**Prompt 3: Module Selection**
```
? Select modules to install:
  [x] BMM (BMad Method) - Software development
  [ ] BMB (BMad Builder) - Coming soon
  [ ] CIS (Creative Intelligence Suite) - Coming soon
```
**Response:** Select only BMM (Space to select, Enter to confirm)

**Prompt 4: Core Settings**
```
? Project documentation location: (docs/)
```
**Response:** Accept default `docs/` (matches current structure)

**Prompt 5: Document Format**
```
? PRD format:
  ( ) Single file (docs/prd.md)
  (*) Sharded (docs/prd/)
```
**Response:** Single file (matches current `docs/prd.md`)

**Prompt 6: Architecture Format**
```
? Architecture format:
  ( ) Single file (docs/architecture.md)
  (*) Sharded (docs/architecture/)
```
**Response:** Sharded (matches current `docs/architecture/`)

**Prompt 7: Story Location**
```
? Story location: (docs/stories/)
```
**Response:** Accept default `docs/stories/` (matches current structure)

**Prompt 8: IDE Integration**
```
? Configure IDE integrations:
  [x] Claude Code (.claude/)
  [ ] Cursor
  [ ] Windsurf
```
**Response:** Select Claude Code (we're using Claude Code)

**Prompt 9: Installation Confirmation**
```
? Install BMAD v6 with these settings? (Y/n)

  Summary:
  - Modules: BMM
  - Docs: docs/
  - PRD: docs/prd.md (single)
  - Architecture: docs/architecture/ (sharded)
  - Stories: docs/stories/
  - IDE: Claude Code
```
**Response:** Y (Yes - proceed with installation)

### 5.4 Installation Process

The installer will:
1. ✓ Back up `.bmad-core/` to `v4-backup/.bmad-core/`
2. ✓ Remove legacy IDE commands (if selected)
3. ✓ Create `bmad/` directory structure
4. ✓ Install core framework (`bmad/core/`)
5. ✓ Install BMM module (`bmad/bmm/`)
6. ✓ Create configuration files (`bmad/_cfg/`)
7. ✓ Configure IDE integration (`.claude/`)
8. ✓ Generate installation report

**Expected Output:**
```
✓ BMAD v6 installation complete!

  Installation Summary:
  - v4 backup: v4-backup/.bmad-core/
  - v6 location: bmad/
  - Modules: BMM (BMad Method)
  - IDE: Claude Code configured

  Next Steps:
  1. Run workflow-init (see docs/ide-info/claude-code.md)
  2. Specify project track (BMad Method recommended)
  3. Review agent system (bmad/bmm/agents/)

  Documentation: bmad/docs/
  Support: https://discord.gg/gk8jAdXWmj
```

### 5.5 Verify Installation

**Check File Structure:**
```bash
# From project root
ls bmad/
# Expected: core/, bmm/, _cfg/, docs/

ls bmad/bmm/
# Expected: agents/, workflows/, templates/, tasks/

ls bmad/_cfg/
# Expected: agents/ (empty - for customizations)

ls v4-backup/
# Expected: .bmad-core/
```

**Check IDE Integration:**
```bash
# From project root
ls .claude/
# Expected: claude_agent_files.yaml or similar v6 config
```

**Git Status Check:**
```bash
git status
# Expected:
#   new file: bmad/
#   new file: v4-backup/
#   modified: .claude/
#   deleted: .bmad-core/ (tracked separately in backup)
```

---

## 6. Post-Upgrade Configuration

### 6.1 Initialize Workflow System

**Load Analyst Agent:**

Follow IDE-specific instructions from `bmad/docs/ide-info/claude-code.md`:

```
In Claude Code:
1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type: "Claude Code: Manage Agents"
3. Select: Analyst (from BMM module)
4. Agent menu will appear
```

**Or use text-based invocation:**
```
@analyst
```

**Run workflow-init:**
```
@analyst *workflow-init
```

### 6.2 Workflow Initialization Prompts

**Prompt 1: Project Track**
```
? Select project track:
  ( ) Quick Flow - Rapid prototyping, minimal docs
  (*) BMad Method - Comprehensive planning, testing
  ( ) Enterprise Method - Large teams, compliance
```
**Response:** BMad Method (matches v1.x approach)

**Prompt 2: Project Level**
```
Your project has completed PRD and Architecture.
This maps to Level 3 in the BMad Method track.

? Confirm project level: (3)
  1 - Concept only
  2 - PRD complete
  3 - Architecture complete ← YOU ARE HERE
  4 - Active development
  5 - Production-ready
```
**Response:** 3 (Architecture complete, ready for v2.0 stories)

**Prompt 3: Document Locations**
```
? PRD location: (docs/prd.md)
? Architecture location: (docs/architecture/)
? Story location: (docs/stories/)
```
**Response:** Accept defaults (matches current structure)

**Prompt 4: Workflow Selection**
```
Based on your project type (CLI tool, no UI):
Recommended workflow: bmad-method-service

? Confirm workflow: (bmad-method-service)
```
**Response:** Accept default `bmad-method-service`

### 6.3 Configuration Summary

After workflow-init completes, you'll have:

**Workflow Context File:** `bmad/_cfg/workflow-context.yaml`
```yaml
project_track: bmad-method
project_level: 3
workflow_type: service
documents:
  prd: docs/prd.md
  architecture: docs/architecture/
  stories: docs/stories/
agent_team: team-no-ui
```

### 6.4 Agent System Verification

**List Available Agents:**
```
@analyst *list-agents
```

**Expected Output:**
```
Available BMM Agents:
- @analyst - Requirements elicitation
- @architect - System design
- @pm - Project management
- @dev - Development implementation
- @qa - Quality assurance
- @sm - Story management
- @po - Product ownership

Current Team: team-no-ui (Analyst, Architect, PM, Dev, QA, SM, PO)
```

### 6.5 Update Project Documentation

**Update README.md:**

Add BMAD v6 references:
```markdown
### Development Workflow

This project uses **BMAD (Breakthrough Method for AI-driven Agile Development) v6.0**.

**Workflow:**
- **Story Creation**: `@sm *draft-story`
- **Story Implementation**: `@dev *implement-story {story}`
- **Story Review**: `@qa *review-story {story}`
- **Risk Assessment**: `@qa *assess-risk {story}`

See `bmad/docs/` for complete workflow documentation.
```

**Update CLAUDE.md (Project Root):**

Reference v6 system:
```markdown
## BMAD Integration

This project uses BMAD METHOD v6.0 (bmad/ directory).

**Key Agents:**
- `@analyst` - Requirements and planning
- `@architect` - System design
- `@dev` - Implementation
- `@qa` - Quality assurance
- `@sm` - Story management

**Workflows:**
- Story creation: `@sm *draft-story`
- Sprint planning: `@pm *sprint-planning`
- Development: `@dev *implement-story`
```

---

## 7. V2.0 Initialization

### 7.1 Starting V2.0 Development with BMAD v6

Now that v6 is installed, you can begin v2.0 development using the new system.

**Phase 2.0 Goals:**
- TOON format integration (15-25% token savings)
- Multi-agent architecture (parallel sub-agents)
- Multi-repo comparison analysis
- GitHub API integration

### 7.2 Create V2.0 Epic

**Invoke Story Management Agent:**
```
@sm *draft-epic
```

**Provide Epic Details:**
```
Epic Title: Phase 2.0 - Multi-Repository Analysis

Description:
Extend GitIngest Agent to support multi-repository analysis through
TOON format integration and parallel sub-agent orchestration.

Key Features:
- TOON format conversion (15-25% token savings)
- Multi-agent parallel processing (5+ repositories)
- Multi-repo comparison synthesis
- GitHub API integration with TOON

Stories:
1. TOON Format Integration (2.1)
2. Multi-Repo Sequential Analysis (2.2)
3. Parallel Sub-Agent Orchestration (2.3)
4. GitHub API with TOON (2.4)
```

**SM will generate:** `docs/stories/epic-2.0.md` using v6 BDD template

### 7.3 Create First V2.0 Story (Story 2.1)

**Invoke Story Management Agent:**
```
@sm *draft-story epic-2.0
```

**Provide Story Details:**
```
Story: 2.1 - TOON Format Integration

Description:
Add TOON format support to extractor module for 15-25% token savings
on repository content, especially GitHub API data.

Acceptance Criteria (BDD Format):

**Given** a GitHub repository URL
**When** user runs extract-full with --format toon flag
**Then** content is converted to TOON format and saved with .toon extension

**Given** TOON-formatted content
**When** token counter processes the file
**Then** token count shows 15-25% reduction compared to JSON/text

**Given** extraction command with --format parameter
**When** format is 'text' (default)
**Then** existing Phase 1.5 behavior is preserved (backward compatible)

Implementation Notes:
- Add subprocess wrapper for TOON CLI (npm package @toon-format/cli)
- Update extractor.py with format parameter
- Update CLI commands with --format option
- Validate with docker/toon-test/ container
```

**SM will generate:** `docs/stories/2.1.story.md` using v6 BDD template

### 7.4 V2.0 Development Workflow

**Sprint Planning:**
```
@pm *sprint-planning
```

**PM will:**
- Review epic-2.0 and story 2.1
- Assess dependencies
- Estimate effort (2-4 hours for story 2.1)
- Create sprint plan

**Implementation:**
```
@dev *implement-story 2.1
```

**Dev will:**
- Read architecture.md section 14 (V2.0 preview)
- Implement TOON integration as specified
- Write tests (maintain 96%+ coverage)
- Update documentation

**Quality Assurance:**
```
@qa *review-story 2.1
```

**QA will:**
- Verify acceptance criteria (BDD format)
- Run test suite
- Validate token savings (15-25%)
- Check backward compatibility

### 7.5 V2.0 Branch Strategy

**Create V2.0 Development Branch:**
```bash
# From main branch (v1.1.0 complete)
git checkout -b v2.0-development

# Create first feature branch
git checkout -b feature/story-2.1-toon-integration

# After story 2.1 complete
git checkout v2.0-development
git merge feature/story-2.1-toon-integration
git push origin v2.0-development
```

**Branch Structure:**
```
main (v1.1.0 stable)
└── v2.0-development (v6 workflows)
    ├── feature/story-2.1-toon-integration
    ├── feature/story-2.2-multi-repo-sequential
    ├── feature/story-2.3-parallel-agents
    └── feature/story-2.4-github-api-toon
```

---

## 8. Rollback Plan

### 8.1 If Upgrade Fails During Installation

**Restore v4 from Backup:**
```bash
# From project root
rm -rf bmad/  # Remove incomplete v6 installation
cp -r v4-backup/.bmad-core .bmad-core  # Restore v4
git checkout .claude/  # Restore IDE config (if modified)
```

**Verify Restoration:**
```bash
ls .bmad-core/  # Should show v4 structure
git status  # Should show clean or only v4-backup/ as untracked
```

### 8.2 If Issues Discovered After Installation

**Parallel Operation (Recommended):**
- Keep both v4 (backup) and v6 (bmad/) available
- Use v4 backup as reference for v6 migration
- v4 workflows still accessible via backup

**Reference v4 While Using v6:**
```bash
# Read v4 agent files
cat v4-backup/.bmad-core/agents/dev.md

# Compare v4 vs v6 workflows
diff v4-backup/.bmad-core/workflows/brownfield-service.yaml \
     bmad/bmm/workflows/bmad-method-service.yaml
```

### 8.3 Complete Rollback (Last Resort)

**Full Restoration to v4:**
```bash
# Remove v6
rm -rf bmad/

# Restore v4
cp -r v4-backup/.bmad-core .bmad-core

# Restore IDE config
git checkout .claude/

# Commit rollback
git add .
git commit -m "Rollback: Restore BMAD v4 from backup"
git push origin main
```

**When to Rollback:**
- Critical v6 bugs blocking development
- Incompatibility with existing workflows
- Team decision to stay on v4

**Recommendation:** Rollback is unlikely needed. v6 is designed for backward compatibility.

---

## 9. Validation Checklist

### 9.1 Post-Installation Validation

**✓ File Structure:**
- [ ] `bmad/` directory exists with `core/`, `bmm/`, `_cfg/`
- [ ] `v4-backup/.bmad-core/` contains complete v4 installation
- [ ] `.claude/` updated with v6 agent configuration
- [ ] No `.bmad-core/` in project root (moved to backup)

**✓ Configuration:**
- [ ] `bmad/_cfg/workflow-context.yaml` created by workflow-init
- [ ] Project track set to "bmad-method"
- [ ] Project level set to 3 (architecture complete)
- [ ] Document paths match existing structure

**✓ IDE Integration:**
- [ ] `@analyst` command recognized in Claude Code
- [ ] Agent menu appears when invoked
- [ ] `*workflow-init` command executed successfully
- [ ] `*list-agents` shows all BMM agents

**✓ Git Status:**
- [ ] Changes staged or committed
- [ ] v4 checkpoint tag created (optional but recommended)
- [ ] No unintended file deletions
- [ ] `.gitignore` updated if needed (add `bmad/` if desired)

### 9.2 Functional Validation

**✓ Workflow System:**
- [ ] `@sm *draft-story` command works
- [ ] Story templates use BDD format
- [ ] `@dev *implement-story` command works
- [ ] `@qa *review-story` command works

**✓ Backward Compatibility:**
- [ ] v1.x stories still readable
- [ ] Existing documentation accessible
- [ ] No breaking changes to v1.x implementation
- [ ] Execute/CLI still functional

**✓ Documentation:**
- [ ] README.md updated with v6 references
- [ ] CLAUDE.md updated with v6 agent commands
- [ ] Architecture.md section 14 (V2.0) still accurate
- [ ] User-facing docs unchanged (users don't see BMAD internals)

### 9.3 V2.0 Readiness

**✓ Planning Phase:**
- [ ] V2.0 feature requirements documented
- [ ] Architecture section 14 (V2.0 preview) reviewed
- [ ] TOON validation completed (docker/toon-test/)
- [ ] Epic 2.0 ready for creation

**✓ Development Environment:**
- [ ] Node.js installed (for TOON CLI: @toon-format/cli)
- [ ] UV environment functional (execute/.venv)
- [ ] Test suite passing (190 tests, 96%+ coverage)
- [ ] Git branch strategy defined

**✓ Agent System:**
- [ ] `@sm` for story creation
- [ ] `@pm` for sprint planning
- [ ] `@dev` for implementation
- [ ] `@qa` for quality gates
- [ ] `@architect` for design reviews

---

## 10. Key Takeaways

### 10.1 Why Upgrade Now?

**Perfect Timing:**
- ✅ v1.1.0 complete and stable (no active development)
- ✅ v2.0 not yet started (clean slate)
- ✅ v6 alpha5 is latest stable (mature enough for use)
- ✅ Track system simplifies v2.0 workflow selection
- ✅ BDD templates improve v2.0 story quality

**Avoiding Future Pain:**
- ❌ Upgrading mid-v2.0 development is disruptive
- ❌ v4 is legacy and won't receive updates
- ❌ Missing out on workflow modernizations
- ❌ Delaying increases technical debt

### 10.2 What You Gain with v6

**Immediate Benefits:**
- Simpler track system (BMad Method = your natural fit)
- Better workflow clarity (bmad-method-service vs brownfield-service)
- Improved story templates (BDD format = clearer acceptance criteria)
- Agent file accuracy (authoritative YAML files)

**Long-Term Benefits:**
- Future-proof (v6 is the foundation for ongoing development)
- Better brownfield guidance (if you add Phase 0 later)
- Unified module system (if you add BMB or CIS later)
- Active community (v4 is legacy, v6 is current)

### 10.3 Risk Mitigation

**Low Risk Upgrade:**
- ✅ Automatic backup (v4-backup/)
- ✅ Non-destructive (v6 installs to bmad/, v4 preserved)
- ✅ Document compatibility (existing docs work as-is)
- ✅ Rollback available (restore from v4-backup/)
- ✅ No impact on v1.x (historical work untouched)

**What Can't Break:**
- ✓ v1.x implementation (execute/ directory untouched)
- ✓ Git history (commits remain unchanged)
- ✓ Tests (execute/tests/ still pass)
- ✓ CLI functionality (uv run gitingest-agent still works)
- ✓ User documentation (README.md, CHANGELOG.md)

### 10.4 Success Criteria

**Upgrade is successful when:**
1. ✅ `bmad/` directory structure created
2. ✅ `@analyst *workflow-init` completes successfully
3. ✅ `@sm *draft-story` generates BDD-format story
4. ✅ v4 backup accessible at `v4-backup/.bmad-core/`
5. ✅ No git-tracked files lost or corrupted
6. ✅ Ready to create epic-2.0 and story 2.1

---

## 11. Next Steps After Upgrade

### 11.1 Immediate (Day 1)

1. **Verify Installation:**
   - Run validation checklist (Section 9)
   - Test agent commands (@analyst, @sm, @dev, @qa)
   - Confirm workflow-init configuration

2. **Update Documentation:**
   - Update README.md with v6 references
   - Update CLAUDE.md with v6 agent commands
   - Commit changes with message: "chore: Upgrade to BMAD v6 alpha5"

3. **Create Git Checkpoint:**
   ```bash
   git tag v1.1.0-bmad-v6-upgraded
   git push origin v1.1.0-bmad-v6-upgraded
   ```

### 11.2 Short-Term (Week 1)

1. **Create V2.0 Epic:**
   - Use `@sm *draft-epic` command
   - Generate `docs/stories/epic-2.0.md`
   - Review with BDD format

2. **Create Story 2.1:**
   - Use `@sm *draft-story epic-2.0` command
   - Generate `docs/stories/2.1.story.md`
   - Validate acceptance criteria

3. **Sprint Planning:**
   - Use `@pm *sprint-planning` command
   - Review story 2.1 estimates
   - Create v2.0-development branch

### 11.3 Long-Term (Month 1)

1. **Implement Story 2.1:**
   - TOON format integration
   - Validate 15-25% token savings
   - Maintain 96%+ test coverage

2. **Continue V2.0 Stories:**
   - Story 2.2: Multi-repo sequential
   - Story 2.3: Parallel sub-agents
   - Story 2.4: GitHub API + TOON

3. **Release V2.0:**
   - Complete all Phase 2.0 stories
   - Update CHANGELOG.md
   - Create v2.0.0 release tag

---

## Appendix A: Reference Links

**BMAD METHOD v6:**
- **Repository:** https://github.com/bmad-code-org/BMAD-METHOD
- **Changelog:** https://github.com/bmad-code-org/BMAD-METHOD/blob/main/CHANGELOG.md#600-alpha5
- **Upgrade Guide:** https://github.com/bmad-code-org/BMAD-METHOD/blob/main/docs/v4-to-v6-upgrade.md
- **Discord Community:** https://discord.gg/gk8jAdXWmj

**GitIngest Agent V2.0:**
- **Architecture:** `docs/architecture.md` (Section 14: V2.0 Preview)
- **Feature Request:** `user-context/v2-toon-multiagent-feature-request.md`
- **TOON Validation:** `docker/toon-test/RESULTS.md`

---

## Appendix B: Troubleshooting

### Issue: Installer Not Found

**Error:** `npx bmad-method: command not found`

**Solution:**
```bash
# Ensure you're in BMAD-METHOD repository
cd c:\Users\drewa\work\dev\BMAD-METHOD

# Install dependencies
npm install

# Retry installer
npx bmad-method install
```

### Issue: V4 Backup Not Created

**Error:** Installer completes but no `v4-backup/` directory

**Solution:**
```bash
# Manually create backup before reinstalling
mkdir v4-backup
cp -r .bmad-core v4-backup/.bmad-core

# Retry installer
```

### Issue: Agent Commands Not Recognized

**Error:** `@analyst` command not found in Claude Code

**Solution:**
```bash
# Verify IDE configuration
cat .claude/claude_agent_files.yaml

# Restart Claude Code IDE
# Reload window (Ctrl+Shift+P > "Developer: Reload Window")

# Retry agent command
```

### Issue: Workflow-Init Fails

**Error:** `*workflow-init` command errors or hangs

**Solution:**
```bash
# Verify bmad/ structure
ls bmad/bmm/workflows/

# Check for workflow YAML files
ls bmad/bmm/workflows/*.yaml

# If missing, reinstall BMM module:
npx bmad-method install --modules bmm
```

### Issue: Git Conflicts After Upgrade

**Error:** Git shows unresolvable conflicts

**Solution:**
```bash
# Reset to pre-upgrade state
git reset --hard HEAD

# Restore v4 backup manually
mv v4-backup/.bmad-core .bmad-core

# Review upgrade plan and retry carefully
```

---

## Document Metadata

- **Created:** 2025-11-04
- **Author:** GitIngest Agent (Claude Code)
- **Version:** 1.0
- **Status:** ✅ Ready for Review
- **Related Documents:**
  - docs/architecture.md (Section 14: V2.0 Preview)
  - user-context/v2-toon-multiagent-feature-request.md
  - docker/toon-test/RESULTS.md

---

**Document Status:** ✅ Complete and Ready for Execution

**Next Action:** Review this plan, then proceed with [Section 5: Step-by-Step Upgrade Process](#5-step-by-step-upgrade-process)
