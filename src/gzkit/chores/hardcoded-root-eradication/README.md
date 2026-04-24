# Config-First Enforcement (Anti-Vibe-Code)

Enforce 12-factor config-first discipline. Eradicate hardcoded paths, magic
numbers, and structural assumptions that should flow from manifest/config.

## Quick Start

```bash
grep -rn "Path(__file__).*parents" src/
uv run gz check-config-paths
```

## Lane

**lite**
