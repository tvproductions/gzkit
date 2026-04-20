# Plan: OBPI-0.0.18-03 — Pool Curation Policy

## Context

ADR-0.0.18 (ADR taxonomy doctrine) locks the three-kind model: `pool`, `foundation`, `feature`. The parent ADR establishes pool semantics at a high level ("pool freely, promote deliberately; pool is the storage/waiting area") but operators currently have no named policy document they can cite for *when* an idea enters the pool, *when* it's promoted, *when* it's retired, and *who/what cadence* reviews it. OBPI-0.0.18-03 closes that gap by authoring `docs/governance/pool-curation.md` as a first-class governance doctrine page, consistent with the existing trust-doctrine / state-doctrine / storage-tiers trio.

The OBPI brief (`docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/obpis/OBPI-0.0.18-03-pool-curation-policy.md`) is Lite lane and specifies 7 FAIL-CLOSED requirements: pool-role statement, entry criteria, promotion criteria, retirement criteria, review cadence, FAQ, and `mkdocs build --strict` passing.

## Approach

Write one new governance doctrine page and register it in `mkdocs.yml`. Faithfully expand ADR-0.0.18's pool doctrine into operator-facing policy; do not redefine or introduce new vocabulary. Stay within the brief's Allowed Paths — no unsolicited runbook edits.

## Files to modify

1. **`docs/governance/pool-curation.md` (new)** — authoritative policy page.

   Structure (mirrors the trust-doctrine / state-doctrine / storage-tiers pattern):

   - **Title + metadata line** — Source ADR (`ADR-0.0.18`), companion docs (adr-taxonomy concept page, governance_runbook), enforcement surface (`gz adr promote` kind/semver gate).
   - **Why this doctrine exists** — 2–3 sentences. Pool is the waiting area; without a named policy, entry/promotion/retirement become folk wisdom and drift.
   - **The pool's role** (REQ-01) — quotes the parent ADR: "The pool is the storage/waiting area for ADR-shaped concerns that are seen but not yet committed. Pool entries are cheap to create and should be created freely."
   - **Entry criteria** (REQ-02) — the three-part test (a) problem visible and named, (b) solution space sketched enough to scaffold a pool file, (c) no sponsor committing in the current release cycle. Files live at `docs/design/adr/pool/ADR-pool.<slug>.md` (cross-ref storage-tiers Tier A). No semver, no `kind:` field (cross-ref adr-taxonomy concept page).
   - **Promotion criteria** (REQ-03) — four conditions: sponsor exists, acceptance criteria ready for OBPI authoring, no unresolved foundation dependencies, capacity in the cycle. Mechanical gate is `uv run gz adr promote ADR-pool.<slug> --kind {foundation,feature} --semver X.Y.Z` — describe the kind/semver binding (foundation ⇒ `0.0.x`, feature ⇒ non-`0.0.x`) as mechanically enforced by the CLI. Link to `docs/user/commands/adr-promote.md` for flag reference.
   - **Retirement criteria** (REQ-04) — three paths: superseded (cross-reference the accepted ADR), rejected-on-review (written rationale preserved in frontmatter or a `## Retirement` section), dissolved (problem no longer exists). *Retirement preserves the file; it does not delete it.*
   - **Review cadence** (REQ-05) — three triggers: during `gz tidy` sweeps, at minor-version closeout boundaries, opportunistically when a new PRD may absorb existing entries. Explicit: "No harder cadence is prescribed."
   - **FAQ** (REQ-06) — at minimum three questions:
     - "How long can an ADR stay in the pool?" — as long as the concern is real; duration is not a retirement criterion.
     - "Who decides promotion?" — the sponsor, subject to Gate 1 ceremony.
     - "Can a foundation be created directly without pool?" — yes; foundations are often identified by doing, not queuing.
   - **Anti-patterns** — (a) deleting a pool file instead of retiring it, (b) promoting without a sponsor, (c) treating pool inactivity as a retirement trigger, (d) creating a pool file with no problem statement.
   - **Related** — links to `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`, `docs/user/concepts/adr-taxonomy.md`, `docs/user/commands/adr-promote.md`, `docs/governance/governance_runbook.md`, `docs/governance/storage-tiers.md`.

2. **`mkdocs.yml`** — register the new page under the existing `Governance (Canonical)` nav section, placed alphabetically/logically near `Feature Flags` and `Parity Intake Rubric`:

   ```yaml
   - Pool Curation Policy: governance/pool-curation.md
   ```

## Files NOT to modify

Per the Allowed Paths, `docs/user/runbook.md` and `docs/governance/governance_runbook.md` cross-references are permitted only "if natural." Both files already reference `gz adr promote` and the pool in passing, and the new policy page links back to them. No edits are necessary — leaving them untouched keeps the diff minimal and avoids surprises for Stage 4 attestation.

## Verification

Phase 1 — baseline quality checks (always run):

```bash
uv run gz lint
uv run gz test --obpi OBPI-0.0.18-03-pool-curation-policy    # Lite lane; no source tests expected
uv run gz validate --documents
```

Phase 2 — REQ-specific verification (from the brief):

```bash
uv run mkdocs build --strict
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

Phase 3 — manual review walkthrough against the 7 REQs:

- REQ-01: pool-role statement present and quotes the canonical phrasing.
- REQ-02: entry criteria enumerate the three-part test (a/b/c).
- REQ-03: promotion criteria enumerate the four conditions and cite `gz adr promote`.
- REQ-04: retirement criteria enumerate the three paths and assert file preservation.
- REQ-05: review cadence enumerates the three triggers and disclaims any harder cadence.
- REQ-06: FAQ answers at least the three named questions.
- REQ-07: `mkdocs build --strict` exits 0 with the new page and nav entry.

## Risks

- **New vocabulary drift.** Temptation to coin new terms ("pool hygiene", "curation steward") — the brief explicitly asks for "no new vocabulary." Stay inside the ADR-0.0.18 lexicon.
- **Scope creep.** Temptation to edit the user runbook to add a `pool curation` workflow entry — the brief lists that as cross-reference-only-if-natural, and the runbook already references `gz adr promote`. Declining the edit is the right call.
- **mkdocs strict breakage.** A broken internal link will fail strict build. Verify every cross-ref resolves before Stage 3.

## Estimated size

- `docs/governance/pool-curation.md`: ~150–200 lines.
- `mkdocs.yml`: 1 line added.
- Zero source code changes. Zero test changes.
