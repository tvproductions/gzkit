<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Multi-Factor Staleness Classification

**Status:** Active
**Last reviewed:** 2026-02-12
**Parent ADR:** ADR-0.0.25 (Compounding Engineering & Session Handoff Contract)
**OBPI:** OBPI-0.0.25-05

---

## Overview

Session handoff documents degrade in reliability over time. The staleness classification system evaluates four independent factors to determine whether a handoff can be resumed directly or requires human verification.

This extends the time-only classification from ADR-0.0.25 Decision 4 into a **multi-factor** system that also considers git activity (commits, file changes, branch divergence).

### Design Principles

1. **Unknown = Fresh**: Missing git information does not artificially escalate staleness
2. **Worst-of semantics**: Any single factor at the highest severity governs the result (fail-closed)
3. **Import, don't duplicate**: Time classification delegates to the existing `classify_staleness()`
4. **Per-factor transparency**: `StalenessDetail` provides a full breakdown, not just the composite level

---

## Four-Factor Model

| # | Factor | Signal | Levels | Rationale |
|---|--------|--------|--------|-----------|
| 1 | **Time** | Timestamp age | Fresh / Slightly Stale / Stale / Very Stale | Oldest signal; context degrades with time regardless of code changes |
| 2 | **Commits** | Commit count since handoff | Fresh / Slightly Stale / Stale / Very Stale | Measures code velocity; many commits = many potential invalidations |
| 3 | **Files** | Unique files changed | Fresh / Stale / Very Stale | Coarser signal (no Slightly Stale); breadth of change matters |
| 4 | **Branch** | Branch divergence | Fresh / Stale | Binary: handoff branch is either still ancestral to HEAD or it isn't |

---

## Threshold Constants

### Time

| Classification | Age |
|----------------|-----|
| Fresh | < 24 hours |
| Slightly Stale | 24h - 72h |
| Stale | 72h - 7 days |
| Very Stale | > 7 days |

### Commits

| Classification | Commit Count |
|----------------|-------------|
| Fresh | 0 or unknown |
| Slightly Stale | 1 - 4 |
| Stale | 5 - 19 |
| Very Stale | 20+ |

### Files Changed

| Classification | File Count |
|----------------|-----------|
| Fresh | 0 - 9 or unknown |
| Stale | 10 - 49 |
| Very Stale | 50+ |

### Branch Divergence

| Classification | State |
|----------------|-------|
| Fresh | Not diverged or unknown |
| Stale | Diverged |

---

## Composition Semantics

The composite staleness level is determined by **worst-of** across all four factors:

```text
composite_level = max(time_level, commit_level, file_level, branch_level)
```

When multiple factors share the worst level, the **decisive factor** is the first in priority order:

1. Time (highest priority)
2. Commits
3. Files
4. Branch (lowest priority)

### Human Verification Gate

| Composite Level | Requires Human Verification |
|-----------------|----------------------------|
| Fresh | No |
| Slightly Stale | No |
| Stale | **Yes** |
| Very Stale | **Yes** |

---

## Programmatic API

### Data Types

```python
from tests.governance.test_staleness import GitContext, StalenessDetail

# Git context with known values
ctx = GitContext(
    commits_since=3,
    files_changed=5,
    branch_diverged=False,
    handoff_branch="feature/handoff",
    current_branch="feature/handoff",
)

# Git context with unknown values (all default to None => Fresh)
ctx_unknown = GitContext()
```

### Per-Factor Classifiers

```python
from tests.governance.test_staleness import (
    classify_staleness_by_time,
    classify_staleness_by_commits,
    classify_staleness_by_files,
    classify_staleness_by_branch,
)

classify_staleness_by_time("2026-02-10T10:00:00Z")  # => "Fresh"
classify_staleness_by_commits(3)    # => "Slightly Stale"
classify_staleness_by_files(25)     # => "Stale"
classify_staleness_by_branch(True)  # => "Stale"
```

### Multi-Factor Compositor

```python
from tests.governance.test_staleness import classify_staleness_multi, GitContext

detail = classify_staleness_multi(
    "2026-02-10T10:00:00Z",
    GitContext(commits_since=10, files_changed=5),
)
print(detail.level)            # "Stale" (worst-of)
print(detail.decisive_factor)  # "commits"
print(detail.requires_human_verification)  # True
```

### Git Context Gathering

```python
from tests.governance.test_staleness import gather_git_context

ctx = gather_git_context("2026-02-10T10:00:00Z", handoff_branch="main")
# Returns GitContext with live git state (None fields on failure)
```

---

## See Also

- [Session Handoff Schema](session-handoff-schema.md) -- Time-only staleness spec (superseded for multi-factor use)
- [ADR-0.0.25](../../design/adr/adr-0.0.x/ADR-0.0.25-compounding-engineering-session-handoff-contract/ADR-0.0.25-compounding-engineering-session-handoff-contract.md) -- Architecture decision record
- Tests: `tests/governance/test_staleness.py`
- Agent rules: `.github/skills/gz-session-handoff/assets/staleness-rules.md`
