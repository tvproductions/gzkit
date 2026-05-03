# ARB Middleware — Agent Self-Reporting Receipts

This document is the deep-dive reference for ARB (Agent Self-Reporting), the
QA middleware layer that wraps real verification steps (lint, type check,
tests, coverage, docs build) and emits structured JSON receipts used as
attestation evidence.

The **binding rules** — the em-dash enrichment pattern, the canonical-invocations
table, lane behavior (Lite warn / Heavy fail-closed), and the worked example —
live in `AGENTS.md` § Attestation. Read that section first; this file expands
the middleware surface the rules depend on.

Consolidation lineage: `.gzkit/rules/attestation-enrichment.md` (retired
2026-04-23, ADR-0.0.20 OBPI-03) → AGENTS.md § Attestation (binding) + this
file (deep-dive).

## ARB Middleware — Core Concept

ARB (Agent Self-Reporting) is a QA middleware layer that wraps real
verification steps (lint, type check, tests, coverage, docs build) and
emits structured JSON receipts. Every claim in the Canonical invocations
table in `AGENTS.md` § Attestation is a thin wrapper over a real tool;
the receipt is the deterministic evidence artifact.

ARB intercepts QA command execution and records:

- **Execution metadata** (timestamp, duration, environment)
- **Input/output** (command, arguments, exit code, stderr/stdout)
- **Structured findings** (linting violations, type errors, test failures)
- **Receipt artifacts** (JSON schema-validated, persistent)

This lets agents and humans:

1. Validate QA step outcomes programmatically
2. Aggregate recurring patterns across runs
3. File issues with deterministic evidence
4. Audit compliance and enforcement

## Available commands

The canonical invocations (binding) live in `AGENTS.md` § Attestation. The
commands below are the practical surface for producing and consuming receipts.

### Wrap a QA tool

```bash
uv run gz arb ruff
uv run gz arb ruff --fix
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb typecheck
uv run gz arb coverage run -m unittest discover -s tests -t .
```

### Validate and analyze receipts

```bash
uv run gz arb validate
uv run gz arb validate --limit 50
uv run gz arb advise
uv run gz arb advise --limit 10
```

### Extract recurring anti-patterns

```bash
uv run gz arb patterns
uv run gz arb patterns --compact
uv run gz arb patterns --json
```

## Receipt schema and storage

- **Lint receipt schema:** `data/schemas/arb_lint_receipt.schema.json`
  (`$id: gzkit.arb.lint_receipt.schema.json`)
- **Step receipt schema:** `data/schemas/arb_step_receipt.schema.json`
  (`$id: gzkit.arb.step_receipt.schema.json`)
- **Storage:** `artifacts/receipts/` (configurable via `arb.receipts_root` in `.gzkit.json`)

## Receipt-binding gate

Authored under [ADR-0.0.24](../design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/ADR-0.0.24-attestation-receipt-binding.md). The receipt-binding gate is the mechanical floor under the previously-narrative covenant in `AGENTS.md` § Attestation that "the citing agent must verify the receipt exists and status matches the claim." Verification is no longer narrative discipline; the gate fires automatically on every attestation surface.

### Invocation point

The gate is invoked pre-emission inside:

- `uv run gz obpi complete --attestation-text … --attestor …`
- `uv run gz adr emit-receipt … --attestor …`
- `uv run gz validate --attestation-receipts <text|@file> [--lane heavy|lite] [--kind foundation|feature]` — the standalone surface, also used by `gz check` and the OBPI pipeline's pre-flight checklist (`gz obpi precomplete`).

The gate parses the attestation string for inline IDs of shape
`arb-(ruff|step-<name>)-[a-f0-9]{32}`, reads each receipt from
`artifacts/receipts/<id>.json` (resolved via `gzkit.arb.paths.receipts_root()`),
and asserts each receipt:

1. Exists and parses as JSON conforming to its declared schema
   (`gzkit.arb.lint_receipt.v1` or `gzkit.arb.step_receipt.v1`).
2. Has `exit_status == 0`.
3. Matches the canonical claim category derived from its shape
   (`arb-ruff-*` → `lint`; `arb-step-<name>-*` → `<name>` keyed to
   `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py`) against
   the category named adjacent to the citation in the attestation text.

### `arb-meta-receipt-bind-…` family

When the gate ratifies an attestation it writes a self-attesting ledger
event of family `arb-meta-receipt-bind-<id>` — the gate's own evidence
trail. The meta-receipt records the cited receipt IDs, the per-ID
verification result (resolved / missing / status_mismatch /
claim_mismatch), the lane/kind axes the gate was evaluated under, and
the verdict it returned. Audits that need to verify "the gate fired on
attestation X" read the meta-receipt; the gate-fired condition is
itself observable, dated, and replayable from the ledger rather than
inferred from the absence of a defect.

The family is reserved in `CANONICAL_STEP_COMMANDS` under the same
extend-only rule as the rest of the table (`AGENTS.md` § Canonical
invocations) — adding a new gate-emitted family requires an ADR or OBPI
naming the surface; shrinking the table is forbidden.

### Failure modes

| Failure | Gate verdict | Lane behavior |
|---|---|---|
| `missing` — cited receipt file not present in `artifacts/receipts/` | Reject the attestation; meta-receipt records the missing IDs | Heavy / foundation = exit 3 (fail-closed); lite-non-foundation = warning, attestation still records |
| `status_mismatch` — receipt found but `exit_status != 0` | Reject the attestation; meta-receipt records the offending receipt + status | Heavy / foundation = exit 3; lite-non-foundation = warning |
| `claim_mismatch` — receipt category from shape does not match the category named adjacent to the citation (e.g. `lint:` adjacent to an `arb-step-typecheck-…` receipt) | Reject the attestation; meta-receipt records both categories | Heavy / foundation = exit 3; lite-non-foundation = warning |
| `no_ids` — attestation string contains zero `arb-…` citations | Reject on heavy/foundation; warn on lite-non-foundation | Heavy / foundation = exit 3 (the canonical "narrative-only" failure); lite-non-foundation = warning |

### Lane / kind matrix

The gate evaluates the same three-way OR predicate as the rest of the
attestation surface (foundation kind OR heavy lane OR security
sensitivity → fail-closed; otherwise warn). The matrix below is the
gate-verdict projection of `_requires_human_obpi_attestation` (see
`AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix for the
full predicate):

| Lane × Kind | Gate verdict on `missing` / `status_mismatch` / `claim_mismatch` / `no_ids` |
|---|---|
| Heavy / any kind | Exit 3 (fail-closed) |
| Any lane / `foundation` kind | Exit 3 (fail-closed) |
| Lite / `feature` kind / `sensitivity: security` | Exit 3 (fail-closed) |
| Lite / `feature` kind / no security sensitivity | Warning; attestation records narrative-only |

### Why a gate, not a reviewer checklist

ADR-0.0.24 § Alternatives Considered #1 records the rejection of "keep
advisory, raise visibility via reviewer checklist" — the Opus 4.7 system
card § 2.3.6.2 documents a model writing six memory files about a
verification rule and re-violating it. Discipline-only enforcement is
demonstrably insufficient at the current capability frontier; the gate
is the mechanical backstop under the narrative discipline.

### Cross-references

- `AGENTS.md` § Attestation — binding rules, canonical-invocations table, lane behavior bullets that cite this gate
- `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix — three-axis predicate the gate evaluates
- `docs/user/commands/validate.md` § `--attestation-receipts` — operator-facing CLI surface and EXAMPLES
- ADR-0.0.24-attestation-receipt-binding — Decision text, non-goals (no `--skip-receipt-binding`, no git pre-receive enforcement, no fail-closed on lite-non-foundation), and consequences

## Exit codes

- **0:** Command succeeded; receipt created
- **1:** Command failed; receipt created with error status
- **2:** ARB internal error

## Rationale

### Why receipts, not narrative

Narrative recall is post-hoc reconstruction: the reporting pathway and the
execution pathway are structurally separate (Lindsey et al. 2025 — the
math-explanation pathway and the math-execution pathway are distinct circuits;
a model can produce a plausible explanation of reasoning it did not actually
perform). The only faithful record of a QA step is the wrapped-command receipt.

### Why canonical commands

GHI #199 traces the class of failure where an ARB receipt reported exit 0
against `ty check .` while the governance gate (`gz typecheck` → `ty check src`)
reported exit 1. Parallel approximations (different scope, different target
tree, different flags) drift from the gate. `gz arb typecheck` (GHI #199)
wraps `uv run ty check src` — the same command `gz typecheck` and
`gz closeout` invoke.

### TDD RED evidence is not ARB-shaped (GHI #157)

ARB step receipts encode `exit_status=0` as success and `exit_status=1` as
failure. A TDD RED test is the inverse — a first-run failure is the *correct*
outcome. Until the dedicated RED/GREEN receipt stream lands (tracked under
`ADR-pool.tdd-receipt-stream`), Gate 2 TDD claims cite ARB receipts only for
the GREEN side (`arb-step-unittest-*`); the RED side is recorded as
per-increment observed-output pasted into the commit body or OBPI
verification section, under the same observed-evidence discipline that
governs routing-skill output claims.

### Eval-feedback-source trailer (ADR-0.0.26)

Rule edits that land as a result of the evaluation feedback loop carry an
`Eval-feedback-source: <event-id-or-artifact-path>` commit trailer alongside
the existing `Task:` / `Ceremony:` trailers. The trailer is validated by
`gz validate --commit-trailers`. See ADR-0.0.26 for the full loop doctrine.
