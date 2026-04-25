# Plan — OBPI-0.0.21-06-rule-and-doc-updates: Rule and Documentation Updates

OBPI canonical slug: `OBPI-0.0.21-06-rule-and-doc-updates`

## Context

ADR-0.0.21 moves the chores surface from `ops/chores/` + `config/gzkit.chores.json`
(removed by OBPI-01) to a two-surface layout: canonical package source under
`src/gzkit/chores/` (shipped in the wheel) plus an optional project-local overlay
under `.gzkit/chores/`. OBPI-04 (Completed) added the `--explain` flag to the
resolver. Sibling OBPIs 08 (`gz validate --chores-layout`) and 09 (`gz chores
doctor`) are Draft but specify exact CLI shapes in their REQs — those shapes are
the canon source of truth for documentation.

Today, the operator-facing surfaces still describe the old layout:

- `.gzkit/rules/chores.md` frontmatter `paths:` lists `src/gzkit/**`, `config/**`
  (overly broad, doesn't reflect new layout); body is silent on the two-surface
  resolution model.
- `src/gzkit/chores/README.md` was migrated by OBPI-01 but still references
  `config/gzkit.chores.json` (line 25), `ops/chores/...` (lines 47, 84-89), and
  the pre-migration template tree.
- `docs/user/runbook.md` § Chores Commands lists `list/show/advise/plan/run/audit`
  — missing `--explain` and the forthcoming `doctor`.
- No `docs/user/manpages/gz-chores.md` exists (only arb, closeout, gz-justify,
  gz-personas, patch-release).
- `CLAUDE.md`, `AGENTS.md`, root grep is clean (no `ops/chores` or
  `config/gzkit.chores` hits) — verify and no-op.
- `docs/governance/GovZero/gzkit-structure.md` exists; pre-grep shows zero
  `chores`/`ops/` hits — verify and no-op.
- `docs/user/concepts/` contains no chores page — no-op.

Acceptance is mechanical: `grep -rn "ops/chores\|config/gzkit\.chores" .gzkit/rules/
docs/ CLAUDE.md AGENTS.md` returns zero hits; `gz validate --documents --surfaces
--brief-headings --cli-alignment` exits 0; `mkdocs build --strict` passes;
`gz agent sync control-surfaces` shows no drift.

**Sibling-shape risk (STOP-on-BLOCKERS).** OBPI-08 and OBPI-09 are Draft, but
each brief specifies REQs nailing the exact CLI shape (subcommand names, flags,
exit codes). Per the brief's intent — documenting the parent ADR's committed
surface — I will document per the OBPI briefs' REQs. If the briefs change later,
this OBPI's docs get re-synced as part of those OBPIs' Gate 3 work.

## Critical Files To Modify

| File | Action | Why |
|------|--------|-----|
| `.gzkit/rules/chores.md` | Rewrite frontmatter `paths:` and body | REQ-01, REQ-07; bump skill-version |
| `src/gzkit/chores/README.md` | Rewrite for new two-surface layout | REQ-03; remove `ops/chores`/`config/gzkit.chores.json` refs |
| `docs/user/manpages/gz-chores.md` | **NEW** | REQ-02; cover all subcommands incl. `doctor` and `--explain` |
| `docs/user/runbook.md` | Edit § Chores Commands (lines 691-702) | REQ-03 (parent: documenting `gz chores` surface); add `--explain` and `doctor` |

## Files Verified Clean (No Action)

- `CLAUDE.md`, `AGENTS.md` — pre-grep returned zero hits for stale refs
- `docs/governance/GovZero/gzkit-structure.md` — pre-grep returned zero hits
- `docs/user/concepts/` — no chores page exists; nothing to update

## Out-of-Scope Defects (Track, Don't Fix)

- `.gzkit/skills/gz-chore-runner/SKILL.md` references `config/gzkit.chores.json`
  (line 24) and `ops/chores/{slug}/proofs/CHORE-LOG.md` (line 29). The brief's
  Allowed Paths do **not** include `.gzkit/skills/**`. Defer to a follow-up
  GHI rather than expanding scope. Will file `gh issue create --label defect`
  if the operator agrees, or note in evidence section.

## Implementation Steps

1. **`.gzkit/rules/chores.md`** — rewrite frontmatter `paths:` to scope the rule
   to `src/gzkit/chores/**` and `.gzkit/chores/**`; bump version (add a
   `metadata.skill-version` field — current file has none, so introduce it at
   `0.1.0` to match canonical pattern in other rules); rewrite body to describe
   the two-surface resolution model (project-first → package-fallback) and the
   `--explain`/`doctor`/`--chores-layout` surfaces.

2. **`src/gzkit/chores/README.md`** — rewrite as canonical agent contract:
   - Two-surface layout explainer (`src/gzkit/chores/<slug>/` is canon, shipped
     in wheel; `.gzkit/chores/<slug>/` is optional project overlay; `proofs/` is
     **always project-local, never canonical**).
   - File table per slug: `CHORE.md`, `acceptance.json`, `README.md`, plus
     `proofs/` (project-local execution evidence).
   - Discovery: `gz chores list --explain` shows resolution source.
   - Authoring guidance for new chores (canonical lives in `src/gzkit/chores/`,
     project overrides go in `.gzkit/chores/`).
   - Health check: `gz chores doctor` (per OBPI-09 REQ-09-01..09).
   - Layout enforcement: `gz validate --chores-layout` (per OBPI-08 REQ-08-04).
   - Strip every `ops/chores/` and `config/gzkit.chores.json` reference.

3. **`docs/user/manpages/gz-chores.md`** — NEW manpage matching the shape of
   `gz-personas.md` (synopsis, subcommand sections, options table, exit codes,
   examples). Required sections per REQ-02: Synopsis, Description, Subcommands
   (`list`, `show`, `plan`, `advise`, `run`, `audit`, `doctor`), Options
   (including `--explain` on `list`, `--dry-run`/`--json` on `doctor`), Exit
   Codes (0/1/2/3 per `.gzkit/rules/cli.md`), Examples, Files (naming both
   `.gzkit/chores/` and `importlib.resources("gzkit.chores")` per REQ-04 of
   parent OBPI text + REQ-04-02 of OBPI-04). See Also section linking the
   skill and parent ADR.

4. **`docs/user/runbook.md`** — edit § Chores Commands (lines 691-702): add
   `gz chores list --explain`, add `gz chores doctor [--dry-run] [--json]`, and
   note the project-first → package-fallback resolution. Keep existing examples
   that already resolve to registered verbs.

5. **Sync** — `uv run gz agent sync control-surfaces` propagates `.gzkit/rules/`
   to `.claude/rules/` and `.github/instructions/`. Vendor mirrors are
   write-only outputs; never edit directly.

6. **Verify**:
   - `grep -rn "ops/chores\|config/gzkit\.chores" .gzkit/rules/ docs/ CLAUDE.md AGENTS.md` → zero hits
   - `uv run gz validate --documents --surfaces --brief-headings --cli-alignment` → exit 0
   - `uv run gz lint` → green
   - `uv run mkdocs build --strict` → green
   - `uv run gz agent sync control-surfaces` re-run → no drift on second invocation

## Subagent Strategy

This OBPI is docs-only with mechanical requirements and a small file count
(4 files). Per the OBPI Decomposition Matrix and the pipeline's complexity
classifier, this falls under the `simple`/`standard` boundary. Recommendation:
**inline implementation** (`--no-subagents` semantics). The brief allowlist is
narrow, the changes are coordinated (manpage cross-references the rule and
README), and a single coherent author produces fewer cross-file inconsistencies
than parallel subagents on a doc set this small.

## Verification (End-to-End)

```bash
# REQ-01 mechanical check
grep -rn "ops/chores\|config/gzkit\.chores" .gzkit/rules/ docs/ CLAUDE.md AGENTS.md \
  | grep -v "^Binary" | grep -v ".gzkit/ledger.jsonl"
# Expected: empty

# REQ-02 manpage shape
test -f docs/user/manpages/gz-chores.md
grep -E "^##? (Synopsis|Description|Subcommands|Options|Exit Codes|Examples|Files)" \
  docs/user/manpages/gz-chores.md

# REQ-04
uv run gz validate --documents --surfaces --brief-headings --cli-alignment

# REQ-05
uv run mkdocs build --strict

# REQ-06 (mirror parity)
uv run gz agent sync control-surfaces
# Re-run; second run must report no drift
uv run gz agent sync control-surfaces

# REQ-07 (version bump) — confirm via inspection
grep "skill-version" .gzkit/rules/chores.md
```

## Risks / Open Questions

1. **Should `.gzkit/skills/gz-chore-runner/SKILL.md` defect be fixed in this OBPI
   or deferred?** Allowed Paths exclude `.gzkit/skills/**`. Recommendation: file
   a follow-up GHI; do not expand scope. (Will confirm with operator at Stage 4
   ceremony or earlier if explicit direction is desired.)

2. **`.gzkit/rules/chores.md` has no `skill-version` today** — REQ-07 says "MUST
   be bumped". Treating "introduce a starting version" as compliance with intent
   (the rule has never had a version marker; introducing `0.1.0` establishes the
   versioning baseline mandated by `.claude/rules/skill-surface-sync.md`).
