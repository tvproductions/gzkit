# State of gzkit — an honest reckoning (2026-06-20)

> **Status:** Diagnostic artifact. No governance mutation — no ledger event, no
> ADR, no attestation. Commissioned by the operator ("gzkit is in utter shambles,
> totally off the rails") to produce *one* evidence-grounded picture to decide
> from, instead of 1,589 lines of campaign and 116 handoffs.
>
> **Method:** Every claim below was independently verified against the running
> code this session (four parallel read-only audits), not relayed from the
> handoff. Where the handoff over- or under-stated a number, the corrected figure
> is given and flagged. Citations are `file:line`.

---

## Bottom line

gzkit's thesis is that governance makes stochastic LLM vibing **structurally
inert**. The evidence says the machine built to enforce that thesis has, in its
most load-bearing places, become the thing it warns against:

1. **The gates that catch fabrication don't fire.** The two corpus→rendition
   integrity gates are inert by default and their tests *certify the inertness*.
2. **The antibody is hollow — and it passed Gate 5.** ADR-0.0.73, the
   "QC-binding meta-audit" built specifically to catch verification theater, has
   *both* detection channels defeated, yet was human-attested "Completed" on a
   green self-check that exercises a mode the live system never runs.
3. **The accretion is measurable**, not a mood: 70 validate scopes behind a
   162-parameter function, 33 modules over the 600-line limit, 12 waiver/
   grandfather/baseline files, 10,913 ledger events, 1,835 unlinked specs, a
   1,589-line campaign with 77 stacked amendment blocks, 116 handoffs.

The operator's recent instinct — **ADR-0.0.74 MX Mode, the "lobotomy," gates
become T/F sensors, drain the debt** — is the correct response. This document is
the evidence base for it: what is facade (cut or fix), what is real (keep), and
the order to drain.

None of this implies bad faith. The hollow antibody was attested in good faith
against a passing check. **That is precisely the failure class** — the witness
was shown a passing *simulation*. It happened at gzkit's own Gate 5.

---

## Part 1 — The facade inventory

### 1a. Two integrity gates that do not gate

The corpus→rendition CMS (ADR-0.0.37) is supposed to guarantee that the rendered
`AGENTS.md`/`CLAUDE.md` never drops an invariant and never drifts from its
corpus. Two validate-time gates claim to enforce this. Both are inert by default.

| Gate | Inert flag | Live behavior |
|---|---|---|
| `rendition_freshness.py` | `_FRESHNESS_FAIL_CLOSED = False` (`:37`) | drift → stderr WARNING, **returns `[]`**, `gz check` stays green (`:102-108`) |
| `rendition_floor_coherence.py` | `_FLOOR_FAIL_CLOSED = False` (`:37`) | dropped invariant → WARNING, **`continue`**, returns `[]` (`:91-107`) |

The live call sites pass no `fail_closed` override, so production always runs the
warn-only path. Verified at runtime: both flags read `False`.

### 1b. Tests that certify the inertness

This is the sharp part. `tests/governance/test_rendition_floor_coherence.py`
contains `TestStagedWarn`:

```python
def test_warn_stage_missing_invariant_returns_no_errors(self) -> None:
    """Default (warn) staging: a missing invariant warns, returns no errors."""
    ...
    self.assertEqual(validate_rendition_floor_coherence(self.root), [])
```

A **green, passing test whose assertion is "when an invariant is dropped, the gate
reports nothing."** The only tests that show the gate *can* fail pass an explicit
`fail_closed=True` — a mode the live system never invokes. The test suite locks in
"the gate does nothing" as correct behavior.

The one *real* enforcement survives at compose time: `assert_invariant_verbatim`
(`content/composer.py:57` → `content/tier_policy.py:17-30`) raises `ValueError`
unconditionally when an invariant entry is missing from rendered text. **This is
genuine** — and it makes the two validate-time gates redundant *as well as* inert.

### 1c. The hollow antibody, attested complete

ADR-0.0.73 ("verification-layer-binding-audit") was the cure for exactly this
disease: it was built to catch QC steps that are prose-only, fixture-only, or
otherwise theater. It has two channels. **Both are defeated:**

- **Channel 1 (static theater-signature scan) is permanently inert.** `QCStep`
  is a frozen Pydantic model (`qc_binding.py:44`, `frozen=True`); `theater_flags`
  is hardcoded `[]` on every real step (`:147`, `:196`). The scan loop iterates an
  always-empty list and never fires. This is the *exact* defect OBPI-0.0.73-02 was
  **repudiated** for on 2026-06-18; the 2026-06-19 recovery wired only channel 2.
- **Channel 2 (behavioral negative-controls) certifies a counterfactual.** The
  NCs for the two rendition gates force `fail_closed=True`
  (`_qc_negative_controls.py:164`, `:194`) — their own comments admit *"the live
  gate is staged in warn mode."* So the anti-theater control proves the inert
  gates "genuine" by testing a mode the inert gates never run in.

**Ledger truth** (`.gzkit/ledger.jsonl`):
```
{"event":"attested","id":"ADR-0.0.73-...","ts":"2026-06-19T12:36:04Z","status":"completed","by":"g0"}
{"event":"lifecycle_transition","id":"ADR-0.0.73-...","from_state":"Proposed","to_state":"Completed","ts":"2026-06-19T12:37:49Z"}
```

So per Layer-2 truth, the antibody is **attested-complete**. `gz validate
--qc-binding` exits 0 — by exercising the simulation, not the system. The cure
the campaign says *"alone would have caught the ADR-0.0.37 facade"* does not catch
it.

> **Layer-drift footnote (live instance of the disease):** the ADR's frontmatter
> still reads `status: Validated` while the ledger says `Completed`. Minor, but
> it's the exact Layer-1-vs-Layer-2 drift AGENTS.md § Never #7 exists to catch,
> sitting on the ADR about catching drift.

### 1d. The lock system — a category error in five confirmed defects

The OBPI lock forces *custody* (mutual exclusion) to pay *grounding*'s tax
(handoff-as-evidence). All five defects confirmed in code:

| # | Defect | Evidence |
|---|---|---|
| 1 | **Completion never releases the lock** (GHI #619) | `delete_lock` called only in `obpi_lock.py:64,228`; **zero** callers in any `obpi_complete` path |
| 2 | **Release fail-closed without a handoff** | `obpi_lock.py:211-225` — a custody act (exit 3) gated on grounding evidence |
| 3 | **TTL drift 12×** (GHI #604) | preflight/CLI default `120` min (`preflight.py:51`, `parser_artifacts.py:1380`) vs canon `1440` min (`token-block-discipline.md`) |
| 4 | **Two divergent reapers** | `lock_manager.reap_expired_locks` writes full ledger ceremony (`:273-335`); `preflight._apply_cleanup` raw-`unlink`s with zero ledger (`:77`) |
| 5 | **SessionStart auto-reap is fiction** | `reap_expired_locks` only caller is `gz obpi lock list` (`obpi_lock.py:295`); `session_orientation.py` hardcodes `"obpi_locks": []` (`:347`) |

The *claim* path (O_EXCL) and the *release* path are sound. The *completion* and
*auto-reap* paths are disconnected from the lock lifecycle entirely.

---

## Part 2 — What is real (keep this)

A reckoning that only indicts is its own kind of vibe. These were verified as
genuine, fail-closed, working controls — the kernel worth preserving through any
cut:

| Control | Why it's real | Evidence |
|---|---|---|
| **Compose-time invariant floor** | raises `ValueError` unconditionally on a dropped invariant | `tier_policy.py:17-30` |
| **Waiver-ratchet** | shrink-only baseline; fails (exit 3) if count > baseline *and* on unregistered waiver files | `waiver_ratchet.py:146-181,286-299` |
| **Insights-shape audit** | Pydantic-validates every line of the append-only insights log each run | `insights.py:79-97` |
| **Kind-aware REQ coverage** | the model the rest should emulate: SUPPORT/STRUCTURAL-FENCE exempt from `@covers` | `obpi_complete.py:592` |
| **O_EXCL lock claim** | atomic `open(path, "x")`; sound mutex primitive | `lock_manager.py:153` |
| **Human attestation + ledger** | operator-verbatim Gate 5; the flight recorder | canon, `.gzkit/ledger.jsonl` |

The floor the lobotomy handoff already named — **Gate 5, ledger integrity,
operator-PII, secrets** — is non-negotiable and stays a hard stop regardless of
the severity-leveling rework.

---

## Part 3 — The cost of the heap (measured)

| Surface | Measure | Note |
|---|---|---|
| Validate scopes | **70** (`VALIDATOR_REGISTRY`) | campaign says "~90" — **overstated**; still 11 default + 59 explicit |
| `validate()` signature | **162** boolean params | one function, 162 `check_*` flags |
| Oversized modules | **33 of ~91 (36%)** over 600 lines | largest: `parser_artifacts.py` 1,729; `obpi_complete.py` 1,659; `quality.py` 1,481 |
| Waiver/grandfather/baseline files | **12** (`data/`), 9 under `waiver_ratchet_registry.json` | a grandfather gated by a ratchet gated by a baseline |
| Unlinked specs | **1,835** | confirmed via `triangle.py` DriftReport; the largest single coherence gap |
| Ledger | **10,913** events | system-of-record at production scale |
| Insights | 254 records | course-correction log, healthy |
| Campaign | **1,589** lines, **77** `> **` amendment blocks | the plan to escape accretion is an accretion |
| Handoffs | **116** files, **987 KB** | continuity by sediment |
| ADR packages | **103** | |

**The campaign is a symptom, not just a victim.** Build-to-1.0 was ratified to
*"get our legs back under us."* It is now 1,589 lines of stacked resequencings
with a paragraph-long "Topmost (sequenced)" marker. A session cannot hold it. Any
honest cut includes cutting *this document* down to a spine a session can carry.

---

## Part 4 — Recommended cut order (drain sequence for MX)

This is a recommendation, not an execution. It sequences by **confidence ×
daily-pain**, and it is consistent with ADR-0.0.74 (gates become T/F sensors; MX
drains the debt) — it is *not* a competing plan.

1. **The attested-hollow facade (Part 1a–1c) — highest severity, do first.**
   Either make the rendition gates real (only possible once B.1 rebuilds the
   corpus) or **delete them and the tests that certify their inertness**, and fix
   the qc-binding NCs to exercise the *live* configuration. Leaving an
   attested-complete hollow cure in place is the single most corrosive thing in
   the repo — it teaches that Gate 5 can be passed by simulation.
   *Connector: GHI #634 (repudiated OBPI renders ATTESTED COMPLETED) and the
   `status:` Layer-drift footnote in §1c.*

2. **The lock category error (Part 1d) — bounded, high friction, five known
   defects.** Re-model as a lease: O_EXCL + TTL auto-expire; completion releases;
   release/reap = unlink + ledger event, no handoff-as-evidence. Removes a tax
   paid on every OBPI. *The de-tax relaxes token-block Sub-Invariant 5 and amends
   ADR-0.0.41 — operator ratification pending.*

3. **The kind-blind behave gate — ~3 lines, pure friction.**
   `audit_behave_req_tags` (`briefs.py:524`) demands a `@REQ` scenario for *every*
   REQ; mirror the `obpi_complete.py:592` SUPPORT/STRUCTURAL-FENCE exemption.

4. **The 162-param `validate()` / 70-scope registry — Phase I reduction.**
   `VALIDATOR_REGISTRY` collapse is already begun (#618); finish it so scopes are
   data, not a 162-flag signature. Parity-test before/after (already the standing
   guardrail).

5. **The campaign itself — reduce to a spine.** Lift the 77 amendment blocks to a
   dated appendix; leave a one-screen "what is topmost and why." The steering
   surface must fit in a session's working memory or it cannot steer.

6. **Census inputs, not pre-1.0 actions:** the 1,835 unlinked specs, the
   33 oversized modules, the waiver stack (reviewed 2026-06-19 — irreducible as
   data, the *stacking* is the target). These speak at Phase I with working
   proof, per standing doctrine.

---

## What this document is not

It is not authorization to cut. It is the picture to decide the cut from. The
operator rules the sequence; this artifact only makes the heap legible enough to
rule over.
