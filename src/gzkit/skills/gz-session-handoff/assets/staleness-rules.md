# Staleness Classification Rules (Agent Reference)

Quick-reference for multi-factor staleness classification.
Full spec: `docs/governance/GovZero/staleness-classification.md`

---

## Factor Thresholds

### Time (from timestamp age)

| Level | Age |
|-------|-----|
| Fresh | < 24h |
| Slightly Stale | 24h - 72h |
| Stale | 72h - 7d |
| Very Stale | > 7d |

### Commits (since handoff)

| Level | Count |
|-------|-------|
| Fresh | 0 / unknown |
| Slightly Stale | 1 - 4 |
| Stale | 5 - 19 |
| Very Stale | 20+ |

### Files Changed (unique, since handoff)

| Level | Count |
|-------|-------|
| Fresh | 0 - 9 / unknown |
| Stale | 10 - 49 |
| Very Stale | 50+ |

### Branch Divergence

| Level | State |
|-------|-------|
| Fresh | Not diverged / unknown |
| Stale | Diverged |

---

## Composition Rule

**Worst-of**: The composite level equals the highest severity across all four factors.

**Priority order** (for decisive factor): time > commits > files > branch

---

## Human Verification Decision

```text
composite_level in (Stale, Very Stale) => requires_human_verification = True
composite_level in (Fresh, Slightly Stale) => requires_human_verification = False
```

---

## Key Principle

**Unknown = Fresh.** Missing git data does not escalate staleness.
