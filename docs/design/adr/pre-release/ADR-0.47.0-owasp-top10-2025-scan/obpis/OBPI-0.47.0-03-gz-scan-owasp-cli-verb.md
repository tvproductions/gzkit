---
id: OBPI-0.47.0-03-gz-scan-owasp-cli-verb
parent: ADR-0.47.0-owasp-top10-2025-scan
item: 3
lane: Heavy
sensitivity: security
status: Draft
---

# OBPI-0.47.0-03-gz-scan-owasp-cli-verb: gz scan owasp CLI verb

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/ADR-0.47.0-owasp-top10-2025-scan.md`
- **Checklist Item:** #3 — `OBPI-0.47.0-03-gz-scan-owasp-cli-verb: CLI verb gz scan owasp — argparse, scope resolution, --json, manpage`

**Status:** Draft

## Objective

Land the `gz scan owasp` CLI verb under a new `scan` namespace (future-proofs `gz scan cwe`, `gz scan secrets`, `gz scan license`). The verb resolves scope (`all` default, plus `touched`, `path <PATH>`, `adr <ADR-ID>`, `obpi <OBPI-ID>`), invokes the OBPI-02 chore, formats human or `--json` output, and applies the exit-code contract specified in the ADR Decision (`0` clean, `1` critical/high present, `2` config/IO error, `3` policy breach). Authors the manpage and the runbook + governance-runbook references that close the tool/skill/runbook alignment chain.

## Lane

**Heavy** — adds a new top-level CLI namespace (`scan`) and a verb (`gz scan owasp`) with a documented exit-code and `--json` contract. External tooling and CI gates may consume the contract.

> Sensitivity: `security`. The verb is the operator-facing entry point
> for the OWASP Top 10 scan; argparse parsing of operator-supplied paths
> (`gz scan owasp path <PATH>`, `--json`, scope-resolver flags) crosses
> the same input-validation boundary that `data/security_surfaces.json`
> categorizes as `subprocess_user_input` for sibling modules
> (`src/gzkit/utils.py`, `src/gzkit/git_sync.py`, etc.). Escalating
> sensitivity to `security` per `.gzkit/rules/security-sensitivity.md`
> § Invariant; OBPI-05 may register `src/gzkit/cli/parser_scan.py`
> in `data/security_surfaces.json` if dogfood findings warrant it.

## Allowed Paths

- `src/gzkit/cli/parser_scan.py` — new argparse subparser module (sibling to `parser_governance.py`, `parser_arb.py`)
- `src/gzkit/cli/parser.py` — register the `scan` subparser (one wiring edit)
- `src/gzkit/cli/main.py` — route the `scan owasp` dispatch (one wiring edit)
- `src/gzkit/scan/cli.py` — handler implementation (scope resolution, chore invocation, output formatting)
- `src/gzkit/scan/scope.py` — pure scope-resolver functions (`all`, `touched`, `path`, `adr`, `obpi`)
- `src/gzkit/scan/exit_codes.py` — `IntEnum` with the four documented exit codes
- `docs/user/manpages/scan-owasp.md` — manpage (existing convention drops `gz-` prefix; ADR's `gz-scan-owasp.md` path was speculative — see Defects)
- `docs/user/runbook.md` — operator runbook gains a `### Security scanning` section (one section append)
- `docs/governance/governance_runbook.md` — governance runbook gains a `### scan-as-gate` section (one section append)
- `tests/scan/test_gz_scan_owasp_cli.py` — argparse, scope resolution, exit code, `--json` shape tests
- `tests/scan/test_scope_resolver.py` — pure scope-resolver unit tests

## Denied Paths

- `src/gzkit/scan/models.py`, `src/gzkit/scan/mapping.py` — schema lives in OBPI-01 (read-only consumer here)
- `.gzkit/chores/owasp-top10-2025-scan/runner.py` — runner is OBPI-02; this brief invokes it, never mutates it
- `.gzkit/skills/gz-owasp-scan/**` — skill authoring belongs to OBPI-04
- `pyproject.toml`, `uv.lock` — no new deps
- `data/security_surfaces.json` — registry edit deferred to OBPI-05
- Any file under `docs/design/adr/` other than this OBPI brief and the parent ADR
- BDD scenarios — heavy-lane Gate 4 BDD belongs in OBPI-05 dogfood (where scenarios cover end-to-end run, not just argparse plumbing)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz scan` MUST be a noun-namespace subcommand, NOT a verb (matches `gz adr ...`, `gz obpi ...`, `gz agent ...` shape); rejected-alternative-5 in the parent ADR locks this.
2. REQUIREMENT: `gz scan owasp` MUST default scope to `all` (whole repo) when no scope flag is passed.
3. REQUIREMENT: `gz scan owasp` MUST accept these scope modes (mutually exclusive): `--scope all`, `--scope touched`, `--scope path PATH`, `--scope adr ADR-ID`, `--scope obpi OBPI-ID`.
4. REQUIREMENT: `gz scan owasp --json` MUST emit exactly `OwaspScanReport.model_dump_json(indent=2)` to stdout and nothing else; non-JSON noise on stdout is a fail-closed contract violation.
5. ALWAYS: Exit codes MUST be: `0` (no critical or high finding), `1` (critical or high finding present), `2` (config/IO error: chore not registered, scope path missing, ruff not callable), `3` (policy breach: heavy-lane gate with unresolved critical/high under `--enforce-gate`).
6. ALWAYS: Human-readable (non-`--json`) output MUST follow the `gz adr status` table-rendering precedent (Output Contract per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariant 3).
7. NEVER: The CLI handler MUST NOT re-implement any analyzer logic — every finding flows from the OBPI-02 chore's emitted proof JSON.
8. ALWAYS: The manpage at `docs/user/manpages/scan-owasp.md` MUST include an `EXAMPLES` section showing real CLI output (Gate-5 runbook-code covenant; placeholder examples are fail-closed).
9. ALWAYS: `gz cli audit` MUST recognize `gz scan owasp` after this brief (registration into the CLI audit registry; failure is a fail-closed defect per `.gzkit/rules/governance-core.md` § Operator-doc verb resolution).
10. ALWAYS: The runbook + governance-runbook references MUST resolve to a registered parser verb (`gz validate --cli-alignment` exit 0).

> STOP-on-BLOCKERS: if `gz cli audit` does not exist as a CLI verb, halt and report.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote verbatim into Implementation Summary:** "New verb `gz scan owasp` under a new `scan` namespace (future-proofs for `gz scan cwe`, `gz scan secrets`, `gz scan license`). Default scope mode: `all` (whole repo). Additional scope modes: `touched`, `path <PATH>`, `adr <ADR-ID>`, `obpi <OBPI-ID>`. `--json` flag emits `OwaspScanReport` to stdout for machine consumers. Default exit codes: `0` (no critical/high), `1` (critical or high finding present), `2` (config/IO error), `3` (policy breach, e.g., heavy-lane gate with unresolved critical/high). Manpage at `docs/user/manpages/gz-scan-owasp.md` with EXAMPLES section showing real CLI output (Gate 5 runbook-code covenant)."
- [ ] Parent ADR § Alternatives Considered #5 — single-word vs two-word verb shape.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` — three invariants for tool↔skill↔runbook coherence.
- [ ] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution — `gz validate --cli-alignment` is fail-closed.
- [ ] `.gzkit/rules/gate5-runbook-code-covenant.md` — manpage EXAMPLES must be real output.
- [ ] `.gzkit/rules/cross-platform.md` — argparse path handling via `pathlib.Path`.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.47.0-01 (schema) and OBPI-0.47.0-02 (chore) have landed and are passing.
- [ ] `src/gzkit/cli/parser.py` exists; `parser_governance.py`, `parser_arb.py` exist as siblings (this brief follows their convention).
- [ ] `gz cli audit` is a registered verb.
- [ ] `docs/user/manpages/` exists and uses the unprefixed naming convention (`adr-audit-check.md`, `adr-emit-receipt.md`).

**Existing Code (understand current state):**

- [ ] `src/gzkit/cli/parser_governance.py` — read for subparser-creation pattern.
- [ ] `src/gzkit/cli/parser_arb.py` — read for noun-namespace convention.
- [ ] `docs/user/manpages/adr-audit-check.md` — manpage shape + EXAMPLES section convention.
- [ ] `docs/user/runbook.md` — section header conventions for the new `### Security scanning` block.

## Quality Gates

### Gate 1: ADR

- [ ] Decision quote in Implementation Summary
- [ ] Manpage path matches existing convention (`docs/user/manpages/scan-owasp.md`); ADR's `gz-scan-owasp.md` was speculative and is reconciled in the brief's Tracked Defects with a path-correction note routed back into the ADR if needed

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Argparse parses each scope mode + rejects mutually-exclusive combinations
- [ ] `--json` output validates as `OwaspScanReport`
- [ ] Exit code 0 / 1 / 2 / 3 each tested with fixture input
- [ ] `uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan` passes

### Code Quality

- [ ] `uv run gz arb ruff` clean
- [ ] `uv run gz arb typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
- [ ] `gz cli audit` recognizes `gz scan owasp` (manpage + index parity)
- [ ] `gz validate --cli-alignment` exit 0 (runbook references resolve)

### Gate 4: BDD (Heavy)

- [ ] N/A — argparse plumbing is unit-tested; end-to-end `gz scan owasp` run lives in OBPI-05 BDD

### Gate 5: Human (Heavy + Security)

- [ ] Heightened walkthrough; `arb-step-security-scan-*` receipt confirmed.

## Verification

```bash
uv run gz validate --documents
uv run gz validate --briefs
uv run gz validate --cli-alignment
uv run gz cli audit
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# Specific verification for this OBPI
gz scan owasp --help
gz scan owasp --scope all --json | head -20
test -f docs/user/manpages/scan-owasp.md
```

## Demo

```bash
# Default scope is `all`; clean repo exits 0
gz scan owasp
echo "exit: $?"  # expect 0 on clean dogfood

# JSON contract for machine consumers
gz scan owasp --scope all --json | uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); import json; from gzkit.scan.models import OwaspScanReport; report = OwaspScanReport.model_validate_json(sys.stdin.read()); print(f'A06: {report.coverage[\"A06\"]}; findings: {len(report.findings)}')"

# Scoped run against one path
gz scan owasp --scope path src/gzkit/utils.py
```

## Acceptance Criteria

- [ ] REQ-0.47.0-03-01: Given `gz scan owasp --help`, when invoked, then the help text lists each scope mode (`all`, `touched`, `path`, `adr`, `obpi`) and the four documented exit codes; `tests/scan/test_gz_scan_owasp_cli.py::test_help_lists_scopes_and_exit_codes` covers.
- [ ] REQ-0.47.0-03-02: Given `gz scan owasp --scope all --json` against a clean fixture repo, when invoked, then stdout parses cleanly via `OwaspScanReport.model_validate_json` and exit code is `0`; `tests/scan/test_gz_scan_owasp_cli.py::test_json_output_is_valid_report` covers.
- [ ] REQ-0.47.0-03-03: Given `gz scan owasp` against a fixture with a critical finding, when invoked, then exit code is `1`; `tests/scan/test_gz_scan_owasp_cli.py::test_exit_1_on_critical_finding` covers.
- [ ] REQ-0.47.0-03-04: Given `gz scan owasp --scope path /nonexistent`, when invoked, then exit code is `2` and stderr names the missing path; `tests/scan/test_gz_scan_owasp_cli.py::test_exit_2_on_io_error` covers.
- [ ] REQ-0.47.0-03-05: Given `gz scan owasp --scope all --scope touched` (mutually exclusive), when invoked, then argparse rejects with exit code `2`; `tests/scan/test_gz_scan_owasp_cli.py::test_mutually_exclusive_scope_modes` covers.
- [ ] REQ-0.47.0-03-06: Given `gz cli audit`, when invoked after this brief, then `gz scan owasp` is listed and the manpage `docs/user/manpages/scan-owasp.md` exists; `tests/scan/test_gz_scan_owasp_cli.py::test_cli_audit_registration` covers.
- [ ] REQ-0.47.0-03-07: Given `gz validate --cli-alignment`, when invoked, then runbook `gz scan owasp` references resolve and exit is `0`; `tests/scan/test_gz_scan_owasp_cli.py::test_cli_alignment_validator_passes` covers.
- [ ] REQ-0.47.0-03-08: Given the manpage `docs/user/manpages/scan-owasp.md`, when read, then the `EXAMPLES` section contains real CLI output (no `<placeholder>` strings, no `# example output` stubs); `tests/scan/test_gz_scan_owasp_cli.py::test_manpage_examples_are_real` covers.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Decision quote present; manpage convention reconciled
- [ ] **Gate 2 (TDD):** Eight REQ-derived tests pass; coverage receipt captured
- [ ] **Code Quality:** `arb-ruff-*`, `arb-step-typecheck-*` receipts captured
- [ ] **Value Narrative:** Operators have a single-command entry to the OWASP floor
- [ ] **Key Proof:** `gz scan owasp --json` round-trips through OBPI-01's schema
- [ ] **OBPI Acceptance:** Human attestation recorded (heavy + security)

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded; Decision-quote present in Implementation Summary

### Gate 2 (TDD — Red-Green-Refactor)

```text
# arb-step-unittest-<sha>     (uv run -m unittest -q tests/scan)
# arb-step-coverage-<sha>     (coverage discover -s tests/scan)
```

### Code Quality

```text
# arb-ruff-<sha>
# arb-step-typecheck-<sha>
```

### Gate 3 (Docs)

```text
# arb-step-mkdocs-<sha>
# gz cli audit clean
# gz validate --cli-alignment exit 0
```

### Gate 4 (BDD)

```text
# N/A in this brief
```

### Gate 5 (Human)

```text
# arb-step-security-scan-<sha> (sensitivity:security heightened walkthrough)
# Attestation text recorded at completion. Receipt via `gz adr emit-receipt`.
```

### Value Narrative

Before this OBPI: the OWASP analyzer floor exists as a chore (OBPI-02) but only chore-runner regulars know how to invoke it. After this OBPI: any operator types `gz scan owasp` and gets a Top-10 report. CI gates can consume `--json` and key on exit code. The `scan` namespace is shaped so future siblings (`cwe`, `secrets`, `license`) ship without restructuring.

### Key Proof

`gz scan owasp --json | uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from gzkit.scan.models import OwaspScanReport; OwaspScanReport.model_validate_json(sys.stdin.read())"` returns 0 — the CLI's machine contract round-trips through OBPI-01's schema.

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- The parent ADR's Decision § CLI surface specifies the manpage path as `docs/user/manpages/gz-scan-owasp.md`, but the existing convention drops the `gz-` prefix (`adr-audit-check.md`, `obpi-complete.md`). This brief uses `docs/user/manpages/scan-owasp.md` (convention-aligned) and notes the path drift as a low-impact ADR-text correction; if operator review prefers the ADR text be authoritative, file a single-line ADR amendment in OBPI-05 closeout.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
