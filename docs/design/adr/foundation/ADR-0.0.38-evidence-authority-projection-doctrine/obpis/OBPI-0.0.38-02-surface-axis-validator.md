---
id: OBPI-0.0.38-02-surface-axis-validator
parent: ADR-0.0.38-evidence-authority-projection-doctrine
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.38-02-surface-axis-validator: Surface-Axis Validator Scope

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.38-evidence-authority-projection-doctrine/ADR-0.0.38-evidence-authority-projection-doctrine.md`
- **Checklist Item:** #2 — `surface-axis-validator` — Implement `gz validate --surface-axis` (Heavy-lane CLI surface) — fail-closes on missing declarations, on Projection-as-gate-input call shapes, and on Evidentiary→Authoritative promotion without foundation-kind ADR.

**Status:** Draft

## Objective

Implement `gz validate --surface-axis` as a new validator scope: enumerate every gzkit surface from the canonical inventory (skills, rules, code-level receipt-emitting modules, registered validator scopes, declared CLI verbs); fail-close (exit 3) on (a) any surface lacking an axis declaration site, (b) any call-graph pattern treating a Projection-tagged surface as fail-closed gate input, (c) any commit promoting a previously-Evidentiary surface to Authoritative without a referenced foundation-kind ADR. Land the BDD acceptance scenarios, the manpage update, and the runbook + governance-runbook entries that the Heavy-lane gate-3/4 covenant requires.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.38-evidence-authority-projection-doctrine/**` — parent ADR package
- `src/gzkit/governance/trust_audits.py` — extend with `audit_surface_axis_declarations`, `audit_projection_consumed_as_gate`, `audit_evidentiary_to_authoritative_promotion`
- `src/gzkit/governance/surface_axis.py` — extend with surface enumeration helpers (`enumerate_surfaces()`, `discover_call_sites()`)
- `src/gzkit/governance/surface_axis_inventory.py` (new) — canonical inventory enumerator (skill files, rule files, code-level modules, validator scopes, CLI verbs)
- `src/gzkit/governance/surface_axis_callgraph.py` (new) — Projection-as-gate-input pattern detector (analyzes `.returncode`, exit-code branching, `passed=False` reads against Projection-tagged surfaces)
- `src/gzkit/cli/parser_validate.py` (or active equivalent) — register `--surface-axis` flag
- `src/gzkit/commands/validate.py` — wire the new scope into the validate dispatcher
- `tests/governance/test_surface_axis_validator.py` (new) — REQ-derived assertions
- `tests/governance/test_surface_axis_inventory.py` (new) — surface enumeration assertions
- `tests/governance/test_surface_axis_callgraph.py` (new) — Projection-as-gate detector assertions
- `features/governance/surface_axis.feature` (new) — BDD acceptance scenarios tagged `@REQ-0.0.38-02-NN`
- `docs/user/manpages/gz-validate.md` — document `--surface-axis` scope
- `docs/user/runbook.md` — operator workflow entry
- `docs/governance/governance_runbook.md` — governance-maintainer workflow entry
- `data/surface_axis_waivers.json` (new) — explicit waiver list for legitimate Projection-as-input cases (parallel to `_UTF8_PIPE_WAIVERS`)
- `src/gzkit/arb/validator.py` — register `arb-step-surface-axis-*` slot in `CANONICAL_STEP_COMMANDS`

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/rules/evidence-vs-authority.md` — rule body authored under OBPI-0.0.38-01; this OBPI may not edit it
- Existing skill axis declarations — backfill is OBPI-0.0.38-03's scope; this OBPI may only add new declarations to surfaces it itself authors (the new validator modules and the new feature file)
- `artifacts/audits/surface-axis-*.md` — produced under OBPI-0.0.38-03
- `src/gzkit/governance/surface_axis.py` SurfaceAxis enum + base helpers — landed under OBPI-0.0.38-01; this OBPI may extend with enumeration/discovery helpers but may not modify the enum definition
- New runtime dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz validate --surface-axis` is a registered scope at `src/gzkit/cli/parser_validate.py` and dispatches to `src/gzkit/commands/validate.py`. The scope is included in the default scope set for `uv run gz check` (Heavy-lane gate path), gated by an opt-out only for the duration of OBPI-0.0.38-03's retroactive classification — the opt-out is removed in -03's terminal commit.
2. REQUIREMENT: The validator audits three orthogonal failure classes, each in a separately-named function in `src/gzkit/governance/trust_audits.py`:
   (a) `audit_surface_axis_declarations` — every surface in the canonical inventory has an axis declaration site populated;
   (b) `audit_projection_consumed_as_gate` — no caller in `src/gzkit/**` or `.gzkit/skills/**` treats a Projection-tagged surface as fail-closed gate input;
   (c) `audit_evidentiary_to_authoritative_promotion` — git-log inspection: a commit that flips a surface's declared axis from `evidentiary` to `authoritative` references a foundation-kind ADR in its body.
3. REQUIREMENT: `surface_axis_inventory.enumerate_surfaces()` returns a frozen Pydantic model `SurfaceInventory` listing every: (i) skill under `.gzkit/skills/**/SKILL.md`; (ii) rule under `.gzkit/rules/**.md`; (iii) Python module under `src/gzkit/**/*.py` whose source contains the canonical `SURFACE_AXIS` constant or imports `arb` receipt-emit helpers; (iv) registered validator scope in `parser_validate.py`; (v) CLI verb in `parser_*.py` files. The enumeration is deterministic — same repo state produces same inventory.
4. REQUIREMENT: `surface_axis_callgraph.discover_projection_gate_consumers()` walks `src/gzkit/**` and `.gzkit/skills/**` AST/text and flags call shapes consuming a Projection-tagged surface as fail-closed input. Detected patterns include but are not limited to:
   (a) `subprocess.run(["gz", "<projection-verb>", ...]).returncode` branched on non-zero;
   (b) reading a Projection-tagged module's emit and treating its `passed` field as gate-binding;
   (c) skill body asserting "if `gz status` shows X, then halt" without a tracing-to-Layer-2 step.
5. REQUIREMENT: The validator emits exit code 3 on any unwaived violation per `.gzkit/rules/cli.md` (Policy Breach). Default human-readable output is a Rich table per `.claude/rules/tool-skill-runbook-alignment.md` Invariant 3 (Output Contract). `--json` emits machine-readable shape consumed by ARB / reconciliation tooling.
6. REQUIREMENT: `data/surface_axis_waivers.json` is a frozen Pydantic-validated registry naming explicit waivers (legitimate Projection-as-input cases — e.g., a CLI smoke-test that genuinely wants to run a status command and exit-code-check it as a sanity gate, with the named-and-cited reason). Waivers require a `reason` field, a `cited_authority` field (foundation ADR or operator decision-record reference), and a `expires_after` field (date or `null` for permanent). Adding a waiver requires the brief authoring it to declare `sensitivity: security` if the waiver covers a security-surface-overlapping path; otherwise default sensitivity. The waiver registry's own schema enforces this.
7. REQUIREMENT: `tests/governance/test_surface_axis_validator.py` asserts each of the three audit functions returns `passed=True` on a fixture repo with all surfaces correctly classified, and returns explicit failure with named-violation evidence on each of the three failure modes. Fixtures must include at least one Projection-as-gate-input violation, one missing-declaration violation, and one Evidentiary→Authoritative promotion violation.
8. REQUIREMENT: `features/governance/surface_axis.feature` defines the Gate 4 BDD acceptance scenarios — at minimum: the validator passes on a clean fixture; the validator fails-closed (exit 3) on each of the three failure classes; the validator honors waivers from `data/surface_axis_waivers.json`; the `--json` output shape matches the documented schema. Tags use `@REQ-0.0.38-02-NN`.
9. REQUIREMENT: `docs/user/manpages/gz-validate.md` documents the new `--surface-axis` scope, including an EXAMPLES section with real CLI output (per `.gzkit/rules/cli.md` § "Adding CLI Features" → "New Subcommand (Heavy Lane)" item 4).
10. REQUIREMENT: `docs/user/runbook.md` and `docs/governance/governance_runbook.md` add entries for `gz validate --surface-axis` per `.gzkit/rules/gate5-runbook-code-covenant.md`.
11. REQUIREMENT: `gz cli audit` exits 0 with the new `validate --surface-axis` scope appearing in the manpage, command doc index, and SKILL coverage roster, per `.gzkit/rules/cli.md` § "Consistency".
12. REQUIREMENT: The validator MUST NOT modify any existing surface's axis declaration — it reads-only and reports. Surface declaration edits are OBPI-0.0.38-03's exclusive scope.
13. REQUIREMENT: NEVER reduce the validator's fail-closed semantic for "ergonomic reasons" — a violation is exit 3, full stop. The only escape is the explicit waiver registry. Authoring a `--ignore-violations` flag or a "warn-only" mode is a doctrine violation per AGENTS.md § Anti-Vibing Mantra.
14. REQUIREMENT: The validator's three audit functions MUST each fit within `.gzkit/rules/pythonic.md` size limits (≤50 lines/function). If an audit's logic exceeds 50 lines, decompose into private helpers in the same module rather than relaxing the limit.
15. REQUIREMENT: The validator emits an `arb-step-surface-axis-*` receipt under canonical-step provenance per AGENTS.md § Attestation. The receipt name is added to `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` so that attestation citation works for OBPI-0.0.38-02 closeout and downstream attestations.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.38-evidence-authority-projection-doctrine/ADR-0.0.38-evidence-authority-projection-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.38-evidence-authority-projection-doctrine/ADR-0.0.38-evidence-authority-projection-doctrine.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.38-evidence-authority-projection-doctrine/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

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
# OBPI-specific tests (REQ-derived)
uv run -m unittest tests/governance/test_surface_axis_validator.py -v
uv run -m unittest tests/governance/test_surface_axis_inventory.py -v
uv run -m unittest tests/governance/test_surface_axis_callgraph.py -v

# BDD scenarios (Gate 4)
uv run -m behave features/governance/surface_axis.feature

# CLI alignment + manpage coverage (.gzkit/rules/cli.md § Consistency)
uv run gz cli audit
uv run gz validate --cli-alignment

# The validator runs against itself — must pass on the clean repo at OBPI close
uv run gz validate --surface-axis
uv run gz validate --surface-axis --json

# Standard heavy-lane gates
uv run gz lint
uv run gz typecheck
uv run gz validate --documents
uv run mkdocs build --strict

# ARB-wrapped receipt for attestation
uv run gz arb step --name surface-axis -- uv run gz validate --surface-axis

# Confirm canonical artifacts exist
test -f src/gzkit/governance/surface_axis_inventory.py
test -f src/gzkit/governance/surface_axis_callgraph.py
test -f data/surface_axis_waivers.json
test -f features/governance/surface_axis.feature
test -f docs/user/manpages/gz-validate.md
grep -q "surface-axis" docs/user/runbook.md
grep -q "surface-axis" docs/governance/governance_runbook.md
grep -q "arb-step-surface-axis" src/gzkit/arb/validator.py
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. The closeout
     ceremony walkthrough harvests this section (parser-validated;
     unregistered verbs are dropped). Prefer real paths and arguments
     over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.38-02-01: Given a clean repo with all surfaces classified, when `uv run gz validate --surface-axis` runs, then exit code is 0 and stdout contains a Rich table summarizing surfaces by axis.
- [ ] REQ-0.0.38-02-02: Given a fixture surface lacking an axis declaration, when the validator runs, then exit code is 3 and the diagnostic names the surface and the missing declaration site (frontmatter / body marker / module constant / scope registration / CLI registration).
- [ ] REQ-0.0.38-02-03: Given a fixture call site treating a Projection-tagged surface as fail-closed gate input, when the validator runs, then exit code is 3 and the diagnostic names the caller path, the Projection surface, and the gate-shape pattern detected.
- [ ] REQ-0.0.38-02-04: Given a git history with a commit flipping a surface's `surface_axis` from `evidentiary` to `authoritative` without a foundation-ADR reference in the commit body, when the validator runs, then exit code is 3 and the diagnostic names the commit hash, the surface, and the missing-ADR-reference field.
- [ ] REQ-0.0.38-02-05: Given a waiver in `data/surface_axis_waivers.json` covering a specific Projection-as-input call site with a `reason`, `cited_authority`, and unexpired `expires_after`, when the validator runs, then the violation is suppressed and stdout names the waiver in a "waived" section.
- [ ] REQ-0.0.38-02-06: Given `--json` flag, when the validator runs, then stdout is JSON-parseable and the schema matches the documented shape (`{scope: "surface-axis", passed: bool, violations: [...], waivers_applied: [...]}`).
- [ ] REQ-0.0.38-02-07: Given `gz cli audit` and `gz validate --cli-alignment`, when run after the new scope lands, then both exit 0 with the new scope appearing in manpage + command doc index + SKILL coverage roster.
- [ ] REQ-0.0.38-02-08: Given `features/governance/surface_axis.feature`, when `uv run -m behave` runs against it, then all scenarios pass and each carries a `@REQ-0.0.38-02-NN` tag covering the requirement set above.
- [ ] REQ-0.0.38-02-09: Given the Pythonic size-limit rule (≤50 lines/function), when `uv run gz lint` runs against the validator modules, then no function exceeds 50 lines.
- [ ] REQ-0.0.38-02-10: Given `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py`, when read, then it includes `arb-step-surface-axis-*` so attestation citations using this receipt prefix validate.
- [ ] REQ-0.0.38-02-11: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no axis declarations are added to existing surfaces (skills, rules, modules) other than the new modules this OBPI itself authors.
- [ ] REQ-0.0.38-02-12: Given the validator's MUST-NOT-degrade requirement, when the validator's source is read, then no `--ignore-violations`, `--warn-only`, or equivalent escape flag exists. Waivers are the sole escape.

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

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
