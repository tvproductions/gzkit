# gz justify

Render an 8-section pre-execution reasoning walkthrough scaffold for a
GHI, OBPI, or draft anchor. The CLI is deterministic — every byte of
the scaffold is produced by the renderer in `src/gzkit/justify/`, never
by an LLM. The `validate` subverb reverse-parses a filled walkthrough
back into the same Pydantic model used for rendering, gating completion
on whether every section was filled.

See parent ADR-0.0.19 for the walkthrough protocol and the operator
flow that ties scaffolding to OBPI Key Proof and ADR attestation.

---

## Usage

```bash
# Parent verb — render the scaffold
gz justify <anchor> [--save | --output PATH] [--related A,B] \
                    [--draft TEXT --draft-slug SLUG]

# Validate subverb — reverse-parse a filled walkthrough
gz justify validate <file> [--json]
```

---

## Anchor Types

| Anchor | Form | Example |
|--------|------|---------|
| GHI issue | `GHI-<N>` or `#<N>` | `gz justify GHI-232` |
| OBPI brief | `OBPI-X.Y.Z-NN` | `gz justify OBPI-0.0.19-05` |
| Draft text | omit anchor; pass `--draft` | `gz justify --draft "..." --draft-slug my-idea` |

ADR anchors are intentionally rejected (exit 1). ADRs are the doctrine
substrate; reasoning walkthroughs attach to in-flight work units (GHIs
and OBPIs) or pre-decision drafts.

---

## Options

Parent verb (`gz justify <anchor>`):

| Flag | Description |
|------|-------------|
| `--save` | Write scaffold to `artifacts/justify/<slug>-<ts>.md`. |
| `--output PATH` | Write scaffold to an explicit path; fails if exists. |
| `--related A,B` | Comma-separated related anchors for evidence context. |
| `--draft TEXT` | Literal draft text in place of a resolvable anchor. |
| `--draft-slug SLUG` | Slug used to name `--save` output for `--draft`. |

`validate` subverb (`gz justify validate <file>`):

| Flag | Description |
|------|-------------|
| `--json` | Emit `ValidateResult` JSON instead of a sentence. |

Common to both:

| Flag | Description |
|------|-------------|
| `--quiet`, `-q` | Suppress non-error output. |
| `--verbose`, `-v` | Enable verbose output. |
| `--debug` | Enable debug mode with full tracebacks. |

---

## Exit Codes

Parent verb:

| Code | Meaning |
|------|---------|
| 0 | Scaffold rendered. |
| 1 | User/config error (bad anchor, ADR anchor, missing `--draft-slug`, `--output` exists, neither anchor nor `--draft` supplied). |
| 2 | System or I/O error (resolver failure, write failure). |

`validate` subverb:

| Code | Meaning |
|------|---------|
| 0 | Parseable and complete (no `_[To be filled]_` blocks). |
| 1 | Parseable but incomplete (unfilled section names listed). |
| 2 | Unparseable markdown. |

---

## Operator Flow

A typical walkthrough lifecycle, from anchor to attestation:

1. **Resolve and scaffold.** Pick the anchor for the work in flight
   (`GHI-N` for a defect, `OBPI-X.Y.Z-NN` for an OBPI implementation
   pass, or `--draft` for pre-decision exploration). Run with `--save`
   so the artifact lands under `artifacts/justify/` and survives the
   session:

   ```bash
   uv run gz justify OBPI-0.0.19-05 --save
   ```

2. **Fill the scaffold.** Open the saved file and replace each
   `_[To be filled]_` block with grounded reasoning that cites the
   evidence the renderer gathered (matching rules, ledger events,
   recent commits, related anchors).

3. **Validate the filled artifact.** Before citing the walkthrough in
   downstream evidence, confirm completion:

   ```bash
   uv run gz justify validate artifacts/justify/obpi-0.0.19-05-*.md
   ```

   Exit 0 means every section is filled. Exit 1 lists which sections
   are still empty so the operator can finish before attesting.

4. **Cite in OBPI Key Proof or ADR Evidence.** The validated artifact
   path is suitable for inclusion in OBPI Key Proof or ADR Evidence
   sections — it preserves the reasoning the operator did before
   implementation, not after.

---

## Troubleshooting

- **`--draft` + `--save` exits with code 1 ("missing --draft-slug").**
  When both flags are set, `--draft-slug SLUG` is mandatory because
  the renderer cannot derive a save path from anonymous draft text.
  Re-run with `--draft-slug <slug>`. The slug becomes the prefix of
  the saved filename.
- **ADR anchor exits 1.** ADRs are not valid anchors for justify.
  Use the GHI or OBPI under the ADR instead, or `--draft` for
  pre-decision text that does not yet have a tracked anchor.
- **`--output PATH` exits 1 ("path already exists").** There is no
  `--force` flag in v1. Either pick a fresh path, delete the existing
  file, or use `--save` (which timestamps the filename).

---

## When to Use

- The OBPI brief is ambiguous and self-reported confidence is below
  the Prime Directive invariant 11 threshold (90%).
- `gz adr evaluate` returned a low score and the upstream skill
  suggested running justify before continuing.
- `gz obpi pipeline` Stage 1→2 confidence gate routed you here.
- A free-text proposal needs structured reasoning before it becomes a
  draft GHI or OBPI.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| `gz adr evaluate` | Low scores suggest running `gz justify`. |
| `gz obpi pipeline` | Stage 1→2 confidence gate routes here. |
| `gz attest` | The validated walkthrough is suitable evidence. |
