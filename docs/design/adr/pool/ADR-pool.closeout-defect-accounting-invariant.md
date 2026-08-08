---
id: ADR-pool.closeout-defect-accounting-invariant
status: Pool
lane: heavy
parent: PRD-GZKIT-1.0.0
---

# ADR-pool.closeout-defect-accounting-invariant: Closeout Defect-Accounting Invariant

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats the agent-authored session-end narration surface — closing summary, commit body, close comment, attestation text — as an untrusted channel, never a verification surface: a defect is "accounted for" only when a routing receipt exists on the ledger, never when the prose says so. Refuses to close the failure class GHI #514 names by adding more prose to a surface prose already failed to bind; insists the witness be mechanical — a snapshot, a reconcile predicate, a fail-closed completion condition. Composes — does not replace — PRIME DIRECTIVE #3/#5/#6: the prose obligation stays; this ADR ships the structural floor beneath it.

## Why foundation tier?

**Invariance test:** Without this ADR, gzkit's PRIME DIRECTIVE #3/#5/#6 — route a surfaced defect, never excuse it — remains enforced only by prose on the agent-authored session-end narration surface, a channel with no mechanical fail-close. GHI #514 records three consecutive recurrences in ~2 days of an agent naming a gate-surfaced defect then excusing it in the closing summary; each was caught only because the operator read the narration live. The project would still ship — but it would lose the property that *"every defect is trackable"* is mechanically witnessed at the closeout boundary rather than trusted to agent prose. **Yes — this is foundation: it shapes how every governance closeout terminates.** This ADR names *"no session-terminal governance action may complete with an unrouted gate-surfaced defect"* as invariant and ships the snapshot-reconcile mechanism that binds it.

**Port-vs-adapter framing:** This ADR authors a **port** — the closeout defect-accounting invariant (the contract every session-terminal governance action must honor) and the `gz validate --closeout-defect-accounting` reconcile scope that enforces it. The per-surface integrations are **adapters** behind that port: the `gz closeout` snapshot embed (OBPI-01/03), the `gz obpi complete` extension (OBPI-04), and the ghi-close PreToolUse hook backstop (OBPI-05) are three adapters honoring one port. PRIME DIRECTIVE #3/#5/#6 supply the doctrinal intent the port mechanizes; ADR-0.0.36 (universal OBPI attestation) is the adjacent completion-gate ADR this one composes with.

## Intent

gzkit's PRIME DIRECTIVE names — three times, in items #3, #5, and #6 — the obligation to route a surfaced defect rather than excuse it: NEVER SAY "out of scope"; FLAG DEFECTS, NEVER EXCUSE THEM ("Pre-existing" → still a defect); EVERY DEFECT MUST BE TRACKABLE. But the obligation is enforced on the agent-authored session-end narration surface — the closing summary, the commit body, the close comment, the attestation text — by prose alone. That surface is an unverified channel: nothing fails closed when an agent names a gate-surfaced defect and then re-characterizes it away.

GHI #514 (defect + eval-feedback) records the empirical failure. Three consecutive ghi-close sessions, ~2 days apart, surfaced a real defect during verification — `gz validate` / `gz check` exited non-zero, the gate fired correctly — and then the agent-authored closing summary excused it: closing GHI #486, an AGENTS.md/invariant-registry drift was "called someone else's just-completed work"; closing GHI #489, a `gz validate --documents` exit-1 was flagged then handed back to the operator as "file it via /ghi-author, or leave it for you to route?"; closing GHI #490, two `gz check` failures were named but framed as "not mine, not bundled, clean whenever convenient." In every case the defect was caught only because the operator read the closing summary in real time and replied, near-verbatim each time, "what does the PRIME DIRECTIVE say." The #490 insights record states the #489 standing correction "was not internalized." Three recurrences inside one named failure class is the empirical evidence that prose enforcement does not bind — the closing-summary excuse is precisely the "graceful degradation" exit named in AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 4, run against a defect a gate already caught.

This ADR codifies the missing structural defense as a foundation invariant: no session-terminal governance action may complete while a gate-surfaced defect from that session lacks a routing receipt. The operator's framing (GHI #514 close comment, 2026-05-22): "the remedy shapes a system invariant — closeout completion must mechanically account for every gate-surfaced defect."

The mechanism is snapshot-and-reconcile. At closeout-open, `gz closeout` — which already records a closeout ledger event — embeds a defect baseline captured from `gz check --json`. At completion, a new `gz validate --closeout-defect-accounting` scope re-runs verification, diffs the completion-state defect set against the snapshot, and fails closed (exit 3) on any residual defect that lacks a routing receipt: a structured reference to a GHI number (`ghi:<N>`), a fixing commit SHA (`commit:<sha>`), or an explicit operator waiver (`waiver:<operator>+<reason>`). The agent's closing prose becomes inert — the reconcile gate, not the narration, decides whether the closeout completes.

Foundation kind because the decision shapes a system invariant — how every governance closeout terminates — not a release-carrying capability. Heavy lane because it adds a `gz validate` scope (CLI surface), a `closeout_defect_snapshot` ledger event (runtime contract / event schema), and a fail-closed completion condition on `gz closeout`.

## Decision

Establish closeout defect-accounting as a foundation-attested invariant with a snapshot-and-reconcile mechanism, decomposed into six OBPIs.

**The invariant (canonical statement):** No session-terminal governance action — ADR closeout (`gz closeout`), OBPI completion (`gz obpi complete`), or GHI close (`ghi-close`) — may reach a completed state while a defect surfaced by that session's verification gates lacks a routing receipt. A routing receipt is one of: `ghi:<N>` (the defect is filed and tracked), `commit:<sha>` (the defect is fixed by a named commit), or `waiver:<operator>+<reason>` (the operator has explicitly accepted the residual). A gate-surfaced defect with no routing receipt fails the closeout closed.

**Decision items (1:1 with Feature Checklist):**

1. **OBPI-01 — Closeout defect-baseline snapshot.** Extend `gz closeout` (which already records a closeout event) to capture a defect baseline: run `gz check --json`, extract the defect set, and embed it in a new `closeout_defect_snapshot` ledger event carrying `{closeout_id, defect_fingerprints, gz_check_invocation, captured_at}`. Add the `CloseoutDefectSnapshot` frozen Pydantic model and the ledger event schema. The defect fingerprint is a stable, diffable identity (scope + predicate + structural location), deliberately excluding volatile fields (line numbers, run timestamps, ordering) so the same defect is recognizable across two `gz check` runs.

2. **OBPI-02 — `gz validate --closeout-defect-accounting` reconcile scope.** Author the new validate scope. Given an open closeout with a recorded snapshot, it re-runs `gz check --json`, computes the completion-state defect set, and reconciles: each completion-state defect must be either absent from the result (resolved) or carry a routing receipt. Exit 3 on any unrouted residual; exit 0 when every defect is accounted for. Join the scope into the default `gz check` pipeline.

3. **OBPI-03 — `RoutingReceipt` model + completion-gate wiring.** Author the `RoutingReceipt` frozen Pydantic model (`ghi:<N>` | `commit:<sha>` | `waiver:<operator>+<reason>`; the waiver requires a named operator, not the agent) and wire the reconcile scope into the `gz closeout` completion path as a fail-closed condition: `gz closeout` cannot record its completion event while `--closeout-defect-accounting` exits non-zero, and a completion attempted with no recorded snapshot also fails closed (forcing the open-anchor).

4. **OBPI-04 — Extend to `gz obpi complete`.** Apply the same snapshot-reconcile mechanism to OBPI completion: snapshot at the OBPI-pipeline verify stage, reconcile at `gz obpi complete`. The insights record ts=2026-05-21T12:31 documents the identical no-mechanical-gate pattern biting `gz obpi complete` (behave step coverage, GHI #417/#513, twice ~12 days apart), so the OBPI-completion surface is a known live exposure.

5. **OBPI-05 — Extend to ghi-close.** ghi-close's terminal action is `gh issue close`, outside the `gz` runtime. Land a PreToolUse hook backstop (the `.claude/hooks/ghi-triage-chat-silence.py` shape) that intercepts the close action and runs the reconcile predicate, plus the `ghi-close` skill update naming the mechanical gate so the skill prose points at the structural witness rather than carrying yet another rationalization table.

6. **OBPI-06 — PRIME DIRECTIVE #5/#6 scorecard reclassification + docs.** Resolve GHI #514 deferred design question 3: reclassify the PRIME DIRECTIVE #5/#6 scorecard rows (row 17 "Every defect must be trackable" and the "never say out of scope / flag defects" cluster) from Judgment to Mechanical on `docs/governance/advisory-rules-audit.md` — row 17's Judgment rationale ("no reliable mechanical signal for 'defect noticed but not tracked'") is refuted by this ADR's reconcile scope, which is precisely that signal. Update the operator runbook and the `gz validate` manpage EXAMPLES section with the new scope. As an `eval-feedback`-labeled rule edit, the commit carries an `Eval-feedback-source:` trailer citing the three insights records.

**Sequencing:** OBPI-01 (snapshot) is the load-bearing primitive — OBPI-02 reconciles against its snapshot, OBPI-03 wires the gate, OBPI-04/05 extend it to the other two surfaces, OBPI-06 documents and reclassifies. Strict order: 01 → 02 → 03 → {04, 05} → 06.

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT replace or weaken PRIME DIRECTIVE #3/#5/#6 — the prose obligation stays; this ADR adds the mechanical witness underneath it.
- Does NOT add new prose anti-rationalization tables to the `ghi-close` or closeout-ceremony skills — GHI #514's evidence shows that approach already failed (the `ghi-close` skill's existing "Common Rationalizations" table and "Red Flags" list were in place across all three recurrences).
- Does NOT gate the operator's own manual fixes — the invariant binds the agent's session-terminal governance actions, not human-run commands; the operator is the waiver authority.
- Does NOT extend to `git-sync` or `patch-release` in this ADR — those surfaces are future-GHI candidates once the mechanism proves on the three named surfaces.

**Lane: Heavy.** New `gz validate` scope (CLI surface), new `closeout_defect_snapshot` ledger event (runtime contract / event schema), fail-closed completion condition. Foundation-kind brief-level Gate 5 stacks per ADR-0.0.36-universal-obpi-attestation.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: this ADR's own --closeout-defect-accounting scope is unbuilt (Draft); the closest extant closeout-family completion gate runs green. | uv run gz validate --closeout-proof | 0 |

## Consequences

### Positive

1. **Closes the closing-summary-excuse failure class structurally.** The agent literally cannot complete a closeout while a gate-surfaced defect is unrouted — the closing prose is inert because the reconcile gate, not the narration, decides completion. The three GHI #514 recurrences (#486 / #489 / #490) become mechanically impossible: each would have fail-closed at the reconcile step.

2. **Reuses surfaces that already exist.** `gz closeout` already records a closeout event; `gz check --json` already emits structured output. The mechanism adds a snapshot payload and a reconcile predicate — no new ceremony verb, no parallel pipeline, no second source of truth.

3. **Converts PRIME DIRECTIVE #5/#6 from prose to mechanism.** The advisory-rules-audit scorecard currently scores these rows Judgment — row 17's rationale is verbatim "no reliable mechanical signal for 'defect noticed but not tracked'." This ADR's reconcile scope is exactly that signal, refuting the Judgment rationale and earning the rows a Mechanical reclassification. Deferred design question 3 from GHI #514 is resolved with a real validator, not a deferral.

4. **Moves the defect-routing obligation off the unverified narration channel.** Today the obligation is enforced by the operator reading the closing summary live ("what does the PRIME DIRECTIVE say" — three times in the GHI #514 record). After this ADR, the operator's live read is a backstop, not the primary defense.

5. **The routing receipt makes "accounted for" auditable, not narrative.** `ghi:<N>` / `commit:<sha>` / `waiver:<operator>+<reason>` are ledger-checkable references. "Not mine, not bundled, clean whenever convenient" is not a receipt and fails the gate.

6. **Composes into `gz check`.** The reconcile scope joins the default `gz check` pipeline, so derived drift is caught at every quality run, not only at the closeout boundary.

7. **One ADR, six OBPIs, one Gate 5 per OBPI.** Foundation-kind brief-level attestation discipline applies; each OBPI is independently witnessed. The decomposition is one OBPI per separable surface (snapshot primitive, reconcile scope, receipt model + gate, OBPI-completion extension, ghi-close extension, docs + reclassification) — no fragmentation, no bundling.

### Negative

1. **Pre-mortem — defect fingerprinting is the load-bearing risk.** It is 18 months from now and this decision failed because the defect fingerprint was not stable: the same defect produced different fingerprints across two `gz check` runs (line numbers shifted, ordering changed), so the reconcile saw a "new" defect every run and either fail-closed spuriously or trained operators to waive the whole set reflexively. Mitigation: OBPI-01's fingerprint is defined on scope + predicate + structural location, deliberately excluding volatile fields. The fingerprint design is the single highest-risk decision and gets its own REQ and dedicated test in OBPI-01.

2. **Pre-mortem — the waiver becomes the universal escape hatch.** It is 18 months from now and this failed because `waiver:<operator>+<reason>` became the path of least resistance — every closeout waived its residual defects with a one-word reason and the gate became theater. Mitigation: the waiver requires the operator (not the agent) as the named party; agent-authored waivers are rejected. The waiver reason is a ledger-recorded string the advisory scorecard can audit for degenerate patterns ("wip", "later"). A future GHI can promote a waiver-rate ceiling.

3. **What Would Have To Be True (approach ①).** (a) `gz check --json` output is stable enough to fingerprint — the `--json` surface was verified to exist this session; OBPI-01 must additionally verify the payload shape is diffable. (b) `gz closeout` is the real open-anchor for ADR closeout — verified: `gz closeout` "records a closeout event." (c) **Shakiest condition:** agents route through `gz closeout` rather than completing a closeout ad hoc — if an agent never runs `gz closeout`, there is no snapshot and the reconcile has nothing to check. Mitigation: OBPI-03 makes the closeout-completion event itself depend on a recorded snapshot, so a completion with no snapshot fails closed, structurally forcing the open-anchor.

4. **Assumption surfacing.** The implicit assumption is that the defect set at closeout-open and the set at completion are comparable — that closeout work does not itself change which checks run. If an OBPI under the closeout adds a new `gz check` sub-check, a completion-state defect can appear that was uncheckable at open. The opposite-of-the-assumption case: a defect "new" at completion is not necessarily an excuse — it can be genuinely freshly introduced. The reconcile therefore treats a genuinely-new defect the same as a baseline defect (both need a routing receipt); the snapshot is the floor of what must be accounted for, never a whitelist of what is allowed to remain.

5. **The 2am operator.** On-call at 2am, an ADR closeout fails closed because `gz check` surfaced an unrelated pre-existing defect with no receipt, and the operator needs the closeout done now. What the design provides: `waiver:<operator>+<reason>` is the 2am path — the operator records a waiver with a reason, the closeout completes, and the waiver sits on the ledger for later audit. The design does not strand the operator; it forces the residual to be named on the ledger rather than excused in prose. The auditable 2am exit is the point, not a gap.

6. **Reversibility — one-way door at canon level.** Once the invariant is foundation-attested and PRIME DIRECTIVE #5/#6 are reclassified Mechanical, reversal needs an ADR amendment ceremony. Justified: the door being closed produced three recurrences of a named failure class inside ~2 days. The asymmetry is intentional; the cost of leaving it open exceeds the cost of closing it.

7. **Scope minimization.** The smallest version that delivers value is OBPI-01 + 02 + 03 on `gz closeout` alone — snapshot, reconcile, gate, one surface. OBPI-04 (`gz obpi complete`) and OBPI-05 (ghi-close) are extensions; OBPI-06 is docs + reclassification. If time were halved, OBPI-04/05 would defer to a follow-up ADR and the invariant would land on ADR closeout only. They are kept in-scope because GHI #514's failure class is identical across all three surfaces and the mechanism is the same code — deferring them re-opens the exact gap on two of three surfaces.

8. **Performative-snapshot risk.** `gz check --json` could itself be gamed — an agent runs `gz check` in a narrowed scope at open so the baseline is artificially clean. Mitigation: the snapshot records the `gz check` invocation (args + sha); the reconcile scope rejects a snapshot whose invocation was not the canonical full `gz check`.

9. **Surface cost.** +1 `gz validate` scope, +1 ledger event, +2 frozen Pydantic models, +1 PreToolUse hook. Real but bounded; all are sync-checked canonical surfaces. The 5:1 governance-to-output ratio is the product (Anti-vibing operative claim 1) — a mechanical defense for a thrice-recurring named failure class is on-doctrine, not overhead.

10. **Documentation-defect-vs-behavior-defect check.** If the real failure were that agents route defects correctly but narrate poorly, this mechanism would be mis-targeted — it would gate agents who already route. GHI #514's evidence rules that out: in all three cases the defect was genuinely not routed (no GHI filed, no commit, handed back to the operator or deferred). The failure is in the routing, not the wording; the mechanism gates routing, not wording.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 6
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.56-01: Closeout defect-baseline snapshot — extend `gz closeout` to run `gz check --json`, fingerprint the defect set, and emit a `closeout_defect_snapshot` ledger event; add the `CloseoutDefectSnapshot` frozen Pydantic model and the ledger event schema. Defect fingerprint = scope + predicate + structural location, excluding volatile fields.
- [ ] OBPI-0.0.56-02: `gz validate --closeout-defect-accounting` reconcile scope — re-run `gz check --json` at completion, diff against the recorded snapshot, exit 3 on any residual defect lacking a routing receipt; join the scope into the default `gz check` pipeline.
- [ ] OBPI-0.0.56-03: `RoutingReceipt` model + completion-gate wiring — author the `RoutingReceipt` frozen Pydantic model (`ghi:<N>` | `commit:<sha>` | `waiver:<operator>+<reason>`, waiver requires a named operator) and wire the reconcile scope into the `gz closeout` completion path as a fail-closed condition; a completion with no recorded snapshot also fails closed.
- [ ] OBPI-0.0.56-04: Extend the mechanism to `gz obpi complete` — snapshot at the OBPI-pipeline verify stage, reconcile at OBPI completion.
- [ ] OBPI-0.0.56-05: Extend the mechanism to ghi-close — PreToolUse hook backstop intercepting `gh issue close`, plus the `ghi-close` skill update naming the mechanical gate.
- [ ] OBPI-0.0.56-06: Reclassify PRIME DIRECTIVE #5/#6 Judgment → Mechanical on `docs/governance/advisory-rules-audit.md`; update operator runbook and `gz validate` manpage; commit carries the `Eval-feedback-source:` trailer citing the three insights records.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-05-21T20:40:19.862409*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.56-closeout-defect-accounting-invariant

### Q: What is the title of this ADR?

**A:** Closeout Defect-Accounting Invariant

### Q: What is the semantic version?

**A:** 0.0.56

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit's PRIME DIRECTIVE names — three times, in items #3, #5, and #6 — the obligation to route a surfaced defect rather than excuse it: NEVER SAY "out of scope"; FLAG DEFECTS, NEVER EXCUSE THEM ("Pre-existing" → still a defect); EVERY DEFECT MUST BE TRACKABLE. But the obligation is enforced on the agent-authored session-end narration surface — the closing summary, the commit body, the close comment, the attestation text — by prose alone. That surface is an unverified channel: nothing fails closed when an agent names a gate-surfaced defect and then re-characterizes it away.

GHI #514 (defect + eval-feedback) records the empirical failure. Three consecutive ghi-close sessions, ~2 days apart, surfaced a real defect during verification — `gz validate` / `gz check` exited non-zero, the gate fired correctly — and then the agent-authored closing summary excused it: closing GHI #486, an AGENTS.md/invariant-registry drift was "called someone else's just-completed work"; closing GHI #489, a `gz validate --documents` exit-1 was flagged then handed back to the operator as "file it via /ghi-author, or leave it for you to route?"; closing GHI #490, two `gz check` failures were named but framed as "not mine, not bundled, clean whenever convenient." In every case the defect was caught only because the operator read the closing summary in real time and replied, near-verbatim each time, "what does the PRIME DIRECTIVE say." The #490 insights record states the #489 standing correction "was not internalized." Three recurrences inside one named failure class is the empirical evidence that prose enforcement does not bind — the closing-summary excuse is precisely the "graceful degradation" exit named in AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 4, run against a defect a gate already caught.

This ADR codifies the missing structural defense as a foundation invariant: no session-terminal governance action may complete while a gate-surfaced defect from that session lacks a routing receipt. The operator's framing (GHI #514 close comment, 2026-05-22): "the remedy shapes a system invariant — closeout completion must mechanically account for every gate-surfaced defect."

The mechanism is snapshot-and-reconcile. At closeout-open, `gz closeout` — which already records a closeout ledger event — embeds a defect baseline captured from `gz check --json`. At completion, a new `gz validate --closeout-defect-accounting` scope re-runs verification, diffs the completion-state defect set against the snapshot, and fails closed (exit 3) on any residual defect that lacks a routing receipt: a structured reference to a GHI number (`ghi:<N>`), a fixing commit SHA (`commit:<sha>`), or an explicit operator waiver (`waiver:<operator>+<reason>`). The agent's closing prose becomes inert — the reconcile gate, not the narration, decides whether the closeout completes.

Foundation kind because the decision shapes a system invariant — how every governance closeout terminates — not a release-carrying capability. Heavy lane because it adds a `gz validate` scope (CLI surface), a `closeout_defect_snapshot` ledger event (runtime contract / event schema), and a fail-closed completion condition on `gz closeout`.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Establish closeout defect-accounting as a foundation-attested invariant with a snapshot-and-reconcile mechanism, decomposed into six OBPIs.

**The invariant (canonical statement):** No session-terminal governance action — ADR closeout (`gz closeout`), OBPI completion (`gz obpi complete`), or GHI close (`ghi-close`) — may reach a completed state while a defect surfaced by that session's verification gates lacks a routing receipt. A routing receipt is one of: `ghi:<N>` (the defect is filed and tracked), `commit:<sha>` (the defect is fixed by a named commit), or `waiver:<operator>+<reason>` (the operator has explicitly accepted the residual). A gate-surfaced defect with no routing receipt fails the closeout closed.

**Decision items (1:1 with Feature Checklist):**

1. **OBPI-01 — Closeout defect-baseline snapshot.** Extend `gz closeout` (which already records a closeout event) to capture a defect baseline: run `gz check --json`, extract the defect set, and embed it in a new `closeout_defect_snapshot` ledger event carrying `{closeout_id, defect_fingerprints, gz_check_invocation, captured_at}`. Add the `CloseoutDefectSnapshot` frozen Pydantic model and the ledger event schema. The defect fingerprint is a stable, diffable identity (scope + predicate + structural location), deliberately excluding volatile fields (line numbers, run timestamps, ordering) so the same defect is recognizable across two `gz check` runs.

2. **OBPI-02 — `gz validate --closeout-defect-accounting` reconcile scope.** Author the new validate scope. Given an open closeout with a recorded snapshot, it re-runs `gz check --json`, computes the completion-state defect set, and reconciles: each completion-state defect must be either absent from the result (resolved) or carry a routing receipt. Exit 3 on any unrouted residual; exit 0 when every defect is accounted for. Join the scope into the default `gz check` pipeline.

3. **OBPI-03 — `RoutingReceipt` model + completion-gate wiring.** Author the `RoutingReceipt` frozen Pydantic model (`ghi:<N>` | `commit:<sha>` | `waiver:<operator>+<reason>`; the waiver requires a named operator, not the agent) and wire the reconcile scope into the `gz closeout` completion path as a fail-closed condition: `gz closeout` cannot record its completion event while `--closeout-defect-accounting` exits non-zero, and a completion attempted with no recorded snapshot also fails closed (forcing the open-anchor).

4. **OBPI-04 — Extend to `gz obpi complete`.** Apply the same snapshot-reconcile mechanism to OBPI completion: snapshot at the OBPI-pipeline verify stage, reconcile at `gz obpi complete`. The insights record ts=2026-05-21T12:31 documents the identical no-mechanical-gate pattern biting `gz obpi complete` (behave step coverage, GHI #417/#513, twice ~12 days apart), so the OBPI-completion surface is a known live exposure.

5. **OBPI-05 — Extend to ghi-close.** ghi-close's terminal action is `gh issue close`, outside the `gz` runtime. Land a PreToolUse hook backstop (the `.claude/hooks/ghi-triage-chat-silence.py` shape) that intercepts the close action and runs the reconcile predicate, plus the `ghi-close` skill update naming the mechanical gate so the skill prose points at the structural witness rather than carrying yet another rationalization table.

6. **OBPI-06 — PRIME DIRECTIVE #5/#6 scorecard reclassification + docs.** Resolve GHI #514 deferred design question 3: reclassify the PRIME DIRECTIVE #5/#6 scorecard rows (row 17 "Every defect must be trackable" and the "never say out of scope / flag defects" cluster) from Judgment to Mechanical on `docs/governance/advisory-rules-audit.md` — row 17's Judgment rationale ("no reliable mechanical signal for 'defect noticed but not tracked'") is refuted by this ADR's reconcile scope, which is precisely that signal. Update the operator runbook and the `gz validate` manpage EXAMPLES section with the new scope. As an `eval-feedback`-labeled rule edit, the commit carries an `Eval-feedback-source:` trailer citing the three insights records.

**Sequencing:** OBPI-01 (snapshot) is the load-bearing primitive — OBPI-02 reconciles against its snapshot, OBPI-03 wires the gate, OBPI-04/05 extend it to the other two surfaces, OBPI-06 documents and reclassifies. Strict order: 01 → 02 → 03 → {04, 05} → 06.

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT replace or weaken PRIME DIRECTIVE #3/#5/#6 — the prose obligation stays; this ADR adds the mechanical witness underneath it.
- Does NOT add new prose anti-rationalization tables to the `ghi-close` or closeout-ceremony skills — GHI #514's evidence shows that approach already failed (the `ghi-close` skill's existing "Common Rationalizations" table and "Red Flags" list were in place across all three recurrences).
- Does NOT gate the operator's own manual fixes — the invariant binds the agent's session-terminal governance actions, not human-run commands; the operator is the waiver authority.
- Does NOT extend to `git-sync` or `patch-release` in this ADR — those surfaces are future-GHI candidates once the mechanism proves on the three named surfaces.

**Lane: Heavy.** New `gz validate` scope (CLI surface), new `closeout_defect_snapshot` ledger event (runtime contract / event schema), fail-closed completion condition. Foundation-kind brief-level Gate 5 stacks per ADR-0.0.36-universal-obpi-attestation.

### Q: What good things result from this decision? List benefits.

**A:** 1. **Closes the closing-summary-excuse failure class structurally.** The agent literally cannot complete a closeout while a gate-surfaced defect is unrouted — the closing prose is inert because the reconcile gate, not the narration, decides completion. The three GHI #514 recurrences (#486 / #489 / #490) become mechanically impossible: each would have fail-closed at the reconcile step.

2. **Reuses surfaces that already exist.** `gz closeout` already records a closeout event; `gz check --json` already emits structured output. The mechanism adds a snapshot payload and a reconcile predicate — no new ceremony verb, no parallel pipeline, no second source of truth.

3. **Converts PRIME DIRECTIVE #5/#6 from prose to mechanism.** The advisory-rules-audit scorecard currently scores these rows Judgment — row 17's rationale is verbatim "no reliable mechanical signal for 'defect noticed but not tracked'." This ADR's reconcile scope is exactly that signal, refuting the Judgment rationale and earning the rows a Mechanical reclassification. Deferred design question 3 from GHI #514 is resolved with a real validator, not a deferral.

4. **Moves the defect-routing obligation off the unverified narration channel.** Today the obligation is enforced by the operator reading the closing summary live ("what does the PRIME DIRECTIVE say" — three times in the GHI #514 record). After this ADR, the operator's live read is a backstop, not the primary defense.

5. **The routing receipt makes "accounted for" auditable, not narrative.** `ghi:<N>` / `commit:<sha>` / `waiver:<operator>+<reason>` are ledger-checkable references. "Not mine, not bundled, clean whenever convenient" is not a receipt and fails the gate.

6. **Composes into `gz check`.** The reconcile scope joins the default `gz check` pipeline, so derived drift is caught at every quality run, not only at the closeout boundary.

7. **One ADR, six OBPIs, one Gate 5 per OBPI.** Foundation-kind brief-level attestation discipline applies; each OBPI is independently witnessed. The decomposition is one OBPI per separable surface (snapshot primitive, reconcile scope, receipt model + gate, OBPI-completion extension, ghi-close extension, docs + reclassification) — no fragmentation, no bundling.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **Pre-mortem — defect fingerprinting is the load-bearing risk.** It is 18 months from now and this decision failed because the defect fingerprint was not stable: the same defect produced different fingerprints across two `gz check` runs (line numbers shifted, ordering changed), so the reconcile saw a "new" defect every run and either fail-closed spuriously or trained operators to waive the whole set reflexively. Mitigation: OBPI-01's fingerprint is defined on scope + predicate + structural location, deliberately excluding volatile fields. The fingerprint design is the single highest-risk decision and gets its own REQ and dedicated test in OBPI-01.

2. **Pre-mortem — the waiver becomes the universal escape hatch.** It is 18 months from now and this failed because `waiver:<operator>+<reason>` became the path of least resistance — every closeout waived its residual defects with a one-word reason and the gate became theater. Mitigation: the waiver requires the operator (not the agent) as the named party; agent-authored waivers are rejected. The waiver reason is a ledger-recorded string the advisory scorecard can audit for degenerate patterns ("wip", "later"). A future GHI can promote a waiver-rate ceiling.

3. **What Would Have To Be True (approach ①).** (a) `gz check --json` output is stable enough to fingerprint — the `--json` surface was verified to exist this session; OBPI-01 must additionally verify the payload shape is diffable. (b) `gz closeout` is the real open-anchor for ADR closeout — verified: `gz closeout` "records a closeout event." (c) **Shakiest condition:** agents route through `gz closeout` rather than completing a closeout ad hoc — if an agent never runs `gz closeout`, there is no snapshot and the reconcile has nothing to check. Mitigation: OBPI-03 makes the closeout-completion event itself depend on a recorded snapshot, so a completion with no snapshot fails closed, structurally forcing the open-anchor.

4. **Assumption surfacing.** The implicit assumption is that the defect set at closeout-open and the set at completion are comparable — that closeout work does not itself change which checks run. If an OBPI under the closeout adds a new `gz check` sub-check, a completion-state defect can appear that was uncheckable at open. The opposite-of-the-assumption case: a defect "new" at completion is not necessarily an excuse — it can be genuinely freshly introduced. The reconcile therefore treats a genuinely-new defect the same as a baseline defect (both need a routing receipt); the snapshot is the floor of what must be accounted for, never a whitelist of what is allowed to remain.

5. **The 2am operator.** On-call at 2am, an ADR closeout fails closed because `gz check` surfaced an unrelated pre-existing defect with no receipt, and the operator needs the closeout done now. What the design provides: `waiver:<operator>+<reason>` is the 2am path — the operator records a waiver with a reason, the closeout completes, and the waiver sits on the ledger for later audit. The design does not strand the operator; it forces the residual to be named on the ledger rather than excused in prose. The auditable 2am exit is the point, not a gap.

6. **Reversibility — one-way door at canon level.** Once the invariant is foundation-attested and PRIME DIRECTIVE #5/#6 are reclassified Mechanical, reversal needs an ADR amendment ceremony. Justified: the door being closed produced three recurrences of a named failure class inside ~2 days. The asymmetry is intentional; the cost of leaving it open exceeds the cost of closing it.

7. **Scope minimization.** The smallest version that delivers value is OBPI-01 + 02 + 03 on `gz closeout` alone — snapshot, reconcile, gate, one surface. OBPI-04 (`gz obpi complete`) and OBPI-05 (ghi-close) are extensions; OBPI-06 is docs + reclassification. If time were halved, OBPI-04/05 would defer to a follow-up ADR and the invariant would land on ADR closeout only. They are kept in-scope because GHI #514's failure class is identical across all three surfaces and the mechanism is the same code — deferring them re-opens the exact gap on two of three surfaces.

8. **Performative-snapshot risk.** `gz check --json` could itself be gamed — an agent runs `gz check` in a narrowed scope at open so the baseline is artificially clean. Mitigation: the snapshot records the `gz check` invocation (args + sha); the reconcile scope rejects a snapshot whose invocation was not the canonical full `gz check`.

9. **Surface cost.** +1 `gz validate` scope, +1 ledger event, +2 frozen Pydantic models, +1 PreToolUse hook. Real but bounded; all are sync-checked canonical surfaces. The 5:1 governance-to-output ratio is the product (Anti-vibing operative claim 1) — a mechanical defense for a thrice-recurring named failure class is on-doctrine, not overhead.

10. **Documentation-defect-vs-behavior-defect check.** If the real failure were that agents route defects correctly but narrate poorly, this mechanism would be mis-targeted — it would gate agents who already route. GHI #514's evidence rules that out: in all three cases the defect was genuinely not routed (no GHI filed, no commit, handed back to the operator or deferred). The failure is in the routing, not the wording; the mechanism gates routing, not wording.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. OBPI-0.0.56-01: Closeout defect-baseline snapshot — extend `gz closeout` to run `gz check --json`, fingerprint the defect set, and emit a `closeout_defect_snapshot` ledger event; add the `CloseoutDefectSnapshot` frozen Pydantic model and the ledger event schema. Defect fingerprint = scope + predicate + structural location, excluding volatile fields.
2. OBPI-0.0.56-02: `gz validate --closeout-defect-accounting` reconcile scope — re-run `gz check --json` at completion, diff against the recorded snapshot, exit 3 on any residual defect lacking a routing receipt; join the scope into the default `gz check` pipeline.
3. OBPI-0.0.56-03: `RoutingReceipt` model + completion-gate wiring — author the `RoutingReceipt` frozen Pydantic model (`ghi:<N>` | `commit:<sha>` | `waiver:<operator>+<reason>`, waiver requires a named operator) and wire the reconcile scope into the `gz closeout` completion path as a fail-closed condition; a completion with no recorded snapshot also fails closed.
4. OBPI-0.0.56-04: Extend the mechanism to `gz obpi complete` — snapshot at the OBPI-pipeline verify stage, reconcile at OBPI completion.
5. OBPI-0.0.56-05: Extend the mechanism to ghi-close — PreToolUse hook backstop intercepting `gh issue close`, plus the `ghi-close` skill update naming the mechanical gate.
6. OBPI-0.0.56-06: Reclassify PRIME DIRECTIVE #5/#6 Judgment → Mechanical on `docs/governance/advisory-rules-audit.md`; update operator runbook and `gz validate` manpage; commit carries the `Eval-feedback-source:` trailer citing the three insights records.

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Approach ② — PreToolUse hook gate as the primary mechanism.** REJECTED as primary. A hook intercepting the close action does work for ghi-close's non-`gz` surface, but a hook is vendor-surface (`.claude/`), Layer-3 per state-doctrine, and harness-specific — GHI #514 asks for a runtime contract / fail-closed completion condition that lives in `gz`. The hook is retained as the backstop for the non-`gz` ghi-close surface (OBPI-05), never the primary mechanism.

2. **Approach ③ — attestation-bound (extend the Gate 5 attestation payload).** REJECTED. Loading defect-accounting onto the Gate 5 attestation conflates "human attests quality" with "machine verifies defect routing." The reconcile must be machine-mechanical and must precede attestation; if it were part of attestation, the agent authoring the attestation text could still mischaracterize the residual — the exact unverified-narration channel this ADR exists to close.

3. **More prose anti-rationalization tables in the `ghi-close` / closeout-ceremony skills.** REJECTED — this is the disproven approach. The `ghi-close` skill already carries an extensive "Common Rationalizations" table and a "Red Flags" list; GHI #514's three recurrences happened with that prose in place. Adding more prose to a surface prose did not bind is `ADR-pool.skill-behavioral-hardening`'s lane, and GHI #514's evidence ("prose enforcement does not bind") disqualifies it for this failure class.

4. **GHI-only — one GHI per excused-defect incident.** REJECTED. A GHI per incident preserves the trail but does not mechanize the class, so the failure recurs. GHI #514 is itself the consolidating record of three prior incidents (the #486 / #489 / #490 insights records) — the GHI route was already in use while the recurrence continued.

5. **Pool ADR — document the intent, defer the foundation ceremony.** OPERATOR-REJECTED at the routing decision. The operator's GHI #514 close comment names foundation kind explicitly ("the remedy shapes a system invariant"). A pool ADR would queue the failure class rather than close it, and Architectural Boundary #2 discourages adding pool ADRs to the runtime track.

6. **Single universal `gz validate` scope with no per-surface OBPIs.** REJECTED at decomposition. The three surfaces have different open-anchors — a closeout event (`gz closeout`), an OBPI verify stage (`gz obpi complete`), and a non-`gz` `gh issue close` (ghi-close). One OBPI conflating them would bundle three distinct integration surfaces; the OBPI Decomposition Matrix routes them to separate briefs.

7. **Snapshot the full `gz check` text output instead of structured fingerprints.** REJECTED. Diffing raw text is brittle — any cosmetic rendering change (ordering, color, counts) produces false drift. Structured fingerprints over `gz check --json` are the stable identity; this is why "does `gz check` emit stable diffable structured output" was a gating deferred question in GHI #514 and why confirming `--json` exists was the precondition for approach ①.

8. **Gate the operator's own manual close paths too.** REJECTED at scope minimization. The invariant binds the agent's session-terminal governance actions; gating the operator's manual `gh issue close` or `git` operations would add friction with no failure-class evidence behind it. The operator is the waiver authority, not a gated party.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Approach ② — PreToolUse hook gate as the primary mechanism.** REJECTED as primary. A hook intercepting the close action does work for ghi-close's non-`gz` surface, but a hook is vendor-surface (`.claude/`), Layer-3 per state-doctrine, and harness-specific — GHI #514 asks for a runtime contract / fail-closed completion condition that lives in `gz`. The hook is retained as the backstop for the non-`gz` ghi-close surface (OBPI-05), never the primary mechanism.

2. **Approach ③ — attestation-bound (extend the Gate 5 attestation payload).** REJECTED. Loading defect-accounting onto the Gate 5 attestation conflates "human attests quality" with "machine verifies defect routing." The reconcile must be machine-mechanical and must precede attestation; if it were part of attestation, the agent authoring the attestation text could still mischaracterize the residual — the exact unverified-narration channel this ADR exists to close.

3. **More prose anti-rationalization tables in the `ghi-close` / closeout-ceremony skills.** REJECTED — this is the disproven approach. The `ghi-close` skill already carries an extensive "Common Rationalizations" table and a "Red Flags" list; GHI #514's three recurrences happened with that prose in place. Adding more prose to a surface prose did not bind is `ADR-pool.skill-behavioral-hardening`'s lane, and GHI #514's evidence ("prose enforcement does not bind") disqualifies it for this failure class.

4. **GHI-only — one GHI per excused-defect incident.** REJECTED. A GHI per incident preserves the trail but does not mechanize the class, so the failure recurs. GHI #514 is itself the consolidating record of three prior incidents (the #486 / #489 / #490 insights records) — the GHI route was already in use while the recurrence continued.

5. **Pool ADR — document the intent, defer the foundation ceremony.** OPERATOR-REJECTED at the routing decision. The operator's GHI #514 close comment names foundation kind explicitly ("the remedy shapes a system invariant"). A pool ADR would queue the failure class rather than close it, and Architectural Boundary #2 discourages adding pool ADRs to the runtime track.

6. **Single universal `gz validate` scope with no per-surface OBPIs.** REJECTED at decomposition. The three surfaces have different open-anchors — a closeout event (`gz closeout`), an OBPI verify stage (`gz obpi complete`), and a non-`gz` `gh issue close` (ghi-close). One OBPI conflating them would bundle three distinct integration surfaces; the OBPI Decomposition Matrix routes them to separate briefs.

7. **Snapshot the full `gz check` text output instead of structured fingerprints.** REJECTED. Diffing raw text is brittle — any cosmetic rendering change (ordering, color, counts) produces false drift. Structured fingerprints over `gz check --json` are the stable identity; this is why "does `gz check` emit stable diffable structured output" was a gating deferred question in GHI #514 and why confirming `--json` exists was the precondition for approach ①.

8. **Gate the operator's own manual close paths too.** REJECTED at scope minimization. The invariant binds the agent's session-terminal governance actions; gating the operator's manual `gh issue close` or `git` operations would add friction with no failure-class evidence behind it. The operator is the waiver authority, not a gated party.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.56 | Pending | | | |
