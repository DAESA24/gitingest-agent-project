# GitIngest Agent - Version 2.0 Roadmap

- **Version:** 2.0 Roadmap
- **Status:** 📋 Proposed (Planning Phase)
- **Target Release:** TBD (Post Phase 1.5)
- **Document Owner:** Product Manager

---

## Overview

Version 2.0 represents the next evolution of GitIngest Agent, focusing on:
- **Context efficiency** - Reducing agent instruction overhead
- **Performance optimization** - TOON format integration for token reduction
- **Extensibility** - Plugin architecture for custom workflows
- **Maturity** - Production-ready features and automation

**Note:** These are proposed features for future development. Priorities and scope subject to change based on v1.5 learnings and user feedback.

---

## 2.1 Context-Efficient Agent Architecture

### 2.1.1 Overview

**Status:** 📋 Proposed

**Problem Statement:**

Current CLAUDE.md file contains ~3.2k tokens of workflow instructions loaded in every Claude Code session, regardless of whether repository analysis is occurring. As agent capabilities expand, instruction bloat will impact context efficiency and limit tokens available for actual analysis work.

**Proposed Solution:**

Migrate workflow orchestration from documentation to executable code using progressive disclosure:
- CLI `analyze` command encapsulates full workflow (9 steps → 1 command)
- CLAUDE.md reduced to minimal orchestrator instructions (~300 tokens)
- Optional slash commands for detailed help (on-demand loading)
- Foundation for future plugin/skill system

**Value Proposition:**

- **90% context reduction** (3.2k → 300 tokens in CLAUDE.md when idle)
- **Testable workflows** (code vs. documentation ensures consistency)
- **Extensibility** (plugin architecture for custom workflows)
- **Maintainability** (workflow logic in Python, not Markdown)
- **User empowerment** (direct CLI usage without Claude Code)

**Strategic Alignment:**

This architectural improvement enables:
- More complex analysis types (more tokens available for actual work)
- Third-party integrations (plugins can extend functionality)
- CI/CD automation (analyze command usable in scripts)
- Future AI agent frameworks (modular, composable workflows)

---

### 2.1.2 User Stories

#### **User Story 2.1.1: Context-Efficient Sessions**

As a Claude Code user,
I want GitIngest Agent to use minimal context when idle,
So that I have more tokens available for repository analysis and other tasks.

**Acceptance Criteria:**
- [ ] CLAUDE.md reduced to <500 tokens
- [ ] Workflow logic moved to CLI `analyze` command
- [ ] Sessions without active analysis consume <500 tokens for agent instructions
- [ ] Active analysis sessions load detailed docs only when needed via `/analyze-help`
- [ ] Context usage tracked and reported in session summary

---

#### **User Story 2.1.2: Executable Workflow Command**

As a developer using GitIngest Agent,
I want to execute the complete workflow with a single command,
So that I can automate repository analysis without manual orchestration.

**Acceptance Criteria:**
- [ ] `gitingest-agent analyze <url>` command orchestrates full workflow automatically
- [ ] Handles size check → routing → extraction → analysis → save without intervention
- [ ] Provides interactive prompts for analysis type and save confirmation
- [ ] Works from any directory (leverages Phase 1.5 multi-location output)
- [ ] Supports `--non-interactive` mode for CI/CD usage
- [ ] Returns appropriate exit codes for scripting

**Example Usage:**
```bash
# Interactive mode (prompts for analysis type)
gitingest-agent analyze https://github.com/fastapi/fastapi

# Non-interactive mode (CI/CD)
gitingest-agent analyze https://github.com/fastapi/fastapi \
  --type architecture \
  --output-dir ./docs/research \
  --non-interactive
```

---

#### **User Story 2.1.3: Plugin Architecture Foundation**

As a future contributor or power user,
I want the ability to extend GitIngest Agent with custom workflows,
So that I can add specialized analysis types without modifying core code.

**Acceptance Criteria:**
- [ ] Plugin interface for custom analysis generators
- [ ] Plugin discovery mechanism (e.g., `.gitingest-plugins/` directory or pip-installable packages)
- [ ] Example plugin demonstrating extensibility (e.g., security-focused analysis)
- [ ] Documentation for plugin development
- [ ] Plugin versioning and compatibility checking
- [ ] Error handling for missing or incompatible plugins

**Example Plugin Structure:**
```python
# .gitingest-plugins/security_analysis.py
from gitingest_agent.plugins import AnalysisPlugin

class SecurityAnalysisPlugin(AnalysisPlugin):
    name = "security"
    description = "Security-focused repository analysis"

    def analyze(self, extraction_path, repo_name):
        # Custom analysis logic
        return analysis_content
```

---

### 2.1.3 Technical Architecture

#### **Before (Phase 1.x):**

```
User provides GitHub URL
  ↓
Claude Code reads CLAUDE.md (3.2k tokens)
  ↓
Claude executes 9 workflow steps manually:
  - check-size
  - extract-full/extract-tree
  - extract-specific (if needed)
  - prompt for analysis type
  - generate analysis
  - prompt to save
  - save analysis
  - display summary
  ↓
Each step requires Claude to call CLI commands separately
```

**Context Overhead:** 3.2k tokens every session + workflow coordination overhead

---

#### **After (Phase 2.0):**

```
User provides GitHub URL
  ↓
Claude Code reads CLAUDE.md (300 tokens)
  ↓
Claude executes: gitingest-agent analyze <url>
  ↓
CLI orchestrates all 9 steps internally:
  - Size check and routing
  - Extraction (full or selective)
  - Interactive analysis type prompt
  - Analysis generation
  - Save confirmation
  - Summary display
  ↓
Claude monitors output and assists only if errors occur
```

**Context Overhead:** 300 tokens for CLAUDE.md + zero coordination overhead

---

#### **Progressive Disclosure Model:**

**Tier 1 - Always Loaded (~300 tokens):**
- `CLAUDE.md` - Minimal orchestrator instructions
- Role: Detect GitHub URLs, execute `analyze` command

**Tier 2 - On-Demand (~2.0k tokens):**
- `/analyze-help` slash command - Detailed workflow documentation
- Loaded only when user explicitly requests help

**Tier 3 - Future Plugins (variable):**
- Plugin-specific documentation loaded only when plugin invoked
- Keeps context minimal for common workflows

---

#### **Implementation Components:**

**1. CLI Orchestration Command:**
```python
# execute/cli.py

@gitingest_agent.command()
@click.argument('url')
@click.option('--type', type=click.Choice(['installation', 'workflow', 'architecture', 'custom']))
@click.option('--output-dir', type=click.Path())
@click.option('--non-interactive', is_flag=True)
def analyze(url, type, output_dir, non_interactive):
    """
    Execute complete GitIngest workflow: check → extract → analyze → save.

    Orchestrates the full repository analysis workflow:
    1. Check repository token count
    2. Route to full or selective extraction
    3. Prompt for analysis type (or use --type)
    4. Generate analysis
    5. Save to appropriate location

    Example:
        gitingest-agent analyze https://github.com/user/repo
        gitingest-agent analyze https://github.com/user/repo --type architecture
    """
    # Full workflow orchestration
    pass
```

**2. Reduced CLAUDE.md:**
```markdown
# GitIngest Agent

## Role
Execute `gitingest-agent analyze <url>` when user provides GitHub URL.

## Workflow
1. Detect GitHub URL in user message
2. Execute: `gitingest-agent analyze <url>`
3. Monitor output and assist with prompts
4. Display completion summary

For detailed workflow documentation: `/analyze-help`
```

**3. On-Demand Help Slash Command:**
```markdown
# .claude/commands/analyze-help.md

Detailed GitIngest Agent workflow documentation.

[Full 9-step workflow, error handling, quality standards]
[Only loaded when user requests help]
```

---

### 2.1.4 Benefits Analysis

#### **Context Efficiency:**

| Scenario | Current (v1.5) | Proposed (v2.0) | Savings |
|----------|---------------|-----------------|---------|
| Idle session (no analysis) | 3.2k tokens | 300 tokens | **2.9k (90%)** |
| Active analysis | 3.2k tokens | 300 tokens | **2.9k (90%)** |
| User requests help | 3.2k tokens | 2.3k tokens | **0.9k (28%)** |

**Impact:** With 200k token budget, saving 2.9k tokens = **1.45% more capacity for analysis content**.

---

#### **Workflow Consistency:**

- ✅ **Testable:** Workflow logic can be unit tested
- ✅ **Consistent:** Same execution path every time
- ✅ **Maintainable:** Changes in one place (Python code) vs. Markdown docs
- ✅ **Debuggable:** Standard Python debugging tools apply

---

#### **User Empowerment:**

- ✅ **Direct CLI usage:** Users can run `analyze` command without Claude Code
- ✅ **Scriptable:** CI/CD integration with `--non-interactive` mode
- ✅ **Transparent:** Clear command output shows what's happening

---

### 2.1.5 Migration Path

**Phase 1: Implement Analyze Command (v2.0-alpha.1)**
- Create `gitingest-agent analyze` command with full orchestration
- Test interactively and in non-interactive mode
- Verify Phase 1.5 multi-location output integration

**Phase 2: Create On-Demand Help (v2.0-alpha.2)**
- Create `/analyze-help` slash command
- Migrate detailed workflow docs from CLAUDE.md
- Test context savings

**Phase 3: Reduce CLAUDE.md (v2.0-alpha.3)**
- Update CLAUDE.md to minimal orchestrator instructions
- Test Claude Code sessions (idle and active)
- Measure context usage improvements

**Phase 4: Plugin Foundation (v2.0-beta.1)**
- Design plugin interface
- Implement plugin discovery
- Create example plugin
- Document plugin development

**Phase 5: Release v2.0**
- Full testing across use cases
- Documentation updates
- CHANGELOG.md update
- Release with context efficiency improvements

---

### 2.1.6 Success Metrics

**Context Efficiency:**
- [ ] CLAUDE.md <500 tokens
- [ ] 90% context reduction in idle sessions
- [ ] Measurable improvement in analysis depth (more tokens available)

**Workflow Quality:**
- [ ] 100% feature parity with v1.5 manual workflow
- [ ] Test coverage >90% for analyze command
- [ ] Zero regressions in user workflows

**User Adoption:**
- [ ] Direct CLI usage metrics (if telemetry added)
- [ ] Positive user feedback on workflow simplification
- [ ] Reduced "how do I use this?" questions

**Extensibility:**
- [ ] At least 1 example plugin functional
- [ ] Plugin API documentation complete
- [ ] Community contributor interest (GitHub discussions/issues)

---

## 2.2 TOON Format Integration

### 2.2.1 Overview

**Status:** 📋 Proposed

Integrate TOON (Token-Oriented Object Notation) format as an output option for repository metadata and analysis results, providing 30-60% token reduction for uniform structured data.

**Problem Statement:**

Repository metadata (file listings, commit history, dependency trees) is currently output in verbose formats (JSON, Markdown). When passing this data to LLMs for analysis, token consumption is high.

**Proposed Solution:**

- Add `--format toon` option to extraction commands
- Generate TOON-formatted output for repository metadata
- Benchmark token savings vs. JSON/Markdown
- Provide conversion utilities (TOON ↔ JSON)

**Value Proposition:**

- **30-60% token reduction** for repository metadata
- **Faster LLM processing** (fewer tokens to parse)
- **Cost savings** for API-based LLM usage
- **Showcase for BMAD community** (real-world TOON usage)

### 2.2.2 User Stories

#### **User Story 2.2.1: TOON Output Option**

As a developer analyzing large repositories,
I want the option to output metadata in TOON format,
So that I can reduce token consumption when passing data to LLMs.

**Acceptance Criteria:**
- [ ] `--format toon` option on extract commands
- [ ] TOON output maintains all information from JSON format
- [ ] Documented token savings vs. JSON baseline
- [ ] Conversion utility: `gitingest-agent convert json-to-toon <file>`

---

### 2.2.3 Technical Approach

**Dependencies:**
- TOON Python library: `pip install toon-format`
- TOON specification: https://github.com/toon-format/toon

**Implementation:**
```python
# execute/formatters.py

def format_toon(metadata: dict) -> str:
    """Convert repository metadata to TOON format."""
    import toon
    return toon.encode(metadata)

# execute/cli.py
@click.option('--format', type=click.Choice(['json', 'markdown', 'toon']),
              default='markdown')
def extract_full(url, format):
    """Extract repository with specified output format."""
    pass
```

**Benchmarking:**
- Measure token counts: JSON vs. TOON
- Test repositories: small (<10k), medium (10-50k), large (50k+ tokens)
- Document token reduction percentages

---

### 2.2.4 Success Metrics

**Performance:**
- [ ] Achieve 30%+ token reduction for typical repositories
- [ ] TOON encoding/decoding <100ms overhead
- [ ] No information loss vs. JSON format

**Adoption:**
- [ ] Example workflow demonstrating TOON benefits
- [ ] BMAD community showcase (blog post or discussion)
- [ ] User feedback on token savings

---

## 2.3 Claude Code Skills Integration

### 2.3.1 Overview

**Status:** 📋 Proposed (Alternative to 2.1)

**Problem Statement:**

Same context efficiency problem as 2.1, but solved through Claude Code's native Skills system rather than CLI orchestration.

**Proposed Solution:**

Create a Claude Code Skill that encapsulates GitIngest Agent workflow, loaded on-demand only when GitHub URLs are detected.

**Reference Implementation:**
- Leverage Anthropic's skill-creator skill: `C:\Users\drewa\.claude\skills\skill-creator`
- Follow Anthropic best practices for skill development
- Create `.claude/skills/gitingest-agent.md` in project

**Value Proposition:**
- Native Claude Code integration
- On-demand loading (0 tokens when idle)
- Pattern-based activation (GitHub URL detection)
- Portable across projects (skill can be installed globally)

**Trade-offs vs. Section 2.1:**

| Aspect | 2.1 CLI Orchestration | 2.3 Skills Integration |
|--------|----------------------|------------------------|
| Context efficiency | 300 tokens always loaded | 0 tokens when idle |
| Direct CLI usage | ✅ Yes | ❌ No (requires Claude Code) |
| Scriptability | ✅ Yes | ❌ No |
| Integration complexity | Higher (new CLI command) | Lower (just a skill file) |
| Portability | ✅ Works anywhere | Requires Claude Code |

---

### 2.3.2 User Stories

#### **User Story 2.3.1: On-Demand Skill Loading**

As a Claude Code user,
I want GitIngest Agent workflow loaded only when I provide a GitHub URL,
So that I have zero context overhead when not analyzing repositories.

**Acceptance Criteria:**
- [ ] Skill file created: `.claude/skills/gitingest-agent.md`
- [ ] Skill contains complete 9-step workflow instructions
- [ ] Skill activates on GitHub URL pattern detection
- [ ] Zero tokens consumed when skill not active
- [ ] Skill can be installed globally or per-project

---

#### **User Story 2.3.2: Leverage Anthropic Best Practices**

As a developer creating the GitIngest Agent skill,
I want to use Anthropic's skill-creator skill as a guide,
So that I follow established patterns and best practices.

**Acceptance Criteria:**
- [ ] Review `C:\Users\drewa\.claude\skills\skill-creator` for patterns
- [ ] Skill structure matches Anthropic conventions
- [ ] Proper YAML frontmatter with metadata
- [ ] Clear trigger patterns defined
- [ ] Documentation for users on skill installation

---

### 2.3.3 Implementation Plan

**Phase 1: Research (2 hours)**
- Study skill-creator skill structure
- Identify trigger patterns for GitHub URLs
- Define skill metadata and interface

**Phase 2: Skill Creation (4 hours)**
- Create `.claude/skills/gitingest-agent.md`
- Migrate workflow from CLAUDE.md to skill
- Test activation on GitHub URL patterns
- Verify zero context overhead when idle

**Phase 3: Documentation (2 hours)**
- Document skill installation (global vs. project-specific)
- Create usage examples
- Update README with skill option

**Phase 4: Testing (2 hours)**
- Test across multiple directories
- Verify multi-location output (Phase 1.5) works with skill
- Test pattern matching edge cases

**Total Effort:** ~10 hours

---

### 2.3.4 Decision Point

**Should we pursue Section 2.1 (CLI) or Section 2.3 (Skills)?**

This decision should be made based on:
- Primary use case (Claude Code vs. direct CLI)
- Context efficiency goals (300 tokens vs. 0 tokens)
- Scriptability requirements (CI/CD needs?)
- Development effort (new CLI command vs. skill file)

**Recommendation:** Create skill FIRST (lower effort), then evaluate if CLI orchestration still needed.

---

### 2.3.5 Success Metrics

**Context Efficiency:**
- [ ] 0 tokens consumed when skill not active
- [ ] Skill loads <3k tokens when activated
- [ ] 100% context reduction vs. always-loaded CLAUDE.md

**Usability:**
- [ ] Skill activates reliably on GitHub URLs
- [ ] No false positives (non-GitHub URLs)
- [ ] Clear user feedback when skill activates

**Adoption:**
- [ ] Skill installable globally for all projects
- [ ] Documentation clear for users
- [ ] Community interest (if open-sourced)

---

## 2.4 Future Enhancement Ideas

### 2.4.1 Multi-Repository Analysis

Analyze multiple related repositories in a single workflow (e.g., microservices architecture).

### 2.4.2 Incremental Updates

Re-analyze only changed files since last extraction (git diff-based).

### 2.4.3 Custom Analysis Templates

User-defined analysis templates with placeholders and custom prompts.

### 2.4.4 Analysis Comparison

Compare analyses across repository versions or different repositories.

### 2.4.5 CI/CD Integration

GitHub Actions workflow for automated repository analysis on PR/release.

---

## Version History

- **2025-11-06:** Added Section 2.3 - Claude Code Skills Integration
  - Alternative approach to context efficiency using Claude Code Skills
  - References Anthropic's skill-creator skill for best practices
  - User stories and implementation plan (~10 hours)
  - Decision framework for choosing CLI vs. Skills approach

- **2025-11-04:** Initial v2.0 roadmap created
  - Context-efficient agent architecture
  - TOON integration proposal
  - Future enhancement tracking

---

## Related Documents

- [Master PRD](prd.md) - Product requirements overview
- [Phase 1.5 User Stories](prd.md#115-phase-15-multi-location-output) - Current active development
- [Architecture Documentation](architecture.md) - System design
- [TOON Specification](https://github.com/toon-format/toon) - Token format details
- [Anthropic Skill Creator](C:\Users\drewa\.claude\skills\skill-creator) - Reference for skill development

---

**Document Status:** ✅ Complete
**Last Updated:** 2025-11-06
**Next Review:** After Phase 1.5 completion
