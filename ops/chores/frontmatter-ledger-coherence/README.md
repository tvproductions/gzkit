# Frontmatter-Ledger Coherence Audit

Validate YAML frontmatter (id, parent, lane) against ledger truth. Detects
drift where derived frontmatter fields no longer match the ledger's artifact
graph.

## Quick Start

```bash
uv run gz validate --frontmatter
```

## Lane

**lite**
