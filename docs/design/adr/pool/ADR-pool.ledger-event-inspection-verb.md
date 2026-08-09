---
id: ADR-pool.ledger-event-inspection-verb
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.ledger-event-inspection-verb: Ledger event-inspection read verb

## Status

Pool

## Intent

**The ledger is the system-of-record and every write goes through a governed verb, but reads have no verb at all.** `CLAUDE.md` § Compact Instructions states it plainly — *"The ledger (`.gzkit/ledger.jsonl`) is the system-of-record"* — and `gz` offers no way to ask it a question. The only answer to *"did this ceremony emit its event?"* is a raw file read:

```bash
grep "composition_candidate_emitted" .gzkit/ledger.jsonl
```

That idiom is canon (`.claude/rules/token-block-discipline.md` § Audit Path, and the doctrine expansion it points at), so it works. It is nonetheless a raw read against a Layer-2 source of truth with no schema awareness, no event-type validation, and no cross-platform guarantee — `grep` is not present by default on Windows, which `.claude/rules/cross-platform.md` treats as co-equal with macOS and Linux.

**The demand is evidenced, not hypothesized.** Three independent governed surfaces, authored at different times by different passes, each reached for the same verb that has never existed (`gz ledger tail --event <name>`):

| Surface | Reference |
|---|---|
| `docs/user/runbook.md` | `uv run gz ledger tail --event rendition_advisor_verdict` |
| `docs/user/manpages/content.md` | `uv run gz ledger tail --event rendition_advisor_verdict` |
| `.gzkit/skills/gz-content-compose/SKILL.md` | `gz ledger tail --event composition_candidate_emitted` |

Three surfaces converging on one invented shape is a design signal about the affordance, not three authors' slips. The dead references themselves were repaired under GHI #745, which widened `gz validate --cli-alignment` to read skills and fenced blocks; this entry is about the **missing affordance**, which that repair deliberately did not supply.

**Why pool rather than a direct fix (routing, operator-ruled 2026-08-09).** GHI #747 is labeled `enhancement` and self-describes as new feature work. Operator canon grants direct-repair authority to *defect* repair — *"those criteria gate planned ADR work, not defect repair"* — so it does not reach an enhancement. A new subcommand is a CLI contract change, which `.claude/rules/cli.md` § Heavy Lane Trigger and AGENTS.md § Defect-fix routing both send to OBPI ceremony; and an OBPI cannot be headless (operator canon: *"There is no such thing as a 'headless' OBPI: every OBPI is ALWAYS attached to a parent ADR"*), while no existing ADR promises a ledger read verb. Pool is therefore the only available home, and `only one feature at a time` parks it behind `ADR-0.35.0-canon-entry-corpus-landing`.

**ADR-worthiness (per `docs/governance/pool-curation.md` § Is it ADR-shaped at all?).** Hard to reverse — a registered verb is a contract callers bind to. Surprising without context — the obvious shape (a new `gz ledger` namespace) is not clearly right, since `gz state` already reads the ledger. A real tradeoff — see § Alternatives Considered, where the leading candidates genuinely compete.

## Decision

*(To be authored at promotion — this entry records the problem and the option space, not the choice.)*

The scope a promoter would be committing to:

1. A **read-only** ledger query surface: filter by event type, and plausibly by ADR/OBPI id and time window. Read-only is a boundary, not a convenience — `AGENTS.md` § Behavior Rules — Never #2 forbids modifying the ledger outside gzkit commands, and this verb must never become a second write path.
2. Schema-aware output: typed events via `gzkit.events`, so an unknown `--event` value is a named refusal rather than an empty result. An empty grep and a misspelled event name are indistinguishable today, and that is half the defect.
3. `--json` / `--plain` output contracts per `.claude/rules/cli.md`, so the verb is usable from scripts without re-inventing the grep.
4. Manpage, command doc, and index coverage (`gz cli audit` fail-closes without them), plus a wielding skill (`gz validate --skill-alignment` Invariant 1).
5. Repointing the three surfaces above from the grep idiom onto the real verb, and the § Audit Path doctrine with them.

## Alternatives Considered

**(a) New `gz ledger` verb with subcommands.** What all three surfaces assumed. Clearest namespace for a Layer-2 read surface, and leaves room for later read-only siblings. Cost: a new top-level verb is the largest contract surface of the options, and gzkit's verb catalog is already wide.

**(b) Extend `gz state` with an `--event` filter.** `gz state` already reads the ledger — its help is *"Query artifact graph, blockers, and readiness from ledger"* — and it carries `--json`, `--blocked`, `--ready`, `--include-withdrawn`, `--repair`, `--full`. Cheapest surface addition. Cost: `gz state` answers *artifact-graph* questions, and raw event inspection is a different question wearing the same noun; conflating them makes the verb's contract harder to state than either half. Note this alternative is still a CLI contract change and still Heavy lane — cheaper is not free.

**(c) Portable-read documentation only.** Decline the verb; keep the grep idiom and fix only the genuine gap by documenting a portable read for Windows. Smallest possible change. Cost: leaves the three-surface convergence unanswered and leaves a Layer-2 read path with no schema awareness, so a misspelled event type keeps returning silence that reads as a clean result.

**(d) Do nothing.** The idiom is canon and works on two of three co-equal platforms. Recorded for completeness; rejected as the reason this entry exists.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

**Provenance.** Discharges GHI #747. Sibling cuts of the same root family — *a governed surface asserting where something lives while the thing lives elsewhere or nowhere* — are GHI #778 (rule-document cut, closed `fixed`) and GHI #779 (guard-blindness cut). Each escaped a different validator scope, which is what made them siblings rather than duplicates.
