# GHI Triage — 2026-07-21

**Scope:** 44 open GHIs, all ranked. `fix()` precedent (60d): 262 commits — every
issue below routes **direct-fix** per `AGENTS.md` § Defect-fix routing.

**Method:** `/ghi-triage` Step 1 fetched structured records; four readers read all
44 bodies and ran the named validators where the issue claimed a failure; severity
and ordering are the agent's judgment, rendered deterministically by
`.claude/skills/ghi-triage/scripts/triage.py --format rank`.

**Status:** diagnosis only. Nothing was modified. No GHI was closed, relabelled, or
commented on.

---

## Severity definitions

| Severity | Meaning |
|----------|---------|
| `blocking` | Current work fails, a gate is green over a known-red tree, or an enforcement surface is bypassable |
| `degrading` | Work succeeds but produces drift, wrong counts, stale artifacts, or silent incorrectness |
| `latent` | Deferrable — cosmetic, speculative, or awaiting an unlanded prerequisite |

---

## Blocking (8)

| # | GHI | Finding |
|---|-----|---------|
| 1 | #654 | Every `gz content remember` leaves the tree `gz check`-red with no warning; only a hand-authored multi-step recovery exists. |
| 2 | #635 | `gz content compose AGENTS.md` exits 1 on an unsatisfiable invariant floor — the canon-to-rendition spine cannot run. |
| 3 | #698 | Negative control passes on a narrower violation, so the enforcement floor counts the populated-sections claim verified while deleting the check breaks nothing. |
| 4 | #606 | Pipeline gate arms only on a plan-audit receipt; an agent skipping plan mode implements locked OBPIs freeform with no block. |
| 5 | #578 | `preflight --apply` unlinks expired locks with a bare unlink, bypassing the mandatory reaping register entry. |
| 6 | #607 | Any mention of Pydantic in `models.md` makes every adopter `@dataclass` a fail-closed `gz validate` error — the dogfooding stricture leaks across the adopter boundary. |
| 7 | #664 | Two regex gaps report false `req_count` drift on 38% of briefs and every completed brief, blocking pipeline Stage 1→2. |
| 8 | #615 | 597/600 briefs bypass the Pydantic schema into regex scraping; phantom drift has already blocked legitimate reconcile work. |

**Sequencing note:** #664 is a ~10-line fix and should land *before* the broader
#615 parser flip. #654 and #635 are the same wound — both sit on the corpus→rendition
spine that the campaign's Movement A residual scope depends on; fixing one without
the other likely leaves the path still unrunnable.

## Degrading (14)

| # | GHI | Finding |
|---|-----|---------|
| 9 | #584 | 230 orphaned `obpi_created` events verified still present; Layer-2 asserts briefs that do not exist, corrupting roll-up counts. |
| 10 | #532 | Worse than filed — no `gz-*.md` manpage exists; ~130 refs across 28 files, including 5 literal `test -f` brief verification steps. |
| 11 | #701 | Advisory reports 57 proof-channel-exempt SUPPORT/fence REQs as owing `@covers`, steering agents into authoring tests that cannot fail. |
| 12 | #703 | Four SUPPORT REQs carry `@covers`, inflating the coverage census with structural assertions. |
| 13 | #665 | Raw `gz specify` scaffolds and fully-authored briefs render identically as `draft`, so unauthored briefs enter pipelines undetected. |
| 14 | #641 | Mis-picking `gz brief reconcile` vs `gz obpi reconcile` exits clean on the wrong axis — silent false assurance, no error signal. |
| 15 | #650 | Rules and skill tell agents to check `.gzkit/mx-active`; code writes `.gzkit/mx.json`, so manual MX checks always read absent. |
| 16 | #577 | `gz context` and `gz status` project different current gates for lite-lane ADRs carrying gate-3/4 pass events — operator reads two answers. |
| 17 | #573 | Attestation-verdict classifier is duplicated across closeout and `ceremony_state`; a one-sided edit silently diverges ledger status from lifecycle state. |
| 18 | #702 | Verified live — 103 of 262 fidelity rows across 110 ADRs are self-referential; counts inflate but no ADR is wholly tautological, so gates stay honest. |
| 19 | #696 | Mechanisms 1 and 5 landed; settled-decision channel, operator-vs-agent attribution, and unverified next-step advisories remain, so rulings still decay into re-adjudication. |
| 20 | #551 | REQ-coverage gate fires "heavy/foundation policy" on Lite briefs; doctrine never names that trigger, so lane declarations mean nothing. |
| 21 | #565 | 40 compound Verification commands error opaquely under the shell-less runtime, and block promoting `--brief-command-shape` into default check. |
| 22 | #682 | Two post-cutover briefs fail `--sensitivity`, but the scope sits outside default check so nothing in flight fails. |

## Latent (22)

Ordered cheapest-first. Rows 23–27 are **verify-and-close candidates**, not work —
see § Stale issues below.

| # | GHI | Finding |
|---|-----|---------|
| 23 | #480 | Stale — `gz validate --documents` exits 0 today; the 3536-error condition no longer reproduces. |
| 24 | #561 | Stale — `gz validate --req-kind-discipline` exits 0; the missing citation no longer reproduces. |
| 25 | #563 | Stale — `gz validate --task-envelope-coherence` exits 0; neither signature fires today. |
| 26 | #564 | Stale instance — `gz preflight` clean, no orphan receipt on tree; the class fix (route B) remains unproven. |
| 27 | #538 | Largely delivered by ADR-0.0.69 — `resolve_fence_proof` returns `unproven-fence` when the parent anchor is absent. |
| 28 | #688 | Boot-hook crash needs a non-UTF-8 markdown file in the scanned dirs; none exists today. Ten-line fix, contingent trigger. |
| 29 | #652 | `pythonic.md`'s 600-line cap is authoring-time guidance only — nothing enforces it; file has grown to 806 lines. |
| 30 | #669 | All current status writers already route through the guard; risk is hypothetical future writers. Author concedes non-blocking. |
| 31 | #614 | Miner emits no run-log, so a zero-cluster run cannot be distinguished from a decayed lexicon. Observability only. |
| 32 | #545 | `ReqCoverageRecord` still never constructed in `src/gzkit/`, but it is inert dead schema. Blocked on #543. |
| 33 | #546 | Confirmed asymmetry — no bypass flag in `validate_cmd.py` — but the gate passes clean and `gz covers` already offers an escape hatch. |
| 34 | #547 | Pure doctrine clarification for a boundary case; no runtime surface fails. |
| 35 | #691 | Rules have no staleness clock, but this is a deliberate exclusion needing an operator ruling and a 25-file schema landing. |
| 36 | #594 | 1875 receipts accumulate in a gitignored machine-local directory; disk growth only, no correctness impact. |
| 37 | #581 | Reconcile misses dead surfaces and cross-directory couplings; the issue itself defers the cure pending registry collapse under #519. |
| 38 | #579 | Open design question on whether char count is the right budget unit; nothing fails today. |
| 39 | #580 | Section-ordering policy on already-attested substrate; speculative attention-bias optimization with no observed failure. |
| 40 | #533 | 5k AGENTS.md budget target unreachable until ADR-0.0.37 registry projection lands; the current 15k budget already governs. |
| 41 | #670 | Cross-family design review is unreproducible until `codex:rescue` is callable from the Agent toolset. |
| 42 | #567 | External-catalog design capture; no gzkit surface is broken. |
| 43 | #611 | Architectural absence of a general corrective-action primitive; requires pool ADR and operator design. |
| 44 | #644 | Self-declared open-with-blocker strategy tracker; destination is a future operator design conversation. Gated on #512 Option B. |

---

## Stale issues — fastest queue reduction available

Five issues describe failures that **no longer reproduce**. Readers ran the named
validators and got exit 0 where the body describes an error:

| GHI | Claim in body | Observed today |
|-----|---------------|----------------|
| #480 | 3536 errors from `--documents` | exit 0, zero errors |
| #561 | missing `gz validate --<scope>` proof citation | `--req-kind-discipline` exit 0 |
| #563 | seq=01-only TASKs, worklog events missing `task_id` | `--task-envelope-coherence` exit 0 |
| #564 | orphan `.plan-audit-receipt-*.json` on tree | `gz preflight` clean, no orphan present |
| #538 | no validator checks parent `## Boundary Invariants` shape | `resolve_fence_proof` returns `unproven-fence`, wired into `closeout_proof` |

These were ranked `latent` conservatively. If the verifications hold under a second
look, they are **verify-and-close**, not work — five issues off the queue for the
cost of five command runs. #564 has a caveat: the *instance* is gone but the
*class* fix (route B) remains unproven, so closing it discards the class signal.

---

## Cross-cutting observations

**The queue is entirely direct-fix.** At 262 `fix()` commits in 60 days the precedent
threshold is met many times over for every issue here. Per operator canon — *"GHIs
are AUTHORIZED for direct repair, always"* — none of these needs an ADR or OBPI to
discharge. Escalation to a new ADR is a one-way operator decision, and triage cannot
manufacture it.

**Enforcement-floor work is unfinished.** #698 is the same defect family as the
GHI #699 series just landed (negative controls that pass for the wrong reason). It
was filed during that work and is the tail of it, not a new front.

**REQ-kind proof channels leak in both directions.** #701 tells agents to write
`@covers` tests for REQs that are exempt by proof channel; #703 records four REQs that
already carry them. Same underlying confusion, opposite symptoms — worth fixing as one
unit rather than two.

---

## Provenance

- Rank input: `.gzkit/cache/triage/rank-20260721.json` (gitignored — `.gitignore:56`)
- Renderer: `.claude/skills/ghi-triage/scripts/triage.py --format rank`
- Skill contract: `.gzkit/skills/ghi-triage/SKILL.md`
