# CHORE: GHI Cross-Reference Staleness

**Lane:** Lite
**Slug:** `ghi-cross-reference-staleness`

---

## Overview

Detect **transcribed sibling-state annotations that have decayed**: an open issue body
writing `#889 (open)` when #889 is closed.

The annotation transcribes a Layer-2 fact — GitHub's issue state — into prose that never
reconciles. It was true when authored and becomes false the moment the sibling closes,
with nothing observing the transition. Measured at landing, 2026-09-20: **5 of the 10**
such annotations in the open queue were already false, a **50% decay rate**.

The absolute count is small. The rate is the finding.

## Background

Commissioned as disposition row 3 of `docs/rnd/ghi-landscape-reorganization.md`
(operator-funded 2026-09-20), which measured the decay while asking why the open queue
does not drain, and named it *"an instance of the very family the campaign names."*

Scope was narrowed by operator ruling the same day, after a design dialogue: this chore
covers **issue cross-references only**. Transcribed values in live governance prose — the
sibling case, where a campaign carried `19 of 32` for 18 days against a true denominator
of 37 — route instead to the `doctrine-declared-without-mechanism` box, where the clause
is already scored at row `17h` of `docs/governance/advisory-rules-audit.md`.

## Policy and Guardrails

- **Lane:** Lite — read-only. The chore reads GitHub and the baseline; it writes nothing.

- **A body is NEVER rewritten, and this is the chore's central constraint.** `#889 (open)`
  is a dated record of what its author observed. Editing it to `(closed)` so it agrees
  with today falsifies that record — the move `AGENTS.md` forbids for every other archive,
  and the reason a published report is corrected by a linked follow-up rather than an
  edit. `gh issue edit` is additionally not among the allowed commands in
  `.gzkit/rules/gh-cli.md`. This chore has no repair verb and is not entitled to one.

- **The remedy is subtractive, and it lives at authoring time.** GitHub renders issue
  state live, so the durable form of a reference is a bare `#889`. The second copy is
  what decays. This is the same subtraction GHI #768 ruled for transcribed ADR counts —
  *stop writing the number down* — applied one surface over. Recommending that amendment
  to `ghi-author` is this chore's proposal; performing it is not.

- **Scope is the ANNOTATED form only, and the bound is real.** The detector binds an
  annotation to the reference immediately preceding it. Prose that merely *reasons* as if
  a sibling were open is invisible here: GHI #969's argument rests on #889 being open and
  never writes `(open)` in that clause. The R&D record's larger count included such cases;
  this gate does not claim them. A window-based detector was tried first and returned nine
  hits for five real ones — a 44% false-positive rate — by reading `(open)` from a
  neighbouring clause. The tight form is not a refinement, it is the correctness condition.

- **The "premises falsified by later landings" half of row 3 is ADVISORY, by its own
  text and by operator ruling (2026-09-20).** Whether a later commit quietly made an
  issue's premise false — GHI #815 and #943 are the named instances — is not mechanically
  detectable, and no check here claims it. Stating it advisory rather than leaving it
  implied is the `doctrine-declared-without-mechanism` completion criterion applied to
  this chore's own text: *a declared discipline either carries a mechanical witness or is
  demoted to advisory in its own text — no third state.*

- **Growth is disclosed, not forbidden — and the ratchet is mechanical, not claimed.**
  `data/ghi_cross_reference_baseline.json` is registered shrink-only in
  `data/waiver_ratchet_registry.json`, so `gz validate --waiver-ratchet` fails closed if
  the disclosure list grows. Verified by negative control at landing: a sixth entry exits
  3, removing it exits 0. An entry records an absence; it does not justify one.

- **The census is bounded, never a page.** `gh issue list` returns one page and exits 0
  when truncated (GHI #972). The detector requests a limit well above the queue size and
  **refuses** a result that reaches that limit rather than reporting a capped page.

## Workflow

### 1. Report the population — observe

```bash
uv run python .gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py --report
```

Record the output in `proofs/cross-reference-staleness.md`. The rate matters more than
the count: a low count with a high rate means the convention is unreliable wherever it
is used, not that the queue is healthy.

### 2. Route each undisclosed instance — propose

| Route | When |
|---|---|
| **Disclose** | the annotation is decoration — a Related-list mention the issue's argument does not rest on |
| **Surface to the operator** | the annotation is load-bearing: the issue's reasoning depends on the sibling being open, so the argument needs re-reading against what actually landed |
| **Recommend the subtraction** | the pattern recurs — propose that `ghi-author` stop transcribing sibling state at authoring time |

Disclosure is the honest holding state, never the default. This chore rules on nothing.

### 3. Enforcement — observe

```bash
uv run python .gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py
```

Exit 1 when a decayed annotation is not disclosed in the baseline.

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with
`uv run gz chores plan ghi-cross-reference-staleness`. This section explains them and
does not restate them (GHI #1002).

- The self-test exits 0 — detector semantics hold with no network and no repo state,
  including the neighbouring-clause trap that produced the 44% false-positive rate
- The gate exits 0 — every decayed annotation is disclosed in the shrink-only baseline

The gate criterion measures the **population against a shrink-only bound**. That is a
volume mechanism, and per GHI #998 a volume mechanism says nothing about coverage: it
cannot observe an annotation form the detector does not recognise, nor implicit decay.
Stated here rather than discovered later.

## Cadence

Elapsed-time, 30 days. Issue state changes continuously and is not a repo surface, so
`content-delta` has nothing to watch and `accumulated-work` would declare a counter that
does not compute (GHI #1009). Run before a triage pass or a planning session, when the
queue's own cross-references are about to be read as current.

## Related

- `docs/rnd/ghi-landscape-reorganization.md` — disposition row 3, which commissioned this
- Row `17h`, `docs/governance/advisory-rules-audit.md` — the general clause, scored
  **Promotable**; the governance-prose sibling of this chore's subject
- GHI #768 — the transcribed-ADR-count subtraction this chore's remedy follows
- GHI #1064 — that subtraction's witness, pointed at a superseded campaign edition
- `.gzkit/rules/gh-cli.md` — the allowed-command list, which excludes `gh issue edit`
- `data/waiver_ratchet_registry.json` — where this chore's baseline is registered
