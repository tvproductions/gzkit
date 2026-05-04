---
id: ADR-pool.complexity-doctrine-validate-suite
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.0.27
inspired_by: ADR-0.0.27
---

# ADR-pool.complexity-doctrine-validate-suite: Complexity Doctrine Validate Suite

## Status

Pool

## Date

2026-05-04

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Aggregate the auxiliary `gz validate` scopes that harden the complexity-doctrine surface beyond OBPI-0.0.27-07's link-integrity validator. Three named candidate scopes were surfaced during the ADR-0.0.27 design dialogue: `--classifier-schema-frozen` (asserts the advisor classifier schema is locked between distillations and only amendment-protocol changes can move it), `--corpus-shas-pinned` (asserts every `data/exemplar_corpus.json` entry is a pinned SHA, fail-closed against floating-HEAD drift), and `--distillation-cadence` (asserts the distilled-characteristics document timestamps satisfy the cadence triggers in `.gzkit/rules/complexity-doctrine.md`). Together these form the mechanical defense suite for the complexity-doctrine cluster's data integrity. This ADR-pool entry holds the forward-reference until the suite's individual scopes accumulate enough operator-observed defect signal to warrant a single foundation ADR.

Booked at OBPI-0.0.27-02 as a forward-reference in the citation graph. Activates when one or more of the named candidate scopes proves load-bearing in operator practice.
