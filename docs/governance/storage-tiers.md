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

**Storage Catalog (exhaustive):**

| Location | Content |
|----------|---------|
| `.gzkit/ledger.jsonl` | Append-only governance event ledger |
| `.gzkit/manifest.json` | Governance manifest (skill/rule registry) |
| `.gzkit/governance/` | Ontology schemas (`ontology.json`, `ontology.schema.json`) |
| `.gzkit/ceremonies/` | Ceremony records (JSON) |
| `.gzkit/insights/agent-insights.jsonl` | Agent insight journal |
| `.gzkit/lessons/` | Lessons learned |
| `.gzkit/schemas/` | Rule and skill validation schemas |
| `.gzkit/prompts/` | Alignment prompts |
| `.gzkit/gzkit-companion-adr-prompt.md` | ADR companion prompt |
| `.gzkit/README.md` | Governance directory README |
| `docs/design/adr/**/ADR-*.md` | Architecture Decision Records |
| `docs/design/adr/**/obpis/OBPI-*.md` | OBPI implementation briefs |
| `docs/design/adr/pool/` | Pool (backlog) ADRs awaiting promotion |
| `docs/governance/**/*.md` | Governance policy and runbook documents |
| `docs/user/**` | User-facing documentation and runbooks |
| `src/gzkit/**/*.py` | Source code |
| `tests/**/*.py` | Test code |
| `features/**/*.feature` | BDD feature specifications |
| `data/schemas/*.json` | Data validation schemas |
| `config/*.json` | Configuration schemas, doctrine, and chore definitions |
| `config/AGENTS.md` | Config-level agent contract |
| `ops/` | Operational scripts |
| `pyproject.toml` | Project metadata and dependency declarations |
| `uv.lock` | Dependency lock file |
| `mkdocs.yml` | Documentation site configuration |
| `.github/workflows/` | CI/CD workflow definitions |
| `.github/instructions/` | Agent instruction canon (source for rule mirrors) |
| `AGENTS.md`, `CLAUDE.md` | Agent operating contracts |

**Rules:**

- Tier A artifacts are the authoritative record.
- All Tier A state is committed to git and survives `git clone`.
- No external dependency is required to read or write Tier A data.
- Modifications follow lane-appropriate governance (Lite or Heavy).
- **Every on-disk location MUST appear in this catalog.** Unclassified locations are a governance defect.

---

## Tier B — Derived / Rebuildable

Tier B artifacts are computed from Tier A sources. They improve performance or convenience but carry no unique state.

**Authority:** Automated tooling creates and updates Tier B artifacts. Any agent or operator may delete them; they rebuild on demand.

**Storage Catalog (exhaustive):**

| Location | Content | Rebuild Command |
|----------|---------|-----------------|
| `.gzkit/markers/` | Pipeline markers and state flags | Recreated by pipeline execution |
| `.gzkit/locks/` | OBPI work locks (local coordination) | `/gz-obpi-lock claim` |
| `.claude/rules/` | Mirrored governance rules | `uv run gz agent sync control-surfaces` |
| `.claude/skills/` | Mirrored skill definitions | `uv run gz agent sync control-surfaces` |
| `.claude/plans/` | Plan files, pipeline markers, receipts | Pipeline execution / plan mode |
| `.agents/skills/` | Codex skill mirror | `uv run gz agent sync control-surfaces` |
| `.github/skills/` | Copilot skill mirror | `uv run gz agent sync control-surfaces` |
| `site/` | Built documentation (gitignored) | `uv run mkdocs build` |
| `artifacts/receipts/` | ARB receipt artifacts | `uv run -m gzkit arb <tool>` |

**Ephemeral / gitignored (not tracked in git):**

| Location | Content |
|----------|---------|
| `.venv/` | Python virtual environment |
| `.ruff_cache/` | Ruff linter cache |
| `build/`, `dist/` | Python build artifacts |
| `__pycache__/` | Python bytecode cache |

**Rules:**

- Tier B artifacts must be fully rebuildable from Tier A sources plus deterministic tooling.
- Losing all Tier B data is an inconvenience, not a data loss event.
- `git clone` + `uv sync` + rebuild commands must recover all Tier B state.
- No unique governance state may accumulate in Tier B. If it does, that is an unaudited tier escalation (see Anti-Patterns below).
- Gitignored ephemeral artifacts are excluded from governance classification but listed above for completeness.

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

| Surface | Pattern | Regex | Example |
|---------|---------|-------|---------|
| ADR | `ADR-X.Y.Z` | `^ADR-\d+\.\d+\.\d+$` | `ADR-0.0.10` |
| OBPI | `OBPI-X.Y.Z-NN` | `^OBPI-\d+\.\d+\.\d+-\d+$` | `OBPI-0.0.10-01` |
| REQ | `REQ-X.Y.Z-NN-MM` | `^REQ-\d+\.\d+\.\d+-\d+-\d+$` | `REQ-0.0.10-01-01` |
| TASK | `TASK-X.Y.Z-NN-MM-SS` | `^TASK-\d+\.\d+\.\d+-\d+-\d+-\d+$` | `TASK-0.20.0-01-01-01` |
| Evidence | `EV-X.Y.Z-NN-SSS` | `^EV-\d+\.\d+\.\d+-\d+-\d+$` | `EV-0.0.10-01-001` |

These identifiers work identically whether stored in Tier A markdown, Tier B indexes, or a future Tier C database.

### Identity Surface Models

Each surface has a corresponding Pydantic model in `src/gzkit/core/models.py`:

| Surface | Model | ConfigDict |
|---------|-------|------------|
| ADR | `AdrId` | `frozen=True, extra="forbid"` |
| OBPI | `ObpiId` | `frozen=True, extra="forbid"` |
| REQ | `ReqId` | `frozen=True, extra="forbid"` |
| TASK | `TaskId` | `frozen=True, extra="forbid"` |
| Evidence | `EvidenceId` | `frozen=True, extra="forbid"` |

All models provide `parse(raw: str)` and `__str__()` for lossless round-trip. These are identity-only models. Entity decomposition (extracting semver components) belongs to domain-specific models in `triangle.py` and `tasks.py`.

### Portability Guarantee

1. **Same string, any tier.** An ID parsed in Tier A markdown produces the same model as the same ID parsed in a Tier B index or a future Tier C store.
2. **No translation layer.** There is no mapping table, no tier-specific prefix, and no encoding transform. The raw string is the identity.
3. **Pydantic enforcement.** Identity models validate format at parse time. Invalid IDs are rejected immediately.
4. **Hierarchical containment.** Each surface ID contains its parent context: OBPI contains its ADR semver, REQ contains its OBPI item, TASK and EV contain their parent chain.

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
