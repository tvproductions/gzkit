# gz justify

Pre-execution reasoning walkthrough scaffold.

## NAME

gz justify — render an 8-section pre-execution reasoning walkthrough for
a GHI, OBPI, or draft anchor; reverse-parse a filled walkthrough.

## SYNOPSIS

```text
gz justify <anchor> [--save | --output PATH] [--related A,B] \
                    [--draft TEXT --draft-slug SLUG]
gz justify validate <file> [--json]
```

## DESCRIPTION

`gz justify` is the deterministic pre-execution reasoning surface
introduced by ADR-0.0.19. The parent verb resolves an anchor (a GHI
issue, an OBPI brief, or a free-text draft) and renders an 8-section
walkthrough scaffold whose section titles, section ordering, and anchor
evidence are fixed by the renderer. The CLI never invokes a language
model — every byte of the scaffold is produced by the deterministic
renderer in `src/gzkit/justify/`, and every citation is grounded in the
evidence the resolver gathered for that anchor.

The `validate` subverb accepts a filled walkthrough markdown file and
reverse-parses it into the same Pydantic model used for rendering.
Validate exit semantics differ from the parent verb:

- `0` parseable and complete (no `_[To be filled]_` blocks remain)
- `1` parseable but incomplete (one or more sections are still
  unfilled — the unfilled section names are listed on stderr)
- `2` unparseable markdown (frontmatter or section headings are
  malformed beyond the renderer's grammar)

Use the parent verb at planning time to scaffold a walkthrough; use
`validate` at attestation time to confirm the operator filled it before
citing the artifact in OBPI Key Proof.

## OPTIONS

Parent verb (`gz justify <anchor>`):

- `--save` — Write scaffold to
  `artifacts/justify/<slug>-<timestamp>.md`.
- `--output PATH` — Write scaffold to an explicit path; fails if the
  path already exists (no `--force` in v1).
- `--related A,B` — Comma-separated related anchors for evidence.
- `--draft TEXT` — Literal draft text in place of a resolvable anchor.
- `--draft-slug SLUG` — Slug used to name `--save` output when
  `--draft` is set. Required when both `--save` and `--draft` are set.

`validate` subverb (`gz justify validate <file>`):

- `--json` — Emit `ValidateResult` JSON instead of a sentence summary.

Common (both):

- `--quiet`, `-q` — Suppress non-error output.
- `--verbose`, `-v` — Enable verbose output.
- `--debug` — Enable debug mode with full tracebacks.

## EXIT STATUS

Parent verb (`gz justify <anchor>`):

- `0` — Scaffold rendered successfully.
- `1` — User/config error: bad anchor, ADR anchor rejected, missing
  `--draft-slug`, `--output` path already exists, or neither anchor
  nor `--draft` supplied.
- `2` — System or I/O error: resolver failure, filesystem write
  failure.

`validate` subverb (`gz justify validate <file>`):

- `0` — Parseable and complete (no `_[To be filled]_` blocks remain).
- `1` — Parseable but incomplete (unfilled section names listed on
  stderr).
- `2` — Unparseable markdown (frontmatter or section headings
  malformed beyond the renderer's grammar).

## EXAMPLES

```bash
# Resolve a GHI issue and render the scaffold to stdout
gz justify GHI-232

# Resolve an OBPI brief and persist the scaffold under artifacts/justify/
gz justify OBPI-0.0.19-05 --save

# Scaffold a free-text draft (saved with the supplied slug)
gz justify --draft "proposal text" --save --draft-slug my-idea

# Validate a filled walkthrough (exit 0/1/2 per EXIT STATUS table above)
gz justify validate artifacts/justify/my-idea-2026-04-22T05-15-00.md

# Machine-readable validate output
gz justify validate path/to/walkthrough.md --json
```

## SEE ALSO

- [`gz-adr-evaluate`](../skills/gz-adr-evaluate.md) — low-score output
  suggests this command for low-confidence anchors
- [`gz-obpi-pipeline`](../skills/gz-obpi-pipeline.md) — Stage 1→2
  confidence gate routes operators here when self-reported confidence
  is below the Prime Directive invariant 11 threshold
- ADR-0.0.19 — pre-execution reasoning walkthrough doctrine
