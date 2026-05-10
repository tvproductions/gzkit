# OBPI-0.47.0-01 Implementation Plan

## Context

OBPI-0.47.0-01 is the foundational data-contract brief under ADR-0.47.0-owasp-top10-2025-scan: lands the Pydantic models (`OwaspScanReport`, `OwaspFinding`), a JSON-schema'd `mapping.json` binding A01:2025–A10:2025 to analyzer sources, and invariant tests. Heavy lane, sensitivity absent. Foundational — OBPIs 02 (chore runner), 03 (CLI), 04 (skill) all depend on this contract. No analyzer code, CLI, or skill content lands here.

Brief: [OBPI-0.47.0-01-owasp-data-model-and-mapping-schema.md](docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/obpis/OBPI-0.47.0-01-owasp-data-model-and-mapping-schema.md)
Parent ADR: [ADR-0.47.0-owasp-top10-2025-scan.md](docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/ADR-0.47.0-owasp-top10-2025-scan.md)

## Confirmed precedents (reuse, don't reinvent)

- **Pydantic pattern** — `BaseModel + ConfigDict(frozen=True, extra="forbid")` per `src/gzkit/lock_manager.py:21` and `.gzkit/rules/models.md` (binding).
- **JSON Schema infra** — `jsonschema>=4.26` already in `pyproject.toml`. Use `Draft202012Validator` per `src/gzkit/complexity/advisor/archetype_rules.py:130-136`. **No new dependency.**
- **Cross-platform path test** — `tests/governance/test_path_separator_portability.py:92-107` shape: `assertEqual(violations, [], msg=...)`.
- **Chore dir layout** — sibling chores have `CHORE.md` + `README.md` + `acceptance.json`. **OBPI-01 creates only `mapping.json` + `mapping.schema.json`**; the rest land in OBPI-02.
- **Greenfield confirmed** — `src/gzkit/scan/`, `tests/scan/`, `.gzkit/chores/owasp-top10-2025-scan/` all absent.

## CRITICAL CORRECTION — OWASP 2025 vs 2021 category names

The Phase-2 Plan subagent's `mapping.json` sketch regressed to OWASP **2021** category names (e.g. A02="Cryptographic Failures", A03="Injection", A06="Vulnerable Components", A10="SSRF"). These are wrong for our 2025 ADR — the regression is a textbook stochastic-vibing failure (anti-vibing binding claim 4). **Implementation must use OWASP 2025 names** per the ADR Decision section and the WebFetch result earlier in the design dialogue:

| Code | OWASP 2025 category name (canonical) |
|---|---|
| **A01** | Broken Access Control |
| **A02** | Security Misconfiguration |
| **A03** | Software Supply Chain Failures |
| **A04** | Cryptographic Failures |
| **A05** | Injection |
| **A06** | Insecure Design |
| **A07** | Authentication Failures |
| **A08** | Software or Data Integrity Failures |
| **A09** | Security Logging and Alerting Failures |
| **A10** | Mishandling of Exceptional Conditions |

The implementer MUST use these names when authoring `mapping.json`. The analyzer-source mapping (`source`, `ruff_rules`, `ast_visitors`, `reused_chores`) for each category follows the ADR Decision § A01–A10 table verbatim — that table is correct; only the agent's category-name strings drifted.

## Pydantic model design

Use the Phase-2 agent's model code sketch as the implementation basis — it's correct on Pydantic mechanics. Key design choices to preserve:

- **Path-as-posix via `field_validator`** (reactive, not transformative): `path: str` field rejects backslashes via `_path_posix` validator; `scanned_paths` field uses `_paths_posix` list-validator. Tests assert via `with self.assertRaises(ValidationError)` for backslash-bearing payloads + happy-path posix round-trip.
- **Zero-finding attestation = explicit `coverage_attestations: dict[str, bool]` field** (default `{}`). Justification: keeps `findings` semantically pure; JSON-readable; `extra="forbid"` already protects the field.
- **Three `@model_validator(mode="after")` methods**: `_check_a06_not_mechanical`, `_check_a07_not_applicable`, `_check_mechanical_floor`. Plus `_coverage_keys_complete` to enforce A01..A10 keyset.
- **Module-level constants** `_ALL_CATS` (frozenset), `_MECHANICAL_SOURCES` (frozenset).

## `mapping.json` schema (Draft 2020-12)

`mapping.schema.json` validates `owasp_year: const 2025` + `categories` object with `additionalProperties: false`, required keys `A01..A10`, each entry requires `category_name | source | ruff_rules | ast_visitors | reused_chores | coverage_baseline | notes`. `source` enum includes the four `OwaspSource` literals plus `judgment-only` and `not-applicable`. `ruff_rules` items match `^S[0-9]{3}$`.

Per-category content per ADR Decision § A01–A10 table:

| Cat | source | ruff_rules / ast_visitors / reused_chores | coverage_baseline |
|---|---|---|---|
| A01 | judgment-only | — | not-mechanical |
| A02 | stdlib-ast + judgment-only | AST: chmod-0o777, verify-False, shell-True-literal | partial-mechanical |
| A03 | chore-reused + stdlib-ast | reused: dependency-currency; AST: pip-install-subprocess | partial-mechanical |
| A04 | ruff-S + stdlib-ast | S324,S501-S509; AST: hardcoded-keys, random-for-tokens | mechanical |
| A05 | ruff-S + stdlib-ast | S608,S609,S301-S307,S605-S607; AST: f-string-into-execute | mechanical |
| A06 | judgment-only | — | not-mechanical |
| A07 | not-applicable | — | not-applicable |
| A08 | ruff-S + stdlib-ast + judgment-only | S301,S302,S506; AST: artifact-integrity-checks | partial-mechanical |
| A09 | chore-reused + stdlib-ast | reused: exceptions-and-logging-rationalization; AST: secrets-in-log-strings | partial-mechanical |
| A10 | chore-reused + ruff-S | reused: exceptions-and-logging-rationalization; ruff: S110,S112 | partial-mechanical |

`source` is a list-or-string in JSON (a category may have multiple analyzer families). Schema must permit either `string` or `array<enum>` — adjust the schema accordingly. (Phase-2 agent's schema only permitted single `enum`; widen to `oneOf: [{enum: ...}, {array of enum}]`.)

## Test fixtures (4 named JSON files)

- `tests/scan/fixtures/valid_minimal_report.json` — empty findings; coverage `not-mechanical` for A01-A06,A08-A10; A07=`not-applicable`. `commit` = 40-char zero string. Valid.
- `tests/scan/fixtures/invalid_a06_mechanical.json` — same as above but `coverage["A06"] = "mechanical"`. Must reject.
- `tests/scan/fixtures/invalid_a07_other.json` — `coverage["A07"] = "mechanical"`. Must reject.
- `tests/scan/fixtures/invalid_mechanical_floor.json` — `coverage["A04"] = "mechanical"`, no A04 findings, `coverage_attestations = {}`. Must reject.

## TDD ordering (RED → GREEN → REFACTOR)

1. Create scaffolding: `src/gzkit/scan/__init__.py` (empty), `tests/scan/__init__.py` (empty), `tests/scan/fixtures/` directory.
2. RED-1 → GREEN-1: `test_a06_must_be_not_mechanical` then minimal `models.py` with `_check_a06_not_mechanical`.
3. RED-2 → GREEN-2: `test_a07_must_be_not_applicable` then `_check_a07_not_applicable`.
4. RED-3 → GREEN-3: `test_mechanical_floor_invariant` then `_check_mechanical_floor` + `coverage_attestations` field. Add paired GREEN case (`coverage_attestations["A04"]=True` accepts).
5. RED-4 → GREEN-4: `test_round_trip_equality`.
6. RED-5 → GREEN-5: `test_path_serialization_posix` (Windows-separator regression).
7. RED-6 → GREEN-6: `test_mapping_validates_against_schema` then `mapping.schema.json` → `mapping.json` → `src/gzkit/scan/mapping.py` loader.
8. REFACTOR: extract module-level constants; verify `<=50 lines/function`, `<=600 lines/module` per pythonic.md.
9. Decorate every test with `@covers(REQ-0.47.0-01-NN)` per `.gzkit/rules/adr-audit.md`.

## REQ → test coverage matrix (1:1)

| REQ | Test method |
|---|---|
| REQ-0.47.0-01-01 | `test_owasp_mapping.py::test_mapping_validates_against_schema` |
| REQ-0.47.0-01-02 | `test_owasp_models.py::test_a06_must_be_not_mechanical` |
| REQ-0.47.0-01-03 | `test_owasp_models.py::test_mechanical_floor_invariant` |
| REQ-0.47.0-01-04 | `test_owasp_models.py::test_a07_must_be_not_applicable` |
| REQ-0.47.0-01-05 | `test_owasp_models.py::test_round_trip_equality` |
| REQ-0.47.0-01-06 | `test_owasp_models.py::test_path_serialization_posix` |

## Creates these files

- `src/gzkit/scan/__init__.py`
- `src/gzkit/scan/models.py`
- `src/gzkit/scan/mapping.py`
- `.gzkit/chores/owasp-top10-2025-scan/mapping.json`
- `.gzkit/chores/owasp-top10-2025-scan/mapping.schema.json`
- `tests/scan/__init__.py`
- `tests/scan/test_owasp_models.py`
- `tests/scan/test_owasp_mapping.py`
- `tests/scan/fixtures/valid_minimal_report.json`
- `tests/scan/fixtures/invalid_a06_mechanical.json`
- `tests/scan/fixtures/invalid_a07_other.json`
- `tests/scan/fixtures/invalid_mechanical_floor.json`

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan
uv run gz arb coverage run -m unittest discover -s tests/scan -t .
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents

# Brief-named spot checks
test -f src/gzkit/scan/models.py
test -f .gzkit/chores/owasp-top10-2025-scan/mapping.json
test -f .gzkit/chores/owasp-top10-2025-scan/mapping.schema.json
uv run python -c "import json, jsonschema; jsonschema.validate(json.load(open('.gzkit/chores/owasp-top10-2025-scan/mapping.json')), json.load(open('.gzkit/chores/owasp-top10-2025-scan/mapping.schema.json')))"

# Negative-path demo (REQ-02)
uv run python -c "
from gzkit.scan.models import OwaspScanReport
try:
    OwaspScanReport.model_validate_json(open('tests/scan/fixtures/invalid_a06_mechanical.json').read())
    raise SystemExit('FAIL: should have rejected A06=mechanical')
except Exception as e:
    print('OK: rejected -', type(e).__name__)
"
```

All six receipt artifacts (`arb-ruff-*`, `arb-step-typecheck-*`, `arb-step-unittest-*`, `arb-step-coverage-*`, `arb-step-mkdocs-*`) must be captured for the OBPI completion ceremony.

## Pipeline next step (after operator-approved implementation)

`uv run gz obpi pipeline OBPI-0.47.0-01` — runtime stages: implement → verify → ceremony → sync. Heavy lane forces Gate-5 human attestation.

## Out of scope (Denied Paths — enforced)

- `src/gzkit/cli/**` (OBPI-03)
- `.gzkit/chores/owasp-top10-2025-scan/runner*` (OBPI-02)
- `.gzkit/skills/gz-owasp-scan/**` (OBPI-04)
- `docs/user/manpages/**` (OBPI-03)
- runbooks (OBPI-03/05)
- `pyproject.toml`, `uv.lock` (no new deps)
