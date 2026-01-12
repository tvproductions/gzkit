# Governance

Governance defines **who has authority to decide**. It is the human-native layer of the covenant.

## Purpose

Without governance:

- Authority is implicit (who decides?)
- Completion is undefined (when is it done?)
- Audit trails don't exist (what happened?)
- Agents may overstep (they're helpful, but not authoritative)

Governance reserves judgment for humans while enabling productive partnership.

## Authority Boundary

| Role | Authority |
|------|-----------|
| **Human** | Originates intent; defines constraints; attests completion |
| **Agent** | Interprets intent; operates within constraints; generates evidence |
| **Verification** | Mutual—both parties trust gates and tests |

The key asymmetry: **agents present, humans decide**.

## Gate 5: Human Attestation

Gate 5 is the governance gate. It cannot be automated.

### Purpose

Human directly observes artifacts and attests that work is complete.

### What Attestation Means

| Term | Meaning |
|------|---------|
| **Completed** | Work finished; all claims verified |
| **Completed — Partial: [reason]** | Subset accepted; remainder deferred |
| **Dropped — [reason]** | Work rejected; rationale provided |

These terms are canonical. Other terms (approved, signed off, LGTM) are not valid.

### What Attestation Requires

1. **Observation** — Human must actually look at artifacts
2. **Verification** — Human confirms evidence satisfies intent
3. **Recording** — Attestation is written with timestamp
4. **Finality** — Once attested, work is closed (changes require new ADR)

### What Agents Cannot Do

- Attest on behalf of humans
- Skip Gate 5 for Heavy lane work
- Declare work "complete" without attestation
- Override human judgment

## Audit Trail

Governance produces an audit trail:

```
ADR-0.1.0 (Accepted 2024-01-15)
  └── Gate 1: ADR document
  └── Gate 2: 47 tests passing, 85% coverage
  └── Gate 3: Docs build clean
  └── Gate 4: 12 scenarios passing
  └── Gate 5: Completed (2024-01-22, JB)
```

The trail shows:
- What was intended (Gate 1)
- What evidence was generated (Gates 2-4)
- Who attested and when (Gate 5)

## Ceremonies

Governance includes ceremonies—structured moments for human judgment.

### ADR Review

Before accepting an ADR:
- Read the problem statement
- Evaluate alternatives considered
- Confirm decision makes sense
- Accept or request changes

### Attestation Ceremony

Before attesting completion:
- Review gate evidence
- Confirm acceptance criteria met
- Run key workflows manually
- Record attestation

### Audit Ceremony

Periodically:
- Review ADR status
- Check for stale work
- Identify drift patterns
- Update canon if needed

## For Humans

As the human in a gzkit project:

1. **Define constraints clearly** — Agents work better with explicit boundaries
2. **Review at gates** — Don't wait until Gate 5 to look
3. **Attest honestly** — "Completed — Partial" is valid; don't lie
4. **Maintain canon** — Update invariants when you learn

## For Agents

As an agent in a gzkit project:

1. **Present evidence, don't decide** — Show your work
2. **Flag potential issues** — If something seems wrong, say so
3. **Respect human judgment** — Even if you disagree
4. **Stop at Gate 5** — Your job ends at evidence generation

## Principles

1. **Governance is verification, not celebration** — Gates produce evidence, not applause
2. **Silence is non-compliance** — If you didn't attest, it's not done
3. **Human attestation is final** — No automation bypasses this
4. **Agents advise, humans decide** — Authority asymmetry is intentional
5. **Audit trails are permanent** — Once recorded, history is immutable
