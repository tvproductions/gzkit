<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Agent Session Handoff Obligations

**Status:** Active
**Last reviewed:** 2026-02-13
**Parent ADR:** ADR-0.0.25 (Compounding Engineering & Session Handoff Contract)
**OBPI:** OBPI-0.0.25-08

---

## Overview

This document codifies the behavioral contract that binds all AI coding agents operating under GovZero governance to use the session handoff mechanism correctly. These obligations apply to every agent listed in the Agent Profiles table of `AGENTS.md` — Claude Code, Codex, and GitHub Copilot.

The handoff system preserves engineering context across sessions. Without normative rules, agents may silently drop context, skip handoffs, or resume on stale state. These obligations close those gaps.

---

## Proactive Triggers

### MUST Create a Handoff When

1. **Session ending with incomplete work** — If the current OBPI or task is not yet `Completed`, the agent MUST create a handoff document before the session ends.
2. **Switching ADR scope** — When pivoting from one ADR's work to another within the same session, the agent MUST create a handoff for the ADR being left.
3. **Human requests it** — When the operator explicitly asks for a handoff (e.g., `/gz-session-handoff CREATE`).

### SHOULD Create a Handoff When

- A session has produced significant decisions or discoveries not yet recorded elsewhere.
- The agent has accumulated substantial context that would be expensive to reconstruct.
- More than 2 hours of focused work has occurred on a single ADR.

---

## Normative Obligations

| # | Obligation | Rationale |
|---|-----------|-----------|
| 1 | **MUST populate all 7 required sections** with session-specific content — no placeholders, no HTML comment stubs. | The validation pipeline rejects incomplete documents. Partial handoffs provide false confidence. |
| 2 | **MUST pass the full validation pipeline** (frontmatter schema, placeholder detection, secret detection, section presence, file reference existence) before considering a handoff complete. | Fail-closed validation is the design principle — only a clean document can serve as reliable context. |
| 3 | **MUST set `continues_from`** when a prior handoff exists for the same ADR. | Chaining preserves lineage. An unchained handoff orphans prior context. |
| 4 | **MUST record accurate `branch` and `adr_id`** in frontmatter matching the actual working state. | RESUME workflow uses these fields for context verification. Mismatches trigger warnings that undermine trust. |

---

## Prohibitions

1. **MUST NOT resume a "Very Stale" handoff without human verification.** The staleness classification system marks documents older than 7 days (or with significant git divergence) as requiring human review. Proceeding without verification risks acting on invalidated context.

2. **MUST NOT bypass validation by writing handoff files directly.** Always use the CREATE workflow (`create_handoff()` or the `/gz-session-handoff CREATE` skill). Direct file writes skip placeholder detection, secret scanning, and section validation.

3. **MUST NOT silently discard handoff context during RESUME.** When resuming, the agent must acknowledge the handoff content (staleness classification, chain depth, first next step) before proceeding with new work.

---

## CREATE Workflow Summary

1. **Scaffold** — Generate document from template with frontmatter populated
2. **Populate** — Fill all 7 required sections with session-specific content
3. **Validate** — Run full validation pipeline (6 checks)
4. **Write** — Persist to `{ADR-package}/handoffs/{timestamp}-{slug}.md`

Full specification: [gz-session-handoff SKILL](../../../.github/skills/gz-session-handoff/SKILL.md)

---

## RESUME Workflow Summary

1. **Discover** — List available handoffs for the target ADR, sorted newest-first
2. **Classify** — Evaluate staleness (time, commits, files, branch divergence)
3. **Gate** — If Stale or Very Stale, require human verification before proceeding
4. **Load chain** — Traverse `continues_from` links for full lineage
5. **Extract** — Pull first next step for immediate action

Full specification: [gz-session-handoff SKILL](../../../.github/skills/gz-session-handoff/SKILL.md)

---

## Staleness Handling Rules

| Classification | Age | Action |
|----------------|-----|--------|
| **Fresh** | < 24 hours | Resume directly |
| **Slightly Stale** | 24h – 72h | Resume with caution; note elapsed time |
| **Stale** | 72h – 7 days | Human verification required before proceeding |
| **Very Stale** | > 7 days | Human verification required; consider creating a fresh handoff instead |

Multi-factor staleness (commits, files, branch divergence) can escalate the classification independently of time. See [Multi-Factor Staleness Classification](staleness-classification.md) for the full four-factor model.

---

## Chaining Requirements

- Every handoff after the first for a given ADR MUST set `continues_from` to the canonical path of its predecessor.
- Chain depth is hard-limited at 20 documents (error) with an advisory warning at 5.
- Circular references are detected and rejected.
- Chain traversal returns documents in chronological (oldest-first) order.

Full specification: [Handoff Document Chaining Protocol](handoff-chaining.md)

---

## See Also

- [Session Handoff Schema](session-handoff-schema.md) — Schema specification (OBPI-01)
- [Handoff Document Validation](handoff-validation.md) — Validation checks (OBPI-06)
- [Multi-Factor Staleness Classification](staleness-classification.md) — Staleness system (OBPI-05)
- [Handoff Document Chaining Protocol](handoff-chaining.md) — Chaining protocol (OBPI-07)
- [ADR-0.0.25](../../design/adr/adr-0.0.x/ADR-0.0.25-compounding-engineering-session-handoff-contract/ADR-0.0.25-compounding-engineering-session-handoff-contract.md) — Architecture decision record
- [gz-session-handoff SKILL](../../../.github/skills/gz-session-handoff/SKILL.md) — Skill specification
- [AGENTS.md § Session Handoff](../../../AGENTS.md) — Agent contract integration
