# OBPI-0.0.19-04: Skill authoring + upstream integrations — Plan

## Context

OBPI-0.0.19-02/03 already shipped the `gz justify` CLI verb (positional `<anchor>`, subverb `validate <file>`, flags `--save`/`--output`/`--related`/`--draft`/`--draft-slug`/`--json`; rendered scaffold starts with a `---` YAML frontmatter delimiter per `src/gzkit/justify/templates/walkthrough.md.j2:1`). Agents have no way to discover or be prompted to use this verb — `.gzkit/skills/gz-justify/` does not exist, and the two upstream skills that should suggest it (`gz-adr-evaluate` after low scores; `gz-obpi-pipeline` at the Stage 1→2 confidence boundary) don't mention it.

This OBPI fixes that. It lands the new `gz-justify` canonical skill, edits two neighbors to surface `justify` at the right moments, and regenerates the `.claude/` and `.github/` mirrors via `gz agent sync control-surfaces`. The Prime Directive invariant 11 ("<90% confidence → ask/justify") becomes mechanically surfaced in the OBPI pipeline for the first time.

Lane is **Heavy** — touches governance-canon skills; requires version bumps and surface sync. Tests pin every REQ via `@covers`.

## Implementation plan (TDD per-increment)

### Task 1 — Author skill-shape tests (RED)

File: `tests/skills/__init__.py` (new, empty) and `tests/skills/test_gz_justify_skill.py` (new).

Tests (each with `@covers(REQ-0.0.19-04-NN)`):

- `test_frontmatter_required_keys_present` (REQ-01): parse YAML frontmatter of `.gzkit/skills/gz-justify/SKILL.md`; assert keys `name == "gz-justify"`, `persona == "main-session"`, `len(description) >= 40`, `category` present, `metadata.skill-version` matches `^6\.`, `metadata.govzero-framework-version == "v6"`, top-level `gz_command == "justify"`, `lifecycle_state == "active"`, `owner == "gzkit-governance"`, ISO-date `last_reviewed`.
- `test_body_sections_appear_in_order` (REQ-02): scan H2 headings; assert exact sequence `Purpose → Common Rationalizations → Red Flags → Persona → Trust Model → Invocation → When to Use → Procedure → Acceptance Criteria → Related Skills`.
- `test_red_flags_table_names_fabrication` (REQ-03): scan Red Flags section; assert a row containing case-insensitive token `fabricat` exists.
- `test_gz_command_resolves_via_verify_chain` (REQ-04): import `verify_gz_chain` from `gzkit.hooks.obpi`; assert `verify_gz_chain(["justify"]) == (True, ...)`.
- `test_justify_first_line_is_frontmatter_or_h1` (REQ-09): import rendering entrypoint from `gzkit.justify` (or subprocess `uv run -m gzkit justify` against a mocked/draft anchor using `--draft "x"` + `--draft-slug "t"`); assert first non-empty line is `---` or starts with `# `. Prefer in-process render to keep <200ms — use `tempfile` for any `--save` artifacts.

Use `tempfile.TemporaryDirectory()` for all fixture work. Read canonical skill paths read-only. **Never write under `.gzkit/skills/` or `.claude/skills/`.** Run tests — watch them fail for the right reason (skill file missing).

### Task 2 — Author surface-sync tests (RED)

File: `tests/skills/test_skill_surface_sync_justify.py` (new).

Tests:

- `test_adr_evaluate_has_low_score_footer_block` (REQ-05): grep canon for a block that (a) names `<3.0` threshold, (b) mentions tracking GHI or OBPI, (c) contains literal `uv run -m gzkit justify`. Assert skill-version bumped to `6.3.0` (from `6.2.0`).
- `test_obpi_pipeline_has_low_confidence_block` (REQ-06): grep canon for a Stage 1→2 block that cites Prime Directive invariant 11, fires at <90% confidence, contains `uv run -m gzkit justify` and `--save`. Assert skill-version bumped to `6.9.0` (from `6.8.0`).
- `test_sync_produces_equivalent_mirrors` (REQ-07): copy `.gzkit/skills/{gz-justify,gz-adr-evaluate,gz-obpi-pipeline}/`, `.gzkit/manifest.json`, and required control-surface inputs into a tempfile project root; invoke the programmatic sync entrypoint (`gzkit.sync.sync_all` or `gzkit.sync_skills`) against that root; assert `.claude/skills/gz-justify/SKILL.md` and the two neighbor mirrors exist and body content matches canon modulo deterministic vendor rendering.
- `test_validate_surfaces_passes_after_sync` (REQ-08): in the same tempfile root, call `gzkit.validate_pkg.surface.validate_surfaces(root, check_sync_parity=True)`; assert returned errors list is empty.
- `test_tests_do_not_mutate_live_repo_paths` (REQ-10): walk this test module's AST; assert no literal string `str(Path(".gzkit/skills"))` or `.claude/skills` appears with a write-mode open/unlink — static self-check that tests don't target live paths.

Confirm all five fail before moving on.

### Task 3 — Author `.gzkit/skills/gz-justify/SKILL.md` (GREEN for Task 1)

File: `.gzkit/skills/gz-justify/SKILL.md` (new).

Frontmatter (nested `metadata` matches gz-plan-audit/gz-adr-evaluate pattern; `gz_command` top-level matches every other skill):

```yaml
---
name: gz-justify
persona: main-session
description: <=50+ chars describing investigatory pre-execution walkthrough — invoke before implementation when confidence is <90% or scope is unclear; produces grounded reasoning against anchor evidence.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-22
gz_command: justify
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
---
```

Body (H2 in the order REQ-02 demands; content grounded in CLI reality from OBPI-02/03):

- **Purpose** — what the skill does, problem it solves.
- **Common Rationalizations** — table ("I already understand the brief"; "The anchor is obvious"; "I'll justify later"). Each row paired with counter.
- **Red Flags** — table; one row MUST name **fabrication** of filled reasoning as a red flag (REQ-03).
- **Persona** — main-session persona reference.
- **Trust Model** — Layer-1 evidence gathering; scaffold is authored by CLI + agent together; agent grounds filled blocks in anchor evidence only.
- **Invocation** — `uv run -m gzkit justify <anchor>` default; `--save` for persisted artifact; `validate` subverb for round-trip check.
- **When to Use** — low-confidence moments; <90% per invariant 11; low gz-adr-evaluate score; scope ambiguity.
- **Procedure** — numbered steps: (1) invoke CLI with anchor, (2) read rendered scaffold, (3) for each `_[To be filled]_` block use Edit tool to replace with grounded reasoning citing the evidence the CLI gathered, (4) save artifact via `--output` or `--save`, (5) run `gz justify validate <file>` to confirm round-trip, (6) cite artifact in subsequent plan/brief.
- **Acceptance Criteria** — scaffold filled, no fabricated claims, round-trip validates, artifact cited in downstream governance surface.
- **Related Skills** — gz-adr-evaluate (low-score suggestion source), gz-obpi-pipeline (Stage 1→2 prompt), gz-plan-audit (downstream consumer of filled walkthrough).

Include `## Related ADRs` sub-paragraph citing ADR-0.0.19 (REQ-08).

Run Task 1 tests → GREEN.

### Task 4 — Edit `.gzkit/skills/gz-adr-evaluate/SKILL.md` (GREEN for REQ-05)

File: `.gzkit/skills/gz-adr-evaluate/SKILL.md`.

Edits:

- Bump `metadata.skill-version: "6.2.0"` → `"6.3.0"` and `last_reviewed` to today.
- After Step 6 (scorecard verdict, around line 197) and before Step 7, insert a new subsection (H3 or labeled paragraph) titled **Low-Score Footer Guidance**: when the weighted total is `<3.0` AND the ADR has a tracking GHI-N parent or at least one OBPI brief, append to the emitted scorecard a line `> Consider: uv run -m gzkit justify <parent-GHI-or-first-OBPI>` (with the concrete identifier substituted). Include a one-sentence rationale: "Low confidence in ADR structure is an invariant-11 trigger — run the pre-execution walkthrough before promotion."
- Append a `## Related ADRs` line at end of file: cites ADR-0.0.19 and summarizes coupling.

Re-run Task 2 test `test_adr_evaluate_has_low_score_footer_block` → GREEN.

### Task 5 — Edit `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (GREEN for REQ-06)

File: `.gzkit/skills/gz-obpi-pipeline/SKILL.md`.

Edits:

- Bump top-level `skill-version: "6.8.0"` → `"6.9.0"` and `last_reviewed` to today.
- Insert a new subsection between the "Abort if" block at ~line 150 and the `### Stage 2: Implement` heading. Name it **Stage 1→2 Confidence Gate**. Content: when the agent's self-reported confidence in the planned implementation is <90% (per `.gzkit/rules/agent-contract.md` Invariant 11), pause before Stage 2 and run `uv run -m gzkit justify <current-OBPI-id> --save`. The rendered + filled artifact is grounded evidence for the Stage 2 implementation pass and Stage 4 ceremony. This mechanizes what was previously a subjective judgment.
- Append `## Related ADRs` citing ADR-0.0.19.

Re-run Task 2 test `test_obpi_pipeline_has_low_confidence_block` → GREEN.

### Task 6 — Run `uv run gz agent sync control-surfaces` (GREEN for REQ-07)

Regenerates `.claude/skills/gz-justify/SKILL.md`, `.claude/skills/gz-adr-evaluate/SKILL.md`, `.claude/skills/gz-obpi-pipeline/SKILL.md`, plus `.github/skills/` equivalents. Expect exit 0. Re-run `test_sync_produces_equivalent_mirrors` → GREEN.

### Task 7 — Run `uv run gz validate --surfaces` (GREEN for REQ-08)

Expect exit 0. Re-run `test_validate_surfaces_passes_after_sync` → GREEN.

### Task 8 — Quality + coverage sweep

- `uv run gz lint`
- `uv run gz typecheck`
- `uv run -m pymarkdown scan .gzkit/skills/gz-justify/SKILL.md .gzkit/skills/gz-adr-evaluate/SKILL.md .gzkit/skills/gz-obpi-pipeline/SKILL.md` — clean.
- `uv run -m unittest tests.skills.test_gz_justify_skill tests.skills.test_skill_surface_sync_justify -v` — all green.
- `uv run gz covers OBPI-0.0.19-04-skill-and-upstream-integrations --json` — confirm `uncovered_reqs == 0`.
- `uv run gz arb step --name unittest-justify-04 -- uv run -m unittest tests.skills.test_gz_justify_skill tests.skills.test_skill_surface_sync_justify` — GREEN receipt.

## Critical files

- `.gzkit/skills/gz-justify/SKILL.md` — NEW
- `.gzkit/skills/gz-adr-evaluate/SKILL.md` — edit Step 6/7 + version bump 6.2.0→6.3.0
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — edit Stage 1→2 boundary (~line 150) + version bump 6.8.0→6.9.0
- `tests/skills/__init__.py` — NEW (empty)
- `tests/skills/test_gz_justify_skill.py` — NEW (pins REQ-01/02/03/04/09)
- `tests/skills/test_skill_surface_sync_justify.py` — NEW (pins REQ-05/06/07/08/10)

## Existing utilities reused

- `verify_gz_chain` from `src/gzkit/hooks/obpi.py:80-121` — REQ-04 verification.
- `gzkit.justify` rendering entrypoint — REQ-09 first-line check (in-process preferred over subprocess).
- `gzkit.sync.sync_all` / `gzkit.sync_skills` — REQ-07 tempfile-based sync invocation.
- `gzkit.validate_pkg.surface.validate_surfaces(root, check_sync_parity=True)` at `src/gzkit/validate_pkg/surface.py:16-34` — REQ-08.
- `@covers` decorator from `gzkit.testing.coverage` (existing pattern under `tests/` — match `tests/test_agent_sync.py` decorator style).
- PyMarkdown via `uv run -m pymarkdown scan` — markdown-lint per Gate 3.

## Verification (end-to-end)

```bash
uv run gz lint
uv run gz typecheck
uv run gz covers OBPI-0.0.19-04-skill-and-upstream-integrations --json
uv run -m pymarkdown scan .gzkit/skills/gz-justify/SKILL.md .gzkit/skills/gz-adr-evaluate/SKILL.md .gzkit/skills/gz-obpi-pipeline/SKILL.md
uv run gz arb step --name unittest-justify-04 -- uv run -m unittest tests.skills.test_gz_justify_skill tests.skills.test_skill_surface_sync_justify
uv run gz agent sync control-surfaces
uv run gz validate --surfaces
test -f .gzkit/skills/gz-justify/SKILL.md && test -f .claude/skills/gz-justify/SKILL.md
grep -q "^gz_command: justify$" .gzkit/skills/gz-justify/SKILL.md
grep -E 'skill-version.*6\.3\.0' .gzkit/skills/gz-adr-evaluate/SKILL.md
grep -E 'skill-version.*"6\.9\.0"' .gzkit/skills/gz-obpi-pipeline/SKILL.md
```

All green → Stage 2 complete; proceed through Stage 3 verification dispatch, Stage 4 evidence presentation (lane Heavy → human attestation deferred to ADR closeout per lane inheritance), Stage 5 sync/reconcile/complete.

## Notes

- `gz_command: justify` is bare-verb style, matching every other skill (`gz_command: audit`, `gz_command: state`, etc. observed at `.gzkit/skills/gz-adr-audit/SKILL.md:14`, `.gzkit/skills/gz-adr-map/SKILL.md:10`).
- `metadata.skill-version` nesting matches gz-plan-audit/gz-adr-evaluate convention; gz-obpi-pipeline uses top-level but its version bump keeps the existing shape.
- H2 section ordering for gz-justify follows the brief literally ("Purpose, Common Rationalizations, Red Flags, Persona, Trust Model, Invocation, When to Use, Procedure, Acceptance Criteria, Related Skills") — this is flatter than gz-plan-audit (which nests Common Rationalizations/Red Flags under Persona), but the brief is explicit so we follow it.
- No BDD scenarios (Gate 4 N/A; deferred to OBPI-05 per brief).
- Gate 5 human attestation deferred to ADR-0.0.19 closeout per lane inheritance (`AGENTS.md` § OBPI Acceptance Protocol).
