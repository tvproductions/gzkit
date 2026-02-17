---
id: ADR-0.2.0
status: Draft
semver: 0.2.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-01-29
---

# ADR-0.2.0: Gate Verification + Dry Run

## Intent

Make gate verification operational and dogfood-safe. The CLI must run gates with evidence and record results, and the core mutation commands must support `--dry-run` so humans can rehearse workflows without changing state.

## Decision

Implement the following changes:

1. **Gate verification commands**
   - Add `gz implement` to run Gate 2 (tests) and report results.
   - Add `gz gates` to run all gates required for the current lane (or a specific gate via `--gate`).
   - Use verification commands from `.gzkit/manifest.json` as the source of truth.
   - Record a `gate_checked` ledger event for each gate run (gate number, command, status, return code).
   - Exit non-zero when a required gate fails.

2. **Dry-run support for mutation commands**
   - Add `--dry-run` to: `gz init`, `gz prd`, `gz constitute`, `gz plan`, `gz specify`, `gz attest`, `gz sync`, `gz tidy`.
   - Dry-run prints intended actions and ledger events, but **does not** write files or append to the ledger.

3. **Documentation updates**
   - Document `gz implement` and `gz gates`.
   - Update existing command docs to include `--dry-run`.

## Consequences

### Positive

- Gate evidence is explicit, repeatable, and recorded.
- Humans can rehearse governance flows without modifying the repo (dogfooding).

### Negative

- Additional command surface increases maintenance burden.
- Dry-run paths add branching logic and require tests.

## OBPIs

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

1. Implement `gz implement` and `gz gates`, including `gate_checked` ledger events.
2. Add `--dry-run` to mutation commands listed above with no side effects.
3. Update user docs for new commands and `--dry-run` usage.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.2.0 | Pending | | | |
