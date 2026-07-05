# Flight-Test Manifest

> The **coverage contract**. Six sorties, in build-up order, spanning every
> gzkit system. Each sortie below lists its design claim, ordered test points
> (governed path → expected black-box observable), and its pass signature. A
> full [flight card](flight-card-template.md) is authored per sortie at fly
> time; this manifest is the standing plan the cards are drawn from.
>
> Systems coverage is proven by the matrix in §7 — an unmapped gzkit system is a
> visible hole, not a silent omission.

Envelope legend: **●** center · **◐** expansion · **○** corner.

---

## S1 — Cold Start & Spine ●

**Design claim:** The canonical spine chains end-to-end — a virgin repo becomes
an attested, closed ADR — and every link is gated by the one before it, with the
whole chain recorded to Layer-2.

| # | Governed path | Expected observable (black box) |
|---|---|---|
| 1 | `gz init` | Canonical surfaces materialize; `gz validate --distribution` byte-equivalent |
| 2 | `gz agent sync control-surfaces` | Skill mirrors + manifest regenerate; no drift |
| 3 | `gz personas list` / `gz skill list` | Discovery returns the seeded catalogs |
| 4 | gz-prd | PRD artifact authored + linked; ledger `artifact_edited` |
| 5 | gz-constitute | Constitution artifact anchors the PRD lineage |
| 6 | gz-plan / gz-adr-create | ADR booked; `kind`/`lane`/`semver` consistent; `gz validate --taxonomy` clean |
| 7 | gz-obpi-specify | OBPI brief(s) 1:1 with ADR checklist; REQ kinds tagged; `gz validate --req-kind-discipline` clean |
| 8 | gz-plan-audit / gz-justify | Pre-implementation alignment recorded before any edit |
| 9 | gz-obpi-lock (claim) | `obpi_lock_claimed` event; lock visible in orientation |
| 10 | gz-implement | Gate 2 tests pass; REQ-coverage gate satisfied |
| 11 | gz-arb (ruff/typecheck/unittest/coverage) | Receipts `arb-ruff-`, `arb-step-typecheck-`, `arb-step-unittest-`, `arb-step-coverage-` |
| 12 | `gz gates` / `gz status` | Gates 1–4 green for the ADR |
| 13 | gz-adr-closeout-ceremony + `--attestation-text` | Gate 5 human attestation recorded; `gz obpi complete` |
| 14 | gz-adr-emit-receipt | `obpi_receipt_emitted` / `audit_receipt_emitted` with scoped payload |
| 15 | gz-obpi-lock (release) | `obpi_lock_released` event |
| 16 | `gz register-adrs` + `gz validate --adr-status-fresh` | Layer-3 index regenerated from canon; freshness passes |
| 17 | gz-git-sync (`--apply --lint --test`) | Clean tree, gates green, branch synced |

**Pass signature:** an unbroken ledger chain from `artifact_edited` (PRD) →
Gate-5 attestation → receipt, with all ARB receipts present and
`gz validate --distribution --taxonomy --req-kind-discipline --adr-status-fresh`
clean at exit.

---

## S2 — Promotion & Decomposition ◐

**Design claim:** The pool→promote path and the decomposition matrix produce
correctly-shaped, traceable artifacts, and contract-bearing OBPIs are carried by
the runtime pipeline, not freehand.

| # | Governed path | Expected observable |
|---|---|---|
| 1 | gz-plan (`--kind pool`) | `ADR-pool.<slug>` scaffold; no `kind`/`semver` frontmatter |
| 2 | gz-adr-promote (`--kind feature`\|`foundation`) | Promoted ADR gains correct `kind`/semver; taxonomy clean |
| 3 | gz-obpi-specify (decomposition matrix) | Briefs right-sized per the matrix; 1:1 checklist sync holds |
| 4 | `gz obpi pipeline <ID>` | Stage sequence verify→ceremony→git-sync→completion recorded |
| 5 | gz-adr-map | Traceability graph resolves ADR→OBPI→REQ→test |
| 6 | gz-adr-sync | `@covers` discovery + ledger reconciliation converge |
| 7 | gz-adr-status | Focused lifecycle view matches Layer-2 |

**Pass signature:** promotion events + pipeline stage events in the ledger; a
traceability map with no dangling artifact; taxonomy + 1:1-sync validators clean.

---

## S3 — Defect & Issue Loops ◐

**Design claim:** A defect routes by the mechanical thresholds — not intuition —
to the direct-fix path, is tracked end-to-end, and brief/OBPI drift is caught
and reconciled under attestation.

| # | Governed path | Expected observable |
|---|---|---|
| 1 | (induce a defect in the substrate) | A failing test / observed wrong behavior |
| 2 | ghi-author | GHI created via `/ghi-author` (Step-0 prior-art lookup ran) |
| 3 | defect-fix routing decision | Routing facts computed (diff size, scope, precedent via `git log --grep`) |
| 4 | direct fix | `fix(<scope>): … (GHI #N)` commit with TDD evidence |
| 5 | ghi-close | GHI closed citing the commit SHA |
| 6 | ghi-triage | Open-queue triage renders a deterministic rank |
| 7 | gz-brief-reconcile | Induced brief drift detected; amendment written under attestation; `brief_reconciled` event |
| 8 | gz-obpi-reconcile | Stale OBPI metadata corrected; ADR table synced |
| 9 | gz-obpi-simplify | Reuse/quality pass over brief scope; fixes applied |
| 10 | gz-issue-file | Cross-repo filing routes to the gzkit repo with provenance trailer *(note if N/A on substrate)* |

**Pass signature:** GHI open→close with SHA citation; `brief_reconciled` event;
routing facts logged before the fix; no ceremony inflation on a direct-fix-class
defect.

---

## S4 — Integrity & Adversarial ○

**Design claim:** gzkit's anti-vibing invariants **fail closed** — fraudulent
completions can be reversed, phantom work retired, bypasses blocked, and derived
views can never masquerade as truth.

| # | Governed path | Expected observable |
|---|---|---|
| 1 | `gz obpi repudiate` | A fabricated Gate-5 reversed; `repudiated=True`, OBPI still visible, re-completable |
| 2 | `gz obpi withdraw` | A phantom/superseded OBPI permanently retired; hidden from roll-ups |
| 3 | hook-block integrity | A `--no-verify` / drifted commit **blocked**; cannot be worked around |
| 4 | `gz validate --adr-status-fresh` (desynced) | Hand-edited Layer-3 index fails closed; `register-adrs` regenerates |
| 5 | `gz validate --invariant-coherence` | Mutated rendered AGENTS.md caught against corpus source of truth |
| 6 | gz-content-remember → gz-content-compose | Corpus round-trip: `remember` appends, `compose` validates invariant floor |
| 7 | gz-advisor-qc | `advise-rendition` receipt produced for the composed candidate |
| 8 | `gz validate --cli-alignment` | An unregistered `gz <verb>` reference in a doc fails closed |
| 9 | gz-migrate-semver | Identifier migration event recorded correctly |
| 10 | `gz validate` (sweep) | `--documents --surfaces --unscoped-rules --advisory-scorecard --advisor-proof-binding` clean |

**Pass signature:** every adversarial probe produces a *fail-closed* result or a
correct reversal event; no probe succeeds by leaving the governed path (that
would itself be the finding).

---

## S5 — Quality & Maintenance ◐

**Design claim:** The quality, complexity, and maintenance systems produce
receipted, attestable evidence and route their findings without unattended
governance mutation.

| # | Governed path | Expected observable |
|---|---|---|
| 1 | gz-check | Full lint/format/test/typecheck pass in one sweep |
| 2 | `gz arb validate` | Canonical step-command drift detection clean |
| 3 | gz-complexity-advisor / gz-complexity-guide | Diagnosis + authoring-time hints render |
| 4 | gz-complexity-distill | Distillation pass refreshes doctrine against the exemplar corpus |
| 5 | gz-pythonic-pattern-detect / -apply | Candidate flagged; rewrite backed by semantics-pinning test + non-regressing complexity deltas |
| 6 | gz-tech-debt-review | Line-grounded prioritized report; routes to chores/GHI, never OBPI |
| 7 | gz-adr-evaluate | ADR/OBPI scored on weighted dimensions; red-team challenges run |
| 8 | gz-context-diet | Pedagogical narrative lifted; binding bullets remain; budgets hold |
| 9 | gz-tidy / gz-check-config-paths / gz-cli-audit | Hygiene, path coherence, and manpage parity clean |
| 10 | gz-mx (enter/status/exit) | Maintenance-hangar session opens, repairs, and exits cleanly |
| 11 | gz-deps-upgrade | Toolchain/pins refreshed *(optional — mutates toolchain; note if deferred)* |

**Pass signature:** each system emits its receipt/report; complexity rewrites
carry TDD GREEN + complexity deltas; no maintenance system mutates governance
state without attestation.

---

## S6 — Release & Continuity ◐

**Design claim:** A completed increment becomes a released artifact with no
version left unreleased, and session context survives a handoff boundary intact.

| # | Governed path | Expected observable |
|---|---|---|
| 1 | version bump | `pyproject.toml` + `__init__.py` + README badge bumped together |
| 2 | gz-patch-release | Narrative release notes drafted; operator-approved; RELEASE_NOTES updated |
| 3 | gz-git-sync | Final guarded sync; gates green |
| 4 | `gh release create vX.Y.Z` | Release published; no bump left unreleased |
| 5 | gz-session-handoff (create) | Handoff doc written; advised next steps recorded |
| 6 | gz-session-handoff (resume) | RESUME contract: advises, does not authorize; context reconstituted |
| 7 | gz-context `<ADR-ID>` | Focused context bundle (body + briefs + covering tests + rules) loads |

**Pass signature:** a `gh` release exists for the bumped version; a handoff doc
round-trips (create→resume) with the advised-vs-authorized boundary intact.

---

## 7. Systems → Sortie coverage matrix

Every gzkit system maps to at least one sortie. A system with no row is untested
design surface.

| System / `gz` surface | Sortie |
|---|---|
| `gz init` | S1 |
| agent sync control-surfaces | S1 |
| personas list / skill list / skill-router | S1 |
| PRD (gz-prd) | S1 |
| constitution (gz-constitute) | S1 |
| ADR create / plan (gz-plan, gz-adr-create) | S1 |
| OBPI specify / decomposition (gz-obpi-specify) | S1, S2 |
| plan-audit / justify | S1 |
| obpi-lock (claim/release) | S1 |
| implement (Gate 2, REQ coverage) | S1 |
| arb receipts (ruff/typecheck/unittest/coverage/mkdocs) | S1, S5 |
| gates / status | S1 |
| closeout ceremony + Gate-5 attestation | S1 |
| emit-receipt | S1 |
| register-adrs / adr-status-fresh | S1, S4 |
| git-sync (guarded) | S1, S6 |
| state | S1 (throughout) |
| ADR promote (pool→feature/foundation) | S2 |
| decomposition matrix | S2 |
| obpi pipeline (contract-bearing) | S2 |
| adr-map / adr-sync / adr-status | S2 |
| taxonomy validate | S1, S2 |
| GHI author / close / triage | S3 |
| defect-fix routing | S3 |
| issue-file (cross-repo) | S3 |
| brief-reconcile | S3 |
| obpi-reconcile / obpi-simplify | S3 |
| repudiate / withdraw (ADR-0.0.71) | S4 |
| hook-block integrity (no-verify, drift) | S4 |
| invariant-coherence | S4 |
| content remember / compose | S4 |
| advisor-qc / advise-rendition | S4 |
| cli-alignment validator | S4 |
| req-kind-discipline validator | S1, S4 |
| migrate-semver | S4 |
| validate sweep (documents/surfaces/distribution/unscoped-rules/advisory-scorecard/advisor-proof-binding) | S1, S4 |
| gz check | S5 |
| arb validate | S5 |
| complexity advisor / guide / distill | S5 |
| pythonic-pattern detect / apply | S5 |
| tech-debt review | S5 |
| adr-evaluate (scoring + red-team) | S5 |
| context-diet | S5 |
| tidy / check-config-paths / cli-audit | S5 |
| mx maintenance hangar | S5 |
| deps-upgrade | S5 |
| patch-release / gh release | S6 |
| session-handoff (create/resume) | S6 |
| context load (gz-context) | S6 |

> Systems intentionally **not** flown (with reason) are recorded here as they
> arise — e.g. `airlineops-parity-scan` and `competitor-radar` are gzkit-repo
> operations, not substrate-facing workflows, so they are out of the
> substrate-flight envelope. Record any such exclusion rather than dropping it
> silently.
