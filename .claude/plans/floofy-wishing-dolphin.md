# Implementation Plan — OBPI-0.0.37-20 — Setpoint Declaration + Coherence Validator

**OBPI:** `OBPI-0.0.37-20-setpoint-declaration-coherence-validator`
**Parent ADR:** ADR-0.0.37 (foundation/heavy) · **Lane:** Heavy · **Gate 5 human attestation mandatory (no self-close)**

## Context

ADR-0.0.37's re-aligned CMS pipeline (§ Decision Re-Alignment, 2026-06-03) defines a **setpoint thermostat**: *"Temperature = compression setpoint … A declared parsimony target per (surface × consumer), stored in the existing `data/vendor-manifest.json` `content_type_temperatures` map."* OBPI-20 delivers the **declaration surface + its coherence gate** — not the composer (OBPI-21), rendition store/playback (OBPI-22), or invariant tier (OBPI-23).

Today the substrate is half-present: `src/gzkit/content/vendors.py:119` already has a fail-closed `temperature_for(content_type, vendor, *, project_root)` accessor, and `data/vendor-manifest.json` already has both `content_type_routes` (8 content types) and `content_type_temperatures` (AgentContract only). Nothing yet asserts that every routed `(surface × consumer)` pair has a declared, legal setpoint — so the composer that consumes the thermostat could be built over a hollow declaration. This OBPI closes that gap with a fail-closed `gz validate --setpoint-coherence` scope and pins the accessor's fail-closed contract with a test.

## Open Implementation Decision (requires operator ratification at Gate 5)

`content_type_routes` routes 8 content types; `content_type_temperatures` declares setpoints for **only `AgentContract`**. The forward-coherence rule (every routed pair needs a setpoint) therefore fails-closed against current canon until the other 7 pairs (`Bullet`, `Chore`, `Handoff`, `Persona`, `Rule`, `Scenario`, `Skill` — all → `claude`) are declared. **Recommendation A (this plan's default):** declare a setpoint for every routed pair, with non-`AgentContract` surfaces set to `heavy` (the fullest-retention tier = no-compression sentinel; the composer only compresses `AgentContract`). Alternative B (narrow the coherence domain to compression targets only) is recorded in the brief. Operator confirms A or redirects to B at Gate 5 before the manifest edit is final.

## Approach (TDD, mirrors the existing `--vendor-manifest` validator)

### Creates these files (net-new)

- `src/gzkit/governance/trust_audits/setpoint_coherence.py` — **CREATE** the validator scope module
- `tests/governance/test_setpoint_coherence.py` — **CREATE** unit tests (REQ-01/02/03)
- `features/setpoint_coherence.feature` — **CREATE** BDD scenario (Gate 4)
- `features/steps/setpoint_coherence_steps.py` — **CREATE** step definitions

### Step 1 — Validator module (Gate 2 RED→GREEN)

Model directly on `src/gzkit/governance/trust_audits/vendor_manifest.py`. New `validate_setpoint_coherence(project_root: Path) -> list[ValidationError]`:
1. Load `data/vendor-manifest.json` (fail-closed if missing/malformed — same shape as `vendor_manifest.py`).
2. Read `content_type_routes` and `content_type_temperatures`.
3. For each `(content_type, vendor)` in routes, if it has no entry in temperatures → `ValidationError(type="setpoint_coherence", artifact="data/vendor-manifest.json", message=…)` (REQ-01).
4. For each declared setpoint token, if not in `{lite, medium, heavy}` → `ValidationError` (REQ-02). (Legal enum lives in `src/gzkit/schemas/vendor_manifest.json`; read it, do not edit it.)
5. Return `[]` when every routed pair has a legal setpoint (REQ-03).

`ValidationError` is `gzkit.core.validation_rules.ValidationError(type, artifact, message, field=)`.

### Step 2 — Wire the CLI scope

- `src/gzkit/governance/trust_audits/__init__.py` — re-export `validate_setpoint_coherence` (mirror `validate_vendor_manifest` / `validate_invariant_coherence`).
- `src/gzkit/cli/parser_maintenance.py` — register `--setpoint-coherence` (`dest="check_setpoint_coherence"`, `action="store_true"`), modeled on `--invariant-coherence` (line ~601) / `--vendor-manifest` (line ~657).
- `src/gzkit/commands/validate_cmd.py` — add `check_setpoint_coherence: bool` through the param chain, a `_setpoint_coherence_runner(project_root)` (mirror `_invariant_coherence_runner`, lines ~309/320–324), the dispatch-table entry, and the scope-name registry entry. **Do not** add to the default `gz check` scope (deferred operator decision).

### Step 3 — Declare missing setpoints (per ratified decision A)

`data/vendor-manifest.json` — add `content_type_temperatures` entries for the 7 non-`AgentContract` routed pairs at `heavy`, so `gz validate --setpoint-coherence` exits 0 (REQ-03 green against real canon). Held pending Gate 5 ratification.

### Step 4 — Accessor pin (REQ-04)

`tests/content/test_vendor_manifest.py` — add a `@covers(REQ-0.0.37-20-04)` test asserting `temperature_for` raises `ValueError` on an undeclared pair. Re-derive the assertion from the REQ (fail-closed semantics); if an equivalent assertion already exists, pin via the legitimate overlay marker rather than cosmetic backfill (`.claude/rules/adr-audit.md`).

### Step 5 — Docs (Gate 3) + BDD (Gate 4)

- `docs/user/manpages/validate.md` — document the `--setpoint-coherence` scope (REQ-05). Then `gz validate --cli-alignment` must resolve it (exit 0), and `gz cli audit` must stay green.
- `features/setpoint_coherence.feature` + steps — coherent-manifest (exit 0), missing-setpoint (exit 3), illegal-token (exit 3) scenarios.

## Critical files

| File | Change |
|---|---|
| `src/gzkit/governance/trust_audits/setpoint_coherence.py` | NEW validator |
| `src/gzkit/governance/trust_audits/__init__.py` | re-export |
| `src/gzkit/cli/parser_maintenance.py` | `--setpoint-coherence` flag |
| `src/gzkit/commands/validate_cmd.py` | runner + dispatch + scope registry |
| `data/vendor-manifest.json` | declare 7 missing setpoints (decision A) |
| `tests/governance/test_setpoint_coherence.py` | NEW REQ-01/02/03 tests |
| `tests/content/test_vendor_manifest.py` | REQ-04 accessor pin |
| `features/setpoint_coherence.feature` + steps | NEW BDD |
| `docs/user/manpages/validate.md` | scope docs (REQ-05) |

## Verification (end-to-end)

```bash
uv run gz validate --setpoint-coherence     # exit 0 on coherent canon; 3 on gap/illegal token
uv run gz validate --cli-alignment           # REQ-05: manpage reference resolves
uv run gz cli audit                           # new verb covered across manpage/doc/index
uv run gz lint && uv run gz typecheck && uv run gz test
uv run mkdocs build --strict
uv run -m behave features/setpoint_coherence.feature
```

Then the contract-bearing pipeline: `uv run gz obpi pipeline OBPI-0.0.37-20` (verify → ceremony → guarded `gz git-sync --apply --lint --test` → completion), **pausing at Gate 5** for operator attestation. Foundation/heavy → no self-close.

## Out of scope

Composer (OBPI-21), rendition store/playback (OBPI-22), invariant tier (OBPI-23), adding `--setpoint-coherence` to default `gz check`, editing the schema token enum. The 53 sibling-ADR scope-collisions reported by `gz plan audit` are advisory (every validator scope edits the same four CLI-wiring files); not a blocker.
