# AUDIT — ADR-0.0.67-tool-skill-invariant1-enforcement

**Lifecycle transition:** COMPLETED → VALIDATED
**Lane / Kind:** heavy / foundation
**Audit date:** 2026-06-09
**Driver persona:** pipeline-orchestrator
**Independent reviewers:** spec-reviewer (REQ-tracing), quality-reviewer (structural coherence), narrator (value framing)
**Trust layer:** Layer-2 (consumes ledger proof; `gz adr audit-check` PASS, attestations 1–2 days old, inside 7-day staleness window)

---

## Feature Demonstration

The operator can now trust that tool-skill **Invariant 1** — *every CLI verb is wielded by a skill or it is a defect* — holds across the **entire** CLI surface, not just the top-level verbs. Before this ADR, the orphan check saw only 51 top-level verbs; the 73 multi-word leaf paths beneath them were invisible, so a capable-but-unwielded subcommand could ship undetected.

Delivered capabilities:

- **Full-surface enforcement.** The orphan check now recurses into multi-word subcommands — 104 full leaf paths, including all 73 multi-word leaves — instead of stopping at the 51 top-level verbs.
- **10 orphaned-but-capable verbs adopted, zero waivers.** Six skills now genuinely wield verbs that previously had no skill home — including `gz obpi audit` (a deterministic auditor reconcile) and `gz obpi withdraw` (phantom-lock cleanup).
- **3 deprecated aliases removed.** The `obpi lock-*` hyphen aliases the source itself marked for removal are gone; the CLI no longer advertises verbs it had already deprecated.
- **A deterministic per-OBPI audit array.** `gz obpi audit` now emits a structured, per-criterion audit table that `gz-obpi-reconcile` Phase 1 wields directly — replacing ad-hoc agent Read/Grep/Bash reconnaissance with one reproducible command.

### Capability 1 — Invariant 1 enforced across the full CLI surface

Command: enumerate the recursed surface and confirm coverage of multi-word leaves.

```
top-level verbs: 51
full leaf paths: 104
multi-word leaf paths enumerated: 73
obpi audit in paths: True
obpi withdraw in paths: True
obpi lock-claim (deleted alias) in paths: False
obpi lock claim (canonical) in paths: True
```

Validator confirmation:

```
gz validate --skill-alignment    → All validations passed (1 scopes)
gz validate --req-kind-discipline → All validations passed
```

**Why this matters:** A verb that exists but no skill wields it is a vibing surface — a capability an agent can reach for outside any governed workflow. The orphan check now sees all 73 multi-word leaves that were previously invisible, so that gap is closed mechanically rather than by goodwill.

### Capability 2 — Deprecated hyphen aliases actually removed

Command: invoke a deleted alias and the canonical replacement.

```
$ gz obpi lock-claim
BLOCKERS: gz obpi: error: argument obpi_command: invalid choice: 'lock-claim'
  (choose from emit-receipt, status, pipeline, reconcile, validate,
   precomplete, withdraw, audit, complete, lock)
$ gz obpi lock list
No active locks.
```

**Why this matters:** The CLI no longer advertises verbs the source already marked deprecated. The hyphen alias is gone and the canonical `gz obpi lock <subcommand>` path works — the surface now matches its own deprecation decision instead of carrying dead aliases.

### Capability 3 — Deterministic per-OBPI audit array

Command: `gz obpi audit --adr ADR-0.0.67`

```
OBPI-0.0.67-01: FAIL
    PASS Test files exist: tests/governance/test_promoted_advisory_audits.py
    PASS Tests pass: 64 tests
    FAIL Coverage >= 40%: 14.0%
OBPI-0.0.67-02: FAIL
    PASS Test files exist: tests/commands/test_skill_alignment_10verbs.py
    PASS Tests pass: 2 tests
    FAIL Coverage >= 40%: 12.0%
OBPI-0.0.67-03: FAIL
    PASS Test files exist: tests/commands/test_obpi_lock_aliases_removed.py
    PASS Tests pass: 3 tests
    FAIL Coverage >= 40%: 12.0%
```

**What the deliverable is:** the **structured, deterministic per-OBPI audit array** itself — one reproducible command emitting per-criterion PASS/FAIL rows. `gz-obpi-reconcile` Phase 1 now consumes this array directly instead of reconstructing the same picture from ad-hoc agent Read/Grep/Bash.

**Reading the coverage FAIL correctly:** Each `FAIL Coverage >= 40%` row is the **expected artifact of the audit's coverage denominator** — `_measure_coverage` (`obpi_audit_cmd.py:289-318`) runs the OBPI's own test files under `coverage run --source=src`, measuring those focused tests against the **entire `src/` tree** as the denominator. A well-scoped OBPI with a focused test file is therefore structurally unable to reach 40% — the percentage is unreachable by construction, not low by accident (the exact mechanism GHI #591 tracks). It is **not** a defect:

- The **suite-level coverage floor passed at Gate 2** (5958–5961 tests green).
- The **authoritative L2 gate, `gz adr audit-check ADR-0.0.67`, PASSES** — that is the source-of-truth verdict, not the per-OBPI scoped percentage.

**Why this matters:** Reconcile reasoning that used to depend on an agent improvising shell reconnaissance is now anchored to a deterministic command whose output is the same every run.

---

## Execution Log

| # | Check | Command | Outcome | Proof |
|---|-------|---------|---------|-------|
| 1 | L2 ledger proof | `gz adr audit-check ADR-0.0.67` | ✓ PASS — all 3 OBPIs completed with evidence | `proofs/audit-check.txt` |
| 2 | Invariant-1 enforcement (core capability) | `gz validate --skill-alignment` | ✓ PASS | `proofs/skill-alignment.txt` |
| 3 | REQ-kind proof channels | `gz validate --req-kind-discipline` | ✓ PASS (fail-closes on any uncovered BEHAVIOR REQ) | `proofs/req-kind-discipline.txt` |
| 4 | Recursion port (C1) | `_known_cli_verb_paths()` enumeration | ✓ PASS — 73 multi-word leaves enumerated; `obpi audit` present, deleted alias absent | `proofs/demo1-recursion-port.txt` |
| 5 | Alias deletion + canonical intact (C4) | `gz obpi lock-claim` / `gz obpi lock list` | ✓ PASS — alias rejected (argparse), canonical works | `proofs/demo2-alias-deleted.txt` |
| 6 | Deterministic audit engine (C3) | `gz obpi audit --adr ADR-0.0.67` | ⚠ Structured array emitted; coverage column FAIL is expected per-OBPI-scoped artifact (see § Shortfalls) | `proofs/demo3-obpi-audit-engine.txt` |
| 7 | Lifecycle (before) | `gz adr report ADR-0.0.67` | ✓ Completed / attested / 3 OBPIs attested_completed | `proofs/adr-report-before.txt` |

---

## Independent Review Synthesis

### spec-reviewer — REQ-tracing — PASS-WITH-CONCERNS

- **8/8 BEHAVIOR REQs** have real semantic `@covers` tests asserting REQ semantics (not string-pins): `test_promoted_advisory_audits.py:302/321/348/381` (01-01..04, incl. a non-vacuous synthetic-verb injection at :321), `test_skill_alignment_10verbs.py:38/55` (02-01), `test_obpi_audit_cmd.py:43/75` (02-03), `test_obpi_withdraw_cmd.py:23/55` (02-04), `test_obpi_lock_aliases_removed.py:19/35/51` (03-01).
- **The 5 `@covers`-uncovered REQs are genuinely SUPPORT-kind** (02-02, 02-05, 02-06, 03-02, 03-03) — confirmed by direct read of the brief Acceptance-Criteria lines. **No BEHAVIOR coverage gap.**
- **Headline wiring is genuine procedural use, not a name-drop:** `gz-obpi-reconcile/SKILL.md:124-152` invokes `gz obpi audit` / `--adr`, `gz obpi emit-receipt`, `gz obpi withdraw` in runnable Phase-1 command blocks. Spot-checked `gz-arb` (`arb ty`) and `gz-status` (`obpi status`) — genuine.
- **`_NO_SKILL_VERBS` scrubbed** of all 10 reclaimed verbs (`cli.py:24-71`).
- **CONCERN (adjudicated below):** the 5 SUPPORT REQ brief lines name an `artifact_edited` ledger event as proof, but no such event exists for the (non-markdown) artifacts — `artifact_edited` only fires for governance markdown. Edits are ledger-witnessed by alternate event types (`agent_sync_completed` line 8986, `task_completed`, `obpi_receipt_emitted` line 8989 "3 SUPPORT grandfathered").

### quality-reviewer — structural coherence — COHERENT-WITH-RISKS

- **Three OBPIs compose into a coherent end-state** regardless of the staged landing order. Integration proved non-vacuously by `test_skill_alignment_10verbs.py:56 test_audit_skill_alignment_clean_on_live_tree` (recursive enumerator over live tree asserts zero skill_alignment errors → transitively proves all 10 wirings visible, no stale waiver, no dangling waiver from deletion).
- **Deletion is clean across all coupled surfaces** (parser, `_NO_SKILL_VERBS`, `doc-coverage.json`, `mkdocs.yml` nav, behave scenario, behave-coverage waiver). **Zero real dangling references** — all `lock-claim|lock-release|lock-status` hits outside the ADR package are legitimate concept/ledger/historical references.
- **Two minor latent risks (non-blocking, future-proofing):**
  1. Waiver-helper asymmetry: `_verb_path_waived` cascades top-level token only, `_waiver_targets_live_verb` matches arbitrary-depth prefix — a future multi-word group key would be deemed live but cascade nothing (latent; no multi-word keys today). `cli.py:195-206`.
  2. Headline schema guard covers command→output axis (`test_obpi_audit_cmd.py` asserts `criteria_evaluated`); the skill-doc "Ledger Schema v1" ↔ `_build_entry` coupling is prose-only.

### Driver adjudication of the spec-reviewer CONCERN — does NOT block VALIDATED

Verified against the runtime surface (`src/gzkit/req_kind.py:182-183, 216-220`): the mechanical enforcer resolves SUPPORT REQs to `proof_status = "advisory-support"` — *"always advisory; ledger query deferred."* Only BEHAVIOR-without-`@covers` is fail-closed (`behavior_uncovered_reqs`); SUPPORT lands in the `grandfathered_reqs` advisory bucket **by design**, which is exactly the "3 SUPPORT grandfathered" language the OBPI-02 completion receipt records. `gz validate --req-kind-discipline` is GREEN. The implemented T2 enforcement does not require a per-REQ `artifact_edited` event; the work is done and structurally verified by both reviewers. **The CONCERN is a genuine doctrine/template gap (ADR-0.0.59 prose + brief template cite an event type that never fires for non-markdown artifacts, while the validator defers the ledger query entirely) — tracked as a GHI, non-blocking.**

---

## Summary Table

| Dimension | Verdict | Basis |
|-----------|---------|-------|
| Completeness | ✓ Complete | 3/3 OBPIs attested_completed; all 3 ADR Decision items landed (recursion port, wire-not-waive, alias deletion) |
| Integrity | ✓ Sound | `skill-alignment` + `req-kind-discipline` green; deletion clean across all coupled surfaces; no dangling references |
| Alignment (code = docs = tests) | ✓ Aligned | 8/8 BEHAVIOR REQs covered; wirings genuine procedural use; demos reproduce claimed behavior |
| Value demonstrated | ✓ Yes | Full-surface enforcement, alias removal, deterministic audit array shown working live |
| Anomalies | ⚠ 1 explained + 1 tracked | per-OBPI coverage FAIL (expected scoped artifact); SUPPORT proof-channel doctrine gap (GHI) |

---

## Shortfalls (Step 5)

| Severity | Shortfall | Disposition |
|----------|-----------|-------------|
| Non-blocking (explained + tracked) | `gz obpi audit --adr` reports per-OBPI coverage FAIL (12–14% < 40%). | **Explained, not a defect.** `_measure_coverage` runs the OBPI's own test files under `coverage run --source=src` — whole-`src/`-tree denominator, so a focused test file is unreachable-by-construction; suite floor passed at Gate 2 (5977 tests this audit); authoritative L2 gate `gz adr audit-check` PASSES. Documented in Feature Demonstration § Capability 3. Already tracked by **GHI #591** (`gz obpi audit` whole-src coverage denominator unreachable for scoped OBPIs). |
| Non-blocking (tracked) | SUPPORT REQ brief template cites `artifact_edited` as the ledger-event proof channel, but that event never fires for non-markdown artifacts AND `req-kind-discipline` defers the SUPPORT ledger query entirely (`req_kind.py:182,218`). The "ledger event + structural validator" doctrine in ADR-0.0.59 is unsatisfiable-as-written for source/config/feature/skill SUPPORT artifacts. | **Routed to existing GHI #543** ("SUPPORT proof channel does regex match only; no actual ledger query runs"). This audit's fresh evidence (5 ADR-0.0.67 SUPPORT REQs witnessed by alternate event types; the non-markdown-artifact wrinkle) added as a comment refining #543's Expected section. No duplicate filed (Step-0 prior-art lookup). |
| Non-blocking (latent) | Waiver-helper asymmetry (`cli.py:195-206`) + prose-only skill-doc schema coupling. | Noted by quality-reviewer; future-proofing, no current defect. Recorded in the #543 comment thread context as related observations. |

No unresolved ✗ failures. No blocking shortfalls.

---

## Evidence Index

- `proofs/audit-check.txt` — L2 ledger proof (PASS)
- `proofs/skill-alignment.txt` — Invariant-1 enforcement (PASS)
- `proofs/req-kind-discipline.txt` — REQ-kind proof channels (PASS)
- `proofs/demo1-recursion-port.txt` — recursion enumeration (C1)
- `proofs/demo2-alias-deleted.txt` — alias deletion + canonical intact (C4)
- `proofs/demo3-obpi-audit-engine.txt` — deterministic audit array (C3)
- `proofs/adr-report-before.txt` — lifecycle state before audit
- `AUDIT_PLAN.md` — claims-to-checks plan

---

## Attestation

**Agent audit attestation (pipeline-orchestrator):** I have verified the ledger proof (L2 `audit-check` PASS), reproduced the key evidence live, dispatched independent spec-reviewer and quality-reviewer personas whose findings are synthesized above, demonstrated the ADR's delivered value with reproducible commands, and adjudicated the single CONCERN as non-blocking with a tracked GHI. All BEHAVIOR REQs are covered; the integration is coherent; no blocking shortfalls remain. The ADR is ready for the operator's audit-validation acceptance (Gate 5).

**Human attestation (Gate 5):** Operator verbal acceptance recorded 2026-06-09 via `gz adr emit-receipt ADR-0.0.67 --event validated`.

- Attestor: g0
- Operator verbatim ack: **"accept audit"**
- Re-verification receipts (fresh, this audit): `arb-step-unittest-0530bd3787984062a79ea7cbe112e1d0` (5977 pass), `arb-ruff-b7640c24bf0846c19fe4c67bcb9d52e6`, `arb-step-typecheck-1f868616e51041248ccd06826203a2a4`, `arb-step-mkdocs-0559dd5f28ac4ec5a5833e09a1c82f1d`
- Date: 2026-06-09
- Lifecycle: COMPLETED → **VALIDATED**
