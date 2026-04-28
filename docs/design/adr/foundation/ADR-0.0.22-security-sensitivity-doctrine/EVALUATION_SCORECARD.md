ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.22 — Security Sensitivity Doctrine
Evaluator: main-session (manual review supersedes CLI pre-screen)
Date: 2026-04-28 (revision)

CLI Pre-Screen (for traceability)
---------------------------------

- Initial verdict (pre-revision): GO, 3.55 / 4.0
- Re-run verdict (post-revision): GO, 3.70 / 4.0
- The CLI under-scored Problem Clarity (3) and Decision Justification (3)
  on pattern-match heuristics (false negatives — the after-state lives in
  named Decision bullets, not Intent prose; decisions are bulleted with
  independent justification rather than numbered).
- The CLI now scores OBPI Decomposition at 4 (was 3, "Allowed Paths overlap
  significantly") because the briefs no longer point at the bare ADR
  package — Allowed Paths now name the specific implementation surfaces.
- Manual scores below are authoritative; CLI scores are recorded for
  traceability per skill protocol.

Revision summary
----------------

Six OBPI briefs were revised in this session to close the structural
defects flagged in the prior CONDITIONAL GO:

1. **Per-OBPI Requirements scoping.** Each brief's identical 28-item
   Requirements block was replaced with brief-scoped requirements that
   assert only the contract that brief owns. Cross-brief invariants
   stay in the parent ADR Decision.
2. **Allowed Paths now name the implementation surfaces.** Each brief's
   Allowed Paths were expanded to include the specific files / module
   directories named in its Objective:
   - OBPI-01 added `src/gzkit/schemas/{adr,obpi}.json`, `src/gzkit/models/**`, `tests/**`.
   - OBPI-02 added `src/gzkit/schemas/security_surfaces.json`, `src/gzkit/models/**`, `tests/**`.
   - OBPI-03 added `src/gzkit/governance/trust_audits.py`, `src/gzkit/cli/parser_validate.py`, `src/gzkit/cli/**`, `tests/**`, waiver file.
   - OBPI-04 added `src/gzkit/commands/adr_audit.py`, `tests/commands/**`.
   - OBPI-05 added `src/gzkit/commands/obpi.py`, `src/gzkit/arb/validator.py`, `tests/**`, waiver file.
   - OBPI-06 added rule mirror paths, `docs/governance/advisory-rules-audit.md`, `tests/governance/**`.
3. **Boilerplate REQs replaced with REQ-derived per-behavior assertions.**
   The generic REQ-X-NN-01/02/03 ("artifacts exist", "stays in scope",
   "commands run") was replaced in every brief with 5-7 per-behavior
   REQs that derive from each brief's specific contract (e.g. OBPI-01
   now asserts schema-accepts-security, schema-rejects-malformed,
   Pydantic-model-exposes-field, backwards-compatibility floor).
4. **Dependency graph declared in frontmatter.** `depends_on:` was added
   to each brief mirroring the ADR's parallelism: `{01, 02} → 03 →
   {04 → 05} → 06`. OBPI-01/02 carry `depends_on: []`; OBPI-03 lists
   01 and 02; OBPI-04 lists 01; OBPI-05 lists 04; OBPI-06 lists 03/04/05.

`uv run gz validate --documents` passes after the revisions.

--- ADR-Level Scores (Manual, post-revision) ---

| #   | Dimension               | Weight | CLI | Manual | Weighted | Findings |
|-----|-------------------------|--------|-----|--------|----------|----------|
| 1   | Problem Clarity         | 15%    | 3   | 4      | 0.60     | Veracode 45/86/88% with cited 211M-line study; before-state (no mechanical sensitivity classification); after-state (auto-detect floor + audit OR + Gate 5 walkthrough). CLI heuristic missed the after-state because it lives in named Decision bullets. |
| 2   | Decision Justification  | 15%    | 3   | 4      | 0.60     | 7 alternatives REJECTED with specific reasons; each decision references precedent (ADR-0.0.18, GHI #290). CLI heuristic counted numbered items only — false negative. |
| 3   | Feature Checklist       | 15%    | 4   | 4      | 0.60     | 6 items, 1:1 with OBPIs, each with concrete deliverable. |
| 4   | OBPI Decomposition      | 15%    | 4   | 4      | 0.60     | Was 2 pre-revision (duplicated Requirements + non-specific Allowed Paths). Post-revision: each brief has scoped Requirements, Allowed Paths matching Objective, declared `depends_on` graph. |
| 5   | Lane Assignment         | 10%    | 4   | 4      | 0.40     | All Heavy. Schema enum, validate scope, audit OR, ARB canonical command extension all trigger Heavy per `cli.md` and `gate5-runbook-code-covenant.md`. |
| 6   | Scope Discipline        | 10%    | 4   | 4      | 0.40     | Six explicit non-goals (toolchain, content-injection, additional sensitivity values, separation-of-duties, allow-list expiry, lane/kind axes). |
| 7   | Evidence Requirements   | 10%    | 4   | 4      | 0.40     | Per-OBPI verification commands now align with per-behavior REQs (e.g. `gz validate --sensitivity --explain` for OBPI-03; `gz obpi complete` walkthrough fixture for OBPI-05). |
| 8   | Architectural Alignment | 10%    | 4   | 4      | 0.40     | Mirrors ADR-0.0.18 OR-pattern at `_requires_human_obpi_attestation`; reuses GHI #290 TTY+ATTEST closure as the precedent for the new walkthrough; module paths enumerated in Decision and now in per-OBPI Allowed Paths. |

WEIGHTED TOTAL: 4.00 / 4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores (Manual, post-revision) ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|--------------|-------------|-------|------|---------|-----|
| 01 schema-frontmatter-field        | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 02 security-surface-registry       | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 03 validate-sensitivity-scope      | 4 | 4 | 4 | 2 | 4 | 3.6 |
| 04 requires-security-review-attestation | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 05 gate5-walkthrough-arb-slot      | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 06 rule-file-matrix-scorecard      | 4 | 4 | 4 | 3 | 4 | 3.8 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

OBPI score rationale (concrete evidence, post-revision):

- **Independence (4 across all):** `depends_on:` declared in frontmatter
  matches the ADR's documented parallelism. OBPI-01 and OBPI-02 are
  parallel-roots; downstream briefs declare exact predecessor sets.
- **Testability (4 across all):** Every brief now carries 5-7 REQ-derived
  per-behavior acceptance criteria. Each REQ names a specific given/when/then
  with observable outcome (schema accept/reject, function return value,
  CLI exit code, output shape). Per `.claude/rules/tests.md` Invariant 6f,
  REQs assert semantics, not strings.
- **Value (4 across all):** Removing any of the 6 leaves a visible
  capability gap — schema field, registry data, validator, audit OR,
  walkthrough, rule file are each independently necessary for the
  doctrine's mechanical closure.
- **Size:**
  - OBPI-02 = 4 — registry data file + JSON schema fragment + small
    Pydantic model is a focused 1-2 day unit.
  - OBPI-01, 04, 05, 06 = 3 — solid 1-3 day units, with OBPI-06's
    sync-mirror discipline pushing toward 4.
  - **OBPI-03 = 2** — `validate_sensitivity_binding` + CLI registration +
    `--explain` subform + `--json` output + `gz validate --all` and
    `gz check` integration is closer to 4-5 days. Candidate for a future
    split (OBPI-03a: validator + flag; OBPI-03b: `--explain` subform +
    composite-command integration). Scoring at 2 because the framework
    says "too large or too small"; not blocking GO at average 3.6.
- **Clarity (4 across all):** Allowed Paths now match each brief's
  Objective; Requirements are brief-scoped; Acceptance Criteria are
  REQ-derived. Two agents reading any brief would produce similar
  implementations.

--- Red-Team Challenges ---

Not run (no `--red-team` flag specified in this evaluation). Recommended
before promotion to Proposed if the operator wants stronger adversarial
review. The structural integrity is now sufficient that red-teaming
would test substantive content rather than skeleton defects.

--- Overall Verdict ---

[X] GO — ADR weighted total 4.00; all OBPIs >= 3.6; no dimension at 1.
    Ready for proposal/defense review.
[ ] CONDITIONAL GO
[ ] NO GO

ACTION ITEMS (advisory, non-blocking)
-------------------------------------

1. **Consider splitting OBPI-03.** Size scored 2 because `validate_sensitivity_binding`
   + CLI flag registration + `--explain` subform + `--json` output +
   `gz validate --all` and `gz check` integration is a 4-5 day unit.
   Operator may accept as-is or split into:
   - **OBPI-03a:** `validate_sensitivity_binding` + `--sensitivity` flag +
     `--json` output + integration into `gz validate --all` + `gz check`.
   - **OBPI-03b:** `--explain ALLOWED_PATHS_LIST` subform (the 2am-operator
     predictive-classification valve) — independently shippable.
   - The split is structural improvement, not a blocker; current size 2
     produces average 3.6, well above the 3.0 floor.
2. **Run `/gz-adr-evaluate ADR-0.0.22 --red-team`** if stronger adversarial
   review is desired before proposal/defense.

History
-------

- 2026-04-28 (initial CLI run): GO, 3.55 / 4.0 — accepted by CLI, but
  manual review surfaced structural defects in the OBPI briefs
  (duplicated Requirements, non-specific Allowed Paths, boilerplate
  Acceptance Criteria, missing dependency graph).
- 2026-04-28 (manual override): CONDITIONAL GO — 6 action items recorded.
- 2026-04-28 (post-revision): GO, manual 4.00 / 4.0 — all six action
  items closed; CLI re-run shows 3.70 / 4.0; manual review confirms the
  briefs are now ready for promotion.
