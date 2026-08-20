---
id: OBPI-0.0.69-03-closeout-proof-derived-view
parent: ADR-0.0.69-channels-first-closeout-proof
item: 3
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible labor unit — the derived-view
# function (01), its re-run-command output (02), the gz-check wiring (03), the
# fail-open seam fix (04), the ceremony-gate swap + its doc/cross-ref surface as
# one SUPPORT deliverable (05), the no-persist structural fence (06), and the
# kind-tag enforcement branch (07). None decomposes into parallel seq=02+ sub-tasks
# (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.69-03-01
  - REQ-0.0.69-03-02
  - REQ-0.0.69-03-03
  - REQ-0.0.69-03-04
  - REQ-0.0.69-03-05
  - REQ-0.0.69-03-06
  - REQ-0.0.69-03-07
---

# OBPI-0.0.69-03-closeout-proof-derived-view: Closeout-Proof Derived View

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md`
- **Checklist Item:** #3 - "OBPI-0.0.69-03: Derived `gz validate --closeout-proof` view (new `trust_audits/closeout_proof.py`) printing the per-failed-SUPPORT-REQ re-run command (no stderr inlining) + READ-ONLY pre-audit of all 19 `ln`-carrying briefs before the ceremony-gate repoint lands + ceremony-gate repoint + fail-open seam fix + repoint ADR-0.0.41 OBPI-02/03 verification text + manpage (Heavy)"

**Status:** Completed

## Objective

A new `gz validate --closeout-proof` view recomputes per-REQ proof for in-closeout ADRs
over the three REQ-kind channels every run, JOINs the `gz check` default set (memoized per
scope per run), replaces the ceremony gate `_gate_proof_binding` with `_gate_closeout_proof`
on the same EXECUTE->ATTESTATION edge, fixes the fail-open seam in `audit_skill_alignment`,
repoints ADR-0.0.41's verification text, prints the exact re-run command per failed SUPPORT
REQ, and is pre-audited READ-ONLY against the 19 `ln`-carrying briefs before the gate repoint
lands.

## Lane

**Heavy** - Adds a new `gz validate --closeout-proof` scope (a CLI/runtime-contract surface),
wires it into the `gz check` default scope, and changes ceremony-gate behavior on the
EXECUTE->ATTESTATION edge.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/traceability.py` (added by brief reconcile, attestor g0)

<!-- What files/directories are IN SCOPE? -->

- `src/gzkit/governance/trust_audits/closeout_proof.py` **CREATE** — NEW: the derived view computing per-REQ proof over the three channels for in-closeout ADRs; frozen `CloseoutProofReport` reusing `ReqCoverageRecord`; per-REQ table + `--json`; exit 0 (all proven) / 3 (any unproven) / 2 (dispatch I/O error); prints the exact re-run command per failed SUPPORT REQ
- `src/gzkit/governance/trust_audits/__init__.py` — re-export the new audit
- `src/gzkit/governance/trust_audits/cli.py` — fix the fail-open seam at lines ~222-225 (`audit_skill_alignment` bare `except` -> `return []`) to surface `ValidationError`
- `src/gzkit/quality.py` — `run_closeout_proof_audit` runtime delegate
- `src/gzkit/commands/quality.py` — add the scope to `_build_check_steps()` (memoized per scope per run)
- `src/gzkit/commands/validate_cmd.py` — dispatch the `--closeout-proof` scope
- `src/gzkit/cli/parser_maintenance.py` — register the `--closeout-proof` flag
- `src/gzkit/commands/closeout_ceremony.py` — replace `_gate_proof_binding` (lines ~264-290, wired at `_commit_advance:336`) with `_gate_closeout_proof` on the same EXECUTE->ATTESTATION edge, same fail-close shape
- `tests/` — fail-close + green-path tests; fail-open-seam regression test; check-scope membership test
- `docs/user/manpages/validate.md` — document the new `--closeout-proof` scope and its exit-0/3/2 contract and re-run-command output
- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/obpis/` — repoint ADR-0.0.41 OBPI-02/03 verification text from the removed `--closeout-proof-binding` flag to `--closeout-proof` (else `--cli-alignment` exits 3); tag ADR-0.0.41's untagged REQs during the pre-audit
- `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md` — parent ADR (read-only); home of REQ-0.0.69-03-06's Boundary-Invariants entry
- `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/obpis/OBPI-0.0.69-03-closeout-proof-derived-view.md` — this brief

> The module homes above are the current locations of the validate-scope and ceremony
> machinery; if a refactor has moved them, locate the real home before editing and note
> the divergence — do not author against a stale path. Confirm ADR-0.0.41's real package
> path before repointing.

## Denied Paths

<!-- What is OUT OF SCOPE? -->

- The `ln:` closeout-proof-binding surface (`closeout_proof_binding.py`, schema `ln`, producer, 19-brief strip) — OBPI-04's scope; this OBPI only READS the 19 briefs in the pre-audit
- `.pre-commit-config.yaml` and the `gz check` session-green wiring (ADR-0.0.68) — must stay untouched (parent ADR Boundary Invariant 3)
- The SUPPORT branch (`_check_support_req`) and the FENCE arm internals — OBPI-01/02 scopes; this OBPI consumes their computed `proof_status`
- Persisting `CloseoutProofReport` to disk as a gate-read artifact (parent ADR Boundary Invariant 2)
- New runtime dependencies; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz validate --closeout-proof` MUST recompute per-REQ proof for in-closeout ADRs over the three channels every run and exit 0 (all proven) / 3 (any unproven) / 2 (dispatch I/O error). It MUST NOT read proof from any stored block.
1. REQUIREMENT: For every failed SUPPORT REQ, the output MUST print the exact re-run command (the cited `uv run gz validate --<scope>`) so the failing channel reproduces in one paste; full stderr inlining is OUT OF SCOPE (ruling 6.2-A).
1. REQUIREMENT: An Acceptance-Criteria REQ carrying no inline `[kind]` tag MUST be reported unproven by `--closeout-proof` — explicit tags are required at closeout; kind inference remains authoring-time advisory only (ruling 6.2-A, first clause).
1. REQUIREMENT: The `--closeout-proof` scope MUST be part of the `gz check` default set, memoized per scope per run (ruling 6.1-A).
1. REQUIREMENT: The ceremony gate `_gate_proof_binding` MUST be replaced by `_gate_closeout_proof` on the SAME EXECUTE->ATTESTATION edge with the same fail-close shape; ADR-0.0.68's session-green gate and `.pre-commit-config.yaml` MUST stay untouched (Boundary Invariant 3).
1. REQUIREMENT: The fail-open seam in `audit_skill_alignment` (`trust_audits/cli.py:222-225`, bare `except` -> `return []`) MUST be fixed to surface `ValidationError`, with a covering test.
1. REQUIREMENT: ADR-0.0.41 OBPI-02/03 verification text MUST be repointed from `--closeout-proof-binding` to `--closeout-proof`; `gz validate --cli-alignment` MUST stay exit 0.
1. REQUIREMENT (pre-audit, ruling 6.1-A): BEFORE the ceremony-gate repoint lands, `gz validate --closeout-proof` MUST be run READ-ONLY against all 19 `ln`-carrying briefs and any unprovable REQ surfaced and fixed (e.g. ADR-0.0.41's untagged REQs tagged), so no real closeout goes red on first contact.
1. NEVER: persist `CloseoutProofReport` to disk as a gate-read artifact; touch the `ln:` surface (OBPI-04) beyond reading it in the pre-audit; touch ADR-0.0.68 surfaces.
1. ALWAYS: reconcile this brief against the parent ADR § Decision item (3) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item (3)** — quote it verbatim into this brief's Implementation Summary.
- [ ] Parent ADR § Intent and § Boundary Invariants (Invariants 2 and 3).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md`

> **STOP:** If you cannot quote the parent ADR § Decision item (3) that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] OBPI-01 (SUPPORT arm) and OBPI-02 (FENCE arm) have landed — the view consumes their computed `proof_status`

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.69-01 and OBPI-0.0.69-02 have landed (the SUPPORT and FENCE arms compute real proof)
- [ ] `run_adr_status_fresh_audit` / `run_session_green_gate_audit` precedent in `src/gzkit/quality.py` reviewed
- [ ] `_build_check_steps()` default-scope list in `src/gzkit/commands/quality.py` located
- [ ] `closeout_ceremony.py` `_gate_proof_binding` (lines ~264-290) and `_commit_advance` (line ~336) located
- [ ] `src/gzkit/governance/trust_audits/cli.py` `audit_skill_alignment` bare-except seam (lines ~222-225) located
- [ ] ADR-0.0.41's package path and OBPI-02/03 verification text located; the 19 `ln`-carrying briefs enumerated
- [ ] `ReqCoverageRecord` reviewed for reuse in the `CloseoutProofReport`

**Existing Code (understand current state):**

- [ ] The `--session-green-gate` scope (ADR-0.0.68) reviewed as the `run_*_audit` + `_build_check_steps()` wiring precedent
- [ ] Existing validator-scope tests reviewed for the fail-close + check-scope test shape

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- Single-program, shell-less invocations only (GHI #415). -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --closeout-proof
uv run gz validate --cli-alignment
uv run gz cli audit
```

## Demo

```bash
# The derived view recomputes per-REQ proof for in-closeout ADRs over the three channels,
# printing the per-failed-SUPPORT-REQ re-run command and exiting 0/3/2:
uv run gz validate --closeout-proof
# JSON form for machine consumption:
uv run gz validate --closeout-proof --json
# Self-referential wiring: the scope runs as part of the default gz check:
uv run gz check
```

## Acceptance Criteria

<!-- Each REQ carries exactly one inline [kind] tag (ADR-0.0.59). -->

- [ ] REQ-0.0.69-03-01 [behavior]: Given an in-closeout ADR, when `gz validate --closeout-proof` runs, then it recomputes per-REQ proof over the three channels and exits 0 (all proven) / 3 (any unproven) / 2 (dispatch I/O error). (@covers test driving each exit)
- [ ] REQ-0.0.69-03-02 [behavior]: Given a failed SUPPORT REQ, when `gz validate --closeout-proof` reports it, then the output prints the exact re-run command (the cited `uv run gz validate --<scope>`) and does NOT inline full stderr. (@covers test asserting the re-run line, ruling 6.2-A)
- [ ] REQ-0.0.69-03-03 [behavior]: Given the `gz check` default scope, when it is enumerated, then `--closeout-proof` is included and is dispatched at most once per run (memoized per scope). (@covers test asserting check-scope membership + single dispatch)
- [ ] REQ-0.0.69-03-04 [behavior]: Given an input that raises `ValidationError` inside `audit_skill_alignment`, when the audit runs, then the error is surfaced — not swallowed by a bare `except` returning `[]`. (@covers regression test for the fail-open seam)
- [ ] REQ-0.0.69-03-05 [support]: The ceremony gate `_gate_proof_binding` is replaced by `_gate_closeout_proof` on the same EXECUTE->ATTESTATION edge; ADR-0.0.41 OBPI-02/03 verification text is repointed to `--closeout-proof` and its untagged REQs are tagged; the READ-ONLY pre-audit of all 19 `ln`-carrying briefs is run before the repoint lands; the manpage documents the scope. Proof: `artifact_edited` ledger events + `gz validate --cli-alignment` exit 0 + `gz validate --closeout-proof` run across the 19 briefs + `mkdocs build --strict` green.
- [ ] REQ-0.0.69-03-06 [structural-fence]: The `--closeout-proof` view MUST NOT persist its `CloseoutProofReport` to disk as a gate-read artifact — it recomputes from live evidence every run. Verified at ADR-0.0.69 closeout via the parent ADR `## Boundary Invariants` (Invariant 2).
- [ ] REQ-0.0.69-03-07 [behavior]: Given an in-closeout ADR whose brief contains an Acceptance-Criteria REQ with no inline `[kind]` tag, when `gz validate --closeout-proof` runs, then that REQ is reported unproven and the run exits 3 — explicit tags are required at closeout; inference stays authoring-time advisory. (@covers test, ruling 6.2-A first clause)

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

Before: closeout proof was read from the stored `ln:` block via the ceremony gate
`_gate_proof_binding`, and `audit_skill_alignment` swallowed `ValidationError` in a bare
`except`. Now: `gz validate --closeout-proof` recomputes per-REQ proof from live evidence
on every `gz check` run, the ceremony gate reads the derived view on the same
EXECUTE->ATTESTATION edge, the fail-open seam surfaces errors, and a 2am operator gets the
exact re-run command for any failed SUPPORT REQ.

### Key Proof


$ uv run gz validate --closeout-proof
✓ All validations passed (10 scopes).   # exit 0 — ADR-0.0.41 parked ceremony excluded by 24h freshness gate

$ uv run gz validate --cli-alignment
✓ All validations passed (1 scopes).     # exit 0 — ADR-0.0.41 repoint clean

Receipts: arb-step-unittest-52a09b6c81694ce4b265cfe4306dc5d6 (6034 pass), arb-ruff-d95f254a34e3452c8433826e983da2a0 (clean), arb-step-typecheck-b1f37b70e0a149628a3ceec2d9723788 (clean), arb-step-mkdocs-8676fc556e1a43eda72c1712e2f8397b (clean).

### Implementation Summary


- Created: src/gzkit/governance/trust_audits/closeout_proof.py — validate_closeout_proof recomputes per-REQ proof for in-closeout ADRs over three channels (BEHAVIOR via @covers, SUPPORT via resolve_support_proof ledger+validator dispatch, STRUCTURAL-FENCE via resolve_fence_proof anchor); exit 0/3/2; never persists (BI-2).
- Ceremony gate: _gate_proof_binding → _gate_closeout_proof on the same EXECUTE→ATTESTATION edge (closeout_ceremony.py); explicit-adr_id path always enforces, gz-check sweep applies a 24h active-ceremony freshness window (operator ruling 2026-06-10) so parked closeouts (e.g. ADR-0.0.41) do not redden gz check.
- Fail-open seam fixed: removed bare `except: return []` in audit_skill_alignment (cli.py).
- Wired --closeout-proof into gz check default scope (quality.py + commands/quality.py); registered the flag (parser_maintenance.py), dispatched the scope (validate_cmd.py, exit 3 via _POLICY_BREACH_ERROR_TYPES); re-exported (__init__.py).
- Pre-audit (ruling 6.1-A): ran --closeout-proof READ-ONLY across the ln-carrying briefs; tagged ADR-0.0.41 OBPI-01's 6 untagged REQs [SUPPORT] + added citations; repointed ADR-0.0.41 OBPI-02/03 verification text from --closeout-proof-binding to --closeout-proof.
- Carve-out fix (operator-approved cross-cut): extended _ADR_DECISION_DOC_RE to exempt pool ADRs from task-envelope Sig (a), closing the gap GHI #563's carve-out left for ADR-pool.*.
- Manpage: docs/user/manpages/validate.md documents --closeout-proof (exit 0/3/2, channels).
- Tests added: test_closeout_proof_view.py (12), test_audit_skill_alignment_seam.py (1), test_task_envelope_coherence.py pool-ADR carve-out (1); 6034 total pass.
- Date completed: 2026-06-10
- Attestation status: operator-attested ("attest completed", Stage 4)
- Defects noted: fixed fail-open seam (cli.py:222-225); fixed exit-code mapping (1→3); fixed task-envelope pool-ADR carve-out gap.

## Tracked Defects

- Fixes the fail-open seam at `trust_audits/cli.py:222-225` (bare `except` -> `return []`).

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.69-03 closeout-proof derived view: gz validate --closeout-proof recomputes per-REQ proof over three live channels (BEHAVIOR @covers, SUPPORT ledger+validator dispatch, STRUCTURAL-FENCE Boundary-Invariants anchor) for in-closeout ADRs, wired into gz check; ceremony gate swapped to _gate_closeout_proof on the EXECUTE→ATTESTATION edge with a 24h active-ceremony freshness window (operator ruling 2026-06-10) so parked closeouts don't redden gz check; fail-open seam in audit_skill_alignment fixed; ADR-0.0.41 OBPI-01 REQs tagged + OBPI-02/03 repointed; pool-ADR task-envelope carve-out gap closed (operator-approved cross-cut). 6034/6034 tests pass. Receipts: arb-step-unittest-52a09b6c81694ce4b265cfe4306dc5d6, arb-ruff-d95f254a34e3452c8433826e983da2a0, arb-step-typecheck-b1f37b70e0a149628a3ceec2d9723788, arb-step-mkdocs-8676fc556e1a43eda72c1712e2f8397b.
- Date: 2026-06-10

---

**Date Completed:** 2026-06-10

**Evidence Hash:** -
