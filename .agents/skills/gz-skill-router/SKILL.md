---
name: gz-skill-router
description: Route agents to the correct skill for a given task type. Use when starting a session, when unsure which skill applies, or when an agent needs to discover the right workflow for a task.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-11
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
---

# gz-skill-router

Route agents to the correct gzkit skill based on task type. This is a lookup
aid, not an orchestrator — it maps intent to the right workflow entry point.

---

## When to Use

- Starting a new session and unsure which skill applies
- Task description is ambiguous across multiple skill domains
- Onboarding a new agent to gzkit's skill catalog

## When NOT to Use

- You already know which skill to invoke
- The task is a simple CLI command (just run it)

---

## Decision Tree

```
Task arrives
    │
    ├── Exploring a new idea or feature?
    │   ├── Vague idea, needs design dialogue ──────→ gz-design
    │   ├── Ready to define product requirements ───→ gz-prd
    │   └── Ready to record an architecture decision → gz-plan
    │
    ├── Creating or managing ADRs?
    │   ├── Create a new ADR with interview ────────→ gz-adr-create
    │   ├── Promote a pool ADR to canonical ────────→ gz-adr-promote
    │   ├── Evaluate ADR quality (scoring) ─────────→ gz-adr-evaluate
    │   ├── Check ADR lifecycle/OBPI status ────────→ gz-adr-status
    │   ├── Sync ADR index/status registries ───────→ gz-adr-sync
    │   ├── Build ADR-to-artifact traceability ─────→ gz-adr-map
    │   ├── Scan @covers tags and update links ─────→ gz-adr-autolink
    │   └── Emit a receipt event to the ledger ─────→ gz-adr-emit-receipt
    │
    ├── Working on an OBPI?
    │   ├── Decompose ADR into OBPI briefs ─────────→ gz-obpi-specify
    │   ├── Audit plan alignment before coding ─────→ gz-plan-audit
    │   ├── Execute the full implementation pipeline → gz-obpi-pipeline
    │   ├── Claim/release OBPI work locks ──────────→ gz-obpi-lock
    │   ├── Review code quality after implementation → gz-obpi-simplify
    │   └── Reconcile briefs against evidence ──────→ gz-obpi-reconcile
    │
    ├── Auditing or closing out?
    │   ├── Gate 5 audit (COMPLETED → VALIDATED) ───→ gz-adr-audit
    │   ├── Human attestation ceremony ─────────────→ gz-adr-closeout-ceremony
    │   └── GHI-driven patch release ───────────────→ gz-patch-release
    │
    ├── Running checks or validation?
    │   ├── Full quality checks (lint+test+type) ───→ gz-check
    │   ├── Gate compliance for an ADR ─────────────→ gz-gates
    │   ├── Gate 2 implementation verification ─────→ gz-implement
    │   ├── Validate governance artifacts ──────────→ gz-validate
    │   ├── Query artifact relationships ───────────→ gz-state
    │   ├── Report gate/lifecycle status ───────────→ gz-status
    │   └── Audit CLI doc coverage ─────────────────→ gz-cli-audit
    │
    ├── Governance infrastructure?
    │   ├── Initialize gzkit scaffolding ───────────→ gz-init
    │   ├── Create/refresh constitution ────────────→ gz-constitute
    │   ├── Validate config path coherence ─────────→ gz-check-config-paths
    │   └── Record semver migration events ─────────→ gz-migrate-semver
    │
    ├── Agent & repository operations?
    │   ├── Sync skill mirrors and surfaces ────────→ gz-agent-sync
    │   ├── Commit and push with quality gates ─────→ git-sync
    │   ├── Preserve context across sessions ───────→ gz-session-handoff
    │   ├── Run maintenance chores ─────────────────→ gz-chore-runner
    │   └── Repository hygiene and cleanup ─────────→ gz-tidy
    │
    └── Cross-repository?
        └── AirlineOps governance parity scan ──────→ airlineops-parity-scan
```

---

## Keyword Lookup

| Intent / Keyword | Skill |
|------------------|-------|
| design, brainstorm, explore, "let's build" | `gz-design` |
| create ADR, new ADR, book ADR | `gz-adr-create` |
| promote pool ADR | `gz-adr-promote` |
| evaluate ADR, score ADR, red-team | `gz-adr-evaluate` |
| ADR status, lifecycle | `gz-adr-status` |
| specify, decompose, create briefs | `gz-obpi-specify` |
| plan audit, alignment check | `gz-plan-audit` |
| implement, execute pipeline, run OBPI | `gz-obpi-pipeline` |
| lock, claim, release OBPI | `gz-obpi-lock` |
| simplify, code review, craft | `gz-obpi-simplify` |
| reconcile, audit briefs, sync table | `gz-obpi-reconcile` |
| audit ADR, Gate 5, validate ADR | `gz-adr-audit` |
| closeout, ceremony, attest | `gz-adr-closeout-ceremony` |
| patch release, cut release | `gz-patch-release` |
| check, lint, test, quality | `gz-check` |
| gates, gate compliance | `gz-gates` |
| status, blockers, next actions | `gz-status` |
| state, artifact graph, lineage | `gz-state` |
| validate, schema, surfaces | `gz-validate` |
| sync, mirrors, control surfaces | `gz-agent-sync` |
| commit, push, git sync | `git-sync` |
| handoff, session, context | `gz-session-handoff` |
| chore, maintenance | `gz-chore-runner` |
| tidy, cleanup, hygiene | `gz-tidy` |
| parity, airlineops | `airlineops-parity-scan` |

---

## Staleness Warning

This router must be updated when skills are added, renamed, or retired. After
any skill catalog change, verify this decision tree still covers all active
skills. The `gz-agent-sync` skill should trigger a router review.

---

## Attribution

Routing pattern adapted from `using-agent-skills` in
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT).

## Related

- `AGENTS.md` § Available Skills (the authoritative catalog)
- `gz-agent-sync` (triggers after skill changes)
