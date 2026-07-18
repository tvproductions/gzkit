---
id: OBPI-0.0.37-06-brief-reconcile-cli
parent: ADR-0.0.37-constitutional-invariant-composition
item: 6
lane: Heavy
status: Completed
---

<!-- gz-validate-skip: brief-demo-section -->

# OBPI-0.0.37-06-brief-reconcile-cli: Brief Reconcile CLI

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #6 — "OBPI-0.0.37-06 — `gz brief reconcile <OBPI-ID> [--apply]` CLI verb (operator-runnable; `brief_reconciled` ledger event; `--apply` writes operator-attested amendments)"

**Status:** Completed

## Objective

<!-- gz-validate-skip: command-shape -->
Land the operator-runnable surface that wraps OBPI-05's engine: `gz brief reconcile <OBPI-ID>` emits a `brief_reconciled` ledger event on every run, and `gz brief reconcile <OBPI-ID> --apply --attestor "<name>"` writes operator-attested amendments back into the brief frontmatter (allowlist additions, REQ-count fixes, verb corrections).

## Lane

**Heavy** — New CLI verb, new ledger event types (`brief_reconciled`, `brief_reconcile_drift_detected`), parser registration. CLI/runtime/schema surfaces.
<!-- gz-validate-skip: command-shape -->
Forward-reference verb introduced by this OBPI: `gz brief reconcile`.

## Allowed Paths

> Allowlist amendments (operator-attested 2026-06-05 / 2026-06-06): event-type
> registration and its coupled validators span more files than the original
> draft named — event models, factories, the enforced schema, the handler-waiver
> registry, the command-shape suggestion hook, and the doc/skill surfaces every
> new CLI verb obliges. Each entry below is the operator-approved real surface.

- `src/gzkit/commands/brief_reconcile.py` **CREATE** (new) — command implementation
- `src/gzkit/cli/parser_artifacts.py` (modify) — register the brief reconcile verb
- `src/gzkit/events.py` (modify) — typed event models + TypedLedgerEvent union entries
- `src/gzkit/ledger_events.py` (modify) — event factory functions
- `src/gzkit/governance/events.py` (modify) — emit helpers
- `src/gzkit/schemas/ledger.json` (modify) — enforced event schema entries
- `src/gzkit/governance/trust_audits/events.py` (modify) — NO_GRAPH_IMPACT handler waivers
- `src/gzkit/hooks/obpi.py` (modify) — command-shape suggestion ordering (new verb shifted the truncated list; coupled fix)
- `src/gzkit/cli/__init__.py` (consume) — imported by REQ tests
- `src/gzkit/config.py` (consume) — imported by REQ tests
- `src/gzkit/ledger.py` (consume) — imported by REQ tests
- `src/gzkit/traceability.py` (consume) — covers import in REQ tests
- `.gzkit/schemas/ledger_events.json` (modify) — documentary schema copy
- `.gzkit/skills/gz-brief-reconcile/SKILL.md` **CREATE** (new) — wielding skill (Invariant 1)
- `.gzkit/skills/gz-governance/SKILL.md` (modify) — route brief reconcile under the governance router
- `tests/commands/test_brief_reconcile.py` **CREATE** (new) — CLI tests
- `tests/test_schemas.py` (modify) — register the two models in the schema-alignment registry
- `docs/user/manpages/brief-reconcile.md` **CREATE** (new) — command manpage
- `docs/user/manpages/index.md` (modify) — manpage index entry
- `docs/user/skills/gz-brief-reconcile.md` **CREATE** (new) — skill manpage
- `docs/user/skills/index.md` (modify) — skill index entry
- `docs/user/runbook.md` (modify) — operator runbook drift-control entry
- `docs/governance/governance_runbook.md` (modify) — governance runbook entry
- `features/brief_reconcile.feature` (modify) — CLI scenarios tagged REQ-0.0.37-06
- `config/doc-coverage.json` (modify) — per-command documentation-obligation manifest
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-06-brief-reconcile-cli.md` (this brief)
- Generated artifacts (do not hand-edit): vendor skill mirrors under `.claude/`, `.agents/`, `.github/` and pkg copies under `src/gzkit/skills/` (via `gz agent sync control-surfaces`); `data/distribution_baseline_manifest.json` (via `gz validate --distribution --regenerate`); `AGENTS.md` control-surface timestamp; `.gzkit/ledger.jsonl` append-only events; `.gzkit/locks/` runtime lock state

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/governance/brief_reconcile.py` (OBPI-05's engine — consume, do not modify)
- Pipeline gates — OBPI-07/08
- `src/gzkit/governance/trust_audits/__init__.py` (OBPI-05 owns the trust_audits-scope registration; this OBPI only consumes the engine)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- gz-validate-skip: command-shape -->
1. REQUIREMENT: `gz brief reconcile <OBPI-ID>` resolves the OBPI brief path via existing OBPI-id resolver (e.g. `src/gzkit/governance/briefs.py`), runs OBPI-05's `reconcile_brief`, prints the delta summary, and emits a `brief_reconciled` ledger event with payload `(brief_id, has_drift, allowlist_delta_count, verification_delta_count, req_count_delta, citation_delta_count)`.
2. REQUIREMENT: Exit code 0 when `has_drift` is False; exit code 3 when True. (Consistent with `gz validate --*` convention.)
3. REQUIREMENT: When drift is detected, an additional `brief_reconcile_drift_detected` event is emitted with the full per-dimension delta payload.
4. REQUIREMENT: `--apply` mode requires `--attestor "<name>"`. Without `--attestor`, `--apply` fails with argparse error "--apply requires --attestor". With `--attestor`, the CLI writes amendments to the brief: allowlist additions append to `## Allowed Paths`; REQ-count fixes update Acceptance Criteria; unresolved-verb amendments append a `## Tracked Defects` note (the CLI never silently rewrites verb references — that's an operator-judgment call). The applied amendments are recorded in a `brief_reconciled` ledger event with `applied: true` and the attestor name.
5. REQUIREMENT: `--dry-run` mode is the default for `--apply` previews (`--apply --dry-run` prints the would-be diff without writing). `--apply` without `--dry-run` is non-interactive write.
<!-- gz-validate-skip: command-shape -->
6. REQUIREMENT: `brief reconcile` verb registered in `parser_artifacts.py`; resolves via `gz brief reconcile --help`.
7. REQUIREMENT: The two new ledger event types registered in the enforced ledger schema and the documentary copy. Schema-conformant: each event declares required fields and property types per the events schema convention, and round-trips through the typed-event discriminated union.
8. REQUIREMENT: A command manpage exists with NAME/SYNOPSIS/DESCRIPTION/OPTIONS/EXAMPLES sections, where EXAMPLES shows real CLI output; the verb is declared in the per-command doc-coverage manifest with a wielding skill (Invariant 1).

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

**Existing Code (understand current state):**

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
<!-- gz-validate-skip: command-shape -->
- [ ] Gate 3: `docs/user/manpages/gz-brief.md` with NAME/SYNOPSIS/DESCRIPTION/OPTIONS/EXAMPLES (EXAMPLES section shows real `gz brief reconcile` output); runbook entry; mkdocs strict
- [ ] Gate 4: `features/brief_reconcile.feature` includes CLI-level scenarios tagged `@REQ-0.0.37-06-*`; behave passes
- [ ] Gate 5: Foundation-kind attestation

## Verification

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.commands.test_brief_reconcile -v
uv run mkdocs build --strict
uv run -m behave features/brief_reconcile.feature --tags=REQ-0.0.37-06

# REQ-01: verb registered, default-mode run
uv run gz brief reconcile --help
uv run gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli

# REQ-04: --apply requires --attestor
uv run gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli --apply

# REQ-07: event types registered
uv run python -c "
import json
events_txt = open('.gzkit/schemas/ledger_events.json').read()
assert 'brief_reconciled' in events_txt and 'brief_reconcile_drift_detected' in events_txt
print('REQ-07 OK')
"
```

## Acceptance Criteria

<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.37-06-01 [behavior]: `gz brief reconcile <OBPI-ID>` resolves the brief, runs the engine, prints delta summary, emits `brief_reconciled` ledger event; exits 0 on no-drift, 3 on drift
- [ ] REQ-0.0.37-06-02 [behavior]: When drift is detected, a `brief_reconcile_drift_detected` event is emitted with full per-dimension delta payload
<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.37-06-03 [behavior]: `gz brief reconcile <OBPI-ID> --apply` without `--attestor` exits with error message containing `--apply requires --attestor`
<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.37-06-04 [behavior]: `gz brief reconcile <OBPI-ID> --apply --attestor "<name>"` writes allowlist/REQ-count amendments to the brief and emits a `brief_reconciled` event with `applied: true` and the attestor name
- [ ] REQ-0.0.37-06-05 [behavior]: `--apply --dry-run` prints the would-be diff without writing the brief
<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.37-06-06 [behavior]: `brief reconcile` verb resolves via `gz brief reconcile --help`; verb is registered in `parser_artifacts.py`
- [ ] REQ-0.0.37-06-07 [behavior]: `brief_reconciled` and `brief_reconcile_drift_detected` event type schemas are present in the enforced `src/gzkit/schemas/ledger.json` (and the documentary `.gzkit/schemas/ledger_events.json`) and pass the events-schema validator
<!-- gz-validate-skip: command-shape -->
- [ ] REQ-0.0.37-06-08 [behavior]: `docs/user/manpages/brief-reconcile.md` exists with all required manpage sections; EXAMPLES contains real CLI output (not placeholder)

## Completion Checklist

- [ ] All gates satisfied
<!-- gz-validate-skip: command-shape -->
- [ ] `gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli` reports zero drift

## Evidence

```text
# Per-gate receipts (arb)
arb-ruff-f7b925da190b49358e26c6f12d8d8e6b           ruff       exit 0
arb-step-typecheck-ec7db062f1374908bd867ff6823442f9 ty         exit 0
arb-step-unittest-a4f83dff2be6407ab47ca7333d38f4bc  unittest   exit 0 (5904 tests)
arb-step-mkdocs-b315d800da0c4173a32a0fc514239610    mkdocs     exit 0 (--strict)
behave: 328 scenarios passed, 0 failed (24 @wip skipped)
```

### Value Narrative

Before: detecting whether an OBPI brief had drifted from project reality (stale
allowlist, dead discovery paths, unregistered verbs, REQ/criteria mismatch,
missing citations) required reading the brief and walking the tree by hand —
exactly the silent drift invariant CIC-2 names. After: `gz brief reconcile
<OBPI-ID>` surfaces all five dimensions in one run with exit-3-on-drift, ledger
receipts on every run, and an operator-attested `--apply` amendment path. The
verb was dogfooded against its own brief, which now reports zero drift.

### Key Proof


uv run gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli --json -> has_drift:false, exit 0

### Implementation Summary


- Files created/modified: `src/gzkit/commands/brief_reconcile.py` (new command);
  `src/gzkit/cli/parser_artifacts.py` (verb registration); `src/gzkit/events.py`
  + `src/gzkit/ledger_events.py` + `src/gzkit/governance/events.py` (two event
  types: typed models, factories, emit helpers); `src/gzkit/schemas/ledger.json`
  + `.gzkit/schemas/ledger_events.json` (schema entries);
  `src/gzkit/governance/trust_audits/events.py` (NO_GRAPH_IMPACT waivers);
  `src/gzkit/hooks/obpi.py` (command-shape suggestion ordering — coupled fix);
  `config/doc-coverage.json`, `docs/user/manpages/brief-reconcile.md` + index,
  `docs/user/skills/gz-brief-reconcile.md` + index, runbook + governance_runbook
  entries; `.gzkit/skills/gz-brief-reconcile/SKILL.md` + governance router;
  `tests/test_schemas.py` (model registry).
- Tests added: `tests/commands/test_brief_reconcile.py` (8 tests, @covers
  REQ-0.0.37-06-01..07); `features/brief_reconcile.feature` (@REQ-0.0.37-06-*
  CLI scenarios, @wip per file convention).
- Date completed: 2026-06-06
- Attestation status: awaiting Gate 5 (foundation-kind, heavy lane)
- Defects noted: REQ-08 (manpage) is a SUPPORT-kind doc REQ witnessed by the
  doc-coverage manifest + `gz cli audit`, not a `@covers` unit test.

## Tracked Defects

- GHI #495, GHI #485

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed -- gz brief reconcile lands the CIC-2 operator surface; zero drift on its own brief (dogfooded), cli-audit 107/107, behave 0-failed. Receipts: arb-ruff-26a2f6c11bae4542a6ebfe6501c2f183, arb-step-typecheck-26de2b9dbaf14e29a0a054849af208e9, arb-step-unittest-492af29593284047a0d60fa28ae5a8ac.
- Date: 2026-06-06

---

**Brief Status:** Draft

**Date Completed:** 2026-06-06

**Evidence Hash:** -
