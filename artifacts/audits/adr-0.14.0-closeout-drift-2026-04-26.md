# ADR-0.14.0 Closeout Drift — Formal Acknowledgement-of-Historical-Drift

**Audit date:** 2026-04-26
**Subject:** ADR-0.14.0-multi-agent-instruction-architecture-unification (closed, v0.14.0 released 2026-03-17)
**Originating GHI:** [#331](https://github.com/tvproductions/gzkit/issues/331)
**Doctrine anchor:** ADR-0.0.33 Agent Control Surface Fidelity (Draft) — D2 framing: doctrine names the failure class, audit names the historical instances.
**Remediation chosen:** Formal acknowledgement-of-historical-drift. **Not** re-attestation.
**Evidence sources:** `.gzkit/ledger.jsonl` (28 OBPI completion receipt events), `docs/design/adr/pre-release/ADR-0.14.0-multi-agent-instruction-architecture-unification/ADR-CLOSEOUT-FORM.md`, OBPI brief frontmatter under same directory.

## Why acknowledgement, not re-attestation

ADR-0.14.0 was attested, closed, and released as v0.14.0 on 2026-03-17. The drift named below is on receipts already in the ledger and on a closeout form already shipped. Re-attesting historical brief artifacts after release would be revisionist — it would overwrite the audit trail the ledger exists to preserve. The GHI #331 acceptance offers two paths and explicitly excludes silent continuation; this artifact is the second path.

ADR-0.0.33's Era-1 validators (`gz validate --bullet-retention`, `--surface-weight`, `--pointer-anchors`, `--scenario-reachability`, composite `--surface-fidelity`) are forward-looking. They guard *future* surfaces from this class of drift. This audit is the historical companion: when those validators run their first audit sweep against the historical record, they cite this file as the named-instance evidence for ADR-0.14.0.

## Drift rows

### Row 1 — Dirty-worktree completion receipts

| Field | Value |
|-------|-------|
| Instance count | 18 of 28 OBPI completion receipt events for OBPI-0.14.0-01..06 |
| Pattern | `evidence.git_sync_state.dirty: true` AND `evidence.recorder_warnings: ["Working tree was dirty when the completion receipt was captured."]` |
| Per-OBPI distribution | 01: 2 dirty / 4 total · 02: 3/5 · 03: 2/4 · 04: 3/4 · 05: 5/7 · 06: 3/4 |
| Status | Remediated by re-emission. Every OBPI's *terminal* completion receipt has `dirty: false` and empty `recorder_warnings`. The historical receipts retain the warning per ledger immutability. |
| Receipt timestamps (terminal clean) | 01: 2026-03-17T09:26:17 · 02: 2026-03-17T09:27:22 · 03: 2026-03-17T09:27:49 · 04: 2026-03-17T09:28:10 · 05: 2026-03-17T09:28:32 · 06: 2026-03-17T09:28:54 |
| Anchor commits (terminal) | 01: `8f1b081` · 02: `9f5665b` · 03: `8434c37` · 04: `b34c99c` · 05: `855a196` · 06: `ef10286` |
| Acknowledgement | Each OBPI has at least one clean-tree completion receipt as its terminal record; the dirty receipts are preserved for audit lineage but were superseded by clean re-emissions before closeout. |

### Row 2 — Brief-file Human Attestation sections null or incomplete

| Field | Value |
|-------|-------|
| Instance count | 4 of 6 OBPIs (briefs 02, 03, 04, 06) |
| Pattern | Closeout audit-row evidence (`closeout_initiated` event, 2026-03-17T09:29:16) reports `human_attestation.valid: false` for these briefs. Three variants: `present: false` (02, 04); `present: true, attestor: null, attestation_text: null, date: null` (03, 06). |
| Layer comparison | Layer 2 (ledger receipts) records `attestor: human:jeff`, `attestation_text` non-empty, `human_attestation: true`. Layer 1 (brief file Human Attestation section) drifted to null/missing for these four. |
| Reflection issues recorded in ledger | "brief human attestation section is missing or incomplete" — present on rows 02, 03, 04, 06; absent on rows 01 and 05. |
| Status | Drift between Layer 1 (brief canon) and Layer 2 (ledger receipt) at brief-level Gate 5 attestation. Per `state-doctrine.md`: ledger is source-of-truth for the *attestation event*; brief canon is source-of-truth for *brief frontmatter*. The brief Human Attestation prose section is documentary. The mechanical drift is real but the binding fact (the attestation event) is recorded. |
| Acknowledgement | Brief-file attestation prose drift is a Layer-1-vs-Layer-2 documentation gap, not a missing attestation event. Going forward, ADR-0.0.33's Era-2+ pointer/bullet validators (and any successor brief-attestation completeness check) should fail-close on this class. For ADR-0.14.0, the briefs ship as shipped. |

### Row 3 — ADR-CLOSEOUT-FORM attested by "Test User"

| Field | Value |
|-------|-------|
| File | `docs/design/adr/pre-release/ADR-0.14.0-multi-agent-instruction-architecture-unification/ADR-CLOSEOUT-FORM.md` |
| Pattern | `## Human Attestation` § `### Verbatim Attestation` records `completed` (single token) attested by `Test User` at `2026-03-17T09:30:20Z`. The closeout-initiated ledger event records `by: "Test User"`. |
| Comparison | OBPI-level closeout receipts at the same timestamps record `attestor: human:jeff`. The closeout-form attestor and the OBPI-level attestor diverge. |
| Status | The closeout form's attestor field is fixture-shaped (literal string "Test User") and the verbatim attestation text is the bare token "completed" — both characteristic of automation-scaffolded closeout that did not receive a human walkthrough rewrite. |
| Acknowledgement | The closeout form ships as-is. Going forward: closeout ceremony should refuse to advance with `Test User` as the attestor field and should require a verbatim attestation with operator-grounded enrichment per `AGENTS.md` § Attestation. The follow-up rule belongs in the closeout-ceremony skill, not in this audit. |

## Hypotheses tested vs. landed

| GHI #331 hypothesis | Verdict for ADR-0.14.0 scope |
|---|---|
| Heavy-lane parent with at least one OBPI self-closed at lite-lane | **Not present.** All six OBPI-0.14.0-* completion receipts record `attestation_requirement: required`, `obpi_completion: attested_completed`, and a human attestor. The "self-closed lite-lane" instance pattern manifests in ADR-0.16.0 OBPI-03 (where `attestation_requirement: optional`, `attestor: agent:claude-code`, `obpi_completion: completed`) and is the proper subject of GHI #332. |
| Brief-level Gate-5 attestation missing where matrix requires it | **Present in documentary form** (Row 2). The ledger receipts record the attestation event; the brief-file Human Attestation prose sections drifted to null/missing in 4 of 6 briefs. |
| Completion receipt(s) captured against a dirty worktree | **Present** (Row 1). 18 of 28 receipt events. Remediated by clean-tree terminal re-emission for all six OBPIs. |

## Companion finding (out of #331 scope, recorded for cross-reference)

The "self-closed at lite-lane" pattern named in the GHI body, while not present in ADR-0.14.0, is present in:

- **ADR-0.16.0 OBPI-0.16.0-03-vendor-manifest-schema** — receipt at 2026-03-18T20:21:52 records `parent_lane: heavy`, `attestation_requirement: optional`, `attestor: agent:claude-code`, `obpi_completion: completed` (not `attested_completed`). Tracked under [GHI #332](https://github.com/tvproductions/gzkit/issues/332).

This audit does not enumerate ADR-0.16.0 drift further — that is #332's scope.

## Forward bindings honored by this audit

1. **ADR-0.0.33 first audit sweep cite-target.** When `gz validate --surface-fidelity` runs its first audit sweep against the historical record, the named-instance file for ADR-0.14.0 is this audit. ADR-0.0.33's Evidence section adds a back-pointer to this artifact in the same patch as this file.
2. **No mechanical re-attestation.** Per the remediation choice, no `gz adr emit-receipt` events are emitted against ADR-0.14.0 or its OBPIs as a result of this audit. The ledger remains immutable; the historical record remains the historical record.
3. **No brief-file rewrites.** The four briefs with null/incomplete Human Attestation sections (02, 03, 04, 06) are not retroactively edited. The drift is acknowledged here.

## Closure

GHI #331 acceptance criteria — concrete drift rows (Rows 1–3 above), remediation path chosen (formal acknowledgement-of-historical-drift, not silent continuation, not re-attestation), evidence captured under `artifacts/audits/`, listed in ADR-0.0.33's first-audit-sweep cite-target via back-pointer added to ADR-0.0.33 Evidence — are satisfied by this artifact + the same-patch ADR-0.0.33 Evidence-section update.

The historical record stands. The doctrine going forward closes the class.
