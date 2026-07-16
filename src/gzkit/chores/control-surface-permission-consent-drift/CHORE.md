# CHORE: Control Surface — Rule Prose vs. Permission Standing Consent (Pass D)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `control-surface-permission-consent-drift`

---

## Overview

Audit-only pass. For every prohibition declared in `AGENTS.md` and `.gzkit/rules/**`, check whether the agent permission surfaces (`.claude/settings.json`, `.claude/settings.local.json`) grant standing consent for the prohibited action. Output is a drift ledger naming each contradiction, its doctrine citation, and — critically — whether the contradiction is *mechanically witnessable at all*.

Background: on 2026-07-16 the local permission surface was found carrying `Bash(python3:*)`, granting standing consent for a command `AGENTS.md` § Execution Rules forbids ("Always use `uv run` for Python commands"). The rule had been in the file long enough that its origin was unrecoverable — each entry is an auto-append from a past "always allow" click. It surfaced only because an operator noticed an agent using bare `python3` in-session and asked why it had not prompted. Nothing re-reads permission surfaces against the agent contract.

The failure class is the family signature: **T1 doctrine with no T2 mechanical fail-close** — the same shape as Pass A (rules contradict each other), Pass B (skills route around rules), and Pass C (promoted checks under-enforce their prose). Pass D is the permission-surface cut. Every "always allow" click converts a one-time situational judgment into a permanent rule that outlives the context that justified it.

The harm is **not** agent comprehension — permission rules never enter agent context and cannot confuse a model. The harm is that the one mechanical interposition point (the permission prompt) is pre-disabled for a prohibited action. See `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT operative claim 3 (doctrine drift is invariant drift).

## Policy and Guardrails

- **Lane:** Lite — audit-only; zero file edits outside `.gzkit/chores/control-surface-permission-consent-drift/proofs/`.
- **Read-only on permission surfaces.** This chore does NOT edit `.claude/settings.json`, `.claude/settings.local.json`, `AGENTS.md`, or any rule. It reads and reports. Remediation routes to a direct-fix GHI.
- **Advisory, never gating.** This chore has no `gz validate` scope and must never acquire one without operator ruling. `gz validate` already carries 90 flags against an open campaign checkbox to collapse that surface (#618 residual); a Pass D scope would be #91. Advisory-sweep framing is also the honest one — see § Known coverage limits.
- **No speculation.** A drift row requires a concrete doctrine citation (file + § section or line) AND the verbatim allow rule. No "this rule looks risky" entries.
- **Local surface may be absent.** `.claude/settings.local.json` is gitignored (`.gitignore:54`). On a fresh clone it does not exist. Absence is a **skip with a recorded note**, never a pass — see § Known coverage limits.

## Known coverage limits (binding — record these verbatim in every summary)

This chore's coverage is structurally partial. A summary that does not restate these limits overstates what was audited (GHI #690).

1. **Context-dependence — the hard ceiling.** Much of `AGENTS.md` forbids an action *in a context*: "never call `gh issue create` **outside this skill**" (Always #13), "never X directly", "never X without ceremony". Permission rules are context-free string matches. The sanctioned and forbidden invocations are byte-identical. `Bash(gh issue:*)` is **load-bearing, not drift** — `/ghi-author` invokes `gh issue create` at `SKILL.md:199` as its own final step, and denying it would break the only sanctioned path for filing a GHI. Any context-dependent prohibition is **out of scope for a Pass D row** and belongs in `proofs/unwitnessable.md`.
2. **Broad-rule blindness.** A drift row can only be raised against a rule that *mentions* the prohibited token. `Bash(git *)` permits `git checkout -b feature/foo`, contradicting operator canon (verbatim, 2026-06-16: never create feature branches, work directly on main), but contains no matching substring. Broad rules are the more dangerous class and this pass cannot see them. Record known-broad rules in `proofs/unwitnessable.md` rather than silently passing them.
3. **CI-blindness.** The committed `.claude/settings.json` is checkable anywhere; `.claude/settings.local.json` exists only on the operator's machine. This chore is therefore **local-run only** and its findings are not reproducible in CI. Never wire it to a CI gate.
4. **Curated-list drift.** The doctrine→pattern mapping in `proofs/doctrine-map.md` is hand-maintained and can itself drift from `AGENTS.md`, reproducing the drift failure one level up. Step 1 re-derives the map from the corpus each run rather than trusting the prior run's map.

## Workflow

### 1. Re-derive the doctrine map (never trust the prior run)

Enumerate prohibitions from `AGENTS.md` (§ Execution Rules, § Behavior Rules — Never, § Behavior Rules — Always, § Operator Doctrine) and `.gzkit/rules/**`. For each, record in `proofs/doctrine-map.md`:

- Doctrine citation (file + § section, verbatim quote)
- Whether the prohibition is **context-free** (a command is forbidden outright) or **context-dependent** (forbidden only outside a skill/ceremony)
- For context-free entries only: the command token(s) that would appear in a permission rule

Context-dependent entries go straight to `proofs/unwitnessable.md` with the reason. Do not attempt to pattern-match them.

### 2. Enumerate the permission surfaces

Read `.claude/settings.json` and (if present) `.claude/settings.local.json`. Record every `allow` and `deny` rule verbatim in `proofs/permission-inventory.md`, tagged by source file. If the local file is absent, record the skip and its cause — do not report a clean pass.

### 3. Drift walk (context-free prohibitions only)

For each context-free doctrine entry × each allow rule, ask: does this rule grant standing consent for the prohibited command? One row per hit in `proofs/consent-drift.md`:

- Doctrine citation + verbatim quote
- Verbatim allow rule
- Source file (`settings.json` / `settings.local.json`)
- Whether a `deny` rule already neutralizes it (deny takes precedence over allow)
- Severity: `live` (no deny covers it) / `neutralized` (a deny rule already wins) / `historical` (rule is dead-in-practice)

### 4. Unwitnessable ledger

Write `proofs/unwitnessable.md`: every context-dependent prohibition and every known-broad allow rule this pass structurally cannot audit, each with the reason. **This artifact is the point of the chore as much as the drift ledger** — it is the honest record of what was not checked, and it is what stops a future reader from mistaking a short drift ledger for a clean surface.

### 5. Summary + routing list

Write `proofs/summary.md` with: counts by severity; the § Known coverage limits restated verbatim; and a routing list where each `live` row is sized for a direct-fix GHI (`fix(<scope>): … (GHI #N)`). Per operator canon, a GHI-tracked defect repair routes to direct fix — never spin up an ADR or OBPI to discharge one.

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/doctrine-map.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/permission-inventory.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/consent-drift.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/unwitnessable.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/summary.md` | 0 |

`unwitnessable.md` is a required artifact, not an optional one. A run that produces a drift ledger without the coverage-limits ledger has advertised a coverage it does not have — the precise failure GHI #690 named.

## Evidence Commands

```bash
ls -1 .claude/settings.json .claude/settings.local.json 2>&1 \
  > .gzkit/chores/control-surface-permission-consent-drift/proofs/surface-listing.txt
git check-ignore -v .claude/settings.local.json \
  >> .gzkit/chores/control-surface-permission-consent-drift/proofs/surface-listing.txt 2>&1
```

## Related

- GHI #690 — origin; carries the four design problems verbatim
- GHI #669 — sibling cut (OBPI-status writers; convention-only enforcement)
- `control-surface-rule-conflicts` (Pass A), `control-surface-skill-rule-reachability` (Pass B), `control-surface-rule-vs-check-drift` (Pass C)
- `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT operative claim 3
- `docs/governance/trust-doctrine.md` (T1/T2/T3 trust-chain)

---
