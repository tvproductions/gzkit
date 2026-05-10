# Summary — Control Surface Skill ↔ Rule Reachability Audit (Pass B)

Generated: 2026-05-10
Scope: 50 active skills × 20 canonical rules under .gzkit/rules/**
Output: audit-only; no edits to skills, rules, or source

## Headline counts

| Bucket | Count | Share |
|---|---|---|
| Honored — explicit body cite | 13 | 26% |
| Honored — mechanical (validator/runtime) | 22 | 44% |
| Gap — latent (no matching GHI) | 6 | 12% |
| Gap — known-blocking (matching GHI exists) | 11 | 22% |
| Total matrix rows | 50 | 100% |

## Top 5 known-blocking gaps with one-line recommendation

1. **gz-obpi-pipeline + gz-adr-closeout-ceremony ↛ gate5-runbook-code-covenant.md** (rows 3, 18, 26; GHIs #427, #422, #436, #259, #155, #335) — **promote mechanical check**: wire `gz validate --doc-surface-parity` into pipeline Stage 4 and closeout Step 2 as fail-close.
2. **gz-obpi-lock ↛ token-block-discipline.md § Sub-Invariants 1–5** (row 24; GHIs #410, #248, #245, #244, #243) — **reconcile skill**: edit SKILL.md body to cite the five binding sub-invariants at the release step.
3. **gz-chore-runner ↛ chores.md § Two-Surface Layout** (row 14; GHIs #306, #304, #189) — **reconcile skill**: add §0 instructing `gz validate --chores-layout` and `gz chores doctor --dry-run` as preflight.
4. **git-sync ↛ gh-cli.md + commit-message discipline** (row 50; GHIs #439, #437, #201, #343) — **promote mechanical check**: gate `gz git-sync` on `gz validate --commit-trailers` rejecting `fix()` subject rewrites.
5. **gz-tech-debt-review ↛ tests.md § Tests assert semantics** (row 42; GHIs #310, #272 — chore source case) — **reconcile skill**: cite the invariant in § Review dimensions to prevent the GHI #268-class pattern.

Routing distribution: reconcile skill = 3, promote mechanical check = 2, reconcile rule = 0, accept gap = 0.

The chore's source-case GHI #268 / #272 pattern (skill procedure pushes agent into rule-violating action without naming the rule) recurs in rows 14, 24, 42. Fix template is identical: body-level cite of rule § section at the relevant procedure step.
