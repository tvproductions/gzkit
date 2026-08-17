# CHORE: Instructions & Memory Files Diet (Progressive Disclosure)

**Version:** 3.0.0
**Lane:** Lite
**Slug:** `instructions-files-diet`

> **3.0.0 (operator directives 2026-08-17, verbatim: *"the chore should render,
> check, trim, compress. and ask questions if needed."* and *"it should recommend
> compression and trimming and consult the operator before acting."*) — the
> procedure now MEASURES BEFORE IT CUTS, RECOMMENDS RATHER THAN DECIDES, and
> consults the operator BEFORE the first edit rather than only at Gate 5.**
> The consult gate moved upstream for a measured reason: of 59 corpus entries
> only 4 are `tier: compressible`, and three of those four are
> `prime-directive-ownership` and `operator-doctrine-verbatim-canon`. There is no
> compressible remainder that is not operator canon, so "the chore compresses and
> the operator attests the result" would have the agent exercising editorial
> judgment over the operator's own words and presenting the outcome as a fait
> accompli. `2.0.0` stopped at the right boundary for *landing* canon and the
> wrong one for *authoring* it. This chore now produces a ranked recommendation
> with byte estimates and waits; it mutates nothing — not the corpus, not a rule
> file, not a doc — until the operator has ruled on the specific items.
>
> The measurement half of the same restructure: `2.0.0` routed
> the edits correctly but began at § Score and § Lift: it never composed the
> artifact first, so it had no measurement of the thing it was trimming. Its
> § Inventory step was `wc -l` — **line counts against no cap at all** — while
> the binding constraint is bytes per consumer plus the byte offset of each
> must-survive section. `gz validate --instructions-files-budget`, which runs the
> delivery witness that knows both, appeared only under § Evidence Commands:
> never in the workflow, never in an acceptance criterion. A run could therefore
> compress canon, pass all twelve criteria, and never learn whether it closed the
> gap it exists to close. The new § 1 Render and § 2 Check produce that
> measurement first, § 5c re-renders and re-checks so the loop terminates on
> evidence, and § When to stop and ask names the four states in which the honest
> move is a question rather than a cut. Measured cost of not having had this: the
> 2026-08-17 evaluation of whether to run this chore against GHI #815 found by
> hand — not by the chore — that the compressible budget is **1,894 B** against a
> **1,586 B** overage while `tier: invariant` holds **14,427 B**, and that a
> compliant `codex` rendition already existed and was delivered to nothing. § 2
> is written to surface exactly that class of finding mechanically.

> **2.0.0 (GHI #817) — the surfaces this chore trims are DERIVED, and `1.0.0`
> edited them directly.** `AGENTS.md` is played back from a committed rendition
> composed out of `.gzkit/corpus/AGENTS.md.jsonl`; hand-editing it is drift that
> `gz validate --invariant-coherence` fails closed, and that a later
> `gz agent sync control-surfaces` silently overwrites. `1.0.0` named `AGENTS.md`
> as a direct edit target, carried **zero** mentions of the corpus, and omitted
> `--invariant-coherence` from its acceptance set — so it could edit a rendered
> surface, go green on its own gate, and hand the drift to an unrelated
> `gz check`. It also contradicted itself on mirrors: § 3 named
> `.claude/rules/<rule>.md` as an origin while § 5 and § Anti-patterns both said
> never to edit mirrors. Both arms are now routed to their canonical source, and
> the corpus arm stops at the Gate 5 boundary rather than landing canon
> unattested. `1.0.0` predated the composition architecture (baseline 2026-04-26)
> and aged into incorrectness silently — nothing couples a chore's procedure to a
> change in the layer model of the surfaces it names.

---

## Overview

Trim per-turn agent context weight by lifting pedagogical narrative from
`AGENTS.md`, `CLAUDE.md`, and `.claude/rules/**` to corresponding pages
under `docs/governance/`. The contract retains binding bullets and one-line
pointers to the lifted rationale — pedagogy becomes reachable on demand,
not loaded per-turn.

This is a **narrative trim**, never an invariant relaxation. The doctrine
is explicit at `AGENTS.md` § Anti-vibing mantra operative claim 2:
*"lighter ceremony is not a tradeoff axis."* The same binding invariants
remain in-contract; only the in-place rationale moves.

## Source

GHI #327 — *AGENTS.md: trim per-turn contract weight, lift pedagogy to
docs/governance*. The meta-tension is already named at
`AGENTS.md:13-22` (§ Why this contract is not minimal); this chore acts on
that articulated cost.

Precedent: `AGENTS.md` § Extracted pedagogy (line 99) already lifted the
anti-pattern canon and TASK-driven workflow binding to
`docs/governance/agent-contract-rationale.md`, leaving a one-line pointer
behind. This chore generalizes that pattern across the remaining pillars.

## Baseline (2026-04-26 — a dated record, not a target)

Historical measurement from the chore's authoring date, retained to show what the
surface weighed then. **It is in lines, which is not the constraint** — see § 1,
which measures bytes per consumer against each vendor's delivery cap. Do not
compare a run's output to this table; re-derive the baseline from
`uv run gz validate --instructions-files-budget`.

| Surface | Lines (2026-04-26) |
|---|---|
| `AGENTS.md` | 632 |
| `CLAUDE.md` (imports AGENTS.md + addendum) | 60 |
| `.claude/rules/*.md` (13 path-scoped rule files) | 1085 |
| **Total contract weight** | **~1777 lines** |

## Policy and Guardrails

- **Lane:** Lite — editorial curation against existing canon
- **Foundation-kind content rigor:** the agent contract is an app/system
  invariant surface; bullet retention is gated on the advisory scorecard
  (`docs/governance/advisory-rules-audit.md`), not author judgment
- **Binding-bullet preservation:** every bullet scoring Mechanical or
  Promotable on the scorecard MUST remain in the per-turn contract
- **Judgment-bullet folding:** Judgment-class bullets that duplicate a
  Mechanical neighbor get folded; standalone Judgment bullets that carry
  unique signal stay
- **Pedagogy lift target:** `docs/governance/agent-contract-rationale.md`
  is the established home for lifted pedagogy; new pages may be authored
  under `docs/governance/` when the rationale is large enough to warrant
  a dedicated page (e.g. `docs/governance/anti-vibing-mantra.md`)
- **Pointer discipline:** every lift leaves a one-line pointer at the
  origin site naming the destination page, in the same shape as the
  existing § Extracted pedagogy entry

## Workflow

**Order is binding: render → check → recommend → consult → act.** Steps 1–4
mutate nothing. The first write of any kind happens in § 5, and only against
items the operator ruled in § 4.

### 1. Render

Compose a **baseline** candidate per consumer from the corpus as it stands, with
no edits. This is the artifact the rest of the chore reasons about; every figure
below is measured from it rather than from the file on disk.

```bash
uv run gz content compose AGENTS.md --consumer claude --candidate .gzkit/renditions/AGENTS.md/claude.candidate.md
uv run gz content compose AGENTS.md --consumer codex  --candidate .gzkit/renditions/AGENTS.md/codex.candidate.md
```

Always pass `--candidate` explicitly: omitted, it reads STDIN and silently
validates empty input.

Record the baseline in `proofs/baseline-YYYY-MM-DD.txt` — **bytes per consumer**,
not `wc -l`. Line counts are not the constraint and cannot be compared to a cap.

### 2. Check

Measure the baseline against what actually binds. Three questions, in order.

**(a) Is each consumer's candidate under its own delivery cap?**

```bash
uv run gz validate --instructions-files-budget
```

This runs the surface-delivery witness, which reports rendered bytes against each
vendor cap and the byte offset of every must-survive section from
`data/agents_md_survival_declaration.json`. It is the only check here that knows
about vendor caps — through `2.0.0` it appeared in this file only under
§ Evidence Commands, so a run could pass every criterion while the surface stayed
undelivered.

**(b) Does the DELIVERED surface match the compliant candidate?** A per-consumer
candidate can be under its cap while the file that consumer actually reads is a
different rendition. Resolve which rendition is played back where before
concluding a surface is over-weight:

```bash
grep -n 'load_rendition(project_root, "AGENTS.md"' src/gzkit/sync_surfaces.py
```

If a compliant candidate exists for a consumer whose delivered surface is
non-compliant, **the finding is a delivery-routing defect, not a size defect —
stop and go to § When to stop and ask.** Compressing canon cannot fix a playback
target, and doing so spends operator doctrine to work around it.

**(c) Is the gap closable within the compressible budget?**

```bash
# required delta: rendered bytes over cap, from step (a)
# available budget: non-invariant corpus text only
uv run python -c "import json,pathlib;
e=[json.loads(l) for l in pathlib.Path('.gzkit/corpus/AGENTS.md.jsonl').read_text(encoding='utf-8').splitlines()];
c=[x for x in e if x.get('tier')=='compressible'];
i=[x for x in e if x.get('tier')=='invariant'];
print('compressible entries:',len(c),'bytes:',sum(len(x['text'].encode()) for x in c));
print('invariant entries:',len(i),'bytes:',sum(len(x['text'].encode()) for x in i))"
```

`tier: invariant` entries are verbatim-preserved by the composer and are not
compressible by any amount of editorial judgment. **Measure the remainder; never
assume it.** If required delta approaches or exceeds the compressible budget, the
gap is not closable here — go to § When to stop and ask.

### 3. Recommend

Produce a **ranked recommendation, not an edit.** For each candidate item record:

| Field | Content |
|---|---|
| Item | corpus entry id (with its `tier` and `section`), or the pillar/rule file |
| Action | `lift` (relocate narrative to `docs/governance/`) or `compress` (fold or rewrite in place) |
| Estimated saving | bytes, measured from the entry text — never estimated by eye |
| Scorecard class | Mechanical / Promotable / Judgment / Ambiguous, from § 3a |
| Cost | what a reader loses, stated plainly — especially for operator canon |

Rank by bytes-saved per unit of meaning lost, and stop the list once the
cumulative saving clears the required delta from § 2(c) with headroom. Write it
to `proofs/recommendation-YYYY-MM-DD.md`.

**Never include a `tier: invariant` entry as a candidate.** Never include a
bullet scoring Mechanical or Promotable — those are the load-bearing per-turn
payload and their retention is gated on the scorecard, not author judgment.

### 3a. Score

Class each candidate bullet against the advisory scorecard so the
recommendation's Scorecard column is grounded:

```bash
uv run gz validate --advisory-scorecard
```

Mark each **Mechanical / Promotable / Judgment / Ambiguous**. Mechanical and
Promotable are retained verbatim; Judgment-class bullets that duplicate a
Mechanical neighbour are fold candidates; standalone Judgment bullets carrying
unique signal stay.

### 4. Consult the operator — BEFORE any edit

**Binding gate. Nothing has been written yet and nothing may be until the
operator rules on the specific items.**

Present the § 3 recommendation with the § 2 measurements attached: required
delta, available compressible budget, and per-item saving and cost. Ask for a
ruling per item or per rank-band — not a blanket approval, and never a summary
that asks the operator to trust an aggregate.

This gate exists because the compressible remainder **is** operator canon. Of 59
corpus entries only 4 are `tier: compressible`, and three of those are
`prime-directive-ownership` and `operator-doctrine-verbatim-canon`. An agent
exercising editorial judgment over the operator's own words and presenting the
result for attestation inverts § Attestation, which passes operator words through
unchanged. Recommending is this chore's job; deciding is not.

Record the ruling verbatim in `proofs/CHORE-LOG.md` before proceeding, and carry
declined items forward as declined rather than silently dropping them.

### 5. Act — trim and compress the ruled items only

Move Judgment-class narrative paragraphs and "Why this is canon" /
"Relationship to the rest of the contract" codas to:

**Never edit the origin surface named below — edit its SOURCE.** Both origins are
derived artifacts; the middle column is where the change is actually authored.

| Origin pillar (derived — do NOT edit) | Edit this source instead | Destination for the lifted narrative |
|---|---|---|
| `AGENTS.md` § DO IT RIGHT — multi-paragraph rationale | `.gzkit/corpus/AGENTS.md.jsonl` (see § 5a) | `docs/governance/agent-contract-rationale.md` (existing) |
| `AGENTS.md` § Anti-vibing mantra — philosophical framing | `.gzkit/corpus/AGENTS.md.jsonl` (see § 5a) | `docs/governance/anti-vibing-mantra.md` (new, if size warrants) |
| `AGENTS.md` § Stdlib-First — "Why this is canon" coda | `.gzkit/corpus/AGENTS.md.jsonl` (see § 5a) | `docs/governance/stdlib-first-doctrine.md` (new, if size warrants) |
| `AGENTS.md` § Operator economy — "Why this is canon" coda | `.gzkit/corpus/AGENTS.md.jsonl` (see § 5a) | `docs/governance/operator-economy.md` (new, if size warrants) |
| `.claude/rules/<rule>.md` — multi-paragraph "Rationale" beyond the binding rule | `.gzkit/rules/<rule>.md`, then `gz agent sync control-surfaces` | `docs/governance/<rule>-rationale.md` (per-rule lift, only when narrative >20 lines) |

The rules row restates `.gzkit/rules/skill-surface-sync.md` § Non-negotiable rules
#4 (*"Never edit vendor mirrors directly"*), which § 6 and § Anti-patterns below
have always said. Through `1.0.0` this table contradicted both by naming the
mirror as the origin to edit.

### 5a. The `AGENTS.md` arm goes through the corpus, and stops at Gate 5

`AGENTS.md` is **not** a hand-authored file. It is played back from a committed
rendition under `.gzkit/renditions/AGENTS.md/<consumer>.md`, composed from the
append-only corpus at `.gzkit/corpus/AGENTS.md.jsonl`. Editing the rendered file
is drift on two counts: `gz validate --invariant-coherence` fails closed on it
(`src/gzkit/quality.py` — *"AGENTS.md vs committed rendition playback"*), and
`gz agent sync control-surfaces` re-renders over it.

Compression is therefore authored against corpus entries, not prose:

```bash
# 1. Retire a superseded entry (append-only retraction — never delete a line)
uv run gz content retire AGENTS.md --entry <entry-id> --reason "<why>"

# 2. Capture a replacement when combining or rewriting
uv run gz content remember AGENTS.md --address <section> --text "<compressed text>"

# 3. Compose a candidate per consumer. ALWAYS pass --candidate explicitly:
#    omitted, it reads from STDIN and silently validates empty input.
uv run gz content compose AGENTS.md --consumer claude --candidate /tmp/claude.md
uv run gz content compose AGENTS.md --consumer codex  --candidate /tmp/codex.md
```

**STOP THERE.** `gz content compose` writes a *candidate* and emits byte
evidence; it never writes a rendered surface. Promotion is
`uv run gz content commit`, which requires human attestation — landing a
recomposed `AGENTS.md` is a Layer-1 canon change and Gate 5 is universal
(ADR-0.0.36). **This chore does the compression labor and hands the operator a
candidate to attest. It never lands canon itself.**

`tier: invariant` corpus entries are verbatim-preserved by the composer and are
not compressible by any amount of editorial judgment. The compressible budget is
the non-invariant remainder; measure it rather than assuming it.

Each lifted block leaves a one-line pointer at the origin in the shape:

```markdown
> See [<destination title>](<destination path>) for the rationale, worked
> examples, and citations underlying the bullets above.
```

### 5b. Compress

After lifting, walk each ruled pillar and:

- Fold Judgment bullets that duplicate a Mechanical neighbor
- Collapse multi-paragraph framings down to a one-sentence binding statement
- Preserve verbatim every Mechanical / Promotable bullet — these are the
  load-bearing per-turn payload

Act only on items the operator ruled in § 4. An item that looks compressible but
was not ruled is out of scope for this run; carry it into the next run's § 3
recommendation rather than taking it now.

### 5c. Re-render and re-check

Repeat § 1 and § 2 against the edited corpus. The loop terminates on evidence,
never on the sense that enough was cut:

- **Under cap, must-survive sections all before the cap** → done, go to § 6.
- **Still over, and ruled items remain unapplied** → continue § 5.
- **Still over, all ruled items applied** → STOP. Do not extend the cut to
  unruled items on your own judgment. Return to § 3, re-rank what remains against
  the new measurement, and go back to § 4 for a fresh ruling.

Record each iteration's bytes-per-consumer in `proofs/CHORE-LOG.md` so the run
shows its own convergence rather than asserting it.

### 6. Sync mirrors

```bash
uv run gz agent sync control-surfaces
```

`.claude/rules/**` is generated from `.gzkit/rules/**` per
`.claude/rules/skill-surface-sync.md`. Edit the canonical surface; let sync
propagate.

### 7. Validate

```bash
uv run gz validate --invariant-coherence
uv run gz validate --instructions-files-budget
uv run gz validate --advisory-scorecard
uv run gz validate --documents --surfaces
uv run gz lint
uv run mkdocs build --strict
uv run -m unittest -q
```

`--invariant-coherence` leads because it is the only one of these that can see
whether a rendered surface drifted from the rendition it is played back from.
Through `1.0.0` it was absent from every acceptance list in this chore, so the
chore's own gate was blind to the exact failure its § 5 procedure invited.
`--instructions-files-budget` is second because it is the only one that knows
what a vendor cap is; through `2.0.0` it was not in this list at all.

### 8. Measure

Re-run § 1 and record the post-trim baseline in
`proofs/post-trim-YYYY-MM-DD.txt` — **bytes per consumer**. Compute the delta
against § 1's baseline and record it in `proofs/CHORE-LOG.md`, alongside the
operator's verbatim § 4 ruling and any items carried forward as declined.

## When to stop and ask

Four states in which the honest move is a question, not a cut. In each, record
the finding in `proofs/CHORE-LOG.md` and consult the operator before any edit.

| State | Signal | Why cutting is wrong |
|---|---|---|
| **Delivery-routing defect** | § 2(b) finds a compliant candidate for a consumer whose delivered surface is non-compliant | The overage is a playback target, not a size. Compression spends canon to work around a hardcoded consumer literal — and leaves the routing defect in place to recur |
| **Gap exceeds the compressible budget** | § 2(c) required delta ≥ available `tier: compressible` bytes | Closing it means compressing `tier: invariant` entries, which the composer preserves verbatim by design. The remaining lever is architectural (reorder, split, per-consumer delivery), not editorial |
| **Only operator canon remains** | Every surviving candidate is `prime-directive-ownership`, `operator-doctrine-verbatim-canon`, or another entry carrying operator words | § Attestation passes operator words through unchanged. Editing them is the operator's act, and the agent's job stops at proposing |
| **A binding bullet is the only saving left** | Every remaining candidate scores Mechanical or Promotable | Bullet retention is gated on the scorecard, not author judgment. A trim that removes a witnessed rule is an invariant relaxation wearing a diet's clothes |

The doctrine is explicit at `AGENTS.md` § Anti-vibing mantra operative claim 2:
*"lighter ceremony is not a tradeoff axis."* A chore that cannot hit its target
without crossing one of these lines has found a finding, not a failure — report
it.

## Posture: exceedance is permitted; this chore is the management valve

**Operator ruling 2026-08-17, verbatim:** *"in fact, permit exceedances of
accumulated render sources, then, let the chore handle overages. It keeps the
management of control surface sizes trimmed and managed at a more
realistic/manageable cadence."*

**And, same day, the division of labour it implies:** *"that is saner than
constantly nagging when it seems we'll go over. let the chore manage the limits.
let normal discovery and operations add to or suggest modifications to sources.
then, the chore is what gets render surfaces back into shape. otherwise, we
churn. If the operator wants immediate effect, then the operator can run the
chore."*

Accumulation is allowed to exceed budget **at capture time**. `gz content
remember` never refuses an entry for weight, and the budget audit reports without
blocking. The correction happens **here**, on a cadence, rather than at the
moment canon is captured.

The division of labour is explicit and binding:

| Phase | Owner | May it resize a render surface? |
|---|---|---|
| Normal discovery and operations | any session | **No** — it adds to sources, or *suggests* a modification to one. Weight is not its problem |
| Getting render surfaces back into shape | **this chore** | **Yes** — this is the only phase that trims, and only on an operator ruling per § 4 |
| Immediate effect wanted | **the operator**, by running this chore | Yes — on demand is a first-class trigger, not an exception to the cadence |

**The named failure mode is churn, and it has two faces.** One is a capture-time
gate that refuses or nags whenever a surface *looks* like it will go over: it
converts every unrelated session into a weight negotiation, and the weight is not
that session's problem. The other is an ordinary session deciding to trim on its
own initiative — which spreads editorial judgment over canon across every agent
that happens to notice a number, with no ruling and no measurement. Both produce
motion without convergence. Concentrating the trim here, on a cadence plus
on-demand, is what makes the movement legible: one place, one measurement, one
ruling, one recorded delta.

The reason is the one already recorded in `data/instructions_files_budget.json`
(2026-07-28): *strictness is earned by the mechanism that discharges it.* A gate
that refuses a capture whose only remedy is an unbuilt trim pass does not force
the trim — it blocks the capture, and then gets widened under pressure. Permitting
the exceedance and running a real trim on a cadence inverts that: canon lands when
the operator says it, and weight is managed where a human is already reviewing
proposals.

Two consequences bind this chore:

- **Overage is this chore's normal input, never an error state.** A run that opens
  on an over-cap surface is the chore working as designed. Do not treat the
  exceedance as a defect to escalate — escalate only on the four states in
  § When to stop and ask.
- **Cadence is the control, so the run must be cheap to repeat.** §§ 1–4 mutate
  nothing and can be run purely as a report. Prefer running the diagnosis often
  and cutting rarely over one heroic pass.

## Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| 0 | No rendered surface drifted from its rendition | `uv run gz validate --invariant-coherence` exit 0 |
| 1 | Advisory scorecard audit passes | `uv run gz validate --advisory-scorecard` exit 0 |
| 2 | Documents and surfaces validate | `uv run gz validate --documents --surfaces` exit 0 |
| 3 | Lint clean | `uv run gz lint` exit 0 |
| 4 | Docs build strict | `uv run mkdocs build --strict` exit 0 |
| 5 | Tests pass | `uv run -m unittest -q` exit 0 |
| 6 | Control-surface sync clean | `uv run gz agent sync control-surfaces` reports no stale or divergent mirrors |
| 7 | Per-turn contract weight reduction recorded | `proofs/baseline-*.txt` and `proofs/post-trim-*.txt` exist with a measurable line-count delta |
| 8 | Every binding bullet retained | Each Mechanical / Promotable scorecard entry resolves to a bullet still present in the per-turn contract (manual cross-check recorded in `proofs/bullet-retention-audit.md`) |
| 9 | Pedagogy reachable via in-line link | Every pillar that lifted narrative carries a one-line pointer to its destination page |
| 10 | `AGENTS.md` compression authored in the corpus, not the rendered file | `git diff` shows changes under `.gzkit/corpus/` and `.gzkit/renditions/`; a diff touching `AGENTS.md` with no corresponding corpus change is drift, not a trim |
| 11 | Canon left at the attestation boundary | A composed candidate exists at `.gzkit/renditions/AGENTS.md/<consumer>.candidate.md` and `gz content commit` has NOT been run by the chore — promotion is the operator's Gate 5 act |
| 12 | Measured before it cut | `proofs/baseline-*.txt` records **bytes per consumer** measured from a § 1 composed candidate, and predates every corpus/rule/doc edit in the run |
| 13 | Delivery measured, not just weight | `uv run gz validate --instructions-files-budget` output is recorded for the baseline AND the post-trim state, including each must-survive section's byte offset against the cap |
| 14 | Recommended, did not decide | `proofs/recommendation-*.md` exists, carries per-item bytes + scorecard class + cost, and lists no `tier: invariant` entry and no Mechanical/Promotable bullet |
| 15 | Consulted before acting | `proofs/CHORE-LOG.md` records the operator's verbatim § 4 ruling, timestamped before the first edit of the run; every applied item appears in it, and declined items are carried forward as declined |
| 16 | Loop terminated on evidence | Each § 5c iteration's bytes-per-consumer is recorded; the run ends under cap, or with a recorded § When to stop and ask state — never with an unruled cut |

## Evidence Commands

```bash
uv run gz content compose AGENTS.md --consumer codex --candidate .gzkit/renditions/AGENTS.md/codex.candidate.md
uv run gz validate --invariant-coherence
uv run gz validate --instructions-files-budget
uv run gz validate --advisory-scorecard
uv run gz validate --documents --surfaces
uv run gz lint
uv run mkdocs build --strict
uv run -m unittest -q
uv run gz agent sync control-surfaces
```

`--instructions-files-budget` is the outcome measure: it reports each surface's
byte distance to its budget AND to each consuming vendor's delivery cap. Budget
overruns are advisory until 1.0 by operator ruling; a vendor-cap exceedance is a
physical truncation no gzkit ruling can stay, so that line is the one this chore
exists to move.

## Anti-patterns

- Removing a Mechanical or Promotable bullet to hit a line-count target
  ("lighter ceremony is not a tradeoff axis")
- Lifting binding bullets to `docs/governance/` and replacing them with a
  pointer — only narrative rationale lifts; bullets stay
- Treating the line-count delta as the headline metric — bullet retention
  is the floor; the delta is the by-product
- **Measuring in lines rather than bytes per consumer** — a line count cannot be
  compared to a vendor cap, so a run that reports one has not measured the
  constraint it exists to relieve (the `2.0.0` § Inventory defect)
- **Cutting before the operator has ruled on the specific items** — §§ 1–4
  mutate nothing by design. Composing a recommendation and applying it in the
  same breath makes the consult a notification
- **Treating an overage as an error to escalate** — exceedance at capture is
  permitted by operator ruling and is this chore's normal input (§ Posture).
  Escalate on the four states in § When to stop and ask, not on the overage
- **Compressing to work around a delivery-routing defect** — if a compliant
  candidate exists for a consumer whose delivered surface is not compliant, the
  overage is a playback target. Cutting canon hides the defect and it recurs
- Editing `.claude/rules/**` mirrors directly — edit `.gzkit/rules/**` and
  let sync propagate
- **Editing `AGENTS.md` directly** — it is played back from a committed
  rendition composed out of `.gzkit/corpus/AGENTS.md.jsonl`. A hand-edit is
  drift that `gz validate --invariant-coherence` fails closed and that
  `gz agent sync control-surfaces` overwrites. Author against the corpus (§ 5a)
- **Running `gz content commit` from this chore** — promotion of a candidate to
  the committed rendition is a Layer-1 canon change requiring human attestation
  (Gate 5 is universal, ADR-0.0.36). The chore composes and stops
- **Compressing a `tier: invariant` corpus entry** — the composer preserves them
  verbatim and the invariant floor is not an editorial judgment. Compress the
  non-invariant remainder, and measure it rather than assuming it
- **Reading a byte figure out of a markdown doc** — thresholds and measurements
  live in JSON and in validator output. Re-derive from
  `uv run gz validate --instructions-files-budget`; a number in prose is a dated
  record, never the authority
- Running this chore mid-OBPI without a quiet tree — the diff is large
  and reviewing it tangled with feature work hides binding-bullet drift

## Related

- GHI #327 — origin
- GHI #817 — the `2.0.0` correction: `1.0.0` edited rendered and mirror surfaces
- GHI #815 — the Codex delivery-cap breach this chore's shrink pass would relieve
- GHI #533 — the `<15k` shrink destination
- `AGENTS.md` § Why this contract is not minimal — articulated tradeoff
- `AGENTS.md` § Extracted pedagogy — lift precedent
- `docs/governance/advisory-rules-audit.md` — scorecard catalogue
- `.gzkit/rules/skill-surface-sync.md` § Non-negotiable rules #4 — mirror prohibition
- `ADR-0.0.37` / `ADR-0.35.0` — the composition architecture § 5a routes through
- `docs/governance/agent-contract-rationale.md` — established lift home
- `.claude/rules/skill-surface-sync.md` — canonical-vs-mirror discipline
