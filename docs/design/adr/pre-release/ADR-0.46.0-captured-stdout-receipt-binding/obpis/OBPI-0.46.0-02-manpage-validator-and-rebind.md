---
id: OBPI-0.46.0-02-manpage-validator-and-rebind
parent: ADR-0.46.0-captured-stdout-receipt-binding
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.46.0-02-manpage-validator-and-rebind: `--manpage-examples` validator + rebind tool

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.46.0-captured-stdout-receipt-binding/ADR-0.46.0-captured-stdout-receipt-binding.md`
- **Checklist Item:** #2 — "Implement `gz validate --manpage-examples` scope; parse EXAMPLES blocks, locate receipt-citation comments, hash-match against captured stdout; heavy-lane fail-closed, lite-lane warn-only; `gz arb rebind-manpage <path>` rebind tool"

**Status:** Draft

## Objective

Author the validator that parses manpage EXAMPLES blocks, locates adjacent `<!-- bound to receipt arb-step-… -->` citation comments, and hash-matches the EXAMPLES content against the receipt's captured stdout. Author the rebind tool that runs the cited command and rebinds the manpage.

## Lane

**Heavy** — New validate scope and new CLI verb.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — `validate_manpage_examples`
- `src/gzkit/cli/parser_artifacts.py` — register `--manpage-examples` flag
- `src/gzkit/commands/arb_rebind.py` (new) — `gz arb rebind-manpage <path>` verb
- `tests/governance/test_manpage_examples.py`
- `tests/commands/test_arb_rebind.py`
- `data/manpage_example_waivers.json` — corpus-freeze waiver list
- `docs/design/adr/pre-release/ADR-0.46.0-captured-stdout-receipt-binding/**`

## Denied Paths

- `src/gzkit/arb/**` — owned by OBPI-01
- `docs/user/manpages/**` — corpus sweep happens in OBPI-03
- `features/**` — BDD coverage in OBPI-03
- Any path not listed

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: New function `validate_manpage_examples(manpage_paths: Iterable[Path]) -> ValidationResult`.
2. REQUIREMENT: For each manpage, parse for fenced code blocks within an `## EXAMPLES` section. For each fenced block, look for an adjacent HTML comment of form `<!-- bound to receipt <receipt-id> -->` (immediately preceding or following).
3. REQUIREMENT: For each bound block, look up the receipt in `.gzkit/ledger.jsonl`, read the captured stdout from the receipt's `captured_stdout_path`, and assert SHA-256 of the fenced block content (with leading/trailing newline normalization) equals the receipt's `captured_stdout_hash`.
4. REQUIREMENT: Heavy-lane manpages (registered via `parser_artifacts.py` for a real CLI verb) require receipt binding: unbound EXAMPLES block in heavy-lane manpage = exit 3.
5. REQUIREMENT: Lite-lane manpages or manpages catalogued in `data/manpage_example_waivers.json` are advisory: unbound block = warn-only.
6. REQUIREMENT: New CLI verb `gz arb rebind-manpage <manpage-path>` parses the EXAMPLES blocks, runs each cited command (or prompts for the command if no comment exists), captures via `gz arb step --capture`, and writes the new binding comment + content into the manpage.
7. REQUIREMENT: Rebind is interactive — TTY confirmation required per binding. Headless mode produces a dry-run report.
8. REQUIREMENT: Tests cover: bound block with matching hash → exit 0; bound block with hash mismatch → exit 3; unbound heavy-lane block → exit 3; unbound waivered block → exit 0 with warn; rebind tool runs cited command and updates manpage; rebind in headless mode is dry-run only.
9. REQUIREMENT: Tests use `tempfile`-backed manpage and ledger fixtures.
10. REQUIREMENT: Each test decorated with `@covers(REQ-0.46.0-02-NN)`.
11. REQUIREMENT: NEVER include the operator's personal email.
12. REQUIREMENT: TDD discipline.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (capture fields and proofs storage do not exist), STOP.

## Discovery Checklist

- [ ] Parent ADR § Decision items 3, 4
- [ ] OBPI-0.46.0-01 evidence — confirm capture flag and receipt fields stable
- [ ] `docs/user/manpages/<existing>.md` — read existing EXAMPLES block format
- [ ] `src/gzkit/governance/trust_audits.py` — existing validator shape
- [ ] `.claude/rules/cli.md` — heavy-lane vs lite-lane manpage scope

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
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_manpage_examples.py tests/commands/test_arb_rebind.py -v
# Smoke
uv run gz validate --manpage-examples
```

## Acceptance Criteria

- [ ] REQ-0.46.0-02-01: Given a manpage with a bound EXAMPLES block whose content hash matches the receipt's captured-stdout hash, when `gz validate --manpage-examples` runs, then exit 0.
- [ ] REQ-0.46.0-02-02: Given a manpage with a bound block whose hash mismatches, when the validator runs, then exit 3.
- [ ] REQ-0.46.0-02-03: Given an unbound EXAMPLES block in a heavy-lane manpage, when the validator runs, then exit 3.
- [ ] REQ-0.46.0-02-04: Given an unbound block in a manpage catalogued in the waiver list, when the validator runs, then exit 0 with a warning.
- [ ] REQ-0.46.0-02-05: Given `gz arb rebind-manpage <path>` in a TTY, when invoked, then each cited command is run, captured, and the manpage block is rebound.
- [ ] REQ-0.46.0-02-06: Given the same in headless mode, when invoked, then a dry-run report is produced and no manpage edits occur.

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
