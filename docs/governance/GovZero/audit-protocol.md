# GovZero Audit Protocol

Status: Active
Last reviewed: 2026-01-18
Authority: Canon (defines ADR audit workflow and closeout ceremony)

This document defines the audit protocol for ADR closeout within GovZero governance.
Gate definitions are in [charter.md](charter.md) — this document references gates by number only.

---

## ADR Closeout Ceremony

The ADR closeout ceremony is a **hard mode transition** that transfers interpretive authority
from the agent to the human. It ensures human attestation is grounded in direct observation,
not mediated through agent claims.

### Trigger

The ceremony begins when the human invokes:

- "ADR closeout ceremony"
- Or recognized equivalent (e.g., "begin closeout", "closeout ADR-X.Y.Z")

### Attestation Forms

The human MUST provide one of the following explicit attestations:

| Attestation | Meaning |
|-------------|---------|
| **Completed** | ADR work is finished; all claims verified; ready to finalize |
| **Completed — Partial: [reason]** | Subset of work accepted; remainder deferred with documented rationale |
| **Dropped — [reason]** | ADR rejected; clear rationale provided; does not advance |

---

## Agent Behavior: MUST

1. Agent **MUST** recognize the closeout trigger phrase as a mode transition command.

2. Agent **MUST** immediately yield interpretive authority to the human upon entering closeout mode.

3. Agent **MUST** present raw artifact paths and commands for human execution, not summaries or interpretations.
   - A short **paths/commands-only** inventory is permitted if it is derived solely from the
     provided paths/commands and contains **no outcomes or conclusions**.

4. Agent **MUST** wait for explicit human attestation before recording closeout status.

5. Agent **MUST** record the human's attestation verbatim, including timestamp and any stated rationale.

6. Agent **MUST** run audit checks **only after** the human has provided attestation (post-closeout audit).

7. Agent **MUST** reference gate semantics by number only (e.g., "Gate 5") and defer to `docs/governance/GovZero/charter.md` for definitions.

8. Agent **MUST** treat logs and ledgers as reconciliation artifacts for agent use, not as proof of human attestation.

9. Agent **MUST** surface this document for human reference during closeout.

---

## Agent Behavior: MUST NOT

1. Agent **MUST NOT** summarize, interpret, or editorialize evidence outcomes during closeout mode.
   - Correct: "Run `uv run -m unittest -v` to see test results"
   - Forbidden: "All tests pass"

2. Agent **MUST NOT** infer attestation from silence, continuation, or implicit approval. Attestation must be explicit.

3. Agent **MUST NOT** auto-close an ADR based on passing checks. Human attestation is the closeout gate, not CI status.

4. Agent **MUST NOT** run audit checks during closeout mode. Audit is post-attestation only.

5. Agent **MUST NOT** present ledger entries or logs as proof of completion. These are agent-facing reconciliation, not human-facing evidence.

6. Agent **MUST NOT** redefine, restate, or reinterpret gate semantics. Reference by number only; definitions live in the charter.

7. Agent **MUST NOT** offer to "check if requirements are met" during closeout. The human checks; the agent presents paths.

8. Agent **MUST NOT** proceed to post-closeout tasks until attestation is recorded.

---

## Mode Transition: Before vs During vs After Closeout

| Phase | Agent Role | Human Role | Permitted Agent Actions |
|-------|------------|------------|------------------------|
| **Pre-Closeout** | Active executor | Reviewer/requester | Run tests, generate reports, interpret results, suggest next steps, update code |
| **During Closeout** | Passive presenter | Active observer/attestor | Present artifact paths, surface commands, record attestation verbatim, answer factual questions only |
| **Post-Closeout** | Audit executor | Passive (informed of results) | Run audit checks, update ledgers, file reconciliation receipts, report audit findings |

**Trigger:** Human invokes "ADR closeout ceremony" (or recognized equivalent)

**Exit condition:** Human provides explicit attestation (Completed / Completed — Partial / Dropped)

**Transition rules:**

- Pre → During: Triggered by human invoking closeout ceremony
- During → Post: Triggered by human providing attestation
- Agent cannot self-transition out of "During" phase

---

## Why This Prevents Mediated Observation

The core integrity risk in agent-assisted governance is **mediated observation**: the human sees
reality only through the agent's lens. If the agent says "tests pass" and the human accepts this,
the human has not observed the tests — they have observed the agent's claim about the tests.
This creates an epistemic gap where the agent's errors, biases, or hallucinations become invisible.

The closeout ceremony eliminates mediated observation by **inverting the information flow**:

- The agent presents **paths**, not **conclusions** ("see `artifacts/reports/coverage.html`" not "coverage is 87%")
- The agent presents **commands**, not **outcomes** ("run `uv run -m unittest -v`" not "all 42 tests pass")
- The human **executes and observes directly**, with the agent as a silent index

This ensures the human's attestation is grounded in direct observation of artifacts, not in trust
of agent claims. The agent cannot corrupt what it does not interpret.

Post-closeout audit is permitted because it serves a different function: reconciliation and drift
detection for future agent runs, not proof of the current closeout. Ledgers and logs are explicitly
labeled as agent-facing artifacts so no future agent (or human) mistakes them for attestation evidence.

---

## Closeout Ceremony: Agent Script

When the human invokes "ADR closeout ceremony", the agent MUST respond with:

```text
ADR CLOSEOUT CEREMONY — MODE TRANSITION

I am now in PASSIVE PRESENTER mode. I will not interpret evidence.

Summary (paths/commands only; no outcomes):
- ADR under review: [ADR path]
- Related briefs: [OBPI paths]
- Runbook/manpage paths (for walkthrough commands): [paths]
- Evidence commands listed below

Artifacts for your direct observation:
- Tests: Run `uv run -m unittest -v`
- Coverage: Run `uv run coverage report` or view `artifacts/reports/coverage.html`
- Docs build: Run `uv run mkdocs build -q`
- BDD (if Heavy): Run `uv run behave features/{feature}.feature`
- Runbook walkthrough (product commands from runbook/manpages): [commands]

Docs alignment check (human-confirmed):
- [ ] Manpage exists and reflects current CLI behavior
- [ ] Runbook includes relevant commands
- [ ] Dataset documentation updated if applicable
- [ ] CLI --help matches manpage SYNOPSIS

When you have observed the artifacts, provide your attestation:
- "Completed"
- "Completed — Partial: [reason]"
- "Dropped — [reason]"

I await your attestation.
```

The agent MUST NOT deviate from this script or add interpretive commentary.

---

## Post-Closeout Audit

After the human provides attestation, the agent MAY:

1. Record the attestation in the ADR metadata
2. Update ledgers/logs with reconciliation data
3. Run automated audit checks
4. Update ADR status to **Validated** after audit completion (see ADR lifecycle)
5. Report audit findings to the human

Ledger entries are for agent reconciliation only. They do not constitute proof of human attestation.

---

## References

- Gate definitions: [charter.md](charter.md)
- ADR/OBPI/GHI/audit linkage: [adr-obpi-ghi-audit-linkage.md](adr-obpi-ghi-audit-linkage.md)
- Disposition rubric (legacy): [../ADR_DISPOSITION_RUBRIC.md](../ADR_DISPOSITION_RUBRIC.md)
- Agent contract: [/AGENTS.md](/AGENTS.md)
