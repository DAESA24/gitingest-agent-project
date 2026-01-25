# Feature Backlog Staging - Frontmatter Template

Copy the required fields when creating new feature backlog items. Optional fields are added as the workflow progresses.

## Required Fields (New Capture)

```yaml
---
doc_type: feature-backlog-item
title: "Descriptive Feature Title"
created: YYYY-MM-DD
status: captured
feature_type_tags:
  - tag1
  - tag2
---
```

## Optional Fields (Added as Workflow Progresses)

```yaml
# When status → approved
approved_date: YYYY-MM-DD

# When status → implemented
implemented_date: YYYY-MM-DD

# When status → deferred
deferred_date: YYYY-MM-DD
deferred_reason: "Why this feature was deferred"
reconsider_after: YYYY-MM-DD  # optional, for scheduled reconsideration

# When status → rejected
rejected_date: YYYY-MM-DD
rejected_reason: "Why this feature was rejected"
```

## Status Definitions

| Status | Meaning | File Prefix |
|--------|---------|-------------|
| `captured` | Idea documented, not yet considered for implementation | (none) |
| `approved` | Green-lit for implementation, awaiting execution | (none) |
| `implemented` | Feature shipped | `x-` |
| `deferred` | Not now, keeping for later consideration | `x-` |
| `rejected` | Won't implement, keeping for record | `x-` |

## Feature Type Tags

Claude suggests tags based on document content analysis. Common feature types include:

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

Use 2-4 tags per item. Create new tags as needed—the taxonomy will evolve.

## File Naming Convention

- **New items:** `descriptive-title-YYYY-MM-DD.md` (topic first, date at end)
- **Decided items:** `x-descriptive-title-YYYY-MM-DD.md` (x- prefix when implemented/deferred/rejected)
