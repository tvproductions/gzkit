ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.24-attestation-receipt-binding
Evaluator: main-session (manual review supersedes CLI pre-screen)
Date: 2026-05-02
Framework: assets/ADR_EVALUATION_FRAMEWORK.md (v1.0)
Red-team protocol: not requested (no `--red-team` flag)

--- CLI Pre-Screen (for traceability) ---

CLI verdict: GO (3.40 / 4.0)
CLI per-dimension: 3, 3, 4, 4, 4, 4, 4, 1
CLI flagged Dim 8 = 1 ("No exemplar/precedent language; No anti-pattern guidance")
CLI flagged Dim 1 = 3 ("No after/target-state language in Intent")
CLI flagged Dim 2 = 3 ("No rationale language in Decision")

Per framework Part 1 intro and skill Common Rationalizations, any
dimension scoring 1 must be revised regardless of weighted total. The
CLI's Dim 8 = 1 verdict was investigated as a structural blocker before
authoring this scorecard — verdict: heuristic false negative, no defect.

NOTE: rerunning `gz adr evaluate` overwrites this file with the CLI
pre-screen. This manual scorecard is the authoritative artifact and
must be restored after any rerun.

--- ADR-Level Scores (manual, authoritative) ---

| # | Dimension | Weight | Manual | CLI | Weighted | Heuristic-mismatch / rationale |
|---|-----------|--------|--------|-----|----------|--------------------------------|
| 1 | Problem Clarity | 15% | 4 | 3 | 0.60 | CLI keyword heuristic missed before/after framing; Intent quantifies the problem with external evidence (Opus 4.7 § 2.3.6.2 "Skipped cheap verification"; GPT-5.5 Apollo § 9.2 — 29% Impossible-Coding-Task lie rate) and contrasts current narrative-trust state ("the citing agent must verify") with mechanical fail-closed end state. |
| 2 | Decision Justification | 15% | 4 | 3 | 0.60 | CLI flagged "no rationale language in Decision" — false negative; rationale lives in the dedicated `## Alternatives Considered` section enumerating three rejected alternatives (advisory-only, fail-closed-on-all-lanes, git-pre-receive hook), each with specific reasoning citing Opus 4.7 § 2.3.6.2 and the layered-trust T2 doctrine. CLI looked inside `## Decision` only. |
| 3 | Feature Checklist | 15% | 4 | 4 | 0.60 | Agree. Four items map cleanly to runtime/wiring/doc/BDD; each is necessary (removing any breaks a gate covenant), no padding. |
| 4 | OBPI Decomposition | 15% | 3 | 4 | 0.45 | Slight downgrade. OBPI-03 (doc-only) and OBPI-04 (BDD-only) are each plausibly small enough to bundle, but separating them is defensible because Gate 3 (docs) and Gate 4 (BDD) are independent heavy-lane gates with distinct verification surfaces. Decomposition Scorecard yields baseline 4 with no splits — consistent. |
| 5 | Lane Assignment | 10% | 4 | 4 | 0.40 | Agree. OBPI-03's `## Lane` block now explicitly cites the foundation-kind inheritance rule from § Lane & Kind & Sensitivity Attestation Matrix, naming the doctrine-drift-is-invariant-drift rationale that overrides the AGENTS.md § Lane Rules doc-only-stays-Lite default. Polish applied during this evaluation. |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | Agree. ADR now carries a dedicated `## Non-Goals` section naming three explicit non-goals (no emergency-skip flag, no git-pre-receive enforcement, no fail-closed on lite-lane non-foundation), each with reasoning. Polish applied during this evaluation. |
| 7 | Evidence Requirements | 10% | 4 | 4 | 0.40 | Agree. Each OBPI carries a Verification block with concrete commands; each Acceptance Criterion is REQ-tagged Given/When/Then; Heavy Gate 3/4/5 obligations explicit per OBPI; coverage floor stated (40%) in OBPI-01 REQ. |
| 8 | Architectural Alignment | 10% | 4 | 1 | 0.40 | **CLI false negative — investigated and overridden.** ADR explicitly cites: `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` (Decision-1, Negative consequence, OBPI-02 REQ-6); `_enforce_human_attestation_authenticity` (OBPI-02 REQ-7); `_requires_human_obpi_attestation` at `src/gzkit/commands/adr_audit.py` (Decision-3 inheritance); AGENTS.md § Lane & Kind Attestation Matrix (Decision-3); `docs/governance/arb-middleware.md` (Decision-5). Anti-patterns named with external evidence: GHI #290 attestation-payload-synthesis vector (Positive consequence #2), Opus 4.7 § 2.3.6 six-pattern failure taxonomy (Intent), GPT-5.5 Apollo § 9.2 (Intent). Guardrails: extend-only rule on `CANONICAL_STEP_COMMANDS` cited as mitigation. CLI keyword heuristic searched for "exemplar"/"pattern"/"anti-pattern" tokens verbatim and missed the structural-equivalent prose. |

WEIGHTED TOTAL (manual): **3.85 / 4.0** — GO
WEIGHTED TOTAL (CLI):  3.40 / 4.0 — GO
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

No dimension scored 1 under manual review. The CLI's Dim 8 = 1 was a
heuristic false negative: the ADR references multiple module-pathed
precedents (`src/gzkit/arb/validator.py`, `src/gzkit/commands/adr_audit.py`,
`docs/governance/arb-middleware.md`) and names anti-patterns with concrete
external evidence (Opus 4.7 system card, GPT-5.5 Apollo evaluation,
GHI #290). No structural defect.

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|--------------|-------------|-------|------|---------|-----|
| 01 validator-scope        | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 02 wire-into-completion   | 3 | 4 | 4 | 3 | 4 | 3.6 |
| 03 doc-updates            | 3 | 3 | 4 | 3 | 4 | 3.4 |
| 04 bdd-coverage           | 3 | 4 | 4 | 3 | 4 | 3.6 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised. **PASS** — all OBPIs >= 3.0; no dimension at 1.

OBPI scoring rationale (where manual differs from CLI's blanket 3.8):

- **OBPI-02 Independence: 3** — declared dependency on OBPI-01 (validator
  function); STOP-on-BLOCKERS in brief.
- **OBPI-03 Independence: 3** — declared dependencies on OBPI-01 and -02
  (manpage cannot show real output for unimplemented surface).
- **OBPI-03 Testability: 3** — verification is a small set of commands
  (`mkdocs build --strict`, `gz cli audit`, `gz validate --documents`,
  grep checks), not a single command.
- **OBPI-03 Clarity: 4** — Lane rationale tightened during this
  evaluation to cite foundation-kind inheritance explicitly.
- **OBPI-04 Independence: 3** — declared dependencies on OBPI-01, -02,
  and -03.
- **OBPI-04 Clarity: 4** — REQ-9 now names the TTY-mock boundary
  explicitly: `pexpect`-shaped fixture at the subprocess boundary,
  with explicit prohibition on internally patching
  `_enforce_human_attestation_authenticity` (that's the unit-tier
  surface in OBPI-02). Polish applied during this evaluation.

--- Red-Team Challenges ---

Not run. `--red-team` flag was not specified. The 10-challenge protocol
is optional per the skill; the GO verdict is based on the rubric alone.
Recommend running the red-team pass before promoting Draft -> Proposed
if the operator wants stronger adversarial review — especially Challenge
9 (Regression): silent-break vector six months out when a new ARB receipt
family ships without `CANONICAL_STEP_COMMANDS` extension.

--- Overall Verdict ---

[x] **GO** — Ready for proposal/defense review
[ ] CONDITIONAL GO
[ ] NO GO

POLISH APPLIED DURING THIS EVALUATION:

1. **ADR-level `## Non-Goals` section added** — names three explicit
   non-goals (no emergency-skip flag, no git-pre-receive enforcement, no
   fail-closed on lite-lane non-foundation). Closed Dim 6 polish item.
2. **OBPI-03 Lane rationale tightened** — now cites foundation-kind
   inheritance from § Lane & Kind & Sensitivity Attestation Matrix as
   the rule that overrides the AGENTS.md doc-only-stays-Lite default.
   Closed Dim 5 polish item.
3. **OBPI-04 REQ-9 tightened** — names `pexpect`-shaped subprocess-
   boundary fixture as the canonical TTY-mock; explicitly prohibits
   internal-patching of `_enforce_human_attestation_authenticity`
   (which is the unit-tier surface in OBPI-02). Closed OBPI-04 Clarity
   under-specification.

REMAINING (NON-BLOCKING):

1. **Optional: red-team pass** — `/gz-adr-evaluate ADR-0.0.24 --red-team`
   for adversarial review before Draft -> Proposed. Especially Challenge 9.
