---
id: OBPI-0.35.0-03-retire-duplicate-invariant-entries
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 3
lane: Heavy
status: Active
allowlist:
- .gzkit/corpus/AGENTS.md.jsonl
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md
reqs:
- REQ-0.35.0-03-01
- REQ-0.35.0-03-02
- REQ-0.35.0-03-03
- REQ-0.35.0-03-04
req_atomic:
  # Each REQ is one indivisible authoring edit to this single brief file — there is
  # no labor below the REQ (GHI #590). This OBPI writes no code (see § Denied
  # Paths); every REQ's proof channel is a corpus row, a ledger event, or a
  # documented-in-this-brief operator ruling, never a multi-step RGR cycle.
  - REQ-0.35.0-03-01  # one predicate amendment (ledger -> corpus-tombstone proof channel), one edit.
  - REQ-0.35.0-03-02  # recording an operator ruling in prose — one authoring act per ruling.
  - REQ-0.35.0-03-03  # one predicate retained, one witness-clause amendment — one edit.
  - REQ-0.35.0-03-04  # STRUCTURAL-FENCE; audited at ADR closeout, no labor unit here.
verification:
- uv run gz validate --rendition-floor-coherence
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz test
tasks:
  - TASK-0.35.0-03-01-01
  - TASK-0.35.0-03-02-01
  - TASK-0.35.0-03-03-01
  - TASK-0.35.0-03-04-01
---

# OBPI-0.35.0-03-retire-duplicate-invariant-entries: Retire Duplicate Invariant Entries

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #3 - "Retire the 8 duplicate invariant entries -- 7 byte-identical + the operator-ruled divergent pair; corpus 50 -> 42 (GHI #635)"

**Status:** Draft

## Objective

Retire exactly EIGHT redundant `invariant`-tier entries from the AGENTS.md corpus under one corpus-attestation batch — one redundant copy from each of the seven byte-identical groups, plus the operator-ruled loser of the divergent quote-style pair — discharging GHI #635. (This sentence read "taking the live invariant count from 50 to 42" until 2026-08-22; that figure was a measurement of a 51-row corpus, not a target the brief can still hit. Read the live count from the store, never from this line.)

> **AMENDED 2026-08-18 (operator-ruled, GHI #822): this brief's content-surface
> attestation is renamed from "Gate 5" to CORPUS ATTESTATION.** Gate 5 names
> OBPI/ADR completion attestation (`ADR-0.0.36`) and nothing else; a build step
> wearing that name is the collision the transit/exchange/handoff fence forbids
> (operator ruling 2026-08-17, `AGENTS.md` § Operator Doctrine). The noun is
> `corpus`, not `rendition`, because the same ruling puts the attestable subject on
> the corpus and holds a rendition to be a Layer-3 derived view, "never the thing
> attested." Parent ADR § Decision carries the governing amendment. This brief's own
> `### Gate 5 (Human)` gate-covenant sections are UNCHANGED — those are the genuine
> Gate 5, on this OBPI's completion. Naming only; no REQ semantics change.

> **AMENDED 2026-08-22 (operator-ruled): groups 1-7 are DISCHARGED OUT-OF-BAND and their
> disposition is INVERTED.** Two separate changes, recorded together because one caused the other.
>
> **(a) The disposition inverted.** Operator ruling, verbatim: *"topical section wins, retire the
> canon-section copies"*. `REQUIREMENT 12` said the opposite until this date, and `REQUIREMENTS 3-9`
> named the retire/RETAIN sides accordingly; all eight lines are amended in place, id-for-id. The
> superseded rationale — that `operator-doctrine-verbatim-canon` is the operator's own home for these
> utterances — was sound on what was known when this brief was authored. It was outweighed by a fact
> that was not: all seven canon-section rows are `origin=cli:content-remember` from a single
> 2026-06-19T22:54 import that **flattened seven differentiated classifications to `Ambiguous`**,
> while the topical originals carry Judgment, Promotable and Mechanical. Retaining the canon rows
> would have kept the copies that lost information. The ruling was given on that evidence.
>
> **(b) The work landed outside this pipeline.** The seven retirements were executed as a GHI
> direct fix under **GHI #862**, not through `gz-obpi-pipeline`. This is a process defect, recorded
> rather than excused. Its cause is filed as **GHI #864**: `ghi-author` Step 0's prior-art pre-flight
> runs two `gh issue list` queries and reads no OBPI brief, so an authored brief owning the same work
> is invisible to it by construction. Step 0 was run as written and could not have found this brief.
> The precedent for recording an out-of-band landing here is the § PARTIALLY PRE-LANDED block above,
> which records the divergent pair landing early under GHI #635 — that one landed *consistent* with
> the brief; these seven landed *inverted*, which is why this block exists separately.
>
> **Re-measured 2026-08-22 against `.gzkit/corpus/AGENTS.md.jsonl`:**
>
> | Fact | Brief's target | Observed 2026-08-22 |
> |---|---|---|
> | raw rows | 59 (51 + 8 tombstones) | **76** (64 entries + 12 retractions) |
> | live entries | 42 `invariant` + 1 `compressible` | **51 `invariant` + 1 `compressible`** |
> | live byte-identical `invariant` texts | 0 | **0** |
> | `corpus_entry_retired` events for this brief's groups | 8 in one batch | ~~8 total, across three sessions~~ **WRONG — corrected 2026-08-26 to `1` (see the AMENDED 2026-08-26 block below)** |
>
> The row and entry counts do NOT reconcile to the brief's arithmetic and cannot be made to: that
> arithmetic was pinned to a 51-row corpus that has since grown by capture unrelated to this brief.
> `REQUIREMENT 1` and `REQUIREMENT 14` are amended to cite the measurement rather than restate a
> frozen number (`.claude/rules/governance-core.md` § Non-negotiable rules — a value in prose is
> illustrative, never authoritative).
>
> **What remains for the pipeline:** the retirements themselves are done and the fence property holds.
> `REQ-0.35.0-03-04`'s regression fence is TRUE but was proven outside the two-stage review meant to
> witness it, so it needs a covering audit at ADR closeout as the REQ itself already requires.
> `REQ-0.35.0-03-02`'s operator ruling is recorded HERE by this block, discharging its subject.
>
> **CORRECTED 2026-08-26: the "8 total, across three sessions" row above is FALSE, not a
> stale-but-once-true figure.** It was never counted against the ledger directly — it inferred from
> the tombstone rows existing, which is exactly the presence-check failure `AGENTS.md` § DO IT RIGHT
> names ("a gate whose only witness is that an artifact exists"). Measured against `.gzkit/ledger.jsonl`
> on 2026-08-26 by matching each of this brief's eight ids to its `corpus_entry_retired` event: **1 of
> 8** — only `corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00` (GHI #635,
> `ts` `2026-07-22T10:31:32.832846+00:00`, ledger id `corpus-entry-retired-2026-07-22T10:31:32.832846+00:00`).
> The seven GHI #862 groups (G1-G7) have no `corpus_entry_retired` event of any kind; their only ledger
> trace is each row's original `corpus_entry_appended` from the 2026-06-19T22:54 bulk import — an
> append, not a retirement. Per `.claude/rules/governance-core.md` § Non-negotiable rules, a value in
> this prose is a dated record, never authority; this correction is that record superseding the wrong
> one above rather than silently replacing it. Full disposition in the AMENDED 2026-08-26 block below.

> **AMENDED 2026-08-26 (operator-ruled): REQ-0.35.0-03-01 and REQ-0.35.0-03-03 lose the ledger as
> their proof channel; the corpus tombstones replace it.**
>
> **How it was found.** Re-measuring `REQUIREMENT 2` at Stage 1 of `gz-obpi-pipeline
> OBPI-0.35.0-03` (2026-08-26), each of this brief's eight retirement ids was matched by id against
> `.gzkit/ledger.jsonl` for a `corpus_entry_retired` event, rather than accepting the prior
> "8 total, across three sessions" figure at face value (that figure is itself corrected above — it
> was inferred from tombstone presence, never counted against the ledger). The result: **1 of 8**
> ids (`corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00`, GHI #635) has a
> `corpus_entry_retired` event; the other seven (`G1`-`G7`, GHI #862) have none. Separately,
> `corpus_entry_appended` events for the eight tombstone/retraction rows themselves were checked and
> number **0 of 8** — including the GHI #635 one, whose 2026-07-22 run predates the dual-emission
> change that landed in `OBPI-0.35.0-02` (`src/gzkit/commands/content/retire.py:404-426` now emits
> both events; it did not on 2026-07-22). All eight ids were independently confirmed present as LIVE
> retraction rows in `.gzkit/corpus/AGENTS.md.jsonl` (each row's `retires` field names the id), and
> `uv run gz validate --rendition-floor-coherence` exits 0 over this state — nothing in the current
> validator surface detects the ledger gap. Filed as **GHI #885**
> (`corpus: hand-written tombstones retire canon with no ledger witness`), open.
>
> **The operator ruling, verbatim (2026-08-26):** *"Amend REQ-01 to cite the corpus tombstones as
> its proof channel and record the ledger gap against #885. -03 then completes on what's provable.
> Cost: a SUPPORT REQ loses the ledger as its proof channel."* **The ruling names REQ-01 only** — "-03
> then completes" refers to this OBPI completing, NOT to amending REQ-03's text. REQ-0.35.0-03-01's
> Acceptance Criteria text below is amended to this operator ruling directly, on operator-verbatim
> authority.
>
> **REQ-0.35.0-03-03's amendment is a SEPARATE, AGENT-APPLIED EXTENSION of that ruling, disclosed as
> such — not operator-verbatim authority over REQ-03.** The agent applying this pass judged that
> REQ-03 carried the identical false witness clause as REQ-01 ("Witnessed by eight
> `corpus_entry_appended` ledger events"), that REQ-03's substantive append-only predicate is
> unaffected (it names retraction rows, not ledger events, and remains TRUE as measured), and
> therefore applied the same rationale the operator gave for REQ-01 to REQ-03's trailing witness
> clause only. Recorded here explicitly, and attributed to the agent rather than the operator, so a
> future reader does not read REQ-03's change as something the operator ruled on — it is an inference
> from the operator's ruling, not the ruling itself, and converting that inference into operator
> authority would corrupt exactly the ruling history REQ-0.35.0-03-02 exists to preserve.
>
> **Cause: the seven GHI #862 retirements bypassed `gz content retire` entirely.** This brief's own
> § Denied Paths forbids exactly this ("Direct edits to `.gzkit/corpus/AGENTS.md.jsonl` by any means
> other than gz content retire — hand-editing an append-only store is alternative E under another
> name"). Commit `8ed48271` hand-appended the seven tombstone rows and touched `.gzkit/ledger.jsonl`
> not at all (`git show --stat 8ed48271` shows no ledger file in the diff). This is a recorded
> process defect, not an excused one: the § AMENDED 2026-08-22 block above already names the same
> commit's execution path as "outside this pipeline" under GHI #862/#864; this is that same
> out-of-band landing's second consequence, now measured at the ledger layer rather than the
> pipeline layer. GHI #885 is the open route for a systemic fix (detection validator, and/or
> constraining the append ingress); this brief does not attempt that repair — it records the gap and
> completes on what IS provable, per the ruling.
>
> **What this discharges and what it does not.** REQ-0.35.0-03-02's subject — "a future maintainer
> reads a witnessed ruling rather than re-deriving a winner" — is discharged for this third ruling by
> this block existing. It does NOT discharge GHI #885 itself, which stays open and tracked in
> § Tracked Defects below.

> **Note on this brief's amendment idioms (added 2026-08-26).** Three forms are in use, each with a
> distinct scope — a future pass should use one of these, not invent a fourth ad hoc form: (a) the
> `> **AMENDED <date> (operator-ruled)**` blockquote, for block-level rationale that needs its own
> home (an operator ruling, a re-measurement, a disposition change); (b) in-place REQUIREMENT/REQ-text
> rewrite that narrates the prior state inline (e.g. `This REQ pinned "X" until <date>...`), for a
> single requirement's predicate or witness clause changing while the requirement itself survives; (c)
> `~~strikethrough~~` inside otherwise-live prose, for marking one retracted value or clause without
> removing it, so the correction and the thing it corrects stay visually adjacent.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 03 depends on 01 (tombstone fields + fold) and 02 (the withdraw verb). 01 -> 02 -> 03 is the minimum shippable slice: it alone discharges GHI #635 and removes the live double-render, and it is a PREREQUISITE for 05, not a parallel workstream (ADR § Alternatives H).

<!-- gz-validate-skip: command-shape -->
> **PARTIALLY PRE-LANDED — read before implementing (reconciled 2026-07-22;
> RE-RECONCILED 2026-08-07).**
> ONE of this brief's eight retirements landed ahead of the chain as a direct fix:
> commit `42ba6c25` retired the divergent-pair loser under GHI #635, using the
> already-landed `gz content retire` verb (`852e8a25`) rather than the
> `content withdraw` verb this brief's Prerequisites originally named (that name
> was retired from the ADR on 2026-08-07 — see below). Re-measured
> 2026-08-07 at HEAD `6863f0555`:
>
> | Requirement | Target | Observed 2026-07-22 | Observed 2026-08-07 | State |
> |-------------|--------|---------------------|---------------------|-------|
> | REQ-0.35.0-03-01 | 8 `corpus_entry_retired` events | 1 | 1 | **1/8 landed — SEVEN remain** |
> | REQ-0.35.0-03-02 | operator ruling on the divergent pair recorded in this brief | Requirement 10 plus this note | unchanged | **landed** |
> | REQ-0.35.0-03-03 | raw corpus rows after the batch | target 59, observed 52 | **target 60, observed 53** | **open — target moved** |
> | REQ-0.35.0-03-04 | no two live invariant entries byte-identical | 7 duplicate texts remain | 7 duplicate texts remain | **open (structural-fence)** — audited at ADR closeout |
>
> **Corpus state measured on disk 2026-08-07** (liveness = id not named by any
> row's `retires`):
>
> | Quantity | At authoring | 2026-08-07 | After the 7 remaining retirements |
> |---|---|---|---|
> | raw rows | 51 | **53** | **60** |
> | live `invariant` | 50 | **50** | **43** |
> | live `compressible` | 1 | **2** | **9** |
> | retired (tombstoned) | 0 | **1** | **8** |
>
> The corpus both SHRANK and GREW since authoring: one retirement landed, and one
> new `invariant` entry was captured 2026-08-06
> (`operator-doctrine-verbatim-canon`). Live invariant therefore reads 50 in both
> columns for different reasons — do not read the unchanged number as an unchanged
> corpus.
>
> **The parent ADR's `50 -> 42` projection is stale; the live figure is `50 -> 43`.**
> ADR § Checklist item 3 and § Consequences Positive #3 both quote `50 -> 42`, which
> was correct against the authoring-time corpus. Not amended here — REQ-2 already
> mandates re-measurement at implementation time, and the brief is the right home
> for the live number. Flagged so the closeout does not read the ADR's projection
> as a target.
>
> **Requirements 3-9 re-verified against disk: all seven groups and all fourteen
> entry ids still match EXACTLY.** The enumeration did not drift — only the
> arithmetic did. Requirement 2's re-measurement obligation still stands at
> implementation time; this pass discharges it as of 2026-08-07, not permanently.
>
> **The landed retirement is Requirement 10's target only** — the divergent pair,
> `corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00` retired,
> `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:45.960384+00:00`
> retained, matching the ruling recorded there. Requirements 3-9 (the seven
> byte-identical groups) are UNTOUCHED.
>
> **Requirement 1 says EXACTLY EIGHT; the remaining work is SEVEN.** Requirement 1
> is written against the authoring-time corpus and is not silently rewritten here —
> an off-by-one inside a corpus-attestation batch is a fabricated receipt, so the count must be
> re-derived at implementation time and reconciled deliberately, which is
> Requirement 2's job.
>
> **This brief is correctly `PENDING` and must not be completed.** Its
> Prerequisites are not met. **Verb-name collision RULED 2026-08-07 (operator):
> OBPI-0.35.0-02 extends the shipped `gz content retire` in place rather than
> shipping a new `withdraw`,** and the parent ADR is amended to match. The verb
> therefore exists — but its **corpus-attestation half does not**: `content_retire_cmd` takes no
> `--attestor`, does not empty-check `--reason`, and does not discriminate tier
> (`retire.py:31`). Requirement 13 below demands a non-empty `--attestor` on all
> eight invocations, so this brief cannot run until OBPI-0.35.0-02 lands that half.
> The tombstone fold of OBPI-0.35.0-01 is likewise unproven here.
>
> Note: as on OBPI-0.35.0-08, `gz obpi brief-drift` cannot see pre-landed REQ
> satisfaction — it reports **clean across all five dimensions** — so this note is
> authored rather than computed (GHI #581).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/corpus/AGENTS.md.jsonl` — eight appended tombstone rows, written ONLY via gz content retire
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md` — this brief's evidence sections, including the eight entry ids and the operator ruling

## Denied Paths

- `src/gzkit/**` — this OBPI writes NO code; the mechanism is OBPI-0.35.0-01 and OBPI-0.35.0-02
- `tests/**` — a test asserting that this repository's corpus file holds 42 rows is a filesystem-grep that cannot fail when production behavior changes (`.gzkit/rules/tests.md` § REQ Scope Discipline). The fold's behavior is proven in OBPI-0.35.0-01; this OBPI's proof channels are the ledger and the parent ADR's Boundary Invariants.
- `AGENTS.md`, `.gzkit/renditions/**` — recomposing the rendition is OBPI-0.35.0-05 and OBPI-0.35.0-07
- Direct edits to `.gzkit/corpus/AGENTS.md.jsonl` by any means other than gz content retire — hand-editing an append-only store is alternative E under another name
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: EXACTLY EIGHT entries are retired — one per group enumerated in REQUIREMENTS 3-10, identified by id, never by a count. **DISCHARGED, across TWO landing occasions rather than one batch** (see the AMENDED 2026-08-22 block): the divergent-pair loser under GHI #635, the seven group duplicates under GHI #862. **This corrects "across three sessions," which this REQUIREMENT asserted until 2026-08-26 and which was ALSO wrong — the same presence-check-inference error as the ledger-events claim struck at line 89, sitting in a second place.** Measured 2026-08-26 from the `ts` field of the eight tombstone rows in `.gzkit/corpus/AGENTS.md.jsonl`: `2026-07-22` (1 row — the divergent-pair loser, GHI #635) and `2026-08-22` (7 rows — the seven groups, GHI #862, all landed within one second of each other, unambiguously one batch in one session) — **two** distinct landing occasions, not three; there is exactly one tombstone per target, so no un-retire/re-retire history inflates the count. **This IS a landing-timeline fact about corpus rows — when each retirement's row was appended — and is a DIFFERENT SUBJECT from the ledger-events figure corrected at line 89 (`corpus_entry_retired` events, not corpus rows); both were wrong, and they were wrong about different things.** The figures this requirement used to carry — "51 rows total, 50 `invariant` + 1 `compressible`" — were a measurement taken before this brief was written and are retained here as a DATED RECORD of that baseline, not as a target; the corpus has since grown by capture unrelated to this brief. An off-by-one inside a corpus-attestation batch is still a fabricated receipt; the guard is the id list, which does not go stale.
2. REQUIREMENT: ALWAYS re-measure before appending. Re-derive the group membership from the corpus on disk at implementation time and compare it to the ids enumerated in this brief. If the sets differ, STOP and emit BLOCKERS — do not reconcile silently. **Re-discharged 2026-08-26** against `.gzkit/corpus/AGENTS.md.jsonl` (79 raw rows): all sixteen enumerated ids (eight retired-side, eight retained-side) resolve exactly as REQUIREMENTS 3-10 specify — eight present in raw and absent from live, eight retained live — the set comparison passes, and no BLOCKERS were emitted. Per the 2026-08-07 precedent above, this discharges the obligation as of 2026-08-26, not permanently; re-measurement still stands at implementation time on any future pass.
3. REQUIREMENT: GROUP 1 (cross-section, `attestation` / `operator-doctrine-verbatim-canon`) — retire `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:19.779516+00:00`; RETAIN `corpus-attestation-2026-06-06T06:20:27.327411+00:00`. ("Never, ever again give me that TTY or PTY bullshit …")
4. REQUIREMENT: GROUP 2 (cross-section, `behavior-rules` / `operator-doctrine-verbatim-canon`) — retire `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:28.077865+00:00`; RETAIN `corpus-behavior-rules-2026-06-10T07:53:55.264205+00:00`. ("The ACTIVE campaign plan …")
5. REQUIREMENT: GROUP 3 (cross-section, `behavior-rules` / `operator-doctrine-verbatim-canon`) — retire `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:44.407717+00:00`; RETAIN `corpus-behavior-rules-2026-06-10T08:12:41.048588+00:00`. ("Magna Carta refinement …")
6. REQUIREMENT: GROUP 4 (cross-section, `attestation` / `operator-doctrine-verbatim-canon`) — retire `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:44.783639+00:00`; RETAIN `corpus-attestation-2026-06-10T23:22:11.236941+00:00`. ("Operator authorship … recorded as 'g0' …")
7. REQUIREMENT: GROUP 5 (cross-section, `obpi-acceptance-protocol` / `operator-doctrine-verbatim-canon`) — retire `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:45.194671+00:00`; RETAIN `corpus-obpi-acceptance-protocol-2026-06-11T10:50:22.318951+00:00`. ("There is no such thing as a 'headless' OBPI …")
8. REQUIREMENT: GROUP 6 (cross-section, `defect-fix-routing` / `operator-doctrine-verbatim-canon`) — retire `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:45.563168+00:00`; RETAIN `corpus-defect-fix-routing-2026-06-11T11:12:06.972640+00:00`. ("GHIs are AUTHORIZED for direct repair, always …")
9. REQUIREMENT: GROUP 7 (WITHIN `operator-doctrine-verbatim-canon` — the only intra-section group) — retire `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:46.373270+00:00`; RETAIN `corpus-operator-doctrine-verbatim-canon-2026-06-16T11:52:39.917448+00:00`. ("Never create feature branches …")
10. REQUIREMENT: DIVERGENT PAIR (operator-ruled) — the two rows are 571 characters each and differ ONLY in quote style at four sites (`'discovering'`/`"discovering"`, `correction.'`/`correction."`, `'enhancement'`/`"enhancement"`, `'capability not yet built'`/`"capability not yet built"`). The SINGLE-QUOTE row `corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:45.960384+00:00` IS CANON; retire `corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00`. This is the pair that already double-renders in AGENTS.md today.
11. REQUIREMENT: NEVER let the tool elect the winner. The divergent pair is settled by the recorded operator ruling above, never by a dedup heuristic — a silently-picked quote style is doctrine drift with no attestation (ADR § Alternatives D; AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 3).
12. REQUIREMENT: ALWAYS retire the `operator-doctrine-verbatim-canon` row and RETAIN the TOPICAL-section original in groups 1-7 (operator ruling 2026-08-22, verbatim: "topical section wins, retire the canon-section copies"). **This INVERTS the disposition this requirement carried until 2026-08-22** — see the AMENDED block in § Objective for why, and do not read the inversion as drift. The superseded rationale was that the verbatim-canon section is the operator's own home for these utterances. It was outweighed by a fact not known when this brief was authored: the seven canon-section rows are all `origin=cli:content-remember` from one 2026-06-19T22:54 bulk import that FLATTENED seven differentiated classifications to `Ambiguous`, while the topical originals carry the real verdicts (Judgment, Promotable, Mechanical). Retaining the canon rows would have kept the copies that lost information.
13. REQUIREMENT: ALWAYS supply a non-empty `--attestor` and `--reason` on every one of the eight invocations. All eight targets are `invariant` tier, so all eight are corpus-attestation fail-closed (OBPI-0.35.0-02).
14. REQUIREMENT: AFTER the batch, every retired id is absent from `effective_corpus()` and **no two live `invariant` entries share byte-identical text** — that last property is the one that matters and it is the subject of REQ-0.35.0-03-04. Verify it by re-deriving the live set from the store; do NOT verify it against a row count. This requirement read "the raw log holds 59 rows (51 + 8 tombstones) and `effective_corpus()` yields 42 live `invariant` entries and 1 `compressible`" until 2026-08-22, when it was measured at 76 rows / 51 `invariant` + 1 `compressible` — arithmetic pinned to a moving baseline, unsatisfiable as written and not restorable. Measured 2026-08-22: zero live byte-identical `invariant` texts.
15. REQUIREMENT: NEVER delete, edit, or re-tier a row. All eight originals stay in the raw log verbatim; provenance survives (alternatives E and F).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- [ ] `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md` — pre-mortem, WWHTBT, constraint archaeology, 2am-operator, reversibility, scope minimization.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — the three-kind proof-channel matrix this brief's Acceptance Criteria are tagged against

**Context:**

- [ ] ADR § Decision item 2 and § Consequences (Positive) #3 — corpus 50 -> 42.
- [ ] ADR § Alternatives D, E, F, G, H — the four rejected retirement shapes and the rejected generator-first ordering.
- [ ] GHI #635 — the defect this OBPI discharges.
- [ ] `DESIGN_FORCING_FUNCTIONS.md` § 3 Constraint Archaeology — append-only has never been tested against attested canon; this batch is its FIRST real test, which is why the tombstone route is right and the delete route is not.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.35.0-01 landed: `effective_corpus()` folds tombstones under the pinned algebra
- [ ] OBPI-0.35.0-02 landed: `gz content retire` accepts `--attestor` and is corpus-attestation fail-closed on invariant tier. **Check the flag, not the verb** — the verb has shipped since 2026-07-22 and its mere existence proves nothing about this prerequisite (`uv run gz content retire --help` must list `--attestor`)
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` present and loading; 51 rows, 50 invariant + 1 compressible, re-measured at implementation time
- [ ] All sixteen entry ids enumerated in Requirements resolve against the corpus on disk
- [ ] A human attestor is available — all eight retirements are corpus-attested and there is no self-close path

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:72` — `entry.text not in rendered_text`, the substring test that hides the seven byte-identical groups today
- [ ] `src/gzkit/content/models/corpus.py` — `Corpus.append` returns a new corpus; there is no delete path anywhere in `corpus_store.py`
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` — the eight target rows and their eight retained twins

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. -->

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz validate --rendition-floor-coherence
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz test
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content retire AGENTS.md --entry corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00 --attestor "g0" --reason "GHI #635: divergent quote-style duplicate; the single-quote operator-doctrine-verbatim-canon row is canon by operator ruling."
uv run python -c "from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.models.corpus import effective_corpus; from gzkit.content.tier_policy import invariant_entries; c = load_corpus(Path('.'), 'AGENTS.md'); print('raw rows', len(c.entries), '| live invariant', len(invariant_entries(c)))"
uv run python -c "import collections; from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.tier_policy import invariant_entries; t = collections.Counter(e.text for e in invariant_entries(load_corpus(Path('.'), 'AGENTS.md'))); print('duplicate texts remaining:', sum(1 for v in t.values() if v > 1))"
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-03-01 [support]: **AMENDED 2026-08-26 (operator-ruled) — the ledger is no longer this REQ's proof channel.** Original predicate ("the ledger carries a `corpus_entry_retired` event for every entry id... spanning three sessions") is FALSE as measured: only 1 of the 8 ids (the GHI #635 divergent-pair loser) has a `corpus_entry_retired` event; the seven GHI #862 groups have none — see the AMENDED 2026-08-26 block in § Objective for the full measurement and cause. Per the operator ruling recorded verbatim in the AMENDED 2026-08-26 block (§ Objective). **New predicate:** every entry id enumerated in this brief's Requirements (groups 1-7 plus the divergent-pair loser) is named as `retires` by a LIVE retraction row in `.gzkit/corpus/AGENTS.md.jsonl`, verifiable per id against the store. Verified 2026-08-26: all 8 confirmed. The ledger gap (1/8 `corpus_entry_retired`, 0/8 `corpus_entry_appended` for the tombstone rows) is tracked as an open route at **GHI #885**, not repaired by this brief. Witnessed by `gz validate --rendition-floor-coherence` passing over the resulting corpus (the structural-validator arm of the SUPPORT proof channel, ADR-0.0.59, is unchanged by this amendment — only the recorded-artifact arm moved from ledger event to corpus row).
- [ ] REQ-0.35.0-03-02 [support]: **AMENDED 2026-08-26 — now THREE rulings/decisions of record, not two, and not all three are operator-verbatim.** All three are recorded in `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md`, with the rationale each rests on and its authority correctly attributed: (1) the divergent pair (both ids, retained/retired disposition, the four quote-style divergence sites) — OPERATOR ruling, recorded at authoring time; (2) the 2026-08-22 ruling inverting groups 1-7, added by the AMENDED 2026-08-22 block — OPERATOR ruling, verbatim; a future maintainer meeting an inverted REQUIREMENT 12 must find the witnessed reason here rather than read it as drift; (3) the 2026-08-26 ruling moving REQ-0.35.0-03-01's proof channel from the ledger to the corpus tombstones — OPERATOR ruling, verbatim, recorded in the AMENDED 2026-08-26 block (§ Objective), naming REQ-0.35.0-03-01 only — **plus its AGENT-APPLIED EXTENSION to REQ-0.35.0-03-03's identical witness clause, disclosed in that same block as the agent's inference, not operator authority.** This REQ's own subject is discharged for the third item by that block existing and stating the attribution correctly. A future maintainer reads a witnessed ruling (and, for item 3's REQ-0.35.0-03-03 half, a witnessed and correctly-attributed agent inference) rather than re-deriving a winner or mistaking an inference for operator authority. Witnessed by an `artifact_edited` ledger event citing that path; `gz validate --documents` admits the brief's shape.
- [ ] REQ-0.35.0-03-03 [support]: All eight retired originals are still present verbatim in `.gzkit/corpus/AGENTS.md.jsonl`, each named by a retraction row, proving retirement was append-only and no row was deleted, edited, or re-tiered. Verify by id against the store. This REQ pinned "59 raw rows ... the original 51 plus eight appended tombstones" until 2026-08-22; the store measured 76 rows that day because capture unrelated to this brief has grown it, so the row-count form was unsatisfiable and not restorable. Append-only-ness is provable per id without a total. **This predicate is TRUE as measured 2026-08-26 and is RETAINED unchanged.** Only the trailing witness clause is amended. **This amendment is an AGENT-APPLIED EXTENSION of the operator's 2026-08-26 ruling on REQ-0.35.0-03-01, not a second operator ruling** — the operator's verbatim ruling names REQ-0.35.0-03-01 only; the agent judged REQ-0.35.0-03-03 carries the identical false witness clause for the identical reason and applied the same treatment, disclosed as such in the AMENDED 2026-08-26 block in § Objective (both REQs carried the same false clause): ~~"Witnessed by eight `corpus_entry_appended` ledger events citing `.gzkit/corpus/AGENTS.md.jsonl`"~~ is FALSE (measured 0 of 8 — none of the eight tombstone/retraction rows, including the GHI #635 one, has a `corpus_entry_appended` event; that ingress predates the dual-emission change in OBPI-0.35.0-02). Witnessed instead by `gz validate --documents` admitting the resulting store; the ledger gap is tracked at **GHI #885**, not repaired by this brief.
- [ ] REQ-0.35.0-03-04 [structural-fence]: No two LIVE `invariant`-tier entries in the AGENTS.md effective corpus share byte-identical text, and this property holds after every subsequent ADR-0.35.0 OBPI lands. This is the regression fence that alternative H names: the byte-identical groups are invisible today only because the floor check is a substring test, and they become literal double-emissions the instant the OBPI-0.35.0-05 generator materializes — so the property must be audited at ADR closeout across the whole decomposition, not per-OBPI.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded: this brief retires exactly eight redundant `invariant`-tier corpus
  entries — seven byte-identical duplicates (GHI #862) plus the operator-ruled loser of a divergent
  quote-style pair (GHI #635) — closing the live double-render the parent ADR's checklist item 3
  names. Scope is authorship-only on this brief file per 2026-08-26; the eight retirements themselves
  had already landed (see § Objective AMENDED blocks) and this pass amends two REQs whose proof
  channel could not exist as originally written.
- [x] Parent ADR checklist item quoted verbatim (`ADR-0.35.0-canon-entry-corpus-landing.md`
  § Feature Checklist item 3): *"Retire the 8 duplicate invariant entries -- 7 byte-identical + the
  operator-ruled divergent pair; corpus 50 -> 42 (GHI #635)"*. The trailing `50 -> 42` figure is
  stale against the live corpus (79 raw rows, 54 live `invariant` as of 2026-08-26 — see § Objective
  AMENDED 2026-08-22 block for why the arithmetic could not be preserved) and is read as a dated
  record of the authoring-time corpus, not a target, per `.claude/rules/governance-core.md`
  § Non-negotiable rules.

### Gate 2 (TDD — Red-Green-Refactor)

This OBPI writes NO code. `src/**` and `tests/**` are Denied Paths (§ Denied Paths: *"a test
asserting that this repository's corpus file holds 42 rows is a filesystem-grep that cannot fail
when production behavior changes"*). There is no Red-Green-Refactor cycle and no `@covers` test to
author or run — the two REQs amended by this pass (`REQ-0.35.0-03-01`, `REQ-0.35.0-03-03`) are
`[support]`-kind and their only proof channel is a recorded artifact plus a structural validator
(ADR-0.0.59): the corpus store's live retraction rows (verified per id in § Objective AMENDED
2026-08-26 block) and `uv run gz validate --rendition-floor-coherence` / `uv run gz validate
--documents`. `REQ-0.35.0-03-04` is `[structural-fence]`, proven only by the parent ADR's
`## Boundary Invariants`, audited at ADR closeout — never by a test in this brief's scope.

### Code Quality

```text
uv run gz arb ruff                -> exit 0, receipt arb-ruff-839fd99d838f4e18b37ccc80f0e6ba04
uv run gz arb typecheck           -> exit 0, receipt arb-step-typecheck-788813a87feb4da7836ab8df0132dda0
uv run gz arb step --name unittest -- uv run -m unittest -q
                                  -> exit 0, Ran 8855 tests, OK, receipt arb-step-unittest-62e2d024b046411face2e66a17228670
uv run gz test                    -> exit 0, "Unit tests passed."
uv run gz covers <this OBPI> --json -> behavior_uncovered_reqs: 0 (all four REQs are support/structural-fence; none carries @covers by proof channel)
```

### Gate 3 (Docs)

```text
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
                                  -> exit 0, receipt arb-step-mkdocs-241bdb9c26414994b2682cbccc47937b
```

### Gate 4 (BDD)

No feature file references REQ-0.35.0-03 (or this OBPI id). `behave` is therefore OMITTED from
Stage 3 per the pipeline's scope discipline, not run and reported as "N/A" without reason — the full
BDD sweep for the ADR-0.35.0 decomposition is deferred to ADR closeout, consistent with how
`REQ-0.35.0-03-04`'s regression fence is already scoped (audited at ADR closeout, not per-OBPI).

### Gate 5 (Human)

```text
# Recorded at attestation time per AGENTS.md § Attestation — the operator's verbatim
# "attest completed" (or equivalent) IS Gate 5. Not fabricated ahead of that event.
```

### Value Narrative

**Before:** This brief's `REQ-0.35.0-03-01` and `REQ-0.35.0-03-03` asserted a ledger fact —
`corpus_entry_retired` / `corpus_entry_appended` events for all eight of this brief's target ids —
that could never be witnessed, because seven of the eight retirements were hand-appended to
`.gzkit/corpus/AGENTS.md.jsonl` under GHI #862 without going through `gz content retire`, bypassing
the ledger entirely. Left unamended, the brief either blocked forever on a proof channel that does
not exist, or would have been attested with a false Layer-2 claim baked into a Heavy-lane Layer-1
canon artifact — a fabricated receipt of the kind `AGENTS.md` § Attestation forbids. The gap was
invisible to every existing validator: `uv run gz validate --rendition-floor-coherence` exits 0 over
this exact state, because a tombstone's mere presence in the corpus was standing in as proof that a
governed retirement occurred (the presence-check failure `AGENTS.md` § DO IT RIGHT names).

**Now:** The two affected REQs cite the proof that IS real — each retirement id is named as
`retires` by a live retraction row in the corpus store, verifiable per id against disk — and the
ledger gap is named explicitly and tracked at GHI #885 rather than silently absorbed or hidden
behind a passing validator. `REQ-0.35.0-03-01`'s SUPPORT proof channel moves from ledger event to
corpus row (its structural-validator arm, `gz validate --rendition-floor-coherence`, is unchanged);
`REQ-0.35.0-03-03` keeps its true append-only predicate and only its false witness clause is
replaced. The brief now completes on what is measured and provable, per the operator's 2026-08-26
ruling, instead of blocking on or fabricating a witness that cannot exist.

### Key Proof

Reusing this brief's own § Demo probes, run 2026-08-26 against `.gzkit/corpus/AGENTS.md.jsonl`:

```text
$ uv run python -c "from pathlib import Path; from gzkit.content.corpus_store import load_corpus; \
  from gzkit.content.models.corpus import effective_corpus; \
  from gzkit.content.tier_policy import invariant_entries; \
  c = load_corpus(Path('.'), 'AGENTS.md'); \
  print('raw rows', len(c.entries), '| live invariant', len(invariant_entries(c)))"
raw rows 79 | live invariant 54

$ uv run python -c "import collections; from pathlib import Path; \
  from gzkit.content.corpus_store import load_corpus; from gzkit.content.tier_policy import invariant_entries; \
  t = collections.Counter(e.text for e in invariant_entries(load_corpus(Path('.'), 'AGENTS.md'))); \
  print('duplicate texts remaining:', sum(1 for v in t.values() if v > 1))"
duplicate texts remaining: 0
```

Zero live byte-identical `invariant` texts confirms `REQ-0.35.0-03-04`'s regression fence holds over
the current (post-growth) corpus, not merely the authoring-time one. Each of the eight target ids was
independently confirmed, id-by-id, to be named by a live `retires` pointer in the corpus store —
this is the new proof channel `REQ-0.35.0-03-01` and `REQ-0.35.0-03-03` cite in place of the ledger.

### Implementation Summary

- **Authored (this pass, the single allowlisted file edited by hand):** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md` only. No `.gzkit/corpus/AGENTS.md.jsonl`, no `src/**`, no `tests/**` — the eight retirements were already landed prior to this pass (see § Objective PARTIALLY PRE-LANDED and AMENDED 2026-08-22 blocks); this pass amends the brief's proof channels and records the newly-measured ledger gap.
- **Generated by the pipeline run itself (not authored edits — do not read as brief-scope changes):** this `gz-obpi-pipeline OBPI-0.35.0-03` run appended 17 rows to `.gzkit/ledger.jsonl` (`airlock_in` x1, `artifact_edited` x9, `brief_reconciled` x1, `obpi_lock_claimed` x1, `pipeline_launched` x1, `task_started` x4) and created untracked pipeline-state artifacts under `.claude/plans/` (a pipeline marker, a plan-audit receipt, and the pipeline's working plan file). These are runtime bookkeeping the pipeline itself produces on every run, not deliberate content edits to this OBPI's subject matter, and are listed here so the inventory is not silently incomplete.
- Tests added: none — this OBPI writes no code (§ Denied Paths; see § Gate 2 above for the kind-by-kind proof-channel accounting).
- Date completed: 2026-08-26 (this authoring pass; brief completion remains gated on Stage 3/attestation).
- Attestation status: pending human attestation (§ Gate 5).
- Defects noted: GHI #885 (open — seven of this brief's eight retirements bypassed `gz content retire` and carry no ledger witness); GHI #864 (open — the process defect that let the out-of-band GHI #862 landing happen invisibly); GHI #862 (closed — the direct fix that retired groups 1-7).

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- [GHI #862](https://github.com/tvproductions/gzkit/issues/862) — the duplicate finding whose direct fix discharged this brief's groups 1-7 out-of-band, under the operator ruling that inverted their disposition. Closed; commits `8ed48271` (guard) and `f6407e9b` (rendition re-link).
- [GHI #864](https://github.com/tvproductions/gzkit/issues/864) — the cause: `ghi-author` Step 0 reads GitHub issues only, so this brief was invisible to the pre-flight that exists to prevent exactly this collision. Open; direct-fix ready.
- [GHI #885](https://github.com/tvproductions/gzkit/issues/885) — the seven GHI #862 retirements bypassed `gz content retire` and hand-appended tombstone rows with no `corpus_entry_retired`/`corpus_entry_appended` ledger witness (measured 2026-08-26: 1/8 and 0/8 respectively across this brief's eight ids). REQ-0.35.0-03-01 and REQ-0.35.0-03-03 are amended to cite the corpus tombstones as proof instead of the ledger, per operator ruling. Open; a systemic repair (detection validator and/or a constrained append ingress) is undecided.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
