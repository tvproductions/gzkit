---
id: OBPI-0.0.18-03-pool-curation-policy
parent: ADR-0.0.18-adr-taxonomy-doctrine
item: 3
lane: Lite
status: Draft
---

# OBPI-0.0.18-03-pool-curation-policy: pool curation policy doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- **Checklist Item:** #3 — "Pool curation policy"

**Status:** Draft

## Objective

Author `docs/governance/pool-curation.md` — the policy for when an idea enters the pool, when it's promoted, when it's retired, and who/what cadence reviews the pool. Operators need a named policy they can cite, not folk wisdom.

## Lane

**Lite** — governance doctrine.

## Allowed Paths

- `docs/governance/pool-curation.md` (new)
- `docs/user/runbook.md` (cross-reference only if natural)
- `docs/governance/governance_runbook.md` (cross-reference only)
- `mkdocs.yml` (register if needed)

## Denied Paths

- Concepts page (OBPI-01)
- Runbook PRD→ADR guidance (OBPI-02)
- Epic grouping (OBPI-04)
- Skill surfaces (OBPI-05)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The policy document names the pool's role: "The pool is the storage/waiting area for ADR-shaped concerns that are seen but not yet committed. Pool entries are cheap to create and should be created freely."
2. REQUIREMENT: The policy documents **entry criteria**: an idea belongs in the pool when (a) the problem is visible and named, (b) the solution space has been sketched enough to scaffold an ADR-pool file, but (c) no sponsor is committing to the work in the current release cycle.
3. REQUIREMENT: The policy documents **promotion criteria**. A pool ADR is promoted (via `gz adr promote`) when: a sponsor exists (operator willing to attest completion); acceptance criteria are clear enough to write OBPI briefs; no dependency on unresolved foundation ADRs remains; capacity exists in the current cycle.
4. REQUIREMENT: The policy documents **retirement criteria**. A pool ADR is retired when: superseded by an accepted ADR (cross-referenced); rejected on review with a written rationale preserved in the pool file's frontmatter or a short Retirement section; the concern has dissolved (the problem no longer exists). Retirement preserves the file; it does not delete it.
5. REQUIREMENT: The policy documents **review cadence**: pool curation happens (a) during `gz tidy` sweeps, (b) at minor-version closeout boundaries, and (c) opportunistically when a new PRD lands that might absorb existing pool entries. No harder cadence is prescribed.
6. REQUIREMENT: The policy includes a short FAQ addressing at least: "How long can an ADR stay in the pool?" (answer: as long as it's still a real concern — duration is not a retirement criterion); "Who decides promotion?" (answer: the sponsor, with Gate 1 ceremony); "Can a foundation be created directly without pool?" (answer: yes — foundations are often identified by doing, not queuing).
7. REQUIREMENT: `mkdocs build --strict` passes.

## Verification

```bash
uv run mkdocs build --strict
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# Manual review: policy answers the named questions without new vocabulary
```

## Evidence

- Policy page diff
- mkdocs receipt
- Manual review notes

## REQ Coverage

- REQ-0.0.18-03-01 through REQ-0.0.18-03-07
