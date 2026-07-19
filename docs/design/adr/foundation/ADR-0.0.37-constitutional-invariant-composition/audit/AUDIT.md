# AUDIT — ADR-0.0.37-constitutional-invariant-composition

**Date:** 2026-07-18
**Ceremony:** `/gz-adr-audit` — COMPLETED → VALIDATED
**Driver persona:** `pipeline-orchestrator`
**Lane / kind:** heavy / foundation
**Entry state:** Lifecycle `Completed`, closeout phase `attested`, OBPI 15/15

---

## Fidelity Gate (Step 3 — bound)

`uv run gz adr fidelity ADR-0.0.37-constitutional-invariant-composition` → **exit 0, 4 pass / 0 fail**

| # | Claim | Command | Expected | Observed | Result |
|---|---|---|---|---|---|
| 1 | Committed AGENTS.md byte-matches deterministic playback of the committed rendition; hand-edits fail closed | `gz validate --invariant-coherence` | 0 | 0 | ✓ |
| 2 | CIC-2 brief↔reality reconciliation is live and fail-closed | `gz validate --brief-reconcile` | 0 | 0 | ✓ |
| 3 | Corpus↔rendition freshness and rendition-byte integrity are enforced | `gz validate --rendition-freshness` | 0 | 0 | ✓ |
| 4 | The Fidelity Assertions block is parseable by the fidelity gate | `gz adr fidelity … --check` | 0 | 0 | ⚠ **tautological** |

⚠ **Row 4 is not evidence.** It asserts the block is parseable and verifies that by running the
gate that parses the block — it cannot fail while being evaluated. The ADR's real fidelity
evidence is **3 rows, not 4**. Filed as **GHI #702**, cross-linked to #699 as a sibling cut of the
same root cause on a different surface. Proof: `audit/proofs/fidelity.txt`.

## Execution log

| # | Check | Command | Result |
|---|---|---|---|
| C1 | Ledger completeness | `gz adr audit-check ADR-0.0.37` | ✓ exit 0 — PASS, all 15 linked OBPIs completed with evidence |
| C2 | REQ coverage (independent) | `spec-reviewer` dispatch | ✓ PASS — no BEHAVIOR gap |
| C3 | Fidelity gate | `gz adr fidelity` | ✓ exit 0 (4 pass; see ⚠ above) |
| C4 | Heavy-lane gates | `gz gates --adr ADR-0.0.37` | ✓ Gates 1–4 PASS; Gate 5 pending (this ceremony) |
| C5 | Unit suite | `uv run -m unittest -q` | ✓ **7160 tests, OK** |
| C6 | CLI governance | `gz cli audit` | ✓ exit 0 — 130/130 commands covered |
| C7 | Structural coherence (independent) | `quality-reviewer` dispatch | ⚠ CONCERNS — see Shortfalls |
| C8 | Checklist 1:1 sync | checklist vs `gz adr status` | ✗ → **remediated** (S1) |
| — | BDD | `uv run -m behave features/` (inside C4) | ✓ 66 features, 401 scenarios, 0 failed |
| — | Docs build | `mkdocs build --strict` (inside C4 + ARB) | ✓ clean |
| — | Documents | `gz validate --documents` | ✓ exit 0 (re-run post-remediation) |

## ARB receipts

| Claim | Receipt ID |
|---|---|
| Lint clean | `arb-ruff-0864e223064745a69725fd348217f296` |
| Type check clean | `arb-step-typecheck-997ab50e851c42cb851d042a915ecb8f` |
| Tests pass | `arb-step-unittest-753d3dda7252450da406703b9045b696` |
| Docs build clean | `arb-step-mkdocs-b3861e3c6db34d8282a625f6f10119d1` |

All four exit 0. Proof: `audit/proofs/arb-receipts.txt`.

## Evidence index

| Artifact | Path |
|---|---|
| Audit plan | `audit/AUDIT_PLAN.md` |
| Fidelity gate output | `audit/proofs/fidelity.txt` |
| Unit suite output | `audit/proofs/unittest.txt` |
| Heavy-lane gates output | `audit/proofs/gates.txt` |
| CLI audit output | `audit/proofs/cli-audit.txt` |
| ARB receipts | `audit/proofs/arb-receipts.txt` |
| audit-check capture | scratchpad `audit-check.txt` |

## Independent persona dispatches

**`spec-reviewer` — VERDICT: PASS.** Traced all 157 REQs across 27 briefs against 305 `@covers`
decoration sites. Every BEHAVIOR REQ on all 15 linked OBPIs is covered. Of the 27 uncovered REQs
belonging to linked briefs, **26 are `[SUPPORT]` and 1 is `[structural-fence]`** — which under
ADR-0.0.59 owe no `@covers` test by proof channel; authoring one would be the `.claude/rules/adr-audit.md`
Rules (c) anti-pattern. The "non-blocking" advisory is honest; no coverage gap is papered over.
The reviewer self-corrected a first-pass error (it had read OBPI-08/10's lowercase `[behavior]`
tags as untagged).

**`quality-reviewer` — VERDICT: CONCERNS.** See Shortfalls S1–S2. The driver independently
verified each load-bearing claim and **refuted one**: the reviewer's F3 asserted `tier_policy` had
no live consumer, but `src/gzkit/content/composer.py:20` and
`src/gzkit/governance/trust_audits/rendition_floor_coherence.py:24` both import it.

## Shortfalls

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| S1 | Blocking | Checklist 1:1 drift — items 02/03/21/22 carried no `[withdrawn]` marker while 09 and 11–17 did; scorecard read `Final Target OBPI Count: 19` against 15 actual survivors | **Remediated** |
| S2 | Blocking | Terminal Disposition credited the delivered playback floor to OBPIs 18–27, but `rendition_store.py` / `rendition_freshness.py` / `composer.py` / `tier_policy.py` originate in the withdrawn briefs 21/22 | **Remediated** |
| S3 | Non-blocking | Fidelity row 4 is tautological | **GHI #702** (cross-linked to #699) |
| S4 | Non-blocking | `triangle` REQ parser skips bold kind-tags — 6 REQs silently dropped on the `ADR-0.34.0` capstone | **GHI #700** |
| S5 | Non-blocking | audit-check advisory is REQ-kind-agnostic, reporting SUPPORT/STRUCTURAL-FENCE as owing `@covers` | **GHI #701** |
| S6 | Non-blocking | `REQ-0.0.37-15-05/-06` are `[SUPPORT]` yet `@covers`-decorated — inverted proof channel | **GHI #703** |

### Remediation applied (S1, S2)

Operator-authorized in-session, then re-verified:

1. `[withdrawn]` markers added to checklist items **02, 03, 21, 22**, each naming the repudiation
   date, the `obpi_withdrawn` event and commit `d03ce98f`, and the GHI #623 severance.
2. Items 21/22 additionally carry a **NOTE** pointing at the source files that ship from their work.
3. Scorecard corrected **19 → 15**, with a dated reconciliation comment deriving the new count
   (7 base + 8 re-aligned) and tying it to `gz adr status` 15/15.
4. New **"Attribution (2026-07-18 audit reconciliation)"** paragraph in § Terminal Disposition,
   naming OBPIs 21/22 as the origin of the shipped playback floor, distinguishing the *severed
   unbuilt half* (attributable corpus→candidate generator, `rendition ⊆ corpus` lineage gate) from
   the *shipped code*, and keeping re-completion refused.

Re-verification after remediation: `gz validate --documents` exit 0; `gz adr fidelity` exit 0
(4 pass / 0 fail); `gz adr audit-check` exit 0 PASS; `gz adr status` unchanged at 15/15.

---

## What this audit bought

Every mechanical gate on ADR-0.0.37 was green before either reviewer opened a file — audit-check exit 0, fidelity 4/4, 7160 tests passing, 130/130 CLI coverage. A checklist read would have stopped there and validated the ADR on the strength of those numbers. What the adversarial dispatch bought was the discovery that two of those green numbers were themselves wrong, and that the checklist had drifted out from under the code that was actually running in production.

The concrete find: OBPI-0.0.37-22 carries `status: Abandoned` in its frontmatter, but `src/gzkit/content/rendition_store.py` and `src/gzkit/governance/trust_audits/rendition_freshness.py` — the deliverables of that "abandoned" brief — are shipping, imported, and load-bearing (`composer.py:20`, `rendition_floor_coherence.py:24`). The Terminal Disposition had already credited this code as delivered. No test failed, no lint failed, no gate failed — because the defect isn't in the code, it's in the paper trail describing the code. That's exactly the failure class ADR-0.0.37 exists to prevent: canon diverging from delivered reality. A green checklist is structurally blind to this because "Abandoned" and "load-bearing in production" are both true simultaneously, and nothing in the mechanical layer cross-checks frontmatter status against import graphs.

The audit also caught a fidelity row that couldn't have failed under any circumstance — row 4 asserts the composition block is "parseable by the fidelity gate," verified by running the fidelity gate against it. That's not evidence, it's a tautology wearing evidence's clothes. `gz adr fidelity` reported 4/4 pass; the honest count is 3 real assertions and one that measures nothing. This is the same defect class already tracked as GHI #699 (32 of 47 enforcement claims don't exercise their claim) — ADR-0.0.37 turns out to be a live instance of the pattern it was itself scrutinizing.

The scorecard error (claimed "Final Target OBPI Count: 19," actual survivors 15) and the missing `[withdrawn]` markers on items 02/03/21/22 are smaller instances of the same drift: the artifact stopped being reconciled against the project's current shape somewhere along the way, and nothing forced a reconciliation before this ceremony. The quality-reviewer's independent verification also matters here in the other direction — it checked its own F3 claim (that `tier_policy` had no live consumer) against the actual import graph and found itself wrong. That's a materially different signal than a rubber-stamp "LGTM": both the finding and the reviewer's self-correction are visible in this record, which is what makes the CONCERNS verdict trustworthy rather than performative.

None of this changes what shipped. The playback floor works, the tests cover the BEHAVIOR REQs that owe coverage, and the 27 nominally-uncovered REQs are legitimately exempt by proof channel (26 SUPPORT, 1 structural-fence, per ADR-0.0.59). What the audit bought is the difference between "the code works" and "the record of why and how it works is accurate" — and on this ADR, before today, it wasn't.

## Disposition

The operator should validate this ADR as **Completed — Partial (superseded)**, not as a clean full-scope completion. The foundation invariant — constitutional-invariant composition as a kept, load-bearing mechanism — is real and shipping. The originally-scoped full composition engine was never built and is explicitly severed to GHI #623 as post-1.0 work; that's a scope reduction the ADR should say plainly rather than let a stale "19 OBPIs" scorecard imply otherwise.

Validating today is defensible specifically because the drift was caught and repaired in this session, not because it didn't exist: the four checklist items now carry `[withdrawn]` markers with disposition and GHI #623 pointers, the scorecard is corrected 19→15 with a dated reconciliation note, and a new Attribution paragraph names OBPI-0.0.37-21/22 as the true origin of the shipped playback floor while explicitly declining re-completion of those briefs. Attesting Gate 5 now is attesting to that reconciled record — code that works, plus a checklist that finally agrees with it — not to the pre-audit version where "Abandoned" quietly meant "shipped."

---

## Attestation

**Agent (audit driver):** all checks in the execution log executed and recorded; S1 and S2
remediated and re-verified; S3–S6 routed to GHIs #700–#703. No unresolved ✗ remains.

**Human (Gate 5):** recorded via `gz adr emit-receipt --event validated` with the operator's
verbatim audit acceptance relayed in `attestation_text`. See the ledger receipt for the
authoritative record.
