<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Build-to-1.0 Campaign — 2026-07-18 (Magna Carta)

Status: **ACTIVE — the one canonical plan** (operator-ratified 2026-07-18).
Supersedes [`build-to-1.0-campaign-2026-06-30.md`](build-to-1.0-campaign-2026-06-30.md);
priors are retained for audit and no longer steer.

> **Topmost (sequenced):** **Movement A — close the Foundation Sunset.** ~~`ADR-0.0.37` audit~~ **done 2026-07-18 (`b40a8026`)** → **NEXT: re-home the composition engine as a feature (GHI #623)** → `ADR-0.34.0` capstone. Then Movement B (airlock on the real doors), C (reduce), D (rulings). Pool backlog is post-1.0 (§7).

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
- [ ] Re-home the registry→AGENTS.md composition engine as a **feature** ADR. **DONE as authoring: the successor is `ADR-0.35.0-canon-entry-corpus-landing` (authored 2026-07-21, `Draft`, 9 OBPIs, 0/9 landed) — this item is started-not-done, and the tracker is the ADR, not a GHI.** GHI #623 closed 2026-07-19 and **GHI #654 closed 2026-07-22 `superseded` into `ADR-0.35.0`**, whose § Intent names it: *"Discharges GHI #654 (orchestration gap) and GHI #635 (duplicate invariant entries) -- the same wound."* Do not reopen #623 **or #654** to find this scope; read the ADR. Its OBPI-05 carries the corpus→candidate generator and OBPI-07 the `gz content land` orchestrator. GHI #654's capture-silence gap was direct-fixed ahead of the chain (`48a5f799`, `dcf29b95`) because it was a live footgun; see the pre-landed note in `OBPI-0.35.0-08`. The absorption direction `ADR-0.0.37` § Terminal Disposition recorded (*"tracked at GHI #623 (absorbing GHI #654)"*) is backwards relative to what survived: #623 was an audit finding and its findings are discharged, while #654 states the same unbuilt capability as operator pain with a reproduction — *"there is no generator that renders the corpus delta into a candidate."* Closed after a full re-verification: claims (3)/(4) had been fixed by later work and never credited back, corrective scope (A) had landed as `--rendition-floor-coherence`, the discarded registry parameters were removed (`4f9c7d2b`), and a standing witness-resolution gate was added (`e409bb08`). **Residual scope, unbuilt and feature-shaped:** the attributable corpus→candidate generator and the `rendition ⊆ corpus` lineage gate — today `compose()` *validates* an agent-supplied candidate rather than *materializing* one from the corpus, so prose absent from canon can still pass. The registry spine is NOT the successor: `ADR-0.0.37` § Terminal Disposition permanently withdrew OBPI-02/03 as *"obsoleted by the 2026-06-03 corpus Re-Alignment."* The successor is corpus-shaped.
- [ ] **Disposition `foundation-adr-registers-invariant`** *(one-line operator canon call, fenced not blocking)*. It declares structural witness `gz validate --foundation-registers-invariant`, which has never existed; the claim is also unenforceable as written — `constitutional_invariant.json` carries no field naming which ADR registered an entry, and the ratio is 4 invariants to 74 foundation ADRs. It was NOT retired: `REQ-0.0.37-01-03` (attested, OBPI-0.0.37-01) asserts three seed invariants, so deleting the entry would falsify attested canon. Fenced shrink-only by `tests/governance/test_invariant_witness.py`; `--invariant-witness` stays out of `gz check` until this is ruled, since holding a gate green over a known-red tree is the staging-flag anti-pattern.
- [ ] `ADR-0.34.0-foundation-sunset` capstone — 5 authored OBPIs, currently `Draft` **1/5** (OBPI-01 `attested_completed` 2026-07-19: grandfather manifest + closed-kind assertion): demote the ~23 unstarted foundations to pool · ~~populate the grandfather manifest~~ · backfill `foundation_grandfathered` · `gz ontology resense` · wire the permanent `--taxonomy` gate into `gz check`.

**Movement B — Put the membrane on the real doors** *(new feature ADR extending `ADR-0.33.0`; heavy)*

> **The doors mostly exist. They do not fire.** `gz permitted-entry` shipped with
> `ADR-0.33.0` (OBPI-05) and has **2** recorded transits. `gz airlock in` is wired into
> `gz obpi pipeline` Stage 1 and fires reliably there — because the pipeline *triggers*
> it. Everywhere else the airlock is **invocable but opt-in**, and an opt-in gate is not a
> gate. This is the §4 failure class one level up: a mechanism that exists, is documented
> as governing entry, and does not bite. **Operator ruling 2026-07-18: GHI and ad-hoc
> (permitted) entry MUST trigger the airlock mechanism.**

- [ ] **GHI direct-fix triggers the airlock.** `GHI : MX :: OBPI : Build` — the MX door must carry the same membrane the Build door does. A `fix(...)` landing without a transit is an unaccounted entry. This is the single highest-volume ungoverned door: **470 `fix` commits in 90 days, zero transits.**
- [ ] **Ad-hoc / permitted entry triggers the airlock.** Make `permitted-entry` fire on ad-hoc reconnaissance and light repair rather than waiting to be invoked — the reason selects the door, never *whether* the gate fires (`ADR-0.33.0` door principle).
- [ ] **Session entry triggers the airlock.** A model entering the project is a transit. The SessionStart hook already runs orientation; it should seat a seam-map and a go/no-go. Evidence this is the live hole: the 2026-07-18 session ran a full corpus survey, filed 2 GHIs, changed 3 source files, and rewrote Magna Carta across **zero** transits.
- [ ] Close the transit-accounting gap: **23 `airlock_in` vs 10 `airlock_out`** — 13 transits never accounted for on exit. Failure-atomic pairing precedent: GHI #679 / `89c5ee9a`.
- [ ] Bind with a §4 live NC on each widened door: **un-triggered entry → the claim fails**. Not "un-accounted seam → GO unreachable" (that is `ADR-0.33.0`'s existing NC, and it only fires once you are already inside the airlock). The new NC must catch *never entering at all* — the failure mode that let ~97% of commits through.

**Movement C — Reduce the accretion** *(deferral LIFTED 2026-07-18 — this is pre-1.0)*
- [ ] **Surface mirroring** — 703 of 810 chore commits (47% of all commits) are `gz git-sync` regenerating five copies of every skill/rule across `.gzkit/`, `src/gzkit/`, `.claude/`, `.agents/`, `.github/`. One canonical location; generate at install, not at commit. Largest single line item on the board.
- [ ] Collapse the `validate()` surface to the registry — **92 flags** today (GHI #618).
- [ ] Oversized modules (33 > 600 lines) — census-driven, with working proof.
- [ ] **The Firewall** *(recovered orphan, § 9a)* — classify every delivered surface by destiny: **wheel-borne / authored-into-battlefield / lab-only-jig**, enforced at scaffold-time and validate-time. Operator, 2026-06-14: *"the rigging and jigs do not remain attached to the fuselage once we open the factory hangar doors for final delivery — we haven't been careful about this."* Booked 06-14, never built. Load-bearing for §1's public-product trajectory: today an adopter inherits gzkit's lab jigs. Genuinely reductive — it defines what does **not** ship.
- [ ] **Render the stability-gradient spine** *(recovered orphan, § 9a)* — the 06-14 ruling ordered the tree `Constitution → PRD → ADR → OBPI` by rate of change and declared the legacy `PRD → Constitution` spine backwards. AGENTS.md § Workflow still carries the old order across ~12 surfaces. Booked and never rendered.

**Movement D — Stop the re-adjudication** *(ruling lifecycle)*
- [x] **Handoff-local repair** — every authored next step now survives the resume (`ResumeResult.next_steps`); the `continues_from` chain link is correct-by-construction. GHI #696, commit `5ec44ad1`, receipt `arb-step-unittest-430503d2`.
- [x] **Recover the orphaned 06-10 rulings.** Done 2026-07-18, in-session. Counted **17** amendments + 4 scope decisions + a goal-state — not the "77" the 06-30 edition asserted. All dispositioned in § 9a. Highest-value catch: **Scope decision #1 ("Full pool build-out … no item left undecided at 1.0") was live and unwithdrawn**, in direct contradiction to today's post-1.0 pool ruling — the precise orphan that resurfaces months later as *"but we booked that for 1.0."*
- [ ] **Rulings become first-class** — `ruling_issued` / `ruling_superseded` typed ledger events; a `gz ruling` verb; the handoff *Settled* section and per-decision operator-ruled/agent-chose attribution as **rendered projections**; the campaign body as a rendered Layer-3 view; supersession **fail-closed on orphaned rulings**. Sibling: GHI #611. Diagnosis: **nothing in gzkit represents the state "settled"** — 60+ typed ledger event kinds, no ruling event — so settled decisions are re-derived, and re-deriving is re-adjudicating. § Rulings Register is the manual stand-in until this lands.

**Housekeeping (not a Movement, but tracked so it stops being invisible)**
- [ ] `ADR-0.44.0-vendor-alignment` is `IN_PROGRESS` at **1/6** and was tracked by no campaign edition. Finish it or formally park it to pool.

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
