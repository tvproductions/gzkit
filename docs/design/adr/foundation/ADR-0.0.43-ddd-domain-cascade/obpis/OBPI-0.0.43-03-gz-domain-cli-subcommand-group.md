---
id: OBPI-0.0.43-03-gz-domain-cli-subcommand-group
parent: ADR-0.0.43-ddd-domain-cascade
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.43-03-gz-domain-cli-subcommand-group: gz domain CLI subcommand group

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #3 — "gz domain CLI subcommand group — `init` / `list` / `status` / `show` / `regenerate` verbs; structured table + `--json` output forms; idempotent `regenerate` with diff summary."

**Status:** Draft

## Objective

Land the `gz domain` CLI subcommand group: `init` (scaffold a DM), `list` (enumerate DMs), `status` (DM coverage vs PRD-declared BCs), `show` (render one BC's cascade), and `regenerate` (rebuild Layer-3 derived views). Every verb supports table and `--json` output. `regenerate` is idempotent, atomic, with `--check` dry-run.

## Lane

**Heavy** — new top-level CLI verb group with five subcommands and manpages.

## Allowed Paths

- `src/gzkit/cli/domain.py` — NEW; subcommand parser registration and dispatch
- `src/gzkit/domain/__init__.py` — NEW package
- `src/gzkit/domain/registry.py` — NEW; reads PRD § 2.2 + DM files into cascade view
- `src/gzkit/domain/regenerator.py` — NEW; rebuilds Layer-3 views
- `src/gzkit/domain/init.py` — NEW; scaffolds a DM
- `src/gzkit/domain/renderers.py` — NEW; table + JSON renderers
- `docs/user/manpages/domain-init.md` — NEW
- `docs/user/manpages/domain-list.md` — NEW
- `docs/user/manpages/domain-status.md` — NEW
- `docs/user/manpages/domain-show.md` — NEW
- `docs/user/manpages/domain-regenerate.md` — NEW
- `tests/cli/test_domain_*.py` — NEW (one per verb)

## Denied Paths

- `src/gzkit/governance/domain_models.py` — OBPI-01 / OBPI-02 (consume only)
- `src/gzkit/schemas/**` — OBPI-01 / 02 / 04 / 07
- `src/gzkit/governance/trust_audits/domain_cascade.py` — OBPI-06 (CLI may invoke validator but never implement it)
- `src/gzkit/governance/legacy_mapping.py` — OBPI-07
- `src/gzkit/governance/cascade_import_check.py` — OBPI-11
- `src/gzkit/ledger/**` — OBPI-05 (CLI may emit via existing API; no new event-type authoring)
- `.gzkit/skills/**` — OBPI-08 / 09 / 10
- `docs/design/prd/**` — OBPI-13
- `docs/design/domain/DM-*.md` content — only `gz domain init` scaffolder writes these
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (`gz domain init <bc-slug>`).** Scaffolds `docs/design/domain/DM-<bc-slug>.md` from template. Refuses exit 3 if (a) BC slug unknown to PRD § 2.2, (b) target file exists. Emits `domain_model_created` ledger event.
2. **REQUIREMENT (`gz domain list`).** Table with columns `BC`, `DM`, `State`, `ADRs`, `OBPIs`, `Open GHIs` for every PRD § 2.2 BC. Missing DM → `—  (missing)`. `--json` form structurally equivalent.
3. **REQUIREMENT (`gz domain status`).** Coverage comparison; orphan DM and missing DM detection. Exit 3 under `--strict` on drift; exit 0 with warning otherwise.
4. **REQUIREMENT (`gz domain show <bc-slug>`).** Full cascade for one BC: PRD § 2.2 entry + DM inlined + inbound/outbound context-map + BC-scoped glossary + linked ADRs/OBPIs/GHIs. `--json` is the agent-consumption surface.
5. **REQUIREMENT (`gz domain regenerate`).** Rebuilds `docs/design/domain/glossary.md`, `bounded-contexts.md`, `context-map.md`. Idempotent (re-run with no changes = byte-equal). Atomic (write-temp-then-rename). `--check` is dry-run-only (exit 3 if would change). Diff summary to stdout.
6. **REQUIREMENT (output forms).** Table = human default; `--json` = canonical structured form. JSON is valid; never embedded prose. Verb form honors `gz domain <verb>` (space) per operator-doc verb resolution invariant.
7. **REQUIREMENT (registry reader pure-functional).** `registry.py` reads-only. Mutations live in `init.py` and `regenerator.py`.
8. **REQUIREMENT (Layer separation invariant — binding).** `regenerate` MAY touch `docs/design/domain/{glossary,bounded-contexts,context-map}.md` and DM files' `## Decision History` only. MUST NOT touch any other DM section, any PRD, any ADR, any GHI, any source file. Violation = critical bug.
9. **REQUIREMENT (manpage parity).** Every verb has a manpage; all pass `gz cli audit`.

> STOP-on-BLOCKERS: if OBPI-01 or OBPI-02 schemas are not landed, halt — registry reader needs both.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #3 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § Behavior Rules
- [ ] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md`
- [ ] `docs/governance/state-doctrine.md` — Layer-3 derived views

**Context:**

- [ ] OBPI-01 strategic Pydantic landed
- [ ] OBPI-02 DM Pydantic + template landed
- [ ] Existing CLI patterns in `src/gzkit/cli/`
- [ ] Existing table/JSON renderers (e.g., `gz adr status`)

**Prerequisites:**

- [ ] `src/gzkit/governance/domain_models.py` complete
- [ ] `src/gzkit/templates/dm.md` exists
- [ ] `docs/design/domain/` exists

**Existing Code:**

- [ ] `src/gzkit/cli/adr.py` — subcommand-group pattern
- [ ] `src/gzkit/cli/validate.py` — `--json` form parity

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #3 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] `init`: happy path; unknown BC rejected; existing file rejected; ledger event emitted
- [ ] `list`: N BCs → N rows; missing DM flagged; `--json` round-trips
- [ ] `status`: orphan + missing detected; `--strict` exit 3
- [ ] `show`: BC with full cascade renders all sections; `--json` structurally complete
- [ ] `regenerate`: idempotence, atomic write, `--check` dry-run, Layer-separation invariant
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint / typecheck clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean
- [ ] Five manpages parse via `gz cli audit`
- [ ] `gz validate --cli-alignment` clean

### Gate 4: BDD (Heavy only)

- [ ] At least one scenario: `gz domain init` → `gz domain show` → `gz domain regenerate`

### Gate 5: Human (Heavy + Foundation)

- [ ] Attestation recorded

## Verification

```bash
uv run gz validate --documents --cli-alignment
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run mkdocs build --strict

uv run gz domain --help
for verb in init list status show regenerate; do
    uv run gz domain $verb --help
done
```

## Demo

```bash
# List BCs (after OBPI-13 populates PRD § 2.2)
uv run gz domain list
uv run gz domain list --json --output /tmp/bcs.json  # then inspect with jq /tmp/bcs.json

# Status check
uv run gz domain status

# Show one BC's cascade
uv run gz domain show governance --json --output /tmp/gov.json
# then: jq '.bounded_context, .domain_model.aggregates' /tmp/gov.json

# Regenerate; idempotence check
uv run gz domain regenerate
uv run gz domain regenerate --check
```

## Acceptance Criteria

- [ ] REQ-0.0.43-03-01: Given unknown BC slug, when `gz domain init <unknown>`, then exit 3 with `Resolve:` line
- [ ] REQ-0.0.43-03-02: Given `gz domain init <bc-slug>` succeeds, when ledger inspected, then `domain_model_created` event present
- [ ] REQ-0.0.43-03-03: Given PRD with no § 2.2 entries, when `gz domain list`, then header-only table
- [ ] REQ-0.0.43-03-04: Given N BCs and M DMs (M < N), when `gz domain status`, then exactly N − M rows flagged missing
- [ ] REQ-0.0.43-03-05: Given DM with no PRD entry, when `gz domain status`, then DM flagged orphan
- [ ] REQ-0.0.43-03-06: Given `gz domain show <bc-slug>`, when BC has cross-context entries, then they appear in both directions
- [ ] REQ-0.0.43-03-07: Given `gz domain regenerate` runs twice with no canon changes, then second run = byte-equal first
- [ ] REQ-0.0.43-03-08: Given `gz domain regenerate --check`, when output would differ, then exit 3 and no writes
- [ ] REQ-0.0.43-03-09: Given DM file, when before-after `gz domain regenerate`, then non-`## Decision History` sections byte-equal
- [ ] REQ-0.0.43-03-10: Given five new manpages, when `gz cli audit`, then all five pass

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR followed
- [ ] **Code Quality:** Clean
- [ ] **Gate 3 (Docs):** mkdocs + cli audit + cli-alignment clean
- [ ] **Gate 4 (BDD):** Scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/typecheck output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs + cli audit output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
