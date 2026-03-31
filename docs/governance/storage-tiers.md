<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Storage Tiers Reference

**Purpose:** Define the three-tier storage model for gzkit. Every storage location in the repository is classified into one of three tiers with explicit authority boundaries.

**Authority:** [ADR-0.0.10 — Storage Tiers and Simplicity Profile](../design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md)

**Companion:** [State Doctrine](state-doctrine.md) — three-layer trust model and authority rules

---

## Three-Tier Model

| Tier | Name | Definition | Authority Boundary |
|------|------|------------|--------------------|
| **A** | Canonical | Authored markdown with YAML frontmatter + append-only JSONL ledger. The default for all governance data. | Human and agent authors via governed workflows. Changes tracked in git. No external dependencies. |
| **B** | Derived / Rebuildable | Deterministic derived indexes and caches rebuilt from Tier A sources. Permitted freely but must be rebuildable from scratch. | Automated tooling (CLI, hooks, sync commands). May be deleted and regenerated at any time without data loss. |
| **C** | External / Stateful | External runtime backends (databases, servers, protocols). | Only by explicit Heavy-lane ADR authorization. Not present today. Introduction requires its own ADR. |

---

## Tier A — Canonical (Authored)

Tier A is the source of truth. All governance state originates here.

**Authority:** Human authors and governed agent workflows create and modify Tier A artifacts. All changes are committed to git.

**Examples from gzkit:**

| Location | Content |
|----------|---------|
| `.gzkit/ledger.jsonl` | Append-only governance event ledger |
| `docs/design/adr/**/ADR-*.md` | Architecture Decision Records |
| `docs/design/adr/**/obpis/OBPI-*.md` | OBPI implementation briefs |
| `docs/governance/**/*.md` | Governance policy and runbook documents |
| `src/gzkit/**/*.py` | Source code |
| `tests/**/*.py` | Test code |
| `config/*.json` | Configuration schemas and doctrine |
| `AGENTS.md`, `CLAUDE.md` | Agent operating contracts |

**Rules:**

- Tier A artifacts are the authoritative record.
- All Tier A state is committed to git and survives `git clone`.
- No external dependency is required to read or write Tier A data.
- Modifications follow lane-appropriate governance (Lite or Heavy).

---

## Tier B — Derived / Rebuildable

Tier B artifacts are computed from Tier A sources. They improve performance or convenience but carry no unique state.

**Authority:** Automated tooling creates and updates Tier B artifacts. Any agent or operator may delete them; they rebuild on demand.

**Examples from gzkit:**

| Location | Content | Rebuild Command |
|----------|---------|-----------------|
| `.gzkit/markers/` | Pipeline markers and state flags | Recreated by pipeline execution |
| `.claude/rules/` | Mirrored governance rules | `uv run gz agent sync control-surfaces` |
| `.claude/skills/` | Mirrored skill definitions | `uv run gz agent sync control-surfaces` |
| `site/` | Built documentation | `uv run mkdocs build` |
| `artifacts/receipts/` | ARB receipt artifacts | `uv run -m gzkit arb <tool>` |

**Rules:**

- Tier B artifacts must be fully rebuildable from Tier A sources plus deterministic tooling.
- Losing all Tier B data is an inconvenience, not a data loss event.
- `git clone` + `uv sync` + rebuild commands must recover all Tier B state.
- No unique governance state may accumulate in Tier B. If it does, that is an unaudited tier escalation (see Anti-Patterns below).

---

## Tier C — External / Stateful

Tier C represents external runtime dependencies that hold state not derivable from Tier A + B. **No Tier C dependency exists in gzkit today.**

**Authority:** Introduction of any Tier C dependency requires a dedicated Heavy-lane ADR authorizing the escalation.

**Potential future examples:**

- SQLite database for query optimization (acknowledged as post-1.0 path per ADR-0.0.10)
- External MCP server state
- Remote API endpoints holding governance state

**Rules:**

- Tier C is not permitted without explicit ADR authorization.
- No external protocol (MCP, LSP, etc.) may become a prerequisite for core governance operations.
- CLI + hooks + ledger is the universal baseline that must always function without Tier C.
- BEADS' JSONL-to-SQLite progression is acknowledged as a likely future path, governed by tier escalation when the time comes.

---

## Tier Escalation Governance

Moving data from Tier A/B to Tier C is a **tier escalation** — a Heavy-lane decision requiring its own ADR.

**Escalation triggers:**

1. A Tier B cache begins accumulating state not derivable from Tier A
2. A new external runtime dependency is proposed for core governance operations
3. An existing Tier A workflow would be replaced by an external backend

**Process:**

1. Author a Heavy-lane ADR documenting the escalation rationale
2. Demonstrate that the universal baseline (CLI + hooks + ledger) continues to function without the Tier C dependency
3. Document conflict, replay, and recovery behavior for the new storage backend
4. Obtain human attestation through Gate 5

---

## Identity Surfaces Across Tiers

Five identity surfaces are portable across all tiers. IDs require no tier-specific translation:

| Surface | Pattern | Example |
|---------|---------|---------|
| ADR | `ADR-X.Y.Z` | `ADR-0.0.10` |
| OBPI | `OBPI-X.Y.Z-NN` | `OBPI-0.0.10-01` |
| REQ | `REQ-X.Y.Z-NN-MM` | `REQ-0.0.10-01-01` |
| TASK | `TASK-*` | `TASK-0.0.10-01-001` |
| Evidence | `EV-*` | `EV-0.0.10-01-001` |

These identifiers work identically whether stored in Tier A markdown, Tier B indexes, or a future Tier C database.

---

## Anti-Patterns

| Anti-Pattern | Risk | Mitigation |
|-------------|------|------------|
| Tier B cache accumulates non-derivable state | Silent tier escalation to C without governance | Periodic rebuild test: delete Tier B, rebuild, verify no data loss |
| External service becomes prerequisite for `gz` commands | Protocol dependency violates simplicity profile | All core commands must work with only git + filesystem |
| Tier A data duplicated in Tier B with divergence | Conflicting sources of truth | Tier B must always be regenerated from Tier A, never edited directly |
| Config stored in environment variables | Invisible, non-auditable state outside git | Config precedence must never include env vars (hard rule) |

---

## Recovery: git clone from scratch

All Tier A + B state must survive a clean recovery:

```bash
git clone <repo-url>
cd gzkit
uv sync
uv run gz agent sync control-surfaces   # Rebuild Tier B mirrors
uv run gz lint                           # Verify tooling works
uv run gz test                           # Verify tests pass
```

After these commands, the repository is fully operational. No external service, database, or protocol is required.
