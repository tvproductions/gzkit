ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.33-agent-control-surface-fidelity
Evaluator: gz-adr-evaluate skill (manual pass superseding CLI pre-screen)
Date: 2026-05-15
Revision: post-improvement (action items from initial evaluation resolved)

---

## CLI Pre-Screen (for traceability)

Initial (pre-improvement):
```
ADR Eval: ADR-0.0.33 -- GO
  Weighted total: 3.45/4.0
  OBPIs scored: 5
```

Post-improvement:
```
ADR Eval: ADR-0.0.33 -- GO
  Weighted total: 3.70/4.0
  OBPIs scored: 5
```

CLI bumped D4 (OBPI Decomposition) 3→4 and D8 (Architectural Alignment) 3→4
after the OBPI Allowed Paths, Requirements narrowing, and ADR anti-patterns
section were authored.

---

## Part 1: ADR Quality Dimensions

| # | Dimension | Weight | CLI Score | Manual Score | Weighted | CLI Reconciliation |
|---|-----------|--------|-----------|--------------|----------|--------------------|
| 1 | Problem Clarity | 15% | 3 | 3 | 0.45 | Agreed: before-state is implicit ("Today's gzkit cannot answer that question structurally"); the prose is comprehensible but doesn't carry an explicit "Before X / After Y" headline in Intent. Stylistic, not structural. |
| 2 | Decision Justification | 15% | 3 | **4** | **0.60** | CLI false negative (persistent): heuristic looks for rationale language in Decision section header only; rationale is fully argued in Alternatives Considered (4 named alternatives A–D, each with a specific rejection reason citing DO IT RIGHT #1, substrate-invariance, and architectural-layer mismatch) and woven through the Decision body. Manual override stands. |
| 3 | Feature Checklist | 15% | 4 | 4 | 0.60 | Confirmed: 5 items, each maps to a named validator command; consistent granularity. |
| 4 | OBPI Decomposition | 15% | 4 | 4 | 0.60 | **Improved from 3→4 (CLI) and 2→4 (manual).** Each OBPI now scopes a distinct implementation module under `src/gzkit/governance/trust_audits/<scope>.py`; Requirements narrowed to the single invariant each brief implements; OBPI-05 declares its sequential dependency on 01–04 with predecessor symbol names. |
| 5 | Lane Assignment | 10% | 4 | 4 | 0.40 | Confirmed: all 5 OBPIs add new `gz validate --<scope>` commands; Heavy is correct. |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | Confirmed: behavioral fidelity explicitly deferred; alternatives C and D name and reject spot-fixing and wait-for-substrate; non-goals argued. |
| 7 | Evidence Requirements | 10% | 4 | 4 | 0.40 | Confirmed: test file names, validator module paths, and data file paths all specified. |
| 8 | Architectural Alignment | 10% | 4 | 4 | 0.40 | **Improved from 3→4.** Anti-Patterns section now names six explicit failure shapes (un-wired scope, edit-without-revalidate, silent band recalibration, ignored Era-1 advisory, lift-without-back-pointer, `--no-verify` bypass). Local exemplars (`validate_advisor_proof_binding`, `--reconcile-freshness` fail-open pattern) referenced in OBPI briefs. |

**Manual Weighted Total: 3.85/4.0**

(CLI weighted total: 3.70/4.0. Divergence is the single D2 false-negative the
CLI heuristic cannot detect.)

---

## Part 2: OBPI Quality Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg | Notes |
|------|-------------|-------------|-------|------|---------|-----|-------|
| OBPI-0.0.33-01 bullet-retention-validator | 4 | 4 | 4 | 4 | 4 | **4.0** | Allowed Paths concrete (`bullet_retention.py`, `__init__.py`, `parser_maintenance.py`, test file, manpage); Requirements narrowed to Invariant 1; 5 specific REQ IDs with given/when/then semantics. |
| OBPI-0.0.33-02 surface-weight-validator | 4 | 4 | 3 | 3 | 4 | **3.6** | Concrete Allowed Paths including `data/surface_weight_floor.json` and `data/surface_weight_waivers.json`; Requirements specify direction-binding, waiver schema, ledger event, exit code discipline. Size 3: snapshot + waiver schema + ledger-event drift detection is at the upper edge of 1–3 days. Value 3: weight regression is less critical than retention. |
| OBPI-0.0.33-03 pointer-integrity-validator | 4 | 4 | 4 | 4 | 4 | **4.0** | Concrete Allowed Paths; Requirements specify forward anchor resolution, reverse back-pointer check, error-message format. |
| OBPI-0.0.33-04 scenario-reachability-validator | 4 | 4 | 3 | 4 | 4 | **3.8** | **Era-1 behavior now fully specified.** REQ-04-01 pins the registry-absent advisory line verbatim; REQ-04-02/03 pin Era-2 behavior with stubbed-registry test fixtures; REQ-04-04 pins fail-closed schema validation. Independence 4: dependency on ADR-0.0.34 is no longer ambiguous (validator works in both eras). Value 3: advisory-only Era 1 means removing it doesn't break CI. |
| OBPI-0.0.33-05 surface-fidelity-composite | 4 | 4 | 4 | 3 | 4 | **3.8** | Dependencies on OBPIs 01–04 now declared with predecessor symbol names. Allowed Paths include composite wiring, CLI registration, pre-commit config, manpage. Requirements specify exit-code aggregation, `gz check` integration, pre-commit cheap-subset wiring. Size 3: composite + check + pre-commit + tests at upper edge. |

**OBPI threshold: avg ≥ 3.0 per OBPI. No OBPI scores 1 on any dimension.**
All OBPIs pass with floor at 3.6.

---

## Improvement Delta (initial → post-improvement)

| Surface | Before | After |
|---------|--------|-------|
| ADR D4 OBPI Decomposition (manual) | 2 | 4 |
| ADR D8 Architectural Alignment | 3 | 4 |
| OBPI-01 Clarity | 2 | 4 |
| OBPI-02 Clarity | 2 | 4 |
| OBPI-03 Clarity | 2 | 4 |
| OBPI-04 Independence | 3 | 4 |
| OBPI-04 Testability | 3 | 4 |
| OBPI-04 Clarity | 2 | 4 |
| OBPI-05 Independence | 3 | 4 |
| OBPI-05 Clarity | 3 | 4 |
| ADR weighted total (manual) | 3.45 | **3.85** |
| ADR weighted total (CLI) | 3.45 | **3.70** |
| OBPI floor average | 3.0 | **3.6** |

---

## Divergences from CLI Pre-Screen (post-improvement)

| Dimension | CLI | Manual | Reason |
|-----------|-----|--------|--------|
| D2 Decision Justification | 3 | 4 | CLI false negative: heuristic looks for rationale in Decision section header only; rationale is in Alternatives Considered (4 specific rejections). Persistent across both evaluations — known CLI limitation. |

All other dimensions and OBPI scores now agree with the CLI.

---

## Verdict

| Check | Result |
|-------|--------|
| ADR weighted total | 3.85 ≥ 3.0 (manual) / 3.70 ≥ 3.0 (CLI) |
| Any ADR dimension = 1 | No |
| All OBPI averages ≥ 3.0 | Yes (floor: OBPIs 02 and 04 tied at 3.6) |
| Any OBPI dimension = 1 | No |
| Action items from prior evaluation | All P1 and P2 resolved; P3 (anti-patterns) also resolved |

**Overall Verdict: GO**

ADR is structurally sound and ready for proposal/defense review. No remaining
blockers. The P3 anti-patterns improvement was completed alongside the P1/P2
fixes, lifting D8 to 4.

---

## Resolved Action Items

| Priority | Status | Scope | Resolution |
|----------|--------|-------|------------|
| P1 | ✅ Resolved | OBPI-01..04 Allowed Paths | Each OBPI now lists `src/gzkit/governance/trust_audits/<scope>.py`, `__init__.py`, `parser_maintenance.py`, the test file, and manpage. |
| P1 | ✅ Resolved | OBPI-01..05 Requirements | Each OBPI's Requirements section now scopes only the invariant that brief implements, with specific NEVER/ALWAYS bindings and exit-code discipline. |
| P1 | ✅ Resolved | OBPI-04 Era-1 behavior | REQ-04-01 pins the verbatim advisory line for registry-absent state; REQ-04-02/03/04 pin Era-2 behavior including schema-validation fail-close. |
| P2 | ✅ Resolved | OBPI-05 dependencies | New `## Dependencies` section names the four predecessor validators by OBPI ID and symbol name; Prerequisites section enforces existence. |
| P2 | ✅ Resolved | OBPI-05 Allowed Paths | Composite scope, CLI registration, pre-commit config, both relevant manpages now in scope. |
| P3 | ✅ Resolved | ADR anti-patterns | New `## Anti-Patterns` section in the ADR body names six specific failure shapes the validators are built to catch. |

---

## Remaining Stylistic Opportunities (non-blocking)

These do not affect the GO verdict and may be addressed at the operator's
discretion before proposal/defense, or deferred:

1. **D1 Problem Clarity → 4**: Restructure the Intent paragraph to lead with an
   explicit before/after headline (e.g., "Before: silently-missing rules are
   invisible to PRIME DIRECTIVE / DO IT RIGHT / anti-vibing mantra. After:
   drift in the rendered surface is detectable at compile time."). The content
   is present; only the formatting would change.
2. **OBPI-02 and OBPI-05 Size 3→4**: Consider whether the waiver-schema +
   ledger-event work (02) or composite + pre-commit + check (05) should split
   further. Current sizing is defensible; this is a judgment call on
   implementation cadence.
