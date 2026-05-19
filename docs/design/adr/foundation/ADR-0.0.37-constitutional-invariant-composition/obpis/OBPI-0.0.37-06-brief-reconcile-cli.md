---
id: OBPI-0.0.37-06-brief-reconcile-cli
parent: ADR-0.0.37-constitutional-invariant-composition
item: 6
lane: Heavy
status: Draft
---

<!-- gz-validate-skip: brief-demo-section -->

# OBPI-0.0.37-06-brief-reconcile-cli: Brief Reconcile CLI

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #6 — "OBPI-0.0.37-06 — `gz brief reconcile <OBPI-ID> [--apply]` CLI verb (operator-runnable; `brief_reconciled` ledger event; `--apply` writes operator-attested amendments)"

**Status:** Draft

## Objective

Land the operator-runnable surface that wraps OBPI-05's engine: `gz brief reconcile <OBPI-ID>` emits a `brief_reconciled` ledger event on every run, and `gz brief reconcile <OBPI-ID> --apply --attestor "<name>"` writes operator-attested amendments back into the brief frontmatter (allowlist additions, REQ-count fixes, verb corrections).

## Lane

**Heavy** — New CLI verb (`gz brief reconcile`), new ledger event types (`brief_reconciled`, `brief_reconcile_drift_detected`), parser registration. CLI/runtime/schema surfaces.

## Allowed Paths

- `src/gzkit/commands/brief_reconcile.py` (new) — `gz brief reconcile` command implementation
- `src/gzkit/cli/parser_artifacts.py` (modify) — register `brief reconcile` verb
- `src/gzkit/governance/events.py` (modify) — register `brief_reconciled` and `brief_reconcile_drift_detected` event types
- `.gzkit/schemas/ledger_events.json` (modify) — schema definitions for the two new event types
- `tests/commands/test_brief_reconcile.py` (new) — CLI tests
- `docs/user/manpages/gz-brief.md` (new) — manpage per gate5-runbook-code-covenant
- `features/brief_reconcile.feature` (modify) — add CLI-level scenarios tagged `@REQ-0.0.37-06-*`; file created by OBPI-05
- `docs/user/runbook.md` (modify) — operator runbook entry: "When briefs drift: `gz brief reconcile <OBPI-ID>` then `--apply` after review"
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-06-brief-reconcile-cli.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/governance/brief_reconcile.py` (OBPI-05's engine — consume, do not modify)
- Pipeline gates — OBPI-07/08
- `src/gzkit/governance/trust_audits/__init__.py` (OBPI-05 owns the trust_audits-scope registration; this OBPI only consumes the engine)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz brief reconcile <OBPI-ID>` resolves the OBPI brief path via existing OBPI-id resolver (e.g. `src/gzkit/governance/briefs.py`), runs OBPI-05's `reconcile_brief`, prints the delta summary, and emits a `brief_reconciled` ledger event with payload `(brief_id, has_drift, allowlist_delta_count, verification_delta_count, req_count_delta, citation_delta_count)`.
2. REQUIREMENT: Exit code 0 when `has_drift` is False; exit code 3 when True. (Consistent with `gz validate --*` convention.)
3. REQUIREMENT: When drift is detected, an additional `brief_reconcile_drift_detected` event is emitted with the full per-dimension delta payload.
4. REQUIREMENT: `--apply` mode requires `--attestor "<name>"`. Without `--attestor`, `--apply` fails with argparse error "--apply requires --attestor". With `--attestor`, the CLI writes amendments to the brief: allowlist additions append to `## Allowed Paths`; REQ-count fixes update Acceptance Criteria; unresolved-verb amendments append a `## Tracked Defects` note (the CLI never silently rewrites verb references — that's an operator-judgment call). The applied amendments are recorded in a `brief_reconciled` ledger event with `applied: true` and the attestor name.
5. REQUIREMENT: `--dry-run` mode is the default for `--apply` previews (`--apply --dry-run` prints the would-be diff without writing). `--apply` without `--dry-run` is non-interactive write.
6. REQUIREMENT: `brief reconcile` verb registered in `parser_artifacts.py`; resolves via `gz brief reconcile --help`.
7. REQUIREMENT: The two new ledger event types registered in `.gzkit/schemas/ledger_events.json`. Schema-conformant: each event has id, name, schema, required-fields keys per the events schema convention.

> STOP-on-BLOCKERS: OBPI-05's engine and OBPI-04's BriefStructure must be landed.

## Discovery Checklist

**Parent ADR:**

- [ ] Quote ADR § Decision item #6 (CLI verb) verbatim
- [ ] ADR § Decision Rationale point 4 (five dimensions — the CLI surfaces them all)
- [ ] ADR § Consequences Negative #4 (operator-bandwidth-protection framing)

**Governance:**

- [ ] `.gzkit/rules/cli.md` — CLI verb registration conventions
- [ ] `.gzkit/rules/gate5-runbook-code-covenant.md` — manpage + runbook obligations
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` — every CLI verb must have at least one skill; check whether a skill for `brief reconcile` exists or needs scaffolding (forward-reference to a follow-on skill OBPI/GHI)

**Context (exemplars):**

- [ ] `src/gzkit/commands/attest.py` — example of an `--attestor`-requiring CLI command
- [ ] `src/gzkit/commands/specify_cmd.py` — example of `--apply` write mode + `--dry-run`
- [ ] `src/gzkit/governance/events.py` — event-registration pattern

**Prerequisites:**

- [ ] OBPI-04 + OBPI-05 landed
- [ ] `src/gzkit/cli/parser_artifacts.py` accepts new verb registrations

## Quality Gates

- [ ] Gate 1: CLI-verb paragraph quoted
- [ ] Gate 2: `test_brief_reconcile.py` covers default-mode (no drift / drift), `--apply` without `--attestor` (error), `--apply` with attestor (writes amendments + emits event); RGR followed
- [ ] Code Quality: lint + typecheck
- [ ] Gate 3: `docs/user/manpages/gz-brief.md` with NAME/SYNOPSIS/DESCRIPTION/OPTIONS/EXAMPLES (EXAMPLES section shows real `gz brief reconcile` output); runbook entry; mkdocs strict
- [ ] Gate 4: `features/brief_reconcile.feature` includes CLI-level scenarios tagged `@REQ-0.0.37-06-*`; behave passes
- [ ] Gate 5: Foundation-kind attestation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.commands.test_brief_reconcile -v
uv run mkdocs build --strict
uv run -m behave features/brief_reconcile.feature --tags=REQ-0.0.37-06

# REQ-01: verb registered, default-mode run
uv run gz brief reconcile --help
uv run gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli && echo "REQ-01 OK"

# REQ-04: --apply requires --attestor
uv run gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli --apply 2>&1 | rg -q "requires --attestor" && echo "REQ-04 OK"

# REQ-07: event types registered
uv run python -c "
import json
events_txt = open('.gzkit/schemas/ledger_events.json').read()
assert 'brief_reconciled' in events_txt and 'brief_reconcile_drift_detected' in events_txt
print('REQ-07 OK')
"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-06-01: `gz brief reconcile <OBPI-ID>` resolves the brief, runs the engine, prints delta summary, emits `brief_reconciled` ledger event; exits 0 on no-drift, 3 on drift
- [ ] REQ-0.0.37-06-02: When drift is detected, a `brief_reconcile_drift_detected` event is emitted with full per-dimension delta payload
- [ ] REQ-0.0.37-06-03: `gz brief reconcile <OBPI-ID> --apply` without `--attestor` exits with error message containing `--apply requires --attestor`
- [ ] REQ-0.0.37-06-04: `gz brief reconcile <OBPI-ID> --apply --attestor "<name>"` writes allowlist/REQ-count amendments to the brief and emits a `brief_reconciled` event with `applied: true` and the attestor name
- [ ] REQ-0.0.37-06-05: `--apply --dry-run` prints the would-be diff without writing the brief
- [ ] REQ-0.0.37-06-06: `brief reconcile` verb resolves via `gz brief reconcile --help`; verb is registered in `parser_artifacts.py`
- [ ] REQ-0.0.37-06-07: `brief_reconciled` and `brief_reconcile_drift_detected` event type schemas are present in `.gzkit/schemas/ledger_events.json` and pass the events-schema validator
- [ ] REQ-0.0.37-06-08: `docs/user/manpages/gz-brief.md` exists with all required manpage sections; EXAMPLES contains real CLI output (not placeholder)

## Completion Checklist

- [ ] All gates satisfied
- [ ] `gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli` reports zero drift

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: drift detection required reading the brief and the project tree manually. After: one CLI invocation surfaces all five drift dimensions with operator-attested amendment flow. -->

### Key Proof

<!-- Real CLI output: `gz brief reconcile OBPI-0.0.37-06-...` showing delta summary. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #495, GHI #485

## Human Attestation

- Attestor: `<name>`
- Attestation: per ADR-0.0.36 universal Gate 5; substantive text grounded in `--apply` write demonstration
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
