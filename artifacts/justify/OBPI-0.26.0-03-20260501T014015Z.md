---
anchor_id: OBPI-0.26.0-03
anchor_kind: obpi
generated_at: 2026-05-01T01:40:15.376809+00:00
scaffold_version: 1.0
---

# Walkthrough: OBPI-0.26.0-03

## 1. What I see (the problem)

**Prompt:** *What did I observe that motivates this change? What hurts if nothing happens?*

**Evidence:**

- OBPI-0.26.0-03-adr-recon
- OBPI-0.26.0-03
- ADR-0.26.0

The parent ADR-0.26.0 mandates a 12-module subtraction-test pass over `../airlineops/src/opsdev/lib/`: every reusable governance primitive in opsdev gets one of three outcomes (Absorb / Confirm / Exclude), with the bookkeeping forced into one OBPI per module so per-module rationale survives audit. The brief's Cross-Reference Matrix row for `adr_recon.py` (607 lines) declares "no gzkit equivalent" and tags it as a "Strong absorption candidate unless reconciliation logic is ops-specific" (ADR-0.26.0 line 28, 32). The OBPI brief narrows the decision space further: "No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path" (OBPI-0.26.0-03 line 38, mirrored verbatim from the OBPI-02 sibling at line 42 of OBPI-0.26.0-02). The hurt of doing nothing is doctrinal drift — a reusable governance primitive stranded in opsdev would violate the subtraction test the ADR is built to enforce.

## 2. Per-instance severity

**Prompt:** *How bad is each occurrence? One incident, a pattern, or a class of failure?*

**Evidence:**

- ADR-0.26.0 OBPI Decomposition table (lines 161-172) — 12 module-decision instances, each Heavy lane.
- OBPI-0.26.0-02-references (Completed, decision Exclude) and OBPI-0.26.0-01-adr-management (Completed) — sibling precedents establish the comparison pattern.
- ADR-0.26.0 execution warning (lines 178-183): "OBPIs 01–03 are decision units first, not guaranteed single execution chunks."

This is one instance of a class — the 12-module decision sweep. Each instance carries doctrinal-drift risk if the comparison is shortcut (the failure mode the ADR's Anti-Pattern Warning at lines 65-67 explicitly names: "assuming gzkit's monolithic cli.py already covers what these focused modules provide"). Per-instance severity is Heavy because (a) the decision binds the subtraction-test verdict for adr_recon permanently, (b) Absorb decisions create runtime / CLI surface change, (c) Exclude decisions still bind future companion-absorption work to not re-open the question without new evidence (Long-Term Validity Guard at ADR lines 266-268).

## 3. Why this scope

**Prompt:** *Why is the change boundary drawn here and not wider or narrower?*

**Evidence:**

- ADR-0.26.0 Alternatives Considered table (lines 127-132) — single-mega-OBPI and grouped-domain alternatives explicitly rejected for "hide per-module rationale" and "stronger modules masking weaker ones".
- OBPI-0.26.0-03 Allowed Paths (lines 56-58): `src/gzkit/`, `tests/`, the ADR's own folder.
- ADR execution warning (lines 178-183): "If comparison shows that Absorb requires substantial implementation or broad refactoring, split the absorb path into follow-on execution units/tasks before code changes rather than forcing one brief to carry the full comparison-plus-implementation load."

Scope is one module (`adr_recon.py`, 607 lines) compared against the gzkit reconciliation surface, with the decision artifact landing in this brief. Wider scope (bundling 03 with 04 governance or 05 ledger-schema) was the rejected alternative at ADR lines 127-132. Narrower scope (skip the side-by-side and infer from filename) was the rejected alternative at line 131-132. If the decision is Absorb, this brief records the decision only — implementation gets a follow-on OBPI per the execution warning. If the decision is Exclude, this brief is the entire deliverable.

## 4. What it proposes

**Prompt:** *In one paragraph, what is the change?*

**Evidence:**

- OBPI-0.26.0-03 Requirements (lines 46-52): read both implementations, document comparison, record decision, adapt or document why excluded.
- OBPI-0.26.0-02-references Comparison + Decision sections (lines 152-262) — the canonical pattern this brief will mirror.
- Plan file `.claude/plans/obpi-0.26.0-03-adr-recon-plan.md` Steps 3-7.

Read all 607 lines of opsdev `lib/adr_recon.py`; audit gzkit's reconciliation surface (governance/trust_audits/reconcile.py, governance/adr_status_index.py, governance/frontmatter_coherence.py, commands/frontmatter_reconcile.py, commands/obpi_precomplete.py, commands/obpi_stages.py, ledger_semantics.py); render a dimension-by-dimension comparison table in the brief covering feature completeness, error handling, cross-platform robustness, test coverage, fit with gzkit conventions; record one final decision (Absorb or Exclude) with concrete line-anchored rationale per REQ-01..05; fix the `briefs/` → `obpis/` path drift in the brief's Verification section (the same drift OBPI-02 fixed). No `pyproject.toml` edits, no opsdev edits, no new dependencies introduced as a side-effect.

## 5. Routing decision

**Prompt:** *Direct fix, OBPI ceremony, or new ADR? Cite the threshold that routed it.*

**Evidence:**

- AGENTS.md § Defect-fix routing thresholds — "Crosses ADR or active-OBPI brief boundaries" → OBPI ceremony required.
- ADR-0.26.0 Feature Checklist row 3 (lines 83-84): pre-existing OBPI book reservation.
- OBPI-0.26.0-03 brief already exists at `obpis/` and is `status: Pending` (line 5).

OBPI ceremony, not direct fix. The work is part of the planned 12-module subtraction-test sweep declared by ADR-0.26.0 — by definition it is feature work, not in-flight defect closure. The OBPI brief was authored as part of the ADR's WBS (line 163 in the OBPI Decomposition table); this run is the planned execution of that brief, not a discovery during another brief's implementation. The Heavy lane and Heavy parent ADR force Gates 1-5 including Gate 5 human attestation. Direct-fix thresholds (≤10 source lines, ≤2 source files, ≥3 fix(...) precedents in 60 days) are inapplicable: the comparison-and-decision artifact alone is hundreds of lines of brief prose; there are zero recent fix(...) commits in the 60-day window (`gh issue list` returned 0 open GHIs and the ARB precedent count cached at 0).

## 6. Why this design is right-sized

**Prompt:** *Why isn't this bigger or smaller? What does this shape defend against?*

**Evidence:**

- ADR-0.26.0 Alternatives Considered table (lines 127-132).
- ADR-0.26.0 execution warning (lines 178-183).
- ADR-0.26.0 Scope Creep Guardrails (lines 234-246): "If a comparison exposes a larger architectural redesign beyond the target module, split that redesign into a follow-on ADR or OBPI…"
- OBPI-0.26.0-02-references closing argument (lines 343-374): the proven shape of an Exclude outcome — brief-only, no `src/gzkit/` change, no tests.

This brief is exactly one module's decision. Bigger (bundle with 04 governance + 05 ledger-schema) hides per-module rationale and is the explicit rejected alternative. Smaller (decide from filename or matrix row alone) violates the ADR's anti-pattern warning at lines 65-67 ("blindly copying opsdev code without adapting … Equally bad: assuming gzkit … already covers"). The shape defends against (a) doctrine-drift through under-reading, (b) absorption-as-cargo-cult through over-eager Absorb, (c) implementation-bundling through the execution-warning split rule, and (d) silent scope-creep through the explicit Scope Creep Guardrails.

## 7. What convinces me (evidence)

**Prompt:** *Which rules, ledger events, and commits ground this decision?*

**Evidence:**

- ADR-0.26.0 status: Pending; OBPI Decomposition table marks 03 as `Pending`.
- OBPI-0.26.0-02-references status: Completed; decision Exclude with five-point rationale; ledger event `obpi_completed` at the parent ADR's audit ledger.
- gzkit reconciliation surface grep — 22 files in src/gzkit/ contain "reconcile" or "reconciliation"; specific dedicated modules are governance/trust_audits/reconcile.py, governance/adr_status_index.py, governance/frontmatter_coherence.py, commands/frontmatter_reconcile.py, commands/obpi_precomplete.py, commands/obpi_stages.py, ledger_semantics.py.
- AGENTS.md § PRIME DIRECTIVE invariant 1 (Coupled-surface coherence): producer-side completion without re-running the consumer's check is incomplete work — applies if Absorb pulls in a module whose ledger schema doesn't match gzkit's main ledger.
- AGENTS.md § STDLIB-FIRST DOCTRINE: a new dependency requires named rationale; opsdev `adr_recon.py` imports `airlineops.paths.subpaths` and `opsdev.lib.ledger_schema` — both ops-internal — meaning Absorb implies inheriting two upstream absorption obligations (paths + ledger-schema OBPI-0.26.0-05) before adr_recon can land cleanly.

The decisive grounding is the gzkit-side reconciliation surface inventory: the brief's "no equivalent" assertion conflicts with the codebase. Until the dimension-by-dimension comparison reads both surfaces, the decision direction is undetermined; that is the legitimate residual uncertainty captured in section 8.

## 8. Residual uncertainty

**Prompt:** *What am I not sure about? What would change my mind?*

**Evidence:**

- _[No evidence in gathered sources]_ — section ground requires reading opsdev source, which is Stage 2 work.

Three open questions remain after Stage 1:

1. **Ledger-shape compatibility.** Opsdev's adr_recon reads from `docs/design/adr/{adr-series}/{adr-folder}/logs/obpi-audit.jsonl` (per-ADR audit ledger). gzkit uses a single root `.gzkit/ledger.jsonl` plus `_audit.jsonl` files per ADR (per OBPI-0.0.21 and ADR-0.0.10 storage tiers). If opsdev's per-ADR format and consumption pattern is materially different from gzkit's existing `gz obpi reconcile` and `governance/trust_audits/reconcile.py`, that is an Absorb signal. If gzkit already reconciles equivalently from `_audit.jsonl`, that is an Exclude signal.
2. **Drift-detection capability gap.** Opsdev's `DriftReport` dataclass enumerates drift between table state and ledger state. gzkit's `frontmatter_coherence.py` checks frontmatter coherence; `governance/adr_status_index.py` regenerates an index; `validate --reconcile-freshness` fails-open on zero-event history (per AGENTS.md Architectural Boundary 4). The question is whether opsdev surfaces drift the gzkit chain misses.
3. **Test coverage delta.** Whether opsdev's tests for adr_recon (in `../airlineops/tests/`) cover semantics gzkit's reconciliation tests don't already cover (the gzkit test surface is `tests/governance/test_*.py` and `tests/commands/test_*.py`).

Reading opsdev `lib/adr_recon.py` end-to-end and gzkit's reconciliation modules during Stage 2 resolves all three questions; the dimension table in the brief makes them addressable cell-by-cell.

What would change my mind: if opsdev's `ReconResult` and `DriftReport` produce strictly more drift signals than gzkit's combined reconciliation chain (with concrete examples), the decision tilts Absorb (with implementation deferred per the ADR execution warning). If they overlap or gzkit produces a strict superset, the decision tilts Exclude with a five-point rationale mirroring OBPI-02's pattern.
