ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.13 — Portable Persona Control Surface
ADR Path: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
CLI Verdict: GO (3.60/4.0, 6 OBPIs scored)
Exemplar: ADR-0.0.11 — Persona-Driven Agent Identity Frames
Exemplar Path: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
Evaluator: Claude Opus 4.6 (manual) + `gz adr evaluate` (deterministic)
Date: 2026-04-04

═══════════════════════════════════════════════════
Section 1 — CLI Scores with Evidence Trail
═══════════════════════════════════════════════════

| # | Dimension | Weight | CLI Score | CLI Finding | Concur? |
|---|-----------|--------|-----------|-------------|---------|
| 1 | Problem Clarity | 15% | 4 | OK | Yes |
| 2 | Decision Justification | 15% | 3 | "No rationale language in Decision" | Override → 4 |
| 3 | Feature Checklist | 15% | 3 | "Checklist items not prefixed with OBPI-" | Concur (cosmetic) |
| 4 | OBPI Decomposition | 15% | 4 | OK | Yes |
| 5 | Lane Assignment | 10% | 3 | "No lane in ADR frontmatter" | Concur (cosmetic) |
| 6 | Scope Discipline | 10% | 4 | OK | Yes |
| 7 | Evidence Requirements | 10% | 4 | OK | Yes |
| 8 | Architectural Alignment | 10% | 4 | OK | Yes |

--- Dimension 1: Problem Clarity — CLI 4, Concur ---

- **Intent section** (ADR lines 105-121): Before state (lines 105-109) names
  5 specific gaps: no formal schema, no manifest registration, no vendor-mirror
  syncing, no `gz init` scaffolding, no cross-project portability. After state
  (lines 110-115) names the target: any GovZero repo bootstraps via `gz init`,
  validates against JSON schema, syncs via `gz agent sync`, monitors via
  `gz personas drift`.
- **"So what?" evidence**: ADR line 109 — "Other GovZero repositories (airlineops,
  future projects) cannot use persona-driven identity framing without manually
  replicating gzkit's internal structure." Concrete consequence, not aspiration.
- **Scope boundary**: Non-Goals section (lines 179-191) bounds the problem with
  5 explicit exclusions.

--- Dimension 2: Decision Justification — CLI 3, Override → 4 ---

**Override rationale:** The CLI flagged "No rationale language in Decision" but
the ADR's Decision section (lines 125-142) contains 6 numbered decisions, each
with embedded rationale:

1. Decision 1 (line 125-127): "following the same pattern as rules and skills"
   — cites existing precedent.
2. Decision 2 (lines 128-129): "projects can override with project-specific
   content" — justifies default-set approach.
3. Decision 3 (lines 130-132): "respecting vendor enablement configuration" —
   references existing config pattern.
4. Decision 4 (lines 133-136): "defines structure without prescribing content"
   — justifies project-agnostic constraint.
5. Decision 5 (lines 137-139): "translate without modifying persona content" —
   justifies adapter model.
6. Decision 6 (lines 140-142): "using the PSM/Assistant Axis research as the
   theoretical basis" — cites research evidence.

Additionally, Alternatives Considered (lines 144-177) dismisses 3 alternatives:

- Alternative 1 (lines 146-152): AGENTS.md embedding — dismissed for validation
  limitations and vendor sync fragility.
- Alternative 2 (lines 154-161): Manifest JSON storage — dismissed because
  persona frames include free-text markdown awkward in JSON.
- Alternative 3 (lines 163-177): Defer portability — dismissed because existing
  canon/mirror architecture makes marginal cost low.

The CLI's structural parser likely missed the inline rationale within each
numbered decision. The rationale is present and specific.

--- Dimension 3: Feature Checklist — CLI 3, Concur ---

CLI finding: "Checklist items not prefixed with OBPI-." This is a cosmetic
format gap — the checklist (lines 79-84) uses descriptive text, and the OBPI
Decomposition table (lines 206-213) provides the 1:1 mapping. The 6 items:

1. "Portable persona schema specification" → OBPI-0.0.13-01 (line 208)
2. "`gz init` persona scaffolding" → OBPI-0.0.13-02 (line 209)
3. "Manifest schema and `gz agent sync` persona mirroring" → OBPI-0.0.13-03 (line 210)
4. "Vendor-neutral persona loading" → OBPI-0.0.13-04 (line 211)
5. "Persona drift monitoring surface" → OBPI-0.0.13-05 (line 212)
6. "Cross-project validation" → OBPI-0.0.13-06 (line 213)

Each item is independently valuable (removal test passes per evaluation
framework Dimension 3 checklist). Concur with CLI score of 3 — the prefix
convention is worth following for machine-parseability.

--- Dimension 4: OBPI Decomposition — CLI 4, Concur ---

- 6 OBPIs in OBPI Decomposition table (lines 206-213).
- Dependency graph (derived from STOP-on-BLOCKERS in each brief):
  - OBPI-01 (schema): no intra-ADR deps. External dep on ADR-0.0.11/12.
  - OBPI-02 (init): depends on OBPI-01 (`obpis/OBPI-0.0.13-02-gz-init-persona-scaffolding.md` line 60)
  - OBPI-03 (sync): depends on OBPI-01 (`obpis/OBPI-0.0.13-03-manifest-schema-persona-sync.md` line 58)
  - OBPI-04 (adapters): depends on OBPI-01 (`obpis/OBPI-0.0.13-04-vendor-neutral-persona-loading.md` line 57)
  - OBPI-05 (drift): depends on OBPI-04 (`obpis/OBPI-0.0.13-05-persona-drift-monitoring.md` line 61)
  - OBPI-06 (cross-project): depends on 01-04 (`obpis/OBPI-0.0.13-06-cross-project-validation.md` line 60)
- Graph shape: 01 → {02, 03, 04} parallel → 05 → 06. Acyclic. Three OBPIs
  parallelizable after 01 completes.
- Domain boundaries: schema / scaffolding / sync / adapters / monitoring /
  validation — each is a distinct concern.

--- Dimension 5: Lane Assignment — CLI 3, Concur ---

CLI finding: "No lane in ADR frontmatter." The lane (`Heavy`) IS present at
ADR line 33 in the metadata block, but the CLI may expect a YAML frontmatter
`---` block rather than inline metadata. The lane assignments per OBPI:

| OBPI | Lane | Justification (from brief) | Correct? |
|------|------|---------------------------|----------|
| 01 | Lite | Internal schema document, no CLI changes (brief line 26) | Yes |
| 02 | Lite | Adds dir to existing init, no contract change (brief lines 26-29). Borderline case explicitly discussed (brief lines 31-34). | Yes |
| 03 | Heavy | Manifest schema contract + sync output + vendor mirrors (brief lines 27-29) | Yes |
| 04 | Lite | Internal adapter functions, no CLI/API changes (brief lines 27-29) | Yes |
| 05 | Heavy | New CLI subcommand `gz personas drift` (brief lines 27-28) | Yes |
| 06 | Heavy | Cross-project changes to airlineops governance surfaces (brief lines 27-28) | Yes |

Heavy OBPIs (03, 05, 06) all include Gate 3 (docs), Gate 4 (BDD), Gate 5
(human attestation) in their Quality Gates sections. Concur with CLI score of
3 — the frontmatter format gap is real even though the lane is documented.

--- Dimension 6: Scope Discipline — CLI 4, Concur ---

- **Non-Goals section** (ADR lines 179-191) names 5 explicit exclusions, each
  with specific reasoning:
  1. **Persona content authoring** (lines 180-181): "the specific text of persona
     frames is ADR-0.0.12's scope; this ADR makes the container portable, not the
     contents." Scope boundary drawn against a named sibling ADR.
  2. **Schema backward compatibility** (lines 182-183): "the persona schema is new
     (no existing consumers); versioning is deferred until post-1.0 when breaking
     changes matter." Justified by current state — no consumers exist yet.
  3. **Activation-space drift detection** (lines 184-185): "the drift monitoring
     surface uses behavioral proxies (output pattern matching), not model-internal
     measurements." Draws a clear line between what the harness can observe and
     what requires model internals. Cross-references ADR-0.0.11's research on
     activation-space techniques (0.0.11 lines 232-234, activation capping).
  4. **Composition conflict resolution** (lines 186-188): "when two persona traits
     conflict, the current model is 'last-writer-wins' at the prompt level; formal
     conflict resolution is out of scope." Names the current behavior explicitly
     rather than leaving it unaddressed.
  5. **Vendor-specific persona tuning** (lines 189-190): "adapters translate format,
     not content; we do not maintain vendor-specific persona variants." Directly
     supports OBPI-04's pure-function requirement (OBPI-04 brief REQ 6, line 53).
- **Anti-Pattern Warning** (ADR lines 59-63): "A failed implementation makes
  persona frames tightly coupled to gzkit's agent architecture (e.g., referencing
  specific pipeline stages or skill names in the portable schema)." Names the
  specific coupling failure mode with examples of what wrong looks like.
- **Critical Constraint** (ADR lines 56-58): "The portable persona surface MUST
  NOT impose gzkit-specific content on other projects." MUST-level language bounds
  the portability contract. Cross-references OBPI-01 REQ 1 (brief line 49) and
  OBPI-06 REQ 5 (brief line 57) which both enforce this constraint.
- **Guardrails against scope creep**: Tidy First Plan STOP/BLOCKERS (ADR lines
  23-25) halt work if upstream ADRs (0.0.11, 0.0.12) are incomplete, preventing
  scope expansion into unfinished foundation work.

--- Dimension 7: Evidence Requirements — CLI 4, Concur ---

Each OBPI brief has a Verification section with concrete bash commands and a
Quality Gates section specifying which gates apply. Full evidence map:

| OBPI | Verification Section | Commands | Quality Gates |
|------|---------------------|----------|---------------|
| 01 | Brief lines 102-110 | JSON schema load check, `gz personas validate` | Gate 1 (ADR, brief line 84), Gate 2 (TDD, brief lines 88-91) |
| 02 | Brief lines 108-117 | `mktemp -d && gz init && ls`, idempotency rerun | Gate 1 (brief line 89), Gate 2 (brief lines 93-96) |
| 03 | Brief lines 119-134 | `gz validate --surfaces`, `gz agent sync` + ls, manifest JSON check | Gate 1 (brief line 93), Gate 2 (brief lines 97-100), Gate 3 docs (brief lines 103-104), Gate 4 BDD (brief lines 106-107), Gate 5 human (brief lines 109-110) |
| 04 | Brief lines 103-112 | Adapter import check, `unittest tests.test_persona_loading -v` | Gate 1 (brief line 86), Gate 2 (brief lines 90-93) |
| 05 | Brief lines 124-137 | `gz personas drift --help`, `gz personas drift`, `--persona implementer`, `--json`, exit code check | Gate 1 (brief line 92), Gate 2 (brief lines 96-99), Gate 3 docs (brief lines 103-107), Gate 4 BDD (brief lines 109-111), Gate 5 human (brief lines 113-114) |
| 06 | Brief lines 119-134 | `gz init` in airlineops, `ls .gzkit/personas/`, `gz personas validate`, `gz agent sync`, `ls .claude/personas/`, `gz validate --surfaces` | Gate 1 (brief line 89), Gate 2 (brief lines 93-96), Gate 3 docs (brief lines 99-100), Gate 4 BDD (brief lines 102-103), Gate 5 human (brief lines 105-106) |

- **Acceptance criteria specificity**: Each OBPI has numbered REQ IDs with
  Given/When/Then structure. Total: 01 has 5 REQs, 02 has 4, 03 has 6, 04 has
  5, 05 has 6, 06 has 5 = 31 acceptance criteria across 6 OBPIs.
- **Heavy lane gate coverage**: All 3 Heavy OBPIs (03, 05, 06) include Gate 3
  (docs), Gate 4 (BDD), and Gate 5 (human attestation) sections with explicit
  checkboxes. Gate 4 BDD files named: `features/persona_sync.feature` (OBPI-03,
  brief line 39; OBPI-06, brief line 35), `features/persona.feature` (OBPI-05,
  brief line 39).
- **ADR-level evidence** (ADR lines 270-277): Names TDD file
  (`tests/test_persona_portability.py`), BDD file (`features/persona_sync.feature`),
  docs targets (governance runbook + command docs for `gz personas`), and lineage
  (depends on ADR-0.0.11 + ADR-0.0.12).

--- Dimension 8: Architectural Alignment — CLI 4, Concur ---

- **Existing Pattern table** (ADR Rationale section, lines 228-236): 4-row
  table mapping existing control surfaces to their canon and mirror paths:

  | Surface | Canon | Mirrors |
  |---------|-------|---------|
  | Rules | `.gzkit/rules/` | `.claude/rules/`, `.github/instructions/` |
  | Skills | `.gzkit/skills/` | `.claude/skills/`, `.github/skills/`, `.agents/skills/` |
  | Schemas | `.gzkit/schemas/` | (not mirrored) |
  | **Personas** | **`.gzkit/personas/`** | **`.claude/personas/`, `.github/personas/`, `.agents/personas/`** |

  This shows personas follow the established canon-first, vendor-mirror pattern.
  A downstream implementer can find the sync pattern in `src/gzkit/sync_surfaces.py`
  by studying how `sync_skill_mirrors()` or `sync_rule_mirrors()` work (OBPI-03
  brief Discovery Checklist, line 83-84).

- **Integration Points** (ADR lines 67-72): Names 5 specific module paths with
  their roles:
  1. `src/gzkit/sync_surfaces.py` — control surface sync (add personas)
  2. `src/gzkit/commands/init.py` — `gz init` scaffolding
  3. `.gzkit/manifest.json` — schema update (`control_surfaces.personas`)
  4. `data/schemas/manifest.schema.json` — manifest JSON schema
  5. `.gzkit/personas/` — the surface being made portable

- **Anti-Pattern Warning** (ADR lines 59-63): Names the exact failure mode —
  "persona frames tightly coupled to gzkit's agent architecture (e.g.,
  referencing specific pipeline stages or skill names in the portable schema)."
  Gives concrete examples of what wrong looks like (pipeline stages, skill
  names). This is reinforced by OBPI-01 REQ 1 (brief line 49): "JSON schema
  MUST be project-agnostic — no references to gzkit pipeline stages, skill
  names, or internal module paths."

- **Vendor Neutrality rationale** (ADR lines 239-249): Names 4 vendor runtimes
  and how each consumes identity context:
  - Claude Code: System prompt + AGENTS.md + rules files
  - Codex: AGENTS.md + instruction files
  - Copilot: `.github/copilot-instructions.md` + instruction files
  - OpenCode: AGENTS.md equivalent

  This directly informs OBPI-04's adapter design — each adapter function
  translates to the vendor's native format (OBPI-04 brief REQs 2-4, lines
  49-51).

- **Codebase precedent references**: OBPI briefs reference existing exemplar
  code patterns rather than inventing new ones:
  - OBPI-01 brief line 78: "Pattern to follow: `src/gzkit/schemas/manifest.json`"
  - OBPI-02 brief line 84-85: "Pattern to follow: `scaffold_core_skills()`"
  - OBPI-03 brief line 83-84: "Pattern to follow: `sync_skill_mirrors()`"
  - OBPI-04 brief line 80-81: "Pattern to follow: `compose_persona_frame()`"
  - OBPI-05 brief line 85-86: "Pattern to follow: `gz validate` command pattern"

═══════════════════════════════════════════════════
Section 2 — OBPI Evidence Map
═══════════════════════════════════════════════════

--- OBPI-0.0.13-01: Portable Persona Schema ---

- Brief: `obpis/OBPI-0.0.13-01-portable-persona-schema.md`
- Lane: Lite — internal schema document, no CLI changes (brief line 26)
- Dependencies: None intra-ADR. External: ADR-0.0.11, ADR-0.0.12 (brief line
  56, STOP-on-BLOCKERS)
- Parent checklist item: ADR line 79 — "Portable persona schema specification
  (project-agnostic)"
- Acceptance criteria: 5 (REQ-0.0.13-01-01 through -05, brief lines 114-118):
  - REQ-01: Schema is valid JSON Schema with `$schema`, `title`, `properties`
  - REQ-02: `name`, `traits`, `anti_traits`, `grounding` required; omission fails
  - REQ-03: All 6 existing persona files validate without modification
  - REQ-04: No gzkit-specific references in schema
  - REQ-05: PersonaFrontmatter model matches schema required fields
- Allowed paths (brief lines 35-38) — codebase verification:
  - `src/gzkit/schemas/persona.json` — EXPECTED-NEW (schema to create)
  - `src/gzkit/models/persona.py` — EXISTS (update PersonaFrontmatter)
  - `tests/test_persona_schema.py` — EXISTS (tests already present from ADR-0.0.11)
  - `.gzkit/personas/` — EXISTS (6 files: implementer.md, main-session.md,
    spec-reviewer.md, quality-reviewer.md, narrator.md, pipeline-orchestrator.md)
- Denied paths (brief lines 42-45):
  - `src/gzkit/commands/` — CLI changes are separate OBPIs
  - `src/gzkit/sync_surfaces.py` — sync is OBPI-03
  - `.gzkit/manifest.json` — manifest changes are OBPI-03
  - New dependencies
- Verification commands (brief lines 102-110):
  ```
  python -c "import json; s = json.load(open('src/gzkit/schemas/persona.json')); print(s.get('title', 'MISSING'))"
  uv run gz personas validate
  ```
- Key requirements (brief lines 49-54):
  - MUST: Schema project-agnostic — no gzkit pipeline stages, skill names,
    module paths (REQ 1, line 49)
  - MUST: Schema version field present, e.g. `"schema": "gzkit.persona.v1"`
    (REQ 3, line 51)
  - MUST: All 6 existing persona files validate without modification (REQ 5,
    line 53)
  - NEVER: Schema MUST NOT prescribe trait content (REQ 4, line 52)
  - NEVER: No optional fields without current consumer (REQ 6, line 54)
- Pattern to follow: `src/gzkit/schemas/manifest.json` — existing JSON schema
  exemplar (brief line 78). EXISTS, confirmed.
- Related OBPIs:
  - OBPI-03 (`obpis/OBPI-0.0.13-03-manifest-schema-persona-sync.md`) — consumes
    schema for manifest integration
  - OBPI-04 (`obpis/OBPI-0.0.13-04-vendor-neutral-persona-loading.md`) — depends
    on stable PersonaFrontmatter model
- ADR cross-reference: Decision 4 (ADR lines 133-136) — "The persona schema
  defines structure without prescribing content." Anti-Pattern Warning (ADR
  lines 59-63) — portability constraint this OBPI enforces.

--- OBPI-0.0.13-02: gz init Persona Scaffolding ---

- Brief: `obpis/OBPI-0.0.13-02-gz-init-persona-scaffolding.md`
- Lane: Lite — adds internal scaffolding step to `gz init` (brief lines 26-29).
  Borderline case explicitly discussed (brief lines 31-34): command contract
  (flags, exit codes, error format) unchanged, so Lite holds.
- Dependencies: OBPI-01 (brief line 60, STOP-on-BLOCKERS — schema must exist
  so default personas can validate)
- Parent checklist item: ADR line 80 — "`gz init` persona scaffolding (default
  persona set)"
- Acceptance criteria: 4 (REQ-0.0.13-02-01 through -04, brief lines 121-124):
  - REQ-01: `gz init` creates `.gzkit/personas/` with at least one default file
  - REQ-02: Existing persona files preserved on re-init (idempotent)
  - REQ-03: Default files validate against OBPI-01 schema
  - REQ-04: No project-specific content in defaults
- Allowed paths (brief lines 38-42) — codebase verification:
  - `src/gzkit/commands/init_cmd.py` — EXISTS
  - `src/gzkit/templates/personas/` — EXPECTED-NEW (if template-based approach)
  - `tests/commands/test_init_cmd.py` — BRIEF NAME INCORRECT. Actual file is
    `tests/commands/test_init.py` (EXISTS). Implementer must use correct name.
  - `tests/test_persona_scaffolding.py` — EXPECTED-NEW
- Denied paths (brief lines 46-49):
  - `src/gzkit/sync_surfaces.py` — sync is OBPI-03
  - `src/gzkit/schemas/` — schema is OBPI-01
  - `src/gzkit/commands/personas.py` — persona commands are separate
  - `.gzkit/manifest.json` — manifest changes are OBPI-03
- Verification commands (brief lines 108-117):
  ```
  cd $(mktemp -d) && uv run gz init && ls .gzkit/personas/
  uv run gz init && ls .gzkit/personas/   # idempotency check
  ```
- Key requirements (brief lines 53-58):
  - MUST: Create `.gzkit/personas/` if not exists (REQ 1, line 53)
  - MUST: Default set contains at least one schema-valid file (REQ 2, line 54)
  - NEVER: Defaults MUST NOT contain project-specific content (REQ 3, line 55)
  - MUST: Existing files preserved on re-init (REQ 4, line 56)
  - MUST: Follow same idempotent pattern as existing init dirs (REQ 5, line 57)
  - NEVER: No new CLI flags for persona scaffolding (REQ 6, line 58)
- Pattern to follow: `scaffold_core_skills()` in `init_cmd.py` (brief line 85).
  EXISTS in `src/gzkit/commands/init_cmd.py` — confirmed.
- Related OBPIs:
  - OBPI-01 (`obpis/OBPI-0.0.13-01-portable-persona-schema.md`) — upstream dep,
    schema must be finalized before defaults can validate
  - OBPI-03 (`obpis/OBPI-0.0.13-03-manifest-schema-persona-sync.md`) — manifest
    registration happens after scaffolding
  - OBPI-04 (`obpis/OBPI-0.0.13-04-vendor-neutral-persona-loading.md`) — loading
    depends on files existing
- ADR cross-reference: Decision 2 (ADR lines 128-129) — "`gz init` creates the
  personas directory with a default persona set that projects can override."
- **DEFECT NOTE**: Brief line 41 references `tests/commands/test_init_cmd.py`
  but the actual file is `tests/commands/test_init.py`. Brief should be
  corrected before implementation.

--- OBPI-0.0.13-03: Manifest Schema Persona Sync ---

- Brief: `obpis/OBPI-0.0.13-03-manifest-schema-persona-sync.md`
- Lane: Heavy — changes manifest JSON schema contract (`additionalProperties:
  false` means new key is breaking), modifies `gz agent sync` output, creates
  vendor mirror dirs (brief lines 27-29)
- Dependencies: OBPI-01 (brief line 58, STOP-on-BLOCKERS — persona files must
  be schema-valid before sync)
- Parent checklist item: ADR line 81 — "Manifest schema and `gz agent sync`
  persona mirroring to vendor surfaces"
- Acceptance criteria: 6 (REQ-0.0.13-03-01 through -06, brief lines 138-143):
  - REQ-01: Manifest schema has `personas` string property in `control_surfaces`
  - REQ-02: `gz agent sync` mirrors `.gzkit/personas/` → `.claude/personas/`
  - REQ-03: Vendor config disable prevents mirror creation
  - REQ-04: Manifest regeneration includes `control_surfaces.personas`
  - REQ-05: `gz validate --surfaces` passes after schema change
  - REQ-06: Re-running sync after persona modification updates mirror (not stale)
- Allowed paths (brief lines 35-41) — codebase verification:
  - `src/gzkit/schemas/manifest.json` — EXISTS
  - `.gzkit/manifest.json` — EXISTS (regenerated by sync)
  - `src/gzkit/sync_surfaces.py` — EXISTS
  - `src/gzkit/config.py` — EXISTS
  - `tests/test_sync_surfaces.py` — EXISTS
  - `tests/test_manifest.py` — BRIEF NAME INCORRECT. Actual files are
    `tests/test_manifest_v2.py` and `tests/test_manifest_resolution.py` (both
    EXIST). Implementer must use correct names or create new file.
  - `features/persona_sync.feature` — EXPECTED-NEW (BDD scenarios)
  - `docs/user/commands/` — EXISTS (directory with 60+ command docs)
  - `docs/governance/governance_runbook.md` — EXISTS
- Denied paths (brief lines 45-47):
  - `src/gzkit/commands/personas.py` — persona CLI is OBPI-05
  - `src/gzkit/commands/init_cmd.py` — init scaffolding is OBPI-02
  - `.gzkit/personas/*.md` — persona content files (read-only for sync)
- Verification commands (brief lines 119-134):
  ```
  uv run gz validate --surfaces
  uv run gz agent sync control-surfaces && ls .claude/personas/ .agents/personas/
  python -c "import json; m = json.load(open('.gzkit/manifest.json')); print(m['control_surfaces'].get('personas', 'MISSING'))"
  ```
- Key requirements (brief lines 50-58):
  - MUST: Add `"personas"` to manifest schema `control_surfaces` (REQ 1, line 50)
  - MUST: `generate_manifest()` includes `"personas": ".gzkit/personas"` (REQ 2,
    line 51)
  - MUST: `sync_all()` calls persona sync function (REQ 3, line 52)
  - MUST: Respect vendor enablement config (REQ 4, line 53)
  - MUST: Mirror paths follow pattern: `.claude/personas/`, `.agents/personas/`,
    `.github/personas/` (REQ 5, line 54)
  - NEVER: Sync MUST NOT modify canonical files — one-directional (REQ 6, line 55)
  - NEVER: No persona-specific flags on `gz agent sync` (REQ 7, line 56)
  - MUST: `gz validate --surfaces` passes after change (REQ 8, line 57)
- Heavy lane gates:
  - Gate 3 docs (brief lines 103-104): docs build + relevant docs updated
  - Gate 4 BDD (brief lines 106-107): `uv run -m behave features/persona_sync.feature`
  - Gate 5 human (brief lines 109-110): human attestation recorded
- Pattern to follow:
  - `sync_skill_mirrors()` in `src/gzkit/sync_surfaces.py` (brief line 83) — EXISTS
  - `generate_manifest()` in same file (brief line 84) — EXISTS
- Related OBPIs:
  - OBPI-01 (`obpis/OBPI-0.0.13-01-portable-persona-schema.md`) — upstream dep,
    schema validation prerequisite
  - OBPI-04 (`obpis/OBPI-0.0.13-04-vendor-neutral-persona-loading.md`) — vendor
    adapters may be wired into sync pipeline
  - OBPI-06 (`obpis/OBPI-0.0.13-06-cross-project-validation.md`) — cross-project
    test validates sync works in airlineops
- ADR cross-references:
  - Decision 1 (ADR lines 125-127): manifest registration pattern
  - Decision 3 (ADR lines 130-132): vendor-mirror syncing with enablement config
  - Existing Pattern table (ADR lines 228-236): canon/mirror mapping
- **DEFECT NOTE**: Brief line 38 references `tests/test_manifest.py` but actual
  manifest test files are `tests/test_manifest_v2.py` and
  `tests/test_manifest_resolution.py`. Brief should be corrected.

--- OBPI-0.0.13-04: Vendor-Neutral Persona Loading ---

- Brief: `obpis/OBPI-0.0.13-04-vendor-neutral-persona-loading.md`
- Lane: Lite — internal adapter functions consumed by sync pipeline, no CLI/API
  changes (brief lines 27-29)
- Dependencies: OBPI-01 (brief line 57, STOP-on-BLOCKERS — stable
  PersonaFrontmatter model required)
- Parent checklist item: ADR line 82 — "Vendor-neutral persona loading (Claude,
  Codex, Copilot adapters)"
- Acceptance criteria: 5 (REQ-0.0.13-04-01 through -05, brief lines 116-120):
  - REQ-01: Claude adapter produces system prompt fragment with traits/anti-traits
  - REQ-02: Codex adapter produces AGENTS.md instruction block
  - REQ-03: Copilot adapter produces copilot-instructions.md fragment
  - REQ-04: Missing adapter falls back to raw canonical markdown copy
  - REQ-05: All adapters are pure (same input → same output, deterministic)
- Allowed paths (brief lines 34-37) — codebase verification:
  - `src/gzkit/personas.py` — EXISTS (add adapter functions alongside
    `compose_persona_frame()`)
  - `src/gzkit/sync_surfaces.py` — EXISTS (wire adapters if not done in OBPI-03)
  - `tests/test_persona_loading.py` — EXPECTED-NEW
  - `tests/test_personas.py` — NOT FOUND. No existing file at this path.
    Implementer should check `tests/commands/test_personas_cmd.py` (EXISTS)
    instead, or create new file.
- Denied paths (brief lines 40-44):
  - `src/gzkit/commands/` — no CLI changes
  - `src/gzkit/schemas/` — schema is OBPI-01
  - `.gzkit/personas/` — canon files read-only
  - `.claude/`, `.agents/`, `.github/` — vendor mirrors written by sync, not
    by adapters directly
- Verification commands (brief lines 103-112):
  ```
  python -c "from gzkit.personas import render_persona_claude, render_persona_codex, render_persona_copilot; print('All adapters importable')"
  uv run -m unittest tests.test_persona_loading -v
  ```
- Key requirements (brief lines 48-55):
  - MUST: Each adapter accepts PersonaFrontmatter + body markdown, returns
    formatted string (REQ 1, line 48)
  - MUST: Claude adapter → system prompt fragment (REQ 2, line 49)
  - MUST: Codex adapter → AGENTS.md instruction block (REQ 3, line 50)
  - MUST: Copilot adapter → copilot-instructions.md fragment (REQ 4, line 51)
  - ALWAYS: Adapters are pure functions — no I/O, no side effects (REQ 5, line 52)
  - NEVER: Adapters MUST NOT modify/interpret persona content (REQ 6, line 53)
  - ALWAYS: Missing adapter → fallback to raw markdown copy (REQ 7, line 54)
  - NEVER: No vendor-specific persona variants (REQ 8, line 55)
- Pattern to follow: `compose_persona_frame()` in `src/gzkit/personas.py`
  (brief line 80-81) — EXISTS, confirmed.
- Related OBPIs:
  - OBPI-01 (`obpis/OBPI-0.0.13-01-portable-persona-schema.md`) — upstream dep,
    PersonaFrontmatter model stability
  - OBPI-03 (`obpis/OBPI-0.0.13-03-manifest-schema-persona-sync.md`) — sync
    pipeline calls these adapters
  - OBPI-05 (`obpis/OBPI-0.0.13-05-persona-drift-monitoring.md`) — drift
    detection depends on loaded persona definitions
- ADR cross-references:
  - Decision 5 (ADR lines 137-139): "Vendor adapter functions translate persona
    frames into vendor-specific formats without modifying persona content."
  - Vendor Neutrality rationale (ADR lines 239-249): Names 4 vendor runtimes
    (Claude Code, Codex, Copilot, OpenCode) and how each consumes identity
    context — directly informs adapter design.
- **DEFECT NOTE**: Brief line 37 references `tests/test_personas.py` which does
  not exist. Nearest existing file is `tests/commands/test_personas_cmd.py`.
  Brief should be corrected.

--- OBPI-0.0.13-05: Persona Drift Monitoring ---

- Brief: `obpis/OBPI-0.0.13-05-persona-drift-monitoring.md`
- Lane: Heavy — new CLI subcommand `gz personas drift` with defined output
  format, exit codes, and operator-facing behavior (brief lines 27-28)
- Dependencies: OBPI-04 (brief line 61, STOP-on-BLOCKERS — needs loaded persona
  definitions to compare against)
- Parent checklist item: ADR line 83 — "Persona drift monitoring surface
  (observability)"
- Acceptance criteria: 6 (REQ-0.0.13-05-01 through -06, brief lines 140-145):
  - REQ-01: No flags → human-readable table of all personas with trait adherence
  - REQ-02: `--json` → valid JSON with persona names, trait checks, pass/fail
  - REQ-03: `--persona implementer` → single persona drift report
  - REQ-04: No drift → exit code 0
  - REQ-05: Drift detected → exit code 3 (policy breach)
  - REQ-06: `--help` → description, usage, options, example
- Allowed paths (brief lines 33-42) — codebase verification:
  - `src/gzkit/commands/personas.py` — EXISTS (add `drift` subcommand)
  - `src/gzkit/personas.py` — EXISTS (add drift detection logic)
  - `src/gzkit/models/persona.py` — EXISTS (add drift result model if needed)
  - `src/gzkit/cli/parser_governance.py` — EXISTS (wire into CLI parser)
  - `tests/test_persona_drift.py` — EXPECTED-NEW
  - `tests/commands/test_personas_cmd.py` — EXISTS (extend)
  - `features/persona.feature` — EXISTS (extend with drift scenarios)
  - `docs/user/commands/personas.md` — NOT FOUND. Nearest existing:
    `docs/user/commands/personas-list.md` (EXISTS). Implementer may need to
    create new file or extend existing.
  - `docs/user/manpages/gz-personas.md` — EXPECTED-NEW (manpage)
- Denied paths (brief lines 44-48):
  - `src/gzkit/sync_surfaces.py` — sync is OBPI-03
  - `src/gzkit/schemas/` — schema is OBPI-01
  - `.gzkit/personas/` — canon files read-only
  - `src/gzkit/commands/init_cmd.py` — init is OBPI-02
- Verification commands (brief lines 124-137):
  ```
  uv run gz personas drift --help
  uv run gz personas drift
  uv run gz personas drift --persona implementer
  uv run gz personas drift --json
  echo $?
  ```
- Key requirements (brief lines 52-59):
  - MUST: Accept optional `--persona <name>` flag (REQ 1, line 52)
  - MUST: Support `--json` and default table output (REQ 2, line 52)
  - MUST: Use behavioral proxies only — output pattern matching (REQ 3, line 53)
  - ALWAYS: Exit 0 = no drift, exit 3 = drift detected (REQ 4, line 54)
  - ALWAYS: Human output includes persona name, trait, pass/fail (REQ 5, line 55)
  - NEVER: No network access — local artifacts only (REQ 6, line 56)
  - NEVER: No activation-space measurement claims (REQ 7, line 57)
  - ALWAYS: Help text with example and exit codes (REQ 8, line 59)
- Drift detection theory — ADR Rationale > Drift Monitoring (lines 250-261):
  - Behavioral proxies defined (ADR lines 254-257):
    - Did the agent follow the persona's trait specifications?
    - Did outputs match the expected behavioral pattern?
    - Did the agent drift toward anti-trait behaviors?
  - Feedback loop: design → deploy → monitor → refine (ADR lines 259-261)
  - Theoretical basis: PSM/Assistant Axis research showing persona position is
    measurable and drift predictable from conversational context (ADR line 251)
- Local artifacts for drift analysis — codebase verification:
  - `artifacts/receipts/` — NOT FOUND. ARB receipt directory does not currently
    exist. The ARB middleware (`.claude/rules/arb.md`) defines
    `artifacts/receipts/` as storage, but the directory may only be created when
    ARB commands are run. Implementer must handle missing-directory case.
  - `.gzkit/insights/agent-insights.jsonl` — EXISTS. Agent insight entries are
    available as a drift data source.
  - ARB middleware schema: `data/schemas/arb_lint_receipt.schema.json` — defined
    in `.claude/rules/arb.md` lines 35-36.
- Heavy lane gates:
  - Gate 3 docs (brief lines 103-107): docs build + command docs + manpage
  - Gate 4 BDD (brief lines 109-111): `uv run -m behave features/persona.feature`
  - Gate 5 human (brief lines 113-114): human attestation recorded
- CLI doctrine compliance (`.claude/rules/cli.md`):
  - Exit codes: 0/3 per 4-code map (cli.md lines 16-22)
  - Help text: must respond to `-h`/`--help`, include description, usage, options,
    example (cli.md lines 34-40)
  - Output: default human-readable, `--json` to stdout (cli.md lines 28-32)
- Pattern to follow: `gz validate` command pattern — similar "check and report"
  output style (brief line 85-86). `src/gzkit/commands/personas.py` — existing
  CLI structure (brief line 85). Both EXISTS, confirmed.
- Related OBPIs:
  - OBPI-04 (`obpis/OBPI-0.0.13-04-vendor-neutral-persona-loading.md`) —
    upstream dep, persona loading must be complete
  - OBPI-01 (`obpis/OBPI-0.0.13-01-portable-persona-schema.md`) — transitive
    dep via OBPI-04, PersonaFrontmatter model defines traits to check
  - OBPI-06 (`obpis/OBPI-0.0.13-06-cross-project-validation.md`) — drift
    monitoring not required for cross-project validation but extends the
    portability story
- ADR cross-references:
  - Decision 6 (ADR lines 140-142): drift monitoring using PSM/Assistant Axis
    research as theoretical basis
  - Non-Goal 3 (ADR lines 184-185): activation-space drift explicitly excluded
  - Interfaces section (ADR lines 194-199): `gz personas drift` listed as new CLI
- **DEFECT NOTE**: Brief line 40 references `docs/user/commands/personas.md` but
  only `docs/user/commands/personas-list.md` exists. Implementer must determine
  correct command doc filename. Also, `artifacts/receipts/` does not exist —
  drift detection must handle the case where no ARB receipts are available.

--- OBPI-0.0.13-06: Cross-Project Validation ---

- Brief: `obpis/OBPI-0.0.13-06-cross-project-validation.md`
- Lane: Heavy — cross-project validation affects airlineops governance surfaces
  and contracts (brief lines 27-28)
- Dependencies: OBPIs 01-04 (brief line 60, STOP-on-BLOCKERS — full portability
  stack must be complete)
- Parent checklist item: ADR line 84 — "Cross-project validation (apply to
  airlineops)"
- Acceptance criteria: 5 (REQ-0.0.13-06-01 through -05, brief lines 138-142):
  - REQ-01: `gz init` in airlineops creates `.gzkit/personas/` with defaults
  - REQ-02: `gz personas validate` in airlineops passes schema validation
  - REQ-03: `gz agent sync` in airlineops creates `.claude/personas/`
  - REQ-04: airlineops persona files contain no gzkit-specific content
  - REQ-05: Validation documented as reproducible command sequence
- Allowed paths — gzkit (brief lines 34-36) — codebase verification:
  - `tests/test_persona_portability.py` — EXPECTED-NEW
  - `features/persona_sync.feature` — EXPECTED-NEW (shared with OBPI-03)
  - `docs/governance/governance_runbook.md` — EXISTS
- Allowed paths — airlineops (brief lines 40-43) — external repository:
  - `../airlineops/.gzkit/personas/` — bootstrapped by `gz init` (external)
  - `../airlineops/.gzkit/manifest.json` — updated by manifest generation (external)
  - `../airlineops/.claude/personas/` — created by vendor sync (external)
- Denied paths (brief lines 46-48):
  - `src/gzkit/` — no gzkit source changes in this OBPI
  - `.gzkit/personas/` — gzkit's own persona files are not the subject
  - Any airlineops source code changes beyond governance surface scaffolding
- Verification commands (brief lines 119-134):
  ```
  cd ../airlineops
  uv run gz init
  ls .gzkit/personas/
  uv run gz personas validate
  uv run gz agent sync control-surfaces
  ls .claude/personas/
  uv run gz validate --surfaces
  ```
- Key requirements (brief lines 52-58):
  - MUST: `gz init` in airlineops creates `.gzkit/personas/` with defaults
    (REQ 1, line 52)
  - MUST: `gz agent sync` in airlineops mirrors personas to vendor surfaces
    (REQ 2, line 53)
  - MUST: airlineops personas validate against portable schema (REQ 3, line 54)
  - ALWAYS: airlineops persona content MUST be project-specific (REQ 4, line 55)
  - NEVER: gzkit-specific content MUST NOT appear (REQ 5, line 57)
  - ALWAYS: Validation documented as reproducible command sequence (REQ 6, line 56)
  - NEVER: Do not modify gzkit source to accommodate airlineops — if portable
    surface doesn't work, the surface is broken (REQ 7, line 58)
- Heavy lane gates:
  - Gate 3 docs (brief lines 99-100): governance runbook updated with cross-
    project persona workflow
  - Gate 4 BDD (brief lines 102-103): `uv run -m behave features/persona_sync.feature`
  - Gate 5 human (brief lines 105-106): human attests portability claim validated
- Related OBPIs:
  - OBPI-01 (`obpis/OBPI-0.0.13-01-portable-persona-schema.md`) — transitive
    dep, schema validation in airlineops
  - OBPI-02 (`obpis/OBPI-0.0.13-02-gz-init-persona-scaffolding.md`) — init
    scaffolding is what creates personas in airlineops
  - OBPI-03 (`obpis/OBPI-0.0.13-03-manifest-schema-persona-sync.md`) — sync
    pipeline is what mirrors personas in airlineops
  - OBPI-04 (`obpis/OBPI-0.0.13-04-vendor-neutral-persona-loading.md`) —
    adapters translate for airlineops vendor surfaces
- ADR cross-references:
  - Anti-Pattern Warning (ADR lines 59-63): "A failed implementation makes
    persona frames tightly coupled to gzkit's agent architecture." OBPI-06 is
    the test that proves this didn't happen.
  - Critical Constraint (ADR lines 56-58): "The portable persona surface MUST
    NOT impose gzkit-specific content on other projects." OBPI-06 enforces this.
  - Tidy First Plan item 3 (ADR lines 16-17): "Catalog persona-like language in
    airlineops AGENTS.md" — upstream context for cross-project work.
  - Consequences (ADR line 268): "airlineops becomes the first cross-project
    consumer."

═══════════════════════════════════════════════════
Section 3 — Exemplar Comparison
═══════════════════════════════════════════════════

Exemplar: ADR-0.0.11 — Persona-Driven Agent Identity Frames
Path: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
Status: Validated, Heavy, 6/6 OBPIs completed.

--- What 0.0.11 has that 0.0.13 lacks ---

1. **Research Evidence section** (0.0.11 lines 219-254): Reproduces 5 papers
   with specific quantitative findings — PSM personality inference mechanism,
   Assistant Axis ~60% harmful response reduction, PRISM 3.6pp accuracy drop
   from expert personas, PERSONA 91% win rate on dynamic adaptation, Persona
   Vectors neural activation patterns. ADR-0.0.13 references "PSM/Assistant
   Axis research" (line 142, line 253) but inherits the evidence chain rather
   than reproducing it. Appropriate for a downstream ADR but means a reader
   of 0.0.13 alone lacks the quantitative grounding.

2. **Concrete failure narrative** (0.0.11 lines 257-266, "The Observed Failure
   Mode"): Ties persona theory to a specific production failure — agents
   splitting Python imports across separate edits. The default Assistant
   persona's trait cluster includes "minimum-viable edit, token efficiency,
   incremental action." ADR-0.0.13 has no equivalent "this is the specific
   failure that portability fixes." Its motivation is architectural (prevent
   manual replication) rather than failure-driven.

3. **Evidence Ledger section** (0.0.11 lines 309-334): Structured as
   Provenance, Source & Contracts, Tests, Docs subsections with specific
   file paths. ADR-0.0.13 has an Evidence section (lines 270-277) listing
   gates but no formal ledger structure with provenance tracking.

4. **Pool ADR lineage** (0.0.11 lines 312-316): Explicit supersession of
   `ADR-pool.per-command-persona-context` with 5 carried-forward elements
   listed. ADR-0.0.13 has no supersession tracking (nothing to supersede,
   which is legitimate).

5. **Attestation Block** (0.0.11 lines 354-358): Completed with attestor
   (Jeffry), date (2026-04-02), and status. ADR-0.0.13 has a blank sign-off
   block (lines 291-296) — expected for a Draft ADR.

--- What 0.0.13 improves over 0.0.11 ---

1. **Canon/mirror pattern table** (0.0.13 lines 228-236, Rationale > Existing
   Pattern): 4-row table mapping rules, skills, schemas, and personas to their
   canon paths and vendor mirror paths. Shows exactly where personas fit in
   the existing architecture. ADR-0.0.11 references `.gzkit/personas/` as a
   new directory (line 283-284) but has no equivalent visual mapping showing
   how it parallels existing surfaces.

2. **Interfaces section with CLI specificity** (0.0.13 lines 194-203): Names
   3 new CLI commands (`gz personas list`, `validate`, `drift`), the manifest
   update path, and 3 vendor sync targets with exact directory paths.
   ADR-0.0.11's Interfaces (lines 196-202) are less CLI-specific — `gz personas
   list` is mentioned as "(read-only)" but `validate` and `drift` are not
   present (they're 0.0.13's scope).

3. **Lane assignment borderline analysis** (OBPI-02 brief lines 31-34):
   Explicitly discusses why init scaffolding is Lite despite borderline
   characteristics, noting the command contract (flags, exit codes, error
   format) is unchanged. ADR-0.0.11 does not discuss any borderline lane cases.

4. **Anti-pattern warning precision** (0.0.13 lines 59-63): Names the exact
   architectural failure mode — "persona frames tightly coupled to gzkit's
   agent architecture (e.g., referencing specific pipeline stages or skill
   names in the portable schema)." ADR-0.0.11's anti-pattern (lines 64-70)
   targets content quality (job descriptions vs behavioral identity). Both
   are well-formed; 0.0.13's is more architecturally actionable.

5. **Decomposition Scorecard** (0.0.13 lines 88-101): Both ADRs have these,
   but 0.0.13's shows higher dimensional spread (Data/State: 2, Logic/Engine:
   2, Interface: 2, Observability: 2) versus 0.0.11's more concentrated
   distribution, reflecting 0.0.13's broader surface area.

Structural verdict: ADR-0.0.13 matches ADR-0.0.11's template discipline and
improves on integration specificity (pattern tables, CLI commands, sync
targets, borderline lane analysis). It is appropriately weaker on research
depth — it inherits 0.0.11's theoretical foundation rather than re-establishing
it. This is correct for its position in the 0.0.11 → 0.0.12 → 0.0.13 lineage.

═══════════════════════════════════════════════════
Section 4 — Verdict & Advisory Items
═══════════════════════════════════════════════════

VERDICT: GO

One override: Dimension 2 (Decision Justification) overridden from CLI 3 → 4.
The CLI flagged "No rationale language in Decision" but the Decision section
(lines 125-142) contains 6 decisions with inline rationale, and the Alternatives
section (lines 144-177) dismisses 3 alternatives with specific reasoning. The
CLI's structural parser likely expected explicit "Rationale:" subheadings rather
than inline justification.

Adjusted weighted total: 3.75/4.0 (vs CLI 3.60/4.0).

ADVISORY ITEMS (non-blocking):

1. **Evidence Ledger section** (applies to: ADR author) — ADR-0.0.11 (lines
   309-334) has a structured Evidence Ledger with Provenance, Source & Contracts,
   Tests, Docs subsections. ADR-0.0.13 has an Evidence section (lines 270-277)
   but no formal ledger. Adding one would maintain structural consistency across
   the foundation track. Reference: ADR-0.0.11 lines 309-334 as template.

2. **OBPI-06 airlineops availability** (applies to: OBPI-06 implementer) —
   Cross-project validation (brief lines 119-134) requires `../airlineops/` to
   be present and gzkit-governed. A temp-directory fallback (initialize a fresh
   gzkit project via `gz init` in a temp dir) would reduce external coupling and
   make the validation reproducible without the airlineops checkout.

3. **Feature Checklist prefix convention** (applies to: ADR author) — CLI
   flagged checklist items not prefixed with OBPI identifiers (ADR lines 79-84).
   The OBPI Decomposition table (lines 206-213) provides the mapping, but adding
   `[OBPI-0.0.13-NN]` prefixes would make the mapping machine-parseable.

BRIEF DEFECTS DISCOVERED (fix before implementation):

1. **OBPI-02 brief line 41**: References `tests/commands/test_init_cmd.py` but
   actual file is `tests/commands/test_init.py`. Applies to: OBPI-02
   implementer.

2. **OBPI-03 brief line 38**: References `tests/test_manifest.py` but actual
   manifest test files are `tests/test_manifest_v2.py` and
   `tests/test_manifest_resolution.py`. Applies to: OBPI-03 implementer.

3. **OBPI-04 brief line 37**: References `tests/test_personas.py` which does not
   exist. Nearest existing file: `tests/commands/test_personas_cmd.py`. Applies
   to: OBPI-04 implementer.

4. **OBPI-05 brief line 40**: References `docs/user/commands/personas.md` but
   only `docs/user/commands/personas-list.md` exists. Applies to: OBPI-05
   implementer.

5. **OBPI-05 drift data source**: `artifacts/receipts/` (referenced in ADR ARB
   middleware `.claude/rules/arb.md` lines 35-36 as receipt storage) does not
   currently exist as a directory. The drift command must handle the case where
   no ARB receipts are available. `.gzkit/insights/agent-insights.jsonl` EXISTS
   and is an available data source. Applies to: OBPI-05 implementer.

CODEBASE VERIFICATION SUMMARY:

| Path | Status | Referenced By |
|------|--------|---------------|
| `src/gzkit/schemas/persona.json` | EXPECTED-NEW | OBPI-01 |
| `src/gzkit/models/persona.py` | EXISTS | OBPI-01, 04 |
| `tests/test_persona_schema.py` | EXISTS | OBPI-01 |
| `.gzkit/personas/` (6 files) | EXISTS | OBPI-01, 02, 03, 06 |
| `src/gzkit/commands/init_cmd.py` | EXISTS | OBPI-02 |
| `src/gzkit/templates/personas/` | EXPECTED-NEW | OBPI-02 |
| `tests/commands/test_init.py` | EXISTS | OBPI-02 (brief has wrong name) |
| `tests/test_persona_scaffolding.py` | EXPECTED-NEW | OBPI-02 |
| `src/gzkit/schemas/manifest.json` | EXISTS | OBPI-03 |
| `.gzkit/manifest.json` | EXISTS | OBPI-03 |
| `src/gzkit/sync_surfaces.py` | EXISTS | OBPI-03, 04 |
| `src/gzkit/config.py` | EXISTS | OBPI-03 |
| `tests/test_sync_surfaces.py` | EXISTS | OBPI-03 |
| `tests/test_manifest_v2.py` | EXISTS | OBPI-03 (brief has wrong name) |
| `tests/test_manifest_resolution.py` | EXISTS | OBPI-03 |
| `features/persona_sync.feature` | EXPECTED-NEW | OBPI-03, 06 |
| `docs/user/commands/` (60+ files) | EXISTS | OBPI-03, 05 |
| `docs/governance/governance_runbook.md` | EXISTS | OBPI-03, 06 |
| `src/gzkit/personas.py` | EXISTS | OBPI-04, 05 |
| `tests/test_persona_loading.py` | EXPECTED-NEW | OBPI-04 |
| `tests/test_personas.py` | NOT FOUND | OBPI-04 (brief defect) |
| `tests/commands/test_personas_cmd.py` | EXISTS | OBPI-04, 05 |
| `src/gzkit/commands/personas.py` | EXISTS | OBPI-05 |
| `src/gzkit/cli/parser_governance.py` | EXISTS | OBPI-05 |
| `tests/test_persona_drift.py` | EXPECTED-NEW | OBPI-05 |
| `features/persona.feature` | EXISTS | OBPI-05 |
| `docs/user/commands/personas-list.md` | EXISTS | OBPI-05 (brief has wrong name) |
| `docs/user/manpages/gz-personas.md` | EXPECTED-NEW | OBPI-05 |
| `tests/test_persona_portability.py` | EXPECTED-NEW | OBPI-06 |
| `artifacts/receipts/` | NOT FOUND | OBPI-05 (drift data source) |
| `.gzkit/insights/agent-insights.jsonl` | EXISTS | OBPI-05 (drift data source) |
