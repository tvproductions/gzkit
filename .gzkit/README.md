# .gzkit/ - GovZero Kit

Canonical home for gzkit governance state, canonical skills, and learning artifacts.

**Full documentation:** [gzkit-structure.md](../docs/governance/GovZero/gzkit-structure.md)

## Directory Structure

```text
.gzkit/
|-- governance/           # Governance ontology and related schemas
|   |-- ontology.json
|   `-- ontology.schema.json
|-- insights/             # Agent insight ledgers
|   `-- agent-insights.jsonl
|-- lessons/              # Learning ledgers scaffold
|   `-- .gitkeep
|-- skills/               # Canonical skill source for mirrored agent surfaces
|-- ledger.jsonl          # Append-only governance event ledger
|-- manifest.json         # Control-surface and repository manifest
`-- README.md             # This file
```

## Subdirectories

| Directory | Purpose |
| --- | --- |
| `governance/` | Structured GovZero ontology and validation schema |
| `insights/` | Agent observations captured during work sessions |
| `lessons/` | Structured learning ledger scaffold for future compound-engineering work |
| `skills/` | Canonical skill definitions mirrored into agent control surfaces |

## File Conventions

| Path | Convention |
| --- | --- |
| `ledger.jsonl`, `insights/*.jsonl`, future `lessons/*.jsonl` | JSONL, append-only, UTF-8 |
| `manifest.json` | Repository governance manifest used by sync and audit surfaces |
| `governance/*.json` | Structured governance artifacts tracked in git |

See [Unified Ledger Schema](../docs/governance/GovZero/ledger-schema.md) for ledger field definitions and [Governance Registry Design](../docs/governance/GovZero/governance-registry-design.md) for ontology semantics.
