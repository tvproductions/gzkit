---
id: OBPI-0.0.52-10-docs-and-runbook-updates
parent: ADR-0.0.52-artifact-staleness-propagation
item: 10
lane: Heavy
status: Draft
allowlist:
- docs/user/manpages/adr-clear-stale.md
- docs/user/manpages/adr-explain-stale.md
- docs/user/manpages/adr-propagation.md
- docs/user/manpages/validate.md
- docs/user/runbook.md
- docs/governance/governance_runbook.md
- docs/governance/state-doctrine.md
- docs/user/index.md
- tests/governance/test_manpage_coverage_staleness.py
- docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md
reqs:
- REQ-0.0.52-10-01
- REQ-0.0.52-10-02
- REQ-0.0.52-10-03
- REQ-0.0.52-10-04
- REQ-0.0.52-10-05
- REQ-0.0.52-10-06
- REQ-0.0.52-10-07
- REQ-0.0.52-10-08
verification:
- uv run gz lint
- uv run gz typecheck
- uv run mkdocs build --strict
- uv run gz cli audit
- uv run -m unittest tests.governance.test_manpage_coverage_staleness -v
---

# OBPI-0.0.52-10-docs-and-runbook-updates: Docs, manpages, and runbook updates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #10 — "Docs + runbook updates — operator runbook, governance runbook, new-verb manpages (`clear-stale`, `explain-stale`, `propagation retry-tier2`, `gz validate --adr-eval-fresh`, `gz validate --staleness-coherence`), AGENTS.md § Behavior Rules entry naming the staleness-flag-resolution discipline"

**Status:** Draft

## Objective

Author the heavy-lane Gate 3 documentation deliverables: manpages for the five new verb/scope surfaces, runbook sections in both operator and governance runbooks, and an AGENTS.md § Behavior Rules entry naming the staleness-flag-resolution discipline as canonical. Add the rule entry under § Always or § Never as appropriate per AGENTS.md structure.

## Lane

**Heavy** — Heavy-lane Gate 3 documentation deliverables are required; this OBPI delivers all of them in one coordinated patch.

## Allowed Paths

- `docs/user/manpages/adr-clear-stale.md` — **PRIMARY:** manpage for the new resolution verb
- `docs/user/manpages/adr-explain-stale.md` — **PRIMARY:** manpage for the new explain verb
- `docs/user/manpages/adr-propagation.md` — **PRIMARY:** manpage for the new parent verb (covers `retry-tier2`)
- `docs/user/manpages/validate.md` — extend with `--adr-eval-fresh` and `--staleness-coherence` scopes
- `docs/user/runbook.md` — **PRIMARY:** new § "Staleness propagation" section (operator workflow)
- `docs/governance/governance_runbook.md` — **PRIMARY:** new § "Cross-artifact coherence" section (governance maintainer workflow)
- `AGENTS.md` — new § Behavior Rules entry naming the staleness-flag-resolution discipline
- `CLAUDE.md` — no edit expected (AGENTS.md is the primary; CLAUDE.md inherits)
- `docs/governance/state-doctrine.md` — cross-link to new propagation surface as Layer-1+Layer-2 coupled boundary
- `docs/user/index.md` — link to new manpages from the verb index
- `tests/governance/test_manpage_coverage_staleness.py` — `gz cli audit` style verification: every new verb has a manpage; every manpage has at least one example
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- Source implementations (OBPIs 01-08)
- BDD features (OBPI-09)
- Pyproject / dependency manifest

## Creates These Files

- `docs/user/manpages/adr-clear-stale.md` — **CREATE** manpage for the resolution verb
- `docs/user/manpages/adr-explain-stale.md` — **CREATE** manpage for the explain verb
- `docs/user/manpages/adr-propagation.md` — **CREATE** manpage for the parent verb (covers `retry-tier2`)
- `docs/user/manpages/validate.md` — **CREATE** (or extend existing) — add `--adr-eval-fresh` and `--staleness-coherence` scopes
- `tests/governance/test_manpage_coverage_staleness.py` — **CREATE** manpage-coverage verification

Existing files modified: `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, `AGENTS.md`, `docs/governance/state-doctrine.md`, `docs/user/index.md`.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Each new CLI surface introduced by this ADR MUST have a manpage under `docs/user/manpages/`: `gz-adr-clear-stale`, `gz-adr-explain-stale`, `gz-adr-propagation`. Existing `gz-validate.md` MUST be extended with the two new scopes.
2. REQUIREMENT: Each manpage MUST follow the canonical structure (Description, Usage, Options, Exit Codes, Examples). Each MUST include at least one real working example per `.claude/rules/cli.md` § Help Text Requirements.
3. REQUIREMENT: `docs/user/runbook.md` MUST gain a "Staleness propagation" section covering: what causes flags, how to read `gz status --table` Stale column, how to use `explain-stale`, how to resolve via `clear-stale` (both kinds, with attestation examples).
4. REQUIREMENT: `docs/governance/governance_runbook.md` MUST gain a "Cross-artifact coherence" section covering: how to interpret `gz validate --staleness-coherence` failures, recovery procedure for `tx_id` orphan events, how to read the tripwire receipt for operational health, Phase 1 / Phase 2 deployment cadence.
5. REQUIREMENT: AGENTS.md MUST gain a § Behavior Rules entry (Always or Never as appropriate) naming the staleness-flag-resolution discipline — agents MUST NOT clear flags via direct frontmatter edits; canonical path is the resolution verb; attestation is mandatory.
<!-- gz-validate-skip: command-shape -->
6. REQUIREMENT: `uv run gz cli audit` MUST exit 0 with every new verb (`clear-stale`, `explain-stale`, `propagation retry-tier2`, validator flags `--adr-eval-fresh`, `--staleness-coherence`) covered across manpage + command-doc + index parity.
7. REQUIREMENT: `uv run mkdocs build --strict` MUST exit 0 — no broken cross-links, no missing pages referenced from the runbooks or AGENTS.md.
8. REQUIREMENT: `state-doctrine.md` MUST gain a paragraph cross-linking to the propagation pipeline as the Layer-1 (frontmatter) and Layer-2 (ledger) coupled boundary with `tx_id` atomic pairing — reinforces existing state-doctrine canon rather than introducing new doctrine.

> STOP-on-BLOCKERS: ALL of OBPI-01 through OBPI-09 MUST have landed before this OBPI starts — docs reference the integrated, tested surface.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"Docs + runbook updates — operator runbook, governance runbook, new-verb manpages, AGENTS.md § Behavior Rules entry naming the staleness-flag-resolution discipline"*.
- [ ] Parent ADR § Evidence — surfaces this OBPI provides evidence for (the docs deliverables).

**Governance:**

- [ ] `.claude/rules/cli.md` § Help Text Requirements — manpage structure conventions.
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — runbook-vs-code parity rule (this OBPI satisfies the runbook half).
- [ ] `.claude/rules/tool-skill-runbook-alignment.md` — Invariant 1, 2, 3 — every new verb must have a wielding skill and runbook prescription. (Skill registration for the new verbs happens via the standard agent-sync ceremony post-merge; this OBPI delivers the runbook half.)
- [ ] AGENTS.md § Behavior Rules — structure for the new entry (Always / Never tier).

**Prerequisites:**

- [ ] OBPI-0.0.52-01 through OBPI-0.0.52-09 ALL have landed — the docs describe the integrated, tested surface.

**Existing Code:**

- [ ] An existing manpage (e.g., `docs/user/manpages/attest.md`) reviewed for structure conventions.
- [ ] Existing runbook sections in `docs/user/runbook.md` reviewed for tone and depth.
- [ ] AGENTS.md § Behavior Rules existing entries reviewed for shape and length.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests derived from brief acceptance criteria
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only) — PRIMARY for this OBPI

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] CLI audit clean: `uv run gz cli audit`
- [ ] Runbook updated (operator + governance)
- [ ] Manpages present for all new verbs and scopes

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass (covered by OBPI-09)

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run gz cli audit
uv run -m unittest tests.governance.test_manpage_coverage_staleness -v
```

## Demo

```bash
# Manpages render and include examples
ls docs/user/manpages/adr-clear-stale.md docs/user/manpages/adr-explain-stale.md docs/user/manpages/adr-propagation.md
grep -c "^## Examples" docs/user/manpages/adr-clear-stale.md docs/user/manpages/adr-explain-stale.md docs/user/manpages/adr-propagation.md

# Runbook sections present
grep -E "^##\s+(Staleness propagation|Cross-artifact coherence)" docs/user/runbook.md docs/governance/governance_runbook.md

# AGENTS.md entry present
grep -E "staleness.flag.resolution|evaluation_stale" AGENTS.md

# CLI audit clean
uv run gz cli audit

# Docs build strict
uv run mkdocs build --strict
```

## Acceptance Criteria

- [ ] REQ-0.0.52-10-01: Given the three new verb manpages (`gz-adr-clear-stale`, `gz-adr-explain-stale`, `gz-adr-propagation`), when inspected, then each contains Description, Usage, Options, Exit Codes, and at least one Example section.
- [ ] REQ-0.0.52-10-02: Given the existing `gz-validate.md` manpage, when inspected, then it now documents `--adr-eval-fresh` and `--staleness-coherence` scopes with exit-code semantics.
- [ ] REQ-0.0.52-10-03: Given `docs/user/runbook.md`, when read, then it contains a "Staleness propagation" section covering flag inspection, explain-stale usage, and the resolution ceremony (both kinds with attestation examples).
- [ ] REQ-0.0.52-10-04: Given `docs/governance/governance_runbook.md`, when read, then it contains a "Cross-artifact coherence" section covering `--staleness-coherence` recovery, tripwire receipt interpretation, and Phase 1 / Phase 2 deployment.
- [ ] REQ-0.0.52-10-05: Given AGENTS.md, when read, then a § Behavior Rules entry names the staleness-flag-resolution discipline (no direct frontmatter edits; canonical path is the resolution verb; attestation mandatory).
- [ ] REQ-0.0.52-10-06: Given `uv run gz cli audit`, when invoked, then it exits 0 with all five new surfaces covered across manpage + command-doc + index parity.
- [ ] REQ-0.0.52-10-07: Given `uv run mkdocs build --strict`, when invoked, then it exits 0 — no broken cross-links, no missing pages.
- [ ] REQ-0.0.52-10-08: Given `docs/governance/state-doctrine.md`, when read, then it cross-links to the propagation pipeline as the canonical Layer-1+Layer-2 coupled boundary example with `tx_id` atomic pairing.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle followed
- [ ] **Code Quality:** Lint, type checks clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** included
- [ ] **Gate 3 (Docs):** mkdocs strict + CLI audit + runbook update + AGENTS entry — all complete

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs strict + gz cli audit output here
```

### Gate 4 (BDD)

```text
# n/a — covered by OBPI-09
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before: the new propagation surface had no operator-facing documentation, no manpages for the new verbs, no AGENTS.md entry naming the discipline — the agent contract was implicit. Now: every new verb has a manpage, both runbooks have new sections covering the operator and governance workflows, AGENTS.md names the staleness-flag-resolution discipline as canonical, and `gz cli audit` mechanically enforces the parity going forward.

### Key Proof

```text
$ uv run gz cli audit
[OK] CLI audit clean: 92 verbs covered across manpages + command docs + index.

$ uv run mkdocs build --strict
INFO    -  Documentation built in 4.21 seconds

$ grep -c "evaluation_stale" AGENTS.md docs/user/runbook.md docs/governance/governance_runbook.md
AGENTS.md:3
docs/user/runbook.md:7
docs/governance/governance_runbook.md:5
```

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

**Date Completed:** -

**Evidence Hash:** -
