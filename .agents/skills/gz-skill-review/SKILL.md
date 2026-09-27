---
name: gz-skill-review
persona: main-session
description: Review a skill by re-verifying every claim it makes against the code it wields, then correct it and move last_reviewed. Use when the operator asks to review a skill, when the skill audit warns a review is ageing or stale, or when a skill's command changed under it.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
model: sonnet
metadata:
  skill-version: "1.0.0"
---

# gz skill-review

## Overview

A review re-verifies what a skill says against what its command does, then fixes
the skill and every surface that repeats it. Moving `last_reviewed` without that
check certifies claims nobody read. The skill audit blocks every push once a
review ages past its ceiling; `DEFAULT_MAX_REVIEW_AGE_DAYS` and the earlier
warning window `DEFAULT_WARN_REVIEW_AGE_DAYS` in `src/gzkit/skills_audit.py` are
the authority for both.

Review two skills per commit at most, so each diff stays readable.

The catalog commands around a review:

- `uv run gz skill audit` — which reviews are ageing or stale, among the
  audit's other findings.
- `uv run gz skill list` — the active catalog.
- `uv run gz skill new <slug>` — scaffolds a new skill. Its first review starts
  the clock; give it a row in a namespace router and in the `gz-how` catalog.

## Workflow

1. **Read the skill and its echoes.** Read `.gzkit/skills/<slug>/SKILL.md` and
   anything beside it (`agents/openai.yaml`, `references/`), its operator page
   `docs/user/skills/<slug>.md`, and the manpage of each verb it wields,
   `docs/user/manpages/<verb>.md`. Edit `.gzkit/skills/` only: the other skill
   roots are generated mirrors.
2. **Find the code it wields.** Locate the parser registration
   (`src/gzkit/cli/parser_*.py`) and the handler
   (`src/gzkit/cli/parser_handler_manifest.py` names its module). Read the
   handler through, not only its docstring.
3. **Observe it.** Run `uv run gz <verb> --help`, then one run that changes
   nothing (`--dry-run`, a query, or a refusal path). A verifier's exit status is
   its own: capture to a file and read `$?` in the very next statement, or the
   verifier-pipe gate refuses the command (`.gzkit/rules/tests.md` § Verification
   exit-code integrity). Never run a writing mode to check a claim.
4. **Check every claim.** Tag each statement the skill makes true, stale or
   false against steps 2–3: flags and defaults, exit codes, what the verb writes
   (ledger events, files), cited paths, GHIs (`gh issue view <N>`), canon
   sections, rules and skills named. Check the same claims where they are
   repeated: the manpage, the docs page, runbook lines
   (`docs/user/runbook.md`, `docs/governance/governance_runbook.md`), and any
   exemption list naming the verb, such as `_NO_SKILL_VERBS` in
   `src/gzkit/governance/trust_audits/cli.py`.
5. **Rewrite what is wrong.** State what the verb does, in the terms the code
   uses. Cite the authority for any threshold, roster or count rather than
   copying its value. Replace any remaining scaffold template text ("Operate the
   gz X command surface as a reusable governance workflow", "Confirm target
   context, IDs, and lane assumptions"). Correct the echoing surfaces in the
   same change.
6. **Version and date.** Bump `metadata.skill-version`: minor when behaviour
   guidance changed, patch for wording. Set `last_reviewed` to today.
7. **Sync, gate, commit.** `uv run gz agent sync control-surfaces`, then
   `git add -A` and `uv run gz check`. Commit
   `docs(skills): review <slug> [and <slug>]` with a `Task:` trailer
   (`TASK-review-<slug>`), and push. The message names each defect found and the
   code it was checked against.
8. **Route what lies outside the skill.** A defect in the code, another skill
   or canon is not fixed silently inside a review: file it through
   `ghi-author`, or record it with `gz-insights-remember`, and report it to the
   operator as a decision.

## Example

```bash
uv run gz obpi brief-drift --help
uv run gz obpi brief-drift OBPI-0.35.0-07-content-land-orchestrator --apply --dry-run
uv run gz agent sync control-surfaces
git add -A
uv run gz check
```

## Related

- `gz-how` — the skill-maintenance flow this skill belongs to
- `gz-agent-sync` — regenerates the mirrors after the edit
- `ghi-author`, `gz-insights-remember` — where findings outside the skill go
