# gz handoff authorize

Book the operator's ruling on a resumed handoff — the command that lifts the
Operator Authorization Gate (GHI #574).

---

## Overview

`gz-session-handoff` SKILL.md § RESUME declares a **universal** Operator
Authorization Gate:

> "Every resume requires explicit operator authorization before any execution, at
> every freshness level — Fresh included. ... no file mutation / `gz` ceremony /
> migration until the operator rules."

That was prose plus a template banner until 2026-07-16 — an agent could read the
banner and proceed anyway, and nothing stopped it. It now binds:
`.claude/hooks/handoff-resume-gate.py` (PreToolUse on `Write|Edit|NotebookEdit`
**and** `Bash`) refuses every mutating tool call while this session has resumed a
handoff with no operator ruling on the ledger.

`gz handoff authorize` is how the ruling is booked. The gate reads Layer-2, so a
ruling given in conversation and never booked leaves the gate armed — **by
design**. Memory is not evidence.

Authorization is **session-scoped**: it cites the harness `session_id`, so a
prior session's ruling can never license this one, and a mechanically written
completion handoff (`gz obpi complete`, GHI #619) cannot re-arm the gate
mid-session.

---

## Usage

```
gz handoff authorize --handoff PATH --operator-text TEXT
                     [--session-id ID] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--handoff PATH` | The resumed handoff the ruling covers (required). Must exist. |
| `--operator-text TEXT` | The operator's **verbatim** authorization words (required). |
| `--session-id ID` | Harness session the ruling binds to. Defaults to `$CLAUDE_SESSION_ID`; the gate's block message carries the id the harness reported. |
| `--json` | Emit `{"status": "authorized", ...}` instead of the human line. |

---

## `--operator-text` is verbatim, and this is not a formality

Pass the operator's words **unchanged**. Do not paraphrase, summarize, or
improve them (`AGENTS.md` § Attestation; § OPERATOR ECONOMY OF EFFORT #3 — the
agent seats the operator's words, it never rewrites them).

**Authorizing words the operator did not say is fabrication** — the same failure
class as fabricating an ARB receipt id, and the gate cannot detect it. This
command is a relay, not a check: it carries the same trust model as Gate 5, where
the operator's verbatim attestation relayed via `--attestation-text` IS the
attestation and the mechanism serves it rather than gating it. The mechanism
here forces a *stop*; the honesty is still yours.

---

## Example

The gate fires on the first mutating call of a resumed session:

```
BLOCKED: Write refused — this session resumed a handoff
(.gzkit/handoffs/20260716T204012Z-rule-surface-reconciliation-pass-a.md) and the
operator has not ruled on it.

WHY: `gz-session-handoff` SKILL.md § RESUME declares a universal Operator
Authorization Gate — 'Every resume requires explicit operator authorization
before any execution, at every freshness level — Fresh included ... no file
mutation / gz ceremony / migration until the operator rules.' A handoff ADVISES;
it does not authorize. ...

NEXT STEP: present the handoff's advised next steps to the operator and wait for
a ruling. When they rule, book it verbatim: ...
```

Present the advised steps, wait for the ruling, then book it:

```bash
uv run gz handoff authorize \
  --handoff .gzkit/handoffs/20260716T204012Z-rule-surface-reconciliation-pass-a.md \
  --operator-text "focus on handoff first"
```

```
authorized — .gzkit/handoffs/20260716T204012Z-rule-surface-reconciliation-pass-a.md (session abc123)
```

Execution proceeds for the rest of the session.

---

## What stays permitted while unauthorized

The gate blocks *execution*, never the verification that precedes it — and never
its own recovery path. Permitted while unauthorized:

- `gz handoff authorize` itself (a rule that blocks the command lifting it is
  worse than the hole it plugs)
- The § Trust Model reads RESUME requires before presenting: `gz state`,
  `gz gates`, `gz obpi status`, `gz obpi lock list`, `gz status`
- `gz handoff list` / `gz handoff resume`
- All read-only **tools** — `Read`, `Grep`, `Glob` are never gated

Everything else fails **closed**, including compound commands: `gz state && rm -rf x`
is not a read of `gz state`.

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Ruling booked; the gate is lifted for this session. |
| 1 | No session id, or the named handoff does not exist (nothing written). |
