---
mode: CREATE
adr_id: ADR-0.0.74
obpi_id: OBPI-0.0.74-03-mx-gate5-invariants
branch: main
timestamp: "2026-06-22T11:35:00+00:00"
agent: claude-code
session_id: main-2026-06-22
last_lock_event_timestamp: "2026-06-22T11:29:29+00:00"
last_commit_sha: 1651f27dc3a5ff0662a76d514422bdd450be277a
---

# OBPI-0.0.74-03 Completion Handoff

## Current State Summary

OBPI-0.0.74-03 is completed and operator-attested. The never-relax floor now
lands as a code constant: `GATE5_INVARIANTS` lives at `src/gzkit/mx/invariants.py`
as a five-member frozenset — faked Gate-5 attestation, secrets, operator-PII,
ledger integrity, and grader-gaming. `checkpoint.py` imports the canonical
constant instead of defining a local four-member set, so the never-relax list
lives in exactly one place. The lock is released and pipeline markers are cleared.

## Important Context

grader-gaming is the fifth member, named here per ADR-0.0.74 Decision item 3 and
Boundary Invariants #3. Its floor membership is made live (not merely named) by
OBPI-0.0.74-13's proxy-reality detector per the section-5 enforcement-claim rule.
The leveled checkpoint pins every member to CRITICAL (`Route.AOG_MX_HANGAR`) in
or out of the hangar; no marker, lane, or sensitivity can downgrade a member.

## Decisions Made

- Authored `GATE5_INVARIANTS` in a dedicated `invariants.py` rather than leaving
  it embedded in `checkpoint.py` — one canonical home for the never-relax list.
- Refactored `checkpoint.py` to import the constant, preserving all resolve and
  is_advisory logic unchanged; existing `test_checkpoint.py` continues to pass.
- Stage-5 brief-reconcile flagged allowlist drift: the REQ tests import
  `gzkit.mx.marker` (active-hangar fixture for REQ-02) and the `gzkit.mx`
  package. Amended the brief allowlist to declare `src/gzkit/mx/__init__.py` and
  `src/gzkit/mx/marker.py` as test-fixture reads, matching the identical
  OBPI-0.0.74-02 precedent (same two paths, same reconcile annotation).

## Immediate Next Steps

- Complete git-sync (commit was made locally; push pending validator green).
- Run `uv run gz obpi reconcile OBPI-0.0.74-03-mx-gate5-invariants` to confirm
  receipt and brief agree.
- Refresh the parent ADR view via `uv run gz adr status ADR-0.0.74 --json`.

## Pending Work / Open Loops

Parent ADR-0.0.74 (MX Mode Maintenance Hangar) remains in progress. Per the
Build-to-1.0 campaign Movement I, the topmost remaining MX work includes:

- OBPI-0.0.74-09 — gates-as-sensors: migrate live guards to emit `GZ_<LEVEL>`
  through `checkpoint.resolve` (currently zero production callers) and retire the
  two hand-set staging flags so Boundary Invariant 2's second half holds.
- OBPI-0.0.74-13 — the proxy-reality detector that makes grader-gaming's floor
  membership live (this OBPI named the membership; 13 makes it compliant).
- MX lean kernel plus hardening, then release 0.29.0.

Resume from the campaign's topmost unchecked item whose gate is met; the campaign
governs the pull order, not this handoff.

## Verification Checklist

- Gate 1 (ADR): intent recorded, parent ADR item 3 quoted.
- Gate 2 (TDD): RED then GREEN cycle; 8 tests in `tests/mx/test_gate5_invariants.py`.
- Gate 3 (Docs): `mkdocs build --strict` clean.
- Gate 5 (Human): operator-verbatim conversational attestation accepted.
- Full suite 6394 of 6394 pass; lint clean; typecheck clean.
- REQ coverage: REQ-01 and REQ-02 BEHAVIOR (test-covered); REQ-03 STRUCTURAL-FENCE
  (parent ADR Boundary Invariants #3).

## Evidence / Artifacts

- Unittest receipt: `arb-step-unittest-bfe6514e169e4802af5f8c0525c7c6b1`
- Lint receipt: `arb-ruff-95815aa7e71245a08bbb102886b180f6`
- Typecheck receipt: `arb-step-typecheck-5310eaf4ca3a405a8827727e63be23f8`
- Docs receipt: `arb-step-mkdocs-9757904e3dca481eba2b567f76bb3e29`
- Files: `src/gzkit/mx/invariants.py` (new), `src/gzkit/mx/checkpoint.py` (import),
  `tests/mx/test_gate5_invariants.py` (new, 8 tests).
- Base commit: 1651f27dc3a5ff0662a76d514422bdd450be277a
