# Major releases ($X.0.0$) — contract break lane

Status: DRAFT
Last reviewed: 2026-01-10

## Canonical assertions

A release is a governance assertion, not a batch of commits.

Major releases are rare and SHALL be unmistakable.

Silence is non-compliance.

Lane dividers have fuzz, but classification requires explicit rationale and smell checks.

This doctrine exists to detect drift in both the agent and the human operator.

## Major definition (PRD required)

Major releases:

- Introduce intentional breaking change(s).
- Redefine contracts explicitly.
- Declare transition and migration posture.

Major releases MUST have a PRD as the primary intent carrier.

Major releases MUST have ADR(s) and OBPI(s) that implement the PRD intent.

Major is not an escalation for convenience.

## Governance artifact requirements

This lane SHALL comply with the SemVer × Governance Artifact Matrix:

- Primary intent carrier: PRD (mandatory).
- Supporting artifacts: ADR(s) (mandatory) and OBPIs (mandatory).
- GitHub Issues: rare and edge-only.

## Transition and migration posture (mandatory)

Every major release SHALL declare a transition posture.

The posture SHALL include:

- Compatibility strategy.
- Migration obligations.
- Explicit statement of what breaks and why.

Silence is non-compliance: absence of transition posture is non-compliance.

## Major classification rationale (required)

Every major release SHALL include an explicit rationale statement that answers:

- What contract is being broken or redefined?
- Why is a breaking change necessary?
- What is the migration posture and compatibility strategy?
- Which PRD carries the intent, and which ADR(s) and OBPI(s) implement it?

Silence is non-compliance: missing rationale is a release blocker.

## GovZero Gate Obligations

This section is mandatory.

### Gate 1 — Intent

Obligation:

- A PRD SHALL exist and SHALL be the primary intent carrier.
- OBPIs SHALL exist and SHALL itemize expectations.

Satisfying artifacts:

- PRD narrative.
- OBPI checklist(s) linked to PRD intent.

Non-compliance:

- Major intent is carried primarily in ADRs or issues without a PRD.

### Gate 2 — Design

Obligation:

- ADR(s) SHALL exist and SHALL implement the PRD intent.
- ADR(s) SHALL define constraints and the compatibility strategy.

Satisfying artifacts:

- ADR content and linkage to PRD and OBPIs.

Non-compliance:

- Design decisions are implicit.
- Compatibility strategy is unclear or unrecorded.

### Gate 3 — Implementation

Obligation:

- Implementation SHALL enact the declared breaking change(s).
- Implementation SHALL include the declared transition posture.
- Documentation claims SHALL align to the new contracts.

Satisfying artifacts:

- Code and documentation aligned with PRD and ADR(s).

Non-compliance:

- The breaking change is accidental.
- Backward compatibility is claimed but not honest.

### Gate 4 — Verification

Obligation:

- Verification SHALL defend the breaking change and the migration posture.

Satisfying artifacts:

- Verification evidence that demonstrates the new contract and the transition posture.

Non-compliance:

- Major claims are asserted without defensible verification.

### Gate 5 — Human Attestation

Obligation:

- Gate 5 SHALL be required for all major releases.
- Attestation is elevated: the operator witness SHALL cover the contract break and migration posture.

Satisfying artifacts:

- Recorded human attestation that the major release claim holds on the operator-visible surfaces.

Silence is non-compliance: missing attestation is non-compliance.

## Smell checks

### Major smells (breaking change avoidance)

If any smell is present, the major classification SHALL be enforced, not avoided:

- Contracts are being redefined.
- Backward compatibility is no longer honest.
- Migrations become conceptual, not additive.

### Minor smells (re-evaluate as minor)

If the change is additive and backward compatible, major classification SHALL be re-evaluated:

- The capability is new but does not break contracts.
- Deprecations are declared without enforcement.

## Authorized agent challenges

The AI Pair is authorized to challenge classification.

If any smell check in this document is present, the AI Pair MUST raise a classification challenge before proceeding.

- “This discovery affects invariants — should this trigger a new minor or major reclassification?”
- “Contracts are being redefined — is backward compatibility still honest?”
- “This patch request seems to redefine behavior — is this actually a minor/major?”

Silence is non-compliance: unanswered challenges SHALL be treated as a blocker.
