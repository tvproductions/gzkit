# /gz-skill-review

Review a skill by re-verifying every claim it makes against the code it wields, then correct it and move `last_reviewed`.

---

## Purpose

`/gz-skill-review` makes a skill review mean something. The pre-push skill audit blocks once a skill's `last_reviewed` passes its ceiling (`DEFAULT_MAX_REVIEW_AGE_DAYS` in `src/gzkit/skills_audit.py`); a date bump alone would pass that check while certifying claims nobody read. The review reads the skill, finds the parser and handler it wields, observes `--help` and a safe run, tags each claim true, stale or false, and corrects the skill together with the manpage, docs page and runbook lines that repeat it.

Trigger phrases: "review <skill>", "the skill audit says a review is stale", "this skill no longer matches its command".

## When to Use

- The operator asks for a skill review.
- The skill audit warns that a review is inside its warning window, or blocks on a stale one.
- A skill's command changed and the skill has not been re-read since.

## What to Expect

The skill reads its execution contract from `.gzkit/skills/gz-skill-review/SKILL.md` (mirrored into `.claude/skills/` and `.agents/skills/`). Each review ends in a `docs(skills): review …` commit that names the defects found and the code checked against. Defects outside the skill are routed through `/ghi-author` or `/gz-insights-remember`, never fixed silently inside the review.

## Invocation

```text
/gz-skill-review gz-state
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| skill slug | Yes | The skill to review; two per commit at most |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-skill-review/SKILL.md` | Canonical skill contract | Read |
| `.gzkit/skills/<slug>/SKILL.md` | The skill under review | Read/Write |
| `docs/user/manpages/<verb>.md`, `docs/user/skills/<slug>.md` | Surfaces that repeat the skill's claims | Read/Write |
| `src/gzkit/skills_audit.py` | Review-age authority | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-how`](gz-how.md) | The skill-maintenance flow this skill belongs to |
| [`/gz-agent-sync`](gz-agent-sync.md) | Regenerates the mirrors after the edit |
| [`/ghi-author`](ghi-author.md) | Where a defect found outside the skill goes |
