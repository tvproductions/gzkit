# .gzkit/ Directory Structure

**Status:** Active
**Last reviewed:** 2026-02-11
**Parent ADR:** ADR-0.0.25 (Compounding Engineering & Session Handoff Contract)

---

## Overview

`.gzkit/` (GovZero Kit) is the canonical root directory for GovZero governance ledgers, ontology artifacts, canonical skills, and learning scaffolds. It consolidates governance outputs that were previously scattered across `artifacts/` into a single, version-controlled location.

### Purpose

- **Centralized governance storage:** Single root for GovZero ledgers, ontology artifacts, and control-surface manifests
- **Compound engineering:** Learning artifacts accumulate across sessions, enabling future work to build on past insights
- **Canonical skill source:** `.gzkit/skills/` is the source of truth for mirrored agent skill surfaces
- **Git-tracked by default:** All files in `.gzkit/` are version-controlled unless explicitly gitignored
- **Append-only ledgers:** JSONL files grow monotonically, preserving full audit history

---

## Directory Structure

```text
.gzkit/
├── README.md                          # Quick orientation
├── governance/                        # Governance ontology + schema
│   ├── ontology.json
│   └── ontology.schema.json
├── insights/                          # Agent insight ledgers
│   └── agent-insights.jsonl           # Observations captured during work sessions
├── lessons/                           # Learning ledgers (compound engineering)
│   └── (*.jsonl files added by future OBPIs)
├── skills/                            # Canonical skill source for mirrored agents
├── ledger.jsonl                       # Append-only governance ledger
└── manifest.json                      # Repository/control-surface manifest
```

---

## Subdirectory Definitions

### `insights/`

Agent observations captured automatically during work sessions. These are raw, unstructured insights harvested by hooks or recorded by agents during problem-solving.

| File | Description |
|------|-------------|
| `agent-insights.jsonl` | Observations from all agents across sessions |

### `governance/`

Structured GovZero registry artifacts used to describe doctrines, policies, rules, and actions in machine-readable form.

| File | Description |
|------|-------------|
| `ontology.json` | Populated GovZero ontology for gzkit's currently adopted process-plane governance |
| `ontology.schema.json` | JSON Schema used to validate ontology structure |

### `lessons/`

Structured learning ledgers for compound engineering. Unlike raw insights, lessons are curated and categorized for future consumption. This directory is scaffolded by OBPI-0.0.25-02; learning ledger files will be populated by subsequent OBPIs in the ADR-0.0.25 series.

### `skills/`

Canonical skill definitions used by `gz agent sync control-surfaces` to regenerate mirrored agent surfaces under `.agents/skills/`, `.claude/skills/`, and `.github/skills/`.

### Root manifests

| File | Description |
|------|-------------|
| `ledger.jsonl` | Repo-scoped governance event ledger |
| `manifest.json` | Control-surface manifest, path contract, and verification command catalog |

---

## JSONL Conventions

All ledger files in `.gzkit/` follow these conventions:

| Convention | Rule |
|------------|------|
| Format | JSONL (JSON Lines) — one JSON object per line |
| Mutability | **Append-only** — never edit or delete existing lines |
| Encoding | UTF-8, no BOM |
| Timestamps | ISO 8601 UTC (Z-suffixed preferred) |
| Required fields | `timestamp` at minimum; `type` for typed ledgers |

### Example Entry

```json
{"timestamp": "2026-02-11T14:30:00Z", "type": "insight", "category": "pattern", "insight": "Port adapters delegate all business logic to legacy ingest modules."}
```

For the full field specification of typed governance ledgers (obpi-audit, covers-map, etc.), see [Unified Ledger Schema](ledger-schema.md).

---

## Storage Conventions (ADR-0.0.25 Decision 3)

ADR-0.0.25 defines a storage architecture that splits artifacts by scope:

| Artifact Type | Location | Rationale |
|---------------|----------|-----------|
| GovZero ledgers | `.gzkit/` | Repo-wide governance outputs |
| Governance ontology | `.gzkit/governance/` | Structured machine-readable governance model |
| Learning ledgers | `.gzkit/lessons/` | Cross-session compound learning |
| Agent insights | `.gzkit/insights/` | Raw agent observations |
| Canonical skills | `.gzkit/skills/` | Source of truth for mirrored agent skill surfaces |
| Session handoffs | `{ADR-package}/handoffs/` | Package-local, tied to specific ADR work |
| ADR audit ledgers | `{ADR-package}/logs/` | Per-ADR OBPI audit trails |

`.gzkit/` holds **repo-scoped** artifacts. **ADR-scoped** artifacts (handoffs, per-ADR audit logs) remain in their ADR package directories.

---

## Relationship to `artifacts/`

The `artifacts/` directory holds runtime outputs (databases, caches, logs) and is gitignored. `.gzkit/` is distinct:

| Aspect | `artifacts/` | `.gzkit/` |
|--------|-------------|-----------|
| Git status | Gitignored | Tracked |
| Content | Runtime data (DB, cache) | Governance ledgers |
| Mutability | Read/write | Append-only |
| Lifecycle | Ephemeral, regenerable | Permanent audit trail |

Migration of existing GovZero outputs (agent-insights.jsonl) from root to `.gzkit/` was completed by OBPI-0.0.25-09.

---

## References

- [ADR-0.0.25](../../design/adr/adr-0.0.x/ADR-0.0.25-compounding-engineering-session-handoff-contract/ADR-0.0.25-compounding-engineering-session-handoff-contract.md) — Parent ADR
- [Unified Ledger Schema](ledger-schema.md) — JSONL field definitions and validation API
- [Layered Trust Architecture](layered-trust.md) — Tool layer model and boundaries
- [GovZero Charter](charter.md) — Gate definitions and authority
