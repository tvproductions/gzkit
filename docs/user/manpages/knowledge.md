# gz knowledge

Generate or refresh the OKF knowledge bundle for documentation orientation.

---

## Usage

```bash
gz knowledge generate | refresh
```

---

## Description

Generates an OKF-conformant markdown bundle over the governance tracer slice
(state doctrine, trust doctrine, agent-contract rationale, active campaign).
The bundle provides typed YAML frontmatter (type/title/description/resource)
and markdown links so agents can traverse documentation without whole-corpus reads.

### Subcommands

- `generate` — Emit the bundle to `.gzkit/governance/knowledge/`
- `refresh` — Re-generate the bundle idempotently from current sources (produces byte-identical output on unchanged sources)

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Bundle generated successfully |
| 2 | System/IO error (permission denied, disk full, source docs missing) |

---

## Examples

```bash
# Generate the bundle
uv run gz knowledge generate

# Refresh from current sources (idempotent)
uv run gz knowledge refresh
```

---

## See Also

- `docs/governance/okf-cms-knowledge-structure-note-2026-06-23.md` — Design rationale
- `src/gzkit/knowledge/` — Generator module
