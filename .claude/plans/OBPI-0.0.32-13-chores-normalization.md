# Plan: OBPI-0.0.32-13-chores-normalization

**OBPI:** OBPI-0.0.32-13-chores-normalization
**Parent ADR:** ADR-0.0.32-canonical-surface-packaging
**Lane:** Heavy
**Execution Mode:** Normal

## Plan-Before-Exploration Disclosure

**Destination-in-mind:** Before exploration, the approach was clear from the brief:
classifier in `.gzkit/rules/skill-surface-sync.md`, Python helper `_classify_chore_file()` in
`src/gzkit/chores/__init__.py`, and byte-parity normalization via `.gzkit/ → src/gzkit/`.

**Rejected alternatives:**
1. JSON data file for classifier: rejected in favor of Python helper for direct importability by OBPI-08.
2. Separate `classifier.py` module: rejected; brief mandates narrow additive change to `__init__.py`.
3. Ignoring AGENTS.md header-only difference: rejected; byte-parity is binding for canonical-class files.

## Divergence Inventory (pre-implementation evidence)

Three canonical-class files diverge (confirmed by `diff -qr`):

| File | Canonical (.gzkit/) | Mirror (src/) | Resolution |
|---|---|---|---|
| `AGENTS.md` | v1.0.0, `.gzkit/chores` header | v1.0.0, `src/gzkit/chores` header | `.gzkit/ → src/` (direction-of-truth) |
| `complexity-reduction-xenon/CHORE.md` | v1.0.0 | v2.0.0 | Mirror-promoted: copy `src/ → .gzkit/` first, then re-sync |
| `pythonic-design-pattern-detection/scan.py` | fewer docstrings | more docstrings | Mirror-promoted: copy `src/ → .gzkit/` first, then re-sync |

Non-standard file types found (need explicit classifier rules):
- `acceptance.json` — per-slug spec file, in parity, canonical class
- `registry.json` — canonical authored data, in parity, canonical class
- `scan.py` in `pythonic-design-pattern-detection/` — authored tool script, canonical class
- `check_evidence.py` (only in src/control-surface-rule-conflicts/) — Python tool, only in src/; classified as package_only (no canonical counterpart)
- `eval_feedback_cluster_lib.py` (only in src/ at package root) — package module, package_only
- `mapping.json`/`mapping.schema.json` in `owasp-top10-2025-scan/` — canonical authored data, only in .gzkit/ (owasp chore has no src/ counterpart)

STOP-on-BLOCKERS resolution: `scan.py` is classified as **canonical** (authored tool script, not runtime-generated). `check_evidence.py` is classified as **package_only** (only in src/, no canonical counterpart — file GHI after OBPI for cross-surface promotion decision). Classifier must document these decisions explicitly.

## Files

### Create
- `tests/test_chores.py` — byte-parity test for canonical-class files

### Modify
- `src/gzkit/chores/__init__.py` — add `_classify_chore_file(path)` helper function
- `.gzkit/rules/skill-surface-sync.md` — add § "Chores class-classifier" section (bump version to 0.4.0)
- `.gzkit/chores/complexity-reduction-xenon/CHORE.md` — promote mirror v2.0.0 → canonical
- `.gzkit/chores/pythonic-design-pattern-detection/scan.py` — promote mirror (more docstrings) → canonical
- `src/gzkit/chores/AGENTS.md` — normalize from canonical .gzkit/ (direction-of-truth)

### No changes
- `.gzkit/chores/AGENTS.md` — is the direction-of-truth; src/ copy is updated to match
- `src/gzkit/chores/complexity-reduction-xenon/CHORE.md` — already at v2.0.0; .gzkit/ promoted to match
- `src/gzkit/chores/pythonic-design-pattern-detection/scan.py` — already has full docstrings; .gzkit/ promoted to match

## Steps

### Task 1: Promote mirror-version files to canonical

Mirror content supersedes canonical per `skill-surface-sync.md` conflict resolution (mirror version > canonical version → promote mirror to canonical).

1. Copy `src/gzkit/chores/complexity-reduction-xenon/CHORE.md` → `.gzkit/chores/complexity-reduction-xenon/CHORE.md`
2. Copy `src/gzkit/chores/pythonic-design-pattern-detection/scan.py` → `.gzkit/chores/pythonic-design-pattern-detection/scan.py`

### Task 2: Write byte-parity test (RED phase)

Add `tests/test_chores.py` with `TestChoresLayoutDualSurface.test_canonical_class_byte_parity`.

The test must:
- Import and call `_classify_chore_file(path)` from `gzkit.chores`
- Walk every file under `.gzkit/chores/<slug>/` and `src/gzkit/chores/<slug>/`
- Apply the classifier
- Assert byte-parity for `canonical`-classified files only
- Skip `package_only` and `runtime_state` files

At this point the test FAILS (RED) because: (a) `_classify_chore_file` doesn't exist yet, (b) `AGENTS.md` is still divergent.

Add `@covers REQ-0.0.32-13-01`, `@covers REQ-0.0.32-13-03`, `@covers REQ-0.0.32-13-04`, `@covers REQ-0.0.32-13-05` decorators to appropriate test methods.

### Task 3: Add `_classify_chore_file` helper to `src/gzkit/chores/__init__.py`

Narrow additive change only. The function signature:

```python
def _classify_chore_file(path: Path) -> Literal["canonical", "package_only", "runtime_state"]:
```

Classification rules (must match the classifier section in `.gzkit/rules/skill-surface-sync.md`):
- `package_only`: `__init__.py`, any path under `__pycache__/`, `README.md` directly under `src/gzkit/chores/<slug>/` with no `.gzkit/chores/<slug>/README.md` counterpart, `eval_feedback_cluster_lib.py`, `check_evidence.py` (Python modules with no canonical counterpart)
- `runtime_state`: `CHORE-LOG.md`, any path under `proofs/`, `.gitkeep`, per-run timestamped artifacts
- `canonical` (default for everything else): `CHORE.md`, `AGENTS.md`, `*.md` outside `proofs/`, `acceptance.json`, `registry.json`, `scan.py` (authored tool scripts), `mapping.json`, `mapping.schema.json`, `*.json`/`*.schema.json` canonical authored data

Add `@covers REQ-0.0.32-13-02` to the classifier helper's test.

### Task 4: Add § "Chores class-classifier" to `.gzkit/rules/skill-surface-sync.md`

Bump rule version to `0.4.0`. Add after the "## Anti-patterns" section:

```markdown
## Chores class-classifier

This section codifies the three-class chores surface model per ADR-0.0.32 § Named exceptions / Exception 2. Every file under `.gzkit/chores/<slug>/` or `src/gzkit/chores/<slug>/` falls into exactly one class:

| Class | Examples | Byte-parity | Notes |
|---|---|---|---|
| **canonical** | `CHORE.md`, `AGENTS.md`, `*.md` (outside `proofs/`), `acceptance.json`, `registry.json`, `scan.py`, `mapping.json`/`*.schema.json` | Required | `.gzkit/chores/` is direction-of-truth; sync propagates `.gzkit/ → src/gzkit/` |
| **package_only** | `__init__.py`, `__pycache__/**`, `README.md` (when no `.gzkit/` counterpart), `eval_feedback_cluster_lib.py`, `check_evidence.py` | Exempt | Package surface only; NEVER sync onto canonical side |
| **runtime_state** | `CHORE-LOG.md`, `proofs/<artifact>`, `.gitkeep` | Exempt | Each surface owns its runtime-state independently; NEVER sync either direction |

**Default rules:**
- Unmatched `.md` files outside `proofs/` → **canonical**
- Files under `proofs/` → **runtime_state**
- Python files with no `.gzkit/` counterpart → **package_only**
- Authored tool scripts (e.g., `scan.py`) present in `.gzkit/` → **canonical**

**Conflict resolution** (mirror version > canonical version): promote mirror content to canonical, then re-sync. Apply `skill-surface-sync.md` § Conflict resolution.

**Long-term note:** This classifier is a temporary accommodation. The deeper design concern — runtime-state (logs/receipts/proofs) co-located with canonical instructions — is parked at `ADR-pool.canonical-vs-runtime-separation`. When that ADR is promoted, runtime-state moves out of `<slug>/` directories and this classifier shrinks to a single class (canonical only).

**Python helper:** `_classify_chore_file(path)` in `src/gzkit/chores/__init__.py` implements this classifier for OBPI-08's sync mechanism.
```

### Task 5: Normalize canonical-class files

After task 3 (classifier exists), normalize the remaining canonical-class divergence:
- Copy `.gzkit/chores/AGENTS.md` → `src/gzkit/chores/AGENTS.md` (direction-of-truth: .gzkit/)

At this point the byte-parity test PASSES (GREEN).

### Task 6: Run quality checks

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests.test_chores -v
```

Fix any lint or type errors.

### Task 7: Run gz agent sync control-surfaces

Propagate the updated `.gzkit/rules/skill-surface-sync.md` to vendor mirrors.

```bash
uv run gz agent sync control-surfaces
```

### Task 8: Full quality gate

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
```

### Task 9: REQ covers gate

```bash
uv run gz covers OBPI-0.0.32-13-chores-normalization --json
```

All REQs must show `covered: true`.

### Task 10: Present OBPI Acceptance Ceremony

## Verification

```bash
# Byte-parity for canonical-class files only
uv run -m unittest tests.test_chores.TestChoresLayoutDualSurface.test_canonical_class_byte_parity -v

# Classifier importable + sample classification
python -c "from gzkit.chores import _classify_chore_file; from pathlib import Path; assert _classify_chore_file(Path('.gzkit/chores/skill-authoring-quality/CHORE.md')) == 'canonical'"
python -c "from gzkit.chores import _classify_chore_file; from pathlib import Path; assert _classify_chore_file(Path('src/gzkit/chores/__init__.py')) == 'package_only'"
python -c "from gzkit.chores import _classify_chore_file; from pathlib import Path; assert _classify_chore_file(Path('.gzkit/chores/skill-authoring-quality/proofs/CHORE-LOG.md')) == 'runtime_state'"

# Confirm no canonical-class drift after normalization
diff -qr .gzkit/chores src/gzkit/chores | grep -v "Only in src/gzkit/chores: __" | grep -v "/proofs/" | grep "differ$"
# Expected: only package_only (check_evidence.py) and runtime_state paths remain

# Rule re-affirmation
grep -A 3 "Chores class-classifier" .gzkit/rules/skill-surface-sync.md | head -10

# Full quality gate
uv run gz check
```

## Notes

- **Scope collision advisory**: `src/gzkit/chores/__init__.py` overlaps with ADR-0.0.21/OBPI-0.0.21-01-physical-migration. Change is narrow and additive only (`_classify_chore_file` function); OBPI-0.0.21-01 status is Completed so no active conflict.
- **check_evidence.py**: Only in `src/gzkit/chores/control-surface-rule-conflicts/`. Classified as `package_only` because it has no `.gzkit/` counterpart. File a follow-up GHI after OBPI for cross-surface promotion decision.
- **owasp-top10-2025-scan/**: Only in `.gzkit/chores/`. No `src/gzkit/chores/owasp-top10-2025-scan/` counterpart. The `mapping.json` and `mapping.schema.json` are canonical authored data. Byte-parity test must handle the case where a slug exists only in `.gzkit/` and not in `src/` — skip parity check for slugs with no `src/` counterpart (these would be scaffolded by `gz init`).
- **docs/governance/canonical-routing-doctrine.md**: Optional per brief. Skip if time-constrained.
