# Promoted Check Inventory

**Generated:** 2026-05-10
**Sources:**
- `uv run gz validate --help` (flag list captured to `proofs/validate-help.txt`)
- `src/gzkit/governance/trust_audits/*.py` (audit function bodies)
- `docs/governance/advisory-rules-audit.md` (promotion-status ledger)

Every row is a `gz validate --<scope>` flag that resolves to a concrete audit
function and asserts a defined invariant. Rule-shaped flags that have no
underlying audit function (`--manifest`, `--documents`, `--surfaces`,
`--ledger`, `--briefs`, `--personas`, `--frontmatter`, etc.) are out of
scope for this drift audit because they wrap schema validation, not rule
prose.

| # | Scope flag | Audit function | Module | What it asserts |
|---|------------|----------------|--------|-----------------|
| 1 | `--advisory-scorecard` | `audit_advisory_scorecard` | `src/gzkit/governance/trust_audits/release.py:83` | Every `.gzkit/rules/*.md` stem appears (case-folded substring) in `docs/governance/advisory-rules-audit.md`. |
| 2 | `--utf8-prefix` | `audit_utf8_prefix` | `src/gzkit/governance/trust_audits/cross_platform.py:80` | No `PYTHONUTF8=1 uv run gz` anti-pattern, no `gz \| python` fresh-interpreter pipes without `sys.stdout.reconfigure`, no `gz \| {jq,awk,sed}` non-Python pipes, and `tools/**/*.py` entry points configure UTF-8. |
| 3 | `--version-release` | `audit_version_release` | `src/gzkit/governance/trust_audits/release.py:19` | The `pyproject.toml` version has a matching `vX.Y.Z` git tag OR an in-flight `docs/releases/PATCH-vX.Y.Z.md` manifest. |
| 4 | `--pool-adr-isolation` | `audit_pool_adr_isolation` | `src/gzkit/governance/trust_audits/taxonomy.py:50` | No ledger event whose artifact id has prefix `ADR-pool.` carries an event type in `{gate_checked, attestation, obpi_completed, adr_attested, adr_audit, adr_closeout, lifecycle_transition}`. |
| 5 | `--taxonomy` | `audit_adr_taxonomy` | `src/gzkit/governance/trust_audits/taxonomy.py:175` | `kind:foundation` requires semver `0.0.x`, `kind:feature` requires non-`0.0.x`, pool ADRs (id-prefix `ADR-pool.`) carry neither `kind:` nor `semver:`. |
| 6 | `--adr-status-fresh` | `audit_adr_status_fresh` | `src/gzkit/governance/trust_audits/taxonomy.py:232` | `docs/governance/GovZero/adr-status.md` agrees with on-disk ADR canon (frontmatter + H1) under `docs/design/adr/{foundation,pre-release}/`. |
| 7 | `--test-tiers` | `audit_test_tiers` | `src/gzkit/governance/trust_audits/code_quality.py:126` | No `tests/{integration,e2e,slow,bdd}/` subdir; no forbidden `--integration`/`--e2e`/`--slow`/`--bdd-only` flags in `parser_*.py`. |
| 8 | `--type-ignores` | `audit_type_ignores` | `src/gzkit/governance/trust_audits/code_quality.py:37` | No `# type: ignore[<code>]` comment under `src/`; only bare `# type: ignore` or `# ty: ignore[<ty-code>]` permitted. |
| 9 | `--class-size` | `audit_class_size` | `src/gzkit/governance/trust_audits/code_quality.py:73` | Every `ast.ClassDef` under `src/gzkit/` spans <=300 source lines unless waived in `_CLASS_SIZE_WAIVERS`. |
| 10 | `--pydantic-models` | `audit_pydantic_models` | `src/gzkit/governance/trust_audits/models.py:69` | No `@dataclass` decorator in `src/gzkit/**` (unless waived in `_DATACLASS_WAIVERS`); every `BaseModel` subclass declares a `model_config` attribute. |
| 11 | `--cli-alignment` | `audit_cli_alignment` | `src/gzkit/governance/trust_audits/cli.py:87` | Every backticked / quoted `gz <verb>` reference in operator-facing docs (`docs/user/runbook.md`, `docs/user/{commands,manpages}/**`, `features/**/*.feature`) resolves to a registered parser subcommand. |
| 12 | `--skill-alignment` | `audit_skill_alignment` | `src/gzkit/governance/trust_audits/cli.py:149` | Every top-level CLI verb has at least one wielding skill in `.gzkit/skills/**` (via frontmatter `gz_command:` or body) OR is in `_NO_SKILL_VERBS` with rationale. |
| 13 | `--event-handlers` | `audit_event_handlers` | `src/gzkit/governance/trust_audits/events.py:88` | Every ledger event type emitted by `src/gzkit/ledger_events.py` has a graph handler in `src/gzkit/ledger.py` OR an explicit `_NO_GRAPH_IMPACT` waiver. |
| 14 | `--validator-fields` | `audit_validator_fields` | `src/gzkit/governance/trust_audits/events.py:262` | Every `info.get('<field>')` read in `validate_frontmatter.py` has a corresponding writer in `ledger.py` (graph-write, entry-key, or `_artifact_creation_entry` initializer). |
| 15 | `--audits` | aggregator | `src/gzkit/commands/validate.py` | Runs `audit_event_handlers`, `audit_event_schemas`, `audit_validator_fields` together. No new invariant of its own. |
| 16 | `--reconcile-freshness` | `audit_reconcile_freshness` | `src/gzkit/governance/trust_audits/reconcile.py:68` | The latest `reconcile_*` ledger event is within 24h of HEAD commit time; fail-open at zero-event bootstrap. |
| 17 | `--insights-shape` | `audit_insights_shape` | `src/gzkit/governance/trust_audits/insights.py:74` | Every record in `.gzkit/insights/agent-insights.jsonl` validates against the `InsightRecord` Pydantic model (`extra="forbid"`, ISO8601 `ts`, enum `type`, `evidence: list[str]`). |
| 18 | `--instructions-files-budget` | `audit_instructions_files_budget` | `src/gzkit/governance/trust_audits/instructions_files_budget.py:61` | `AGENTS.md`, `CLAUDE.md`, and each `.claude/rules/*.md` file stays within the char budget configured in `data/instructions_files_budget.json` (defaults: 40k AGENTS.md/CLAUDE.md, 16k per rule file). |
| 19 | `--orientation-freshness` | `audit_orientation_freshness` | `src/gzkit/governance/trust_audits/orientation.py:200` | The SessionStart orientation hook and the `scripts/session_orientation.py` script remain wired (GHI #341). |
| 20 | `--brief-headings` | `audit_brief_headings` | `src/gzkit/governance/trust_audits/briefs.py:83` | OBPI briefs under `docs/design/adr/**/OBPI-*.md` carry `Implementation Summary`, `Key Proof`, `Closing Argument` as H3 (`### …`), not H2. |
| 21 | `--behave-req-tags` | `audit_behave_req_tags` | `src/gzkit/governance/trust_audits/briefs.py:203` | Every REQ-ID extracted from the `## Acceptance Criteria` section of a heavy-lane OBPI brief in status `completed` or `validated` (non-pool) has a matching scenario-level `@REQ-X.Y.Z-NN-MM` tag under `features/**` OR is waived in `data/behave_coverage_waivers.json`. |
| 22 | `--chores-layout` | `audit_chores_layout` | `src/gzkit/governance/trust_audits/chores.py:28` | No stray `CHORE.md` / `acceptance.json` outside `src/gzkit/chores/` or the project-configured chores path (default `.gzkit/chores/`) unless waived in `data/chores_layout_waivers.json`. |
| 23 | `--unscoped-rules` | (delegated to `gzkit.rules.unscoped_audit`) | `src/gzkit/rules.py` + ADR-0.0.20 | Every `.gzkit/rules/*.md` carries scoped `paths:` frontmatter; `paths: "**"` or missing `paths:` fail-closed unless allowlisted in `.gzkit/manifest.json` `rules.unscoped_allowlist`. |
| 24 | `--sensitivity` | `audit_sensitivity_binding` | `src/gzkit/governance/trust_audits/sensitivity.py:168` | Briefs whose `## ALLOWED PATHS` overlap an entry in `data/security_surfaces.json` MUST declare `sensitivity: security`; escalation-without-overlap is permitted. |
| 25 | `--commit-trailers` | (delegated to `gzkit.commands.validate_cmd`) | `src/gzkit/commands/validate*.py` | HEAD commits touching `src/` or `tests/` carry a `Task:`, `Ceremony:`, or `Eval-feedback-source:` trailer. |
| 26 | `--complexity-doctrine-links` | `validate_complexity_doctrine_links` | `src/gzkit/governance/trust_audits/complexity_doctrine_links.py:188` | Citations of distilled-characteristics docs from cluster ADRs (0.0.27/0.0.28/0.0.29/0.0.30) and `.gzkit/rules/complexity-doctrine.md` resolve (file + anchor) and `corpus_revision` falls within the supported portability window. |
| 27 | `--complexity-thresholds` | `validate_complexity_thresholds` | `src/gzkit/governance/trust_audits/complexity_thresholds.py:43` | `.gzkit/rules/complexity-thresholds.json` declares a `block` band for every canonical metric; trigger semantics restricted to `{block, warn, advise}`; citation tuple parses; bootstrap-mode notice is informational only. |
| 28 | `--doc-surface-parity` | `audit_doc_surface_parity` | `src/gzkit/governance/trust_audits/doc_surface_parity.py:22` | The decommissioned `docs/user/commands/` directory does not exist (GHI #418). |
| 29 | `--absorption-duplicates` | `audit_absorption_duplicates` | `src/gzkit/governance/trust_audits/absorption_duplicates.py:83` | The same `opsdev` source path appearing across multiple parent ADRs requires a `paired_with:` declaration (GHI #376). |
| 30 | `--evaluation-justify-binding` | `validate_evaluation_justify_binding` | `src/gzkit/governance/trust_audits/evaluation_justify_binding.py:20` | Low ADR evaluation scores (<3.0) require a paired `gz-justify` artifact (ADR-0.0.26). |
| 31 | `--intrinsic-attestation` | `validate_intrinsic_attestation` | `src/gzkit/governance/trust_audits/intrinsic_attestation.py:30` | `intrinsic-complexity-attestation` ledger events validate against the OBPI-0.0.29-07 payload schema. |
| 32 | `--advisor-proof-binding` | `validate_advisor_proof_binding` | `src/gzkit/governance/trust_audits/advisor_proof_binding.py:30` | Every advisor diagnosis fixture under `tests/fixtures/advisor/*.json` carries a non-empty `proof` array; the schema enforces `minItems >= 1`; ledger events citing diagnoses with empty proofs fail-closed. |
| 33 | `--attestation-receipts` | `validate_attestation_receipts` | `src/gzkit/governance/trust_audits/attestation_receipts.py:171` | Receipt IDs in an attestation string reference real `.gzkit/arb/receipts/*.json` files; heavy-lane fail-closed on missing IDs, lite-lane warn. |

## Out-of-scope flags (schema/IO wrappers)

These flags appear in `gz validate --help` but operate on JSON Schema / manifest
IO rather than rule prose, so they are excluded from the parity diff:

- `--manifest` — validates `.gzkit/manifest.json` against schema
- `--documents` — validates governance docs (PRD/ADR/OBPI shape)
- `--surfaces` — validates control surfaces (skills, mirrors)
- `--ledger` — validates ledger integrity against `schemas/ledger.json`
- `--instructions` — validates AGENTS.md / CLAUDE.md instructions structure
- `--briefs` — validates OBPI briefs against the OBPI schema
- `--personas` — validates `.gzkit/personas/*.md`
- `--interviews` — verifies ADRs with OBPIs have interview transcripts
- `--decomposition` — validates ADR decomposition scorecards + 1:1 checklist sync
- `--requirements` — flags OBPI briefs whose REQUIREMENTS sections lack REQ-IDs
- `--frontmatter` / `--adr` / `--explain` — frontmatter-vs-ledger drift validator
- `--version` — version-consistency check across pyproject/`__init__.py`/README
- `--allowlist-only` — list current unscoped-rule allowlist entries; not an enforcement flag
- `--lane` / `--kind` — modifiers for `--attestation-receipts`, not standalone scopes
