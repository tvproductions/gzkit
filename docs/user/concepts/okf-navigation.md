# OKF Knowledge Navigation

The OKF (Open Knowledge Format) bundle at `.gzkit/governance/knowledge/index.md`
is the navigation entry point for gzkit's orientation knowledge layer.

## What the OKF bundle is (and is not)

The bundle is an **orientation aid** — a typed, self-describing map over gzkit's
governance doctrine. It helps agents find the relevant explanatory document
without reading the whole corpus.

The bundle is **not** an authority surface. Never cite OKF frontmatter, tags, or
links as proof of a governance claim. For evidence, always cite the canonical
source doc (the `resource:` target), the ledger, or an ADR.

## The three-step progressive-disclosure path

1. **Start at the bundle root** — `.gzkit/governance/knowledge/index.md`
   This file lists all concept docs in the bundle as markdown links.

2. **Follow a concept link** — each concept doc carries typed frontmatter:
   `type`, `title`, `description`, and a `resource:` field naming the
   canonical source document.

3. **Follow the `resource:` link** — this is the canonical source. Read and
   cite it; the OKF concept doc is a pointer, not the authority.

## Example navigation

```bash
# Step 1: inspect the bundle root
cat .gzkit/governance/knowledge/index.md

# Step 2: open a concept doc (e.g. trust-doctrine)
cat .gzkit/governance/knowledge/trust-doctrine.md

# Step 3: read the canonical source named in resource:
cat docs/governance/trust-doctrine.md
```

## Keeping the bundle current

After editing a tracer-slice source doc, refresh the bundle:

```bash
uv run gz knowledge refresh
```

The bundle is generated and additive; the source docs are never modified by the
generator.
