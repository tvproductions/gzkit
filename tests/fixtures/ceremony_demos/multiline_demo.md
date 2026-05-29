---
id: OBPI-FIXTURE-multiline-demo
parent: ADR-FIXTURE
item: 1
lane: Lite
status: Draft
---

# Fixture brief: multi-line demo extraction

Fixture for `brief_commands.extract_fenced_commands` and
`ceremony_data._commands_from_demo_sections` regression tests (GHI #539). The
`## Demo` section below holds one single-line command followed by a multi-line
`python -c "…"` construct that the legacy per-line extractor would shred.

## Demo

```bash
uv run gz status --json
uv run python -c "
from pathlib import Path
print('multi-line demo body', Path('.').name)
"
```
