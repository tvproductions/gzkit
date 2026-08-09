# GHI Cross-Reference — Pass B

> Chore: `control-surface-skill-rule-reachability` (Lite lane, audit-only)
> Run: **2026-08-09**. Supersedes the 2026-08-01 cross-reference.

CHORE.md § Workflow 3: a `no` row with a historical GHI hit is a **known-blocking**
gap; a `no` row without one is **latent**. The distinction is what separates a
reachability gap that has already cost something from one that has not yet.

**9 of 11 gaps carry a GHI.** That ratio is the finding: these are not hypothetical
collisions. Each named issue is a case where the gap already produced a defect
someone had to file.

| Gap | Skill | Rule | GHI | What the GHI recorded |
|---|---|---|---|---|
| N1 | `gz-agent-sync` | `skill-surface-sync.md` #6 | **#492** | `skill-version` / `last_reviewed` coupling — the promotion is parked in `ADR-pool.skill-version-review-coupling`, unbuilt |
| N2 | `gz-obpi-pipeline` | `model-selection.md` #4 | **#284** | subagent dispatch naming a model instead of an effort directive |
| N3 | `gz-obpi-pipeline` | `model-selection.md` #5 | **#643** | subagent factual assertions relayed into ceremony without re-derivation |
| N4 | `gz-obpi-lock` | `token-block-discipline.md` SI-5 | **#619** | lock release without an exchange register entry or `--abandon` |
| N7 | `gz-check` | `gate5-runbook-code-covenant.md` § Do Not | **#317** | bare commands cited as attestation evidence; no `arb-*` receipt |
| N8 | `gz-tidy`, `gz-check` | `agents-md-map-doctrine.md` § Budget | **#373** | per-file instruction budgets duplicated into prose and drifting from the JSON |
| N9 | `ghi-close` | `task-discovery.md` § Invariant | **#552** | `src/**`/`tests/**` commits missing the mandatory `Task:` trailer |
| N10 | `gz-obpi-simplify` | `complexity-thresholds.md` § Invariant | **#652** | a second threshold authority contradicting the canonical table |
| N11 | `gz-cli-audit` | `cli.md` § Consistency | **#353** | per-flag documentation backlog accumulating behind a report-only audit |
| N5 | `gz-adr-audit` | `adr-audit.md` § Audit sequence | *none* | **latent** — bare verification commands feeding an evidence index, and an `--evidence-json` payload with no `receipts` key |
| N6 | `gz-adr-audit` | `adr-audit.md` § Rules | *none* | **latent** — `gz audit` invoked three times before attestation, against a flat prohibition |

## Reading the pattern

**Both latent rows are in the same skill**, `gz-adr-audit`, and both concern the
same subject: the ordering and receipt-form of audit evidence. A skill that has
accumulated two independent, un-filed collisions with the one rule named after it
is the strongest candidate in this matrix for a reconcile pass.

**Five of the nine known-blocking gaps name a promotion that was never built:**
#492 (`--skill-version-review-coupling`, parked in an unpromoted pool ADR), #643
(`--pipeline-review-receipts`, cited twice in the skill and *not registered* in
`validate_cmd.py`), #284, #619, #353. In each case the skill and the rule both
exist, both are correct in isolation, and the arm that would have reconciled them
is the thing missing.

That is the Pass B analogue of what Pass A and Pass C each found independently
today: **the gap is never the rule and rarely the skill — it is the absent
witness.**

## Not carried forward

The prior run's cross-reference is superseded rather than merged: every GHI above
was re-checked this run against the current skill and rule text, and rows whose
skill or rule moved (N1, N4, N7, N8, N10) were re-derived from the current
`file:line`, not copied. No prior GHI hit was dropped without a verdict — see
`reachability-matrix.md` § Prior-row accounting.
