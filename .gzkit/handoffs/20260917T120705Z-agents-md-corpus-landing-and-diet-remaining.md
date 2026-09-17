---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-17T12:07:05Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260917T015645Z-rnd-double-diamond-frame-and-adr-lifecycle-defects.md
---

## Current State Summary

Operator-on-demand run of the `instructions-files-diet` chore under GHI #921, 2026-09-17. Root `AGENTS.md` was reviewed part by part (22 parts, every part operator-ruled), rewritten in plain terse wording, and landed through the corpus: 48,511 B to 19,112 B. Every content line is a live invariant corpus entry; `gz content own` flipped 8 sections to corpus-owned; generated-mode `gz content compose` is byte-identical to the committed rendition; the unowned floor fell 6,005 B to 32 B (the two bare H1 heading lines, which no verb can own — GHI #1018, filed this session). Full `uv run gz check` passed on the staged tree (third run), commit `8ecb176f0` landed on main with `Task: TASK-instructions-files-diet-#921`, and `uv run gz git-sync --apply` pushed it (`b8bc4881d` carries the post-commit ledger row). main is level with origin/main. Only root AGENTS.md is done: CLAUDE.md, governance-core, the path-scoped rules, the skill catalog, the budget `_doc` diary and the whole of Phase C (model-card refresh) are untouched.

## Important Context

Workflow fronts (campaign `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, selected by `data/active_campaign.json`): this session touched only the GHI-triage front (GHI #921 advanced, GHI #1018 filed and cross-linked on #978); the handoff, ADR/OBPI-campaign and R&D fronts were not observed and need verification through `gz-status`. The 2026-09-12 context audit at `docs/governance/context-audit-2026-09-12/` is the review packet this run should have opened with; its proposals supplied most of the landed wording, and D09, D10 and D14 (approved 2026-09-12, lost to a concurrent checkout restore) are now landed. Mechanics a successor needs: `gz content remember` accepts only H2 sections (AgentContract pillars), so all content was moved out of the two H1 sections; entries render in append order, so a changed bullet is retired and the whole run of bullets after it recaptured to keep order; bullet entries carry their own `- ` marker and must be passed as `--text=<value>` because argparse reads a leading dash as a flag; `gz content commit` does not promote the candidate lineage file, so `--rendition-lineage` reports the 20 owned sections as ungraded until OBPI-0.35.0-07 (Draft, operator-initiated) lands. `gz validate --bullet-retention` binds Mechanical and Promotable scorecard rows to exact per-turn wording; rows 15 and 59 were re-pointed. Tests that asserted literal AGENTS.md wording were re-derived (seven tests, six files); canon also regained four tokens attested REQs need (Gate 5 is universal with ADR-0.0.36, GHI #342 and its witness; backticked lite and heavy with Gate 3 and Gate 4; CLOSED to new authoring; the REQ-coverage gate label). Measured and not yet acted on: on Claude the same rule text is delivered twice on first edit under a path, because nested `CLAUDE.md` files import nested `AGENTS.md` (GHI #923) while path-scoped `.claude/rules` mirrors also load; and `task-discovery.md` is scoped to `.gzkit/**` and `docs/design/adr/**` although its version note says `src/gzkit/**`.

## Decisions Made

- [operator-ruled] Verbatim: "we will never, ever, ever run a lone/orphan obpi" — the floor-amendment option offered as an OBPI with no Feature Checklist item was withdrawn.
- [operator-ruled] Verbatim: "i want to review these, part by part, as rendered, to backport changes to canon entries" and "you need to SHOW me your edits, not give me these brief clips" — proposals are delivered as the complete proposed text plus a word-level redline per part.
- [operator-ruled] Verbatim: "use the advise from pocock and read the whole thing, onboard some or all if useful" — onboarded as `agents-md-map-doctrine.md` 0.12.0 § Writing levers.
- [operator-ruled] Verbatim: "we won't have evidence other than considering the mechanical part you mention, let's go section by section" — no behavioral A/B probe; each part was judged on its mechanical witnesses.
- [operator-ruled] Verbatim: "every section should be corpus sourced and rendered from corpus" and "nothing should be hand carried" — landing architecture; also the attestation text of the rendition commits.
- [operator-ruled] The Operator PII bullet is retained byte for byte ("this needs to be retained"); D11 (read all docs and all code) is kept verbatim; `.gzkit/agents.local.md` is deleted; P13 option A (corrected gate table); P14 A; P15 A; P16 A (canonical invocations move to the `gz-arb` skill); P17 A (precedent criterion dropped); P18 A; P19 to P22 as recommended.
- [operator-ruled] Verbatim: "tests that hardcode to AGENTS.md are bullshit/invalid tests" and ruling "A" — tests pinning old wording were re-derived from the ruled canon instead of restoring the pinned content.
- [operator-ruled] Verbatim: "working with bdd deserves its own gz command but we'll file that for later" — recorded as an insight, not filed.
- [operator-ruled] Verbatim: "claude.md should be a pointer/include of AGENTS.md" and "I think the same audit needs to be applied to other control surfaces that are rendered" — direction for the next surfaces, not yet acted on.
- [agent-chose] Retired every live entry and recaptured the whole ruled document in render order, so generated mode reproduces the rendition byte for byte; rehearsed the full sequence twice on an isolated copy before touching the real corpus.
- [agent-chose] Moved the five Local Agent Rules bullets under Execution Rules and the title tagline under Project Identity, because the capture verb refuses H1 sections; the PII rule thereby gained an invariant floor.
- [agent-chose] Repaired four tokens in canon rather than editing the tests that needed them, where the repair was a label, a citation or a witness name; deferred the dangling `DO IT RIGHT 6a` citation in `agent-failure-modes.md` to the Phase C edit of that file.

## Immediate Next Steps

1. Present these steps to the operator and wait for a ruling; none is authorized by this document.
2. CLAUDE.md as a pointer or include of AGENTS.md: it renders from `.gzkit/templates/claude.md`; show the operator where its three Claude-only blocks (Invariant 10a, Model tuning, Compact Instructions) would go, and surface that `test_claude_md_carries_10a_and_agents_md_does_not` (REQ-0.0.20-02-03) requires 10a to live in CLAUDE.md.
3. Apply the same part-by-part redline audit to `.gzkit/rules/governance-core.md` (always loaded, 8.5 KB), then the path-scoped rules largest first (`tests.md`, `token-block-discipline.md`, `task-discovery.md`, `cli.md`, `skill-surface-sync.md`), including the `task-discovery.md` scope question.
4. Skill catalog proposal: make the eight namespace-router skills user-invoked (`disable-model-invocation: true`), tighten descriptions to trigger phrases, and put to the operator whether `gz-obpi-pipeline` should be user-invoked as a mechanical arm of operator-only initiation.
5. Phase C under GHI #934 and GHI #943: run the `frontier-model-card-currency` chore, consume the Claude Fable 5.1 and Mythos 5.1 System Card (2026-09-01; the PDF exceeds the web-fetch size limit and must be read locally), re-source `CLAUDE.md` § Model tuning and `docs/governance/opus-tuning.md`, and fix the dangling `6a` citation in the same edit of `agent-failure-modes.md`.

## Pending Work / Open Loops

- File through `ghi-author` when the operator calls for it: the Claude double-delivery of nested instruction files (generator in `src/gzkit/rules/__init__.py`); the stale Gate 3 and Gate 4 rows in `.gzkit/templates/agents.md` and its `src/` twin, which every `gz init` scaffolds; a dedicated `gz` verb for BDD work.
- Lift the `_doc` diary out of `data/instructions_files_budget.json` to `docs/governance/`, leaving a one-line pointer; budget values unchanged.
- Widen `agents-md-map-doctrine.md` `paths:` to the canonical authoring surfaces only after that rule is itself trimmed; widening now fans 12 KB into two generated nested AGENTS.md files.
- A sweep of `tests/` and `features/` for remaining assertions against literal AGENTS.md wording (recorded as an insight); the ones still passing pass by coincidence of wording.
- Re-measure the per-turn and on-edit load table against `proofs/baseline-2026-09-17.txt`, run `uv run gz chores run instructions-files-diet` and `uv run gz chores audit --slug instructions-files-diet` to close the chore run, and record the post-trim proof.
- The stop-turn hook's block prose cites an AGENTS.md rule number the rewrite removed; the hook text lives under `src/` and was not edited.
- The prior handoff `.gzkit/handoffs/20260917T015645Z-rnd-double-diamond-frame-and-adr-lifecycle-defects.md` advised five steps on the R&D discussion and GHI #1014 and #1015; none was acted on this session and no ruling on them was booked.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` returns 0 and 0.
- `uv run gz validate --invariant-coherence` exits 0, and `cmp AGENTS.md .gzkit/renditions/AGENTS.md/root.md` is silent.
- `uv run gz validate --rendition-floor-coherence` and `uv run gz validate --rendition-freshness` exit 0.
- `uv run gz content compose AGENTS.md --consumer root` with empty stdin stages a candidate byte-identical to `.gzkit/renditions/AGENTS.md/root.md`.
- `uv run gz validate --bullet-retention` and `uv run gz validate --advisory-scorecard` exit 0.
- `gh issue view 1018 --json state,title` shows the H1-section defect open.

## Evidence / Artifacts

- `.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md` — every operator ruling of the run, verbatim and timestamped
- `.gzkit/chores/instructions-files-diet/proofs/baseline-2026-09-17.txt`
- `.gzkit/chores/instructions-files-diet/proofs/proposed-root-2026-09-17.md`
- `.gzkit/chores/instructions-files-diet/proofs/corpus-operations-2026-09-17.json`
- `.gzkit/chores/instructions-files-diet/proofs/recommendation-2026-09-17.md`
- `.gzkit/corpus/AGENTS.md.jsonl`
- `.gzkit/renditions/AGENTS.md/root.md`
- `.gzkit/ownership/AGENTS.md.json`
- `.gzkit/rules/agents-md-map-doctrine.md`
- `docs/governance/behavior-rules.md`
- `docs/governance/defect-fix-routing.md`
- `docs/governance/rule-version-history.md`
- `docs/governance/advisory-rules-audit.md`
- `.gzkit/skills/gz-arb/SKILL.md`
- `tests/arb/test_unittest_runner_lockstep.py`
- `tests/governance/test_attestation_fold.py`
- `tests/governance/test_defect_fix_routing_fold.py`
- `tests/governance/test_agent_contract_fold.py`

## Settled Rulings

902 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
