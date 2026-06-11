---
id: OBPI-0.0.63-06-req-evidence-schema-consumption
parent: ADR-0.0.63-closeout-ceremony-runtime-engine-parity
item: 6
lane: Heavy
status: Completed
allowlist:
  - src/gzkit/commands/ceremony_data.py
  - src/gzkit/commands/ceremony_steps.py
  - src/gzkit/commands/closeout_ceremony.py
  - src/gzkit/commands/ceremony_state.py
  - tests/governance/test_ceremony_ln_consumption.py
reqs:
  - REQ-0.0.63-06-01
  - REQ-0.0.63-06-02
  - REQ-0.0.63-06-03
  - REQ-0.0.63-06-04
verification:
  - uv run gz validate --documents
  - uv run gz arb ruff
  - uv run gz arb typecheck
  - uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_ceremony_ln_consumption.py -v
citations:
  - - docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md
    - "Decision 4 + BI-3"
  - - docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/obpis/OBPI-0.0.63-03-evidence-summary-and-proof-binding.md
    - "Implementation Summary — deferred runtime surface"
---

# OBPI-0.0.63-06-req-evidence-schema-consumption: **req-evidence-schema-consumption** — Post-P2 increment. The runtime engine consumes the `req_evidence:` field added to `obpi_brief_structure.json` by `ADR-pool.obpi-authoring-mechanical-floor`; binding logic is mechanical, not prose.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`
- **Checklist Item:** #6 - "OBPI-0.0.63-06: **req-evidence-schema-consumption** — Post-P2 increment. The runtime engine consumes the `req_evidence:` field added to `obpi_brief_structure.json` by `ADR-pool.obpi-authoring-mechanical-floor`; binding logic is mechanical, not prose."

**Status:** Completed

## Objective

**Parent ADR Decision item verbatim (GHI #321):**
> "OBPI-0.0.63-06: **req-evidence-schema-consumption** — Post-P2 increment. The runtime engine consumes the `req_evidence:` field added to `obpi_brief_structure.json` by `ADR-pool.obpi-authoring-mechanical-floor`; binding logic is mechanical, not prose."

The closeout ceremony runtime (`ceremony_data.py`, `ceremony_steps.py`, `closeout_ceremony.py`) gains mechanical consumption of the structured `ln: list[ReqEvidence]` field (added to `BriefStructure` by OBPI-0.0.63-03):

1. `extract_brief_metadata()` in `ceremony_data.py` gains `ln_entries` extraction — the ceremony data layer reads the `ln` frontmatter and returns structured proof-binding data alongside the existing metadata keys.
2. `render_step_6_attestation()` in `ceremony_steps.py` gains a rendered REQ↔receipt binding table sourced from `ln_entries` — section 3c of the Evidence Summary becomes a machine-rendered table, not an agent prose instruction.
3. The Step 5→6 transition in `closeout_ceremony.py` gains a proof-binding gate — if `validate_closeout_proof_binding` finds unbound REQs, the advancement to ATTESTATION fails closed with a named remediation.

## Lane

**Heavy** — Changes the closeout ceremony state machine (`closeout_ceremony.py`), ceremony data layer (`ceremony_data.py`), and step renderer (`ceremony_steps.py`). These are runtime-contract surfaces.

## Allowed Paths

- `src/gzkit/commands/ceremony_data.py` — add `ln_entries` extraction to `extract_brief_metadata()`
- `src/gzkit/commands/ceremony_steps.py` — add structured proof-binding table to `render_step_6_attestation()`
- `src/gzkit/commands/closeout_ceremony.py` — add proof-binding gate at EXECUTE→ATTESTATION edge
- `src/gzkit/commands/ceremony_state.py` — **CREATE** src/gzkit/commands/ceremony_state.py (operator-directed scope expansion): models + state I/O + step/verdict helpers extracted from `closeout_ceremony.py` to restore the 600-line budget (precedent: `pipeline_markers.py`)
- `tests/governance/test_ceremony_ln_consumption.py` — REQ-derived tests (new file)

## Denied Paths

- `src/gzkit/governance/brief_structure.py` — schema already complete (OBPI-03)
- `src/gzkit/governance/trust_audits/closeout_proof_binding.py` — validator already complete (OBPI-03)
- `src/gzkit/commands/validate_cmd.py` — CLI surface already wired (OBPI-03)
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ~~REQUIREMENT: `extract_brief_metadata` MUST return an `ln_entries` key containing a list of `{req_id, receipt_ids, file_lines}` dicts parsed from the brief's `ln:` frontmatter; an empty list when `ln:` is absent.~~ [REQ-0.0.63-06-01] — **SUPERSEDED by ADR-0.0.69 + GHI #601:** the `ln:` surface was retired (producer in OBPI-0.0.69-04, consumer in GHI #601). Closeout proof is now computed by the derived `gz validate --closeout-proof` view; `extract_brief_metadata` no longer emits `ln_entries` and its covering test was removed.
2. ~~REQUIREMENT: `render_step_6_attestation` MUST accept `ln_entries` (from brief metadata) and render a structured REQ↔receipt binding table in its output when at least one `ln_entries` entry is present; the table replaces the prose instruction "run gz validate --closeout-proof-binding".~~ [REQ-0.0.63-06-02] — **SUPERSEDED by ADR-0.0.69 + GHI #601:** the `ln:` render branch was dead (0 briefs carry `ln:`) and is removed; `render_step_6_attestation` no longer accepts `ln_entries`. Its covering test was removed.
3. REQUIREMENT: The EXECUTE→ATTESTATION step transition MUST call `validate_closeout_proof_binding` and raise `PolicyBreachError` naming the unbound REQs when the validator returns any errors; bare `--next` cannot advance past this gate without a clean proof-binding check. [REQ-0.0.63-06-03]
4. REQUIREMENT: When `validate_closeout_proof_binding` returns zero errors, the EXECUTE→ATTESTATION transition MUST succeed (the gate passes without blocking). [REQ-0.0.63-06-04]
5. NEVER: Modify `brief_structure.py`, `closeout_proof_binding.py`, or `validate_cmd.py` — those surfaces belong to OBPI-03.
6. ALWAYS: Keep `ceremony_data.py`, `ceremony_steps.py`, and `closeout_ceremony.py` under 600 lines/module (pythonic.md size limit).

> STOP-on-BLOCKERS: OBPI-0.0.63-03 (`attested_completed`) is a prerequisite. Run `uv run gz adr status ADR-0.0.63` before starting; halt if OBPI-03 is not completed.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [x] **Parent ADR § Decision item #4 quoted verbatim** in Objective above. Decision: "Render in markdown + structured JSON for the closeout state machine to consume."
- [x] Parent ADR § BI-3: "Gate-5 cannot be self-advanced. Anchored by OBPI-01; consumed by OBPI-03 (proof-binding) and OBPI-06 (req-evidence)."
- [x] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/commands/ceremony_data.py` — must exist; `extract_brief_metadata` is the target function. ✓
- [x] `src/gzkit/commands/ceremony_steps.py` — must exist; `render_step_6_attestation` is the target renderer. ✓
- [x] `src/gzkit/commands/closeout_ceremony.py` — must exist; `_commit_advance` and `_gate_attestation_boundary` are the target gate path. ✓
- [x] OBPI-0.0.63-03 `attested_completed` — `BriefStructure.ln: list[ReqEvidence]` and `validate_closeout_proof_binding` must be shipped. ✓
- [x] `tests/governance/test_ceremony_ln_consumption.py` — **CREATE** tests/governance/test_ceremony_ln_consumption.py (new file, will be created during implementation)

**Existing Code (understand before editing):**

- [x] `ceremony_data.py::extract_brief_metadata()` — reads frontmatter via raw line scan; returns dict with id, title, objective, status, lane, acceptance_criteria keys.
- [x] `ceremony_steps.py::render_step_6_attestation()` — prose-only renderer; Step 6 currently tells the agent to "present the Evidence Summary Template now."
- [x] `closeout_ceremony.py::_commit_advance()` — shared advance path; calls `_gate_attestation_boundary()` for the Step 6→7 edge. The new gate fires at the Step 5→6 edge.
- [x] `closeout_ceremony.py::_gate_attestation_boundary()` — gates Step 6→7 on a fresh `attested` ledger receipt. Pattern to replicate for the new gate.

**Governance:**

- [x] `.claude/rules/pythonic.md` — module size limit: 600 lines.
- [x] `AGENTS.md` — tests assert semantics, not strings; TDD Red-Green-Refactor.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR Decision item #4 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from REQs, not from implementation
- [ ] Red-Green-Refactor cycle followed
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] No user-facing doc changes required (runtime-internal changes only)

### Gate 4: BDD (Heavy only)

- [ ] Check for @REQ-0.0.63-06 tagged behave scenarios; scope invocation if present

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_ceremony_ln_consumption.py -v
uv run gz covers OBPI-0.0.63-06-req-evidence-schema-consumption --json
```

## Demo

```bash
# Show that extract_brief_metadata returns ln_entries
uv run python3 -c "
from pathlib import Path
from gzkit.commands.ceremony_data import extract_brief_metadata
import json
brief = Path('docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/obpis/OBPI-0.0.63-06-req-evidence-schema-consumption.md')
meta = extract_brief_metadata(brief)
print(json.dumps({'ln_entries': meta.get('ln_entries', [])}, indent=2))
"

# Show that render_step_6_attestation renders the binding table when ln_entries present
uv run python3 -c "
from gzkit.commands.ceremony_steps import render_step_6_attestation
out = render_step_6_attestation('ADR-0.0.63-closeout-ceremony-runtime-engine-parity', ln_entries=[{'req_id': 'REQ-0.0.63-06-01', 'receipt_ids': ['arb-step-unittest-abc'], 'file_lines': ['tests/governance/test_ceremony_ln_consumption.py:42']}])
print(out[:400])
"
```

## Acceptance Criteria

- [ ] REQ-0.0.63-06-01 [BEHAVIOR]: Given an OBPI brief with `ln:` frontmatter entries, when `extract_brief_metadata` is called, then the returned dict contains an `ln_entries` key with the structured proof-binding data (`req_id`, `receipt_ids`, `file_lines`) — **SUPERSEDED (ADR-0.0.69 / GHI #601):** `ln:` surface retired; `ln_entries` no longer emitted; covering test removed
- [ ] REQ-0.0.63-06-02 [BEHAVIOR]: Given brief metadata with non-empty `ln_entries`, when `render_step_6_attestation` is called, then the rendered output contains the REQ↔receipt binding table sourced from `ln_entries` — **SUPERSEDED (ADR-0.0.69 / GHI #601):** `ln:` render branch removed; `render_step_6_attestation` no longer accepts `ln_entries`; covering test removed
- [ ] REQ-0.0.63-06-03 [BEHAVIOR]: Given an ADR in active closeout ceremony where `validate_closeout_proof_binding` returns errors, when `--next` advances from EXECUTE (Step 5) to ATTESTATION (Step 6), then `PolicyBreachError` is raised naming the unbound REQs
- [ ] REQ-0.0.63-06-04 [BEHAVIOR]: Given an ADR in active closeout ceremony where all REQs have valid `ln` bindings, when `--next` advances from EXECUTE to ATTESTATION, then the transition succeeds without error

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief; Decision item quoted
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from REQs, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now documented
- [ ] **Key Proof:** One concrete usage example included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` § OBPI Acceptance Protocol.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded; Decision item quoted verbatim

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
No user-facing doc changes required — runtime-internal surface only.
```

### Gate 4 (BDD)

```text
# Paste behave output here if @REQ-0.0.63-06 tagged scenarios exist
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before this OBPI: the Evidence Summary section 3c was prose — an agent instruction to manually run `gz validate --closeout-proof-binding`. The `ln` field existed in the schema (OBPI-03) but nothing in the ceremony runtime read it, so "every REQ is bound" was still agent-narrated prose, and `--next` could advance from EXECUTE to ATTESTATION regardless of proof-binding state.

After: `extract_brief_metadata()` extracts `ln_entries` structurally; `render_step_6_attestation()` renders the REQ↔receipt binding table from that data automatically; and `_gate_proof_binding` fail-closes the EXECUTE→ATTESTATION edge when proof binding is incomplete — binding logic is mechanical, not prose (BI-3 "Gate-5 cannot be self-advanced", consumed by OBPI-06).

### Key Proof


```text
$ uv run -m unittest tests.governance.test_ceremony_ln_consumption.TestExecuteToAttestationGate.test_gate_raises_policy_breach_when_validator_returns_errors -v
test_gate_raises_policy_breach_when_validator_returns_errors ... ok
# _gate_proof_binding(project_root, state@EXECUTE) raises PolicyBreachError when
# validate_closeout_proof_binding returns errors — the EXECUTE->ATTESTATION
# transition is blocked. Complement test_gate_succeeds_* confirms it passes clean.

# Full surface: 7/7 OBPI tests + full suite 5761/5761
# Receipts: arb-step-unittest-c2dd7bc86d8c4aba87fa1a851531d501 (unittest),
#           arb-ruff-f0c21471bc024596b243eaec818e21f2 (lint),
#           arb-step-typecheck-f227efcbc0bb449da05083f858945eba (typecheck)
```

### Implementation Summary


- Files created: `src/gzkit/commands/ceremony_state.py` (models + state I/O + step/verdict helpers extracted from `closeout_ceremony.py` to restore the 600-line budget; public API re-imported), `tests/governance/test_ceremony_ln_consumption.py` (7 REQ-derived tests)
- Files modified: `src/gzkit/commands/ceremony_data.py` (`extract_brief_metadata` returns `ln_entries`, YAML-guarded), `src/gzkit/commands/ceremony_steps.py` (`render_step_6_attestation` renders REQ↔receipt table), `src/gzkit/commands/closeout_ceremony.py` (`_gate_proof_binding` gate at EXECUTE→ATTESTATION; re-imports from `ceremony_state`; 743→575 lines)
- Tests added: 7 (TestExtractBriefMetadataLnEntries [REQ-01], TestRenderStep6AttestationLnEntries [REQ-02], TestExecuteToAttestationGate [REQ-03/04])
- Date completed: 2026-05-30
- Attestation status: operator-attested (Stage 4 verbatim "attest completed")
- Defects noted: 2 surfaced + resolved (closeout_ceremony.py module-split; gz-adr-promote stale-version test) — see Tracked Defects

## Tracked Defects

- **Module-size budget overrun — RESOLVED (operator-directed, 2026-05-30).** `src/gzkit/commands/closeout_ceremony.py` was 707 lines at HEAD (already over the 600-line budget in `.claude/rules/pythonic.md`); this OBPI's `_gate_proof_binding` + `_commit_advance` wiring pushed it to 743. Per operator direction ("just fix them"), the models + state I/O + step/verdict helpers were extracted into the new `src/gzkit/commands/ceremony_state.py` (precedent: `pipeline_markers.py`/`ledger_events.py` carved out of `pipeline_runtime.py`), with the public API preserved by re-import. Result: `closeout_ceremony.py` → **575 lines** (under budget), `ceremony_state.py` → 204 lines. All 108 ceremony/closeout tests pass; full suite green; lint/typecheck clean.
- **Unrelated red test on main — FIXED (separate commit, 2026-05-30).** `tests/governance/test_foundation_invariance_skill_enrichment.py::test_gz_adr_promote_version_bumped` expected `gz-adr-promote` skill-version `1.4.2` but the skill is at `1.5.0` (bumped under GHI #568, commit `ab9507c0`); the test's expected-version table was stale. Per operator direction, the expectation was aligned to `1.5.0`. This is a distinct surface from OBPI-0.0.63-06 and lands as its own `fix(test):` commit (`Task: TASK-adr-promote-version-align-#568`), not folded into this brief's changeset. Full suite is green post-fix. Recorded in `.gzkit/insights/agent-insights.jsonl`.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.63-06 wires the closeout ceremony runtime to mechanically consume the structured `ln` (ReqEvidence) proof-binding field OBPI-03 added to the brief schema: extract_brief_metadata returns ln_entries (YAMLError-guarded), render_step_6_attestation renders the REQ↔receipt binding table, and _gate_proof_binding fail-closes the EXECUTE→ATTESTATION edge when validate_closeout_proof_binding returns errors (BI-3, consumed by OBPI-06). 7/7 REQ-derived tests pass; full suite 5761/5761 (arb-step-unittest-c2dd7bc86d8c4aba87fa1a851531d501); lint clean (arb-ruff-f0c21471bc024596b243eaec818e21f2); typecheck clean (arb-step-typecheck-f227efcbc0bb449da05083f858945eba); mkdocs clean (arb-step-mkdocs-af9e1cfde5c84c7a923b8b68a4041376). Two in-flight defects resolved per operator direction: closeout_ceremony.py split 743→575 lines (new ceremony_state.py, public API preserved) and the gz-adr-promote stale-version test aligned 1.4.2→1.5.0 (lands as its own fix(test) commit).
- Date: 2026-05-30

---

**Date Completed:** 2026-05-30

**Evidence Hash:** -
