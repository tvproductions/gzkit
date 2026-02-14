# Patch releases ($X.Y.Z$) — defect lane

Status: DRAFT
Last reviewed: 2026-01-10

## Canonical assertions

A patch release is a governance assertion, not a batch of commits.

Patch releases SHALL be classified as defect work.

Silence is non-compliance.

Lane dividers have fuzz, but classification requires explicit rationale and smell checks.

This doctrine exists to detect drift in both the agent and the human operator.

## Patch definition (precise)

Patch releases address defects in existing behavior, including:

- Bugs
- Discovery gaps found during implementation
- Sharpening and clarifying ambiguous requirements
- Hardening, robustness, and invariance articulation

When and only when these changes improve the availability, correctness, or robustness of already-intended behavior.

Patch releases MUST NOT introduce new capability.

Patch releases MUST be driven by GitHub Issues as the authoritative capture mechanism.

Doctrine notes:

- Patch is NOT “sub-minor.”
- Minor is how the product advances; patch is how intended behavior becomes reliably available.

## Governance artifact requirements

This lane SHALL comply with the SemVer × Governance Artifact Matrix:

- Primary intent carrier: GitHub Issue (mandatory).
- Supporting artifacts: none by default.

An ADR is not expected for a patch unless the patch reveals a design break.

If a design break is discovered, the work SHALL be reclassified.

## Patch classification rationale (required)

Every patch release SHALL include an explicit rationale statement that answers:

- What existing behavior was intended but unavailable or incorrect?
- What defect prevented availability, correctness, or robustness?
- Why does this change not introduce new capability?

Silence is non-compliance: missing rationale is a release blocker.

## GovZero Gate Obligations

This section is mandatory.

### Gate 1 — Intent

Obligation:

- A GitHub Issue SHALL exist and SHALL be the primary intent record.

Satisfying artifacts:

- The issue text, labels, and acceptance criteria.

Non-compliance:

- The patch is carried as an OBPI or ADR without an issue.
- The issue is vague and does not specify the defect.

### Gate 2 — Design

Obligation:

- Patch work SHALL not require a new ADR.

Satisfying artifacts:

- The patch rationale and smell checks.

Reclassification triggers:

- The patch changes invariants rather than clarifying them.
- The patch introduces new concepts.

### Gate 3 — Implementation

Obligation:

- Implementation SHALL correct the defect.
- Implementation SHALL not introduce new capability.

Satisfying artifacts:

- Code changes that restore intended behavior.
- Documentation claims remain aligned to behavior.

Non-compliance:

- New user-facing concepts are introduced to support the patch.

### Gate 4 — Verification

Obligation:

- Verification SHALL defend the claim that intended behavior is now available and correct.

Satisfying artifacts:

- Tests or other verification evidence appropriate to the defect.

Non-compliance:

- The defect is declared fixed without defensible verification.

### Gate 5 — Human Attestation

Obligation:

- Gate 5 is required when a patch changes observable behavior or operator workflow in a way that must be witnessed.

Threshold declaration:

- If the defect affects user-visible CLI output, documented operator procedures, or external contracts, Gate 5 SHALL be required.

Satisfying artifacts:

- Recorded human attestation that the observable surfaces match the claim.

Silence is non-compliance: if the threshold is met, attestation SHALL occur.

## Smell checks

### Patch smells (re-evaluate as minor)

If any smell is present, the patch classification SHALL be re-evaluated:

- Introduces new capability.
- Adds new concepts or entities that were not already intended.
- Requires new user-facing explanation beyond defect correction.

### Minor spillover rule

If patch-level defects are discovered during minor implementation:

- They SHALL be carried as patch increments.
- They SHALL NOT be smuggled into the minor lane.

## Authorized agent challenges

The AI Pair is authorized to challenge classification.

If any smell check in this document is present, the AI Pair MUST raise a classification challenge before proceeding.

- “This GH Issue appears to introduce new capability — should this be an OBPI?”
- “This patch request seems to redefine behavior — is this actually a minor/major?”
- “This discovery affects invariants — should this trigger a new minor or major reclassification?”

Silence is non-compliance: unanswered challenges SHALL be treated as a blocker.
