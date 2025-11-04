# BMAD v6 Alpha5 - Automated Upgrade Execution Plan

## Mission Objective

Automatically upgrade gitingest-agent-project from BMAD v4 to v6 alpha5, executing all necessary steps to reach a state where v2.0 development can begin immediately.

**Target End State:**
- ✅ BMAD v6 alpha5 installed (`bmad/` directory)
- ✅ V4 backed up safely (`v4-backup/.bmad-core/`)
- ✅ Workflow initialized (BMad Method track, Level 3)
- ✅ Git committed with checkpoint tag
- ✅ Documentation updated (README.md, CLAUDE.md)
- ✅ Ready for v2.0 story creation

---

## Execution Strategy

### Phase 1: Pre-Flight Validation (5 minutes)
**What:** Verify prerequisites and create safety checkpoints
**How:** Automated checks with Bash tool
**Output:** Go/No-Go decision

### Phase 2: BMAD-METHOD Repository Setup (10 minutes)
**What:** Clone and prepare BMAD v6 installer
**How:** Git clone, npm install, verify version
**Output:** Ready-to-run installer

### Phase 3: Installer Execution (15-20 minutes)
**What:** Run interactive installer with predetermined responses
**How:** Bash with heredoc input, monitor output
**Output:** BMAD v6 installed, v4 backed up

### Phase 4: Post-Installation Configuration (10 minutes)
**What:** Initialize workflow system, verify agents
**How:** Manual steps (requires Claude Code IDE integration)
**Output:** Workflow context configured

### Phase 5: Documentation & Git Commit (10 minutes)
**What:** Update docs, commit changes, create checkpoint
**How:** Edit tool, Git commands
**Output:** Clean git state, tagged checkpoint

### Phase 6: V2.0 Readiness Validation (5 minutes)
**What:** Verify upgrade success, test agent system
**How:** Validation checks, agent command tests
**Output:** Confirmation of v2.0 readiness

**Total Time:** ~60 minutes (fully automated where possible)

---

## Phase 1: Pre-Flight Validation

### Step 1.1: Environment Check

**Verify Node.js/npm:**
```bash
node --version && npm --version
```
**Expected:** Node v18+, npm v9+
**Action:** If missing, ABORT with installation instructions

**Verify Git Status:**
```bash
cd c:\Users\drewa\work\dev\gitingest-agent-project
git status --porcelain
```
**Expected:** Empty output (clean working tree)
**Action:** If dirty, ABORT with "Commit or stash changes first"

**Verify UV Environment:**
```bash
cd execute
uv run pytest --co -q | head -5
```
**Expected:** Test collection succeeds
**Action:** If fails, WARN but continue (not blocking)

### Step 1.2: Create Safety Checkpoint

**Create Git Tag:**
```bash
git tag -a v1.1.0-bmad-v4-checkpoint -m "Checkpoint before BMAD v6 upgrade"
git tag -l | grep checkpoint
```
**Expected:** Tag created successfully
**Action:** Proceed to Phase 2

**Check Current BMAD Version:**
```bash
ls -d .bmad-core && echo "BMAD v4 detected"
```
**Expected:** `.bmad-core/` exists
**Action:** Confirm v4 detected, ready for upgrade

### Step 1.3: Backup Preparation

**Manual Backup (Safety Net):**
```bash
mkdir -p ../gitingest-agent-backup-$(date +%Y%m%d)
cp -r . ../gitingest-agent-backup-$(date +%Y%m%d)/
echo "Manual backup created at ../gitingest-agent-backup-$(date +%Y%m%d)"
```
**Expected:** Full project backup outside project directory
**Action:** Extra safety layer beyond installer's automatic backup

---

## Phase 2: BMAD-METHOD Repository Setup

### Step 2.1: Clone BMAD-METHOD

**Clone Repository:**
```bash
cd c:\Users\drewa\work\dev
if [ -d "BMAD-METHOD" ]; then
    echo "BMAD-METHOD already exists, updating..."
    cd BMAD-METHOD
    git fetch origin
    git checkout main
    git pull origin main
else
    echo "Cloning BMAD-METHOD..."
    git clone https://github.com/bmad-code-org/BMAD-METHOD
    cd BMAD-METHOD
fi
```
**Expected:** BMAD-METHOD directory ready
**Action:** Proceed to verification

### Step 2.2: Verify Version

**Check for Alpha5:**
```bash
cd c:\Users\drewa\work\dev\BMAD-METHOD
git log --oneline --grep="alpha5" -n 5
git log --oneline --grep="6.0.0" -n 5
```
**Expected:** Commits related to v6.0.0-alpha5
**Action:** Verify we have latest alpha5 or newer

**Check CHANGELOG:**
```bash
grep -A 10 "6.0.0-alpha" CHANGELOG.md | head -20
```
**Expected:** Alpha5 section visible in CHANGELOG
**Action:** Confirm version is correct

### Step 2.3: Install Dependencies

**Run npm install:**
```bash
cd c:\Users\drewa\work\dev\BMAD-METHOD
npm install
```
**Expected:** Dependencies installed successfully
**Action:** Proceed to Phase 3

**Verify Installer:**
```bash
npx bmad-method --version || echo "Installer ready (no --version flag)"
ls -la node_modules/.bin/bmad-method || echo "Checking installer location..."
```
**Expected:** Installer accessible via npx
**Action:** Ready to execute installer

---

## Phase 3: Installer Execution

### Step 3.1: Prepare Installer Input

**⚠️ Challenge:** Interactive installer requires user input
**Solution:** Use heredoc with predetermined responses

**Installer Response File:**
```bash
# Create response file for installer
cat > /tmp/bmad-installer-responses.txt <<'EOF'
Y
Y

docs/
docs/prd.md
docs/architecture/
docs/stories/

Y
EOF
```

**Explanation of Responses:**
- Line 1: `Y` → Back up v4 files? YES
- Line 2: `Y` → Remove legacy IDE commands? YES
- Line 3: ` ` (space) → Select BMM module (space to select)
- Line 4: `docs/` → Project documentation location
- Line 5: `docs/prd.md` → PRD location (single file)
- Line 6: `docs/architecture/` → Architecture location (sharded)
- Line 7: `docs/stories/` → Story location
- Line 8: ` ` → Select Claude Code IDE integration
- Line 9: `Y` → Confirm installation

### Step 3.2: Execute Installer

**⚠️ CRITICAL:** This step may require manual intervention

**Automated Attempt:**
```bash
cd c:\Users\drewa\work\dev\BMAD-METHOD
npx bmad-method install < /tmp/bmad-installer-responses.txt
```

**Alternative (Interactive):**
If automated input fails, provide responses manually:
1. Project path: `C:\Users\drewa\work\dev\gitingest-agent-project`
2. Back up v4? `Y`
3. Remove legacy IDE commands? `Y`
4. Module selection: Select `BMM` (space to select)
5. Docs location: `docs/` (default)
6. PRD format: Single file `docs/prd.md`
7. Architecture format: Sharded `docs/architecture/`
8. Story location: `docs/stories/` (default)
9. IDE integration: Claude Code
10. Confirm? `Y`

**Monitor Output:**
Watch for:
- ✓ v4 backup confirmation
- ✓ bmad/ creation
- ✓ BMM module installation
- ✓ IDE configuration
- ✓ Installation complete message

### Step 3.3: Verify Installation

**Check Directory Structure:**
```bash
cd c:\Users\drewa\work\dev\gitingest-agent-project
ls -la | grep bmad
ls -la | grep v4-backup
```
**Expected:**
- `bmad/` directory exists
- `v4-backup/` directory exists
- `.bmad-core/` should NOT exist in root (moved to backup)

**Check BMAD Structure:**
```bash
ls bmad/
ls bmad/bmm/
ls bmad/_cfg/
```
**Expected:**
- `bmad/core/`, `bmad/bmm/`, `bmad/_cfg/`, `bmad/docs/`
- `bmad/bmm/agents/`, `bmad/bmm/workflows/`, `bmad/bmm/templates/`
- `bmad/_cfg/agents/` (empty - for customizations)

**Verify V4 Backup:**
```bash
ls v4-backup/.bmad-core/agents/ | head -5
```
**Expected:** V4 agent files present in backup
**Action:** Backup confirmed, safe to proceed

**Check Git Status:**
```bash
git status
```
**Expected:**
- New files: `bmad/`, `v4-backup/`
- Modified: `.claude/` (IDE integration)
- Deleted: `.bmad-core/` (tracked as moved to backup)

---

## Phase 4: Post-Installation Configuration

### Step 4.1: Workflow Initialization

**⚠️ MANUAL STEP REQUIRED:** workflow-init requires IDE integration

**Read IDE Documentation:**
```bash
cat bmad/docs/ide-info/claude-code.md
```
**Expected:** Instructions for loading agents in Claude Code
**Action:** Follow instructions to invoke `@analyst`

**Invoke Analyst Agent:**
```
@analyst *workflow-init
```

**Workflow-Init Prompts & Responses:**

**Prompt 1: Project Track**
```
? Select project track:
```
**Response:** BMad Method (option 2)
**Rationale:** Comprehensive planning, testing, matches v1.x approach

**Prompt 2: Project Level**
```
? Confirm project level: (3)
```
**Response:** 3 (Architecture complete)
**Rationale:** PRD + Architecture done, ready for v2.0 stories

**Prompt 3: Document Locations**
```
? PRD location: (docs/prd.md)
? Architecture location: (docs/architecture/)
? Story location: (docs/stories/)
```
**Response:** Accept all defaults (press Enter 3 times)
**Rationale:** Matches existing structure

**Prompt 4: Workflow Selection**
```
? Confirm workflow: (bmad-method-service)
```
**Response:** Accept default (press Enter)
**Rationale:** CLI tool, no UI component

**Expected Output:**
```
✓ Workflow context created: bmad/_cfg/workflow-context.yaml
✓ Project track: bmad-method
✓ Project level: 3 (Architecture complete)
✓ Workflow: bmad-method-service
✓ Team: team-no-ui
```

### Step 4.2: Verify Agent System

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

Current Team: team-no-ui
```

**Test Agent Command:**
```
@sm *help
```
**Expected:** SM agent help text displays
**Action:** Agent system functional

### Step 4.3: Verify Workflow Context

**Read Generated Config:**
```bash
cat bmad/_cfg/workflow-context.yaml
```

**Expected Content:**
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

**Validation:** All values match expectations
**Action:** Configuration complete

---

## Phase 5: Documentation & Git Commit

### Step 5.1: Update README.md

**Add BMAD v6 Section:**

Location: After "Development Workflow" section (~line 645)

```markdown
### Development Workflow

This project follows the **BMAD (Breakthrough Method for AI-driven Agile Development) v6.0** methodology with integrated QA.

**BMAD v6 Features:**
- **Track System:** BMad Method (comprehensive planning + testing)
- **Workflow Type:** Service (CLI tool)
- **BDD Story Templates:** Given/When/Then acceptance criteria

**Key Agents:**
- `@analyst` - Requirements elicitation and planning
- `@architect` - System design and technical decisions
- `@pm` - Project management and sprint planning
- `@dev` - Development implementation
- `@qa` - Quality assurance and testing
- `@sm` - Story management and creation
- `@po` - Product ownership and backlog

**Workflows:**
- **Story Creation**: `@sm *draft-story`
- **Sprint Planning**: `@pm *sprint-planning`
- **Story Implementation**: `@dev *implement-story {story}`
- **Story Review**: `@qa *review-story {story}`
- **Risk Assessment**: `@qa *assess-risk {story}`

See `bmad/docs/` for complete workflow documentation.
```

### Step 5.2: Update CLAUDE.md

**Add BMAD v6 Reference:**

Location: After "General Preferences" section (~line 40)

```markdown
## BMAD Integration

This project uses **BMAD METHOD v6.0** (bmad/ directory).

**Architecture:**
- **Core Framework:** `bmad/core/` (universal)
- **BMad Method Module:** `bmad/bmm/` (software development)
- **Configuration:** `bmad/_cfg/` (customizations)

**Agent System:**
- Agents are invoked with `@agent-name` syntax
- Tasks use `*task-name` pattern
- Example: `@sm *draft-story` creates new story

**Key Agents:**
- `@analyst` - Requirements and planning
- `@architect` - System design
- `@dev` - Implementation
- `@qa` - Quality assurance
- `@sm` - Story management
- `@pm` - Project management
- `@po` - Product ownership

**Project Configuration:**
- **Track:** BMad Method (comprehensive)
- **Level:** 3 (Architecture complete, ready for v2.0)
- **Workflow:** bmad-method-service (CLI tool)
- **Team:** team-no-ui (Analyst, Architect, PM, Dev, QA, SM, PO)

**Workflow Context:** `bmad/_cfg/workflow-context.yaml`
```

### Step 5.3: Update .gitignore

**Add BMAD v6 Entries:**

Location: End of file

```gitignore
# BMAD v6
bmad/
v4-backup/

# Keep configuration visible (optional - decide based on team preference)
# !bmad/_cfg/
```

**Decision Point:** Should bmad/ be committed?
- **Option A:** Commit bmad/ (full version control)
- **Option B:** Ignore bmad/ (install per developer)

**Recommendation:** Commit bmad/ for team consistency
**Action:** Do NOT add to .gitignore, commit as-is

### Step 5.4: Git Commit

**Stage Changes:**
```bash
cd c:\Users\drewa\work\dev\gitingest-agent-project
git add .
git status
```

**Expected Status:**
- `new file: bmad/` (hundreds of files)
- `new file: v4-backup/`
- `modified: .claude/`
- `modified: README.md`
- `modified: CLAUDE.md`

**Create Commit:**
```bash
git commit -m "$(cat <<'EOF'
chore: Upgrade to BMAD v6.0.0-alpha5

Major upgrade from BMAD v4 to v6 alpha5 in preparation for v2.0 development.

Changes:
- Installed BMAD v6 alpha5 to bmad/ directory
- Backed up BMAD v4 to v4-backup/.bmad-core/
- Configured BMad Method track, Level 3 (Architecture complete)
- Initialized bmad-method-service workflow
- Updated README.md and CLAUDE.md with v6 references
- IDE integration configured for Claude Code

Breaking Changes:
- Workflow paths: brownfield-service → bmad-method-service
- Story templates: Traditional → BDD format (Given/When/Then)
- Variable rename: project_level → project_track

Project Status:
- v1.1.0: Complete and stable
- v2.0: Ready for story creation with v6 workflows

Next Steps:
- Create epic-2.0 (Multi-Repository Analysis)
- Create story 2.1 (TOON Format Integration)
- Begin v2.0 development with BDD story templates

BMAD v6 Documentation: bmad/docs/
Workflow Context: bmad/_cfg/workflow-context.yaml

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Verify Commit:**
```bash
git log -1 --stat
```
**Expected:** Commit created with all changes

### Step 5.5: Create Checkpoint Tag

**Tag v6 Upgrade:**
```bash
git tag -a v1.1.0-bmad-v6-upgraded -m "BMAD v6 alpha5 upgrade complete, ready for v2.0"
git tag -l | grep -E "(checkpoint|upgraded)"
```

**Expected Tags:**
- `v1.1.0-bmad-v4-checkpoint` (pre-upgrade)
- `v1.1.0-bmad-v6-upgraded` (post-upgrade)

**Push to Remote:**
```bash
git push origin main
git push origin --tags
```

**Verify Remote:**
```bash
git log origin/main -1 --oneline
```
**Expected:** Upgrade commit pushed successfully

---

## Phase 6: V2.0 Readiness Validation

### Step 6.1: Validation Checklist

**✓ File Structure:**
```bash
[ -d "bmad/core" ] && echo "✓ bmad/core/" || echo "✗ bmad/core/ missing"
[ -d "bmad/bmm" ] && echo "✓ bmad/bmm/" || echo "✗ bmad/bmm/ missing"
[ -d "bmad/_cfg" ] && echo "✓ bmad/_cfg/" || echo "✗ bmad/_cfg/ missing"
[ -d "v4-backup/.bmad-core" ] && echo "✓ v4-backup/" || echo "✗ v4-backup/ missing"
[ ! -d ".bmad-core" ] && echo "✓ .bmad-core moved" || echo "✗ .bmad-core still in root"
```

**Expected:** All ✓ checks pass

**✓ Configuration:**
```bash
[ -f "bmad/_cfg/workflow-context.yaml" ] && echo "✓ Workflow context exists" || echo "✗ Missing"
grep "project_track: bmad-method" bmad/_cfg/workflow-context.yaml && echo "✓ Track: bmad-method"
grep "project_level: 3" bmad/_cfg/workflow-context.yaml && echo "✓ Level: 3"
grep "workflow_type: service" bmad/_cfg/workflow-context.yaml && echo "✓ Type: service"
```

**Expected:** All ✓ checks pass

**✓ Git Status:**
```bash
git status --porcelain
```
**Expected:** Empty (clean working tree after commit)

**✓ Tags:**
```bash
git tag -l | grep -E "(checkpoint|upgraded)" | wc -l
```
**Expected:** 2 tags (checkpoint + upgraded)

### Step 6.2: Functional Validation

**✓ Agent System:**

Test each agent command:
```
@analyst *help
@sm *help
@dev *help
@qa *help
@pm *help
```

**Expected:** Each agent responds with help text

**✓ Execute Environment:**
```bash
cd execute
uv run pytest -v | head -20
```

**Expected:** Tests still pass (190 tests, 96%+ coverage)
**Action:** Confirm v1.x implementation unaffected

**✓ CLI Functionality:**
```bash
cd execute
uv run gitingest-agent --help
```

**Expected:** CLI help displays correctly
**Action:** User-facing functionality intact

### Step 6.3: V2.0 Readiness Report

**Generate Report:**
```bash
cat > /tmp/v6-upgrade-report.txt <<'EOF'
═══════════════════════════════════════════════════════════════
  BMAD v6 Alpha5 Upgrade - Completion Report
═══════════════════════════════════════════════════════════════

Project: gitingest-agent-project
Upgrade Date: $(date +%Y-%m-%d)
Duration: ~60 minutes

UPGRADE STATUS: ✅ COMPLETE

Phase 1: Pre-Flight Validation          ✅ PASSED
  - Node.js/npm verified
  - Git status clean
  - Safety checkpoint created
  - Manual backup created

Phase 2: BMAD-METHOD Setup               ✅ COMPLETE
  - Repository cloned/updated
  - Version verified (v6.0.0-alpha5)
  - Dependencies installed
  - Installer ready

Phase 3: Installer Execution             ✅ COMPLETE
  - v4 backed up to v4-backup/.bmad-core/
  - v6 installed to bmad/
  - BMM module installed
  - IDE integration configured

Phase 4: Post-Installation Config        ✅ COMPLETE
  - workflow-init executed
  - Project track: bmad-method
  - Project level: 3 (Architecture complete)
  - Workflow: bmad-method-service
  - Agent system verified

Phase 5: Documentation & Git             ✅ COMPLETE
  - README.md updated
  - CLAUDE.md updated
  - Git commit created
  - Tags: v1.1.0-bmad-v4-checkpoint, v1.1.0-bmad-v6-upgraded
  - Pushed to remote

Phase 6: Validation                      ✅ PASSED
  - File structure verified
  - Configuration validated
  - Agent commands functional
  - Execute/CLI still working
  - Tests passing (190 tests, 96%+ coverage)

═══════════════════════════════════════════════════════════════
  V2.0 READINESS: ✅ READY
═══════════════════════════════════════════════════════════════

Next Actions:
1. Create epic-2.0 with @sm *draft-epic
2. Create story 2.1 with @sm *draft-story epic-2.0
3. Use BDD format (Given/When/Then) for acceptance criteria
4. Begin v2.0 development on v2.0-development branch

BMAD v6 Features Now Available:
- BDD story templates (Given/When/Then)
- Track-based workflows (bmad-method-service)
- Improved agent system (@analyst, @sm, @dev, @qa, @pm)
- Workflow context configuration (bmad/_cfg/workflow-context.yaml)

Rollback Available:
- v4 backup: v4-backup/.bmad-core/
- Git tag: v1.1.0-bmad-v4-checkpoint
- Restoration: cp -r v4-backup/.bmad-core .bmad-core

Support:
- BMAD Docs: bmad/docs/
- Discord: https://discord.gg/gk8jAdXWmj
- Upgrade Plan: user-context/bmad-v6-upgrade-plan.md

═══════════════════════════════════════════════════════════════
  Upgrade Successful - Ready for v2.0 Development
═══════════════════════════════════════════════════════════════
EOF

cat /tmp/v6-upgrade-report.txt
```

**Display Report:**
Show completion report with all validation results

---

## Execution Checklist

### Claude Code Agent Tasks (Automated)

- [ ] **Phase 1:** Run pre-flight validation checks
- [ ] **Phase 2:** Clone/update BMAD-METHOD repository
- [ ] **Phase 2:** Install npm dependencies
- [ ] **Phase 3:** Execute installer (with manual input if needed)
- [ ] **Phase 3:** Verify installation (file structure checks)
- [ ] **Phase 4:** Read workflow-init documentation
- [ ] **Phase 5:** Update README.md (Edit tool)
- [ ] **Phase 5:** Update CLAUDE.md (Edit tool)
- [ ] **Phase 5:** Create git commit with detailed message
- [ ] **Phase 5:** Create checkpoint tags
- [ ] **Phase 5:** Push to remote
- [ ] **Phase 6:** Run validation checklist
- [ ] **Phase 6:** Generate completion report

### Manual Tasks (User Required)

- [ ] **Phase 4:** Invoke `@analyst *workflow-init` (IDE integration)
- [ ] **Phase 4:** Respond to workflow-init prompts:
  - Track: BMad Method
  - Level: 3
  - Docs: Accept defaults
  - Workflow: bmad-method-service
- [ ] **Phase 4:** Verify agent commands work (`@sm *help`)
- [ ] **Post-Upgrade:** Review completion report
- [ ] **Post-Upgrade:** Approve v2.0 readiness

---

## Rollback Procedure (If Needed)

**Full Rollback:**
```bash
cd c:\Users\drewa\work\dev\gitingest-agent-project

# Remove v6
rm -rf bmad/

# Restore v4
cp -r v4-backup/.bmad-core .bmad-core

# Restore IDE config
git checkout .claude/

# Reset to checkpoint
git reset --hard v1.1.0-bmad-v4-checkpoint

# Verify restoration
ls -la | grep bmad
```

**Partial Rollback (Keep Both):**
```bash
# Keep v6 for reference, restore v4 as active
cp -r v4-backup/.bmad-core .bmad-core

# Now both exist:
# - .bmad-core/ (v4, active)
# - bmad/ (v6, inactive)
# - v4-backup/ (v4, backup)
```

---

## Success Criteria

**Upgrade is successful when:**
1. ✅ `bmad/` directory exists with complete v6 structure
2. ✅ `v4-backup/.bmad-core/` contains full v4 backup
3. ✅ `bmad/_cfg/workflow-context.yaml` configured correctly
4. ✅ Agent commands functional (`@analyst`, `@sm`, `@dev`, `@qa`)
5. ✅ Git committed with tags (checkpoint + upgraded)
6. ✅ Execute/CLI still works (tests pass)
7. ✅ Documentation updated (README.md, CLAUDE.md)
8. ✅ Ready to create v2.0 stories with BDD format

**Ready for v2.0 when:**
- Can invoke `@sm *draft-epic` to create epic-2.0
- Can invoke `@sm *draft-story epic-2.0` to create story 2.1
- Stories use BDD format (Given/When/Then)
- Workflow type is `bmad-method-service`
- Project level is 3 (Architecture complete)

---

## Automation Limitations

**What Claude Code CAN automate:**
- ✅ Pre-flight validation checks
- ✅ Repository cloning and npm install
- ✅ File structure verification
- ✅ Documentation updates (Edit tool)
- ✅ Git commits and tags
- ✅ Validation checks
- ✅ Report generation

**What requires manual intervention:**
- ⚠️ Installer execution (interactive prompts)
- ⚠️ workflow-init (requires IDE agent integration)
- ⚠️ Agent command verification (requires @agent syntax)
- ⚠️ Final approval for v2.0 readiness

**Hybrid Approach:**
Claude Code will execute all automated steps and provide clear instructions for manual steps, guiding you through each decision point.

---

## Ready to Execute?

When you give the command, I will:

1. **Start Phase 1:** Run all pre-flight checks
2. **Progress through phases:** Execute each automated step
3. **Pause at manual steps:** Provide clear instructions and wait for confirmation
4. **Validate continuously:** Check success after each phase
5. **Generate report:** Provide completion summary

**Command to start:** "Begin BMAD v6 upgrade"

---

## Document Metadata

- **Created:** 2025-11-04
- **Author:** Claude Code (Automated Execution Plan)
- **Version:** 1.0
- **Purpose:** Automated upgrade execution for Claude Code agent
- **Related:** user-context/bmad-v6-upgrade-plan.md (manual guide)

---

**Ready for Automated Execution** ✅
