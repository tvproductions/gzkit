# Plan — OBPI-0.0.20-02-fold-agent-contract: Fold `agent-contract.md` into AGENTS.md / CLAUDE.md / rationale doc

**OBPI:** `OBPI-0.0.20-02-fold-agent-contract`
**Parent ADR:** `ADR-0.0.20-agent-rule-placement-invariant`

## Context

`.gzkit/rules/agent-contract.md` is a 213-line rule file scoped `paths: "**"`,
meaning it loads into every turn on every code path. ADR-0.0.20 established the
agent-rule placement invariant: unscoped rules that aren't mechanical enforcement
points belong in `AGENTS.md` (persistent contract), `CLAUDE.md` (Claude-specific
addendum), or a governance rationale doc (pedagogy) — not in `.gzkit/rules/`.

OBPI-0.0.20-01 landed the validator and the three-entry allow-list that keeps
`agent-contract.md`, `attestation-enrichment.md`, and `defect-fix-routing.md`
allowed while they await migration. This OBPI (02) removes the first of the
three. After it, `gz validate --unscoped-rules` passes with two allow-list
entries remaining.

**Lane:** Lite. Governance/doc content migration + one allow-list edit + one
new test module + sync regeneration. No CLI contract, schema, or runtime
change.

**Prerequisites verified:** `gz validate --unscoped-rules` exits 0 today;
manifest has three allow-list entries; `.gzkit/rules/agent-contract.md` exists
(213 lines).

## Migration map (semantic dedupe)

Source-file sections and their destinations:

| agent-contract.md content | Already in AGENTS.md? | Destination |
|---|---|---|
| Ownership table (invariants 1–6) | **Yes** — § Prime Directive items 1–6 (prose form, canonical wording) | Drop — no duplication |
| Craftsmanship 6a / 6b / 6d / 6e / 6f | **Yes** — § DO IT RIGHT items 1/2/4/5/6 | Drop — no duplication |
| Craftsmanship 6c (defect-fix-routing) | **No** | AGENTS.md § DO IT RIGHT — add as new item 7 |
| Craftsmanship 6g (verify runtime surface, GHI #263) | **No** | AGENTS.md § DO IT RIGHT — add as new item 8 |
| Craftsmanship 6h (quote rules verbatim, GHI #261) | **No** | AGENTS.md § DO IT RIGHT — add as new item 9 |
| Rationale for 6g/6h (Lindsey 2025) | **No** | **rationale.md § Rationale for 6g/6h** |
| Process invariants 7–10 | **Yes** — § Behavior Rules Always 1–4 | Drop — no duplication |
| Invariant 10a (skill-tool-invoke-same-turn) | **No** (Claude-specific — names `EnterPlanMode`) | **CLAUDE.md § Claude Code addendum** |
| Judgment invariant 11 (<90% ask human) | **Yes** — § Behavior Rules Always #7 | Drop — no duplication |
| Judgment 12 (surface assumptions) | **No** | AGENTS.md § Behavior Rules Always — add |
| Judgment 13 (STOP on inconsistencies) | **No** | AGENTS.md § Behavior Rules Always — add |
| Judgment 14 (push back on flawed plans) | **No** | AGENTS.md § Behavior Rules Always — add |
| Efficiency 15, 16 | **Yes** — § Behavior Rules Always #5, #6 | Drop — no duplication |
| Do-not § TDD discipline | Source rule is `.gzkit/rules/tests.md` (scoped, canonical) | Drop — source rule is authoritative |
| Do-not § Data models | Source rule is `.gzkit/rules/models.md` | Drop |
| Do-not § Surface sync | Source rule is `.gzkit/rules/skill-surface-sync.md` | Drop |
| Do-not § Documentation covenant | Source rule is `.gzkit/rules/gate5-runbook-code-covenant.md` | Drop |
| Do-not § Pipeline lifecycle | **No mirror in AGENTS.md** — this is the "Pipeline" subsection the brief REQ-2 names | AGENTS.md § Behavior Rules Never — add compact restatement |
| Do-not § OBPI completion | Source is OBPI brief template | Drop |
| Do-not § ADR closeout | Source is closeout skill | Drop |
| Do-not § ADR creation | Source is adr-create skill | Drop |
| Do-not § State doctrine | **No mirror in AGENTS.md** — this is the "Source-of-truth" subsection the brief REQ-2 names | AGENTS.md § Behavior Rules Never — add compact restatement |
| Do-not § Storage tiers | Source is `docs/governance/storage-tiers.md` | Drop |
| Do-not § Architectural boundaries | **Yes** — AGENTS.md (embedded via agents.local.md) § Architectural Boundaries | Drop |
| Anti-pattern canon (vibe-coding list) | **Yes** — currently in AGENTS.md § DO IT RIGHT subsection | **Move to rationale.md § Anti-pattern canon** (extract from AGENTS.md) |
| TASK-driven workflow binding | **Yes** — currently in AGENTS.md § DO IT RIGHT subsection | **Move to rationale.md § TASK-driven workflow** (extract from AGENTS.md) |
| Attribution footer | N/A | Drop (skill catalog doesn't need a rule-file attribution) |

**Net effect on AGENTS.md line count:** +~25 lines added (6c/6g/6h, 12/13/14,
Pipeline-lifecycle block, State-doctrine block), -~65 lines removed (anti-pattern
canon + TASK-driven workflow extracted to rationale.md). AGENTS.md net shorter.

**Net effect on per-turn preamble:** -213 lines (the full `agent-contract.md`
no longer loads via `paths: "**"`). AGENTS.md stays authoritative.

## Inbound-reference rewrite targets (Bucket 1 — live)

Grep returned these files referencing `agent-contract.md` or
`agent_contract.instructions.md`. Mirrors (`.claude/**`, `.github/instructions/**`,
`.agents/**`, `.github/skills/**`) regenerate via sync; do not hand-edit.

Live files to rewrite:

1. `AGENTS.md` — line 22 refers to `.gzkit/rules/agent-contract.md` § Judgment
   (#11–14) and § Craftsmanship — DO IT RIGHT (#6a–6e). Rewrite to point at
   `AGENTS.md § Behavior Rules Always` + `AGENTS.md § DO IT RIGHT` (self-reference
   since content now lives in same file).
2. `CLAUDE.md` — no current reference; only receives new 10a addendum text.
3. `.gzkit/skills/gz-justify/SKILL.md` — update citation target.
4. `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — update citation target.
5. `.gzkit/rules/tests.md` — update citation target (§ Craftsmanship references).
6. `.gzkit/rules/gh-cli.md` — update citation target.
7. `.gzkit/rules/defect-fix-routing.md` — update "Related" section.
8. `.github/AGENTS.md` — update if references present.
9. `docs/design/adr/AGENTS.md` — update if references present.
10. `tests/AGENTS.md` — update if references present.
11. `docs/governance/advisory-rules-audit.md` — scorecard entry for the rule
    must reflect removal (entry either removed or marked "consolidated into
    AGENTS.md"). **Verify the advisory-scorecard validator accepts this shape**
    before editing — may be automatic, may need the scorecard row kept with a
    status change.
12. `docs/governance/governance_runbook.md` — update citation target.
13. `docs/user/runbook.md` — update citation target.
14. `RELEASE_NOTES.md` — historical entries are Bucket 3 (leave untouched);
    only forward-looking/unreleased sections get updated. Inspect first.
15. `src/gzkit/templates/agents.md` — this is the **template** used by
    `gz init` to scaffold new project `AGENTS.md` files. If it contains a
    reference to `.gzkit/rules/agent-contract.md`, the template would propagate
    a dangling reference to new repos. Update if present; leave if reference
    is to AGENTS.md sections (which would still resolve).
16. `.gzkit/manifest.json` — remove the first allow-list entry (agent-contract).

**Historical (Bucket 3) — left untouched per brief Denied Paths:**
- `.claude/plans/adaptive-squishing-lovelace.md`, `eager-snacking-perlis.md`,
  `spicy-leaping-eich.md` (session plan snapshots)
- `docs/design/adr/foundation/ADR-0.0.20-*/obpis/OBPI-0.0.20-0{1,3,4,5}-*.md`
  (these legitimately reference `.gzkit/rules/agent-contract.md` because they
  describe the migration — their text is historical)

## Implementation increments (TDD rhythm)

Each increment is one test, one observed RED, minimum code to GREEN, next.

### Increment 1: Test scaffold + frontmatter assertion (RED → GREEN)

- Create `tests/governance/test_agent_contract_fold.py` with class
  `TestAgentContractFold(unittest.TestCase)`.
- Test 1 (derived from REQ-0.0.20-02-05): `test_agent_contract_rule_file_deleted`
  — asserts `.gzkit/rules/agent-contract.md` does not exist.
- `@covers("REQ-0.0.20-02-05")` decorator.
- Observe RED (file still exists), then delete the file → GREEN.

### Increment 2: AGENTS.md migrated invariants (RED → GREEN)

- Test 2 (REQ-0.0.20-02-01, REQ-0.0.20-02-02): `test_agents_md_contains_migrated_invariants`
  — asserts AGENTS.md contains semantic markers for the unique migrated items:
  - "6c" + "defect-fix-routing" (craftsmanship invariant extension)
  - "6g" + "runtime surface" (or equivalent REQ-safe phrase)
  - "6h" + "quote the rule" + "verbatim"
  - Judgment 12: "Surface assumptions explicitly"
  - Judgment 13: "STOP, name confusion, present tradeoff"
  - Judgment 14: "Push back"
  - "Do not summarize after Stage 2 or 3 and stop" (Pipeline lifecycle don't)
  - "Do not read YAML frontmatter" (State doctrine don't)
- `@covers("REQ-0.0.20-02-01", "REQ-0.0.20-02-02")`.
- Observe RED, then edit AGENTS.md to add the content → GREEN.

### Increment 3: CLAUDE.md 10a placement (RED → GREEN)

- Test 3 (REQ-0.0.20-02-03): `test_claude_md_carries_10a_and_agents_md_does_not`
  — asserts `CLAUDE.md` contains "invoke it in the same turn" (or canonical
  10a phrasing) under a heading at/after "Claude Code addendum", AND AGENTS.md
  does NOT contain that exact Claude-specific phrase.
- `@covers("REQ-0.0.20-02-03")`.
- Observe RED, edit CLAUDE.md → GREEN.

### Increment 4: Rationale file creation (RED → GREEN)

- Test 4 (REQ-0.0.20-02-04): `test_rationale_md_has_three_named_sections`
  — asserts `docs/governance/agent-contract-rationale.md` exists and contains
  headings matching "Anti-pattern canon", "TASK-driven workflow",
  "Rationale for 6g" (or "Rationale for 6g/6h"), AND each section cites its
  origin GHI (#157, #160, #261/#263 respectively).
- `@covers("REQ-0.0.20-02-04")`.
- Observe RED, create the file with content extracted from AGENTS.md (anti-pattern
  canon + TASK-driven workflow) and from the legacy rule (6g/6h rationale) → GREEN.

### Increment 5: Remove extracted pedagogy from AGENTS.md

- Edit AGENTS.md to remove the "### The anti-pattern canon" subsection and
  the "### TASK-driven workflow (binding)" subsection, replacing each with
  a one-line pointer: `See docs/governance/agent-contract-rationale.md § …`.
- Re-run Test 2 (still GREEN — it checks only for migrated-invariant markers,
  not the pedagogy text).

### Increment 6: Manifest allow-list edit (RED → GREEN)

- Test 5 (REQ-0.0.20-02-06): `test_manifest_allowlist_has_two_entries`
  — load `.gzkit/manifest.json`, assert `rules.unscoped_allowlist` has exactly
  two entries and neither is `agent-contract.md`.
- `@covers("REQ-0.0.20-02-06")`.
- Observe RED (three entries), remove the agent-contract entry → GREEN.

### Increment 7: Inbound-reference rewrites (no new test — manual sweep)

- Rewrite references across the 14+ live files enumerated above.
- Run `grep -l 'agent-contract\.md' <bucket-1 set>` — should return empty.
  Historical Bucket-3 files may still match and that is correct.

### Increment 8: Sync regeneration + quality gates

- `uv run gz agent sync control-surfaces` — regenerates mirrors; the mirror
  files for `agent-contract` should disappear.
- `uv run gz validate --unscoped-rules` → exit 0 (REQ-09)
- `uv run gz validate --all` → exit 0 (REQ-10)
- `uv run gz lint` → clean
- `uv run gz typecheck` → clean
- `uv run mkdocs build --strict` → clean (REQ-11)
- `uv run -m unittest tests.governance.test_agent_contract_fold -v` → all pass (REQ-12)
- `uv run gz covers OBPI-0.0.20-02 --json` → `uncovered_reqs == 0` (Stage 3 parity gate)

## Critical files

**Modified:**
- `AGENTS.md` (+~25 / -~65 lines net; add 6c/6g/6h, 12/13/14, Pipeline + State
  doctrine "Do not" blocks; extract anti-pattern canon + TASK-driven workflow
  to rationale.md)
- `CLAUDE.md` (+~5 lines; add 10a to Claude Code addendum)
- `.gzkit/manifest.json` (-1 allow-list entry)
- `.gzkit/skills/gz-justify/SKILL.md` (reference rewrite)
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (reference rewrite)
- `.gzkit/rules/tests.md` (reference rewrite)
- `.gzkit/rules/gh-cli.md` (reference rewrite)
- `.gzkit/rules/defect-fix-routing.md` (reference rewrite)
- `.github/AGENTS.md` (if references present)
- `docs/design/adr/AGENTS.md` (if references present)
- `tests/AGENTS.md` (if references present)
- `docs/governance/advisory-rules-audit.md` (scorecard row handling)
- `docs/governance/governance_runbook.md` (reference rewrite)
- `docs/user/runbook.md` (reference rewrite)
- `RELEASE_NOTES.md` (forward-looking sections only)
- `src/gzkit/templates/agents.md` (if template carries a dangling reference)

**Created:**
- `docs/governance/agent-contract-rationale.md` (three named sections)
- `tests/governance/test_agent_contract_fold.py` (five test methods, all
  `@covers`-decorated)

**Deleted:**
- `.gzkit/rules/agent-contract.md` (canonical; mirror auto-cleaned by sync)

## Reused utilities

- `@covers(REQ-...)` decorator — standard test decoration pattern per
  `.gzkit/rules/tests.md`.
- `unittest.TestCase` + `pathlib.Path` — no new dependencies per REQ-13.
- `json.loads(Path(...).read_text(encoding="utf-8"))` — standard manifest
  load pattern.
- Existing `gz agent sync control-surfaces` command — no modification needed,
  just invoked.
- Existing `gz validate --unscoped-rules` validator (landed in OBPI-01) —
  verifies the post-migration state.

## Verification (end-to-end)

```bash
# Pre-migration snapshot
wc -l .gzkit/rules/agent-contract.md
uv run gz validate --unscoped-rules  # exit 0, 3 allowlisted

# Per-increment TDD (run after each Red/Green pair, not batched)
uv run -m unittest tests.governance.test_agent_contract_fold -v

# After Increment 8 — final gates
test ! -f .gzkit/rules/agent-contract.md
test ! -f .claude/rules/agent-contract.md
test ! -f .github/instructions/agent_contract.instructions.md
test -f docs/governance/agent-contract-rationale.md
grep -q "quote the rule" AGENTS.md
grep -q "invoke it in the same turn" CLAUDE.md
grep -q "Anti-pattern canon" docs/governance/agent-contract-rationale.md

uv run gz validate --unscoped-rules     # exit 0, 2 allowlisted
uv run gz validate --all
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run gz covers OBPI-0.0.20-02 --json  # uncovered_reqs == 0
```

## Risk + mitigation

- **Risk:** `gz validate --advisory-scorecard` fails after removing the rule,
  because the scorecard expects a row for every `.gzkit/rules/` file.
  **Mitigation:** read the scorecard doc and validator before edit — either
  the row is removed automatically (validator iterates rule files) or the row
  is kept with status "consolidated" (verify by running `gz validate
  --advisory-scorecard` after file deletion but before final sync).
- **Risk:** `mkdocs build --strict` breaks on a rewritten internal link.
  **Mitigation:** run after each batch of rewrites, not just at the end.
- **Risk:** `gz init` template has a dangling reference. **Mitigation:**
  Increment 7 explicitly checks `src/gzkit/templates/agents.md`.
- **Risk:** Ceremony-template skills (under `.gzkit/skills/`) reference the
  legacy rule path in their instructional body. **Mitigation:** sync handles
  mirror regeneration, but canonical skill bodies need the rewrite — covered
  in Increment 7.
