# Check Behaviors (Audit Function Mechanics)

**Generated:** 2026-05-10
**Source:** `src/gzkit/governance/trust_audits/*.py` — read-only inspection.

One paragraph per promoted scope, describing what the audit function
literally does (file enumeration, regex match, AST walk, frontmatter
read, etc.). Behavior described, not asserted intent.

## `--advisory-scorecard` — `audit_advisory_scorecard` (`release.py:83`)

Reads `docs/governance/advisory-rules-audit.md`, case-folds the contents,
walks `.gzkit/rules/*.md`, and emits a `ValidationError` if any rule's
file stem (case-folded substring) is not present in the scorecard text.
Treats the scorecard as a flat lookup; does NOT validate that the rule
has been *scored* (Mechanical / Promotable / Judgment / Ambiguous),
only that the file stem is mentioned anywhere.

## `--utf8-prefix` — `audit_utf8_prefix` (`cross_platform.py:80`)

Regex-walks documentation and feature/skill surfaces searching for
(a) `PYTHONUTF8=1 uv run (gz|-m gzkit)` literal prefix patterns,
(b) `gz ... | python` fresh-interpreter pipes lacking
`sys.stdout.reconfigure(encoding="utf-8")` in the pipeline,
(c) `gz ... | {jq|awk|sed}` non-Python pipes (file-handoff anti-pattern),
and (d) AST-walks `tools/**/*.py` entry points to confirm they call
`sys.stdout.reconfigure`. Each match emits a `ValidationError` keyed to
`<file>:<lineno>` unless the entry is in `_UTF8_PIPE_WAIVERS`.

## `--version-release` — `audit_version_release` (`release.py:19`)

Reads the `version = "X.Y.Z"` line from `pyproject.toml`, shells out to
`git tag --list v*`, and emits a `ValidationError` if `vX.Y.Z` is not in
the tag set. Accepts an in-flight `docs/releases/PATCH-vX.Y.Z.md`
manifest as equivalent evidence (covers the window between commit and
`gh release create`).

## `--pool-adr-isolation` — `audit_pool_adr_isolation` (`taxonomy.py:50`)

Streams `.gzkit/ledger.jsonl` line by line, parses each event as JSON,
and emits a `ValidationError` for the (artifact_id, event_type) pair
when artifact_id starts with `ADR-pool.` AND event_type is in
`{gate_checked, attestation, obpi_completed, adr_attested, adr_audit,
adr_closeout, lifecycle_transition}`. Each unique pair is flagged once.

## `--taxonomy` — `audit_adr_taxonomy` (`taxonomy.py:175`)

Walks `docs/design/adr/{foundation,pre-release}/**/ADR-*.md` (skipping
nested `obpis/`, `briefs/`, `audit/` artefacts), parses YAML
frontmatter, and asserts:
foundation kind → semver matches `^0\.0\.\d+$`;
feature kind → semver is non-`0.0.x`;
pool ADRs (id-prefix `ADR-pool.`) carry neither `kind:` nor `semver:`.

## `--adr-status-fresh` — `audit_adr_status_fresh` (`taxonomy.py:232`)

Regenerates the `docs/governance/GovZero/adr-status.md` table from
on-disk ADR canon (frontmatter + H1 truth under
`docs/design/adr/{foundation,pre-release}/`) and diffs the result
against the committed file. Drift emits a `ValidationError`. Operator
recovery is `uv run gz register-adrs`.

## `--test-tiers` — `audit_test_tiers` (`code_quality.py:126`)

Walks `tests/` for subdirectories named `integration`, `e2e`, `slow`,
or `bdd`, and scans `src/gzkit/commands/parser_*.py` for forbidden CLI
flags `--integration`, `--e2e`, `--slow`, `--bdd-only`. Any hit emits a
`ValidationError`; the gzkit project commits to exactly two test tiers
(unit via unittest, BDD via behave).

## `--type-ignores` — `audit_type_ignores` (`code_quality.py:37`)

Tokenizes every `.py` file under `src/` with the stdlib `tokenize`
module and matches the regex `#\s*type:\s*ignore\[` against COMMENT
tokens only (skipping string literals). Any match emits a
`ValidationError` because ty does not honor bracketed mypy-style codes.
Bare `# type: ignore` and `# ty: ignore[<ty-code>]` pass through.

## `--class-size` — `audit_class_size` (`code_quality.py:73`)

AST-parses every `.py` file under `src/gzkit/`, walks all `ClassDef`
nodes, and computes `end_lineno - lineno + 1` for each. Classes over
300 lines emit a `ValidationError` unless the qualified key
`<rel-path>::<ClassName>` is in `_CLASS_SIZE_WAIVERS`. Stale waivers
(class no longer present) are also flagged. Functions and modules are
not measured by this audit (ruff / pre-commit covers them).

## `--pydantic-models` — `audit_pydantic_models` (`models.py:69`)

AST-walks every `.py` under `src/gzkit/`. Flags `@dataclass`-decorated
classes (`models.py:97`) unless waived in `_DATACLASS_WAIVERS`. Flags
classes extending `BaseModel` (by name or attribute) that do not assign
`model_config = ...` in the class body. Does NOT inspect the contents
of `ConfigDict(...)` — a class with `model_config = SomeOtherThing()`
passes the audit.

## `--cli-alignment` — `audit_cli_alignment` (`cli.py:87`)

Enumerates `features/**/*.feature`, `docs/user/runbook.md`, and
`docs/user/{commands,manpages}/**/*.md`. For each line, applies three
regexes: backticked `` `gz <verb>` ``, quoted `"gz <verb>"`, and
behave-step `the gz command "<verb>"`. Each captured verb is compared
against the set returned by `_build_parser()` subparser choices. Unknown
verbs emit a `ValidationError`. Multi-word subcommands are matched on
the first token only.

## `--skill-alignment` — `audit_skill_alignment` (`cli.py:149`)

Enumerates registered top-level CLI verbs from `_build_parser()` and
scans `.gzkit/skills/**/SKILL.md` for `gz_command:` frontmatter values
and body invocations. Verbs with no wielding skill emit a
`ValidationError` unless waived in `_NO_SKILL_VERBS` (currently 21
entries — `init`, `register-adrs`, `task`, `interview`, etc.).

## `--event-handlers` — `audit_event_handlers` (`events.py:88`)

AST-parses `src/gzkit/ledger_events.py` collecting every `event="<name>"`
keyword in factory calls. AST-parses `src/gzkit/ledger.py` collecting
event-name string literals appearing in `event.event == "<literal>"`
comparisons and in inline sets/lists/tuples. Emits a `ValidationError`
for every emitted event not claimed by a handler and not waived in
`_NO_GRAPH_IMPACT` (currently 14 waivers). Stale waivers are also
flagged.

## `--validator-fields` — `audit_validator_fields` (`events.py:262`)

AST-walks `validate_frontmatter.py` for `info.get("<field>")` calls;
collects every literal `<field>` name. AST-walks `ledger.py` for
`graph[…]["<field>"]` writes, `entry["<field>"]` accesses, and dict
keys inside `_artifact_creation_entry`. Read fields not written
anywhere (and not in `_VALIDATOR_FIELD_WAIVERS`, currently empty) emit
a `ValidationError`.

## `--audits` — aggregator

Runs `audit_event_handlers`, `audit_event_schemas`, and
`audit_validator_fields` and merges their outputs. No new invariant of
its own.

## `--reconcile-freshness` — `audit_reconcile_freshness` (`reconcile.py:68`)

Loads `.gzkit/ledger.jsonl`, scans for the most recent
`reconcile_*`-shaped event, compares its timestamp against the HEAD
commit time, and emits a `ValidationError` if drift > 24h. Fail-opens
at zero-event bootstrap (no `reconcile_*` events yet — first-run
bootstrap is not drift).

## `--insights-shape` — `audit_insights_shape` (`insights.py:74`)

Reads `.gzkit/insights/agent-insights.jsonl` line by line, validates
each record against the `InsightRecord` Pydantic model (`extra="forbid"`,
ISO8601 `ts` field, enum `type`, `evidence: list[str]`). Pre-lock
entries are waived by content-hash in `_INSIGHTS_SHAPE_WAIVERS`; new
writes must conform.

## `--instructions-files-budget` — `audit_instructions_files_budget` (`instructions_files_budget.py:61`)

Reads `data/instructions_files_budget.json`. For each tracked file
(`AGENTS.md`, `CLAUDE.md`, every `.claude/rules/*.md`), measures the
character count against the configured budget. Default ceilings: 40k
chars for `AGENTS.md`/`CLAUDE.md`, 16k per rule file. Overruns emit a
`ValidationError` with remediation pointer to `/gz-context-diet`.

## `--orientation-freshness` — `audit_orientation_freshness` (`orientation.py:200`)

Verifies the `SessionStart` hook in `.claude/settings.json` (or
ancestor) is wired to `scripts/session_orientation.py`, and that the
script exists, is readable, and has not drifted from a baseline fingerprint.
Drift emits a `ValidationError` (GHI #341).

## `--brief-headings` — `audit_brief_headings` (`briefs.py:83`)

Walks `docs/design/adr/**/OBPI-*.md`. For each line, checks whether the
line starts with `## ` and the casefolded heading-stem matches one of
`{Implementation Summary, Key Proof, Closing Argument}`. Matches emit
a `ValidationError` because these sections must be `### ` (H3) for
ceremony extractor compatibility.

## `--behave-req-tags` — `audit_behave_req_tags` (`briefs.py:203`)

Enumerates `docs/design/adr/**/OBPI-*.md` excluding the `pool/` subtree.
For each brief, parses YAML frontmatter `lane:` (heavy required) and
`status:` (`completed` or `validated` required). Extracts REQ-IDs from
the `## Acceptance Criteria` section via regex
`\bREQ-\d+\.\d+\.\d+-\d+-\d+\b`. Walks `features/**/*.feature` for
scenario-level `@REQ-X.Y.Z-NN-MM` tags. Missing REQ-IDs emit a
`ValidationError` unless the OBPI is waived in
`data/behave_coverage_waivers.json`.

## `--chores-layout` — `audit_chores_layout` (`chores.py:28`)

Walks the project tree from `project_root`, filters to files named
`CHORE.md` or `acceptance.json`, skips hidden / `__pycache__` / `.venv`
/ `dist` / `build` / `node_modules` ancestors. Files not under either
canonical root (`src/gzkit/chores/` or the project-configured chores
path, default `.gzkit/chores/`) and not waived in
`data/chores_layout_waivers.json` emit a `ValidationError`.

## `--unscoped-rules` — `gzkit.rules.unscoped_audit`

(Delegated outside `trust_audits/`.) Enumerates `.gzkit/rules/*.md`,
parses YAML frontmatter, and fails closed on any file carrying
`paths: "**"` or missing `paths:` unless allow-listed in
`.gzkit/manifest.json` `rules.unscoped_allowlist`. Allow-list schema
enforced via `UnscopedAllowlistEntry` Pydantic model + manifest JSON
Schema.

## `--sensitivity` — `audit_sensitivity_binding` (`sensitivity.py:168`)

Loads `data/security_surfaces.json` via the `SecuritySurfaceEntry`
Pydantic model (fail-closed on missing/malformed registry). For each
brief, parses the `## ALLOWED PATHS` block, extracts backticked path
literals, intersects them against the registry's path globs. If
intersection is non-empty and the brief's `sensitivity:` frontmatter
is absent or not `security`, emits a `ValidationError` (auto-detect
floor). Escalation (sensitivity:security without overlap) is permitted.

## `--commit-trailers` — delegated

(Outside `trust_audits/`.) Runs `git log -1 --name-only`, lists files
touched by HEAD, and if any path matches `src/**` or `tests/**`,
asserts the commit message contains a `Task:`, `Ceremony:`, or
`Eval-feedback-source:` trailer.

## `--complexity-doctrine-links` — `validate_complexity_doctrine_links` (`complexity_doctrine_links.py:188`)

Scans cluster ADRs (0.0.27/0.0.28/0.0.29/0.0.30) and
`.gzkit/rules/complexity-doctrine.md` for citation tuples matching the
`§ <anchor> (corpus revision N)` heuristic. Verifies the cited
`docs/governance/complexity/distilled-characteristics-*.md` file
exists, the anchor resolves, and the corpus revision falls within the
supported portability window (N or N+1). HTML-comment escape marker
`<!-- gz-validate-skip: complexity-doctrine-links -->` supported.

## `--complexity-thresholds` — `validate_complexity_thresholds` (`complexity_thresholds.py:43`)

Loads `.gzkit/rules/complexity-thresholds.json` via the `ThresholdTable`
Pydantic model. Asserts every canonical metric (twelve named) declares
a `block` band; every band has percentile + absolute paired; trigger
semantics restricted to `{block, warn, advise}`; citation tuple parses.
Bootstrap-mode notice (for `radon_mi`, `lizard_nesting_depth`,
`cohesion_lcom4`) is informational, not a policy breach.

## `--doc-surface-parity` — `audit_doc_surface_parity` (`doc_surface_parity.py:22`)

Asserts the decommissioned `docs/user/commands/` directory does not
exist (GHI #418). Single-purpose archeological check.

## `--absorption-duplicates` — `audit_absorption_duplicates` (`absorption_duplicates.py:83`)

Scans `opsdev/` evidence references across parent ADRs; flags the same
source path appearing under multiple parent ADRs without a
`paired_with:` declaration (GHI #376).

## `--evaluation-justify-binding` — `validate_evaluation_justify_binding` (`evaluation_justify_binding.py:20`)

Scans ledger `adr-evaluation` events for scores below 3.0 and asserts
a paired `gz-justify` artifact exists with binding fields. Implements
ADR-0.0.26 evaluation-feedback-loop doctrine.

## `--intrinsic-attestation` — `validate_intrinsic_attestation` (`intrinsic_attestation.py:30`)

Walks `.gzkit/ledger.jsonl` for `intrinsic-complexity-attestation`
events and validates each payload against the OBPI-0.0.29-07 schema
(required: function FQN, complexity metric, attestor, rationale).

## `--advisor-proof-binding` — `validate_advisor_proof_binding` (`advisor_proof_binding.py:30`)

Walks `tests/fixtures/advisor/*.json` for diagnoses with empty `proof`
arrays (skipping fixtures marked `"_negative_case": true`). Inspects
`src/gzkit/schemas/advisor_diagnosis.json` for `properties.proof.minItems
>= 1`. Walks ledger for `intrinsic-complexity-attestation` events
referencing diagnosis IDs whose fixtures have empty proof. Any of the
three failure modes emits a `ValidationError`.

## `--attestation-receipts` — `validate_attestation_receipts` (`attestation_receipts.py:171`)

Parses an attestation string for ARB receipt IDs (prefix patterns
`arb-ruff-`, `arb-step-typecheck-`, `arb-step-unittest-`, etc.),
verifies each referenced ID resolves to a `.gzkit/arb/receipts/*.json`
file. Heavy-lane: missing IDs fail closed. Lite-lane: warn-only.
