---
id: OBPI-0.35.0-02-content-withdraw-verb
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 2
lane: Heavy
sensitivity: security
status: Completed
allowlist:
- src/gzkit/commands/content/retire.py
- src/gzkit/commands/content/__init__.py
- src/gzkit/cli/**
- src/gzkit/ledger_events.py
- src/gzkit/events.py
- src/gzkit/schemas/ledger.json
- src/gzkit/schemas/corpus_entry.json
- src/gzkit/commands/obpi_complete_adversarial.py
- tests/test_adversarial_validation_gate.py
- tests/commands/test_content_retire.py
- tests/test_schemas.py
- features/content_retire.feature
- features/steps/**
- docs/user/manpages/content.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-02-content-withdraw-verb.md
reqs:
- REQ-0.35.0-02-01
- REQ-0.35.0-02-02
- REQ-0.35.0-02-03
- REQ-0.35.0-02-04
- REQ-0.35.0-02-05
- REQ-0.35.0-02-06
- REQ-0.35.0-02-07
- REQ-0.35.0-02-08
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz cli audit
- uv run gz validate --cli-alignment
- uv run gz validate --req-kind-discipline
- uv run mkdocs build --strict
req_atomic:
  # Subdivided instead (seq=02 minted): REQ-01 took four distinct labor rounds — the
  # initial tier gate, the U+200B predicate, the one-hop tombstone lookup, then the
  # hop-independent liveness delta. REQ-05 took three — initial recovery prose, the
  # incomplete retry, then asserting the retry's EFFECT rather than its parse.
  - REQ-0.35.0-02-02  # one guard, one shape: whitespace/invisible refusal on both flags
  - REQ-0.35.0-02-03  # one branch: compressible passes without an attestor
  - REQ-0.35.0-02-04  # one assertion set over one fold call; no labor below it
  - REQ-0.35.0-02-06  # parser option-set shape; a single registration edit
  - REQ-0.35.0-02-07  # one emission site: both events, one ordering, one payload
  - REQ-0.35.0-02-08  # one manpage section; SUPPORT REQ with no code labor
tasks:
  - TASK-0.35.0-02-01-01
  - TASK-0.35.0-02-02-01
  - TASK-0.35.0-02-03-01
  - TASK-0.35.0-02-04-01
  - TASK-0.35.0-02-05-01
  - TASK-0.35.0-02-06-01
  - TASK-0.35.0-02-07-01
  - TASK-0.35.0-02-08-01
  - TASK-0.35.0-02-01-02
  - TASK-0.35.0-02-05-02
---

# OBPI-0.35.0-02-content-withdraw-verb: Content Withdraw Verb

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #2 - "`gz content retire` — corpus-attestation extension of the shipped verb: fail-closed on invariant tier (`--attestor` / `--reason` refused when empty). Amended 2026-08-07 from the `content withdraw` name; see § Decision item 2."

**Status:** Completed

## Objective

Extend the SHIPPED verb `gz content retire` to take `<surface> --entry <id> --attestor <name> --reason <text>` — the operator surface that appends an OBPI-0.35.0-01 tombstone. Retirement is already keyed to the entry id and never to the entry text; what this OBPI adds is the corpus-attestation half: retiring an `invariant`-tier entry becomes fail-closed on empty `--attestor` or `--reason`, mirroring `gz obpi repudiate` (ADR-0.0.71).

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

> **AMENDED 2026-08-25 (operator-ruled): REQ-0.35.0-02-04's "verbatim" is SCOPED to the
> entry's fields, not to its bytes.** Operator ruling, verbatim: *"amend REQ-04 under
> attestation, and file the GHI"*. The unqualified claim was false as written, and the
> requirement's own two covering tests had split over it —
> `test_invariant_retirement_grows_raw_log_but_hides_from_effective_corpus` asserts
> `line_before == line_after`, while
> `test_a_legacy_format_row_is_normalized_not_preserved_byte_for_byte` asserts
> `before_line != after_line`. One covering test was asserting the requirement's negation,
> which the tier-1 adversary named at round 3 (2026-08-25).
>
> **Why the encoding moves.** `corpus_store.append_entry`
> (`src/gzkit/content/corpus_store.py:36-45`) reloads the store and rewrites the ENTIRE file
> through `Corpus.dumps()`, so a row persisted in an older shape (reordered keys, explicit
> nulls, spaces after separators) is re-encoded on the next append. Measured 2026-08-25:
> `RAW_ROW_EQUAL=False` on a legacy-format row. For rows this codebase wrote the round-trip
> is byte-stable, which is why the byte-identity test is not circular for its own case.
>
> **Why the requirement moved rather than the code.** Two repairs were available: amend the
> requirement, or change persistence to append without reserializing. The second is
> `corpus_store.py`, a **Denied Path** for this OBPI — and that same function now carries two
> further open defects (GHI #875 persist-before-validate, GHI #880 concurrent appends silently
> drop rows), whose repair ordering is an unresolved operator question. Widening scope into it
> here would land a third uncoordinated pass over six lines.
>
> **What the requirement protects is unchanged**, and is what both tests now assert
> consistently: retirement is append-only (the row count grows, never shrinks), the target
> leaves the `effective_corpus()` projection an auditor or renderer actually reads, and the
> target's CONTENT survives whole. Byte-encoding stability is a property of the serializer,
> not of retirement — naming it in the requirement asserted a guarantee retirement never made.
>
> **Scoped to the single-writer path.** The growth claim holds for one writer at a time. Under
> concurrent writers the raw log can LOSE a row `append_entry` reported as appended
> (reproduced 20/20, GHI #880) — a store-level defect routed out of this brief, not a property
> this requirement can promise.

> **AMENDED 2026-08-25 (operator-ruled): REQ-0.35.0-02-01's Given clause is WIDENED
> from the single empty-attestor case to the general name-plausibility floor
> `_is_named` actually implements.** REQ-01 as originally written named only
> `--attestor ""`; `_is_named` rejects a broader class — empty, whitespace-only,
> punctuation/digit-only, and any value that renders at zero advance width (Unicode
> `Default_Ignorable_Code_Point`, e.g. a Hangul filler). Two independent reviewers
> found the covering tests asserting a subject neither REQ-01 nor REQ-02 literally
> named: three new tests, plus two pre-existing ones —
> `test_an_invisible_attestor_is_not_a_named_human` (U+200B ZERO WIDTH SPACE) and
> `test_punctuation_and_digits_do_not_answer_who_attested` (`.`, `7`, a lone
> combining mark, a punctuation run) — all exercise `--attestor` values that are
> non-empty, General_Category=Lo or punctuation/digit, and `str.isspace()` False,
> none of which REQ-01's `""` or REQ-02's whitespace-only Given clause names.
>
> **Why the requirement moved rather than a new REQ.** A tier-1 cross-vendor
> adversary surfaced the underlying bypass at round 3 — an invisible or
> not-a-name `--attestor` retiring invariant-tier canon while REQ-01/02 as written
> covered only the two narrowest cases the guard was first built to reject.
> Operator ruled (2026-08-25) the repair is to widen REQ-01's Given clause to the
> plausibility floor it should always have named, not to mint a ninth REQ for what
> is one gate with one guarantee — REQ count stays 8. REQ-02 (whitespace-only) is
> unchanged and untouched.

> **AMENDED 2026-08-25 (operator-ruled): REQ-0.35.0-02-03's Given clause is REKEYED
> from the target's TIER to the invariant-liveness DELTA.** REQ-03 promised exit 0
> whenever `--entry` named a `compressible`-tier entry with no `--attestor`. That is
> false as written, and the tier-1 cross-vendor adversary demonstrated both halves at
> round 5: a `compressible` TOMBSTONE whose retirement revived invariant canon was
> observed exiting 1 (`TOMBSTONE_TIER=compressible`, `SECOND_EXIT_NO_ATTESTOR=1`),
> while retiring a tombstone over `compressible` content exited 0 printing *"The
> invariant floor is unchanged"*.
>
> This is the THIRD REQ on this brief written against a surface property while the
> code gates on `_floor_liveness_delta` — REQ-01 (empty attestor) and REQ-04 (verbatim
> bytes) were amended earlier the same day. The brief was authored before the delta
> fold existed, so each REQ encoded the model of its moment; rekeying the third
> completes the migration rather than patching an outlier. REQ count stays 8 and no
> REQ is added, removed, or renumbered.
>
> The same round retired the CATEGORICAL claim that retiring a tombstone grows the
> floor: it grows the floor ONLY when the revived entry is invariant-tier. Every prose
> home now states that condition.
>

> **AMENDED 2026-08-25 (operator-ruled): REQ-0.35.0-02-07 now requires the LIVENESS
> DELTA on the retirement event, not merely the retired row's tier.** The attestor gate
> authorizes on `floor_added | floor_removed`; the event recorded `target.tier`. The
> tier-1 cross-vendor adversary measured the consequence at round 6: retiring a
> compressible tombstone over an invariant entry printed *"The invariant floor GREW"*
> while the event carried `tier='compressible'`, and that event with `attestor=''`
> passed `validate_ledger` with zero errors — so Layer 2 could not tell an unaudited
> floor revival from routine compressible retirement, and a regression in the tombstone
> gate would have stayed ledger-valid.
>
> This is the fourth REQ on this brief rekeyed from a surface property to the delta
> (REQ-01, REQ-03, REQ-04 preceded it). `floor_direction` and `floor_moved_ids` are
> derived from the SAME sets the gate reads, so the witness and the gate cannot
> disagree; both stay OUT of the schema's `required` because the ledger is append-only
> and the ~300 committed rows of GHI #877 can never grow the keys. Present values are
> constrained to the four states by schema enum (round 7). ENFORCEMENT — refusing an
> event whose direction moved the floor with no attestor — needs a conditional rule the
> validator does not support, and is routed to GHI #882.
>

> **This objective was AMENDED 2026-08-07 (operator-ruled) from "ship the new verb
> `content withdraw`."** The verb already shipped under GHI #635; extending it in
> place was ruled over renaming it. Parent ADR § Decision item 2 and § Checklist
> item 2 carry the matching amendment. **This brief's `id` and filename still read
> `content-withdraw-verb`** — renaming an OBPI id is a semver-identifier migration
> touching the ADR's 1:1 checklist mapping and every ledger reference, so it is
> deliberately NOT done here. The id is a label; § Objective is the contract.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 02 depends on 01 (the tombstone fields and the fold must exist before a verb can append one) and is the prerequisite for 03. 01 -> 02 -> 03 is the minimum shippable slice and alone discharges GHI #635.

<!-- gz-validate-skip: command-shape -->
> **PARTIALLY PRE-LANDED, AND THE VERB NAME COLLIDES — read before implementing
> (reconciled 2026-08-07).** A retirement verb already ships. It landed ahead of
> this chain as the GHI #635 direct fix (`852e8a25`) on 2026-07-22, ONE DAY after
> this brief was authored, and it is named **`gz content retire`**
> (`src/gzkit/commands/content/retire.py`) — not the `content withdraw` this brief
> was written against. Implementing
> this brief as written would stand up a SECOND verb doing one job. Measured at
> HEAD `6863f0555`:
>
> | Requirement | Target | Observed in `retire.py` | State |
> |-------------|--------|--------------------------|-------|
> | 1 — never accept a `--text` selector | id-keyed only | `--entry <id>` keyed; no text selector | **landed** |
> | 2 — corpus attestation fail-closed on `invariant` tier | empty `--attestor`/`--reason` exits non-zero, writes nothing | **no `--attestor` parameter at all**; `reason` is not empty-checked (`retire.py:31`) | **open** |
> | 3 — never require corpus attestation for `compressible` | tier discrimination | **no tier discrimination anywhere** | **open** |
> | 4 — always append, never shrink | append-only | appends a retraction row via `corpus_store.append_entry` (`retire.py:74`) | **landed** |
> | 5 — fail closed on unknown / already-retired / absent store | exit non-zero, write nothing | exit 1 on both unknown (`:47`) and already-retired (`:55`) | **landed** |
> | 6 — emit BOTH `corpus_entry_appended` and `corpus_entry_retired` | two events | only `corpus_entry_retired_event` (`:80`); `append_entry` emits none | **half open** |
> | 7 — three-part recovery prose on every fail-closed exit | what failed, cited rule, runnable next step | messages name what failed and that nothing was written, but carry **no runnable next step and no rule citation** | **open** |
>
> **Allowlist drift the reconciler cannot see.** This brief's allowlist names
> `src/gzkit/governance/events.py` as the home of the `corpus_entry_retired` ledger
> event. The shipped event is `corpus_entry_retired_event` in
> **`src/gzkit/ledger_events.py`**; `governance/events.py` carries no corpus-retirement
> helper (its only `corpus` hits are `corpus_fingerprint`). `gz obpi brief-drift`
> reports allowlist=0 because the named file EXISTS — existence is not
> relevance (GHI #581).
>
> **DECISION RULED 2026-08-07 (operator): EXTEND `retire` IN PLACE.** The
> alternative — renaming the shipped verb to `withdraw`, a Heavy CLI contract change
> per `.claude/rules/cli.md` § Heavy Lane Trigger — was declined. Parent ADR
> § Decision item 2, § Checklist item 2, its Fidelity Assertion row, and the
> § Decomposition Scorecard's Interface scoring basis all now read `retire`; the
> § Q&A Transcript keeps `withdraw` as history under a SUPERSEDED banner (the
> ADR-0.0.74 / GHI #640 convention). The Interface dimension score is UNCHANGED at 2.
>
> **How the collision stayed invisible, recorded so the next one does not.** The
> parent ADR's Fidelity Assertion invoked a command that did not exist, and
> `gz validate --cli-alignment` could not say so because the row carried
> `<!-- gz-validate-skip: command-shape -->` — the marker that lets a planned verb be
> documented is also what hid it. With the amendment landed, the marker came OFF
> § Decision item 2 and § Checklist item 2, and the validator immediately caught
> three residual references (exit 1, *"'withdraw' is not a registered subcommand"*).
> Those were reworded rather than re-marked: the marker asserts *planned-but-unlanded*,
> and `withdraw` is no longer planned, so marking it would have stated something false.
>
> Note: `uv run gz obpi brief-drift OBPI-0.35.0-02-content-withdraw-verb` reports
> **clean across all five dimensions**. This note is authored, never computed.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/commands/content/retire.py` — **EXTEND** the shipped module (`content_retire_cmd`): add `--attestor`, the empty-check, tier discrimination, the second ledger event, and recovery prose
- `src/gzkit/commands/content/__init__.py` — command export (already present; touch only if the signature changes)
- `src/gzkit/cli/**` — parser registration for the NEW `--attestor` flag on the existing `retire` subcommand only
- `src/gzkit/ledger_events.py` — the event FACTORY; extend its payload with tier + attestor
- `src/gzkit/events.py` — the event TYPE (`CorpusEntryRetiredEvent`, `extra="forbid"`); declare `tier` and `attestor` as fields
- `src/gzkit/schemas/ledger.json` — the event SCHEMA (`corpus_entry_retired` `required`/`properties`); declare the two fields so they are validated
- `tests/test_schemas.py` — pins event-name -> model; round-trips the extended payload
- `src/gzkit/schemas/corpus_entry.json` — the `retires` field DESCRIPTION, the third home of the shrink-only claim this OBPI corrects in the runtime help; description text only, no shape change
- `src/gzkit/commands/obpi_complete_adversarial.py` — the Step-4b tier resolver; its cross-vendor proof read `argv[0]` only, which the operator-mandated plugin dispatch can never satisfy
- `tests/test_adversarial_validation_gate.py` — regression tests for the wrapper hop and the fail-open it must not reopen

> **ALLOWLIST AMENDED 2026-08-25 (operator-ruled) — a ledger event has THREE homes, and this
> brief named one.** REQ-07 requires the `corpus_entry_retired` payload to carry the tier and
> attestor. The original allowlist named only `ledger_events.py`, the factory. Measured at
> HEAD: `CorpusEntryRetiredEvent` (`src/gzkit/events.py:563`) is `extra="forbid"`, so
> `CorpusEntryRetiredEvent(..., tier="invariant", attestor="g0")` raises
> *"2 validation errors ... tier: Extra inputs are not permitted [extra_forbidden]"*, and
> `tests/test_schemas.py:302` maps the event name to that model.
>
> Riding the fields as UNDECLARED extras was measured and rejected: `validate_ledger` returns
> 0 errors on a row carrying undeclared `tier`/`attestor`, so they would ship unvalidated —
> a garbage tier or an empty attestor would pass the gate that exists to witness them.
>

> **ALLOWLIST AMENDED 2026-08-25 (operator-ruled) — the shrink-only claim has THREE homes, and
> this brief named two.** The tier-1 cross-vendor adversary's round-3 MEDIUM finding named the
> runtime `--help` text, which asserts *"Retirement only ever shrinks the floor"* and then, two
> clauses later, *"whose retirement revives its target and GROWS the floor"*. Measured 2026-08-25,
> that claim lives in THREE places, not one: `src/gzkit/commands/content/__init__.py:335` (the
> parser description), `src/gzkit/commands/content/retire.py` (the module docstring), and
> `src/gzkit/schemas/corpus_entry.json:53` (the `retires` field description — *"retirement only
> ever shrinks the floor and never invalidates a committed rendition"*). The original allowlist
> named the first two.
>
> The schema's owning briefs were checked before widening: OBPI-0.35.0-01 authored it and is
> **Completed** (terminal — a fresh defect against a shipped surface does not block), and
> OBPI-0.35.0-10 is **Draft** but its subject is the `classification` field, so it shares the file
> without owning this defect. Correcting two of three homes would leave the schema asserting the
> retired claim in the exact surface this OBPI is repairing elsewhere — coupled-surface
> coherence (AGENTS.md § DO IT RIGHT 1a). Description text only; no `properties`, `required`, or
> type change, so no corpus row is revalidated.
>

> **ALLOWLIST AMENDED 2026-08-26 (operator-ruled) — obeying the tier-1 dispatch directive made a
> tier-1 claim unclaimable.** `gz obpi complete` proves the Step-4b tier from the ARB receipt's
> `step.command[0]`, deliberately: *"a name can MENTION a vendor while describing its absence …
> an argv cannot mention; it ran."* But the operator's 2026-08-25 directive makes the Codex PLUGIN
> the ONLY permitted tier-1 surface and FORBIDS `codex exec`, and every plugin dispatch is argv
> `['node', '.../codex-companion.mjs', …]`. The resolver saw `node` and refused. Both rules landed
> the same day, so any OBPI obeying the directive could not claim the tier its own evidence proved.
>
> The resolver now walks past a bounded set of runtime wrappers (`node`, `python`, `uv`, `npx`, …)
> and STOPS at the first non-wrapper. Stopping is the load-bearing half: the adversary's PROMPT is
> also in argv and routinely names vendors, so a scan that kept walking would let a MENTIONED vendor
> satisfy the gate — reopening the exact fail-open the function exists to close. Four regression
> tests pin both directions, including a same-vendor helper fronted by `node` and a prompt naming
> Codex. Recorded as a conflict in its own right at GHI #884.
>
> This is the same class the § PARTIALLY PRE-LANDED banner already caught once and did not
> generalise: that banner found the allowlist naming `governance/events.py` for an event that
> lives in `ledger_events.py`, and recorded *"existence is not relevance (GHI #581)"*. It
> corrected the wrong FILE while leaving the wrong CARDINALITY — one home named where three
> exist. `gz obpi brief-drift` cannot see either, because it checks that named paths exist,
> never that the set is complete.
- `tests/commands/test_content_retire.py` — **EXTEND** the existing covering tests
- `features/content_retire.feature`, `features/steps/**` — Gate 4 scenarios **CREATE** (no retire feature exists)
- `docs/user/manpages/content.md` — the existing `### retire` section (line 127), updated for the new flags
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-02-content-withdraw-verb.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/content/models/corpus.py`, `src/gzkit/content/tier_policy.py` — schema and fold are OBPI-0.35.0-01 and are consumed read-only here
- `.gzkit/corpus/AGENTS.md.jsonl` — appending the eight production tombstones is OBPI-0.35.0-03; this OBPI writes only test-fixture corpora
- `src/gzkit/commands/content/commit.py`, `compose.py`, `remember.py` — sibling verbs are out of scope (`remember` is OBPI-0.35.0-08)
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. NEVER accept a `--text` selector. Retirement is per-entry-id, full stop. Six of the seven byte-identical duplicate groups address the same text to TWO DIFFERENT sections, so a text key silently elects a section winner — a question text identity cannot see (ADR § Alternatives D).
2. ALWAYS fail closed on the corpus attestation when a retirement MOVES invariant-tier liveness: an `--attestor` that answers no WHO — empty, whitespace-only, punctuation/digit-only, or rendering at zero advance width — MUST exit non-zero and write NOTHING: no corpus append, no ledger event, no partial file. Mirror `commit.py:47-54` and `gz obpi repudiate`. **AMENDED 2026-08-25 (operator-ruled): the original keyed on the TARGET being `invariant`-tier and bundled `--reason` into the attestation gate. The gate reads the before/after liveness DELTA, and `--reason` is validated separately by the ledger's stripped-non-empty rule — a name predicate on a reason blocked legitimate references like `#880`.**
3. NEVER require corpus attestation for a retirement that leaves invariant-tier liveness UNTOUCHED. The 0-Kelvin floor is what human attestation protects; retirement that does not move it is routine. **AMENDED 2026-08-25 (operator-ruled): the original keyed on the target's TIER and was false as written — a `compressible` TOMBSTONE whose retirement revives invariant canon DOES require an attestor, which a tier-1 adversary observed exiting 1 while this item promised exit 0.**
4. ALWAYS append. The verb appends a tombstone row through `corpus_store.append_entry`; the raw log's row count MUST grow and MUST NEVER shrink (alternatives E and F).
5. ALWAYS fail closed on an unknown `--entry` id, an already-retired target, or an absent corpus store — exit non-zero, write nothing.
6. ALWAYS emit BOTH ledger events on a successful retirement: `corpus_entry_appended` for the tombstone row (a tombstone IS an appended corpus row and goes through `corpus_store.append_entry` like any other), and a new `corpus_entry_retired` carrying the retired entry id, the tombstone row id, the surface, the tier, the attestor, the reason, AND the invariant-liveness delta the gate read — `floor_direction` and `floor_moved_ids` (**AMENDED 2026-08-25, operator-ruled**: `tier` alone is a PROXY for the gate's condition and cannot witness it). The pair is the SUPPORT proof channel for OBPI-0.35.0-03's batch.
7. ALWAYS emit three-part recovery prose on every fail-closed exit per `.claude/rules/guardrail-feedback-prose.md`: what failed, the cited rule, the runnable next step.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

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

- [ ] ADR § Decision item 2 — per-entry-id retirement and its recorded rationale.
- [ ] ADR § Alternatives D — text-keyed dedup, rejected on two counts; do not re-litigate.
- [ ] `.claude/rules/governance-core.md` § Withdraw vs Repudiate (ADR-0.0.71) — the verb-semantics precedent this surface mirrors.
- [ ] OBPI-0.35.0-01 — the fold this verb feeds; a tombstone this verb writes must satisfy Algebra 2, 3, and 7.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.35.0-01 landed: **check `effective_corpus()`, not `CorpusEntry.retires`** — the field has existed since 2026-07-22 (`corpus.py:100`) and proves nothing about this prerequisite. The gate is that `effective_corpus()` exists and folds; today only a flat `Corpus.retired_ids()` does (`corpus.py:129-131`), and REQ-0.35.0-02-04 below asserts against `effective_corpus()` directly
- [ ] `src/gzkit/commands/content/commit.py` exists (the corpus-attestation fail-closed pattern to mirror, lines 88-117; re-seated by GHI #821). Retirement is a canon change, so mirror the fail-closed arm, never the unchanged-canon exemption
- [ ] `src/gzkit/content/corpus_store.py::append_entry` exists
- [ ] `src/gzkit/governance/events.py` exists and carries the emit-helper pattern for corpus events
- [ ] `docs/user/manpages/content.md` exists

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/content/commit.py:39-55` — the canonical empty-attestation fail-closed shape
- [ ] `src/gzkit/commands/content/remember.py` — the sibling capture verb's argument and normalization conventions
- [ ] `uv run gz obpi repudiate --help` — the `--attestor` / `--reason` operator-gated shape being mirrored
- [ ] `tests/commands/test_content_commit.py` — the test style for a fail-closed content verb

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
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run gz validate --cli-alignment
uv run gz validate --req-kind-discipline
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content retire --help
uv run gz content retire AGENTS.md --entry corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00 --attestor "" --reason "probe"
uv run gz content retire AGENTS.md --entry does-not-exist --attestor "g0" --reason "probe"
```

> **OPERATOR RULING 2026-08-25 — the blocking arm is scoped to FLOOR-TIER REMOVAL.**
> The tier-1 adversary surfaced a canon conflict beneath this OBPI: `AGENTS.md` § Operator
> Doctrine says attestation on add/remove is *"RECORDED PROVENANCE, never a blocking gate —
> ADR-0.35.0 Decision 7 stands: capture must never be blocked"*, while this ADR's § Checklist
> item 2 specifies *"fail-closed on invariant tier"*. Both agree retirement is ATTESTED; they
> disagreed on whether that attestation BLOCKS.
>
> Ruled: *"never a blocking gate"* scopes to **CAPTURE** — the clause's own justification is
> *"capture must never be blocked"*. **REMOVAL of 0-Kelvin floor canon is the one blocking
> case**; compressible retirement records without blocking. The AGENTS.md bullet reads
> unscoped today and needs the carve-out stated, but `.gzkit/corpus/**` is a Denied Path
> here, so that amendment is routed separately rather than made in this brief.
>
> **The gate reads CONSEQUENCE, not target.** Keying on `target.tier` was a reproduced
> bypass: a tombstone is always written `compressible`, so retiring one walked through the
> gate while REVIVING invariant canon (Algebra 6) with no attestor recorded
> (`SECOND_EXIT_NO_ATTESTOR=0`, `ORIGINAL_EFFECTIVE_AFTER_SECOND=True`). `_floor_tier_at_risk`
> now asks what a retirement DOES to the floor.

> **TIER-1 ADVERSARIAL REVIEW — two rounds, both REFUTED; findings worked (2026-08-25).**
> Dispatched through OpenAI's Codex plugin for Claude Code. Round 1 reproduced five
> bypasses; round 2, run against the fixes, found five more (four high). Everything below
> is CLOSED with a mutation-verified test unless marked ROUTED.
>
> | Finding | Disposition |
> |---|---|
> | Zero-width space passed as an attestor (`.strip()` misses U+200B) | CLOSED — `_is_named` |
> | Retiring a tombstone revived floor canon with no attestor | CLOSED — liveness delta |
> | **Two-hop chain defeated the one-hop fix** | CLOSED — see below |
> | `--reason ""` reached the handler past argparse | CLOSED — handler-side guard |
> | Printed retries did not run; one did not recover | CLOSED — all six complete; effect asserted |
> | Dual-event test never asserted the events existed | CLOSED — counts + tier + attestor |
> | `.`, `7`, a combining mark, a lone surrogate passed as attestors | CLOSED — Unicode letter required |
> | **Success text claimed the floor shrank while it GREW** | CLOSED — direction reported; `floor_risk` true on revival |
> | REQ-04 byte test was circular (seeded via current serializer) | CLOSED — legacy-format counterexample pins real behavior |
> | Ledger partial write leaves canon moved, witness incomplete | **ROUTED — GHI #878** |
>
> **The gate reads CONSEQUENCE, not target, and not a hop count.** Keying on
> `target.tier` was the first bypass; keying on ONE tombstone edge was the second. Any
> finite hop count is the wrong shape of answer, so `_floor_liveness_delta` computes the
> invariant set before and after over the fold itself — hop-count independent, and it
> separates ADDED from REMOVED because those mean opposite things to a consumer.
>
> **Residuals, disclosed rather than asserted away:**
>
> - **Legacy-format rows normalize on append.** `corpus_store.append_entry` reserializes
>   the whole store, so a row persisted in an older shape is rewritten. REQ-04's byte
>   claim holds for rows this codebase wrote; the legacy case is pinned by a test that
>   asserts the entry SURVIVES whole while its encoding normalizes. `corpus_store.py` is
>   a Denied Path here.
> - **Schema and typed model disagree on an explicitly-empty `tier`.** Reachable only by
>   hand-writing such a row; no producer emits one. Related: GHI #877.
> - **Partial ledger write remains possible** — now REPORTED honestly (which witnesses
>   landed, that the retirement already happened, and the verification step) rather than
>   prevented. Prevention needs a transaction the append-only stores do not offer;
>   posture ruling routed to **GHI #878**.

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-02-01 [behavior]: Given the invocation `AGENTS.md --entry <invariant-tier id> --attestor <value that answers no WHO — empty, whitespace-only, punctuation/digit-only, or rendering at zero advance width> --reason "probe"` passed to gz content retire, when the command runs, then it exits non-zero, the corpus file is byte-unchanged, and NO ledger event is written — The corpus attestation is fail-closed on the invariant tier. **AMENDED 2026-08-25 (operator-ruled); the original Given clause named only `--attestor ""` — see § Objective.**
- [ ] REQ-0.35.0-02-02 [behavior]: Given the same invocation with a non-empty `--reason` but a whitespace-only `--attestor` (and the symmetric case), when the command runs, then it exits non-zero and writes nothing — whitespace is not attestation.
- [ ] REQ-0.35.0-02-03 [behavior]: Given `--entry` naming an entry whose retirement does NOT move invariant-tier liveness, and NO `--attestor`, when the command runs, then it exits 0 and appends the tombstone — The corpus attestation guards the 0-Kelvin floor, not routine retirement. **AMENDED 2026-08-25 (operator-ruled); the original Given clause keyed on the target being `compressible`-tier — see § Objective.** **AMENDED 2026-08-25 (operator-ruled): the original text read "NO `--attestor`/`--reason`"; the `--reason` half is struck.** `--reason` is load-bearing on two surfaces this REQ never named: it becomes the retraction row's `text`, and the `corpus_entry_retired` event's `reason`, which `src/gzkit/validate_pkg/ledger_check.py:111` guards with `min_length=1` over `value.strip()`. Measured 2026-08-25: an event with `reason: ""` returns *"Field 'reason' must be at least 1 non-whitespace characters"*; the same event with a reason returns nothing. So the literal REQ shipped an event `gz validate --ledger` rejects — invisible to these tests, which run in an isolated filesystem and never invoke the validator. The REQ's own stated rationale names the **corpus attestation**, which is the attestor; the `--reason` half was drafting drift, not intent. `--reason` stays required on every tier. Held by `test_every_retirement_emits_a_ledger_event_the_validator_accepts`, which runs the real validator over the real emitted event so the coupling has a witness rather than a memory of having checked it once.
- [ ] REQ-0.35.0-02-04 [behavior]: Given a valid invariant-tier retirement with a non-empty attestor and reason, when the command runs, then the raw corpus GROWS by exactly one row, the target entry is absent from `effective_corpus()`, and the target ENTRY survives in the raw log with every field intact — byte-for-byte for a row written by this codebase's serializer, and with its encoding normalized for a legacy-format row. **AMENDED 2026-08-25 (operator-ruled); the original read "the target row itself is still present verbatim in the raw log", unqualified — see § Objective for why the requirement moved rather than the code.**
- [ ] REQ-0.35.0-02-05 [behavior]: Given `--entry` naming an unknown id, an already-retired id, or a surface with no corpus store, when the command runs, then it exits non-zero, writes nothing, and its stderr carries all three recovery parts (what failed, the cited rule, a runnable next step).
- [ ] REQ-0.35.0-02-06 [behavior]: Given the registered parser, when gz content retire --help is invoked, then the option set contains `--entry` and contains NO text-valued selector — text-keyed retirement is unreachable from the CLI, not merely discouraged.
- [ ] REQ-0.35.0-02-07 [behavior]: Given a successful retirement, when the ledger is read, then a `corpus_entry_appended` event exists for the tombstone row AND a `corpus_entry_retired` event exists carrying the retired entry id, the tombstone row id, the surface, the tier, the attestor, the reason, AND the invariant-liveness delta the attestor gate read — `floor_direction` (one of `unchanged`, `shrank`, `grew`, `changed`) and the exact set of `floor_moved_ids`. **AMENDED 2026-08-25 (operator-ruled); the original listed only the retired row's tier, which is a PROXY for the gate's condition and cannot witness it — see § Objective.**
- [ ] REQ-0.35.0-02-08 [support]: `docs/user/manpages/content.md` carries a `retire` section (already present at line 127, EXTENDED here) documenting the per-entry-id contract and the invariant-tier corpus-attestation fail-close, — witnessed by an `artifact_edited` ledger event citing `docs/user/manpages/content.md` — and `gz validate --cli-alignment` resolves every gz content retire reference it prescribes.

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

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Step 4b — Independent Adversarial Validation

**Tier 1 (cross-vendor), two rounds.** Dispatched through OpenAI's Codex plugin for
Claude Code (`codex-companion.mjs adversarial-review`), refute-framed.

| Round | Verdict | Receipt |
|---|---|---|
| 1 | `REFUTED` | `arb-step-codexadversary-f9d3321edfc447558e1b5f69aa0ed4b7` (exit_status 0) |
| 2 (post-fix) | `REFUTED` — 5 further findings, 4 high | plugin job `review-mt8due3y-qx5t1i` |

Round 1 reproduced five bypasses, including an invariant-tier retirement authorized by a
zero-width space and a tombstone retirement that revived floor canon with no attestor.
Round 2, run against those fixes, found five more — most importantly that the one-hop
liveness lookup missed a two-hop `invariant -> tombstone -> tombstone` chain, and that the
success message claimed the floor SHRANK on a retirement that GREW it.

**All ten findings are worked; every fix carries a test verified to fail against the
pre-fix code.** Two findings whose repair lies in Denied Paths were routed out rather than
patched here: **GHI #877** (typed union rejects ~300 committed ledger rows) and
**GHI #878** (ledger partial write leaves canon moved with an incomplete witness). Both
are open with blocker comments naming the operator ruling each needs.

**Dispatch-surface defect found and fixed in flight.** The pipeline skill mandated the
Codex plugin for tier-1 and then, three paragraphs later, supplied a worked example using
the raw `codex exec` binary. The example won: the hand-rolled run wedged ~15 minutes at
0.07s CPU on an unredirected stdin, produced a 500KB undifferentiated blob, and was then
refused outright by an upstream cyber filter. The plugin path, on identical work, streamed
structured findings and surfaced a high-severity defect the hand-rolled run had missed.
`gz-obpi-pipeline` 6.39.0 -> 6.40.0 removes the forbidden incantation from the file and
records the measured cost (operator directive, 2026-08-25).

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


Mutation probe — neutralise ONLY the guard, leaving every symbol importable:

    _DEFAULT_IGNORABLE_LETTERS := frozenset()
    -> 5 assertion-level failures, 0 errors

    test_a_hangul_filler_attestor_does_not_retire_invariant_canon FAILS:
      AssertionError: 0 == 0 : Retired corpus entry corpus-prime-directive-...
      The invariant floor shrank.

i.e. with the guard removed the CLI ACTUALLY retired invariant-tier canon with an
invisible attestor, exit 0. The positive control
(`test_real_names_across_scripts_still_pass_the_plausibility_floor`) correctly
still passes under the same mutation, proving the failure is coupled to the guard
rather than to the harness.

Ledger-witness probe — a false delta is now unrepresentable:

    floor_added={'floor-a'}, floor_removed=set()  -> grew,      ['floor-a']
    floor_added=set(),       floor_removed=set()  -> unchanged, []
    floor_added={'same-id'}, floor_removed={'same-id'}
      -> ValueError: floor_added and floor_removed overlap on ['same-id']

Both canonical readers agree on the discriminator: `BOGUS` is rejected by
`validate_ledger` AND by `parse_typed_event`; absence yields None on both, so the
~300 committed rows predating the fields still validate.

Gate evidence: `uv run gz check` -> all 56 checks passed, exit 0.

### Implementation Summary


- Invisible-attestor bypass: CLOSED as a class. `_is_named` previously accepted Hangul filler code points (General_Category=Lo, zero advance width) as the human authorizing an irreversible, append-only retirement of governance canon. The repair derives the property — Default_Ignorable_Code_Point INTERSECT GC=Lo — and caught a fourth code point (U+FFA0) the adversary never probed.
- UCD drift witness: WARNS on the retire path, asserts HARD in CI. An earlier revision raised at module import under an unbounded `requires-python >=3.13`, which would have crashed `gz content retire` outright on Python 3.14 (UCD 16.0.0). Operator-ruled warn-not-raise: the hard failure belongs where a maintainer can re-derive the set.
- Reason validation separated from name validation: `_is_named` is now exclusive to `--attestor`. `--reason` uses the ledger's stripped-non-empty rule, so legitimate references (`#880`, `2026-08-25`) are no longer refused with a false "whitespace-only" diagnostic.
- Floor-movement prose corrected across FOUR homes: parser description, module docstring, `corpus_entry.json` `retires` description, and the manpage. Retirement is a before/after invariant-liveness DELTA with four outcomes (unchanged / shrank / GREW / CHANGED), never a two-state property of the row's kind, and a tombstone grows the floor ONLY when the entry it revives is invariant-tier.
- Ledger witness records the gate's own condition: `corpus_entry_retired` now carries `floor_direction` and `floor_moved_ids`, DERIVED inside the factory from the same two sets the attestor gate reads. `tier` alone was a proxy — a compressible tombstone over an invariant target printed "floor GREW" while the event said `tier='compressible'`, and that event with an empty attestor validated clean.
- Impossible witnesses are unrepresentable, not merely detectable: the factory refuses overlapping added/removed sets, and both canonical readers now enforce the four-state enum while preserving absence for historical rows.
- Four REQs rekeyed from surface properties to the liveness delta under operator ruling (REQ-01, REQ-03, REQ-04, REQ-07), and the brief's Requirements items 2, 3 and 6 reconciled with them. REQ count unchanged at 8.
- Test surface grew from 40 to 56 scoped tests, including a manpage-transcript guard that compares the whole observed CLI line rather than a phrase list — the previous guard was itself defective and stayed green through real drift.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- **GHI #877** — ledger: typed union rejects ~300 committed rows the JSON schema accepts.
  Routed out; repair lies outside this brief's allowlist. Open, blocker-commented.
- **GHI #878** — ledger: corpus retirement can change canon with zero or one of its two
  witnesses. Routed out; the partial-write window is reported honestly, not prevented.
  Open, blocker-commented.
- **GHI #880** — corpus_store: concurrent appends silently drop rows from canon
  (reproduced 20/20). Found by the tier-1 adversary at round 3 as a duplicate-tombstone
  race; measured to be a lost-update in `append_entry`, which is a Denied Path here.
  Routed out under the operator ruling of 2026-08-25. Open, blocker-commented.
- **GHI #863** (REOPENED 2026-08-25) — the shrink-only claim this OBPI repairs has a FOURTH
  home: `src/gzkit/content/models/corpus.py:84`'s `CorpusEntry.retires` docstring still reads
  *"Retirement therefore only ever shrinks the invariant floor, so already-committed renditions
  cannot be invalidated by one"* — false per Algebra 6. Found by the independent spec-reviewer
  during this OBPI's Stage-2 review while checking whether the three-homes repair was complete.
  `corpus.py` is a Denied Path here; both briefs owning it (OBPI-0.0.37-18, OBPI-0.35.0-01) are
  **Completed** and therefore terminal, so nothing blocks an ordinary direct fix once this OBPI
  lands. Reopened rather than re-filed because the root cause is identical (`ghi-author` Step 0).
  Open, evidence-commented.
- **GHI #881** — `corpus_store.append_entry` rewrites the whole corpus with
  `Path.write_text`, which truncates before writing, so a disk-full or interrupted
  append can destroy committed canon while this command's `OSError` handler reports
  *"nothing written"*. Found by the tier-1 adversary at round 6. `corpus_store.py` is a
  Denied Path here; cross-linked to #875 (persist-before-validate) and #880 (lost
  update) — three defects in one function, likely cheaper to fix together. Open.
- **GHI #882** — the ledger validator has no conditional rule form, so it cannot assert
  the runtime gate's own condition: an event with `floor_direction: "grew"` and
  `attestor: ""` validates clean. This OBPI landed the RECORDING half (the event now
  carries `floor_direction` + `floor_moved_ids`, so an auditor can DETECT an unattested
  floor revival); ENFORCEMENT needs `validate_pkg/ledger_check.py`, which is outside
  this allowlist and shared by all 54 event types. Operator-ruled 2026-08-25 to route
  it rather than widen scope a third time. Open.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Gate 5 for OBPI-0.35.0-02-content-withdraw-verb, attested 2026-08-26 on evidence the operator held in full, including a STANDING REFUTED verdict from the tier-1 cross-vendor adversary (round 9, receipt arb-step-codexadversary-33c1b0ee8afa472a88831b255c48e681). Six ARB-receipted Codex rounds (4-9) produced ~25 findings; every one is fixed-and-verified or routed to a tracked GHI. Full `uv run gz check` passes all 56 checks, exit 0. Tests 8850 (receipt arb-step-unittest-48f847fda0d540598339f5ac3b24d118); lint clean (arb-ruff-0757153889ee495e84a1584e32040536); typecheck clean (arb-step-typecheck-5296a1f2f695408bae270c3739127bbe); mkdocs --strict clean (arb-step-mkdocs-12faacb760ac44ba9231702cc0ae546f); behave 7/7 scoped scenarios (arb-step-behave-acd685e6216945b6b100844887ff77a6). `gz validate` green across 6 scopes; `gz covers` behavior_uncovered_reqs 0. Stage-2 dispatch is DECLARED SINGLE-DRIVER with a recorded reason, not inferred. Eight operator rulings were taken and applied during this session.
- Date: 2026-08-26

---

**Date Completed:** 2026-08-26

**Evidence Hash:** -
