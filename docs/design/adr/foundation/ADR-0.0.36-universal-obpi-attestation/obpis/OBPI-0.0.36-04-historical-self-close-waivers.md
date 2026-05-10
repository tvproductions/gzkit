---
id: OBPI-0.0.36-04-historical-self-close-waivers
parent: ADR-0.0.36-universal-obpi-attestation
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.36-04-historical-self-close-waivers: Historical Self-Close Waivers

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/ADR-0.0.36-universal-obpi-attestation.md`
- **Checklist Item:** #4 — "`data/historical_self_close_waivers.json` enumeration + waiver-list validator integration"

**Status:** Draft

## Objective

Enumerate every pre-doctrine receipt in `.gzkit/ledger.jsonl` that carries one of the deprecated self-close shapes and would otherwise fail the new `gz validate --receipt-shape` scope, register them in `data/historical_self_close_waivers.json` keyed by receipt ID, and integrate the waiver list with the validator from OBPI-0.0.36-03 such that pre-cutoff receipts pass when waivered and the waiver list itself fail-closes any new entry whose `added_under` is not OBPI-0.0.36-04.

## Lane

**Heavy** — adds a load-bearing data artifact that the validator from OBPI-03 reads on every run; the waiver schema is itself a contract closed by foundation doctrine. Errors in waiver authoring (missed receipts, malformed entries, schema drift) propagate to validator false positives or false negatives — both class-of-failure costs that justify the heavy-lane attestation rigor.

## Allowed Paths

- `data/historical_self_close_waivers.json` — new data artifact
- `src/gzkit/models/historical_waiver.py` — new Pydantic model module (`HistoricalAttestationWaiver`, `HistoricalAttestationWaiverFile`) per `.gzkit/rules/models.md`
- `src/gzkit/governance/trust_audits.py` — extend `_check_receipt_shape` (from OBPI-03) to consume the waiver list
- `tests/models/test_historical_waiver.py` — Pydantic model tests
- `tests/governance/test_historical_waiver_integration.py` — waiver-list-aware validator tests
- `docs/governance/historical-self-close-waivers.md` — narrative documentation of the waiver list, why it is closed to new entries, and the audit trail back to GHI #332

## Denied Paths

- `AGENTS.md` — doctrine surface owned by OBPI-0.0.36-01
- `src/gzkit/commands/adr_audit.py` — runtime gate is OBPI-0.0.36-02
- The validator scope flag registration (OBPI-0.0.36-03 owns; this OBPI extends the scope's behavior, not the flag's existence)
- `.gzkit/skills/**/SKILL.md`, `.claude/rules/**`, `.gzkit/rules/**` — skill/rule prose sweep is OBPI-0.0.36-05
- `.gzkit/ledger.jsonl` — never edit the ledger directly per AGENTS.md Behavior Rules — Never #2 (ledger is the *source* this OBPI scans, not the *destination* this OBPI writes)
- New runtime dependencies; CI files; lockfiles
- Any change to existing receipt fields (waiver list waives whole receipts; it does not patch them)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `data/historical_self_close_waivers.json` MUST conform to the `HistoricalAttestationWaiverFile` Pydantic model with `ConfigDict(frozen=True, extra="forbid")`. Schema fields: `waivers: list[HistoricalAttestationWaiver]`, where each entry has `receipt_id: str`, `obpi_id: str`, `deprecated_shape: str`, `rationale: str`, `added_under: str` (per parent ADR § Decision item #4 data model).
2. REQUIREMENT: Every receipt in `.gzkit/ledger.jsonl` dated before ADR-0.0.36's `date:` cutoff that carries `attestation_requirement: optional`, `obpi_completion: completed` without the `attested_` prefix, OR `attestor: ^agent:` MUST be enumerated in the waiver list. A receipt the validator would refuse but the waiver list does not include is a registration failure (under-enumeration); any waiver entry whose receipt does not match a real ledger event ID is a fabrication failure (over-enumeration). Neither is acceptable.
3. REQUIREMENT: The waiver list MUST be closed to new entries — the validator MUST refuse any waiver entry whose `added_under` field is not exactly `OBPI-0.0.36-04`. Future "waiver-extension" capability (if ever needed) requires its own ADR ceremony; this OBPI deliberately does not author that escape hatch.
4. REQUIREMENT: The validator from OBPI-0.0.36-03 MUST consume the waiver list when scanning pre-cutoff receipts. A receipt waivered in the list MUST pass; a receipt not waivered MUST emit a warning (not a fail-closed exit, per OBPI-03 REQ-05 — pre-cutoff receipts are fail-warn-only since the doctrine binds going forward).
5. REQUIREMENT: `docs/governance/historical-self-close-waivers.md` MUST document the waiver list, cite GHI #332 and ADR-0.0.36, explain the closed-to-new-entries posture, and link to the audit lineage. Documentation drift on a foundation doctrine surface is a Gate 3 failure.
6. REQUIREMENT: `tests/models/test_historical_waiver.py` MUST exercise the Pydantic model — frozen mutation refused, extra field refused, required-field absence refused. `tests/governance/test_historical_waiver_integration.py` MUST assert the validator-waiver interaction (waivered pre-cutoff passes; un-waivered pre-cutoff warns; un-waivered post-cutoff fails closed; bad `added_under` field on a waiver entry is itself rejected by the validator).

> STOP-on-BLOCKERS: if `.gzkit/ledger.jsonl` cannot be parsed (corrupt JSONL, missing file), halt and surface the parse error before authoring the waiver list — partial enumeration would silently waive the wrong set.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item #4 — quote verbatim into Implementation Summary** (the historical-receipt waiver list authoring).
- [ ] Parent ADR § Decision § Data model — the `HistoricalAttestationWaiver` Pydantic shape; copy the field set exactly.
- [ ] Parent ADR § Non-goals — confirm no retroactive re-attestation; waiver list documents drift, never rewrites.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/ADR-0.0.36-universal-obpi-attestation.md`

> **STOP:** If you cannot quote the parent ADR § Decision item #4 that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.claude/rules/models.md` — Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` for all data models; this waiver schema is the canonical exemplar
- [ ] `.gzkit/rules/governance-core.md` § non-negotiable rules — ledger is read, never written
- [ ] OBPI-0.0.36-03 brief — the validator surface this OBPI plugs into

**Context:**

- [ ] `.gzkit/ledger.jsonl` — full enumeration source; scan with `Read` (line by line) and a Python helper script that filters for the deprecated shapes
- [ ] GHI #332 audit findings — the concrete instance set the waiver list must cover; cross-reference receipts named in the audit
- [ ] `src/gzkit/models/` — existing Pydantic model module layout to match for the new waiver model

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/ledger.jsonl` exists and is parseable
- [ ] `src/gzkit/models/` directory exists
- [ ] OBPI-0.0.36-03 has landed (validator scope exists; this OBPI extends its behavior with waiver-list awareness)

**Existing Code (understand current state):**

- [ ] Existing Pydantic models under `src/gzkit/models/` — match field-style and module-import conventions
- [ ] Existing `data/` artifacts (other JSON data files, `data/behave_coverage_waivers.json` if present) — match file shape and indentation conventions
- [ ] `src/gzkit/governance/trust_audits.py::_check_receipt_shape` from OBPI-03 — read to understand the integration surface

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item #4 quoted in Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: `tests/governance/test_historical_waiver_integration.py::test_waivered_pre_cutoff_receipt_passes` fails before waiver list exists
- [ ] GREEN: same test passes after enumeration + integration
- [ ] Pydantic model tests assert frozen + extra-forbid semantics, not byte-level error strings
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/governance/historical-self-close-waivers.md` published and reachable from `docs/governance/state-doctrine.md` cross-references

### Gate 4: BDD (Heavy)

- [ ] Behave scenario tagged `@REQ-0.0.36-04-NN` covering: (a) waivered pre-cutoff receipt passes; (b) un-waivered pre-cutoff receipt warns; (c) waiver entry with bad `added_under` is rejected; behave passes

### Gate 5: Human (Universal under this very ADR)

- [ ] Human attestation recorded with TTY+ATTEST under `gz obpi complete`

## Verification

```bash
# Enumeration completeness — every pre-cutoff deprecated-shape receipt is in the waiver list
uv run python -c "
import sys, json, pathlib
sys.stdout.reconfigure(encoding='utf-8')
ledger = pathlib.Path('.gzkit/ledger.jsonl').read_text(encoding='utf-8').splitlines()
waiver = json.loads(pathlib.Path('data/historical_self_close_waivers.json').read_text(encoding='utf-8'))
waivered_ids = {w['receipt_id'] for w in waiver['waivers']}
print(f'Waivered receipts: {len(waivered_ids)}')
"

# Pydantic model tests
uv run -m unittest tests.models.test_historical_waiver -v

# Validator-waiver integration
uv run -m unittest tests.governance.test_historical_waiver_integration -v

# Validator end-to-end with the live waiver list
uv run gz validate --receipt-shape

# Standard quality gates
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/

# ARB receipts for Heavy-lane attestation
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Acceptance Criteria

- [ ] REQ-0.0.36-04-01: Given `data/historical_self_close_waivers.json` after this OBPI, when loaded by the `HistoricalAttestationWaiverFile` Pydantic model, then validation succeeds with no extra fields and the waiver list is non-empty (covers at least the GHI #332 audit set).
- [ ] REQ-0.0.36-04-02: Given `.gzkit/ledger.jsonl` and the waiver list after this OBPI, when every pre-cutoff receipt with a deprecated shape is cross-checked against the waiver list, then every such receipt is present (zero under-enumeration) and every waiver entry maps to a real ledger event ID (zero over-enumeration).
<!-- gz-validate-skip: brief-cross-references -->
- [ ] REQ-0.0.36-04-03: Given a waiver entry with `added_under: "OBPI-0.0.36-04"`, when `gz validate --receipt-shape` runs, then the entry is accepted; given a waiver entry with `added_under` set to anything else (including a future-OBPI ID like `OBPI-0.0.36-99`), when the validator runs, then the entry is rejected with exit 3 and stderr names the offending entry.
- [ ] REQ-0.0.36-04-04: Given a pre-cutoff receipt covered by a waiver entry, when `gz validate --receipt-shape` runs, then the receipt passes silently. Given a pre-cutoff receipt with a deprecated shape but no matching waiver entry, when the validator runs, then a warning is emitted (no fail-closed exit), naming the receipt ID and the missing-waiver class of failure.
- [ ] REQ-0.0.36-04-05: Given `docs/governance/historical-self-close-waivers.md` after this OBPI, when read, then it documents the waiver list's purpose, cites GHI #332 and ADR-0.0.36, explains the closed-to-new-entries posture, and links from `docs/governance/state-doctrine.md` cross-references.
- [ ] REQ-0.0.36-04-06: Given the `HistoricalAttestationWaiver` model after this OBPI, when an instance is mutated post-construction, then a Pydantic frozen-mutation error is raised; when an instance is constructed with an extra field, then an extra-forbidden error is raised; when a required field is omitted, then a required-field error is raised.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; Decision item #4 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle followed; assertions are REQ-derived semantics
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** mkdocs --strict clean; waiver doc published and cross-linked
- [ ] **Gate 4 (BDD):** behave scenarios tagged `@REQ-0.0.36-04-NN` and passing
- [ ] **Gate 5 (Human):** TTY+ATTEST attestation recorded
- [ ] **Value Narrative:** Documented below
- [ ] **Key Proof:** Concrete enumeration completeness + validator integration evidence below

> Universal attestation rule applies under ADR-0.0.36; Gate 5 fires regardless of lane.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste RED + GREEN test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs --strict output here; link to historical-self-close-waivers.md
```

### Gate 4 (BDD)

```text
# Paste behave output for tagged scenarios here
```

### Gate 5 (Human)

```text
# Record attestation text + TTY+ATTEST receipt here
```

### Value Narrative

Before this OBPI, ledger immutability and the new validator from OBPI-03 were in tension: a fail-closed validator over the entire ledger would refuse historical receipts the doctrine cannot retroactively re-attest. After this OBPI, the waiver list resolves the tension — pre-cutoff drift is preserved as documented historical fact (auditable, dated, bounded) while the doctrine binds going forward. The waiver list itself is closed to new entries via the `added_under` constraint, so future agents cannot extend the waiver mechanism into a new vibing surface.

### Key Proof

```bash
$ uv run gz validate --receipt-shape
WARNING: 0 historical receipts un-waivered (all pre-cutoff drift accounted for)
OK: 0 post-cutoff violations
$ echo $?
0

$ python -c "import json; w = json.load(open('data/historical_self_close_waivers.json')); print(len(w['waivers']), 'waivers registered')"
N waivers registered
```

### Implementation Summary

- Files created/modified: `data/historical_self_close_waivers.json` (new), `src/gzkit/models/historical_waiver.py` (new), `src/gzkit/governance/trust_audits.py` (extend `_check_receipt_shape` to consume waivers), `docs/governance/historical-self-close-waivers.md` (new), `tests/models/test_historical_waiver.py` (new), `tests/governance/test_historical_waiver_integration.py` (new)
- Tests added: Pydantic frozen/extra-forbid/required-field assertions; waiver-list integration RED→GREEN; bad-`added_under` rejection
- Date completed: TBD
- Attestation status: pending TTY+ATTEST under universal attestation rule
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb` (universal under ADR-0.0.36)
- Attestation: substantive attestation text recorded at completion
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
