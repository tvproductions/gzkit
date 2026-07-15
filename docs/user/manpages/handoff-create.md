# gz handoff create

Author a handoff, fail-closed through the validation gate (ADR-0.0.65).

---

## Overview

`gz handoff create` authors a handoff document and routes it through the
fail-closed `validate_handoff_document` gate (`gzkit.handoff_api.create_handoff`)
before it is written. This is the ADR-0.0.65 § Decision #3 contract: handoff
authoring goes through the validation gate instead of hand-written markdown.

The `--decisions` text becomes the mandatory `## Decisions Made` section;
`--summary`, when given, becomes `## Current State Summary`. On **any** validation
violation nothing is written and the verb exits 1 — the refusal is the correct
behavior. On success the document is written to `.gzkit/handoffs/` and its path
is reported.

---

## Usage

```
gz handoff create --adr ADR --slug SLUG --agent AGENT --decisions TEXT
                  [--branch BRANCH] [--summary TEXT] [--obpi OBPI]
                  [--continues-from REF] [--session-id ID] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--adr ADR` | Parent ADR id, `ADR-X.Y.Z` (required). |
| `--slug SLUG` | Filename slug for the handoff (required). |
| `--agent AGENT` | Authoring agent identity (required). |
| `--decisions TEXT` | `Decisions Made` section body (required). |
| `--branch BRANCH` | Branch name (default: current git branch). |
| `--summary TEXT` | `Current State Summary` section body. |
| `--obpi OBPI` | OBPI id this handoff scopes to. |
| `--continues-from REF` | Prior handoff reference (chain link). |
| `--session-id ID` | Session id. |
| `--json` | Emit `{"path": "..."}` instead of the human path line. |

---

## Example

```bash
uv run gz handoff create --adr ADR-0.0.65 --slug my-work --agent g0 \
  --decisions "Chose the adapter approach over re-implementing handoff logic."
```

Observed output (a document was written under the canonical store):

```
.gzkit/handoffs/20260715T030000Z-my-work.md
```

A validation violation is fail-closed — nothing is written and the verb exits 1:

```bash
uv run gz handoff create --adr ADR-BOGUS --slug x --agent g0 --decisions "d"
```

```
Refusing to write handoff: Refusing to write invalid handoff; violations: ...
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Handoff validated and written; path reported. |
| 1 | Validation refusal (nothing written) or a user/config error. |
