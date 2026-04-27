# ADR-0.16.0 Closeout Drift — Formal Acknowledgement-of-Historical-Drift

**Audit date:** 2026-04-26
**Subject:** ADR-0.16.0-cms-architecture-formalization (closed, terminal `attested` event 2026-03-20T09:48:11Z)
**Originating GHI:** [#332](https://github.com/tvproductions/gzkit/issues/332)
**Sister audit:** [`adr-0.14.0-closeout-drift-2026-04-26.md`](adr-0.14.0-closeout-drift-2026-04-26.md) (GHI #331)
**Doctrine anchors:** ADR-0.0.33 Agent Control Surface Fidelity (Draft) — Era-1 validators close the class going forward. ADR-0.0.34 Agent Control Surface Rendering Substrate (Draft) — already names ADR-0.16.0 a "partial prior" whose scope it generalizes.
**Remediation chosen:** Formal acknowledgement-of-historical-drift. **Not** re-attestation. **Not** ADR-0.16.0 reopening — its scope is generalized into ADR-0.0.34's eight-component delivery sequence.
**Evidence sources:** `.gzkit/ledger.jsonl` (28 events for ADR-0.16.0 / OBPI-0.16.0-* between 2026-03-15 and 2026-03-20), `docs/design/adr/pre-release/ADR-0.16.0-cms-architecture-formalization/ADR-0.16.0-cms-architecture-formalization.md`, `docs/design/adr/pre-release/ADR-0.16.0-cms-architecture-formalization/ADR-CLOSEOUT-FORM.md`.

## Why acknowledgement, not re-attestation

ADR-0.16.0 was attested, closed, and shipped. The drift named below is on receipts already in the ledger and on a closeout form already on disk. Per `docs/governance/state-doctrine.md` ledger immutability, re-attesting historical brief artifacts after release would overwrite the audit trail the ledger exists to preserve. The GHI #332 acceptance offers two paths and explicitly excludes silent continuation; this artifact is the first path — *acknowledge ADR-0.16.0 as a partial prior whose scope ADR-0.0.34 generalizes*.

ADR-0.0.34 already binds this remediation in its Intent section: it names ADR-0.16.0 a "partial prior" that "shipping a partial prior (Pydantic registry + vendor-aware sync via file copy + lifecycle state machine) without the Jinja2-templated rendering its prose promised". This audit is the historical companion — when ADR-0.0.33's `gz validate --surface-fidelity` runs its first audit sweep against the historical record, this file is the named-instance evidence for ADR-0.16.0.

## Drift rows

### Row 1 — Heavy-lane parent, lite-lane self-closed OBPIs (the canonical GHI #332 signal)

| Field | Value |
|-------|-------|
| Pattern | OBPI completion receipts under `parent_lane: heavy` recorded with `attestation_requirement: optional`, `attestor: agent:claude-code` or `agent:claude`, `obpi_completion: completed` (NOT `attested_completed`), `human_attestation: null` |
| Instance count | 5 of 9 OBPI completion receipt events for OBPI-0.16.0-02..05 |
| Receipts (UTC) | OBPI-03 vendor-manifest-schema 2026-03-18T20:21:52 (agent:claude-code) · OBPI-04 template-engine 2026-03-18T20:46:21 (agent:claude-code) · OBPI-02 rules-as-content 2026-03-19T12:30:17 (agent:claude, re-emission stripped prior human attestation) · OBPI-04 2026-03-19T12:30:23 (agent:claude, re-emission) · OBPI-05 lifecycle 2026-03-19T12:30:30 (agent:claude, re-emission) |
| Comparison | Per `AGENTS.md` § OBPI Acceptance Protocol — Lane & Kind Attestation Matrix, an OBPI inside a heavy-lane parent inherits that lane's attestation rigor regardless of OBPI's own lane. The `attestation_requirement: optional` and `attestor: agent:*` fields on these receipts are exactly the lane-inheritance miss the matrix exists to prevent. The mechanical enforcement at `_requires_human_obpi_attestation` (`src/gzkit/commands/adr_audit.py`) and the TTY + `ATTEST` confirmation gate (GHI #290) closed this vector going forward; ADR-0.16.0's receipts predate the gate. |
| Per-OBPI terminal state | OBPI-01: clean, attested_completed by `human:Jeff` (proper). OBPI-02: terminal receipt is the 2026-03-19T12:30:17 re-emission stripped to `agent:claude` / optional / no human attestation. OBPI-03: only receipt is self-closed lite by `agent:claude-code`. OBPI-04: both receipts are self-closed lite by agent. OBPI-05: terminal receipt is the 2026-03-19T12:30:30 re-emission stripped to `agent:claude`; the prior 2026-03-19T10:22:00 receipt did record `human_attestation: true` but with `obpi_completion: completed` (not `attested_completed`) and `attestation_requirement: optional` — mixed shape, not the matrix-required form. |
| Acknowledgement | Five OBPI completion events under heavy parent landed without the brief-level human attestation the matrix requires. The OBPIs ship as shipped. Going forward: ADR-0.0.33 fidelity validators (Era-1+) plus the `_requires_human_obpi_attestation` gate close this class. The historical record retains the lite-self-close shape per ledger immutability. |

### Row 2 — Dirty-worktree completion receipts (no clean-tree terminal re-emission)

| Field | Value |
|-------|-------|
| Pattern | `evidence.git_sync_state.dirty: true` AND `evidence.recorder_warnings: ["Working tree was dirty when the completion receipt was captured."]` |
| Instance count | 6 of 9 OBPI completion receipt events |
| Per-OBPI distribution | OBPI-02: 2 dirty / 2 total · OBPI-03: 0 / 1 · OBPI-04: 2 / 2 · OBPI-05: 2 / 2 (only OBPI-01 and the single OBPI-03 receipt landed clean) |
| Comparison with ADR-0.14.0 (sister audit Row 1) | ADR-0.14.0 had 18/28 dirty receipts but every OBPI received a clean-tree terminal re-emission on 2026-03-17T09:26-28 (anchor commits cited in sister audit Row 1). ADR-0.16.0's re-emissions on 2026-03-19T12:30 were *also* dirty; no subsequent clean-tree re-emission landed. **Terminal state for OBPIs 02, 04, 05 is dirty.** |
| Status | Unremediated. Unlike ADR-0.14.0, the historical record on ADR-0.16.0 carries `recorder_warnings` as the terminal receipt evidence for three OBPIs. |
| Acknowledgement | The dirty-tree warning is the recorder's honest evidence of the capture context. Re-emitting against the current tree (months later) would falsify that evidence. The terminal-dirty receipts ship as-is. Going forward: `gz git-sync --apply --lint --test` is now mandated before final OBPI completion receipt emission per `AGENTS.md` § OBPI Acceptance Protocol — Pipeline mandate; the gate closes the class. |

### Row 3 — Prose-vs-deliverables: Jinja2 templating substrate undelivered

| Field | Value |
|-------|-------|
| Prose claim (ADR-0.16.0 § Decision, line 93) | *"Implement `.gzkit/rules/` as canonical content: vendor-neutral rule definitions with metadata (path scope, description), **rendered into vendor-specific formats by `gz agent sync`**"* |
| Prose claim (ADR-0.16.0 § Rationale, line 138) | *"models define truth (Pydantic from ADR-0.15.0), the template engine renders views (`gz agent sync`), you never edit rendered output (vendor surfaces)"* |
| Prose claim (ADR-0.16.0 § OBPI table, row 4) | OBPI-0.16.0-04 titled `template-engine`: *"Make gz agent sync vendor-aware; render canonical content to enabled vendor shapes"* |
| What landed | Pydantic content-type registry (OBPI-01) ✓. Rules-as-canonical-content directory (OBPI-02) ✓. Vendor manifest schema (OBPI-03) ✓. Vendor-aware sync via **file copy** (OBPI-04 — the title says "template-engine" but the implementation copies canonical files into vendor mirrors; no Jinja2 templates per (content type × vendor) exist). Lifecycle state machine (OBPI-05) ✓. |
| What did NOT land | Jinja2-templated rendering. The "Django parallel" prose at lines 137-139 promised a template engine; the implementation is file-copy with vendor-enablement gating. The round-trip fidelity contract (`content_model = parse(render(content_model))`) was not enforced because there is no `render()`. |
| Authored capture | ADR-0.0.34 (Agent Control Surface Rendering Substrate) names this gap explicitly in its Intent: *"shipping a partial prior (Pydantic registry + vendor-aware sync via file copy + lifecycle state machine) without the Jinja2-templated rendering its prose promised"*. ADR-0.0.34's eight-component delivery sequence (lines 67-89) is the authored capture; OBPI-0.0.34-01 generalizes ADR-0.16.0 OBPI-01's registry, OBPI-0.0.34-02 lands the rendering pipeline ADR-0.16.0 OBPI-04 was titled for, OBPI-0.0.34-08 expands ADR-0.16.0 OBPI-03's vendor manifest schema. |
| Acknowledgement | ADR-0.16.0 ships as a partial prior. Its scope is generalized into ADR-0.0.34's authored substrate doctrine — not reopened, not re-attested. The OBPI-04 title `template-engine` is preserved in the historical record as evidence of the original aspiration; the deliverable shipped under that title was vendor-aware file copy. |

### Row 4 — ADR-CLOSEOUT-FORM: pre-attestation checklist incomplete and bare-token attestation

| Field | Value |
|-------|-------|
| File | `docs/design/adr/pre-release/ADR-0.16.0-cms-architecture-formalization/ADR-CLOSEOUT-FORM.md` |
| Pattern (checklist) | Line 16 records `- [ ] Code reviewed` unchecked while lines 11-15 are checked. The closeout was attested at 2026-03-20T09:48:11Z anyway. |
| Pattern (verbatim attestation) | § Human Attestation § Verbatim Attestation records the bare token `completed` attested by `Jeff`. Same bare-token shape as ADR-0.14.0 closeout-form (sister audit Row 3) — but with `Jeff` as attestor rather than fixture-shaped `Test User`, so the fixture-leak severity is partial. |
| Internal-consistency note | Line 27 (Gate 4 BDD: `uv run -m behave features/`) is checked while ADR-0.16.0 § Evidence (Four Gates) line 154 declares *"BDD: not applicable (Lite lane)"*. The closeout-form's checked Gate-4 box does not name a feature file or scenario it ran. Heavy-parent + lite-self-closed OBPIs (Row 1) further calls the BDD-N/A premise into question. |
| Status | Closeout-form prose drift from operator-grounded enrichment per `AGENTS.md` § Attestation worked-example. The bare-token verbatim and unchecked Code-reviewed box did not block the closeout sequence. |
| Acknowledgement | The closeout form ships as-is. Going forward: closeout ceremony should refuse to advance with a verbatim attestation that is a single token, and should require `Code reviewed` to be checked or explicitly waived with a reason. The follow-up rule belongs in the `gz-adr-closeout-ceremony` skill, not in this audit. (Same forward binding as sister audit Row 3.) |

## Hypotheses tested vs. landed

| GHI #332 hypothesis | Verdict for ADR-0.16.0 scope |
|---|---|
| ADR's prose claims not all delivered | **Confirmed** (Row 3). Jinja2-templated rendering is the named gap; ADR-0.0.34 is the authored capture of the missing substrate. |
| OBPIs self-closed lite when parent is heavy | **Confirmed** (Row 1). 5 of 9 receipt events under heavy parent recorded `attestation_requirement: optional`, agent attestor, `obpi_completion: completed` (not `attested_completed`). |
| Receipts have dirty-worktree warnings | **Confirmed** (Row 2). 6 of 9 receipts dirty; unlike sister ADR-0.14.0, no clean-tree terminal re-emission landed. Terminal state for OBPIs 02, 04, 05 is dirty. |

## Forward bindings honored by this audit

1. **ADR-0.0.33 first audit sweep cite-target.** The same Evidence-section line 165 that cites the ADR-0.14.0 audit is updated in this patch to cite this file; the deferred-to-#332 marker is replaced with the resolved-by-#332 audit path.
2. **ADR-0.0.34 partial-prior back-pointer.** ADR-0.0.34's Evidence section gains an entry pointing at this audit, paralleling the sister-audit pattern. ADR-0.0.34's Intent already names ADR-0.16.0 a partial prior; the back-pointer makes the audit artifact discoverable from the substrate ADR.
3. **No mechanical re-attestation.** Per the remediation choice, no `gz adr emit-receipt` events are emitted against ADR-0.16.0 or its OBPIs as a result of this audit. The ledger remains immutable; the historical record remains the historical record.
4. **No brief-file or closeout-form rewrites.** The OBPI briefs and the ADR-CLOSEOUT-FORM ship as shipped. Drift acknowledged here.
5. **No ADR-0.16.0 reopening.** Its scope is generalized into ADR-0.0.34's eight-component delivery — that is the live work, not a retroactive ADR-0.16.0 amendment.

## Closure

GHI #332 acceptance criteria — concrete drift rows (Rows 1–4 above), remediation path chosen (acknowledge ADR-0.16.0 as partial prior whose scope ADR-0.0.34 generalizes), evidence captured under `artifacts/audits/`, cross-reference between ADR-0.16.0 and ADR-0.0.34 established (the latter's Intent already names the former; this patch adds the audit back-pointer in ADR-0.0.34 Evidence and resolves the deferred-to-#332 marker in ADR-0.0.33 Evidence) — are satisfied by this artifact + the same-patch ADR-0.0.33 and ADR-0.0.34 Evidence-section updates.

The historical record stands. The doctrine going forward closes the class.
