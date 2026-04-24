---
id: OBPI-0.0.21-02-config-schema-paths-chores
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.21-02-config-schema-paths-chores: Config Schema — paths.chores

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- **Checklist Item:** #2 — Config schema: add `paths.chores` to `GzkitConfig` with default `.gzkit/chores`, mirroring `paths.skills`.

**Status:** Draft

## Objective

Add a single frozen Pydantic field `chores: str = ".gzkit/chores"` to `PathConfig` in `src/gzkit/config.py` adjacent to `skills` and `personas`, with REQ-derived unit tests proving the default resolves, user overrides round-trip, and `extra="forbid"` still rejects typos.

## Lane

**Heavy** — changes the `GzkitConfig` schema, a public contract consumed by every downstream project's `.gzkit.json`. Schema boundary is Heavy per `.gzkit/rules/cli.md`.

## Allowed Paths

- `src/gzkit/config.py` — add `chores` field to `PathConfig` class adjacent to `skills` and `personas`
- `tests/test_config.py` — REQ-derived unit tests for the new field
- `tests/test_config_paths.py` — path-specific tests if sibling path-resolution tests live here

## Denied Paths

- Every other file under `src/gzkit/` — this OBPI is a one-field schema addition
- `src/gzkit/commands/chores.py`, `chores_exec.py` — resolver OBPI-04 consumes the key
- `src/gzkit/commands/init_cmd.py` — scaffolder OBPI-05 owns wiring
- `pyproject.toml`, `features/**`, `docs/**`, `.gzkit/rules/**` — unrelated surfaces

## Requirements (FAIL-CLOSED)

1. The field MUST be added to `PathConfig` (frozen Pydantic per `.claude/rules/models.md`) adjacent to `skills` and `personas` at `src/gzkit/config.py:99-100` so reviewers see sibling parity at a glance.
2. The default value MUST be exactly `".gzkit/chores"` — any other value breaks OBPI-04's resolver contract and OBPI-05's scaffolder contract.
3. The field type MUST be `str` (not `Path`) to match existing siblings; consumers call `Path(...)` at the resolve site.
4. `ConfigDict(frozen=True, extra="forbid")` on `PathConfig` MUST remain unchanged. Do NOT relax `extra="forbid"`.
5. Tests MUST assert: (a) `GzkitConfig().paths.chores == ".gzkit/chores"`; (b) user-supplied `paths.chores` round-trips through `model_validate`; (c) a typo field under `paths` still raises `ValidationError`.
6. The field style (bare `str = "..."` vs `Field(default=..., description=...)`) MUST match the sibling style — do not introduce a new shape.
7. No unrelated config subtree (`VendorsConfig`, `ArbConfig`, etc.) may be touched.

> STOP-on-BLOCKERS:
> - If sibling `skills`/`personas` fields use `Field(..., description=...)`, match that exactly; if they use bare `str = "..."`, match that. Read before writing.
> - If `extra="forbid"` has been relaxed upstream, STOP — the regression test depends on it.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.claude/rules/models.md` — Pydantic discipline, `frozen=True`, `extra="forbid"`
- [ ] Parent ADR ADR-0.0.21 § Decision #4

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`

**Prerequisites:**

- [ ] `src/gzkit/config.py:99` sibling `skills` field exists (confirms the pattern)
- [ ] `tests/test_config.py` and `tests/test_config_paths.py` exist (sibling test patterns)

**Existing Code:**

- [ ] Read `src/gzkit/config.py:80-100` whole — full `PathConfig` shape
- [ ] Read at least one test in `tests/test_config.py` asserting `paths.skills` to mirror the pattern

## Quality Gates

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
- [ ] RED: `test_paths_chores_default_resolves` observes `AttributeError`.
- [ ] GREEN: add the field; test passes.
- [ ] RED: `test_paths_chores_preserves_user_override` observes failure or success — if success without code change, refactor the test to exercise a distinct code path.
- [ ] GREEN: passes.
- [ ] RED: `test_paths_extra_field_still_rejected` observes baseline (should pass without change — this is a regression guard, not a new behavior).
- [ ] `uv run gz test` fully green.

### Code Quality
- [ ] `uv run gz lint`
- [ ] `uv run gz typecheck` — ty diagnostics on `PathConfig` clean

### Gate 3 (Docs) — Heavy
- [ ] `uv run mkdocs build --strict` green

### Gate 4 (BDD) — Heavy
- [ ] Deferred to OBPI-07 (end-to-end scenario exercises this field transitively)

### Gate 5 (Human) — Heavy + Foundation
- [ ] Brief-level human attestation

## Verification

```bash
uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from gzkit.config import GzkitConfig; cfg = GzkitConfig(); assert cfg.paths.chores == '.gzkit/chores', cfg.paths.chores; print('paths.chores default OK')"

uv run -m unittest tests.test_config -v 2>&1 | grep -E "paths_chores|OK|FAIL"
uv run gz test
uv run gz typecheck
```

## Acceptance Criteria

- [ ] REQ-0.0.21-02-01: `GzkitConfig().paths.chores` resolves to `".gzkit/chores"` with no user config.
- [ ] REQ-0.0.21-02-02: A user-supplied `paths.chores` value in `.gzkit.json` round-trips through `GzkitConfig.load()`.
- [ ] REQ-0.0.21-02-03: `GzkitConfig.model_validate({"paths": {"chores_typo": "x"}})` raises `pydantic.ValidationError` (regression guard on `extra="forbid"`).
- [ ] REQ-0.0.21-02-04: The field's type annotation is `str` matching sibling `skills`/`personas` fields.
- [ ] REQ-0.0.21-02-05: `uv run gz typecheck` exits 0 after the change.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** 3 REQ-derived tests, RED→GREEN per increment
- [ ] **Code Quality:** lint + typecheck green
- [ ] **Gate 3:** docs build green
- [ ] **Gate 5:** human attestation
- [ ] **Value Narrative:** before — chores had no addressable config path; after — `paths.chores` joins the addressable surface set.
- [ ] **Key Proof:** one-liner showing `GzkitConfig().paths.chores == ".gzkit/chores"`.

## Evidence

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD)
```text
# paste test output
```

### Code Quality
```text
# paste lint + typecheck output
```

### Gate 5 (Human)
```text
# attestation text
```

### Value Narrative
Before: `PathConfig` knew about skills/personas/ceremonies but not chores — any consumer had to hard-code a path. After: `paths.chores` is addressable with the same shape as siblings.

### Key Proof

```bash
$ uv run python -c "from gzkit.config import GzkitConfig; print(GzkitConfig().paths.chores)"
.gzkit/chores
```

REQ coverage: 5/5 via `gz covers OBPI-0.0.21-02 --json` (`total_reqs=5, covered_reqs=5, coverage_percent=100.0`).

Quality receipts: lint `arb-ruff-078f98e2e8714bbe8d1d8c01f5afc54e`, types `arb-step-typecheck-41c98ead3e794d9d9378d50e5e095537`, tests `arb-step-unittest-686e4fed9b1a4858a92830d045940557` (3550 pass), docs `arb-step-mkdocs-5ba5cd9f8a2a4ef4b9fc10dde7a863ae`.

### Implementation Summary

- Files modified: `src/gzkit/config.py` (+1 line), `tests/test_config.py` (+4 tests)
- Tests added: 4 — `test_paths_chores_default_resolves`, `test_paths_chores_annotation_matches_siblings`, `test_paths_chores_preserves_user_override`, `test_paths_extra_field_still_rejected`
- Production diff: added `chores: str = ".gzkit/chores"` to `PathConfig` at `src/gzkit/config.py:101` adjacent to `skills`/`personas`, preserving bare-`str` sibling style and `ConfigDict(frozen=True, extra="forbid")`
- Date completed: 2026-04-24
- Attestation status: operator attested "completed"
- Defects noted: GHI #302 (gz test --obpi resolver bug, pre-existing, out of scope)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — paths.chores field landed on PathConfig with sibling parity to skills/personas (bare str, frozen, extra='forbid' preserved); 4 REQ-derived tests authored RED then GREEN, 5/5 REQ coverage via gz covers, 3550-test unit suite green, mkdocs strict green, typecheck clean. Receipts: lint arb-ruff-078f98e2e8714bbe8d1d8c01f5afc54e; types arb-step-typecheck-41c98ead3e794d9d9378d50e5e095537; tests arb-step-unittest-686e4fed9b1a4858a92830d045940557; docs arb-step-mkdocs-5ba5cd9f8a2a4ef4b9fc10dde7a863ae. Surfaced pre-existing defect GHI #302 (gz test --obpi resolver).
- Date: 2026-04-24

---

**Brief Status:** Completed

**Date Completed:** 2026-04-24

**Evidence Hash:** -
