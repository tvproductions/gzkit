# OBPI-0.0.21-01-physical-migration — Physical Migration of Chores Tree

**OBPI ID:** `OBPI-0.0.21-01-physical-migration` (parent ADR: `ADR-0.0.21-chores-as-gzkit-surface`)

## Context

ADR-0.0.21 decides that chores become a `.gzkit/`-parity surface: canonical source under `src/gzkit/chores/` (packaged in the wheel), project-scaffolded mirror at `.gzkit/chores/` (via `gz init`), resolver fallback from project to package. Today chores live at `ops/chores/<33 dirs>/` with a registry at `config/gzkit.chores.json` — outside `src/`, undistributable, and without parity with skills/personas.

This OBPI is the pure physical move: `git mv` the tree and registry into their canonical locations, preserve history, delete origin paths. No code, schema, or doc changes — those belong to downstream OBPIs (02 config, 03 packaging, 04 resolver, 05 scaffolder, 06 docs, 07 BDD, 08 validator). The CLI (`gz chores list`, etc.) is expected to be broken across the migration window until OBPI-04 lands; that breakage is explicitly accepted by the brief (REQ-8).

Scope is file-move only. The brief (Heavy lane, Foundation kind) requires:
- `git mv` (never copy-then-delete) so `git log --follow` proves history
- byte-identical `CHORE.md` / `acceptance.json` / `README.md` / `proofs/` subtrees post-move
- `ops/chores/CLAUDE.md` → `src/gzkit/chores/README.md` (name change only; content survives)
- `config/gzkit.chores.json` → `src/gzkit/chores/registry.json` (byte-identical at move time)
- new empty `src/gzkit/chores/__init__.py` so `importlib.resources.files("gzkit.chores")` works for OBPI-04
- `ops/chores/` and `config/gzkit.chores.json` MUST NOT exist after the OBPI

## Pre-flight observations

- `ops/chores/` exists with 33 chore dirs + `CLAUDE.md` + `README.md` (34 entries total).
- `config/gzkit.chores.json` exists.
- `src/gzkit/chores/` does **not** exist (green-field destination — no collision risk).
- Git tree has expected in-flight state: `.gzkit/ledger.jsonl` modified, `AGENTS.md` modified, ADR-0.0.21 package directory untracked. Per the brief the "clean tree" check is for chore content itself; none of the dirty paths overlap `ops/chores/**` or `config/gzkit.chores.json`, so the STOP-on-BLOCKERS gates (chore-local modifications, destination collision, unregistered local chores) are all clear.
- One surprise item to confirm with the operator: `ops/chores/README.md` exists alongside `ops/chores/CLAUDE.md`. The brief mandates `CLAUDE.md → src/gzkit/chores/README.md` but is silent on the pre-existing `ops/chores/README.md`. The safest read is to drop it (the CLAUDE.md content supersedes it as the canonical agent contract under the new idiom); the plan assumes drop with operator confirmation at commit time via the closure-narrative gate.

## Plan

Single task: **Execute the physical migration and verify structural invariants.**

All changes land in one logical unit (migration commit in Stage 5's git-sync). No subagent dispatch — the work is a deterministic sequence of `git mv` operations that the main session should perform inline so the brief's structural pre/post assertions can be captured verbatim.

### Step-by-step

1. **Record pre-state evidence** (read-only).
   - `ls ops/chores/ | wc -l` → expect 34
   - `git ls-files ops/chores/ | wc -l` → confirm tracked entry count
   - capture `git log -1 --format=%H ops/chores/coverage-40pct/CHORE.md` to later prove `git mv` preserved history

2. **Execute the migration** (in this order — resolver expectations preserved):
   - `git mv ops/chores src/gzkit/chores`
   - `git mv src/gzkit/chores/CLAUDE.md src/gzkit/chores/README.md` — this overwrites the pre-existing `src/gzkit/chores/README.md` (the carried-over `ops/chores/README.md`). Operator confirmation captured via Stage 5 closure narrative. Alternative: if operator says keep the original README.md, instead `git rm src/gzkit/chores/README.md && git mv src/gzkit/chores/CLAUDE.md src/gzkit/chores/README.md`.
   - `git mv config/gzkit.chores.json src/gzkit/chores/registry.json`
   - Create `src/gzkit/chores/__init__.py` as an empty file (Write tool).

3. **Post-state assertions** (verbatim from brief Verification section):
   - `test ! -e ops/chores`
   - `test ! -e config/gzkit.chores.json`
   - `test -f src/gzkit/chores/README.md`
   - `test -f src/gzkit/chores/registry.json`
   - `test -f src/gzkit/chores/__init__.py`
   - `ls src/gzkit/chores/ | grep -E '^[a-z0-9-]+$' | wc -l` ≥ 30
   - For slugs `coverage-40pct`, `dependency-currency`, `cli-contract-governance`: `test -f src/gzkit/chores/<slug>/CHORE.md && test -f src/gzkit/chores/<slug>/acceptance.json`
   - `uv run python -c "import json, sys; sys.stdout.reconfigure(encoding='utf-8'); json.load(open('src/gzkit/chores/registry.json'))"`
   - `git log --follow src/gzkit/chores/coverage-40pct/CHORE.md | head` — verify history predates the migration commit (REQ-07)

4. **Baseline quality checks** (Stage 3 will re-run):
   - `uv run gz lint` — expected no-op
   - `uv run gz typecheck` — expected no-op
   - `uv run gz validate --documents --surfaces` — must still pass; if it fails because of a cross-reference to `ops/chores/` this escalates to OBPI-06 (per the brief)
   - `uv run mkdocs build --strict` — REQ-08

## Files touched

- **Moved** (33 dirs + 2 files via `git mv`):
  - `ops/chores/*` → `src/gzkit/chores/*`
  - `ops/chores/CLAUDE.md` → `src/gzkit/chores/README.md`
  - `config/gzkit.chores.json` → `src/gzkit/chores/registry.json`
- **Created:**
  - `src/gzkit/chores/__init__.py` (empty package marker)
- **Deleted** (implicit via `git mv`): `ops/chores/`, `config/gzkit.chores.json`
- **Possibly deleted** (operator confirmation needed): pre-existing `ops/chores/README.md`

Strictly within Allowed Paths. All denied paths (`src/gzkit/commands/chores*.py`, `pyproject.toml`, `.gzkit/rules/chores.md`, `CLAUDE.md`, `AGENTS.md`, `tests/**`, `features/**`, `src/gzkit/governance/trust_audits.py`, `src/gzkit/commands/init_cmd.py`, `src/gzkit/config.py`) are untouched.

## Acceptance mapping

| REQ | Satisfied by |
|-----|--------------|
| REQ-0.0.21-01-01 (`ops/chores/` absent) | `test ! -e ops/chores` post-assertion |
| REQ-0.0.21-01-02 (`config/gzkit.chores.json` absent) | `test ! -e config/gzkit.chores.json` post-assertion |
| REQ-0.0.21-01-03 (byte-identical chore subtree at new root) | `git mv` preserves bytes; sample-slug file-existence checks |
| REQ-0.0.21-01-04 (registry parses) | `json.load` post-assertion |
| REQ-0.0.21-01-05 (`README.md` carries agent contract) | `git mv CLAUDE.md → README.md` |
| REQ-0.0.21-01-06 (`__init__.py` exists) | empty file created via Write |
| REQ-0.0.21-01-07 (`git log --follow` history preserved) | verified via `git log --follow` on sample slug |
| REQ-0.0.21-01-08 (mkdocs clean) | `uv run mkdocs build --strict` in Stage 3 |

## Stage 4 evidence outline (Normal mode — Heavy + Foundation → human attestation required)

Per AGENTS.md § OBPI Acceptance Protocol, this OBPI's parent ADR is Heavy-lane AND Foundation-kind, so Stage 4 is a **HUMAN GATE** — the agent must present full evidence and wait for operator `attest completed`. Evidence table will include lint/typecheck/mkdocs/validate results, the 8 REQ rows with `@covers location: N/A (file-move OBPI; structural assertions in Verification)` since no `@covers` decorator exists for a file-move (Gate 2 is explicitly N/A per the brief), pre/post tree snapshots, and the `git log --follow` output proving history preservation.

## Verification summary

- **Structural:** the 10 post-state assertions in Step 3 above
- **Baseline quality:** `gz lint`, `gz typecheck`, `gz validate --documents --surfaces`, `mkdocs build --strict`
- **Downstream blast radius (intentional):** `uv run gz chores list` will fail — expected and explicitly accepted by REQ-8 until OBPI-04 lands
