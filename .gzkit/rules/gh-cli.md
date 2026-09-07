---
id: gh-cli
paths:
  - ".github/**"
  - "docs/design/adr/**"
  - "src/gzkit/commands/issue_cmd.py"
description: GitHub CLI guardrails and cross-repo filing protocol.
---

<!-- rule-version: 0.5.0 -->

# GitHub CLI Guardrails (gzkit)

> **Rule version:** `0.5.0` — GHI #972 (2026-09-07): adds § Census queries. § Allowed commands sanctioned `gh issue list` by *verb* while the hazard is scoped by *result-set size* — every `gh <noun> list` returns a 30-row page with no truncation marker and exit 0, and the handoff chain's own "re-derive the count" step was that capped command, so a session that noticed a wrong count re-derived `30` with fresh confidence. Scored **Judgment** at row 51c. Prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#gh-climd).

Use `gh` for defect tracking, ADR closeout, release ceremony, or active brief / explicit user request.

## Filing an issue — route through `/ghi-author`, never `gh issue create`

**`gh issue create` is forbidden as a direct agent invocation** (AGENTS.md § Behavior Rules — Always #13). Author every GHI through the `/ghi-author` skill; file cross-repo through `gz issue file`. The skill's Step-0 prior-art lookup is the only defense against sibling-cut duplicates (canonical regression: GHI #459/#460).

The prohibition is on the **caller**, not the string: `/ghi-author` itself invokes `gh issue create` at `SKILL.md:199` as its own final step, so the sanctioned and forbidden invocations are byte-identical commands. Nothing mechanical can tell them apart — the discipline is yours to keep.

## Allowed commands

```bash
gh issue list --search "ADR-X.Y.Z" --state open
gh issue close <number> --comment "Resolved by ADR-X.Y.Z closeout."
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file RELEASE_NOTES.md
```

```bash
# Inside /ghi-author only — direct agent invocation is a process defect
# per AGENTS.md § Behavior Rules — Always #13.
gh issue create --label <class> --title "..." --body "..."
```

## Census queries — establish completeness, never count a page (binding)

Every `gh <noun> list` returns ONE page — `--limit` defaults to 30 — with no truncation marker and exit 0, so `--json number --jq 'length'` faithfully counts a silently capped page. Measured 2026-09-06 (GHI #972): the default form returned `30` against a true open count of 44, the handoff chain booked that page size as the queue three times, and the "re-derive the count" step it carried was the same capped command.

- **Scoped search (bounded by design).** `gh issue list --search "ADR-X.Y.Z" --state open` and `/ghi-author` Step 0's `--limit 20` queries answer *"what is in the first N matches"*. They may support *"no match in the first N"*; they can never support *"no such issue exists"* — a completeness claim needs the total below.
- **Count.** Read the authoritative total, never a page length: `gh api -X GET search/issues -f q='repo:<owner>/<repo> is:issue is:open' --jq '.total_count'`. Treat `incomplete_results: true` on that response as *no count obtained* — re-run or say so; never book the number.
- **Inventory.** Retrieve every page — `gh api --paginate 'repos/<owner>/<repo>/issues?state=open&per_page=100' --jq '.[] | select(.pull_request == null) | .number'` — or verify the population: a `gh <noun> list --limit N` result is complete only when it returns fewer than N rows AND its length equals the total above. A result whose length equals its `--limit` is a truncated page.
- **An explicit `--limit` alone is insufficient.** `--limit 200` moves the failure threshold from 30 to 200 and stays silent past it.
- **Book the method beside the figure** (`41 by search total_count`), so the next reader can tell a measurement from a page.

## Prohibited without explicit approval

- Repository/org settings mutations
- Secret/token management
- Force pushes
- Merging PRs without explicit human authorization

## Cross-repo filing

Defects against gzkit-owned surfaces (`gz <verb>`, `.gzkit/`, `src/gzkit/`, `gzkit.<module>`) filed from consuming repos MUST go to `tvproductions/gzkit` via `gz issue file`. The wrapper auto-stamps provenance, validates surface references, and hard-rejects bodies referencing no gzkit surface. Consumer-repo-only defects go to the consumer's tracker.

Operator PII: the wrapper stamps only repo slug + gz version, never operator email.
