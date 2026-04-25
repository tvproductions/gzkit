---
name: ghi-triage
persona: main-session
description: Evaluate and triage all open GitHub Issues (GHIs). Runs scripts/triage.py to fetch, score, and render a routing table + copy/paste short list. Use when reviewing the open-issue queue, before a planning session, or when deciding which GHIs to pull into the next patch window.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-25
metadata:
  skill-version: "2.3.0"
---

# ghi-triage

Triage every open GHI by **running the bundled script** — do not orchestrate
`gh`, `git`, and Python calls by hand. The script encapsulates fetch,
routing classification, urgency scoring, duplicate detection, and rendering.

## Invocation

```text
/ghi-triage              ← triage all open GHIs
/ghi-triage --label defect    ← filter to one label
/ghi-triage --limit 25        ← cap the scan
```

## Behavior — single command

When this skill is invoked, run **exactly one** Bash command and present
its output verbatim:

```bash
uv run python .claude/skills/ghi-triage/scripts/triage.py [args]
```

The script lives entirely under `.gzkit/skills/ghi-triage/scripts/` and is
mirrored to vendor surfaces by `gz agent sync control-surfaces`.

Default output is a **GitHub-flavored markdown table** — renders cleanly
through Claude Code's markdown pipeline, GitHub PR comments, and any other
markdown consumer. The short list is wrapped in a fenced code block so it
copy/pastes verbatim.

For direct-terminal use (real TTY, ANSI color, box-drawing), pass
`--format rich` — that path uses Rich and is the right choice when running
the script outside an agent harness.

## What the script does

1. `gh issue list --state open --limit N --json number,title,labels,createdAt,updatedAt,body`
2. `git log --since='60 days ago' --grep='^fix('` to compute precedent count
3. Detects duplicates by identical title (canonical = lowest number)
4. Routes each issue per `AGENTS.md` § Defect-fix routing thresholds:
   - **direct-fix** when precedent ≥3 AND no OBPI signal AND ≤3 files mentioned
   - **OBPI-ceremony** on schema/contract/scope-expansion/brief-boundary signals
   - **close-dup** when an earlier issue has the same title
   - **ambiguous** when precedent is missing
5. Scores urgency: `now` (blocking signal), `soon` (defect default), `later` (chore)
6. Renders Rich table + copy/paste short list grouped by urgency

## Why script-backed

The triage was originally specified as agent-orchestrated Bash + ad-hoc
Python — that pattern wasted operator tokens and was slower than asking
ad-hoc. The v2 redesign moves all deterministic logic into
`scripts/triage.py` so the agent surface is "run one command, present
output". This matches the [agentskills.io](https://agentskills.io/home)
recommendation: skills should hand the agent a tool, not a procedure.

## Output Contract

Declared form: **Rich table + grouped short list** (single command output).

- The script's output is the deliverable — do NOT re-render it
- The short list is grouped by urgency (now / soon / later) with blank
  lines between groups, ready for direct copy/paste
- `--json` is intentionally not exposed; if structured output is needed,
  invoke the underlying `gh` command directly

## Anti-patterns

- Hand-orchestrating `gh` + `git` + Python in the agent loop instead of
  running the script
- Re-rendering or paraphrasing the script's table in the agent reply
- Modifying GHIs from this skill — triage is read-only

## Related

- `AGENTS.md` § Defect-fix routing — the routing thresholds the script encodes
- `.gzkit/skills/ghi-author/SKILL.md` — authors the GHIs this skill triages
- `.gzkit/skills/ghi-close/SKILL.md` — closes GHIs after the routed work lands
- `.claude/rules/gh-cli.md` — allowed `gh` commands
