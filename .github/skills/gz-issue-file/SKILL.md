---
name: gz-issue-file
persona: main-session
description: Cross-repo defect/enhancement filing wrapper for gzkit-owned surfaces. Use from inside any consuming repository when surfacing a defect or enhancement against the `gz` CLI, schemas under `src/gzkit/schemas/`, validator scopes, ledger event semantics, files under `.gzkit/**` or `src/gzkit/**`, or rules under `.gzkit/rules/**`. Routes the issue at `tvproductions/gzkit` regardless of the consuming repo's `git remote`, auto-stamps a provenance trailer naming the consumer slug and gz version, and hard-rejects bodies that reference no gzkit-owned surface.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-02
metadata:
  skill-version: "1.0.0"
  govzero-framework-version: "v6"
model: sonnet
---

# gz-issue-file

## Invocation

```text
/gz-issue-file
```

No ID argument. `gh issue create` (invoked under the hood by `gz issue file`)
assigns the next available issue number on `tvproductions/gzkit`; the skill
records the assigned number into session evidence after creation.

## When to use

When working **inside a gzkit-consuming repository** and the finding belongs
to a **gzkit-owned surface**:

- The `gz` CLI itself misbehaves (parser, dispatcher, output, exit code).
- A schema under `src/gzkit/schemas/` is over- or under-strict.
- A validator scope (`gz validate --<scope>`) misses or false-flags drift.
- A ledger event semantic drifts from doctrine.
- A rule under `.gzkit/rules/**` contradicts another rule or is silently
  skipped.
- A skill or hook surface in `.gzkit/skills/` or `.gzkit/hooks/` regresses.

For enhancements to any of the above, file with `--enhancement` instead of
`--defect`.

## When NOT to use

- Defects in **consumer-repo** code, content, or governance — file at the
  consumer's tracker via plain `gh issue create`.
- In-flight defects against gzkit that meet the direct-fix thresholds in
  `AGENTS.md` § Defect-fix routing (≤10 source lines, ≤2 source files, ≥3
  recent precedents) — fix in place with `fix(<scope>): … (GHI #N)` rather
  than filing.

## Procedure

1. **Preview first** with `--dry-run`:

   ```bash
   uv run gz issue file \
     --title "<gzkit-surface description>" \
     --body "<must reference gz <verb>, .gzkit/, src/gzkit/, or gzkit.<module>>" \
     --defect \
     --dry-run
   ```

2. **Confirm the trailer and target** in the dry-run output:
   - First line is `Filed from <owner>/<repo> running gz vX.Y.Z`.
   - `Target: tvproductions/gzkit`.
   - `Label: defect` (or `enhancement`).

3. **File live** by re-running without `--dry-run`. The wrapper invokes
   `gh issue create --repo tvproductions/gzkit --title T --body B --label L`
   and propagates `gh`'s exit code on failure.

4. **Record the assigned issue number** into the relevant brief, GHI, or
   commit body so downstream `(GHI #N)` references resolve.

## Doctrine

- `.gzkit/rules/gh-cli.md` § Cross-repo filing — the canonical doctrine
  surface this skill operationalizes.
- `.gzkit/rules/agent-failure-modes.md` § Safeguard circumvention — the
  failure shape this wrapper closes structurally.
- `AGENTS.md` § Local Agent Rules (Operator PII) — the auto-stamped trailer
  composes only the repo slug and gz version; no email is ever derived.

## Output Contract

Default form: **plain text** (one `Target:`/`Label:`/`Title:` line each, then
the composed body). `--dry-run` is the canonical preview affordance.

The wrapper has **no `--json` flag**: filing an issue is a side-effecting
operation whose canonical output is the GHI URL on stdout (`gh issue
create`'s default), not a structured payload.

## Failure Modes

| Failure | Cause | Resolution |
|---------|-------|------------|
| Exit 1, "issue body references no gzkit-owned surface" | Body lacks `gz <verb>`, `.gzkit/`, `src/gzkit/`, or `gzkit.<module>` | Edit body to name the gzkit surface; or file at the consumer's tracker if the defect is consumer-owned |
| Exit 1, "no git remote found" | Working tree is not a git repo or has no remote | Run from a real git working tree |
| Exit 1, mutually-exclusive flag conflict | Both `--defect` and `--enhancement` supplied | Pick one |
| Exit 2 | `gh` subprocess failed (auth, network, GitHub API error) | Run `gh auth status`; check network; re-try |

## Related

- Manpage: `docs/user/manpages/gz-issue.md`
- Command doc: `docs/user/commands/issue-file.md`
- Operator runbook entry: `docs/user/runbook.md` § Cross-Repo Defect Filing
- Governance runbook entry: `docs/governance/governance_runbook.md` § Cross-repo defect routing
- Parent ADR: `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/`
- Source brief: GHI #316
- Sibling skill: `ghi-author` — for filing GHIs at the **current** repo (not cross-repo)
