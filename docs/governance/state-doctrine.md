<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# State Doctrine — Three-Layer Model and Authority Rules

**Source ADR:** [ADR-0.0.9 — State Doctrine and Source-of-Truth Hierarchy](../design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md)

**Purpose:** Define the canonical storage layers and authority rules that every `gz` command must follow when reading or writing state. This document is the single reference for "which layer wins?" questions.

---

## Three-Layer Model

gzkit stores governance state across three layers. Each layer has a distinct role, authority level, and durability guarantee.

### Layer 1: Governance Canon (L1)

**What it is:** The versioned markdown and YAML files checked into git that define ADRs, OBPI briefs, configuration, and governance policy.

**Authority:** Defines *what should exist* — the intent, scope, and structure of governance artifacts.

**Examples in gzkit:**

| Artifact | Path |
|----------|------|
| ADR documents | `docs/design/adr/**/ADR-*.md` |
| OBPI briefs | `docs/design/adr/**/obpis/OBPI-*.md` |
| Governance config | `.gzkit/manifest.json` |
| Governance runbook | `docs/governance/governance_runbook.md` |

**Durability:** Git-versioned. Survives clone, fork, and archive. Rebuildable from any git checkout.

### Layer 2: Event Log (L2)

**What it is:** The append-only JSONL ledger that records every governance event — completions, attestations, receipts, audits, and reconciliations.

**Authority:** Defines *what has happened* — the runtime truth for status and completion.

**Examples in gzkit:**

| Artifact | Path |
|----------|------|
| Global ledger | `.gzkit/ledger.jsonl` |
| ADR-level audit log | `docs/design/adr/**/logs/obpi-audit.jsonl` |
| Ceremony log | `.gzkit/ceremonies/*.jsonl` |

**Durability:** Git-versioned (append-only). Each line is a timestamped, immutable event. Lines are never edited or deleted.

### Layer 3: Derived State (L3)

**What it is:** Caches, indexes, markers, and computed artifacts that are derived from L1 and L2. Deletable and rebuildable.

**Authority:** Defines *what is convenient* — accelerates queries and runtime operations but is never the source of truth.

**Examples in gzkit:**

| Artifact | Path |
|----------|------|
| Pipeline markers | `.claude/plans/.pipeline-active*.json` |
| OBPI work locks | `.gzkit/locks/obpi/*.lock.json` |
| Frontmatter `status:` fields | YAML frontmatter in brief files |
| ADR status table `Status` column | OBPI Decomposition tables in ADR docs |

**Durability:** Ephemeral. Delete all L3 artifacts, run `uv run gz state`, and everything reconstructs from L1 + L2.

---

## Five Authority Rules

These rules are drawn verbatim from the ADR-0.0.9 Decision section. They govern every `gz` command that reads or writes state.

### Rule 1: Ledger Is Authoritative for Runtime Status

> The ledger (`.gzkit/ledger.jsonl`) is authoritative for all runtime status. If frontmatter says `status: Completed` but no corresponding ledger event exists, the entity is not complete.

### Rule 2: Frontmatter Is a Lazy Mirror

> Frontmatter status is a lazy mirror. It is auto-fixed at lifecycle moments (`gz closeout`, `gz attest`, `gz obpi reconcile`) but allowed to lag during active execution. Frontmatter is never read as source-of-truth for completion.

### Rule 3: Layer 3 Is Always Rebuildable

> Layer 3 artifacts (pipeline markers, caches, derived indexes) are always rebuildable. Delete them all, run `gz state`, and everything reconstructs from L1 + L2.

### Rule 4: Reconciliation Is a Core Operation

> Reconciliation is a core architectural operation, not a maintenance chore. It is tested, gated, and optionally run as part of the pipeline.

### Rule 5: Layer 3 Cannot Block Gates

> Layer 3 artifacts cannot block gates. Only L1 (canon) and L2 (events) can be gate evidence. L3 can surface warnings but never fail-close a gate.

---

## Decision Table: When Layers Disagree

When state across layers is inconsistent, use this table to determine which layer wins.

| Conflict | Winner | Action |
|----------|--------|--------|
| Frontmatter says `Completed`, ledger has no completion event | **L2 (Ledger)** — entity is NOT complete | Run `gz obpi reconcile` to fix frontmatter |
| Ledger says completed, frontmatter says `Draft` | **L2 (Ledger)** — entity IS complete | Run `gz obpi reconcile` to update frontmatter |
| Pipeline marker exists but ledger has no pipeline event | **L2 (Ledger)** — marker is stale | Delete the marker; it will be recreated if needed |
| ADR table shows `Pending` but brief frontmatter says `Completed` | **L1 (Brief)** over L3 (table) | Run `gz obpi sync` to update the ADR table from brief source |
| Brief frontmatter says `Completed` but ledger disagrees | **L2 (Ledger)** over L3 (frontmatter) | Run `gz obpi reconcile` to align frontmatter with ledger |
| Lock file exists but process is dead | **L3 is ephemeral** — lock is stale | Re-claim the lock; stale locks auto-release past TTL |
| Config manifest lists a path that no longer exists on disk | **L1 (Disk)** — manifest is stale | Update manifest or run `gz check-config-paths` |

### General Precedence

```text
L2 (Ledger events)  >  L1 (Canon files)  >  L3 (Derived state)
```

- **L2 beats L1** for runtime status questions ("is this done?"). The ledger records what actually happened; canon records what was intended.
- **L1 beats L3** for structural questions ("what briefs exist?"). Canon is the source of truth for artifact identity and scope.
- **L3 loses to everything.** Derived state is always rebuildable and never authoritative.

### Recovery Command

When drift is detected between layers, the canonical repair sequence is:

```bash
uv run gz state --repair       # Force-reconcile all frontmatter from ledger
uv run gz obpi reconcile <ID>  # Reconcile one OBPI
uv run gz adr audit-check <ADR-ID>  # Verify no evidence gaps remain
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| Reading `status: Completed` from YAML frontmatter as proof of completion | Frontmatter is L3 — it can lag or be manually edited | Read the ledger for completion events |
| Using pipeline marker existence as gate evidence | Markers are L3 — they can be stale or orphaned | Use ledger events for gate evidence |
| Manually editing `.gzkit/ledger.jsonl` | Ledger is append-only by policy | Use `gz` commands to emit events |
| Treating reconciliation as optional maintenance | Drift accumulates and gates produce false results | Run reconciliation as part of lifecycle |
| Blocking a gate check on a missing L3 artifact | L3 cannot fail-close gates (Rule 5) | Only L1 and L2 evidence can block gates |
