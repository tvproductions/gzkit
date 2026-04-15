# Plan: OBPI-0.25.0-33 — Absorb airlineops/arb/ into gzkit

## Context

OBPI-0.25.0-33 is the final OBPI blocking ADR-0.25.0-core-infrastructure-pattern-absorption from closeout. The brief asks for an Absorb/Confirm/Exclude decision on `airlineops/src/opsdev/arb/` (Agent Self-Reporting middleware — ruff/step wrapping, JSON receipt emission, validation, and advice synthesis).

**A governance vacuum surfaced during planning:**

- `.gzkit/rules/arb.md` (canonical, v1.0 Active) documents a complete `gz arb` CLI surface — `ruff`, `step`, `ty`, `coverage`, `validate`, `advise` — with schema IDs `gzkit.arb.lint_receipt.v1` and storage at `artifacts/receipts/`.
- `.claude/rules/attestation-enrichment.md` requires ARB receipt IDs for every Heavy-lane attestation claim (fail-closed): *"The only faithful record of a QA step is the wrapped-command receipt."*
- **None of this exists.** No `gz arb` CLI verb, no `src/gzkit/arb/` package, no `data/schemas/arb_*.json`, no `artifacts/receipts/` directory.

**Forensic trace (how the drift happened):**

1. `37c891ca` (2026-03-15, "chore: regenerate control surfaces after tidy implementation") — `.claude/rules/arb.md` was added as a mirrored instruction file copied wholesale from airlineops, with commands prefixed `uv run -m opsdev arb ...` and schema ID `airlineops.arb.lint_receipt.v1`.
2. `4700b623` (2026-03-18, "chore: auto-commit staged changes (gz git-sync)") — A mechanical find-and-replace converted `opsdev` → `gzkit` and `airlineops.arb.lint_receipt.v1` → `gzkit.arb.lint_receipt.v1` (18 insertions, 18 deletions). No accompanying implementation. The rename was bundled into an auto-commit whose message carried no semantic signal.
3. `32dfd36b` (2026-03-18) — `.gzkit/rules/arb.md` canonicalized the renamed content, locking in the drift.
4. `4c7573fc` and `f350cf44` — `attestation-enrichment.md` was added and hardened to fail-closed Heavy-lane status, prescribing ARB receipts as the canonical record, without anyone verifying the infrastructure existed.

ARB is not airline-specific by design intent. Per the user direction: *"we need to onboard it, that is the point of this adr."* The correct decision is **Absorb**. This plan describes the minimum viable port that makes the `.gzkit/rules/arb.md` rule real and closes the governance vacuum for future attestations.

## Intended Outcome

At completion:

1. `gz arb --help` returns the subcommand tree: `ruff`, `step`, `ty`, `coverage`, `validate`, `advise`, `patterns`.
2. `gz arb ruff` wraps ruff and writes a validated lint receipt to `artifacts/receipts/`.
3. `gz arb step --name <name> -- <cmd...>` wraps any command and writes a step receipt.
4. `gz arb validate` and `gz arb advise` read receipts and produce output matching the rule's documented shape.
5. `data/schemas/arb_lint_receipt.schema.json` and `arb_step_receipt.schema.json` exist with schema ID `gzkit.arb.lint_receipt.v1` / `gzkit.arb.step_receipt.v1`.
6. `src/gzkit/arb/` is a proper gzkit package (Pydantic models, pathlib, UTF-8 encoding, typed config wiring).
7. The OBPI brief records Decision: Absorb with concrete file:line rationale.
8. ADR-0.25.0 can close — all 33 OBPIs attested.

## Scope — What to Port from airlineops/arb/

**In scope (core 603+ lines identified by the brief + supporting infrastructure):**

| airlineops file | gzkit target | Lines | Notes |
|-----------------|-------------|-------|-------|
| `advise.py` | `src/gzkit/arb/advisor.py` | 196 | Dataclass → Pydantic; schema ID rename; drop `opsdev` tidy nudge text |
| `validate.py` | `src/gzkit/arb/validator.py` | 154 | Dataclass → Pydantic; schema path points to `data/schemas/arb_*.json` |
| `patterns.py` | `src/gzkit/arb/patterns.py` | 253 | Dataclass → Pydantic; library + CLI verb |
| `paths.py` | `src/gzkit/arb/paths.py` | 43 | Rewire to gzkit `ProjectConfig` typed config |
| `ruff_reporter.py` | `src/gzkit/arb/ruff_reporter.py` | 247 | Drop `github_issues` + `supabase_sync` imports; schema ID rename |
| `step_reporter.py` | `src/gzkit/arb/step_reporter.py` | 138 | Drop external integrations; schema ID rename |
| `__init__.py` | `src/gzkit/arb/__init__.py` | 8 | Re-export public surface |

Total port surface ≈ 1039 lines (not 603 — the brief under-counted by excluding reporters and paths; the three files it names — advise/validate/patterns — are the *analysis* surface and require the reporters to produce receipts).

**Out of scope (deferred or explicitly rejected):**

- `expunge.py` (114L, pruning) — defer to future ARB tidy OBPI.
- `github_issues.py` (149L, `--file-issue` flag) — not in current `.gzkit/rules/arb.md` command list; defer.
- `supabase_sync.py` (157L, external DB) — airline-infra; exclude.
- `tidy.py` (170L, retention policy) — defer.

## Implementation Plan

The plan below is the TDD sequence. Every Green step has a preceding Red step. No batching.

### Step 0 — Amend the OBPI brief's Allowed Paths (scope expansion)

The current brief lists only `src/gzkit/`, `tests/`, and the ADR directory. This port touches:

- `data/schemas/arb_lint_receipt.schema.json`, `data/schemas/arb_step_receipt.schema.json`
- `docs/user/commands/arb.md`, `docs/user/manpages/arb.md`
- `features/arb.feature`, `features/steps/arb_steps.py`
- `.gzkit/rules/arb.md` (rule correction — reality check)
- `.gzkit/skills/` (if a new skill is needed to satisfy Invariant 1)

Amend the brief's ALLOWED PATHS section to include these surfaces. This is scope-honest, not scope creep — the brief was under-scoped at authoring time because it assumed the decision would be Confirm/Exclude.

### Step 1 — Add ARB config to `src/gzkit/config.py`

Extend `ProjectConfig` with `arb: ArbConfig`:

```python
class ArbConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    receipts_root: str = Field(
        default="artifacts/receipts",
        description="Directory where ARB writes receipt JSON files.",
    )
    default_limit: int = Field(
        default=20,
        description="Default number of recent receipts scanned by validate/advise.",
    )
```

Test: `tests/test_config.py` — assert `ArbConfig` round-trips and defaults are stable.

### Step 2 — Port schemas (Red→Green: schema loader test first)

Files: `data/schemas/arb_lint_receipt.schema.json`, `data/schemas/arb_step_receipt.schema.json`.

Port from airlineops with these substitutions:
- `airlineops.arb.lint_receipt.v1` → `gzkit.arb.lint_receipt.v1`
- `airlineops.arb.step_receipt.v1` → `gzkit.arb.step_receipt.v1`

Test first: `tests/arb/test_schemas.py` — load both schemas via `jsonschema.Draft202012Validator.check_schema()`; assert `$id` values match.

### Step 3 — Port `paths.py` (Red first)

Test: `tests/arb/test_paths.py` — `receipts_root()` returns `Path(config.arb.receipts_root)` resolved against project root; respects `GZKIT_ARB_RECEIPTS_ROOT` env override (for tests); creates the directory if missing.

Code: `src/gzkit/arb/paths.py` — use `pathlib.Path`, `encoding="utf-8"`, and the gzkit `ProjectConfig` typed loader (not airlineops's `Settings + registry` pattern).

### Step 4 — Port `ruff_reporter.py` (Red first)

Test: `tests/arb/test_ruff_reporter.py` — mocks `subprocess.run` for ruff:
- Green ruff run → receipt JSON has `schema == "gzkit.arb.lint_receipt.v1"`, `exit_status == 0`, empty findings.
- Failing ruff run → receipt has `exit_status == 1`, parsed findings (rule/path/line/message).
- Broken ruff invocation → fallback `ARB000` finding captured.
- Git context captured when `.git` exists.
- Receipt file named `<uuid>.json` under `receipts_root()`.

Code: `src/gzkit/arb/ruff_reporter.py`:
- Drop `from .github_issues import ...` and `from .supabase_sync import push_receipt`.
- Constant `SCHEMA_ID = "gzkit.arb.lint_receipt.v1"`.
- Keep `_run_command`, `_ruff_version`, `_git_context`, `_fallback_findings`, `_canonical` helpers.
- Use `subprocess.run([...], text=True, encoding="utf-8")` (not `shell=True`) per cross-platform rule.

Size budget: airlineops was 247L; dropping 2 imports + their call sites should land near 200L, well under the 600-line module limit.

### Step 5 — Port `step_reporter.py` (Red first)

Test: `tests/arb/test_step_reporter.py` — mocks `subprocess.run` for arbitrary commands:
- Any command → receipt with `schema == "gzkit.arb.step_receipt.v1"`, `name`, `argv`, `exit_status`, `stdout_tail`, `stderr_tail`, duration.
- Tail truncation respects configured max chars.
- Non-UTF-8 output decodes with `errors="replace"`.

Code: `src/gzkit/arb/step_reporter.py` — drop integrations, keep everything else.

### Step 6 — Port `validator.py` (Red first)

Test: `tests/arb/test_validator.py`:
- Fixture dir with one valid lint receipt + one valid step receipt + one malformed JSON + one unknown schema → `validate_receipts()` returns counts: `{valid: 2, invalid: 1, unknown_schema: 1}`.
- Schema-ID mismatch surfaced as invalid with reason.
- `limit` parameter honored (most-recent N).

Code: `src/gzkit/arb/validator.py`:
- Replace airlineops's dataclass with `ArbReceiptValidationResult(BaseModel, frozen=True, extra="forbid")`.
- Load schemas from `data/schemas/arb_*.json` via project root (`gzkit.paths.project_root()` or equivalent).
- `jsonschema.Draft202012Validator` — already a transitive dep or add to `pyproject.toml`.

### Step 7 — Port `advisor.py` (Red first)

Test: `tests/arb/test_advisor.py`:
- Fixture receipts with style-dominant rules (E/W/I) → advice says "Style-dominant failures: tighten the agent loop…".
- Fixture with correctness rules (F/B) → advice says "Correctness-class rules present…".
- Empty receipts dir → `ArbAdvice` with `scanned_receipts == 0` and the zero-state message.
- `collect_arb_advice(limit=5)` honors limit.
- Retention nudge always appears at end of recommendations and references `uv run gz arb tidy` (gzkit form) rather than `uv run -m opsdev arb tidy`.

Code: `src/gzkit/arb/advisor.py`:
- Convert `ArbAdvice` dataclass to Pydantic `BaseModel` with `frozen=True, extra="forbid"`.
- Rewrite the `tidy` nudge text to the gzkit form (even though `gz arb tidy` is out of scope in this port, the nudge should reference the future-correct command, not `opsdev`).
- Keep `render_arb_advice_text()` as-is.

### Step 8 — Port `patterns.py` (Red first)

Test: `tests/arb/test_patterns.py` — fixture receipts with repeating rule codes → `collect_patterns()` returns `PatternReport` with `PatternCandidate` entries sorted by count; RULE_GUIDANCE dict maps known ruff codes to human-readable advice.

Code: `src/gzkit/arb/patterns.py` — straight port, dataclass → Pydantic, no external integrations.

### Step 9 — Package `__init__.py` and public surface

File: `src/gzkit/arb/__init__.py`:

```python
from gzkit.arb.advisor import ArbAdvice, collect_arb_advice, render_arb_advice_text
from gzkit.arb.models import ArbReceiptValidationResult
from gzkit.arb.patterns import PatternCandidate, PatternReport, collect_patterns
from gzkit.arb.paths import receipts_root
from gzkit.arb.ruff_reporter import run_ruff_via_arb
from gzkit.arb.step_reporter import run_step_via_arb
from gzkit.arb.validator import validate_receipts

__all__ = [
    "ArbAdvice",
    "ArbReceiptValidationResult",
    "PatternCandidate",
    "PatternReport",
    "collect_arb_advice",
    "collect_patterns",
    "receipts_root",
    "render_arb_advice_text",
    "run_ruff_via_arb",
    "run_step_via_arb",
    "validate_receipts",
]
```

### Step 10 — CLI command module (Red first)

Test: `tests/commands/test_arb_cmd.py`:
- `gz arb --help` returns help text mentioning each verb.
- `gz arb ruff --help` exits 0.
- `gz arb step --name foo -- echo hi` (patched subprocess) writes a step receipt.
- `gz arb validate` exits 0 when receipts dir is empty (prints "0 receipts validated").
- `gz arb advise` exits 0 on empty dir.
- Exit code 2 on ARB internal error (e.g., malformed config).
- `--json` flag produces valid JSON to stdout per cli.md contract.

Code: `src/gzkit/commands/arb.py`:
- Dispatcher functions: `arb_ruff_cmd`, `arb_step_cmd`, `arb_ty_cmd`, `arb_coverage_cmd`, `arb_validate_cmd`, `arb_advise_cmd`, `arb_patterns_cmd`.
- Each returns an integer exit code per the rule's 0/1/2 contract.
- Respects `--quiet`, `--verbose`, `--json`, `--plain` flags per cli.md.

Size budget: one module, ~250L max — at or under the 300-line class limit and well under the 600-line module limit.

### Step 11 — Parser registration (Red first)

Test: `tests/test_cli_parser.py` (or new `test_parser_arb.py`):
- `arb` is present in the `gz --help` subcommand list.
- `arb` expands to seven sub-verbs via `commands.choices["arb"]`.
- Each sub-verb has a help string and at least one example.

Code: Extend `src/gzkit/cli/parser_maintenance.py` with a new `_register_arb_parsers(commands)` helper called from `register_maintenance_parsers()`, OR create a dedicated `src/gzkit/cli/parser_arb.py` and wire it in `cli/parser.py`. Prefer the dedicated module if `parser_maintenance.py` is near its 600-line cap — current size is 657L (already over the soft limit), so a new `parser_arb.py` is the size-correct choice.

### Step 12 — Behave feature (Gate 4)

File: `features/arb.feature`:

```gherkin
Feature: ARB self-reporting middleware
  As an agent producing verification evidence
  I want to wrap QA commands in ARB receipts
  So that attestations can cite deterministic artifacts

  Scenario: Wrap a passing ruff run
    Given a clean temporary project
    When I run "uv run gz arb ruff src/gzkit/arb"
    Then the exit code is 0
    And a lint receipt exists under "artifacts/receipts/"
    And the receipt has schema "gzkit.arb.lint_receipt.v1"

  Scenario: Advise over recent receipts
    Given a temporary receipts directory with three mixed receipts
    When I run "uv run gz arb advise --limit 10"
    Then the exit code is 0
    And the output contains "ARB Advice"
```

File: `features/steps/arb_steps.py` — step implementations using `subprocess.run` and temporary directories per cross-platform.md.

### Step 13 — Docs (Gate 3 / Gate 5 runbook-code covenant)

- `docs/user/commands/arb.md` — command reference (description, verbs, flags, exit codes, examples) per cli.md heavy-lane contract.
- `docs/user/manpages/arb.md` — manpage form per cli.md contract.
- Update `docs/user/commands/index.md` to list `arb` in the verb index.
- Update `docs/user/runbook.md` to mention ARB in the verification flow — specifically in the heavy-lane attestation section where receipt IDs are required.
- Update `docs/user/concepts/workflow.md` only if the workflow doc currently claims ARB is in use.

### Step 14 — Rule correction

Update `.gzkit/rules/arb.md`:
- Bump `skill-version` equivalent → minor bump from the implicit v1.0 to v1.1 (per skill-surface-sync.md semver rules — this is a governance procedure change).
- Update "Last reviewed" to 2026-04-14.
- Add `gz arb patterns` to the command list (covers the new verb).
- Remove any references to `--file-issue` (out of scope).
- Keep the rest of the content — the concept section and exit codes were correct; only the verb availability was fictitious.

### Step 15 — Skill / surface-alignment

Per `.claude/rules/tool-skill-runbook-alignment.md` Invariant 1, every CLI tool must have at least one skill that wields it. Check whether a `gz-arb` skill is needed:
- If a skill exists anywhere that references `gz arb ruff/step/validate/advise`, no new skill needed.
- If not, create `.gzkit/skills/gz-arb/SKILL.md` with `gz_command: arb advise` (or similar) and a minimal operator moment ("summarize recent ARB receipts to tune agent defect rate"). Keep it tiny; this is invariant coverage, not a workflow.

Run `uv run gz agent sync control-surfaces` in Stage 5 to propagate all surface changes.

### Step 16 — Author OBPI brief decision sections

File: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-33-arb-analysis-pattern.md`.

Sections to add:
- **Comparison Evidence** (table with file:line anchors for all 7 ported files and the missing `gz arb` verb at commit `4700b623`).
- **Decision: Absorb** with rationale referencing (a) the forensic trace of the drift, (b) the subtraction test (ARB is not airline-specific), (c) the fail-closed attestation-enrichment requirement that cannot be met without this surface, (d) the missing CLI verb as a concrete Invariant-1 gap in the tool/skill/runbook alignment rule.
- **Implementation Summary** — files created, files modified, tests added, schema files, behave scenarios, docs updated, rule corrections.
- **Value Narrative** — before: vaporware rule, no receipts possible; after: real CLI, real receipts, attestation-enrichment fail-closed requirement becomes enforceable.
- **Key Proof** — exact commands the reviewer can run: `uv run gz arb --help`, `uv run gz arb ruff src/gzkit/arb`, `uv run gz arb validate`, `uv run gz arb advise`.
- **Evidence** — gates green, ARB receipt IDs for lint/typecheck/test (yes — eat our own dog food — the ADR closes out citing its own newly-created receipt surface).
- **Human Attestation** — filled in at Stage 4.
- **Closing Argument** — 2-3 paragraphs tying the drift, the forensic evidence, and the Absorb decision into the ADR's core infrastructure pattern absorption narrative.

## Critical Files to Modify or Create

**Create (package):**
- `src/gzkit/arb/__init__.py`
- `src/gzkit/arb/paths.py`
- `src/gzkit/arb/ruff_reporter.py`
- `src/gzkit/arb/step_reporter.py`
- `src/gzkit/arb/validator.py`
- `src/gzkit/arb/advisor.py`
- `src/gzkit/arb/patterns.py`

**Create (CLI + schema + tests + docs + behave):**
- `src/gzkit/commands/arb.py`
- `src/gzkit/cli/parser_arb.py`
- `data/schemas/arb_lint_receipt.schema.json`
- `data/schemas/arb_step_receipt.schema.json`
- `tests/arb/__init__.py`
- `tests/arb/test_paths.py`
- `tests/arb/test_ruff_reporter.py`
- `tests/arb/test_step_reporter.py`
- `tests/arb/test_validator.py`
- `tests/arb/test_advisor.py`
- `tests/arb/test_patterns.py`
- `tests/arb/test_schemas.py`
- `tests/commands/test_arb_cmd.py`
- `tests/test_parser_arb.py`
- `features/arb.feature`
- `features/steps/arb_steps.py`
- `docs/user/commands/arb.md`
- `docs/user/manpages/arb.md`

**Modify:**
- `src/gzkit/config.py` — add `ArbConfig` and wire into `ProjectConfig`
- `src/gzkit/cli/parser.py` (or wherever `register_maintenance_parsers` is called) — register the new `parser_arb` module
- `docs/user/commands/index.md` — add ARB entry
- `docs/user/runbook.md` — reference ARB in the heavy-lane attestation flow
- `.gzkit/rules/arb.md` — version bump, "Last reviewed" date, add `patterns` verb, remove `--file-issue` references
- `tests/test_config.py` — `ArbConfig` round-trip
- `docs/design/adr/pre-release/ADR-0.25.0-.../obpis/OBPI-0.25.0-33-arb-analysis-pattern.md` — brief completion

## Reusable gzkit Patterns

- `src/gzkit/config.py` — extends `ProjectConfig` with a frozen Pydantic section; follow `PathConfig` / `VendorConfig` as the template.
- `src/gzkit/core/models.py` — Pydantic `BaseModel` + `ConfigDict(frozen=True, extra="forbid")` + `Field(..., description=...)`.
- `src/gzkit/cli/parser_maintenance.py` — parser registration pattern (`commands.add_parser(...).set_defaults(func=...)` with `build_epilog` for examples); mirror for `parser_arb.py`.
- `src/gzkit/cli/helpers.py` — `add_dry_run_flag`, `add_json_flag`, `build_epilog` — reuse for ARB flags.
- `src/gzkit/commands/chores.py` / `drift.py` — command module structure (public dispatcher function per verb, returns `int`, handles `--json`/`--plain`).
- `tests/commands/test_chores.py` (or similar) — CLI smoke test pattern.
- `features/core_infrastructure.feature` + steps — behave scenario pattern for ADR-0.25.0 work.

## Verification

The pipeline's Stage 3 will run these in order. Every step must pass before Stage 4 ceremony.

**Baseline quality gates:**
```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run mkdocs build --strict
```

**REQ parity gate:**
```bash
uv run gz covers OBPI-0.25.0-33-arb-analysis-pattern --json
# Expected: summary.uncovered_reqs == 0
```

**Brief-specific verification (from OBPI-0.25.0-33-arb-analysis-pattern.md):**
```bash
test -d ../airlineops/src/opsdev/arb
test -f src/gzkit/commands/closeout_ceremony.py
rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-.../obpis/OBPI-0.25.0-33-arb-analysis-pattern.md
uv run gz test
uv run -m behave features/arb.feature
```

**Self-referential ARB dog-fooding (novel to this OBPI):**
```bash
# Once Steps 1-11 are complete, use the new surface to produce the attestation's own receipts:
uv run gz arb ruff src/gzkit/arb tests/arb src/gzkit/commands/arb.py
uv run gz arb step --name unittest -- uv run -m unittest tests.arb tests.commands.test_arb_cmd -v
uv run gz arb step --name typecheck -- uvx ty check src/gzkit/arb
uv run gz arb validate --limit 10
uv run gz arb advise --limit 10
```

The receipt IDs emitted by these runs are cited in the OBPI brief's Evidence section. ADR-0.25.0 closes out citing evidence from the capability it just absorbed — the first attestation in the repository that satisfies the attestation-enrichment rule honestly.

**End-to-end smoke:**
```bash
uv run gz arb --help
uv run gz arb ruff --help
uv run gz arb validate --help
uv run gz arb advise --help
```

All should exit 0 and show examples per cli.md contract.

## Risk and Open Questions

1. **`patterns.py` has a RULE_GUIDANCE dict** with opinionated advice strings. The port should keep the structure but may want to review the guidance text for gzkit-specific tone. Not a blocker.
2. **`jsonschema` dependency** — verify it's already in `pyproject.toml` (it's used by `validate_pkg/ledger_check.py`). If not, add it.
3. **Parser placement** — `parser_maintenance.py` is already at 657L (past the 600L soft limit). Creating `parser_arb.py` is the size-correct choice and avoids growing an already-large module.
4. **`patterns.py` CLI verb** — adding `gz arb patterns` means updating `.gzkit/rules/arb.md`. That's a minor rule change, version bump 1.0 → 1.1 per skill-surface-sync.md.
5. **Brief Allowed Paths** — Step 0 amends them. This is scope-honest: the brief under-scoped at authoring time because it assumed a Confirm decision.
6. **Pydantic conversion** — airlineops uses `@dataclass(frozen=True)`. Converting to `BaseModel(frozen=True, extra="forbid")` is mechanical but watch for fields like `top_rules: list[tuple[str, int]]` — Pydantic handles tuples but double-check serialization round-trip.

## Out of Scope (Explicitly Deferred)

- `gz arb tidy` pruning/retention — referenced in advice text but not implemented here.
- `gz arb ruff --file-issue` GitHub issue filing.
- Supabase sync.
- ARB schema v2 or extensions.
- Absorption of airlineops `patterns.py` RULE_GUIDANCE dict edits beyond the minimum required.
- Retrofitting prior attestations to cite real ARB receipts — those attestations stand as-is; forward attestations use the real surface.
