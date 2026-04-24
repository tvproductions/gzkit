# OBPI-0.0.21-02 — Config Schema: `paths.chores`

## Context

Parent ADR-0.0.21 is folding chores into the gzkit governance surface. This
OBPI is the schema-layer increment: add a single frozen Pydantic field
`chores: str = ".gzkit/chores"` to `PathConfig` so downstream OBPIs (04 —
resolver, 05 — scaffolder) have an addressable config key. Today
`PathConfig` knows about `skills`, `personas`, etc. but not `chores`, which
means any consumer has to hard-code the path. Scope is deliberately narrow:
one field, three REQ-derived tests, no side-effects on resolver/scaffolder
code that later OBPIs own.

Lane: **Heavy** (schema boundary — `GzkitConfig` is a public contract).
Kind: **foundation** — Gate 5 human attestation required at brief level.

## Approach

Mirror the sibling `skills` / `personas` fields exactly. The pattern already
in place (`src/gzkit/config.py:99-100`) is:

```python
skills: str = ".gzkit/skills"
personas: str = ".gzkit/personas"
```

No `Field(...)` wrapper, no description, bare `str = "..."`. Per brief
requirement #6, match this shape — do not introduce a new style.

`ConfigDict(frozen=True, extra="forbid")` is already on `PathConfig`
(line 66) and must stay unchanged (brief req #4).

## Files to modify

### `src/gzkit/config.py`

Add one line to `PathConfig` immediately after `personas` at line 100:

```python
    skills: str = ".gzkit/skills"
    personas: str = ".gzkit/personas"
    chores: str = ".gzkit/chores"
```

That is the entire production diff.

## Tests (TDD, Red → Green, one increment at a time)

Add three new tests to `tests/test_config.py` under the existing
`TestPathConfig` class (it already lives at line 10). Follow the
surrounding pattern — no `@covers` decorator object import; the existing
class uses plain `unittest` methods. Add `@covers` via docstring tag so
`gz covers` picks them up.

### Test 1 — `test_paths_chores_default_resolves` (REQ-0.0.21-02-01, -04)

```python
def test_paths_chores_default_resolves(self) -> None:
    """PathConfig.chores defaults to .gzkit/chores.

    @covers REQ-0.0.21-02-01
    @covers REQ-0.0.21-02-04
    """
    config = PathConfig()
    self.assertEqual(config.chores, ".gzkit/chores")
    self.assertIsInstance(config.chores, str)
```

**RED:** `AttributeError: 'PathConfig' object has no attribute 'chores'` before the field is added.
**GREEN:** passes once the field lands.

### Test 2 — `test_paths_chores_preserves_user_override` (REQ-0.0.21-02-02)

```python
def test_paths_chores_preserves_user_override(self) -> None:
    """User-supplied paths.chores round-trips through GzkitConfig.load().

    @covers REQ-0.0.21-02-02
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        config_file.write_text(
            '{"paths":{"chores":"custom/chores"}}',
            encoding="utf-8",
        )
        config = GzkitConfig.load(config_file)
        self.assertEqual(config.paths.chores, "custom/chores")
```

**RED:** fails because `PathConfig` has no `chores` field.
**GREEN:** passes once the field lands (existing `GzkitConfig.load` forwards
`paths_data` through `model_validate`).

### Test 3 — `test_paths_extra_field_still_rejected` (REQ-0.0.21-02-03)

```python
def test_paths_extra_field_still_rejected(self) -> None:
    """extra='forbid' on PathConfig still rejects unknown keys.

    @covers REQ-0.0.21-02-03
    """
    from pydantic import ValidationError

    with self.assertRaises(ValidationError):
        GzkitConfig.model_validate({"paths": {"chores_typo": "x"}})
```

**RED (baseline):** passes *before* the field is added (regression guard).
**GREEN (after):** still passes after the field is added — proves
`extra="forbid"` survived the edit.

Test sequencing matches the brief's Gate 2 checklist (lines 80-86): Test 1
first (clean RED), Test 2 next (RED via missing field), Test 3 last
(regression guard — passes both before and after; its purpose is to lock
`extra="forbid"` against accidental relaxation).

## Non-goals (explicitly out of scope per brief)

- Any `src/gzkit/` change outside `config.py` (brief DENIED PATHS).
- Resolver logic in `commands/chores.py` / `chores_exec.py` — OBPI-04.
- Scaffolder wiring in `init_cmd.py` — OBPI-05.
- Any `VendorsConfig`, `ArbConfig`, or other subtree edits (brief req #7).

## Verification (matches brief § Verification)

```bash
# RED/GREEN proof — run after Test 1 is written and before adding the field:
uv run -m unittest tests.test_config.TestPathConfig.test_paths_chores_default_resolves -v
# Expect AttributeError. Then add the field. Re-run — expect OK.

# After all three tests + field land:
uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); \
  from gzkit.config import GzkitConfig; cfg = GzkitConfig(); \
  assert cfg.paths.chores == '.gzkit/chores', cfg.paths.chores; \
  print('paths.chores default OK')"

uv run -m unittest tests.test_config -v 2>&1 | grep -E "paths_chores|OK|FAIL"
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.21-02-config-schema-paths-chores
uv run gz covers OBPI-0.0.21-02-config-schema-paths-chores --json
uv run mkdocs build --strict
```

Acceptance gate: `gz covers --json` reports `uncovered_reqs == 0` for all
five REQs (-01 through -05). REQ-05 (`typecheck exits 0`) is validated by
`gz typecheck` itself, not a unit test — typecheck cleanliness is the
assertion.

## Risk / rollback

Zero-risk schema addition. The field is additive; existing configs that
don't specify `paths.chores` get the default. Rollback is a single-line
revert.
