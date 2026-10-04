---
name: gz-constitute
description: Create constitution artifacts. Use when governance constitutions must be created or refreshed.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-27
metadata:
  skill-version: "0.3.0"
model: opus
---

# gz constitute

## Overview


> **Self-Escalation (opus-tier).** The dialogue with the operator stays in the main session: a subagent cannot ask the operator a question or hear the answer, and what the operator adds is this skill's primary input. When the session model is below opus-tier, you may spawn an `Agent` with `model="opus"` for a bounded drafting or QC track that needs no operator input — pass the operator's words verbatim and the relevant context (ADR IDs, OBPI IDs, prior decisions), and treat what it returns as a draft you verify, not as the operator-facing result.

Scaffold a constitution, then fill it with the operator. `gz constitute <name>`
(`constitute` in `src/gzkit/commands/init_cmd.py`):

- requires an initialized project (`.gzkit.json`); otherwise it exits 1;
- canonicalizes `name` to `CONSTITUTION-<SLUG>-<semver>`: a leading
  `CONSTITUTION-` is dropped, a trailing `-X.Y.Z` becomes the semver (default
  `1.0.0`), and the rest is stripped to alphanumerics and upper-cased, so
  `charter` becomes `CONSTITUTION-CHARTER-1.0.0` (GHI #216). A name with no
  alphanumeric character exits 1;
- renders the `constitution` template (`src/gzkit/templates/constitution.md`)
  with `status: Draft`, today's date and `--title` (default: the id) into
  `<paths.constitutions>/<id>.md`;
- appends one `constitution_created` ledger event, which makes the id a node in
  the `gz state` graph.

The scaffold holds placeholder principles and rules; the content comes from the
operator. It does not check for an existing file: a name that canonicalizes to
an existing id overwrites that file and appends a second event. `--dry-run`
prints the path and event it would write, whether or not the file exists, and
writes nothing.

## Workflow

1. Preview: `uv run gz constitute <name> --dry-run`. If the printed path already
   exists, stop — that constitution is revised in place, not re-scaffolded.
2. Create it: `uv run gz constitute <name> [--title "<title>"]`.
3. Draft each section the template requires with the operator — Purpose, Scope,
   Principles, Rules (requirement, rationale, verification), Exceptions,
   Amendments — using the operator's words. `required_headers` in
   `src/gzkit/schemas/constitution.json` is the authority for the sections and
   the permitted `status` values.
4. Validate: `uv run gz validate --documents` checks the frontmatter and
   headers against that schema. Capture the output to a file and read `$?`
   straight after it.
5. Report the id, path and validation result. Changing `status` from `Draft`
   is the operator's ratification, not the agent's.

## Example

```bash
uv run gz constitute charter --dry-run
uv run gz constitute charter --title "Project Charter"
uv run gz validate --documents
```
