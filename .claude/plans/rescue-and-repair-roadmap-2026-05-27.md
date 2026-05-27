# Rescue & Repair Roadmap — gzkit

> **Owner:** Jeffry. **Purpose:** Operator working-doc that survives context clears. Re-read top-down at every session start until each workstream resolves.
> **Origin:** Authored 2026-05-27 from session orientation + ledger replay + ADR/OBPI status. Update the **Status snapshot** block in each workstream as state moves.
> **Not gzkit-ceremony.** This is operator notebook, not a governance artifact. Don't put it through OBPI ceremony — edit freely.

---

## How to re-engage (run these at every session start)

The SessionStart hook already prints orientation. Before doing anything else, run these in this order:

1. `git status --short` — see what's uncommitted (workstream A's gauge).
2. `cat .claude/plans/.pipeline-active.json` — current OBPI pipeline stage + next_command. Source of truth for "what's the next mechanical action".
3. `ls .gzkit/locks/obpi/` — list active OBPI locks. Empty = no claim held.
4. `uv run gz adr status ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine` — ADR-0.0.59 readiness.
5. `gh issue list --state open --label tech-debt --limit 20` — defect/repair backlog.

Use the **Status snapshot** of each workstream below to compare observed state vs. expected and identify the next move.

---

## Workstream A — OBPI-0.0.59-05 sync → complete (CLOSED 2026-05-27T07:34Z)

**One sentence:** Top-5 governance-test sweep is done and attested but uncommitted; the only thing between here and OBPI-05 closure is the staged git-sync and pipeline drainage.

### Status snapshot (as of 2026-05-27T07:34Z — CLOSED)
- ✅ Lock released at 07:22Z (`obpi_lock_released` event).
- ✅ `.claude/plans/.pipeline-active*` markers removed (Layer-3 stale-marker cleanup, advisor-sanctioned).
- ✅ git-sync applied (commit + push to origin/main).
- ✅ OBPI-05 row reads `attested_completed`; ADR closeout phase advances to `pre_closeout` READY.
- ✅ Pipeline launch attempt confirmed blocker: "OBPI is already completed in the ledger" — Layer-2 ground truth wins.

### Next mechanical actions

```bash
# A.1 — Commit + push everything currently dirty
uv run gz git-sync --apply

# A.2 — Pipeline runtime advances sync -> complete; this releases the lock
#       with a token-block-compliant handoff and emits obpi_lock_released.
uv run gz obpi pipeline OBPI-0.0.59-05-first-sweep-wave-top-5-offenders

# A.3 — Confirm closure
uv run gz adr status ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine  # OBPI-05 row stays attested_completed
ls .gzkit/locks/obpi/  # should be empty
```

### Exit criteria for workstream A
- `.gzkit/locks/obpi/` no longer contains the OBPI-05 lock file.
- `.gzkit/ledger.jsonl` tail contains `obpi_lock_released` event for OBPI-05 with a `handoff_path` pointing to a real file under `.gzkit/handoffs/`.
- `git status --short` empty (or only shows untracked operator files).
- `.claude/plans/.pipeline-active.json` removed or stage reads `complete`.

### Watch for
- **Lock-release fails-closed without a handoff** (token-block Sub-Invariant 5). Pipeline runtime is supposed to create the handoff automatically; if it errors, use `/gz-session-handoff` to author one before retry. Never use `--abandon` on a successful run — that's reserved for failure categories in the closed enum.
- **TTL expires before A.1 runs** (~10:26Z). If that happens, the next session's SessionStart hook reaps the lock with a degenerate `abandoned_by_reaper` handoff — you then re-claim before continuing. Cheaper to just run A.1 promptly.
- **Pre-commit hook surfaces lint/test failures.** Hook owns lint/tests; don't `--no-verify`. Diagnose the failure, fix, re-stage, new commit (never amend per Git Safety Protocol).

---

## Workstream B — ADR-0.0.59 closeout ceremony (CLOSED 2026-05-27T08:50Z — ATTESTED)

**One sentence:** Once workstream A closes, ADR-0.0.59 is `pre_closeout` with 5/5 OBPIs READY and QC PENDING (TDD, Docs, BDD, Human attestation) — drive the closeout ceremony to attested.

### Status snapshot (as of 2026-05-27T07:38Z)
- Lifecycle: `Pending` / `pre_closeout`.
- OBPI completion: 5/5 attested.
- Closeout readiness: `READY`.
- QC: `PENDING` on four channels — TDD, Docs, BDD, Human attestation.
- Sensitivity: absent. Lane: heavy. Kind: foundation.

### B.1 ARB receipts (all PASS)
- `arb-ruff-606059e831ba4244b0044cc0340a03f6` — ruff lint clean
- `arb-step-typecheck-4400bd085e354a0ea12141361ff2d543` — ty typecheck clean (5 advisory unused-ignore diagnostics, exit 0)
- `arb-step-unittest-48897982a060478fb616c3da639be17e` — 5637 tests OK in 58s
- `arb-step-coverage-ce1430c23a6c463e8dbafaed8f4cde50` — 5637 tests OK (skipped=1) in 74s
- `arb-step-mkdocs-eca4173bdcfc43e5aa945934d3b74ef3` — strict build OK in 2.87s

### B.2 validators (all PASS)
- `gz validate --documents` ✓
- `gz validate --req-kind-discipline` ✓
- `gz validate --tautological-test-audit` ✓
- `gz adr audit-check ADR-0.0.59-…` ✓ PASS — 19/36 REQs @covers-covered; 17 advisory uncovered (non-blocking; expected for SUPPORT/STRUCTURAL-FENCE kinds)

### B.3 evidence-package defects (informational, surfaced during B.1)
- mkdocs INFO: `docs/governance/behavior-rules.md` references anchor `#rationale-for-behavior-rule-11-course-correction--insights` in `agent-contract-rationale.md` that does not exist. Direct-fix candidate (≤10 lines, single file) — fix during closeout or after operator preference.
- typecheck: 5 unused `# type: ignore` suppression comments. Advisory, exit 0. Direct-fix candidate.

### B.3 closeout outcome (2026-05-27T08:50Z)
- ✅ Attestation: `attest completed` (operator verbatim) + concrete characterization per AGENTS.md § Attestation
- ✅ All 5 quality gates PASS in closeout pipeline (Gate 2 TDD, Lint, Typecheck, Gate 3 Docs, Gate 4 BDD)
- ✅ ADR lifecycle: `Completed` / closeout phase `attested`
- ✅ Two-sync pattern applied (sync 1 committed closeout artifacts; sync 2 clean no-op)
- ✅ ADR status index regenerated (87 ADRs)

### B.3 follow-ups to file (6 new GHIs via /ghi-author post-closeout)
1. **Completion-layer validator gap (HIGH):** does not enforce "BEHAVIOR-kind cannot be uncovered-accepted" — the fail-close gap that let OBPI-05 REQ-01/04 close through SUPPORT advisory while tagged BEHAVIOR. spec-reviewer caught this manually; no mechanical gate.
2. **STRUCTURAL-FENCE parent-ADR shape check:** ADR-0.0.59 ships STRUCTURAL-FENCE kind but lacks `## Boundary Invariants` H2 in parent body. Suggests `gz validate --documents` should fire a check whenever an ADR's children tag STRUCTURAL-FENCE REQs.
3. **Brief-side demo extractor multi-line split:** `## Examples` python -c heredocs split per-line, producing ~65% noise in walkthroughs (37 demos → 13 real for ADR-0.0.59). Routing: OBPI ceremony (ceremony renderer + brief schema).
4. **Brief-side demo correctness audit:** demos in briefs claim to exercise REQs but often don't (demo 8: stdin ignored; demo 9: ambiguous `--brief` flag). Mechanical defense: `gz validate --brief-demo-section` should execute each demo and assert exit-code matches claim.
5. **`req_kind.py:200` no-op `replace("-", "-")`:** quality-reviewer minor cleanup — direct-fix candidate.
6. **`docs/governance/behavior-rules.md` broken anchor:** `agent-contract-rationale.md#rationale-for-behavior-rule-11-course-correction--insights` target anchor missing — direct-fix candidate.

### Next mechanical actions

```bash
# B.1 — Snapshot canonical proof commands (ARB receipts feed Gate 5 attestation)
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb coverage run -m unittest discover -s tests -t .
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# B.2 — Closeout audit/check pass
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --tautological-test-audit
uv run gz adr audit-check ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine

# B.3 — Closeout ceremony (skill-driven, operator-attested)
# Invoke /gz-adr-closeout-ceremony — presents REQ-by-REQ evidence, you attest verbatim.
```

### Exit criteria for workstream B
- ADR-0.0.59 lifecycle == `Attested`.
- `gz adr status ADR-0.0.59-…` shows QC = ATTESTED (all 4 channels green).
- A `gate5_attestation_emitted` (or equivalent) event for ADR-0.0.59 in the ledger.

### Decision points / watch for
- **BDD deferral:** Brief notes BDD is deferred to ADR-0.0.59 closeout composite scope (same pattern as OBPI-02/-03/-04). Verify which scenarios need landing now vs. which are covered by sibling-ADR coverage before attesting Docs/BDD channels. If `behave` step-def gaps surface mid-closeout (see GHI #490-class regression), file via `/ghi-author` rather than excusing them as "pre-existing".
- **Three legacy REQs** (`REQ-0.0.17-04-10`, `REQ-0.0.32-07-08`, `REQ-0.0.32-07-09`) enter "effective-SUPPORT-pending-reclassification" — brief § Tracked Defects has the reclassification path. Confirm the tracked-defect entries survive into closeout receipts so reclassification doesn't get lost.
- **Operator-verbatim attestation:** Append concrete characterization grounded in session evidence (canonical-invocation receipt IDs from B.1, file counts, REQ counts). Never include `2949663+ahuimanu@users.noreply.github.com`; use `g0` or GitHub noreply if a CLI demands email shape.

---

## Workstream B′ — ADR-0.0.59 post-closeout audit pass (CLOSED 2026-05-27T09:39Z — VALIDATED)

**One sentence:** After B closed at Completed, operator ran an ADR audit pipeline that transitioned ADR-0.0.59 Completed→Validated; commit `7aeb6a65` landed the audit artifacts that had been sitting uncommitted at session start.

### Status snapshot
- ✅ ADR-0.0.59 lifecycle: `Validated` / closeout phase `validated` / QC `READY`.
- ✅ Audit emitted `audit_receipt_emitted` events (meta-receipt-bind + validated) attested by g0.
- ✅ Versioning table row appended: `0.0.59 | Validated | g0 | 2026-05-27 | accept audit — …`.
- ✅ Audit artifacts under `docs/design/adr/foundation/ADR-0.0.59-…/audit/` (`AUDIT_PLAN.md`, `AUDIT.md`, 10 proof files in `proofs/`) committed in `7aeb6a65`.
- ✅ git-sync clean, no active locks, no pipeline markers.
- ✅ B.3 follow-up GHIs all filed/fixed pre-session (#537, #538, #539, #540 filed; #541 `req_kind` no-op replace, #542 broken anchor — both already shipped as direct-fix commits `6588d35a`, `e7d9630f`).

### Audit-surfaced follow-ups (6 non-blocking, identified in AUDIT.md)
Per the Validated row enrichment, the audit identified six channel-depth shortfalls worth tracking. Re-read `audit/AUDIT.md` § Follow-up GHIs to enumerate them before opening tickets — they are distinct from the 6 closeout-time follow-ups above.

---

## Workstream C — Defect / tech-debt GHI cluster (BACKLOG)

**One sentence:** Open repair-flavored GHIs that aren't blocking workstreams A/B but are the next plate after ADR-0.0.59 closes — route each per AGENTS.md § Defect-fix routing thresholds.

### Status snapshot (open GHIs, by rough cluster — re-run `gh issue list --state open --label tech-debt --limit 30` for current truth)

| GHI | Title (short) | Cluster | Routing intuition |
|-----|---------------|---------|-------------------|
| #480 | validate --documents: 3536 errors from schema convention additions | **Big bang validator backfill** | OBPI ceremony — scope crosses many ADRs |
| #524 | ADR-0.2.0-gate-verification fails --documents (status enum + sections) | Same cluster as #480 | Direct fix if ≤10 lines/file; otherwise rolls into #480 |
| #527 | ADR-0.0.9-state-doctrine fails --documents (status enum + sections) | Same cluster as #480 | Direct fix or roll into #480 |
| #519 | codex: gzkit context surface exhausts 258K window | **Codex/runtime emergency** | OBPI ceremony — schema/runtime contract |
| #534 | obpi pipeline: subprocess reader crashes on non-utf8 grandchild stdout | **Pipeline runtime defect** | Direct fix candidate (single surface) |
| #536 | gz adr promote: Target Scope path:line refs produce invalid OBPI paths | **CLI defect** | Direct fix candidate |
| #532 | manpages: 4 brief files reference docs/user/manpages/gz-validate.md | **Doc drift** | Direct fix — trivial path rename |
| #528 | gz-session-handoff: skill + orientation hook disagree on location | **Handoff plumbing** | Direct fix candidate |
| #529 | handoff system: not wired into OBPI pipeline; no gz handoff CLI verb | Same as #528 | OBPI ceremony — adds CLI surface |
| #533 | agents-md-budget: 5k recovery target needs ADR-0.0.37 + registry-projection | **Doctrine** | OBPI ceremony — blocked on ADR-0.0.37 |
| #525 | CLAUDE.md should redirect to AGENTS.md | **Doctrine doc** | Direct fix — done; verify it stays correct |
| #518 | foundation-triage: id-slug split filters all real foundation ADRs | **Triage defect** | Direct fix |
| #516 | closeout-ceremony: passive-presenter loop lacks REQ-evidence mech verify | **Closeout discipline** | OBPI ceremony — touches attestation surface |

### Suggested prioritization (operator override at will)

1. **Unblock workstream B first** — #527 and #524 may surface during ADR-0.0.59 closeout's `gz validate --documents` step. If so, decide in-flight: direct fix (≤10 lines, ≤2 files, precedent ≥3 fix() commits in 60d) vs. file under #480 umbrella.
2. **Pipeline plumbing while context is hot** — #534 (utf8 crash) and #528/#529 (handoff coupling) touch the same runtime you just exercised in workstream A. Cheapest to fix now.
3. **Codex context emergency** — #519 is labeled `emergency`. Triage scope before scheduling; may need its own ADR.
4. **Big-bang validator backfill** — #480 is the heaviest piece. Author an ADR or absorb into ADR-0.0.59 successor; this is OBPI ceremony, not direct fix.

### Per-GHI re-engagement protocol
1. `gh issue view <N>` — re-read body.
2. Compute routing facts (diff size estimate, scope, precedent count, trigger, coverage).
3. Apply AGENTS.md § Defect-fix routing thresholds mechanically.
4. If direct fix: `fix(<scope>): <summary> (GHI #N)` with TDD evidence.
5. If OBPI ceremony: `/gz-obpi-specify` → `/gz-plan` → `/gz-obpi-pipeline`.
6. Never default to ceremony on ambiguity — surface routing facts to operator first.

---

## Cross-workstream invariants (DO NOT FORGET)

- **Never `git add -A` or `git add .`** — stage specific files (Git Safety Protocol).
- **Never amend; always new commit** on hook failure (Git Safety Protocol).
- **Never include `2949663+ahuimanu@users.noreply.github.com`** in any repo-bound artifact (Operator PII rule).
- **Never read frontmatter `status: Completed` as truth** — read the ledger (Behavior Rules — Never #7).
- **<90% sure of direction → ask the human.** Burning context on wrong-direction work is the most expensive failure (Behavior Rule — Always #7).
- **Course-correction → append `improvement` to `.gzkit/insights/agent-insights.jsonl`** before completing the corrected work (Behavior Rule — Always #11).
- **Token-block discipline:** every lock release pairs with a register-entry handoff (`/gz-session-handoff` skill).

---

## State pointers (single-source-of-truth references)

| Question | Authoritative source |
|----------|----------------------|
| "What's the current OBPI pipeline stage?" | `.claude/plans/.pipeline-active.json` |
| "Is an OBPI lock claimed?" | `ls .gzkit/locks/obpi/` |
| "What's the ADR's lifecycle/QC state?" | `uv run gz adr status <ADR-ID>` |
| "What ledger events fired recently?" | `tail .gzkit/ledger.jsonl` |
| "What course-corrections did I take?" | `.gzkit/insights/agent-insights.jsonl` |
| "What handoffs are recorded?" | `ls .gzkit/handoffs/` |
| "What governance rules bind here?" | `AGENTS.md`, `.gzkit/rules/`, `.claude/rules/` |
| "What's the latest plan-audit verdict for active OBPI?" | `.claude/plans/.plan-audit-receipt-<OBPI-ID>.json` |

---

## Update log

- 2026-05-27 — Initial roadmap authored from session orientation. Three workstreams: A=OBPI-05 sync, B=ADR-0.0.59 closeout, C=defect/tech-debt GHI cluster. Active OBPI lock TTL ~10:26Z.
- 2026-05-27T09:39Z — Added Workstream B′ (post-closeout audit pass, CLOSED Validated). Sync of uncommitted audit artifacts landed in `7aeb6a65`. Workstreams A, B, B′ all closed; Workstream C is the next plate.
- 2026-05-27T~10:15Z — Filed 5 net-new audit GHIs (#543 SUPPORT ledger-query, #544 grandfathering schema, #545 ReqCoverageRecord dead schema, #546 bypass asymmetry, #547 suite post-condition doctrine). Comment added to #538 with audit #2 per-REQ anchor depth refinement. Prior-art sweep confirmed no duplicates. Cross-links posted on #537 (for #543). Roadmap update synced.
- 2026-05-27T~10:45Z — Workstream C started. **GHI #534 CLOSED** via direct fix `8a63d91f` (`fix(lock_manager): tolerate non-utf8 stdout in current_branch`). Repo-wide audit during routing revealed scope drift: GHI claimed "≤10 LOC, single surface" but actual class is 39 subprocess sites in 20+ modules. Operator chose direct-fix-only path (no OBPI ceremony for class cleanup); the 38-site audit inventory remains durable in #534's audit comment for future routing. Class cleanup deferred. Regression-fenced by `test_subprocess_run_uses_errors_replace` in `tests/test_lock_manager.py`.
