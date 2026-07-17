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
gz handoff authorize --handoff PATH --operator-text TEXT --session-id ID
                     [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--handoff PATH` | The resumed handoff the ruling covers (required). Must exist. |
| `--operator-text TEXT` | The operator's **verbatim** authorization words (required). |
| `--session-id ID` | Harness session the ruling binds to (required). The gate's block message interpolates it — copy the command from there. |
| `--json` | Emit `{"status": "authorized", ...}` instead of the human line. |

`--session-id` is explicit rather than read from a `CLAUDE_SESSION_ID` env var:
`src/gzkit/commands/` is fenced to a two-entry env allowlist (`NO_COLOR` /
`FORCE_COLOR`) so vendor coupling cannot leak into the command layer. The gate
fills the id into the recovery command, so no caller has to discover it.

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

The gate fires on the first mutating call of a resumed session. Observed output
(`exit 2`, stderr):

```
BLOCKED: Write refused — this session resumed a handoff (.gzkit/handoffs/20260716T204012Z-rule-surface-reconciliation-pass-a.md) and the operator has not ruled on it.

WHY: `gz-session-handoff` SKILL.md § RESUME declares a universal Operator Authorization Gate — 'Every resume requires explicit operator authorization before any execution, at every freshness level — Fresh included ... no file mutation / gz ceremony / migration until the operator rules.' A handoff ADVISES; it does not authorize. Freshness shortens re-verification; it never converts an advisory into a license.

NEXT STEP: present the handoff's advised next steps to the operator and wait for a ruling. When they rule, book their VERBATIM words (copy this line; the session id is already filled in):
  uv run gz handoff authorize --handoff .gzkit/handoffs/20260716T204012Z-rule-surface-reconciliation-pass-a.md \
    --session-id abc123 --operator-text "<their exact words>"

Run it BARE — a `cd ...;` prefix makes it a compound command, which this gate correctly refuses.
Reading is permitted while unauthorized (gz state / gz gates / gz obpi status, and git/grep/cat reads) — the gate blocks execution, never the verification that precedes it, and never its own recovery.
```

The session id is interpolated because the blocked party cannot look it up — it
lives in the hook payload, and the commands that would reveal it are themselves
gated. A recovery command the blocked party cannot complete is not a recovery
path (this was defect #1 on the first cut of this gate; it bricked its author).

Present the advised steps, wait for the ruling, then copy that command:

```bash
uv run gz handoff authorize \
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

- `gz handoff authorize` itself (a rule that blocks the command lifting it is
  worse than the hole it plugs)
- The § Trust Model reads RESUME requires before presenting: `gz state`,
  `gz gates`, `gz obpi status`, `gz obpi lock list`, `gz status`,
  `gz adr status`, `gz context`
- `gz handoff list` / `gz handoff resume`
- Plain shell reads: `git status|log|diff|show|branch|rev-parse|ls-files`,
  `grep`, `rg`, `ls`, `cat`, `head`, `tail`, `wc`, `find`, `jq`, `pwd`

The shell reads are not a convenience. The § Claim Verification Gate **mandates**
verifying a handoff's claims against Layer-2 *before* presenting, and the harness
does not always expose `Grep`/`Glob` tools — so Bash is the read path. A gate that
forbids the verification its own skill requires cannot be complied with, and an
un-compliable gate gets worked around. (The first cut of this gate permitted only
`gz` verbs on the stated premise that "Read/Grep/Glob are never gated"; that
premise was false, and it was defect #3.)

Everything else fails **closed**:

- Compound commands, regardless of head — `gz state && rm -rf x` is not a read of
  `gz state`. Any of `;` `&` `|` `>` `<` `` ` `` `$(` disqualifies.
- Write-capable flags on an allowlisted head — `find . -delete`, `find . -exec`,
  `sed -i`, `--fix`, `--in-place`.
- Unparseable commands (unbalanced quotes).

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Ruling booked; the gate is lifted for this session. |
| 1 | No session id, or the named handoff does not exist (nothing written). |
