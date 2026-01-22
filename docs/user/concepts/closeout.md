# Closeout Ceremony

The closeout ceremony is how ADRs get completed. It's a **mode transition** where the agent yields interpretive authority to the human.

---

## Why a Ceremony?

Without a formal closeout:

- Agents summarize outcomes (you see reality through their lens)
- "Looks good" becomes the default
- You attest to work you didn't verify
- The human becomes a rubber stamp

The ceremony forces **direct observation**. The agent presents paths and commands. You execute them. You see the results yourself.

---

## Triggering Closeout

Say any of these to your agent:

- "ADR closeout ceremony"
- "Begin closeout for ADR-0.1.0"
- "Closeout ADR-0.1.0"

This triggers a mode transition. The agent's behavior changes.

---

## Agent Behavior During Closeout

### The Agent MUST:

1. Recognize the trigger as a mode transition
2. **Yield interpretive authority** immediately
3. Present **raw artifact paths and commands**, not summaries
4. Wait for **explicit** human attestation
5. Run audit checks only **after** attestation
6. Reference gates by number; defer to charter for definitions

### The Agent MUST NOT:

1. Summarize or interpret evidence outcomes
2. Infer attestation from silence
3. Auto-close based on passing checks
4. Present ledger entries as proof
5. Offer to "check if requirements are met"
6. Proceed until attestation is recorded

---

## The Ceremony Flow

### Phase 1: Evidence Presentation

The agent presents:

```
Closeout for ADR-0.1.0

Gate 1 (ADR): design/adr/ADR-0.1.0-feature/ADR-0.1.0-feature.md
Gate 2 (TDD): uv run -m pytest tests/
Gate 3 (Docs): uvx mkdocs build --strict
Gate 4 (BDD): uv run -m behave features/
Gate 5 (Human): Awaiting your attestation

Run these commands and observe the results directly.
```

No interpretation. No "tests pass." Just paths and commands.

### Phase 2: Human Observation

You run the commands. You read the output. You verify the artifacts exist and contain what they should.

This is the discipline: **you observe, not the agent**.

### Phase 3: Attestation

You provide exactly one of:

| Attestation | Meaning |
|-------------|---------|
| **"Completed"** | All work finished; all claims verified |
| **"Completed — Partial: [reason]"** | Subset accepted; remainder deferred |
| **"Dropped — [reason]"** | Work rejected |

Then run:

```bash
gz attest ADR-0.1.0 --status completed
```

### Phase 4: Post-Attestation Audit

Only after attestation does the agent run reconciliation:

- Verify ledger entries
- Check for drift
- Update status tables

Audit is for record-keeping, not for approval.

---

## The Closeout Form

Each ADR can have an optional `ADR-CLOSEOUT-FORM.md`:

```
design/adr/ADR-0.1.0-feature/
├── ADR-0.1.0-feature.md
├── ADR-CLOSEOUT-FORM.md    ← Optional workspace
└── briefs/
    └── ...
```

The form provides:

- Pre-attestation checklist
- Space for human notes
- Post-attestation audit section
- Phase markers (Phase 1 → Phase 2)

---

## Why This Matters

The ceremony exists because of **epistemic integrity**.

If the agent says "tests pass" and you believe it, you've delegated observation. You're trusting the agent's interpretation of reality.

The ceremony breaks that chain:

- Agent: "Here's the command"
- Human: *runs command, sees output*
- Human: "I observed it. Completed."

Your attestation is grounded in **what you saw**, not what you were told.

---

## Common Mistakes

### ❌ Skipping observation

```
Agent: "All gates pass. Ready to attest?"
Human: "Sure, completed."
```

This is rubber-stamping. You didn't observe anything.

### ✅ Actual observation

```
Agent: "Run: uv run -m pytest tests/"
Human: *runs it, sees 47 tests pass*
Human: "Completed"
```

You saw the tests pass. Your attestation means something.

---

## Related

- [Gates](gates.md) — What each gate verifies
- [OBPIs](obpis.md) — Atomic work units
- [gz attest](../commands/attest.md) — Recording attestation
