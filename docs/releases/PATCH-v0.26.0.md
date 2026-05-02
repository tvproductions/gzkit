# Release: v0.26.0

**Date:** 2026-05-01
**Previous Version:** 0.25.19
**Previous Tag:** v0.25.19

## ADR

ADR-0.26.0-governance-library-module-absorption

Item-by-item evaluation and absorption of 12 opsdev/lib governance modules
(~6,200 lines) into gzkit. Each OBPI records a per-module decision (Absorb,
Confirm, or Exclude) backed by code-level subtraction-test evidence.

## Closeout Evidence

All 12 OBPIs Completed and human-attested by g0. Closeout walkthrough
green:

- lint: `arb-ruff-9453b996c0424e49a0de093608f7ca9d`
- typecheck: `arb-step-typecheck-68c819510879480da0e9159264fe5d32`
- unittest: `arb-step-unittest-24779d6c71194f3eae87b4b3a731e3c2`
- mkdocs: `arb-step-mkdocs-0d69e336977a4624a738ee22484e7e19`

## Operator Approval

Approved at ADR-0.26.0 closeout ceremony.

## In-Flight Note

This manifest exists to satisfy `audit_version_release` during the brief
window between the closeout commit and `gh release create v0.26.0`
(GHI #217 in-flight allowance). The tag will be created immediately
following the closeout sync.
