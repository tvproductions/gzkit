# Coverage Floor Baseline

Maintain line coverage at or above `thresholds.coverage_floor` in `.gzkit/manifest.json` through periodic audits.

## Quick Start

```bash
uv run unittest-parallel -t . -s tests --buffer --coverage --coverage-source src/gzkit
uv run python .gzkit/chores/coverage-40pct/check_coverage_floor.py
```

## Lane

**lite**
