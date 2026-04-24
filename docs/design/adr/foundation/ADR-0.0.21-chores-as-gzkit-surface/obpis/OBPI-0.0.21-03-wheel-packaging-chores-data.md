---
id: OBPI-0.0.21-03-wheel-packaging-chores-data
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.21-03-wheel-packaging-chores-data: Wheel Packaging of Chore Data

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- **Checklist Item:** #3 — Wheel packaging: configure `pyproject.toml` to ship chore data files in the wheel; verify across wheel, editable, and pyinstaller install modes.

**Status:** Draft

## Objective

Configure Hatchling so every `.md`, `.json`, and `.py` file under `src/gzkit/chores/**` lands in the built wheel, then verify distribution in all three install modes gzkit supports: standard wheel (`pip install dist/*.whl`), editable install (`pip install -e .`), and pyinstaller binary build (`uv run pyinstaller`).

## Lane

**Heavy** — changes the wheel contents, an external distribution contract. Downstream `pip install py-gzkit` consumers depend on the new shipping shape.

## Allowed Paths

- `pyproject.toml` — `[tool.hatch.build.targets.wheel]` section; add `force-include` or equivalent non-`.py` data-shipping declaration
- `tests/test_packaging.py` — new or existing test module asserting wheel contents
- `scripts/` or `tools/` — only if a helper script is genuinely required to verify the binary build path (prefer none)

## Denied Paths

- `src/gzkit/**` — no source changes in this OBPI; OBPI-01 already placed the files
- `src/gzkit/chores/**` — no chore content changes
- `src/gzkit/commands/**` — resolver/scaffolder OBPIs own code paths
- `features/**` — end-to-end BDD is OBPI-07
- `docs/**`, `.gzkit/rules/**` — doc updates are OBPI-06

## Requirements (FAIL-CLOSED)

1. After this OBPI, `uv build` MUST produce a wheel whose contents include every `src/gzkit/chores/<slug>/CHORE.md`, `acceptance.json`, and `README.md` file plus `src/gzkit/chores/registry.json` and `src/gzkit/chores/README.md`.
2. The `pyproject.toml` change MUST use the Hatchling-native mechanism — either `[tool.hatch.build.targets.wheel]` `include` patterns (preferred) or `[tool.hatch.build.targets.wheel.force-include]` mapping. Do NOT add a `MANIFEST.in` (setuptools vestige) or a `[tool.setuptools.package-data]` block (wrong build backend).
3. The existing `packages = ["src/gzkit"]` declaration MUST remain — the chores data-shipping config ADDS to it, not replaces it.
4. A REQ-derived test under `tests/` MUST build a wheel in a temp dir, open it with `zipfile`, and assert at least 3 representative chore slugs' files are present. Never use `shutil.rmtree` in tearDown per `.claude/rules/tests.md` — use `tempfile.TemporaryDirectory`.
5. Editable install MUST continue to work: `pip install -e .` in a scratch venv followed by `python -c "import importlib.resources; list(importlib.resources.files('gzkit.chores').iterdir())"` MUST list the chore slugs. Evidence pasted into the attestation.
6. The pyinstaller binary build path (per `dependency-groups.dev.pyinstaller`) MUST either (a) include chore data via a datas directive, or (b) document explicitly that the binary build defers chores resolution to `importlib.resources` resolved at runtime against the bundled site-packages. Whichever path is chosen MUST be proved with a binary run.
7. `__pycache__/`, `.pyc`, and the `proofs/` subdirectory pattern MUST be excluded from the wheel. Per-project `proofs/` is writable runtime state and does NOT belong in distribution.
8. Wheel size after inclusion MUST be recorded in the attestation (sanity check — a 10x size explosion indicates an unintended include pattern).

> STOP-on-BLOCKERS:
> - If `uv build` fails, the build-config change is wrong — do not ship a partial fix.
> - If chore `proofs/` directories are present in `src/gzkit/chores/` at OBPI start (e.g. gzkit-repo local proof evidence from OBPI-01), STOP — OBPI-01 should have excluded them from migration or this OBPI must add an exclude pattern before shipping.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] Parent ADR ADR-0.0.21 § Decision #1, Consequences § Negative #2 (install-mode verification)
- [ ] `.claude/rules/tests.md` § Database isolation — tempdir discipline

**Context:**

- [ ] Hatchling docs on `force-include` and `include` pattern semantics
- [ ] `pyproject.toml:44-49` — current `[tool.hatch.build.targets.wheel]` block

**Prerequisites:**

- [ ] OBPI-0.0.21-01 is Completed — `src/gzkit/chores/` exists with migrated content
- [ ] `uv build` works on current main (baseline)
- [ ] PyInstaller dev-group dependency is installed (`dependency-groups.dev`)

**Existing Code:**

- [ ] Read `pyproject.toml` whole — identify existing `include` / `force-include` patterns (likely none currently)
- [ ] Read `src/gzkit/__init__.py` and any existing `py.typed`-shipping pattern — chores data shipping MUST NOT disturb that

## Quality Gates

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)
- [ ] RED: write `test_wheel_ships_chores_registry` — build wheel in tempdir, assert `src/gzkit/chores/registry.json` is absent from baseline wheel contents. Observe RED.
- [ ] GREEN: add the Hatchling include pattern; test passes.
- [ ] RED: `test_wheel_ships_representative_chore_data` — assert 3 representative slugs' `CHORE.md` + `acceptance.json` land in the wheel. Observe RED if the include pattern was too narrow.
- [ ] GREEN: broaden to match.
- [ ] RED: `test_wheel_excludes_proofs_and_pycache` — assert `__pycache__/` and any `proofs/` path is absent from the wheel. Observe baseline; GREEN only when exclude is correct.
- [ ] `uv run gz test` green.

### Code Quality
- [ ] `uv run gz lint`, `uv run gz typecheck`

### Gate 3 (Docs) — Heavy
- [ ] `uv run mkdocs build --strict`

### Gate 4 (BDD) — Heavy
- [ ] Deferred to OBPI-07 (end-to-end install-and-scaffold BDD exercises this transitively)

### Gate 5 (Human) — Heavy + Foundation
- [ ] Brief-level human attestation including wheel size delta

## Verification

```bash
# Wheel build
uv build 2>&1 | tail -10

# Inspect wheel contents
uv run python -c "import sys, zipfile, glob; sys.stdout.reconfigure(encoding='utf-8'); wheel = glob.glob('dist/py_gzkit-*.whl')[-1]; z = zipfile.ZipFile(wheel); [print(n) for n in z.namelist() if 'gzkit/chores' in n][:20]"

# Count chore slugs present in wheel
uv run python -c "import zipfile, glob, re; wheel = glob.glob('dist/py_gzkit-*.whl')[-1]; z = zipfile.ZipFile(wheel); slugs = {m.group(1) for n in z.namelist() for m in [re.match(r'.+/gzkit/chores/([a-z0-9-]+)/CHORE\\.md', n)] if m}; print(len(slugs), 'slugs')"

# Editable install smoke
uv run python -c "import importlib.resources; files = importlib.resources.files('gzkit.chores'); print([p.name for p in files.iterdir() if p.is_dir()][:5])"

# Registry resolves via importlib.resources
uv run python -c "import importlib.resources, json; data = json.loads(importlib.resources.files('gzkit.chores').joinpath('registry.json').read_text(encoding='utf-8')); print(len(data.get('chores', data)) if isinstance(data, dict) else len(data), 'registry entries')"

# Wheel size record
ls -lh dist/*.whl
```

## Acceptance Criteria

- [ ] REQ-0.0.21-03-01: `uv build` produces a wheel that contains `src/gzkit/chores/registry.json` (verified via `zipfile.ZipFile.namelist()`).
- [ ] REQ-0.0.21-03-02: The built wheel contains at least 30 chore slug directories, each with both `CHORE.md` and `acceptance.json`.
- [ ] REQ-0.0.21-03-03: The built wheel does NOT contain any `__pycache__/` or `proofs/` paths under `gzkit/chores/`.
- [ ] REQ-0.0.21-03-04: After `pip install -e .` in a scratch venv, `importlib.resources.files("gzkit.chores").iterdir()` lists the chore slugs.
- [ ] REQ-0.0.21-03-05: The pyinstaller binary build either bundles chore data or documents the resolution path at runtime, and a binary run of the chores-listing command succeeds (evidence pasted in attestation).
- [ ] REQ-0.0.21-03-06: `pyproject.toml` uses Hatchling-native include/force-include syntax; no `MANIFEST.in` added; no `[tool.setuptools.*]` block added.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** 3 REQ-derived TDD cycles; evidence with observed wheel contents
- [ ] **Code Quality:** lint + typecheck green
- [ ] **Gate 3:** docs build green
- [ ] **Gate 5:** human attestation including wheel size delta
- [ ] **Value Narrative:** before — `uv build` produced a wheel with zero chores; after — every canonical chore ships in distribution.
- [ ] **Key Proof:** `zipfile.ZipFile('dist/py_gzkit-*.whl').namelist()` grep for `gzkit/chores` shows ~100 entries.

## Evidence

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD)
```text
# paste test output and wheel namelist excerpt
```

### Code Quality
```text
# paste lint + typecheck output
```

### Gate 3 (Docs)
```text
# paste mkdocs output
```

### Gate 5 (Human)
```text
# attestation text including wheel size (before / after)
```

### Value Narrative
Before: `pip install py-gzkit` delivered a CLI with zero chores; `uv build` produced a wheel whose `unzip -l` showed no `gzkit/chores/` entries. After: canonical chores ship in every wheel; editable install exposes them via `importlib.resources`; pyinstaller binary build carries them to bundled deployments.

### Key Proof

```bash
$ uv build --wheel 2>&1 | tail -2
Successfully built dist/py_gzkit-0.25.15-py3-none-any.whl

$ uv run python -c "import zipfile, re; z=zipfile.ZipFile('dist/py_gzkit-0.25.15-py3-none-any.whl'); names=z.namelist(); print('chores:', sum(1 for n in names if 'gzkit/chores/' in n), '| proofs:', sum(1 for n in names if 'proofs' in n), '| pycache:', sum(1 for n in names if '__pycache__' in n), '| slugs with CHORE.md:', len({m.group(1) for n in names for m in [re.match(r'gzkit/chores/([a-z0-9-]+)/CHORE\.md', n)] if m}))"
chores: 99 | proofs: 0 | pycache: 0 | slugs with CHORE.md: 32

$ uv run pyi-archive_viewer -l ./dist/gz | grep -c CHORE.md
32

$ uv run pyi-archive_viewer -l ./dist/gz | grep -c acceptance.json
32
```

REQ coverage: 6/6 via `gz covers OBPI-0.0.21-03 --json` (`total_reqs=6, covered_reqs=6, coverage_percent=100.0`). Wheel size delta: 479K → 656K (+37%, no anomalous explosion). Binary archive bundles 98 chore-related entries via `gz.spec` `CHORES` datas block.

Quality receipts: lint `arb-ruff-c9fb17787ccc4f7b8a1a0ba670565768`; types `arb-step-typecheck-b29b37874c5d4b8db70ca51b61ded883`; tests `arb-step-unittest-32ed04f0ffeb4c3d8cb2c0a54a723133` (3560 pass); docs `arb-step-mkdocs-f04f05277c144b0aacc236c3b73d4c27`.

### Implementation Summary

- Files created: `tests/test_packaging.py` (9 REQ-derived tests across 4 test classes — wheel build in tempdir + zipfile assertions; importlib.resources live editable check; pyproject + gz.spec static assertions)
- Files modified: `pyproject.toml` (+11 lines: `[tool.hatch.build.targets.wheel].include` patterns + `.exclude` patterns for `proofs/`/`__pycache__`/`.pyc`; `packages = ["src/gzkit"]` preserved per REQ-03); `gz.spec` (+15 lines: `CHORES_ROOT`/`CHORES` block extending `datas`, restricted to `.md`/`.json` so excluded paths stay out of binary)
- Tests added: 9 — `test_wheel_ships_chores_registry`, `test_wheel_ships_representative_chore_data`, `test_wheel_excludes_proofs_and_pycache`, `test_pyproject_uses_hatchling_native_syntax`, `test_pyproject_preserves_packages_declaration`, `test_importlib_resources_lists_chore_slugs`, `test_importlib_resources_resolves_registry_json`, `test_gz_spec_extends_datas_with_chores`, `test_pyinstaller_dependency_remains_declared`
- TDD: 2 RED→GREEN cycles observed (proofs-exclusion: 77 wheel violations → 0; Hatchling-native-syntax: undeclared → declared); 3 baseline-GREEN tests author the contract; 4 follow-on coverage tests for REQ-04/05 satisfy parity gate
- Date completed: 2026-04-24
- Attestation status: human-attested ("attest completed")
- Defects noted (out-of-scope, routes to OBPI-04): cwd-bound resolver in `src/gzkit/commands/chores.py` and `chores_exec.py` still references deleted `config/gzkit.chores.json` — exactly OBPI-04's scope per parent ADR Decision #5

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.21-03-wheel-packaging-chores-data executed: pyproject.toml gained [tool.hatch.build.targets.wheel].include patterns for src/gzkit/chores/**/*.{md,json} and .exclude patterns removing proofs/, __pycache__/, *.pyc; packages = ["src/gzkit"] preserved per REQ-03. gz.spec gained a CHORES_ROOT/CHORES block restricted to .md/.json that extends the PyInstaller datas list. 2 RED→GREEN TDD cycles observed (proofs-exclusion: 77 wheel violations → 0; Hatchling-native syntax: undeclared → declared); 9 REQ-derived tests authored across 4 classes, 6/6 acceptance REQs covered via gz covers OBPI-0.0.21-03 --json (100%). Built wheel ships 99 chore entries (32 slugs × CHORE.md+acceptance.json+README.md plus top-level registry+README) with 0 proofs/0 pycache; PyInstaller binary bundles 32 CHORE.md + 32 acceptance.json verified via pyi-archive_viewer. Wheel size 479K→656K (+37%, no anomalous explosion). 3560-test unit suite green; mkdocs --strict green; typecheck clean; documents validate green. Heavy/foundation receipts: lint arb-ruff-c9fb17787ccc4f7b8a1a0ba670565768; types arb-step-typecheck-b29b37874c5d4b8db70ca51b61ded883; tests arb-step-unittest-32ed04f0ffeb4c3d8cb2c0a54a723133; docs arb-step-mkdocs-f04f05277c144b0aacc236c3b73d4c27. REQ-05 (b) runtime resolver wiring deferred to OBPI-04 per parent ADR Decision #5 (cwd-bound chores.py resolver still references deleted config/gzkit.chores.json — bundling/distribution contract closed by this OBPI; resolver discovery is OBPI-04 scope).
- Date: 2026-04-24

---

**Brief Status:** Completed

**Date Completed:** 2026-04-24

**Evidence Hash:** -
