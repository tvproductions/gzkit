# CHORE: Control Surface — Skill ↔ Rule Reachability Audit (Pass B)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `control-surface-skill-rule-reachability`

---

## Overview

Audit-only pass. For every skill under `.gzkit/skills/**`, enumerate which `.gzkit/rules/**` entries govern its procedure and whether the skill body honors them. Output is a reachability matrix flagging skills that route around applicable rules — a class of drift that `.gzkit/rules/tool-skill-runbook-alignment.md` names at the CLI-verb level but does not yet enumerate at the skill-procedure level.

Background: `gz-adr-audit` Step 2 ("If audit-check fails, fix brief evidence first") can push an agent into violating `tests.md` § "Tests assert semantics" by backfilling cosmetic `@covers` decorators. The skill does not cite the rule; the rule does not anticipate the skill's procedure. Today's ADR-0.0.17 audit surfaced that exact tension and produced GHI #268.

## Policy and Guardrails

- **Lane:** Lite — audit-only; zero edits to skills, rules, or source.
- **Scope:** every `SKILL.md` under `.gzkit/skills/**`. Vendor mirrors (`.claude/skills/`, `.agents/skills/`, `.github/skills/`) are derivatives and are NOT audited.
- **Rule applicability test.** A rule applies to a skill if (a) the skill's `paths:` frontmatter overlaps the rule's `paths:` frontmatter, OR (b) the skill's procedure invokes a CLI verb the rule governs, OR (c) the skill modifies files the rule's `paths:` covers.
- **Honors test.** A skill honors an applicable rule if the skill body either cites the rule by filename OR enforces the rule's invariant mechanically (e.g. by calling `gz validate --<scope>`). Absence of both is a reachability gap.

## Workflow

### 1. Enumerate skills + rules

List every skill with its declared `gz_command`, allowed paths, and body-cited rules. Record in `proofs/skill-inventory.md`.

### 2. Build reachability matrix

For each (skill, applicable-rule) pair, one row in `proofs/reachability-matrix.md`:

- Skill slug + version
- Rule file + § section
- Applicability basis (path overlap / CLI verb / file modification)
- Honored: yes (cite) / yes (mechanical) / no
- If no: concrete worked example of the skill procedure violating the rule

### 3. Cross-reference with GHI trail

For each "no" row, scan recent GHIs (#141–current) for a defect that matches the violation pattern. Record hits in `proofs/ghi-cross-reference.md`. A "no" row with a historical GHI hit is a known-blocking gap; a "no" row without one is latent.

### 4. Summary

`proofs/summary.md`: counts of honored / gap-latent / gap-known-blocking; top 5 known-blocking with a one-line recommendation per (reconcile skill / reconcile rule / promote mechanical check / accept gap).

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/skill-inventory.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/reachability-matrix.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/ghi-cross-reference.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/summary.md` | 0 |

## Evidence Commands

```bash
ls .gzkit/skills/ > .gzkit/chores/control-surface-skill-rule-reachability/proofs/skill-listing.txt
ls .gzkit/rules/ > .gzkit/chores/control-surface-skill-rule-reachability/proofs/rule-listing.txt
```

---
