# Minor releases ($X.Y.0$) — capability lane

Status: DRAFT
Last reviewed: 2026-01-10

## Canonical assertions

A release is a governance assertion, not a batch of commits.

Minor releases are how the product advances.

Silence is non-compliance.

Lane dividers have fuzz, but classification requires explicit rationale and smell checks.

This doctrine exists to detect drift in both the agent and the human operator.

## Minor definition (tight contract)

Minor releases:

- Introduce new capability.
- Preserve backward compatibility.
- May introduce deprecations but do not enforce them.

Minor releases MUST have an ADR.

Minor releases MUST have supporting OBPIs that itemize expectations.

## Governance artifact requirements

This lane SHALL comply with the SemVer × Governance Artifact Matrix:

- Primary intent carrier: ADR (mandatory).
- Supporting artifacts: OBPIs (mandatory).

### Prohibition: GitHub Issues as minor intent

GitHub Issues SHALL NOT be used as an intent mechanism at the minor level.

All minor-level intent MUST be expressed through ADR(s) and OBPI(s).

Using GitHub Issues to carry minor intent constitutes drift and non-compliance.

GitHub Issues may exist as operational trackers, but SHALL NOT be treated as the intent carrier for minor work.

## Minor classification rationale (required)

Every minor release SHALL include an explicit rationale statement that answers:

- What new capability is being introduced?
- How is backward compatibility preserved?
- What is deprecated, if anything, and what is the non-enforcement posture?
- Which ADR(s) carry the intent, and which OBPIs itemize expectations?

Silence is non-compliance: missing rationale is a release blocker.

## GovZero Gate Obligations

This section is mandatory.

### Gate 1 — Intent

Obligation:

- OBPI(s) SHALL exist and SHALL itemize expectations.

Satisfying artifacts:

- OBPI checklist(s) that map to the minor increment.

Non-compliance:

- Intent is carried primarily in GitHub Issues.
- OBPIs are missing or non-specific.

### Gate 2 — Design

Obligation:

- An ADR SHALL exist and SHALL be the primary intent carrier.
- The ADR SHALL define the capability, constraints, and compatibility posture.

Satisfying artifacts:

- ADR content and its linkage to OBPIs.

Non-compliance:

- The minor increment proceeds without an ADR.
- OBPIs no longer trace to ADR intent.

### Gate 3 — Implementation

Obligation:

- Implementation SHALL deliver the new capability.
- Implementation SHALL preserve backward compatibility.
- Deprecations MAY be introduced but SHALL NOT be enforced in the same minor.

Satisfying artifacts:

- Code changes implementing the ADR intent.
- Documentation claims align to implemented behavior.

Non-compliance:

- Breaking change is introduced without major classification.
- Deprecations are enforced rather than declared.

### Gate 4 — Verification

Obligation:

- Verification SHALL defend the new capability and the backward compatibility claim.

Satisfying artifacts:

- Verification evidence that covers new behavior and compatibility.

Non-compliance:

- New capability is shipped without defensible verification.

### Gate 5 — Human Attestation

Obligation:

- Gate 5 SHALL be required for all minor releases.

Satisfying artifacts:

- Recorded human attestation that operator-facing surfaces match the governance assertion.

Silence is non-compliance: missing attestation is non-compliance.

## Patch spillover rule (mandatory)

Patch-level issues discovered during minor implementation become patch increments.

They SHALL NOT be smuggled into the minor lane.

If patch defects are discovered:

- A GitHub Issue SHALL be created for the defect.
- The defect SHALL be resolved under a patch increment.

This rule is mandatory because patch is not sub-minor.

## Smell checks

### Minor smells (re-evaluate segmentation)

If any smell is present, the minor classification SHALL be re-evaluated:

- OBPI count is exploding inside one minor increment.
- OBPIs no longer trace to original ADR intent.
- Repeated “why wasn’t this hardened?” discoveries appear.
- Invariants are changing rather than being clarified.

Drift principle:

- Large OBPI accumulation within a single minor is a drift indicator; stop and reclassify.

### Major smells (re-evaluate as major)

If any major smell is present, reclassify:

- Contracts are being redefined.
- Backward compatibility is no longer honest.
- Migrations become conceptual, not additive.

## Authorized agent challenges

The AI Pair is authorized to challenge classification.

If any smell check in this document is present, the AI Pair MUST raise a classification challenge before proceeding.

- “The number of OBPIs in this minor suggests scope expansion — should we cut a new minor?”
- “This discovery affects invariants — should this trigger a new minor or major reclassification?”
- “This patch request seems to redefine behavior — is this actually a minor/major?”
- “This GH Issue appears to introduce new capability — should this be an OBPI?”

Silence is non-compliance: unanswered challenges SHALL be treated as a blocker.
