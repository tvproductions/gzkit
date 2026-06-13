# AUDIT (Gate-5) — ADR-0.0.70

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.70-turn-end-feedback-and-correction-mining |
| ADR Title | Turn-End Feedback and Ground-Truth Correction Mining |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining |
| Audit Date | 2026-06-13 |
| Auditor(s) | g0 (operator, Gate 5) + main-session agent (pipeline-orchestrator) |
| Persona dispatch | spec-reviewer (REQ trace), quality-reviewer (structural coherence) — both PASS |

## Feature Demonstration (Step 3 — MANDATORY)

**What does ADR-0.0.70 deliver?** Four surfaces that place deterministic sensors
at the two boundaries gzkit's existing machinery could not reach — the harness
turn-end, and the un-instrumented ground-truth transcript:

- A **Stop-hook** that runs `ruff` over git-dirty Python at every agent turn end and
  blocks a premature stop with agent-actionable three-part prose (mechanical
  backstop for Behavior Rules Never #5).
- A **read-only transcript miner** that mines operator-correction patterns from
  `~/.claude/projects/` and emits PII-scrubbed candidate proposals — the third feed
  to the advisory-scorecard Promotable→Mechanical ladder.
- A **versioned guardrail-feedback-prose rule** that makes "engineer the failure
  text as the prompt" a binding contract, with the Stop hook as first consumer.
- A **fourth-source doctrine triangulation** recording Buetow's convergence in the
  harness-engineering appraisal + the Magna Carta campaign B.0 amendment.

### Capability 1: Stop-hook turn-end deterministic feedback (OBPI-01)

```text
$ uv run python .claude/hooks/stop-turn-feedback.py --demo
stop-turn-feedback: BLOCKED — turn-end lint check failed across 1 dirty Python file(s).

What failed:
F401 [*] `os` imported but unused
 --> demo_violation.py:1:8
help: Remove unused import: `os`
Found 1 error.

Why this is forbidden: gzkit forbids ending a turn while the cheap deterministic
tier is red (AGENTS.md Behavior Rules — Never #5; ADR-0.0.70 turn-end feedback;
.gzkit/rules/guardrail-feedback-prose.md).

Governed next step: fix the findings above, verify with `uv run ruff check <files>`,
then end the turn. One block per turn — the next stop proceeds even if findings
remain (fail-open).
```

**Why it matters:** The appraisal's #1 named gap — "agents work blind between gate
transitions" — now has its first mechanical sensor at the harness lifecycle, at
hook-script cost. The block prose exhibits all three bar parts (what failed / why
forbidden, cited / governed next step), so the agent self-corrects in-flight with no
human in the loop. Proof: `audit/proofs/demo-01-stop-hook.txt`.

### Capability 2: Session-correction-mining (OBPI-02)

```text
$ uv run python -m gzkit.insights.correction_mining --dry-run
session-correction-mining: 0 cluster(s) at threshold 3 from
  C:\Users\Jeff\.claude\projects\-Users-Jeff-source-repos-va-gzkit
```

**Why it matters:** A read-only stdlib miner now reads the ground truth (the session
transcripts) that no prior sensor touched. `0 clusters` is honest null output —
corrections are lexically distinct in this project's history; the miner writes
nothing in `--dry-run` and confines all writes to its `proofs/` directory by
construction (sha256-keyed filenames, verified by quality-reviewer). Proof:
`audit/proofs/demo-02-mining.txt`.

### Capability 3: Guardrail-feedback-prose rule (OBPI-03)

```text
$ uv run gz validate --unscoped-rules
✓ 22 rule file(s) checked (0 allowlisted).
$ uv run gz validate --advisory-scorecard
✓ All validations passed (1 scopes).
```

**Why it matters:** "Engineer the failure text as the prompt a human would have
typed" stops being folklore and becomes versioned rule `guardrail-feedback-prose.md`
(v0.1.0), classified on the advisory scorecard, with a real enforcement consumer
(Capability 1's hook) shipping in the same ADR. quality-reviewer confirmed the
coupling is test-enforced (REQ-0.0.70-03-02), not nominal. Proof:
`audit/proofs/demo-03-rule-validators.txt`.

### Capability 4: Fourth-source doctrine triangulation (OBPI-04)

```text
$ rg -n "Buetow" docs/governance/harness-engineering-appraisal.md
119:## Fourth Source — Buetow on the Code-Review Bottleneck (practitioner interview)
121:> Source: Florian Buetow (AI engineer, Xebia), interviewed on the Beyond
     Coding Podcast … published 2026-06-10. Companion site: cracking-ai-engineering.com
$ rg -n "B.0 ADR-0.0.70" docs/governance/build-to-1.0-campaign-2026-06-10.md
217:- [ ] B.0 ADR-0.0.70 Buetow adoption (operator-inserted 2026-06-12; see …)
```

**Why it matters:** Four independent practitioner theses converging on gzkit's
existing equilibrium is itself auditable evidence the heavy-harness bet is correct;
the appraisal records it rather than vibing it, and the campaign carries the
operator-verbatim B.0 amendment. Proof: `audit/proofs/demo-04-buetow.txt`.

### Value Summary

Before ADR-0.0.70, gzkit had **no** deterministic sensor at the agent turn boundary
and **no** surface reading the ground-truth transcripts — the two gaps four
practitioner theses independently named. The operator can now: (1) rely on a
turn-end fence that blocks premature "done" on red lint with prompt-grade recovery
text, and (2) mine cross-session operator-correction recurrence into scorecard
candidates — both at stdlib/hook-script cost, both two-way-door reversible.

---

## Execution Log

- ✓ Passed · ✗ Failed · ⚠ Warning (non-blocking)

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| Ledger proof | `uv run gz adr audit-check ADR-0.0.70` | ✓ | PASS; all 4 OBPIs completed with evidence |
| Coverage (blocking) | `uv run gz adr audit-check ADR-0.0.70 --json` | ✓ | `coverage_blocking: []`; 15/15 BEHAVIOR REQs covered |
| Coverage (advisory) | (same) | ⚠ | 10 REQs without `@covers` — all SUPPORT/STRUCTURAL-FENCE; non-blocking (see Recommendations) |
| CLI audit | `uv run gz cli audit` | ✓ | "CLI audit passed. 105/105 commands fully covered." |
| C1 Stop hook | `uv run python .claude/hooks/stop-turn-feedback.py --demo` | ✓ | BLOCKED, three-part prose, exit 0 |
| C2 Miner | `uv run python -m gzkit.insights.correction_mining --dry-run` | ✓ | 0 clusters (honest null), no writes |
| C3 Rule (unscoped) | `uv run gz validate --unscoped-rules` | ✓ | 22 rule files checked |
| C3 Rule (scorecard) | `uv run gz validate --advisory-scorecard` | ✓ | all validations passed |
| C4 Docs | `rg Buetow …` / `rg "B.0 ADR-0.0.70" …` | ✓ | section @ line 119; B.0 @ line 217 |
| Independent spec trace | spec-reviewer subagent | ✓ | 10 flagged REQs = 8 SUPPORT + 2 STRUCTURAL-FENCE; 0 BEHAVIOR uncovered; fences trace to Boundary Invariants 1 / 2&4 |
| Independent structural review | quality-reviewer subagent | ✓ | four surfaces cohere; hook↔rule coupling real; Stop-phase drift-fenced; miner read-only/fail-soft; stdlib-only |

## Dataset Spot Examples

```text
audit-check --json (coverage block):
  "total_reqs": 25, "covered_reqs": 15, "coverage_percent": 60.0,
  "coverage_blocking": []          ← zero blocking coverage gaps
  "coverage_advisory": [ 10 × "REQ not covered by any @covers test annotation" ]

The 10 advisory REQs and their declared (non-@covers) proof channels:
  REQ-0.0.70-01-07  structural-fence → parent ADR Boundary Invariant 1
  REQ-0.0.70-02-06  support          → gz validate --chores-layout + ledger
  REQ-0.0.70-02-07  structural-fence → parent ADR Boundary Invariants 2 & 4
  REQ-0.0.70-03-01  support          → gz validate --unscoped-rules + sync + ledger
  REQ-0.0.70-03-03  support          → gz validate --advisory-scorecard + ledger
  REQ-0.0.70-03-04  support          → ledger + gz validate --unscoped-rules
  REQ-0.0.70-03-05  support          → ledger + gz validate --surfaces
  REQ-0.0.70-03-06  support          → ledger + gz validate --distribution
  REQ-0.0.70-04-01  support          → ledger + gz validate --documents + mkdocs
  REQ-0.0.70-04-02  support          → ledger + gz validate --documents
```

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ All 4 OBPIs `attested_completed`; 4/4 checklist items shipped |
| Data Integrity | ✓ Ledger proof PASS; `coverage_blocking: []`; CLI audit 105/105 |
| Performance Stability | ✓ Hook sub-2s lint tier, fails open on timeout; miner fail-soft |
| Documentation Alignment | ✓ Appraisal Buetow section + campaign B.0 landed; rule scorecard-classified |
| Risk Items Resolved | ✓ 60%-figure resolved (non-BEHAVIOR artifact); 1 info-level forward-hardening noted |

## Evidence Index

- `audit/proofs/audit-check.json` — ledger proof + coverage (Layer 2)
- `audit/proofs/cli-audit.txt` — CLI doc coverage
- `audit/proofs/demo-01-stop-hook.txt` — Stop-hook `--demo` block prose
- `audit/proofs/demo-02-mining.txt` — miner `--dry-run` cluster summary
- `audit/proofs/demo-03-rule-validators.txt` — rule validators green
- `audit/proofs/demo-04-buetow.txt` — Buetow appraisal section + campaign B.0
- Independent reviews: spec-reviewer (REQ trace, PASS) + quality-reviewer
  (structural coherence, PASS) — verdicts recorded in the audit conversation.

## Recommendations

- **Advisory (non-blocking) — the 60% covers-figure is not a gap.** All 10
  `@covers`-uncovered REQs are 8 SUPPORT + 2 STRUCTURAL-FENCE that prove via their
  correct ADR-0.0.59 channels (ledger event + structural validator; parent-ADR
  Boundary Invariants). `behavior_uncovered_reqs=0`; `coverage_blocking: []`.
  Authoring a `@covers` test for a SUPPORT REQ would be the named anti-pattern.
  **Remedy:** none required.
- **Info (forward-hardening, out of ADR-0.0.70 scope) — miner has no negative-signal
  telemetry.** quality-reviewer noted the miner's `CORRECTIVE_MARKERS` lexicon is the
  most decay-prone seam: a stale lexicon yields zero proposals indistinguishable from
  a healthy run, and — unlike the Stop hook, whose block telemetry is wired to
  `.gzkit/sensors/` — the miner leaves no observable trace when it mines nothing. The
  ADR scoped telemetry to the hook only, so this is a forward enhancement, not a
  shortfall in delivered scope. **Remedy:** surface to operator; candidate for a
  future hardening GHI/OBPI (miner run-telemetry), not a Gate-5 blocker.
- **No blocking issues found.**

## Attestation

I/we attest that ADR-0.0.70 is implemented as intended, evidence is reproducible,
and no blocking discrepancies remain.

- **Agent (pipeline-orchestrator):** Audit ceremony executed end-to-end. Ledger
  proof PASS; all four capabilities demonstrated live; two independent persona
  reviews returned PASS; the sole advisory is a non-blocking REQ-counting artifact.
  Fresh validation receipts generated at emit time (foundation receipt-binding
  gate): `arb-ruff-ed38ddd7aa464dcc8b35627a66dd61f6`,
  `arb-step-typecheck-d83e71329cfa4bb386a902a4bfaf1576`,
  `arb-step-unittest-483ae14cc2a84a05b606b16dcf2fb153` (6097 tests, OK skipped=1),
  `arb-step-mkdocs-fbec5b2ab68c4c94b0ecec962f136a00` — all exit 0. — 2026-06-13
- **Operator (g0):** **"accept audit"** (2026-06-13). Verbal Gate-5
  audit-validation acceptance relayed into the `validated` receipt
  (`gz adr emit-receipt … --event validated`); lifecycle confirmed `Validated`
  via `gz adr report ADR-0.0.70`.

Signed: _agent: pipeline-orchestrator, 2026-06-13 / operator: g0, "accept audit", 2026-06-13_
