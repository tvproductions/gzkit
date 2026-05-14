---
id: OBPI-0.0.32-15-t0-maintenance-surfaces
parent: ADR-0.0.32-canonical-surface-packaging
item: 15
lane: Heavy
status: Completed
---

# OBPI-0.0.32-15-t0-maintenance-surfaces: T0 Maintenance Surfaces

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #15 - "OBPI-0.0.32-15: T0 maintenance surfaces — author the missing recovery CLI and classifier doctrine for the T0 fail-closed mechanism shipped under OBPI-06/07 (resolves GHI #461 S1+S2). (a) Add a `--regenerate` flag to `uv run gz validate --distribution` that rewrites `data/distribution_baseline_manifest.json` from on-disk truth symmetric to `gz register-adrs` for `docs/governance/GovZero/adr-status.md` per `.gzkit/rules/governance-core.md` § ADR status index regeneration; emit `distribution_baseline_regenerated` ledger event; manpage at `docs/user/manpages/validate.md`; behave coverage in `features/validate_distribution.feature`. (b) Extend the chores class-classifier doctrine in `.gzkit/rules/skill-surface-sync.md` § Chores class-classifier to cover non-md files under `src/gzkit/rules/`, `src/gzkit/skills/`, `src/gzkit/personas/`, `src/gzkit/templates/` with `_classify_rule_file`/`_classify_skill_file`/`_classify_persona_file`/`_classify_template_file` helpers in each surface's `__init__.py` (e.g. `_scaffolder.py` and `complexity-thresholds.json` resolve to `canonical` or `package_only` class); extend `pyproject.toml [tool.hatch.build.targets.wheel] include:` globs to admit the non-md classes; integrate with OBPI-08's sync mechanism so syncs never overwrite runtime-state and never propagate package-only files onto the canonical side. Acceptance: `uv run gz validate --distribution` exits 0 against current head. Sibling-cut precedent: GHI #455 → `ADR-pool.agentic-security-review` (registry-coherence axis); OBPI-15 is the distribution-baseline/classifier axis bundled into ADR-0.0.32 rather than spawned as a fresh pool ADR because the T0 mechanism whose drift it remediates was authored here. Depends on OBPI-06 (baseline manifest) and OBPI-07 (T0 validator) already landed."

**Status:** Draft

## Objective

Ship the two missing companion surfaces of the T0 distribution mechanism — a canonical `uv run gz validate --distribution --regenerate` flag that rewrites `data/distribution_baseline_manifest.json` from on-disk truth and emits a ledger event symmetric to `gz register-adrs`, and a per-surface class-classifier doctrine extension that resolves non-md files under `src/gzkit/{rules,skills,personas,templates}/` to a known class (`canonical` / `package_only` / `runtime_state`) — so that `uv run gz validate --distribution` exits 0 against on-disk truth without operator hand-edits (resolves GHI #461 S1+S2).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

### Regenerator surface (S1)

- `src/gzkit/governance/trust_audits/distribution.py` — host the regenerator alongside the validator; add `regenerate_distribution_baseline(project_root)` helper that walks on-disk canonical surfaces + wheel include globs and rewrites the manifest.
- `src/gzkit/commands/validate_cmd.py` — wire the `--regenerate` flag onto the existing `--distribution` action. The flag is the chosen CLI shape; no parallel `gz adr` subcommand is authored under this OBPI.
- `data/distribution_baseline_manifest.json` — output of the regenerator. Written only by the regenerator; never hand-edited.
- `docs/user/manpages/validate.md` — manpage update for the new `--regenerate` flag.
- `features/validate_distribution.feature` — extend existing behave coverage: regenerator turns failing `validate --distribution` into exit-0; idempotent re-run; ledger event emitted.
- `tests/governance/test_distribution_audit.py` — extend existing module with `regenerate_distribution_baseline` round-trip and ledger-event-emission coverage.

### Class-classifier surface (S2)

- `src/gzkit/rules/__init__.py` — add `_classify_rule_file(path, *, project_root=None) -> Literal["canonical","package_only","runtime_state"]` symmetric to `_classify_chore_file` at `src/gzkit/chores/__init__.py:33`.
- `src/gzkit/skills/__init__.py` — add `_classify_skill_file(path, ...)` (extension of the existing skills module surface).
- `src/gzkit/personas/__init__.py` — add `_classify_persona_file(path, ...)`.
- `src/gzkit/templates/__init__.py` — add `_classify_template_file(path, ...)`.
- `.gzkit/rules/skill-surface-sync.md` — extend § Chores class-classifier into a unified class-classifier table covering chores, rules, skills, personas, templates; bump rule version.
- `pyproject.toml` — extend `[tool.hatch.build.targets.wheel] include:` globs so the `canonical`-class members under each surface (e.g. `src/gzkit/rules/**/*.py`, `src/gzkit/rules/**/*.json` to the extent the classifier marks them canonical) are wheel-shipped. Exact glob additions derive from classifier output, not from a guess.
- `src/gzkit/governance/trust_audits/distribution.py` — consult the per-surface classifier when computing `ON_DISK_NOT_INCLUDED` so `package_only` files (e.g. `__init__.py`) are exempt and never flagged.
- `src/gzkit/sync_surfaces.py` — OBPI-08's sync mechanism consults the per-surface classifiers so syncs never propagate `package_only` onto the canonical side and never touch `runtime_state`.
- `tests/test_rules.py`, `tests/test_skills.py`, `tests/test_personas.py`, `tests/test_templates.py` — classifier unit coverage matching the chores precedent (`tests/test_chores.py::TestChoresLayoutDualSurface`).

### Shared

- `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md` — parent ADR (Implementation Summary citations + Feature Checklist marking item-15 `[x]` at completion).
- `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-15-t0-maintenance-surfaces.md` — this brief.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `data/security_surfaces.json` — sibling-cut surface, out of scope (resolved under GHI #455 → `ADR-pool.agentic-security-review`).
- Existing 14 OBPIs' core surfaces (`scaffold_core_*` registries, byte-parity guards, `gz init --update`, `gz upgrade`) — those are attested complete; this OBPI extends their classifier surface but does not modify their existing semantics.
- `data/distribution_baseline_manifest.json` hand-edits — the regenerator writes; no human writes.
- New third-party runtime dependencies — stdlib-first per AGENTS.md § STDLIB-FIRST DOCTRINE.
- CI files, lockfiles, `pyproject.toml` outside the `[tool.hatch.build.targets.wheel] include:` block.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Baseline regenerator is the only writer.** `data/distribution_baseline_manifest.json` MUST be regenerated by the registered `uv run gz validate --distribution --regenerate` invocation that walks on-disk canonical surfaces and `pyproject.toml` wheel include globs as the sole inputs. Hand-edits MUST NOT be a documented or implicit recovery path. The validator's resolution string for `ON_DISK_NOT_BASELINE` MUST point at the regenerator flag, not at the manifest file.
2. REQUIREMENT: **Regenerator emits a ledger event.** Every successful regeneration MUST append a ledger event (event name TBD during implementation; suggested: `distribution_baseline_regenerated`) capturing the manifest hash before/after and the surfaces walked, so Layer-2 truth records the regeneration symmetric to how `gz register-adrs` records ADR-index regenerations.
3. REQUIREMENT: **Validator exits 0 on regenerated tree.** After running the regenerator against the current `main` head with no other mutations, `uv run gz validate --distribution` MUST exit 0 with no errors.
4. REQUIREMENT: **Per-surface classifier exists for every canonical surface.** Each of `src/gzkit/{rules,skills,personas,templates}/__init__.py` MUST export a `_classify_<surface>_file(path, *, project_root=None)` helper returning one of `Literal["canonical","package_only","runtime_state"]`, signature-compatible with `_classify_chore_file` at `src/gzkit/chores/__init__.py:33`.
5. REQUIREMENT: **`_scaffolder.py` and `complexity-thresholds.json` resolve to a known class.** Specifically, `src/gzkit/rules/_scaffolder.py` MUST classify as `package_only` (Python module with no `.gzkit/rules/` counterpart), and `src/gzkit/rules/complexity-thresholds.json` MUST classify deterministically (either `canonical` if it has a `.gzkit/rules/complexity-thresholds.json` counterpart, or `package_only` otherwise). The classifier output drives validator exemption AND pyproject include-glob generation; both surfaces MUST stop appearing in `gz validate --distribution` errors after this OBPI lands.
6. REQUIREMENT: **Validator consults the classifier.** `src/gzkit/governance/trust_audits/distribution.py` MUST exempt `package_only` files from `ON_DISK_NOT_INCLUDED` (they are shipped by other means and not subject to canonical-surface wheel-glob inclusion) and MUST exempt `runtime_state` files from both `ON_DISK_NOT_INCLUDED` and `ON_DISK_NOT_BASELINE`.
7. REQUIREMENT: **Sync mechanism consults the classifier.** `src/gzkit/sync_surfaces.py` (the OBPI-08 sync mechanism for `gz agent sync control-surfaces`) MUST consult the per-surface classifier before propagating files, never copying `package_only` onto the canonical (`.gzkit/`) side and never touching `runtime_state` in either direction.
8. REQUIREMENT: **Doctrine extended in one section.** `.gzkit/rules/skill-surface-sync.md` § Chores class-classifier MUST be extended (renamed if appropriate) into a unified class-classifier table covering every canonical-surface tree (chores + rules + skills + personas + templates) in one section with one set of default rules, bumping the rule version per `skill-surface-sync.md` own discipline.
9. REQUIREMENT: **`pyproject.toml` wheel include matches classifier output.** Every file classified `canonical` under every surface MUST be matched by at least one glob in `[tool.hatch.build.targets.wheel] include:`. The classifier output (or a deterministic enumeration derived from it) is the canon; the include block follows.
10. REQUIREMENT: **No regression of attested OBPI-01..14 invariants.** Byte-parity tests for skills/rules/personas/templates dual surfaces (from OBPIs 01/03/09/11) MUST still pass. `gz init --update` (OBPI-05) and `gz upgrade` (OBPI-14) MUST still operate within their respective three-state and surface-filter semantics. T0 smoke test (OBPI-06) MUST still pass.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the Feature Checklist line for OBPI-0.0.32-15** verbatim into the brief's Implementation Summary. The checklist item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR § Decomposition Scorecard third expansion narrative (`EXPANDED 2026-05-13 14 → 15`) — explains the lifecycle reopen and the rationale for bundling these maintenance surfaces here rather than a fresh pool ADR.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item (Feature Checklist OBPI-15 line) that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § STDLIB-FIRST DOCTRINE — the regenerator MUST be stdlib-based (json, pathlib, hashlib); no new third-party deps.
- [ ] `AGENTS.md` § Architectural Boundaries #6 — derived views must never silently become source-of-truth; this OBPI is the mechanical fix for that boundary on the distribution baseline.
- [ ] `.gzkit/rules/governance-core.md` § ADR status index regeneration — precedent doctrine (`gz register-adrs` as Layer-3 regenerator for `docs/governance/GovZero/adr-status.md`) the regenerator surface MUST mirror.
- [ ] `.gzkit/rules/skill-surface-sync.md` § Chores class-classifier — precedent doctrine + table the classifier extension MUST extend.

**Context (read for shape, do not re-derive):**

- [ ] `src/gzkit/governance/trust_audits/distribution.py` — current validator implementation; the regenerator helper lands alongside; the classifier-consulting branch is the validator-side change.
- [ ] `src/gzkit/chores/__init__.py:33` — `_classify_chore_file` signature and tests at `tests/test_chores.py::TestChoresLayoutDualSurface`; new `_classify_*_file` helpers MUST match shape.
- [ ] `src/gzkit/sync_surfaces.py` — OBPI-08's sync mechanism; the integration point for REQ-07.
- [ ] `pyproject.toml [tool.hatch.build.targets.wheel]` — current include block; classifier output drives the additions.
- [ ] `data/distribution_baseline_manifest.json` — current frozen snapshot; baseline for round-trip regenerator tests.
- [ ] GHI #461 — evidence block (21 errors, category breakdown, canonical-doctrine citations).
- [ ] GHI #455 (CLOSED, sibling-cut) — security-registry analog; how that case was resolved (inline edit + design home at `ADR-pool.agentic-security-review`).

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.32-06 attested complete (baseline manifest authored, T0 smoke test in place).
- [ ] OBPI-0.0.32-07 attested complete (`gz validate --distribution` validator in place).
- [ ] OBPI-0.0.32-08 attested complete (sync mechanism with chores classifier integration in place).
- [ ] `uv run gz validate --distribution` exits 3 with `ON_DISK_NOT_BASELINE` and `ON_DISK_NOT_INCLUDED` errors against current head — confirms the gap this OBPI closes.

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/trust_audits/distribution.py` — current `validate_distribution` flow + error categories.
- [ ] `src/gzkit/chores/__init__.py` — `_classify_chore_file` + tests as the symmetric precedent.
- [ ] `src/gzkit/commands/validate_cmd.py` — current `--distribution` flag wiring + how to extend with `--regenerate` semantically (or add a sibling subcommand).
- [ ] `src/gzkit/sync_surfaces.py` — current sync-mechanism behavior for chores classes (so the per-surface extension is consistent).

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
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below. -->

```bash
# Construction housekeeping (all green before completion).
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# OBPI-specific gates (REQ-mapped).
# REQ-01/02/03 — regenerator surface
uv run gz validate --distribution                    # expected: exit 0 after regenerator runs
git diff data/distribution_baseline_manifest.json    # expected: no diff (regenerator-output matches committed)
rg -n "distribution_baseline_regenerated" .gzkit/ledger.jsonl  # expected: ledger event present

# REQ-04 — per-surface classifier exists
uv run python -c "from gzkit.rules import _classify_rule_file; from gzkit.skills import _classify_skill_file; from gzkit.personas import _classify_persona_file; from gzkit.templates import _classify_template_file; print('OK')"

# REQ-05 — specific files classify correctly
uv run python -c "from pathlib import Path; from gzkit.rules import _classify_rule_file; print(_classify_rule_file(Path('src/gzkit/rules/_scaffolder.py')))"            # expected: package_only
uv run python -c "from pathlib import Path; from gzkit.rules import _classify_rule_file; print(_classify_rule_file(Path('src/gzkit/rules/complexity-thresholds.json')))" # expected: package_only or canonical (deterministic)

# REQ-06 — validator consults classifier
uv run gz validate --distribution 2>&1 | rg -c "ON_DISK_NOT_INCLUDED: 'src/gzkit/rules/_scaffolder.py'" # expected: 0

# REQ-07 — sync consults classifier (no package_only files copied to .gzkit/)
uv run gz agent sync control-surfaces --dry-run 2>&1 | rg -i "package_only|_scaffolder.py|__init__.py" # expected: no propagation lines

# REQ-08 — doctrine extended
rg -n "^## " .gzkit/rules/skill-surface-sync.md | rg -i "class-classifier"  # expected: one unified section, not chores-only title

# REQ-10 — no regression of attested OBPI-01..14 invariants
uv run gz arb step --name unittest -- uv run -m unittest -q  # expected: full pass, no new failures vs OBPI-14 baseline
uv run gz adr audit-check ADR-0.0.32                          # expected: continues to PASS for OBPIs 01-14
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Capability A — Baseline regenerator: drift now has a one-command recovery
# (mirrors the gz register-adrs precedent for the ADR status index).
uv run gz validate --distribution                  # before: exit 3, 21 errors
uv run gz validate --distribution --regenerate     # writes data/distribution_baseline_manifest.json from on-disk truth
uv run gz validate --distribution                  # after: exit 0, no errors
rg -n '"event": "distribution_baseline_regenerated"' .gzkit/ledger.jsonl | tail -1

# Capability B — Per-surface classifier: non-md files under a canonical surface
# resolve to a known class instead of triggering ON_DISK_NOT_INCLUDED.
uv run python -c "from pathlib import Path; from gzkit.rules import _classify_rule_file; print(_classify_rule_file(Path('src/gzkit/rules/_scaffolder.py')))"
# Expected: package_only

# Capability C — Sync mechanism honors per-surface classifier: package_only
# files (e.g. _scaffolder.py) never propagate onto the canonical .gzkit/ side.
ls .gzkit/rules/_scaffolder.py 2>&1                   # expected: No such file or directory
uv run gz agent sync control-surfaces                  # idempotent on classifier-correct tree
ls .gzkit/rules/_scaffolder.py 2>&1                   # expected: still No such file or directory

# Capability D — Idempotency: running the regenerator twice produces no diff.
uv run gz validate --distribution --regenerate
git diff --quiet data/distribution_baseline_manifest.json
echo "exit=$?"                                         # expected: exit=0
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.32-15-01: Given a tree where `gz validate --distribution` fails with `ON_DISK_NOT_BASELINE` errors, when the operator invokes the registered regenerator CLI surface, then `data/distribution_baseline_manifest.json` is rewritten from on-disk canonical-surface + wheel-include-glob truth as the sole inputs.
- [ ] REQ-0.0.32-15-02: Given a successful regenerator invocation, when the regenerator returns, then a ledger event (`distribution_baseline_regenerated` or equivalently named) is appended to `.gzkit/ledger.jsonl` capturing manifest hash before/after and surfaces walked.
- [ ] REQ-0.0.32-15-03: Given the regenerator has run on a clean tree, when `uv run gz validate --distribution` runs, then it exits 0 with no errors.
- [ ] REQ-0.0.32-15-04: Given each of `src/gzkit/{rules,skills,personas,templates}/__init__.py`, when imported, then each module exports `_classify_<surface>_file(path, *, project_root=None) -> Literal["canonical","package_only","runtime_state"]` signature-compatible with `_classify_chore_file`.
- [ ] REQ-0.0.32-15-05: Given `src/gzkit/rules/_scaffolder.py` and `src/gzkit/rules/complexity-thresholds.json`, when each is passed to `_classify_rule_file`, then each resolves to a deterministic class (`package_only` is the expected outcome for both; class is the contract, the specific class membership is the implementation finding) and neither file appears in any `gz validate --distribution` error after this OBPI lands.
- [ ] REQ-0.0.32-15-06: Given a tree where a `package_only` file exists under a canonical surface, when `gz validate --distribution` runs, then no `ON_DISK_NOT_INCLUDED` error is raised for that file.
- [ ] REQ-0.0.32-15-07: Given a tree where a `package_only` file exists under a canonical surface, when `gz agent sync control-surfaces` runs, then the file is not propagated to the `.gzkit/<surface>/` canonical side; and given a `runtime_state` file exists on either surface, when sync runs, then the file is not modified on either surface.
- [ ] REQ-0.0.32-15-08: Given `.gzkit/rules/skill-surface-sync.md`, when read, then it contains one unified class-classifier section (not chores-only) covering chores, rules, skills, personas, and templates with one default-rules table, and the file's rule-version marker is bumped accordingly.
- [ ] REQ-0.0.32-15-09: Given `pyproject.toml [tool.hatch.build.targets.wheel] include:`, when inspected, then every file classified `canonical` by the per-surface classifier under every surface is matched by at least one glob.
- [ ] REQ-0.0.32-15-10: Given the full test suite, when run after OBPI-15 lands, then no test that passed for OBPIs 01–14 newly fails (no regression of byte-parity, `gz init --update` three-state, `gz upgrade` filter, or T0 smoke-test invariants).

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


Before:
  $ uv run gz validate --distribution
  Validation failed with 21 error(s) [ON_DISK_NOT_BASELINE x 19, ON_DISK_NOT_INCLUDED x 2]
  exit=3

Recovery:
  $ uv run gz validate --distribution --regenerate
  Baseline regenerated: 108 files across personas, rules, skills, templates.
  Ledger event emitted (distribution_baseline_regenerated).
  exit=0

After:
  $ uv run gz validate --distribution
  All validations passed (9 scopes).
  exit=0

ARB receipts: arb-ruff-a46e96f0477e4de3993daf4aa066d46e, arb-step-typecheck-1e9b9f7c478b4b59992afcf63c9d0cd5, arb-step-unittest-6d6302dd09fd4ba69628394cf4d84823, arb-step-mkdocs-e4ad1dadc9c24c08a4312b8c5ce95d53.
REQ coverage: 10/10 via gz covers OBPI-0.0.32-15-t0-maintenance-surfaces.

### Implementation Summary


- Regenerator: regenerate_distribution_baseline() in src/gzkit/governance/trust_audits/distribution.py walks canonical surface trees, applies per-surface classifiers, writes manifest with schema_version/gzkit_version/surfaces keys, emits distribution_baseline_regenerated ledger event with hash-before/after
- CLI surface: --regenerate flag on gz validate --distribution (parser_maintenance.py + validate_cmd.py); manpage entry in docs/user/manpages/validate.md
- Classifiers: _classify_rule_file, _classify_skill_file, _classify_persona_file, _classify_template_file added to respective __init__.py files, signature-compatible with _classify_chore_file
- Validator exemption: _collect_errors consults classifiers via _is_package_only() helper to exempt package_only/runtime_state files from ON_DISK_NOT_INCLUDED
- Sync integration: sync_pkg_surfaces consults _classify_rule_file/_classify_persona_file/_classify_template_file before propagating files
- Event plumbing: DistributionBaselineRegeneratedEvent Pydantic model, ledger.json schema entry, _NO_GRAPH_IMPACT waiver
- Doctrine: .gzkit/rules/skill-surface-sync.md bumped to 0.6.0 with unified "Canonical surface class-classifier" section covering chores+rules+skills+personas+templates
- pyproject.toml: added src/gzkit/rules/**/*.json wheel include glob (complexity-thresholds.json is canonical)
- Tests: 23 new tests covering 10 REQs; all 4994 tests pass
- Files modified: 22 source/test files; baseline manifest regenerated to 108 files across 4 surfaces
- Date completed: 2026-05-14

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — Jeffry Babb, the operator, verbatim attestation in conversation 2026-05-14 explicitly authorizing PTY-relay path per skill Stage-5 fallback. OBPI-0.0.32-15-t0-maintenance-surfaces fully implemented: regenerator (gz validate --distribution --regenerate) + per-surface classifiers (_classify_{rule,skill,persona,template}_file) + unified Canonical surface class-classifier doctrine in .gzkit/rules/skill-surface-sync.md v0.6.0. gz validate --distribution exits 0; 4994/4994 tests pass; 10/10 REQs covered per gz covers. ARB receipts: arb-ruff-a46e96f0477e4de3993daf4aa066d46e, arb-step-typecheck-1e9b9f7c478b4b59992afcf63c9d0cd5, arb-step-unittest-6d6302dd09fd4ba69628394cf4d84823, arb-step-mkdocs-e4ad1dadc9c24c08a4312b8c5ce95d53. Behave coverage for REQs 04-10 waived under rationale adr-0.0.32-15-unit-test-only-structural-reqs. Security-floor override applied per GHI #462 (operator-authored escape; changes are structurally additive + defensive, not security-relevant by content).
- Date: 2026-05-14

---

**Brief Status:** Completed

**Date Completed:** 2026-05-14

**Evidence Hash:** -
