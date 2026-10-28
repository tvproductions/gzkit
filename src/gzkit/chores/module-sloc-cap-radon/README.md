# Module Size Cap (Lizard)

Enforce module size against the `lizard_file_nloc` `block` band of the canonical
threshold table (`.gzkit/rules/complexity-thresholds.json`), with a shrink-only
ratchet in `data/module_size_grandfather.json`. The slug keeps its historical
Radon name.

## Quick Start

```bash
uv run python .gzkit/chores/module-sloc-cap-radon/check_module_size.py
```

## Lane

**lite**
