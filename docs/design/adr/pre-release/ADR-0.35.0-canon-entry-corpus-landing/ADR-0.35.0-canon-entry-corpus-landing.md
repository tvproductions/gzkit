---
id: ADR-0.35.0-canon-entry-corpus-landing
status: Draft
kind: feature
semver: 0.35.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-07-21
---

# ADR-0.35.0-canon-entry-corpus-landing: Canon Entry: Corpus Landing and Rendition Lineage

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware,
whole-file-reasoning, direct. Holds that a surface which *validates* a candidate
is not the same surface as one that *materializes* it, and refuses to let the
first be described as the second: `compose()` checking an agent's prose against
the corpus leaves every byte the agent invented unaccounted for, which is the
gap this ADR exists to close. Treats a substring containment test as evidence of
nothing when duplicates are present — seven byte-identical entry groups pass the
current floor invisibly, so the measurement must be re-derived rather than
trusted. Counts the unwitnessed remainder out loud (22,378 B of 31,990 B
undeclared) instead of reporting the witnessed 31.2% as coverage, on the
principle that an unmeasured surface is a claim, not a result.

## Intent

The corpus->rendition seam (ADR-0.0.37) is asserted but not closed. Three gaps, all measured this session:

1. The corpus materializes nothing. `composer.py:24-31` takes `candidate_text` from the agent and validates it; its own docstring line 6 concedes "the drop/combine/rewrite judgment is the agent's." Nothing derives AGENTS.md from the corpus.

2. The floor gate is a substring test that hides duplicates. `rendition_floor_coherence.py:72` is `entry.text not in rendered_text`. Seven byte-identical duplicate groups pass it invisibly today and become literal double-emissions the moment a generator materializes. An eighth pair diverges only by quote style and already double-renders: AGENTS.md carries the correction-vs-enhancement doctrine twice (measured).

3. Only 31.2% of the contract is witnessed. 50 invariant entries (9,612 B) + 1 compressible (354 B) = 9,966 B against AGENTS.md's 31,990 B, addressing 8 of 22 H1/H2 sections. The remaining 22,378 B is unaccounted and undeclared.

Two further defects fold in. `composer.py:63-65` computes `compressible_bytes_after = total_bytes - invariant_bytes` = 22,378 against `compressible_bytes_before` = 354 -- a 63x inflation labelled compression, a witness that cannot fail. And `codex.md` (13,606 B, setpoint `lite`) is composed, committed, attested and floor-gated, but nothing plays it back: `sync_surfaces.py:374-376` and `governance/compose.py:28-29` load only ("AGENTS.md", "claude"). A setpoint with no playback is an unfalsifiable claim.

Goal: make canon capture safe and give the seam a real, fail-closed witness over a named and growing fraction of the contract. Discharges GHI #654 (orchestration gap) and GHI #635 (duplicate invariant entries) -- the same wound.

## Decision

<!-- The tombstone fold's algebra is pinned in item 1 below. It is the one
     genuinely irreversible commitment in this ADR, so it is specified here
     rather than deferred to OBPI-0.35.0-01. -->

Close the seam with section ownership plus a debt ratchet, not a total backfill.

### Tombstone fold algebra (binding)

- **Roles.** `retires` marks a pure tombstone: it contributes NO text to the effective view. `supersedes` marks a replacement row: it retires its target AND is itself a content row.
- **Ordering.** A tombstone strictly follows its target in the append log.
- **Liveness by single reverse pass.** `live(e) = not any(live(t) for t in tombstones targeting e)`. Because every tombstone strictly follows its target, evaluating entries last-to-first resolves every dependency before it is read. This is a **single reverse pass — never a fixpoint iteration and never unbounded recursion.**
- **Un-retirement is retiring the tombstone.** Appending `T2` with `retires = <id of T1>` makes `live(T1)` false, which makes `live(X)` true again. All three rows remain in the raw log; retirement history is preserved, not overwritten.
- **No silent double-retire.** At most one LIVE tombstone may target a given entry; a second is a load-time `ValueError`. "Retire twice" can never be silently read as "un-retire."
- **Projection.** `effective_corpus(corpus)` returns, in append order, every entry where `live(e)` is true AND `e.retires is None`.
- **Serialization.** Unset tombstone fields MUST be omitted from the serialized row. `corpus_fingerprint()` hashes `Corpus.dumps()` (`rendition_store.py:56-64`), so emitting `"supersedes":null,"retires":null` on every row would silently re-fingerprint the whole corpus and flip `gz validate --rendition-freshness` to drift on the very commit that lands this change.

SOURCE-OF-TRUTH DIRECTION (operator-ruled this session, stated explicitly rather than inherited): the corpus is the SOURCE that AGENTS.md is generated from. The 68.8% gap is under-population to be closed over time, not evidence that the corpus is a witness log annotating an authored document. This is recorded because the measured shape (corpus subset-of document; zero of 50 invariant entries absent from AGENTS.md) is equally consistent with the witness-log reading, and every OBPI below rests on the source reading being correct.

1. RETIREMENT IS AN APPENDED TOMBSTONE, NEVER A DELETION. `CorpusEntry` gains optional `supersedes: str | None` and `retires: str | None`. `effective_corpus()` folds the append log; `tier_policy.invariant_entries()` reads the effective view; the raw log is never mutated. Direct analogue of `gz obpi withdraw`/`repudiate` (ADR-0.0.71). The fold's algebra is specified in this ADR, not deferred to implementation -- it is the one genuinely irreversible commitment.

2. `gz content retire <surface> --entry <id>` retires by entry id, never by text. Retiring an invariant-tier entry is Gate 5: `--attestor` + `--reason`, fail closed on empty. Per-entry-id rather than per-text because six of the seven byte-identical groups address the same text to two different sections -- text-keyed retirement silently elects a section winner.

   **AMENDED 2026-08-07 (operator-ruled): the verb is `retire`, EXTENDED IN PLACE — not a new `withdraw`.** This item originally named a new verb, `content withdraw`. A retirement verb had already shipped ahead of this ADR under GHI #635 (`852e8a25`, 2026-07-22 — one day after the OBPI briefs were authored) as `gz content retire`, already carrying per-entry-id keying, append-only semantics, and fail-closed exits on unknown and already-retired targets. Implementing `withdraw` would have stood up a SECOND verb for one job. OBPI-0.35.0-02 therefore EXTENDS `retire` with the half it lacks: `--attestor`, the empty-check, tier discrimination (Gate 5 on `invariant` only), the `corpus_entry_appended` event, and three-part recovery prose. `gz obpi withdraw`/`repudiate` (ADR-0.0.71) remain the precedent for the SEMANTICS; they were never a claim on the verb string. The collision went unseen because `gz obpi brief-drift` checks existence, not relevance (GHI #581), and the Fidelity Assertion below carried a `gz-validate-skip: command-shape` marker — the marker that lets a planned verb be documented is also what hid it.

3. SECTION OWNERSHIP + DECREASE-ONLY RATCHET. Sections declare `corpus-owned` or `unowned`. The generator materializes owned sections from the corpus and carries unowned sections forward verbatim. The unowned byte total is recorded in a decrease-only ratchet. Un-owning a section (which raises the ratchet) requires an attested raise-path, Gate 5, the same shape as the retire path -- an undefined reversal path is the one agents invent.

4. `gz validate --rendition-lineage` fails closed over OWNED SECTIONS ONLY -- 31.2% coverage day one, 8 of 22 sections. The 22,378 B is declared as declining debt, not ignored. The coverage percentage appears in Fidelity Assertions, because a gate whose scope is partial and undeclared is the theater this design exists to kill.

5. The lineage map is a SEPARATE `<consumer>.lineage.json` artifact ({section_id: {owned, entry_ids, byte_span}}), not bolted onto `RenditionProvenance` -- generate-time versus commit-time lifecycle, and `RenditionProvenance` is frozen/extra=forbid.

<!-- gz-validate-skip: command-shape -->
6. `gz content land <surface>` (required positional, matching compose/commit) orchestrates atomic multi-consumer write. ONE Gate 5 attestation on the corpus delta covers N consumers; each sidecar records the same `attestation_text` and a shared `landing_id`. Justified because renditions are Layer-3 derived views and generation over owned sections is deterministic -- N attestations would demand N human judgments where only one exists.

7. `gz content remember` gains a POST-APPEND ADVISORY -- three-part recovery prose per `.claude/rules/guardrail-feedback-prose.md`, never a refusal, exit stays 0. Capture must never be blocked: losing the operator's words is strictly worse than a red tree. The tree going red is correct; GHI #654's defect is the SILENCE, not the redness.

8. Codex playback wires to a real surface, coordinating with ADR-pool.vendor-alignment-codex (which owns that surface). This makes the `lite` setpoint falsifiable for the first time.

9. `classification` IS CORPUS-OWNED WHERE THE CORPUS OWNS THE SECTION (operator-ruled 2026-08-02, GHI #737). `CorpusEntry.classification` is schema-required and part of the baseline identity fingerprint but has NO reader anywhere in `src/` -- every hit is a declaration or a writer. The binding copy lives instead in `docs/governance/advisory-rules-audit.md`, which `bullet_retention.py:141-163` parses. Two differently-typed representations of one governance concept, the structured one inert and the markdown one binding, is precisely the shape `.claude/rules/hexagonal-architecture.md` § Operative rules 8 forbids. Resolution: `bullet_retention` resolves a bullet's classification from the corpus when that bullet's section is corpus-owned, and from the scorecard otherwise -- one reader, declared precedence. Pointing the audit wholesale at the corpus (the shape GHI #737 proposed) is REJECTED on measurement: the scorecard carries 144 rows against the corpus's 52 over 8 sections, so a wholesale swap is a ~64% coverage REGRESSION, not a clean substitution. The two surfaces classify overlapping but unequal populations, which is why the field went inert rather than being wired up. This is item 3's section-ownership seam applied to the classification axis: owning a section makes its entries' classification BINDING, so the 36 `Ambiguous` capture-defaults (all `origin: cli:content-remember`, never revisited) must be reconciled BEFORE ownership binds, not after. The field is never dropped -- it is baseline identity, and removal re-fingerprints every committed rendition.

PRECEDENT NOTED (operator-ruled): attested-record edit is decided locally, scoped to corpus entries -- an attested invariant entry may be superseded by an appended tombstone carrying attestor + reason, never edited or deleted in place. Recorded in Boundary Invariants so `ADR-pool.attested-record-edit-doctrine` inherits rather than re-litigates. This ADR does not block on that pool item.

## Consequences

### Positive

1. The invariant floor becomes ENFORCEABLE over a named, growing fraction of the contract, rather than asserted over all of it and verified over none.
2. Coverage becomes a published number with a decrease-only ratchet, so unwitnessed contract text is VISIBLE DEBT instead of silence. Consistent with gzkit's own posture on Layer-3 derived views and advisory scorecards.
3. Duplicate canon retires without breaking append-only; provenance survives in the log. Corpus goes **50 -> 43** live invariant entries (RE-MEASURED 2026-08-07; the authoring-time projection was `50 -> 42`). One of the eight retirements landed early under GHI #635 and one new `invariant` entry was captured 2026-08-06, so the live count reads 50 today for different reasons than it did at authoring. The binding figure at implementation time is whatever OBPI-0.35.0-03 Requirement 2's mandatory re-measurement returns — never this line.
4. `ByteEvidence` stops reporting a 63x inflation (354 B -> 22,378 B) as a compression accounting.
5. `codex.md` becomes falsifiable -- a `lite` setpoint that is actually consumed, for the first time.
6. `gz content remember` stops being a footgun: capture still always succeeds, but it names the drift it caused and the governed next step.
7. A precedent for attested-record edit, scoped to corpus entries, that `ADR-pool.attested-record-edit-doctrine` inherits rather than re-litigates.
8. The lineage map supplies the provenance artifact (rendered section -> contributing entry ids) that the 2026-06-03 Re-Alignment specified and `RenditionProvenance` never carried -- unblocking bidirectional audit.

### Negative

1. 31.2% FAIL-CLOSED COVERAGE IS HONEST BUT THIN, and thinner than the headline suggests. Corrected during OBPI authoring (2026-07-21): the corpus addresses 8 sections but only **7 carry `invariant`-tier entries** -- `governance-doctrine-surfaces` holds the corpus's single `compressible` entry, so it is not on the invariant floor at all. Of those 7, **two carry exactly one entry each** (`obpi-acceptance-protocol`, `defect-fix-routing`). The floor therefore binds meaningfully over five sections plus two tokens, not "8 of 22". The 31.2% byte figure is unaffected -- it counts bytes, not sections; what is corrected is the section-count gloss. The section histogram is an accretion curve, not a curation -- coverage is concentrated where someone happened to run `gz content remember`, not where the contract is load-bearing.

2. THE RATCHET HAS NO FORCING FUNCTION. Decrease-only permits never decreasing. This is the top-ranked pre-mortem failure precisely because it requires nobody to do anything wrong: 18 months out the total reads 22,100 B while "31.2% witnessed" has been printed in Fidelity Assertions forty times, laundering a mostly-unwitnessed contract as a governed one. Cadence, owner, and scheduled floor-raise are UNDECIDED and forced onward (see `DESIGN_FORCING_FUNCTIONS.md` § Closing items 3 and 4).

3. A SINGLE ATTESTATION OVER N CONSUMERS IS STRUCTURALLY A BUNDLE -- the shape AGENTS.md section MAKE LLM STOCHASTIC VIBES INERT names as a vibing signature. Accepted deliberately on determinism grounds, but it needs a per-consumer repudiation story it does not yet have: ADR-0.0.71 gives `repudiate` at OBPI granularity, so unwinding one consumer means unwinding the attestation for all.

4. OWNED-SECTION FAIL-CLOSED MAY BECOME THE THING AGENTS ROUTE AROUND. The in-repo precedent already exists: `rendition_floor_coherence.py:87-91` ships a staged-warn mode and `_checkpoint.resolve` downgrades it inside the MX hangar. When a legitimate operator edit to an owned section cannot round-trip through the corpus, the cheapest recovery is to mark the section unowned. The attested ratchet-raise path is the mitigation; it is not a guarantee.

5. `effective_corpus()` BECOMES A SECOND SOURCE OF TRUTH. The fold sits between the raw log and every consumer (`tier_policy.invariant_entries()`, `rendition_floor_coherence.py:66`, `composer.py:59`). `load_corpus` returns the raw corpus today, so a consumer that never gets the fold is a one-line omission -- and the symptom is a GREEN gate over a rendition that omits canon, or a retired entry resurrected. Worst detection latency of any failure here.

6. TOMBSTONES ARE PERMANENTLY IN THE LOG. Every future reader must run the fold to interpret the corpus. Un-retiring requires appending a third row that retires the tombstone, which the fold must handle without ambiguity.

7. CLAUDE.md REMAINS OUTSIDE THE SEAM. `sync_claude_md` renders from a template plus `.gzkit/agents.local.md`, entirely outside the corpus. Once AGENTS.md owned sections are fail-closed, `agents.local.md` stays a viable ungoverned route to put doctrine in front of every Claude session. Accepted deliberately for scope; named here rather than left silent, and forced onward as a follow-on ADR. This is the only scenario in which this ADR ends up retrospectively performative.

8. THE TIER DIAL IS DEGENERATE AND THIS ADR DOES NOT FIX IT. 50 invariant / 1 compressible is a dial with one notch on one side. The real 57% reduction in `codex.md` is produced by the agent's freehand judgment (`composer.py` docstring line 6), not by tier policy operating on 354 declared compressible bytes. Named as a forced decision (`DESIGN_FORCING_FUNCTIONS.md` § Closing item 3).

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

Coverage is part of the thesis, not a footnote: this ADR ships a gate that binds
over **31.2% of the AGENTS.md surface** (9,966 B of 31,990 B, across 8
corpus-addressed sections of 22 — of which **7 carry invariant-tier entries**
and so are what the floor actually binds over; see § Consequences Negative #1)
and declares the remaining **22,378 B** as decrease-only debt. A gate
whose scope is partial and undeclared is the theater this ADR exists to remove,
so the coverage figure is asserted here and re-measured on every run.

<!-- gz-validate-skip: command-shape -->
| Claim | Command | Expected exit |
|-------|---------|---------------|
| Owned sections derive from the corpus; hand-authored prose in an owned section is refused. | `uv run gz validate --rendition-lineage` | 0 |
| No invariant-tier entry is emitted twice into a rendition (the duplicate-emission regression this ADR retires). | `uv run gz validate --rendition-floor-coherence` | 0 |
| Retiring an invariant-tier entry without an attestor is refused (Gate 5 fail-closed, empty `--attestor`). | `uv run gz content retire AGENTS.md --entry corpus-prime-directive-ownership-2026-06-19T22:55:06.046462+00:00 --attestor "" --reason "probe"` | 1 |
| Capture never refuses: `remember` appends and warns rather than blocking, so operator words are never lost. | `uv run gz content remember AGENTS.md --section fidelity-probe --tier compressible --text "fidelity probe"` | 0 |
| The corpus materializes a candidate without agent hand-authoring (the `candidate_text` gap this ADR closes). | `uv run gz content land AGENTS.md --dry-run` | 0 |
| Byte accounting is honest: `compressible_bytes_after` no longer reports a 63x inflation as compression. | `uv run gz validate --rendition-lineage` | 0 |

## Boundary Invariants

<!-- The sole proof channel for STRUCTURAL-FENCE REQs (ADR-0.0.59). Each entry
     is audited at ADR closeout, not per-OBPI, because each is violated by
     something a SIBLING OBPI adds rather than by anything visible in the owning
     brief's own diff. -->

**BI-01 — Every corpus consumer reads the effective view, never the raw log.**
The complete consumer set is `tier_policy.invariant_entries()` (OBPI-01),
`rendition_floor_coherence.py` (OBPI-06), and `composer.py` (OBPI-05). A
consumer left on the raw log resurrects retired canon **behind a green gate** —
pre-mortem #3, the worst detection latency in this ADR. Audited once every OBPI
that adds a consumer has landed. *Proves REQ-0.35.0-01-09.*

**BI-02 — No two live `invariant`-tier entries share byte-identical text.**
Holds after every ADR-0.35.0 OBPI lands, not merely after OBPI-03. This is the
regression fence § Alternatives H names: the byte-identical groups are invisible
today only because `rendition_floor_coherence.py:72` is a substring test, and
they become literal double-emissions the instant the OBPI-05 generator
materializes. *Proves REQ-0.35.0-03-04.*

**BI-03 — The lineage map lives in `<consumer>.lineage.json` and nowhere inside
`RenditionProvenance`.** `RenditionProvenance` remains `frozen=True` /
`extra="forbid"` and unextended across every OBPI. Generate-time and commit-time
lifecycles stay separated (§ Alternatives O). Cross-OBPI because OBPI-06 and
OBPI-07 both read these artifacts and either could bolt the map on.
*Proves REQ-0.35.0-05-10.*

**BI-04 — No classification surface exists without a reader, and no bullet
resolves from two surfaces at once.** After section ownership lands (OBPI-04)
and the resolver lands (OBPI-10), exactly one surface answers for any given
bullet: the corpus for corpus-owned sections, `advisory-rules-audit.md`
everywhere else. Cross-OBPI because OBPI-04 owns which sections are
corpus-owned and can move a bullet between the two resolvers without touching
OBPI-10's diff — the resolver can be correct on the day it lands and be reading
the wrong surface a section-declaration later. Also fences the reverse failure:
a `CorpusEntry` field re-added with no consumer is the exact defect GHI #737
named, and BI-04 is what makes its recurrence auditable at closeout rather than
discoverable years later. *Proves REQ-0.35.0-10-07.*

**BI-05 — The fail-closed reach of `--rendition-lineage` is owned sections
only.** No ADR-0.35.0 OBPI extends it over unowned bytes. The gate's partial
scope is a declared property of the whole decomposition — OBPI-04 sets the
scope, OBPI-05 supplies the comparison artifact, OBPI-07 consumes the result.
Widening the gate silently would convert a declared 31.2% into an implied 100%,
which is the theater this ADR exists to remove. *Proves REQ-0.35.0-06-08.*

**BI-06 — `gz content remember` refuses an append on no path introduced anywhere
in ADR-0.35.0.** Capture is unblockable across the whole decomposition. OBPI-06's
gate and OBPI-07's orchestrator both make the tree redder, and either could be
tempted to add a precondition to `remember` to keep it green. Losing the
operator's words is strictly worse than a red tree; the defect this ADR fixes is
the SILENCE, not the redness. *Proves REQ-0.35.0-08-07.*

**BI-07 — ADR-0.35.0 makes no change to the surfaces ADR-pool.vendor-alignment-codex owns.**
Specifically: `.codex/config.toml` generation, Codex hook registration and
adapters, Codex subagent role definitions, the `gz validate --surfaces` Codex
drift scope, and the Codex instruction-budget artifacts. This ADR wires playback
of an existing committed rendition and nothing else. Cross-ADR, so auditable
only once the whole ADR-0.35.0 diff is in hand. *Proves REQ-0.35.0-09-07.*

**BI-08 — Attested-record edit, scoped to corpus entries (precedent).** An
attested `invariant`-tier corpus entry may be superseded ONLY by an appended
tombstone carrying `--attestor` and `--reason`; it is never edited in place and
never deleted. Recorded here so `ADR-pool.attested-record-edit-doctrine`
inherits the ruling rather than re-litigating it. This ADR does not block on that
pool item (operator ruling, 2026-07-21).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 7
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 1
- Split Total: 3
- Final Target OBPI Count: 10

<!-- Scoring basis (each dimension scored against the matrix, not asserted):
     Data/State 2      — new `CorpusEntry` fields, new `<consumer>.lineage.json`
                         artifact, new ratchet state, new ledger events.
     Logic/Engine 2    — `effective_corpus()` fold plus the generator
                         materializer constitute a new subsystem.
     Interface 2       — one new CLI verb (`content land`) plus a Gate-5
                         extension of the shipped `content retire` (amended
                         2026-08-07; was "two new CLI verbs (`content withdraw`,
                         `content land`)"), plus a new `gz validate` scope. The
                         score is UNCHANGED at 2 — extending a verb's contract
                         is the same Interface dimension as adding one, and the
                         `gz validate` scope alone tops the band.
     Observability 2   — lineage map, coverage %, ratchet, advisory prose.
     Lineage 2         — the tombstone fold is a historical lineage migration.

     Baseline Selected 7 inside the 5+ band: the dimension total is at the top
     of the scale (10/10), so the band's floor understates the work. Raised
     6 -> 7 on 2026-08-02 (operator-ruled, GHI #737) when the `classification`
     reader was folded in as checklist item 10. The BASELINE is the right dial
     for this, not a split adder: the split rules divide a fixed scope, and
     this amendment ADDS scope — one more narrative unit on the section-
     ownership seam. `Final Target OBPI Count` is derived (baseline + splits),
     so amending it directly would have been drift; `gz specify` rejects a
     hand-set total, which is how the correct dial was found.

     Split adders (each rule is a boolean +1, not a count):
     Single-Narrative +1 — a draft decomposition bundled "generator AND
       lineage.json AND ByteEvidence" and "advisory AND codex playback". The
       matrix rule is explicit: "Avoid the word 'and' in objectives." Codex
       playback split out (item 9); ByteEvidence stayed with the generator
       because it is arithmetic in one function (`composer.py:63-65`) that only
       becomes meaningful once the generator materializes — single narrative.
     Surface Boundary +1 — the work crosses three surfaces: the content CLI,
       the `gz validate` scope registry, and the sync/playback surface.
     Testability Ceiling +1 — item 7 (`content land`) carries atomic
       multi-consumer write, partial-failure recovery, single attestation
       across N consumers, `landing_id` propagation, and resume semantics.
       If the 2am-operator requirements all land as REQs it exceeds five
       clusters and splits again into "atomic write" / "resume, status,
       rollback". Flagged up front rather than discovered mid-flight; that
       contingency has NOT fired, and if it does the target goes 10 -> 11.

     AMENDED 2026-08-02 (operator-ruled, GHI #737): 7 + 3 = 10. The dimension
       scores are UNCHANGED — the classification cut opens no new dimension, it
       is Interface/Observability work on the section-ownership seam item 3
       already scored at 2/2. What changed is how many narrative units that
       fixed dimension profile is being asked to carry, which is the baseline's
       job. Folded into an ADR with no OBPIs landed at authoring time rather
       than retrofitted
       after its OBPIs land over the same corpus surface. -->

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] `CorpusEntry.supersedes` / `.retires` fields + `effective_corpus()` fold (algebra specified, including retire-the-tombstone) + `tier_policy.invariant_entries()` reads the effective view
- [ ] `gz content retire` — Gate-5 extension of the shipped verb: fail-closed on invariant tier (`--attestor` / `--reason` refused when empty). Amended 2026-08-07 from the `content withdraw` name; see § Decision item 2.
- [ ] Retire the duplicate invariant entries -- 7 byte-identical + the operator-ruled divergent pair; corpus **50 -> 43** live invariant (GHI #635). Re-measured 2026-08-07: the divergent pair landed early (`42ba6c250`), so **7 of the 8 remain**; the authoring-time projection was "8 ... 50 -> 42". Re-derive at implementation time per OBPI-0.35.0-03 Requirement 2 -- an off-by-one inside a Gate 5 batch is a fabricated receipt.
- [ ] Section ownership declaration + decrease-only unowned-byte ratchet + attested ratchet-raise path for un-owning
- [ ] corpus->candidate generator (owned materialize / unowned carry-forward) + `<consumer>.lineage.json` emission + `ByteEvidence` accounting correction
- [ ] `gz validate --rendition-lineage` -- fail-closed over owned sections, coverage % surfaced to Fidelity Assertions
<!-- gz-validate-skip: command-shape -->
- [ ] `gz content land <surface>` orchestrator -- atomic multi-consumer write, single Gate 5 on the corpus delta, shared `landing_id`, landing state file written first and cleared last, `--status` and non-destructive resume that does NOT re-prompt for attestation
- [ ] `gz content remember` post-append advisory -- three-part recovery prose, exit stays 0, never refuses the append
- [ ] Codex playback wiring -- make the `lite` setpoint falsifiable; coordinates with ADR-pool.vendor-alignment-codex
- [ ] `classification` reader -- corpus-owned sections resolve from `CorpusEntry.classification`, scorecard elsewhere; the 36 `Ambiguous` capture-defaults reconciled before ownership binds (GHI #737)

## Q&A Transcript

<!-- Interview transcript preserved for context. Amended after interview per the Decision section (see the amendment dated 2026-08-07). -->

> **SUPERSEDED IN PART — `## Decision` above is authoritative.** This transcript is
> the interview as conducted and is preserved as history, not reconciled in place
> (the ADR-0.0.74 / GHI #640 convention). Known divergence: transcript answers 2 and
> the checklist item 2 name the verb `content withdraw`; § Decision item 2 was
> **amended 2026-08-07** to `gz content retire`, extended in place. Read the verb
> from § Decision, never from here.

*Interview conducted: 2026-07-21T18:32:46.989426*
*Amended: 2026-08-07 (verb is `content retire`, extended in place, not a new `content withdraw`)*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.35.0-canon-entry-corpus-landing

### Q: What is the title of this ADR?

**A:** Canon Entry: Corpus Landing and Rendition Lineage

### Q: What is the semantic version?

**A:** 0.35.0

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** The corpus->rendition seam (ADR-0.0.37) is asserted but not closed. Three gaps, all measured this session:

1. The corpus materializes nothing. `composer.py:24-31` takes `candidate_text` from the agent and validates it; its own docstring line 6 concedes "the drop/combine/rewrite judgment is the agent's." Nothing derives AGENTS.md from the corpus.

2. The floor gate is a substring test that hides duplicates. `rendition_floor_coherence.py:72` is `entry.text not in rendered_text`. Seven byte-identical duplicate groups pass it invisibly today and become literal double-emissions the moment a generator materializes. An eighth pair diverges only by quote style and already double-renders: AGENTS.md carries the correction-vs-enhancement doctrine twice (measured).

3. Only 31.2% of the contract is witnessed. 50 invariant entries (9,612 B) + 1 compressible (354 B) = 9,966 B against AGENTS.md's 31,990 B, addressing 8 of 22 H1/H2 sections. The remaining 22,378 B is unaccounted and undeclared.

Two further defects fold in. `composer.py:63-65` computes `compressible_bytes_after = total_bytes - invariant_bytes` = 22,378 against `compressible_bytes_before` = 354 -- a 63x inflation labelled compression, a witness that cannot fail. And `codex.md` (13,606 B, setpoint `lite`) is composed, committed, attested and floor-gated, but nothing plays it back: `sync_surfaces.py:374-376` and `governance/compose.py:28-29` load only ("AGENTS.md", "claude"). A setpoint with no playback is an unfalsifiable claim.

Goal: make canon capture safe and give the seam a real, fail-closed witness over a named and growing fraction of the contract. Discharges GHI #654 (orchestration gap) and GHI #635 (duplicate invariant entries) -- the same wound.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Close the seam with section ownership plus a debt ratchet, not a total backfill.

SOURCE-OF-TRUTH DIRECTION (operator-ruled this session, stated explicitly rather than inherited): the corpus is the SOURCE that AGENTS.md is generated from. The 68.8% gap is under-population to be closed over time, not evidence that the corpus is a witness log annotating an authored document. This is recorded because the measured shape (corpus subset-of document; zero of 50 invariant entries absent from AGENTS.md) is equally consistent with the witness-log reading, and every OBPI below rests on the source reading being correct.

1. RETIREMENT IS AN APPENDED TOMBSTONE, NEVER A DELETION. `CorpusEntry` gains optional `supersedes: str | None` and `retires: str | None`. `effective_corpus()` folds the append log; `tier_policy.invariant_entries()` reads the effective view; the raw log is never mutated. Direct analogue of `gz obpi withdraw`/`repudiate` (ADR-0.0.71). The fold's algebra is specified in this ADR, not deferred to implementation -- it is the one genuinely irreversible commitment.

<!-- gz-validate-skip: command-shape -->
2. `gz content withdraw <surface> --entry <id>` retires by entry id, never by text. Retiring an invariant-tier entry is Gate 5: `--attestor` + `--reason`, fail closed on empty. Per-entry-id rather than per-text because six of the seven byte-identical groups address the same text to two different sections -- text-keyed retirement silently elects a section winner.

3. SECTION OWNERSHIP + DECREASE-ONLY RATCHET. Sections declare `corpus-owned` or `unowned`. The generator materializes owned sections from the corpus and carries unowned sections forward verbatim. The unowned byte total is recorded in a decrease-only ratchet. Un-owning a section (which raises the ratchet) requires an attested raise-path, Gate 5, the same shape as the retire path -- an undefined reversal path is the one agents invent.

4. `gz validate --rendition-lineage` fails closed over OWNED SECTIONS ONLY -- 31.2% coverage day one, 8 of 22 sections. The 22,378 B is declared as declining debt, not ignored. The coverage percentage appears in Fidelity Assertions, because a gate whose scope is partial and undeclared is the theater this design exists to kill.

5. The lineage map is a SEPARATE `<consumer>.lineage.json` artifact ({section_id: {owned, entry_ids, byte_span}}), not bolted onto `RenditionProvenance` -- generate-time versus commit-time lifecycle, and `RenditionProvenance` is frozen/extra=forbid.

<!-- gz-validate-skip: command-shape -->
6. `gz content land <surface>` (required positional, matching compose/commit) orchestrates atomic multi-consumer write. ONE Gate 5 attestation on the corpus delta covers N consumers; each sidecar records the same `attestation_text` and a shared `landing_id`. Justified because renditions are Layer-3 derived views and generation over owned sections is deterministic -- N attestations would demand N human judgments where only one exists.

7. `gz content remember` gains a POST-APPEND ADVISORY -- three-part recovery prose per `.claude/rules/guardrail-feedback-prose.md`, never a refusal, exit stays 0. Capture must never be blocked: losing the operator's words is strictly worse than a red tree. The tree going red is correct; GHI #654's defect is the SILENCE, not the redness.

8. Codex playback wires to a real surface, coordinating with ADR-0.44.0-vendor-alignment-codex (which owns that surface). This makes the `lite` setpoint falsifiable for the first time.

PRECEDENT NOTED (operator-ruled): attested-record edit is decided locally, scoped to corpus entries -- an attested invariant entry may be superseded by an appended tombstone carrying attestor + reason, never edited or deleted in place. Recorded in Boundary Invariants so `ADR-pool.attested-record-edit-doctrine` inherits rather than re-litigates. This ADR does not block on that pool item.

### Q: What good things result from this decision? List benefits.

**A:** 1. The invariant floor becomes ENFORCEABLE over a named, growing fraction of the contract, rather than asserted over all of it and verified over none.
2. Coverage becomes a published number with a decrease-only ratchet, so unwitnessed contract text is VISIBLE DEBT instead of silence. Consistent with gzkit's own posture on Layer-3 derived views and advisory scorecards.
3. Duplicate canon retires without breaking append-only; provenance survives in the log. Corpus goes 50 -> 42 invariant entries.
4. `ByteEvidence` stops reporting a 63x inflation (354 B -> 22,378 B) as a compression accounting.
5. `codex.md` becomes falsifiable -- a `lite` setpoint that is actually consumed, for the first time.
6. `gz content remember` stops being a footgun: capture still always succeeds, but it names the drift it caused and the governed next step.
7. A precedent for attested-record edit, scoped to corpus entries, that `ADR-pool.attested-record-edit-doctrine` inherits rather than re-litigates.
8. The lineage map supplies the provenance artifact (rendered section -> contributing entry ids) that the 2026-06-03 Re-Alignment specified and `RenditionProvenance` never carried -- unblocking bidirectional audit.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. 31.2% FAIL-CLOSED COVERAGE IS HONEST BUT THIN, and thinner than the headline suggests. Three of the eight covered sections carry exactly one entry each (`governance-doctrine-surfaces`, `obpi-acceptance-protocol`, `defect-fix-routing`). "8 of 22 sections" overstates what is functionally four sections plus three tokens. The section histogram is an accretion curve, not a curation -- coverage is concentrated where someone happened to run `gz content remember`, not where the contract is load-bearing.

2. THE RATCHET HAS NO FORCING FUNCTION. Decrease-only permits never decreasing. This is the top-ranked pre-mortem failure precisely because it requires nobody to do anything wrong: 18 months out the total reads 22,100 B while "31.2% witnessed" has been printed in Fidelity Assertions forty times, laundering a mostly-unwitnessed contract as a governed one. Cadence, owner, and scheduled floor-raise are UNDECIDED and forced onward (see Forced Decisions).

3. A SINGLE ATTESTATION OVER N CONSUMERS IS STRUCTURALLY A BUNDLE -- the shape AGENTS.md section MAKE LLM STOCHASTIC VIBES INERT names as a vibing signature. Accepted deliberately on determinism grounds, but it needs a per-consumer repudiation story it does not yet have: ADR-0.0.71 gives `repudiate` at OBPI granularity, so unwinding one consumer means unwinding the attestation for all.

4. OWNED-SECTION FAIL-CLOSED MAY BECOME THE THING AGENTS ROUTE AROUND. The in-repo precedent already exists: `rendition_floor_coherence.py:87-91` ships a staged-warn mode and `_checkpoint.resolve` downgrades it inside the MX hangar. When a legitimate operator edit to an owned section cannot round-trip through the corpus, the cheapest recovery is to mark the section unowned. The attested ratchet-raise path is the mitigation; it is not a guarantee.

5. `effective_corpus()` BECOMES A SECOND SOURCE OF TRUTH. The fold sits between the raw log and every consumer (`tier_policy.invariant_entries()`, `rendition_floor_coherence.py:66`, `composer.py:59`). `load_corpus` returns the raw corpus today, so a consumer that never gets the fold is a one-line omission -- and the symptom is a GREEN gate over a rendition that omits canon, or a retired entry resurrected. Worst detection latency of any failure here.

6. TOMBSTONES ARE PERMANENTLY IN THE LOG. Every future reader must run the fold to interpret the corpus. Un-retiring requires appending a third row that retires the tombstone, which the fold must handle without ambiguity.

7. CLAUDE.md REMAINS OUTSIDE THE SEAM. `sync_claude_md` renders from a template plus `.gzkit/agents.local.md`, entirely outside the corpus. Once AGENTS.md owned sections are fail-closed, `agents.local.md` stays a viable ungoverned route to put doctrine in front of every Claude session. Accepted deliberately for scope; named here rather than left silent, and forced onward as a follow-on ADR. This is the only scenario in which this ADR ends up retrospectively performative.

8. THE TIER DIAL IS DEGENERATE AND THIS ADR DOES NOT FIX IT. 50 invariant / 1 compressible is a dial with one notch on one side. The real 57% reduction in `codex.md` is produced by the agent's freehand judgment (`composer.py` docstring line 6), not by tier policy operating on 354 declared compressible bytes. Named as a forced decision.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. `CorpusEntry.supersedes` / `.retires` fields + `effective_corpus()` fold (algebra specified, including retire-the-tombstone) + `tier_policy.invariant_entries()` reads the effective view
<!-- gz-validate-skip: command-shape -->
2. `gz content withdraw` verb; Gate 5 fail-closed on invariant tier (`--attestor` / `--reason` refused when empty)
3. Retire the 8 duplicate invariant entries -- 7 byte-identical + the operator-ruled divergent pair; corpus 50 -> 42 (GHI #635)
4. Section ownership declaration + decrease-only unowned-byte ratchet + attested ratchet-raise path for un-owning
5. corpus->candidate generator (owned materialize / unowned carry-forward) + `<consumer>.lineage.json` emission + `ByteEvidence` accounting correction
6. `gz validate --rendition-lineage` -- fail-closed over owned sections, coverage % surfaced to Fidelity Assertions
<!-- gz-validate-skip: command-shape -->
7. `gz content land <surface>` orchestrator -- atomic multi-consumer write, single Gate 5 on the corpus delta, shared `landing_id`, landing state file written first and cleared last, `--status` and non-destructive resume that does NOT re-prompt for attestation
8. `gz content remember` post-append advisory -- three-part recovery prose, exit stays 0, never refuses the append
9. Codex playback wiring -- make the `lite` setpoint falsifiable; coordinates with ADR-0.44.0-vendor-alignment-codex

### Q: What alternatives were considered and why were they rejected?

**A:** B -- TOTAL CORPUS BACKFILL TO 100%. Rejected. Much of the unwitnessed 22,378 B is table-shaped (gate covenant, lane rules, kinds table, control-surface block) with no operator utterance behind it; backfilling means fabricating `origin` and `witness` fields. That poisons the one artifact the whole system trusts, and is the same can't-fail-witness defect class this ADR exists to remove. Honest accounting on the record: because one Gate 5 covers the delta, B's ATTESTATION cost is actually LOWER than A's, not higher -- the intuition that B is attestation-expensive is wrong. Its disqualifying cost is entirely the fabricated provenance. Equally on the record: A's failure mode (a permanent 31.2% that nobody drives down) is INVISIBLE and requires no error by anyone, whereas B's failure mode is at least legible in the log. A trades a visible defect for an invisible one. It remains the right call, but the trade is named here rather than assumed away.

<!-- gz-validate-skip: command-shape -->
C -- DELTA-PATCH GENERATOR ONLY. Rejected as a destination, retained as the presentation layer inside `gz content land`. Diffing effective-corpus against the last-landed fingerprint and patching the prior rendition is the smallest surface and closes the footgun, but the `rendition subset-of corpus` gate CANNOT be built on it: the rendition is by construction prior-rendition-plus-patch with no total corpus derivation anywhere. It also cannot self-heal -- once a rendition drifts, the delta path perpetuates the drift forever.

D -- TEXT-KEYED DEDUP AT COMPOSITION TIME. Rejected on two counts. Six of the seven byte-identical groups address the same text to two DIFFERENT sections, so text-keyed retirement silently elects a section winner -- a question text identity cannot see. And on the divergent pair it would silently pick a quote style with no witness, which is doctrine drift with no attestation: the named root failure in AGENTS.md section MAKE LLM STOCHASTIC VIBES INERT, operative claim 3.

E -- HARD-DELETE THE DUPLICATE ROWS. Rejected. Violates append-only, the corpus's defining property (`Corpus.append` returns a new corpus, `models/corpus.py:60-62`, frozen + extra=forbid; `corpus_store.py` has no delete path). The `dc2bc605` precedent does NOT authorize it: that was a back-out of a same-session, never-composed, never-attested append, not retirement of attested canon. Six of the live groups are rendered, committed, attested canon. Deleting them destroys the ledger's ability to answer when a directive entered canon and under what origin.

F -- MUTATE TIER invariant -> compressible IN PLACE TO DEMOTE A DUPLICATE. Rejected. In-place mutation of an append-only store by another name, and it destroys the historical fact that the entry WAS invariant -- exactly the provenance the corpus exists to hold.

G -- FIX THE SUBSTRING TEST ONLY. Rejected. Making `rendition_floor_coherence.py:72` an exact-match check turns six invisible duplicates into failures with no recovery path, because no retirement verb exists. Strictly worse than the status quo.

H -- SHIP THE GENERATOR FIRST, DEFER RETIREMENT. Rejected. Ships a regression by construction: the byte-identical groups are invisible today ONLY because the floor check is a substring test, and they become literal double-emissions the instant a generator materializes. Supersede is a PREREQUISITE, not a parallel workstream.

I -- AUTO-COMPOSE AND AUTO-COMMIT ON `remember`. Rejected. Auto-commit of a rendition bypasses Gate 5. `gz content commit` is fail-closed on empty `--attestor`/`--attestation-text` by explicit design (`commit.py:47-54`); routing around it is the bypass AGENTS.md Never #1 forbids.

J -- MAKE `remember` REFUSE THE APPEND WHEN IT WOULD DRIFT RENDITIONS. Rejected. Capture is the operator's words entering canon; a capture tool that refuses is a tool that loses doctrine.

K -- REGISTRY-SHAPED SUCCESSOR (revive OBPI-0.0.37-02/03). Rejected -- settled and permanently closed. ADR-0.0.37 Terminal Disposition: "the registry spine, obsoleted by the 2026-06-03 corpus Re-Alignment. Permanently withdrawn (obpi_withdrawn, 2026-07-17, d03ce98f)." Re-deciding this cost the 2026-07-19 session.

L -- LLM IN THE RENDER/PLAYBACK PATH. Rejected -- already recorded as ADR-0.0.37 Alternatives #11 and #16. Non-determinism at the canon layer is the failure this seam exists to close, and determinism is load-bearing for the single-attestation ruling.

M -- FOLD THIS INTO ADR-0.0.37 AS NEW OBPIs. Rejected. ADR-0.0.37 is concluded Completed -- Partial (superseded) and its Terminal Disposition states re-completion is refused. Foundation is sunsetting (Movement A -> ADR-0.34.0 capstone); adding foundation OBPIs runs against the sunset. ADR-0.0.37 itself names the successor as feature-shaped: "a mechanical defense of an invariant is a feature, not the invariant" (ADR-0.0.18).

N -- PARK AS A POOL ADR. Rejected. The operator ruled Movement A, and the campaign is Magna Carta. Campaign section 7 puts pool backlog post-1.0, so pooling would park this behind 1.0 -- which is exactly where it has been stuck.

O -- STORE THE PROVENANCE MAP INSIDE `RenditionProvenance`. Rejected. It is frozen=True/extra=forbid and written at COMMIT time; the lineage map is produced at GENERATE time and is per-section, not per-artifact. Bolting a nested map on conflates two lifecycles and forces the freshness gate to load data it never reads.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

B -- TOTAL CORPUS BACKFILL TO 100%. Rejected. Much of the unwitnessed 22,378 B is table-shaped (gate covenant, lane rules, kinds table, control-surface block) with no operator utterance behind it; backfilling means fabricating `origin` and `witness` fields. That poisons the one artifact the whole system trusts, and is the same can't-fail-witness defect class this ADR exists to remove. Honest accounting on the record: because one Gate 5 covers the delta, B's ATTESTATION cost is actually LOWER than A's, not higher -- the intuition that B is attestation-expensive is wrong. Its disqualifying cost is entirely the fabricated provenance. Equally on the record: A's failure mode (a permanent 31.2% that nobody drives down) is INVISIBLE and requires no error by anyone, whereas B's failure mode is at least legible in the log. A trades a visible defect for an invisible one. It remains the right call, but the trade is named here rather than assumed away.

<!-- gz-validate-skip: command-shape -->
C -- DELTA-PATCH GENERATOR ONLY. Rejected as a destination, retained as the presentation layer inside `gz content land`. Diffing effective-corpus against the last-landed fingerprint and patching the prior rendition is the smallest surface and closes the footgun, but the `rendition subset-of corpus` gate CANNOT be built on it: the rendition is by construction prior-rendition-plus-patch with no total corpus derivation anywhere. It also cannot self-heal -- once a rendition drifts, the delta path perpetuates the drift forever.

D -- TEXT-KEYED DEDUP AT COMPOSITION TIME. Rejected on two counts. Six of the seven byte-identical groups address the same text to two DIFFERENT sections, so text-keyed retirement silently elects a section winner -- a question text identity cannot see. And on the divergent pair it would silently pick a quote style with no witness, which is doctrine drift with no attestation: the named root failure in AGENTS.md section MAKE LLM STOCHASTIC VIBES INERT, operative claim 3.

E -- HARD-DELETE THE DUPLICATE ROWS. Rejected. Violates append-only, the corpus's defining property (`Corpus.append` returns a new corpus, `models/corpus.py:60-62`, frozen + extra=forbid; `corpus_store.py` has no delete path). The `dc2bc605` precedent does NOT authorize it: that was a back-out of a same-session, never-composed, never-attested append, not retirement of attested canon. Six of the live groups are rendered, committed, attested canon. Deleting them destroys the ledger's ability to answer when a directive entered canon and under what origin.

F -- MUTATE TIER invariant -> compressible IN PLACE TO DEMOTE A DUPLICATE. Rejected. In-place mutation of an append-only store by another name, and it destroys the historical fact that the entry WAS invariant -- exactly the provenance the corpus exists to hold.

G -- FIX THE SUBSTRING TEST ONLY. Rejected. Making `rendition_floor_coherence.py:72` an exact-match check turns six invisible duplicates into failures with no recovery path, because no retirement verb exists. Strictly worse than the status quo.

H -- SHIP THE GENERATOR FIRST, DEFER RETIREMENT. Rejected. Ships a regression by construction: the byte-identical groups are invisible today ONLY because the floor check is a substring test, and they become literal double-emissions the instant a generator materializes. Supersede is a PREREQUISITE, not a parallel workstream.

I -- AUTO-COMPOSE AND AUTO-COMMIT ON `remember`. Rejected. Auto-commit of a rendition bypasses Gate 5. `gz content commit` is fail-closed on empty `--attestor`/`--attestation-text` by explicit design (`commit.py:47-54`); routing around it is the bypass AGENTS.md Never #1 forbids.

J -- MAKE `remember` REFUSE THE APPEND WHEN IT WOULD DRIFT RENDITIONS. Rejected. Capture is the operator's words entering canon; a capture tool that refuses is a tool that loses doctrine.

K -- REGISTRY-SHAPED SUCCESSOR (revive OBPI-0.0.37-02/03). Rejected -- settled and permanently closed. ADR-0.0.37 Terminal Disposition: "the registry spine, obsoleted by the 2026-06-03 corpus Re-Alignment. Permanently withdrawn (obpi_withdrawn, 2026-07-17, d03ce98f)." Re-deciding this cost the 2026-07-19 session.

L -- LLM IN THE RENDER/PLAYBACK PATH. Rejected -- already recorded as ADR-0.0.37 Alternatives #11 and #16. Non-determinism at the canon layer is the failure this seam exists to close, and determinism is load-bearing for the single-attestation ruling.

M -- FOLD THIS INTO ADR-0.0.37 AS NEW OBPIs. Rejected. ADR-0.0.37 is concluded Completed -- Partial (superseded) and its Terminal Disposition states re-completion is refused. Foundation is sunsetting (Movement A -> ADR-0.34.0 capstone); adding foundation OBPIs runs against the sunset. ADR-0.0.37 itself names the successor as feature-shaped: "a mechanical defense of an invariant is a feature, not the invariant" (ADR-0.0.18).

N -- PARK AS A POOL ADR. Rejected. The operator ruled Movement A, and the campaign is Magna Carta. Campaign section 7 puts pool backlog post-1.0, so pooling would park this behind 1.0 -- which is exactly where it has been stuck.

O -- STORE THE PROVENANCE MAP INSIDE `RenditionProvenance`. Rejected. It is frozen=True/extra=forbid and written at COMMIT time; the lineage map is produced at GENERATE time and is per-section, not per-artifact. Bolting a nested map on conflates two lifecycles and forces the freshness gate to load data it never reads.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.35.0 | Pending | | | |
