# gz handoff decide

Book the operator's transit decision on a resumed handoff as a Layer-2 record
(GHI #574, #757). The record gates nothing.

> `gz handoff authorize` is a **deprecated alias** for this verb and behaves
> identically. See [`handoff-authorize.md`](handoff-authorize.md).

---

## Overview

`gz-session-handoff` SKILL.md § RESUME binds the resuming agent: a handoff
**advises**, it does not authorize, so the agent presents the advised steps and
waits for the operator to rule before executing any of them.

That obligation bound mechanically from 2026-07-16 to 2026-08-15 as
`.claude/hooks/handoff-resume-gate.py`, a PreToolUse refusal of mutating tool
calls on an unruled handoff. **That gate is retired** (operator ruling, verbatim:
*"the handoff should be an advisor, not a gate-keeping nanny"*) — the `Bash` arm
went 2026-08-14, the `Write|Edit|NotebookEdit` arm 2026-08-15, and the hook and
its generator template are deleted. The obligation still binds the AGENT; no
hook enforces it, and no decision booked here permits or withholds anything.

`gz handoff decide` is how the ruling is booked, and booking it remains the
point: a ruling given in conversation and never booked leaves no Layer-2 record
of what the operator decided. Memory is not evidence. Nothing is refused for the
absence of a record — the loss is the record itself.

The record is **session-scoped**: it cites the harness `session_id`, so a prior
session's ruling is never read as this one's.

---

## Usage

```
gz handoff decide --handoff PATH --operator-text TEXT --session-id ID
                  [--decision {proceed,pause,hold,revert}]
                  [--set-aside STEP] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--handoff PATH` | The resumed handoff the ruling covers (required). Must exist, and must be the handoff this session resumed. |
| `--operator-text TEXT` | The operator's **verbatim** ruling words (required). |
| `--session-id ID` | Harness session the ruling binds to (required). |
| `--decision {proceed,pause,hold,revert}` | The transit decision to record (default `proceed`). All four are equally bookable; none gates anything. See § A transit decision, not an attestation. |
| `--set-aside STEP` | An advised step this ruling declines (repeatable). The clearance-amendment record. |
| `--json` | Emit `{"status": "decided", "decision": ..., ...}` instead of the human line. |

`--session-id` is explicit rather than read from a `CLAUDE_SESSION_ID` env var:
`src/gzkit/commands/` is fenced to a two-entry env allowlist (`NO_COLOR` /
`FORCE_COLOR`) so vendor coupling cannot leak into the command layer.

---

## A transit decision, not an attestation

This verb books an **acknowledge-and-decide** transit. It is deliberately not a
completion attestation, and ADR-0.0.33 § Alternatives rejects the conflation by
name:

> Call the airlock gate an 'attestation' (REJECTED -- doctrine violation):
> completion-attestation is sacrosanct and reserved for claims about completed
> planned work; the airlock's every-transit gate is acknowledge-and-decide, a
> different sort -- conflating them would spend and cheapen the sacred word.

The predecessor event's own docstring claimed *"the same relay model as Gate 5
attestation"* — that conflation, written down. The grammar is now borrowed from
the airlock's `Decision` register while the records stay the handoff layer's
own; the two systems sit on different axes.

| Decision | Meaning |
|---|---|
| `proceed` | Act on the advised steps as ruled |
| `pause` | Looked, not now — revisit shortly |
| `hold` | Looked, deliberately not proceeding |
| `revert` | Undo or back out rather than continue |

The predecessor shape was a **consent boolean**: booking it *was* authorization,
so an operator who reviewed the handoff and said *not yet* left no record at all.
The register could only ever say yes. `pause` / `hold` / `revert` are equally
bookable rulings, and none of the four authorizes anything.

### Recording amendments

`--set-aside` names an advised step the ruling declines. Departure from counsel
was previously invisible: nothing captured which step was set aside or why. The
operator's framing — *"ATC keeps a record of all clearances issued and all
amendments."*

---

## `--operator-text` is verbatim, and this is not a formality

Pass the operator's words **unchanged**. Do not paraphrase, summarize, or
improve them (`AGENTS.md` § Attestation; § OPERATOR ECONOMY OF EFFORT #3 — the
agent seats the operator's words, it never rewrites them).

**Booking a decision the operator did not give is fabrication** — the same
failure class as fabricating an ARB receipt id, and nothing here can detect it.
This command is a relay, not a check.

Keeping the words verbatim while retiring the attestation *register* is the
operator's ruling (2026-08-05). The two are separable: a transit decision is a
lighter sort than a completion claim, but the operator's actual phrasing is what
scopes whole sessions, and summarizing it away would lose the ruling to preserve
the ceremony. The word is still recorded; what changed is the drawer it is filed
in. The honesty is yours.

---

## Example

The agent presents the resumed handoff's advised steps; the operator rules. Book
their words, and set aside the step they declined:

```bash
uv run gz handoff decide \
  --handoff .gzkit/handoffs/20260913T100000Z-session-wrap.md \
  --session-id abc123 --decision proceed \
  --operator-text "do 1, skip the release" --set-aside "2. Cut the patch release"
```

```
proceed — .gzkit/handoffs/20260913T100000Z-session-wrap.md (session abc123)
recorded
```

A ruling not to proceed is booked the same way, and reports the same record:

```bash
uv run gz handoff decide \
  --handoff .gzkit/handoffs/20260913T100000Z-session-wrap.md \
  --session-id abc123 --decision hold --operator-text "not yet"
```

```
hold — .gzkit/handoffs/20260913T100000Z-session-wrap.md (session abc123)
recorded
```

Both exit 0. The line wraps at the console width.

---

## The ruling must name the handoff this session resumed

`--handoff` is compared against the document this session actually resumed,
and a mismatch is refused before anything is written.

A ruling is consent to *a specific document's advised steps*. Until GHI #795
the `handoff_path` on the decision event was written and never read back, so a
ruling booked against document A was accepted for a session resumed on
document B — recording operator consent for steps nobody was shown. Any path
typo, stale copy-paste, or handoff authored before the booking reached that
state.

The refusal names the resumed path and prints a runnable recovery, so the fix is
always a copy-paste:

```console
$ uv run gz handoff decide --handoff .gzkit/handoffs/20260716T000000Z-older.md \
    --session-id session-xyz --decision proceed --operator-text "go ahead"
Refusing to book: .gzkit/handoffs/20260716T000000Z-older.md is not the handoff
this session resumed.
WHY: this session resumed .gzkit/handoffs/20260812T000000Z-armed.md, and a
ruling names the advised steps the operator actually read. ...
NEXT STEP: re-run against the armed handoff, or rule on it explicitly:
  uv run gz handoff decide --handoff .gzkit/handoffs/20260812T000000Z-armed.md \
    --session-id session-xyz --decision proceed --operator-text "<their exact words>"
```

**The check is at booking time, and that is deliberate.** It was written while
the resume gate still existed, when the alternative was comparing paths at
*lift* time — which re-armed the gate against an already-cleared session the
moment any new handoff landed mid-flight (a completion record, an exit bookmark,
a checkpoint), the regression GHI #619 and GHI #755 closed. The gate was retired
2026-08-15 and the placement outlived it: booking time is still where the
operator's reading is verifiable, because that is when they read it.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Ruling booked to Layer-2 for this session. |
| 1 | No session id; the named handoff does not exist; or it is not the handoff this session resumed. Nothing written in every case. |
