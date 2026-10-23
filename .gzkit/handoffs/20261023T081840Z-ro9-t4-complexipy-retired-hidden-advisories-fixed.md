---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-23T08:18:40Z'
agent: claude-code
continues_from: .gzkit/handoffs/20261023T010056Z-ro9-t4-complexity-swap-radon-retired-ghi1183-closed.md
---

## Current State Summary

Safe mode under docs/governance/harbor-pilotage-candidate-2026-10-15.md, MX session 57346836, lease renewed 2026-10-23T01:05Z (24h). 15 acts landed since e8a14e904, all pushed; main is in sync with origin.

1. CI red on 872fb99c8 repaired: lifted rule-banner links (51fc26d19), the scaffold dry-run test's package-name flake (239dadbc1), complexipy's silent -q failure (0515c4526). A pasted diagnosis blamed the NCSurface.md negative-control fixture, twice this session; both times the real cause was a FAILED unit line.
2. RO-9 tranche 4 amended: complexipy retired for a gzkit-owned cognitive-complexity scorer over CPython's ast (682a4003e scorer, 9796dd62f gate and 263-row baseline, 6f0f2a956 retirement from every surface, 29452c0b1 spec amendment).
3. CI red on be15a2c1d (pythonic.md bumped without its advisory Coverage Ledger row) fixed by b6060b95b; CI run 39919274411 then passed on both legs, with windows-latest Lint and Complexity ceiling green for the first time since 25287b8e0.
4. gz check hid every finding a gz validate subprocess demoted under the hangar; 540579297 announces them. The four it exposed were fixed: pythonic.md banner one sentence at 0.5.8 (266be3fbd), the reachability ratchet misreading --catalog (2c23dd1be), scorecard row 51e quoting its rule (36145b59f), two tautological-test rows re-keyed (e7d732c95). gz check now shows no demoted section.

Last action: pushed 504b8ce00; CI run 39922738575 was in progress at writing.

## Important Context

- gz check under an open hangar: a step whose gz validate subprocess demoted a finding now prints under a Demoted by the open MX hangar section (540579297). Before that fix a passing step hid its [MX advisory] line. Read that section after every gz check while the marker is open; an empty one is the only clean reading.
- The per-change gate selects tests from changed .py files only (GHI #1191 ruling). Before pushing any rule, skill, chore or data edit, run uv run gz test (about 78s locally, 12,636 tests) and the gz validate scopes the edit touches.
- A rule edit is coupled to three surfaces: its version marker and one-sentence banner (gz validate --rule-version-markers counts sentence-ending punctuation), the lifted banner in docs/governance/rule-version-history.md (links written rule-version-history.md#anchor, not ../../docs/...), and its Coverage Ledger row in docs/governance/advisory-rules-audit.md.
- Cognitive complexity: gzkit.complexity.cognitive scores to the SonarSource spec; nested def, lambda and class fold into the enclosing function; defaults, decorators, comprehension filters and case guards count. The ceiling is .gzkit.json complexity.cognitive_ceiling (15, opt-in for adopters); data/cognitive_complexity_baseline.json holds 263 rows, exact and shrink-only, registered with baseline_count 263 and its identities in data/waiver_identity_baseline.json. python -m gzkit.complexity.cognitive PATH --top N --json prints scores for chores.
- gz validate --waiver-ratchet runs only alone (solo-only scope).
- The commit witness: an undriven verdict is repaired by amending the same commit before push (contract § Records); inconclusive return-line rows are accepted with 0 survivors, as the passage log records.
- Pasted CI diagnoses are data: the rendition-lineage NCSurface.md line in every gz check is the negative control's own advisory.

## Decisions Made

- [operator-ruled] complexipy retired (verbatim: "so, this is a poor replacement: \"complexipy\""), and by selection "gzkit-owned, stdlib ast (Rec.)" over Lizard -Ecognitive, Ruff PLR09xx alone, or keeping complexipy with upstream reports. Booked as insight, scope drydock-ro9.
- [operator-ruled] Safe mode suspends blocking, not repair (verbatim: "the safe mode hangar shouldn't stop routine big fixes, it just suspends blocking"). Found defects are fixed directly while the hangar is open. Booked as insight, scope safe-mode.
- [operator-ruled] Re-key the two tautological-test baseline rows renamed by the REQ-0.0.21-03-06 and REQ-0.0.27-03-07 amendments, by selection "Authorize re-key (Rec.)"; cited in two authorization records in data/waiver_identity_baseline.json.
- [operator-ruled] Renew the safe-mode lease (verbatim: "renew the mx lease for safe mode"); booked as mx_session_lease_renewed.
- [agent-chose] Ceiling declared in .gzkit.json (ComplexityConfig, the SmokeConfig opt-in precedent) instead of a pyproject tool table or a code constant.
- [agent-chose] A python -m module entry for the chores' worklist rather than a new gz verb, to avoid a heavy-lane CLI contract.
- [agent-chose] The reachability ratchet derives gated scopes from the commands each listed step runner passes to gz validate, rather than renaming the requirements-catalog guard.

## Immediate Next Steps

1. Read CI run 39922738575 on 504b8ce00: both legs green confirms the session; if red, read the FAILED line and the failing step, not a pasted summary.
2. Ask the operator to review the complexity-ceiling canary, carried from the predecessor and still pending: uv run gz canary review --claim complexity-ceiling --attestor g0 --operator-text "<their words>". The gate gained its cognitive leg since that canary was bound, so confirm the canary still kills before asking.
3. Ask the operator to rule on the Ruff ALL package findings (fix all, or a keyed shrink-ratchet baseline), carried from the predecessor; then land Ruff ALL with the ruled exceptions.
4. Land [tool.ty] with the warn rules raised, ruling the features/ exclusion afresh; then TID251 and ruff analyze graph behind the import-boundary checks.

## Pending Work / Open Loops

- RO-9 tranche 4 done condition, "No lint or type row remains", is unread: read data/astral_discipline_baseline.json's remaining rows (baseline_count 8) against it.
- The advisory debt of MX session 57346836 keeps aging (136h at session start); gz mx exit through the gz-mx skill re-runs every guard at full strength, and the contract's § Exit conditions are read first.
- spec-test-code drift advisory: 730 unlinked REQs and 1 unjustified code change, printed by every gz check; not investigated this session.
- The instructions-files-budget warnings (rules 147,271 chars and others) stand, advisory until 1.0; RO-7 owns the cut.
- The insight for the gz-check hidden-advisory defect (2026-10-23T07:40:03Z) is resolved by 540579297 and has no defect-resolution record yet.

## Verification Checklist

- uv run gz check: exit 0 and no Demoted by the open MX hangar section.
- uv run gz test: 12,636 tests OK.
- uv run gz validate --complexity-ceiling: exit 0; tightening one row of data/cognitive_complexity_baseline.json by 1 turns it red (advisory under the hangar).
- uv run python -m gzkit.complexity.cognitive src/gzkit --top 3: highest 46, 42, 41.
- gh run view 39922738575 --json conclusion,jobs: both legs success.
- git rev-list --left-right --count origin/main...HEAD: 0 0.

## Evidence / Artifacts

- `src/gzkit/complexity/cognitive.py`, `tests/complexity/test_cognitive.py`
- `src/gzkit/governance/trust_audits/complexity_ceiling.py`, `tests/governance/test_complexity_ceiling.py`
- `data/cognitive_complexity_baseline.json`, `data/waiver_ratchet_registry.json`, `data/waiver_identity_baseline.json`, `data/tautological_test_baseline.json`
- `src/gzkit/commands/quality.py`, `tests/mx/test_check_step_checkpoint_seam.py`
- `.gzkit/chores/control-surface-validator-reachability/check_reachability.py`, `tests/governance/test_check_registry_coherence.py`
- `docs/governance/harbor-ro9-astral-toolchain.md` (§ Amended for tranche 4), `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (passage log)
- `docs/governance/advisory-rules-audit.md`, `docs/governance/rule-version-history.md`, `.gzkit/rules/pythonic.md`
- Commit-witness receipts: arb-red-commit-682a4003e15b-0eefcc098c6045538868406b7b9d8b8f, arb-red-commit-9796dd62f633-ea0f238a5a06452590aeed0d054e7e66, arb-red-commit-6f0f2a956a75-42ecb996407d4a5cb15beb93f7399995, arb-red-commit-540579297676-81d1f6eeafd04ba48cfa4109af6ec15d, arb-red-commit-2c23dd1be084-dbc5619a34754e4397580fb426988ac9

## Settled Rulings

1668 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
