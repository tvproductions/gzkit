# gz handoff create

Author a handoff, fail-closed through the validation gate (ADR-0.0.65).

---

## Overview

`gz handoff create` authors a handoff document and routes it through the
fail-closed `validate_handoff_document` gate (`gzkit.handoff_api.create_handoff`)
before it is written. This is the ADR-0.0.65 § Decision #3 contract: handoff
authoring goes through the validation gate instead of hand-written markdown.

Each of the seven required sections is filled by its own flag. **All seven must be
populated**: a section left unsupplied renders as an empty heading, and the gate
refuses an empty required section (GHI #692). On **any** validation violation
nothing is written and the verb exits 1 — the refusal is the correct behavior. On
success the document is written to `.gzkit/handoffs/` and its path is reported.

Until GHI #692, only `--decisions` and `--summary` existed while seven sections
were required, so the default invocation emitted five empty headings — and
`validate_handoff_document` checked that each heading was *present*, never that it
carried a body. The result passed. Four handoffs authored that way are frozen in
`data/handoff_section_grandfather.json` (shrink-only); they preserve no context
despite having passed the gate.

---

## Usage

```
gz handoff create --slug SLUG --agent AGENT --decisions TEXT [--adr ADR]
                  [--summary TEXT] [--context TEXT] [--next-steps TEXT]
                  [--pending TEXT] [--verification TEXT] [--evidence TEXT]
                  [--branch BRANCH] [--obpi OBPI]
                  [--continues-from REF] [--session-id ID] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--adr ADR` | Parent ADR id, `ADR-X.Y.Z`. Omit for work with no parent ADR — a design session, triage pass, or GHI burndown (GHI #709). When supplied it must match the format. |
| `--slug SLUG` | Filename slug for the handoff (required). |
| `--agent AGENT` | Authoring agent identity (required). |
| `--decisions TEXT` | `Decisions Made` section body (required). Lead each entry with `[operator-ruled]` or `[agent-chose]` — see § Decision attribution. |
| `--summary TEXT` | `Current State Summary` section body. |
| `--context TEXT` | `Important Context` section body. |
| `--next-steps TEXT` | `Immediate Next Steps` section body. |
| `--pending TEXT` | `Pending Work / Open Loops` section body. |
| `--verification TEXT` | `Verification Checklist` section body. |
| `--evidence TEXT` | `Evidence / Artifacts` section body. Backtick-quoted paths must exist in committed state. |
| `--branch BRANCH` | Branch name (default: current git branch). |
| `--obpi OBPI` | OBPI id this handoff scopes to. |
| `--continues-from REF` | Prior handoff reference (chain link). Omitting it in a directory that already holds handoffs makes this handoff a chain root inheriting **zero** settled rulings — the command warns and names the newest candidate (GHI #717). |
| `--session-id ID` | Session id. |
| `--json` | Emit `{"path": "..."}` instead of the human path line. |

Only `--decisions` is argparse-required; the other six section flags are enforced
by the validation gate, so their absence is a refusal with every empty section
named at once rather than one error at a time.

---

## Decision attribution and settled rulings (GHI #696)

Lead each `--decisions` entry with `[operator-ruled]` or `[agent-chose]`. Matching
is case- and spacing-tolerant. An unmarked entry parses as **unattributed**: it is
never promoted to a ruling nor demoted to a preference, and it does **not** carry
forward — so an unmarked operator ruling is a ruling the next session will
re-argue.

The attribution drives a self-populating channel. `create_handoff` composes the
optional `## Settled Rulings` section by construction from the newest predecessor:
its carried entries plus its `[operator-ruled]` decisions, de-duplicated. A ruling
booked once keeps arriving, so it is never re-filed as an open loop and
re-adjudicated. **In the normal case you do not touch this section at all.**

```bash
uv run gz handoff create --adr ADR-0.0.65 --slug tier-close --agent g0 \
  --decisions "- [operator-ruled] Defer #641 to Movement IV.
- [agent-chose] Reused the lane-aware helper rather than masking in context." \
  ...
```

The successor handoff then carries, without anyone authoring it:

```markdown
## Settled Rulings

- Defer #641 to Movement IV.
```

`Settled Rulings` is deliberately **not** a required section: the
`handoff-documents` gate validates every post-cutover entry in `.gzkit/handoffs/`,
so making it required would fail the entire existing corpus.

### `--settled` — seating a late ruling

Composition happens at authoring time, so a ruling the operator issues **after** a
session's handoff is already committed has no home in that handoff. The next
handoff is the only seat, and `--settled` is it (repeatable):

```bash
uv run gz handoff create --adr ADR-0.0.65 --slug next-session --agent g0 \
  --settled "Reframe #580 to truncation survival." \
  --decisions "- [agent-chose] Resumed the tier." \
  ...
```

`--settled` **unions** with the carried set — it never replaces it. Carried entries
render first (oldest-booked-first reads as a history), then newly seated ones,
de-duplicated on text so re-seating an already-carried ruling is a no-op.

Replacing rather than unioning would drop every ruling booked before the late one,
turning the settled channel into a fresh instance of the decay it exists to stop.
That was a real defect in the first cut of this feature; the union is pinned by
`test_author_supplied_ruling_does_not_drop_carried_rulings`.

The flag is an escape hatch for a timing gap, not part of the normal flow. If you
find yourself passing it routinely, the rulings are arriving outside the handoff
cycle and belong in a durable ruling store — campaign Movement D box 3
(`ruling_issued` / `ruling_superseded` typed events, with this section as a
rendered projection).

---

## Example

All seven sections supplied — the document is written under the canonical store:

```bash
uv run gz handoff create --adr ADR-0.0.65 --slug my-work --agent g0 \
  --summary "Landed the create-side section flags." \
  --context "The gate refuses empty sections as of GHI #692." \
  --decisions "Chose the adapter approach over re-implementing handoff logic." \
  --next-steps "1. Run uv run gz check." \
  --pending "None." \
  --verification "uv run gz check" \
  --evidence "The ledger completion receipt."
```

Observed output:

```
.gzkit/handoffs/20260717T003013Z-my-work.md
```

Omitting the six non-required section flags is fail-closed — nothing is written,
the verb exits 1, and every empty section is named at once:

```bash
uv run gz handoff create --adr ADR-0.0.65 --slug my-work --agent g0 \
  --decisions "Chose the adapter approach."
```

```
Refusing to write handoff: Refusing to write invalid handoff; violations: Empty
required section: Current State Summary; Empty required section: Important
Context; Empty required section: Immediate Next Steps; Empty required section:
Pending Work / Open Loops; Empty required section: Verification Checklist; Empty
required section: Evidence / Artifacts
```

A malformed frontmatter value is refused the same way:

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
