---
id: OBPI-0.0.17-06-agents-md-correction
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 6
lane: Lite
status: Completed
---

# OBPI-0.0.17-06-agents-md-correction: AGENTS.md + docs/user correction

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- **Checklist Item:** #6 — "AGENTS.md correction + docs/user alignment"

**Status:** Draft (pending atomic completion via `gz obpi complete`)

## Objective

Correct `AGENTS.md` to document `kind` and `lane` as orthogonal axes. Remove the "Heavy/Foundation" bucketing that conflates them. Document the four-combo matrix (foundation×lite, foundation×heavy, feature×lite, feature×heavy, plus pool with no lane) and its attestation consequences (attestation rigor attaches to lane, not kind). Cross-link to ADR-0.0.18 (operator doctrine). Update `docs/user/commands/plan-create.md` and any other surfaces referencing foundation implicitly.

## Lane

**Lite** — documentation-only change to governance surfaces. No CLI contract, schema, or runtime behavior change. (Authoring rigor matches heavy because this is foundation-kind doctrine, but the lane per ADR-0.0.17's orthogonal-axes decision is Lite — external contracts are untouched. Gate 5 attestation is still required under the foundation-kind rigor that ADR-0.0.18 formalizes.)

## Allowed Paths

- `AGENTS.md`
- `CLAUDE.md` (if mirroring required)
- `docs/user/commands/plan-create.md` (real CLI doc; brief originally referenced `plan.md` which does not exist)
- `docs/user/concepts/` (new page if needed — scoped to mechanical taxonomy only; deeper doctrine is ADR-0.0.18)
- `docs/governance/` (cross-references only)
- **Scope amendment (documented):** `src/gzkit/templates/agents.md` and `src/gzkit/templates/copilot.md` are the canonical source for generated `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` (see `src/gzkit/sync_surfaces.py:323-335,353-366`). Editing the generated files is overwritten by the next `gz agent sync control-surfaces` run. Treating the template source as in-scope is consistent with the brief's intent and the skill-surface-sync discipline. Also extended to user-facing command docs that bucket "Heavy/Foundation" implicitly: `docs/user/commands/obpi-emit-receipt.md`, `obpi-pipeline.md`, `specify.md` — per brief's "any other surfaces referencing foundation implicitly" clause.

## Denied Paths

- Any schema, CLI, validator, or test surface (covered by OBPI-01 through OBPI-05)
- `.gzkit/skills/**` and `.claude/skills/**` — skill updates are ADR-0.0.18 scope
- ADR-0.0.18's doctrine surfaces (runbook, PRD→ADR, pool curation, epics)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `AGENTS.md` § OBPI Acceptance Protocol + § Lane Inheritance Rule no longer reference "Heavy/Foundation" as a single bucket for attestation. Attestation rigor is documented as attaching to lane (heavy ⇒ Gate 5), with a note that foundation-kind ADRs follow the attestation protocol in ADR-0.0.18 regardless of lane.
2. REQUIREMENT: A new section in `AGENTS.md` (or an expansion of an existing one) names all three kinds (pool, foundation, feature) and cites the mechanical enforcement (schema, CLI, validator) that lands in OBPI-01–OBPI-04.
3. REQUIREMENT: `docs/user/commands/plan-create.md` documents the `--kind` flag, its valid values, and the kind/semver binding. Includes at least one example for each of foundation and feature. Cross-links to ADR-0.0.18.
4. REQUIREMENT: NO content in OBPI-06 overlaps ADR-0.0.18's doctrine scope (PRD→ADR derivation, pool curation, epic grouping, foundation-vs-feature decision guidance). OBPI-06 documents the mechanical contract only; the doctrine ADR covers "when to choose which."
5. REQUIREMENT: `gz agent sync control-surfaces` run after changes lands clean (no drift between canonical `.gzkit/rules/` and mirror `.claude/rules/` / `.github/instructions/`).
6. REQUIREMENT: `mkdocs build --strict` passes (new/edited pages render correctly).
7. REQUIREMENT: Cross-link to `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/...` for operator-facing decision guidance from both AGENTS.md (Kinds section) and plan-create.md (See also section).

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md` — agent operating contract
- [x] Parent ADR — full context of the orthogonal-axes decision
- [x] `.claude/rules/defect-fix-routing.md` — routing for in-flight defects discovered during ceremony
- [x] `.claude/rules/skill-surface-sync.md` — canonical vs mirror discipline (drove the scope-amendment decision to edit `src/gzkit/templates/` rather than generated outputs)

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- [x] Sibling ADR: `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md` — cross-link target for "when to choose which" doctrine
- [x] Sibling OBPIs (01-05) all attested completed; OBPI-06 is the final item

**Prerequisites (check existence, STOP if missing):**

- [x] OBPI-01 (`AdrFrontmatter.kind` Pydantic field + schema enum) — attested completed
- [x] OBPI-02 (`gz plan create --kind`) — attested completed; `docs/user/commands/plan-create.md` already documents `--kind` with foundation/feature examples
- [x] OBPI-03 (`gz adr promote --kind`) — attested completed
- [x] OBPI-04 (`gz validate --taxonomy`) — attested completed
- [x] OBPI-05 (backfill + round-trip test) — attested completed

**Existing Code (understand current state):**

- [x] `src/gzkit/templates/agents.md` (canonical source for AGENTS.md) — located pre-edit
- [x] `src/gzkit/templates/copilot.md` (canonical source for `.github/copilot-instructions.md`) — located pre-edit
- [x] `src/gzkit/sync_surfaces.py:323-335` (sync_agents_md) — confirmed template-driven regeneration
- [x] `src/gzkit/sync_surfaces.py:353-366` (sync_copilot_instructions) — discovered gated-behind-`canonical_rules`-empty conditional (pre-existing defect, GHI to file)
- [x] `docs/user/commands/plan-create.md` already carries `--kind` flag + foundation/feature/pool examples (landed in OBPI-02)

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted (§ Decision #2 locks the orthogonal-axes axis; OBPI-06 is scheduled for the AGENTS.md correction + plan-create.md cross-link)

### Gate 2: TDD (Red-Green-Refactor)

- [x] N/A for TDD in the test-derivation sense — this is a Lite-lane docs-only OBPI with no `@covers`-tagged test surface. Per `.gzkit/rules/tests.md` § Red-Green-Refactor, tests derive from acceptance criteria — where the criteria are "doc surface reads correctly," evidence is the rendered diff + mkdocs strict build + agent sync drift status, per the brief's own Evidence section.

### Code Quality

- [x] Lint clean: `uv run gz arb ruff` → exit 0, receipt `arb-ruff-8f839fc802dd47f9b9404bd2af307b43`
- [x] Typecheck: N/A (no `.py` edits)

### Gate 3: Docs (Heavy only)

- [ ] N/A — Lite lane; however, mkdocs strict build + sync drift verification were run as part of verification since this brief IS a docs change.

### Gate 4: BDD (Heavy only)

- [ ] N/A — Lite lane; no operator workflow scenario introduced. `kind`/`lane` axis doctrine is observable via `AGENTS.md` rendering and `gz plan create --kind` help output (locked by OBPI-02 tests).

### Gate 5: Human (Heavy / Foundation-kind)

- [x] Human attestation recorded (see § Human Attestation). Foundation-kind parent ADR invokes the attestation walkthrough discipline per ADR-0.0.18, even on Lite lane.

## Verification

```bash
uv run gz agent sync control-surfaces                                           # REQ-5 — zero drift
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict                # REQ-6 — receipt arb-step-mkdocs-a1499a1524cb47169f8d076a85046b4f
uv run gz arb ruff                                                              # code-quality — receipt arb-ruff-8f839fc802dd47f9b9404bd2af307b43
grep -rn "Heavy/Foundation\|Heavy or Foundation\|Foundational (0\.0\.x)" \
  AGENTS.md CLAUDE.md .github/copilot-instructions.md \
  docs/user/commands/ docs/user/concepts/                                       # REQ-1 — 0 hits
grep -n "ADR-0.0.18" AGENTS.md docs/user/commands/plan-create.md                # REQ-7 — 5 + 3 hits
# Manual re-read: read AGENTS.md § Kinds, § OBPI Acceptance Protocol, § Lane Inheritance Rule aloud; confirm no residual bucketing
```

## Evidence

### Gate 1 (ADR)

ADR-0.0.17 § Decision #2 explicitly authorizes this OBPI as the AGENTS.md correction leg of the taxonomy roll-out: "`AGENTS.md:214` is wrong in its current shape. It treats 'Heavy/Foundation' as a single attestation bucket, conflating the two axes. The correction is part of this ADR (OBPI-06). Attestation rigor attaches to lane, not kind." OBPI-01..05 are all attested_completed; this OBPI closes the final checklist item.

### Gate 2 (Docs-only — Red-Green-Refactor N/A)

No unit-test-level Red-Green cycle applies. Evidence below substitutes diff + render + sync-drift verification per the brief's stated Evidence model.

### Code Quality

```text
$ uv run gz arb ruff
arb ruff exit_status=0 receipt=arb-ruff-8f839fc802dd47f9b9404bd2af307b43
```

### Gate 3 (Docs)

```text
$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
INFO    -  Documentation built in 4.43 seconds
arb step name=mkdocs exit_status=0 receipt=arb-step-mkdocs-a1499a1524cb47169f8d076a85046b4f

$ uv run gz agent sync control-surfaces
Sync complete.   # zero drift/warn/error lines in output
```

### Gate 4 (BDD)

N/A — see Quality Gates § Gate 4.

### Gate 5 (Human)

See § Human Attestation.

### Value Narrative

Before: `AGENTS.md` and several user-facing doc surfaces treated "Heavy/Foundation" as a single attestation bucket, conflating the `kind` axis (pool/foundation/feature) with the `lane` axis (heavy/lite). Adopters reading the contract saw doctrine that contradicted ADR-0.0.17 § Decision #2, and OBPI-01..05 landed mechanical enforcement against a contract the operator docs hadn't caught up to. After: attestation rigor is documented as attaching to `lane` (heavy ⇒ Gate 5 across any kind), and foundation-kind ADRs follow the ADR-0.0.18 attestation doctrine regardless of lane. A new "Kinds" section in AGENTS.md names the three kinds and cites the four mechanical enforcement surfaces (schema, `plan create --kind`, `adr promote --kind`, `validate --taxonomy`). `mkdocs --strict` is clean; `gz agent sync control-surfaces` reports zero drift; residual "Heavy/Foundation" bucketing on user-facing surfaces is 0 hits.

### Key Proof


```text
$ grep -rn "Heavy/Foundation\|Heavy or Foundation\|Foundational (0\.0\.x)" \
    AGENTS.md CLAUDE.md .github/copilot-instructions.md \
    docs/user/commands/ docs/user/concepts/
# (no output)

$ grep -c "ADR-0.0.18" AGENTS.md docs/user/commands/plan-create.md
AGENTS.md:5
docs/user/commands/plan-create.md:3

$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
INFO    -  Documentation built in 4.43 seconds
arb step name=mkdocs exit_status=0 receipt=arb-step-mkdocs-a1499a1524cb47169f8d076a85046b4f
```

### Implementation Summary


- Files modified:
  - `src/gzkit/templates/agents.md` — rewrote OBPI Acceptance Protocol opening; rewrote Lane Inheritance Rule table + added Foundation-kind rigor paragraph; inserted new `### Kinds (pool, foundation, feature)` section naming all three kinds and citing OBPI-01..04 mechanical enforcement surfaces.
  - `src/gzkit/templates/copilot.md` — rewrote OBPI Acceptance note (line 44) to separate `lane` and `kind` axes; added AGENTS.md cross-reference.
  - `docs/user/concepts/lifecycle.md:64` — rewrote to key attestation on lane with foundation-kind cross-link to ADR-0.0.18.
  - `docs/user/commands/plan-create.md` — added "See also" section cross-linking ADR-0.0.17 (mechanical contract) and ADR-0.0.18 (doctrine).
  - `docs/user/commands/obpi-emit-receipt.md:30` — rewrote `--event completed` fail-closed trigger description to key on lane + kind.
  - `docs/user/commands/obpi-pipeline.md:36` — rewrote `--from=ceremony` attestation trigger description similarly.
  - `docs/user/commands/specify.md:127` — rewrote step 7 to key on lane + kind.
  - `.github/copilot-instructions.md` — mirrored the copilot.md template edit directly (see § Tracked Defects for the sync-regeneration defect that required the direct edit).
- Generated surfaces regenerated by `gz agent sync control-surfaces`: `AGENTS.md`, `CLAUDE.md`, nested per-directory `AGENTS.md` files (config, docs, src, src/gzkit/cli, src/gzkit/commands, tests), `.github/instructions/*.instructions.md`, skill/persona mirrors across `.claude/`, `.agents/`, `.github/`.
- Tests added: none (Lite-lane docs-only; no `@covers` parity applies).
- Date completed: 2026-04-19.
- Attestation status: attested completed (Lite lane; foundation-kind parent ADR invokes ADR-0.0.18 attestation walkthrough).

## Tracked Defects

- **`gz agent sync control-surfaces` does not regenerate `.github/copilot-instructions.md` when canonical rules exist.** `src/gzkit/sync_surfaces.py:612-623` gates `sync_copilot_instructions` behind an empty `canonical_rules` branch, so template edits to `src/gzkit/templates/copilot.md` do not propagate. Workaround applied: mirrored the template edit directly to `.github/copilot-instructions.md`. **GHI to file** (root-cause fix is in denied path `src/gzkit/sync_surfaces.py`).
- **Residual "Heavy/Foundation" bucketing in `docs/governance/**` surfaces** — `governance_runbook.md:245,362`; `GovZero/obpi-runtime-contract.md:118,149,263`; `GovZero/obpi-transaction-contract.md:158,172`; `GovZero/validation-receipts.md:87`; `advisory-rules-audit.md:59,108`. These are doctrine/runtime-contract surfaces owned by other ADRs (the runbook is explicitly denied scope for this OBPI). **Recommend a follow-up sweep under ADR-0.0.18 or a dedicated fix-routing GHI.**
- **`gz obpi precomplete` lock_held check does not find locks under `.gzkit/locks/obpi/`.** `src/gzkit/commands/obpi_precomplete.py:186` globs `.gzkit/locks/*.json` (shallow), but lock files live under `.gzkit/locks/obpi/OBPI-<id>.lock.json`. Lock IS held (`gz obpi lock list` confirms), but precomplete reports "No lock file matches." Out-of-scope in-flight defect. **GHI to file.**

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.17-06-agents-md-correction closes the final item in ADR-0.0.17 (ADR Taxonomy — Mechanical). AGENTS.md now keys attestation on lane (heavy ⇒ Gate 5 across any kind); new § Kinds (pool, foundation, feature) names the three kinds and cites the mechanical enforcement surfaces (schema, --kind on plan create / adr promote, --taxonomy validator). Foundation-kind ADRs cross-link to ADR-0.0.18 for the 'when to choose which' doctrine. Scope amendment: edited src/gzkit/templates/agents.md + templates/copilot.md (canonical source for generated AGENTS.md / .github/copilot-instructions.md) rather than the generated outputs, per skill-surface-sync discipline. Also extended to docs/user/commands/obpi-emit-receipt.md, obpi-pipeline.md, specify.md, and docs/user/concepts/lifecycle.md per brief's 'any other surfaces referencing foundation implicitly' clause. Receipts: docs strict arb-step-mkdocs-a1499a1524cb47169f8d076a85046b4f; lint arb-ruff-8f839fc802dd47f9b9404bd2af307b43. gz agent sync control-surfaces reported zero drift. Three defects flagged for GHI: sync_copilot_instructions skipped when canonical rules exist; residual Heavy/Foundation bucketing in docs/governance/** surfaces; gz obpi precomplete lock_held check does not traverse .gzkit/locks/obpi/ subdir.
- Date: 2026-04-19

## Acceptance Criteria

- [x] REQ-0.0.17-06-01: AGENTS.md no longer buckets "Heavy/Foundation" for attestation; lane is the axis (heavy ⇒ Gate 5); foundation-kind ADRs follow ADR-0.0.18 doctrine.
- [x] REQ-0.0.17-06-02: AGENTS.md § Kinds (pool, foundation, feature) names all three kinds and cites OBPI-01..04 mechanical enforcement surfaces.
- [x] REQ-0.0.17-06-03: `docs/user/commands/plan-create.md` documents `--kind` (already landed in OBPI-02) and carries the ADR-0.0.18 cross-link (added this OBPI).
- [x] REQ-0.0.17-06-04: No doctrine-scope overlap with ADR-0.0.18; "when to choose which" deferred via cross-links.
- [x] REQ-0.0.17-06-05: `gz agent sync control-surfaces` clean (no drift).
- [x] REQ-0.0.17-06-06: `mkdocs build --strict` clean (receipt `arb-step-mkdocs-a1499a1524cb47169f8d076a85046b4f`).
- [x] REQ-0.0.17-06-07: ADR-0.0.18 cross-links present in AGENTS.md (§ Kinds, § OBPI Acceptance Protocol, § Lane Inheritance Rule) and in plan-create.md (§ See also).

## REQ Coverage

- REQ-0.0.17-06-01 through REQ-0.0.17-06-07
