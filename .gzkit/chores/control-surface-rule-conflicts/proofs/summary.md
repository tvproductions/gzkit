# Rule-conflict assessment — 2026-10-10

Persona: main-session. Run under maintenance visit E of the R&D run `renewing-vows`, admitted by the operator ('admit visit E'). Audit population: every Markdown file under `.gzkit/rules/`, plus root `AGENTS.md` and `CLAUDE.md`: 29 files, 406 unordered pairs.

## Counts

| Measure | Value |
|---|---|
| Files in scope | 29 (28 in September; `weaponeering.md` is new) |
| Files changed since the 2026-09-19 baseline | 11 |
| Pairs re-reviewed | 253 |
| Pairs carried unchanged | 153 |
| Concrete conflicts open | **0** |
| Rows closed this period | 2 (R01, F1) |
| Candidates, unproven | 7 |

Severity of open rows: blocking 0, episodic 0, theoretical 0. There is no top five to rank.

## What changed

**R01 is closed.** The one conflict September left open, `chores.md` against `skill-surface-sync.md` on which chore copy is canonical, was settled by operator ruling on 2026-09-28 (`chores.md` 0.6.0, GHI #1044). Both rules now name `.gzkit/chores/` the authoring source.

**F1 was opened and closed today, and this session caused it.** The diet landing of 2026-10-10 lifted two Gate Covenant paragraphs out of `AGENTS.md` as rationale. Each carried one binding sentence, and `tests.md`, `data/check_step_scopes.json`, the `gz-check` skill and a test docstring cite them at that section. The sentences are restored verbatim as one bullet; the rationale stays in `docs/governance/agent-contract-rationale.md`. The diet's net saving is 1,653 bytes, not the 1,795 reported at the landing.

**One leftover line repaired.** `model-selection.md` 0.7.1 corrects a Do Not line that this session's 0.7.0 edit left contradicting the rule's own claim 4.

## Follow-up list

1. **`gh-cli.md` allowlist completeness.** The § Allowed commands block omits `gh issue view`, `gh issue edit` and the `gh api` forms the rule itself prescribes, and three skills step outside it (reachability audit, rows B08 and B25). One operator ruling: is the block exhaustive, and if so which verbs join it. Sized for a direct rule fix.
2. **`model-selection.md` tier mapping.** `haiku` and `sonnet` map to superseded ids. Route through `frontier-model-card-currency`.
3. **GHI #943** still carries the chore-scope candidate; nothing new closes it.

## Evidence and limits

- `rule-inventory.md`: path, version, line and byte counts, SHA-256 and headings per file, hashed after this run's two repairs.
- `current-pair-review.json`: 406 pair records, each naming whether it was re-reviewed or carried.
- `conflict-matrix.md`: the two closed rows with resolvable evidence, the in-file findings and the seven candidates.
- `archive/2026-09-19/`: the September proofs, unchanged.

One reviewer did this pass; the September pass used three independent partitions. The review was diff-driven: a pair between two unchanged files was not re-read, on the ground that neither side moved. A contradiction that existed in September and was missed then is still missed.

This audit reads rule text against rule text. It says nothing about whether an agent follows a rule, and the session that ran it is evidence of the gap: it ran a bare `python3` forty times against the root contract's `uv run` rule, and nothing in the rule set or the hook layer observed it. That finding is recorded in the permission-consent audit of the same visit.
