# ADR-0.35.0 bounded intent trace — 2026-09-12

Persona: spec-reviewer; read-only diagnosis. Sample assigned by the parent after the three preceding health-audit axes. Only ADR-0.35.0 was traced. Matching gz-intent-trace, gz-context and gz-adr-status skills were read before commands. The ADR Decision and Checklist were read before implementation inspection. No OBPI work was initiated and no repository writes were requested.

## Conclusion

Delivered portions of the three sampled claims have concrete runtime evidence. End-to-end corpus landing and the final post-append advisory contract remain unfinished under existing OBPIs 07 and 08; this is not evidence that an attested completed implementation failed. The live lineage gate discloses zero graded coverage today, an operator-ratified temporary state, not proof that owned-section derivation has been verified on the published repository. One minor source-documentation correction was observed in the shared advisory's retirement description; no new runtime malfunction was reproduced.

## Layer-2 lifecycle evidence

`uv run --no-sync --no-cache gz context ADR-0.35.0` exited 0 and produced `/tmp/gz-health-context-035.md` (9,617 lines). This bundle was generated for orientation; this trace read the source Decision/Checklist and relevant current brief contracts directly, rather than claiming every context-bundle line was reviewed.

`uv run --no-sync --no-cache gz adr status ADR-0.35.0` exited 0; exact output is appended below. Its 7/13 count is grounded independently in `Ledger.read_all()` receipts for this ADR's actual brief IDs, not merely the nominal version prefix (older, different artifact identities used the same version).

| OBPI item | Layer-2 attested_completed receipt date | Raw ledger line |
|---|---|---:|
| 01 | 2026-08-24 | 15432 |
| 02 | 2026-08-26 | 15504 |
| 03 | 2026-09-05 | 15854 |
| 04 | 2026-09-05 | 15807 |
| 05 | 2026-09-11 | 16170 |
| 06 | 2026-09-12 | 16347 |
| 09 | 2026-08-21 | 15246 |

All seven recorded attestor `g0`. Items 07,08,10,11,12,13 lack completion receipts. 08's authored annotation (lines 51–75) explicitly says its Active state is unauthorized residue and the legitimate work remains undrawn; only the operator may draw it. No resumption is recommended on the strength of its status.

## Claim 1 — owned materialization and unowned preservation

Verbatim ADR Decision 3 (line 102):

> Sections declare `corpus-owned` or `unowned`. The generator materializes owned sections from the corpus and carries unowned sections forward verbatim.

Verbatim Checklist item 5 (line 397):

> corpus->candidate generator (owned materialize / unowned carry-forward) + `<consumer>.lineage.json` emission + `ByteEvidence` accounting correction

Implemented surface: `src/gzkit/content/composer.py:489–535` selects byte-verbatim slices for unowned sections and joins unchanged effective corpus entry bytes for owned bodies. `generate_candidate` at 539–670 loads the current effective corpus and ownership declaration, refuses unknown addressing/duplicate live invariants, creates an exact UTF-8 partition, and returns a pure candidate-plus-lineage result. It writes no artifact. The entire composer module was inspected; the pure result is deliberately separate from publication (539–554).

Observed against the actual repository, not a test fixture: generator succeeded with 31,244 bytes; all 10 unowned sections were byte-equal to their corresponding prior committed rendition spans. Emitted entry bytes 24,704 + generated structural bytes 535 + carried-forward bytes 6,005 = total 31,244. Compressible population accounting was 354 before and 354 after; no subtraction-based inflation. The return included all 22 section lineage records.

Disposition: **Fulfilled for the delivered pure generator and measured preservation/accounting behavior. Unfinished for end-to-end publication.** The public `content land AGENTS.md --dry-run` probe exited 2 because `land` is not registered. Existing pending OBPI07 owns that orchestrator (ADR line 109; brief 07 REQs at 300–308), not a new enhancement or new ADR.

The public `gz validate --rendition-lineage` probe exited 0 but disclosed 12 sections /41,846 bytes UNGRADED and 0/22 sections /0 of 47,851 bytes graded. `root.lineage.json` is absent. OBPI06 Audit Contract lines 137–152 explicitly ratifies on 2026-09-11 that never-published lineage is disclosed instead of fail-closed; existing committed lineage remains fail-closed. Implementation follows that ruling at `rendition_lineage.py:439–448`, and computes reported scope at 524–531. This pass must not be presented as a successful live owned-section derivation comparison. No publication was attempted.

## Claim 2 — capture and corpus attestation

Verbatim ADR Decision 7 (line 111):

> `gz content remember` gains a POST-APPEND ADVISORY -- three-part recovery prose per `.claude/rules/guardrail-feedback-prose.md`, never a refusal, exit stays 0. Capture must never be blocked: losing the operator's words is strictly worse than a red tree.

Verbatim ADR Decision 2 (line 98):

> Retiring an invariant-tier entry is CORPUS-ATTESTED: `--attestor` + `--reason`, fail closed on empty.

Implemented surface: complete `remember.py` and `_drift.py` were read. `remember.py:127–154` writes capture, emits its L2 witness, then calls the advisory; `_drift.py:95–98` protects the post-append drift read from OSError/ValueError, while 116–121 still prescribes compose/commit. Complete `retire.py` was read: invariant liveness is measured before mutation, empty attestor refuses before append; later handling distinguishes floor growth from shrinkage. `commit.py:88–117` reuses standing attestation only when the corpus fingerprint is unchanged.

Observed live no-write refusal: the ADR's empty-attestor retirement fidelity command exited 1 and named the exact invariant and required attestor, saying “nothing written.” Supplemental isolated evidence: existing `tests.commands.test_content_remember` ran 18 tests successfully. These are fixture tests, not a production capture, and do not prove every live IO failure scenario. No production capture was attempted because it would append canon and ledger entries.

Disposition: **Fulfilled for the observed invariant-retirement refusal; partially delivered capture advisory; unfinished 07/08 completion.** Brief 08 lines 98–126 explicitly accounts for pre-landed advisory fixes and its remaining dependency on 07. Its required seam citation and runnable `land` recovery remain unfinished existing work. Do not treat the 18-test pass as completion or permission to resume 08.

Small attributable documentation correction: `_drift.py:80–85` says “A RETIREMENT only ever removes entries from that set” and that a floor-failure recovery “cannot occur.” The current full retirement implementation explicitly computes `floor_added` for tombstone revival and passes `floor_risk=bool(floor_added)` at its final call (`retire.py:451`). Thus the runtime already handles growth, but this comment describes the opposite. Correction belongs under ADR-0.35.0; `_drift.py` is explicitly owned by live/undrawn OBPI08 (brief lines 8–9,145–146). Surface that ownership to the operator before any repair; this audit makes none. This is not a new feature and does not justify a fresh ADR.

## Claim 3 — decrease-only ratchet

Verbatim ADR Decision 3 (line 102):

> The unowned byte total is recorded in a decrease-only ratchet. Un-owning a section (which raises the ratchet) requires an attested raise-path, corpus-attested, the same shape as the retire path -- an undefined reversal path is the one agents invent.

Implemented surface: ownership load function 624–852 cross-checks declared sections, current byte spans, persisted floor and ledger witness. `record_unowned_total:2139–2284` refuses a rise before any write on its fast path, rereads committed state inside its lock on the write path, and emits a chained floor event after persistence. The source documents the ordinary adapter's unjournaled interrupted-write residual at 2218–2227; this trace neither exercised that writer nor asserts crash recovery complete. The attested unown writer was not executed.

Observed live declaration:12 owned,10 unowned; recorded floor 6,005 and measured unowned bytes 6,005. The floor pointer resolves through `Ledger.read_all()` to `unowned-ratchet-updated-AGENTS.md-owned-stdlib-first-doctrine-dependency-posture-255e275ac942653f`, attestor g0, prior 7,663→new 6,005, predecessor link and section-map digest present. A request to record 6,006 using the already-loaded declaration hit the documented pre-lock refusal, producing the exact recovery prose below and no writes.

Disposition: **Fulfilled for witnessed current decrease and runtime increase refusal.** This does not establish exhaustive concurrency/crash correctness. ADR Consequences Negative 2 expressly states decrease-only permits never decreasing; no cadence/automatic reduction guarantee is inferred from the claim.

## Routing and limits

- No new runtime correction proven by these bounded probes.
- End-to-end landing/lineage publication: existing unfinished OBPI07 under this ADR.
- Final advisory completion and minor contradictory retirement comment: existing undrawn OBPI08 under this ADR; operator initiation/ownership rules continue to govern.
- No claim that zero live lineage coverage is full compliance; its disclosed ungraded state is retained explicitly.
- Source readings were bounded to the three claims. This is not an exhaustive review of all 13 OBPIs, adversarial proof of every input, or ADR closeout audit.
- Commands used `uv run --no-sync --no-cache`. Only temporary report/output files were written. No OBPI lock/TASK/pipeline state, corpus, ownership declaration, rendered surface, or ledger entry was changed by this trace.

## Exact observed outputs

### ADR status — exit 0

```text
                                 ADR Overview
╭────────────┬───────┬───────────┬────────────────┬──────┬──────────┬─────────╮
│ ADR        │ Lane  │ Lifecycle │ Closeout Phase │ OBPI │ Closeout │ QC      │
├────────────┼───────┼───────────┼────────────────┼──────┼──────────┼─────────┤
│ ADR-0.35.0 │ heavy │ Pending   │ pre_closeout   │ 7/13 │ BLOCKED  │ PENDING │
╰────────────┴───────┴───────────┴────────────────┴──────┴──────────┴─────────╯
                                       OBPIs
╭┬┬───────────┬─────────────────────────────────────────────────────────────────
│││ State     │ Brief
├┼┼───────────┼─────────────────────────────────────────────────────────────────
│││ attested… │ completed
│││ attested… │ completed
│││ attested… │ completed — evidence reconciliation; human completion attestati…
│││ attested… │ completed
│││ attested… │ completed
│││ attested… │ completed
│││ pending   │ draft
│││ in_progr… │ draft
│││ attested… │ completed
│││ pending   │ draft
│││ pending   │
│││ pending   │
│││ pending   │ draft
╰┴┴───────────┴─────────────────────────────────────────────────────────────────
Issues
07 ledger proof of completion is missing
08 ledger proof of completion is missing
10 ledger proof of completion is missing
11 ledger proof of completion is missing
12 ledger proof of completion is missing
13 ledger proof of completion is missing
Closeout Readiness: BLOCKED
Closeout Blockers:
  - OBPI-0.35.0-07-content-land-orchestrator: ledger proof of completion is
missing
  - OBPI-0.35.0-08-remember-post-append-advisory: ledger proof of completion is
missing
  - OBPI-0.35.0-10-classification-reader-and-ownership: ledger proof of
completion is missing [tracked defects: GHI-737 (closed)]
  - OBPI-0.35.0-11-corpus-shape-witness: ledger proof of completion is missing
[tracked defects: GHI-922 (open)]
  - OBPI-0.35.0-12-rules-corpus-onboarding: ledger proof of completion is
missing [tracked defects: GHI-921 (open)]
  - OBPI-0.35.0-13-render-order-truncation-survival: ledger proof of completion
is missing
QC Readiness: PENDING (pending: OBPI completion, TDD, Docs, BDD, Human
attestation)
```

### Live lineage scope — exit 0

```text
[advisory] rendition-lineage: What is ungraded: committed rendition 'AGENTS.md/root' declares 12 corpus-owned sections but carries no committed lineage artifact (/Users/jeff/Documents/Code/gzkit/.gzkit/renditions/AGENTS.md/root.lineage.json is absent), so those sections have no provenance baseline to grade against and are reported UNGRADED.
Why it matters: ADR-0.35.0 § Decision item 4 grades owned sections against a committed lineage artifact; counting these as owned coverage would claim proof this gate does not have. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: publish the rendition and its lineage together — `gz content compose AGENTS.md --consumer root`, then `gz content commit AGENTS.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 0/22 sections owned, 0/47851 bytes owned (0.0%); 12 section(s) / 41846 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
Validated: rendition_lineage

✓ All validations passed (1 scopes).
```

### Content land dry-run — exit 2

```text
BLOCKERS: gz content: error: argument content_command: invalid choice: 'land' (choose from 'import', 'list', 'show', 'render', 'edit', 'remember', 'retire', 'unown', 'own', 'compose', 'commit', 'reconcile-retirements', 'advise-rendition')
```

### Empty-attestor retire fidelity probe — exit 1

```text
Error: retiring 'corpus-prime-directive-ownership-2026-06-19T22:55:06.046462+00:00' moves the liveness of invariant-tier entry corpus-prime-directive-ownership-2026-06-19T22:55:06.046462+00:00 — the 0-Kelvin floor every rendition must carry verbatim — un-binding floor canon is a canon change, so it requires a named --attestor (AGENTS.md § Operator Doctrine; the ATTESTATION GRANULARITY FOR THE CONTENT SURFACE ruling); nothing written.
  Retry with `gz content retire AGENTS.md --entry corpus-prime-directive-ownership-2026-06-19T22:55:06.046462+00:00 --reason "<why>" --attestor "<your name>"`.
```

### Existing isolated capture tests — exit 0

```text
..................
----------------------------------------------------------------------
Ran 18 tests in 0.035s

OK
```

### Live pure generator, declaration and pre-lock ratchet refusal

```text
DECLARATION {"sections": {"unowned": 10, "corpus-owned": 12}, "floor": 6005, "measured_unowned": 6005, "floor_event_id": "unowned-ratchet-updated-AGENTS.md-owned-stdlib-first-doctrine-dependency-posture-255e275ac942653f"}
GENERATE {"candidate_bytes": 31244, "unowned_sections_byte_equal": 10, "unowned_total": 10, "evidence": {"invariant_bytes": 24350, "compressible_bytes_before": 354, "compressible_bytes_after": 354, "emitted_entry_bytes": 24704, "generated_structural_bytes": 535, "carried_forward_bytes": 6005, "total_bytes": 31244, "setpoint": "lite"}}
RAISE_REFUSED What failed: recording an unowned-byte total of 6006 for surface 'AGENTS.md' would raise its ratchet floor above the value 6005 you last read -- this fast path does not re-read the committed floor, so the true committed value may differ.
Why forbidden: REQ-0.35.0-04-02 -- the unowned-byte ratchet is decrease-only; recording through this ordinary path can only lower or hold the floor, never raise it. The committed floor is re-read under the write lock, so it may have moved below the value you read before calling.
Next step: raise the floor through the attested raise-path (`gz content unown AGENTS.md --section <id> --attestor <name> --reason <reason>`), never by recording a larger total here.
```

### Selected Layer-2 records

```text
{"event": "obpi_receipt_emitted", "id": "OBPI-0.35.0-09-codex-playback-wiring", "ts": "2026-08-21T08:23:56.091924+00:00", "obpi_completion": "attested_completed", "attestor": "g0"}
{"event": "obpi_receipt_emitted", "id": "OBPI-0.35.0-01-corpus-tombstone-schema-and-fold", "ts": "2026-08-24T11:08:30.180523+00:00", "obpi_completion": "attested_completed", "attestor": "g0"}
{"event": "obpi_receipt_emitted", "id": "OBPI-0.35.0-02-content-withdraw-verb", "ts": "2026-08-26T02:01:49.286557+00:00", "obpi_completion": "attested_completed", "attestor": "g0"}
{"event": "obpi_receipt_emitted", "id": "OBPI-0.35.0-04-section-ownership-and-ratchet", "ts": "2026-09-05T18:11:12.571523+00:00", "obpi_completion": "attested_completed", "attestor": "g0"}
{"event": "obpi_receipt_emitted", "id": "OBPI-0.35.0-03-retire-duplicate-invariant-entries", "ts": "2026-09-05T20:05:13.115083+00:00", "obpi_completion": "attested_completed", "attestor": "g0"}
{"event": "obpi_receipt_emitted", "id": "OBPI-0.35.0-05-corpus-candidate-generator", "ts": "2026-09-11T00:07:23.568395+00:00", "obpi_completion": "attested_completed", "attestor": "g0"}
{"event": "obpi_receipt_emitted", "id": "OBPI-0.35.0-06-validate-rendition-lineage", "ts": "2026-09-12T09:25:12.780168+00:00", "obpi_completion": "attested_completed", "attestor": "g0"}
CURRENT_OWNERSHIP_WITNESS
{"schema": "gzkit.ledger.v1", "event": "unowned_ratchet_updated", "id": "unowned-ratchet-updated-AGENTS.md-owned-stdlib-first-doctrine-dependency-posture-255e275ac942653f", "ts": "2026-09-07T10:51:28.755746+00:00", "prior_unowned_byte_floor": 7663, "covering_entry_ids": ["corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:26.990597+00:00", "corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:27.114752+00:00", "corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:27.238703+00:00", "corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:27.361841+00:00", "corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:27.487766+00:00", "corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:27.617161+00:00", "corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:27.748592+00:00", "corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:27.873240+00:00", "corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:27.998284+00:00", "corpus-stdlib-first-doctrine-dependency-posture-2026-09-07T10:51:28.123612+00:00"], "surface": "AGENTS.md", "attestor": "g0", "reason": "GHI #933 restored the lift pointers canon still declares (Invariant 3); the live corpus now carries every content line of this section verbatim, so the corpus owns it through the GHI #974 transition instead of a raised floor", "predecessor_event_id": "unowned-ratchet-updated-AGENTS.md-owned-make-llm-stochastic-vibes-inert-anti-vibing-mantra-24ad49d06d8f292b", "new_unowned_byte_floor": 6005, "section": "stdlib-first-doctrine-dependency-posture", "covered_lines": 10, "sections_digest": "ed614a3147b2d51a728d485e36253b4e", "body_lines": 10}
RAW_L2_LINES
15246 OBPI-0.35.0-09-codex-playback-wiring attested_completed 2026-08-21T08:23:56.091924+00:00
15432 OBPI-0.35.0-01-corpus-tombstone-schema-and-fold attested_completed 2026-08-24T11:08:30.180523+00:00
15504 OBPI-0.35.0-02-content-withdraw-verb attested_completed 2026-08-26T02:01:49.286557+00:00
15807 OBPI-0.35.0-04-section-ownership-and-ratchet attested_completed 2026-09-05T18:11:12.571523+00:00
15854 OBPI-0.35.0-03-retire-duplicate-invariant-entries attested_completed 2026-09-05T20:05:13.115083+00:00
16170 OBPI-0.35.0-05-corpus-candidate-generator attested_completed 2026-09-11T00:07:23.568395+00:00
16347 OBPI-0.35.0-06-validate-rendition-lineage attested_completed 2026-09-12T09:25:12.780168+00:00
```

## Source roots

/Users/jeff/Documents/Code/gzkit/docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md

/Users/jeff/Documents/Code/gzkit/docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis

/Users/jeff/Documents/Code/gzkit/src/gzkit

/Users/jeff/Documents/Code/gzkit/.gzkit/ledger.jsonl
