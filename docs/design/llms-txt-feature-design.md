# GZKit `llms.txt` Feature Design

**Purpose:** Define a proper gzkit-native `llms.txt` feature for package consumers and public docs.
**Status:** Draft
**Created:** 2026-04-18
**Last Updated:** 2026-04-18
**Temporary home:** `docs/design/` pending ADR authoring

---

## Summary

gzkit should treat `llms.txt` as a first-class documentation surface, not as a
hand-authored side file and not as a docs-plugin afterthought.

The feature should:

- derive a curated LLM-oriented documentation surface from gzkit docs
- publish public `/llms.txt` and `/llms-full.txt` artifacts for the docs site
- ship a package-owned snapshot with each gzkit release
- materialize that snapshot into the adopting project's root `.gzkit/`
- instruct adopting agents that `.gzkit/llms.txt` is the local onboarding entrypoint
- validate that the generated artifacts are present, current, and structurally coherent

This is a real product feature, not a one-off export script.

---

## Problem Statement

Today gzkit has rich documentation for humans, but package adopters do not get a
curated LLM-facing entrypoint when they install and initialize the package.

That creates several problems:

- The docs corpus is broader than what an adopting agent needs on first contact.
- The docs do not travel with the installed package.
- The current package build ships `src/gzkit`, not the repo-root docs tree.
- Adopting agents need a local, explicit, stable place to start.
- Public web discovery still matters because `llms.txt` consumers expect a
  discoverable site-root artifact.

The result is that gzkit can be easier for humans than for agents, even though
the project is explicitly agent-aware.

---

## Goals

- Build `llms.txt` artifacts from the real docs corpus rather than maintaining
  a second hand-authored documentation track.
- Make `.gzkit/llms.txt` available in every adopting project created or repaired
  by `gz init`.
- Publish standards-aligned `/llms.txt` and `/llms-full.txt` for the public docs site.
- Ship version-specific snapshots with the Python package so adopters do not
  depend on the docs repo being checked out locally.
- Provide deterministic docs discovery, generation, and validation.
- Keep the feature compatible with gzkit's existing package-resource to
  project-surface materialization model.

---

## Non-Goals

- User-local merge or override semantics for generated `llms` artifacts
- A generic standalone framework-agnostic `llms.txt` engine in v1
- Manual editing of `.gzkit/llms.txt` after init
- Replacing the existing docs site, MkDocs configuration, or documentation taxonomy
- Solving arbitrary third-party repository documentation extraction in v1

---

## External Guidance And Inspiration

gzkit should draw from open-source implementations, but should own the core
feature because none of the existing projects match gzkit's package-shipped +
project-materialized `.gzkit/` model.

| Project | Useful guidance | What to borrow | What not to copy blindly |
|---|---|---|---|
| [`llmstxt.org`](https://llmstxt.org/) / [`llms-txt`](https://github.com/AnswerDotAI/llms-txt) | Format and consumer expectations | file shape, summary/full split, context expansion semantics | generation architecture |
| [`mkdocs-llms-source`](https://pypi.org/project/mkdocs-llms-source/) | MkDocs-native discovery and multi-artifact generation | nav-derived graph discovery, `.md` page exports, output family design | ownership model; gzkit still needs package-shipped local surfaces |
| [`mkdocs-llmstxt`](https://github.com/pawamoy/mkdocs-llmstxt) | Earlier MkDocs plugin design | build-time emission of `/llms.txt` and `/llms-full.txt` | making MkDocs plugin state the canonical source of truth |
| [`sphinx-llms-txt`](https://pypi.org/project/sphinx-llms-txt/) | Cross-ecosystem precedent | summary/full artifact split | framework assumptions |
| [`fireproof-storage/llms.txt`](https://github.com/fireproof-storage/llms.txt) | Public artifact family | multiple output variants (`llms.txt`, `llms-full.txt`, compact variants) | repository-specific content policy |
| [`autodesk-platform-services/llmstxt`](https://github.com/autodesk-platform-services/llmstxt) | Multi-surface docs curation | structured selection from a broad docs corpus | custom domain assumptions |

### Design takeaway

Borrow:

- the format from `llms-txt`
- the discovery and export patterns from the MkDocs plugins
- the artifact-family pattern from Fireproof and Autodesk

Own:

- the canonical source policy
- the package-shipped snapshot
- the adopting-project `.gzkit/` materialization
- the validation and release integration

---

## Current State Constraints

### Package build constraint

The current wheel configuration ships `src/gzkit`:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/gzkit"]
```

That means repo-root assets such as `docs/` and `.gzkit/` are not packaged
wholesale today.

### Existing materialization pattern

gzkit already follows a consistent pattern:

- package-owned resources live under `src/gzkit/...`
- `gz init` materializes canonical surfaces into the adopting project's root
- examples today include templates, skills, personas, and generated agent surfaces

This feature should reuse that model rather than invent a parallel one.

### Docs platform constraint

The current docs site is MkDocs-backed. That makes a MkDocs-aware discovery
engine the right v1 choice.

### Product constraint

The adopting project's local `.gzkit/` copy is not optional. The public docs
site is useful, but not sufficient by itself.

---

## Proposed Feature Model

### Canonical inputs

The feature should be built from three canonical inputs:

1. `docs/**`
2. `mkdocs.yml`
3. a small gzkit-owned classification surface under `.gzkit/llms/`

Suggested source layout:

```text
.gzkit/llms/
├── manifest.json
├── sections.json
└── prompts.md              # optional authoring guidance, not runtime output
```

### Why a `.gzkit/llms/` source surface

`llms.txt` is a governed control surface, not just a docs-site plugin output.
The source configuration belongs with other canonical control surfaces under
`.gzkit/`, while the generated package resources belong under `src/gzkit/...`.

This mirrors existing doctrine:

- docs remain the source corpus
- `.gzkit` holds the canonical control instructions for how that corpus is surfaced
- packaged resources are generated release artifacts

---

## Artifact Family

The feature should generate four primary artifacts plus optional page mirrors.

| Artifact | Audience | Location | Purpose |
|---|---|---|---|
| `llms.txt` | Public agents/tools | docs site root | compact onboarding and link index |
| `llms-full.txt` | Public agents/tools | docs site root | expanded local-context substitute |
| `.gzkit/llms.txt` | Adopting project agents | project root `.gzkit/` | local first-contact entrypoint |
| `.gzkit/llms-full.txt` | Adopting project agents | project root `.gzkit/` | local expanded context when docs are unavailable |
| page mirrors | Public agents/tools | docs site root, e.g. `/llms-pages/*.md` | Markdown-friendly linked pages |

### Packaged snapshot artifacts

To support install-time and init-time materialization, the package should also
ship a versioned snapshot, for example:

```text
src/gzkit/resources/llms/
├── llms.txt
├── llms-full.txt
├── manifest.json
└── pages/
    ├── quickstart.md
    ├── runbook.md
    └── ...
```

The packaged snapshot is the bridge between source docs and the adopting
project's local `.gzkit/` surfaces.

---

## Architecture

## 1. Discovery

### Recommendation

Use a MkDocs-aware discovery engine in v1.

The discovery graph should combine:

- `mkdocs.yml` `nav` ordering for public section hierarchy
- file existence under `docs/`
- exclusions already enforced by MkDocs config
- `.gzkit/llms/manifest.json` classification metadata

### Why MkDocs-specific first

- gzkit already uses MkDocs
- the strongest open-source references are MkDocs-native
- nav order is meaningful operator intent
- "framework-agnostic from day one" adds abstraction cost before the real
  feature shape is validated

### Discovery output

The graph builder should emit a typed internal model with:

- canonical page ID
- source path
- title
- section
- summary/description
- inclusion tier
- ordering metadata
- output slug
- public URL
- local packaged mirror path

---

## 2. Curation And Selection

Not every docs page belongs in `llms.txt`.

The classification surface should support at least:

- `entrypoint`
- `core`
- `reference`
- `deep_reference`
- `exclude`

### Recommended default corpus

Include:

- quickstart
- runbook
- core concepts
- key command docs
- governance overview pages
- selected reference pages with high onboarding value

Exclude:

- transient design scratch documents
- internal historical debris
- deep audit artifacts
- narrow implementation records not useful to first-contact agents

### Important constraint

The feature should not require authors to maintain an entire parallel TOC.
The docs graph comes from docs. The classification surface only refines it.

---

## 3. Generation

The generator should produce:

- summary `llms.txt`
- expanded `llms-full.txt`
- page-level Markdown mirrors for linked pages
- packaged snapshot files under `src/gzkit/resources/llms/`

### `llms.txt` shape

The summary file should:

- identify gzkit and its purpose
- explain the artifact family briefly
- surface the most important sections first
- link to public page mirrors
- mention the paired `llms-full.txt`

### `llms-full.txt` shape

The full file should:

- begin with the same short project identity block
- then inline curated content from selected docs pages
- preserve stable section ordering
- preserve source attribution per included page
- remain deterministic across repeated runs

### Page mirrors

Public `llms.txt` should not link only to HTML pages. It should link to
Markdown-friendly mirror pages generated from the selected docs corpus.

Suggested public output layout:

```text
site/
├── llms.txt
├── llms-full.txt
└── llms-pages/
    ├── quickstart.md
    ├── runbook.md
    ├── concepts-gates.md
    └── ...
```

---

## 4. Package Distribution

The package should ship generated snapshots, not the raw docs tree.

### Why

- the package already ships `src/gzkit` resources, not repo-root docs
- adopters need a local surface after `gz init`
- release artifacts must be version-specific and deterministic

### Release/build rule

Every gzkit release should regenerate the packaged `llms` resources from the
current docs corpus before the version is finalized.

Version bumps without refreshed `llms` resources should fail validation.

---

## 5. Project Materialization

`gz init` should materialize packaged snapshots into the adopting project's root
`.gzkit/`.

Suggested target layout:

```text
.gzkit/
├── llms.txt
├── llms-full.txt
└── llms-meta.json
```

### `llms-meta.json`

This metadata file should record:

- gzkit package version that produced the artifacts
- source snapshot timestamp
- source docs build identifier or git commit when available
- checksum of generated files

This supports deterministic repair and drift checks without inventing
user-local merge semantics.

### Refresh policy

`gz init` repair mode should refresh local `llms` artifacts when:

- the files are missing
- the installed gzkit version changed
- the checksums do not match the packaged snapshot

### Managed-file policy

`.gzkit/llms.txt` and `.gzkit/llms-full.txt` are generated control surfaces.
They are not user-editable.

If local edits are detected, the system should fail closed or write a parallel
replacement candidate rather than silently merging.

Rejected: user override / merge semantics.

---

## 6. Agent Integration

Generated agent-facing surfaces should explicitly point to local `llms` artifacts.

### Required AGENTS.md addition

The generated `AGENTS.md` contract should include a brief note such as:

> LLM-oriented documentation entrypoints live in `.gzkit/llms.txt` and
> `.gzkit/llms-full.txt`. Consult them before broad repository search when you
> need gzkit workflow, command, or governance orientation.

### Why this matters

- it makes the surface discoverable to agents
- it reduces prompt-time ambiguity
- it gives adopting projects a single local pointer even when docs are not present

---

## Commands And Validation Surfaces

This feature should have explicit runtime surfaces rather than existing only as
release glue.

### Recommended command surfaces

<!-- gz-validate-skip: command-shape -->
- `gz llms build`
  - build public and packaged artifacts from docs + config
<!-- gz-validate-skip: command-shape -->
- `gz llms sync`
  - materialize packaged artifacts into local project `.gzkit/`
<!-- gz-validate-skip: command-shape -->
- `gz llms show`
  - show artifact status, source version, and drift summary

### Recommended validation surface

- `gz validate --llms`

Validation should check:

- docs graph discovery succeeds
- every included page resolves to a real source file
- every generated public artifact exists
- packaged snapshot matches the latest build output
- local `.gzkit` materialization matches the packaged snapshot
- broken links are rejected
- page mirrors exist for every linked page
- `llms-full.txt` section order matches the discovery graph
- generated files contain the expected metadata header

---

## Public And Local Parity Rules

The feature should enforce parity between public and local surfaces.

### Required parity

- local `.gzkit/llms.txt` matches packaged snapshot `llms.txt`
- local `.gzkit/llms-full.txt` matches packaged snapshot `llms-full.txt`
- packaged snapshot matches the public docs build output for the same version

### Allowed divergence

Only location-specific URLs or metadata fields may differ where required by
target environment.

Content drift between public, packaged, and local variants is a defect.

---

## Alternatives Considered

### 1. Hand-maintained `.gzkit/llms.txt`

Rejected.

Why:

- duplicates docs authoring
- drifts immediately
- violates "build from docs"

### 2. Third-party MkDocs plugin as the core feature

Rejected.

Why:

- solves public site generation, not package-shipped local surfaces
- makes MkDocs plugin state the canonical source of truth
- does not fit gzkit's `.gzkit/` control-surface model

### 3. Public site only

Rejected.

Why:

- adopters need a local root `.gzkit/` surface
- package consumers may not have docs locally
- a local agent entrypoint is part of the product requirement

### 4. Local `.gzkit/` only

Rejected.

Why:

- breaks public `llms.txt` discovery expectations
- wastes the strong open-source conventions around site-root publication

### 5. User-local override or merge semantics

Rejected.

Why:

- generated control surfaces should be deterministic
- merge behavior invites invisible drift
- the source of truth should be docs + `.gzkit/llms/` config, not local edits

---

## Suggested Decomposition

If promoted into ADR/OBPI work, the feature naturally decomposes into these
implementation slices:

| OBPI | Scope |
|---|---|
| 01 | Docs graph discovery + source manifest under `.gzkit/llms/` |
| 02 | `llms.txt` / `llms-full.txt` generator + page mirror export |
| 03 | Packaged resource emission under `src/gzkit/resources/llms/` |
| 04 | `gz init` / repair mode materialization into project `.gzkit/` |
| 05 | Agent-surface integration (`AGENTS.md` and mirrors) |
| 06 | `gz validate --llms` + release/version integration |

This decomposition keeps discovery, generation, package shipping, project
materialization, and validation independently testable.

---

## Recommendation

Build this as a proper gzkit feature with:

- MkDocs-aware docs discovery in v1
- canonical source config under `.gzkit/llms/`
- generated package resources under `src/gzkit/resources/llms/`
- public `/llms.txt` and `/llms-full.txt`
- local project `.gzkit/llms.txt` and `.gzkit/llms-full.txt`
- explicit AGENTS integration
- deterministic validation and release gating

The feature should borrow heavily from open-source precedents, but the core
architecture must remain gzkit-native because the critical requirement is not
just "publish `llms.txt`" — it is "ship a governed, package-owned, agent-facing
documentation surface into the adopting project's `.gzkit/`."

---

## Open Questions

These are legitimate follow-ups, but they should not block v1 design:

- Should page mirror export use source Markdown directly or rendered/normalized Markdown?
- Should the local `.gzkit/` copy include page mirrors in addition to `llms-full.txt`?
<!-- gz-validate-skip: command-shape -->
- Should `gz agent sync control-surfaces` refresh local `llms` artifacts, or should that remain owned by `gz llms sync` and `gz init` repair mode?
- Should non-MkDocs discovery adapters exist later, or should this remain intentionally MkDocs-scoped?
