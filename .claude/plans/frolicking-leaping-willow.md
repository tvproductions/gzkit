# Plan — OBPI-0.0.65-03: `gz handoff` CLI verb

## Context

**Why this work exists.** ADR-0.0.65 (*handoff-system-consolidation*, foundation, heavy)
is a **Class-2 foundation** in the active Build-to-1.0 campaign — "attested-but-unclosed,
finished-then-frozen." Its Sunset-sequence directive (06-30 campaign, 07-12 amendment,
line 522) is **"finish 0.0.65 first."** The ADR is **3/5 OBPIs attested** (01/02/04 done);
the two remaining briefs block closeout. OBPI-05 (`gz handoff archive`) **hard-depends on
OBPI-03** (the `gz handoff` verb must exist first), so **OBPI-03 is the only unblocked item**
and the correct next pull.

**The gap OBPI-03 closes.** ADR § Decision item #3: *"Add a `gz handoff` CLI verb (the
original GHI #529 ask) exposing create/resume/list, so handoff authoring routes through the
validation gate instead of hand-authored markdown."* OBPI-02 already shipped the business
logic in `src/gzkit/handoff_api.py` (`create_handoff`, `resume_handoff`, `list_handoffs`,
`load_handoff_chain`, `scaffold_handoff`). **OBPI-03 is purely the CLI adapter over that
shipped surface** — no new domain logic. Today, handoff authoring is hand-written markdown
that bypasses `validate_handoff_document`; the verb makes the gate mechanical.

**Governance findings surfaced (tracked, non-blocking):**
- Active campaign line 509 says "0.0.65 1/5" — stale; ledger truth is 3/5 (Layer-3 drift).
- OBPI-05's brief carries the superseded 06-10 "Phase C" fence — reconcile when OBPI-05 is pulled.

## Design

A thin, read-mostly CLI adapter following the **`gz airlock in|out`** exemplar exactly.
The verb is homed in **`parser_maintenance.py`** — this is a **coupled-surface constraint**:
OBPI-05's Allowed Paths declare it will register the `archive` subcommand in
`parser_maintenance.py` "under the `gz handoff` verb established by OBPI-0.0.65-03."

| Subcommand | Wraps (`handoff_api.py`) | Nature | Output |
|---|---|---|---|
| `gz handoff list [--adr ID] [--json]` | `list_handoffs(adr_id, base_path)` | read-only | table (ts/adr/obpi/path) newest-first; `--json` = HandoffInfo list |
| `gz handoff resume --adr ID [--json]` | `resume_handoff(adr_id, now, base_path)` | read-only | newest handoff + staleness level + extracted next-step; `--json` = ResumeResult |
| `gz handoff create --adr … --slug … --agent … --decisions … [flags]` | `create_handoff(...)` | **writes through the fail-closed gate** | written path on success; on `HandoffValidationError` → print violations, **exit 1, no file** |

`create` flag set is derived from what `validate_handoff_document` requires (read that
function at implementation time to enumerate exactly). At minimum: `--adr`, `--slug`,
`--agent`, `--branch` (default: current git branch), `--decisions` (the mandatory
`## Decisions Made` section); optional `--obpi`, `--continues-from`, `--summary`,
`--session-id`, `--json`. `handoff_api.py` is **read/imported, never edited.**

## Files to change

**Runtime (the adapter):**
- `src/gzkit/commands/handoff.py` — **new**: `handoff_create_cmd`, `handoff_resume_cmd`, `handoff_list_cmd`, human/JSON renderers. Follows `commands/airlock.py` shape (payload builder + `_render_human`).
- `src/gzkit/cli/parser_maintenance.py` — **new** `handoff` parser + `add_subparsers(dest="handoff_command", required=True)`; three subparsers with `add_json_flag` + `set_defaults(func=lambda a: _lazy("handoff_*_cmd")(...))`.
- `src/gzkit/cli/parser_handler_manifest.py` — map `handoff_create_cmd`/`handoff_resume_cmd`/`handoff_list_cmd` → `gzkit.commands.handoff`.

**Docs / CLI-audit parity (heavy-lane Gate 3 — all mechanically enforced by `gz cli audit`):**
- `docs/user/manpages/handoff.md` (umbrella, H1 `# gz handoff` + verb table) + `handoff-create.md` / `handoff-resume.md` / `handoff-list.md` (each: H1 `# gz handoff <sub>`, Overview/Usage/Options/Example-with-observed-output/Exit-codes).
- `docs/user/manpages/index.md` — one linked row per subcommand.
- `config/doc-coverage.json` — one `CommandEntry` per subcommand (5 surfaces + `governance_relevant: true`).
- `docs/user/runbook.md` + `docs/governance/governance_runbook.md` — reference each command name (cross-coverage surfaces).

**Skill coherence (tool-skill-runbook-alignment Invariant 1 — new verb needs a wielding skill in the same patch):**
- `.gzkit/skills/gz-session-handoff/SKILL.md` — reference `gz handoff` in body/`gz_command`; bump `skill-version` + `last_reviewed`; then `uv run gz agent sync control-surfaces`.

**Tests / BDD (Gate 2 + Gate 4):**
- `tests/test_handoff_cli.py` — **new** `unittest` classes, `@covers("REQ-…")` on each BEHAVIOR test method; assertions derive from ADR/REQ semantics (domain objects, exit codes, written-file presence), **not** rendered strings.
- `features/handoff.feature` (+ `features/steps/handoff_steps.py` for any `Given` scaffolding; global subprocess `When`/`Then` steps are reused) — one `@REQ-0.0.65-03-0N`-tagged scenario per BEHAVIOR REQ.

**Release + brief:**
- `RELEASE_NOTES` — heavy-lane subcommand entry.
- OBPI-03 brief itself (semantic authoring pass) + parent ADR checklist tick at closeout.

**Denied:** `src/gzkit/handoff_validation.py`, `lock_manager.py`, `ledger*.py` (registered security surfaces — import/read only, never edit, so no `sensitivity: security` is triggered); the `archive` subcommand and `src/gzkit/handoff_archive.py` (owned by OBPI-05).

## REQs (authored into the brief, with `[kind]` tags)

- **REQ-0.0.65-03-01 [BEHAVIOR]** — `gz handoff list` returns frontmatter-filtered handoffs newest-first; `--adr` scopes; `--json` emits the structured list.
- **REQ-0.0.65-03-02 [BEHAVIOR]** — `gz handoff resume --adr` selects the newest handoff, reports staleness classification + extracted next-step; `--json` emits `ResumeResult`.
- **REQ-0.0.65-03-03 [BEHAVIOR]** — `gz handoff create` routes authoring through the validation gate: invalid input is **refused (exit 1, no file written)**; valid input is written to `.gzkit/handoffs/` and its path reported.
- **REQ-0.0.65-03-04 [SUPPORT]** — manpages (umbrella + 3 subcommands) + index + `config/doc-coverage.json` entries exist and pass `gz cli audit` — proof: `gz validate --documents` + `artifact_edited` event.
- **REQ-0.0.65-03-05 [SUPPORT]** — the `gz-session-handoff` skill wields `gz handoff` (Invariant 1) — proof: `gz validate --cli-alignment` + `artifact_edited` event.

## Execution path (governed — operator directed "pipeline skill")

1. **Semantically author the OBPI-03 brief** (`gz-obpi-specify` authoring pass): narrow Allowed/Denied Paths to the surface above, rewrite Requirements as fail-closed rules, real Discovery Checklist, OBPI-specific Verification + Demo, the 5 REQs with `[kind]` tags. Pre-save ground-truth-check every path. Confirm no path overlaps `data/security_surfaces.json`. Run `uv run gz obpi validate --authored <brief>` until green; consult `assets/HEAVY_LANE_PLAN_TEMPLATE.md`.
2. **`/gz-plan-audit OBPI-0.0.65-03`** — writes the canonical-name plan + PASS receipt (unblocks the pipeline gate).
3. **`uv run gz obpi pipeline OBPI-0.0.65-03`** — runtime owns the stages:
   - **Stage 2 Implement** — strict RGR/TDD per behavior (verified assertion-level RED, never import-error RED).
   - **Stage 3 Verify** — `gz arb ruff` / `arb typecheck` / `arb unittest`; heavy adds `mkdocs --strict` + scoped `@REQ` behave; `gz covers` parity (BEHAVIOR REQs) + `gz arb red` RED-falsifiability witness.
   - **Stage 4 Present Evidence** + **Step 4b Codex adversary** (tier-1, required) → **HUMAN GATE** (wait for attestation).
   - **Stage 5** — `gz obpi precomplete` → `gz obpi complete` (with adversary verdict) → handoff-then-release → two git-syncs.

## Verification (end-to-end proof)

- **Behavior, driven directly:** `uv run gz handoff list --json`; `uv run gz handoff resume --adr ADR-0.0.65-handoff-system-consolidation`; a `create` happy-path (writes a file under `.gzkit/handoffs/`) and a `create` gate-rejection (missing required field → exit 1, no file).
- **Ceremony parity:** `uv run gz cli audit` (exit 0), `uv run gz validate --cli-alignment` (exit 3 if any doc references the verb before the parser registers it — register parser first), `uv run mkdocs build --strict`.
- **Tests:** `uv run -m unittest tests.test_handoff_cli -v`; `uv run -m behave --tags=@REQ-0.0.65-03-01,@REQ-0.0.65-03-02,@REQ-0.0.65-03-03 features/`; `uv run gz covers OBPI-0.0.65-03 --json` → `uncovered_reqs == 0`.
- **Full gate:** `uv run gz check` exit 0.
