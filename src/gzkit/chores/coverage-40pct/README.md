# Coverage >=40% Baseline

Maintain >=40% line coverage floor through periodic audits.

## Quick Start

```bash
uv run unittest-parallel -t . -s tests --buffer --coverage --coverage-source src/gzkit
uv run coverage report --fail-under=40
```

## Lane

**lite**
