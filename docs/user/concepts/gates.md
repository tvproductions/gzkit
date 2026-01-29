# Gates

Gates are verification checkpoints. Work cannot proceed until gates pass.

---

## The Five Gates

| Gate | Name | Purpose | Applies To |
|------|------|---------|------------|
| 1 | **ADR** | Record intent before implementation | All lanes |
| 2 | **TDD** | Verify correctness through tests | All lanes |
| 3 | **Docs** | Ensure documentation matches code | Heavy lane |
| 4 | **BDD** | Verify external contract behavior | Heavy lane |
| 5 | **Human** | Explicit human attestation | Heavy lane |

---

## Gate 1: ADR (Intent)

**What**: An Architecture Decision Record exists.

**Why**: Intent must be recorded before implementation. This prevents scope creep and provides context for future readers.

**Artifact**: ADR document with problem statement, decision, and consequences.

---

## Gate 2: TDD (Tests)

**What**: Tests exist and pass.

**Why**: Automated verification that code does what it claims.

**Artifact**: Passing test suite with reasonable coverage.

---

## Gate 3: Docs (Documentation)

**What**: Documentation accurately describes behavior.

**Why**: Docs are proof of completion. If you can't document it, you don't understand it.

**Artifact**: Documentation that builds, links resolve, content matches code.

**Applies to**: Heavy lane only (external contract changes).

---

## Gate 4: BDD (Behavior)

**What**: Acceptance tests verify external contracts.

**Why**: API/CLI/schema changes need black-box verification.

**Artifact**: Passing acceptance scenarios.

**Applies to**: Heavy lane only.

---

## Gate 5: Human (Attestation)

**What**: A human explicitly signs off on the work.

**Why**: This is the whole point. Humans must verify, not rubber-stamp.

**Artifact**: Attestation record with status, attester, and timestamp.

**Cannot be automated**. That's intentional.

---

## Gate Flow

**Lite lane** (internal changes):

```
ADR → TDD
 1     2
```

**Heavy lane** (external contracts):

```
ADR → TDD → Docs → BDD → Human
 1     2     3      4      5
```

---

## Checking Gates

```bash
# See current gate status
gz status

# Run Gate 2 (tests)
gz implement

# Run all required gates
gz gates

# Validate artifacts
gz validate
```

---

## Related

- [Lanes](lanes.md) — Which gates apply when
- [gz status](../commands/status.md) — Check gate progress
- [gz attest](../commands/attest.md) — Pass Gate 5
