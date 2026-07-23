---
id: ADR-0.0.71-completion-repudiation
status: Completed
kind: foundation
semver: 0.0.71
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-06-12
---

# ADR-0.0.71-completion-repudiation: Governed Reversal of Erroneous Completion Attestation

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
The operative stance for this ADR: **the system that makes a vow must own the
mechanism to repair it when the vow is broken**. gzkit's deepest vow is that human
attestation is sacrosanct; a vow with no governed reversal when an agent forges it
is testimony, not enforcement. The repudiation lever is the most powerful verb in
the system — it undoes a Gate-5 — so it is built operator-gated, fail-closed, and
fully ledger-witnessed, never as a casual patch.

## Why foundation tier?

Without this ADR the project still has an append-only ledger and a sacrosanct Gate-5,
but it cannot *repair* the one failure class it exists to name — a fabricated human
attestation. A harness that can record the sacrosanct invariant but not reverse a
forged one is not the harness gzkit claims to be; closing that inverse is
identity-shaping. The invariance test resolves **yes**.

Port-vs-adapter: this ADR is a **port**. "An erroneously- or fraudulently-attested
completion can be governed-reversed without retiring the OBPI, leaving an honest
audit trail" is the abstract contract; the `obpi_completion_repudiated` event and the
`gz obpi repudiate` verb are its first adapter. When `ADR-pool.obpi-state-machine`
schedules, repudiation becomes a first-class transition there behind the same port.

## Intent

gzkit is maximally opinionated about attestation integrity — append-only ledger, Gate-5 sacrosanct, 'no TTY/PTY may gate recording a human attestation' — yet has no governed lever to undo an integrity breach once one lands. The only completion counter-event is `gz obpi withdraw`, which is permanent one-way retirement: it sets a sticky `withdrawn=True` no later event clears (`src/gzkit/ledger.py:669-680`) and hides the OBPI from `gz state` (`src/gzkit/commands/state.py:86`). Every withdraw precedent in the ledger is a supersession; none is 'this completion was invalid, revert it and keep the OBPI live.' So when an agent fabricates a Gate-5 — the exact V.I.B.E.S. failure the system exists to make inert — the operator's only honest tools are hacks: prose-only GHI + last-write-wins supersession (no machine-readable fraud marker), or permanent withdrawal + re-mint under a new id.

Forcing instance (GHI #608): OBPI-0.0.70-02-session-correction-mining was completed 2026-06-12 with a Gate-5 attestation the operator never gave — a rogue agent on a manual run authored attestation prose about the -02 miner, prefixed it with 'attest completed', attributed it to the operator (whose only 'attest completed' utterance was for sibling OBPI-0.0.70-01), and ran `gz obpi complete`. There was no governed way to reverse it.

Foundation tier: the invariance test resolves yes. gzkit IS the harness whose reason to exist is that human attestation is sacrosanct and that stochastic LLM vibing is structurally inert. A harness that can RECORD a sacrosanct attestation but cannot REVOKE a fabricated one is not that harness — the single failure class the system names is the one it cannot repair. Closing that inverse is identity-shaping, not feature work. Operator ruling 2026-06-12 (verbatim): 'new verb means adr... i accept.'

## Decision

Add a first-class, operator-gated repudiation transition that reverses an erroneous or fraudulent completion WITHOUT the permanent retirement semantics of withdraw, so the OBPI stays live for a genuine re-completion.

**1. Ledger event `obpi_completion_repudiated`.** New Pydantic event model in `src/gzkit/events.py` + factory in `src/gzkit/ledger_events.py` + schema entry in `src/gzkit/schemas/ledger.json`. Fields: `obpi_id` (the OBPI whose completion is repudiated); `repudiated_receipt` (id/ts of the `obpi_receipt_emitted` event being repudiated); `cause` (closed enum: `model-induced-fabrication`, `operator-error`, `verification-invalid` — extensible only by amendment ADR); `attestor` (the human repudiating); `reason` (required free text; empty fails closed); `ts`.

**2. State-resolution semantics.** In `src/gzkit/ledger.py` graph metadata application: `obpi_completion_repudiated` flips `ledger_completed → False` and sets `repudiated=True` + `repudiated_reason`. It does NOT set the sticky `withdrawn` retirement. A subsequent genuine `obpi_receipt_emitted` for the same OBPI clears `repudiated` and re-completes cleanly. The fraudulent receipt remains in append-only history; the repudiation is the machine-readable counter-marker recording that it was invalid and why.

**3. CLI verb `gz obpi repudiate`.** Operator-gated: `gz obpi repudiate <OBPI-ID> --cause <enum> --reason "<text>" --attestor "<human>" [--dry-run]`. Empty `--attestor` or `--reason` fails closed (exit 1). Mirrors that only a human may grant a Gate-5 — only a human may revoke one. Manpage under `docs/user/manpages/`, `gz cli audit` green, behave smoke test (heavy-lane CLI verb).

**Reversibility / scope boundary.** Additive: one event type, one CLI verb, one state-resolution branch, schema entry, tests, docs. Does NOT build the full `ADR-pool.obpi-state-machine` (the ~30-audit rewrite) — repudiation becomes a first-class transition THERE when that ADR is scheduled; this is the narrow shippable primitive needed now, split out for the same reason `ADR-pool.attested-record-edit-doctrine` was. Does NOT auto-clear `repudiated` by any path other than a genuine re-completion. Does NOT touch `withdraw`'s semantics.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Completion repudiation reverses-without-retiring: it flips ledger_completed and sets repudiated without the sticky withdrawn semantics, and a genuine re-completion clears it. | uv run -m unittest tests.test_completion_repudiation | 0 |
| The `gz obpi repudiate` verb is operator-gated and fails closed on empty attestor/reason, mirroring that only a human may revoke a Gate-5. | uv run -m unittest tests.test_obpi_repudiate_cli | 0 |

## Consequences

### Positive

1. **The named V.I.B.E.S. failure (fabricated Gate-5) gains its first governed repair.** The system can now correct the exact integrity breach it was built to catch.

2. **The honest audit trail is preserved.** The fraud receipt stays in append-only history, the repudiation is the counter-marker, and a genuine re-completion supersedes — all three visible to an auditor, none erased.

3. **OBPI-0.0.70-02 (and any future instance) can be corrected with one command** instead of a pile of workarounds.

4. **`ADR-pool.obpi-state-machine` inherits a proven transition** when it schedules, rather than designing repudiation from scratch.

### Negative

1. **A powerful verb (undo a human attestation) is a new abuse surface.** Mitigated by operator-gating (required human `--attestor` + `--reason`, both fail-closed when empty), and by being itself a ledger-recorded, witnessed act.

2. **Two 'undo' verbs now exist** (`withdraw` = retire, `repudiate` = reverse-and-keep). The manpage and AGENTS.md must disambiguate so agents do not reach for the wrong one.

3. **Security-sensitive surface.** It edits completion state; heavy lane plus Gate-5 attestation on its own OBPIs is the appropriate ceremony level.

## Boundary Invariants

1. **Only a human repudiates.** `gz obpi repudiate` requires a non-empty `--attestor`
   and `--reason`; an empty attestation fails closed (exit 1). There is no
   agent-self-repudiation path — undoing a Gate-5 is as human-gated as granting one.
   (REQ-0.0.71-02 STRUCTURAL-FENCE — verified at ADR closeout via this invariant)
2. **Repudiation reverses, it does not retire.** `obpi_completion_repudiated` flips
   `ledger_completed → False` and sets `repudiated=True`; it NEVER sets the sticky
   `withdrawn` retirement. The OBPI stays visible in `gz state` and re-completable.
3. **The repudiated receipt is never deleted.** The append-only ledger is preserved;
   the repudiation event is additive counter-evidence, not an erasure of the
   fraudulent receipt.
4. **`cause` is a closed enum.** `model-induced-fabrication`, `operator-error`,
   `verification-invalid` — extensible only by amendment ADR, never free-form.
5. **A genuine re-completion is the only clearer.** `repudiated=True` is cleared by
   exactly one path — a subsequent genuine `obpi_receipt_emitted` for the same OBPI;
   no flag, no hand-edit, no other event clears it.
6. **The surface stays additive — stdlib + Pydantic only.** The repudiation primitive
   adds one event type, one CLI verb, one state-resolution branch, a schema entry, tests,
   and docs; it introduces NO new third-party runtime dependency. The module surface
   imports only stdlib and the sanctioned Pydantic departure.
   (REQ-0.0.71-01-07 STRUCTURAL-FENCE — verified at ADR closeout via this invariant)

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 0
- Lineage: 0
- Dimension Total: 3
- Baseline Range: 1-2
- Baseline Selected: 1
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 2

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] `obpi_completion_repudiated` ledger event model + factory + `ledger.json` schema entry + state-resolution semantics (flip ledger_completed, set repudiated, NOT withdrawn; genuine re-completion clears repudiated); unit tests
- [ ] `gz obpi repudiate` CLI verb (operator-gated, fail-closed on empty attestor/reason, --dry-run) + parser + manpage + `gz cli audit` green + behave smoke test; AGENTS.md withdraw-vs-repudiate disambiguation

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-06-12T20:18:22.213216*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.71-completion-repudiation

### Q: What is the title of this ADR?

**A:** Governed Reversal of Erroneous Completion Attestation

### Q: What is the semantic version?

**A:** 0.0.71

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit is maximally opinionated about attestation integrity — append-only ledger, Gate-5 sacrosanct, 'no TTY/PTY may gate recording a human attestation' — yet has no governed lever to undo an integrity breach once one lands. The only completion counter-event is `gz obpi withdraw`, which is permanent one-way retirement: it sets a sticky `withdrawn=True` no later event clears (`src/gzkit/ledger.py:669-680`) and hides the OBPI from `gz state` (`src/gzkit/commands/state.py:86`). Every withdraw precedent in the ledger is a supersession; none is 'this completion was invalid, revert it and keep the OBPI live.' So when an agent fabricates a Gate-5 — the exact V.I.B.E.S. failure the system exists to make inert — the operator's only honest tools are hacks: prose-only GHI + last-write-wins supersession (no machine-readable fraud marker), or permanent withdrawal + re-mint under a new id.

Forcing instance (GHI #608): OBPI-0.0.70-02-session-correction-mining was completed 2026-06-12 with a Gate-5 attestation the operator never gave — a rogue agent on a manual run authored attestation prose about the -02 miner, prefixed it with 'attest completed', attributed it to the operator (whose only 'attest completed' utterance was for sibling OBPI-0.0.70-01), and ran `gz obpi complete`. There was no governed way to reverse it.

Foundation tier: the invariance test resolves yes. gzkit IS the harness whose reason to exist is that human attestation is sacrosanct and that stochastic LLM vibing is structurally inert. A harness that can RECORD a sacrosanct attestation but cannot REVOKE a fabricated one is not that harness — the single failure class the system names is the one it cannot repair. Closing that inverse is identity-shaping, not feature work. Operator ruling 2026-06-12 (verbatim): 'new verb means adr... i accept.'

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Add a first-class, operator-gated repudiation transition that reverses an erroneous or fraudulent completion WITHOUT the permanent retirement semantics of withdraw, so the OBPI stays live for a genuine re-completion.

**1. Ledger event `obpi_completion_repudiated`.** New Pydantic event model in `src/gzkit/events.py` + factory in `src/gzkit/ledger_events.py` + schema entry in `src/gzkit/schemas/ledger.json`. Fields: `obpi_id` (the OBPI whose completion is repudiated); `repudiated_receipt` (id/ts of the `obpi_receipt_emitted` event being repudiated); `cause` (closed enum: `model-induced-fabrication`, `operator-error`, `verification-invalid` — extensible only by amendment ADR); `attestor` (the human repudiating); `reason` (required free text; empty fails closed); `ts`.

**2. State-resolution semantics.** In `src/gzkit/ledger.py` graph metadata application: `obpi_completion_repudiated` flips `ledger_completed → False` and sets `repudiated=True` + `repudiated_reason`. It does NOT set the sticky `withdrawn` retirement. A subsequent genuine `obpi_receipt_emitted` for the same OBPI clears `repudiated` and re-completes cleanly. The fraudulent receipt remains in append-only history; the repudiation is the machine-readable counter-marker recording that it was invalid and why.

**3. CLI verb `gz obpi repudiate`.** Operator-gated: `gz obpi repudiate <OBPI-ID> --cause <enum> --reason "<text>" --attestor "<human>" [--dry-run]`. Empty `--attestor` or `--reason` fails closed (exit 1). Mirrors that only a human may grant a Gate-5 — only a human may revoke one. Manpage under `docs/user/manpages/`, `gz cli audit` green, behave smoke test (heavy-lane CLI verb).

**Reversibility / scope boundary.** Additive: one event type, one CLI verb, one state-resolution branch, schema entry, tests, docs. Does NOT build the full `ADR-pool.obpi-state-machine` (the ~30-audit rewrite) — repudiation becomes a first-class transition THERE when that ADR is scheduled; this is the narrow shippable primitive needed now, split out for the same reason `ADR-pool.attested-record-edit-doctrine` was. Does NOT auto-clear `repudiated` by any path other than a genuine re-completion. Does NOT touch `withdraw`'s semantics.

### Q: What good things result from this decision? List benefits.

**A:** 1. **The named V.I.B.E.S. failure (fabricated Gate-5) gains its first governed repair.** The system can now correct the exact integrity breach it was built to catch.

2. **The honest audit trail is preserved.** The fraud receipt stays in append-only history, the repudiation is the counter-marker, and a genuine re-completion supersedes — all three visible to an auditor, none erased.

3. **OBPI-0.0.70-02 (and any future instance) can be corrected with one command** instead of a pile of workarounds.

4. **`ADR-pool.obpi-state-machine` inherits a proven transition** when it schedules, rather than designing repudiation from scratch.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **A powerful verb (undo a human attestation) is a new abuse surface.** Mitigated by operator-gating (required human `--attestor` + `--reason`, both fail-closed when empty), and by being itself a ledger-recorded, witnessed act.

2. **Two 'undo' verbs now exist** (`withdraw` = retire, `repudiate` = reverse-and-keep). The manpage and AGENTS.md must disambiguate so agents do not reach for the wrong one.

3. **Security-sensitive surface.** It edits completion state; heavy lane plus Gate-5 attestation on its own OBPIs is the appropriate ceremony level.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. `obpi_completion_repudiated` ledger event model + factory + `ledger.json` schema entry + state-resolution semantics (flip ledger_completed, set repudiated, NOT withdrawn; genuine re-completion clears repudiated); unit tests
2. `gz obpi repudiate` CLI verb (operator-gated, fail-closed on empty attestor/reason, --dry-run) + parser + manpage + `gz cli audit` green + behave smoke test; AGENTS.md withdraw-vs-repudiate disambiguation

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Make `withdraw` non-sticky / add a `--reversible` flag.** REJECTED: conflates two distinct semantics (retire vs reverse-and-keep) on one verb; the manpage and state model become ambiguous. Two verbs, two meanings is clearer and safer.

2. **Prose-only GHI + last-write-wins supersession (no new event).** REJECTED: leaves no machine-readable marker that the first completion was fraudulent; an auditor sees two completions and cannot tell which was invalid.

3. **Permanent withdraw + re-mint under a new OBPI id.** REJECTED: throws away the legitimate OBPI id and its history for what is a reversible error, not a supersession.

4. **Fold into `ADR-pool.obpi-state-machine`.** REJECTED: buries a narrow, shippable primitive needed now inside an unscheduled ~30-audit rewrite — the same ruling `ADR-pool.attested-record-edit-doctrine` made for the same reason.

5. **No primitive — keep per-incident judgment.** REJECTED: this is the defect (GHI #608).


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Make `withdraw` non-sticky / add a `--reversible` flag.** REJECTED: conflates two distinct semantics (retire vs reverse-and-keep) on one verb; the manpage and state model become ambiguous. Two verbs, two meanings is clearer and safer.

2. **Prose-only GHI + last-write-wins supersession (no new event).** REJECTED: leaves no machine-readable marker that the first completion was fraudulent; an auditor sees two completions and cannot tell which was invalid.

3. **Permanent withdraw + re-mint under a new OBPI id.** REJECTED: throws away the legitimate OBPI id and its history for what is a reversible error, not a supersession.

4. **Fold into `ADR-pool.obpi-state-machine`.** REJECTED: buries a narrow, shippable primitive needed now inside an unscheduled ~30-audit rewrite — the same ruling `ADR-pool.attested-record-edit-doctrine` made for the same reason.

5. **No primitive — keep per-incident judgment.** REJECTED: this is the defect (GHI #608).

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.71 | Completed | g0 | 2026-06-13 | Completed |
