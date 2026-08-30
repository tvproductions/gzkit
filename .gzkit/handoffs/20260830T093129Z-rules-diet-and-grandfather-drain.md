---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-30T09:31:29Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260829T184757Z-copilot-drop-and-composer-fix.md
---

## Current State Summary

Continuation of GHI #921 (OPEN) — the rules half of its ownership split, worked as direct repair under the GHI as its own work order. Two commits landed and BOTH ARE PUSHED (`git rev-list --left-right --count origin/main...HEAD` returns `0 0`); tree clean; `uv run gz check` exits 0 with 9,123 unit tests passing.

Landed:
- `bb85e660` fix(rules): version-chain lift across 10 rules (29,969 B off the per-turn surface), the first three grandfather-pin drops scored for real, and the Copilot-residue repair in `skill-surface-sync.md` plus the sync-drift guard.
- `d8848fd0` fix(rules): the last 9 grandfathered rules scored. `data/advisory_scorecard_grandfather.json` is now 0 entries, baseline_count 0.

`.gzkit/rules` 220,524 B -> 191,414 B. Every canonical rule is version-attributed in the Coverage Ledger, so `--advisory-scorecard` now fails closed on any future rule edit instead of letting it ride a pin.

THE HANDOFF THIS CONTINUES WAS VERIFIED AT RESUME AND TWO CLAIMS WERE STALE. It expected three unpushed commits (`0 3`); actual was `0 0` — the push had already happened, so its top advised step was already discharged. It expected `gz validate --brief-reconcile` to exit 3 on a pre-existing allowlist drift; actual exit 0, clean, while `src/gzkit/hooks/scripts/handoff.py` is still absent from disk AND still listed in OBPI-0.37.0-05-session-entry-door (status Draft). Its measurement of the lift was 18 rules / 44,240 B; the true remaining set was 15 rules / roughly 34.0 KB.

## Important Context

THE MARKER LESSON — the most important thing to carry forward. The generated-by-gzkit HTML comment proves a generator wrote a file. It proves NOTHING about corpus provenance, and it in fact ANTI-CORRELATES with it: root `AGENTS.md` is the ONLY corpus-backed instruction surface (79 entries in `.gzkit/corpus/AGENTS.md.jsonl`, byte-identical to `.gzkit/renditions/AGENTS.md/root.md`) and it is the ONLY one of 27 carrying NO marker. The 26 nested `AGENTS.md` files carry the marker and are generated from `.gzkit/rules/*.md`, which are hand-authored markdown with no corpus behind them. "Mechanically generated" and "CMS-corpus-backed" are two different claims; collapsing them is how an agent (this one, at session start) concluded a design spike was settled on the strength of a grep.

Generation is the DESIGNED state of a nested surface. Finding those files generated is finding the design working — it is not a discovery and carries no information about the spike.

The generator is `sync_nested_agents_md` (`src/gzkit/rules/__init__.py:482`), fed by `_shared_subtree_rules` at line 433, which classifies canonical rules and groups them by `paths:` frontmatter subtree. Hand-authoring did not disappear when nesting was generated — it moved up one level to `.gzkit/rules/*.md` and gets fanned out, which is exactly what GHI #921 asserts.

THE SCORECARD REFUSED FOUR OF THIS SESSION AGENT ROWS. Rows first written Mechanical were rejected for citing no property-level NC claim id from the enforces registry. The precedent is rows 45b and 62c: a unit test proves a property holds today; a registered NC proves the GATE refuses a violation. Only the latter earns Mechanical. A new row CANNOT be parked in `data/mechanical_witness_grandfather.json` — it is shrink-only, which is precisely the escape that ratchet exists to close. Expect this on any future scoring pass.

BULLET RETENTION MATCHES BY SUBSTRING. A scorecard row scored Mechanical or Promotable must have its Rule column appear VERBATIM in the per-turn surface under `.claude/rules/`. Paraphrases, parenthetical rule-number suffixes, and bold markers that swallow the trailing period all fail. Copy the exact fragment out of the rule.

THE VERSION-CHAIN BLOCKQUOTE IS NOT ALWAYS ALONE. `changelog-release-notes.md` carries a second, separate blockquote (Source of authority: Good Docs Project templates) directly beneath its version blockquote, separated by a blank line. Any transform that extends past the blank line eats binding content. Operate on contiguous quote lines only and stop at the first blank.

## Decisions Made

- [operator-ruled] Hold the changelog lift and take the discussions first (verbatim: "Discussions first (item 5)"). Booked via `gz handoff decide --decision proceed` with items 2-4 recorded as set-asides; superseded later in the same session.
- [operator-ruled] The design spike stays FULLY OPEN — nothing closed, no residual routed (verbatim: "Keep it fully open"). The operator was not persuaded by the agent premise-is-dead argument and was right: the agent had run a presence check, not a read. Do not characterize the spike again until the operator has read it.
- [operator-ruled] The root `AGENTS.md` Codex delivery-cap breach stays advisory; what is open is a discussion of whether that posture should hold (verbatim: "Leave it; discuss the advisory ruling"). NOT actioned this session.
- [operator-ruled] Do both halves of GHI #921 — the agent takes the rules diet, the operator takes ADR-0.35.0 (verbatim: "both").
- [operator-ruled] Fix the sync-drift guard defect AND track it, rather than only tracking it (verbatim: "both").
- [operator-ruled] Push, and do the remaining 9 scoring passes (verbatim: "push and do remaining 9").
- [agent-chose] Built the content-neutrality proof as a before/after comparison against HEAD rather than trusting the transform own internal check, and made the transform replace the exact extracted blockquote STRING rather than a line range. The prior attempt sliced from the blockquote to the next heading and silently deleted 24 lines from `mx-mode.md`; string replacement is structurally immune to that.
- [agent-chose] Scored three rows Promotable rather than Mechanical after the scorecard refused them, and named a promotion path in each, instead of seeking an exemption.
- [agent-chose] Repointed BOTH `skill-surface-sync.md` and the sync-drift guard at `.gzkit.json` vendors rather than correcting the vendor names in place — fixing the class, since a transcribed roster goes stale the moment a vendor is enabled or dropped.
- [agent-chose] Retargeted the test asserting the retired Copilot mirror behavior at the surviving `.claude/rules/` mirror rather than deleting it, keeping its assertion true.
- [agent-chose] Updated the literal version pins in three test modules rather than reshaping them to derive, because the rule-version constant is a deliberate bump-me pin and the tests carry attested REQs.
- [agent-chose] Extracted a shared mirror-check helper when xenon rejected the guard at rank D, rather than suppressing the complexity check.

## Immediate Next Steps

1. Hold the two operator-held discussions. Both are ruled open and neither is agent work: (a) the design spike, fully open, premise uncorrected by anything the agent may assert; (b) whether a delivery-cap breach on must-survive canon should stay advisory. Nothing else in this handoff should displace these.
2. Rule on the bullet-narrative compression half of GHI #921. This is the remaining rules-half work and it is gated: the instructions-files-diet chore section 4 is a BINDING consult gate — steps 1-4 mutate nothing, and the operator rules per item or per rank-band before any edit. Present a ranked recommendation with byte estimates; do not cut first.
3. Decide the fate of `.gzkit/renditions/AGENTS.md/codex.md` and its corpus manifest. Frozen at committed_ts 2026-08-17 with corpus_entry_count 59 while the root manifest is at 2026-08-27 with 79. Either something reads a 20-entry-stale rendition, or it is residue contradicting the per-vendor-AgentContract prohibition. Not investigated this session.
4. Determine why `uv run gz validate --brief-reconcile` exits 0 while OBPI-0.37.0-05-session-entry-door (Draft) lists `src/gzkit/hooks/scripts/handoff.py` in its allowlist and that file is absent from disk. Either the validator does not check allowlist-path existence on a Draft brief — a real hole — or the predecessor handoff misattributed an error that was really the seven discovery-index errors.
5. The corpus half of GHI #921 remains operator-initiated under ADR-0.35.0-canon-entry-corpus-landing, per the IRON LAW and the routing table in the GHI body. The surface_content_types map in `data/vendor-manifest.json` still declares only AGENTS.md, so `gz content compose` fails closed on every rule surface.

## Pending Work / Open Loops

DESIGN SPIKE — fully open by operator ruling. The agent argued its premise was dead on the strength of a marker grep plus 30 lines of a generator docstring, and the operator rejected that. The argument was wrong in method (a presence check is not a read) and wrong in two of its four answers: it claimed Rule as the owning content type while content_type_routes maps Rule to claude alone and nested AGENTS.md is a Codex-facing surface Claude does not load; and it answered "which files earn survival" with a mechanism rather than a judgment. Do not re-run that argument.

DELIVERY-CAP BREACH — open for discussion, not action. Root `AGENTS.md` is 46,876 B against a 32,768 B Codex cap: 14,108 B over, with the operator-doctrine-verbatim-canon section spanning 30020-43941 (straddling) and architectural-boundaries starting at 46281 (entirely past). The witness is advisory by the 2026-07-06 decoupling and the 2026-08-17 stay, whose EXIT CONDITION was RETIRED not deferred. Already tracked at GHI #815 (OPEN, title names this exact finding) with remedies owned by ADR-pool.render-order-truncation-survival and GHI #533. What is NEW: the 2026-08-17 attestation disclosed and knowingly accepted a 1,586 B breach; it is now 14,108 B, and no attestation discloses the current figure.

CORPUS ONBOARDING — operator-held. Assigning content types to the 26 canonical rules is the held discussion. Note the sequencing consequence of the corrected spike premise: onboarding a rule governs BOTH its `.claude/rules/` projection and its nested AGENTS.md projections at once, because one generator writes both — so nothing about the nesting needs settling first.

NESTED PROJECTION IS UNMEASURED. `agents-md-map-doctrine.md` declares paths of AGENTS.md, CLAUDE.md and `.claude/rules/*.md`, and `agents_md_map_conformance.py` line 100 pins the rendered path to AGENTS.md alone, so roughly 345 KB across 26 nested AGENTS.md files is governed by no shape doctrine. Surfaced, not routed — it is a spike residual and the spike is the operator.

UNENFORCED CLAUSES FOUND BY THE SCORING PASS, each now carrying a row and a promotion path: `skill-surface-sync.md` rule 6 (a skill-version bump requires a last_reviewed bump in the same edit) is checked by nothing — the existing validator checks format and staleness only, so the exact failure the clause names is the one nothing catches. `models.md` clause 3 (Field descriptions) is unenforced. `security-sensitivity.md` registry edits on the direct-fix path have no declaration channel at all.

`complexity-doctrine.md` disqualifier 1 (post-hoc fitting) is structurally unwitnessable — it is a claim about the ORDER a decision was made in, and a fitted corpus is byte-identical to an honestly-derived one. Scored Judgment; the defense is the distillation cadence, not a gate.

GHI #921 title remains misframed ("22 of 23 AGENTS.md are ungoverned by the CMS corpus"): true that no corpus backs them, but they are not ungoverned, and the title aims repair at the wrong surface. The GHI body routing table is correct; only the title is wrong.

Pre-existing and untouched: the `gz check` advisory reports 696 unlinked specs and 1 unjustified code change.

## Verification Checklist

Run these before trusting any claim above.

`git log --oneline -3`
  Expect d8848fd0, bb85e660, then fac560be.

`git status --short`
  Expect empty.

`git rev-list --left-right --count origin/main...HEAD`
  Expect a zero/zero count. Both commits are pushed; this handoff carries NO data-loss exposure.

`uv run gz validate --advisory-scorecard`
  Expect exit 0. It goes red the moment any rule version bumps past its Coverage Ledger row — that coupling is now armed for EVERY canonical rule, not just the 13 that were listed before.

`python3 -m json.tool data/advisory_scorecard_grandfather.json`
  Expect grandfathered_rules to be an empty array and baseline_count to be 0. The pre-ledger grandfather is drained.

`uv run gz check`
  Expect exit 0.

`uv run gz obpi lock list`
  Expect no active locks.

`gh issue view 921 --json state,title`
  Expect OPEN.

`uv run gz validate --brief-reconcile`
  Expect exit 0 — and note that this DISAGREES with the predecessor handoff, which expected exit 3. See Immediate Next Steps item 4.

`uv run gz validate --instructions-files-budget`
  Expect exit 0 with three advisory WARNINGs naming the Codex cap breach. The warnings are the subject of the held discussion; exit 0 is correct and expected.

Reproduce the nested-AGENTS.md loading finding with the Read tool on a file under `src/gzkit`, observing which instruction files load. Bash reads do not trigger directory-scoped memory. NOTE: this session did NOT re-run that reproduction; it is inherited from the predecessor.

## Evidence / Artifacts

Canonical rules edited this session — all 25 bumped, and lifted or scored:
- `.gzkit/rules/` — 220,524 B -> 191,414 B

Governance surfaces:
- `docs/governance/rule-version-history.md` — the lift destination; 16,889 B -> 54,082 B
- `docs/governance/advisory-rules-audit.md` — Coverage Ledger now lists every canonical rule; 18 rows added or corrected; Summary roll-up 67 Mechanical / 30 Promotable / 60 Judgment
- `data/advisory_scorecard_grandfather.json` — 12 -> 0 entries, baseline_count 23 -> 0

Source changed:
- `src/gzkit/hooks/guards.py` — mirror roots now derived from `.gzkit.json` vendors; a shared mirror-check helper extracted to hold the xenon C ceiling

Test surfaces:
- `tests/test_hooks_guards_ledger_sync.py` — failing-first coverage for the Codex mirror and for the retired-vendor prohibition; the Copilot-mirror test retargeted rather than deleted
- `tests/complexity/test_citation.py` — rule-version pins updated; a stale docstring corrected
- `tests/governance/test_complexity_doctrine_rule.py` — rule-version pins updated
- `tests/governance/test_complexity_thresholds_rule.py` — rule-version constant updated

Insight records written this session, in `.gzkit/insights/agent-insights.jsonl`:
- improvement, scope instruction-surface-provenance — the marker-is-not-provenance correction
- defect-resolution, scope hooks.guards — the hardcoded vendor roster

Predecessor:
- `.gzkit/handoffs/20260829T184757Z-copilot-drop-and-composer-fix.md`

## Settled Rulings

608 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
