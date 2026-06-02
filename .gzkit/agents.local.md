# Local Agent Rules

- **DIRECT-FIX MORATORIUM (operator directive, 2026-06-01).** Defects surfaced in flight get DIRECT-FIXED now — smallest honest fix, TDD (RED→GREEN), `Task:` trailer (slug `-#<ghi>` optional; never file a GHI just to satisfy it). Do NOT reflexively file a GHI/ADR/OBPI to *track* what fits one coherent commit; open one only when the fix genuinely can't land in scope (crosses brief boundaries, needs design, exceeds one commit) and name why. Does not relax TDD, read-before-change, coupled-surface coherence, or attestation.
- Order versioned identifiers semantically, never lexicographically — **scope: feature ADRs only** (non-`0.0.x` semver). Example: `ADR-0.9.0` comes before `ADR-0.10.0`.
- Apply semantic-version ordering in feature-ADR summaries, comparisons, and any operator-facing status narration over feature ADRs.
- **Counter-rule (foundation ADRs):** Foundation ADR IDs (`0.0.x`) are nominal integers — unique identifiers, not sequence positions. Do not order, sort, or compare foundation IDs as semver; foundations have no semantic ordering and may form sparse sets (e.g. `0.0.54`, `0.0.56` with `0.0.55` absent is valid). Doctrine: ADR-0.0.57 § Decision item 1; rule-scope shrink: ADR-0.0.57 § Decision item 3.
- When adding imports in an Edit call, always include the code that uses them in the same edit. The post-edit ruff hook removes unused imports immediately — splitting import addition and usage across separate edits causes the import to be deleted before it's referenced.
- Never prefix `uv run gz` or `uv run -m gzkit` commands with `PYTHONUTF8=1`. The CLI entrypoint handles UTF-8 encoding at runtime.
- Attestation and commit-message enrichment: pass user words verbatim, append concrete characterization grounded in session evidence. See `AGENTS.md` § Attestation.
- Every version bump is a release. After bumping `pyproject.toml`, `__init__.py`, and the README badge, always create a GitHub release with `gh release create vX.Y.Z --target main --title "vX.Y.Z" --latest --notes "..."`. The release workflow triggers PyPI publish and binary builds from the tag. Never leave a version bump uncommitted without a corresponding release.
- When scaffolding `.gitignore` files (in `gz init` or any related skill), use [github/gitignore](https://github.com/github/gitignore) as the canonical reference. The Python template lives at `Python.gitignore` in that repo. Fetch it via `gh api repos/github/gitignore/contents/Python.gitignore --jq '.content' | base64 -d`. Keep the scaffolded version focused on what's relevant to gzkit projects, plus gzkit-specific entries (`.claude/settings.local.json`).
- **Operator PII — never include the operator's personal email in any repo-bound artifact.** This covers commit messages and trailers; file content (source, docs, briefs, ADRs, OBPIs, runbooks, tests); attestation text passed to `gz obpi complete --attestation-text`, `gz obpi complete --attestor`, `gz adr emit-receipt`, `gz attest`, and any other CLI accepting attestor or author identity; ledger entries in `.gzkit/ledger.jsonl`; changelogs, release notes, and co-author trailers. For attestor / author identity fields use the operator's name only (e.g. `g0`). If a CLI requires an email-shaped value, use the operator's GitHub noreply address (`<handle>@users.noreply.github.com`), never the personal address. When in doubt, omit and confirm — recovery from a leak requires a filter-repo rewrite and force-push to `main` (see the 2026-04-19 incident on this repo). This rule overrides any skill, ceremony template, or attestation-enrichment example that would otherwise suggest including the personal email.

## Governance doctrine surfaces

Read these before touching governance code, rules, or audits:

- `docs/governance/trust-doctrine.md` — trust-chain poisoning pattern and the T1/T2/T3 invariants every layer boundary must satisfy.
- `docs/governance/advisory-rules-audit.md` — the scorecard catalogue of every rule in `CLAUDE.md` and `.gzkit/rules/`. Score each new rule **Mechanical / Promotable / Judgment / Ambiguous**; promote Promotable rules to mechanical under a tracking GHI.
- `docs/governance/state-doctrine.md` — storage-tier doctrine; Layer 3 derived views are never source-of-truth.

The scorecard is self-testing via `uv run gz validate --advisory-scorecard`; promoted audits run via `uv run gz validate --<scope>` and are catalogued in the doctrine pages above.

### Mechanical scopes that bind here

- **Per-file char budget for AGENTS.md / CLAUDE.md / `.claude/rules/*.md`** (companion to Anti-vibing operative claim 2) — enforced by `gz validate --instructions-files-budget` (GHI #373). Tracked file budgets live in `data/instructions_files_budget.json` (defaults: 40k chars AGENTS.md/CLAUDE.md, 16k per rule file). Fail-closed on overrun with remediation pointer to `/gz-context-diet`.
- **The editor/IDE authoring-guide protocol envelope (LSP-style Content-Length–framed JSON)** is defined by `src/gzkit/schemas/authoring_guide_protocol.json`. Every request, response, notification, and error shape MUST be named in the schema; protocol drift is caught by JSON Schema validation at server runtime, not by human review (ADR-0.0.30 / OBPI-0.0.30-04).
- **Eval-feedback-source commit trailer** — when a rule edit lands under a GHI labeled `eval-feedback`, include `Eval-feedback-source: <event-id-or-artifact-path>` in the commit trailer. The trailer is validated by `gz validate --commit-trailers` (ADR-0.0.26).
- **`abandon categories are closed`** — lock release is coupled to a handoff/register entry per ADR-0.0.41; runtime warning / fail-closed enforcement and `gz validate --lock-handoff-coupling` are tracked under pending OBPIs (`.gzkit/rules/token-block-discipline.md`).
- **Advisor diagnosis non-empty `proof: tuple[ProofRange, ...]`** binding (`Field(min_length=1)` on `AdvisorDiagnosis.proof`) is enforced by `gz validate --advisor-proof-binding` (OBPI-0.0.29-08).
- **Complexity calibration is grounded in an empirically-measured exemplar corpus** with seven selection criteria (longevity, maintenance health, practitioner reputation NOT GitHub-star count, pure-Python LOC share, author craftsmanship signal, project doctrine fitness, pinned commit SHA); link-integrity enforced by `gz validate --complexity-doctrine-links` (OBPI-0.0.27-07).
- **Heavy/foundation lane requires explicit human attestation before completion** — see § OBPI Acceptance Protocol; enforced by `gz closeout` pipeline.
- **`.gzkit/rules/*.md` with `paths: "**"` or missing `paths:` may not live under any vendor-surface rules directory** (ADR-0.0.20) — enforced by `gz validate --unscoped-rules`.
- **Every canonical surface (skills, rules, hooks, templates, chores, personas) MUST be reproducibly delivered by `pip install py-gzkit && gz init` to a fresh project, byte-equivalent to the wheel's authored canonical content** (T0 distribution invariant, ADR-0.0.31) — enforced by `gz validate --distribution`.
- **`gz validate --invariant-coherence` — composition drift fail-close** re-renders the constitutional invariant registry and byte-compares against committed AGENTS.md; exit 3 on drift; in the `gz check` default scope (ADR-0.0.37 / OBPI-0.0.37-03).
- **OBPI brief reconciles against current project shape before Stage 2 and before completion** — the five-dimension reconciliation engine (`reconcile_brief`) computes per-dimension drift; `gz validate --brief-reconcile` escalates drift for structured `BriefStructure` briefs (ADR-0.0.37 / OBPI-0.0.37-05).
- **Every REQ in an OBPI brief's Acceptance Criteria MUST declare exactly one of three kinds — BEHAVIOR, SUPPORT, or STRUCTURAL-FENCE — via an inline tag `[kind]`; each kind has exactly one proof channel (BEHAVIOR → `@covers` test; SUPPORT → ledger event + structural validator; STRUCTURAL-FENCE → parent-ADR `## Boundary Invariants` entry)** — `gz validate --req-kind-discipline` forthcoming under OBPI-0.0.59-02 (ADR-0.0.59 / OBPI-0.0.59-01).

## Architectural Boundaries

Source: Architecture Planning Memo Section 12 (Decision Record 2026-03-29).

1. **Do not promote post-1.0 pool ADRs into active work.** `ai-runtime-foundations`, `controlled-agency-recovery`, and `evaluation-infrastructure` remain parked until the graph spine, proof architecture, and pipeline lifecycle are stable.
2. **Do not add more pool ADRs to the runtime track.** The pool has sufficient runtime intent; lock foundation first.
3. **Do not build the graph engine without locking state doctrine first.** A graph engine built on implicit state assumptions becomes the single biggest source of reconciliation bugs.
4. **Do not let reconciliation remain a maintenance chore.** Reconciliation is a core architectural operation. Freshness check applies once reconciliation has run at least once; zero-event history is bootstrap, not drift.
5. **Do not let AirlineOps parity become perpetual catch-up.** Current parity is sufficient baseline. Future parity should flow from gzkit innovations adopted by AirlineOps, not gzkit chasing AirlineOps patches.
6. **Do not let derived views silently become source-of-truth.** `gz status`, pipeline markers, and reconciliation caches are Layer 3; every fact traces to Layer 1 canon or Layer 2 ledger.
