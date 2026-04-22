# gz justify

Produce a pre-execution reasoning scaffold (8 sections) for a GHI, OBPI, or
draft anchor. See parent ADR-0.0.19 for the walkthrough protocol. Full
operator guidance, runbook entries, and BDD scenarios ship in a later OBPI
under this ADR; this page is a Gate 3 stub.

## Usage

```text
uv run gz justify <anchor> [--save | --output PATH] [--related A,B] \
                  [--draft TEXT --draft-slug SLUG]
```

## Positional

- `anchor` — Anchor identifier (`GHI-<N>`, `#<N>`, or `OBPI-X.Y.Z-NN`). Omit
  when using `--draft`.

## Options

- `--save` — Write the rendered scaffold to
  `artifacts/justify/<slug>-<ISO8601-basic>.md`.
- `--output PATH` — Write the scaffold to an explicit path. Fails if the path
  exists (there is no `--force` in v1).
- `--related A,B` — Comma-separated list of related anchors to feed into
  evidence gathering.
- `--draft TEXT` — Literal draft text in place of a resolvable anchor.
- `--draft-slug SLUG` — Slug used to name the `--save` output when combined
  with `--draft`. Required when both `--save` and `--draft` are set.

## Exit Codes

- `0` — Scaffold produced successfully.
- `1` — User or configuration error (bad anchor, ADR anchor, missing
  `--draft-slug`, `--output` path already exists, neither anchor nor
  `--draft` supplied).
- `2` — System or I/O error (resolver failure, filesystem write failure).

## Example

```bash
uv run gz justify GHI-232
uv run gz justify GHI-232 --save
uv run gz justify --draft "proposal text" --save --draft-slug my-idea
```
