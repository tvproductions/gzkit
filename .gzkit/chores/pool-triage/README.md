# pool-triage

Read-only drift-surfacing for gzkit's pool ADR backlog. Flags stale items, unarchived-superseded items, newly-unblocked promotion candidates, and duplicate-scope candidates during the between-ADR maintenance window.

- **Lane:** Lite
- **Parent ADR:** `ADR-pool.pool-management` (subordinate; time-bounded stopgap)

**Scope boundary.** Read-only — the chore surfaces drift for operator triage, never mutates pool state. The four heuristics are deliberately coarse; precise cluster-identification, computed priority ranking, and operator override persistence are deferred to the parent ADR's full implementation. Retirement or absorption is decided at parent ADR promotion.

```bash
uv run gz chores advise pool-triage
uv run gz chores run pool-triage
```
