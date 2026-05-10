# OBPI-0.47.0-02 — OWASP chore runner

## Context

Mechanical analyzer floor for the OWASP Top 10:2025 scanner. Lands `.gzkit/chores/owasp-top10-2025-scan/` with: chore manifest (CHORE.md / README.md / acceptance.json), `runner.py` orchestrator, `visitors.py` (7 stdlib-AST `NodeVisitor` subclasses), `adapters.py` (chore-reuse for `dependency-currency` + `exceptions-and-logging-rationalization`). Imports OBPI-01 schema (`OwaspScanReport`/`OwaspFinding`) read-only. Heavy lane, sensitivity:security → extended Gate-5 walkthrough.

Brief: [OBPI-0.47.0-02](docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/obpis/OBPI-0.47.0-02-owasp-chore-runner.md). Parent ADR § Decision § Analyzer floor names every ruff `S`-rule and AST visitor.

## Confirmed precedents (reuse, don't reinvent)

- Sibling chore layout: `.gzkit/chores/dependency-currency/{CHORE.md, README.md, acceptance.json}` (3 files, no runner). Match this shape; the runner.py / visitors.py / adapters.py addition is new for this chore.
- Chore CLI verb: actual entrypoint is **`uv run gz chores run`** (plural), NOT `gz chore run` (brief REQ-10 wording is wrong). Fix REQ-10 wording during implementation; route as in-flight defect (≤1 line, single brief edit).
- Pydantic schema imports: `from gzkit.scan.models import OwaspScanReport, OwaspFinding` (OBPI-01 landed; available).
- Mapping data: `from gzkit.scan.mapping import load_mapping` reads `.gzkit/chores/owasp-top10-2025-scan/mapping.json` and validates against `mapping.schema.json`.
- Subprocess discipline: list-form, `shell=False`, `check=False` per `.gzkit/rules/cross-platform.md` (binding). REQ-09 grep-tests this.

## Creates these files

- `.gzkit/chores/owasp-top10-2025-scan/CHORE.md`
- `.gzkit/chores/owasp-top10-2025-scan/README.md`
- `.gzkit/chores/owasp-top10-2025-scan/acceptance.json`
- `.gzkit/chores/owasp-top10-2025-scan/runner.py`
- `.gzkit/chores/owasp-top10-2025-scan/visitors.py`
- `.gzkit/chores/owasp-top10-2025-scan/adapters.py`
- `.gzkit/chores/owasp-top10-2025-scan/proofs`
- `.gzkit/chores/owasp-top10-2025-scan/proofs/.gitkeep`
- `tests/scan/fixtures/sources`
- `tests/scan/test_owasp_chore_runner.py`
- `tests/scan/test_owasp_visitors.py`
- `tests/scan/test_owasp_adapters.py`
- `tests/scan/fixtures/sources/shell_true_positive.py`
- `tests/scan/fixtures/sources/shell_true_negative.py`
- `tests/scan/fixtures/sources/chmod_world_writable_positive.py`
- `tests/scan/fixtures/sources/chmod_world_writable_negative.py`
- `tests/scan/fixtures/sources/verify_false_positive.py`
- `tests/scan/fixtures/sources/verify_false_negative.py`
- `tests/scan/fixtures/sources/random_for_tokens_positive.py`
- `tests/scan/fixtures/sources/random_for_tokens_negative.py`
- `tests/scan/fixtures/sources/fstring_into_execute_positive.py`
- `tests/scan/fixtures/sources/fstring_into_execute_negative.py`
- `tests/scan/fixtures/sources/hardcoded_crypto_keys_positive.py`
- `tests/scan/fixtures/sources/hardcoded_crypto_keys_negative.py`
- `tests/scan/fixtures/sources/secrets_in_log_strings_positive.py`
- `tests/scan/fixtures/sources/secrets_in_log_strings_negative.py`

## Modifies these files (registry update + brief REQ-10 wording fix)

- `.gzkit/chores/registry.json` — append one entry for `owasp-top10-2025-scan` (slug, lane=heavy, version=1.0.0, allowNetwork=false). No reordering of existing entries.
- `docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/obpis/OBPI-0.47.0-02-owasp-chore-runner.md` — fix REQ-10 wording from "gz chore run" to "gz chores run" (plural; the actual registered verb).

## Implementation outline

### 1. AST visitors (`visitors.py`)

Seven `ast.NodeVisitor` subclasses, one per pattern. Each accumulates `OwaspFinding` instances bound to the visitor's category + rule_id. Module-level constants for each rule_id:

- `gzkit-ast-shell-true-literal` → A02
- `gzkit-ast-chmod-world-writable` → A02
- `gzkit-ast-requests-verify-false` → A02
- `gzkit-ast-random-for-tokens` → A04
- `gzkit-ast-fstring-into-execute` → A05
- `gzkit-ast-hardcoded-crypto-keys` → A04
- `gzkit-ast-secrets-in-log-strings` → A09

Each visitor traverses the AST; positive fixture must trigger ≥1 finding; negative fixture must trigger 0.

### 2. Adapters (`adapters.py`)

Two adapters reading existing chore proof outputs:

- `adapt_dependency_currency() → list[OwaspFinding]` — A03 findings with `source="chore-reused"`, `rule_id` carrying upstream chore's identifier.
- `adapt_exceptions_and_logging() → list[OwaspFinding]` — A09/A10 findings.

Both fail-soft: if upstream chore has no proof, return empty list (operator gets warning, not failure). REQ-08 covers `dependency-currency` round-trip.

### 3. Runner (`runner.py`)

Single `run(scope: Path) -> OwaspScanReport` entry point. Steps:

1. Load `mapping.json` via `gzkit.scan.mapping.load_mapping`.
2. Build ruff `S`-rule list from mapping (no hardcoded duplicate per REQ-01).
3. `subprocess.run(["uv", "run", "ruff", "check", "--select", ",".join(rules), "--output-format", "json", str(scope)], shell=False, check=False, capture_output=True)`. Parse JSON output → list[OwaspFinding] with `source="ruff-S"`.
4. For each Python file under scope: parse to AST, run all 7 visitors, accumulate findings.
5. Run adapters; merge findings.
6. Build `coverage` dict: A06 → `not-mechanical` (REQ-07), A07 → `not-applicable` (REQ-07 from OBPI-01 model), all other categories computed from per-category source presence + finding presence.
7. Assemble `OwaspScanReport`, validate via `model_validate`, write to `proofs/owasp-scan-report-<commit>.json`.

### 4. Chore manifest

- `CHORE.md` — overview, policy/guardrails, workflow, checklist, acceptance criteria, evidence commands. Match `dependency-currency/CHORE.md` shape.
- `README.md` — operator-facing rationale (~200 chars, like sibling chores).
- `acceptance.json` — exitCodeEquals checks for the verification commands.

### 5. Tests

- `test_owasp_visitors.py` — 7 visitors × (positive triggers, negative doesn't) = ~14 tests + REQs 01-05 covered with `@covers`.
- `test_owasp_adapters.py` — REQ-08 `dependency-currency` adapter round-trip test.
- `test_owasp_chore_runner.py` — REQ-06 (proof validates against schema), REQ-07 (A06 stays not-mechanical), REQ-09 (`grep` runner.py for `shell=True` returns no match).

### 6. Registry update

Append to `.gzkit/chores/registry.json` (single entry, no reordering):

```json
{
  "slug": "owasp-top10-2025-scan",
  "title": "OWASP Top 10:2025 Security Scan (stdlib-first analyzer floor)",
  "version": "1.0.0",
  "path": ".gzkit/chores/owasp-top10-2025-scan",
  "lane": "heavy"
}
```

## REQ → test coverage matrix

| REQ | Test |
|---|---|
| REQ-0.47.0-02-01 | `test_owasp_visitors.py::test_shell_true_detected` |
| REQ-0.47.0-02-02 | `test_owasp_visitors.py::test_chmod_world_writable_detected` |
| REQ-0.47.0-02-03 | `test_owasp_visitors.py::test_verify_false_detected` |
| REQ-0.47.0-02-04 | `test_owasp_visitors.py::test_random_for_tokens_detected` |
| REQ-0.47.0-02-05 | `test_owasp_visitors.py::test_fstring_into_execute_detected` |
| REQ-0.47.0-02-06 | `test_owasp_chore_runner.py::test_proof_validates_against_schema` |
| REQ-0.47.0-02-07 | `test_owasp_chore_runner.py::test_a06_never_graded_mechanically` |
| REQ-0.47.0-02-08 | `test_owasp_adapters.py::test_dependency_currency_adapter` |
| REQ-0.47.0-02-09 | `test_owasp_chore_runner.py::test_no_shell_true_in_runner` |

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan
uv run gz arb coverage run -m unittest discover -s tests/scan -t .
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
test -f .gzkit/chores/owasp-top10-2025-scan/CHORE.md
test -f .gzkit/chores/owasp-top10-2025-scan/runner.py
uv run gz chores show owasp-top10-2025-scan
# Smoke run (will dogfood gzkit itself; report lands in proofs/)
uv run gz chores run owasp-top10-2025-scan
```

## Out of scope (Denied Paths)

`src/gzkit/scan/{models,mapping}.py` (OBPI-01 read-only); `src/gzkit/cli/**` (OBPI-03); `.gzkit/skills/gz-owasp-scan/**` (OBPI-04); manpages / runbooks (OBPI-03/05); `pyproject.toml` (no new deps); `data/security_surfaces.json` (OBPI-05).
