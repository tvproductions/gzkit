---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-01T10:35:13Z'
agent: claude-code
session_id: e1a1e12c-fff9-4e10-b878-b0a3ea88a3fc
continues_from: .gzkit/handoffs/20260731T202443Z-campaign-status-refresh-adr-0340-validated.md
---

## Current State Summary

Chore session under the operator directive "let's complete all chores — run all 37 + fix what's fixable". All 37 chores in .gzkit/chores/registry.json were advised, then run and logged; 37/37 now carry a CHORE-LOG entry, up from 36 (test-consolidation-subtest-sweep had never been run since authoring). Eight commits landed on main, 36f3e9f3f..e11a6f5ad, tree clean and pushed, gz check passing as the pre-push gate.

The sweep's real yield was three defects the chores surfaced rather than the chore runs themselves. (1) The four .claude/hooks/*.py blocking hooks are GENERATED, and GHI #582's UnicodeDecodeError fix had been applied to the generated output only — so gz agent sync control-surfaces, the command gz validate --surfaces prints as its own recovery, would have silently reverted the crash guard. Ported into the generators in d92ba332a and verified by running the dangerous command. (2) Test stdout noise 94 lines to 0 (fc67ed67c). (3) The chore-acceptance class itself: 11 of 37 chores were green by construction, now rewired to gate on their own subject (33df03496).

Final catalog state: 33 of 37 green on real witnesses, four control-surface chores RED because their evidence is genuinely stale.

## Important Context

The four red chores are red ON PURPOSE and must not be quieted. Their acceptance was `test -f <proofs>/<report>.md` — existence, never currency — which passes forever once a file exists. Replaced with scripts/check_proof_freshness.py, which compares git COMMIT DATES (not mtimes; a clone or branch switch rewrites those) between each proof and the surfaces it audits. All four fail. The remedy is re-running four deep analysis passes, not a touch, and the failure prose says so explicitly.

GHI #448 named exactly this for one of the four in May 2026 and was closed without changing the acceptance shape. That is why it recurred silently, and it is the reason this handoff exists rather than a green checkmark.

module-sloc-cap-radon's framing in GHI #743's original body was wrong and is corrected in a follow-up comment. It is not merely "declares a cap, never invokes radon" — the cap itself was the drift. .gzkit/rules/complexity-thresholds.md § Invariant: "none of them owns its own thresholds. A new threshold authority appearing anywhere else is doctrine drift by another name." The canonical radon_raw_nloc bands are advise 311.75 / warn 733.2 / block 1031.9; the invented 1000 sat between p90 and p95 and failed cli/parser_governance.py (1010 SLOC), a module the corpus does not block. FIVE modules are genuinely over the band, not six.

radon_raw_nloc maps to radon's `sloc` field — see gzkit.complexity.measurement._run_radon_raw, which records entry.get("sloc") under that key. Measuring any other field compares a different quantity than the corpus was measured with.

Ruff `D` is now in select but scoped by per-file-ignores to src/gzkit. Full adoption surfaces 6321 findings under tests/features/scripts and another 74 in generated skill mirrors and hooks — files that must never be hand-edited per .gzkit/rules/skill-surface-sync.md #4/#5. Widening that scope is a separate decision, not a side effect.

513 mypy-style `# type: ignore[...]` comments sit under tests/ and scripts/. They suppress NOTHING in ty (GHI #197 shape), and tests/governance/test_type_ignore_syntax.py only fail-closes on src/**, so that surface is unguarded. Only the handful corresponding to a live diagnostic were fixed.

## Decisions Made

- [operator-ruled] "let's complete all chores — run all 37 + fix what's fixable" — booked via gz handoff authorize against the 20260731T202443Z handoff. This authorized chore work and NOTHING else; the predecessor's advised steps remain unexecuted.
- [operator-ruled] Rewrite all 37 D401 findings to imperative mood and adopt full ruff `D`, rather than exempting D401 to preserve the "True when ..." predicate convention. Landed in 44f7aac2e.
- [operator-ruled] For module-sloc-cap-radon: adopt the canonical radon_raw_nloc band and register the five over-band modules in a shrink-only ratchet, rather than splitting them now or leaving the chore red. Landed in 33df03496.
- [agent-chose] Scoped ruff `D` to src/gzkit via per-file-ignores instead of repo-wide, because full adoption surfaces 6395 pre-existing findings including 74 in generated mirrors nobody may hand-edit.
- [agent-chose] Left the four control-surface chores RED rather than refreshing their proofs. A touch would restore the green-by-construction gate the freshness check replaced; re-running the audits is the real remedy and is its own session.
- [agent-chose] Filed ONE class GHI (#743) rather than four instance GHIs, because #658, #659, #445 and #448 are all closed instances of the same acceptance-shape defect and filing four more would repeat the pattern.
- [agent-chose] Scoped gz arb validate by the `arb-` filename prefix rather than by the `schema` field. A schema filter would silently skip a real arb-* receipt with a missing schema — exactly the defect the validator exists to catch.

## Immediate Next Steps

1. Re-run the four control-surface audits and commit refreshed proofs. This is the sole outstanding item from this thread and is a real chunk of work — four deep analysis passes (rule-pair conflict matrix over 26 rules, skill/rule reachability over the skill catalog, rule-prose vs promoted-check parity, permission standing-consent drift). Worth its own session; do not tack it onto other work. Each chore's CHORE.md carries its procedure, and check_proof_freshness.py names the fix in its failure prose.
2. Rule on Movement A item 3, the foundation-adr-registers-invariant disposition. One line of operator canon. Carried unexecuted from the predecessor handoff; it unfences tests/governance/test_invariant_witness.py so --invariant-witness can rejoin gz check.
3. Open ADR-0.35.0-canon-entry-corpus-landing and begin landing its 9 briefs (0/9). This is the topmost unchecked campaign item and the campaign governs pull order.
4. Consider whether the 513 mypy-style type-ignore comments under tests/ and scripts/ warrant widening test_type_ignore_syntax.py beyond src/**, or whether that surface is deliberately unguarded.
5. Decide whether ruff `D` should widen past src/gzkit. Deferred deliberately; 6321 findings under tests/features/scripts.

## Pending Work / Open Loops

- FOUR CONTROL-SURFACE CHORES RED (the outstanding item): control-surface-rule-conflicts and control-surface-permission-consent-drift have proofs last committed 2026-07-16 against a surface last moved 2026-07-29; control-surface-skill-rule-reachability and control-surface-rule-vs-check-drift have proofs from 2026-06-25 against surfaces last moved 2026-07-29 and 2026-08-01. All four exit 3.
- GHI #743 remains OPEN, scoped down to exactly those four stale audits. Everything else in the class is discharged.
- Five modules sit over the canonical block band under the shrink-only ratchet: cli/parser_artifacts.py 1743, cli/parser_maintenance.py 1582, commands/obpi_complete.py 1429, commands/validate_cmd.py 1309, commands/adr_audit.py 1034. They may only shrink; splitting them is unscheduled.
- Movement A item 3 (foundation-adr-registers-invariant) still unruled — carried from the predecessor handoff, never authorized.
- ADR-0.35.0-canon-entry-corpus-landing at 0/9 briefs landed.
- ADR-0.34.0 audit shortfalls S1 and S2 still have no GHI of their own; S3 is GHI #740.
- 513 inert mypy-style type-ignore comments under tests/ and scripts/, unguarded by test_type_ignore_syntax.py.

## Verification Checklist

- git rev-parse --short HEAD resolves to e11a6f5ad on main; tree clean, nothing unpushed.
- uv run python scripts/check_proof_freshness.py control-surface-rule-conflicts exits 3, and so do the other three slugs. If any exits 0, its proofs were refreshed after this handoff.
- uv run python .gzkit/chores/module-sloc-cap-radon/check_module_size.py --self-test exits 0 with 7 cases across all four breach directions.
- uv run python .gzkit/chores/module-sloc-cap-radon/check_module_size.py exits 0; five grandfathered modules, none grown.
- uv run gz validate --waiver-ratchet exits 0 — run it ALONE, not bundled, or it refuses with a false-green warning (GHI #704).
- uv run gz arb validate exits 0 scanning 50 receipts, 0 invalid.
- uv run gz chores audit --all reports 37/37 with logs.
- gh issue view 743 reports state OPEN.
- uv run gz check exits 0.

## Evidence / Artifacts

- `.gzkit/chores/module-sloc-cap-radon/check_module_size.py` — the module-size gate with its --self-test teeth-proof
- `scripts/check_proof_freshness.py` — the git-commit-date freshness gate that replaced `test -f`
- `data/module_size_grandfather.json` — the five-module shrink-only ratchet
- `data/waiver_ratchet_registry.json` — where that ratchet is declared under ADR-0.0.73 BI#8
- `.gzkit/rules/complexity-thresholds.json` — the canonical band table the chore now cites
- `src/gzkit/hooks/scripts/quality.py` — hook generator that had lost the GHI #582 guard
- `src/gzkit/arb/validator.py` — the arb receipt scan, now filename-scoped
- `tests/arb/test_validator.py` — two regression tests pinning both scan directions
- `pyproject.toml` — ruff `D` adoption and its per-file-ignores scoping
- `.gzkit/handoffs/20260731T202443Z-campaign-status-refresh-adr-0340-validated.md` — predecessor

## Settled Rulings

- attest completed — OBPI-0.34.0-05 activates the permanent Foundation Sunset closure gate: ("ADR taxonomy", run_taxonomy_audit) is the LAST step in _build_check_steps() and `gz check --json` reports "ADR taxonomy": true, while the registration membrane refuses an un-grandfathered `kind: foundation` package at both adr_created ingresses (gz register-adrs and first-run gz init) with the 51-entry grandfathered roster still booking normally (GHI #706 discharged). 4/4 REQs proven on their correct ADR-0.0.59 channels with behavior_uncovered_reqs 0; REQ-0.34.0-05-01 was re-kinded BEHAVIOR->SUPPORT…
- "update handoff and campaign, then git sync" — booked verbatim via gz handoff authorize as the ruling on the resumed handoff. The predecessor's advised step (continue the ADR-0.34.0 checklist or open the next OBPI) was NOT authorized and remains unexecuted.
- The same words ratify the campaign amendment under section 8, in the same shape as the 2026-07-29 "fix discrepancy" ratification.
- attest completed — ADR-0.34.0 Foundation Sunset closeout, g0 verbatim, 11-step ceremony attested 2026-07-31T11:46:09Z; lifecycle transitioned to Validated and released as v0.34.0 on bump commit 551366064. Receipts arb-step-unittest-f02e079a9c5c4fce83433f15d1ace4b1 (7685 OK), arb-ruff-9b11bcbc647c4b9a9ddb6282f7fc34b4, arb-step-typecheck-4c8436dc00e842b8847ebcacb7dc866c, arb-step-mkdocs-3f31717e44a04a46821f35433f53b0c2.
- accept audit — ADR-0.34.0 Foundation Sunset validated with three shortfalls recorded open, accepted after each was presented with its verification evidence, g0 verbatim 2026-07-31T12:26:25Z. Bound fidelity gate 2/2, gz validate --taxonomy exits 0 on the terminal tree, gz cli audit 132/132 commands covered, 18/20 REQs covered with 2 SUPPORT REQs proof-exempt by ADR-0.0.59 channel. Shortfalls open: S1 inert @covers coverage, S2 missing exit-3 membership assertions, S3 framework-wide closure is the rejected alternative (GHI #740).
- refresh handoff (verbatim) — booked via gz handoff authorize against the 20260731T090547Z handoff for session a7d9d6b9-db29-49a3-8f87-f333222230a6. This is the ruling that lifted the resume gate; it authorizes the handoff refresh and nothing beyond it.
