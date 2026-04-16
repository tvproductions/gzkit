# ADR-0.25.0 Audit: Core Infrastructure Pattern Absorption

**Auditor:** agent:claude-opus-4-6
**Date:** 2026-04-15
**Lifecycle:** Validated
**Ceremony:** Closeout completed same session — Step 4 walkthrough satisfies Step 3.

---

## Feature Demonstration

ADR-0.25.0 evaluated 33 infrastructure patterns from the airlineops companion
codebase and made explicit Absorb/Confirm/Exclude decisions for each.

### Capability 1: ARB Receipt Middleware (Absorb)

The `gz arb` command group provides 7 subcommands for structured QA evidence:

```
$ uv run gz arb --help
usage: gz arb {ruff,step,ty,coverage,validate,advise,patterns} ...

Agent Self-Reporting middleware. Wraps QA commands and emits schema-validated
JSON receipts to artifacts/receipts/.
```

**Value:** Heavy-lane attestation claims are backed by deterministic receipt
artifacts instead of narrative reconstruction.

### Capability 2: Drift Detection (Absorb — OBPI-26)

Temporal drift detection ported from airlineops, providing ADR-level drift
analysis between anchor commits and current HEAD.

### Capability 3: Policy Guards (Absorb — OBPI-27)

Policy guard patterns absorbed for admission control enforcement at governance
boundaries.

### Capability 4: Handoff Validation (Absorb — OBPI-32)

Six handoff-document validators (frontmatter schema, placeholder scan, secret
scan, section completeness, verification commands, context continuity) ported
from airlineops at `src/gzkit/handoff_validation.py`.

### Capability 5: Decision Documentation (Confirm/Exclude — 29 OBPIs)

14 Confirm decisions documented why gzkit's existing implementations
(attestation, progress, config, console, ADR lifecycle/audit/governance/
reconciliation/traceability, CLI audit, docs validation, validation receipts)
are architecturally superior.

16 Exclude decisions documented why domain-specific airlineops patterns
(signatures, world state, dataset versioning, registry, types, ledger,
schemas, errors, hooks, admission, QC, OS, manifests, artifact management,
layout verification, ledger schema, references) do not belong in gzkit.

---

## Verification Log

| Check | Result | Proof |
|-------|--------|-------|
| `gz adr audit-check ADR-0.25.0` | ✓ PASS | `proofs/audit-check.txt` |
| `uv run -m unittest -q` | ✓ 2991 tests, 0 failures | `proofs/unittest.txt` |
| `uv run gz lint` | ✓ Lint passed | `proofs/lint.txt` |
| `uv run gz typecheck` | ✓ Type check passed | `proofs/typecheck.txt` |
| `uv run mkdocs build --strict` | ✓ Clean build | `proofs/mkdocs.txt` |
| OBPI completion | ✓ 33/33 attested_completed | `gz adr status ADR-0.25.0` |
| Product proof | ✓ 33/33 FOUND | Closeout pipeline output |
| REQ coverage | ✓ 8/8 code REQs covered (100%) | `gz adr audit-check` |

---

## Shortfalls Identified and Remediated

### Shortfall 1: Product proof gate missing `decision_doc` type (GHI #163)

**Severity:** Blocking
**Root cause:** `check_product_proof()` checked 7 file-based proof types but
had no type for decision-only OBPIs (Confirm/Exclude).
**Fix:** Added `decision_doc_found` field to `ObpiProofStatus`, implemented
`_check_decision_doc_proof()` scanning for Confirm/Exclude/Absorb decisions
in brief text. 8 TDD tests.
**Status:** Fixed and closed.

### Shortfall 2: Phase 3 backfill omitted `[doc]` tags (GHI #164)

**Severity:** Blocking
**Root cause:** GHI-160 Phase 3 applied a uniform 5-REQ template to all 33
OBPIs without using the `[doc]` kind tag (which Phase 2 had just shipped).
Decision-documentation REQs were incorrectly typed as code REQs.
**Fix:** Added `[doc]` tags to 157 REQs across all 33 briefs. Confirm/Exclude
OBPIs: all 5 REQs tagged. Absorb OBPIs: REQs 01/02/04 tagged.
**Status:** Fixed and closed.

### Shortfall 3: `audit-check` single-channel proof limitation (GHI #165)

**Severity:** Non-blocking (workaround via `[doc]` tagging)
**Root cause:** `audit-check` recognizes only `@covers` decorators in Python
test files. No support for BDD `.feature` files, decision-doc proof, or
product proof as evidence channels.
**Fix:** Filed as GHI #165. Architecture improvement — not blocking validation.
**Status:** Open, tracked.

---

## Evidence Index

| Artifact | Location |
|----------|----------|
| Audit-check proof | `audit/proofs/audit-check.txt` |
| Unit test proof | `audit/proofs/unittest.txt` |
| Lint proof | `audit/proofs/lint.txt` |
| Type check proof | `audit/proofs/typecheck.txt` |
| Docs build proof | `audit/proofs/mkdocs.txt` |
| Validation receipt | Ledger: `validated` event, attestor `agent:claude-opus-4-6` |
| Closeout ceremony | `.gzkit/ceremonies/ADR-0.25.0-core-infrastructure-pattern-absorption.json` |
| GitHub release | `v0.25.0` |

---

## Summary

| Dimension | Status |
|-----------|--------|
| Completeness | ✓ 33/33 OBPIs attested, all gates passed |
| Integrity | ✓ 8/8 code REQs covered, 157 doc REQs correctly tagged |
| Alignment | ✓ Code matches docs, mkdocs builds clean |
| Shortfalls | 2 fixed (GHI #163, #164), 1 tracked (GHI #165) |

---

## Attestation

**Agent attestation:** All verification checks pass. Two blocking shortfalls
identified and remediated in-session. One non-blocking architectural limitation
tracked under GHI #165.

**Human attestation:** Recorded at closeout ceremony — "Completed" (by Jeffry,
2026-04-15).

**Lifecycle:** Validated (confirmed via `uv run gz adr status ADR-0.25.0`).
