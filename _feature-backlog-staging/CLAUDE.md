# Feature Backlog Staging - Claude Instructions

This directory contains feature ideas awaiting consideration for implementation.

## Directory Purpose

**Staging area** for feature backlog items. These are ideas and proposals, not committed work. Items here may be implemented, deferred, or rejected.

## Frontmatter Requirements

**All files in this directory MUST have YAML frontmatter.** See [_frontmatter-template.md](_frontmatter-template.md) for the full schema.

### Required Fields (Every File)

```yaml
---
doc_type: feature-backlog-item
title: "Descriptive Feature Title"
created: YYYY-MM-DD
status: captured  # captured | approved | implemented | deferred | rejected
feature_type_tags:
  - relevant-tag
  - another-tag
---
```

## Status Workflow

```
captured → approved → implemented
              ↓
         deferred/rejected
```

| Status | Meaning | Action |
|--------|---------|--------|
| `captured` | Idea documented, not yet considered | Default for new items |
| `approved` | Green-lit, awaiting execution plan | Add `approved_date` |
| `implemented` | Feature shipped | Add `implemented_date`, rename with `x-` prefix |
| `deferred` | Not now, revisit later | Add `deferred_date`, `deferred_reason`, rename with `x-` prefix |
| `rejected` | Won't implement | Add `rejected_date`, `rejected_reason`, rename with `x-` prefix |

## File Naming Convention

- **Active items:** `descriptive-title-YYYY-MM-DD.md`
- **Decided items:** `x-descriptive-title-YYYY-MM-DD.md`

The `x-` prefix indicates a terminal status (implemented, deferred, or rejected). This makes it visually obvious which items are still active.

## Automation Behaviors

### When Drew asks to "add a feature idea" or "capture this feature"

1. Create file with naming: `descriptive-title-YYYY-MM-DD.md`
2. Apply required frontmatter with `status: captured`
3. **Suggest `feature_type_tags`** based on document content analysis
4. Use reasoning to classify against common feature types: enhancement, integration, tooling, automation, refactor, performance, documentation, security, testing, ux, api, data
5. Use 2-4 tags per item

### When Drew marks a feature as implemented

1. Update `status: implemented`
2. Add `implemented_date: YYYY-MM-DD`
3. **Rename file** with `x-` prefix (e.g., `feature.md` → `x-feature.md`)
4. Ask Drew if there's an execution plan or PRD to note (informal, not required)

### When Drew marks a feature as deferred

1. Update `status: deferred`
2. Add `deferred_date: YYYY-MM-DD`
3. Add `deferred_reason: "reason"`
4. Optionally add `reconsider_after: YYYY-MM-DD`
5. **Rename file** with `x-` prefix

### When Drew marks a feature as rejected

1. Update `status: rejected`
2. Add `rejected_date: YYYY-MM-DD`
3. Add `rejected_reason: "reason"`
4. **Rename file** with `x-` prefix

### When Drew asks "what's in the backlog" or "feature status"

1. Scan frontmatter across all files in this directory
2. Report counts by status
3. List active items (no `x-` prefix) with titles and feature_type_tags
4. Highlight any items that have been in `captured` status for a long time

### When Drew approves a feature for implementation

1. Update `status: approved`
2. Add `approved_date: YYYY-MM-DD`
3. Keep filename unchanged (no `x-` prefix yet—still active)
4. Suggest creating an execution plan if appropriate

## Feature Type Tag Classification

When creating or updating feature backlog items, Claude should classify features using reasoning about:

- **What the feature does** - Is it adding new capability, improving existing, connecting systems?
- **Where it fits in the stack** - Is it tooling, API, data layer, UX?
- **What problem it solves** - Performance, automation, security, developer experience?

Common tags (expand as patterns emerge):

| Tag | Use For |
|-----|---------|
| `enhancement` | Improvements to existing functionality |
| `integration` | Connecting tools, systems, or data flows |
| `tooling` | New tools or utilities |
| `automation` | Automating manual processes |
| `refactor` | Code restructuring without behavior change |
| `performance` | Speed, efficiency, resource optimization |
| `documentation` | Docs, guides, references |
| `security` | Auth, encryption, access control |
| `testing` | Test coverage, validation, quality |
| `ux` | User experience improvements |
| `api` | API design, endpoints, contracts |
| `data` | Data models, storage, processing |

## What NOT To Do

- Do not create feature documents for work that's already in an execution plan
- Do not change status without Drew's explicit instruction
- Do not delete files—even rejected items are kept for record
- Do not add `x-` prefix until status is terminal (implemented/deferred/rejected)
