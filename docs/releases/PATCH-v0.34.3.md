# Patch Release: v0.34.3

**Date:** 2026-08-12
**Previous Version:** 0.34.2
**Tag:** v0.34.2

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 681 | sync_surfaces: generated surfaces written CRLF on Windows (no newline pin) | qualified |  |
| 781 | chores advise: exits 0 while its own output reports FAIL | qualified |  |
| 782 | hardcoded-root-eradication: compliance comment counted as violation | diff_only | GHI #782 has commits touching src/gzkit/ but no 'runtime' label |
| 783 | chores: runtime_state proofs ship in the wheel and --distribution cannot see them | qualified |  |
| 784 | OBPI-0.35.0-02: brief omits sensitivity over a ledger_integrity overlap | excluded |  |
| 785 | gates: no mechanism asks which gates have no automatic caller | qualified |  |
| 786 | critic ADR: R4's built-in transport reviews diffs, not decisions | excluded |  |
| 787 | gz check: _build_check_steps' coupling checklist names 4 obligations, 8 are required | qualified |  |
| 788 | typecheck: --exclude features/** never matches on Windows, so 25 diagnostics reach the gate | qualified |  |
| 790 | handoff lineage: continues_from is single-valued, so a merged chain inherits one parent's rulings | qualified |  |
| 791 | surface-weight: recalibration event has no producer in any gz verb | qualified |  |
| 792 | surface-weight: band constants can drift from their witnessing event | qualified |  |
| 793 | enforcement-floor: preflight NC reports a false FACADE when colour is forced | qualified |  |
| 794 | patch-release: a chore(...)-closed GHI is never enumerated, in any bucket | open_upstream | GHI #794 qualifies on commit markers but is still OPEN upstream; confirm this release closes it before counting it |

## Operator Approval

Approved by gz patch release
