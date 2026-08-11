---
id: OBPI-0.36.0-02-cross-family-transport
parent: ADR-0.36.0-convergence-moment-cross-family-critic
item: 2
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/second_opinion_transport.py
  - tests/governance/test_second_opinion_transport.py
  - docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**
reqs:
  - REQ-0.36.0-02-01
  - REQ-0.36.0-02-02
  - REQ-0.36.0-02-03
  - REQ-0.36.0-02-04
verification:
  - uv run gz validate --documents
  - uv run -m unittest tests.governance.test_second_opinion_transport -v
  - uv run gz validate --req-kind-discipline
---

# OBPI-0.36.0-02-cross-family-transport: Cross-Family Transport

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- **Checklist Item:** #2 - "OBPI-0.36.0-02: **cross-family-transport** — The composed ARB-wrapped `codex exec --sandbox read-only` transport carrying a decision, returning a schema-pinned verdict, with the cross-vendor property proven from the receipt's `step.command` argv"

**Status:** Draft

## Objective

Compose the cross-vendor transport from surfaces that already ship —
`gz arb step --name adversary -- codex exec --sandbox read-only <decision>` —
and make the cross-family property **provable from the ARB receipt's
`step.command` argv** rather than asserted in prose.

Done looks like: a receipt whose argv head is a Claude-family binary is
**rejected as non-cross-vendor**, so "we asked an adversary" can never be true in
narration and false in fact. This is the ADR's own lesson turned into a
mechanism — R4 was ruled on the belief that a shipped plugin already supplied
this transport, and § R4 transport correction records that the belief was
measurably wrong while the ruling stood. The receipt is the antidote to
believing a surface does what its name implies.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/second_opinion_transport.py` — the composed transport. Verified convention: flat modules under `src/gzkit/` (`tasks.py`, `events.py`, `handoff_api.py`).
- `tests/governance/test_second_opinion_transport.py` — covering tests. Verified convention: `tests/governance/*.py`.
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/**` — this brief and its parent ADR.

## Denied Paths

- `src/gzkit/cli/**` — Boundary Invariant #2: the transport composes `gz arb step`; it does not add a verb. A new verb is a CLI-contract change needing its own ceremony, which § Target Scope names circular here.
- `src/gzkit/arb/**` — `gz arb step` is consumed as shipped. Editing ARB to suit the critic would make the receipt evidence circular: the thing being proven would own its own prover.
- `src/gzkit/commands/obpi_complete_adversarial.py` — Step 4b. Boundary Invariant #1; read-only reference only.
- `.claude/hooks/**`, `.claude/settings.json` — OBPI-09, and it lands dark.
- New runtime dependencies — the transport shells out to an installed binary (`codex-cli 0.147.0`, verified on PATH) via stdlib `subprocess`.

## Requirements (FAIL-CLOSED)

1. ALWAYS: Wrap the adversary invocation in `gz arb step` so a receipt exists. An adversary run that emits no receipt did not happen, per `AGENTS.md` § Attestation.
2. ALWAYS: Prove the cross-vendor property from the receipt's `step.command` argv head — verified present at `src/gzkit/arb/step_reporter.py:111` (`"command": list(cmd)`). Reuse the existing predicate shape at `obpi_complete_adversarial.py::_receipt_proves_cross_vendor` rather than authoring a second one (hexagonal rule 8, prefer subsumption).
3. NEVER: Accept a declared adversary name as proof of cross-family. The declaration is the claim; the argv is the evidence.
4. ALWAYS: Pass `--sandbox read-only`. The critic reads the raw surface and must not be able to mutate it.
5. NEVER: Send a branch diff. § R4 transport correction is explicit that the built-in `adversarial-review` reviews *branch diffs, not decisions*; this transport carries a **decision**.
6. NEVER: Return an empty verdict on transport failure. § R4 transport correction records that the `codex:codex-rescue` forwarder is contracted to *"return nothing"* on failure — a silent empty return is indistinguishable from "the critic found nothing wrong", which is the exact inversion this ADR exists to prevent. Failure MUST surface as an error.
7. NEVER: Add a `gz` verb or edit `src/gzkit/arb/**`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR § R4 transport correction and § Mechanics (Transport row) — the measured basis for shelling out.
- [ ] Parent ADR § Boundary Invariants #2 — no new `gz` verb.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Attestation — ARB receipts are the evidence channel; a bare command emits none.
- [ ] `.gzkit/rules/cross-platform.md` § Subprocess reads — text-mode captures MUST pass `errors="replace"`.
- [ ] `.gzkit/rules/hexagonal-architecture.md` — the vendor binary is an external technology and belongs behind an adapter seam.

**Context:**

- [ ] OBPI-0.36.0-01 — supplies the verdict schema this transport returns against.
- [ ] OBPI-0.36.0-03/04/09 — the three doors that call this transport.

**Prerequisites (check existence, STOP if missing):**

- [ ] `codex` is on PATH — verified: `/opt/homebrew/bin/codex`, `codex-cli 0.147.0`.
- [ ] `src/gzkit/arb/step_reporter.py` exists and records the argv — verified at line 111.
- [ ] `src/gzkit/commands/obpi_complete_adversarial.py` carries `_receipt_proves_cross_vendor` and `_receipt_binary_name` — verified at lines 97 and 87.
- [ ] OBPI-0.36.0-01's verdict schema is landed, or this brief's tests stub it explicitly.
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/second_opinion_transport.py`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/governance/test_second_opinion_transport.py`

**Existing Code (understand current state):**

- [ ] `src/gzkit/arb/step_reporter.py` — read `run_step` end to end for the receipt envelope and the `command` field.
- [ ] `src/gzkit/commands/obpi_complete_adversarial.py:75-118` — `_is_cross_vendor_adversary`, `_receipt_binary_name`, `_receipt_proves_cross_vendor`. This is the predicate to reuse; read it before writing a new one.
- [ ] `src/gzkit/quality.py::run_command` — the named good pattern for a text-mode subprocess capture (`errors="replace"`).

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

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.governance.test_second_opinion_transport -v
uv run gz validate --req-kind-discipline
uv run gz arb validate
```

## Demo

```bash
# A real cross-family run, receipt-backed
uv run gz arb step --name adversary -- codex exec --sandbox read-only "Refute: the settled-rulings clip repair should have healed the abridged twins too."

# The receipt proves the vendor from argv, not from a declared name
uv run gz arb validate
```

## Acceptance Criteria

- [ ] REQ-0.36.0-02-01 [BEHAVIOR]: Given a completed transport invocation, when its ARB receipt is read, then `step.command` carries the argv `codex exec --sandbox read-only` and the cross-vendor predicate returns true from that argv alone.
- [ ] REQ-0.36.0-02-02 [BEHAVIOR]: Given a receipt whose argv head is a Claude-family binary, when the cross-vendor predicate runs, then it returns false and the transport refuses the verdict — a declared adversary name never substitutes for the argv.
- [ ] REQ-0.36.0-02-03 [BEHAVIOR]: Given a transport failure (non-zero exit, empty stdout, or unparseable output), when the caller reads the result, then an error surfaces — a silent empty verdict indistinguishable from "nothing wrong" is refused.
- [ ] REQ-0.36.0-02-04 [STRUCTURAL-FENCE]: No `gz` verb is added and `src/gzkit/arb/**` is unmodified across the delivered set — parent ADR § Boundary Invariants #2 (OBPI-02, OBPI-03, OBPI-04).

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

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
