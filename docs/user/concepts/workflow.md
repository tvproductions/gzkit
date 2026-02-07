# Daily Workflow

How gzkit fits into your daily development habits.

---

## The Alignment Chain

Everything in gzkit serves one principle:

```
Intent (ADR/OBPI) ↔ Code (behavior) ↔ Docs (claims)
```

All three links must hold. If any breaks, the work isn't done.

---

## Starting a Feature

### 1. Record intent

Before writing code, capture what you're trying to do:

```bash
# Create a brief for the work
gz specify add-auth --parent PRD-1.0.0 --title "Add authentication"

# Create an ADR with your technical decision
gz plan auth-impl --brief BRIEF-add-auth --title "JWT authentication"
```

### 2. Break into OBPIs

If your ADR has multiple checklist items, create OBPIs:

```bash
gz obpi ADR-0.1.0 --item 1 --title "Set up JWT middleware"
gz obpi ADR-0.1.0 --item 2 --title "Create login endpoint"
gz obpi ADR-0.1.0 --item 3 --title "Add token refresh"
```

### 3. Work through items

Tell Claude which OBPI you're working on:

```
Implement OBPI-0.1.0-01 (JWT middleware) following ADR-0.1.0
```

Claude has the brief, the ADR, and the constraints. It knows the scope.

---

## During Development

### Check status frequently

```bash
gz status
```

Shows which gates are passing, which are pending.

### Run quality checks

```bash
gz check
```

Runs lint, format, typecheck, and tests. Gate 2 requires tests to pass.

### Sync control surfaces

If you've updated governance docs:

```bash
gz sync
```

Regenerates CLAUDE.md and other control surfaces from canon.

---

## Completing Work

### When all OBPIs are done

1. **Trigger closeout ceremony**

   Tell your agent: "Begin closeout for ADR-0.1.0"

2. **Observe directly**

   The agent presents commands. You run them. You see the results.

3. **Attest**

   ```bash
   gz attest ADR-0.1.0 --status completed
   ```

4. **Post-closeout audit**

   The agent reconciles records after your attestation.

---

## Heavy Lane Extras

If you're in heavy lane (external contract changes):

### Documentation is mandatory

Gate 3 requires docs to be updated. This means:

- Docstrings match actual behavior
- CLI help text is current
- User guides reflect changes
- Command manpages reflect current flags and workflows
- Operator runbook steps are current and executable
- Links and anchors are valid

Run to verify:

```bash
uvx mkdocs build --strict
```

### Acceptance tests required

Gate 4 requires BDD scenarios to pass:

```bash
uv run -m behave features/
```

---

## The Two Disciplines

Gates constrain the agent. But gzkit only works if you practice:

### 1. Read Everything

- Every line of generated code
- Every test, not just pass/fail
- Every explanation
- Every warning

Skimming is how you become a rubber stamp.

### 2. Insist on Q&A

At every decision point, stop and question:

- "Why this approach?"
- "What's the tradeoff?"
- "What could break?"

The agent won't ask unprompted. You must demand the conversation.

---

## Common Patterns

### Morning sync

```bash
gz status          # What's pending?
gz state --blocked # What's stuck?
```

### Weekly parity sync

Use `$airlineops-parity-scan` and write a dated report:

`docs/proposals/REPORT-airlineops-parity-YYYY-MM-DD.md`

### Before committing

```bash
gz check           # All quality gates
gz validate        # Governance artifacts valid
```

### Before shipping

```bash
# Closeout ceremony, then:
gz attest ADR-X.Y.Z --status completed
```

---

## Anti-Patterns

### ❌ Skipping the ADR

"It's a small change, I'll just code it."

Every change drifts without recorded intent. Even small changes get ADRs.

### ❌ Batching attestations

"I'll attest to all three ADRs at once."

Each ADR needs individual observation. Batching is rubber-stamping.

### ❌ Trusting agent summaries

"Claude says tests pass, so they pass."

Run the commands yourself. Observe the output. That's the ceremony.

### ❌ Skipping docs in heavy lane

"The code is done, docs can wait."

Documentation IS the Gate 5 artifact. No docs, no completion.

---

## Related

- [Lifecycle](lifecycle.md) — ADR states and pool system
- [Gates](gates.md) — What gets verified
- [Lanes](lanes.md) — Lite vs Heavy
- [OBPIs](obpis.md) — Atomic work units
- [Closeout](closeout.md) — Completing ADRs
