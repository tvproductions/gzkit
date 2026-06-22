<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Build-to-1.0 Campaign — 2026-06-20 (Magna Carta)

Status: **ACTIVE — the one canonical plan** (operator-ratified 2026-06-20).
Supersedes [`build-to-1.0-campaign-2026-06-10.md`](build-to-1.0-campaign-2026-06-10.md)
in place; the predecessor's 1,589 lines and 77 amendment blocks are retained for
audit under § Archive and no longer steer.

> **This file is slim by design — the steering surface fits in a session. The
> Queue (§7) is the daily driver.**
>
> **It steers; the spine propels.** The engines (§3) and the floor (§5) do the
> work; this plan only sequences them. Amendments are operator-ratified and
> **append to the dated archive, never inline** — inline accretion is the disease
> that killed the predecessor. It dies only by a ratified successor.

> **Topmost (sequenced):** Movement I — build the substrate (levels + gates-as-sensors + the enforcement-claim meta-validator), then land MX as the first feature, release `0.29.0` (lean kernel + hardening).
>
> Everything else waits behind a working substrate. See §7.

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

- **Taxonomy reset (operator ruling 2026-06-20, "move everything to pool"):** the
  `foundation` kind is **abolished**. **Everything drops to pool** (inert
  inventory). Two kinds remain: **pool** = universal backlog/origin; **feature** =
  committed, release-carrying. The **release line is the source of truth for what
  is shipped** — not 269 ADR `status:` frontmatters (the frontmatter we proved
  unreliable). Built code stays live; only the ADR *classification* resets.
  Features earn back to release **one at a time**, with executable proof.
- **The airlock is the work discipline:** *way-in* (compute/enumerate the
  seam-map → **go/no-go before work**), *vertical* (ADR → OBPI → REQ → TASK),
  *way-out* (drift-diff / reconcile → block · surface · resolve). AIRLOCK-OUT is
  already mature (reconcile/validate/attest); **AIRLOCK-IN is the unbuilt cure** —
  run it judgment-grade now (agent enumerates seams under discipline), tool-compute
  it later (gated on the graph engine / state doctrine).
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

**E.6 — turn-end claim-grounding gate** (was "pending operator design"): its shape
is now the receipts-footer + guess-flagging above, emitted at turn end.

## 7. The Queue — the daily driver

> Work top-down. Check items off only with **observed command evidence**. Green
> floor inherited: no movement opens while `uv run gz check` is red (the
> enforcement-claim meta-validator joins that floor as it lands).

**Movement I — Build the substrate** *(forward engine; releases MX as `0.29.0`)*
- [x] **Mechanism built** — `GZ_<LEVEL>` severity substrate + the **one disposition handler** (the level→AOG/advisory wire; BI#2's *routing* half built for real): OBPI-0.0.74-11 (`levels.py` GZ_<LEVEL> vocabulary) + OBPI-0.0.74-12 (`disposition.py` + `checkpoint.resolve` level→route/AOG/advisory wire), both ATTESTED COMPLETED 2026-06-22.
- [ ] **Gates are sensors** — migrate every live guard to emit `GZ_<LEVEL>` through the checkpoint instead of self-deciding, and **retire the hand-set staging flags** (`_FRESHNESS_FAIL_CLOSED`/`_FLOOR_FAIL_CLOSED`) so BI#2's second half holds ("no per-gate hand-set staging flag survives anywhere in the codebase"). Today `checkpoint.resolve` has zero production callers and two flags survive — OBPI-0.0.74-09. *Until this lands, the substrate is built but adopted by nothing; do not read the mechanism check as "gates-as-sensors is done."*
- [ ] **MX lean kernel + hardening** → release `0.29.0`: enter / status / exit, the floor, ledger↔marker binding, **no-force exit**, **TTL / max-open**, **no normal release while MX is open**, **live exit negative-controls**, **ledger debt-aging (louder over time)**, **dangling-state detector** ("ledger open but marker missing"). **CUT** the doc-type taxonomy (OBPI-10 — another classification system smuggled into the repair ADR). **Fix** ADR-0.0.74's placeholder fidelity assertions.
- [ ] The **enforcement-claim meta-validator** (§5's mechanism) — the floor's teeth

**Movement II — Drain the facade** *(maintenance engine; patch line 0.29.1+)*
- [ ] **#1: repair the hollow antibody + inert rendition gates**, and **delete the tests that certify their inertness** (state-of-gzkit cut #1)
- [ ] Re-model the **OBPI lock as a lease** (completion releases; O_EXCL + TTL auto-expire; no handoff-as-evidence tax) — the five confirmed defects
- [ ] **Kind-blind behave gate** (~3 lines: mirror the SUPPORT/STRUCTURAL-FENCE exemption)
- [ ] Remaining state-of-gzkit cut order, each as a patch with live-NC proof

**Movement III — Reduce the accretion** *(parity-proven; Sanity-Reduction track)*
- [ ] **Taxonomy migration:** drop all ADRs to pool; abolish `foundation` (schema enum, `gz validate --taxonomy`, supersede ADR-0.0.18) — parity-proven, behavior-preserving
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
