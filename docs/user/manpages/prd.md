# gz prd

Create a new Product Requirements Document (PRD).

---

## Usage

```bash
gz prd <name> [OPTIONS]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | PRD slug (e.g., `my-feature` or `my-feature-1.0.0`), canonicalized to `PRD-<SLUG>-<semver>` |

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--title` | string | PRD title (defaults to the canonical id) |
| `--dry-run` | flag | Print the file and ledger event it would write; write nothing |

---

## What It Does

1. Requires an initialized project (`.gzkit.json`); exits 1 otherwise
2. Canonicalizes `name`: drops a leading `PRD-`, takes a trailing `-X.Y.Z` as the semver (default `1.0.0`), and upper-cases the rest stripped to alphanumerics (`my-feature-1.0.0` → `PRD-MYFEATURE-1.0.0`); a name with no alphanumeric character exits 1
3. Renders the PRD template with `status: Draft` and author prompts in the sections the operator must write, into `<paths.prd>/<id>.md`
4. Appends a `prd_created` ledger event; the id becomes a node in the `gz state` graph, and an ADR recorded with it as parent attaches beneath it

It does not check for an existing file: a name that canonicalizes to an existing id overwrites it and appends a second event. `gz validate --documents` checks the result against `src/gzkit/schemas/prd.json`.

---

## Example

```bash
# Basic usage
gz prd my-feature-1.0.0

# With title
gz prd my-feature-1.0.0 --title "My Awesome Feature"

# Dry run
gz prd my-feature-1.0.0 --dry-run
```

---

## Output

The path printed is absolute and follows `paths.prd` in `.gzkit.json` (this repository: `docs/design/prd`).

```
$ gz prd my-feature-1.0.0 --dry-run
Dry run: no files will be written.
  Would create PRD: /path/to/repo/docs/design/prd/PRD-MYFEATURE-1.0.0.md
  Would append ledger event: prd_created (PRD-MYFEATURE-1.0.0)

$ gz prd my-feature-1.0.0
Created PRD: /path/to/repo/docs/design/prd/PRD-MYFEATURE-1.0.0.md
```

---

## PRD Template

The created PRD contains:

- **Frontmatter**: `id`, `status`, `semver`, `date`
- **Problem Statement**, **North Star**, **Invariants**: author prompts for the operator to answer
- **Gate Mapping**: the gate-to-lane table
- **Q&A Transcript**: an author prompt for the interview that produced the PRD
- **Attestation Block**: one `Pending` row for the semver

`required_headers` in `src/gzkit/schemas/prd.json` is the authority for the required sections.

---

## When to Use

Create a PRD when:

- Starting a new product or major feature
- Defining the project-level intent that ADRs are planned against

For an interactive version that asks each question and writes the answers into the same template, use `gz interview prd`.

---

## Workflow

1. Create a PRD with `gz prd` (this command) and write its sections with the operator
2. Plan ADRs against it with `gz plan create`
3. Create OBPI briefs under each ADR with `gz specify --parent ADR-...`
4. Implement and attest
