# Ledger vocabulary inertness

Observed 2026-09-12T17:17:02.293141+00:00 at HEAD `464dd4ff8fa2ee12d98afe99a867280e1b82b431`, with prior session changes present.

Instrument: `check_ledger_inertness.py --report` (called through its report function to capture unchanged output).

```text
declared event types: 76
fired at least once:  66
never fired:          10
    blocked_by
    blocks
    constitution_created
    discovered_from
    intrinsic-complexity-attestation
    ledger_event_corrected
    obpi_superseded
    section_ownership_unowned
    task_escalated
    validates

paired-event ratios (reported, not judged):
    obpi_lock_claimed 394 / obpi_lock_released 374  (94.9%)
    obpi_parked 377 / obpi_unparked 6  (1.6%)
    airlock_in 63 / airlock_out 21  (33.3%)
    mx_session_opened 1 / mx_session_closed 1  (100.0%)

  A ratio is evidence for an operator ruling, never a verdict. What a
  lopsided pair MEANS depends on which surface emits it — read the
  producer before drawing a conclusion.
EXIT=0
```

Enforcement also returned zero: 10 never-fired types against 11 disclosed baseline entries; `unowned_ratchet_updated` has fired since baseline. No baseline was rewritten. A disclosed absence is not proof that a producer works.

## Paired-event interpretation

Airlock producers book encounters keyed by target, without a unique transit identifier (`airlock/enter.py::_book_transit`, `airlock/exit.py::_book_exit`). Multiple entries and standalone diagnostics can share a target. The 63/21 ratio cannot establish 42 abandoned transits. A disclosed ad-hoc grouping of the same raw ledger found 45 proceed and 18 hold entries, and 21 clean exits; these counts do not prove actual mutation was confined. Production wrappers remain diagnostic and some inject empty reach. Carry this as an intent-trace signal under ADR-0.33.0.

MX has one matching session-id pair, `d3c16ae0-719a-4276-9fca-9c9739ee3be2`: opened 2026-08-21, closed 2026-08-22 (ledger lines 15262 and 15275 at this snapshot). The producer binds these records by session_id; the prior proof's zero-use statement is no longer current. This shows one historical use, not general efficacy.

## Never-fired dispositions

Static producer reading, not fresh isolated-execution credit. No event was
manufactured to drain a count. The disclosed baseline remains unchanged.

| Type | Producer and legitimate trigger | Disposition |
|---|---|---|
| blocked_by | `ontology/work.py:235` shared `emit_work_edge`, vocabulary-attestation gated | Investigate integration under ADR-0.32.0; append-capable library path exists, production caller not located by this inspection |
| blocks | Same shared work-edge emitter | Same; zero live use is not a reason to emit synthetic lineage |
| discovered_from | Same emitter, provenance edge model | Same |
| validates | Same emitter, verification edge model | Same |
| constitution_created | `commands/init_cmd.py:1246` creates a constitution then appends | Retain; no new constitution is warranted by a zero count |
| intrinsic-complexity-attestation | `commands/complexity_advise.py:303` checks threshold crossing, then TTY and confirmation before append | Investigate invocation restriction; a real producer exists, but zero use cannot distinguish non-use from refusal |
| ledger_event_corrected | `commands/ledger_correct.py:109` validates a target event triple and correction, then appends after the dry-run branch | Retain; baseline identifies correction targets held for operator review, not authorization to apply them |
| section_ownership_unowned | `commands/content/unown.py:2834` validates ownership; transaction at 2905 reaches witness append at 535/1765 | Retain; attested un-owning is a legitimate trigger that need not occur merely for audit coverage |
| task_escalated | `commands/task.py:414` moves an in-progress TASK to escalated and persists through `_emit_task_event` | Retain producer; investigate whether actual boundary crossings use an appropriate record, without initiating a TASK |
| obpi_superseded | `commands/obpi_cmd.py:243` resolves source and successor, checks transition, requires rationale and attestor, then appends after the dry-run branch | Retain; wired but unused in this ledger, with no observed failed supersession request |

The intrinsic-complexity branch explicitly reports
`requires an interactive TTY; headless invocation refused` at
`commands/complexity_advise.py:314`. Root operator canon prohibits a transport
requirement from blocking human attestation. This is an observed code/doctrine
mismatch to route; no attestation was attempted or recorded in this run.

The seven existing tests in `tests.commands.test_complexity_advise_attest_intrinsic`
passed, including the test deliberately asserting refusal without a TTY. These
are isolated fixture tests; they preserve the implemented restriction and do
not settle its agreement with newer operator canon.

Lock claims may replace a same-agent or expired lock without emitting a release
(`commands/obpi_lock.py:63–110`); releases also originate from completion and
reaping. Thus 394/374 is not a count of outstanding locks. Park/unpark changes
the child's association with an ADR demotion/promotion destination; parking is
explicitly reversible and does not negate completion
(`foundation/sunset_migrate.py:103–104`, `commands/adr_promote.py:305–318`).
Thus 377/6 is not abandonment. Retain these ratios as attribution questions;
no lock, TASK or OBPI lifecycle state was modified by this audit.
