# ADR-0.35.0 — Design Forcing Functions

Tier 2 of the `gz-adr-create` Step 0 interview. Agent-drafted against session
evidence, operator-audited (AGENTS.md § OPERATOR ECONOMY, operative claim 4).
The `gz interview adr` schema carries no keys for these, so they are preserved
here as a permanent artifact alongside the ADR and its `INTERVIEW_ANSWERS.json`.

Every answer is grounded in a measurement or a `file:line`. Generic answers are
a failure of this exercise.

---

## 1. Pre-Mortem (Klein) — ranked by likelihood

**1. The ratchet becomes a ceiling.** *Most likely, because it requires nobody
to do anything wrong.* Eighteen months out the unowned total reads 22,100 B —
278 B of movement — while "31.2% witnessed" has been printed in Fidelity
Assertions forty times, laundering a mostly-unwitnessed contract as a governed
one. The design as ruled has no cadence, no owner, and no scheduled floor-raise.
Decrease-only permits never decreasing.

**2. Owned-section fail-closed becomes the thing agents route around.** The
in-repo precedent already exists: `rendition_floor_coherence.py:87-91` ships a
staged-warn mode, and `_checkpoint.resolve` downgrades it inside the MX hangar.
The instant a legitimate operator edit to an owned section cannot round-trip
through the corpus, the cheapest recovery is "mark the section unowned" — which
the design permits and the ratchet merely counts. Ownership deflates silently
and coverage falls without a single failing gate. *Mitigation shipped:* the
attested ratchet-raise path (Gate 5, same shape as retire). It is a mitigation,
not a guarantee.

**3. `effective_corpus()` becomes a second source of truth.** The fold sits
between the raw log and every consumer — `tier_policy.invariant_entries()`,
`rendition_floor_coherence.py:66`, `composer.py:59`. `load_corpus` returns the
raw corpus today, so a consumer that never gets the fold is a one-line omission.
Symptom: renditions that pass floor coherence while omitting canon, or a retired
entry resurrected by whichever consumer still reads raw. **Worst detection
latency of any failure here — the gate goes green.**

**4. The bundled attestation is repudiated as a whole.** One Gate 5 over N
consumers is deliberate. When an operator later finds `claude.md` landed
correctly and `codex.md` did not, the shared `landing_id` means one attestation
covered both, and `gz obpi repudiate` (ADR-0.0.71) has no per-consumer
granularity. Moderate likelihood, high blast radius.

**5. CLAUDE.md becomes the escape hatch and the ADR becomes performative.**
`sync_claude_md` renders from a template plus `.gzkit/agents.local.md`, entirely
outside the corpus. This ADR does not close it. Agents that hit the fail-closed
AGENTS.md path write doctrine into `agents.local.md` instead. In eighteen months
the operative contract lives in the ungoverned file and the governed one is a
museum. Lowest likelihood — and the only scenario where the whole ADR is
retrospectively pointless. Named in § Consequences by operator ruling.

---

## 2. What Would Have to Be True (Martin)

### For Approach A to be right

- **a1.** Section boundaries are stable enough that ownership is a durable
  property. AGENTS.md has 22 H1/H2 headings today; renaming one orphans its
  ownership declaration and its lineage entries.
- **a2.** The 8 corpus-addressed sections are the *high-value* ones. **← SHAKIEST.**
- **a3.** Unowned carry-forward is byte-stable, so a generator carrying 22,378 B
  verbatim still satisfies `gz validate --invariant-coherence` (which
  byte-compares the re-render against committed AGENTS.md). Mechanically
  checkable; low risk.
- **a4.** Someone actually drives the ratchet down. Not technical —
  organizational, and the design supplies no forcing function.

**Why a2 is shakiest.** The section histogram is an accretion curve, not a
curation:

```
behavior-rules                  18
operator-doctrine-verbatim-canon 10
do-it-right-craftsmanship-maxim  10
prime-directive-ownership         8
attestation                       2
governance-doctrine-surfaces      1
obpi-acceptance-protocol          1
defect-fix-routing                1
```

Coverage is concentrated where someone happened to run `gz content remember`,
not where the contract is load-bearing. Three sections are witnessed by a single
entry. The published number reads "8 of 22 sections" while functionally being
**four sections plus three tokens** — and the fail-closed gate over those three
protects almost nothing while making the coverage figure look twice as strong as
it is.

### For Approach B (total backfill) to have been better

- **b1.** The remaining 22,378 B is genuinely *addressable* — decomposes into
  entries with real provenance and a real witness. It largely does not: gate
  covenant table, lane rules, kinds table, control-surface block. These have no
  operator utterance behind them; backfilling fabricates `origin`/`witness`.
  **B fails here, and this is the decisive argument.**
- **b2.** One-shot backfill costs less than N incremental attestations. Given the
  single-attestation ruling, this is **true** — B's attestation cost is *lower*.
  The intuition that B is attestation-expensive is wrong; its cost is entirely b1.

**The honest case for B, on the record.** A's failure mode (a permanent 31.2%)
is *invisible* and requires no error by anyone. B's failure mode (fabricated
provenance) is at least *legible in the log*. A trades a visible defect for an
invisible one. It remains the right call — fabricated witness fields would
poison the one artifact the whole system trusts — but the trade is named rather
than assumed away.

---

## 3. Constraint Archaeology

**Append-only — REAL by construction, NEVER TESTED IN ANGER.** Enforced
structurally: `Corpus.append` returns a new corpus (`models/corpus.py:60-62`),
`model_config = ConfigDict(frozen=True, extra="forbid")`, and `corpus_store.py`
has no delete path. The last "test" was `dc2bc605` — and that is **invalid as
precedent**, being a back-out of a same-session, never-composed, never-attested
append. Append-only has therefore never actually been tested against attested
canon. **This ADR is its first real test**, which is precisely why the tombstone
route is right and the delete route is not.

**invariant/compressible tier split — ASSUMED, and currently degenerate.**
50 invariant, 1 compressible. A dial with one notch on one side is not a dial.
`composer.py:52` resolves a setpoint via `temperature_for`, and `codex.md` is
13,606 B against claude's 31,990 B — a real 57% reduction — but the declared
compressible content it is nominally operating on is **354 bytes**. The
reduction is not produced by tier policy; it is produced by the agent's freehand
judgment (`composer.py` docstring line 6). Last tested: never. **No test would
fail if every entry were marked `invariant`** — which is nearly the state today.
The constraint most worth re-examining; forced onward rather than fixed here.

**heavy/lite setpoint — INHERITED, real in effect, unfalsifiable as policy.**
Inherited from `vendors.py`/`temperature_for`. The byte delta is genuine. But
nothing checks that a `lite` rendition is *sufficient* for its consumer, because
nothing plays `codex.md` back at all (`sync_surfaces.py:374-376`,
`governance/compose.py:28-29` both hardcode `("AGENTS.md", "claude")`). **A
setpoint with no playback cannot be wrong.** Checklist item 9 makes it
falsifiable for the first time — which is why codex playback belongs in this ADR
rather than deferred.

---

## 4. Assumption Surfacing

**Implicit and undocumented:**

- **`section` is the right ownership granularity.** The model carries a flat
  `section: str` (`models/corpus.py:43`) with `anchor: str | None` optional and
  largely unused. Ownership is declared at a granularity the model supports only
  weakly.
- **AGENTS.md's H1/H2 skeleton is itself canon.** Nothing witnesses the section
  *list*. A generator that materializes owned sections and carries the rest
  forward assumes the skeleton is stable and correct — but the skeleton has no
  entry, no witness, no tier. **It is the one part of the contract that is 0%
  governed and 100% load-bearing.**
- **"Owned" is surface-wide but materialization is per-consumer.** The corpus is
  per-surface; renditions are per-(surface, consumer) at different setpoints. An
  owned section rendered at `lite` and at `heavy` is not the same bytes. The
  design gets this right in the lineage map (`byte_span` is per-consumer) and
  loose in the declaration (ownership asserted once, surface-wide).
- **Retirement is per-entry-id, never per-text — and the reason must be
  written down.** It is right because six of the seven byte-identical groups
  cross section boundaries, so text-keyed retirement silently elects a section
  winner. Recorded so a future maintainer does not "simplify" it back.

**If the core assumption were false.** Suppose the corpus is a **witness log**,
not a source — a record of what was said, not the definition of what binds. Then
AGENTS.md is canon, the corpus annotates spans of it, and the correct gate
asserts every corpus entry still maps to a live span in the authored document —
the inverse of what this ADR builds.

**The measured evidence is genuinely ambiguous between these readings.** Zero of
50 invariant entries are absent from AGENTS.md; 31.2% of AGENTS.md is
corpus-covered. That shape — corpus ⊂ document, document ⊋ corpus — is exactly
what a witness log looks like. It is *also* what an under-populated source looks
like. **Operator ruled the source reading (2026-07-21), and it is stated
explicitly in § Decision rather than inherited silently** — because if it is
wrong, the ownership gate, the ratchet, and the generator all point backwards,
and nothing in the nine OBPIs would surface the error.

---

## 5. The 2am Operator Question

`gz content land` half-wrote the rendition set and died. What the design as
ruled does not provide:

- **A landing state file written before the first byte.** The shared
  `landing_id` is recorded in each *sidecar* — but sidecars are written alongside
  their renditions. A crash after `claude.md` and before `codex.md` leaves the
  two consumers with no common record that a landing was ever in flight. Needed:
  `landing_id`, intended consumer set, and corpus fingerprint persisted **first**,
  cleared **last**.
- **`gz content land --status <landing_id>`.** At 2am the operator needs "which
  consumers are on the new corpus fingerprint, which are on the old, which are
  indeterminate." Today the only tool is `rendition_exists` plus eyeballing
  mtimes — and mtime comparison is **precisely the fake witness**
  `rendition_floor_coherence.py:1-9` was filed against. Do not hand the operator
  the discredited instrument.
- **Non-destructive resume.** Re-running `land` must be safe against
  already-landed consumers. Atomic multi-write gives all-or-nothing *at write
  time*; it does not cover "process died cleanly after consumer 1 of 3."
- **Resume must NOT require re-attestation.** Gate 5 is on the corpus delta, not
  on the write. Resume reuses the recorded `attestation_text` and `landing_id`.
  If it re-prompts, the operator will `--force` past it at 2am and the
  attestation becomes theater — the exact failure AGENTS.md names.
- **A named rollback.** Committed renditions are single files at
  `.gzkit/renditions/AGENTS.md/<consumer>.md` with no prior-version retention.
  "Put it back" currently means `git checkout`. That may be acceptable — but the
  ADR should say so rather than leave the operator to discover it.

---

## 6. Reversibility

| Piece | Door | 12-month reversal cost |
|---|---|---|
| Renditions | **Two-way** | ~0. Regenerated artifacts; delete and recompose. |
| Generator, `land`, validator | **Two-way** | Low. Deletable code; the corpus survives. |
| Tombstones | **One-way** | The real cost — see below. |
| Ownership declarations | **One-way-ish** | Resolved by the attested raise-path. |

**Tombstones.** One-way by construction. Un-retiring means appending a *third*
row that retires the tombstone, which `effective_corpus()` must fold correctly.
The cost lives entirely in that fold's algebra: naive last-write-wins makes
un-retirement trivial but renders retirement history ambiguous; a strict fold is
correct but introduces a recursion. **The fold's algebra is specified in the ADR,
not deferred to OBPI-01.** It is the one genuinely irreversible commitment and
must not be left as a one-line phrase standing in for a design.

**Ownership.** Reversing owned → unowned is mechanically cheap but *increases*
the unowned total against a **decrease-only** ratchet. Resolved by operator
ruling: an **attested ratchet-raise path, Gate 5, the same shape as the retire
path**. Un-owning a section is the same act on the same kind of canon, so it
takes the same ceremony. Leaving it unstated would guarantee pre-mortem #2 —
*the undefined path is the one agents invent.*

**Overall:** two-way on everything that matters operationally; one-way on eight
tombstone rows and N ownership declarations that every future reader must fold
to interpret. Acceptable.

---

## 7. Scope Minimization

**Smallest version that delivers value: OBPIs 01 + 02 + 03.** Schema, withdraw
verb, retirements. That alone discharges GHI #635, removes the live
double-render, and — decisively — is the *prerequisite*: the byte-identical
pairs are invisible today only because `rendition_floor_coherence.py:72` is a
substring test. They become literal double-emissions the instant a generator
materializes. **Shipping 05 without 01–03 ships a regression.**

**At half the time, cut 04 and 06 — together, never separately.**

- Cutting **06** alone leaves ownership as a claim with no enforcement, which
  *is* pre-mortem #2. Worst possible combination.
- Cutting **04 + 06** reduces the ADR to: retirement + a generator that
  materializes what the corpus covers + `land` + playback. Coverage % remains
  *reportable* — it is computable without a declaration schema. What breaks:
  nothing is fail-closed over owned sections, so the seam stays advisory. That
  is honest and shippable, and `rendition_floor_coherence.py:87-91`'s
  staged-warn posture is direct in-repo precedent for landing a gate in warn
  mode first.

**Do not cut 05 or 07** — without the generator and `land`, OBPIs 01–03 are
schema with no consumer. **Do not cut 09** — codex playback is the only thing
that makes the `lite` setpoint falsifiable, and its cross-ADR coordination with
ADR-0.44.0 gets harder, not easier, if deferred into a window where that ADR has
moved.

---

## Closing — subsequent decisions this forces

1. **`ADR-pool.attested-record-edit-doctrine`** inherits a binding precedent
   whether or not it promotes. Named in `## Boundary Invariants` so the pool item
   inherits rather than re-litigates.
2. **CLAUDE.md's seam.** `sync_claude_md` renders from a template plus
   `.gzkit/agents.local.md`, outside the corpus entirely. Once AGENTS.md is
   corpus-materialized this is the only ungoverned agent-contract surface in the
   repo. Operator ruled: name it in § Consequences, forced onward as a follow-on
   ADR.
3. **The tier dial.** 50 invariant / 1 compressible is degenerate. Once ownership
   and coverage are mechanical, the unavoidable next question: what is
   `compressible` *for*, and should `lite` be produced by tier policy rather than
   agent freehand judgment (`composer.py` docstring line 6)?
4. **Ratchet cadence and ownership-raise ceremony.** Who drives 22,378 → 0, on
   what schedule, under whose attestation. Undecided ⇒ pre-mortem #1 is the
   default outcome.
5. **`.gzkit/rules/*.md` as corpus.** Eleven-plus rule files carry binding
   doctrine; `governance-core.md` carries `paths: "**/*"` and loads on every edit
   in every session. Agent-contract content with no corpus at all. Same question,
   larger surface.
6. **Per-consumer repudiation.** ADR-0.0.71 gives `repudiate` at OBPI
   granularity. One attestation over N consumers needs consumer-granular
   repudiation, or the bundle unwinds only whole.
