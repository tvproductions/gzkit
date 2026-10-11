# /gz-complexity-distill

Run a complexity distillation pass against the exemplar corpus to refresh the
distilled-characteristics doctrine. A cadence trigger below (annual calendar,
advisor verdict-frequency drift > 25% from baseline, or operator judgment for a
ground-breaking project) makes a pass due; the pass itself is OBPI work the
operator initiates.

---

## Purpose

`/gz-complexity-distill` is the operator-facing surface for the
four-ADR complexity-doctrine cluster's distillation cadence (ADR-0.0.27 →
ADR-0.0.28 → ADR-0.0.29 → ADR-0.0.30). Distillation produces a dated
distilled-characteristics document at
`docs/governance/complexity/distilled-characteristics-{YYYY-MM-DD}.md`,
authored jointly by the agent (metric-aggregate prose) and the operator
(practitioner-eye observation per metric) and attested at Gate 5. The first
document was attested at OBPI-0.0.27-04's Gate 5. Each recurring pass runs as
an OBPI under a feature ADR and is attested at that OBPI's Gate 5 (operator
ruling 2026-10-11): `ADR-0.0.27` is terminal and the foundation kind is closed.

## When to Use

Three triggers, any of which makes a distillation pass due:

1. **Annual calendar (default).** Re-distillation runs once per year.
2. **Drift signal.** Advisor verdict-frequency drift > 25% from the
   baseline of the last distillation, with a minimum 6-month
   re-distillation interval to prevent thrashing.
3. **Operator judgment.** Ad-hoc invocation when a ground-breaking
   project emerges that warrants corpus amendment.

## What to Expect

The skill reads its canonical execution contract from
`.gzkit/skills/gz-complexity-distill/SKILL.md` (mirrored into
`.claude/skills/`, `.agents/skills/`, and `.github/skills/` by
`gz agent sync control-surfaces`). Follow the agent-facing instructions
in that file for the joint authoring sequence, the per-metric triple
shape, and the no-overwrite preservation discipline.

## Invocation

```text
/gz-complexity-distill
```

The destination CLI verb is `uv run gz complexity distill`
([manpage](../manpages/complexity-distill.md)). It landed under
[GHI #400](https://github.com/tvproductions/gzkit/issues/400), which closed
the OBPI-0.0.27-06 waiver path.

## Output Contract

The destination verb writes a new dated distilled-characteristics document
under `docs/governance/complexity/`. Form on stdout: a human-readable
progress summary naming the corpus revision under measurement, the
baseline artifact path produced, the destination document path written,
and the count of per-metric sections rendered. Exit codes follow the
clig.dev / `.claude/rules/cli.md` standard: 0 success, 1 user/config
error, 2 system/IO error, 3 policy breach (e.g. would overwrite an
existing same-date document — REQ-0.0.27-04-05 no-overwrite guard).

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-complexity-distill/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-complexity-distill/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-complexity-distill/SKILL.md` | Codex mirror | Read |
| `data/exemplar_corpus.json` | Pinned-SHA corpus (single source of truth) | Read |
| `src/gzkit/complexity/distillation.py` | Engine (render functions, frozen models) | Read |
| `docs/governance/complexity/distilled-characteristics-{date}.md` | Output document | Write |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-justify`](gz-justify.md) | Pre-execution reasoning if methodology trade-offs feel ambiguous |
| [`/gz-obpi-pipeline`](gz-obpi-pipeline.md) | A recurring pass runs as an OBPI the operator initiates under a feature ADR; that OBPI's Gate 5 is the attestation |
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
