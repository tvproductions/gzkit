# gz knowledge generate

Emit the OKF knowledge bundle to the governance tracer slice.

---

## Usage

```bash
gz knowledge generate
```

---

## Description

Generate an OKF-conformant knowledge bundle over the governance tracer slice
(state doctrine, trust doctrine, agent-contract rationale, active campaign).
The bundle provides typed YAML frontmatter and markdown links so agents can
navigate governance documentation without whole-corpus reads.

The bundle is written to `.gzkit/governance/knowledge/` with a stable root
`index.md` and one concept document per tracer-slice source. Frontmatter carries
`type`, `title`, `description`, and `resource` fields; each concept doc links
back to its canonical source document.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Bundle generated successfully |
| 2 | System/IO error (permission denied, disk full, source docs missing) |

---

## Examples

```bash
# Generate the knowledge bundle
uv run gz knowledge generate

# Generate and check the bundle manifest
uv run gz knowledge generate && ls -la .gzkit/governance/knowledge/
```

---

## See Also

- `gz knowledge refresh` — Re-generate the bundle idempotently
- `docs/governance/okf-cms-knowledge-structure-note-2026-06-23.md` — Design rationale
- `src/gzkit/knowledge/` — Generator module
