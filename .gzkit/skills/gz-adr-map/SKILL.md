---
name: gz-adr-map
description: Generate ADR→artifact traceability map via keyword/semantic matching.
compatibility: GovZero v6 framework; infers ADR-to-code mappings
metadata:
  skill-version: "1.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
opsdev_command: adr map
invocation: uv run -m opsdev adr map
---

# gz-adr-map

Infer ADR→artifact mappings via keyword/semantic matching.

**Command:** `uv run -m opsdev adr map`

**Layer:** Layer 1 — Evidence Gathering

---

## When to Use

- To discover which code artifacts relate to which ADRs
- Before auditing an ADR to understand its footprint
- To identify orphan code (artifacts without ADR coverage)
- To verify ADR scope matches implementation

---

## Invocation

```text
/gz-adr-map
/gz-adr-map --json
/gz-adr-map --check
```

**CLI equivalent:**

```bash
# Generate human-readable mapping
uv run -m opsdev adr map

# Emit JSON mapping for tooling
uv run -m opsdev adr map --json

# Fail if any ADR has score < 0.8 (CI gate)
uv run -m opsdev adr map --check

# Limit artifacts per ADR
uv run -m opsdev adr map --limit 5
```

---

## Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--json` | `false` | Emit JSON mapping instead of human-readable |
| `--check` | `false` | Fail if any ADR has confidence score < 0.8 |
| `--limit` | `10` | Max artifacts to show per ADR |

---

## How It Works

1. **Parse ADR** — Extract keywords, concepts, and file references from ADR prose
2. **Scan codebase** — Find files mentioning ADR keywords or concepts
3. **Score matches** — Rank artifacts by relevance (keyword density, path matching)
4. **Report** — Show top N artifacts per ADR with confidence scores

---

## Output Example

```text
ADR-0.0.19 (Manifest-Driven ETL)
  Score: 0.92
  Artifacts:
    - src/airlineops/warehouse/manifest.py (0.95)
    - src/airlineops/warehouse/loader.py (0.88)
    - tests/warehouse/test_manifest.py (0.91)

ADR-0.0.20 (Config Schema)
  Score: 0.78 ⚠️ (below threshold)
  Artifacts:
    - src/airlineops/config/schema.py (0.82)
    - config/settings.json (0.74)
```

---

## JSON Output Format

```json
{
  "ADR-0.0.19": {
    "score": 0.92,
    "artifacts": [
      {"path": "src/airlineops/warehouse/manifest.py", "score": 0.95},
      {"path": "src/airlineops/warehouse/loader.py", "score": 0.88}
    ]
  }
}
```

---

## CI Gate Usage

Use `--check` in CI to ensure ADRs have sufficient artifact coverage:

```bash
uv run -m opsdev adr map --check
# Exit 0 if all ADRs >= 0.8
# Exit 1 if any ADR < 0.8
```

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| gz-adr-autolink | Map via @covers decorators (explicit) |
| gz-adr-verification | Full ADR→tests report |
| gz-adr-check | Blocking evidence audit |

---

## References

- Command: `src/opsdev/commands/adr_subcommands.py`
