<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Build-to-1.0 Campaign — 2026-08-16 (Magna Carta)

Status: **ACTIVE — the one canonical plan** (operator-directed 2026-08-16).
Supersedes [`build-to-1.0-campaign-2026-07-18.md`](build-to-1.0-campaign-2026-07-18.md);
priors are retained for audit and no longer steer.

**This edition is a FULL carry-forward, not a rewrite.** Every box, movement,
amendment, and register entry from the 2026-07-18 edition is retained inline and
in place — no box removed, nothing resequenced, no ruling dropped. Movement B
remains TOPMOST, Movement A remains HELD, the post-1.0 pool ruling stands. The
edition exists because the plan was re-evaluated against the live tree on
2026-08-16 rather than re-read, and a re-evaluation of that scope earns its own
dated identity (operator-directed: *"update that campaign document with today's
date - re-evaluate it thoroughly"* / *"did you update a fresh document with today's
date and sunset the prior?"*). Because the carry-forward is total, no § Rulings
Register disposition pass was owed — the 07-18 amendments travel with the text.

**What the 2026-08-16 re-evaluation measured** (each finding recorded at its own
box; § Amendments 2026-08-16 carries the full table and method notes):

| Claim | 07-18 edition | Re-measured 2026-08-16 |
|---|---|---|
| Oversized modules (>600 lines) | 33 | **51** — largest regression on the board |
| `fix` commits, 90 days | 524 | 528 |
| `airlock_in` / `airlock_out` | 23 / 5 | **23 / 5 — unchanged; zero transits** |
| Scorecard Promotable rows | 0 | **8** (GHI #810) |
| Pool ADRs | — | ~199 `.md` under `docs/design/adr/pool/` |

**Held on re-measurement:** `ADR-0.35.0` `Draft`, `ADR-0.36.0` `Proposed`,
`ADR-0.33.0` `Validated`, GHI #766 and #611 open, surface-mirroring ratio ~49%
over a stated 90-day window.

**The sharpest finding is the number that did not move.** The airlock counters are
identical two days into Movement B holding TOPMOST — zero transits — while `fix`
commits rose by four. The ungoverned door widened while the governed one stayed
shut, inside the window where that Movement was supposedly being worked.

> **Topmost (sequenced):** **AMENDED 2026-08-14 — Movement B is TOPMOST; Movement A is HELD.** **Movement B — put the membrane on the real doors.** The airlock is BUILT and installed on ONE door — run `uv run gz adr status ADR-0.33.0-airlock-membrane` for its lifecycle and landed count rather than trusting a figure transcribed here. Measured live 2026-08-14: **524 `fix` commits in 90 days across zero transits**; **23 `airlock_in` vs 5 `airlock_out`** (18 unaccounted exits — worse than the 23/10 this file recorded); and **20 of 23 transits computed an EMPTY seam-map and auto-proceeded**, only 3 biting (3/4/7 seams → `hold`). **RE-MEASURED 2026-08-16: `airlock_in` 23, `airlock_out` 5 — both UNCHANGED, so zero transits occurred in the two days since Movement B became TOPMOST, while `fix` commits over 90 days moved 524 → 528. The ungoverned door widened by four while the governed one stayed shut.** That is the item-150 gap (`GHI : MX :: OBPI : Build`) reproducing in miniature, and it is the strongest available argument that item 0's calibration is the right first move rather than the widening beneath it. Sequence within B is **calibrate before widening** — a new item 0, ahead of the five checkboxes below, because widening an uncalibrated gate installs three more inert gates (`ADR-0.33.0` § Negative #1, the load-bearing pre-mortem: *"seam-maps rubber-stamped, GO always reached"*). **The feature ADR that carries this Movement is AUTHORED — `ADR-0.37.0-airlock-calibration-and-compulsion` (2026-08-14), which re-homes `ADR-0.33.0`'s disclosed residuals rather than reopening it; run `uv run gz adr status ADR-0.37.0-airlock-calibration-and-compulsion` for its lifecycle and landed count.** (This sentence read *"none is authored yet"* until 2026-08-16 — see the § Amendments record of that date.) See § Amendments 2026-08-14 and § Movement B.
>
> **HELD — Movement A — close the Foundation Sunset.** ~~`ADR-0.0.37` audit~~ **done 2026-07-18 (`b40a8026`)** → ~~`ADR-0.34.0` capstone~~ **`Validated` 2026-07-31, released v0.34.0** → **NEXT: re-home the composition engine as a feature (`ADR-0.35.0-canon-entry-corpus-landing`, `Draft`, IN FLIGHT; run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the landed count — ten authored briefs, `gz obpi validate --authored` 10/10; **the lifecycle step is RULED 2026-08-12 — `Draft` HOLDS through implementation and OBPI work is UNBLOCKED**; *not* GHI #623, closed 2026-07-19; see § Movement A item 3)** → **THEN: install the cross-family critic at the convergence moment (`ADR-0.36.0-convergence-moment-cross-family-critic`, `Proposed`, NEXT-DRAWN after `ADR-0.35.0` lands; run `uv run gz adr status ADR-0.36.0-convergence-moment-cross-family-critic` for the landed count — promoted 2026-08-09 (`dc5fe4d39`) from the pool ADR; the promotion debt is discharged and the remaining work is the build — work the governed path, do NOT hand-wire a hook; delivery is STAGED and OBPI-09 lands dark; see § Movement A item 2)**. The one-line `foundation-adr-registers-invariant` disposition (item 4) is **RULED and checked off 2026-08-02** — it is no longer pending work. Then Movement B (airlock on the real doors), C (reduce), D (rulings). Pool backlog is post-1.0 (§7).
>
> **Ordering note (corrected 2026-08-12).** This banner had continued to assert the 2026-08-09 pull-ahead of `ADR-0.36.0` for a day after the 2026-08-11 amendment (§ Amendments, *"the pull-ahead is WITHDRAWN"*) withdrew it, contradicting items 2 and 3 below and the amendment itself — three surfaces in one file, the stale one read first. `scripts/session_orientation.py` transcribes this line into every session's orientation, so the topmost-item line a fresh session was handed named the wrong feature. Architectural Boundary 6 in the same terms: a transcribed view is Layer 3 and never source-of-truth. **When the sequence changes, this banner is part of the amendment, not a follow-up.**

> **Why this edition exists.** The road to 1.0 was dragging. Measured 2026-07-18 over
> the prior 90 days: **1,508 commits, 43 of them `feat` (2.9%)**; 703 were `gz git-sync`
> regenerating control surfaces (47% of all commits). The system had become its own
> primary consumer. This edition makes 1.0 **finite**, lifts the reduction deferral that
> deadlocked it, moves the airlock onto the doors work actually uses, and books the pool
> backlog as the **post-1.0** release line.

> **Slim by design — and this time it is enforced.** Checkbox entries carry a one-line
> outcome plus a commit/receipt citation. Completion narrative belongs in the ADR, the
> ledger, and the release notes — **not here**. The 06-30 edition forbade inline
> *amendments* and then accreted 800-word completion prose into its checkboxes instead;
> that hole is closed. Amendments append to § Amendments, never inline.

---

## 1. What gzkit is (identity — unchanged)

**Research instrument + published exemplar → personal toolkit → public product.**
gzkit's purpose is to make stochastic LLM vibing **structurally inert** — not by
exhorting agents to behave (they vibe regardless), but by making every claim
**falsifiable by a live test**.

**Amended 2026-07-18:** adoption is still not a 1.0 *gate*, but the absence of any
external consumer is now named as the **root cause of non-convergence** (§2). One
external forcing function is a Movement, not a nicety.

## 2. The reckoning (measured, 2026-07-18)

The 06-30 edition named *enforcement-claim drift* as root cause. That diagnosis was
correct and its cure largely landed (§5's meta-validator, 42 claims verified, 0
facades). A second root cause was not named, and it is why 1.0 receded:

**gzkit has no external forcing function, and its only consumer is its own
construction.** Self-inspection of a self-governing system is unbounded — every
governance surface is a new surface needing governance, and every audit pass finds
*real* defects, which is what makes the loop seductive rather than obviously wasteful.

| Measure (90d to 2026-07-18) | Value |
|---|---|
| Total commits | 1,508 |
| `feat` | **43 (2.9%)** |
| `fix` | 470 (31%) |
| `chore` — of which 703 are `gz git-sync` | 810 (54%) |
| GHIs minted | Apr 304 → May 197 → Jun 86 → **Jul 38** |
| GHIs closed Jul | 51 (net-draining) |
| Surface | 107k src LOC · 146k test LOC · 359 ADRs · **659 OBPI briefs** · 13,488 ledger events · 92 `validate` flags · 59 CLI verbs |

**The GHI backlog is draining, not exploding.** The "GHI after GHI" experience was not a
worsening defect rate — it was defect repair becoming ~100% of the work because nothing
in the system was permitted to say *enough*. §8 fixes that.

**The airlock was built on the wrong door.** Every `airlock_in` in the ledger is an OBPI
or a `permitted-entry`; **zero** are GHI direct-fix or session entry, which together carry
~97% of commits. Last transit: 2026-07-15. The 2026-07-18 session — corpus survey, two
GHIs, three source files, a Magna Carta amendment — crossed **no** airlock. Movement B is
the correction. (Accounting gap also open: **23 `airlock_in` vs 10 `airlock_out`.**)

## 3. Doctrine (carried — see § Rulings Register for provenance)

- **Four modes, one airlock each:** Design · Build (OBPI, minor) · MX (GHI squawks, patch) · Chores (patch). `GHI : MX :: OBPI : Build`.
- **Intent hierarchy:** Constitution → PRD (one per major) → ADR → OBPI → REQ → TASK.
- **Versioning:** feature = minor · MX/GHI = patch · MX-produced contract change = patch + AD artifact. Every bump is a release.
- **Taxonomy:** `foundation` is a **closed, frozen-historic** kind; `pool` and `feature` are the two live kinds. Completed foundations stay; unstarted ones drop to pool. Realized by `ADR-0.34.0`.
- **Code architecture:** Hexagonal (Ports & Adapters) is primary, seated in the DDD → HA → BDD → TDD spine; the domain is modeled as the **ontology** (`ADR-0.32.0`), never a folder tree.
- **STDLIB-FIRST** governs the interior; Pydantic is the one ratified exception.

## 4. The floor — never relaxes, either engine, in or out of the hangar

**`gate5_invariants` (code constant, not config):** human attestation, ledger integrity,
operator-PII, secrets. No marker, lane, sensitivity, or AOG can downgrade a member.

**The enforcement-claim rule:**

> Any place gzkit asserts something is **enforced / validated / fail-closed / gated /
> blocked** — in code, an ADR, a doc, or an agent's claim — there MUST exist a paired
> **live negative-control** test that (a) constructs a known violation of that exact
> claim, (b) runs the real path in its **production** configuration, and (c) asserts it
> **fails**. No live negative control ⇒ the claim is facade ⇒ rejected.

Mechanized by `@enforces(claim=…, neg_control=…)` + the meta-validator.
**Forbidden:** forced-mode counterfactuals; tests that certify enforcement does nothing.

> **Registration is centralized** in the qc NC table (`_qc_negative_controls.py`), NOT
> colocated with the module it guards. Absence of `@enforces` in a module is **not**
> evidence of a missing NC — check `registered_claims()`. A false facade finding was
> filed and withdrawn on this exact mistake (GHI #697, 2026-07-18).

## 5. The 1.0 definition — **FINITE** (amended 2026-07-18)

gzkit is 1.0 when ALL hold. Each gate is bounded; none is a standing obligation.

- **The floor holds** — `gate5_invariants` intact **and** the §4 meta-validator is green
  **over the claim set registered as of 2026-07-18**. Claims registered later are
  post-1.0 maintenance, not 1.0 blockers.
- **The facade is drained — as of the 2026-07-18 census.** No gate returning `[]` on its
  own violation, no test certifying inertness, **among surfaces enumerated in that
  census**. Facades found afterward route to MX/patch. *(This replaces the 06-30 wording,
  which was an unbounded audit obligation with no terminal state — the gate that made 1.0
  unreachable by construction.)*
- **Both engines operate** — a feature can go pool→release through the airlock; the MX
  hangar can drain debt and re-certify at a hard exit.
- **The membrane is on the real doors** — Movement B complete.
- **The accretion is reduced** — Movement C complete.
- **One external forcing function exists** — at least one flight-test sortie flown against
  a non-gzkit substrate, black-box evidence collected (`gz-flighttest`).
- **Release line healthy** from 0.34.0; GHI backlog at steady-state triage scale.
- **v1.0.0 released** through the ceremony.

**Explicitly NOT 1.0 gates:** the pool backlog (§7 — post-1.0 release line), RECALL
(severable enrichment), adoption.

## 6. The Queue

> Work top-down. Check items off only with **observed command evidence**. No movement
> opens while `uv run gz check` is red.

**Movement A — Close the Foundation Sunset** *(TOPMOST; forward engine; closes a kind — reductive)*
- [x] `ADR-0.0.37` → `Validated` via `/gz-adr-audit`. Attribution drift found by independent review and remediated pre-receipt. `b40a8026` · receipt `arb-step-unittest-753d3dda` · detail in § Amendments 2026-07-18 (later session).
- [ ] **Install the cross-family critic at the convergence moment.** **NEXT-DRAWN, after `ADR-0.35.0` lands — the 2026-08-09 pull-ahead was WITHDRAWN by the 2026-08-11 amendment (operator: *"not sure i wan't to author 0.36.0 while we haven't finished 0.35.0"*, spelling preserved).** The withdrawal rests on the staged-delivery ruling, not on a change of mind: because OBPI-09 lands dark, completing all nine still does not deliver the always-on critic the pull-ahead was for. Three briefs (01, 02, 03) were authored 2026-08-11 at `1b808b18d` and remain valid; six are `draft (scaffold)`. The design is complete and unbuilt: **`ADR-0.36.0-convergence-moment-cross-family-critic` (`Proposed`) now holds it** (run `uv run gz adr status ADR-0.36.0-convergence-moment-cross-family-critic` for the landed count), promoted 2026-08-09 from `ADR-pool.convergence-moment-cross-family-critic` (now `Superseded`), which had recovered it verbatim from the three 2026-08-06/07 design transcripts after the operator judged the handoff chain had degraded it — *"multiple audio tape recordings of audio tape recordings where the quality is dissipating rapidly."* **Nothing runs today:** `.claude/hooks/` ships no critic script and `.claude/settings.json` `PreToolUse` has matchers for `ExitPlanMode`, `Write|Edit` and `Bash` only — no `AskUserQuestion` matcher (verified 2026-08-09). **Promotion is done; the remaining work is the nine OBPIs.** Work the governed path; **do not hand-wire a hook** — that was the declined option. Carried design rulings that bind the build: the critic performs BOTH scope and conclusion challenge with full context (*"why is this a choice? we want the adversary to get full context. measure twice, cut once"*); it is a **skill** with three invocation doors — operator, agent, or gate (*"this is a skill but can be invoked by me, by agent, or at gate"*); post-verdict resolution is operator + main agent modeled on Step 4b (*"obpi pipeline 4b already handles this well — observe it"*); and it uses the built-in Codex integration rather than a hand-rolled port (*"why not use that and keep it simple?"*). The critique passes through **unedited** — `updatedInput` enforces it, so the critic's verdict reaches the operator before it enters the agent's context. **This does not relax one-feature-at-a-time:** `ADR-0.35.0` is `Draft` and unstarted (run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the landed count), so this exchanges which feature is in flight rather than running two. **THE PROMOTION DEBT IS DISCHARGED — all four owed items, then the promotion itself (2026-08-09, `8763ec633` + `dc5fe4d39`).** Decomposed against the three doors with the `PreToolUse` adapter as OBPI-09 landing dark; Step 4b generalized without editing it (OBPI-07); A3 and A4 carried as OBPI-05 and OBPI-06; the adversary re-run already discharged by the amendment above. **What remains is the build — no OBPI has landed.** **DELIVERY IS STAGED, not big-bang — the adversary re-run was performed 2026-08-09 and returned `PERFORATED-BUT-NARROWABLE`.** R4 dissolved Pass 1 axis 2 (forbidden same-family critic) and R3 dissolved Pass 2's missing-policy attack at the policy level; axes 1, 3 and 4 remain *partially* addressed. What still perforates: the automatic door binds to a UI event that carries **mandatory clarification** as well as recommendations, so it *"can prevent the very question those rules require"*; prose bypasses it entirely; strong subject binding (prompt hash, scope manifest, primary-output hash) is explicitly unbuilt; and the scope-time-vs-conclusion-time timing question the ADR calls *"live"* is unresolved by R1. **Therefore: ship the skill, the three doors, the scope-first challenge, the A3 envelope, the R3 transition and provenance binding FIRST; the automatic `AskUserQuestion` door lands DARK and is lit only after a calibrated pilot measures *"false blocks, latency, operator reading time, and decisions changed."*** This is sequencing, not abandonment — and the cost is stated rather than softened: until that door lights, this does **not** deliver a second opinion at every structured choice. **A3 → ADOPT-NARROWED** (one decision-scoped envelope, not persistent state across every tool transition). **A4 → ADOPT-NARROWED** (mandatory for the enumerated consequential categories and explicit operator requests, sample the routine; the primary agent's own unvalidated confidence must NOT set the tier — the ADR itself asks whether that confidence is *"placebo"*). **R4's transport premise is measurably wrong and is corrected in the ADR (§ R4 transport correction) — see also GHI #786:** the built-in `adversarial-review` reviews *branch diffs*, not decisions, and the `codex:codex-rescue` forwarder is contracted to *"return nothing"* on failure. R4's ruling (use the current Codex, keep it simple) stands; the belief that the shipped plugin already supplies this transport does not.
<!-- gz-validate-skip: command-shape -->
- [ ] Re-home the registry→AGENTS.md composition engine as a **feature** ADR. **IN FLIGHT — restored to the in-flight feature position by the 2026-08-11 amendment, reversing the one-position deferral of 2026-08-09.** Implementation-ready and reviewed 2026-08-11: ten briefs pass `gz obpi validate --authored` **10/10**, `--req-kind-discipline` / `--brief-reconcile` / `--cli-alignment` each exit 0. Three ADR-body defects were repaired at `584778396` — `BI-07` had lost its REQ's proof channel (it cited `ADR-0.44.0` while `REQ-0.35.0-09-07 [structural-fence]` cited `ADR-pool.vendor-alignment-codex`), `(see Forced Decisions)` pointed at a non-existent section, and the `[kind]` tag case was split. **Status is `Draft`, and the lifecycle step is RULED 2026-08-12: `Draft` HOLDS through implementation. OBPI work is UNBLOCKED and this question is CLOSED — do not re-raise it.** The question had been carried unworked across seven successive handoffs because the answer was never written down; it is written here. Three findings settle it. (i) **Corpus precedent is unanimous:** `ADR-0.33.0` and `ADR-0.34.0` each held `status: Draft` through their *entire* implementation phase and moved straight to `Completed` at release — `ADR-0.34.0` authored `Draft` 2026-07-12 (`946afb5ae`), held it through OBPI-05 (`67cf7c998`) and the orphan-census fix (`7de63c779`), and became `Completed` only at the v0.34.0 release commit (`551366064`), then `Validated` (`73e2f5569`). No feature ADR has ever entered `Proposed` or `Accepted`. (ii) **`Accepted` would be a false Layer-1 claim:** `STATUS_VOCAB_MAPPING` (`src/gzkit/governance/status_vocab.py:42`) maps `"Accepted": "validated"`, and both `governance/frontmatter_coherence.py` and `commands/gates.py` consume it — advancing while OBPIs remain unlanded (`uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the live count) would assert the ledger term `validated` against a Layer-2 that reports `pending`, manufacturing exactly the drift the frontmatter-ledger-coherence chore exists to catch. `Draft` and `Proposed` both map to `pending`, so `Proposed` would be vocab-neutral but precedent-breaking for no gain. (iii) **The `Draft → Proposed → Accepted` chain in `ADR_TRANSITIONS` (`src/gzkit/core/lifecycle.py:48-53`) is dormant on this axis** — it is re-exported by `src/gzkit/lifecycle.py` but no ADR frontmatter writer consumes it, which is why the corpus performs a `Draft → Completed` jump the machine forbids. It is not the governing authority here. **The Lifecycle column reporting `Pending` is not drift:** it is Layer-3 derived from the absence of Layer-2 completion events and can report nothing else while the OBPI set is unlanded, whereas frontmatter is Layer-1 authorship. Different axes, per `docs/governance/state-doctrine.md`. **DONE as authoring: the successor is `ADR-0.35.0-canon-entry-corpus-landing` (authored 2026-07-21, `Draft`; `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the OBPI set and landed count) — this item is started-not-done, and the tracker is the ADR, not a GHI.** GHI #623 closed 2026-07-19 and **GHI #654 closed 2026-07-22 `superseded` into `ADR-0.35.0`**, whose § Intent names it: *"Discharges GHI #654 (orchestration gap) and GHI #635 (duplicate invariant entries) -- the same wound."* Do not reopen #623 **or #654** to find this scope; read the ADR. Its OBPI-05 carries the corpus→candidate generator and OBPI-07 the `gz content land` orchestrator. GHI #654's capture-silence gap was direct-fixed ahead of the chain (`48a5f799`, `dcf29b95`) because it was a live footgun; see the pre-landed note in `OBPI-0.35.0-08`. The absorption direction `ADR-0.0.37` § Terminal Disposition recorded (*"tracked at GHI #623 (absorbing GHI #654)"*) is backwards relative to what survived: #623 was an audit finding and its findings are discharged, while #654 states the same unbuilt capability as operator pain with a reproduction — *"there is no generator that renders the corpus delta into a candidate."* Closed after a full re-verification: claims (3)/(4) had been fixed by later work and never credited back, corrective scope (A) had landed as `--rendition-floor-coherence`, the discarded registry parameters were removed (`4f9c7d2b`), and a standing witness-resolution gate was added (`e409bb08`). **Residual scope, unbuilt and feature-shaped:** the attributable corpus→candidate generator and the `rendition ⊆ corpus` lineage gate — today `compose()` *validates* an agent-supplied candidate rather than *materializing* one from the corpus, so prose absent from canon can still pass. The registry spine is NOT the successor: `ADR-0.0.37` § Terminal Disposition permanently withdrew OBPI-02/03 as *"obsoleted by the 2026-06-03 corpus Re-Alignment."* The successor is corpus-shaped.
- [x] **Disposition `foundation-adr-registers-invariant`** — **RULED 2026-08-02: retire the claim as superseded by the Foundation Sunset.** The entry declared structural witness `gz validate --foundation-registers-invariant`, which never existed, and the claim was unenforceable as written — `constitutional_invariant.json` carries no field naming which ADR registered an entry (fields are `id`, `claim`, `structural_witness`, `composition_targets`, `classification`). The ruling turns on what OBPI-0.34.0-05 sealed: the foundation kind is **closed** at both `adr_created` ingresses, so the claim's subject set is permanently frozen at the 51-entry grandfathered roster and can never be exercised again. The entry now states that sealed reality, witnessed by `gz validate --taxonomy` (exists; already the last step of `gz check`; exits 0 on the terminal tree). The **file is retained, not deleted** — `REQ-0.0.37-01-03` (attested, OBPI-0.0.37-01) asserts only that the three seed files exist, load via `load_invariants`, and validate against the schema, never that the claim text is true; rewriting `claim` + `structural_witness` preserves attested canon exactly, deleting the file would falsify it. `tests/governance/test_invariant_witness.py` fence drops to `frozenset()` and stays shrink-only: a new vapor witness fails immediately. *Two corrections to this item's own prior text:* the "74 foundation ADRs" figure was the `--taxonomy` **findings** count from OBPI-04 (line above), not an ADR count — the roster is **51**; and `--invariant-witness` was described as staying "out of `gz check` until this is ruled", but **that flag has never existed either** — `validate_invariant_witnesses` is a function in `governance/trust_audits/invariant_witness.py` whose only caller is the fence test, with no CLI wiring. Enrolling it was separate work, tracked at GHI #746 and **landed 2026-08-03**: `--invariant-witness` is now a registered default-tier scope, so it runs under bare `gz validate` and therefore inside `gz check` — no separate step entry was needed, because GHI #744's collapse made one bare `gz validate` gate the whole default tier. The scope is now nameable as a `structural_witness` in its own right, which it could not be while unregistered.
- [x] `ADR-0.34.0-foundation-sunset` capstone — **`Validated` 2026-07-31**, released [v0.34.0](https://github.com/tvproductions/gzkit/releases/tag/v0.34.0), tag on the bump commit `551366064`. Closeout ceremony (11 steps, `g0` verbatim *"attest completed"*) then audit ceremony (`g0` verbatim *"accept audit"*); receipts `arb-step-unittest-f02e079a9c5c4fce83433f15d1ace4b1` (7685 OK), `arb-ruff-9b11bcbc647c4b9a9ddb6282f7fc34b4`, `arb-step-typecheck-4c8436dc00e842b8847ebcacb7dc866c`, `arb-step-mkdocs-3f31717e44a04a46821f35433f53b0c2`; bound fidelity gate 2/2. Audit record and three recorded-open shortfalls: `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/audit/AUDIT.md`. All 5 OBPIs `attested_completed`. OBPI-01 2026-07-19: grandfather manifest + closed-kind assertion · OBPI-02: authoring-time kind rejection at all three CLI doors · OBPI-03 2026-07-29 (`f6088fabc`): terminal-partition gate reading grandfathered-foundation terminality from the Layer-2 `foundation_grandfathered` event and never frontmatter, plus `ADR-0.0.18` frozen-historic · OBPI-04 2026-07-30 (`d521ace53`): **the migration executed** — `--taxonomy` moved exit 3 / 74 findings → exit 0, 23 genuinely-unstarted foundations demoted to pool (136 briefs removed, lineage preserved by `obpi_parked` per child), 51 manifest entries bijective with 51 `foundation_grandfathered` ledger events, re-sensed with zero orphans (seams 119→119) · OBPI-05 2026-07-31: the permanent `--taxonomy` gate wired as the **last** step of `gz check`, and the registration membrane sealed at the two manifest-membrane `adr_created` ingresses (GHI #706 discharged). *Audit qualification:* exactly three `adr_created` emission sites exist; the third is the shared helper `register_adr_in_ledger`, whose two callers are both separately guarded — a latent surface (GHI #734), not an open hole. Movement A's capstone is closed; items 2 and 3 remain.

**Movement B — Put the membrane on the real doors** *(carried by `ADR-0.37.0-airlock-calibration-and-compulsion` — authored 2026-08-14, `kind: feature`, `lane: heavy`, re-homing `ADR-0.33.0`'s disclosed residuals; run `uv run gz adr status ADR-0.37.0-airlock-calibration-and-compulsion` for its lifecycle and landed count rather than transcribing one here)* — **TOPMOST as of 2026-08-14 (operator-ratified; § Amendments)**

> **The doors mostly exist. They do not fire.** `gz permitted-entry` shipped with
> `ADR-0.33.0` (OBPI-05) and has **2** recorded transits. `gz airlock in` is wired into
> `gz obpi pipeline` Stage 1 and fires reliably there — because the pipeline *triggers*
> it. Everywhere else the airlock is **invocable but opt-in**, and an opt-in gate is not a
> gate. This is the §4 failure class one level up: a mechanism that exists, is documented
> as governing entry, and does not bite. **Operator ruling 2026-07-18: GHI and ad-hoc
> (permitted) entry MUST trigger the airlock mechanism.**

- [ ] **0. CALIBRATE THE SEAM-MAP BEFORE WIDENING ANY DOOR.** *(added 2026-08-14; sequenced ahead of the five below.)* The gate is not theater — it bit 3 times — but **20 of 23 transits computed an EMPTY seam-map and auto-proceeded** (measured live 2026-08-14: `decision` 20 `proceed` / 3 `hold`; `unaccounted` 20×`0`, then 3, 4, 7). `ADR-0.33.0`'s own calibration-frontier note states the cause: `gz ontology reach(<obpi-id>)` returns transitive **dependents**, of which a leaf OBPI has none, so `push_edges` is empty; and the gate never passes `parent_invariants`, so `pull_edges` is empty too. **This is WWHTBT-(a), the ADR's self-declared load-bearing condition, deferred past the FC-2 tracer and never landed.** Widening to three more doors first would install three more inert gates and put transit ceremony on 524 commits/quarter with no membrane behind it — `ADR-0.33.0` § Negative #1 (*"Theater… seam-maps rubber-stamped, GO always reached… the membrane exists but does not bite"*) arriving through the front door. Done means: a real entry on a real OBPI computes a non-empty seam-map, and the existing NC still cannot be forced. **Destination: `ADR-0.37.0-airlock-calibration-and-compulsion`, AUTHORED 2026-08-14 — NOT corrective work under `ADR-0.33.0`.** The re-homing precedent is `ADR-0.35.0`, which exists because `ADR-0.0.37`'s composition engine was withdrawn and re-homed as a feature rather than appended to a sealed ADR. Appending an OBPI to `ADR-0.33.0` would drag a `Validated` ADR back to `Pending` and retroactively falsify an operator attestation that was honest when it was given — the frontier was *disclosed* in the attested REQ text, so the artifact told the truth and the residual is unscheduled work, not a defective attestation. **The ADR takes exactly this framing** — its `## Intent` re-homes the residual on the `ADR-0.35.0` precedent in the same terms — and the calibration lands in its § Decision D1, **revised 2026-08-15** after the original inverse-`reach` form was **withdrawn on measurement**: the inverse returns the artifact's lineage chain, identical across `-01`, `-02` and `-05`, which converts an empty seam-map into a *constant* one and satisfies a non-emptiness assertion while deciding nothing. Read the OBPI set and landed count from `uv run gz adr status ADR-0.37.0-airlock-calibration-and-compulsion`, never from this page — and note that **OBPI-01's slug still reads `ontology-inverse-reach`, which is tracked rename debt by operator ruling** (repurposed rather than withdrawn, to keep the checklist 1:1 with the briefs on disk), so that slug no longer describes its content.
- [ ] **GHI direct-fix triggers the airlock.** `GHI : MX :: OBPI : Build` — the MX door must carry the same membrane the Build door does. A `fix(...)` landing without a transit is an unaccounted entry. This is the single highest-volume ungoverned door: **470 `fix` commits in 90 days, zero transits** (90d to 2026-07-18; **481** on the same measure to 2026-08-08). **The door is wider than either figure reports.** Measured 2026-08-08 subject-anchored: 546 commits touched `src/**/*.py`, **193 of them (35%) under a `chore` subject**, and **187 of those 193 (97%) were `gz git-sync`-authored** — invisible to `git log --grep='^fix('`, which is both the source of this figure and the precedent query AGENTS.md § Defect-fix routing prescribes for its own routing decision. Fenced at the sweep 2026-08-08 (GHI #708 reopened), so the count is honest going forward and undercounts by an unrecovered amount before it. Measure subjects via `git log --format='%s'`, never `--grep='^chore'` — `--grep` matches the whole message and admits `fix(chores):` commits whose body has a line starting with "chore".
- [ ] **Ad-hoc / permitted entry triggers the airlock.** Make `permitted-entry` fire on ad-hoc reconnaissance and light repair rather than waiting to be invoked — the reason selects the door, never *whether* the gate fires (`ADR-0.33.0` door principle).
- [ ] **Session entry triggers the airlock.** A model entering the project is a transit. The SessionStart hook already runs orientation; it should seat a seam-map and a go/no-go. Evidence this is the live hole: the 2026-07-18 session ran a full corpus survey, filed 2 GHIs, changed 3 source files, and rewrote Magna Carta across **zero** transits.
- [ ] Close the transit-accounting gap: **23 `airlock_in` vs 5 `airlock_out`** — **18** transits never accounted for on exit. Failure-atomic pairing precedent: GHI #679 / `89c5ee9a`. **Count corrected 2026-08-14** from the 23/10 this box carried; re-measure rather than transcribe. Sequence it **second, after item 0** — do not widen what you cannot yet account for. This is the third instance of one paired-event family found on 2026-08-14: the resume gate recorded 160 lifts and 0 blocks (fixed, `2a326f042`), `session_exit` records 37 skips and 0 writes (GHI #766, open), and the airlock pairs 23 entries to 5 exits. Consider dispositioning the family once rather than three times.
- [ ] Bind with a §4 live NC on each widened door: **un-triggered entry → the claim fails**. Not "un-accounted seam → GO unreachable" (that is `ADR-0.33.0`'s existing NC, and it only fires once you are already inside the airlock). The new NC must catch *never entering at all* — the failure mode that let ~97% of commits through.

**Movement C — Reduce the accretion** *(deferral LIFTED 2026-07-18 — this is pre-1.0)*
- [ ] **Surface mirroring** — 703 of 810 chore commits (47% of all commits) are `gz git-sync` regenerating five copies of every skill/rule across `.gzkit/`, `src/gzkit/`, `.claude/`, `.agents/`, `.github/`. One canonical location; generate at install, not at commit. Largest single line item on the board. **RE-MEASURED 2026-08-16 — the ratio holds, and this box's window is unrecorded so the original figures are NOT overwritten.** Over a stated 90-day window: **1561 commits, 761 `chore` subjects, 633 mentioning `gz git-sync`** (`git log --since='90 days ago' --format='%s'`). The proportion is materially unchanged (~49% vs the 47% recorded), so the box's claim stands on fresh evidence rather than on a transcribed number. The original 703/810 is left in place because the window it was taken over is not stated anywhere — replacing figures whose method is unknown with figures from a different method would manufacture a false comparison, which is the transcription failure `gz validate --transcribed-adr-counts` exists to refuse. **Whoever works this box states the window first.**
- [x] Collapse the `validate()` surface to the registry — **DONE 2026-08-08** against the amended criterion. **Done means the enumeration family is closed, not that the count fell** (amended 2026-08-07): the registry is the single source, and *registering a scope enrolls it in the gate* (GHI #744). Siblings that must stop recurring: #704 (six solo-only scopes silently dropped when combined, under a green check), #745 (fenced blocks escape all three verb detectors), #748 (a weaker verb extractor reimplemented alongside one that already shipped). A count target alone leaves every one of those live. **All three sub-claims now hold, each fenced:** *(a)* enrollment landed 2026-08-02 (`0f671b31c`, GHI #744) — `data/check_scope_membership.json` declares membership and `tests/governance/test_check_scope_parity.py` recomputes it from source via AST, so drift in either direction fails and a default-tier scope outside the gate fails closed; *(b)* the registry is **now** genuinely the single source — `--qc-binding`, `--fidelity-presence` and `--waiver-ratchet` had dispatched through the early-return chain alone since the #618 collapse, contradicting the `VALIDATOR_REGISTRY` header's own "Single source of validate dispatch" claim, and that gap had already cost GHI #630 (every SUPPORT REQ citing one read `unproven-support` regardless of truth) which was patched with a *third* hand-maintained map rather than closed; registering the three retired that map (**net −18 source lines**) and the fence now asserts `reached − registry == ∅` instead of accommodating the exception; *(c)* #704, #745 and #748 all closed 2026-08-02 with standing fences, #704 with a genuine class-level fix replacing the per-scope guards that had been copied forward onto every new scope. **Count correction:** the "94 scopes" this box carried matched no enforced surface — `VALIDATOR_REGISTRY` holds **85**, the roster classifies 85 (44 `in_check` / 41 `out_of_check`), and `gz validate --help` prints 99 *flag* lines including non-scope flags. The retargeting off counting is exactly why that stale figure changed nothing about completion.
- [ ] Oversized modules — census-driven, with working proof. **RE-MEASURED 2026-08-16: 51 modules over 600 lines, up from the 33 this box carried — a 55% increase, and the largest measured regression on the board.** Method, so the next reader re-runs rather than transcribes: `find src/gzkit -name '*.py' -exec wc -l {} + | awk '$1>600 && $2!="total"'`. The box is not merely unstarted; its subject grew faster than anything shrank it. Note the threshold itself is contested — `.gzkit/rules/pythonic.md` § Size Limits records that 600 is authoring-time guidance with **no enforcing gate**, and that it disagrees with the canonical `complexity-thresholds.md` table (which warns at 733.2 and blocks at 1031.9), so a census against 600 counts modules that no gate rejects. Settle which number governs as part of the census, or the proof will be measured against an authority the codebase does not enforce.
- [ ] **The Firewall** *(recovered orphan, § 9a)* — classify every delivered surface by destiny: **wheel-borne / authored-into-battlefield / lab-only-jig**, enforced at scaffold-time and validate-time. Operator, 2026-06-14: *"the rigging and jigs do not remain attached to the fuselage once we open the factory hangar doors for final delivery — we haven't been careful about this."* Booked 06-14, never built. Load-bearing for §1's public-product trajectory: today an adopter inherits gzkit's lab jigs. Genuinely reductive — it defines what does **not** ship.
- [ ] **Render the stability-gradient spine** *(recovered orphan, § 9a)* — the 06-14 ruling ordered the tree `Constitution → PRD → ADR → OBPI` by rate of change and declared the legacy `PRD → Constitution` spine backwards. AGENTS.md § Workflow still carries the old order across ~12 surfaces. Booked and never rendered.
- [ ] **Close the doctrine-declared-without-mechanism family** *(added 2026-08-07)* — the family's own name, from GHI #537: *"Layer X declares a discipline that Layer X does not mechanically enforce."* Measured by the `failure-class-index` chore over the 333 GHIs closed since 2026-05-09: the **two deepest recurrence chains in the corpus** (depth 12 and depth 7) are both this family, ~19 members, and it holds the two most-cited ancestors on record (#537 cited 3×, #538 cited 4×). Both arms are in scope — **validator-side** (a check whose subject is narrower than its name: #692 *checks section presence, not population*; #693 *verifies a flag is mentioned, never that its description is true*; #770 *an audit named for dispatch attestation whose entire subject is a frontmatter string*) and **agent-side** (a skill mandate with no receipt: #459, #574, #620). **Completion criterion:** a declared discipline either carries a mechanical witness or is demoted to advisory in its own text — no third state. This is the reductive move that stops the `validate()` surface producing scope #95: it closes the family rather than the instance. **Re-scoped 2026-08-08 (operator-ratified) — the six named issues all closed and the box did NOT discharge; see the amendment for why, and the measurable criterion below.**

  **All six exemplars are CLOSED** — validator-side `#692`, `#693`, `#770`; agent-side `#459`, `#574`, `#620` (verified 2026-08-08 via `gh issue view`). They are **evidence the class exists, not a checklist**: the box's own text says *"it closes the family rather than the instance."* Six closed instances do not discharge a class-level criterion, and checking the box on their strength is the enumerate-the-exemplars habit the criterion was written to resist.

  **The criterion is measurable, and the instrument already exists.** `docs/governance/advisory-rules-audit.md` scores every clause of `CLAUDE.md` + `.gzkit/rules/**` on four values, self-tested by `gz validate --advisory-scorecard`. Those four values ARE the criterion: **Mechanical** = carries a witness; **Judgment** = advisory by its own text; **Promotable** and **Ambiguous** = *the third state this box forbids*. **The live count is the scorecard's own fenced Summary table — deliberately not restated here.** Run `uv run gz validate --advisory-scorecard`; it fails closed when that table disagrees with the rows beneath it.

  > **Count correction, 2026-08-08 (measurement only — the ratified criterion is unchanged).** This paragraph first read *"63 Mechanical, 27 Judgment, **12 Promotable + 2 Ambiguous = 14 rows in the third state**."* None of those four figures reproduce against the file, which had not been modified since 2026-08-06. The measurement was taken by counting *mentions* rather than *rows*: `grep -c 'Ambiguous'` returns exactly 2 — the scorecard's legend row and its own Summary row, neither of which is a rule. The true third state is **9 `Promotable` and 0 `Ambiguous`**, and `Ambiguous` has no members at all, so one of the two arms the criterion named was empty from the start. Per the GHI #768 ruling on this same class — *stop writing the number down; add a narrow check so it cannot decay back into a convention* — the figure is now fenced at the scorecard and cited here rather than transcribed.

  **Done means all three arms hold:**
  1. **Rules arm** — every `Promotable`/`Ambiguous` row reaches zero: each is either mechanized (→ Mechanical) or its rule text amended to state it is advisory (→ Judgment). Re-scoring alone, without the text edit, is laundering. **Read the freeze before choosing an arm:** the scorecard's § Recommended promotion order is FROZEN (2026-06-08, governance-subtraction) — *"Promotion is opt-in-with-justification ... The remaining Promotable rows stay advisory by default."* Under that freeze the default disposition is the **amend-the-text-and-re-score** arm; mechanization is reserved for a row carrying named, observed drift evidence. That reading makes this box a subtraction move, which is what Movement C is for.
  2. **Skill arm** — the scorecard covers **no** `.gzkit/skills/**/SKILL.md` mandate, which is where all three agent-side exemplars lived (`#459`, `#574`, `#620` were each a skill mandate with no receipt). Extend coverage to skill mandates, or record in the audit why skills are structurally out of scope. Today the arm is not failing — it is unmeasured, which is the same blindness one surface over.
  3. **Debt arm** — already mechanized and needs no new work: the 23 pre-ledger rules are pinned in `data/advisory_scorecard_grandfather.json` and registered shrink-only in `data/waiver_ratchet_registry.json` (ADR-0.0.73 BI #8), so debt cannot grow or follow a rule forward silently.

  > **Status change 2026-08-16 — the rules arm REGRESSED from 0 to 8, and that is
  > this box working (GHI #810).** `.gzkit/rules/cli.md` was scored for real, which
  > required dropping its `0.3.1` grandfather pin. Scoring it honestly produced
  > **8 Promotable rows (scorecard rows 76-82, 85)** — the third state this box
  > forbids, returning. **Do not read this as new drift.** The CLI layer had been
  > invisible to the instrument on *both* arms: `cli.md` sat in the grandfather
  > registry unscored, and the 1,037-line specification elaborating it
  > (`docs/design/cli-standards-v3.md`, canonical per ADR-0.0.4) was reachable from
  > that ADR and from **no rule or governance surface**, so nothing carried it into
  > the per-turn contract. Decay under those conditions produces no signal; the 8
  > rows are that decay becoming measurable for the first time. Re-scoring them to
  > **Judgment** without amending the rule text is the laundering arm 1 already
  > forbids, so the arm is genuinely open. Measured alongside: every CLI rule with
  > a mechanical arm holds at or near 100%, every prose-only rule at or near 0%.
  > **The debt arm moved the right way in the same pass** — the grandfather registry
  > shrank 15 → 14 against `baseline_count` 23, which is the shrink-ratchet
  > behaving as designed. Restoring arm 1 means building the arms (rows 76-82 and
  > 85 consolidate to **one** validator, `gz validate --cli-shape`, plus an
  > output-chokepoint ratchet — see the scorecard's § CLI Contract Doctrine), not
  > re-scoring. Tracked at GHI #810.

- [ ] **Name the adoptable mechanisms — the positive half of The Firewall** *(added 2026-08-16, operator-directed)*. Item 160 defines what does **not** ship. Nothing defines what an adopter **gets**, and four mechanisms that already work have no home describing them as a deliverable surface rather than gzkit's private tooling. Two ship today with no adoption story: the **shrink-only waiver ratchet** (`data/waiver_ratchet_registry.json`, ADR-0.0.73 BI #8 — debt may only decrease; it gated the grandfather removal on 2026-08-16, 15 → 14 against baseline 23) and the **verifier-pipe-gate hook** (`.claude/hooks/verifier-pipe-gate.py`, GHI #589 — refuses a verifier in any non-final pipeline stage; it fired against an agent's own `gz validate | grep` on 2026-08-16, which is the class of false green that then gets relayed as attestation evidence). Two are already homed and named here only so the set is legible: the **Mechanical validators** are delivered by `ADR-0.0.31-distribution-invariants` (`Validated`; run `uv run gz adr status ADR-0.0.31-distribution-invariants` for its landed count rather than trusting a figure transcribed here — `pip install py-gzkit && gz init`, byte-equivalent, fail-closed via `gz validate --distribution`), and the **scorecard method** is item 162 above, whose live counts are fenced at the scorecard's own Summary table. **Done means:** each of the four is classified under item 160's destiny taxonomy (wheel-borne / authored-into-battlefield / lab-only-jig) and, for anything wheel-borne, the adopter-facing contract is stated — what it checks, what it costs per turn, and what a project must do to satisfy it. **Explicitly NOT a new pool ADR** (Architectural Boundary 2 — *do not add more pool ADRs to the runtime track*); the pool already holds 190 unscoped items and four hooks-related entries (`claude-hooks-absorption`, `pre-commit-hook-absorption`, `hooks-meta-layer-contract`, `prime-context-hooks`) that this box does **not** unfreeze. **Sequenced with item 160, not ahead of it** — the negative half is the load-bearing one, because until it lands an adopter inherits the lab jigs regardless of how well the positive half is described. Origin: the 2026-08-16 competitive review, which measured the flourishing tools in this category as authoring-side (Spec Kit 93k stars, BMAD 46.7k) with the enforcement side unoccupied as OSS — gzkit's differentiator is real and undescribed.

**Movement D — Stop the re-adjudication** *(ruling lifecycle)*
- [x] **Handoff-local repair** — every authored next step now survives the resume (`ResumeResult.next_steps`); the `continues_from` chain link is correct-by-construction. GHI #696, commit `5ec44ad1`, receipt `arb-step-unittest-430503d2`.
- [x] **Recover the orphaned 06-10 rulings.** Done 2026-07-18, in-session. Counted **17** amendments + 4 scope decisions + a goal-state — not the "77" the 06-30 edition asserted. All dispositioned in § 9a. Highest-value catch: **Scope decision #1 ("Full pool build-out … no item left undecided at 1.0") was live and unwithdrawn**, in direct contradiction to today's post-1.0 pool ruling — the precise orphan that resurfaces months later as *"but we booked that for 1.0."*
<!-- gz-validate-skip: command-shape -->
- [ ] **Rulings become first-class** — `ruling_issued` / `ruling_superseded` typed ledger events; a `gz ruling` verb; the handoff *Settled* section and per-decision operator-ruled/agent-chose attribution as **rendered projections**; the campaign body as a rendered Layer-3 view; supersession **fail-closed on orphaned rulings**. Sibling: GHI #611. Diagnosis: **nothing in gzkit represents the state "settled"** — 60+ typed ledger event kinds, no ruling event — so settled decisions are re-derived, and re-deriving is re-adjudicating. § Rulings Register is the manual stand-in until this lands.

**Housekeeping (not a Movement, but tracked so it stops being invisible)**
- [x] `ADR-0.44.0-vendor-alignment-codex` was `Pending`, partly landed, and tracked by no campaign edition. **RETURNED TO POOL 2026-08-08** as `ADR-pool.vendor-alignment-codex` (GHI #773). Operator ruling, verbatim: *"this was originally an agent overeach. this either becomes 0.36.0, revert to pool, or we just ignore/deleted the implemented code - I won't be paralyzed in purgatory."* (spelling preserved).
  - **Pool, not 0.36.0, and not deletion.** The overreach was the *numbering*, not the work: the implemented Codex surface is real, in use, and stays — only the unsanctioned REQ/OBPI structure retires. Renumbering to `0.36.0` would have re-asserted it as a sanctioned in-sequence feature, the opposite of what "overreach" means, and no governed renumber path exists (`gz migrate-semver` is a bare-id→slugged-id backfill recorder; `gz adr promote --semver` requires a pool source). Deleting the code would have destroyed working capability. Demoted with `--on-collision take-demoted`, so the pool file carries the evolved content rather than the 2026-03 intake. The 6 OBPIs are parked and released on re-promotion.
  - **Three defects blocked this and were fixed first** (`a98c482f7` and successor). **GHI #774** — park is a two-sided protocol with one side never exercised (371 `obpi_parked`, 0 `obpi_unparked`), so these OBPIs read *parked* under a live ADR; `parkable_children` would have skipped them, emitting zero park events while `rmtree` deleted every brief, with the orphan census (which excludes parked OBPIs) reporting nothing. **GHI #775** — neither collision policy could return an ADR that had been worked, and this one had diverged from its intake by 139 insertions / 140 deletions. **Third, found by executing it:** 36 `@covers` decorators named REQs in the briefs being deleted, and `@covers` validates at *import*, so the suite stopped loading. `gz adr demote` now refuses that shape unless `--force`, and strips `promoted_from` and retitles the H1 so a demoted file reads as the pool ADR it has become.
  - **The residual is honest:** the Codex tests keep running and keep asserting the behaviour; what was discarded is REQ-to-test traceability for an OBPI whose coverage was already attested at Gate 5. That was the price of retiring an overreached structure, taken deliberately rather than by omission.

## 7. Post-1.0 — the pool→feature release line

**Operator ruling 2026-07-18: the pool backlog does NOT gate 1.0.** The ~23 unstarted
foundation ADRs that `ADR-0.34.0` demotes to pool are **feature-shaped** and become the
**0.35+ release line after 1.0**, promoted `pool → feature` one at a time with executable
proof, each through the airlock.

Rationale, on the record: ~23 pool ADRs × ~5 OBPIs ≈ **115 OBPIs**. At the observed
feature rate that is quarters, not weeks. Booking them pre-1.0 is what made 1.0 recede.

Known pool set (post-Sunset): pool-management · pool-dag-promotion · pool-triage ·
systematic-debug · validation-pipeline · milestone-maintenance · artifact-staleness ·
validator-remediation · package-import · closeout-defect · prior-art-sensitivity ·
harness-fitness · harness-factoring · afk-diagnosis · deterministic-state · and the
remainder enumerated by the capstone. Plus `ADR-pool.rag-anything-governance-retrieval`
(RECALL) and `ADR-pool.hexagonal-folder-structure-realization`.

## 8. Authority & amendment

Living: items check off with command evidence. Amendments are operator-ratified, recorded
with the operator's verbatim words, and **appended to § Amendments** — never interleaved.
The campaign rules sequencing; handoffs and triage **advise**. ADR, OBPI, and GHI repair
remain the primary propellants; this plan sequences them, never substitutes for them.
No work stream runs outside it except `emergency`-labeled interrupts.

**New (2026-07-18):** a successor edition MUST carry § Rulings Register forward with every
ruling explicitly **carried** or **withdrawn**. Hand-picking "live threads" is what
orphaned ~74 of the 06-10 edition's 77 amendment blocks.

## 9. Rulings Register (carried forward — the anti-orphaning mechanism)

Every ruling from the superseded editions, explicitly dispositioned. **CARRIED** = binding
today. **WITHDRAWN** = no longer steers, with reason.

| Ruling | Origin | Disposition |
|---|---|---|
| Never-relax floor + enforcement-claim rule | 06-30 §5 | **CARRIED** → §4 |
| Ledger + fail-closed human attestation is the irreducible moat | 06-20 §2a | **CARRIED** → §1, §4 |
| Reduction mandate — shed toward superpowers-lightness | 06-20 §2a | **CARRIED** → Movement C |
| Reductive moves wait for post-1.0 | 06-10 sequencing | **WITHDRAWN** 2026-07-18 — deadlocked against the line above; accretion was blocking 1.0 |
| "The facade is drained" as an unbounded gate | 06-30 §8 | **WITHDRAWN** 2026-07-18 — replaced by the dated census bound in §5; had no terminal state |
| Adoption is not a 1.0 gate | 06-30 §1 | **CARRIED, amended** — still not a gate, but one flight-test sortie is now a §5 gate |
| Four airlocks + MX granularity + intent hierarchy | 06-20 §3 | **CARRIED** → §3 |
| Versioning: feature=minor, MX=patch, contract-change=patch+AD | 06-20 §4 | **CARRIED** → §3 |
| Severity ladder = Python `logging` + NOTICE (not kernel 0–7) | 06-21 amendment | **CARRIED** |
| OKF/CMS documentation-knowledge orientation layer | 06-23 amendment | **CARRIED** — delivered `ADR-0.30.0` |
| Harness loop-engineering + OKF notes are advisory sidecars, not steering surfaces | 06-23 amendment | **CARRIED** |
| Airlock seated as a distinct Movement | 06-23 amendment | **CARRIED** — delivered `ADR-0.33.0`; extended by Movement B |
| Re-sense needs a computed graph; AIRLOCK-IN/OUT realize keel-up together | 06-30 Movement III pivot | **CARRIED** — delivered `ADR-0.31.0`/`0.32.0`/`0.33.0` |
| HULL substrate = `tree-sitter + networkx` (GO-attested); `graspologic` stripped | 07-05 withdrawal-of-departure | **CARRIED** |
| One unified HULL ADR (not a 3-ADR constellation) | 07-05 operator ruling | **CARRIED** — delivered `ADR-0.32.0` |
| Taxonomy = partition, not flatten; `foundation` frozen-historic and closed | 07-05 amendment | **CARRIED** → §3, Movement A |
| The taxonomy migration is pre-1.0 | 07-05 amendment | **CARRIED** → Movement A |
| Hexagonal is the primary code-architecture directive | 07-06 amendment | **CARRIED** → §3 |
| Hexagonal seated in DDD→HA→BDD→TDD; domain = ontology, `core/` stays, no folder cosplay | 07-06 amendment | **CARRIED** → §3 |
| Foundation Sunset realized as `ADR-0.34.0`; three-class partition from L2 ledger truth | 07-12 amendment | **CARRIED** → Movement A |
| `ADR-0.0.65` reached `Validated` (corrects the stale `1/5` reading) | 07-15 amendment | **CARRIED** — superseded by live state; `0.0.72` is also `Validated` 3/3, correcting the stale "`0.0.72` (1/4)" in the 06-30 edition |
| Movement V seated as TOPMOST | 07-18 amendment (06-30 ed.) | **WITHDRAWN** same-day — mis-sequenced ahead of a capstone one step from executable; re-seated as Movement D |
| GHIs are authorized for direct repair, always | operator canon | **CARRIED** — AGENTS.md corpus |
| Never create feature branches; work on main | operator canon | **CARRIED** — AGENTS.md corpus |
| Human attestation is sacrosanct; no TTY/PTY excuse | operator canon | **CARRIED** — §4, AGENTS.md corpus |
| Correction vs enhancement — unmet intent is a correction | operator canon | **CARRIED** — AGENTS.md corpus |

### 9a. Recovered from the 06-10 edition (dispositioned 2026-07-18)

The 06-30 edition claimed 06-10 carried "77 amendment blocks." **Counted: 17** (plus 4
scope decisions and a goal-state). The "77" was itself an unverified number this campaign
had been repeating. All are dispositioned below — none left undefined.

| Ruling (06-10) | Disposition |
|---|---|
| "we don't direct edit AGENTS.md; the CMS must be near-top priority" (06-10) | **CARRIED** — AGENTS.md is corpus-rendered; the 2026-07 corpus-derivation work is this |
| Buetow practices adopted → `ADR-0.0.70` (06-12) | **CARRIED** — delivered, `Validated` |
| **Firewall foundation ADR** — classify every delivered surface by destiny (**wheel-borne / authored-into-battlefield / lab-only-jig**); *"the rigging and jigs do not remain attached to the fuselage"* (06-14) | **CARRIED — UNDELIVERED.** No Firewall ADR exists. Load-bearing for §1's "public product" trajectory: today an adopter inherits the lab jigs. Booked as a Movement C box. |
| **Constitution as enduring root; tree ordered by stability gradient** — `Constitution → PRD → ADR → OBPI`; the legacy `PRD → Constitution` spine is *backwards* (06-14) | **CARRIED — UNAPPLIED.** AGENTS.md § Workflow still reads `PRD → Constitution → ADR → OBPI`. The ruling was booked and never rendered. Booked as a Movement C box. |
| CMS ↔ hierarchy coupling; disclosure tier ∝ inverse volatility (06-14) | **CARRIED** — realized as progressive disclosure + the always-injected router |
| Dispatch drift-guards #617 (CLI handler resolution) / #618 (`validate()` scopes) (06-14) | **CARRIED** — #618 → Movement C; **#617 status unverified**, folded into that box |
| Governance-friction drainage empowered to the campaign; file the GHI in the moment of discovery (06-14) | **CARRIED** — now AGENTS.md § Defect-fix routing |
| Turn-end claim-grounding gate #620 → E.6 (06-14) | **CARRIED** — delivered, `ADR-0.0.70` Stop hook, commit `d83db8a2` |
| Pure-A reconciliation of the off-campaign 0.0.65/0.0.72 session (06-14) | **SUPERSEDED** by live state — both are `Validated` (5/5 and 3/3) |
| Pydantic schema-enforcement of fillable artifacts; **frontmatter is rendered + hands-off** (06-15) | **CARRIED** — the hands-off half is AGENTS.md § Never #8; the enforcement half (**GHI #615**, 597/600 briefs on `LegacyBriefShape`) is still **OPEN** |
| Compliance-strength family; **direct-fix moratorium stands as default** (06-15) | **WITHDRAWN** — superseded by operator canon *"GHIs are AUTHORIZED for direct repair, always"* and the 2026-06-01 anti-reflexive-GHI moratorium |
| Airlock North Star; `gz-obpi-pipeline` is the proven reference implementation → E.7 (06-16) | **CARRIED** — delivered `ADR-0.33.0`; extended by Movement B |
| Work-phase theories are a 1.0 completion gate (06-17) | **CARRIED** — discharged by OBPI-0.33.0-06 |
| The heap reckoning — *"don't forget what a garbage heap gzkit has evolved into"* (06-19) | **CARRIED** → §2, and corroborated again by the 2026-07-18 measurements |
| **Sanity Reduction track — completion-before-reduction overridden for named, parity-proven cuts BEFORE 1.0** (06-19) | **CARRIED** → Movement C. **Note:** this already overrode the reduction deferral in June; the "reductive moves wait for post-1.0" line that deadlocked 06-30 was therefore contradicting a ruling that predated it |
| `ADR-0.0.74` MX seated as topmost P0 (06-20) | **CARRIED** — delivered, released `0.29.0` |
| **Scope decision #1 — "Full pool build-out. All 139 live pool items … to a terminal disposition. No item left undecided at 1.0."** | **WITHDRAWN 2026-07-18** — directly contradicted by today's ruling that the pool backlog is the **post-1.0** release line (§7). This is exactly the orphan that would have resurfaced later as *"but we booked full pool build-out for 1.0."* |
| Scope decision #2 — Canon Foundation workstream booked into 1.0 | **WITHDRAWN** — foundation is a closed kind (§3); the workstream's live content routes to pool/feature |
| Scope decision #3 — per-ADR done-bar is `Validated` or operator-parked | **CARRIED** |
| Scope decision #4 — in-flight first, then MOTD | **WITHDRAWN** — MOTD never shipped and is not in §5; superseded by the current Movement order |
| 06-10 goal state (census 100% terminal · MOTD shipped · Canon Foundation Validated · #519 closed) | **WITHDRAWN** — superseded wholesale by §5. MOTD and the census-terminal bar were unbounded gates of the same class §5 exists to retire |

## Archive

- [`build-to-1.0-campaign-2026-06-30.md`](build-to-1.0-campaign-2026-06-30.md) — predecessor (554 lines). Superseded 2026-07-18. **All 10 of its amendment blocks are dispositioned** in § Rulings Register (verified by count, not asserted).
- [`build-to-1.0-campaign-2026-06-20.md`](build-to-1.0-campaign-2026-06-20.md) · [`build-to-1.0-campaign-2026-06-10.md`](build-to-1.0-campaign-2026-06-10.md) — retained for audit.

> **Orphan recovery: complete, not deferred.** The 06-10 edition's rulings — orphaned when
> 06-20/06-30 superseded it naming only three live threads — were **recovered in-session
> on 2026-07-18** and are dispositioned in § 9a. Counted **17 amendments + 4 scope
> decisions + a goal-state**; the "77 amendment blocks" this campaign had been repeating
> was an unverified number. **No ruling from any edition is now undefined.**

## Amendments

### 2026-08-16 (later) — the Topmost line claimed Movement B's feature ADR was unauthored; corrected at three sites

Operator ruling, verbatim: **"Fix the stale Topmost line (Recommended)."**

**Recording under § 8 *"living: items check off with command evidence"* — not a
sequencing amendment.** No box is removed, nothing is resequenced, no ruling is
carried or withdrawn. Movement B remains TOPMOST and Movement A remains HELD.

**What was false.** Three sites asserted that Movement B's feature ADR did not
exist: the § Topmost line (*"none is authored yet"*), the § Movement B header
(*"new feature ADR extending `ADR-0.33.0`"*), and item 0's Destination clause
(*"The feature slot is unallocated until that ADR is authored; read the next free
one off disk"*). `ADR-0.37.0-airlock-calibration-and-compulsion` was authored
**2026-08-14** — `kind: feature`, `lane: heavy` — and its `## Intent` re-homes
`ADR-0.33.0`'s two disclosed residuals in the same terms item 0 uses, citing the
same `ADR-0.35.0` precedent.

**Magna Carta asserted both halves at once.** The § Amendments 2026-08-15 record
cites that ADR by id and lifecycle in the course of explaining why the resume
gate's arm had no door to retire into — 441 lines below a Topmost line saying no
such ADR existed. The claim was therefore not merely stale; it was contradicted
inside the same document, on the item this plan declares TOPMOST.

**The class is this edition's own named failure.** `.gzkit/rules/governance-core.md`
`0.10.0` — landed earlier the same day — binds that *a value written in a Markdown
doc is illustrative, never authoritative*, and carves out campaign `Status:`-style
prose-as-state as *"a defect with a home, not a pattern to copy"*, homed at
Movement D. This is that defect on the highest-traffic sentence in the repository:
the Topmost line is rendered into every SessionStart digest, so a false premise
there misdirects the sequencing question at the top of every session. Note the
same paragraph already does it correctly one sentence earlier — *"run `uv run gz
adr status ADR-0.33.0-airlock-membrane` … rather than trusting a figure
transcribed here"* — and then hardcodes an existence claim it should have cited.
The habit, not the oversight, is the finding.

**Correction shape.** All three sites now name the ADR and point at
`uv run gz adr status ADR-0.37.0-airlock-calibration-and-compulsion` for lifecycle
and landed count; no count is transcribed. Item 0 additionally records that D1 was
**revised 2026-08-15** (the original inverse-`reach` form withdrawn on measurement)
and that OBPI-01's slug is tracked rename debt, so the next reader does not take
either at face value.

### 2026-08-16 — Movement C: rules arm regresses 0 → 8; adoptable-mechanisms box added (operator-directed)

Operator instruction, verbatim: **"ensure that any deficiencies from your four
proposals have a home in the campaign work, remedy that now."**

**No box removed, nothing resequenced.** Movement B remains TOPMOST; Movement A
remains HELD; the post-1.0 pool ruling is unchanged and the 190 pool items stay
frozen. Two changes, both inside Movement C.

**1. Item 162's rules arm regressed from 0 to 8, recorded rather than absorbed.**
`.gzkit/rules/cli.md` was scored for real under GHI #810, which dropped its
`0.3.1` grandfather pin by construction. The honest score produced **8 Promotable
rows** — the third state the box forbids. The box's own criterion is what makes
this reportable rather than hideable: re-scoring to `Judgment` without amending
the rule text is laundering, so the arm is genuinely open until the arms are
built. Recorded at the box; tracked at GHI #810. The **debt arm moved the right
way in the same pass** (grandfather registry 15 → 14 against `baseline_count` 23).

This is the second time in nine days the family-closure box has been reopened by
measuring a surface nobody had measured. That is the box working — but it also
means **its completion criterion cannot be treated as converging while unscored
surfaces remain.** The scorecard covers `CLAUDE.md` + `.gzkit/rules/**`; arm 2
already records that `.gzkit/skills/**` is unmeasured. `docs/design/**` standards
cited as canonical by a `Validated` ADR were likewise unmeasured until this week.

**2. New box — name the adoptable mechanisms.** Item 160 (The Firewall) defines
what does not ship; nothing defined what an adopter gets. Two working mechanisms
— the shrink-only waiver ratchet and the verifier-pipe-gate hook — had no home
describing them as a deliverable surface. Both fired against this session's own
agent work, which is the evidence they are worth naming. Sequenced **with** item
160, not ahead of it, and explicitly **not** a new pool ADR (Architectural
Boundary 2).

**3. Full re-evaluation pass (operator: *"update that campaign document with today's
date - re-evaluate it thoroughly"*).** Every live claim in the document was
re-measured rather than re-read. **This edition carries the result.** The first pass
stamped the findings inline in the 2026-07-18 edition on the reasoning that
re-evaluation is an amendment (as 2026-08-14 was) and that a new edition is a
supersession act needing an explicit ruling. The operator's follow-up — *"did you
update a fresh document with today's date and sunset the prior?"* — settled it the
other way: a full re-evaluation earns a dated edition. The 07-18 edition is
sunset, this one is `ACTIVE`, and the carry-forward is total.

*What changed:*

| Claim | Was | Now | Where |
|---|---|---|---|
| Oversized modules (>600 lines) | 33 | **51** | § Movement C item |
| `fix` commits, 90d | 524 | 528 | § Topmost |
| `airlock_in` / `airlock_out` | 23 / 5 | **23 / 5 — unchanged** | § Topmost |
| Scorecard Promotable rows | 0 | **8** | item 162, above |
| Pool ADRs | — | ~199 `.md` under `docs/design/adr/pool/` | § 7 |

*What held:* `ADR-0.35.0` `Draft`, `ADR-0.36.0` `Proposed`, `ADR-0.33.0`
`Validated`, GHI #766 and #611 open, and the surface-mirroring ratio (~49% over a
stated 90-day window vs the 47% recorded).

**The sharpest finding is the one that did not move.** The airlock counters are
identical two days into Movement B holding TOPMOST — zero transits — while `fix`
commits rose by four. The ungoverned door widened while the governed one stayed
shut, which is item 150's gap (`GHI : MX :: OBPI : Build`) reproducing in the
window where the Movement was supposedly being worked. It is also evidence for
item 0's sequencing: calibrating a gate nobody passes through is cheaper than
widening it to three more doors.

**Method note.** The surface-mirroring figures were NOT overwritten, because the
window they were taken over is unrecorded; substituting a differently-scoped
measurement would manufacture a false comparison. Today's numbers are recorded
alongside with the window stated. This is the same discipline
`gz validate --transcribed-adr-counts` enforces mechanically — it refused a draft
of this very amendment for transcribing a Layer-2 OBPI count into live prose.

**Origin, stated plainly so it is not mistaken for an independent finding.** Both
changes come from an agent-proposed framing during a 2026-08-16 competitive
review, which the operator directed be homed. The review measured the category as
flourishing on the **authoring** side (GitHub Spec Kit 93k stars; BMAD-METHOD
46.7k; OpenCode 160k) with the **enforcement** side unoccupied in OSS — present
only as academic work and enterprise compliance platforms. The proposal was
positioning, not wind-down: gzkit's differentiator is the enforcement layer, and
it is currently undescribed to anyone outside this repository.

### 2026-08-14 — Movement B is TOPMOST; Movement A is HELD; calibration precedes widening (operator-ratified)

Operator ruling: **"the airlock's incompletemess is a problem that needs priority
address."**, ratified **"yes, ratify"** (spelling preserved).

**What changed.** Movement B (put the membrane on the real doors) moves ahead of
Movement A (close the Foundation Sunset). `ADR-0.35.0-canon-entry-corpus-landing`
is HELD in the in-flight position at 0/10 — not withdrawn, not superseded, and
still the next feature when B releases the queue. One-feature-at-a-time is
unchanged. A new **item 0 — calibrate the seam-map** is added ahead of Movement
B's five existing checkboxes, and the accounting-gap box's count is corrected.

**Why this is new evidence, not a change of mind.** The session that produced this
ruling started as a false-refusal complaint against the handoff resume gate and
ended by reading `ADR-0.33.0` properly. Three findings, each measured live rather
than transcribed:

1. **The airlock is BUILT, not unfinished.** `ADR-0.33.0` is `Validated`, 6/6
   `attested_completed`. "Incomplete" means *installed on one door*, which is what
   Movement B has always said: *"The doors mostly exist. They do not fire… an
   opt-in gate is not a gate."* Nothing about the mechanism needs re-designing.
2. **It does not bite where it does fire.** 20 of 23 transits computed an EMPTY
   seam-map and auto-proceeded; 3 bit correctly (3/4/7 unaccounted → `hold`). The
   cause is `ADR-0.33.0`'s own calibration-frontier note — `reach()` returns
   dependents, a leaf OBPI has none, and `parent_invariants` is never passed. This
   is **WWHTBT-(a)**, the ADR's self-declared load-bearing condition, deferred past
   the FC-2 tracer and never landed. It is not in Movement B's checklist at all;
   item 0 adds it. **Widening before calibrating installs three more inert gates**
   and is § Negative #1 arriving through the front door.
3. **The accounting gap is worse than recorded** — 23 in / **5** out, not 23/10.

**What this ruling does NOT do.** It does not reopen `ADR-0.33.0`, whose
attestations stand. It does not make the airlock a `gz validate` scope (BI #6: the
L3 projection informs the gate, never gates). It does not disturb Movements C or
D, which remain after B and A.

**Sequencing within Movement B (agent-proposed under this ratification; operator
may reorder).** 0 calibrate → accounting gap → the "never entered at all" NC →
GHI/MX door (highest volume) → session entry → ad-hoc/permitted. The two NC-first
alternatives were considered and rejected: the new NC cannot be written until
"should have entered" is defined per door, and it would fail on 524 commits/quarter
before any door exists to close.

**Collateral — retired ahead of the door by operator ruling (AMENDED 2026-08-15).**
The `handoff-resume-gate` hook's `Bash` arm was removed on 2026-08-14
(`bc9b72f67`) as a forked fourth door — an un-extracted variant with its own copy
of the airlock's `proceed|pause|hold|revert` grammar, triggering on
artifact-presence rather than on entry. This paragraph then said its surviving
`Write|Edit|NotebookEdit` arm *"retires **into**"* Movement B item 3 *"rather than
as a loose direct fix, so no gap opens in front of the governed door."*

**That is not what happened, and the plan is corrected rather than left standing.**
The operator retired the whole hook on 2026-08-15 — verbatim: *"the handoff should
be an advisor, not a gate-keeping nanny"* — with ADR-0.37.0 at `Pending` 0/6 and
no implementation, so item 3's door did not exist to retire into. A gap IS open in
front of it, deliberately and on the record: the arm's entire measured lifetime was
**9 lifts to 1 block** across the single day refusal-recording existed, against 13
admission-breadth corrections in 29 days. `REQ-0.37.0-05-02` is amended in the same
commit. Movement B item 3 is unchanged in substance — the door is still owed — but
it no longer inherits a retirement, and it must not re-create the forked entry gate
the arm was.

### 2026-08-11 — the pull-ahead is WITHDRAWN; `ADR-0.35.0` returns to the in-flight position (operator-ratified)

Operator ruling: **"not sure i wan't to author 0.36.0 while we haven't finished
0.35.0"**, ratified **"yes, amend campaign"** (spelling preserved).

**What changed.** The 2026-08-09 amendment pulled
`ADR-0.36.0-convergence-moment-cross-family-critic` ahead of
`ADR-0.35.0-canon-entry-corpus-landing`. That pull-ahead is withdrawn.
`ADR-0.35.0` is the in-flight feature; `ADR-0.36.0` is next-drawn, after it lands.
One-feature-at-a-time is unchanged — this restores which feature is in flight
rather than running two.

**Why this is new evidence, not a change of mind.** The 2026-08-09 (2) amendment
made the critic's delivery STAGED: OBPI-09's automatic `AskUserQuestion` door
ships **dark**, lit only after OBPI-08's pilot measures false blocks, latency,
operator reading time, and decisions changed. The ADR states the cost in its own
words — *"Until that door lights, this ADR does not deliver a second opinion at
every structured choice."* The pull-ahead's justification was that every session
without the critic is a session unguarded; staging means the guard is still off
when all nine OBPIs land. So the trade being made was: pause the feature with ten
authored briefs, to author nine more for a feature that still would not supply
the always-on critic. The staging ruling and the pull-ahead were ratified in the
same session and their interaction was not adjudicated then; it is adjudicated
here.

**Measured at the amendment (Layer-2, not transcribed).** Neither feature has
landed an OBPI — `ADR-0.35.0` 0/10, `ADR-0.36.0` 0/9. The asymmetry is in
readiness, not progress: `ADR-0.35.0` carries **ten authored briefs passing
`gz obpi validate --authored` 10/10**, a 299-line `DESIGN_FORCING_FUNCTIONS.md`,
seven Boundary Invariants, and Fidelity Assertions whose coverage figure is part
of the thesis. `ADR-0.36.0` carries three briefs authored 2026-08-11, six
`draft (scaffold)`, empty Forcing Functions, and a Fidelity Assertions table
still holding the scaffold's example row.

**What is NOT withdrawn.** The promotion (2026-08-09 (3)) stands — `ADR-0.36.0`
remains a promoted `feature` ADR with nine briefs, and its pool file remains
`Superseded`. The staged-delivery ruling (2026-08-09 (2)) stands and is the
*reason* for this amendment. The three briefs authored 2026-08-11 (`1b808b18d`)
keep their value and are not reverted; authoring is durable and re-usable
whenever `ADR-0.36.0` is drawn.

**Re-adjudication check.** This edition's own § Amendments names re-adjudication
as the disease, so the test is stated rather than assumed: this amendment is
admitted because it rests on a fact the 2026-08-09 rulings did not weigh — the
interaction between staging and sequencing — and not on re-arguing either ruling
on its original terms. A future amendment restoring the pull-ahead needs new
evidence in the same way; the pilot lighting the dark door would be it.

**Evidence.** `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` (0/10,
ten `draft`); `uv run gz adr status ADR-0.36.0-convergence-moment-cross-family-critic`
(0/9); `uv run gz obpi validate --adr ADR-0.35.0-canon-entry-corpus-landing --authored`
(10/10 PASS, exit 0); ADR-0.35.0 body repairs at `584778396`.

### 2026-08-09 (3) — the critic is PROMOTED; the box's promotion debt is discharged (operator-ratified)

Operator ruling: **"well, clearly the campaign needs updating. do so please."**

**What changed in the world.** `ADR-pool.convergence-moment-cross-family-critic`
was promoted to `ADR-0.36.0-convergence-moment-cross-family-critic`
(`kind: feature`, `lane: heavy`, `status: Proposed`) with **nine OBPI briefs**,
1:1 with the Feature Checklist; the pool file is `Superseded`. Authored at
`8763ec633`, promoted at `dc5fe4d39`. `gz register-adrs` exit 0 (86 ADRs);
`gz validate --sensitivity` exit 0 across 24 briefs, up from 15.

**Why this amendment is a correction, not a completion.** The Movement A item 2
box carried four claims that were true when written and false by the end of
2026-08-09: that the pool ADR *"owes four things first"*, that
`uv run gz adr promote` *"is fail-closed until the pool ADR gains a
`## Target Scope`… it has neither today"*, that the design sits at
`status: Pool`, and the instruction to *"promote to a feature ADR"*. All four
described discharged obligations. **The box remains UNCHECKED** — the critic is
not installed, 0 of 9 OBPIs are built, and nothing runs at the convergence
moment today. Correcting a stale precondition is not progress on the item, and
this amendment must not be read as such.

**How the four owed items were discharged**, each traceable in the promoted ADR
§ Target Scope rather than restated here: decomposed against the **three doors**
with the `PreToolUse` adapter isolated as OBPI-09 landing **dark**; Step 4b's
resolution shape generalized as OBPI-07 **without editing 4b**; A3 and A4
carried forward ADOPT-NARROWED as OBPI-05 and OBPI-06; and the adversary re-run
already discharged by amendment 2026-08-09 (2) above, whose
`PERFORATED-BUT-NARROWABLE` verdict is what forced the staged shape.

**The staging survives promotion intact, including its cost.** Until OBPI-08's
calibrated pilot measures *"false blocks, latency, operator reading time, and
decisions changed"*, OBPI-09 stays dark and **this does not deliver a second
opinion at every structured choice**. That sentence is carried verbatim into the
promoted ADR's § Target Scope and § Persona precisely so it cannot be dropped
from a status report.

**Sequencing is unchanged.** `ADR-0.35.0-canon-entry-corpus-landing` remains next
after, still `Draft`; one feature at a time still binds, and the pull-ahead
exchanged which feature is in flight rather than starting a second.

### 2026-08-09 (2) — the pull-ahead is STAGED, on the adversary's re-run verdict (operator-ratified)

Operator ruling: **"Amend to staged delivery, keep the pull-ahead."** Selected
from a four-option picker; the alternatives were *land as written and stage
inside the ADR*, *revert the pull-ahead*, and *take the no-build-yet path*.

**This amendment exists because the obligation in the prior one was actually
discharged.** `ADR-pool.convergence-moment-cross-family-critic` § Promotion plan
demanded a re-run of the adversary against the post-R1–R4 design, on the ground
that *"per this ADR's own thesis, that re-test is the point."* It was run
2026-08-09 against the current document and returned
**`PERFORATED-BUT-NARROWABLE`** — neither the rubber stamp that would have
justified promoting as written, nor a repeat of the two prior PERFORATED
verdicts that would have justified reverting.

**What R1–R4 genuinely repaired:** Pass 1 axis 2 (the forbidden same-family
critic) is **dissolved** by R4, and Pass 2's missing-policy attack is
**dissolved at the policy level** by R3. The old verdicts cannot transfer
wholesale, which is why the pull-ahead survives.

**What still perforates, and therefore what the box now requires be staged:** the
automatic door binds to a UI affordance carrying **mandatory clarification** as
well as recommendations, so it *"can prevent the very question those rules
require"*; prose bypasses it; strong subject binding is explicitly unbuilt; and
R1 left the scope-time-vs-conclusion-time question the ADR calls *"live"*
unresolved. Axes 1, 3 and 4 are *partially* addressed, not dissolved.

**The staging, and its stated cost.** Skill, three doors, scope-first challenge,
A3 envelope, R3 transition and provenance binding land first; the automatic
`AskUserQuestion` door ships **dark** and lights only after a calibrated pilot
measures *"false blocks, latency, operator reading time, and decisions changed."*
The cost is recorded rather than softened: until that door lights, the operator
does **not** get the second opinion at every structured choice that prompted the
whole amendment. A3 and A4 are both ruled **ADOPT-NARROWED**.

**A premise correction this session forced.** R4 reasoned that the shipped
Anthropic plugin already supplies the transport. Measured 2026-08-09: the
plugin's `adversarial-review` command reviews **branch diffs** — invoked against
this repository it returned *"No branch diff against main was provided or
present"* — and the `codex:codex-rescue` forwarder is contracted to *"return
nothing"* when Codex cannot be invoked, which is what two empty returns looked
like. R4's **ruling** (run the current Codex, keep it simple) stands; its
**factual premise** about the built-in already covering decision critique does
not. Corrected in the ADR at § R4 transport correction and filed as **GHI #786** so
the question survives the ADR's own lifecycle. This also weakens the adversary's own
strongest no-build argument, which rested on that same premise.

### 2026-08-09 — the cross-family critic is pulled ahead of `ADR-0.35.0` (operator-ratified)

Operator ruling: **"Amend the campaign — pull the critic now."** Selected from a
three-option picker; the alternatives were *scope a minimal always-on hook now,
full ADR later* and *hold sequencing, record today as evidence on the ADR*.

**What prompted it**, operator verbatim, 2026-08-09:

> what happened to our 2nd opinion work? it is supposed to kick in anytime you
> invoke AskUserQuestion.

It has never kicked in, because it was never built. Verified this session:
`.claude/hooks/` contains no critic script, and `.claude/settings.json`
`PreToolUse` carries matchers for `ExitPlanMode`, `Write|Edit` and `Bash` only —
there is no `AskUserQuestion` matcher. `ADR-pool.convergence-moment-cross-family-critic`
is `status: Pool`, unpromoted, holding the full design recovered verbatim from
the three 2026-08-06/07 design transcripts.

**The prior placement, now superseded.** The 2026-08-07 session recorded
placement as *"after 0.35.0 I guess, not ready to decide"* — provisional on its
face — while the same session's register names the real blocker in the
operator's words: *"we need to allow the critic to operate, so that needs
resolution."* Those two have sat in tension since; this amendment resolves it in
favour of the second.

**The observed instance that forced it.** In the session that produced this
amendment the agent presented a four-option `AskUserQuestion` picker on GHI #782
in which it had invented a fourth option, argued in the issue body that the
option dominated the three the issue's author had listed, and recommended it.
The operator accepted it. No cross-family challenge to that premise existed at
any point, and the only scrutiny the recommendation received was the recommending
agent's own. That is precisely the convergence moment § Intent of the pool ADR
names, and it passed unchallenged — the design's own worked example, produced
while the design sat parked.

**Consequence for the one-feature-at-a-time ruling (§ Rulings Register).** The
standing ruling is *"only one feature at a time, feature, finish, draw from
pool."* It is NOT relaxed. `ADR-0.35.0-canon-entry-corpus-landing` is `Draft` at
**0/10** OBPIs — authored, never started — so pulling the critic ahead exchanges
which feature is in flight rather than running two. `ADR-0.35.0` returns to the
queue at the position the critic vacates and is the next feature drawn.

**Scope of this amendment.** Movement A's remaining items are re-ordered; no box
is removed, no Movement B/C/D box is touched, and the post-1.0 pool ruling (§7)
is unchanged. The critic is promoted from pool to a feature ADR and worked
through the governed path — ADR → OBPI → gates — not hand-wired as a hook, which
was the declined second option.

### 2026-08-08 (2) — the family-closure box is re-scoped, not checked off (operator-ratified)

Operator ruling: **"Keep open, re-scope to the criterion."** Selected from a
three-option picker; the alternatives were *check it off* and *split the box*.
No box removed, nothing resequenced, no change to Movements A, B, or D, and no
change to the post-1.0 pool ruling.

**What prompted the question.** All six issues the box names by number are
CLOSED — validator-side `#692`, `#693`, `#770`; agent-side `#459`, `#574`,
`#620` (verified via `gh issue view`, 2026-08-08). The corrected failure-class
index puts live work in three other chains. On the enumerated reading the box
was dischargeable.

**Why it is not.** The box's own completion criterion is class-level and says so
in its last sentence: *"it closes the family rather than the instance."* The six
numbers are exemplars proving the class exists. Checking the box on their
strength would be the enumerate-the-exemplars habit the criterion was written to
resist — and it is the failure shape §9a records for the 06-14 rulings that were
*"booked and never rendered"*: work marked done because its visible instances
closed, while the discipline it declared went unwitnessed.

**The re-scope, and the instrument that makes it measurable.** No new machinery
is proposed. `docs/governance/advisory-rules-audit.md` already scores every
clause of `CLAUDE.md` + `.gzkit/rules/**` on four values and is self-tested by
`gz validate --advisory-scorecard`. Those four values *are* this box's criterion,
which nobody had noticed:

| Scorecard score | Criterion state |
|---|---|
| **Mechanical** | carries a mechanical witness ✓ |
| **Judgment** | demoted to advisory in its own text ✓ |
| **Promotable** | **the third state — declared, no witness, not marked advisory** |
| **Ambiguous** | **the third state — scope unclear enough that nothing can witness it** |

The box completes against that criterion and two named arms — the rules arm
(drive the third state to zero, by mechanizing or by amending the rule text;
re-scoring alone is laundering) and the skill arm (`.gzkit/skills/**/SKILL.md`
mandates have **zero** scorecard coverage, which is exactly where all three
agent-side exemplars lived). The debt arm is already mechanized and carries no
new work.

> **Count corrected 2026-08-08 — the ratified criterion above stands unchanged;
> only the measurement under it was wrong.** As first written this paragraph read
> *"Measured 2026-08-08 over the audit: 63 Mechanical, 27 Judgment, **12
> Promotable + 2 Ambiguous = 14 rows in the forbidden third state**"* and the
> rules arm read *"drive 14 → 0."* No figure reproduces: the audit had not been
> touched since 2026-08-06, and the third state is **9 `Promotable`, 0
> `Ambiguous`**. The `2 Ambiguous` was the legend row plus the Summary row
> counted as rules — a `grep -c` over a rendered table, which is the exact
> failure the same session recorded in its own handoff as *"an existence check
> wearing a truth check's clothes."* The live count now lives only in the
> scorecard's Summary table and is fenced there by
> `gz validate --advisory-scorecard`, per the GHI #768 ruling on this class.

**One limit recorded, not hidden.** The skill arm is not *failing* today — it is
**unmeasured**. Stating it as an open arm rather than a clean one is deliberate:
an uncovered surface reported as green is the same defect this whole family
names, and the box would otherwise inherit it.

### 2026-08-08 — C2 checked off; the "single source" claim made true (operator-ratified)

Operator rulings, verbatim, in order: *"Determine C2 status first"*, then
*"Close the residual now (Recommended)"*, then *"Check C2 + sync"*.

**Why this amendment exists at all.** The resumed handoff advised *"Land the C2
enrollment fail-close (GHI #744)"* as its second next step. **That step was
stale on the day it was authored** — #744 closed `COMPLETED` 2026-08-02 at
`0f671b31c`, six days earlier. The handoff had read the `(GHI #744)` parenthetical
in this box — a citation for the criterion the 2026-08-07 amendment adopted — as
unlanded scope. The agent's own recommendation was to set that step aside and pull
GHI #770 instead; the operator overrode it to verify this box's criterion against
source first. That verification is what found the residual below. Recorded as an
`improvement` insight under scope `campaign-item-verification`.

**What the determination found.** Two of the three sub-claims already held. The
third did not, and had not since the #618 collapse: `VALIDATOR_REGISTRY`'s header
called itself *"Single source of validate dispatch"* while `--qc-binding`,
`--fidelity-presence` and `--waiver-ratchet` reached `gz check` without ever
appearing in it. The roster **accommodated** them (`reached_outside_registry`)
rather than closing the gap, and `tests/governance/test_check_scope_parity.py`
documented the contradiction in its own docstring while asserting only that the
exceptions were *classified*.

**This residual was a member of the family the 2026-08-07 amendment ratified a box
to close** — a declared discipline with no mechanism behind it, the same shape as
#770, #692 and #693. It had already produced one real defect: GHI #630 found every
SUPPORT REQ citing one of the three resolving `unproven-support` regardless of
truth, because `_dispatch_validator_scope` resolves scopes through the
registry-derived runner maps. That was patched by hand-wiring a **third** copy of
the scope→audit knowledge (`_early_return_scope_audit`) — fixing the instance, not
the class.

**The fix is reductive, which is the point of Movement C.** Registering the three
(tier `explicit`, `in_other_scopes=False`, matching the `sensitivity` /
`unscoped_rules` / `evaluation_justify_binding` precedent) retired that map:
**+27 source lines, −45, net −18**. The fence now asserts `reached − registry == ∅`
rather than accommodating the exception, and the exclusion-set golden gained a
`_POST_SNAPSHOT_OTHER_SCOPES_EXCLUDED` hatch mirroring the GHI #741 pattern, so the
pre-collapse snapshot stays measured evidence rather than being edited.

**Observed behavior is unchanged in every case** — `_dispatch_early_return_scopes`
still fires first and short-circuits, so each flag keeps its solo 0/2/3 lifecycle
and custom prose: the three solo invocations exit 0, `--qc-binding --documents`
still exits 1 with the GHI #704 refusal verbatim, and bare `gz validate` still runs
13 default scopes.

| Verification | Result |
|---|---|
| `uv run gz arb ruff` | exit 0 · `arb-ruff-317c63275e4b4da09715b23f44238a27` |
| `uv run gz arb typecheck` | exit 0 · `arb-step-typecheck-23d951968d684fdeb626cabf3296cb6f` |
| `uv run gz arb step --name unittest -- uv run -m unittest -q` | 8089 tests OK, exit 0 · `arb-step-unittest-32be07bf2f2545f8b92fc95b674b8ae7` |
| `uv run gz check` | exit 0 |

**One limit recorded, not hidden.** The stale "94 scopes" figure this box carried
matched no enforced surface, and nothing coupled it to one. That is
**GHI #768's exact shape** (*transcribed counts couple to nothing*) sitting inside
the campaign that governs sequencing — the same class of defect as the stale
advised step that opened this session. #768 remains open with no remedy selected.

### 2026-08-07 (2) — Movement C gains a family-closure box; C2 retargeted off flag count (operator-ratified)

Operator ruling, verbatim: *"ratify both, write handoff, git-sync"*.

Two changes to Movement C. **No box removed, nothing resequenced**, no change to
Movements A, B, or D, and no change to the post-1.0 pool ruling.

**1. New box — close the doctrine-declared-without-mechanism family.**
**2. C2 amended** — completion criterion is family closure, not flag count. The
surface read 81 scopes at GHI #618, 92 when the box was authored, and **94** on
2026-08-07: it grew while its reduction box waited. Collapsing the count without
landing the enrollment fail-close (#744) leaves #704, #745, and #748 live.

**Why this is a reframing, not an expansion.** "Reduce the accretion" invites
shrinking 94 scopes, but most are load-bearing one-off checks over a genuinely
large surface. The evidence says the target is **stopping two families from
producing scope #95** — a different verb.

**Evidence, and the instrument that produced it.** The operator declined to
ratify against throwaway analysis (*"Build the class-of-failure index first"*),
so the detector was built as a real surface first: chore `failure-class-index`,
module `src/gzkit/insights/failure_classes.py`, commit `ae4e6dc8c`. It reports,
over the 333 GHIs closed since 2026-05-09:

| Measure | Value |
|---|---|
| Carrying an authored `## Class of failure` section | 288 of 333 (87%) |
| Declaring themselves a recurrence of a named prior class | 71 of 288 (25%) |
| Recurrence chains of depth ≥ 3 | 15 |
| Deepest chain | 12 |

**The precedent this box is modeled on.** Layer drift — the one family measurably
*closing* (10 → 7 → 6 → 1 across May–Aug) — closed because it got three things:
a doctrine (`state-doctrine.md`), a regenerator (`gz register-adrs`), and a
fail-close (`gz validate --adr-status-fresh`). The doctrine family has the first
two at best. That triple is the template.

**Two limits recorded on the ratification, not hidden.** The ~19-member figure
spans two chains that **no author has linked to each other** — treating them as
one family is an operator judgment, not a measurement. And the index detects
*declared* recurrence only, so it is a floor: a family nobody names stays
invisible to it too.

### 2026-08-07 — Movement A count correction: ADR-0.35.0 is 0/10, not 0/9 (operator-ratified)

Operator ruling, verbatim: *"Fix it and file the class-level defect"*.

`uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` reports **0/10** —
ten briefs, `01`–`10`, all `pending`/`draft`. The Topmost banner and Movement A
item 2 both read `0/9`.

**Not an authoring error — coupled-surface drift.** `0/9` was accurate until
`c5a2614db` (2026-08-02) folded the classification reader in as item 10 under
GHI #737. That commit updated no surface that counts OBPIs, so the stale figure
survived and then **propagated by transcription** into
`ADR-pool.primary-source-corroboration` (authored 2026-08-07), which quoted the
campaign rather than Layer-2. Both live sites are corrected here; the ADR line
was corrected in the same pass.

**The 2026-07-29 record at § Amendments is deliberately NOT changed.** Its
*"verified `Draft` 0/9"* was true on the date it was written — OBPI-10 did not
exist for another four days. Amendment records are dated history; correcting one
to match today's count would falsify the record rather than repair it.

**Class-level defect filed as GHI #768**, per the same ruling: nothing couples
adding or removing an OBPI to the surfaces that quote its count. 135 files under
`docs/` carry a transcribed count; the remedy family is undecided, including the
option of not writing the number down at all.

**Derived-count correction, not a scope change.** No checklist item moved, none
was added or struck; sequencing is unchanged.

### 2026-07-31 — Movement A capstone reaches 5/5; remaining work is the ceremony, not OBPIs (operator-ratified)

Operator ruling, verbatim: *"update handoff and campaign, then git sync"*.

`OBPI-0.34.0-04` (`d521ace53`) and `OBPI-0.34.0-05` both reached `attested_completed`,
so `ADR-0.34.0` is **5/5**. Verified against the governed read, not frontmatter:
`uv run gz adr status ADR-0.34.0 --json` renders `lifecycle_status: "Pending"`,
gates `1–4 pass` / `5 pending`, `Closeout READY`, `validated: false`.

**The item does not check off.** § 9a scope decision #3 (**CARRIED**) sets the per-ADR
done-bar at `Validated` or operator-parked — not at 5/5 OBPIs. What changed is the
*shape* of the remainder: the line previously read *"remaining is OBPI-04 and OBPI-05
alone"* and now reads **the closeout ceremony alone**. Movement A's capstone is one
Gate-5 attestation from done, and the Topmost banner is repointed accordingly.

**Fourth occurrence of the identical drift on the identical line** (1/5 → 2/5 → 3/5 →
5/5). The 07-29 mitigation — labelling the number a *snapshot* and shipping
`uv run gz adr status` beside it — did **not** stop it, and could not have: the value
is still hand-carried in Layer-1 prose that the SessionStart banner quotes verbatim.
Labelling a transcribed derived value does not stop it going stale; only rendering it
does. This is the standing evidence for the **Movement D** box *"the campaign body as
a rendered Layer-3 view"* — that box is the actual fix, and every future recurrence of
this amendment is interest paid on not having built it.

**Derived-count correction plus a remainder-shape correction. No checklist item moved,
none was added or struck; no ruling is carried or withdrawn.**

### 2026-07-29 — Movement A count correction: ADR-0.34.0 is 3/5, not 2/5 (operator-ratified)

Operator ruling, verbatim: *"fix discrepancy"*.

`OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement` reached
`attested_completed` on 2026-07-29 (`f6088fabc`), so the true count is **3/5**.
Verified against the governed read, not the frontmatter: `uv run gz adr status
ADR-0.34.0` renders `OBPI 3/5`, with closeout `BLOCKED` on OBPI-04 and OBPI-05
alone.

**This is the second occurrence of the identical drift on the identical line,
four days after the correction below — so the line no longer carries the number
alone.** The capstone line hand-copies a value `gz adr status` computes, and the
session-boot banner quotes that line verbatim; every OBPI that lands therefore
re-stales the top of every session, and clearing it costs an operator ruling each
time. The count now ships with its refresh command beside it, labelled a
snapshot rather than a fact. Per `docs/governance/state-doctrine.md`, a Layer-1
doc hand-carrying a Layer-3 derived value is Architectural Boundary 6 read from
the other end: the drift is the same whether the derived view is mistaken for
truth or truth is transcribed from the derived view.

**Also corrected, same class — this half is agent judgment; reverse it freely.**
The Topmost line routed the NEXT item at **GHI #623**, `CLOSED` 2026-07-19.
Item 2 of Movement A already states *"Do not reopen #623 **or #654** to find
this scope; read the ADR"* and names `ADR-0.35.0-canon-entry-corpus-landing` as
the tracker — so the banner contradicted the checklist it summarizes and aimed
scope discovery at a closed issue. Repointed at the ADR (verified `Draft` 0/9).
The item, its sequence position, and its checkbox are unchanged.

**Derived-count correction, not a scope change.** No checklist item moved, none
was added or struck.

### 2026-07-25 — Movement A count correction: ADR-0.34.0 is 2/5, not 1/5 (operator-ratified)

Operator ruling, verbatim: *"#715 + campaign line 131"*.

The Movement A capstone line recorded `ADR-0.34.0` at **1/5**. Layer-2 carries a
second attested completion — `OBPI-0.34.0-02-authoring-time-kind-rejection`,
`attested_completed` with full receipt evidence — so the true count was **2/5**.
Verified against the governed read, not the frontmatter:
`uv run gz adr status ADR-0.34.0` renders `OBPI 2/5` with OBPI-01 and OBPI-02
both `attested_completed`.

This is a **derived-count correction, not a scope change.** No checklist item
moved, none was added or struck. It is recorded here because the session-boot
orientation banner quotes that line verbatim, so the stale count was
re-injected into the top of every session — and it had been carried unedited
across six handoffs, because campaign amendments are operator-ratified and no
session had held the ruling to make it.

### 2026-07-18 — Disposition change: TSP routing, not a rush to 1.0 (operator-ratified)

Operator, verbatim: *"we need to change the disposition of the campaign, it is not
'rush to 1.0 now.' it is, what is the best 'traveling salesman' path through the backlog
to 1.0. I think there is a tone and temperament misalignment here."*

**CARRIED — binding on this and every successor edition.** The plan optimizes the *route*,
not the *finish date*. Consequences:

1. **The set is taken as given; the win is in the ordering.** Set-shrinking moves
   (bounding gates by dated census, declaring items "explicitly NOT 1.0 gates",
   deferral rulings) are no longer the instrument of progress. Items are *sequenced*,
   not *excluded*. This is why they kept resurfacing as re-adjudication.
2. **Re-entry cost is the metric being minimized.** Measured this session: ~40 orphaned
   governance docs, agents re-deriving structure from source each session and getting it
   wrong. That is a re-entry-cost failure, and it is gzkit's actual disease — not
   accretion volume.
3. **Adjacency is the primary object.** Items that share setup cost are visited together.
4. **The pool is visited as we inch forward** (operator, 2026-07-18) — not a post-1.0
   wall. This **AMENDS §7**: the pool is a far cluster routed to late, not a category
   ruled out. Nothing gets orphaned; nothing resurfaces as *"but we booked that for 1.0."*
5. **Tone is not cosmetic — it selected the plan.** The frustration register of this
   edition ("the road to 1.0 was dragging", "largest single line item on the board")
   produced Movement C item 1, which proposed deleting shipped product to reduce a commit
   count. Temperament defects become correctness defects.

### 2026-07-18 — The rhythm: four mechanisms, four jobs (operator-ratified)

Operator, verbatim: *"AGENTS.md -> how we work; magna carta -> what we are working on.
handoff -> what we were doing last. airlock -> a sortie into the environment. handoff ->
a market [marker] for when we leave the session. That should be our rhythm."*

Also: *"much of agents is there to remind you how I'd like for our working partnership to
exist. the magna carta should help tell the 'story of gzkit' so we stay focused on
emerging priorities AND the executive summary of what gzkit is. It is there to help you."*
And: *"the airlock and magna carta gives us a sense of connectedness/cohesion among the
items."*

| Mechanism | Job |
|---|---|
| `AGENTS.md` | **how we work** — the working partnership, behavioral contract |
| Magna Carta | **what we are working on** — the story of gzkit, the executive summary of what gzkit *is*, and emerging priorities |
| handoff (entry) | **what we were doing last** — informs the airlock entry |
| airlock | **a sortie into the environment** |
| handoff (exit) | **a marker for when we leave the session** |

**Binding consequence: the Magna Carta MUST carry the story and the executive summary.**
This edition does not — §1 is three lines and the remaining ~24KB is movements, rulings,
and census tables. The story half atrophied, which is why each session re-derives what
gzkit is from source. Restoring it is not decoration; it is the orientation organ, and it
lives here rather than in a hook. Airlock + Magna Carta together supply
*connectedness/cohesion among the items* — the route is not a flat list.

### 2026-07-18 — Movement C item 1 retires: install-time assembly already ships

Evidence, this session: `gz init` (`src/gzkit/commands/init_cmd.py:894`) copies only
*canonical inputs* from the wheel via `importlib.resources`, then calls `sync_all()`,
which **generates** every vendor surface in the adopter tree. No pre-rendered `AGENTS.md`
or `CLAUDE.md` ships in the wheel; adopters have never received one. The surviving
file-copy (`sync_pkg_surfaces`, `sync_surfaces.py:701`) is wheel-payload staging, hard
no-op'd for adopters by `_pkg_surface_exists` (`:626`).

- **"Generate at install, not at commit" is already true for the product.** Item retires
  as delivered, not as wrong.
- **Operator ruling: gzkit keeps committing its own mirrors while dogfooding** — verbatim:
  *"we are dogfooding, so we have to keep on generating/mirroring until the product settles
  a bit more."* The 703 `gz git-sync` commits are the dogfooding artifact, an accepted
  cost, and **not** a reduction target.
- **The control surfaces are integral product** (operator, verbatim: *"five copies are
  wheel-borne. the control surfaces are an integral part of the product"*). Already
  mechanized at `.gzkit/manifest.json:45-59` + `gz validate --distribution` (ADR-0.0.31);
  the prose surfaces contradict it by calling them "mirrors / generated / do not edit",
  which misled an agent twice this session.

### 2026-07-18 — Findings booked this session (route inputs, not yet sequenced)

- **~40 orphaned governance docs** (~450KB) under `docs/governance/`: 2 DELIVERED,
  ~24 POINTER-ONLY, ~40 ORPHANED. Includes `agent-control-surface-rendering-substrate.md`
  (26KB, foundation-tier) whose own `## Agent Orientation Index` opens *"Do not re-derive
  the rendering architecture from source each session"* — and which has **zero referrers**
  anywhere in the per-turn surface.
- **The repo diagnosed this on 2026-05-30** (`.gzkit/insights/agent-insights.jsonl:146`):
  *"nothing loads relevant prior learning at decision time … Capture without re-injection
  does not bind."* Prescribed fix: a hook. Shipped (OBPI-0.0.37-27, attested 2026-06-15):
  a markdown section inside the unread document. **Correction, not enhancement — routes
  under ADR-0.0.37.**
- **`instructions-files-diet` chore acceptance criterion #9** treats *the existence of a
  hyperlink* as proof pedagogy is reachable (`CHORE.md:152`); all six evidence commands
  measure weight reduction, none measures retrieval.
- **Two CMS facades** (§4 class): `validate_render` fires only when `project_root` is
  passed, and `sync_agents_md` (`sync_surfaces.py:407`) does not pass it — the one render
  that ships a surface skips fidelity validation. Temperature is inert —
  `pipeline.py:96-101` documents output is byte-identical across all valid temperatures.
- **`render_content_surface()` (`sync_surfaces.py:637`)** — the doctrine-conformant
  render bridge — has zero production callers; one test keeps it alive.
- **Still no `Corpus → str` materializer**; `compose()` validates a hand-authored
  candidate. Prior session's finding stands unrefuted.

### 2026-07-18 — Re-adjudication is the named disease, and it fired again

Operator, verbatim: *"I swear we've covered this before."* Movement D already diagnoses
exactly this — *"nothing in gzkit represents the state 'settled'"* — and its fix
<!-- gz-validate-skip: command-shape -->
(`ruling_issued` / `ruling_superseded` typed events, a `gz ruling` verb) is unbuilt, with
this register as the manual stand-in. The pattern across all three of this session's
findings: **the diagnosis was correct, written down, and terminated in prose instead of a
mechanism.** Orphaned maps (authored, not retrieved) · orientation index (prescribed as a
hook, shipped as a paragraph) · rulings (diagnosed as needing typed events, shipped as a
table someone must remember to fill).

### 2026-07-18 (later session) — Movement A item 1 closed; audit route inputs booked

**Recording under § 8 "living: items check off with command evidence" — not a sequencing
amendment.** Movement A item 1 is checked off with the evidence inline; the queue order is
untouched and no ruling is carried or withdrawn here. Anything below that would change
sequencing is marked as needing operator ratification.

`ADR-0.0.37` is `Validated` (`b40a8026`). The `/gz-adr-audit` ceremony ran with the
independent persona dispatches the skill mandates, and they disagreed — which is the point:

- `spec-reviewer` **PASS** — every BEHAVIOR REQ on all 15 linked OBPIs is `@covers`-covered.
  The 57-REQ advisory is honest: of the 27 belonging to linked briefs, 26 are `[SUPPORT]`
  and 1 is `[structural-fence]`, exempt by proof channel under `ADR-0.0.59`.
- `quality-reviewer` **CONCERNS** — Layer-1 attribution drift, remediated before the receipt
  was emitted. The driver independently verified each claim and **refuted one** (`F3`:
  `tier_policy` does have live consumers at `composer.py:20`,
  `rendition_floor_coherence.py:24`).

**Route inputs (not yet sequenced):**

- **GHI #700 — FIXED, `77ad9d70`.** `_AC_LINE_PATTERN` tolerated markdown emphasis around
  the REQ id but not around the kind tag, so `**[BEHAVIOR]**` lines fell to a *warn-only*
  skip branch. `ADR-0.34.0-foundation-sunset` — the Movement A item 3 capstone — was
  silently losing **6 REQs, 5 of them BEHAVIOR**, while `audit-check` reported exit 0.
  Repo-wide scan after the fix: **0 remaining unparseable REQ lines.** Item 3's coverage
  arithmetic could not have been trusted before this landed.
- **GHI #701** — the uncovered-REQ advisory is REQ-kind-agnostic, reporting SUPPORT and
  STRUCTURAL-FENCE REQs as owing `@covers`. Steers agents directly into the
  `.claude/rules/adr-audit.md` Rules (c) anti-pattern. Same limitation already documented
  for the sibling behave gate at `data/behave_coverage_waivers.json:79,80,82`.
- **GHI #702** — a fidelity assertion row can name the fidelity gate as its own command.
  `ADR-0.0.37` row 4 asserted *"the block is parseable by the fidelity gate"*, verified by
  running that gate; it cannot fail while being evaluated. **This is §4's failure class
  inside the mechanism ADR-0.0.73 built to enforce §4** — cross-linked to GHI #699 as a
  sibling cut (#699 audits the 47 enforcement claims; #702 is the same shape on the
  fidelity-assertion surface, which #699's audit did not cover). A sweep of existing
  `## Fidelity Assertions` blocks for the same row is unscoped.
- **GHI #703** — `REQ-0.0.37-15-05/-06` are `[SUPPORT]` yet `@covers`-decorated: the
  inverted proof channel, inflating apparent coverage. Non-blocking (withdrawn brief).

**Observation for Movement A item 2 (GHI #623), needs no ratification but changes what the
successor inherits.** The audit's Attribution repair is now the honest inventory: the
composition engine's *shipped* half — `rendition_store.py`, `rendition_freshness.py`,
`composer.py`, `tier_policy.py` — originates in the **withdrawn** briefs 21/22 and is
load-bearing. What is genuinely absent is the attributable corpus→candidate generator and
the `rendition ⊆ corpus` lineage gate. The feature ADR re-homing this should scope to the
absent half, not re-declare the shipped half as new work.
