---
id: OBPI-0.41.0-03-attestation-enrichment-tdd-integration
parent: ADR-0.41.0
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.41.0-03: Attestation-Enrichment TDD Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/ADR-0.41.0-tdd-emission-and-graph-rot-remediation.md`
- **Checklist Item:** #3 — "Attestation-enrichment rule integration accepting TDD event citations"

**Status:** Draft

## Objective

Update `.gzkit/rules/attestation-enrichment.md` so the receipt-ID requirement accepts `tdd_red_observed` and `tdd_green_observed` event IDs as valid citations for Gate 2 TDD claims. Add a new `gz validate` check that enforces the citation pattern when a Heavy-lane attestation claims Gate 2. This OBPI is the *policy* layer — OBPI-01 provides the events, OBPI-02 emits them, this OBPI makes them load-bearing in attestation.

## Lane

**Heavy** — changes the attestation enrichment rule, which governs how agents populate commit trailers and OBPI attestation text for every lane. Downstream effect on all future attestations.

## Allowed Paths

- `.gzkit/rules/attestation-enrichment.md` — canonical rule update
- `src/gzkit/commands/validate_cmd.py` — add `_validate_tdd_citations()` check
- `src/gzkit/cli/parser_maintenance.py` — register `--tdd-citations` flag
- `tests/commands/test_validate_cmds.py` — extend test suite
- `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/obpis/OBPI-0.41.0-03-attestation-enrichment-tdd-integration.md` — this brief

## Denied Paths

- `src/gzkit/events.py` / `src/gzkit/commands/tdd.py` — OBPIs 01 and 02
- `.claude/rules/**` — generated mirrors (regenerated via `gz agent sync`)
- `docs/user/commands/tdd.md` — OBPI-04 owns manpage
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. `.gzkit/rules/attestation-enrichment.md` lists `tdd_red_observed` and `tdd_green_observed` event IDs as a valid receipt class alongside ARB receipts in the "Receipt-ID Requirement" table.
2. The rule explains that Heavy-lane Gate 2 attestations that cite TDD events without matching RED→GREEN pairs are rejected.
3. The rule documents the citation format: `(tdd: red=<red-event-id> green=<green-event-id>)`.
4. A new `gz validate --tdd-citations <adr-id>` check scans OBPI attestation text under the named ADR and flags any Gate 2 attestation claim that lacks either a TDD event citation OR an ARB receipt citation.
5. The `gz validate --tdd-citations` check reads the ledger to verify cited event IDs actually exist and their `req_id` matches the OBPI's REQs.
6. Tests cover: rule file contains the new section, `gz validate --tdd-citations` detects missing citations, `gz validate --tdd-citations` detects citations whose event IDs don't match the ledger.
7. The generated `.claude/rules/attestation-enrichment.md` mirror is regenerated via `gz agent sync control-surfaces` and passes `gz validate --surfaces`.

## Discovery Checklist

**Governance:**

- [ ] `.gzkit/rules/attestation-enrichment.md` — current rule state
- [ ] `AGENTS.md` — Gate Covenant, DO IT RIGHT section

**Context:**

- [ ] OBPI-0.41.0-01 (event types) and OBPI-0.41.0-02 (CLI) must be complete
- [ ] `src/gzkit/commands/validate_cmd.py` — existing validate scope patterns (see `_validate_requirements`, `_validate_commit_trailers` from GHI-160 Phase 6)

**Prerequisites:**

- [ ] OBPIs 01 and 02 Completed

**Existing code:**

- [ ] The Phase 6 validate checks from GHI-160 are the closest precedent — read `_validate_requirements` and `_validate_commit_trailers` in `validate_cmd.py`.

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded

### Gate 2: TDD

- [ ] Per-REQ RGR cycle using `gz tdd` (OBPI-02 is complete by this point)

### Gate 3: Docs (Heavy)

- [ ] Docs build passes

### Gate 4: BDD (Heavy)

- [ ] BDD scenarios pass (or explicitly n/a if no new BDD scope)

### Gate 5: Human (Heavy)

- [ ] Attestation at ADR closeout

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.commands.test_validate_cmds -v
uv run gz agent sync control-surfaces
uv run gz validate --surfaces
uv run gz validate --tdd-citations ADR-0.41.0
```

## Acceptance Criteria

- [ ] REQ-0.41.0-03-01: Given `.gzkit/rules/attestation-enrichment.md`, when read, then the Receipt-ID Requirement table lists `tdd_red_observed` and `tdd_green_observed` as valid Gate 2 receipt classes.
- [ ] REQ-0.41.0-03-02: Given `.gzkit/rules/attestation-enrichment.md`, when read, then the citation format `(tdd: red=<id> green=<id>)` is documented with at least one worked example.
- [ ] REQ-0.41.0-03-03: Given `gz validate --tdd-citations <adr-id>`, when invoked on an ADR whose OBPI attestations cite no TDD events and no ARB receipts for a Gate 2 claim, then the check flags the OBPI with a validation error.
- [ ] REQ-0.41.0-03-04: Given `gz validate --tdd-citations <adr-id>`, when invoked on an OBPI that cites a TDD event ID not present in the ledger, then the check flags the citation as unresolved.
- [ ] REQ-0.41.0-03-05: Given `gz validate --tdd-citations <adr-id>`, when invoked on an OBPI that cites a TDD event whose req_id does not belong to the OBPI's REQ list, then the check flags the mismatch.
- [ ] REQ-0.41.0-03-06: Given an OBPI with valid TDD citations, when `gz validate --tdd-citations` runs, then exit code is 0.
- [ ] REQ-0.41.0-03-07: Given the regenerated `.claude/rules/attestation-enrichment.md` mirror, when `gz validate --surfaces` runs, then no drift is reported.

## Completion Checklist

- [ ] Gate 1/2/3/4/5 recorded
- [ ] Code Quality clean
- [ ] Evidence filled

## Evidence

### Value Narrative

Before this OBPI: attestation enrichment accepted ARB receipts but had no channel for verified TDD evidence. After this OBPI: Heavy-lane Gate 2 claims must cite either ARB receipts OR TDD events (or both), and `gz validate --tdd-citations` enforces the chain by reading the ledger.

### Implementation Summary

- Files modified:
- Tests added:
- Date completed:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: at ADR closeout
- Date: n/a

---

**Brief Status:** Draft

**Date Completed:** -
