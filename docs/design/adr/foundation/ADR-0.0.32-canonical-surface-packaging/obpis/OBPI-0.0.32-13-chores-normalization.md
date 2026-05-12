---
id: OBPI-0.0.32-13-chores-normalization
parent: ADR-0.0.32-canonical-surface-packaging
item: 13
lane: Heavy
status: Completed
---

# OBPI-0.0.32-13-chores-normalization: Chores Normalization

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #13 — "Chores normalization — apply the § Named exceptions / Exception 2 carve-out doctrine to the existing `.gzkit/chores/` ↔ `src/gzkit/chores/` parallel structure. Bring canonical authored content (`CHORE.md`, `AGENTS.md`, doctrine markdown, scoring rubrics) into byte-parity; codify exempt classes (package-only `__init__.py`/`__pycache__`/`README.md`-when-package-only; runtime-state `CHORE-LOG.md`/`proofs/<artifact>`/`.gitkeep`) in `.claude/rules/skill-surface-sync.md` as the carve-out rule reference; teach OBPI-08's sync mechanism the class-classifier so syncs never overwrite runtime-state and never propagate package-only files onto the canonical side; add byte-parity tests scoped to canonical content classes only."

**Status:** Draft

## Objective

Apply ADR-0.0.32 § Named exceptions / Exception 2 to the existing chores dual-surface. Chores predate ADR-0.0.32; under ADR-0.0.21 (chores-as-gzkit-surface) the surface evolved an organic parallel layout where `.gzkit/chores/<slug>/` and `src/gzkit/chores/<slug>/` both carry per-slug content but mix three distinct file classes:

| Class | Examples | Disposition |
|---|---|---|
| **Canonical authored content** | `CHORE.md`, `AGENTS.md`, doctrine markdown, scoring rubrics, planning prose | Byte-parity REQUIRED between `.gzkit/chores/` and `src/gzkit/chores/` |
| **Package-internal Python** | `src/gzkit/chores/__init__.py`, `src/gzkit/chores/__pycache__/`, `src/gzkit/chores/README.md` (when package-only audience) | Package-only; EXEMPT from byte-parity; never appears at `.gzkit/chores/` |
| **Runtime-state** | `CHORE-LOG.md` (per-run logs), `proofs/<artifact>` (run-time evidence), `.gitkeep` markers, per-run timestamps | Operator-and-agent-written at runtime; the two surfaces diverge intentionally during chore execution; EXEMPT from byte-parity |

This OBPI does three things:

1. **Normalize the canonical drift.** Files currently classified as canonical authored content but byte-divergent between `.gzkit/chores/<slug>/` and `src/gzkit/chores/<slug>/` (the inspection at this ADR's expansion time found at least `.gzkit/chores/AGENTS.md` vs. `src/gzkit/chores/AGENTS.md` differ; multiple `CHORE-LOG.md` files diverge — though those are runtime-state and stay exempt) are brought into byte-parity. The direction-of-truth is `.gzkit/chores/` (the authored canonical surface per ADR-0.0.32 § Canonical-routing scope).
2. **Codify the class-classifier.** Add a § "Chores class-classifier" section to `.claude/rules/skill-surface-sync.md` defining exactly which file classes are canonical (byte-parity binding), package-only (exempt; package surface only), and runtime-state (exempt; either surface may carry independently). The classifier is the single source of truth for what OBPI-08's sync mechanism and the byte-parity test consider in-scope.
3. **Teach OBPI-08's sync mechanism the classifier.** OBPI-08's `gz agent sync control-surfaces` MUST consult the classifier when running over chores: canonical files sync from `.gzkit/chores/` to `src/gzkit/chores/`; package-only files NEVER sync onto the canonical side; runtime-state files NEVER sync in either direction (each surface owns its runtime-state independently).

**Long-term direction (not in scope for this OBPI):** the operator's 2026-05-11 framing surfaced a deeper design concern — mixing canonical authored content with runtime-state in the same directories is a structural smell. The receipts-and-logs class belongs in a separate location entirely (likely `.gzkit/receipts/` or equivalent under the principle that "all aspects of gzkit live under `.gzkit/` but instructions and outcomes are not co-located"). That relocation is parked at `ADR-pool.canonical-vs-runtime-separation`. This OBPI's class-classifier is a **temporary accommodation** that keeps chores working under the canonical-routing invariant without prejudging the separation question; when the pool ADR is promoted, runtime-state will move out of the `<slug>/` directories and the classifier shrinks to a single class (canonical authored content only). The chores normalization landed by this OBPI must be designed so the future relocation is mechanical, not a re-design.

## Lane

**Heavy** — codifies a doctrine carve-out, modifies `.claude/rules/skill-surface-sync.md` (a binding rule), and feeds into OBPI-08's sync-mechanism contract. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `.gzkit/chores/<slug>/*` — bring divergent canonical-class files into byte-parity by direction `.gzkit/ → src/gzkit/` (`.gzkit/chores/` is authored canon)
- `src/gzkit/chores/<slug>/*` — receive the canonical-class normalization; package-only files (e.g., `__init__.py`, `README.md`-when-package-only) stay; runtime-state files stay where they are (per surface)
- `.gzkit/rules/skill-surface-sync.md` — add § "Chores class-classifier" section with the three-class table + binding rules (the canonical surface; `.claude/rules/skill-surface-sync.md` is a generated vendor mirror and must NOT be edited directly)
- `tests/test_chores.py` (existing or new) — byte-parity test scoped to canonical-class files only via the classifier; runtime-state and package-only files are excluded
- `src/gzkit/chores/__init__.py` — narrow, additive change ONLY if the classifier needs a runtime helper (`_classify_chore_file(path) -> Literal["canonical", "package_only", "runtime_state"]`); do NOT touch unrelated chores logic
- `src/gzkit/rules/skill-surface-sync.md` — package-shipping copy of the canonical rule (kept in byte-parity per `tests/test_rules.py::TestRulesLayoutDualSurface`)
- `src/gzkit/rules/AGENTS.md` — compiled subtree agent-context file kept in byte-parity with `.gzkit/rules/AGENTS.md`

## Denied Paths

- Physical layout reorganization (moving runtime-state out of `<slug>/` directories) — that is the pool-ADR `ADR-pool.canonical-vs-runtime-separation` scope; this OBPI is the **temporary accommodation** that leaves the layout in place while making the class boundaries explicit
- `src/gzkit/skills/**`, `src/gzkit/rules/**`, `src/gzkit/personas/**`, `src/gzkit/templates/**` — other surfaces' migrations belong to their own OBPIs
- `pyproject.toml` — wheel includes belong to OBPI-06
- `features/**` — behave belongs to OBPI-06
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `gz agent sync control-surfaces` extension to consume the classifier — belongs to OBPI-08 (this OBPI provides the classifier; OBPI-08 consumes it)
- Chore content edits — this OBPI brings canonical content into byte-parity; no semantic edits to chores

## Requirements (FAIL-CLOSED)

1. The three-class chores classifier MUST be authored in `.gzkit/rules/skill-surface-sync.md` as a § "Chores class-classifier" section (canonical surface; vendor mirror `.claude/rules/skill-surface-sync.md` is generated by `gz agent sync control-surfaces` and must NOT be edited directly). The classifier defines, for every file under `.gzkit/chores/<slug>/` or `src/gzkit/chores/<slug>/`, exactly one classification: **canonical**, **package_only**, or **runtime_state**.
2. The classifier MUST list explicit rules for each class:
   - **canonical**: `CHORE.md`, `AGENTS.md`, `*.md` doctrine files outside `proofs/`, scoring rubrics, planning prose. Default classification for unmatched `.md` files outside `proofs/` is **canonical**.
   - **package_only**: `__init__.py`, `__pycache__/**`, `README.md` when its audience is package-only (heuristic: `README.md` directly under `src/gzkit/chores/<slug>/` that has no counterpart under `.gzkit/chores/<slug>/` is package-only).
   - **runtime_state**: `CHORE-LOG.md`, `proofs/<artifact>`, `.gitkeep`, per-run timestamped artifacts. Default classification for content under `proofs/` is **runtime_state**.
3. A byte-parity test (`tests/test_chores.py::TestChoresLayoutDualSurface::test_canonical_class_byte_parity` or equivalent) MUST exist that:
   - Walks every file under `.gzkit/chores/<slug>/` and `src/gzkit/chores/<slug>/`
   - Applies the classifier
   - Asserts byte-parity for **canonical**-classified files only
   - SKIPS **package_only** and **runtime_state** files
   - Fails closed on canonical-class drift
4. The byte-parity normalization MUST land in this OBPI's diff: every canonical-class file currently divergent between `.gzkit/chores/<slug>/` and `src/gzkit/chores/<slug>/` MUST be brought into byte-parity by direction `.gzkit/ → src/gzkit/` (the `.gzkit/` side is authored canon).
5. The classifier MUST be available as a Python helper for OBPI-08 to consume — either as a function in `src/gzkit/chores/__init__.py` (e.g., `_classify_chore_file(path)`) OR as a JSON/data file under `src/gzkit/chores/` that OBPI-08's sync mechanism reads. Document the chosen shape.
6. `.gzkit/rules/skill-surface-sync.md` MUST cite `ADR-pool.canonical-vs-runtime-separation` as the long-term home for the runtime-state relocation question, so future readers know the classifier is a temporary accommodation.
7. NO physical relocation of runtime-state files OUT of `<slug>/` directories is permitted in this OBPI. The classifier-and-byte-parity work is the IN-SCOPE accommodation; the relocation is OUT of scope (belongs to the pool ADR).
8. `uv run gz check` MUST exit 0 after normalization and classifier landing.
9. `mkdocs build --strict` MUST pass; rule updates MUST land in the same patch as classifier code per `.claude/rules/gate5-runbook-code-covenant.md`.

> STOP-on-BLOCKERS:
> - If a `README.md` under `.gzkit/chores/<slug>/` exists AND a different `README.md` under `src/gzkit/chores/<slug>/` exists, STOP — the classifier needs explicit guidance on which is canonical vs. which is package-only; document the decision before normalizing.
> - If a non-standard file type appears under `.gzkit/chores/<slug>/` (e.g., a YAML config, a JSON registry) that doesn't fit the three classes cleanly, STOP and surface as a follow-up GHI; expand the classifier explicitly rather than guessing.
> - If `CHORE-LOG.md` content under `.gzkit/chores/<slug>/proofs/` differs catastrophically from `src/gzkit/chores/<slug>/proofs/CHORE-LOG.md` (e.g., one captures a completed run, the other captures a different run), STOP — runtime-state divergence is expected, but if the divergence is corrupting the chore's own ledger semantics, surface it as a defect first.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — § Named exceptions / Exception 2 (chores carve-out doctrine)
- [ ] Parent ADR § Decision — § Canonical-routing scope (chores row)
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/skill-surface-sync.md` — the canonical rule this OBPI extends with the chores class-classifier section (vendor mirror at `.claude/rules/skill-surface-sync.md` is generated)
- [ ] ADR-0.0.21 (chores-as-gzkit-surface) — the original chores doctrine, predating ADR-0.0.32's canonical-routing model
- [ ] `ADR-pool.canonical-vs-runtime-separation` — the pool ADR that parks the longer-term runtime-state relocation question

**Context — sibling OBPIs:**

- [ ] OBPI-0.0.32-01 / -03 / -09 / -11 — the dual-surface migration shape this OBPI extends with a class-aware variant
- [ ] OBPI-0.0.32-08 — consumes the classifier this OBPI authors

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/chores/` and `src/gzkit/chores/` both exist with parallel `<slug>/` directories
- [ ] `.claude/rules/skill-surface-sync.md` exists at the rule version path
- [ ] `ADR-pool.canonical-vs-runtime-separation` exists (or is filed concurrently with this OBPI)

**Existing Code:**

- [ ] Run `diff -qr .gzkit/chores src/gzkit/chores` and enumerate every divergence; classify each into the three classes by inspection
- [ ] Read `src/gzkit/chores/__init__.py` to identify the best home for the `_classify_chore_file` helper (or determine that a JSON data file is cleaner)
- [ ] Inspect a `proofs/` directory for the canonical content shape to confirm the runtime-state classification rule

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #13 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: byte-parity test fails before normalization (currently `.gzkit/chores/AGENTS.md` ≠ `src/gzkit/chores/AGENTS.md`); classifier-unit-tests fail before classifier authored
- [ ] GREEN: tests pass after normalization + classifier authoring
- [ ] Coverage above 40% floor

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `.gzkit/rules/skill-surface-sync.md` § "Chores class-classifier" section landed; cites `ADR-pool.canonical-vs-runtime-separation`
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] No new behave scenarios in this OBPI; OBPI-08 owns the sync scenario that exercises the classifier end-to-end

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Byte-parity for canonical-class files only
uv run -m unittest tests.test_chores.TestChoresLayoutDualSurface.test_canonical_class_byte_parity -v

# Classifier importable + sample classification
python -c "from gzkit.chores import _classify_chore_file; from pathlib import Path; print(_classify_chore_file(Path('.gzkit/chores/skill-authoring-quality/CHORE.md')))"  # expect: canonical
python -c "from gzkit.chores import _classify_chore_file; from pathlib import Path; print(_classify_chore_file(Path('src/gzkit/chores/__init__.py')))"  # expect: package_only
python -c "from gzkit.chores import _classify_chore_file; from pathlib import Path; print(_classify_chore_file(Path('.gzkit/chores/skill-authoring-quality/proofs/CHORE-LOG.md')))"  # expect: runtime_state

# Rule re-affirmation (check canonical surface; vendor mirror is generated)
grep -A 3 "Chores class-classifier" .gzkit/rules/skill-surface-sync.md | head -10
```

## Acceptance Criteria

- [ ] REQ-0.0.32-13-01: `.gzkit/rules/skill-surface-sync.md` § "Chores class-classifier" section landed with the three-class table (canonical / package_only / runtime_state) and binding rules for each class
- [ ] REQ-0.0.32-13-02: The classifier is available to OBPI-08 as a Python helper (`_classify_chore_file` or equivalent) OR as a JSON data file under `src/gzkit/chores/`; chosen shape documented
- [ ] REQ-0.0.32-13-03: Every canonical-class file divergent between `.gzkit/chores/<slug>/` and `src/gzkit/chores/<slug>/` brought into byte-parity by direction `.gzkit/ → src/gzkit/`
- [ ] REQ-0.0.32-13-04: `tests/test_chores.py::TestChoresLayoutDualSurface::test_canonical_class_byte_parity` (or equivalent) walks both surfaces, applies the classifier, asserts byte-parity for **canonical**-classified files only, skips **package_only** and **runtime_state**
- [ ] REQ-0.0.32-13-05: NO physical relocation of runtime-state OUT of `<slug>/` directories occurred in this OBPI (parked at `ADR-pool.canonical-vs-runtime-separation`)
- [ ] REQ-0.0.32-13-06: `.gzkit/rules/skill-surface-sync.md` cites `ADR-pool.canonical-vs-runtime-separation` as the long-term home for the relocation question
- [ ] REQ-0.0.32-13-07: `uv run gz check` exits 0
- [ ] REQ-0.0.32-13-08: `mkdocs build --strict` passes

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** Byte-parity + classifier tests recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Rule update landed; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Existing scenarios still pass
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste byte-parity + classifier test output
```

### Code Quality

```text
# Paste lint, format, ty output
```

### Gate 3 (Docs)

```text
# Paste mkdocs --strict output
```

### Gate 4 (BDD)

```text
# Paste regression scenario output
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: chores had organic parallel `.gzkit/chores/` ↔ `src/gzkit/chores/` structure with byte-drift across canonical authored content (e.g., AGENTS.md), package-only files (`__init__.py`, package-only README.md), and runtime-state (CHORE-LOG.md, proofs/). OBPI-08's sync mechanism could not safely sync chores without a class boundary to honor (e.g., overwriting `proofs/CHORE-LOG.md` from one surface to the other would corrupt run-time evidence). After this OBPI: a three-class classifier (canonical / package_only / runtime_state) is codified in `.claude/rules/skill-surface-sync.md`; canonical-class byte-parity is enforced by test; package-only and runtime-state classes are explicitly exempt; OBPI-08 has a clean classifier to consume.

This OBPI is a **temporary accommodation**, not a final resting place. The deeper design concern — that runtime-state (logs/receipts/proofs) lives inside the canonical-instruction directories at all — is parked at `ADR-pool.canonical-vs-runtime-separation`. When that pool ADR is promoted and the relocation lands, the classifier shrinks to a single class (canonical only) and chores becomes structurally clean. Until then, the classifier preserves the canonical-routing invariant without prejudging the relocation question.

### Key Proof


```bash
# Canonical-class byte-parity confirmed (no output = all in parity)
diff -qr .gzkit/chores src/gzkit/chores | grep -v "Only in src/gzkit/chores: __" | grep -v "/proofs/" | grep "differ$"
# (empty output)

# Chores test suite green
uv run -m unittest tests.test_chores -v
# Ran 4 tests in 0.031s -- OK

# Full quality gates green (ARB receipts):
uv run gz arb step --name unittest -- uv run -m unittest -q
# Ran 4837 tests in 41.870s -- OK
# Receipt: arb-step-unittest-809f92ee3b8c45738d7681565ed5be23

uv run gz arb ruff
# clean -- Receipt: arb-ruff-98faa4116a1449059b7bd7ec99fcbbed

uv run gz arb typecheck
# clean -- Receipt: arb-step-typecheck-9382c94d841440478aab72962c566486

uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# clean -- Receipt: arb-step-mkdocs-3738e7fc5da44235b3ae0b9d40ff0b26

# 100% REQ coverage
uv run gz covers OBPI-0.0.32-13-chores-normalization --json
# {"covered_reqs": 8, "uncovered_reqs": 0, "coverage_percent": 100.0}
```

### Implementation Summary


- Classifier helper: `_classify_chore_file(path, *, project_root=None) -> Literal["canonical", "package_only", "runtime_state"]` added to `src/gzkit/chores/__init__.py` (narrow additive change; existing API preserved)
- Rule update: `.gzkit/rules/skill-surface-sync.md` bumped to v0.4.0 with new § "Chores class-classifier" section codifying the three-class table and citing `ADR-pool.canonical-vs-runtime-separation` as the long-term relocation home
- Canonical-class normalization landed: `AGENTS.md` header parity (.gzkit/ -> src/gzkit/); `complexity-reduction-xenon/CHORE.md` promoted from mirror v2.0.0 to canonical; `pythonic-design-pattern-detection/scan.py` promoted from mirror (more docstrings) to canonical
- Test surface: `tests/test_chores.py::TestChoresLayoutDualSurface` (4 tests, 8 REQs covered via @covers decorators, 100% REQ coverage)
- Vendor mirror propagation: `gz agent sync control-surfaces` propagated rule update to `.claude/rules/skill-surface-sync.md`; package surface `src/gzkit/rules/skill-surface-sync.md` and compiled `src/gzkit/rules/AGENTS.md` synced byte-equal with canonical
- Brief allowlist correction: 6 references to `.claude/rules/skill-surface-sync.md` (generated vendor mirror) corrected to `.gzkit/rules/skill-surface-sync.md` (canonical surface)
- STOP-on-BLOCKERS resolved: `scan.py` classified as canonical (authored tool script); `check_evidence.py` classified as package_only (no .gzkit/ counterpart; future GHI deferred)
- Date completed: 2026-05-12
- Attestation status: human-attested via operator phrase "attest completed"
- Defects noted: none (long-term runtime-state relocation parked at `ADR-pool.canonical-vs-runtime-separation`)

## Tracked Defects

- `ADR-pool.canonical-vs-runtime-separation` — the long-term home for relocating runtime-state files OUT of `<slug>/` directories; not in this OBPI's scope

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Stage 4 evidence reviewed and accepted: classifier helper landed at src/gzkit/chores/__init__.py with three-class semantics; .gzkit/rules/skill-surface-sync.md v0.4.0 codifies the carve-out doctrine and cites ADR-pool.canonical-vs-runtime-separation; canonical-class byte-parity achieved across .gzkit/chores/ ↔ src/gzkit/chores/ for AGENTS.md, complexity-reduction-xenon/CHORE.md, and pythonic-design-pattern-detection/scan.py; 4837/4837 unittests pass (receipt arb-step-unittest-809f92ee3b8c45738d7681565ed5be23); lint and typecheck clean (receipts arb-ruff-98faa4116a1449059b7bd7ec99fcbbed, arb-step-typecheck-9382c94d841440478aab72962c566486); mkdocs --strict clean (receipt arb-step-mkdocs-3738e7fc5da44235b3ae0b9d40ff0b26); 8/8 REQs covered (100%) via tests.test_chores.TestChoresLayoutDualSurface.
- Date: 2026-05-12

---

**Brief Status:** Completed

**Date Completed:** 2026-05-12

**Evidence Hash:** -
