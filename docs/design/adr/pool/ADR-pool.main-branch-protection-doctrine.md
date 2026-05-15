---
id: ADR-pool.main-branch-protection-doctrine
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: EveryInc/compound-engineering-plugin
---

# ADR-pool.main-branch-protection-doctrine: Main Branch Protection Doctrine

## Status

Pool

## Intent

Codify gzkit's stance on `main` branch protection. Every Inc's Compound Engineering plugin's `AGENTS.md` § Working Agreement states: *"All changes to `main` go through pull requests. Direct pushes and direct merges are not allowed; branch protection on `main` enforces this by requiring the `test` status check to pass. The direct path bypasses `release:validate`, the test suite, and PR title validation — past direct merges have caused version drift requiring multi-PR recovery."*

gzkit currently has **no equivalent rule** in `AGENTS.md` and the observed behavior is direct commits to `main`. The 2026-05-15 session committed `16d70788`, `bf0bf2b0`, `c1394d80`, and prior commits directly to `main`, currently 3 commits ahead of `origin/main` at the time this ADR was filed. This is not framed as a defect — gzkit's ceremony (`gz check`, ARB receipts, Gate 5 attestation, ledger-of-truth) may substitute for traditional PR review in the solo-operator + solo-agent context. But the *posture is undocumented*, which is the gap this ADR resolves.

The doctrinal axis: does gzkit's existing governance ceremony substitute for a PR-required workflow, or is PR review a separate-and-additional structural defense that should be adopted?

Evidence to weigh:

- gzkit's ceremony is *agent-attestable* (`gz arb` receipts, ledger events). A PR adds a *human-observable* signal that an external reviewer (operator or CI) saw the change before it landed on `main`.
- CE's stated rationale for PR-required is concrete: *"past direct merges have caused version drift requiring multi-PR recovery."* gzkit's analog is its own history — whether gzkit has observed any drift class that a PR workflow would have caught is the empirical question for promotion.
- gzkit's solo-operator + solo-agent context is structurally different from CE's multi-contributor open-source project. PR review where the reviewer is the same person who authored the change is theater unless CI is doing the load-bearing work.

## Decision

_(Pool — design conversation in progress. The right answer is sensitive to gzkit's operator-engagement model and CI surface, both of which are operator-decidable.)_

Open surface decisions:

- **Workflow stance.** PR-required, no-PR-posture explicitly attested, or hybrid by commit type.
- **CI status check.** If PR-required, what is the `test` analog? Candidates: `gz check`, `gz validate --documents --surfaces`, `mkdocs build --strict`, or a composite.
- **Branch protection configuration.** If PR-required, configure GitHub branch protection on `main` (manual repo-settings change). If no-PR-posture, document the rationale in `AGENTS.md` so the absence is a positive doctrine, not an oversight.
- **Existing direct-commit precedent.** This session's commits ahead of `origin/main` were authored under the implicit no-PR posture; no retrospective re-routing is in scope.

## Alternatives Considered

### Path A — PR-required (CE-aligned)

**Shape.** Configure GitHub branch protection on `main` requiring (a) PR review approval (self-approval permitted given gzkit's solo posture) and (b) green status check on the PR (initially `gz check`; later expanded to include the full validator surface). `AGENTS.md` gains a § Branch Protection section stating: *"Direct pushes to `main` are blocked; all changes go through PR + green status check."*

**Strengths.**

- Mechanical defense: GitHub fail-closes on direct push, removing the failure mode entirely.
- External-observable signal: a PR creates a witnessable artifact (the PR description, the green check, the merge commit) that the ceremony's internal evidence (receipts, ledger) doesn't supply.
- Aligns with industry norm and CE's pattern; reduces friction if external contributors enter.

**Weaknesses.**

- For solo-operator + solo-agent work, self-approving a PR is theater. The structural signal is "the operator clicked Approve," which is the same gate as "the operator typed `git commit`."
- Adds workflow steps (push branch → open PR → wait for CI → merge) that the current solo posture skips.
- The status check is itself an inferential signal that's already supplied by `gz check` run pre-commit.

### Path B — Explicit no-PR posture

**Shape.** Document in `AGENTS.md` that gzkit's governance ceremony substitutes for PR review. Direct push to `main` is the canonical path. Add a § Branch Protection section that explicitly attests: *"gzkit does not use a PR workflow on `main`. The ceremony — `gz check` pre-commit, ARB receipts, Gate 5 attestation, ledger-of-truth — is the substitute. This posture is intentional for the solo-operator + solo-agent context; revisit when external contributors enter the picture."*

**Strengths.**

- Smallest workflow change; preserves the current effective posture.
- The doctrine is *explicit* (positive attestation of the no-PR choice) rather than the current implicit-by-omission state.
- Honest about gzkit's solo context — doesn't import process that exists for multi-contributor projects.

**Weaknesses.**

- The substitute claim ("ceremony = PR review") is asserted, not validated. There may be drift classes a PR workflow catches that the ceremony doesn't — unenumerated risks.
- No mechanical fail-closed for an accidental direct push of broken code. Pre-commit hooks are the only defense; if bypassed with `--no-verify`, nothing else blocks.
- If gzkit ever opens to external contributors, the posture must reverse — a future migration cost.

### Path C — Hybrid by commit type

**Shape.** Direct-commit allowed for `chore:`, `docs:`, `style:` commits. PR-required for `feat:`, `fix:`, `refactor:` and any commit touching `src/gzkit/**`, schemas, or `.gzkit/rules/**`. GitHub branch protection on `main` configured with a path-based or commit-type-based gate (depending on what's mechanically supported via GitHub Actions / status check rules).

**Strengths.**

- Matches the actual risk profile: docs and chores rarely break gates; source changes can.
- Lighter ceremony for low-risk changes; PR rigor where it matters.
- Composable with gzkit's existing Defect-fix routing thresholds (≤10 LOC direct fix vs OBPI ceremony).

**Weaknesses.**

- GitHub branch protection doesn't natively gate by commit-type or path in a way that's both deny-first and override-safe; implementation may require a custom Action that classifies the diff and gates the status check.
- Adds a new judgment surface: *"is this change `chore:` or `fix:`?"* The boundary is the existing conventional-commit doctrine, but now it has gate-affecting weight beyond changelog classification.
- More complex than A or B; harder to communicate; more vibing surface in the classification step.

### Path D — Defer

**Shape.** No rule articulation. The implicit no-PR posture continues. Revisit when (a) an external contributor opens a PR, (b) a direct-commit drift class surfaces, or (c) gzkit's contributor model changes.

**Strengths.**

- Zero workflow cost.
- Honest: the posture exists; documenting it now without operator decision is premature.

**Weaknesses.**

- The current implicit-by-omission state continues — future readers of `AGENTS.md` cannot tell whether gzkit *chose* the no-PR posture or merely *fell into* it.
- Defers a doctrinal axis that's load-bearing on agent behavior (an agent reading `AGENTS.md` gets no signal about whether to push directly or open a PR; this session was a worked example of the ambiguity).

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

### Related artifacts

- **CE plugin's `AGENTS.md` § Working Agreement** — branch protection rule with stated rationale (multi-PR recovery from version drift)
- **`docs/governance/defect-fix-routing.md`** — gzkit's existing direct-fix vs OBPI-ceremony routing thresholds (orthogonal but related)
- **`.gzkit/rules/gh-cli.md`** — gh CLI guardrails (currently silent on PR vs direct-push)
- **This session's git history** — `16d70788`, `bf0bf2b0`, `c1394d80` are recent direct-to-`main` commits under the current implicit posture; not retrospectively re-routed
- **`docs/governance/harness-engineering-appraisal.md` § Third confirming thesis** — surfaces CE's branch-protection rule as an operator-decision item

### Promotion guidance

The promotion author must commit to one of Path A, B, C, or D. If A or C is chosen, the resulting feature ADR must include:

- GitHub branch protection configuration plan. The ADR text can describe the config; applying it requires a manual repo-settings change by the operator (the ADR can't apply it).
- `AGENTS.md` § Branch Protection rule text.
- Status check definition (which `gz` invocations are required to pass).

If B is chosen, the resulting feature ADR must include:

- `AGENTS.md` § Branch Protection text explicitly attesting the no-PR posture with rationale.
- An "open question" subsection naming the drift classes the posture relies on the ceremony to cover (and how the ceremony does so).

If D is chosen, this pool ADR remains in the backlog until one of the named triggers fires.

### Inspired by

[EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) — `AGENTS.md` § Working Agreement is the most concrete branch-protection rule in published agent-contract prior art, with stated empirical rationale (past version drift requiring multi-PR recovery). The CE rule's specificity — *"branch protection on `main` enforces this by requiring the `test` status check to pass"* — is the model whether gzkit adopts the rule (Path A/C) or explicitly rejects it (Path B). Path D defers the decision but acknowledges CE as the prior-art anchor.
