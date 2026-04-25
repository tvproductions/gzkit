---
id: OBPI-0.46.0-01-receipt-schema-and-capture
parent: ADR-0.46.0-captured-stdout-receipt-binding
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.46.0-01-receipt-schema-and-capture: Receipt schema + `--capture` flag

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.46.0-captured-stdout-receipt-binding/ADR-0.46.0-captured-stdout-receipt-binding.md`
- **Checklist Item:** #1 — "Extend ARB receipt schema with optional `captured_stdout_path` / `captured_stdout_hash` / `captured_stderr_*` fields; implement `gz arb step --capture` opt-in flag with `.gzkit/proofs/<receipt-id>/` storage"

**Status:** Draft

## Objective

Extend the ARB receipt Pydantic model with optional captured-stdout/stderr fields and implement `gz arb step --capture` to write captured bytes under `.gzkit/proofs/<receipt-id>/` with SHA-256 hashing.

## Lane

**Heavy** — ARB receipt schema is a runtime contract.

## Allowed Paths

- `src/gzkit/arb/validator.py` — receipt model extension
- `src/gzkit/arb/middleware.py` — `--capture` flag + proofs storage
- `src/gzkit/arb/capture.py` (new) — capture and hash helpers
- `src/gzkit/schemas/arb_receipt.json` (or wherever the schema lives) — schema update
- `tests/arb/test_capture.py`, `tests/arb/test_receipt_schema.py`
- `.gitignore` — ensure `.gzkit/proofs/` is gitignored except for explicitly committed bound paths
- `docs/design/adr/pre-release/ADR-0.46.0-captured-stdout-receipt-binding/**`

## Denied Paths

- `src/gzkit/governance/trust_audits.py` — manpage-examples validator in OBPI-02
- `src/gzkit/commands/arb_rebind.py` — rebind tool in OBPI-02
- `features/**` — BDD coverage in OBPI-03
- Any path not listed

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: ARB receipt Pydantic model gains optional fields `captured_stdout_path`, `captured_stdout_hash`, `captured_stderr_path`, `captured_stderr_hash` (all `str | None`).
2. REQUIREMENT: `model_config = ConfigDict(frozen=True, extra="forbid")` preserved per `.claude/rules/models.md`.
3. REQUIREMENT: New `gz arb step --capture` flag (boolean, default False). When set, the wrapped command's stdout and stderr are captured to `.gzkit/proofs/<receipt-id>/stdout.txt` and `stderr.txt`, hashed (SHA-256), and the receipt is decorated with the path + hash fields.
4. REQUIREMENT: Capture is opt-in. Default `gz arb step` behavior (no `--capture`) does not write proofs and does not decorate the receipt.
5. REQUIREMENT: Captured files are written atomically (temp + rename) to avoid partial writes on interruption.
6. REQUIREMENT: `.gitignore` adds `.gzkit/proofs/*` with a `!.gzkit/proofs/.gitkeep` exception or similar to allow the directory to exist without committing all captures.
7. REQUIREMENT: Tests cover: `--capture` writes stdout and stderr files; SHA-256 hashes match file contents; receipt fields populate correctly; default mode does not write or decorate; large output (>10MB) does not break (streaming write).
8. REQUIREMENT: Tests use `tempfile`-backed proofs roots; NEVER write to the live `.gzkit/proofs/`.
9. REQUIREMENT: Each test decorated with `@covers(REQ-0.46.0-01-NN)`.
10. REQUIREMENT: NEVER include the operator's personal email.
11. REQUIREMENT: TDD discipline.

> STOP-on-BLOCKERS: if `.claude/rules/models.md` Pydantic conventions have changed, STOP and reconcile.

## Discovery Checklist

- [ ] Parent ADR § Decision items 1, 2, 5
- [ ] `.claude/rules/models.md` — Pydantic frozen + extra forbid
- [ ] `src/gzkit/arb/validator.py` — existing receipt model shape
- [ ] `src/gzkit/arb/middleware.py` — existing step wrapper
- [ ] `.gitignore` — existing patterns

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded
### Gate 2: TDD
- [ ] RGR; tests pass
### Code Quality
- [ ] Lint, type clean
### Gate 3: Docs (Heavy)
- [ ] In OBPI-03
### Gate 4: BDD (Heavy)
- [ ] In OBPI-03
### Gate 5: Human (Heavy)
- [ ] Required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/arb/test_capture.py tests/arb/test_receipt_schema.py -v
# Smoke
uv run gz arb step --capture --name smoke -- echo "captured!"
ls .gzkit/proofs/arb-step-smoke-*/
```

## Acceptance Criteria

- [ ] REQ-0.46.0-01-01: Given `gz arb step --capture --name X -- <cmd>`, when invoked, then the receipt has populated `captured_stdout_path` and `captured_stdout_hash` fields.
- [ ] REQ-0.46.0-01-02: Given the same invocation, when the captured file is read, then its SHA-256 matches the receipt's `captured_stdout_hash`.
- [ ] REQ-0.46.0-01-03: Given `gz arb step` without `--capture`, when invoked, then no proofs files are written and the receipt's capture fields are None.
- [ ] REQ-0.46.0-01-04: Given a wrapped command with large output (>10MB), when `--capture` is set, then capture completes without OOM and hash is correct.
- [ ] REQ-0.46.0-01-05: Given `.gitignore` updates, when `git status` is run after a capture, then proofs files do not appear unless explicitly added.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** RGR; tests pass
- [ ] **Code Quality:** clean
- [ ] **OBPI Acceptance:** Heavy = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD)
```text
# RGR + unittest output
```

### Code Quality
```text
# lint/typecheck output
```

### Gate 5 (Human)
```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy lane requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
