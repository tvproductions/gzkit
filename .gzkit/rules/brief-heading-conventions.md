---
id: brief-heading-conventions
paths:
  - "docs/design/adr/**/obpis/**"
description: Brief evidence sections must use H3 (not H2) — enforced by gz validate --brief-headings (GHI #238)
---

# Brief Heading Conventions (gzkit)

<!-- rule-version: 0.2.0 -->

> **Rule version:** `0.2.0` — scored for real under GHI #921 (2026-08-30). This rule sat in `data/advisory_scorecard_grandfather.json`, pinned at `0.1.0` against a version nobody recorded; the pin is stripped by any edit, so its clauses were re-read and its Coverage Ledger rows added or corrected in the same commit. Prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#brief-heading-conventionsmd). Binding rules unchanged.

OBPI brief evidence sections MUST use H3 (`###`), not H2 (`##`).

## Canonical evidence sections (H3)

| Heading | Consumer |
|---------|----------|
| `### Implementation Summary` | `gz obpi complete`, closeout evidence pass |
| `### Key Proof` | `gz obpi complete`, closeout evidence pass |
| `### Closing Argument` | `extract_closing_argument`, defense-brief renderer |

`## Acceptance Criteria` (H2) is the canonical top-level brief section and
is deliberately not in the list above — do not conflate it with the per-pass
evidence `### ACCEPTANCE` section (which, if present, is H3).

## Why H3, not H2

Ceremony renderers and completion hooks extract these sections by H3 heading
match. A brief that drifts one of the canonical evidence headings to `##`
silently passes schema validation (the section exists) but the extractor
stops at the next H2 boundary and returns an empty body — triggering
mid-ceremony failures and post-attestation diagnostic noise.

Gate 2 (`## Objective`, `## Acceptance Criteria`, `## ALLOWED PATHS`, etc.)
remains H2: those are top-level brief structure, not per-pass evidence.

## Mechanical check

```bash
uv run gz validate --brief-headings
```

Exits 3 on drift. Recovery: rewrite the heading as H3 and re-run
completion. Do not "accept both levels" at the hook — the hook is the
contract; the brief is the defect.

## Related

- GHI #238 — promotion of this rule from hook-level silent failure to a
  `gz validate --brief-headings` scope.
- `.gzkit/rules/gate5-runbook-code-covenant.md` — documentation is a
  first-class deliverable; evidence-section heading drift is the same
  class of failure as runbook drift.
- `docs/governance/advisory-rules-audit.md` — scorecard entry.
