# Stage 4a — OBPI-0.35.0-05-corpus-candidate-generator — PRIOR ROUNDS (history)

> Preserved verbatim from earlier acceptance rounds, tied to their own reviewed state.
> NOT the current argument: the current packet is `OBPI-0.35.0-05-corpus-candidate-generator.stage4a.md`.
> Transcripts here were reproducible against the tree of THEIR round and are not expected to
> reproduce today; they are retained as a record, never as present-tense evidence.

## Prior rounds (preserved)

Everything below is the earlier acceptance argument, retained verbatim as history and tied to its
own reviewed state. It is NOT the current argument; where it disagrees with the sections above, the
sections above govern.

# Stage 4a — OBPI-0.35.0-05-corpus-candidate-generator

**Rebuilt 2026-09-08 from inspected artifacts and observed results.** Every figure below was
re-measured in this session. Figures inherited from earlier revisions without re-measurement
are marked as such. No attestation is solicited by this packet.

## 1. Value Narrative

Before this OBPI the corpus materialized nothing: `composer.py` took `candidate_text` from
the agent and only validated it, its own docstring conceding "the drop/combine/rewrite
judgment is the agent's" (ADR-0.35.0 § Intent gap 1). Nothing derived AGENTS.md from the
corpus, and `ByteEvidence` reported `total_bytes - invariant_bytes` as "compression".

Now `gz content compose <surface> --consumer <vendor>` with no candidate materializes one:
owned sections generated from the EFFECTIVE corpus, unowned sections carried forward
byte-verbatim from the prior committed rendition, a per-consumer
`<consumer>.candidate.lineage.json` recording which is which with half-open UTF-8 spans
forming a disjoint complete partition, and byte accounting attributing only entries actually
emitted.

## 2. Key Proof

```text
$ uv run python -c "from pathlib import Path; from gzkit.content.composer import generate_candidate; from gzkit.content.corpus_store import load_corpus; from gzkit.content.tier_policy import assert_invariant_verbatim; from gzkit.content.ownership import iter_section_boundaries; r=generate_candidate(Path('.'),'AGENTS.md','root'); c=r.rendition.candidate_text; p=Path('.gzkit/renditions/AGENTS.md/root.md').read_text(encoding='utf-8'); pb=p.encode(); cb=c.encode(); r2=generate_candidate(Path('.'),'AGENTS.md','root'); r.lineage.assert_complete_partition(len(cb)); assert_invariant_verbatim(load_corpus(Path('.'),'AGENTS.md'), c); print('sections', len(r.lineage.sections), 'owned', sum(1 for v in r.lineage.sections.values() if v.owned)); print('verbatim', all(cb[r.lineage.sections[b.section_id].byte_span[0]:r.lineage.sections[b.section_id].byte_span[1]]==pb[b.start:b.end] for b in iter_section_boundaries(p) if not r.lineage.sections[b.section_id].owned)); print('deterministic', r2.rendition.candidate_text==c and r2.lineage==r.lineage); print('evidence', r.rendition.byte_evidence.compressible_bytes_before, r.rendition.byte_evidence.compressible_bytes_after)"
sections 22 owned 12
verbatim True
deterministic True
evidence 354 354
```

**What this establishes:** on the live corpus the generator is deterministic across two
runs, its lineage forms a complete partition of the candidate, every unowned span is
byte-identical to the prior rendition, and the invariant floor holds.
**What it does NOT establish:** it is a self-consistency check of production against
production for the partition and determinism halves. The `verbatim` half IS externally
anchored — it compares candidate bytes against the committed rendition file on disk.

## 3. Evidence

**Quality checks — all receipts emitted in THIS session, 2026-09-08:**

| Check | Command | Result |
|-------|---------|--------|
| Tests | `arb:unittest` (see below) | 9966 tests, OK (skipped=4) — receipt `arb-step-unittest-ebee8240d52d4445a4b66b141116b14a` (`exit_status: 0`) |
| Lint | `arb:ruff` (see below) | clean — receipt `arb-ruff-1946f90d6e1146488d5be04b67abfbab` (`exit_status: 0`) |
| Typecheck | `arb:typecheck` (see below) | clean — receipt `arb-step-typecheck-39e32125123d40c4b50234ad4f9b1fbd` (`exit_status: 0`) |
| Docs (Gate 3) | `arb:mkdocs` (see below) | clean — receipt `arb-step-mkdocs-c631aa5f7d29430c88283829eed0dff2` (`exit_status: 0`) |
| BDD (Gate 4) | `arb:behave` (see below) | 5 scenarios passed, 0 failed — receipt `arb-step-behave-4176f496d9694cbbb4ea776d0fc19052` (`exit_status: 0`) |

```bash
# arb:unittest
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
# arb:ruff
uv run gz arb ruff
# arb:typecheck
uv run gz arb typecheck
# arb:mkdocs
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# arb:behave
uv run gz arb step --name behave -- uv run -m behave --tags=@REQ-0.35.0-05-01,@REQ-0.35.0-05-02,@REQ-0.35.0-05-04,@REQ-0.35.0-05-05,@REQ-0.35.0-05-08 features/
```

> **Correction to the prior packet.** It cited `9952/9952`. The observed count this session
> is 9966 with 4 skipped. The earlier figure was accurate when captured and went stale.

**REQ → @covers parity, re-run this session:**

```text
$ uv run gz covers OBPI-0.35.0-05-corpus-candidate-generator --json
```

Observed `summary`: `total_reqs: 10`, `covered_reqs: 9`, `uncovered_reqs: 1`,
`behavior_uncovered_reqs: 0`. The single uncovered REQ is `REQ-0.35.0-05-10`, which is
STRUCTURAL-FENCE and correctly carries no `@covers` test (ADR-0.0.59). Parity holds.

## 4. Per-claim evidence ledger

Each row states the requirement, the exact evidence, and the bound on that evidence.

| REQ | Kind | Exact evidence | What it establishes | What it does NOT establish |
|-----|------|----------------|---------------------|----------------------------|
| 05-01 | BEHAVIOR | `TestOwnedSectionBodyFromCorpus`; mutation row 1 (reproducible: `chunk = heading_bytes + body` → prior-text slice) → `assertion` kill | owned bytes come from the corpus, not the prior rendition | nothing about WHICH corpus entries when several address one section |
| 05-02 | BEHAVIOR | `test_unowned_section_bytes_are_byte_verbatim` (`test_composer.py:516`); mutation row 2 (prose-only) | carried bytes are byte-identical under an LF→CRLF reflow | boundary LOCATION — both slices are located by the same production parser; a correlated shift passes. Structural check is `test_content_compose.py:457` |
| 05-03 | BEHAVIOR | `TestRetiredEntryExcludedButVerbatimSpanUnaffected`; mutation row 3 (reproducible) | retired entries contribute no bytes and no lineage id | nothing about tombstone ordering |
| 05-04 | BEHAVIOR | `test_compose_generates_candidate_and_lineage_on_tty_stdin`; rows 4, 10 (reproducible) | the lineage artifact exists with the declared shape | that any recorded VALUE is correct — the cited test asserts key presence (`assertIn("owned"/"entry_ids"/"byte_span", section)`, `test_content_compose.py:289-291`). Values are checked elsewhere; this row alone does not prove REQ-04. Nor is the `owned` flag verified against `.gzkit/ownership/AGENTS.md.json` anywhere in § 6 |
| 05-05 | BEHAVIOR | `TestPerConsumerOffsetsAndRouteRefusal`; row 5 (reproducible) | off-route consumers refused; per-consumer spans differ | `assertNotEqual` on spans is a weak form — it proves difference, not correctness of either |
| 05-06 | BEHAVIOR | `test_a_compressible_entry_in_an_unowned_section_is_never_attributed`; row 6 (reproducible) | attribution counts only emitted entries | — |
| 05-07 | BEHAVIOR | `test_byte_evidence_raises_when_attributed_exceeds_before`; row 7 (reproducible: guard → `if False:`) | the inflation guard fails closed | — |
| 05-08 | BEHAVIOR | `TestDeterministicGeneration`; row 8 (prose-only) | two runs agree | agreement of two runs of the same code is the REQ's own semantic; it is not an external oracle |
| 05-09 | BEHAVIOR | `TestDuplicateLiveInvariantRefusal`; row 9 (reproducible) | duplicate live invariants refuse, naming both ids | — |
| 05-10 | STRUCTURAL-FENCE | parent-ADR `## Boundary Invariants` BI-03 | audited at ADR closeout | not audited here |


## 5. Determination — the assertion classifier is AUXILIARY, not required proof

**Question put by the operator 2026-09-08:** are the assertion audit's classifications
required proof for this OBPI's acceptance, or an auxiliary diagnostic introduced during the
review rounds?

**Determination: AUXILIARY.** Traced against the governing acceptance requirements on four
independent grounds, each checkable:

1. **No requirement asks for it.** The brief's `## Acceptance Criteria` carries exactly ten
   REQs — `REQ-0.35.0-05-01` through `-10`, nine `[behavior]` and one `[structural-fence]`.
   Every one is a claim about the GENERATOR: corpus-derived owned bytes, byte-verbatim
   carry-forward, retired-entry exclusion, lineage artifact shape, per-consumer spans,
   accounting attribution, the fail-closed inflation guard, determinism, duplicate-invariant
   refusal, and the `RenditionProvenance` fence. Not one is a claim about assertion
   strength, assertion classification, or the size of an assertion population.
2. **It is not a proof channel.** `.gzkit/rules/tests.md` § REQ Scope Discipline admits
   exactly three: BEHAVIOR → an `@covers`-decorated test in `tests/**`; SUPPORT → a
   path-citing ledger event plus a structural validator; STRUCTURAL-FENCE → a parent-ADR
   `## Boundary Invariants` entry. A classifier's output is none of the three, and
   `gz validate --req-kind-discipline` — the mechanical witness — reads the tags and those
   channels, never any classifier artifact.
3. **It is not a deliverable of this brief.** No REQ names it and no `## Allowed Paths`
   entry produces it; the brief's declared work surface is `src/**`, `tests/**`,
   `features/**` and this brief's evidence sections. *Stated carefully, because an earlier
   draft of this ground proved too much:* it said `.gzkit/evidence/**` "appears nowhere in
   Allowed Paths", which is true and would equally disqualify THIS packet, which lives
   there. `.gzkit/evidence/**` is where evidence apparatus lives by convention. The point is
   that the classifier is not a REQUIRED PRODUCT of any acceptance criterion — grounds 1 and
   2 are the load-bearing ones and this ground adds nothing they do not already carry.
4. **It postdates the work it was being used to judge.** The classifier was authored at
   round 12 (2026-09-08) in response to a finding about the EVIDENCE RECORD's prose — three
   rounds after the last change to `src/**` or `tests/**`. Rounds 10 and 11 preceded it and
   litigated census and classification claims made without any published measurer; round 10's
   subject was a 144-vs-145 assertion count, not a classifier. "Classifier thread" is used
   below as shorthand for rounds 10-14 as a whole; only rounds 12-14 had a classifier.

**Measured consequence of the drift, and the reason the operator's ruling bites.** The last
commit touching `src/**`, `tests/**` or `features/**` is `1cef5d80` (round 9's repair).
Rounds 10 through 14 — the entire classifier thread — produced **zero** production change
and **zero** test change:

```text
$ git diff --stat -- src tests features
(empty)
```

Five adversarial rounds — **all five returning `NOT-CORROBORATED | refuted`** (brief `:960`,
`:1008`, `:1064`, `:1129`, `:1186`) — were spent on the accuracy of a diagnostic that proves
no requirement.

**A false attribution is corrected here, and it was load-bearing for this ruling.** An
earlier draft wrote that *"every round from 8 through 14 recorded the same sentence — 'No
production defect has been demonstrated.'"* **Measured: it does not.** That exact sentence
occurs at brief `:1051`, `:1119` and `:1179` — rounds 11, 12 and 13 only. Round 10 uses
different wording, and **round 14 carries no such sentence at all**. It is also the agent's
own cumulative summary line, not a reviewer verdict. Writing a quotation as if seven rounds
had recorded it, without grepping for it, is the defect class this whole sequence is about;
the correction is recorded rather than silently applied.

What the rounds DO support, checkably: **rounds 10-14 changed no production code and no
test** (the `git diff` above), and no round from 10 to 14 reports a defect in
`src/gzkit/content/**`. Their findings are about the evidence record's prose and the
classifier's own output. That, not the miscounted quotation, is what makes the standing
verdict's subject the commentary rather than the generator.

**What follows.** The classifier's classifications and totals — the 145-row census, the
`ANCHORED` / `CODE-VS-CODE` / `LITERAL-ONLY` split, and the disagreement with round 11's
`ANCHORED=121 CODE_OR_MIXED=20 FIXTURE_ONLY=4` — are **withdrawn from the acceptance
argument** and moved to § 8 as history. The artifact and every finding made through it are
preserved there unaltered, including the two open misclassification families. **No
regression test discovered through the review rounds is removed** — the tautology removal
(round 9), the contract-derived oracle (rounds 8–9), the persisted-candidate test (rounds
4–5) and the fence-scanner tests (round 3) all remain in the suite, and § 6 exercises them.

**The acceptance argument is rebuilt in § 6 on direct, requirement-specific evidence.**

## 6. Direct evidence, by requirement — observed 2026-09-08

**Binding:** revision `1cef5d80`, working tree carrying this session's evidence-record edits
only (`git diff --stat -- src tests features` empty), Python 3.13, Darwin 25.6.0. Every
block below is pasted from a run made in this session.

### 6.1 The required proof channel, re-run

```text
$ uv run -m unittest tests.content.test_composer tests.content.test_lineage \
    tests.content.test_ownership tests.commands.test_content_compose
Ran 191 tests in 0.261s
OK (skipped=4)                                                    REAL EXIT: 0

$ uv run gz validate --documents --req-kind-discipline \
    --invariant-coherence --rendition-floor-coherence
✓ All validations passed (4 scopes).                              REAL EXIT: 0

$ uv run -m behave features/content_compose.feature
1 feature passed, 11 scenarios passed, 102 steps passed           REAL EXIT: 0
```

Nine BEHAVIOR REQs carry `@covers` bindings across `test_composer.py`, `test_lineage.py`
and `test_content_compose.py`; `REQ-0.35.0-05-10` is STRUCTURAL-FENCE and correctly carries
none.

**A claim about the witness is corrected here.** An earlier draft wrote that
*"`--req-kind-discipline` passing is the mechanical witness that each REQ's declared kind
matches an admitted proof channel."* **That is false, and reading the validator shows it.**
Its BEHAVIOR arm is `src/gzkit/commands/validate_req_kind.py:72-81` in full:

```python
def _check_behavior_req(req_id: str, allowed_section: str, artifact: str) -> list[ValidationError]:
    if "tests/" in allowed_section:
        return []
```

It tests whether the literal string `tests/` occurs anywhere in the brief's `## Allowed
Paths` prose. It opens no test file and resolves no `@covers` decorator. For nine of ten
REQs the "witness" is one substring match against Markdown — **a presence check**, which
AGENTS.md names by class: *"A PRESENCE CHECK ANSWERS 'is something armed', NEVER 'did the
governed procedure run'."* Asserting a mechanism establishes a property without reading the
mechanism is the same defect rounds 10-14 kept finding, reproduced at the sentence this
section opens with.

**The decorator-resolving witness is `gz covers`, cited in § 3** — `covered_reqs: 9`,
`behavior_uncovered_reqs: 0`, the one uncovered REQ being the STRUCTURAL-FENCE. That is what
binds REQs to tests here. `--req-kind-discipline`'s contribution is narrower and worth
stating exactly: it confirms each REQ carries exactly one kind tag and that a BEHAVIOR REQ's
brief declares a `tests/` path at all.

### 6.2 The generator (REQ-01, -02, -03)

```text
$ uv run gz content compose AGENTS.md --consumer root
Candidate: .gzkit/renditions/AGENTS.md/root.candidate.md
Lineage:   .gzkit/renditions/AGENTS.md/root.candidate.lineage.json
Byte evidence: invariant=24350B compressible=354B→354B total=31244B setpoint=lite
                                                                  REAL EXIT: 0
```

Measured against the live 31,244 B candidate and the committed 47,851 B prior rendition by
a **published** measurer — `.gzkit/evidence/OBPI-0.35.0-05-live-artifact-probe.py`, which
carries its own scope limits in its module docstring and is `ruff`-clean. Reproduce:

```bash
uv run gz content compose AGENTS.md --consumer root
uv run python .gzkit/evidence/OBPI-0.35.0-05-live-artifact-probe.py
```

Round 12's finding — *classifications published without their measuring artifacts* — applies
to §§ 6.2-6.6 exactly as it applied to the classifier, and an earlier draft of this packet
published these figures with no program behind them. Corrected. Observed output:

```text
SECTIONS 22   OWNED 12   UNOWNED 10
UNOWNED_SLICES_PRESENT_VERBATIM_IN_PRIOR   10/10   missing=[]
CORPUS all=95 live=71 retired=24
LINEAGE_CITES 71 ids;  retired_ids_cited=[]        CITED_IDS_ALL_LIVE=True
CITED_ENTRY_TEXT_INSIDE_ITS_OWN_SLICE      71/71   misplaced=[]
DUPLICATE_ID_EMISSIONS                     []
```

*Establishes:* every one of the 10 unowned sections' candidate bytes occurs byte-verbatim in
the prior rendition (REQ-02); all 71 live entries are cited and **none of the 24 retired
entries is cited anywhere in the lineage** (REQ-03); every cited entry's text is present
inside its own section's slice, and no id is emitted twice (REQ-01, and the standing
duplicate-emission fence).
*Does NOT establish:* which entry supplied which byte where several address one section.

### 6.3 Persisted lineage (REQ-04, -05)

Read back from the two files on disk, not from an in-memory result:

```text
PARTITION contiguous_from_zero=True  gaps=[]  overlaps=[]
          covers_end=True (cursor=31244 == len(candidate))
UNOWNED_WITH_ENTRY_IDS []                      (REQ-04: must be empty)
INDEPENDENT_SCAN heads=22  production_span_starts=22  AGREE=True
```

*Establishes:* the persisted spans form a complete, disjoint, contiguous-from-zero partition
covering exactly the persisted candidate's byte length, with `entry_ids` empty for every
unowned section (REQ-04).

**An earlier draft claimed this partly closes REQ-02's shared-parser bound. WITHDRAWN — the
input does not exercise the arm the claim rested on.** The probe reports its own control:

```text
FENCE_ARM_EXERCISED=False (heading_shaped_lines_inside_fences=0)
fence_blind_control_agrees=True
```

Measured over both the 31,244 B candidate and the 47,851 B prior rendition: **zero
heading-shaped lines occur inside a fence.** The three balanced fence pairs in the candidate
enclose no `#`-prefixed line. A three-line fence-**blind** scanner returns the identical 22
offsets, so `AGREE=True` cannot distinguish production's fence-aware walker from a
fence-blind one, and the word "fence-aware" was doing rhetorical work the measurement did
not support.

*What the line establishes:* production's 22 span starts agree with an independently written
scanner on this document — a weak corroboration that the offsets are not arbitrary.
*What it does NOT establish:* anything about fence handling, span ENDS beyond what contiguity
forces, or REQ-02's correlated-shift bound, **which stands open and undiminished** (§ 4 row
05-02; § 7 item 7). This is round 6's finding at a new site — *"it ran the fence-disabling
defect against a fixture carrying no fence, so the agreement tests survived because nothing
touched them"* (brief `:724-733`) — and it is recorded rather than deleted for that reason.

### 6.4 Accounting (REQ-06)

```text
invariant_bytes            24350
compressible_bytes_before  354
total_bytes (candidate)    31244
RETIRED formula total-invariant  ->  6894      (19.5x the input)
SHIPPED compressible_bytes_after ->  354
after <= before              -> True
after != total - invariant   -> True
```

*Establishes:* the shipped attribution counts only compressible-tier bytes actually emitted,
satisfies `after <= before`, and is demonstrably not the retired `total - invariant` formula.

**A stale illustrative figure, disclosed rather than repaired.** REQ-0.35.0-05-06's own text
and Requirement 7 both cite the retired formula as yielding **22,378** against an input of
354 — a 63x inflation. Measured today the retired formula yields **6,894** (19.5x).

**Its provenance could not be established, and a first attempt to establish it was wrong.**
This packet initially stated that 22,378 "reconciles to the committed rendition (47,851 B)
at an invariant total of 25,473 B" — an inference drawn from one arithmetic identity
(`47851 − 22378 = 25473`) and written as if observed. It was then tested against the corpus
log and **falsified**: recomputing the effective invariant total at all 20 revisions of
`.gzkit/corpus/AGENTS.md.jsonl` from 2026-06-13 to 2026-09-07 yields `47851 − invariant`
values of 23,501 / 26,637 / 28,436 / 29,798 / 30,805 / 28,324 / 30,557 / 32,070 / 33,119 /
34,567 / 36,087 / 37,858 / 38,812 / 38,239 / 38,959 / 38,589 / 38,959 / 39,175 / 44,797 /
45,098. **None is 22,378.** The figure may reconcile against a prior rendition of a
different size, which was not recovered. Recorded rather than deleted because writing an
inference as an observation is the exact defect class this OBPI's review sequence is about,
and this instance was authored, caught and corrected inside the correction itself.

The magnitude was never a constant in any case: it is whatever `total − invariant` is for
the document it is applied to, at the time. **The
REQ's binding clause is unaffected and holds under either reading** — `after` counts only
emitted compressible bytes, is `<= before`, and is never `total − invariant`. Recorded here
per `.claude/rules/governance-core.md`: *a value written in a Markdown doc is ILLUSTRATIVE,
never authoritative.* The REQ text is NOT edited — `## Acceptance Criteria` is outside this
brief's Allowed Paths, which admit only "this brief's evidence sections". Carried to § 7.

### 6.5 Failure behavior (REQ-05, -07, -09)

```text
$ uv run gz content compose AGENTS.md --consumer claude          REAL EXIT: 1
Error: Surface 'AGENTS.md' (content type 'AgentContract') declares no route to consumer
'claude'; declared routes are ['root']. Declare the route in content_type_routes
(data/vendor-manifest.json) before generating a candidate for 'claude'.

$ uv run gz content compose AGENTS.md --consumer codex           REAL EXIT: 1
Error: ... declares no route to consumer 'codex'; declared routes are ['root']. ...
```

*Establishes:* both off-route consumers are refused with a named, actionable refusal, and
the refusal is attributable to the route gate — it names the gate, the declared route set
and the recovery surface (REQ-05).

Inflation guard, driven by attributing invariant-tier entries as compressible:

```text
REFUSED: compressible_bytes_after (24704) exceeds compressible_bytes_before (354).
Compression cannot add compressible bytes, and an inflated figure is a witness that
cannot fail (ADR-0.35.0 REQ-0.35.0-05-07). ...
names both figures: True
```

*Establishes:* the guard raises rather than clamping or printing, and its prose names both
figures and the recovery action.

**An earlier draft said "fails closed on real data." WITHDRAWN — the attribution driving it
is synthetic and unreachable through the generator.** REQ-05-07's literal text says *"when
**the generator** runs, then it FAILS."* Reading `composer.py:468`, `emitted_compressible` is
extended only from `section_entries`, itself filtered from `effective.entries` (`:463`);
`_byte_evidence` computes `before` over that same effective compressible set (`:84`) and
dedupes `after` by id (`:95-101`); section ids cannot repeat (`ownership.py:328-329`
refuses collisions). Therefore `after ⊆ before` **structurally**, and the guard at
`composer.py:103` **cannot fire on any input reachable through `generate_candidate`.**

The probe drives it by attributing invariant-tier entries as compressible — an input the
generator cannot construct. The covering test `test_composer.py:283-323` likewise calls the
private `_byte_evidence` directly with a non-corpus `foreign_entry`, and mutation row 7
kills against that same direct call. So the proven subject is **the private helper's
defensive assertion**, not the generator. Carried as an open finding (§ 7 item 8); not
repaired here, because changing the covering test is OBPI implementation work.

Duplicate live byte-identical invariants (REQ-09) are refused before any candidate is
written; proven by `TestDuplicateLiveInvariantRefusal` and mutation row 9
(`len(group) <= 1` → `len(group) <= 2`, an `assertion`-class kill). It is not exercised
against the live corpus here because doing so would require appending a deliberate duplicate
to the append-only corpus log.

### 6.6 Determinism (REQ-08)

```text
$ uv run gz content compose AGENTS.md --consumer root   (run 1, bytes captured)
$ uv run gz content compose AGENTS.md --consumer root   (run 2)
candidate: BYTE-IDENTICAL
lineage:   BYTE-IDENTICAL
```

*Establishes:* both persisted artifacts are byte-identical across two runs on the live
corpus — the property OBPI-0.35.0-07's single-attestation-over-N-consumers ruling rests on.
*Does NOT establish:* an external oracle. Agreement of two runs of the same code IS the
REQ's semantic, and § 4's row for 05-08 states that bound.

### 6.7 The structural fence (REQ-10)

```text
$ uv run python -c "from gzkit.content.rendition_store import RenditionProvenance; ..."
frozen= True  extra= forbid
FIELDS: ['algorithm', 'attestation_text', 'attestor', 'committed_ts',
         'corpus_entry_count', 'corpus_fingerprint', 'rendition_fingerprint']
lineage-bearing fields: []
```

Parent ADR carries BI-03 at
`ADR-0.35.0-canon-entry-corpus-landing.md:198-205`, closing *"Proves REQ-0.35.0-05-10."*
Model state matches the fence today; the fence itself audits at ADR closeout, not here.

### 6.8 Falsifiability — the per-REQ negative controls stand unchanged

The brief's `#### Falsifiability` table remains the strongest evidence that these tests
BITE: 18 one-edit mutations, each violating a named requirement, all 18 `assertion`-class
kills on green baselines. It is untouched by this correction.

**Three qualifications, because an earlier draft endorsed it without them:**

- *"each run against only that REQ's own covering test"* is not literally true of every row.
  The transcript shows rows 15 and 17 each failing TWO tests (brief `:409`, `:411`).
- *"requirement-specific by construction"* has a known counter-example the brief itself
  records: **row 16's kill is attributable to `load_declaration` refusing an undeclared
  section, not to REQ-04/05** (brief `:387`, `:816-824`), and round 6 classified it MISSING
  PROOF. The row is retained as a real kill and explicitly does not evidence the persisted
  oracle's incremental strength.
- The table's **line citations have drifted** — see § 7 item 9. The outcomes were observed;
  the anchors were not re-measured.

Its disclosed limits are reproducibility (§ 7 item 2) **and** these three.

## 7. Unresolved findings affecting these requirements or their proof

Stated in full. None is withdrawn. Items 7-16 were found by the independent review of THIS
corrected argument (§ 9) and were recorded, not repaired: repairing a test or a production
writer is OBPI implementation work, which under the IRON LAW only the operator initiates.

> **SUPERSEDED IN PART, 2026-09-08 — the operator initiated the repair.** Items 7, 9, 10,
> 11, 12, 13 and 14 are now REPAIRED; items 8, 15 and 16 were confirmed from source and
> ESCALATED unrepaired as operator rulings (8 and 15 are design questions, 16 is a routing
> question). The authoritative record of each disposition, the mutation sweeps that prove
> the repaired tests can fail, and the re-run Stage-3 receipts are in the brief's
> `### Step 4b` section under **Round 15 repair pass**. The items below are preserved as
> the review found them; read them against that record, not as current state.

1. **`[open]` GHI #983 — 10 of 12 corpus-owned sections carry no covering corpus content.**
   Materializing from the live corpus yields 31,244 B against the 47,851 B committed
   rendition, a −16,607 B delta. Operator ruled 2026-09-07 that the generator stays faithful
   to its brief and the finding routes to a GHI. **The largest open item, and it is about the
   DECLARATION, not this deliverable** — but any reader of § 6.2 should know the candidate is
   35% smaller than the committed rendition for this reason.
2. **`[open]` 10 of the 18 mutation rows are not reproducible from the record.** Rows 1, 3,
   4, 5, 6, 7, 9, 10 carry exact find→replace strings; rows 2, 8, 11-18 carry prose only, and
   every row bearing an isolation claim is in the non-reproducible set. Outcomes were
   observed when the sweeps ran; this session did not re-run them.
3. **`[open]` REQ-05-06 and Requirement 7 carry a stale illustrative figure** (22,378 / 63x;
   measured today 6,894 / 19.5x, and the 22,378 provenance could not be recovered — § 6.4).
   Binding clause unaffected. Not repaired: `## Acceptance Criteria` is outside the evidence
   sections this brief's prose gloss admits. **Operator's call** — GHI or scoped amendment.
4. **`[open]` `.gitignore:75` ignores `.gzkit/renditions/**/*.candidate.md` but not
   `*.candidate.lineage.json`.** A compose run leaves the staged lineage sidecar untracked and
   offered for commit while its paired candidate is ignored. `.gitignore` is outside Allowed
   Paths. No prior GHI (searched 2026-09-08; open queue 40 by search `total_count`).
5. **`[disclosed]` Semantic falsifiability is proven per REQUIREMENT, not per assertion.** The
   18 negative controls prove each REQ's covering test fails when that REQ is violated. No
   per-assertion mutation was run.
6. **`[open, auxiliary]` Two classifier misclassification families remain open** — 2 inline
   `str(ctx.exception)` rows and 6 loop-binding rows, root-caused to the taint rule walking
   `ast.Assign` and never `ast.For` (`assertion-audit.py:97`). Preserved in § 8. **These
   affect no requirement above.**

### Found by the independent review of this corrected argument

7. **`[open, MAJOR]` REQ-02's correlated-shift bound has no working remedy, and the finding
   that says so was never carried forward.** § 4's row 05-02 names
   `test_content_compose.py:457` as the parser-independent structural check answering that
   bound. Round 11 measured (brief `:1033`) that **`:457`'s contiguity check is anchored only
   on its first iteration** — `cursor = 0` anchors iteration 1, then `cursor = end` is taken
   from the lineage's own values, so every internal boundary is lineage-vs-lineage. Verified
   by reading `test_content_compose.py:454-460`. That finding appears in neither the earlier
   § 7 nor § 8; it is **not** a classifier finding, so "the classifier thread is out of scope"
   never covered it. Both reviewers found it independently. **REQ-02's bound therefore stands
   open with no compensating check identified.**
8. **`[open, MAJOR]` REQ-05-07's guard cannot fire through the generator.** `after ⊆ before`
   holds structurally on every input `generate_candidate` can construct; the covering test and
   mutation row 7 both exercise the private `_byte_evidence` directly with a non-corpus entry.
   The REQ says *"when the generator runs."* See § 6.5.
9. **`[open]` The falsifiability table's line citations are stale.** Row 16 cites `:541` as
   "the exit-code assertion" — `:541` is now a fixture literal, `:552` is the exit-code
   assertion, the literals are at `:563`. Rows 17/18 cite `:367`/`:373`; `:367` is a `def`
   line, `:373` an assignment, and the assertions are at `:376`/`:382`. The brief at `:944`
   claims citations were anchored to the revision measured — applied to the prose, **not to
   the table cells**, which carry bare numbers. This is verbatim the recurrence round 8 found
   (brief `:892-895`: *"the prose was, the cell was not"*).
10. **`[open, MAJOR]` `tests/content/test_ownership.py:384-409` exercises zero production
    code.** `test_contract_literals_reject_a_roster_a_fence_blind_parser_would_produce`
    derives `broken_ids` test-locally from a class constant and compares it against another
    class constant. It calls nothing from `gzkit.content`. Under `.gzkit/rules/tests.md`
    § The discriminator — *"if the production code's behavior changed but its text did not,
    would this test fail?"* — the answer is no, under every possible change. Round 9 removed
    the literal tautology `assertEqual(broken_ids, broken_ids)` from this test's body and left
    the surrounding test, which still asserts only facts about its own fixture: **the instance
    was removed, the class was not.**
11. **`[open]` `tests/content/test_composer.py:877-886` — two assertions dominated by a
    production guard on the same object.** `generate_candidate` cannot return without passing
    `_refuse_generated_lineage_drift` (`composer.py:479`, which computes the same
    `iter_section_boundaries` mapping and raises on mismatch) and `assert_complete_partition`
    (`:482`). Both assertions re-evaluate those guarantees; neither can fail while the guards
    stand.
12. **`[open]` `tests/content/test_composer.py:620-622`** asserts `isinstance(byte_span, tuple)`
    and `len(byte_span) == 2` on a Pydantic `tuple[int, int]` field with `frozen=True` and a
    field validator — unconstructible otherwise. These are two of the six rows round 14 flagged
    as loop-binding *misclassifications*; the thread classified them and never asked whether
    they can fail.
13. **`[open]` `tests/content/test_composer.py:509-516`** computes `expected` as
    `prior_bytes[boundary.start:boundary.end]`, which is **literally the expression production
    evaluates** at `composer.py:456`. § 4's disclosure ("located by the same production
    parser") is true but understates: it is the same expression, not merely a shared locator.
14. **`[open, MAJOR]` `src/gzkit/content/lineage.py:164` uses `write_text` where its sibling
    uses `write_bytes`.** `src/gzkit/commands/content/compose.py:118-123` carries a five-line
    comment explaining that the candidate must be persisted with `write_bytes` because
    `write_text` opens with `newline=None` and performs LF→CRLF translation on Windows —
    round 1's finding 3. `save_candidate_lineage`, the paired writer for the same staged
    artifact pair created under the same OBPI, still calls `path.write_text(...)`. No test
    guards it. JSON tolerates CRLF so there is no current correctness break, but this is
    AGENTS.md § DO IT RIGHT #1 — *"Fix the class of failure, not the instance"* — with the
    class named in the sibling file's own comment. **§ 6.6's "lineage: BYTE-IDENTICAL" is
    therefore platform-local**, and OBPI-0.35.0-07 will publish this artifact.
15. **`[open]` Stated-rationale contradiction in the generator.**
    `_refuse_unknown_section_addressing` (`composer.py:271-297`) refuses an entry addressed to
    an undeclared section, reasoning that *"silently omitting the entry would drop it from both
    the candidate text and its lineage with no trace."* A **compressible** entry addressed to a
    section declared `unowned` is dropped from both with no trace and is accepted — counting
    toward `compressible_bytes_before` and nothing else. Only the invariant tier is caught, by
    `assert_invariant_verbatim` (`composer.py:490`). Two paths, opposite rationales, same
    observable outcome. Whether this is a defect is a design question for the operator.
16. **`[open, advisory]` Size guidance.** `generate_candidate` (`composer.py:371-506`) is ~100
    executable lines carrying 14 numbered contract steps against `.claude/rules/pythonic.md`'s
    ≤50 guidance; `src/gzkit/content/ownership.py` is 2,448 lines against ≤600, with
    `load_declaration` (`:624-851`) at ~170 body lines. Both files are in Allowed Paths.
    Guidance, not a gate.

### What the review did NOT reach — do not read silence as clean

The quality review reports leaving unread: `features/content_compose.feature` and its steps
(the Gate 4 surface § 6.1 cites), `docs/governance/evidence-record-contract.md`,
`src/gzkit/content/rendition.py` / `rendition_store.py` / `corpus_store.py` / `tier_policy.py`
/ `models/corpus.py` (including `RenditionProvenance`, which REQ-05-10's fence is about, so
§ 6.7's field listing is unverified by that reviewer), `ownership.py:1149-2448`, and
`test_ownership.py:517-3160`. It executed nothing — every figure in §§ 2, 3, 6 is unverified
by it beyond internal arithmetic consistency.

## 8. Auxiliary diagnostic — preserved as history, NOT acceptance evidence

This section is a **summary**; the artifacts it names are verbatim and the full round
records live unaltered in the brief at `### Step 4b`. **None of it is offered as proof of any
REQ**, and no acceptance claim in §§ 4, 6 depends on it. (An earlier draft called this section
"retained verbatim in substance," which is self-contradictory — a summary is not verbatim. The
verbatim record is the brief's.)

**A routing defect in this section, found by review and corrected.** The sort applied here was
*"was it found via the classifier thread"*, when the rule that matters is *"does it bear on a
live acceptance claim."* Round 11's finding that **`test_content_compose.py:457` is anchored
only on its first iteration** failed that sort: it was compressed away as classifier-thread
history while §§ 4 and 6.3 leaned on that very line as REQ-02's compensating check. It is now
carried as § 7 item 7. Any other round-10-to-14 finding bearing on a live claim belongs in
§ 7, not here.

**Artifacts, unaltered and still published:**
`.gzkit/evidence/OBPI-0.35.0-05-assertion-audit.py` (the classifier, carrying its population
and classification rules in its docstring) and its captured output
`.gzkit/evidence/OBPI-0.35.0-05-assertion-inventory.txt` (sha256
`0e9e04a087db7d5316262a7a7bd075b2ea175de6fc8e0f5f7a7d69cb28cf4ed4`), one row per assertion
with file, line, method, enclosing test, class and complete untruncated source. Reproduce
with `uv run python .gzkit/evidence/OBPI-0.35.0-05-assertion-audit.py`.

**Census (population size only).** 145 `self.assert*` calls on lines added by
`git diff -U0 c9e62790..HEAD` across the four test files — `test_composer.py` 64,
`test_lineage.py` 13, `test_ownership.py` 33, `test_content_compose.py` 35. Independently
reproduced by round 10 (`TOTAL self_assertions= 145`) and round 11 (`TOTAL 145`,
cross-checked `489 − 344 = 145`). *Establishes the size and membership of a population under
a stated rule; establishes nothing about any requirement.*

**Tautology scan.** Zero syntactic self-comparisons; reproduced by rounds 10 and 11.
*Establishes that no assertion compares a value to itself syntactically. Does not establish
semantic falsifiability* — that is § 6.8's job, done per requirement.

**Classification — WITHDRAWN from the acceptance argument, kept here with its known errors
named.** The heuristic operand-tracing split (`ANCHORED=103 CODE-VS-CODE=17 LITERAL-ONLY=25`)
disagrees with round 11's independent tracing (`ANCHORED=121 CODE_OR_MIXED=20
FIXTURE_ONLY=4`). Both sum to 145; neither is claimed correct. Of the 25 LITERAL-ONLY rows,
**8 are known misclassifications** — 2 inline `str(ctx.exception)` (`:756`, `:1137`) and 6
loop-binding rows (`test_composer.py:621/:622`, `test_content_compose.py:289/:290/:291`,
`:457`), root cause the `ast.Assign`-only taint walk at `assertion-audit.py:97`. The
remaining composition: 13 `assertRaises` (one operand, an exception class — not a value
comparison), 4 genuinely literal or self-fixture. Refusal-message checks are 18 rows in
ANCHORED, not LITERAL-ONLY; operands are checked symmetrically, not positionally.

**Findings made through this thread, preserved:** round 10's census miscount and `:939`/`:940`
misattribution; round 11's non-reproducing totals; round 12's missing measuring artifacts,
six 150-character truncations, and the auto-enforcement/compliant-authoring conflation;
round 13's symmetric-rule and false-characterisation findings; round 14's corrected
composition and the located `ast.For` gap. Also preserved: the agent's own `awk`
byte-versus-character verification error, and the classifier's shipped `BLE001`/`B023`
defects (fixed; regenerated inventory byte-identical, so round 12's and 13's readings stand).

**Two withdrawals stand.** *"The CLASS of defect is removed here rather than the instance"*
and the claim that publishing raw artifacts made later findings *"structurally impossible"*
are both WITHDRAWN as untested claims about a remedy. Operator ruling 2026-09-08, verbatim:
*"A command can faithfully reproduce a tautology or measure the wrong thing. Interpretation
still needs independent review."*

**The root this thread finally surfaced,** and the reason it is filed here rather than in the
acceptance argument: an auxiliary diagnostic was allowed to become the subject of review, and
its accuracy became a de facto prerequisite for accepting a generator it never measured.
Operator ruling 2026-09-08: *"Stop making the accuracy of optional diagnostic commentary a
prerequisite for accepting the generator."*

## 9. Stage 4b — independent review of this corrected argument

Two independent read-only reviewers were dispatched against the corrected argument and the
brief's Evidence sections, one on spec compliance and one on evidence architecture and test
quality.

**Both returned `CONCERNS`. Both confirmed the § 5 determination** — *auxiliary, not required
proof* — the spec review checking all four grounds independently and reporting *"No REQ
arguably requires assertion classification"*, and **both confirmed the acceptance bar was not
lowered**: no test deleted, the 18-row control table intact, § 6.1 running a superset of the
brief's declared verification (4 modules / 191 tests against 3 declared; the full 11-scenario
feature against the 5 tagged).

**Both also refuted parts of the corrected argument itself, and every accepted finding was
verified against source before adoption** — round 13's lesson that a reviewer's
characterisation is evidence to verify, never a fact to relay. Accepted and repaired above:
the false *"every round from 8 through 14"* attribution (§ 5), the false claim that
`--req-kind-discipline` witnesses the proof channel (§ 6.1), the `INDEPENDENT_SCAN` fence
overclaim (§ 6.3), *"fails closed on real data"* for a guard unreachable through the generator
(§ 6.5), the blanket endorsement of the mutation table (§ 6.8), the `refuted` verdict
miscount, the self-undermining ground 3, the empty REQ-04 bound cell, the unpublished probes
(now `.gzkit/evidence/OBPI-0.35.0-05-live-artifact-probe.py`, `ruff`-clean and carrying its
own scope limits), and § 8's routing defect. Accepted and carried as open findings: § 7
items 7-16.

**The reviewers' shared verdict on the root, recorded unmodified:** *"the rebuilt argument
reproduces the discipline defect it was rebuilt to escape"* — a mechanism named as
establishing a property without the mechanism being read (§ 6.1), and a measurement whose
relevant arm was never exercised (§ 6.3). Both instances were in the NEW material, not the
withdrawn material. The probe now prints `FENCE_ARM_EXERCISED` as part of its own output so
that specific failure cannot recur silently.

**Not re-reviewed:** these corrections were made after both reviewers finished, so no
independent round has seen the current text. Closure is demonstrated, never round-counted.

**No attestation is solicited. Stage 5 is not entered.**
