# Pass B Summary — Skill ↔ Rule Reachability

> Chore: `control-surface-skill-rule-reachability` (Lite lane, audit-only)
> Date: **2026-08-09** (prior run: 2026-08-01)
> Inputs: `skill-inventory.md`, `reachability-matrix.md`, `ghi-cross-reference.md`
> Trigger: `scripts/check_proof_freshness.py` failed closed — both audited surfaces
> moved: `.gzkit/rules` (18 files) and `.gzkit/skills` (14 files).

## Counts

| Measure | Value |
|---|---|
| Skills audited | **68** |
| Canonical rules | 26 |
| Applicable pairs | **624** |
| Honored by citation | 21 |
| Honored mechanically | 8 |
| **Gaps with a worked example** | **11** — 9 known-blocking, 2 latent |
| Skills citing **zero** rules | **36 of 68** |
| Citations resolving only through a `.claude/rules/` mirror | **5** |

Prior-row accounting: **all 25 rows plus 6 structural notes have a verdict** —
23 carried, 2 closed, 1 premise refuted.

## Headline 1: 9 of 11 gaps have already cost something

A gap is `known-blocking` when a filed GHI records the defect it produced. Nine do:
**#492, #284, #643, #619, #317, #373, #552, #652, #353.** These are not predicted
collisions; each is a case where a skill's procedure already walked an agent into a
rule violation and someone had to file it.

**Five of the nine name a promotion that was never built.** #643 is the sharpest:
`gz-obpi-pipeline` cites `gz validate --pipeline-review-receipts` twice as its
reconciling arm, and **that flag is not registered in `validate_cmd.py`.** The skill
routes to a witness that does not exist.

## Headline 2: the two most dangerous gaps are in the pipeline skill

`gz-obpi-pipeline` (6.35.0) carries N2 and N3, both against `model-selection.md`,
whose `paths:` binds all 68 skills:

- **N2** — Stage 2 passes `model: haiku|sonnet|opus` into the Agent call. The rule:
  *"Subagents use effort directives, not model names."*
- **N3** — Stage 4 dispatches a `narrator` to render the Gate-5 attestation surface
  and **no step re-derives its claims** before presenting them to the human. The
  rule: *"Never relay a subagent's factual assertion into ceremony, attestation, or
  an operator-facing conclusion on the subagent's word."*

N3 is the one to fix first. It sits directly on the attestation path, and its
failure mode is a human attesting to a subagent's unverified narrative — which is
the fabrication class the whole receipt system exists to prevent.

## Headline 3: 71 stale proof files ship to adopters

Found while accounting for the prior row set, and verified first-party:

```
$ ls -d src/gzkit/chores/*/proofs | wc -l
29
$ find src/gzkit/chores -path '*/proofs/*' -type f | wc -l
71
$ grep -n "always project-local" .gzkit/rules/chores.md
35:`proofs/` is **always project-local, never canonical** — execution evidence is
$ …distribution_baseline_manifest.json → proofs mentions: 0
```

**29 chore directories ship a `proofs/` folder into `src/gzkit/chores/`** — the
wheel surface — while two rules declare that surface carries no proofs content
(`chores.md` § Two-Surface Layout, `skill-surface-sync.md` § class-classifier). The
distribution baseline manifest does not mention `proofs` at all, so
`gz validate --distribution` has nothing to compare against and reports clean.

This chore's own stale copy is one of the 71: a 24 KB, 2026-05-08, 50-row
`reachability-matrix.md`, still shipping. **The rows the 2026-08-01 pass dropped did
not disappear — adopters are still receiving them.**

## The pattern, and its agreement with Passes A and C

Three audits ran today on three different subjects. Each concluded the same thing by
a different route:

| Pass | Subject | Conclusion |
|---|---|---|
| A (rule ↔ rule) | 19 rows | rules that *describe* a gate rot; rules that *disclose* having none do not |
| C (prose ↔ check) | 43 rows | 19 rows assert a mechanism and all 19 drifted; 6 disclose and none ever has |
| **B (skill ↔ rule)** | **11 gaps** | **the gap is rarely the skill and never the rule — it is the absent witness** |

In every N-row above, the skill is internally coherent and the rule is internally
coherent. What is missing is the arm that would make them agree. Five gaps name that
arm explicitly and it was never built.

## Prioritized follow-up

Operator canon: a GHI-tracked repair routes to direct fix. This chore is read-only
on skills and rules; nothing below was applied.

| # | Route | Target | Fix | Gap |
|---|---|---|---|---|
| 1 | **direct-fix** | `.gzkit/skills/gz-obpi-pipeline/SKILL.md` Stage 4 | Add a re-derivation step before the narrator's output reaches the attestation surface. **On the Gate-5 path; fix first.** | N3 |
| 2 | direct-fix | same skill, Stage 2 | Replace `model: <tier>` with an effort directive per `model-selection.md` #4 | N2 |
| 3 | direct-fix | `.gzkit/skills/gz-obpi-lock/SKILL.md` § Release | Teach `--abandon <category>:<reason>`; correct *"`--force` … bypass ownership check"* and drop the *"automatically released on next claim"* line the rule names as an anti-pattern | N4 |
| 4 | direct-fix | `.gzkit/skills/gz-check/SKILL.md` § Full Quality Evidence Sequence | Replace the four bare commands with ARB-wrapped canonical invocations. The section is headed *"When deterministic receipts are needed"* and produces none. | N7 |
| 5 | direct-fix | `gz-tidy` + `gz-check` | Delete the hardcoded "200 lines" CLAUDE.md budget; point at `gz validate --instructions-files-budget`. The doctrine's own prohibition, violated as it predicts. | N8 |
| 6 | direct-fix | `.gzkit/skills/ghi-close/SKILL.md` Step 6 + 7a | Add the `Task:` trailer floor for `src/**`/`tests/**` commits | N9 |
| 7 | direct-fix | `.gzkit/skills/gz-obpi-simplify/SKILL.md` Dimension 2 | Cite the canonical threshold table instead of the 50/600 pair, per `pythonic.md:29`'s own resolution | N10 |
| 8 | **file a GHI** | `src/gzkit/chores/*/proofs/` | 71 stale evidence files ship to adopters from a declared-project-local surface, invisible to `--distribution`. Sync should skip `proofs/`, and the classifier should say so. | Headline 3 |
| 9 | direct-fix | `.gzkit/skills/gz-adr-audit/SKILL.md` | Two latent collisions with the rule named after it (bare verification commands; `gz audit` before attestation). Strongest reconcile candidate in the matrix. | N5, N6 |
| 10 | direct-fix | `.gzkit/skills/gz-cli-audit/SKILL.md` | Add the remediation step `cli.md` § Consistency binds — *"author the missing artifacts in the same patch"* | N11 |
| 11 | **operator ruling** | 5 mirror-only citations | `governance-core.md` and `pythonic.md` are reachable from skills **only** through `.claude/rules/` paths — a live pointer into a surface `skill-surface-sync.md` #4 forbids editing. Repoint to canonical, or accept mirrors as citable. | inventory |

## Audit posture

- **Lane:** Lite — audit-only. This run edited exactly six files, all under this
  chore's `proofs/`. No skill, rule, or source file was modified.
- **Admission bar held:** 624 pairs are "applicable" by the CHORE's own test, and
  only **11** produced rows. The other 613 are pairs where a broad `paths:` glob
  overlaps but no procedure can collide — recorded as applicable, not as gaps.
  A gap requires a concrete worked example.
- **Mechanically generated:** `skill-inventory.md` is emitted from the 68 `SKILL.md`
  files; `skill-listing.txt` and `rule-listing.txt` from directory listings.
- **First-party verification:** Headline 3 was re-verified directly by the session
  (directory counts, the rule quote, and the baseline-manifest search), not accepted
  from the reader that surfaced it.
