# Plan: OBPI-0.0.13-05 — Persona Drift Monitoring

## Context

ADR-0.0.13 (Portable Persona Control Surface) needs a `gz personas drift` command
that reports persona adherence metrics using behavioral proxies. This is item #5
on the ADR checklist. OBPIs 01-04 are complete — persona schema, scaffolding,
manifest sync, and vendor loading are all in place. This OBPI closes the feedback
loop: personas define expected behavior, drift detection measures observed behavior.

The command scans local governance artifacts (ledger events, OBPI audit logs) for
evidence of trait-aligned behavior. No network access, no model-internal
measurement. Heavy lane (new subcommand).

Existing patterns reused:
- `src/gzkit/commands/drift.py` — check-and-report CLI pattern with DriftReport model
- `src/gzkit/commands/validate_cmd.py` — multi-scope validation with error accumulation
- `src/gzkit/cli/helpers/exit_codes.py` — EXIT_POLICY_BREACH = 3
- `src/gzkit/models/persona.py` — PersonaFrontmatter, parse_persona_file, discover_persona_files
- `src/gzkit/personas.py` — compose_persona_frame, vendor adapters, TRAIT_PROXY_REGISTRY pattern

---

## Implementation Steps

### Step 1: Add Pydantic models to `src/gzkit/models/persona.py`

Add after existing models (~55 lines, file goes from 108 to ~163):

- `TraitCheckResult` — frozen model: `trait`, `status` (pass/fail/no_evidence), `proxy`, `detail`, `is_anti_trait`
- `PersonaDriftResult` — frozen model: `persona`, `checks: list[TraitCheckResult]`, `has_drift: bool`
- `PersonaDriftReport` — frozen model: `personas: list[PersonaDriftResult]`, `total_personas`, `total_checks`, `drift_count`, `scan_timestamp`

### Step 2: Add drift engine to `src/gzkit/personas.py`

Add after vendor adapter section (~200 lines, file goes from 263 to ~460):

**Artifact scanning helpers:**
- `_scan_ledger_events(project_root: Path) -> list[dict[str, Any]]` — read `.gzkit/ledger.jsonl`
- `_scan_obpi_audit_logs(project_root: Path) -> list[dict[str, Any]]` — glob `docs/design/adr/**/logs/obpi-audit.jsonl`

**Five proxy functions** (each <=30 lines, signature: `(Path, list[dict], list[dict]) -> tuple[str, str]`):

| Proxy | Evidence checked | Traits served |
|---|---|---|
| `_governance_activity_proxy` | gate_checked, attested, audit_receipt_emitted events | governance-aware, governance-fidelity, evidence-anchoring |
| `_test_evidence_proxy` | OBPI audit test_count > 0, tests_passed = true | test-first, thorough, architectural-rigor |
| `_evidence_quality_proxy` | criteria_evaluated with PASS + substantive evidence text | evidence-driven, evidence-based-assessment, precision |
| `_completion_quality_proxy` | brief_status_after = Completed, obpi_receipt completed | complete-units, atomic-edits, ceremony-completion |
| `_plan_discipline_proxy` | adr_created events temporally before gate_checked events | methodical, plan-then-write, stage-discipline, sequential-flow |

**Trait proxy registry:**
- `TRAIT_PROXY_REGISTRY: dict[str, tuple[str, TraitProxyFn]]` — maps trait keywords to (proxy_name, proxy_fn)
- Unmapped traits get `status="no_evidence"`, `proxy="unmapped"`
- `no_evidence` does NOT count as drift — only `fail` counts

**Anti-trait semantics:** Anti-traits that have a proxy are checked inversely. Most anti-traits will be `no_evidence` (honest — cannot prove absence of behavior from artifacts).

**Main entry point:**
- `evaluate_persona_drift(project_root: Path, persona_name: str | None = None) -> PersonaDriftReport`
- Pre-loads ledger events and audit logs once, passes to each proxy
- Filters to single persona when `persona_name` is set

### Step 3: Add CLI command to `src/gzkit/commands/personas.py`

Add alongside `personas_list_cmd` (~95 lines, file goes from 65 to ~160):

- `persona_drift_cmd(*, persona: str | None, as_json: bool) -> None`
- JSON output: `report.model_dump_json(indent=2)` to stdout
- Human output: Rich table per persona (Trait, Type, Proxy, Status, Detail columns)
- No-drift case: prints "No persona drift detected."
- Exit: `SystemExit(EXIT_POLICY_BREACH)` when `drift_count > 0`, implicit 0 otherwise
- `_format_drift_table(report)` helper for human rendering

### Step 4: Wire parser in `src/gzkit/cli/parser_governance.py`

Add `drift` subcommand to existing `personas_commands` subparser (~25 lines, file goes from 556 to ~582):

- Import `persona_drift_cmd` at top alongside existing `personas_list_cmd` import
- Register `drift` parser with `--persona` (default None) and `--json` flags
- Help text includes description mentioning behavioral proxies and example usage
- Epilog with 3 examples: bare, --json, --persona

### Step 5: Write unit tests in `tests/test_persona_drift.py` (new)

~200 lines. Table-driven tests with `@covers` decorators:

- `TestTraitProxyRegistry` — verify known traits are mapped, unmapped traits get no_evidence
- `TestGovernanceActivityProxy` — pass with events, fail without
- `TestTestEvidenceProxy` — pass with test counts, fail without
- `TestEvaluatePersonaDrift` — integration: all personas, single filter, drift_count semantics
- `TestAntiTraitInversion` �� anti-traits marked correctly in results

All tests use `tempfile.TemporaryDirectory` with synthetic ledger/audit JSONL.

### Step 6: Add CLI tests to `tests/commands/test_personas_cmd.py`

Add `TestPersonasDriftCmd` class (~75 lines, file goes from 105 to ~180):

- `test_drift_human_output` — REQ-01: table with persona names
- `test_drift_json_output` �� REQ-02: valid JSON with expected keys
- `test_drift_single_persona` — REQ-03: --persona filter works
- `test_drift_exit_0_no_drift` — REQ-04: exit 0 when no drift
- `test_drift_exit_3_on_drift` — REQ-05: exit 3 on policy breach
- `test_drift_help` — REQ-06: help text with description and examples

### Step 7: Add BDD scenarios to `features/persona.feature`

Add ~20 lines of drift scenarios using existing steps + new step for ledger seeding:

- Drift reports no drift with governance evidence (exit 0)
- Drift JSON output is valid
- Drift filters to single persona
- New step `the ledger contains gate check events` in `features/steps/persona_steps.py`

### Step 8: Write docs

**`docs/user/commands/personas-drift.md`** (new, ~60 lines):
- Usage, description, options table, exit codes table, examples, proxy categories

**`docs/user/manpages/gz-personas.md`** (new, ~40 lines):
- Manpage covering both `list` and `drift` subcommands

---

## Verification

```bash
# Unit tests
uv run -m unittest tests.test_persona_drift -v
uv run -m unittest tests.commands.test_personas_cmd -v

# Quality gates
uv run gz lint
uv run gz typecheck
uv run gz test

# Heavy lane gates
uv run mkdocs build --strict
uv run -m behave features/persona.feature

# Functional verification
uv run gz personas drift --help
uv run gz personas drift
uv run gz personas drift --persona implementer
uv run gz personas drift --json
echo $?
```
