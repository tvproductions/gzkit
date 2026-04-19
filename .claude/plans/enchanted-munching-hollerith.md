# Plan: OBPI-0.0.17-06-agents-md-correction — AGENTS.md + docs/user correction

Full OBPI slug: `OBPI-0.0.17-06-agents-md-correction`. Parent ADR: `ADR-0.0.17-adr-taxonomy-mechanical`.

## Context

OBPI-0.0.17-06-agents-md-correction is the final OBPI under ADR-0.0.17 (ADR Taxonomy — Mechanical). OBPIs 01-05 landed the schema, CLI (`--kind`), validator, promote flag, and backfill. This OBPI closes the loop by fixing the governance-doctrine surfaces that conflate `kind` (pool / foundation / feature) with `lane` (heavy / lite).

Current defect: `AGENTS.md` and two adjacent surfaces treat "Heavy/Foundation" as a single attestation bucket. ADR-0.0.17 § Decision #2 declared this wrong — attestation rigor attaches to **lane** (heavy ⇒ Gate 5), and foundation-kind ADRs follow the attestation doctrine in ADR-0.0.18 regardless of lane.

Intended outcome:
- `AGENTS.md` documents `kind` and `lane` as orthogonal axes and names all three kinds.
- `docs/user/commands/plan-create.md` cross-links to ADR-0.0.18 (the "when to choose which" doctrine).
- `docs/user/concepts/lifecycle.md:64` is corrected.
- Copilot mirror + generated CLAUDE.md stay in sync.
- `mkdocs --strict` is green; `gz agent sync` reports no drift.

Lane: Lite (docs-only, no CLI/schema/test surface touched). Parent ADR is foundation/heavy — human attestation required at Stage 4.

## Scope amendment (canonical vs generated)

Brief Allowed Paths list `AGENTS.md`, `CLAUDE.md`, `docs/user/commands/plan.md`, `docs/user/concepts/**`, `docs/governance/**`. Mechanical reality:

- `AGENTS.md` is **generated** by `gz agent sync control-surfaces` from `src/gzkit/templates/agents.md` (see `src/gzkit/sync_surfaces.py:323-335`). Editing the generated file is overwritten on next sync (§ skill-surface-sync.md anti-pattern).
- `.github/copilot-instructions.md` is generated from `src/gzkit/templates/copilot.md` (same sync module).
- `CLAUDE.md` is `@AGENTS.md` + `agents.local.md` — inherits the template edit transitively.
- The real CLI doc is `docs/user/commands/plan-create.md` (not `plan.md`, which does not exist).

The canonical, non-drifting edit targets are `src/gzkit/templates/agents.md` and `src/gzkit/templates/copilot.md`. These are **not** "schema, CLI, validator, or test surfaces" (the brief's denied scope); they are the template source for the allowed doc outputs. Treating them as in-scope is consistent with the brief's intent and the governance-sync discipline. Flagging explicitly per § scope-honesty.

## Requirements → evidence map

| REQ | Mechanism | Evidence |
|-----|-----------|----------|
| REQ-0.0.17-06-01 | Remove "Heavy/Foundation" bucketing from AGENTS.md Acceptance Protocol (template line 206) + Lane Inheritance Rule table (lines 222-227) | AGENTS.md diff after sync |
| REQ-0.0.17-06-02 | New "### Kinds" subsection in AGENTS.md template naming pool/foundation/feature + citing OBPI-01..04 enforcement | AGENTS.md diff |
| REQ-0.0.17-06-03 | Verify `plan-create.md` already documents `--kind` with foundation/feature examples; add "See also" cross-link to ADR-0.0.18 | plan-create.md diff |
| REQ-0.0.17-06-04 | Keep all OBPI-06 text **mechanical only** (kind names, enforcement surfaces, orthogonality); defer "when to choose which" to ADR-0.0.18 via cross-link | Self-review of diff |
| REQ-0.0.17-06-05 | `uv run gz agent sync control-surfaces` — zero drift | Sync command exit 0 + clean output |
| REQ-0.0.17-06-06 | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` — receipt present | ARB receipt `arb-step-mkdocs-*` |
| REQ-0.0.17-06-07 | Cross-link to ADR-0.0.18 appears in both AGENTS.md (new Kinds section) and plan-create.md | Grep confirmation post-sync |

No `@covers` parity gate applies — this is Lite-lane, docs-only, with no REQ-tagged tests. Evidence is diff + ARB receipt + sync drift status, per the brief's own Evidence section.

## Critical files to modify

1. **`src/gzkit/templates/agents.md`** — three local edits:
   - Line 206 (OBPI Acceptance Protocol opening sentence): rewrite lane-first.
   - Lines 222-227 (Lane Inheritance Rule table + note): replace two-row "Heavy/Foundation / Lite" table with single-axis table keyed on lane, with a separate paragraph naming foundation-kind rigor and cross-linking ADR-0.0.18.
   - Insert new `### Kinds (pool, foundation, feature)` subsection immediately after the Lane Rules subsection (around line 218), naming the three kinds + citing the four mechanical enforcement surfaces: `kind:` frontmatter (OBPI-01), `gz plan create --kind` (OBPI-02), `gz adr promote --kind` (OBPI-03), `gz validate --taxonomy` (OBPI-04). Ends with "See ADR-0.0.18 for when to choose which."

2. **`src/gzkit/templates/copilot.md` line 44** — rewrite: "Heavy lane work (any kind) requires explicit human attestation. Foundation-kind ADRs follow the attestation doctrine in ADR-0.0.18."

3. **`docs/user/commands/plan-create.md`** — add "See also" cross-link to `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/` near the `--kind` row or at the bottom of the page.

4. **`docs/user/concepts/lifecycle.md:64`** — rewrite: "Heavy-lane parent ADRs require explicit human-attestation evidence. Foundation-kind ADRs additionally follow the attestation protocol in ADR-0.0.18 regardless of lane."

## Implementation steps

1. Edit `src/gzkit/templates/agents.md` (three changes: line 206 sentence, lines 222-227 table/paragraph, new Kinds subsection).
2. Edit `src/gzkit/templates/copilot.md` (single sentence on line 44).
3. Edit `docs/user/concepts/lifecycle.md` (single sentence on line 64).
4. Edit `docs/user/commands/plan-create.md` (add ADR-0.0.18 cross-link).
5. Run `uv run gz agent sync control-surfaces`. Expect: regenerates `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`; reports zero drift.
6. Run `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`. Expect: ARB receipt emitted, exit 0.
7. Run `uv run gz arb ruff` for good-measure lint (no `.py` edits but template files are in tree).
8. Manual re-read of rendered `AGENTS.md` for REQ-1 verification ("no residual Heavy/Foundation bucketing").

## Verification (end-to-end)

```bash
uv run gz agent sync control-surfaces            # REQ-5 — zero drift
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict   # REQ-6
uv run gz arb ruff                               # no .py changes but lint clean
grep -rn "Heavy/Foundation\|Heavy or Foundation\|Foundational (0\.0\.x)" \
  AGENTS.md CLAUDE.md .github/copilot-instructions.md docs/     # expect no hits
grep -n "ADR-0.0.18" AGENTS.md docs/user/commands/plan-create.md  # REQ-7
```

## Existing functions / utilities reused

- `gz agent sync control-surfaces` (`src/gzkit/sync_surfaces.py:sync_agents_md`, `sync_copilot_instructions`) — the regeneration pipeline. Not modified.
- `gz arb step` (`src/gzkit/arb/`) — canonical invocation per `.gzkit/rules/attestation-enrichment.md` § Canonical invocations. Produces `arb-step-mkdocs-*` receipt.
- ADR-0.0.17 § Decision #2 — the operator-locked axis statement that this OBPI is implementing.
- ADR-0.0.18 — cross-link target for "when to choose which" doctrine.

## Out of scope (guarded)

- `docs/user/concepts/adr-taxonomy.md` — owned by ADR-0.0.18 per its Intent section. Do not create here.
- Any `.gzkit/skills/**` or `.claude/skills/**` edits — explicitly denied.
- Renaming or restructuring ADRs.
- Editing the validator, schema, or CLI parser — covered by OBPIs 01-04, already attested.
