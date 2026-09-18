---
name: gz-status
description: Report project workflow fronts alongside ADR lifecycle and gate status. Use for ordinary status inquiries, blockers, and next actions, or a focused governance status check.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-17
metadata:
  skill-version: "1.3.0"
model: haiku
---

# gz status

## Overview

Operate the gz status command surface as a reusable governance workflow.

## Operator ruling (verbatim canon)

Status covers handoff system, GHI triage, ADR/OBPI campaign, and new R&D. Read Workflow fronts in the campaign selected by data/active_campaign.json; use gz-status to report evidence, freshness or unknowns, and next actions. Focused inquiries include material dependencies. Handoffs preserve the map reference and session changes. The campaign owns the map; live sources establish progress. Campaign sequence, ascending feature-ADR order, and operator-only OBPI initiation govern execution.

> Carried verbatim from root `AGENTS.md` § Operator Doctrine on 2026-09-17 (GHI #921); the corpus `.gzkit/corpus/AGENTS.md.jsonl` keeps the ruling's history.

## Workflow

1. Determine whether the inquiry is project-wide or focused on an ADR/OBPI.
   An ordinary "status?" is project-wide; the operator need not name every front.
2. Run `uv run gz status` with the required options. If the project registers an
   active campaign in `data/active_campaign.json`, read its `## Workflow fronts`
   section, also projected in the command's `workflow_fronts` JSON field.
   This is declared context, not a live assessment of every front. Report an
   unavailable declared source explicitly; do not infer that the front is healthy.
3. For project-wide status, consider every declared front. In gzkit these are
   **handoff system**, **ghi triage**, **adr/obpi campaign**, and **new R&D**.
   Read each front's named evidence: handoff lineage/rulings and observed resume
   behavior; current GitHub work orders (use `ghi-triage` for a full ranked pass);
   campaign sequencing and ledger-backed lifecycle; research questions and
   experiment results. Date cached evidence and label anything not re-verified.
   Do not equate issue volume, an unresolved hypothesis, or declared context with
   ill health. Keep observed defects and actual blockers specific.
4. For a focused single-OBPI runtime view, run `uv run gz obpi status <id>` to
   inspect one brief's lifecycle state, gate completion, and lock status.
5. Give each front a concise state, evidence/date, and next action in a general
   answer. A focused answer covers its target and material cross-front dependencies.
   Campaign sequence and operator initiation govern execution; a status inquiry
   does not initiate OBPI work or promote an R&D question into a new ADR.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with `uv run gz status` or `uv run gz state`.

## Example

```bash
# Project fronts and ADR-level gate status summary
uv run gz status

# Focused single-OBPI view (runtime state, gates, locks)
uv run gz obpi status OBPI-0.0.67-02-wire-orphan-verbs-into-skills
```
