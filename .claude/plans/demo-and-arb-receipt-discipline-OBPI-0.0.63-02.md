# Heavy-Lane Plan — OBPI-0.0.63-02-demo-and-arb-receipt-discipline

**Parent ADR:** ADR-0.0.63-closeout-ceremony-runtime-engine-parity
**Lane:** Heavy
**Closes:** GHI #539 (multi-line demo split), GHI #540 (demos never executed); builds BI-1 classifier reused by OBPI-0.0.63-07 (GHI #550)

## Decision items implemented (quoted from parent ADR)

- #2: "Add demo-extraction re-execution preflight. Before emitting an ARB receipt from extracted demo content, re-execute the demo command and bind the receipt to the observed exit code and stdout SHA, not the T1 prose claim."
- #3: "Quote multi-line ARB commands. ARB receipt generators must accept multi-line command strings as a single quoted argv list, not split-on-newline."

## Scope boundary

Pure, unit-testable functions land in `src/gzkit/brief_commands.py` (BI-1 shared spine) + the delegation in `ceremony_data.py`. The closeout-walkthrough *wiring* of these functions is deferred to OBPI-0.0.63-01 (which restructures `closeout_ceremony.py` into the ledger-gated state machine — its natural home). End-to-end behavior is audited at ADR closeout via BI-1.

## Allowed Paths

- `src/gzkit/brief_commands.py` (NEW — shared module)
- `src/gzkit/commands/ceremony_data.py` (delegate `_commands_from_demo_sections`)
- `tests/test_brief_commands.py` (NEW)
- `tests/test_ceremony_demo_discovery.py` (RED-first)
- `tests/fixtures/ceremony_demos/multiline_demo.md` (NEW fixture)

## Phase 1: Implementation (Gates 1-4)

1. [x] Gate 1: parent ADR Decision items #2/#3 quoted into brief Implementation Summary
2. [x] RED: author `tests/test_brief_commands.py` + `tests/test_ceremony_demo_discovery.py` (14 tests) against REQ-01..04; observe failure (module missing + per-line shred)
3. [x] GREEN: implement `brief_commands.py` — `extract_fenced_commands` (quote-aware join, REQ-01), `is_shell_less_executable` (classifier, REQ-02 / BI-1), `reexecute_demo`+`DemoReceipt` (observed exit + stdout SHA + mismatch, REQ-03), `command_argv` (single-argv multiline, REQ-04)
4. [x] Refactor `ceremony_data._commands_from_demo_sections` to delegate per-block parsing to `extract_fenced_commands` (preserve registered-`gz`-verb validation)
5. [x] Gate 2: 14 tests GREEN; 25 existing ceremony tests still pass (no regression)
6. [x] Code Quality: `uv run gz lint` clean, `uvx ty check` clean
7. [x] Gate 3 (Docs): `uv run mkdocs build --strict` PASS, `gz validate --documents` PASS. No operator-facing CLI contract changed in this OBPI (functions not yet wired); operator-visible walkthrough doc updates land with the OBPI-01 wiring.
8. [x] Gate 4 (BDD): waived in `data/behave_coverage_waivers.json` with rationale — pure-Python library functions proven by unittest; no CLI surface to drive until OBPI-01 wires them; REQ-05 STRUCTURAL-FENCE (BI-1, closeout-audited).

## Phase 2: Gate 5 (Human Attestation) — MANDATORY

9. [ ] Present product-surface verification commands to human
10. [ ] STOP — wait for human to execute and attest
11. [ ] Record attestation in brief; then `gz obpi complete`

## Gate 5: Human Attestation (commands for verification)

```bash
uv run -m unittest tests.test_brief_commands tests.test_ceremony_demo_discovery -v
uv run python -c "from pathlib import Path; from gzkit.commands.ceremony_data import _commands_from_demo_sections; print(_commands_from_demo_sections([Path('tests/fixtures/ceremony_demos/multiline_demo.md')]))"
```

**Awaiting attestation.** Human executes the above and responds Completed / Completed — Partial / Dropped. DO NOT mark closed before attestation.
