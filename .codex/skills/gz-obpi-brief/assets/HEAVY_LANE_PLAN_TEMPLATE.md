# Heavy Lane Plan Template (MANDATORY)

**THIS TEMPLATE IS BINDING FOR ALL HEAVY LANE OBPI IMPLEMENTATIONS.**

An agent implementing a Heavy lane OBPI MUST use this structure. Deviation is a governance violation.

---

## Plan Structure

### Phase 1: Implementation (Gates 1-4)

```
1. [ ] Gate 1 prep: Read parent ADR, record intent in brief
2. [ ] Code changes: [list specific files]
3. [ ] Gate 2: Create/update unit tests
4. [ ] Gate 3: Create/update documentation
5. [ ] Gate 4: Create/update BDD scenarios
6. [ ] Validation: Run lint, format, tests, BDD
```

### Phase 2: Gate 5 (Human Attestation) — MANDATORY

```
7. [ ] Present attestation commands to human
8. [ ] STOP — Wait for human to execute CLI commands
9. [ ] STOP — Wait for human attestation response
10. [ ] Record attestation in brief
11. [ ] THEN mark OBPI closed
```

---

## Gate 5 Attestation Block (copy into plan)

```markdown
## Gate 5: Human Attestation

**Product surface commands for verification:**

\`\`\`bash
# [Command 1 - primary product surface]
uv run -m airlineops [command]

# [Command 2 - secondary verification]
uv run -m airlineops [command]
\`\`\`

**Awaiting attestation.** Human must execute above commands and respond with:
- "Completed" — All claims verified
- "Completed — Partial: [reason]" — Subset accepted
- "Dropped — [reason]" — Rejected

**DO NOT PROCEED UNTIL ATTESTATION RECEIVED.**
```

---

## Prohibitions

- **NEVER** mark a Heavy lane OBPI as closed before human attestation
- **NEVER** assume implementation completion = brief completion
- **NEVER** offer raw SQL as attestation evidence (CLI only)
- **NEVER** skip the "STOP — Wait" steps

---

## Attestation Response Recording

After human attests, record in brief:

```markdown
## Gate 5 Attestation

**Date:** YYYY-MM-DD
**Attestor:** [human]
**Response:** [Completed | Completed — Partial | Dropped]
**Evidence:** [CLI command executed and observed output summary]

**OBPI Status:** Closed
```

---

## Why This Exists

Gate 5 is human attestation of product surface behavior. The agent cannot attest on behalf of the human. The agent's role is to:

1. Complete implementation (Gates 1-4)
2. Present verification commands
3. **Wait**
4. Record the attestation

Steps 3 and 4 are not optional. They are not implicit. They require explicit human action.
