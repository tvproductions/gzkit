<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Layer 3 derived-view inventory

**Session date:** 2026-04-18
**Companion doctrine:** [state-doctrine.md](./state-doctrine.md), [trust-doctrine.md](./trust-doctrine.md)
**Tracking GHI:** [#214](https://github.com/tvproductions/gzkit/issues/214)

The state doctrine declares Layer 3 (L3) artifacts as *derived, rebuildable views*. Every fact in L3 must trace to Layer 1 (canonical source) or Layer 2 (ledger events). This document enumerates the L3 views currently known to gzkit, names the canonical L1/L2 producer for each, and identifies which ones have an independent write-path audit today.

---

## L3 views and their producers

| L3 view | Canonical producer | Trust-chain audit | Notes |
|---|---|---|---|
| ADR frontmatter (`status:`, `lane:`, etc.) | Ledger `adr_attested` / `lifecycle_transition` / `gate_checked` events | `audit_frontmatter_coherence` / `gz validate --frontmatter` | Primary L3 — locked under ADR-0.0.16 |
| OBPI frontmatter | Ledger `obpi_created` / `obpi_completed` / `obpi_receipt_emitted` | `audit_frontmatter_coherence` | Same surface as ADR; shared validator |
| Artifact graph (`gz state`) | Ledger event stream (`_apply_*_metadata` handlers) | `audit_event_handlers`, `audit_validator_fields` | Locked under GHIs #193 / #199 |
| `gz status` prose / table | Artifact graph | Shared renderer (`status.py:adr_status_cmd`) | Locked under GHI #141 / #149 |
| Pipeline markers under `.gzkit/pipeline/` | Pipeline controller emits markers as convenience | No independent audit yet — tracked here | L3 convenience cache; must never be read as proof of gate state |
| OBPI lock files under `.gzkit/locks/` | `obpi_lock_claimed` / `obpi_lock_released` events | Waived in `_NO_GRAPH_IMPACT` | L3 ephemeral state; regenerated from ledger on demand |
| Reconciliation cache | `gz frontmatter reconcile` / `gz state` | Partial — `gz validate --reconcile-freshness` (GHI #213) | Advisory until `reconcile_*` events are standardized |
| Skills mirror (`.claude/skills/**`, `.github/skills/**`) | `.gzkit/skills/**` via `gz agent sync control-surfaces` | Pre-commit sync guard (GHI #210); `skill-version` and commit-hash resolution | Version+hash tiebreaker is mechanical |
| Rules mirror (`.claude/rules/**`, `.github/instructions/**`) | `.gzkit/rules/**` via `gz agent sync control-surfaces` | Same sync guard | Same as skills mirror |
| ARB receipts (`artifacts/receipts/*.json`) | `gz arb <verb>` wrapping a QA command | `gz arb validate` enforces canonical commands | Receipt-ID citation enforced for Heavy-lane attestation |
| `adr_report` / `adr_status` rendered output | `artifact_graph` + CLI deterministic renderer | Shared renderer + `test_adr_status_renders_shared_table_via_deterministic_renderer` | Invariant 3 (tool-skill-runbook) locks renderer form |
| Release notes rendering | GitHub release API + local `RELEASE_NOTES.md` | `gz validate --version-release` (GHI #205) | Mechanical for presence; notes content is editorial |
| Manpage / command doc content | `src/gzkit/commands/**` + `_build_parser` | `gz cli audit`, `gz validate --cli-alignment` | Locked under GHI #198 |
| Advisory-rules scorecard | `.gzkit/rules/**` + `CLAUDE.md` | `gz validate --advisory-scorecard` (GHI #212) | Self-testing — a new rule file without a scorecard row fails the audit |

## Views still lacking an independent write-path audit

The rows marked "No independent audit yet" or "Advisory" in the table above are the current L3 attack surface — they look authoritative but have no mechanical check that the L1/L2 producer actually wrote what the consumer reads.

**Pipeline markers** are the highest-leverage gap. Multiple skills (gz-obpi-pipeline, plan-audit gate) read pipeline-marker presence as a signal of prior stage completion. Trust-chain poisoning vectors:

1. A stage fires, writes its marker, then the ledger event emission fails. Marker says "done"; ledger says "never happened." Downstream consumers read the marker and proceed.
2. A stale marker survives a branch switch or a `git checkout` and misrepresents the current HEAD's pipeline state.

The mechanical fix is an audit that cross-references every pipeline marker against a corresponding ledger event emitted against the same HEAD — a Trust Invariant T2 ("every consumed value has a write-path audit") for the marker → ledger chain. Tracked as follow-up to #214.

**Reconciliation cache freshness** is partially mechanized under GHI #213 (`gz validate --reconcile-freshness`), but the audit is a no-op when no reconcile events exist in the ledger. Standardizing the reconciliation event vocabulary (`frontmatter_reconciled` / `state_reconciled` / `obpi_reconciled`) and emitting them from `gz frontmatter reconcile` / `gz state` is the complement.

## Triage

| Layer gap | Action | Mechanical handle |
|---|---|---|
| Pipeline markers are read without ledger cross-check | Define a marker → ledger event mapping; add an audit that fails if a marker exists without a corresponding HEAD-scoped ledger event | Follow-up GHI |
| Reconciliation event emission is not wired | Emit `frontmatter_reconciled` from `gz frontmatter reconcile`; emit `state_reconciled` from `gz state` when it writes to the derived cache | Follow-up GHI (complements #213) |
| Manpage rendering drift (prose vs argparse help) | Extend `gz cli audit` to diff manpage options against `_build_parser` actions | Follow-up GHI |
| Release notes content drift | No mechanical shape yet — editorial L3 view; leave judgment-scored | n/a |

## Related

- `docs/governance/state-doctrine.md` — storage tiers L1/L2/L3
- `docs/governance/trust-doctrine.md` — invariants T1/T2/T3
- `docs/governance/advisory-rules-audit.md` — promoted-audit catalogue
- GHI #214 — this enumeration
