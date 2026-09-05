# Plan — OBPI-0.35.0-04-section-ownership-and-ratchet

**Parent ADR:** ADR-0.35.0-canon-entry-corpus-landing (§ Decision item 3)
**Brief:** docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md
**Lane:** Heavy

## Context

ADR § Decision item 3, quoted verbatim:

> SECTION OWNERSHIP + DECREASE-ONLY RATCHET. Sections declare `corpus-owned` or
> `unowned`. The generator materializes owned sections from the corpus and carries
> unowned sections forward verbatim. The unowned byte total is recorded in a
> decrease-only ratchet. Un-owning a section (which raises the ratchet) requires an
> attested raise-path, corpus-attested, the same shape as the retire path -- an
> undefined reversal path is the one agents invent.

This OBPI ships the declaration and the ratchet. It does NOT ship materialization
(OBPI-0.35.0-05) or the `--rendition-lineage` gate (OBPI-0.35.0-06).

**Unit ruled 2026-09-02 (operator):** *"span-based, consistent with REQ-05"*.
Unowned bytes = summed byte span of sections declared `unowned`.

Baseline re-measured 2026-09-02 with the canonical `gzkit.content.parse.section_id`:
22 H1/H2 sections, 46,876 B total; 10 corpus-addressed sections spanning 38,239 B;
12 unowned sections spanning 8,637 B; coverage 81.6%. Derived at run time, never stored.

## Step 6a Disclosures (plan-before-exploration, advisory)

**Destination-in-mind.** Before writing this plan I had already formed the approach it
proposes: a Pydantic declaration model plus a JSON schema, byte spans computed by
reusing the existing `section_id` vocabulary, and a decrease-only guard in the store's
update path. That destination came from reading the brief's Allowed Paths, which name
`ownership.py`, `unown.py`, and `section_ownership.json` as CREATE targets — the brief
largely fixes the shape, so the plan is closer to a decomposition than a free design.

**Rejected alternatives.**

1. A fresh slugifier local to `ownership.py`. Rejected on reading
   `markdown_parser.py:183` — `section_id` is documented as "the single section-id
   vocabulary shared by every surface that names a section ... a second slugifier would
   let those surfaces disagree." Inventing one would also have silently failed REQ-06.
2. Storing the baseline figures in the declaration as authoritative. Rejected: REQ-07
   requires derivation at run time, and `.claude/rules/governance-core.md` makes a
   written value illustrative. The declaration stores the FLOOR (a ratchet needs
   durable state) but recomputes the coverage figure.
3. Reusing `surface_delivery_witness._rendered_sections` for spans. Rejected: it scans
   H2 only and returns heading offsets, not spans; AGENTS.md carries two H1s that the
   brief's "22 H1/H2 sections" counts. A shared helper is the right eventual home but
   widening that private function is outside this brief's allowlist.
4. Folding the raise-path into the existing `content retire` verb. Rejected: retire
   acts on corpus ENTRIES, un-own acts on SECTIONS. The brief names `unown.py` as a
   CREATE target and the ADR calls for "the same shape", not the same verb.

## Files

- `src/gzkit/schemas/section_ownership.json` — CREATE, declaration schema
- `src/gzkit/content/ownership.py` — CREATE, model, store, span measurement, ratchet
- `.gzkit/ownership/AGENTS.md.json` — CREATE, day-one declaration and floor
- `src/gzkit/commands/content/unown.py` — CREATE, attested raise-path command
- `src/gzkit/commands/content/__init__.py`, `src/gzkit/cli/**` — MODIFY, register verb only
- `src/gzkit/governance/events.py` — MODIFY, ownership and ratchet events
- `tests/content/test_ownership.py` — CREATE, covering tests
- `tests/commands/test_content_unown.py` — CREATE, covering tests
- `features/**` — ADD, Gate 4 scenarios for the raise-path
- `docs/user/manpages/content.md` — MODIFY, raise-path section

## Steps

1. Schema and model. `section_ownership.json`: `surface`, `sections` (map of section id
   to the closed enum `corpus-owned` / `unowned`), `unowned_byte_floor` (int >= 0),
   `measured_at`. Pydantic `OwnershipDeclaration` mirrors it. The closed enum satisfies
   REQ-01's "no third value". (REQ-01)
2. Span measurement. `measure_section_spans(surface)` returns a mapping of section id to
   byte span over H1/H2 headings, keyed by `section_id(title)` imported from
   `gzkit.content.parse`. (REQ-06)
3. Fail-closed load. `load_declaration(path, surface)` cross-checks declared keys against
   measured ids: an undeclared present section, a declared-but-absent id, or a value
   outside the enum raises, naming the offending section id. Three-part recovery prose.
   (REQ-01, REQ-09)
4. Baseline computation. `compute_baseline(surface, corpus)` returns owned count, unowned
   span, total span, coverage pct, and the per-section entry-count histogram — all
   derived, none stored. (REQ-07, REQ-08)
5. Decrease-only ratchet. `record_unowned_total(decl, total)` — a total less than or equal
   to the floor updates it and emits a ratchet event carrying prior and new values; a
   greater total is REFUSED with recovery prose and no write. (REQ-02, REQ-03, REQ-09)
6. Ledger events. Add the ownership-transition and ratchet-floor-change events to
   `events.py`, following the existing emit-helper pattern. (REQ-05)
7. Attested raise-path. `gz content unown <surface> --section <id> --attestor --reason`,
   mirroring the FAIL-CLOSED arm of `commands/content/commit.py:88-117`: an empty or
   whitespace-only attestor or reason exits non-zero, writes nothing, emits nothing. On
   success the section flips to `unowned`, the floor RISES by that section's span, and the
   event records the section id, both floor values, the attestor, and the reason.
   (REQ-04, REQ-05, REQ-09)
8. Day-one declaration. Generate `.gzkit/ownership/AGENTS.md.json` from the measured
   baseline. (REQ-08)
9. Parser registration in `commands/content/__init__.py` and `cli/**`. Verb only.
10. Docs and BDD. Manpage section for `content unown`; behave scenarios tagged
    `@REQ-0.35.0-04-04` and `@REQ-0.35.0-04-05` for the attested raise-path.

Each step follows Red-Green-Refactor: one minimal test, watched to fail on its own
assertion (never an import error), then the simplest code that passes.

## Recovery Protocol — the complete interruption-state account (operator ruling 2026-09-05)

Authored because the recovery path was being repaired one adversary finding at a time
without an account of what each interrupted state MEANS. Operator ruling, verbatim:
*"Do not use successive adversary rounds as the process for discovering the recovery
design."* Three assumptions in the code are invalid and are corrected here:

| Invalid assumption | What is actually established |
|---|---|
| Declaration is visible -> declaration is durable | The directory durability barrier may have failed |
| Journal exists -> recovery remains possible | It holds a digest, but not the lost bytes recovery requires |
| Ledger witness is absent -> journal can safely be deleted | The declaration may already reference that missing witness |

`_commit_transition` writes in this order: journal -> declaration -> ledger witness ->
clear journal. `write_declaration_atomically` performs `os.replace` and THEN the parent
directory fsync, so **every** write in the sequence has a window where the swap landed but
its durability barrier did not. That is the fact the states below are enumerated against.

### The five states

| # | State | Evidence available on disk | Retry action | Retained recovery data | Truthful operator instruction |
|---|---|---|---|---|---|
| A | **Journal persisted**, declaration untouched | Journal parses; declaration `floor_event_id` == journal `parent_event_id`; declaration floor == journal `prior_unowned_byte_floor`; landed sections == predecessor | Replay the unlanded branch: re-validate against the on-disk predecessor, derive the successor, write the declaration, witness it, clear the journal | Journal (`surface`, `surface_digest`, `declaration_json`, `parent_event_id`, `event_id`) + source snapshot | "Re-run the same command." |
| B | **Declaration replaced, durability UNCONFIRMED** | Declaration carries the new floor and new `floor_event_id`; journal present; ledger has no event for `event_id`. **Indistinguishable from C by inspection** — that is the defect | **Re-establish the durability barrier on the declaration and its directory BEFORE witnessing or clearing.** Persistent barrier failure must keep refusing with the journal retained | Journal + source snapshot; journal MUST NOT be cleared until the barrier confirms | "The declaration appears to carry the new floor, but its durability is unconfirmed. Re-running re-establishes it; nothing is cleared until it succeeds." |
| C | **Declaration durable, witness ABSENT** | Same on-disk shape as B; distinguished only by the barrier having succeeded | Append the witness (idempotent — `_append_event_once` requires exact semantic equality on an existing id), then clear the journal | Journal until the witness lands | "Re-run to append the missing ledger witness." |
| D | **Witness PRESENT** | Ledger carries `event_id`; declaration `floor_event_id` == that id | Clear the journal only **when the source axis is also reconciled** — see the operator ruling below; D alone does NOT discharge reconciliation or cleanup | Nothing further **only when not also in E** | "The transition already completed. Re-run to clear the pending journal." — and in D+E, *"transition witnessed; source reconciliation pending"* at a non-success status |
| E | **Source CHANGED** since measurement | Measured surface digest != journal `surface_digest` | Extract the retained source snapshot to a side path; reconcile; complete once the measured bytes match the journalled digest | Journal + **the measured source bytes**, retained as immutable recovery material | Name the snapshot path and the reconciliation steps. NEVER silently rewrite the source; newer edits must be preserved |

### CORRECTION (2026-09-05) — E is ORTHOGONAL to A-D, not a fifth partition member

The table above presents five states as if they partitioned the space. **They do not.**
A-D are mutually exclusive positions in the commit sequence; **E is a second axis** — a
transition in ANY of A-D may also have a changed source. Presenting them as one list is a
defect in this plan, and it produced one in the code: the state-E check was placed ahead of
the state-D probe, so a transition interrupted between the ledger append and the journal
unlink, followed by an ordinary editor save, reported **state E** and instructed a full
reconcile-and-restore — when D's retry action is "clear the journal only; the transition is
complete." The E prose *"completing the transition now would witness a span the surface no
longer has"* is also false in D, where `_append_event_once` finds the existing id and
appends nothing.

**Resolution (2026-09-05, FIRST ATTEMPT — SUPERSEDED, recorded because it is the defect's
origin): "D beats E."** Probe the ledger witness before concluding E; when the witness is
present the transition is already complete and the source no longer matters, so D's action
governs. **That resolution overreached and Step-4b round 11 refuted it (finding 1, `high`).**
Making D *govern* made D *swallow* E: in D+E the command cleared the journal, the retained
source and the extract, and exited 0 while the declaration's floor exceeded the live span —
`D+E retry_exit 0 floor 83 span 102 journal False snapshot False extract False`, then
`advertised_raise alpha-section exit 1`. The advertised recovery re-run could not repair it,
because its own initial load rejects the exceeded floor. The orthogonality observation above
is CORRECT and stands; only the resolution built on it was wrong.

**RESOLUTION (OPERATOR RULING 2026-09-05, BINDING — supersedes the above).** Verbatim:
*"Reject 'D beats E.' Keep three obligations separate: the transition is durably witnessed;
the source is reconciled; recovery cleanup is complete. Establishing one does not discharge
the others."*

Read the lifecycle as THREE INDEPENDENT OBLIGATIONS, never as a precedence order:

| Obligation | Established by | Never implies |
|---|---|---|
| **Witnessed** — the transition is durable | Declaration `floor_event_id` names this transition AND the ledger carries its witness | that the source is reconciled, or that cleanup ran |
| **Reconciled** — the surface still carries the measured bytes | Measured surface digest == journal `surface_digest` | that the witness landed |
| **Cleaned** — no recovery residue remains | Journal, retained source, and extract are all absent | that either of the above holds |

Consequences that bind the implementation:

- In **D+E**, preserve the existing witness WITHOUT duplication, report *"transition
  witnessed; source reconciliation pending"*, return a **non-success** status, and RETAIN
  the measured bytes while preserving the operator's newer edits. D proves the original
  transition was witnessed — never that source reconciliation is finished.
- A refusal path that establishes one obligation MUST NOT clear the material another
  obligation still depends on.
- **Attempted unlink does not establish cleanup.** Cleanup is its own obligation with its own
  failure reporting (see § Binding constraints 5, below).

### Binding constraints on the implementation

1. **B is the correction for round-10 blocker 1.** Landed recovery currently sees the new
   `floor_event_id`, skips the atomic writer entirely, witnesses and clears — never retrying
   the barrier that failed. Measured: `REAL_WRITER first_exit 2 directory_fsync_attempts 2`
   then `REAL_WRITER retry_exit 0 fsync_calls 0 witnesses 1 journal False`.
2. **E is the correction for round-10 blocker 2**, and the operator PREFERS preserving the
   measured source bytes. Copied bytes do not create a second authority — the journal already
   copies the serialized successor declaration; retained recovery material is historical
   evidence, not canon. **A snapshot without a usable recovery route is incomplete**: define
   extraction and restoration end to end, preserve newer edits, and never silently rewrite
   the source.
3. **The journal-deletion advice in `_refuse_forged_journal` is WRONG and must be corrected.**
   It currently says: if the ledger carries no `section_ownership_unowned` event, "the raise
   never completed: delete the journal and re-run." Absence of a witness does not prove the
   declaration was unchanged — states B and C both have an absent witness with the declaration
   already replaced. Following that instruction destroys the only remaining recovery record.
   Recovery prose must be derived from the enumerated state, never from one signal read alone.
4. **Every operator instruction in this module must name the state it was derived from.**
5. **Cleanup is recoverable, and an attempted unlink does not establish it** (operator ruling
   2026-09-05 point 3; round-11 finding 2, `medium`). `_clear_recovery_state` currently wraps
   all three unlinks in one `contextlib.suppress(OSError)`, so journal deletion can fail while
   its snapshot is deleted — `journal_unlink_failed exit 0 journal True snapshot False
   diagnostic_mentions_IO_fault False` — and later requests recover the same uncleared journal
   repeatedly without ever exposing the fault. Required: suppress only **expected absence**;
   report any other cleanup failure as **state-D cleanup pending**; **retain the remaining
   material when journal removal fails** (the journal is what gates replay, so its dependents
   must outlive a failed removal); account for **interruption between the deletions, including
   their durability barriers**; and make **retries handle residual artifacts even when the
   journal is already absent** — today an absent journal returns early and orphaned snapshot
   or extract files are never swept.
6. **The extraction-file family is final AND temporary** (operator ruling 2026-09-05 point 4;
   round-11 finding 3, `medium`). The atomic writer stages under
   `.<surface>.unowning-recovery.<n>.tmp`; the ignore rule covers only the final
   `<surface>.unowning-recovery`. Measured: `EXTRACT_CRASH exit 99 residue
   ['/review/.doc.md.unowning-recovery.3.tmp']`, `RESIDUE_IS_MEASURED_SOURCE True`, and a
   successful recovery retained it. Independently verified: `git check-ignore` exits 0 for
   `AGENTS.md.unowning-recovery` and 1 for `.AGENTS.md.unowning-recovery.abc123.tmp`. Both the
   ignore rules and the recovery cleanup must cover the whole family — a staging file holding
   measured source bytes is exactly the material an unignored `git add -A` would stage.
7. **Recovery prose must be PROVEN, not merely emitted** (operator ruling 2026-09-05 point 2).
   Executing the printed sequence verbatim, starting from the reproduced failure, must end
   with a canonical `load_declaration` ACCEPTING the recovered state while the operator's
   newer edit remains safely saved. Restoring the retained measured bytes achieves this.
   **Never instruct the operator to re-apply an oversized edit and then invoke a command whose
   initial loader rejects it** — that is the defect in the current step 5.

8. **DURABLE JOURNAL ABSENCE IS THE BOUNDARY, and it is mandatory** (operator ruling
   2026-09-05, escalation response). This SUPERSEDES the implementation's earlier argued
   position that no directory-fsync barrier was needed after the unlinks — an argument both
   Task-2 reviewers found addressed only a single removal's own durability while the invariant
   actually relied upon is CROSS-FILE ordering, across two directories (journal and retained
   source in `.gzkit/ownership/`, extract beside the surface). Operator verbatim:

   > Establish durable journal absence before deleting or reusing dependent recovery files,
   > including when the journal is already absent on entry. Failure to establish that boundary
   > preserves the files and exits non-zero.

   The barrier is required on BOTH entries — after removing a journal, and on an invocation
   that finds none. A journal whose directory entry removal is not durable can come back after
   a crash; deleting its dependents before that is settled is the round-11 finding-2 inversion
   restated by the filesystem rather than by the code.

9. **Orphan residue and current-transaction cleanup are DIFFERENT OBLIGATIONS** (same ruling).
   - Cleanup failure belonging to the CURRENT transaction remains **non-success**.
   - After the durability boundary is established, failed removal of UNRELATED orphan residue
     may **warn and permit fresh work** — but normal declaration validation and persistence of
     the new transaction's recovery snapshot remain mandatory. A warning never buys a shortcut
     past either.
   - **Orphan warnings stay distinct THROUGH FINALIZATION.** The same old leftover must never
     be reclassified as a failure of the NEW transaction's cleanup — that would report a fault
     the new transaction did not cause, the mirror of the false-premise defect named just below.
   - **An orphan sweep reports only what it OBSERVED.** The refusal previously announced
     *"the un-owning of `<surface>` is complete"* and *"exactly two are discharged — transition
     witnessed; source reconciled"* on a path reachable by a crash during the transaction's
     FIRST write, where no journal, no declaration change and no witness exist. Both premises
     false, and the message contradicted itself in one paragraph.
   - **Test these distinctions, including failure of the journal-removal durability barrier.**

### Demonstration obligations

Repeated failure followed by successful recovery, using **only data the implementation
retained** — never an original copy held by the test. Cover **both** replay branches
(unlanded and landed). Persistent barrier failure must keep refusing with recovery state
retained. Update the coupled documentation (`docs/user/manpages/content.md`) in the same
patch set per `.gzkit/rules/gate5-runbook-code-covenant.md`.

#### FOUR DEMONSTRATIONS REQUIRED BEFORE THE NEXT ADVERSARIAL ROUND (operator ruling, 2026-09-05)

These are **preconditions on dispatching Step 4b**, not acceptance criteria the adversary is
asked to check. A round dispatched against undemonstrated behavior spends a tier-1 pass
rediscovering what a test should already have witnessed — which is how rounds 9, 10 and 11
were spent. Operator verbatim: *"Before another adversarial round, demonstrate:"*

1. **D+E remains recoverable across REPEATED retries** — non-success status, no duplicate
   witness, newer edits preserved, measured bytes retained. Repetition is the point: a single
   retry proving the refusal says nothing about whether the *second* and *third* leave the
   recovery material intact, and the round-11 defect was precisely a retry that behaved
   differently from the first invocation.
2. **The printed recovery instructions work** — starting from the reproduced failure, follow
   them using implementation-retained bytes and finish with a canonical loader ACCEPTING the
   recovered state. Newer edits preserved separately. The circular instruction to invoke
   `gz content unown` against an already-exceeded floor is removed.
3. **Cleanup survives failure and interruption** — a failed journal removal preserves dependent
   material; retries handle partial cleanup, **including residue after the journal disappears**;
   deletion durability is accounted for.
4. **Extraction artifacts are contained** — final AND staging filenames ignored, and interrupted
   staging files have a **tested** cleanup path.

Then: update this plan and the recovery documentation to match implemented behavior, run the
required verification, and **bind the recorded mutation evidence to the final source SHA**
before the round is dispatched.

## Verification

```
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz cli audit
uv run mkdocs build --strict
```

## Notes

- Denied: `AGENTS.md` itself, `composer.py`, `trust_audits/**`, `models/corpus.py`.
- REQ-08 is [support] — proven by the `artifact_edited` ledger event citing
  `.gzkit/ownership/AGENTS.md.json` plus `gz validate --documents`, never by a unit test
  authored to fill the cell (ADR-0.0.59).
- Scope collisions reported by `gz plan audit` are all against TERMINAL briefs on shared
  infrastructure files; none is a live brief owning this work.
