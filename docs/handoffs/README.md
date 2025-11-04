# Handoff Documents

This directory contains **agent-to-agent handoff documents** for context preservation across Claude Code sessions.

## Purpose

When Claude Code sessions end (due to context limits, user closing session, etc.), handoff documents ensure the next agent can pick up exactly where the previous one left off without:
- Re-reading the entire PRD
- Re-analyzing all architecture docs
- Losing context about what was decided
- Duplicating work already completed

## Document Format

Each handoff document should include:

1. **Executive Summary** - What was completed, what's next
2. **Deliverables** - Links to files created/modified
3. **Next Steps** - Clear instructions for next agent
4. **Key Technical Details** - Critical decisions, code patterns, constraints
5. **Context Needed** - Minimal files to load (not everything)
6. **Quick Start Command** - Exact command to resume work

## Naming Convention

```
{phase}-{status}.md
```

Examples:
- `phase-1.5-ready-for-implementation.md`
- `phase-2.0-architecture-review-needed.md`
- `epic-3-stories-created.md`

## Usage

**When to create:**
- Agent completes major work unit (stories, architecture, etc.)
- Session nearing context limit
- Natural workflow pause point (SM → Architect → Dev → QA)

**How to use in next session:**

```bash
# Start new session
/BMad:agents:bmad-orchestrator

# Then say:
"Read handoff document: docs/handoffs/{filename}.md and continue from there"
```

## Benefits

- ✅ **Context preservation** - No information loss between sessions
- ✅ **Faster startup** - Agent knows exactly what to do
- ✅ **Minimal context usage** - Load only what's needed
- ✅ **Clear accountability** - Documents who did what
- ✅ **BMad workflow continuity** - Maintains agent collaboration flow

## Current Handoffs

- **[phase-1.5-ready-for-implementation.md](phase-1.5-ready-for-implementation.md)** - Phase 1.5 fully planned, ready for developer

---

**This pattern should become standard BMad practice for complex multi-session work.**
