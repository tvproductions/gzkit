---
id: OBPI-0.0.21-01-physical-migration
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.0.21-01-physical-migration: Physical Migration of Chores Tree

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- **Checklist Item:** #1 — Physical migration: move `ops/chores/<33 dirs>` → `src/gzkit/chores/`; move `config/gzkit.chores.json` → `src/gzkit/chores/registry.json`; delete origin paths including `ops/chores/CLAUDE.md`.

**Status:** Draft

## Objective

Relocate the canonical chore tree (33 chore directories + registry JSON + agent-contract README) from `ops/chores/` and `config/` to `src/gzkit/chores/` using `git mv` so history is preserved, and delete the origin paths — producing the layout every downstream OBPI consumes.

## Lane

**Heavy** — changes the canonical on-disk location of a governance surface that downstream tooling (resolver, scaffolder, packaging) references. Layout is a runtime contract.

## Allowed Paths

- `ops/chores/**` — source of migration (read + delete)
- `config/gzkit.chores.json` — source of registry migration (read + delete)
- `src/gzkit/chores/**` — destination of migration (create)
- `src/gzkit/chores/registry.json` — destination of registry migration (create)
- `src/gzkit/chores/__init__.py` — package marker enabling `importlib.resources` lookup in OBPI-04

## Denied Paths

- `src/gzkit/commands/chores.py` — resolver changes belong to OBPI-04
- `src/gzkit/commands/chores_exec.py` — resolver changes belong to OBPI-04
- `src/gzkit/commands/init_cmd.py` — scaffolder wiring belongs to OBPI-05
- `src/gzkit/config.py` — config-key addition belongs to OBPI-02
- `pyproject.toml` — packaging changes belong to OBPI-03
- `.gzkit/rules/chores.md`, `docs/user/**`, `CLAUDE.md`, `AGENTS.md` — doc updates belong to OBPI-06
- `src/gzkit/governance/trust_audits.py` — layout validator belongs to OBPI-08
- `features/**`, `tests/**` — no test or BDD changes in this OBPI (migration is behavior-preserving at this step; the resolver OBPI re-tests)

## Requirements (FAIL-CLOSED)

1. `git mv ops/chores/<slug> src/gzkit/chores/<slug>` MUST be used for every directory so history is preserved; a bulk `mv` or copy-then-delete is NEVER acceptable.
2. Every chore directory under `ops/chores/` MUST land at `src/gzkit/chores/<same-slug>/` with byte-identical `CHORE.md`, `acceptance.json`, `README.md`, and `proofs/` subtree (if present).
3. `config/gzkit.chores.json` MUST be `git mv`'d to `src/gzkit/chores/registry.json`. The JSON content MUST be byte-identical at move time; any `path` field rewrite to reflect the new canonical location is ALLOWED as a separate follow-up commit inside this OBPI but MUST update every `"path": "ops/chores/<slug>"` to `"path": "<slug>"` (relative-to-registry) or to the resolver's expected shape — the final shape is coordinated with OBPI-04's resolver.
4. `ops/chores/CLAUDE.md` MUST be `git mv`'d into `src/gzkit/chores/README.md` (the agent contract content survives; the filename becomes the `.gzkit/` surface idiom).
5. `ops/chores/` and `config/gzkit.chores.json` MUST NOT exist after this OBPI completes. Leaving a stale `ops/chores/` root is a STOP condition — layout drift would immediately trigger the future OBPI-08 validator.
6. `src/gzkit/chores/__init__.py` MUST exist (even if empty) so `importlib.resources.files("gzkit.chores")` resolves at runtime.
7. No code file under `src/gzkit/commands/` MAY be edited in this OBPI — the CLI MUST keep working in a broken state (chores commands will fail until OBPI-04 lands) and that is the expected migration-window state.
8. `uv run gz chores list` is EXPECTED to fail after this OBPI until OBPI-02/03/04 land. This OBPI does NOT attempt to keep the command working across the migration.

> STOP-on-BLOCKERS:
> - If any chore under `ops/chores/` has uncommitted local modifications, STOP and request operator confirmation before moving.
> - If `git mv` reports a name collision (a `src/gzkit/chores/<slug>/` already exists), STOP and investigate — do not merge silently.
> - If the operator has added project-local chores directly to `ops/chores/` that are not in `config/gzkit.chores.json`, STOP and register them in the registry before moving (or confirm they should be dropped).

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Prime Directive, § DO IT RIGHT
- [ ] Parent ADR ADR-0.0.21 § Decision items 1, 2, 11
- [ ] `.gzkit/rules/chores.md` (current workflow rule referencing `ops/chores/`)

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- [ ] Sibling OBPIs 02, 03, 04, 05, 06 — confirm no path overlap

**Prerequisites (check existence, STOP if missing):**

- [ ] `ops/chores/` exists and contains ~33 subdirectories (`ls ops/chores/ | wc -l`)
- [ ] `config/gzkit.chores.json` exists and parses as JSON (`python -c "import json; json.load(open('config/gzkit.chores.json'))"`)
- [ ] `ops/chores/CLAUDE.md` exists
- [ ] `src/gzkit/chores/` does NOT yet exist (green-field destination)
- [ ] Git working tree is clean — run `git status` and abort if dirty

**Existing Code (understand current state):**

- [ ] Read `src/gzkit/skills.py:302-338` as the layout-parity exemplar (canonical source under `src/gzkit/`)
- [ ] Read `ops/chores/README.md` and `ops/chores/CLAUDE.md` — understand what survives as `src/gzkit/chores/README.md`
- [ ] Read 2-3 sample `ops/chores/<slug>/CHORE.md` + `acceptance.json` pairs to confirm the data shape

## Quality Gates

### Gate 1 (ADR)

- [ ] Intent and scope recorded in this brief
- [ ] Parent ADR Decision #1, #2, #11 cited

### Gate 2 (TDD — Red-Green-Refactor)

- [ ] **Note:** this OBPI is a file-move only; no code changes. TDD applies to OBPIs 02, 04, 05, 08, 09. For this OBPI, the Red-Green discipline is replaced by pre/post structural assertions captured in Verification evidence.

### Code Quality

- [ ] `uv run gz lint` (no-op expected — no code touched)
- [ ] `uv run gz typecheck` (no-op expected)

### Gate 3 (Docs) — Heavy

- [ ] `uv run mkdocs build --strict` passes (migration must not break existing cross-references; any break is escalated to OBPI-06 in the same PR if discovered here)

### Gate 4 (BDD) — Heavy

- [ ] Deferred to OBPI-07. This OBPI does not add BDD coverage.

### Gate 5 (Human) — Heavy + Foundation

- [ ] Brief-level human attestation via `gz obpi complete --attestation-text "<verbatim-user-words> — <session-grounded enrichment>"`

## Verification

```bash
# Pre-state (record as evidence)
ls ops/chores/ | wc -l                                  # expect ~33
test -f config/gzkit.chores.json
test -f ops/chores/CLAUDE.md

# Execute migration
git mv ops/chores src/gzkit/chores
git mv src/gzkit/chores/CLAUDE.md src/gzkit/chores/README.md
git mv config/gzkit.chores.json src/gzkit/chores/registry.json
touch src/gzkit/chores/__init__.py

# Post-state assertions
test ! -e ops/chores
test ! -e config/gzkit.chores.json
test -f src/gzkit/chores/README.md
test -f src/gzkit/chores/registry.json
test -f src/gzkit/chores/__init__.py
test "$(ls src/gzkit/chores/ | grep -E '^[a-z0-9-]+$' | wc -l)" -ge 30

# Byte-identical chore data (pick 3 representative slugs)
for slug in coverage-40pct dependency-currency cli-contract-governance; do
  test -f src/gzkit/chores/$slug/CHORE.md
  test -f src/gzkit/chores/$slug/acceptance.json
done

# Registry resolves as JSON
uv run python -c "import json, sys; sys.stdout.reconfigure(encoding='utf-8'); json.load(open('src/gzkit/chores/registry.json'))"

# Existing validators still green (no unrelated regressions)
uv run gz validate --documents --surfaces
uv run mkdocs build --strict
```

## Acceptance Criteria

- [ ] REQ-0.0.21-01-01: `ops/chores/` does not exist in the working tree after this OBPI.
- [ ] REQ-0.0.21-01-02: `config/gzkit.chores.json` does not exist in the working tree after this OBPI.
- [ ] REQ-0.0.21-01-03: `src/gzkit/chores/<slug>/` exists for every slug that previously existed under `ops/chores/<slug>/`, with byte-identical `CHORE.md` and `acceptance.json` content.
- [ ] REQ-0.0.21-01-04: `src/gzkit/chores/registry.json` exists and parses as valid JSON.
- [ ] REQ-0.0.21-01-05: `src/gzkit/chores/README.md` exists and contains the agent-contract content migrated from `ops/chores/CLAUDE.md`.
- [ ] REQ-0.0.21-01-06: `src/gzkit/chores/__init__.py` exists (empty is fine) enabling `importlib.resources.files("gzkit.chores")` resolution used by OBPI-04.
- [ ] REQ-0.0.21-01-07: `git log --follow src/gzkit/chores/<sample-slug>/CHORE.md` shows history predating the migration commit (proof that `git mv` was used, not copy-then-delete).
- [ ] REQ-0.0.21-01-08: `uv run mkdocs build --strict` exits 0 (no cross-reference breakage).

## Completion Checklist

- [ ] **Gate 1:** Intent recorded in brief; parent ADR cited.
- [ ] **Gate 2:** N/A — pure file-move OBPI. Structural pre/post assertions recorded in Evidence.
- [ ] **Code Quality:** lint + typecheck no-op green.
- [ ] **Gate 3:** docs build green.
- [ ] **Gate 5:** human attestation recorded.
- [ ] **Value Narrative:** before — chores lived outside src/ and were undistributable; after — canonical tree in `src/gzkit/chores/` and agent contract surfaced as `README.md`.
- [ ] **Key Proof:** `ls src/gzkit/chores/ | wc -l` ≥ 30 AND `test ! -e ops/chores`.

## Evidence

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD)
```text
N/A — file-move OBPI; see structural assertions in Verification evidence.
```

### Code Quality
```text
# paste uv run gz lint, uv run gz typecheck output
```

### Gate 3 (Docs)
```text
# paste uv run mkdocs build --strict output
```

### Gate 5 (Human)
```text
# paste attestation text
```

### Value Narrative
Before: chore definitions lived in `ops/chores/` outside the `src/` tree, were not packaged in the wheel, and had no parity with other `.gzkit/` surfaces. After: canonical source at `src/gzkit/chores/` aligned with skills/personas precedent, ready for packaging (OBPI-03) and resolution (OBPI-04).

### Key Proof

```
$ test ! -e ops/chores && test ! -e config/gzkit.chores.json && echo migrated
migrated

$ ls src/gzkit/chores/ | grep -E '^[a-z0-9-]+$' | wc -l
      32

$ shasum -a 256 src/gzkit/chores/coverage-40pct/CHORE.md
44fa69219e00fb59a2c8fa7f4c8fcb692ccfeaa9ac34edffaa15f7b9854dba0b  src/gzkit/chores/coverage-40pct/CHORE.md
# (matches pre-move ops/chores/coverage-40pct/CHORE.md — byte-identical via git mv)

$ shasum -a 256 src/gzkit/chores/README.md
282897ca0ffadfd8c1a929764712cd40bd0205f3600d70acb8701b54ae4775cf  src/gzkit/chores/README.md
# (matches pre-move ops/chores/CLAUDE.md — agent contract content survives per REQ-05)

$ uv run python -c "import json; d=json.load(open('src/gzkit/chores/registry.json')); print(list(d.keys())[:5])"
['specVersion', 'description', 'project', 'lanes', 'chores']

$ uv run mkdocs build --strict    # REQ-08
INFO    -  Documentation built in 2.75 seconds
# exit 0, ARB receipt arb-step-mkdocs-12770bc390de4ddda3979a75864d4c8f
```

ARB receipts (Heavy lane): lint `arb-ruff-1a953b4a84804ff5b12a7e527674980e`; typecheck `arb-step-typecheck-8f6282ba57764b37ab5bcd09a593cd31`; mkdocs/REQ-08 `arb-step-mkdocs-12770bc390de4ddda3979a75864d4c8f`. Gate 2 N/A per brief (file-move OBPI); `gz covers OBPI-0.0.21-01-physical-migration` → `uncovered_reqs == 0`.

### Implementation Summary

- Files moved: 175 tracked files from `ops/chores/**` to `src/gzkit/chores/**` via `git mv` (history preserved); `config/gzkit.chores.json` → `src/gzkit/chores/registry.json`; `ops/chores/CLAUDE.md` → `src/gzkit/chores/README.md`
- Files created: `src/gzkit/chores/__init__.py` (empty — enables `importlib.resources.files("gzkit.chores")` for OBPI-04)
- Files deleted: `ops/chores/` root, `config/gzkit.chores.json`, pre-existing `ops/chores/README.md` (superseded by CLAUDE.md agent contract per REQ-05)
- Tests added: N/A — brief explicitly marks Gate 2 as N/A for this file-move OBPI; pre/post structural assertions replace Red-Green discipline
- Date completed: 2026-04-24
- Attestation status: operator-attested (Heavy + Foundation → brief-level human gate)
- Defects noted: GHI #301 filed for Stage-4 REQ-coverage table cosmetic double-render (non-blocking)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.21-01-physical-migration executed: 175 tracked files relocated via git mv from ops/chores/** to src/gzkit/chores/**, config/gzkit.chores.json → src/gzkit/chores/registry.json, ops/chores/CLAUDE.md → src/gzkit/chores/README.md (byte-identical checksums verified on coverage-40pct, dependency-currency, cli-contract-governance), ops/chores/ and config/gzkit.chores.json absent post-migration, src/gzkit/chores/__init__.py created (empty, enables importlib.resources). All 8 REQs pass structural assertions. Gate 2 N/A per brief (file-move OBPI). Heavy-lane ARB receipts: lint arb-ruff-1a953b4a84804ff5b12a7e527674980e; types arb-step-typecheck-8f6282ba57764b37ab5bcd09a593cd31; docs (Gate 3 / REQ-08) arb-step-mkdocs-12770bc390de4ddda3979a75864d4c8f. Cosmetic ceremony-render defect tracked as GHI #301 (non-blocking).
- Date: 2026-04-24

---

**Brief Status:** Completed

**Date Completed:** 2026-04-24

**Evidence Hash:** -
