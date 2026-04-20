<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Pool Curation Policy

**Purpose:** Define the operator policy for when an idea enters the ADR pool, when a pool ADR is promoted, when it is retired, and at what cadence the pool is reviewed. Operators can cite this page by name instead of folk wisdom.

**Authority:** [ADR-0.0.18 — ADR Taxonomy Doctrine](../design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md)

**Companions:** [ADR Taxonomy concept page](../user/concepts/adr-taxonomy.md) · [adr-promote command reference](../user/commands/adr-promote.md) · [Governance Runbook](governance_runbook.md) · [Storage Tiers](storage-tiers.md)

**Enforcement surface:** `uv run gz adr promote` (kind/semver binding is fail-closed). `uv run gz validate --taxonomy` (pool ⇒ no `kind`/`semver` frontmatter).

---

## Why this doctrine exists

ADR-0.0.18 locks the three-kind taxonomy (`pool`, `foundation`, `feature`) but does not by itself tell an operator *when* to file a pool ADR, *when* a pool ADR is ready to promote, or *when* it is time to retire one. Without a named policy those calls become folk wisdom and drift between agents and sessions. This page fixes the drift point: every decision about pool intake, promotion, retirement, and review cadence traces here.

---

## The pool's role

> The pool is the storage/waiting area for ADR-shaped concerns that are seen but not yet committed. Pool entries are cheap to create and should be created freely.

Pool ADRs live in `docs/design/adr/pool/` as `ADR-pool.<slug>.md`. They carry no `semver` and no `kind:` frontmatter field — both are absent by design, and `gz validate --taxonomy` fail-closes if either appears on a pool file. The ADR Taxonomy concept page documents the kind/semver binding in full.

The doctrine is **pool freely, promote deliberately**. A pool ADR that has sat for a year is not a problem per se — it is documented intent that has not earned promotion yet. Duration alone is not a retirement criterion (see [Retirement criteria](#retirement-criteria)).

---

## Entry criteria

An idea belongs in the pool when **all three** of the following hold:

1. **The problem is visible and named.** There is a real concern — a capability gap, an invariant that should exist, a workflow that hurts — and someone has written it down in their own words. A vague "we should probably think about X someday" is not ready; "operators cannot currently do Y, and the cost shows up as Z" is.
2. **The solution space has been sketched enough to scaffold a pool file.** The author can write a short problem statement and at least one target-scope bullet that a future sponsor could expand into an ADR body. The pool file is not an empty placeholder — it has enough content that a promoter can see what they would be promoting.
3. **No sponsor is committing to the work in the current release cycle.** Either the capacity is not there, dependencies are not ready, or no operator has agreed to drive the ADR through its gates. If a sponsor *is* ready to commit now, the work skips the pool and is authored directly as a foundation or feature ADR — see the [FAQ](#faq) on creating foundations without pooling first.

When all three hold, scaffold the pool file with `uv run gz plan create --kind pool --slug <slug>` (or edit one by hand). Pool creation is a Lite-lane, Gate-1-only activity — the bar is intentionally low.

---

## Promotion criteria

A pool ADR is promoted to an active foundation or feature ADR when **all four** of the following hold:

1. **A sponsor exists.** One operator is willing to attest completion — run the work through its gates, sit the Gate 5 walkthrough (for Heavy-lane or foundation-kind work), and own the brief.
2. **Acceptance criteria are clear enough to author OBPI briefs.** The promoter can decompose the ADR into 1–N OBPI checklist items where each item has a named deliverable and a verifiable outcome. If the scope is still too fuzzy to split into OBPIs, it is not ready to promote.
3. **No dependency on unresolved foundation ADRs remains.** If the pool entry depends on a foundation invariant that has not itself been accepted, the foundation lands first. Promoting on top of pending doctrine produces reconciliation debt.
4. **Capacity exists in the current cycle.** Promotion commits the sponsor and the project to the work landing in a near-term release (for feature kind) or to an invariant change being walked through (for foundation kind). If capacity is not there, the pool entry waits — that is what the pool is for.

The mechanical gate is:

```bash
uv run gz adr promote ADR-pool.<slug> --kind {foundation,feature} --semver X.Y.Z
```

`gz adr promote` enforces the kind/semver binding at the CLI boundary: `foundation` requires `0.0.x`, `feature` requires non-`0.0.x`, and `pool` is rejected as a `--kind` value (pool is the source, not the target). The command scaffolds the canonical ADR package, derives OBPI briefs from the pool file's Target Scope bullets, and records `artifact_renamed` plus one `obpi_created` event per brief in the ledger. Flag reference and worked examples live in the [adr-promote command doc](../user/commands/adr-promote.md).

Promotion is deliberate, not automatic. A promoted ADR begins at Gate 1 like any other; nothing about having lived in the pool grants a gate skip.

---

## Retirement criteria

A pool ADR is retired when **one** of the following paths applies:

1. **Superseded.** An accepted ADR now covers the concern the pool entry documented. Record the supersession by setting `status: Superseded` and `superseded_by: ADR-X.Y.Z-<slug>` in the pool file's frontmatter, and add a short "Superseded by" line at the top of the body. Cross-reference the accepted ADR so future readers can follow the lineage.
2. **Rejected on review.** The operator group has reviewed the concern and decided it will not be promoted — the problem is not real, the cost is lower than the solution, or the direction is wrong. Record the rationale in the pool file, either in the frontmatter (`status: Rejected`, `rejection_reason: "<short rationale>"`) or as a dedicated `## Retirement` section in the body. The written rationale matters more than the status field: future readers need to know *why* the decision was made, not only *that* it was.
3. **Dissolved.** The problem no longer exists — the upstream change that made the concern relevant has been reversed, the workflow has been redesigned, or what looked like a gap turned out to be covered by an existing surface. Document the dissolution in a short note on the pool file.

**Retirement preserves the file; it does not delete it.** The git history and the `docs/design/adr/pool/` directory retain the pool file forever — a retired pool ADR is a record of intent that was considered, not a mistake to hide. Deleting a retired pool file is an anti-pattern (see [Anti-patterns](#anti-patterns)).

Duration is not a retirement criterion. A pool ADR that has been on the shelf for five years and still names a real concern is still a valid pool ADR. It only retires when one of the three paths above applies.

---

## Review cadence

Pool curation happens on three triggers. No harder cadence is prescribed — the pool is not a ticket queue and it does not have an SLA.

1. **During `gz tidy` sweeps.** Repository-hygiene runs opportunistically walk the pool directory, flag missing frontmatter fields, and surface entries whose rationale has drifted. Agents running `gz tidy` may file GHIs against pool entries that look wrong; they do not silently edit the substance.
2. **At minor-version closeout boundaries.** When a minor release is being cut, the release ceremony's ADR sweep is a natural checkpoint to review whether pool entries have become ready to promote, have been superseded by shipped work, or have dissolved. A closeout that ships a feature addressing a pool entry should retire the pool entry in the same patch.
3. **Opportunistically when a new PRD lands.** PRD authoring surfaces problems the PRD author was not initially aware were already pooled. When a new PRD lands, the author (or their reviewer) scans the pool for entries that overlap — entries that should be absorbed into the PRD's ADR lineage, or entries the PRD explicitly supersedes. Opportunistic absorption is preferred over parallel work streams on the same concern.

Cadence is triggered by these events, not by a calendar. A pool that sees no promotions in a quarter is not a backlog failure — it is a pool doing its job as a waiting area.

---

## FAQ

### How long can an ADR stay in the pool?

As long as the concern is still real. There is no duration limit, and duration is not a retirement criterion. A pool ADR that has sat for five years and still names a problem worth solving is still a valid pool ADR. Retirement is triggered by supersession, rejection on review, or dissolution — not by staleness.

### Who decides promotion?

The sponsor decides. A sponsor is an operator willing to attest completion of the resulting ADR — authoring the OBPI briefs, running the work through its gates, and (for Heavy-lane or foundation-kind ADRs) sitting the Gate 5 walkthrough. Gate 1 ceremony runs on the promoted ADR like any other: promotion from the pool does not shorten Gate 1, it only starts it. The sponsor's decision to promote is the commit; the Gate 1 review is the verification.

### Can a foundation be created directly without pool?

Yes. Foundations are often identified *by doing* — an agent lands work and notices the work rested on an unstated invariant that should be named. In that case, the correct move is to author the foundation ADR directly at the point of discovery. Pooling a foundation that is already ready-to-author adds a step that produces no value. The pool exists for concerns that are *seen but not yet committed*; a foundation surfaced mid-flight is already committed the moment its sponsor writes it down.

The same applies to features when the sponsor is ready in the same breath as the scope: skip the pool and author the feature ADR directly. Pool is the right answer when the concern is named but the sponsor-capacity-dependency tuple is not yet complete.

---

## Anti-patterns

- **Deleting a retired pool file instead of marking it retired.** Retirement preserves the record so future readers can trace the decision; deletion erases the history.
- **Promoting without a sponsor.** A promoted ADR without a sponsor is a blocked ADR: nobody is on the hook for gates, attestation, or landing. Wait for the sponsor.
- **Treating pool inactivity as a retirement trigger.** A quiet pool entry is not a stale pool entry. Staleness is a [Storage Tiers](storage-tiers.md) concern for derived caches, not for Tier A pool files.
- **Creating a pool file with no problem statement.** Pool entries that are pure placeholders (`# Maybe we should look at X`) do not meet entry criterion 1. Either the problem is nameable or the entry is not ready to exist.
- **Skipping the pool when the concern is not yet sponsored.** Authoring a foundation or feature ADR for work that has no sponsor produces a zombie ADR — it will sit at Draft indefinitely. The pool is the honest home for unsponsored intent.

---

## Related

- [ADR-0.0.18 — ADR Taxonomy Doctrine](../design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md) — the kind/lane/semver model this policy operationalizes
- [ADR Taxonomy concept page](../user/concepts/adr-taxonomy.md) — operator doctrine on when to choose each kind, with worked examples
- [adr-promote command reference](../user/commands/adr-promote.md) — flag reference and preconditions for `gz adr promote`
- [Governance Runbook](governance_runbook.md) — operator procedures including pool-promotion checkpoints
- [Storage Tiers](storage-tiers.md) — Tier A placement of `docs/design/adr/pool/`
