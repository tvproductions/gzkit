# gz handoff decide

Book the operator's transit decision on a resumed handoff — the command that
lifts the Operator Authorization Gate (GHI #574, #757).

> `gz handoff authorize` is a **deprecated alias** for this verb and behaves
> identically. See [`handoff-authorize.md`](handoff-authorize.md).

---

## Overview

`gz-session-handoff` SKILL.md § RESUME declares a **universal** Operator
Authorization Gate:

> "Every resume requires explicit operator authorization before any execution, at
> every freshness level — Fresh included. ... no file mutation / `gz` ceremony /
> migration until the operator rules."

It bound mechanically from 2026-07-16 to 2026-08-15 as
`.claude/hooks/handoff-resume-gate.py`, a PreToolUse refusal of mutating tool
calls on an unruled handoff. **That gate is retired** (operator ruling, verbatim:
*"the handoff should be an advisor, not a gate-keeping nanny"*) — the `Bash` arm
went 2026-08-14, the `Write|Edit|NotebookEdit` arm 2026-08-15, and the hook and
its generator template are deleted. The clause above still binds the AGENT; no
hook enforces it.

`gz handoff decide` is how the ruling is booked, and booking it remains the
point: a ruling given in conversation and never booked leaves no Layer-2 record
of what the operator decided. Memory is not evidence. Nothing is refused for the
absence of a record — the loss is the record itself.

Authorization is **session-scoped**: it cites the harness `session_id`, so a
prior session's ruling can never license this one, and a mechanically written
completion handoff (`gz obpi complete`, GHI #619) cannot re-arm the gate
mid-session.

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
| `--handoff PATH` | The resumed handoff the ruling covers (required). Must exist. |
| `--operator-text TEXT` | The operator's **verbatim** ruling words (required). |
| `--session-id ID` | Harness session the ruling binds to (required). The gate's block message interpolates it — copy the command from there. |
| `--decision {proceed,pause,hold,revert}` | The transit decision (default `proceed`). **Only `proceed` lifts the gate.** See § A transit decision, not an attestation. |
| `--set-aside STEP` | An advised step this ruling declines (repeatable). The clearance-amendment record. |
| `--json` | Emit `{"status": "decided", "decision": ..., ...}` instead of the human line. |

`--session-id` is explicit rather than read from a `CLAUDE_SESSION_ID` env var:
`src/gzkit/commands/` is fenced to a two-entry env allowlist (`NO_COLOR` /
`FORCE_COLOR`) so vendor coupling cannot leak into the command layer. The gate
fills the id into the recovery command, so no caller has to discover it.

---

## A transit decision, not an attestation

This gate books an **acknowledge-and-decide** transit. It is deliberately not a
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

| Decision | Meaning | Lifts the gate? |
|---|---|:---:|
| `proceed` | Act on the advised steps as ruled | **yes** |
| `pause` | Looked, not now — revisit shortly | no |
| `hold` | Looked, deliberately not proceeding | no |
| `revert` | Undo or back out rather than continue | no |

The predecessor shape was a **consent boolean**: booking it *was* authorization,
so an operator who reviewed the handoff and said *not yet* left no record at all.
The register could only ever say yes. `pause` / `hold` / `revert` are equally
bookable rulings, and none of them authorizes anything.

### Recording amendments

`--set-aside` names an advised step the ruling declines. Departure from counsel
was previously invisible: nothing captured which step was set aside or why. The
operator's framing — *"ATC keeps a record of all clearances issued and all
amendments."*

```bash
uv run gz handoff decide --handoff <path> --session-id abc123 \
  --decision proceed --operator-text "do 1 and 2, skip the release" \
  --set-aside "3. Cut the patch release"
```

---

## `--operator-text` is verbatim, and this is not a formality

Pass the operator's words **unchanged**. Do not paraphrase, summarize, or
improve them (`AGENTS.md` § Attestation; § OPERATOR ECONOMY OF EFFORT #3 — the
agent seats the operator's words, it never rewrites them).

**Booking a decision the operator did not give is fabrication** — the same
failure class as fabricating an ARB receipt id, and the gate cannot detect it.
This command is a relay, not a check.

Keeping the words verbatim while retiring the attestation *register* is the
operator's ruling (2026-08-05). The two are separable: a transit decision is a
lighter sort than a completion claim, but the operator's actual phrasing is what
scopes whole sessions, and summarizing it away would lose the ruling to preserve
the ceremony. The word is still recorded; what changed is the drawer it is filed
in. The mechanism here forces a *stop*; the honesty is still yours.

---

## Example

The gate fires on the first mutating call of a resumed session. Observed output
(`exit 2`, stderr):

```
BLOCKED: Write refused — this session resumed a handoff (.gzkit/handoffs/20260716T204012Z-rule-surface-reconciliation-pass-a.md) and the operator has not ruled on it.

WHY: `gz-session-handoff` SKILL.md § RESUME declares a universal Operator Authorization Gate — 'Every resume requires explicit operator authorization before any execution, at every freshness level — Fresh included ... no file mutation / gz ceremony / migration until the operator rules.' A handoff ADVISES; it does not authorize. Freshness shortens re-verification; it never converts an advisory into a license.

NEXT STEP: present the handoff's advised next steps to the operator and wait for a ruling. When they rule, book their VERBATIM words (copy this line; the session id is already filled in):
  uv run gz handoff decide --handoff .gzkit/handoffs/20260716T204012Z-rule-surface-reconciliation-pass-a.md \
    --session-id abc123 --operator-text "<their exact words>"

Run it BARE — a `cd ...;` prefix makes it a compound command, which this gate correctly refuses.
Reading is permitted while unauthorized (gz state / gz gates / gz obpi status, gh issue|pr read verbs, and git/grep/cat reads; quoted metacharacters like grep "A\|B" are data, not pipes) — the gate blocks execution, never the verification that precedes it, and never its own recovery.
```

The session id is interpolated because the blocked party cannot look it up — it
lives in the hook payload, and the commands that would reveal it are themselves
gated. A recovery command the blocked party cannot complete is not a recovery
path (this was defect #1 on the first cut of this gate; it bricked its author).

Present the advised steps, wait for the ruling, then copy that command:

```bash
uv run gz handoff decide \
  --handoff .gzkit/handoffs/20260716T204012Z-rule-surface-reconciliation-pass-a.md \
  --session-id abc123 --operator-text "focus on handoff first"
```

```
authorized — .gzkit/handoffs/20260716T204012Z-rule-surface-reconciliation-pass-a.md (session abc123)
```

Execution proceeds for the rest of the session.

---

## What stays permitted while unauthorized

The gate blocks *execution*, never the verification that precedes it — and never
its own recovery path. Permitted while unauthorized:

- `gz handoff decide` **and** its `authorize` alias (a rule that blocks the
  command lifting it is worse than the hole it plugs)
- The § Trust Model reads RESUME requires before presenting: `gz state`,
  `gz gates`, `gz obpi status`, `gz obpi lock list`, `gz status`,
  `gz adr status`, `gz context`
- `gz handoff list` / `gz handoff resume`
- `gh` **read** verbs: `gh issue view|list|status`, `gh pr view|list|diff|status`,
  `gh release view|list`
- Plain shell reads: `git status|log|diff|show|branch|rev-parse|ls-files`,
  `grep`, `rg`, `ls`, `cat`, `head`, `tail`, `wc`, `find`, `jq`, `pwd`

The reads are not a convenience. The § Claim Verification Gate **mandates**
verifying a handoff's claims against Layer-2 *before* presenting, and the harness
does not always expose `Grep`/`Glob` tools — so Bash is the read path. A gate that
forbids the verification its own skill requires cannot be complied with, and an
un-compliable gate gets worked around.

This allowlist is derived from the § Claim Verification Gate's **obligation**, not
from the § Trust Model's example verbs. Deriving it from the examples under-covered
the duty twice: the first cut permitted only `gz` verbs on the stated premise that
"Read/Grep/Glob are never gated" (false in this harness — defect #3); the second
omitted `gh`, leaving a resume unable to check the GHI-state claims its own advised
steps turned on, since GitHub is the only Layer-2 surface for them.

`gh` is admitted as a **read** surface only. `gh issue create` is independently
forbidden by `AGENTS.md` § Behavior Rules — Always #13 (author GHIs through
`/ghi-author`), and `gh api` is excluded because `-X POST` mutates.

Everything else fails **closed**:

- Compound commands, regardless of head — `gz state && rm -rf x` is not a read of
  `gz state`. Detection is quote-aware (`shlex`, `punctuation_chars=True`): a real
  `;` `&` `|` `>` `<` operator disqualifies, while the same character *inside
  quotes* is data — `grep "A\|B"` and `gh issue list -q '.[] | select(…)'` are
  reads and are permitted.
- Command substitution in **any** quoting form — `` ` `` and `$(`. Double quotes do
  not make substitution inert, and posix tokenization cannot distinguish the live
  `"$(…)"` from the inert `'$(…)'`, so both are refused.
- Write-capable flags on an allowlisted head — `find . -delete`, `find . -exec`,
  `sed -i`, `--fix`, `--in-place`.
- Unparseable commands (unbalanced quotes).

---

## The ruling must name the handoff this session resumed

`--handoff` is compared against the document this session actually resumed,
and a mismatch is refused before anything is written.

A ruling is consent to *a specific document's advised steps*. Until GHI #795
the `handoff_path` on the decision event was written and never read back, so a
ruling booked against document A lifted a gate armed on document B — recording
operator consent for steps nobody was shown. Any path typo, stale copy-paste,
or handoff authored between the block message and the booking reached that
state.

The refusal names the armed path and prints a runnable recovery, so the fix is
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
*lift* time — which would have re-armed the gate against an already-cleared
session the moment any new handoff landed mid-flight (a completion record, an
exit bookmark, a checkpoint), the regression GHI #619 and GHI #755 closed. The
gate was retired 2026-08-15 and the placement outlived it: booking time is
still where the operator's reading is verifiable, because that is when they
read it.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Ruling booked to Layer-2 for this session. |
| 1 | No session id; the named handoff does not exist; or it is not the handoff this session resumed. Nothing written in every case. |
