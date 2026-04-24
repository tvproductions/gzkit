# Plan: OBPI-0.0.21-03-wheel-packaging-chores-data — Wheel Packaging of Chores Data

**OBPI:** `OBPI-0.0.21-03-wheel-packaging-chores-data`
**Parent ADR:** `ADR-0.0.21-chores-as-gzkit-surface`
**Lane:** Heavy / Kind: foundation (brief-level human attestation required)
**Brief:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/obpis/OBPI-0.0.21-03-wheel-packaging-chores-data.md`

## Context

Parent ADR-0.0.21 makes `src/gzkit/chores/` a first-class `.gzkit/` surface. OBPI-01 already moved 33 chore directories + `registry.json` + `README.md` into `src/gzkit/chores/`, and OBPI-02 added `paths.chores` to `GzkitConfig`. This OBPI locks the **distribution contract**: every canonical chore must ship in the built wheel, exclude writable runtime state (`proofs/`, `__pycache__/`), and continue to resolve in editable installs and the pyinstaller binary build.

The brief is explicit about the mechanism (Hatchling-native include/force-include — no `MANIFEST.in`, no `[tool.setuptools.*]`), the test surface (zipfile assertions in tempdir), and the three install modes that must pass (wheel, editable, pyinstaller). Lane is **Heavy**, parent kind is **foundation**, so brief-level human attestation is required at Stage 4 (Normal mode).

Baseline reality (verified by inspecting `dist/py_gzkit-0.25.2-py3-none-any.whl`): Hatchling's `packages = ["src/gzkit"]` already auto-includes most non-`.py` data files (templates, schemas, README.md), but the wheel was built before the chores migration. The 0.0.21-01 migration moved 175 files including `proofs/` directories — the latter MUST be excluded. We need an explicit Hatchling-native contract that (a) is the documented truth for shipped chore data and (b) excludes runtime evidence from the wheel.

## Critical files

| File | Change |
|------|--------|
| `pyproject.toml:48-49` | Add `[tool.hatch.build.targets.wheel.force-include]` mapping for `src/gzkit/chores` and explicit `[tool.hatch.build.targets.wheel] exclude` patterns for `**/proofs/**`, `**/proofs`, `**/__pycache__/**`, `**/*.pyc` |
| `tests/test_packaging.py` (new) | 3 REQ-derived tests building wheel in tempdir + zipfile assertions |
| `gz.spec:14-26` | Extend the `datas` list with chores `.md`/`.json` files via a `CHORES = [...]` block mirroring `TEMPLATES`/`SCHEMAS`; preserves binary-build path per REQ-05 |

## Implementation approach

### Step 1 — Stage 1→2 confidence check
Confidence is **>90%**: brief is fully specified (all 8 requirements concrete), parent ADR Decision #1 prescribes the mechanism, OBPI-01 + OBPI-02 already landed prerequisites cleanly, and the precedent file `gz.spec` shows the exact pattern for adding chore datas. **Skip** the `gz justify` walkthrough.

### Step 2 — Author tests RED (TDD discipline per `.claude/rules/tests.md`)
Create `tests/test_packaging.py` with `unittest.TestCase` subclass(es) and `@covers(REQ-...)` decorators. Each test:
1. `tempfile.TemporaryDirectory` for build output (no `shutil.rmtree` in tearDown).
2. Run `uv build --out-dir <tempdir>` via `subprocess.run(["uv", "build", "--out-dir", str(tempdir)], check=True, encoding="utf-8")`.
3. Open the built wheel with `zipfile.ZipFile`.
4. Assert REQ-derived semantics (presence of registry, ≥30 slugs, exclusion of proofs/pycache).

Tests + `@covers` decorators:

| Test | REQ(s) | Assertion |
|------|--------|-----------|
| `test_wheel_ships_chores_registry` | REQ-0.0.21-03-01 | `gzkit/chores/registry.json` is in `z.namelist()` |
| `test_wheel_ships_representative_chore_data` | REQ-0.0.21-03-02 | ≥30 chore slug directories each have BOTH `CHORE.md` and `acceptance.json` |
| `test_wheel_excludes_proofs_and_pycache` | REQ-0.0.21-03-03 | No path matches `**/__pycache__/**`, `**/proofs/**`, or `**/proofs` under `gzkit/chores/` |
| `test_pyproject_uses_hatchling_native_syntax` | REQ-0.0.21-03-06 | parse `pyproject.toml`; assert `[tool.hatch.build.targets.wheel.force-include]` OR `[tool.hatch.build.targets.wheel].include` exists; assert no `MANIFEST.in` file in repo root; assert no `[tool.setuptools` table in pyproject |

Run each: observe RED (the current pyproject has no excludes, so proofs/pycache will be in the wheel after migration; the registry presence may be GREEN baseline due to Hatchling's package auto-include behavior — that's still a valid TDD step because we're locking the contract explicitly even where it happens to hold).

REQ-04 (editable install) and REQ-05 (pyinstaller) are verified by **manual evidence pasted into attestation** rather than CI tests — the brief's Verification block explicitly defines the commands and the brief's Acceptance Criteria #4-#5 do not require unit-test coverage of the install modes (they require evidence). REQ-04 will be covered by the manual smoke + the existing live editable install (uv sync state). REQ-05 will be covered by a binary build + chores-listing run.

### Step 3 — Implement GREEN: edit `pyproject.toml`
Add explicit Hatchling-native data shipping with excludes:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/gzkit"]
exclude = [
    "**/__pycache__",
    "**/__pycache__/**",
    "**/*.pyc",
    "src/gzkit/chores/*/proofs",
    "src/gzkit/chores/*/proofs/**",
]

[tool.hatch.build.targets.wheel.force-include]
"src/gzkit/chores" = "gzkit/chores"
```

The `force-include` is belt-and-suspenders: even if Hatchling's default scan would already pick up the `.md`/`.json` files via the `packages` declaration, this makes the contract explicit per REQ-02 and survives any future Hatchling default change. The `exclude` block enforces REQ-03 and REQ-07 (proofs and pycache).

### Step 4 — Implement GREEN: extend `gz.spec` for pyinstaller
In `gz.spec` after the SCHEMAS block, add:

```python
CHORES_ROOT = SRC / "chores"
CHORES = []
if CHORES_ROOT.exists():
    for slug_dir in sorted(p for p in CHORES_ROOT.iterdir() if p.is_dir() and not p.name.startswith("__")):
        for f in slug_dir.iterdir():
            if f.is_file() and f.suffix in {".md", ".json"} and f.name != "acceptance.json.lock":
                CHORES.append((str(f), f"gzkit/chores/{slug_dir.name}"))
    # Top-level registry + README
    for top in CHORES_ROOT.iterdir():
        if top.is_file() and top.suffix in {".md", ".json"}:
            CHORES.append((str(top), "gzkit/chores"))

datas = TEMPLATES + SCHEMAS + CHORES
```

Skips `proofs/` (only iterates `.md`/`.json` files in slug roots, not the proofs subdirectory). Skips `__pycache__/` (`startswith("__")` filter). Mirrors the existing TEMPLATES/SCHEMAS shape.

### Step 5 — Re-run tests; observe GREEN; refactor only if needed
Each TDD increment runs `uv run -m unittest tests.test_packaging -v` after the implementation step. Refactor (extract helpers for wheel-build + extract namelist filter) only after Green.

### Step 6 — Manual install-mode verification (evidence for attestation)

```bash
# REQ-04: editable install smoke
uv run python -c "import importlib.resources; print([p.name for p in importlib.resources.files('gzkit.chores').iterdir() if p.is_dir()][:5])"

# REQ-05: pyinstaller binary build
uv run pyinstaller gz.spec --clean --noconfirm
# Verify chore data is bundled and resolvable from binary:
./dist/gz chores list 2>&1 | head -20  # expect ≥30 slugs listed

# REQ-08: wheel size delta (sanity)
ls -lh dist/py_gzkit-*.whl
```

Capture all three outputs verbatim for the Stage 4 attestation.

### Step 7 — Quality gates (Stage 3 baseline)
```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz covers OBPI-0.0.21-03 --json   # parity gate: 0 uncovered REQs
```

## Reused patterns

| Pattern | Source |
|---------|--------|
| `tempfile.TemporaryDirectory` + zipfile inspection | `.claude/rules/tests.md` § Patterns; tests across `tests/commands/` |
| `@covers("REQ-...")` decorator | `tests/test_attest_deprecation.py:14, 36` |
| `subprocess.run([...], encoding="utf-8")` for build | `.claude/rules/cross-platform.md` § Subprocess |
| PyInstaller datas pattern | `gz.spec:18-26` (existing TEMPLATES, SCHEMAS) |
| `force-include` Hatchling syntax | parent ADR Decision #1 |

## Anti-patterns explicitly avoided

- ❌ `MANIFEST.in` (setuptools vestige; brief req #2)
- ❌ `[tool.setuptools.package-data]` (wrong build backend; brief req #2)
- ❌ Replacing `packages = ["src/gzkit"]` (brief req #3 — additive only)
- ❌ `shutil.rmtree` in tearDown (`.claude/rules/tests.md`; use `TemporaryDirectory` context manager)
- ❌ Bare `subprocess.run([...])` without `encoding="utf-8"` (`.claude/rules/cross-platform.md`)
- ❌ Stopping after Stage 2/3 to summarize (Iron Law — pipeline runs to Stage 5)

## Verification (end-to-end)

1. **Tests:** `uv run -m unittest tests.test_packaging -v` — all 4 pass
2. **Wheel inspection:** `uv build` then inspect `dist/py_gzkit-0.25.15-py3-none-any.whl` for `gzkit/chores/registry.json`, ≥30 slug `CHORE.md`+`acceptance.json` pairs, zero `proofs/` or `__pycache__/` paths under `gzkit/chores/`
3. **Editable install:** `importlib.resources.files('gzkit.chores').iterdir()` lists slugs (REQ-04)
4. **PyInstaller binary:** `dist/gz chores list` succeeds and lists ≥30 slugs (REQ-05)
5. **Quality gates:** lint + typecheck + unittest + mkdocs all GREEN
6. **REQ → @covers parity:** `uv run gz covers OBPI-0.0.21-03 --json` reports `uncovered_reqs: 0` (or REQs 04/05 documented as evidence-only)
7. **Wheel size delta:** record `du -h` before/after for attestation sanity

## Stages 4 + 5 (governance)

- **Stage 4 (HUMAN GATE):** Present evidence template with all REQ rows populated, wheel size delta, install-mode evidence outputs. Wait for operator attestation phrase.
- **Stage 5:** `gz obpi precomplete` → present closure narrative → `gz obpi complete --attestor-present` (primary path; PTY fallback only if marker rejected) → release lock → git-sync × 2 → reconcile → adr status refresh.
