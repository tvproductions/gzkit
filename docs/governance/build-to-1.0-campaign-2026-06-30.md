<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Build-to-1.0 Campaign — 2026-06-30 (Magna Carta)

Status: **ACTIVE — the one canonical plan** (operator-ratified 2026-06-30).
Supersedes [`build-to-1.0-campaign-2026-06-20.md`](build-to-1.0-campaign-2026-06-20.md)
and the earlier [`build-to-1.0-campaign-2026-06-10.md`](build-to-1.0-campaign-2026-06-10.md);
priors are retained for audit and no longer steer. **This edition commits the
airlock-in/out constellation orchestration (Movement III) to the critical path** —
the 2026-06-30 re-sense-needs-a-computed-graph pivot (§3a) and the keel-up
constellation (KEEL state-machine → HULL graph substrate → HATCH membrane →
deferred RECALL) that realizes the §8 "work-phase theories lawful" 1.0 gate.

> **This file is slim by design — the steering surface fits in a session. The
> Queue (§7) is the daily driver.**
>
> **It steers; the spine propels.** The engines (§3) and the floor (§5) do the
> work; this plan only sequences them. Amendments are operator-ratified and
> **append to the dated archive, never inline** — inline accretion is the disease
> that killed the predecessor. It dies only by a ratified successor.

> **Topmost (sequenced):** Movement III — realize the entry airlock as the keel-up constellation — is **COMPLETE**. **Phase 0 (airlock-in, GO attested 2026-07-02), Phase 1 (KEEL `obpi-state-machine`, released [v0.31.0](https://github.com/tvproductions/gzkit/releases/tag/v0.31.0) + Validated), Phase 2 (HULL `gzkit-ontology`, released [v0.32.0](https://github.com/tvproductions/gzkit/releases/tag/v0.32.0) + Validated 2026-07-07), and Phase 3 (HATCH `airlock-membrane`, released [v0.33.0](https://github.com/tvproductions/gzkit/releases/tag/v0.33.0) + Validated 2026-07-12) are all complete.** Movements I & II complete. **Phase 3 (HATCH) closed the loop 6/6:** the tracer trio (OBPI-01 data-model+events · OBPI-02 airlock-IN + pipeline Stage 1 + §5 live NC · OBPI-03 airlock-OUT + Stage 5) and the gated-breadth doors (OBPI-04 mx · OBPI-05 permitted-entry) `ATTESTED COMPLETED` by g0, then OBPI-06 (doctrine-lawful — the one-way §2 seam-widening) discharged the §8-gate box, ADR closed out + released, and `/gz-adr-audit` **Validated** (bound fidelity gate 4/4; spec-reviewer PASS + quality-reviewer COHERENT; in-flight defect GHI #679 fixed direct — exit-side failure-atomic pairing, commit `89c5ee9a`). **Topmost is now the remaining pre-1.0 work: the deferred Phase 4 — RECALL (severable enrichment behind the shipped floor) and the Movement IV reduction track (taxonomy migration · `validate()` registry collapse #618 · oversized-module census).** The airlock ships and gates on the floor (Phases 1–3) alone; RECALL is enrichment, not a 1.0 blocker (§8). Operator selects the next pull per the sequencing ruling.
>
> Everything else waits behind the airlock constellation. See §7.

---

## 1. What gzkit is (identity — unchanged)

**Research instrument + published exemplar → personal toolkit → public product.**
1.0 serves the first identity; adoption is not a 1.0 gate. gzkit's purpose is to
make stochastic LLM vibing **structurally inert** — not by exhorting agents to
behave (they vibe regardless), but by making every claim **falsifiable by a live
test**.

## 2. Where we are (the reckoning)

gzkit became a **vibe monster** — the anti-vibing machine accreted the very
surface it warns against. The evidence is code-grounded in
[`state-of-gzkit-2026-06-20.md`](state-of-gzkit-2026-06-20.md): integrity gates
that return `[]` on real violations; tests that *certify* that inertness; a
QC "antibody" (ADR-0.0.73) whose own detection is hollow yet passed human
attestation; 70 validate scopes behind a 162-param function; 269 ADRs; 33
oversized modules.

**Root cause (named, verbatim from independent review + Anthropic's own
practice):** *enforcement-claim drift* — governance asserts "validated /
fail-closed / enforced," the test exercises a weaker path, and the human attestor
sees a green facade. Anthropic's production analytics system states the law
directly: **"Governance without enforcement quickly decays back to the multiple
candidates problem."** gzkit already has *more* governance structure than that
system; the discipline it lost is that **enforcement must actually fire.** The
whole campaign is the recovery of that one property.

## 2a. The lightness lesson (superpowers — captured 2026-06-20)

An independent strawman/steelman against
[obra/superpowers](https://github.com/obra/superpowers) (14 Markdown skills, one
always-injected router, no ledger, MIT, multi-harness, **≈234.6k★ / 21k forks** —
GitHub API, 2026-06-18) returned an identity-forcing verdict:

- **Superpowers is a different thing, not a substitute.** On the one axis where
  they compete — making a single agent plan, test, and not vibe — superpowers is
  at least as effective and *dramatically* cheaper to maintain. Most of gzkit's
  anti-vibe doctrine is achievable as prompt discipline; superpowers proves it
  with ~14 pressure-tested skill files and no machinery.
- **gzkit's irreducible moat** (superpowers cannot copy without *becoming* gzkit):
  the **tamper-evident JSONL ledger as system-of-record + fail-closed human
  attestation + the runtime negative-control enforcement rule (§5).** That —
  forensic, cross-session auditability — is the *only* place gzkit's weight is
  justified; superpowers explicitly declines to build it ("if you lie, you'll be
  replaced" is reputational, post-hoc, unenforceable).
- **The ruling it forces (consistent with §1 identity):** keep the never-relax
  floor (§5) and the ledger; **shed everything else aggressively toward
  superpowers-lightness.** Heaviness never caused good behavior — the floor does;
  the rest is the vibe-monster. This is the reduction mandate, externally
  corroborated.

**Steal (booked):** (1) the **always-injected single-router bootstrap** — demote
the giant per-turn AGENTS.md/CLAUDE.md contract to on-demand pull behind a router
(`gz-skill-router` becomes the *injected* surface); (2) the
rationalizations-table / red-flags / checklist **SKILL.md format**; (3) cite
superpowers' RED→GREEN `writing-skills` (mandatory negative controls, ≥5 reps,
pressure scenarios: time / sunk-cost / authority / exhaustion) as **external
corroboration of §5** and adopt it as the *test design* for gzkit's
negative-control tests; (4) keep the skill layer **harness-portable Markdown**,
not `gz`-CLI-welded, if reach beyond Claude Code ever matters.

## 3. Modes — the four airlocks (and the two engines over them)

gzkit has **four modes, each entered through the same airlock** — way-in
(seam-map → go/no-go) · work · way-out (drift-diff → block/surface/resolve).
Every unit of work crosses exactly one. Two **engines** (a direction + a version
bump) run over the four modes. *(Operator realization, cemented in the
airlock/seam discussion, 2026-06-20.)*

| Airlock (mode) | What it does | Unit / instrument | Engine | Bump |
|---|---|---|---|---|
| **Design** | author / evaluate PRD · ADR · OBPI · REQ · TASK (intent / LAW) | the artifacts | forward | none |
| **Build** | construct fact to fulfil intent | the **OBPI pipeline** | forward | **minor** |
| **MX** | find designs that were *wrong* or *wrongly-implemented*, repair | **GHIs** — its squawks | maintenance | **patch** |
| **Chores** | recurring quality / hygiene maintenance | the chore-runner | maintenance | **patch** |

**GHI : MX :: OBPI : Build.** A GHI is *not* a mode — it is MX's **squawk**: the
work-order that opens at entry and the receipt that closes at exit, exactly as the
OBPI is the Build airlock's unit. MX is where we ask, of a shipped design, *was it
wrong, or was it wrongly implemented?* — and repair either the intent or the fact.

**Intent hierarchy (what the Design airlock authors/evaluates):** Constitution
(enduring root) → **PRD — one per major version** → ADR → OBPI → REQ → TASK.

**MX granularity** mirrors Build's lite/heavy: **light MX** = a single squawk on
the existing **GHI direct-fix** path (Defect-fix routing thresholds; the GHI is
the work order *and* the receipt) — marker-light, the daily-rhythm fix; **full
MX** = a sustained hangar session (marker on, many squawks, the hard-exit
re-cert). The never-relax floor (§5) binds both. **Chores** is the fourth airlock:
*scheduled MX plus hygiene* — recurring and cadence-triggered, not squawk-driven.

The two engines detail below; every unit of work is one or the other.

### 3a. Forward engine — pool → feature, through the airlock

- **Taxonomy reset (operator ruling 2026-06-20 "move everything to pool", refined
  2026-07-05 to a *partition* — see § Amendments):** `foundation` is **retired as a
  live kind** (no new foundation ADRs) but survives as a **frozen-historic class** —
  every **completed/Validated** `0.0.x` foundation **remains in place** with
  `kind: foundation` as the historic, invariant-shaping record (kept, not dropped);
  only **unstarted/pending** foundations **drop to pool** (inert backlog). Two kinds
  are **live** going forward: **pool** = universal backlog/origin; **feature** =
  committed, release-carrying. The **release line is the source of truth for what
  is shipped** — not 269 ADR `status:` frontmatters (the frontmatter we proved
  unreliable). Built code stays live; only the *classification* of unstarted work
  resets. Features earn back to release **one at a time**, with executable proof.
  This migration is **pre-1.0** (2026-07-05 ruling), exempt from the post-1.0
  reductive-deferral.
- **The airlock is the work discipline:** *way-in* (compute/enumerate the
  seam-map → **go/no-go before work**), *vertical* (ADR → OBPI → REQ → TASK),
  *way-out* (drift-diff / reconcile → block · surface · resolve). AIRLOCK-OUT is
  already mature (reconcile/validate/attest); **AIRLOCK-IN is the unbuilt cure**.
  **Pivot (2026-06-30, operator-ratified):** re-sense is its keystone and real
  re-sense needs a *computed graph* (an agent's working model is a lossy, stale
  snapshot — "I didn't see that" is an observation-completeness failure no
  by-hand gate can close). So the graph moves ONTO the critical path and
  AIRLOCK-IN/OUT realize together as **one keel-up constellation**, not
  judgment-grade-now / tool-compute-later. See Movement III.
- **A feature advances via the pipeline (minor) or via MX (patch).**

### 3b. Maintenance engine — levels → MX hangar (self-repair)

- **Gates become T/F sensors** emitting a Python `logging` `GZ_<LEVEL>`
  (CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25 / INFO 20 / DEBUG 10 — NOTICE
  the agent-fidelity / V.I.B.E.S. drift band) to the ledger. The level — not a
  hand-set `_FAIL_CLOSED` bool — drives the **disposition**: CRITICAL → **AOG**
  (immediate hangar trip + GHI + insight); below the `>= ERROR` grounding
  threshold → **advisory debt accrued, visibly, on the ledger**.
- **The hangar (MX):** a filesystem **marker** means "in maintenance." While the
  marker is present: **PRIME DIRECTIVE binds the whole session**, most gates drop
  to advisory **except the never-relax floor (§5)**, and a **hard exit re-runs
  every gate at full strength** against the enter-time scope — green-or-grounded,
  **no `--force`**.
- **MX = patch; GHIs are its squawks.** A GHI is the work-order/receipt that
  documents an MX squawk's entry and exit (GHI : MX :: OBPI : Build); repair is
  direct, no ADR ceremony. If MX produces an **altered contract, it is recorded as
  an Airworthiness Directive (AD) and is still a patch** (operator ruling
  2026-06-20) — the AD is the witness that keeps the contract-change honest
  without a minor bump.

## 4. Versioning doctrine (locked 2026-06-20)

| Driver | Bump | Series |
|---|---|---|
| ADR pipeline / feature commit | **minor** | 0.29.0, 0.30.0, … |
| MX-mode + GHI maintenance | **patch** | 0.29.1, 0.29.2, … |
| MX-produced contract change | **patch + AD artifact** | (no minor bump) |

- Last published: **0.28.1**. The next completed feature releases as the next
  minor.
- **Creating MX is a feature** (ADR pipeline) → **MX releases as `0.29.0`** (the
  old `0.29.0` ADR dropped to pool, freeing the number; the counter continues from
  the last *actual* release).
- After MX lands, maintenance drains as **patch** (0.29.1+) until we are "back in
  rhythm" and the forward engine resumes minting minors.
- Every bump is a release (`gz-patch-release` / pipeline ceremony).

## 5. The floor — never relaxes, either engine, in or out of the hangar

**`gate5_invariants` (code constant, not config):** human attestation, ledger
integrity, operator-PII, secrets. No marker, lane, sensitivity, or AOG can
downgrade a member.

**The enforcement-claim rule (new floor — the structural cure for the facade
class):**

> Any place gzkit asserts something is **enforced / validated / fail-closed /
> gated / blocked** — in code, an ADR, a doc, or an agent's claim — there MUST
> exist a paired **live negative-control** test that (a) constructs a known
> violation of that exact claim, (b) runs the real path in its **production**
> configuration, and (c) asserts it **fails** (nonzero / non-empty errors). No
> live negative control ⇒ the claim is facade ⇒ rejected.

- **Forbidden:** forced-mode counterfactuals (the antibody's defeat) and green
  tests that certify enforcement does *nothing* (`TestStagedWarn`).
- **Mechanized structurally:** each enforcement surface declares its live NC
  (`@enforces(claim=…, neg_control=…)`); a meta-validator **runs** every NC
  against a known violation in live config and **fail-closes** if any enforcement
  claim lacks a passing-on-violation live NC; each emits a ledger receipt so
  "this is enforced" is a replayable fact, not a sentence. One primitive, used in
  three places: the floor, the MX exit gate, and the antibody repair.

## 6. Anti-hallucination doctrine (seated — structural, not exhortation)

Agents mischaracterize and fabricate regardless of instruction (proven live this
session). The defense is **structural falsifiability**, mirrored from Anthropic's
production practice:

| Tactic | gzkit form |
|---|---|
| Single source of truth | the pool-reset + state-doctrine (L1 canon / L2 ledger; **L3 never source-of-truth**); release line = "what shipped" |
| Receipts | **footer on every substantive claim: `Source · Confidence · Reviewed · Freshness`** + flag guesses + name one thing to double-check |
| Second opinion | **institutionalized cross-model review** (e.g. Codex) at high stakes — not ad hoc |
| Test on known answers | **the enforcement-claim rule (§5)** — live negative controls are gzkit's "known-answer" evals |

**E.6 — turn-end claim-grounding gate** (was "pending operator design"; shipped
2026-07-01, GHI #620, commit `d83db8a2`): the Stop hook (ADR-0.0.70,
`stop-turn-feedback.py`) now blocks the turn-end when the assistant's last
turn contains a governance state-claim (OBPI/ADR completion, lock state,
"tests pass", "tree is clean") with no citation token — a `gz` command +
observed output, a commit SHA, a ledger reference, or a file:line — within
300 chars. Gates citation FORM (presence), not TRUTH; fail-open on any
internal failure. **Narrower than this row's receipts-footer idea**: covers
4 governance-state-claim patterns, not a universal footer on every
substantive claim. The general receipts-footer + guess-flagging tactic (the
`Source · Confidence · Reviewed · Freshness` row above) remains undelivered
as a broader mechanism — E.6 closes the specific #620 gap, not the full
row.

## 7. The Queue — the daily driver

> Work top-down. Check items off only with **observed command evidence**. Green
> floor inherited: no movement opens while `uv run gz check` is red (the
> enforcement-claim meta-validator joins that floor as it lands).

**Action/structure sidecars (advisory to execution, not new steering surfaces):**
use [`harness-loop-engineering-strategy-note-2026-06-23.md`](harness-loop-engineering-strategy-note-2026-06-23.md)
to shape new harness mechanisms by loop leverage and function×topology
declarations; use
[`okf-cms-knowledge-structure-note-2026-06-23.md`](okf-cms-knowledge-structure-note-2026-06-23.md)
when executing CMS documentation-knowledge orientation work. The Queue still
governs order.

**Movement I — Build the substrate** *(forward engine; releases MX as `0.29.0`)*
- [x] **Mechanism built** — `GZ_<LEVEL>` severity substrate + the **one disposition handler** (the level→AOG/advisory wire; BI#2's *routing* half built for real): OBPI-0.0.74-11 (`levels.py` GZ_<LEVEL> vocabulary) + OBPI-0.0.74-12 (`disposition.py` + `checkpoint.resolve` level→route/AOG/advisory wire), both ATTESTED COMPLETED 2026-06-22.
- [x] **Gates are sensors** — migrate every live guard to emit `GZ_<LEVEL>` through the checkpoint instead of self-deciding, and **retire the hand-set staging flags** (`_FRESHNESS_FAIL_CLOSED`/`_FLOOR_FAIL_CLOSED`) so BI#2's second half holds ("no per-gate hand-set staging flag survives anywhere in the codebase"). **Completed (2026-06-25, GHI #637 + GHI #638):** the `gz validate` scope dispatcher + both rendition gates route through `checkpoint.resolve` (GHI #637), staging flags retired, and the `gz check` step layer (~30 steps) + solo `validate_cmd` paths now resolve through `checkpoint.resolve` (GHI #638, OBPI-0.0.74-20). No hand-set staging flags survive; all live guards emit `GZ_<LEVEL>` through checkpoint.
- [x] **MX lean kernel + hardening** → release `0.29.0`: enter / status / exit, the floor, ledger↔marker binding, **no-force exit**, **TTL / max-open**, **no normal release while MX is open**, **live exit negative-controls**, **ledger debt-aging (louder over time)**, **dangling-state detector** ("ledger open but marker missing"). **CUT** the doc-type taxonomy (OBPI-10 — another classification system smuggled into the repair ADR). **Fix** ADR-0.0.74's placeholder fidelity assertions **and reconcile its drifted Q&A transcript (GHI #640 — asserts cut decisions as live)**. **Completed (2026-06-27):** ADR-0.0.74 closed out (19/19 OBPIs attested; Gate-5 "Completed" by g0), 10 real fidelity-assertion rows green, OBPI-10 cut, GHI #640 closed; **MX released as `0.29.0`** ([v0.29.0](https://github.com/tvproductions/gzkit/releases/tag/v0.29.0) — `gh release list` → Latest). A corrective closeout-proof meta-property-fence deferral fix landed mid-closeout (33 tests; `gz check` exit 0).
- [x] The **enforcement-claim meta-validator** (§5's mechanism) — the floor's teeth. **Implemented and completed (2026-06-25, OBPI-0.0.74-15…20):** re-homed from abandoned ADR-0.0.75 per GHI #639 to ADR-0.0.74, seated as OBPI-0.0.74-15..19 (registry, runner, floor migration, proof upgrade, floor wiring), plus OBPI-0.0.74-20 (step-layer checkpoint seam for "every live guard"). All 6 OBPIs attested_completed. Booked decisions realized: NCs un-forced through the real path; runner-driven `@enforces`; strict no-debt; 37+ production enforcement claims verified, 0 facades.

**Movement II — Drain the facade** *(maintenance engine; patch line 0.29.1+)*
- [x] **#1: repair the hollow antibody + inert rendition gates**, and **delete the tests that certify their inertness** (state-of-gzkit cut #1). **Completed (2026-06-28):** all three parts green. (a) The inert rendition gates were repaired as a side effect of Movement I's checkpoint migration (`rendition-freshness`/`rendition-floor-coherence` now ground at ERROR through `checkpoint.resolve`); **verified** this session via the §5 meta-validator (both PASS in un-forced production config). (b) The inertness-certifying tests (`TestStagedWarn`/`test_warn_stage_missing_invariant`) were already deleted in Movement I; confirmed absent. (c) The **hollow antibody was repaired by building the missing channel-1 static analyzer** (operator-ruled a *correction*, not a retirement — ADR-0.0.73's two-layer design deliberately wanted static signatures "layered on top" of behavioral detection; the inertness was an incomplete implementation, the auto-populating detector deferred to the repudiated OBPI-0.0.73-02). `theater_signature_scan.py` detects 3 structurally-decidable signatures (copy-vs-self, mtime-where-name-says-content, skip-if-PASS); the 4 semantic signatures stay in channel 2 (a static detector for them would be the GHI #624 shape-grading facade). Bound by a §5 live NC (`theater-signature-scan`; meta-validator 42 verified / 0 facades) + a real-tree zero-FP regression. GHI #657, commit `334269b4`; 6603 tests pass, `gz check` exit 0.
- [x] **CMS OKF documentation knowledge structure** — after MX substrate lands,
  make CMS emit/maintain an OKF-conformant semantic map over documentation
  knowledge surfaces (orientation layer only; not authority, not control
  surfaces first). See
  [`okf-cms-knowledge-structure-note-2026-06-23.md`](okf-cms-knowledge-structure-note-2026-06-23.md).
  **Completed (2026-06-29):** ADR-0.30.0-okf-documentation-knowledge-structure
  closed out (6/6 OBPIs attested; Gate-5 "Completed" by g0; 25/25 REQs verified
  by independent spec-review, quality-review COHERENT — four integration seams,
  Boundary Invariant 1 orientation-only fence holds). Delivered: typed
  concept-frontmatter model + JSON-schema mirror, the tracer-slice bundle
  generator, `gz validate --okf-conformance` (generated-bundle-only), the
  `gz knowledge generate`/`refresh` CLI, one wired progressive-disclosure path,
  and the `.gzkit/` vs `docs/` content-boundary doctrine (homed under `.gzkit/`;
  wholesale relocation declared as a phased subsequent decision, not performed).
  **Released as `0.30.0`** ([v0.30.0](https://github.com/tvproductions/gzkit/releases/tag/v0.30.0)).
  Two defects fixed mid-closeout: a malformed insights record (`finding`→`discovery`)
  and the product-proof gate's blindness to bare-directory allowed-paths
  (class-fix at `_expand_allowed_paths`, TDD).
- [x] Re-model the **OBPI lock as a lease** (completion releases; O_EXCL + TTL auto-expire; no handoff-as-evidence tax) — the five confirmed defects. **Completed (2026-06-28) — as a *correction*, not a literal lease re-model.** The operator-ratified reframing (prior session, `358332b0`) ruled this is **not** a lease re-model and **not** a reversal of ADR-0.0.41: the O_EXCL claim path and the fail-closed register-entry precondition are correct by design — the category error lived on the *completion* and *reaping* edges, never the lock primitive. All five §1d defects drained: **(1)** completion never releases → `gz obpi complete` now surrenders the lock mechanically and writes the register entry (GHI #619, `74e428fb`); **(2)** "release fail-closed without a handoff" → resolved *correct-by-design*: completion satisfies the precondition mechanically while the manual fail-closed path stays for mid-traversal surrender (token-block-discipline § Sub-Invariant 6); **(3)** TTL drift 12× → single `DEFAULT_LOCK_TTL_MINUTES = 1440` constant (GHI #604, `6d490278`); **(4)** two divergent reapers → `preflight._apply_cleanup` now routes expired-lock surrender through the canonical `reap_expired_locks` (register entry + `obpi_lock_released` before unlink), no raw `unlink` (`ec83b5e8`); **(5)** SessionStart auto-reap fiction → `session_orientation.collect_obpi_locks` reaps past-TTL locks and surfaces held ones — the real Sub-Invariant 4 cadence (`b7c20dd3`). A pre-existing fail-closed tautological-audit blocker on `tests/test_skills.py` (GHI #453) was cleared in the same sweep (`6ba97c87`). `gz check` exit 0; pushed to `origin/main`.
- [x] **Kind-blind behave gate** (~3 lines: mirror the SUPPORT/STRUCTURAL-FENCE exemption) — **Completed (already landed; checkbox reconciled 2026-06-28).** State-of-gzkit cut #3 named one target: `audit_behave_req_tags` (`briefs.py`) demanded a `@REQ` scenario for *every* REQ; the fix was to mirror the `obpi_complete.py:592` SUPPORT/STRUCTURAL-FENCE exemption. That mirror shipped under **GHI #636** in commit `ba6a1456` (`fix(governance): make behave_req_tags REQ-kind-aware`) on **2026-06-21** — one day after this cut document was written — as part of the #636 effort rather than under this campaign checkbox, leaving the box stale-open. Verified this session: all four behave-gate sites carry the exemption (`audit_behave_req_tags` `briefs.py:592`; `_check_behave_req_coverage_scoped` `obpi_precomplete.py:391`; the completion chokepoint `obpi_complete.py:592`; and `closeout_proof.py`), `tests.md` v0.9.0 documents the kind-aware channel, and `gz check` is exit 0. No code change this session — the work was already done; only the Magna Carta checkbox needed reconciling to reality (Behavior Rule #9: surface, don't silently re-implement).
- [x] Remaining state-of-gzkit cut order, each as a patch with live-NC proof — **Reconciled as drift (2026-06-28), not executed.** This catch-all decomposed into cuts #4/#5/#6 of `state-of-gzkit-2026-06-20.md` § Part 4, and each is already sequenced — by the campaign's own structure — *after* this Movement II window, so none is a "topmost item whose gate is met" here: **(#4)** the `validate()` 162-param / registry collapse (GHI #618, OPEN — census drifted to **81 scopes**; `validate_cmd.py` 1,440 lines) is **Movement IV line 249** (Sanity-Reduction track, parity-proven — not live-NC); **(#5)** reduce the campaign to a spine is a **reductive move**, deferred to the post-1.0 phase per the campaign ruling (`scripts/session_orientation.py:47` — *"reductive moves wait for the post-1.0 phase"*); **(#6)** the census (1,835 unlinked specs, **36 modules >600 lines** as of this session, waiver stack) is **explicitly "not pre-1.0 actions"** in the cut doc and maps to **Movement IV lines 248/250**. Cuts #1/#2/#3 were already drained (facade, lock, behave gate). The catch-all duplicated Movement IV and contradicted the reductive-deferral ruling — exactly the accretion the cut list warns against. Resolved by routing, not by premature reduction work (Behavior Rule #9: surface the inconsistency, reconcile the steering surface; do not unilaterally jump sequence). The live cuts now live solely in Movement IV / post-1.0.

**Movement III — Realize the entry airlock** *(forward engine; the §8 "work-phase theories lawful" 1.0 gate; lands after Movement I, gates Movement IV)*
> **Pivot (2026-06-30, operator-ratified — the campaign is not oracular).** The
> §3a "judgment-grade now, tool-compute later (parked on the graph engine)"
> sequencing is **falsified** by one discovery: **re-sense is the airlock's
> keystone, and real re-sense requires a computed graph.** "I didn't see that /
> failed to look there" is an *observation-completeness* failure no by-hand gate
> can close — you cannot certify you saw every seam by judgment, only against a
> graph that enumerates them. So the graph moves ONTO the critical path:
> AIRLOCK-IN and AIRLOCK-OUT realize **together**, as one constellation built
> keel-up. Heliocentric over geocentric; no clinging.

> **Amendment (2026-07-05, operator-ratified).** One correction to this Movement's
> literal Phase-2 wording, verified before any ADR is authored: **(b)** the
> work-domain edges (`blocks`/`blocked_by`/`discovered_from`/`validates`) are a
> **net-new L2 event schema** — verified: the ledger carries only `parent` edges
> today (the original *"already in the L2 ledger… no new store"* was factually wrong).
>
> **Withdrawn same day — two departures from the GO-attested Phase-0 record, reverted
> to it.** **(a) Substrate:** an earlier 2026-07-05 amendment reversed the HULL floor
> from `tree-sitter + networkx` to stdlib `graphlib`/`ast`; **reverted** — that floor
> is **GO-attested** (Phase-0 airlock-in, 2026-07-02;
> [`airlock-in-constellation-2026-06-30.md`](airlock-in-constellation-2026-06-30.md)),
> STDLIB-FIRST departure rationale already named (*"multi-surface extraction +
> topo/cycle stdlib cannot supply"*); `tree-sitter + networkx` stands, Pydantic the
> object/link layer, `graspologic` stripped (#290). **(c) ADR count:** the same
> session split HULL into a 3-ADR constellation; **reverted** to the GO record's
> **single HULL feature ADR** (operator ruling: *"one unified HULL ADR"*) — corpus ·
> work · source are three typed **domains (subgraphs)** within one ontology,
> OBPI-decomposed, not three ADRs.

The airlock-in/out system is **four feature ADRs** (pool→feature per §3a), built
keel-up. graphify / LightRAG / Plumb are studied **bones, not dependencies** —
the honed runtime floor is **tree-sitter + networkx** (the GO-attested HULL floor,
Phase-0 airlock-in 2026-07-02; a named STDLIB-FIRST departure attested in the HULL
ADR — multi-surface extraction + topo/cycle stdlib cannot supply; Pydantic the
object/link layer; `graspologic` stripped: unused for seam-queries *and* not
installable on Python 3.13+, graphify #290). The graph cache is a **Tier-B derived index** (ADR-0.0.10), rebuildable
from L1/L2, never source-of-truth. **All-tool, no MCP.** The ready/blocked queue
is **BEADS-shaped** — replayed from `blocks`/`blocked_by`/`discovered_from`/
`validates` edges in a **net-new L2 event schema** (2026-07-05 amendment; verified:
the ledger carries only `parent` edges today — gzkit's Yegge heritage supplies the
shape, not an existing store). The single §5 `@enforces` live
NC binds the hatch (un-accounted seam → real entry → assert refuses GO),
registered through Movement I's enforcement-claim surface, not a second framework.

- [x] **Phase 0 — airlock-in the constellation itself** *(judgment-grade, by hand — the airlock does not yet exist; the discipline does)*. Before any ADR is touched: enumerate the seam-map (every surface the promotions/supersessions touch), declare the volume (footprint + reach), pre-register the falsifier, record a go/no-go to the ledger. The first use of the airlock is building the airlock (§5 spirit). See [`airlock-in-constellation-2026-06-30.md`](airlock-in-constellation-2026-06-30.md). **Completed (2026-07-02, GO attested):** the airlock-in record carries all four deliverables — seam-map (footprint), volume declaration, three pre-registered falsifiers (landing/preservation/sequence), and the Go/No-Go — with operator-ratified verdict **GO, keel-up** (verbatim authorization: *"take on Movement III Phase 0"*). Two gates were declared: Phase 0 gates Phase 1 (operator attestation before any ADR is authored — satisfied), and Phase 1's landing falsifier gates Phase 2. That landing falsifier — *"the KEEL monitor refuses silent drift in production"* — was subsequently **discharged live by ADR-0.31.0 OBPI-03** (the `TransitionMonitor` refuses the exact GHI #348 shape at the reconcile chokepoint), so the Phase 0 → Phase 2 gate is now open.
- [x] **Phase 1 — KEEL: OBPI state machine** *(promote `ADR-pool.obpi-state-machine` → feature; heavy)* — locks state doctrine (Arch-Boundary §12 item 3), making re-sense *trustable* (no silent node-drift, the GHI #348 class). Airlock-critical subset: **Pydantic `State`/`Transition` models** (with a thin `StrEnum` for the closed name-set) · withdraw/supersede first-class transitions + CLI verbs (closes GHI #348) · the **runtime invariant monitor** (load-bearing). Deferred-in-keel (the ADR's later OBPIs, non-blocking): full choreography retirement, concurrency caps, failure-class taxonomy, event vocabulary. **Completed (2026-07-04):** promoted `ADR-pool.obpi-state-machine` → `ADR-0.31.0`, closed out and attested by g0 (`closeout_phase: attested`), released as [v0.31.0](https://github.com/tvproductions/gzkit/releases/tag/v0.31.0). The airlock-critical subset landed as 3 attested OBPIs: **01** — closed `OBPIState` StrEnum + frozen Pydantic `State`/`Transition` models + committed JSON schema; **02** — witnessed `gz obpi withdraw`/`supersede` transitions closing the GHI #348 root (withdrawal is now a validated transition, not a silently-demoted hand-edit); **03** — the runtime `TransitionMonitor` at the `gz frontmatter reconcile` write chokepoint, refusing the exact GHI #348 silent-demotion shape (the pre-registered landing falsifier). Independent review: spec-reviewer 18/18 REQs PASS, quality-reviewer COHERENT (one `CANONICAL_TRANSITIONS` consumed by both the verbs and the monitor). All 5 GovZero gates satisfied (Heavy lane) + real fidelity gate 2 pass. Deferred-in-keel items remain non-blocking under the ADR's transition-emitter migration — now also carrying two disclosed carry-forwards from closeout review: model-driven witness enforcement (verbs currently enforce the attestor via a hardcoded check, not by reading `t.witness`) and the `STATUS_VOCAB_MAPPING` 5/8-state gap.
- [x] **Phase 2 — HULL: graph substrate** *(single feature ADR — "the gzkit ontology"; supersedes `artifact-graph-navigation` + `execution-memory-graph` + `covers-source-anchors`, read-folds `ADR-0.0.47`; heavy)* — ONE **networkx multigraph** (Pydantic-typed nodes/edges), three typed domains as subgraphs, queried by `gz` verbs (designed here, no MCP): **corpus** (ADR/OBPI/REQ/GHI/receipt lineage — reads canon, can start parallel-early) · **work** (TASK nodes + ready/blocked queue, replayed from the keel's **net-new L2 edges** — a *derived consumer*, not parallel machinery) · **source** (tree-sitter code-coupling edges + `@covers`/`@surface` anchors). Tier-B derived cache. **Completed (2026-07-07):** `ADR-0.32.0-gzkit-ontology` authored, closed out, and attested by g0 — 7/7 OBPIs `attested_completed`, released as [v0.32.0](https://github.com/tvproductions/gzkit/releases/tag/v0.32.0). Delivered as designed: ONE `networkx.MultiDiGraph` (1171 nodes / 1757 edges live) with corpus/work/source subgraphs + OKF Docs composed in-place, imaged by read-only `gz ontology sense`/`trace`/`resense`/`seams`/`reach` (`--json`/`--dot`); Tier-B derived-never-authority (BI#2); Harness-Purity fence (BI#4); rebuild-fidelity self-report coupled to the **live** `TypedLedgerEvent` discriminator registry (BI#1). **Validated (2026-07-07)** via `/gz-adr-audit`: bound Fidelity Gate 4/4 pass, Layer-2 ledger proof PASS, independent spec-reviewer (no BEHAVIOR REQ escaped coverage; 16 advisories all SUPPORT/STRUCTURAL-FENCE) + quality-reviewer (COHERENT; ONE graph, BI#1 registry-derived confirmed at `corpus.py:118-129`); `validated` receipt emitted (attestor g0, fresh L1 receipts cited: unittest 6804/6804, ruff/ty/mkdocs clean). Two audit findings, **both resolved**: (a) per-OBPI gates did not self-certify ADR-level integration — the domains were islands until corrective composition (GHI #672/#674, closed); (b) source-domain fidelity confessed only directory-presence — **hardened to confess tree-sitter parse failures** (`SourceParser.parse_failures`, GHI #675 → commit `a7e9fc0b`), so BI#1's fence now protects corpus/work/source vocabularies (OKF stays presence-based by design — all-or-raise absorption). Phase 1's landing falsifier (KEEL monitor refuses live drift) gated this phase — discharged. Topmost advances to Phase 3 (HATCH).
- [x] **Phase 3 — HATCH: airlock-in/out membrane** *(new feature ADR; makes `work-phases-and-airlock.md` lawful — the §8 gate; heavy)* — re-sense (query the hull) → declare volume (**footprint** seam-map: push/pull edges · **reach** descent/tracer plan) → name mode · authority · source-ranking · topology-purpose → pre-register **falsifier(s)** (landing + preservation) → record go/no-go to the ledger. AIRLOCK-OUT wires the mature exit surfaces (`gz validate` / reconcile / closeout) as falsifier-check + drift-diff (Plumb-bones for decision-extraction). Invoked judgment-grade at each existing door (MX-enter, `gz obpi pipeline` Stage 1). Bound by the §5 live NC above. **ABSORBS** the former Movement IV "loop/topology declaration discipline" item (the topology-purpose declaration IS this gate's checklist for new harness mechanisms). **Airlock-in GO-attested (2026-07-07)** — record [`airlock-in-hatch-2026-07-07.md`](airlock-in-hatch-2026-07-07.md) (re-sense GREEN, two-layer seam-map [seam = body + boundary], volume footprint+reach, 3 pre-registered falsifiers, GO). **ADR authored & booked (2026-07-08):** `ADR-0.33.0-airlock-membrane` (feature/heavy) with 6 OBPIs 1:1 — **tracer** FC-01 data-model+events · FC-02 airlock-IN + pipeline Stage 1 + the §5 live NC (landing keystone) · FC-03 airlock-OUT + Stage 5 (co-equal, "same shape both ways"); **gated-breadth** FC-04 mx door · FC-05 permitted-entry door (the ad-hoc/spurious entry, closes the silent-bypass hole) · FC-06 doctrine made lawful (§2 seam body+boundary widening; one-way door, sequenced last). Design captured verbatim: model-amnesia intent ("reconstruct… on each sortie"), the door principle (reason selects the door, never *whether* the gate fires), acknowledge-and-decide gate ≠ Gate-5 completion attestation, airlock-never-writes-L1 (proposes attested amendments only), graspologic ruled out (networkx-community if ever, L3-advisory). Green: authored 6/6, `req-kind-discipline`/`cli-alignment`/`documents`, evaluate 3.40/4.0, `mkdocs --strict`. **Progress (2026-07-12): membrane built 6/6** — OBPI-01–05 landed and `ATTESTED COMPLETED` (g0); OBPI-06 (doctrine-lawful — one-way §2 seam-widening, sequenced last) lands this promotion, registering NO runtime code. **Doctrine made lawful via OBPI-0.33.0-06** — `work-phases-and-airlock.md` + `four-phases-of-work.md` promoted Draft→binding with the §2 seam BODY-and-BOUNDARY widening, gated behind the §5 live NC (`airlock-in-unaccounted-seam`, un-accounted seam → GO unreachable, un-forced) biting in production. **§8 gate discharged. Closed out and released ([v0.33.0](https://github.com/tvproductions/gzkit/releases/tag/v0.33.0), Gate-5 "Completed" by g0, 2026-07-12), then Validated (2026-07-12)** via `/gz-adr-audit`: bound fidelity gate 4/4 pass (fresh post-#679), spec-reviewer PASS (25/25 BEHAVIOR REQs semantically covered; the 8 raw-uncovered all SUPPORT/STRUCTURAL-FENCE by kind) + quality-reviewer COHERENT (one primitive, three doors, BI #1/#2/#3 hold in code), `validated` receipt emitted (attestor g0; receipts arb-ruff/typecheck/unittest cited, 7014 tests exit 0). One in-flight corrective follow-up resolved: **GHI #679** (exit-side L2 booking not failure-atomic) fixed as direct repair (commit `89c5ee9a`, `Verdict.ABORTED` + failure-atomic pairing), closed — the airlock now accounts for every transit on both edges even under exit failure.
- [ ] **[deferred] Phase 4 — RECALL: governance retrieval** *(promote `ADR-pool.rag-anything-governance-retrieval` → feature; heavy; severable, post-first-airlock)* — LightRAG-bones (dual-level retrieval + incremental + citation; local model; file-store; `gz` verb), strictly **L3-advisory** (never gates, state-doctrine Rule 5), adding semantic-seam *recall* the deterministic floor can't express. The airlock ships and gates on the floor (Phases 1–3) alone; this is enrichment.

**Movement IV — Reduce the accretion** *(parity-proven; Sanity-Reduction track)*
- [ ] **Taxonomy migration (pre-1.0; refined 2026-07-05 — partition, not flatten):** completed/Validated foundations **stay** as a **frozen-historic** `kind: foundation` set; **unstarted/pending** foundations **drop to pool**; `foundation` becomes a **closed kind**. Mechanize: schema enum keeps `foundation` (closed), `gz validate --taxonomy` **grandfathers** the existing set and **rejects new `foundation`**, retire ADR-0.0.18's choose-foundation guidance — parity-proven, behavior-preserving. **Realized (2026-07-12, operator-ratified) as the Foundation Sunset movement, capstoned by [`ADR-0.34.0-foundation-sunset`](../../design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md)** (authored + 5 OBPIs; three-class partition from Layer-2 ledger truth; committed grandfather manifest; `foundation_grandfathered` backfill; ontology re-sense). Box stays open until the capstone's implementation lands (sequences last, after the Class-2 closeouts make the tree terminal). See § Amendments 2026-07-12
- [ ] Collapse the 70-scope / 162-param `validate()` surface to the registry (#618 residual)
- [ ] Oversized modules (33 > 600 lines) — census-driven, with working proof

## 8. The 1.0 definition (slim)

gzkit is 1.0 when ALL hold:
- **The floor holds** — `gate5_invariants` intact **and the enforcement-claim
  rule is green** (every enforcement claim has a passing live negative control).
- **Both engines operate** — a feature can be committed pool→release through the
  airlock; the MX hangar can drain debt and re-certify at a hard exit.
- **The facade is drained** — no gate that returns `[]` on its own violation; no
  test that certifies inertness; the antibody catches its target.
- **Release line healthy** from 0.28.1; GHI backlog at steady-state triage scale.
- **Work-phase theories lawful** — the airlock (entry membrane realized) and the
  four-phase model are built, apparatus-proven, and bound by a fail-close
  mechanism (operator ruling 2026-06-17: Magna Carta is not complete until these
  are law).
- **v1.0.0 released** through the ceremony.

## 9. Status — the 2026-06-20 design session is fully seated

All decisions are now doctrine: four airlocks + MX granularity + intent hierarchy
→ §3; versioning → §4; never-relax floor + enforcement-claim rule → §5;
anti-hallucination → §6; superpowers lightness-lesson → §2a. No items pending
operator confirmation. Next session works the Queue (§7) top-down.

## Authority & amendment

Living: items check off with command evidence. Amendments are operator-ratified,
recorded with the operator's verbatim words, and **appended to § Archive** — never
interleaved into the body. The campaign rules sequencing; handoffs and triage
**advise**. No work stream runs outside it except `emergency`-labeled interrupts.

## Archive

- [`build-to-1.0-campaign-2026-06-10.md`](build-to-1.0-campaign-2026-06-10.md) —
  the predecessor (1,589 lines, 77 amendment blocks). Superseded in place
  2026-06-20; retained for audit. Its live threads (the green floor invariant, the
  work-phase theories as a 1.0 gate, the GHI backlog cadence) are carried forward
  above; its accreted resequencing history is **history**, not steering.

### Amendments

- **2026-06-21 (operator-ratified) — §3b severity ladder: kernel/syslog 0–7 →
  Python `logging` + NOTICE.** §3b originally specified a kernel-style
  `GZ_<LEVEL>` (0 `EMERG` → 7 `DEBUG`). ADR-0.0.74 D1 supersedes it with the
  Python `logging` ladder (CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25 /
  INFO 20 / DEBUG 10), NOTICE=25 the V.I.B.E.S. drift band, grounding threshold
  effective `>= ERROR`, on **STDLIB-FIRST** grounds — the stdlib constants are
  reused rather than re-inventing a 0–7 convention whose top rungs (EMERG/ALERT)
  no governance gate uses (ADR-0.0.74 § Alternatives, rejection (f)). §3b is
  amended in place to match. Ratified: "ratified" — g0, 2026-06-21.
- **2026-06-23 (operator-ratified) — CMS adopts OKF for documentation
  knowledge orientation after MX substrate.** The operator approved capturing the
  OKF/CMS decision as a separate note plus a campaign pointer: "yes, let's do
  that please". The campaign adds a Movement II item for an OKF-conformant CMS
  semantic map over documentation knowledge surfaces, explicitly as orientation
  only: not an authority layer, not control surfaces first, and not a revival of
  the cut doc-type taxonomy. Design note:
  [`okf-cms-knowledge-structure-note-2026-06-23.md`](okf-cms-knowledge-structure-note-2026-06-23.md).
- **2026-06-23 (operator-ratified) — harness loop-engineering note made
  campaign-aware.** The operator ruled that both notes "have insights for
  action/structure." The Queue now names the OKF/CMS note and the harness
  loop-engineering note as action/structure sidecars, without making either a new
  steering surface. Movement III carries the resulting structural action:
  function×topology declaration discipline for new harness mechanisms and
  accretion-reduction work. Design note:
  [`harness-loop-engineering-strategy-note-2026-06-23.md`](harness-loop-engineering-strategy-note-2026-06-23.md).
- **2026-06-23 (operator-ratified) — the entry airlock is seated as a distinct
  Movement (III), after the facade-drain.** AIRLOCK-IN was a §8 1.0 gate
  ("work-phase theories lawful — the airlock entry membrane realized") with no §7
  builder — a gate with no puller. The operator ruled it *"a distinct movement"*
  and placed it *"Movement III, after the facade-drain,"* so it lands after
  Movement I (binding to the §5 enforcement-claim primitive) and gates the
  now-Movement-IV reduction (the highest-blast-radius refactor on the board —
  work-phases §4). Scope ruled *option (i)*: build the judgment-grade airlock as a
  discipline invoked at each mode's existing door, doors in place; tool-computed
  (graph-backed) AIRLOCK-IN and true door-unification stay deferred on
  Architecture Boundary §12.3. Terminology ruled *"keep entry airlock /
  AIRLOCK-IN"* — the less-cryptic rename defers to Phase I per work-phases §7. The
  former Movement III "loop/topology declaration discipline" item folds into the
  airlock Movement (superseding its placement in the harness-loop archive entry
  above). Design source:
  [`work-phases-and-airlock.md`](work-phases-and-airlock.md),
  [`four-phases-of-work.md`](four-phases-of-work.md),
  [`harness-loop-engineering-strategy-note-2026-06-23.md`](harness-loop-engineering-strategy-note-2026-06-23.md).
- **2026-07-05 (operator-ratified) — taxonomy migration refined from *flatten* to
  *partition*; `foundation` becomes a frozen-historic kind; the migration is
  pre-1.0.** The 2026-06-20 "move everything to pool" ruling (§3a, Movement IV)
  over-reached: it abolished `foundation` and dropped *all* ADRs to pool. The
  operator refined it (verbatim): *"1) completed foundations remain for historic
  purposes. 2) unstarted foundations are moved to pool. 3) only pool and feature
  remain. this is all pre-release (1.0), so the campaign needs to accommodate
  this."* Reconciled to a **frozen-historic** treatment (operator-selected over
  relabel-to-feature): `foundation` survives as a **closed kind** — every
  completed/Validated `0.0.x` foundation **remains in place** with
  `kind: foundation` as the historic, invariant-shaping record; **no new
  foundation may be minted**; only **unstarted/pending** foundations **drop to
  pool**. `pool` + `feature` are the two **live/forward** kinds. Mechanically:
  `gz validate --taxonomy` **grandfathers** the existing foundation set and
  **rejects new `foundation`** (not a blanket abolition); ADR-0.0.18's
  choose-foundation-for-new-work guidance is retired while the historic set
  stands. The migration is **pre-1.0** — exempt from the "reductive moves wait for
  post-1.0" deferral (`scripts/session_orientation.py`); the Movement IV taxonomy
  item is thereby a pre-1.0 requirement. §3a and Movement IV are amended in place
  to match. Ratified: g0, 2026-07-05.
- **2026-07-06 (operator-ratified) — Hexagonal (Ports & Adapters) is gzkit's
  primary code-architecture directive; the parameter-injection seam is blessed as
  the canonical hexagon and the dormant ports/adapters facade is retired.** This
  amendment records operator-ratified code-architecture doctrine that landed as a
  binding per-turn rule (`.gzkit/rules/hexagonal-architecture.md`) plus a
  direct-fix correction under ADR-0.0.3 (commit `ba01f1e9`) — **not** a Queue
  item, so no §7 Movement checkbox moved. Two rulings: **(1)** Hexagonal is the
  primary code-architecture directive (deps behind adapters, stdlib+Pydantic core,
  parameterize-everything, Protocol>ABC, encapsulate-first). **(2)** The
  two-hexagons conformance gap (the declared `src/gzkit/ports/` +
  `src/gzkit/adapters/` + `tests/fakes/` layer was wired into zero production code
  and injected into zero domain tests) is resolved by decision **(b)**: bless
  gzkit's **parameter-injection seam** (`project_root: Path` at 738 sites,
  `Ledger(path)`, `load_config(path=)`, wired by the command-layer configurator,
  Cockburn Fig 2.1) as the canonical hexagon and **retire the dormant facade**
  (~1,064 lines deleted; supersession callouts on OBPI-0.0.3-01/-04/-05/-09). The
  wire-the-ports alternative (a) was rejected as the speculative generality the
  new rule forbids. The Cockburn "adapters live outside the core" folder-structure
  realization is the intended direction but **deferred to a new pool ADR**
  (`ADR-pool.hexagonal-folder-structure-realization`) — operator: *"too big to
  rewire in a correction; gzkit + adopters not yet ready."* This changes no §8
  1.0 gate and no sequencing: the topmost item remains Movement III Phase 2 (HULL),
  now inheriting a clean single-seam code-architecture floor. Campaign-edit scope
  operator-selected this session: *"Append § Amendments entry"* (no checkbox, no
  Topmost-note change). Ratified: g0, 2026-07-06.
- **2026-07-06 (operator-ratified) — Hexagonal seated inside the DDD → HA → BDD →
  TDD spine; the domain is modeled as the ontology (ADR-0.32.0), not a folder
  tree.** A follow-on to the same-day hexagonal-primary-directive amendment above,
  prompted by an independent cross-vendor (ChatGPT) cold read of the repo toward
  the operator's goal of *"a strong ddd → ha → bdd → tdd foundation for gzkit (and
  adherents)"* and the operator's acknowledgement that gzkit *"grew ad hoc"* over
  time. Operator directive this session, verbatim: *"strengthen guidance
  anywhere/everywhere this applies."* Landed as doctrine strengthening — **not** a
  §7 Queue item, so no Movement checkbox moved:
  - **`.gzkit/rules/hexagonal-architecture.md` `0.1.0 → 0.2.0`** + canon
    `docs/governance/hexagonal-architecture.md`: seat HA as the **second stage** of
    the four-stage architectural spine and add the binding cohesion doctrine —
    **`core/` stays; no `domain/`/`application/`/`adapters/`/`contexts/` folder
    cosplay** (Cockburn §2.4: internal layout is not part of the pattern); **domain
    cohesion lives in the type system, not the folder tree**; **subsumption over
    parallel models**; **"why is this here?" is a required answer** (ADR-0.32.0
    persona). The cross-vendor read converged on gzkit's existing doctrine
    (injection-first, stdlib/no-ORM, Pydantic-as-named-departure,
    unittest-not-pytest) — recorded as confirmation the spine is legible to an
    outsider (an adopter property, §1). Commit `f6094725`.
  - **Sequencing insight (no sequencing change):** ADR-0.32.0 (Phase 2 HULL, the
    ontology) **is gzkit's DDD move** done as a typed graph, not a folder
    restructure — the bounded contexts are subgraphs (corpus / work / source),
    which is exactly why `core/` stays. Phase 2 inherits this cohesion floor; §8
    gates and the Topmost note are unchanged.
  - **Two coupled fixes drained (patch-line MX, GHIs as their own receipts):**
    **GHI #671** — `validate_referenced_files` hardened to resolve handoff Evidence
    paths against **committed/tracked** state, not local disk (inverse sibling of
    #633; the disk-vs-clone drift class that surfaced twice this session); commit
    `0747f6a5`, RED→GREEN TDD, full unittest 6748 OK. **`tests/fakes/`
    retirement-shell swept** (commit `cb7e8429`) — the third and last leftover of
    the `ba01f1e9` facade retirement, completing it; the two-hexagons handoff
    Evidence reference reconciled in the same thread (invariant 1a).
  - Campaign-edit scope this session: **Append § Amendments entry** (no checkbox,
    no Topmost-note change, no §8 gate change) — matching the prior hexagonal
    amendment's scope. Ratified: g0, 2026-07-06.
- **2026-07-12 (operator-ratified) — the Movement IV taxonomy migration is realized
  as the Foundation Sunset movement, capstoned by `ADR-0.34.0-foundation-sunset`.**
  The 2026-07-05 partition amendment (above) is now realized in a governed ADR after
  a design dialogue + mandatory forcing-function review. Refinements the review
  surfaced: **(1)** the partition is computed from **Layer-2 ledger truth, not
  frontmatter** (the ADR-0.0.37 investigation proved frontmatter lies about repudiated
  OBPIs), and it resolves to **three** classes, not two: ~46 already-Validated/Completed
  foundations **stay** frozen-historic; **5 Class-2** foundations holding attested-but-
  unclosed work (`0.0.37` 15/19, `0.0.54` 4/4, `0.0.64` 5/5, `0.0.65` 1/5, `0.0.72` 1/4)
  are **finished-then-frozen** rather than pooled (pooling would discard attested work);
  **23 genuinely-unstarted** (0/N OBPIs, incl. storybook `0.0.42` and `0.0.1`) **drop to
  pool**, re-promotable later as features. **(2)** The capstone is a **`feature`** ADR
  (`0.34.0`) — by its own rule it cannot be `foundation`; closing the kind must reach
  through the feature track. **(3)** A committed **grandfather manifest**
  (`data/foundation_grandfather.json`, identity-only, golden-file-guarded) is the
  closed-set enforcement; `gz validate --taxonomy` gains **closed-kind** and
  **terminal-partition** assertions, the latter reading a **backfilled
  `foundation_grandfathered` ledger event** (ledger made complete-by-construction; old
  pre-ledger foundations witnessed by the migration's Gate-5 attestation), never
  frontmatter. **(4)** An **ontology re-sense** (`gz ontology resense` + diff) is a
  Sunset step guarding the 23-node `ADR-0.0.X`→`ADR-pool.slug` rename. **Sunset
  sequence:** finish `0.0.65`/`0.0.72` → closeout `0.0.54`/`0.0.64` → closeout `0.0.37`
  (withdraw the 4 fabricated composition OBPIs → 15/15; re-home the real registry→
  AGENTS.md composition as a **feature**, closing GHI #623) → `ADR-0.34.0` capstone
  (demote 23 · populate · backfill · resense; then reconcile + wire the **permanent**
  `--taxonomy` gate into `gz check`). The Movement IV taxonomy item (§7) is realized by
  this movement; the checkbox stays open until the capstone's implementation lands
  (it sequences last, after the closeouts make the tree terminal). Campaign-edit scope:
  **Append § Amendments entry + annotate the Movement IV taxonomy checkbox** with the
  realizing ADR. Ratified: g0, 2026-07-12.
