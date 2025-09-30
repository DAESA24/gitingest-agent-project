# Agent Configuration Files - Location Rationale

**Created:** 2025-09-30
**Context:** Execute directory refactoring (Phase 3.6)

## Files Staying in Project Root

The following files remain in the project root directory (not moved to execute/):

- `CLAUDE.md` - GitIngest Agent operating instructions
- `CLAUDE_ANALYSIS_GUIDE.md` - Agent analysis generation specifications

## Rationale for Root Location

### 1. **Runtime Configuration for Claude Code Agent**
These files configure how the Claude Code AI agent operates, not application implementation logic. They are runtime instructions for the AI assistant.

### 2. **Conceptual Layer Separation**
The project has three distinct layers:

**Agent Layer** (How Claude Code operates):
- `CLAUDE.md`
- `CLAUDE_ANALYSIS_GUIDE.md`
- `.claude/` directory

**Framework Layer** (How BMAD operates):
- `.bmad-core/`
- `docs/`
- `explore/`
- `plan/`
- `user-context/`

**Implementation Layer** (How Python app operates):
- `execute/` directory (all Python code, tests, dependencies)

### 3. **Similar to BMAD Framework Files**
Just as `.bmad-core/` provides framework-level configuration for the BMAD methodology, `CLAUDE.md` provides agent-level configuration for Claude Code operation. Neither are application implementation.

### 4. **Convention and Tool Expectations**
Claude Code looks for `CLAUDE.md` at the project root by convention. Moving it would break the agent persona functionality.

### 5. **Analogous to Agent Instructions in BMAD**
In BMAD framework, agent instruction files (like `.bmad-core/bmad-orchestrator.md`) stay at framework level, not implementation level. Our agent config files follow the same pattern.

## What This Means for Refactoring

**Files NOT Moved:**
- CLAUDE.md (stays in root)
- CLAUDE_ANALYSIS_GUIDE.md (stays in root)
- .claude/ (stays in root)

**Files Moved to execute/:**
- All Python source code (*.py)
- All tests (tests/)
- All Python dependencies (pyproject.toml, uv.lock)
- Python environment (.venv/)

## Conceptual Diagram

```
gitingest-agent-project/
│
├── Agent Layer (AI Configuration)
│   ├── CLAUDE.md ← Stays in root
│   ├── CLAUDE_ANALYSIS_GUIDE.md ← Stays in root
│   └── .claude/ ← Stays in root
│
├── Framework Layer (BMAD Configuration)
│   ├── .bmad-core/ ← Stays in root
│   ├── docs/ ← Stays in root
│   ├── explore/ ← Stays in root
│   ├── plan/ ← Stays in root
│   └── user-context/ ← Stays in root
│
└── Implementation Layer (Python Application)
    └── execute/ ← All implementation moved here
        ├── *.py (source code)
        ├── tests/ (test suite)
        ├── pyproject.toml (dependencies)
        ├── uv.lock (lock file)
        └── .venv/ (virtual environment)
```

## Summary

Agent configuration files remain in root because they configure the AI assistant's behavior, not the Python application's implementation. This separation maintains clear boundaries between agent configuration, framework configuration, and application implementation.

This decision aligns with BMAD methodology's layered approach and Claude Code's expected project structure conventions.
