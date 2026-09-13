---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-13T02:48:06Z'
agent: claude-code
session_id: 89fe194c-e710-4a42-a2c2-c4dd7c0bbc7d
continues_from: .gzkit/handoffs/20260912T235557Z-rnd-alignment-chores-rnd-reconstructed.md
---

## Current State Summary

Session 89fe194c resumed `20260912T235557Z-rnd-alignment-chores-rnd-reconstructed.md` (step 1 had already been done by session 7bf35675, commits `fd6ededf2` and `44b8f4a98`). The operator ruled step 2 via one GHI, so the chore class system work order was filed as GHI #999, and step 1 of its ratified order (the registry declaration schema) landed in `f1c9b0e59`: `ChoreDeclaration` in `src/gzkit/commands/chores_declaration.py` with class, rung, idempotent, staleness, remediation, nonAuthority, governingRule. A partial or malformed declaration fails closed; an absent one is announced (`gz chores list` reports 40 of 40 undeclared) and still runs.

The operator then called the session report sloppy for listing three found defects as notes. All three were closed or routed in-session: the design record's chore lists were re-measured by reading every CHORE.md and corrected (`1fc04aef2`); the rulings-store lag was traced to its cause and filed as GHI #1000; the exit-code disagreement was traced to a three-surface canon conflict and filed as GHI #1001. Found and fixed along the way: CLI error text rendered as Rich markup, deleting bracketed spans (`670e018cc`); the same class in 12 more print sites via widening GHI #944's roster (`2081eab69`); handoff rulings, resume preview and create refusal printing operator-verbatim text through markup, and a rulings search miss reported as an empty store (`a432a5877`); stale SLOC caps in module-sloc-cap-radon and a dangling chore reference in skill-trigger-testing (`1fc04aef2`). Chore metadata duplication (CHORE.md vs acceptance.json / registry) filed as GHI #1002. gz check passed all 61 steps before each commit set.

## Important Context

- Canon settles the exit-code direction only partly: `.gzkit/rules/cli.md` and attested REQ-0.0.4-02-07 say 2 = System/IO; `docs/design/cli-standards-v3.md` (named canonical) says 2 = usage error and its Document status marks the section met. That is a conflict between canon surfaces, so it is the operator's ruling, not an agent's (GHI #1001).
- GHI #1000 is a design ruling too: booking a handoff's own rulings at authoring changes who inherits (`_compose_settled` records "changing the transport must not change who inherits"); the alternative is a read-side-only lookup fix.
- This handoff links to the resumed handoff with --continues-from, which is what carries its 20 operator rulings into `.gzkit/handoffs/rulings.jsonl`; before it, 20 of 20 were absent from the store.
- Chore lists (authoritative now in `docs/governance/chore-class-system.md` § The measured state): stop-at-data firm cli-contract-governance, evidence-integrity-audit, skill-trigger-testing; borderline dependency-currency, control-surface-rule-vs-check-drift. Self-contradictory firm repository-structure-normalization, skill-command-doc-parity; ambiguous ledger-vocabulary-inertness.
- Chore declaration keys are camelCase to match the registry; remediation categories use CSAF underscore spelling.
- The markup ratchet (`tests/policy/test_rich_markup_escaping.py`) is roster-keyed and declares that limit; widening the roster is the class fix, not a parallel check.

## Decisions Made

- [operator-ruled] Resume ruling: "Step 2 via one GHI (Recommended)" — file one work-order GHI for the chore class system (#999), GHI #936 stays the order for the status verb, then start the registry schema.
- [operator-ruled] Licenses at the schema step: "rung + idempotent (Recommended)" — rung carries the writing license; a required boolean idempotent carries the scheduling license.
- [operator-ruled] Authorization expiry: "Not now (Recommended)" — no expiry field; recorded, not adopted.
- [operator-ruled] Rollout: "Warn, flip at step 5 (Recommended)" — an undeclared chore is announced and still runs until the per-chore declarations land, when absence flips to refusal.
- [agent-chose] Split the CLI markup-escape defect into its own commit rather than folding it into the chore schema commit, since it is a different surface.
- [agent-chose] Routed the exit-code conflict and the rulings lag to GHIs with an operator ruling required, because each resolves a disagreement between canon surfaces or prior rulings; fixed directly everything canon already decided.

## Immediate Next Steps

1. Put GHI #1001 and GHI #1000 to the operator as the two rulings they carry, then repair whichever arm is ruled.
2. GHI #999 step 3: the class-conformance validator (a CHORE.md whose workflow contradicts its declared rung fails), reading criteria and version from the authority GHI #1002 settles.
3. GHI #936 (step 2): `gz chores status` rendering current / due / overdue / paused from the new staleness declaration, announced in `scripts/session_orientation.py`.
4. GHI #1002: reconcile CHORE.md criteria and version with acceptance.json and registry.json under one declared authority, with a witness.

## Pending Work / Open Loops

- GHI #999 steps 4-6: README class and rung semantics, per-chore declarations with the absence-to-refusal flip, the suppression rule with its witness.
- GHI #1000 awaiting operator ruling (write-side booking versus read-side lookup).
- GHI #1001 awaiting operator ruling (usage error 1 per cli.md and the attested REQ, or 2 per the spec).
- GHI #1002 open: 17 CHORE.md acceptance tables and 7 versions disagree with their JSON authorities.
- Handoff step 3 (alignment arm, rule-chore Pass D) and step 4 (R&D skill design, fresh session) from the resumed handoff remain unworked.
- The rendition-lineage advisory for `NCSurface.md/root` in gz check is the QC negative-control fixture, present before this session.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
uv run gz handoff rulings --search "class seams"
uv run gz chores list
uv run -m unittest tests.commands.test_chores_declaration tests.policy.test_rich_markup_escaping tests.test_handoff_cli tests.cli.test_error_boundary_markup
gh issue view 999 --json state,title
gh issue view 1000 --json state,title
gh issue view 1001 --json state,title
gh issue view 1002 --json state,title
```

Expected at authoring: 0 0 after sync; the class seams search returns the chore-class ruling now that this handoff links its predecessor; chores list ends with 40 of 40 chores carry no class declaration; tests green; all four GHIs OPEN.

## Evidence / Artifacts

- `src/gzkit/commands/chores_declaration.py` — ChoreDeclaration model and parser (GHI #999).
- `tests/commands/test_chores_declaration.py` — declaration load, refusal table, announcement tests.
- `docs/governance/chore-class-system.md` — licenses reconciled, field table as landed, measured state corrected.
- `src/gzkit/chores/README.md` — Class Declaration section.
- `tests/policy/test_rich_markup_escaping.py` — widened free-text roster.
- `tests/cli/test_error_boundary_markup.py` — CLI boundary escape test.
- `tests/test_handoff_cli.py` — rulings search-miss and verbatim rendering tests.
- Commits `f1c9b0e59`, `670e018cc`, `2081eab69`, `a432a5877`, `1fc04aef2`.
- GitHub issues #999, #1000, #1001, #1002; comments on #936, #944, #997, #808, #810, #717.

## Settled Rulings

823 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
