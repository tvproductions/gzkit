---
id: OBPI-0.0.33-02-surface-weight-validator
parent: ADR-0.0.33-agent-control-surface-fidelity
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.33-02-surface-weight-validator: Surface Weight Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- **Checklist Item:** #2 - "OBPI-0.0.33-02: Surface-weight validator (`gz validate --surface-weight`) — snapshot file, waiver schema, fail-closed direction-binding, provisional warning bands, recalibration commitment"

**Status:** Completed

## Objective

Implement `gz validate --surface-weight` (ADR-0.0.33 Invariant 2): compute the
per-turn surface corpus line count (`AGENTS.md`, `CLAUDE.md`,
`.claude/rules/**`), read the direction-binding floor from
`data/surface_weight_floor.json`, and enforce band-based exit codes (green
≤1800 pass; yellow 1801–2200 fail unless an active waiver in
`data/surface_weight_waivers.json` covers the delta; red >2200 fail with no
waiver dispensation). Detect floor drift when the snapshot timestamp predates
the most recent ledger `surface_weight_recalibrated` event by >24h. Re-export
`validate_surface_weight` from the `gzkit.governance.trust_audits` package and
wire the flag into the `gz validate` parser and dispatch surfaces.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/**` — parent ADR package scope
- `src/gzkit/governance/trust_audits/surface_weight.py` — validator implementation (new module)
- `src/gzkit/governance/trust_audits/__init__.py` — package re-export of `validate_surface_weight`
- `src/gzkit/cli/parser_maintenance.py` — `gz validate --surface-weight` flag registration and dispatch
- `tests/governance/test_surface_weight.py` — Gate-2 TDD asset
- `data/surface_weight_floor.json` — initial snapshot (created in this OBPI)
- `data/surface_weight_waivers.json` — empty waiver schema bootstrap (created in this OBPI)
- `docs/user/manpages/validate.md` — manpage entry for the new flag

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New runtime dependencies (stdlib line-count only)
- Composite wiring into `--surface-fidelity` (owned by OBPI-05)
- Other invariants' validator modules
- Recalibration of the warning bands themselves (band values come from the ADR Decision; this OBPI only enforces them)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

This OBPI implements parent-ADR Invariant 2 only. The other three invariants
are out of scope for this brief.

1. REQUIREMENT: **Direction-binding enforcement.** `gz validate --surface-weight` computes the current line count of the per-turn surface corpus (`AGENTS.md`, `CLAUDE.md`, files under `.claude/rules/**`), reads the floor from `data/surface_weight_floor.json`, and asserts current ≤ floor. Growth past the snapshot is fail-closed.
2. REQUIREMENT: **Provisional warning bands.** Green ≤ 1800 (pass), yellow 1801–2200 (exit 0 with warning unless waiver entry covers the delta), red > 2200 (exit 3, no waiver dispensation). Band values are pinned by the parent ADR Decision; ALWAYS read from a single constant block in `surface_weight.py`.
3. REQUIREMENT: **Waiver schema is structural.** `data/surface_weight_waivers.json` MUST validate against a JSON Schema declared in the validator module: required keys `waiver_id`, `expires`, `delta_lines`, `attestor`, `reason`. An expired waiver NEVER counts. NEVER hand-edit waivers without an attested recalibration receipt.
4. REQUIREMENT: **Recalibration is a ledger event.** A floor recalibration MUST update `data/surface_weight_floor.json` AND emit a `surface_weight_recalibrated` event to the ledger via `gz adr emit-receipt`. NEVER allow silent floor mutation; the validator MUST reject a floor whose timestamp predates the most recent recalibration event by more than 24h (drift detection).
5. REQUIREMENT: **Exit code discipline.** Exit 0 (clean), exit 0 (yellow band with active waiver), exit 3 (yellow band with no waiver), exit 3 (red band), exit 3 (floor drift detected). NEVER conflate yellow-without-waiver with green.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Parent ADR file exists: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- [ ] Per-turn surface corpus exists: `AGENTS.md`, `CLAUDE.md`, `.claude/rules/`
- [ ] Trust-audits package exists: `src/gzkit/governance/trust_audits/__init__.py`
- [ ] CLI parser exists: `src/gzkit/cli/parser_maintenance.py`
- [ ] `data/` directory exists (snapshot and waivers will be created in this OBPI)

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz validate --surface-weight                    # must exit 0 on a clean tree against snapshot
uv run -m unittest tests.governance.test_surface_weight -v
test -f src/gzkit/governance/trust_audits/surface_weight.py
test -f data/surface_weight_floor.json
test -f data/surface_weight_waivers.json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.33-02-01: Given the per-turn surface corpus at or below the snapshot floor, when `gz validate --surface-weight` runs, then it exits 0 with no warning.
- [ ] REQ-0.0.33-02-02: Given a corpus line count in the yellow band (1801–2200) with no active waiver covering the delta, when `gz validate --surface-weight` runs, then it exits 3 with a `ValidationError` of `type="surface_weight"` naming the delta.
- [ ] REQ-0.0.33-02-03: Given a corpus line count in the red band (>2200), when `gz validate --surface-weight` runs, then it exits 3 regardless of waiver entries (no dispensation in red).
- [ ] REQ-0.0.33-02-04: Given `data/surface_weight_waivers.json` containing an expired waiver entry, when `gz validate --surface-weight` runs, then the expired entry is rejected and the delta it covered is treated as un-waived.
- [ ] REQ-0.0.33-02-05: Given a floor snapshot whose timestamp predates the most recent ledger `surface_weight_recalibrated` event by >24h, when `gz validate --surface-weight` runs, then it exits 3 with a `type="surface_weight"` error citing floor drift.
- [ ] REQ-0.0.33-02-06: Given the validator module, when imported, then `gzkit.governance.trust_audits.validate_surface_weight` resolves and matches the package re-export pattern.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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


```
$ uv run gz validate --surface-weight
Validated: surface_weight

✓ All validations passed (1 scopes).
$ echo $?
0
```

Corpus at floor (1859 = 1859). ARB receipts: arb-ruff-2e658d3f60624f66bc7b499782cc1d00, arb-step-typecheck-24b75d83148040d88ff7b8acc467c3c2, arb-step-unittest-ad8301ce3c0644f68db4316a0b4b3284 (5054/5054 full sweep), arb-step-unittest-2b6366187de04fbfae15a1f3dd39462e (24/24 scoped), arb-step-mkdocs-4a1de6014a16498981edcb2ccc9a6bd5.

### Implementation Summary


- Files created: `src/gzkit/governance/trust_audits/surface_weight.py` (190-line validator), `tests/governance/test_surface_weight.py` (24 tests across 6 classes), `data/surface_weight_floor.json` (snapshot 1859 lines), `data/surface_weight_waivers.json` (empty bootstrap)
- Files modified: `src/gzkit/governance/trust_audits/__init__.py` (re-export validate_surface_weight), `src/gzkit/cli/parser_maintenance.py` (--surface-weight flag + dispatch), `src/gzkit/commands/validate_cmd.py` (param wiring + opt_in_scopes + _POLICY_BREACH_ERROR_TYPES), `docs/user/manpages/validate.md` (usage + section), `data/behave_coverage_waivers.json` (deferred-to-OBPI-05 rationale)
- Tests added: 24 tests covering all 6 REQs (REQ coverage 100% via gz covers, uncovered_reqs: 0)
- Date completed: 2026-05-15
- Attestation status: operator-verbatim-conversational ("attest completed")
- Defects noted: discovered + fixed mid-implementation — _resolve_scopes opt_in_scopes and _POLICY_BREACH_ERROR_TYPES both lacked "surface_weight"; remediated in same OBPI commit

## Demo

```bash
uv run gz validate --surface-weight
```

Runs the surface-weight audit: each per-turn surface file (`AGENTS.md`, `CLAUDE.md`, `.claude/rules/*.md`) must hold its share of the direction-binding floor recorded in `data/surface_weight_floor.json`. Exits 0 when no file is below its snapshot floor; exits 3 when a directive surface has been silently thinned.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — Stage 4 evidence accepted; 24/24 scoped tests, 5054/5054 full sweep, ruff clean, ty clean, mkdocs strict clean; gz validate --surface-weight returns exit 0 on the current 1859-line corpus snapshot; 100% REQ coverage via gz covers; ARB receipts arb-ruff-2e658d3f60624f66bc7b499782cc1d00, arb-step-typecheck-24b75d83148040d88ff7b8acc467c3c2, arb-step-unittest-ad8301ce3c0644f68db4316a0b4b3284, arb-step-unittest-2b6366187de04fbfae15a1f3dd39462e, arb-step-mkdocs-4a1de6014a16498981edcb2ccc9a6bd5.
- Date: 2026-05-15

---

**Brief Status:** Draft

**Date Completed:** 2026-05-15

**Evidence Hash:** -
