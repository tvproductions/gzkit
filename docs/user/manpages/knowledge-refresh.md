# gz knowledge refresh

Re-generate the OKF knowledge bundle idempotently from current sources.

---

## Usage

```bash
gz knowledge refresh
```

---

## Description

Re-generate the OKF knowledge bundle from current governance documentation.
Running refresh twice on unchanged sources produces byte-identical output,
ensuring deterministic and idempotent operator-driven bundle updates.

Use this command after editing governance documentation to reflect the changes
in the knowledge bundle. The bundle is regenerated with current frontmatter,
links, and index; existing entries are updated or added as needed.

---

## Idempotency Guarantee

When run twice on unchanged source documentation, the resulting bundle files
are byte-identical. This property makes refresh safe for automated governance
pipelines and ensures operators can re-run the command without side effects.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Bundle refreshed successfully |
| 2 | System/IO error (permission denied, disk full, source docs missing) |

---

## Examples

```bash
# Refresh the knowledge bundle after editing docs
uv run gz knowledge refresh

# Verify idempotency: refresh twice and check no changes
uv run gz knowledge refresh && uv run gz knowledge refresh && git diff .gzkit/knowledge/
```

---

## See Also

- `gz knowledge generate` — Generate the knowledge bundle from scratch
- `docs/governance/okf-cms-knowledge-structure-note-2026-06-23.md` — Design rationale
- `src/gzkit/knowledge/` — Generator module
