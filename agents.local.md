# Local Agent Rules

- Order versioned identifiers semantically, never lexicographically. Example: `ADR-0.9.0` comes before `ADR-0.10.0`.
- Apply semantic-version ordering in ADR summaries, comparisons, and any operator-facing status narration.
- When adding imports in an Edit call, always include the code that uses them in the same edit. The post-edit ruff hook removes unused imports immediately — splitting import addition and usage across separate edits causes the import to be deleted before it's referenced.
- Never prefix `uv run gz` or `uv run -m gzkit` commands with `PYTHONUTF8=1`. The CLI entrypoint handles UTF-8 encoding at runtime.
- Attestation and commit-message enrichment: pass user words verbatim, append concrete characterization grounded in session evidence. See `.gzkit/rules/attestation-enrichment.md`.
- Every version bump is a release. After bumping `pyproject.toml`, `__init__.py`, and the README badge, always create a GitHub release with `gh release create vX.Y.Z --target main --title "vX.Y.Z" --latest --notes "..."`. The release workflow triggers PyPI publish and binary builds from the tag. Never leave a version bump uncommitted without a corresponding release.
- When scaffolding `.gitignore` files (in `gz init` or any related skill), use [github/gitignore](https://github.com/github/gitignore) as the canonical reference. The Python template lives at `Python.gitignore` in that repo. Fetch it via `gh api repos/github/gitignore/contents/Python.gitignore --jq '.content' | base64 -d`. Keep the scaffolded version focused on what's relevant to gzkit projects, plus gzkit-specific entries (`.claude/settings.local.json`).

## Governance doctrine surfaces

Read before touching governance code, rules, or audits:

- `docs/governance/trust-doctrine.md` — trust-chain poisoning pattern and the T1/T2/T3 invariants every layer boundary must satisfy.
- `docs/governance/advisory-rules-audit.md` — the scorecard catalogue of every rule in `CLAUDE.md` and `.gzkit/rules/`. Score each new rule **Mechanical / Promotable / Judgment / Ambiguous**; promote Promotable rules to mechanical under a tracking GHI.
- `docs/governance/state-doctrine.md` — storage-tier doctrine; Layer 3 derived views are never source-of-truth.

The advisory scorecard is self-testing via `uv run gz validate --advisory-scorecard`: a new rule file under `.gzkit/rules/` without a scorecard entry fails the audit.

Promoted audits run via `uv run gz validate --<scope>` — see `gz validate --help` for the full flag list. The trust-doctrine and scorecard pages list every promoted scope and the GHI under which it landed.

## Architectural Boundaries

*Source: Architecture Planning Memo Section 12 (Decision Record 2026-03-29).*

1. **Do not promote post-1.0 pool ADRs into active work.** `ai-runtime-foundations`, `controlled-agency-recovery`, and `evaluation-infrastructure` (the pool version) are post-1.0 concerns. The graph spine, proof architecture, and pipeline lifecycle are not stable enough to support AI runtime controls on top.
2. **Do not add more pool ADRs to the runtime track.** The pool has sufficient architectural intent for 2-3 years of work. The problem is insufficient foundation locking, not insufficient vision.
3. **Do not build the graph engine without locking state doctrine first.** A graph engine built on implicit state assumptions becomes the single biggest source of reconciliation bugs.
4. **Do not let reconciliation remain a maintenance chore.** If the state doctrine says "derived state is rebuildable," then reconciliation is a core architectural operation — tested, gated, and part of the pipeline.
5. **Do not let AirlineOps parity become perpetual catch-up.** Current parity is sufficient baseline. Future parity should flow from gzkit innovations adopted by AirlineOps, not gzkit chasing AirlineOps patches.
6. **Do not let derived views silently become source-of-truth.** `gz status` output, pipeline markers, and reconciliation caches are Layer 3. Every fact must trace to Layer 1 (canon) or Layer 2 (ledger).
