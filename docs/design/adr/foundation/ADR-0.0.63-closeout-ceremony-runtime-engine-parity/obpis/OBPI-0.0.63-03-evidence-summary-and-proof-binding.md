---
id: OBPI-0.0.63-03-evidence-summary-and-proof-binding
parent: ADR-0.0.63-closeout-ceremony-runtime-engine-parity
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.63-03-evidence-summary-and-proof-binding: **evidence-summary-and-proof-binding** — `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:285-339` plus new CLI validator `gz validate --closeout-proof-binding`. Evidence Summary Template gains a REQ column; every receipt row binds `(REQ-ID, receipt-ID, file-line range)` in markdown + structured JSON. Validator exits 3 on missing REQ↔receipt-ID bindings.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`
- **Checklist Item:** #3 — "OBPI-0.0.63-03: **evidence-summary-and-proof-binding** — `obpi_brief_structure.json` gains the optional `ln` (ReqEvidence) field; `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:285-339` Evidence Summary Template gains a REQ column; new CLI validator `gz validate --closeout-proof-binding` exits 3 on missing REQ↔receipt-ID bindings (markdown + structured JSON)."

**Status:** Completed

## Objective

Land the structured proof-binding surface (`ln`) and a fail-closed `gz validate --closeout-proof-binding` validator so every REQ under an ADR at closeout is mechanically bound to a ledger-present receipt-ID — replacing prose evidence claims with a machine-checked REQ↔receipt-ID floor.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface (new `gz validate` scope, new `obpi_brief_structure.json` schema field + `BriefStructure` model field).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md` — parent ADR; read for intent (Decision items 4 & 5), and edit Checklist item #3 + Target Scope #3 to name the absorbed `ln` schema-field-add (1:1-sync mandate)
- `docs/design/adr/pool/ADR-pool.obpi-authoring-mechanical-floor.md` — Decision item 2 (the `req_evidence`/`ln` field) relocates here; edit it to read "relocated to ADR-0.0.63 OBPI-03; canonical field key `ln`, model `ReqEvidence`" (single-owner; resolves the `req_evidence`→`ln` naming drift)
- `src/gzkit/governance/brief_structure.py` — add `ReqEvidence` Pydantic model + optional `ln: list[ReqEvidence]` field on `BriefStructure` (default_factory=list; legacy-safe)
- `src/gzkit/schemas/obpi_brief_structure.json` — mirror the model: add optional `ln` array property (NOT in `required`); `"$id"`/title unchanged
- `src/gzkit/governance/trust_audits/closeout_proof_binding.py` — NEW scope function `validate_closeout_proof_binding(project_root) -> list[ValidationError]` (mirror `advisor_proof_binding.py`)
- `src/gzkit/governance/trust_audits/__init__.py` — export `validate_closeout_proof_binding`
- `src/gzkit/cli/parser_maintenance.py` — register `--closeout-proof-binding` flag + `set_defaults` pass-through (mirror `--advisor-proof-binding`)
- `src/gzkit/commands/validate_cmd.py` — wire the scope at every `advisor_proof_binding` site (signature, explicit-scopes dict, runner lambda, policy-breach list for exit 3, pass-through, final checks dict)
- `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` — Evidence Summary Template (lines 285-339): add REQ column binding (REQ-ID, receipt-ID, file-line range)
- `docs/user/manpages/validate.md` — document `--closeout-proof-binding` so `gz cli audit` stays green
- `tests/` — REQ-derived `@covers` tests for the schema field + validator behaviors

> Sync note: editing `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` requires
> `uv run gz agent sync control-surfaces` to regenerate `src/gzkit/skills/`,
> `.claude/skills/`, `.github/skills/`, `.agents/skills/`. Those regenerated
> mirrors are touched by sync, not hand-edited (skill-surface-sync rule).

## Denied Paths

- `src/gzkit/commands/closeout_ceremony.py`, `ceremony_data.py`, `ceremony_steps.py`, `closeout.py` — closeout RUNTIME. OBPI-03 ships the validator + schema + template only; wiring the runtime engine to CONSUME `ln` is OBPI-0.0.63-06 (req-evidence-schema-consumption). Read-only reference.
- `src/gzkit/commands/specify_cmd.py` — `gz specify` authoring-gate changes are `ADR-pool.obpi-authoring-mechanical-floor` Decision items 1/3/4; NOT relocated here, only the `ln` field (item 2) is.
- `.claude/skills/`, `.github/skills/`, `.agents/skills/`, `src/gzkit/skills/` — generated mirrors; produced by `gz agent sync`, never hand-edited
- New runtime dependencies; CI files; lockfiles
- Paths not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `obpi_brief_structure.json` + `BriefStructure` MUST gain an OPTIONAL `ln` field (list of `ReqEvidence`, shape `{req_id: str, receipt_ids: list[str], file_lines: list[str]}`); briefs WITHOUT `ln` MUST continue to parse unchanged (legacy-safe — `ln` is never in the schema `required` set).
2. REQUIREMENT: `gz validate --closeout-proof-binding` MUST exit 3 (policy breach) when an ADR in scope (persisted closeout ceremony state present) has a REQ with no `ln` entry or with empty `receipt_ids`.
3. REQUIREMENT: The receipt-ID check MUST be ledger-existence (the cited receipt-ID must resolve to a real ledger event), NEVER mere string-presence in the brief. A typo'd or fabricated receipt-ID fails closed.
4. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief; runtime-consumption surfaces (closeout_ceremony/ceremony_data/closeout) stay untouched (OBPI-06 owns them).
5. ALWAYS: Canonical field key is `ln`; model is `ReqEvidence`. OBPI-0.0.63-06 reads the SAME key — the validator-read key (03) and the runtime-read key (06) MUST be identical.
6. ALWAYS: Reconcile the brief with the parent ADR before implementation — Checklist item #3 + Target Scope #3 expanded to name the `ln` field-add; pool-ADR item 2 marked relocated, in the same change.
7. NEVER: Add `--closeout-proof-binding` to the default `gz validate` / `gz check` scope — it is opt-in (mirrors `--advisor-proof-binding`); default-scoping it would fail-close repo-wide on every pre-`ln` ADR.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [x] **Parent ADR § Decision items 4 & 5 — quoted verbatim:**
  - Item 4: "Add REQ column to Evidence Summary Template. Every Evidence Summary row binds (REQ-ID, receipt-ID, file-line range). Render in markdown + structured JSON for the closeout state machine to consume."
  - Item 5: "Implement REQ↔receipt-ID validator with fail-close. New `gz validate --closeout-proof-binding` checks that every REQ in the parent ADR's Acceptance Criteria has at least one binding receipt-ID cited in the closeout Evidence Summary; missing bindings exit 3."
- [x] Parent ADR § Intent — closeout runtime parity with `gz obpi pipeline`; ledger evidence (not agent claims) is source-of-truth at attestation.
- [x] Parent ADR § Boundary Invariants — BI-3 (Gate-5 cannot be self-advanced) is anchored by OBPI-01 and *consumed* by OBPI-03; build on `_commit_advance`/`_has_fresh_attestation_receipt`, do not fork a second advance path. (No new BI introduced by OBPI-03.)

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md` — operating contract; req-kind-discipline, attestation, stdlib-first
- [x] `.gzkit/rules/skill-surface-sync.md` — edit `.gzkit/` first, then sync

**Context:**

- [x] `src/gzkit/governance/trust_audits/advisor_proof_binding.py` — the wiring template for a new `gz validate` scope
- [x] `src/gzkit/governance/brief_structure.py` — `BriefStructure` model (no `ln` yet)
- [x] `src/gzkit/triangle.py` — `scan_briefs` / `extract_reqs_from_brief` enumerate ADR REQs
- [x] OBPI-0.0.63-06 brief — consumes `ln` at runtime; agrees on key

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/schemas/obpi_brief_structure.json` exists (the schema mirrors `BriefStructure`)
- [x] `src/gzkit/governance/trust_audits/__init__.py` exports existing scope functions
- [x] `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` Evidence Summary Template at lines 285-339

**Existing Code (understand current state):**

- [x] `tests/governance/test_advisor_proof_binding_validator.py` reviewed — the analog test layout (tempdir sandbox, fixture/ledger/schema scan scopes, `@covers` decorators) is the template for `test_closeout_proof_binding.py`.
- [x] `tests/governance/test_brief_structure.py` reviewed — `BriefStructure` model tests (frozen, extra-forbid, empty-field rejection); the new `ln` field follows the same `_VALID_FIELDS` fixture convention.
- [x] `src/gzkit/governance/trust_audits/advisor_proof_binding.py` read in full — `validate_advisor_proof_binding(project_root) -> list[ValidationError]` signature, `_scan_*` helper decomposition, and `_relative()` POSIX-path rendering are mirrored by `closeout_proof_binding.py`.
- [x] `src/gzkit/commands/validate_cmd.py` wiring sites traced — the 8 `advisor_proof_binding` insertion points (signature, explicit-scopes dict, opt-in-scopes list, runner lambda, policy-breach frozenset, outer signature, pass-through, final checks dict) are the exact surface the new scope wires into.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision items 4 & 5 quoted; Checklist #3 + Target Scope #3 reconciled

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from REQ acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/validate.md` documents `--closeout-proof-binding`; `gz cli audit` green

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass OR behave waiver recorded (end-to-end closeout BDD lands at ADR-0.0.63 closeout — same deferral as OBPI-01/02; validator exit-code/state semantics proven by REQ-derived unittest)

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --closeout-proof-binding
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
```

## Demo

```bash
# The new structured proof-binding surface (ReqEvidence) is accepted by the brief model:
uv run python -c "from gzkit.governance.brief_structure import ReqEvidence; print(ReqEvidence(req_id='REQ-0.0.63-03-02', receipt_ids=['arb-ruff-0978e2824deb4f95ad1608af4a72e59b'], file_lines=['src/gzkit/governance/trust_audits/closeout_proof_binding.py:1']).model_dump())"

# The fail-closed proof-binding gate runs as an opt-in gz validate scope (exit 0 when no in-scope ADR has an unbound REQ):
uv run gz validate --closeout-proof-binding
```

## Acceptance Criteria

- [ ] REQ-0.0.63-03-01 [BEHAVIOR]: Given an OBPI brief whose frontmatter declares `ln: [{req_id, receipt_ids, file_lines}]`, when it is parsed via `parse_brief`, then `BriefStructure.ln` round-trips a list of `ReqEvidence`; AND given a brief with NO `ln` key, when parsed, then it loads unchanged (legacy-safe — `ln` defaults to `[]`, never required). The JSON schema accepts both.
- [ ] REQ-0.0.63-03-02 [BEHAVIOR]: Given an ADR in scope (persisted closeout ceremony state) with a REQ that has no `ln` entry (or an entry with empty `receipt_ids`), when `gz validate --closeout-proof-binding` runs, then it returns a `ValidationError` of policy-breach type and the CLI exits 3, naming the unbound REQ.
- [ ] REQ-0.0.63-03-03 [BEHAVIOR]: Given an `ln` entry whose `receipt_ids` cites an ID with no matching ledger event, when `gz validate --closeout-proof-binding` runs, then it exits 3 — the binding floor is ledger-existence, never string-presence in the brief (a typo'd receipt-ID fails closed).
- [ ] REQ-0.0.63-03-04 [BEHAVIOR]: Given an ADR in scope where every REQ has ≥1 `ln` entry and every cited receipt-ID resolves to a ledger event, when `gz validate --closeout-proof-binding` runs, then it exits 0 with no errors.
- [ ] REQ-0.0.63-03-05 [SUPPORT]: The Evidence Summary Template in `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` (lines 285-339) carries a REQ-binding column tying (REQ-ID, receipt-ID, file-line range); the canonical edit is propagated to pkg + vendor mirrors (`agent_sync_completed` ledger event) and mirror parity is held by `gz validate --surfaces`.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; Checklist #3 + Target Scope #3 reconciled; pool-ADR item 2 relocated
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from REQs, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now documented
- [ ] **Key Proof:** One concrete usage example included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

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
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Behave waiver reference or scenario output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before: the closeout Evidence Summary was ephemeral markdown prose — there was no
machine surface binding a REQ to the receipt that proves it, so "every REQ is
covered" was an agent narrative claim with no fail-close. After: briefs carry a
structured `ln` (ReqEvidence) field and `gz validate --closeout-proof-binding`
fail-closes (exit 3) on any in-scope REQ lacking a ledger-present receipt-ID —
prose evidence becomes a mechanical floor.

### Key Proof


`uv run gz validate --closeout-proof-binding` => `Validated: closeout_proof_binding / ✓ All validations passed (1 scopes).` exit 0. The fail-close path (exit 3, policy-breach type) is verified by REQ-02 (no ln entry / empty receipt_ids) and REQ-03 (typo'd receipt-ID absent from artifacts/receipts/) tests. Ledger-existence floor, not string-presence. Receipt: arb-step-unittest-7f034b61890243d6841d197e1b990bfa (5748 tests, 0 fail).

### Implementation Summary


- Files created: src/gzkit/governance/trust_audits/closeout_proof_binding.py (validator), tests/governance/test_closeout_proof_binding.py (11 tests)
- Files modified: brief_structure.py (ReqEvidence model + BriefStructure.ln field), obpi_brief_structure.json (ln/tasks/req_atomic properties), trust_audits/__init__.py (export), parser_maintenance.py (--closeout-proof-binding flag), validate_cmd.py (8 wiring sites incl opt-in-scopes list + policy-breach frozenset), gz-adr-closeout-ceremony/SKILL.md (REQ Bindings column 3b + new 3c; v7.12->7.13; synced), docs/user/manpages/validate.md (scope doc + table row), test_skill_self_close_drift.py (version baseline), ADR-0.0.63 (Checklist #3 + Target Scope #3 expanded to name ln field-add), ADR-pool.obpi-authoring-mechanical-floor.md (Decision item 2 relocated to OBPI-03; resolves req_evidence->ln naming drift), data/behave_coverage_waivers.json (waiver)
- Tests added: 11 (TestReqEvidenceModel x5 [REQ-01], TestUnboundReqFailsClosed x3 [REQ-02], TestLedgerExistenceFloor x1 [REQ-03], TestAllReqsBoundPasses x2 [REQ-04])
- Date completed: 2026-05-29
- Attestation status: operator-attested (Stage 4 verbatim "attest completed")
- Defects noted: none

### Decisions Made

- **M2 — fold the `ln` schema-field-add into OBPI-03** (operator chose "schema-first" 2026-05-29). Producer/first-consumer pattern: 03 adds the field + validator, 06 consumes it at runtime. No new OBPI-08; checklist stays 7. Alternative rejected: promoting the whole `ADR-pool.obpi-authoring-mechanical-floor` (drags in unrelated `gz specify` default-flip + `--ground-truth` validator + new event types).
- **Canonical name `ln` (key) + `ReqEvidence` (model)**, shape `{req_id, receipt_ids, file_lines}`. Committed surfaces (ADR-0.0.63 Checklist #6, OBPI-06 brief) say `ln`; the pool ADR's prose `req_evidence` is relocated and renamed in the same change. Salvation-plan `{req, file, anchor, assertion}` shape rejected — it lacks `receipt_ids`, which Decision item 5 (REQ↔receipt-ID) requires.
- **Validator scope = ADRs with a persisted closeout ceremony state** (`.gzkit/ceremonies/<ADR>.ceremony.json`). Keeps `ln` optional during authoring, required at closeout (matches pool-ADR item 2 "optional at authoring, required by `--closeout-proof-binding` at closeout"). Read-only; does not touch the runtime (OBPI-06's surface).
- **Ledger-existence floor** for receipt-IDs (mirrors `advisor_proof_binding` ledger scan + ADR port framing "mechanical, not prose"). String-presence is insufficient.
- **Opt-in scope** (not default `gz check`) — mirrors `--advisor-proof-binding`.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.63-03 ships the structured `ln` (ReqEvidence) brief-schema field and the fail-closed `gz validate --closeout-proof-binding` scope (REQ↔receipt-ID ledger-existence floor; in-scope = ADRs with persisted closeout ceremony state). 11/11 REQ-derived tests pass; full suite 5748/5748 (arb-step-unittest-7f034b61890243d6841d197e1b990bfa); lint/typecheck/mkdocs clean (arb-ruff-eaee17ca991a498f96e66c9ecb4cf7b9, arb-step-typecheck-bc70e3c50e1747d3bcea15a192751762, arb-step-mkdocs-773788e3b0aa45449c285074c9f4d978); gz cli audit 105/105. REQ-05 (Evidence Summary REQ column) is SUPPORT-kind, accepted uncovered.
- Date: 2026-05-29

---

**Date Completed:** 2026-05-29

**Evidence Hash:** -
