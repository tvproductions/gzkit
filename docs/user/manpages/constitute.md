# gz constitute

Create a constitution document.

---

## Usage

```bash
gz constitute <name> [OPTIONS]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Constitution slug (e.g., `charter`), canonicalized to `CONSTITUTION-<SLUG>-<semver>` |

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--title` | string | Constitution title (defaults to the canonical id) |
| `--dry-run` | flag | Print the file and ledger event it would write; write nothing |

---

## What It Does

1. Requires an initialized project (`.gzkit.json`); exits 1 otherwise
2. Canonicalizes `name`: drops a leading `CONSTITUTION-`, takes a trailing `-X.Y.Z` as the semver (default `1.0.0`), and upper-cases the rest stripped to alphanumerics (`charter` → `CONSTITUTION-CHARTER-1.0.0`); a name with no alphanumeric character exits 1
3. Renders the constitution template (Purpose, Scope, Principles, Rules, Exceptions, Amendments) with `status: Draft` into `<paths.constitutions>/<id>.md`
4. Appends a `constitution_created` ledger event

It does not check for an existing file: a name that canonicalizes to an existing id overwrites it and appends a second event. `gz validate --documents` checks the result against `src/gzkit/schemas/constitution.json`.

---

## Example

```bash
# Create a constitution
gz constitute charter

# With title
gz constitute charter --title "Project Charter"

# Dry run
gz constitute charter --dry-run
```

---

## Output

The path printed is absolute and follows `paths.constitutions` in `.gzkit.json` (this repository: `docs/design/constitutions`).

```
$ gz constitute charter --dry-run
Dry run: no files will be written.
  Would create constitution: /path/to/repo/docs/design/constitutions/CONSTITUTION-CHARTER-1.0.0.md
  Would append ledger event: constitution_created (CONSTITUTION-CHARTER-1.0.0)

$ gz constitute charter
Created constitution: /path/to/repo/docs/design/constitutions/CONSTITUTION-CHARTER-1.0.0.md
```
