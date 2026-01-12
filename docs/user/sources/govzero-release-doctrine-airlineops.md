# GovZero SemVer Release Doctrine

Status: DRAFT
Last reviewed: 2026-01-10

## Purpose

This doctrine extends GovZero and defines how SemVer release numbers function as governance assertions.

A release classification is an explicit claim about intent, design, implementation, verification, and attestation.

- A release is a governance assertion, not a batch of commits.
- Silence is non-compliance.
- Lane dividers have fuzz, but classification requires explicit rationale and smell checks.
- This doctrine exists to detect drift in both the agent and the human operator.

This doctrine is governance. It is not automation, tooling, CI/CD, or tagging instructions.

## Definitions

### SemVer as governance assertions

A SemVer number $X.Y.Z$ is a structured assertion:

- $X$ (Major): intentional contract breaks; transition posture is explicit.
- $Y$ (Minor): new capability; backward compatibility remains honest.
- $Z$ (Patch): defect correction and hardening of already-intended behavior; no new capability.

### Lane exclusivity

Release lanes are mutually exclusive by definition.

If an increment cannot be justified under its lane obligations and smell checks, it SHALL be reclassified.

## SemVer × Governance Artifact Matrix

This matrix is mandatory. Each release-class document below is subordinate to this matrix.

| SemVer lane | Primary intent carrier | Supporting artifacts | GitHub Issues posture |
| --- | --- | --- | --- |
| Major ($X.0.0$) | PRD (mandatory; primary) | ADRs (mandatory), OBPIs (mandatory) | Rare and edge-only |
| Minor ($X.Y.0$) | ADR (mandatory; primary) | OBPIs (mandatory) | Prohibited as minor intent |
| Patch ($X.Y.Z$) | GitHub Issue (mandatory; primary) | None by default | Mandatory as patch intent |

Doctrine notes:

- Patch is NOT “sub-minor.”
- Minor is how the product advances; patch is how intended behavior becomes reliably available.

## GovZero Gate Obligations

Every SemVer release SHALL map its governance assertion to GovZero’s gates.

### Gate 1 — Intent

What it means:

- The release has an explicit, reviewable intent record.

Evidence requirements by lane:

- Patch: GitHub Issue is the intent record.
- Minor: OBPI(s) are the intent record.
- Major: PRD is the intent record.

### Gate 2 — Design

What it means:

- Design intent and constraints are explicit.
- The lane classification is justified against the doctrine.

Evidence requirements by lane:

- Patch: ADR is not expected unless the patch reveals a design break.
- Minor: ADR is required.
- Major: ADR(s) are required and SHALL implement the PRD.

### Gate 3 — Implementation

What it means:

- Code changes and documentation claims are aligned.
- The release does not violate lane prohibitions.

Evidence requirements by lane:

- Patch: implementation SHALL not introduce new capability.
- Minor: implementation SHALL preserve backward compatibility.
- Major: implementation SHALL include the declared contract breaks and transition posture.

### Gate 4 — Verification

What it means:

- Verification is sufficient to defend the governance assertion.

Evidence requirements by lane:

- Patch: verification SHALL demonstrate the defect is corrected and the intended behavior is available.
- Minor: verification SHALL demonstrate the new capability and its backward compatibility posture.
- Major: verification SHALL demonstrate the breaking change(s) and the migration posture.

### Gate 5 — Human Attestation

What it means:

- A human witnesses the relevant surfaces and attests the assertion is true.

Evidence requirements by lane:

- Patch: required when a patch changes observable behavior or operator workflow in a way that must be witnessed.
- Minor: required, always.
- Major: required, always, and elevated.

Silence is non-compliance: if Gate 5 is required, it SHALL be performed and recorded.

## Fuzzy Boundaries and Classification Smells

Classification is not always clean in agentic development.

Lane dividers have fuzz, but classification requires explicit rationale and smell checks.

The purpose of smell checks is reclassification, not blame.

### Patch smells (might actually be minor)

A patch classification SHALL be re-evaluated if any of the following are true:

- The change introduces new capability.
- The change adds new concepts or entities that were not already intended.
- The change requires new user-facing explanation beyond defect correction.

### Minor smells (scope is expanding)

A minor classification SHALL be re-evaluated if any of the following are true:

- The number of OBPIs is exploding inside a single minor increment.
- OBPIs no longer trace to the original ADR intent.
- Repeated “why wasn’t this hardened?” discoveries appear.
- Invariants are changing rather than being clarified.

Drift principle:

- Large OBPI accumulation within a single minor is a drift indicator; stop and reclassify.

### Major smells (breaking change avoidance)

A major classification SHALL be re-evaluated if any of the following are true:

- Contracts are being redefined.
- Backward compatibility is no longer honest.
- Migrations become conceptual, not additive.

## Authorized Agent Challenges (Non-Vibed Compliance Questions)

The AI Pair is authorized and expected to challenge lane selection.

These challenges are compliance prompts, not opinions.

- “This GH Issue appears to introduce new capability — should this be an OBPI?”
- “The number of OBPIs in this minor suggests scope expansion — should we cut a new minor?”
- “This discovery affects invariants — should this trigger a new minor or major reclassification?”
- “This patch request seems to redefine behavior — is this actually a minor/major?”

Silence is non-compliance: unanswered classification challenges SHALL be treated as a blocker.

## Mandatory agent challenge triggers

- If any smell check condition is present for a lane, the AI Pair MUST raise the relevant classification challenge.
- Failure to raise the challenge when smells are present is non-compliance.
- Unanswered challenges SHALL block release advancement.

## Anti-example narrative: ADR-0.1.9

ADR-0.1.9 accumulated a long-running set of work while remaining under a single $0.1.9$ identity.

Observed drift pattern:

- The effort dragged on as “0.1.9” while accumulating roughly 100 OBPIs.
- Many patch-level discoveries surfaced during minor implementation.
- Additional minor advances emerged during discovery.

Under this doctrine:

- The work SHOULD have segmented into multiple minor increments and patch increments.
- Patch-level discoveries SHOULD not have been carried inside a single minor indefinitely.

This doctrine exists specifically to prevent that drift pattern and to allow the agent to detect it.

## Roadmap note: end of 0.1.x posture

The $0.1.x$ series is nearing the end of its roadmap purpose.

This doctrine is foundational for a cleaner $0.2.x$ posture with explicit lane discipline and drift detection.

## Coercion and audit (design only)

This section defines governance enforcement intent.

It does not define tooling mechanics.

### Proposed contributor instructions (intent only)

These instructions SHALL be treated as gating conditions for advancing a release number.

Patch ($X.Y.Z$):

- A GitHub Issue exists and is the primary intent record.
- The change improves availability, correctness, or robustness of already-intended behavior.
- No new capability is introduced.
- Gate obligations are satisfied for the patch lane, including Gate 5 when required.

Minor ($X.Y.0$):

- An ADR exists and is the primary intent record.
- OBPIs exist and itemize expectations.
- GitHub Issues are not used as minor intent.
- Verification defends new capability while preserving backward compatibility.
- Gate 5 human attestation is performed.

Major ($X.0.0$):

- A PRD exists and is the primary intent record.
- ADR(s) exist and implement the PRD intent.
- OBPIs exist and itemize expectations.
- Breaking change(s) and transition posture are explicit.
- Gate 5 human attestation is performed and elevated.

Silence is non-compliance: if any condition is unknown or undocumented, the release SHALL not advance.

### Proposed chores (names and intent only)

These chores are governance audits.

- audit-release-classification
  - Audits: each release increment has an explicit lane classification rationale.
  - Non-compliance: classification is implicit, contested without response, or violates smell checks.
  - Evidence expected: release rationale text referencing the matrix and smell checks.

- audit-gates-evidence
  - Audits: Gate 1 through Gate 5 obligations are explicitly satisfied per lane.
  - Non-compliance: missing gate mapping, missing required artifacts, or missing attestation where required.
  - Evidence expected: documented gate mapping and references to the required intent carriers.

- audit-obpi-count-smell
  - Audits: minor increments do not accumulate drift-level OBPI counts.
  - Non-compliance: large OBPI accumulation within a single minor without reclassification.
  - Evidence expected: a rationale explaining segmentation decisions and spillover handling.

- audit-issue-lane-misuse
  - Audits: GitHub Issues are not used as minor-level intent mechanisms.
  - Non-compliance: minor intent is captured primarily in issues rather than ADR(s) and OBPI(s).
  - Evidence expected: lane declaration and artifact linkage demonstrating ADR and OBPI primacy.

## Related documents

- Patch doctrine: patch-release.md
- Minor doctrine: minor-release.md
- Major doctrine: major-release.md
