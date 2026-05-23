# AUDIT_PLAN — ADR-0.0.57-foundation-adr-nominal-id-triage

**Audit date:** 2026-05-23
**Driver persona:** `pipeline-orchestrator`
**Layer:** L2 (consumes ledger proof; re-verifies only where evidence drifts)
**Lifecycle on entry:** Completed (attested 2026-05-23T15:54:28Z)
**Lane:** heavy
**Kind:** foundation

## Persona dispatch (procedural note)

The skill's Persona Dispatch table requires `spec-reviewer`, `quality-reviewer`, and `narrator` to run as independent subagents. The available tool surface in this session does not expose a Task/Agent dispatch tool. The driver therefore executes each lens in-line and labels each finding with the persona it was produced under (`[spec-reviewer]`, `[quality-reviewer]`, `[narrator]`). Surfacing this constraint rather than papering it over — per AGENTS.md § Prime Directive #5 (flag defects, never excuse them). Non-blocking; recorded as a procedural shortfall (S-02 below).

## Claims extracted from ADR prose

The Decision section makes three claims:

- **C-1** Foundation ADR IDs (0.0.x) third component is a nominal integer — unique identifier, not sequence position.
- **C-2** `gz-adr-create`'s minor-version odometer is replaced by a next-free-integer (gap-fill) nominal allocator.
- **C-3** A `gz-foundation-triage` on-demand skill ranks the in-flight foundation backlog using insights/GHI/invariant signals; diagnosis only, ephemeral.

Plus one rule-scope claim:

- **C-4** The CLAUDE.md/AGENTS.md 'order versioned identifiers semantically' rule scope shrinks to feature ADRs only.

## Checks

| # | Claim | Check | Evidence file |
|---|---|---|---|
| 1 | C-1 | ADR-0.0.17 + ADR-0.0.18 carry the dated amendment block; `trust_audits.py` records the sequence-position audit | `proofs/demo-capability.txt` (Capability 5); REQ-0.0.57-01-04 + REQ-0.0.57-01-03 covered |
| 2 | C-1 | AGENTS.md ordering counter-rule for foundation IDs present, citing ADR-0.0.57 § Decision item 1 + 3 | `proofs/demo-capability.txt` (Capability 6) |
| 3 | C-2 | `_next_free_nominal_foundation_id` returns lowest unused integer on sparse, contiguous, and empty corpora | `proofs/demo-capability.txt` (Capability 2) |
| 4 | C-2 | `gz validate --taxonomy` passes on real (contiguous) corpus without asserting sequence-position | `proofs/demo-capability.txt` (Capability 3) |
| 5 | C-3 | `gz-foundation-triage` skill registered and discoverable via `gz skill list` | `proofs/demo-capability.txt` (Capability 4) |
| 6 | C-3 | Triage script exposes `--format {json,rank}` operator surface and gathers in-flight foundations | `proofs/triage-step1.json` |
| 7 | C-3 | OBPI-04 rubric module lands as canonical structured-rubric (per OBPI-04 attestation: EvidenceRef adapter, 20/20 OBPI-scoped tests) | OBPI-04 ledger entry, `logs/obpi-audit.jsonl` |
| 8 | C-4 | OBPI-05 docs+manpage+runbook reflect nominal allocator + Foundation Triage invocation | `docs/user/manpages/plan-create.md`, `docs/user/runbook.md` § Foundation Triage, `docs/governance/governance_runbook.md` § Foundation Triage |
| 9 | Ledger proof | `uv run gz adr audit-check ADR-0.0.57` PASS, all 5 OBPIs attested_completed | `proofs/audit-check.txt` |
| 10 | Governance hygiene | `uv run gz cli audit` PASS (101/101 commands covered) | `proofs/cli-audit.txt` |

## Risk focus

- **R-1** Foundation backlog may "accumulate if triage is not run regularly" (ADR Consequences Negative #4) — Foundation Triage must actually work end-to-end, not just be present as a skill body.
- **R-2** "Tools that assume foundation IDs are ordered may break silently" (ADR Consequences Negative #3) — `gz validate --taxonomy` audit landed under REQ-01-03 via `trust_audits.py`; that's the structural defense.
- **R-3** Historical navigation becomes date-based (Consequences Negative #1) — outside the audit's verification scope.

## Value-demonstration plan (Step 3)

Run six product-surface demonstrations capturing live output, framed by the operator value each delivers — composed under `narrator` lens:

1. The corpus itself (nominal sparse-set capable shape)
2. Allocator gap-fill behavior under synthetic sparse, contiguous, and empty corpora
3. Taxonomy validator passes without sequence-position assumption
4. Skill registration via `gz skill list`
5. Doctrine amendment landed in ADR-0.0.17/18 + trust_audits.py
6. AGENTS.md counter-rule present

## Outstanding work the audit will NOT do

- Per AGENTS.md § Prime Directive #6, defects found are flagged and routed (GHI / fresh OBPI) — never silently fixed inside the audit.
- `implementer` persona is NOT dispatched; no code is written in this ceremony.
