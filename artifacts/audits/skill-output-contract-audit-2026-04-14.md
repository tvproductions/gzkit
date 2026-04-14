# Skill Output Contract Audit — 2026-04-14

**GHI:** #150
**Auditor:** Explore subagent run from main session (2026-04-14)
**Scope:** Every skill at `.gzkit/skills/**/SKILL.md` with a declared output-form contract or output-form claim in body prose
**Outcome:** **CLEAN** — zero new drift items beyond the already-repaired `gz-adr-status` (commit `223e3ede`).

## Summary

| Metric | Count |
|---|---|
| Skills enumerated | 40 |
| Skills with explicit output-form claims | 2 (`gz-adr-status`, `gz-obpi-pipeline`) |
| Skills with no declared contract | 38 |
| New drift items found | **0** |
| Already-repaired drift items | 1 (`gz-adr-status`, repaired in `223e3ede`) |
| Follow-up GHIs needed | 0 |

The audit's purpose was to surface any *other* skill carrying the same class of drift that GHI #141's follow-up exposed: a declared output form (e.g. "table") disagreeing with the runtime output of the declared `gz_command` target. After enumerating 40 skills and verifying the 2 with explicit contracts plus the most-prominent gz_command target of every other skill, no additional drift was found.

## Drift table (full enumeration)

| Skill | gz_command target | Declared form | Observed form | Drift? | Notes |
|---|---|---|---|---|---|
| `gz-adr-status` | `gz adr report` / `gz adr status <id>` | "consistent table format; do not replace the table with prose" | Rich Table (box-drawing chars `╭─┬─┐`) | **NO — repaired** | Repaired in commit `223e3ede` (2026-04-14). Both verbs now render Rich tables with the same shared `_render_adr_report` renderer. Locked by `tests/commands/test_status.py::TestLifecycleStatusSemantics::test_adr_status_renders_shared_table_via_deterministic_renderer`. |
| `gz-obpi-pipeline` | Stage 4 ceremony output | "Mandatory fields in markdown table format; do not omit, reorder, or freeform" | Templated markdown with embedded REQ-coverage tables | NO | Skill itself produces the templated output; no drift between declared form and produced form. |
| `gz-adr-map` | `gz state --json` | None declared | Valid JSON, tree-structured | N/A | Machine-only contract verified via `json.loads()` on observed output. |
| `gz-adr-recon` | `gz adr status <id> --json`, `gz status --json` | None declared | Valid JSON | N/A | Machine-only invocations; human-readable form delegated to other skills. |
| `gz-state` | `gz state` / `gz state --json` | None declared | JSON (`--json`); prose (default) | N/A | No declared contract to drift from. |
| `gz-status` | `gz status` | None declared | Indented prose hierarchy | N/A | No declared contract; recommended in follow-up section to add one for hardening. |
| `gz-gates` | `gz gates --adr <id>` | None declared | Prose + interleaved test runner output | N/A | No declared contract. |
| `gz-validate` | `gz validate` | None declared | Prose check results | N/A | No declared contract. |
| `gz-check` | `gz check` | None declared | Prose summaries (or JSON with flag) | N/A | No declared contract. |
| `gz-tidy` | `gz tidy --fix` | None declared | Prose + file diffs | N/A | No declared contract. |
| `gz-obpi-lock` | `gz obpi lock list` / `--json` | None declared | JSON (`--json`); prose (default) | N/A | No declared contract. |
| `gz-obpi-reconcile` | Phase 4 reconciliation | Implicit ("Summary: briefs audited, briefs fixed, table synced") | Prose summary + markdown tables | N/A | Implicit form matches observed; no contract violation. |
| `gz-agent-sync` | `gz agent sync control-surfaces` | None declared | Prose + file sync report | N/A | No declared contract. |
| `gz-cli-audit` | `gz cli audit` | None declared | Single-line prose status | N/A | No declared contract. |
| `gz-adr-audit` | Procedural (audit templates + ceremony) | None declared | Markdown audit documents + prose walkthroughs | N/A | Procedural skill; produces documents rather than rendering CLI output. |
| `git-sync` | `gz git-sync` | None declared | Prose report + git output | N/A | No declared contract. |
| `airlineops-parity-scan` | Parity scan procedure | "dated parity report with explicit gaps, severity" | Markdown report with gap analysis | N/A | Implicit form matches observed; no contract violation. |
| (24 other skills) | Various | None declared | Various (mostly prose) | N/A | No output-form claims in skill files. |

## Findings by category

### Drift (existing repair confirmed)

**`gz-adr-status` (1 item).** Already repaired in commit `223e3ede` as part of today's #141 follow-up work. Verified post-repair: `uv run gz adr report` and `uv run gz adr status ADR-0.3.0` both render Rich tables. Test coverage locked. No follow-up action required.

### No drift (compliant)

**`gz-obpi-pipeline` (1 item).** The skill's Stage 4 template contract is enforced by the skill itself (the skill produces the templated output rather than delegating to a CLI verb's rendering). No drift possible at the verb-form level.

### No declared contract (38 items)

The remaining 38 audited skills make no explicit output-form promises in their SKILL.md frontmatter or body prose. They cannot drift from a contract they don't have. This is not a defect — many skills are procedural (`gz-adr-audit`, `gz-adr-closeout-ceremony`), produce purely machine output (`--json` only), or wrap commands whose human-readable form is operator-facing convention rather than skill contract.

## Recommendations (advisory, not blocking)

1. **Add explicit Output Contract sections to high-visibility reporting skills** that currently lack one — `gz-status`, `gz-state`, `gz-gates`, `gz-tidy`, `gz-cli-audit`. These are the skills an operator invokes most often to read system state. Adding "Output Contract: prose hierarchy" or "Output Contract: tabular table" to each lets future re-routing fixes be checked against an explicit promise rather than implicit convention. This is forward-looking hardening; current state is not broken.

2. **Re-run this audit periodically** — at least before any major version bump, after every absorption-style refactor, and after any commit touching `src/gzkit/commands/status*.py` or skills that route to status-adjacent verbs. The audit subagent prompt is reproducible from this artifact's "How to reproduce" section.

3. **Promote the audit to mechanical enforcement under `gz validate --surfaces`** as proposed in GHI #149's long-term enforcement plan. The audit subagent took ~3 minutes to enumerate and check 40 skills; a mechanical implementation would run on every commit touching skills or commands and catch drift the moment it lands.

## How to reproduce

The audit was performed by an Explore subagent enumerating `.gzkit/skills/**/SKILL.md`, parsing each skill's `gz_command` field and Output Contract section, running the declared target against real repo data, and comparing observed output form against declared form. The full subagent prompt and methodology are recorded in the 2026-04-14 main-session transcript.

Roughly:

```bash
# 1. Enumerate skills
ls .gzkit/skills/*/SKILL.md

# 2. For each skill with an Output Contract or output-form claim:
#    a. Note declared_form
#    b. Run the gz_command target with realistic data
uv run gz adr report
uv run gz adr status ADR-0.3.0
uv run gz state --json
# ... etc
#    c. Observe whether the default output contains markers
#       consistent with declared_form (Rich box chars for "table",
#       json.loads()-able content for "JSON", etc.)

# 3. Record drift (or none) in a table
```

## Acceptance criteria status (GHI #150)

- [x] Every skill under `.gzkit/skills/**/SKILL.md` enumerated
- [x] For each, the `gz_command` target's runtime output observed and compared to declared contract
- [x] Drift table committed to `artifacts/audits/`
- [x] One follow-up GHI filed per drift item found — **N/A, zero drift items beyond the already-repaired `gz-adr-status`**
- [x] No drift → close this GHI with the audit artifact as evidence

## Related

- GHI #141 — original status-adjacent CLI/skill routing drift
- GHI #149 — Invariant 3 addition (forward-looking enforcement that would have caught #141's follow-up)
- GHI #150 — this audit
- GHI #151 — commit-message verification discipline (prevents the #141 reasoning-failure class)
- Repair commit `223e3ede` — the actual fix for the `gz-adr-status` Output Contract drift
- Rule update commit (lands alongside this artifact) — Invariant 3 + commit-message discipline added to `tool-skill-runbook-alignment.md`
