---
id: ADR-pool.controlled-language-for-control-surfaces
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.controlled-language-for-control-surfaces: Controlled Language for Control Surfaces

## Status

Pool

## Intent

Give the control-surface diet a **computable criterion for what counts as
directive prose**, so that trimming `AGENTS.md`, `CLAUDE.md`, and
`.claude/rules/**` stops being a judgment call made fresh each time.

The gap is stated in the chore's own posture. `instructions-files-diet` v3.0.0
"recommends rather than decides, consulting the operator before the first
edit" (`data/instructions_files_budget.json`, 2026-08-17 fifth ruling). That
consultation is correct and is not what this ADR proposes to remove. What is
missing underneath it is any measurable test for *"this sentence is narrative,
not directive"* — the distinction the chore exists to act on. Every existing
lever on these files is a **byte count**: the per-file budgets, the vendor cap
witness, the render-order remedy. None of them can see the difference between
600 bytes of binding rule and 600 bytes of rationale.

**Prior art: ASD-STE100 Simplified Technical English** (ASD, Issue 9,
2025-01-15) — a controlled language for aerospace maintenance documentation,
in continuous revision since AECMA's 1986 first issue. Its mechanism is three
constraints applied to instructional prose: a bounded approved dictionary,
one-word-one-meaning, and caps on sentence length. gzkit's per-turn contract
surface is instructional prose read under time pressure by a reader who
must not misinterpret it. The fit is close enough to be worth a destination.

### Measured warrant

**Both blocks below are dated records of a measurement, not authoritative
values** (`.gzkit/rules/governance-core.md` § Non-negotiable rules). Method:
strip fenced code, HTML comments, table rows, and inline code spans; split on
sentence-terminal punctuation followed by a capital, and on blank lines;
count word tokens matching `[A-Za-z][A-Za-z'-]*`. The measuring script was
run from a scratchpad and is **not committed** — re-derive before acting.

Record of 2026-08-18, across `AGENTS.md`, `CLAUDE.md`, and 26
`.claude/rules/*.md` files:

```
1,466 sentences   3,861 distinct word forms   1,788 used exactly once (46%)

most directive-shaped                mean   >20w   >30w
  changelog-release-notes.md         11.1     6%     3%
  gh-cli.md                          11.9     6%     0%
  chores.md                          10.6     9%     3%

most narrative-shaped
  governance-core.md                 22.0    45%    26%
  agents-md-map-doctrine.md          22.8    41%    27%
  tool-skill-runbook-alignment.md    25.2    60%    23%
  guardrail-feedback-prose.md        28.3    55%    41%
```

The distribution is the warrant, and it points the same way the diet chore
does: the files that are **purely directive already pass** a 20-word bar
without anyone having aimed at it, and the files that fail it are the ones
carrying version history and rationale — the material
`.claude/rules/agents-md-map-doctrine.md` § Invariant already says does not
belong on a per-turn surface. A sentence-length measure is therefore not a
new opinion about style. It is a **proxy for a distinction gzkit has already
ruled on and cannot currently see.**

Record of 2026-08-18, modal-keyword census over the same files:

```
MUST 36 · NEVER 14 · ALWAYS 5 · MUST NOT 3 · SHOULD 3 · MAY 2
```

Two readings, both load-bearing. First, modality is almost entirely
mandatory, while the binding-versus-advisory axis that
`docs/governance/advisory-rules-audit.md` actually scores is carried in
**prose** (`**(Advisory — no mechanical witness…)**`) rather than in
keywords. Second, `NEVER` and `ALWAYS` are performing `MUST NOT` and `MUST`'s
work under different names: four keywords, two meanings, no registry naming
which is canonical. That is a one-word-one-meaning violation in the strict
sense, sitting in the surfaces an agent reads every turn.

### Intake tests

Run against `ADR-pool.external-strength-absorption-doctrine`'s four binding
tests, since this is a borrowed external strength:

| Test | Result |
|---|---|
| Identity preservation | **Passes.** Adds a witness where a Judgment-class chore has none; strengthens no surface by weakening another. |
| Front door | **Passes.** Shorter directive prose lowers entry cost for a new adopter reading `AGENTS.md` cold. |
| Compounding loop | **Passes.** A terminology registry is a governed reuse surface; each ruling lands once and binds thereafter. |
| Mechanical witness | **Passes for three arms, fails for the fourth.** Sentence length, modal keywords, and term consistency are computable. The approved-dictionary arm is licence-gated — see § Decision constraint 2. |

## Decision

Deferred to post-1.0. Parked rather than folded into an active ADR because the
in-flight feature is `ADR-0.35.0-canon-entry-corpus-landing`, and *"only one
feature at a time, feature, finish, draw from pool"* holds. Promotion needs its
own operator ruling.

On promotion, build **five arms, in this order** — the ordering is the design,
because the cheapest arm attaches to a distinction gzkit already models and the
most expensive one is the only one that needs anybody's permission.

1. **Modal-keyword discipline (RFC 2119 / RFC 8174).** Declare the canonical
   modal set and reconcile `NEVER`/`ALWAYS` against `MUST NOT`/`MUST` — either
   collapsed, or ratified as gzkit-canonical synonyms with the mapping written
   down. Ranked first because it is small, free of licence encumbrance, already
   half-adopted, and lands on the **binding-versus-advisory axis the advisory
   scorecard already scores** rather than on a new one.

2. **Terminology registry (one-word-one-meaning).** A declared term → meaning
   map with forbidden synonyms, held to a **shrink-only disclosure baseline**.
   Structurally modelled on `.gzkit/chores/ledger-vocabulary-inertness` and
   `data/ledger_vocabulary_grandfather.json`, which already governs a
   vocabulary this exact way — including the honest framing that an entry
   records a *disclosed* absence, never a justified one. gzkit has scattered
   terminology rulings today (the transit/exchange/handoff fence; Gate 5
   versus corpus attestation; withdraw versus repudiate) with no registry
   holding them; this arm consolidates them rather than inventing them.

3. **Decrease-only ratchet on prose metrics.** Per-file mean sentence length
   and hapax count, recorded, may only decrease — modelled on
   `ADR-0.35.0` § Decision 3's decrease-only ratchet on unowned bytes. Chosen
   over an absolute threshold deliberately: a ratchet needs no ruling on
   whether 20 is the right number, and it cannot be satisfied by argument.

4. **Imperative-density measurement (absorbs GHI #579).** Count binding
   instructions per surface alongside sentence length, and hold the count in
   the same decrease-only ratchet as arm 3. #579 opened this axis on
   2026-06-03 against external evidence that instruction-following decays
   *uniformly by count* — every instruction followed slightly worse as the
   count rises — and recorded 375 lines / ~105 binding imperatives in
   `AGENTS.md` on that date (a dated record, not a current value; re-derive
   before acting). Its § Design questions name the open metric choice —
   binding-bullet count, imperatives per 1k chars, or classification-weighted
   count — and that choice is left to promotion rather than pre-empted here.

   **Absorbed rather than merely cited** (operator ruling 2026-08-19). The
   absorption is load-bearing, not administrative: each of arms 3 and 4 closes
   a failure mode the other has. A length ratchet alone is satisfiable by
   splitting one long directive into three short ones — mean sentence length
   falls while the instruction count the model actually pays for **rises**. A
   count alone has no definition of what constitutes one instruction, which is
   what arm 1's modal-keyword set supplies. Promotion inherits both arms or
   neither is sound. #579's own scope-boundary note stands unchanged:
   re-anchoring the budget unit cannot fold into `ADR-0.0.54`, and does not
   fold into it here either.

5. **Approved-word dictionary — GATED, not scheduled.** Blocked on the
   reproduction question in constraint 2. Do not begin this arm without an
   operator ruling; do not treat arms 1–4 as blocked by it.

**The chore is the wielding mechanism, never a per-turn gate.** The 2026-08-17
fifth ruling put control-surface size on a chore cadence precisely to stop
per-turn interruption — *"I can't be stopping to trim them at every turn"* —
and a language gate that fires on every edit would reintroduce exactly what
that ruling removed. Arms 1–4 produce **chore-time criteria and observational
witnesses**; `instructions-files-diet` consumes them. Any future draft that
routes these into per-turn `gz check` failure is re-litigating a settled
ruling and should be refused on that ground.

### Constraints already measured that bind any future implementation

1. **The invariant tier is out of scope by construction.** Invariant-tier
   corpus entries render verbatim under `--rendition-floor-coherence`; the
   operator's words are canon *because* they are unaltered. Rewriting them
   into controlled English destroys the property the floor exists to
   guarantee. This arm reaches the compressible tier and newly-authored rule
   prose, and stops there. The seam is clean because the corpus already
   models the distinction.

2. **The dictionary is licence-gated; the rules are not.** ASD-STE100 Issue 9
   § Copyright notices sets a default deny on reproduction or publication in
   whole or in part absent written ASD authority, then grants irrevocable
   free reproduction rights to eight enumerated categories. Category 8 is
   "Universities and research institutes for educational purposes" — a live
   question for this operator rather than a settled one, and note the grant
   is scoped *for educational purposes*, which a package distributed to
   arbitrary adopters may exceed even where the author is covered. What is
   **not** encumbered: applying the standard, and implementing its writing
   rules. A 20-word sentence cap is a fact about a rule, not ASD's expression
   of it, and a validator enforcing one reproduces nothing. Paraphrase in
   gzkit's own words is likewise clear; verbatim rule text is the line.
   Compiling the ~900-entry dictionary into `data/*.json` and shipping it on
   PyPI is the act that needs permission. Three clean paths exist: rely on
   category 8 if the operator judges it applies; write to an ASD officer,
   which the notice names as the mechanism; or substitute a public-domain
   list (Ogden's Basic English, 850 words; the VOA Learning English list,
   ~1,500) and treat the standard as doctrine rather than dictionary.

   **A fourth path, and the cleanest: an operator-installed lookup tool at
   authoring time.** `dfch/biz.dfch.AsdSte100Mcp` is an MCP server exposing
   `word_find`, `word_match`, `word_fuzzy`, `rules_find`, `rules_by_section`
   and similar over Issue 9, backed by `dfch/biz.dfch.AsdSte100Vocab`. gzkit
   would not redistribute anything: the operator installs the server, the
   chore consults it during a diet pass, and no dictionary enters `data/` or
   the wheel. This dissolves the redistribution question rather than answering
   it, which is why it ranks above the other three.

   **Surveyed 2026-08-19 and recorded as constraints, not as endorsements:**
   both `dfch` packages are **AGPL-3.0-or-later**, and gzkit is **MIT**
   (`pyproject.toml:16`, `License :: OSI Approved :: MIT License`). A runtime
   dependency on either is therefore **foreclosed independently of any
   copyright question** — AGPL copyleft would reach a distributed MIT package
   that gzkit cannot relicense. The separate-process MCP path is what survives
   that, and it survives because gzkit ships neither the code nor the data.
   Note also that both repos carry ASD's copyright notice verbatim alongside
   *"not affiliated with ASD; ASD does not endorse"* — they disclaim
   endorsement, they do not assert permission. **An upstream that ships the
   data does not transfer the right to ship it.** Depending on one inherits
   the unresolved question and adds a licence conflict; it does not resolve
   constraint 2.

3. **Trademark is a separate axis from copyright.** ASD-STE100 Simplified
   Technical English is an EU registered trademark owned by ASD. Describing
   gzkit prose as *written toward* the standard is nominative reference;
   describing gzkit as **STE-compliant** or **certified** claims something
   only ASD confers. Cheap at authoring time, expensive to retract from a
   published surface. This ADR's slug deliberately names the capability, not
   the standard, so the destination survives a change of source.

4. **No foreign-runtime prose linter.** Vale (Go), redpen and LanguageTool
   (Java), textlint / write-good / alex (Node) are the mature tools in this
   space; `proselint` is the Python option and is literary-style-oriented.
   Every named departure in `pyproject.toml` — networkx, tree-sitter, radon,
   lizard, cohesion — is a **Python library, measurement-only,
   adapter-confined**, with inline rationale citing its ADR. None of the
   prose linters fit that shape, and a foreign binary collides with
   `ADR-0.0.31`'s reproducible-delivery invariant. The checks gzkit actually
   needs are arithmetic over token counts; write them.

5. **Readability formulas are deltas, not gates.** Flesch-Kincaid, Gunning
   Fog, SMOG, Coleman-Liau, ARI are all computable in stdlib (syllable
   estimation is the only heuristic part; Dale-Chall additionally needs its
   public-domain 3,000-word list). They punish technical terms and reward
   short words, so they are weak as absolute thresholds and meaningful mainly
   as movement across a diet pass. Do not let one become a gate.

## Alternatives Considered

1. **Adopt ASD-STE100 wholesale, dictionary included.** Rejected on two
   independent grounds, either sufficient: the reproduction question in
   constraint 2 is unanswered, and the invariant tier could not comply
   without destroying the verbatim floor. Retained as the shape arm 5 takes
   *if* permission resolves.

2. **Vendor Vale or redpen and configure a style pack.** Rejected on
   dependency posture — see constraint 4. Reconsider only if a future
   requirement needs checks that are genuinely beyond token arithmetic
   (parse-tree-dependent style rules), and then as a named departure with
   the same rationale shape the existing five carry.

3. **LLM-as-judge conformance read via `gz content advise-rendition`.**
   Rejected **as the witness**, retained as a complement. `ADR-0.0.39`
   doctrine is advisory-never-gating, so a judge cannot discharge a
   Judgment-class rule into a Mechanical one — that is the whole point of
   the promotion. It can carry the conformance reading no metric captures,
   alongside arms 1–4, and its existing receipt path already works.

4. **Readability formulas alone as the criterion.** Rejected as primary; see
   constraint 5. A Flesch-Kincaid floor on `.claude/rules/**` would flag
   correct technical prose and pass vacuous prose, which is the failure mode
   `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT operative claim 3 names.

5. **POS-tagging via spaCy or NLTK for active voice and noun-cluster caps.**
   Rejected. Heaviest dependency in the survey, worst fit against
   stdlib-first, and it buys the least load-bearing of STE's constraints.
   Sentence length and term consistency carry the signal; voice does not.

6. **Do nothing — leave the diet chore judgment-only.** Rejected, but the
   counter-argument is real and is recorded so promotion does not discover
   it late: the chore already works by operator consultation, and the
   2026-08-17 ruling deliberately chose cadence over gate. The answer is
   that arms 1–4 **feed** that consultation rather than replacing it — the
   operator still decides, with a measurement in hand instead of an
   impression. If a promotion draft cannot preserve that, it has drifted.

7. **File as a bibliography entry rather than a pool ADR.** Rejected on the
   operator's ruling of 2026-08-18, and the reasoning is worth keeping: a
   reference entry records that a standard exists, whereas the finding here
   is that a **named chore lacks a criterion** and this supplies one. That
   is a destination, not a citation. `ADR-pool.design-references-bibliography`
   remains the right home for the source document itself.

## Notes

Origin: operator raised `asd-ste100.org` in session 2026-08-18 and pressed the
question — whether control surfaces and rules would benefit from these
simplifications — against an initial agent framing that had drawn the line at
doctrine-versus-procedure. That framing was wrong and the measurement above
refuted it: the real line is **binding directive versus rationale narrative**,
which gzkit had already ruled on. The correction is recorded rather than
smoothed over because the wrong line is the plausible one, and the next reader
will draw it again.

Sibling destinations, so promotion does not collide:

| Concern | Owner |
|---|---|
| Byte size of the surface (the **cure**) | GHI #533 → `ADR-0.35.0` decrease-only ratchet |
| Delivery order under a vendor cap | `ADR-pool.render-order-truncation-survival` |
| Language of the surface (**this ADR**) | here |
| Doctrine for borrowing external strengths | `ADR-pool.external-strength-absorption-doctrine` |
| The source document as a citation | `ADR-pool.design-references-bibliography` |
| Instruction **count** as the budget unit | **absorbed as arm 4** — GHI #579, closed `superseded` 2026-08-19 |

**Independent convergence, surveyed 2026-08-19.** At least six public projects
apply ASD-STE100 to *agent-facing* English rather than to maintenance manuals:
`dfch/biz.dfch.AsdSte100Vocab` (Issue 9 Technical Nouns and Technical Verbs
from R1.5/R1.12, AGPL-3.0), its siblings `…AsdSte100Lookup` and
`…AsdSte100Mcp`, plus the agent-skill cut — `dandye/ste-writing-style`,
`danyuchn/asd-ste100-skill`, `nuelcyoung/asd-ste100`, `fre-sch/skill-asd-ste100`,
`AminBlg/SimpleEnglish`. Two observations are worth keeping and one caution.

First, `danyuchn/asd-ste100-skill` deliberately applies the *principle* — the
plainest available word, used the same way every time — rather than checking
against a fixed list, which is arms 1-4 of this ADR arrived at independently.
That is corroboration of the design, not of the standard.

Second, the ecosystem clusters on **skills**, not validators: every one of these
is an authoring-time prompt surface. None carries a mechanical witness, which is
exactly the gap this ADR exists to close and the reason none of them substitutes
for it.

The caution, stated because it would otherwise be the easiest bad argument to
make from this paragraph: **ecosystem activity is not rationale.** `AGENTS.md`
§ STDLIB-FIRST DOCTRINE operative claims 3 and 4 name *"most projects use X"*
and recent prominence as explicit anti-rationales. Six repositories agreeing is
evidence that the problem is felt, never evidence that the answer is right. The
warrant for this ADR remains the measurement in § Intent.

The byte axis and the language axis are complementary and neither substitutes
for the other: shrinking a surface does not make its remaining sentences
readable, and shortening its sentences does not by itself bring it under a cap.

**GHI #579 is the closest open neighbour, and it was not consulted when this ADR
was first drafted.** It surfaced on a `ghi-author` Step-0 prior-art sweep for an
unrelated finding — late, and recorded here rather than quietly folded in. Filed
2026-06-03 and unrouted until this ADR absorbed it, it argues the budget's
*unit* is wrong: char count
is a proxy for instruction-following degradation by **count**, and its § Design
questions ask *"what metric — count of binding bullets? imperatives per 1k chars?
classification-weighted count?"* That is the same dissatisfaction this ADR
records, answered on a different axis — #579 says the real unit is how **many**
instructions there are; this ADR says the tractable lever is what **language**
they are written in. Neither axis answers the other, which is precisely why the
disposition is absorption rather than substitution.

**Routing booked 2026-08-19** (operator ruling, verbatim: *"include 579 as a part
of it"*). #579 is **absorbed as arm 4** and closed `superseded` against this ADR;
a pool ADR is a valid `superseded` destination under `ghi-close` once registered,
and this one is. The three options the earlier draft left open — close, sibling,
or absorb — are settled, and the reason absorb won is recorded in arm 4 rather
than here: the two ratchets are individually gameable and jointly sound. Anyone
reopening this should have to defeat that argument, not merely re-weigh taste.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
