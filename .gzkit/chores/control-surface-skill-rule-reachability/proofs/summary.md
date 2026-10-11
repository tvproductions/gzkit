# Pass B Summary — Skill ↔ Rule Reachability

> Chore: `control-surface-skill-rule-reachability` (Lite lane, audit-only)
> Date: **2026-10-10** (prior run: 2026-08-09), maintenance visit E
> Inputs: `skill-inventory.md`, `reachability-matrix.md`, `ghi-cross-reference.md`
> Trigger: the freshness gate failed closed; all 73 skill files changed since the prior proofs.

## Counts

| Measure | Value |
|---|---|
| Skills audited | **73**, each read whole by one of four independent reviewers |
| Authored rules | 26, each read whole by all four |
| Applicable pairs by path overlap | 294 |
| Skills citing no rule | 53 of 73 |
| **Gaps with a worked example** | **35**: 17 known-blocking, 18 latent |
| Carried from August | 6 (N1, N5, N7, N8 gz-check half, N9, N10) |
| Closed since August | 5 and a half (N2, N3, N4, N6, N11, N8 gz-tidy half) |
| New | 29 (10 high confidence, 19 medium) |
| Quoted lines verified by the main session | 83 of 83 |

## Headline 1: rules move and skills are not swept

Ten of the 29 new gaps are a skill still carrying wording a rule or ruling has since reversed:

- **Chore canon (2026-09-28).** `chores.md` 0.6.0 made `.gzkit/chores/` the authoring source. `gz-chore-runner`, `gz-context-diet` and `gz-obpi-specify` still call the package copy canonical, and `gz-pythonic-pattern-detect` still prescribes a bare `gz chores doctor` (B18, B22).
- **Gate 5 naming (GHI #822).** `gz-advisor-qc` and `gz-complexity-distill` still call a non-completion attestation "Gate 5" (B14, B21).
- **No branches, and worktrees (2026-09-27).** `gz-obpi-lock` still teaches a named branch and a merge (B01).
- **Foundation closed.** `gz-foundation-triage` still recommends reclassification to foundation (B20).
- **Boundary 5 (2026-09-29).** `airlineops-parity-scan` still treats AirlineOps as canon to chase (B17).
- **Release notes ownership.** `gz-adr-closeout-ceremony` still edits and publishes the cumulative file (B06, B09).
- **Weaponeering (2026-10-10).** The pipeline flies red before constraints (B02), expected until the sortie layer lands.

Nothing couples a rule's version to the skills that restate it. `skill-authoring.md` Parsimony clause 2 says "one home per meaning"; these are the places where a second home went stale.

## Headline 2: the `gh` allowlist is narrower than what skills prescribe

`gh-cli.md` § Allowed commands lists five verbs. Skills prescribe `gh issue edit` (B08), `gh issue view` (B25, and `ghi-close`, `gz-status`, this repository's own chore evidence gate), plain `gh issue create` outside `ghi-author` (B07), and the rule's own § Census prescribes `gh api`. The operator has widened the block twice after a step proved unreachable. One ruling settles the class: is the block exhaustive, and which read-only verbs join it.

## Headline 3: three skills let an agent act where the root contract reserves the act

`gz-obpi-lock` "Lock first, always" (B03), `gz-state --repair` after telling rather than asking (B27), and `gz-skill-review` rewriting and pushing a skill on an audit warning (B29). Each is medium confidence because the root clause is general and the skill's step is plausible on its own terms. Each is the kind of step the root contract was written to stop.

## Top five known-blocking, ranked

1. **B06** `gz-adr-closeout-ceremony:243` publishes the cumulative release notes; GHI #710 fixed this in one skill and left the twin. Reconcile the skill.
2. **B15** `gz-deps-upgrade:85` uses a bare `python3`; the clause was breached 40 times this session with nothing observing it. Reconcile the skill; a mechanical witness is proposed in the permission-consent audit.
3. **B18 and B22** the chore-canon labels in four skills. Reconcile the skills; one pass.
4. **N9** `ghi-close` never names the `Task:` trailer its commits require. Reconcile the skill.
5. **B14 and B21** the Gate 5 naming in two skills. Reconcile the skills.

Every gap row carries its recommendation in the matrix: 25 reconcile the skill, 4 reconcile the rule (B08, B25, B28, B29), and the carried six as stated in August.

## What this run did not do

It repaired nothing. A repair that touches a skill is operator-only (`skill-authoring.md` § Enforcement posture), and this chore is audit-only. No reviewer ran a command, so verbs, flags and exit codes named in skills were read, not observed. The gap list is bounded at eight per partition by the brief the reviewers worked to; partitions P1, P2 and P3 each returned eight, so more may exist there.

## After the run: the sweep of 2026-10-11

"It repaired nothing" describes the run of 2026-10-10. On 2026-10-11 the operator ordered the
sweep of headline 1, and commit `04fda99d3` repairs it: six rows closed (B01, B06, B14, B18, B20,
B22), three narrowed and still open (B02, B09, B17), one withdrawn for a ruling (B21). The
operator ruled on B21 the same day ("B": each recurring pass runs as an OBPI the operator
initiates) and commit `a87603775` closes it. 28 of the 35 gaps are open. Row detail and limits
are in `reachability-matrix.md`.
