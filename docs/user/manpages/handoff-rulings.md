# gz handoff rulings

Read the append-only settled-ruling corpus (GHI #838).

---

## Overview

`gz handoff rulings` is a read-only projection over
`.gzkit/handoffs/rulings.jsonl`, the append-only store that holds every operator
ruling booked across sessions. It never writes: rulings are booked by
`gz handoff create`, which composes them from the predecessor's carried corpus
and the `[operator-ruled]` decisions that predecessor booked.

**Why the corpus is not in the handoff any more.** Rulings used to be
transported by *copying prose*: each session read them out of the predecessor's
rendered body and re-embedded all of them in its own. Measured on
`20260822T132232Z`, that was 98,247 of 107,480 bytes — **91.4% of the
document** — and seven authored handoffs over two days spent 687,729 bytes
shipping a corpus that is conceptually one list. A handoff now carries a count
and a pointer; this verb reads what it points at.

**Nothing retires.** The retention question GHI #838 poses — *should a booked
ruling ever stop carrying forward* — is answered **no**. The corpus is
append-only and no ruling is ever dropped, aged out, or collapsed. What changed
is the transport, not the retention.

**Ruling identity is deliberately narrow.** Two entries are the same ruling only
when they differ in characters that carry no meaning — quote glyph, whitespace,
case. Nothing that could distinguish one ruling from another is folded, because
the two failure directions are not symmetric: a duplicate is visible and
harmless, while collapsing two genuinely distinct rulings drops a booked
operator ruling silently. GHI #838 explicitly rejects a fix that widens this.

---

## Usage

```
gz handoff rulings [--limit N] [--search TEXT] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--limit N` | Show only the newest `N` rulings. Default: all. |
| `--search TEXT` | Show only rulings containing `TEXT` (case-insensitive). |
| `--json` | Emit the rulings as a JSON array of strings. |

---

## Examples

Read the whole corpus:

```
$ uv run gz handoff rulings
settled rulings — do NOT re-open (461):
  - Work the degrading tier starting with #696 (verbatim authorization booked
via gz handoff authorize, session 81765765).
  ...
```

The newest few, which is what a resuming session has not already met:

```
$ uv run gz handoff rulings --limit 3
settled rulings — do NOT re-open (3):
  - Discharge GHI #852 rather than close it administratively (verbatim: 'close
852', then 'why close something thst yoy didn't fix?' -- spelling preserved).
  - Fix the red build immediately (verbatim: 'fix shit now').
  - Sync, then address the handoff volume (verbatim: 'sync it and fix this
nonsense').
```

Find whether a question was already ruled on, before re-arguing it:

```
$ uv run gz handoff rulings --search "feature branches" --json
[
  "Allow ephemeral worktrees (scratch checkouts, land on main, no branch dance) -- a carve-out from \"never create feature branches\"; ratifying it is a hard promotion gate for ADR-pool.worktree-parallel-agents."
]
```

That search is the verb's real job. Re-adjudication happens when a session
cannot tell that a question is already settled, and a 461-entry section rendered
in full is not a surface anyone reads.

---

## What this does not fix

**Identity.** GHI #838's worked example — one decision re-derived by three
sessions in three phrasings, each promoted as a new entry because the narrow key
correctly declined to fold them — is an identity problem. Rulings are prose with
no id, so they can be *carried* reliably but not *recognized*. The campaign's
Movement D names the destination: a typed `ruling` ledger event. This store is
the surface that event replaces, and the place ids attach without changing the
handoff format a second time.

---

## Related

- [`gz handoff create`](handoff-create.md) — books rulings into the store
- [`gz handoff resume`](handoff-resume.md) — previews the newest rulings and points here
- [`gz handoff decide`](handoff-decide.md) — records an operator's transit ruling on a resumed handoff
- `.gzkit/skills/gz-session-handoff/SKILL.md` — the authoring and resume contract
