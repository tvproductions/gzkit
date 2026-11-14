---
id: security-sensitivity
paths:
  - "docs/design/adr/**/obpis/**"
  - "data/security_surfaces.json"
description: Security-sensitivity third axis of attestation rigor (ADR-0.0.22).
---

<!-- rule-version: 0.7.0 -->

# Security Sensitivity (gzkit)

> **Rule version:** `0.7.0` — § Heightened walkthrough carries the checklist `gz obpi complete` reads, and drops the co-presence proxy gate ADR-0.0.36 removed (RP-7 held ruling H4, operator, 2026-11-13: *"A: Add checklist now"*); prior banners in [Rule Version History](../../docs/governance/rule-version-history.md#security-sensitivitymd).

## Invariant

**Security work needs heightened review regardless of lane or kind.** A brief carrying `sensitivity: security` always requires human attestation for completion — consistent with the universal attestation rule in ADR-0.0.36. The axis is additive: heavy lane, foundation kind, and security sensitivity each independently determine which gates fire; Gate 5 brief-level human attestation is universal for every OBPI regardless of kind, lane, or sensitivity.

## Registry contract

Security surfaces are named in [`data/security_surfaces.json`](../../data/security_surfaces.json). The registry is self-bootstrapping: edits require the editing brief to declare `sensitivity: security`.

**Direct-fix path (no brief exists).** Operator canon routes GHI-tracked defect repair to a direct `fix(<scope>): … (GHI #N)` commit and forbids spinning up an OBPI merely to discharge a GHI — so a registry correction filed as a GHI has **no brief and therefore no declaration channel**. `gz validate --sensitivity` reads OBPI brief frontmatter only (`src/gzkit/commands/validate_sensitivity.py`: `declared = frontmatter.get("sensitivity")`; the audit in `src/gzkit/governance/trust_audits/sensitivity.py` reads the same field); a briefless commit to `data/security_surfaces.json` is never inspected, so the self-bootstrapping floor is **unenforced on the path operator canon mandates**. Until a commit-side channel exists (candidate: a `Sensitivity: security` trailer checked by `gz validate --commit-trailers`), the declaration on a direct-fix registry edit is a **discipline obligation, not a mechanical one** — state the sensitivity in the commit body and cite the GHI. Do not read the absence of a fail-close as permission.

## `gz validate --sensitivity` (binding)

1. **Auto-detect floor.** Briefs whose allowed-paths overlap a registered security surface MUST declare `sensitivity: security` (exit 3 on violation).
2. **Escalate-not-escape.** A brief MAY declare sensitivity without overlap (escalation). A brief MAY NOT omit sensitivity while overlapping (escape is fail-closed). Both an *omitted* declaration (`sensitivity-floor-violation`) and a *wrong* declaration (`sensitivity-escape-attempt`) over an overlap fail closed at exit 3 (GHI #625).
3. **The floor demotes to advisory inside the MX hangar — say so out loud.** When the MX condition is on (the `.gzkit/mx.json` marker is present, parses, is bound to an open `mx_session_opened` and is not exiting: `marker.condition(...).on`, read by `src/gzkit/mx/checkpoint.py`), `mx-mode.md` § Honor the marker drops every guard outside `GATE5_INVARIANTS` to advisory. `sensitivity` is **not** a member of that set (`src/gzkit/mx/invariants.py`), so `checkpoint.resolve("sensitivity", …)` returns ADVISORY and the exit-3 errors above are dropped from the exit code. The "escape is fail-closed" language in clause 2 does **not** hold in the hangar. This demotion is **deliberate, not a defect**: the briefs most likely to trip the floor are exactly the ones an operator enters the hangar to repair (GHI #682, closed 2026-07-24, was two post-cutover briefs failing the floor over incidental overlap), and a fail-closed sensitivity scope would lock the repair path against the thing being repaired. Promoting `sensitivity` into `GATE5_INVARIANTS` would set that trap; do not do it without first discharging #682. What was wrong was the **silence** — the demotion happened unannounced. It is now named.

### Grandfather cutover (GHI #625)

The omitted-declaration floor was tightened from informational (`sensitivity-floor-info`, exit 0) to fail-closed (`sensitivity-floor-violation`, exit 3) after 87 pre-existing briefs were found overlapping a registered surface without a declaration — most overlaps incidental (e.g. an additive audit-wrapper touching `src/gzkit/quality.py`), not unflagged security work. Those briefs are grandfathered in [`data/sensitivity_floor_grandfather.json`](../../data/sensitivity_floor_grandfather.json); they remain at the informational floor. Every **new** brief that overlaps a registered surface MUST declare `sensitivity: security` or it fails closed. If the overlap is an incidental false positive, narrow the Allowed Paths or discharge at completion via `gz obpi complete --accept-security-floor`. Do not add new entries to the grandfather file to silence a fresh violation — that is the escape the cutover exists to close.

## Heightened walkthrough

`gz obpi complete` on a `sensitivity: security` brief fires an extended Gate 5 walkthrough over the checklist below, which it reads from this section at runtime (REQ-0.0.22-05-02). Scanner-unavailable is fail-closed (no degradation). The co-presence proxy gate this walkthrough once named was removed with the TTY attestation gate (ADR-0.0.36; its residue is GHI #1308).

### Walkthrough checklist

- Surface enumeration: name every registered security surface the brief touched (`data/security_surfaces.json`), and the operator confirms each.
- Receipt confirmation: cite the canonical security-scan receipt (`arb-step-security-scan-*`) by its ID.
- Classification confirmation: the operator confirms the `sensitivity: security` declaration matches the work.

## Do Not

- Declaring `sensitivity: absent` while touching a registered surface
- Editing `data/security_surfaces.json` without declaring `sensitivity: security`
- Narrative substitution for the security-scan receipt
- Bundling security work into a non-security parent OBPI

> See [`docs/governance/security-sensitivity-rationale.md`](../../docs/governance/security-sensitivity-rationale.md) for walkthrough enumeration details, scanner-unavailable failure mode rationale, and related references.
