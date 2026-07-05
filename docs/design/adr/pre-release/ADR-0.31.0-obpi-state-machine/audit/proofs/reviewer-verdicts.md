# Independent Reviewer Verdicts — ADR-0.31.0 Audit (2026-07-05)

## spec-reviewer (independent REQ-coverage trace) — CONCERNS→resolved

- 18/18 REQs verified; no fabricated or tautological BEHAVIOR proof found under targeted hunting.
- REQ-0.31.0-03-03 (landing falsifier): GENUINELY SEMANTIC — constructs the GHI #348 drift,
  asserts monitor refusal via pre/post SHA-256 hash equality; "if the monitor hookup were
  reverted... both assertions would fail." → the covers-backfill heuristic fix (GHI #667)
  corrected a false-positive, did NOT launder a cosmetic test.
- 7 non-@covers REQs (01-06, 02-04/05/06, 03-04/05/06) all correctly SUPPORT/STRUCTURAL-FENCE.
- Surfaced the sibling-path monitor bypass (corroborating quality-reviewer).

## quality-reviewer (independent structural coherence) — FINAL: COHERENT

- Pass 1: BRITTLE — monitor wired only into reconcile_frontmatter; auto_fix_obpi_brief_frontmatter
  (gz attest/closeout/obpi reconcile) bypassed it → GHI #348 class reproducible. [→ GHI #668]
- Pass 2 (after closeout_form fix): still BRITTLE — found gz obpi complete (obpi_complete.py) as a
  3rd unguarded writer. [→ full class-fix]
- Pass 3 (FINAL, commit 7fb44884): COHERENT. Independently swept all _upsert/write_text/rewrite
  callers; every governed OBPI-status writer now consults the single obpi_status_is_terminal
  predicate (sourced from OBPI-01's OBPIState/OBPI_STATES model). No remaining uncovered writer.
  Central-chokepoint design sound. GHI #348 class closed at the integration level.
- Residual (info, non-blocking): writer-coverage is convention-enforced, not mechanically enforced
  → tracked as GHI #669 (Promotable hardening); explicitly "not a gate on this ADR."
