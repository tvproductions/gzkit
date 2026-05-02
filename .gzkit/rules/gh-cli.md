---
id: gh-cli
paths:
  - ".github/**"
  - "docs/design/adr/**"
  - "src/gzkit/commands/issue_cmd.py"
description: GitHub CLI usage guardrails
---

<!-- rule-version: 0.1.0 -->

# GitHub CLI Guardrails (gzkit)

> **Rule version:** `0.1.0` — initialized under OBPI-0.0.23-04 to introduce
> the body-level marker convention and canonize the § Cross-repo filing
> subsection. Prior unversioned content treated as pre-marker.

Use `gh` for (a) defect tracking per `.gzkit/rules/governance-core.md` and
`AGENTS.md` § Prime Directive (filing defect GHIs is always
authorized — it is not a user-intent gate), (b) ADR closeout per
`.gzkit/rules/adr-audit.md`, (c) release ceremony, or (d) any active brief
or explicit user request. The "Prohibited without explicit approval" list
below still binds regardless of the authorization surface.

## Allowed commands

```bash
gh auth status
gh issue create --label defect --title "..." --body "..."
gh issue list --search "ADR-X.Y.Z" --state open
gh issue close <number> --comment "Resolved by ADR-X.Y.Z closeout."
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file RELEASE_NOTES.md
```

## Prohibited without explicit approval

- Repository/org settings mutations
- Secret/token management
- Force pushes
- Merging PRs without explicit human authorization

## Defect tracking requirement

When a defect cannot be fixed in the current patch:

1. `gh issue create --label defect ...`
2. Link the issue in the relevant ADR/OBPI evidence section.

## Cross-repo filing

When an agent or operator working **inside a gzkit-consuming repository**
surfaces a defect or enhancement against a **gzkit-owned surface**, the
issue MUST be filed at `tvproductions/gzkit` — not at the consuming
repo's tracker, not as a `.gzkit/insights/agent-insights.jsonl` entry,
not as an in-flight workaround that escapes triage.

This subsection operationalizes the `Safeguard circumvention` failure
shape codified in `.gzkit/rules/agent-failure-modes.md`: misrouting a
gzkit-surface defect to the consumer's tracker (or burying it as an
insight) is the same class of failure as bypassing a hook block — the
agent works around the authorization path instead of producing the
evidence the path is asking for.

### What counts as a "gzkit-owned surface"

A defect or enhancement is gzkit-owned when its body references at least
one of:

- `gz <verb>` — the CLI surface (e.g. `gz validate fails on ...`).
- `.gzkit/` — canonical artifacts (skills, rules, manifest, ledger).
- `src/gzkit/` — the implementation tree (modules, schemas, validators).
- `gzkit.<module>` — Python module references (`gzkit.events`, `gzkit.ledger`).

A defect or enhancement that references **only** consumer-repo code,
content, or governance is **not** gzkit-owned and belongs at the
consumer's tracker. The asymmetry is intentional: consumer repos own
their own remediation surface; gzkit owns its.

### Canonical wrapper: `gz issue file`

Cross-repo filing is operationalized by the `gz issue file` wrapper. The
wrapper auto-stamps a provenance trailer of shape
`Filed from <consumer-repo-slug> running gz vX.Y.Z` at the top of the
issue body, validates that the body references at least one of the
markers above, and routes the issue against `tvproductions/gzkit`
regardless of the consuming repo's `git remote`.

```bash
# File a defect (default label) — body must reference a gzkit surface
gz issue file --title "T" --body "gz validate --documents miscounts X" --defect

# Preview before live filing
gz issue file --title "T" --body "src/gzkit/commands/y.py crashes" \
              --enhancement --dry-run
```

The wrapper **hard-rejects** (exit 1) bodies that reference no
gzkit-owned surface and emits a diagnostic naming every checked marker.
This closes the misrouting failure class structurally — an agent or
operator cannot file a misrouted issue at `tvproductions/gzkit` even by
accident. See `docs/user/manpages/gz-issue.md` for the full surface.

### When `gz issue file` is the right route

| Trigger | Filing path |
|---|---|
| `gz` CLI behavior is wrong (parser, dispatcher, output, exit code) | `gz issue file --defect` against `tvproductions/gzkit` |
| Schema rejection logic in `src/gzkit/schemas/` is over- or under-strict | `gz issue file --defect` |
| Validator scope (`gz validate --<scope>`) misses or false-flags drift | `gz issue file --defect` |
| Ledger event semantics drift from doctrine | `gz issue file --defect` |
| Rule under `.gzkit/rules/` is silently skipped or contradicts another rule | `gz issue file --defect` |
| Skill or hook surface in `.gzkit/skills/` or `.gzkit/hooks/` regresses | `gz issue file --defect` |
| Enhancement to any of the above (new flag, new validator scope, new skill) | `gz issue file --enhancement` |
| Defect in **consumer-repo** code, content, governance, or workflow | `gh issue create` against the consumer's tracker — **not** this wrapper |

### Operator privacy

The wrapper auto-stamps only the consumer repo slug and the gzkit
version. The operator's email is never derived, inferred, or written
into the trailer or the body — `AGENTS.md` § Local Agent Rules (Operator
PII) binds this surface as much as any other repo-bound artifact. When
an operator's identity is genuinely required (rare; almost always the
provenance trailer is sufficient), use the GitHub noreply address
(`<handle>@users.noreply.github.com`).
