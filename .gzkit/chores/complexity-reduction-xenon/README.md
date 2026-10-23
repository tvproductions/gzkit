# Complexity Reduction (C/C/C ceiling)

Reduce cyclomatic complexity to meet the Lizard C/C/C ceiling, held at the
`max-complexity` Ruff reads, and shrink the cognitive-complexity baseline gzkit holds
at the ceiling `.gzkit.json` declares.
The slug keeps its historical `xenon` name; xenon was retired in RO-9 tranche 4.

## Quick Start

```bash
uv run gz validate --complexity-ceiling
uv run python -m gzkit.complexity.cognitive src/gzkit --top 20
```

## Lane

**lite**
