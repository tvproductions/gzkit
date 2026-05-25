# Behavior Rules — Rationale and Prose Explanations

*Lifted from `AGENTS.md` § Behavior Rules under OBPI-0.0.54-02. The
numbered binding bullets remain canonical in `AGENTS.md` as one-line
bindings; this file preserves the verbatim prose explanations that
previously appeared inline in those bullets, per the map-not-encyclopedia
doctrine (ADR-0.0.54).*

## Anchor in AGENTS.md

The Behavior Rules section in `AGENTS.md` has two subsections:

- **Always** — 15 numbered rules every agent must follow
- **Never** — 7 numbered prohibitions every agent must respect

The bindings are the bullets. This document is the rationale and the
prose-narrative expansion the bullets used to carry inline.

## Always — prose expansions

### Always #1 — Read AGENTS.md before starting work

Mechanical backstop: SessionStart hook auto-runs `scripts/session_orientation.py`.

### Always #5 — Subagent offload boundary

Offload online research, codebase exploration, and log analysis to
subagents when work splits across independent items, when direct
`rg`/read commands would not suffice, or when context isolation is the
goal. Do not spawn subagents for single-surface checks, direct grep/read
tasks, or work whose next step depends on the result.

### Always #6 — Subagent 'Why' parameter

When spawning a subagent, always include a 'Why' parameter in the
subagent system prompt to filter signal from noise.

### Always #7 — <90% sure of direction → ask the human

Confident-wrong-direction runs are the most expensive failure mode —
burn context, produce discarded work, erode trust. 30-second
clarification beats 10-minute wrong-direction implementation. Applies to
architectural choices, scope interpretation, file targeting, upstream
comparison.

### Always #8 — Surface assumptions explicitly before implementing

Building on unstated assumptions the human would have corrected is how
confident-wrong-direction runs start. Name; let human ratify or replace.
(Judgment 12)

### Always #9 — On inconsistencies: STOP, name confusion, present tradeoff, wait

Silently picking one interpretation is vibe-coding's judgment-time face.
When brief, ADR, runbook, code disagree, the disagreement is the signal —
raise it, don't resolve unilaterally. When a unilateral pick IS forced
(operator absent, autonomous run): pick one — more recent / more tested
— explain why, flag the loser for cleanup. Never blend conflicting
patterns. (Judgment 13; sharpened by Rule 5, 2026-05-24.)

### Always #10 — Push back when an approach has clear problems

Sycophantic agreement with a flawed plan is a trust defect. Say "this
breaks X" or "this contradicts Y"; cite the rule or constraint.
(Judgment 14)

### Always #11 — Course-correction → insights record

When the operator course-corrects in flight, append an `improvement`
record to `.gzkit/insights/agent-insights.jsonl` before completing the
corrected work. Required fields: `scope`, `summary`, `evidence`,
`next_action`. See
[`docs/governance/agent-contract-rationale.md` § Rationale for Behavior Rule 11](agent-contract-rationale.md#rationale-for-behavior-rule-11-course-correction--insights)
(GHI #357).

### Always #12 — Eval-feedback-source commit trailer

When a rule edit landing under a GHI labeled `eval-feedback` is
committed, include `Eval-feedback-source: <event-id-or-artifact-path>`
in the commit trailer. The trailer is validated by
`gz validate --commit-trailers` and traces the rule change back to the
evaluation feedback loop source artifacts (ADR-0.0.26).

### Always #13 — Author GHIs through `/ghi-author` — never `gh issue create` directly

The skill's Step 0 prior-art lookup
(`gh issue list --state all --search …` + recent-by-date skim) is the
only mechanical defense against sibling-cut duplicates that bypass
`ghi-close`'s destination-routing rule. The canonical regression is
GHIs #459/#460 (2026-05-12): same T1→T2 doctrine-drift root cause, no
shared title keywords, second filed ~17 min after first without
cross-link until follow-up. Cross-repo filing through `gz issue file`
inherits the same Step-0 obligation against the target repository.

### Always #14 — Goal-driven execution

Define success criteria. Loop until verified. Strong success criteria
let Claude loop independently. (Rule 4, 2026-05-24.)

### Always #15 — Match the codebase's conventions, even if you disagree

Conformance > taste inside the codebase. If you think a convention is
harmful, surface it. Don't fork it silently. (Rule 8, 2026-05-24.)

## Never — prose expansions

### Never #5 — Do not summarize after Stage 2 or 3 and stop

OBPI pipeline runs through Stage 5; "tests passing" / "implementation
complete" is not completion. Premature summaries leave OBPIs
implemented-but-unverified, unattested, unsynced.

### Never #6 — Do not work around hook blocks

A blocking hook signals missing evidence or inactive pipeline state.
Diagnose; never hand-write marker files or ledger entries.

### Never #7 — Do not read YAML frontmatter `status: Completed` as proof of completion — read the ledger

Frontmatter is Layer-1 authorship; ledger is Layer-2 truth. Pipeline
markers and derived views (`gz status`, reconciliation caches) are
Layer-3 and never source-of-truth. Every gate decision must trace to
Layer-1 (canon) or Layer-2 (ledger).

## Local Agent Rules — verbatim prose expansions

*Lifted from `AGENTS.md` § Local Agent Rules under OBPI-0.0.54-02. The
one-line bindings remain in AGENTS.md; the verbose prose blocks each binding
carried inline are preserved here verbatim.*

### Semantic vs lexicographic ordering (feature ADRs)

Order versioned identifiers semantically, never lexicographically — **scope: feature ADRs only** (non-`0.0.x` semver). Example: `ADR-0.9.0` comes before `ADR-0.10.0`. Apply semantic-version ordering in feature-ADR summaries, comparisons, and any operator-facing status narration over feature ADRs.

### Counter-rule (foundation ADRs)

Foundation ADR IDs (`0.0.x`) are nominal integers — unique identifiers, not sequence positions. Do not order, sort, or compare foundation IDs as semver; foundations have no semantic ordering and may form sparse sets (e.g. `0.0.54`, `0.0.56` with `0.0.55` absent is valid). Doctrine: ADR-0.0.57 § Decision item 1; rule-scope shrink: ADR-0.0.57 § Decision item 3.

### Imports edited with their usage

When adding imports in an Edit call, always include the code that uses them in the same edit. The post-edit ruff hook removes unused imports immediately — splitting import addition and usage across separate edits causes the import to be deleted before it's referenced.

### Version bump → release ceremony

Every version bump is a release. After bumping `pyproject.toml`, `__init__.py`, and the README badge, always create a GitHub release with `gh release create vX.Y.Z --target main --title "vX.Y.Z" --latest --notes "..."`. The release workflow triggers PyPI publish and binary builds from the tag. Never leave a version bump uncommitted without a corresponding release.

### `.gitignore` scaffolding source

When scaffolding `.gitignore` files (in `gz init` or any related skill), use [github/gitignore](https://github.com/github/gitignore) as the canonical reference. The Python template lives at `Python.gitignore` in that repo. Fetch it via `gh api repos/github/gitignore/contents/Python.gitignore --jq '.content' | base64 -d`. Keep the scaffolded version focused on what's relevant to gzkit projects, plus gzkit-specific entries (`.claude/settings.local.json`).

### Operator PII — never in any repo-bound artifact

Operator PII — never include the operator's personal email in any repo-bound artifact. This covers commit messages and trailers; file content (source, docs, briefs, ADRs, OBPIs, runbooks, tests); attestation text passed to `gz obpi complete --attestation-text`, `gz obpi complete --attestor`, `gz adr emit-receipt`, `gz attest`, and any other CLI accepting attestor or author identity; ledger entries in `.gzkit/ledger.jsonl`; changelogs, release notes, and co-author trailers. For attestor / author identity fields use the operator's name only (e.g. `g0`). If a CLI requires an email-shaped value, use the operator's GitHub noreply address (`<handle>@users.noreply.github.com`), never the personal address. When in doubt, omit and confirm — recovery from a leak requires a filter-repo rewrite and force-push to `main` (see the 2026-04-19 incident on this repo). This rule overrides any skill, ceremony template, or attestation-enrichment example that would otherwise suggest including the personal email.

## Related

- `AGENTS.md` § Behavior Rules — the binding bullets
- `AGENTS.md` § Local Agent Rules — the binding one-liners for the prose expansions above
- `docs/governance/agent-contract-rationale.md` § Rationale for Behavior Rule 11 — the course-correction insight pattern
- `.gzkit/rules/agent-failure-modes.md` — the six-pattern failure-mode taxonomy backstopped by these rules
- `docs/governance/trust-doctrine.md` — T1/T2/T3 invariants Never #7 binds to
- `ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine` — parent ADR for this lift
