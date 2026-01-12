# Specification

Specification defines **what invariants must hold**. It is the agent-native layer of the covenant.

## Purpose

Agents need constraints to reason against. Without explicit specification:

- Agents infer conventions (often incorrectly)
- Intent drifts across sessions
- "Should" becomes "could" becomes "did"

Specification prevents this by making constraints explicit and testable.

## Artifacts

### Canon

Immutable reference documents that define project invariants.

```markdown
# Canon: Determinism

All scoring functions MUST be deterministic.
Same inputs → same outputs, always.

This is non-negotiable. No randomness, no time-dependence,
no external state that varies between runs.
```

Canon is:
- **Immutable** once accepted (changes require new canon)
- **Authoritative** (overrides other guidance)
- **Testable** (invariants can be verified)

### Acceptance Criteria

Testable claims that define completion.

```markdown
## Acceptance Criteria

- [ ] API returns 200 for valid input
- [ ] API returns 400 for missing required fields
- [ ] Response time < 100ms at p95
- [ ] Error messages include field name
```

Acceptance criteria are:
- **Binary** (pass or fail, no partial credit)
- **Observable** (can be verified by running something)
- **Specific** (no ambiguity about what "done" means)

### Constraints

Explicit boundaries for implementation.

| Pattern | Example |
|---------|---------|
| NEVER | "NEVER use pytest" |
| ALWAYS | "ALWAYS annotate public functions" |
| MUST | "MUST preserve backward compatibility" |
| MUST NOT | "MUST NOT store secrets in code" |

Constraints are:
- **Constraint-forward** (prohibitions over suggestions)
- **Enforceable** (can be checked automatically)
- **Explicit** (written down, not assumed)

## For Agents

When working in a gzkit project:

1. **Read canon first** — It defines what you cannot violate
2. **Check acceptance criteria** — They define what "done" means
3. **Respect constraints** — NEVER/MUST boundaries are hard
4. **Flag violations early** — If you can't comply, say so

## Constraint Patterns That Work

| Pattern | Why it works |
|---------|--------------|
| Explicit prohibitions | "NEVER use X" is unambiguous |
| Declarative intent | "Ensure Y" lets you reason about goals |
| Testable claims | "Response < 100ms" can be verified |
| Immutable reference | Canon doesn't change mid-session |

## Constraint Patterns That Fail

| Pattern | Why it fails |
|---------|--------------|
| Implicit conventions | "We usually do X" invites drift |
| Vague suggestions | "Consider Y" has no enforcement |
| Unstated assumptions | "Obviously Z" isn't obvious to agents |
| Mutable guidance | Changing rules mid-work causes confusion |

## Relationship to Gates

Specification feeds into gates:

- **Gate 1 (ADR)**: Captures intent specification
- **Gate 2 (TDD)**: Tests verify specification claims
- **Gate 3 (Docs)**: Documentation describes specified behavior
- **Gate 4 (BDD)**: Acceptance tests verify acceptance criteria

Gate 5 (Human) doesn't consume specification directly—it observes the evidence that specification produced.
