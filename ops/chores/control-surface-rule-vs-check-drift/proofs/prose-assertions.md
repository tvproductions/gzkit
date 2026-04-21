# Prose Assertions — control-surface-rule-vs-check-drift (Pass C)

Normalized prose assertions for each promoted rule. Extracted close to
verbatim from the rule file's binding sections; numbered so `parity-diff.md`
can cite specific assertion numbers.

Scope: rule assertions, not prefatory rationale or anti-pattern narrative
(anti-patterns are captured only when they *assert* a specific forbidden form
beyond the main binding table).

---

## `CLAUDE.md` § Architectural Boundaries, rules 1–2 (pool ADR runtime isolation)

Source: `CLAUDE.md` § Architectural Boundaries (binding memo, Section 12).
Promoted as `--pool-adr-isolation`.

Assertions:

1. Do not promote post-1.0 pool ADRs into active work.
2. Do not add more pool ADRs to the runtime track.
3. Scorecard elaboration: "a pool ADR receiving `gate_checked` /
   `lifecycle_transition` / `attestation` / `obpi_completed` / `adr_audit` /
   `adr_closeout` is a violation" (scorecard row #2 Notes).
4. A pool ADR is either id-prefixed `ADR-pool.` or lives under `docs/design/adr/pool/` (scorecard Notes).

---

## `CLAUDE.md` § Architectural Boundaries, rule 4 (reconciliation freshness)

Source: `CLAUDE.md` § Architectural Boundaries (rule 4). Promoted as
`--reconcile-freshness`.

Assertions:

1. Do not let reconciliation remain a maintenance chore.
2. If the state doctrine says "derived state is rebuildable," then
   reconciliation is a core architectural operation — tested, gated, and part
   of the pipeline.
3. Scorecard elaboration: "flags when the latest reconcile ledger event is
   older than HEAD by more than 24h" (scorecard row #4 Notes).

---

## `CLAUDE.md` § Architectural Boundaries, rule 6 (derived views never source-of-truth) — `--frontmatter`

Source: `CLAUDE.md` § Architectural Boundaries (rule 6); state-doctrine.md
and trust-doctrine.md carry the operational spec. Promoted as `--frontmatter`
(plus `--event-handlers` and `--validator-fields`, separately below).

Assertions (frontmatter-coherence specific):

1. Frontmatter `id`, `parent`, `lane`, `status` fields must match the
   ledger's artifact graph values (source: `validate_frontmatter.py:1-9`
   module docstring is the canonical statement).
2. Lookup is keyed on filesystem path only, never on frontmatter `id:`
   (reproducing GHI #166).
3. A frontmatter `status` of "Completed" is acceptable when the ledger has
   `attested_completed` (status supersetting, `validate_frontmatter.py:26-29`).

---

## `CLAUDE.md` § Architectural Boundaries, rule 6 (derived views never source-of-truth) — `--event-handlers`

Source: `CLAUDE.md` § Architectural Boundaries (rule 6); trust-doctrine T2.
Promoted as `--event-handlers`.

Assertions:

1. Every ledger event type emitted by `ledger_events.py` must be claimed by a
   graph handler in `ledger.py`, OR appear in `_NO_GRAPH_IMPACT` with a
   rationale.
2. Stale waivers (entries in `_NO_GRAPH_IMPACT` for events no longer emitted)
   must be removed.

---

## `CLAUDE.md` § Architectural Boundaries, rule 6 (derived views never source-of-truth) — `--validator-fields`

Source: `CLAUDE.md` § Architectural Boundaries (rule 6); trust-doctrine T2.
Promoted as `--validator-fields`.

Assertions:

1. Every `info.get('<field>')` read in `validate_frontmatter.py` must have a
   corresponding graph-write or creation-entry-initializer in `ledger.py`, OR
   appear in `_VALIDATOR_FIELD_WAIVERS` with a rationale.

---

## `CLAUDE.md` § Architectural Boundaries, rule 6a (ADR taxonomy)

Source: `CLAUDE.md` § Kinds table + § ADR-0.0.17 bullet; operator guidance in
ADR-0.0.18. Promoted as `--taxonomy`.

Assertions:

1. Pool ADRs (id prefix `ADR-pool.`) derive kind from the id; they carry no
   `kind:` frontmatter and no `semver:` frontmatter.
2. Non-pool ADRs MUST carry `kind:` frontmatter.
3. `kind:` is one of `foundation` or `feature` (enum).
4. `kind: foundation` requires `semver:` matching `0.0.x`.
5. `kind: feature` forbids `semver:` matching `0.0.x` (must be `0.y.z` or
   later, non-`0.0.x`).
6. Nested obpi/brief/audit artifacts under the ADR tree are exempt from
   taxonomy checking (convention shared with `_validate_decomposition`).

---

## `CLAUDE.md` § Local Agent Rules (rule 9) + `.gzkit/rules/cross-platform.md` § Console Output — no `PYTHONUTF8=1` prefix

Source: `CLAUDE.md` § Local Agent Rules (rule 9) and
`.gzkit/rules/cross-platform.md` § "Console Output". Promoted as
`--utf8-prefix`.

Assertions:

1. Never prefix `uv run gz` or `uv run -m gzkit` commands with `PYTHONUTF8=1`
   — the CLI entrypoint handles UTF-8 encoding at runtime.
2. The scope of the runtime guard is **only** `uv run gz ...` and
   `uv run -m gzkit ...` — fresh Python interpreters (`python -c`,
   `python tools/<helper>.py`, `uv run python <script>`) are **not** covered
   by the guard and must configure UTF-8 stdin/stdout explicitly
   (`cross-platform.md:79-101`).
3. Ad-hoc `python -c` / helper scripts that process gz output MUST configure
   UTF-8 stdin/stdout (`cross-platform.md:113`).
4. "Prefer gz-native extraction > reconfigured `uv run python` > raw
   `python -c`" (preference order, `cross-platform.md:101`).

---

## `CLAUDE.md` § Local Agent Rules (rule 11) — every version bump is a release

Source: `CLAUDE.md` § Local Agent Rules (rule 11). Promoted as
`--version-release`.

Assertions:

1. Every version bump is a release.
2. After bumping `pyproject.toml`, `__init__.py`, and the README badge,
   always create a GitHub release with `gh release create vX.Y.Z
   --target main --title "vX.Y.Z" --latest --notes "..."`.
3. The release workflow triggers PyPI publish and binary builds from the
   tag.
4. Never leave a version bump uncommitted without a corresponding release.
5. GHI #217 elaboration (from validator docstring): an in-flight release
   manifest at `docs/releases/PATCH-v{version}.md` is equivalent evidence
   during the window between bump commit and `gh release create`.

---

## `.gzkit/rules/governance-core.md` § Proof commands — `--cli-alignment`

Source: `.gzkit/rules/governance-core.md` § Proof commands (implicit;
explicit rule text lives in `.gzkit/rules/tool-skill-runbook-alignment.md` §
Invariant 2). Promoted as `--cli-alignment`.

Assertions (from validator docstring, since governance-core.md does not state
the rule directly — this is a cross-file prose-binding):

1. Every `gz <verb>` string appearing in `features/**/*.feature`,
   `docs/user/runbook.md`, `docs/user/commands/**`, and
   `docs/user/manpages/**` must resolve to a registered top-level CLI verb.
2. The verb is recognized when it appears in backtick, double-quote, or
   `the gz command "X"` step-definition form.
3. `_DOC_PROSE_VERBS` waivers are allowed for verbs that appear only as
   documentation prose.

---

## `.gzkit/rules/pythonic.md` § "Size Limits & Refactoring" — classes ≤300 lines

Source: `.gzkit/rules/pythonic.md` § Size Limits, core principle 9, plus
scorecard row #21. Promoted as `--class-size`.

Assertions:

1. Classes under `src/gzkit/**` ≤300 lines (body span, first decorator to
   last line).
2. Over-limit classes must appear in `_CLASS_SIZE_WAIVERS` with rationale.
3. Stale waivers (for classes no longer present) must be removed.
4. Sister limits (functions ≤50 lines, modules ≤600 lines) exist but are
   stated as mechanically enforced via xenon/ruff/pre-commit hooks — the
   validator scope covers **only** the class limit.

---

## `.gzkit/rules/pythonic.md` § "Type-check suppression syntax (ty — binding)"

Source: `.gzkit/rules/pythonic.md:46-62`. Promoted as `--type-ignores`.

Assertions:

1. `ty` does not honor mypy-style bracketed codes — `# type: ignore[<code>]`
   looks valid but suppresses nothing (the diagnostic still fires).
2. Use exactly one of: bare `# type: ignore` OR `# ty: ignore[<ty-code>]`.
3. Bare `# type: ignore` is for unconditional, imprecise suppression.
4. `# ty: ignore[<ty-code>]` is for specificity — citing ty's own error code
   (examples: `invalid-method-override`, `no-matching-overload`,
   `invalid-assignment`, `unresolved-attribute`, `call-non-callable`,
   `invalid-argument-type`).
5. Scope: `src/**` (from rule text: "under `src/**`").
6. `tests/governance/test_type_ignore_syntax.py` fail-closes on violations.

---

## `.gzkit/rules/models.md` (rules 25 + 26) — Pydantic discipline

Source: `.gzkit/rules/models.md:10-13`. Promoted as `--pydantic-models`.

Assertions (rule 25):

1. Use **Pydantic `BaseModel`** for all data models; no stdlib `dataclasses`.

Assertions (rule 26):

2. Immutable models use `ConfigDict(frozen=True, extra="forbid")`.
3. Every BaseModel subclass declares `model_config = ConfigDict(...)`
   (minimally `extra="forbid"`).

Additional assertions (listed as "Anti-Patterns DO NOT USE"):

4. No stdlib `dataclass` for governance data.
5. No Pydantic without `ConfigDict`.
6. No `Optional`/`List` instead of `| None` and `list[]`.

(Assertions 4/5 restate 1–3; #6 is assigned to ruff UP006/UP007 per
scorecard row #27, not `--pydantic-models`.)

Additional assertion (from "Verify" section):

7. Immutable snapshots use `frozen=True`.

---

## `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 1 — wielding-skill coverage

Source: `.gzkit/rules/tool-skill-runbook-alignment.md:18-22` (Invariant 1
only; Invariants 2 and 3 remain Promotable). Promoted as
`--skill-alignment`.

Assertions (Invariant 1 only):

1. Every CLI verb registered in `src/gzkit/cli/` must be invoked by at least
   one skill under `.gzkit/skills/` — either via frontmatter `gz_command:`
   field OR in the skill body instructions.
2. Orphaned tools (live CLI verb with no skill pointer) are a defect signal.
3. Scorecard elaboration: `_NO_SKILL_VERBS` provides explicit-waiver
   discipline for bootstrap/internal/subcommand verbs with rationale.

Not in scope of `--skill-alignment` (still advisory per scorecard rows 29
and 30):

- Invariant 2 (skill → runbook operator-moment match)
- Invariant 3 (destination verb's default output honors skill's Output
  Contract)

---

## `.gzkit/rules/tests.md` § TASK-Driven Workflow — governance-intent trailers

Source: `.gzkit/rules/tests.md:63-86`. Promoted as `--commit-trailers`.

Assertions:

1. Every commit touching `src/**` or `tests/**` MUST carry one governance-
   intent trailer.
2. Acceptable trailer forms: `Task: TASK-X.Y.Z-NN-MM-PP` for task-scoped
   work, OR `Ceremony: <name>` for chore/sync commits bundling multiple
   governance anchors.
3. `Task:` trailer must be the final line of the commit body.
4. `gz git-sync` emits `Ceremony:` trailers automatically.
5. Check scope is HEAD only (validator docstring:
   `validate_cmd.py:122-129` "Scans HEAD only — the check is advisory and
   focused on preventing *new* trailer omissions rather than retroactively
   flagging historical commits").

---

## `.gzkit/rules/tests.md` § Runner anti-patterns — no third test tier

Source: `.gzkit/rules/tests.md:138-143` and `.gzkit/rules/tests.md:95-101`.
Promoted as `--test-tiers`.

Assertions:

1. The two test runners are `unittest` (over `tests/`) and `behave` (over
   `features/`). No third tier.
2. No directory `tests/integration/`, `tests/e2e/`, `tests/slow/`, or
   `tests/bdd/` may exist.
3. No CLI flag `--integration`, `--e2e`, `--slow`, or `--bdd-only` may
   reappear in CLI `parser*.py` files.
4. Scorecard row #37 Notes names the same prohibition: "fails on
   `tests/{integration,e2e,slow,bdd}/` or forbidden `--integration` /
   `--e2e` / `--slow` / `--bdd-only` flags re-appearing in `parser_*.py`".

---

## `.gzkit/rules/tests.md` § Behave scenario tagging — `@REQ-X.Y.Z-NN-MM`

Source: `.gzkit/rules/tests.md:122-135`. Promoted as `--behave-req-tags`.

Assertions:

1. Behave scenarios covering a REQ carry `@REQ-X.Y.Z-NN-MM` as a
   scenario-level tag (one per REQ, with leading `@`).
2. Feature-level `# @covers REQ-...` comments remain supported for narrative
   authorship but are too coarse for OBPI-scoped filtering.
3. Scorecard row #39 elaboration: scans "heavy-lane and foundation-kind
   OBPIs for REQ-IDs without matching scenario-level `@REQ-*` tags."
4. Every REQ cited in a feature-level `# @covers` comment must have a
   corresponding scenario-level tag somewhere in the same file (validator
   docstring).

---

## Scorecard meta-rule — `--advisory-scorecard`

Source: `docs/governance/advisory-rules-audit.md` § Promotion discipline
("This audit is itself a candidate for promotion: the catalog above could be
a test that fails when a new rule is added without a score."). Promoted as
`--advisory-scorecard`.

Assertions:

1. Every rule file under `.gzkit/rules/*.md` must appear in the scorecard
   (referenced by stem — case-insensitive match against scorecard text).
2. A missing scorecard row for a new rule file is a defect.

---

## `.gzkit/rules/brief-heading-conventions.md` — H3 evidence sections

Source: `.gzkit/rules/brief-heading-conventions.md:10-33`. Promoted as
`--brief-headings`.

Assertions:

1. OBPI brief evidence sections MUST use H3 (`###`), not H2 (`##`).
2. Canonical H3-only evidence headings: `Implementation Summary`,
   `Key Proof`, `Closing Argument`.
3. `## Acceptance Criteria` (H2) is the canonical top-level brief section
   and is deliberately NOT in the H3-only list.
4. Gate 2 headings (`## Objective`, `## Acceptance Criteria`,
   `## ALLOWED PATHS`, etc.) remain H2.
5. Scope: all `OBPI-*.md` briefs under `docs/design/adr/**`.
6. Mechanical check: `uv run gz validate --brief-headings`; exits 3 on
   drift.
