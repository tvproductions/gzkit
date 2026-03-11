# OBPI Transaction Contract

**Status:** Active
**Last reviewed:** 2026-03-11
**Parent ADR:** `ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`

---

## Overview

The OBPI transaction contract defines the fail-closed execution boundary for one
OBPI increment.

An OBPI is not just a brief file or checklist row. It is a bounded transaction
with an explicit scope contract, required evidence, and a human authority
boundary for Heavy and Foundation work.

This contract governs what later runtime validators and operator workflows must
enforce. Machine-readable runtime state remains defined in
[OBPI Runtime Contract](obpi-runtime-contract.md).

---

## Context Loading

Every OBPI transaction begins by loading the execution context that justifies
the work.

Minimum context inputs are:

- the OBPI brief
- the parent ADR
- the active allowlist and denied-path contract
- prior handoff context when the session is resumed

When a plan-audit receipt exists, it becomes part of the transaction context and
must be read before implementation begins. Until receipt-generation parity lands
in gzkit, missing receipt files are a compatibility gap, not permission to skip
scope review or improvise the plan.

---

## Core Rules

1. Every OBPI MUST declare `Allowed Paths` as an explicit allowlist contract.
1. Any file outside `Allowed Paths` is denied unless the OBPI is amended or a
   replacement OBPI is created.
1. Completion MUST fail closed when the changed-files audit shows a path outside
   the allowlist.
1. Missing orchestration primitives MUST be treated as blockers or explicit
   compatibility constraints, never silently ignored.
1. Heavy and Foundation work MUST preserve Gate 5 human attestation as the
   completion authority boundary.
1. If prerequisites, evidence, or scope conditions are missing, the workflow
   MUST STOP and emit `BLOCKERS`.

Advisory wording is not sufficient. Scope isolation is law, not guidance.

---

## Scope Isolation

`Allowed Paths` define the full write surface for an OBPI transaction.

Required implications:

- listed paths are in scope
- unlisted paths are out of scope
- widening scope requires governance action, not silent expansion
- "related cleanup" is not a valid justification for touching denied surfaces

The minimum audit is the repository changed-files set:

```bash
git diff --name-only
```

If the changed-files set contains an unallowlisted path, the OBPI must halt with
`BLOCKERS` before completion can proceed.

---

## Spine Surfaces

Some repository surfaces create cross-OBPI merge and authority risk and must be
treated as spine surfaces.

Spine surfaces include:

- dependency and lock files
- CI and automation configuration
- global registries, manifests, and routing tables
- repository-wide governance doctrine that changes multiple downstream surfaces
- build, release, or ingest facades that affect unrelated workstreams

An OBPI that touches a spine surface MUST say so explicitly in its allowlist.
Only one spine-touch OBPI may be active at a time unless a stricter local rule
already exists.

---

## Parallel Execution

Parallel OBPI execution is allowed only when all of the following are true:

- the active OBPIs have disjoint allowlists
- none of the active OBPIs touches a shared spine surface
- blocker-producing prerequisites are already satisfied for each OBPI
- evidence and attestation ownership remain independent per OBPI

Parallel execution must stop with `BLOCKERS` when:

- allowlists overlap in a way that can produce semantic conflicts
- one OBPI needs scope expansion into another OBPI's surface
- a spine surface is shared
- prerequisite evidence or human review for the lane is missing

Disjointness must be reasoned from the allowlists, not from agent confidence.

---

## Compatibility Constraints

The transaction contract must stay honest about current repository capability.

Current gzkit compatibility rules:

- if a plan-audit receipt exists, consume it during context loading
- if no receipt exists, record that absence as a governance gap and continue
  only with explicit brief-grounded scope review
- until `gz-obpi-lock` parity exists, any shared-scope or spine-touch work must
  run as a single active OBPI
- if concurrent execution is needed and no lock surface exists, stop with
  `BLOCKERS`

Compatibility notes narrow behavior. They do not relax the contract.

---

## Evidence and Authority

Every OBPI transaction must produce enough evidence for a human reviewer to
inspect what changed and why the change is valid.

Minimum evidence expectations:

- changed-files audit against `Allowed Paths`
- verification command list and outcomes
- value narrative and key proof
- lane-appropriate attestation evidence

Agents may prepare and summarize this evidence. They may not replace human
attestation for Heavy or Foundation work.

---

## BLOCKERS Output

When work cannot continue, emit `BLOCKERS:` followed by one blocker per line.

Typical blocker causes:

- prerequisite file or directory missing
- plan-audit receipt exists but fails alignment or references the wrong OBPI
- changed-files audit includes a denied path
- required evidence is absent or placeholder-only
- Heavy or Foundation completion lacks human attestation evidence
- parallel execution would overlap or share a spine surface
- concurrent/shared-scope execution is needed but no lock surface exists

---

## Related

- [OBPI Runtime Contract](obpi-runtime-contract.md)
- [ADR/OBPI/GHI/Audit Linkage](adr-obpi-ghi-audit-linkage.md)
- [Audit Protocol](audit-protocol.md)
