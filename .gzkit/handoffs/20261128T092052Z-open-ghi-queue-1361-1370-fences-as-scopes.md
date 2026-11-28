---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-28T09:20:52Z'
agent: claude-code
session_id: 810ee815-da93-4d5e-89dc-eb68ccbdd128
continues_from: .gzkit/handoffs/20261128T003736Z-prompt-audit-m49-m51-era-fidelity-closed.md
---

## Current State Summary

The prompt-audit walk (M1-M51) was complete on arrival. The operator chose to work its open residue as the open-issue queue in issue-number order, starting at #1361. That is the queue the operator agreed to, not a governed process; the campaign plan governs work selection beyond it.

Closed this session, each with an independent reviewer's CONFIRMED verdict on the issue:
- #1361: Copilot surfaces dropped from the OBPI brief template.
- #1324: AirlineOps residue in the brief template; reopened and closed again.
- #1363: gz init writes the JSONL merge routing into an adopter's .gitattributes.
- #1415: reopened twice for regressions its own fix introduced. e35b5b040 repaired the Stage 2 procedure pin, which d62efd5d3's hand edit had broken: gz obpi pipeline refused Stage 2 and CI on d4dea64c5 went red. 6dff893e0 added the coverage-floor CI job.
- #1370: the nine prompt-audit prose fences are now gz validate scopes in gz check (13 commits, c95ac83f0 to d6ceab88a).

Filed: #1418 (adopter .gitattributes lacks eol=lf).
Left open with a blocker comment: #1365.

Last full unit tier: 14469 tests OK. gz check passes with only the pre-existing MX demotions (tautological-debt, sensitivity, hexagon_tests, tautological_test_audit).

## Important Context

- Read gz check output for [MX advisory] demotion lines before claiming a pass. The open hangar turns findings into exit 0. GZKIT_MX_FULL_STRENGTH=1 uv run gz validate --<scope> shows the real verdict.
- gz check's Test (changed) step selects tests by Python module stem only (_select_changed_tests). A Markdown, JSON or data edit selects nothing, so this session twice landed commits that broke tests it never ran: the Stage 2 pin, and the scope-membership _counts and guard-canary tests. Run the full unit tier before committing in a multi-file series: uv run unittest-parallel -t . -s tests --buffer, about 80s. Read CI after every push.
- The Stage 2 to 5 procedure files under .gzkit/skills/gz-obpi-pipeline/references/ are renders of data/obpi_pipeline_control_inventory.json, pinned by sha256 in src/gzkit/pipeline_procedure.py STAGE_PROCEDURES. Never hand-edit them. Make a declared rewording on the control, re-render, repin, and sync.
- A new gz validate scope touches about 15 surfaces. Use 75d6d2c8f (--model-class-only) or 9772dd444 as the template:
  - registry, parser flag and passthrough, gz check step and _STEP_GUARD_META;
  - qc_binding, the exemption and population entries, the negative control (builder, entrypoint, table row);
  - guard canary, check_scope_membership with recomputed _counts, check_step_concurrency, registry-parity test;
  - the validate manpage synopsis, section and table row.
- A prose fence whose roots include src/gzkit reads its own source, the control builders and docs/user. Assemble planted refused text at run time and never quote a refused shape verbatim there.
- A subagent with no booked gz wp dispatch is refused every gz write (RP-12). Forks cannot run the gates; do gated work in the main session.
- When the full-strength tautology audit output is filtered, count with grep -oE '\] tests/[^ ]+\.py': some findings print after a '→ [tautological_test_audit]' prefix. A '^tests/' filter missed two fences and misstated #1370's population once (corrected on the issue).
- The full-strength-report CI job fails on the pre-existing MX debt, on runs before this session too. It is continue-on-error and report only.

## Decisions Made

- [operator-ruled] Work the prompt-audit residue rather than R&D T37 (verbatim: "no, continue with the M1-M51 findings"), as the open issues in number order (verbatim: "yes, start with #1361").
- [operator-ruled] Fix the reopened #1324 before #1363 (verbatim: "yes, fix #1324 now").
- [operator-ruled] #1363: gz init, repair included, writes the three merge=gzkit-jsonl routing lines into the adopter's .gitattributes. It appends only what is missing and never rewrites a line (verbatim: "A").
- [operator-ruled] #1415: wire a CI caller for the uncalled coverage-40pct floor gate rather than grandfather it (verbatim: "ok", on that recommendation).
- [operator-ruled] #1370: each prompt-audit fence becomes a gz validate scope that reads prose as data, run by gz check, with no tautology-audit exemption (verbatim: "A").
- [agent-chose] Each fence is its own scope, not one combined scope. This follows the 2026-11-25 ruling "Witness per mechanism", and the scorecard requires property-level controls (the #1266 multi-leg gap).
- [agent-chose] gzkit.rules._is_framework_tree became public is_framework_tree (c95ac83f0). A private cross-package import is shrink-only rostered, and the roster's pass 2 prescribes promotion.
- [agent-chose] On gzkit's tree a missing fence root is a finding, so a renamed directory cannot shrink a fence; in an adopter project it is skipped. harness-session and canon-relative-links read nothing in an adopter project, because their subject is gzkit's own tree.
- [agent-chose] #1365 stays open with a blocker: it needs OBPI-0.35.0-20, which only the operator initiates, and safe mode suspends OBPI initiation.

## Immediate Next Steps

1. Brief the operator: strategic, operational and tactical, vital facts first. Then read CI on the pushed head: the run for this sync is the first containing the coverage-floor job and the nine new gz check steps.
2. On the operator's go, work #1367: widen --size-limit-citations to the F1 phrasings, F2 roots, F3 history allowance, F4 false positives and F5 witness naming in pythonic.md and the Coverage Ledger. It is unblocked now that #1370 [settled] is closed. Build it in src/gzkit/governance/trust_audits/size_limit_citations.py and its tests and control, not in tests/policy.
3. Put one question to the operator: should test_git_sync_flags_stated_once.py (#1390 [settled]), which passes the tautology audit, also become a scope?
4. Continue the open-issue queue in number order: #1371, #1372, #1377, #1378, #1380, #1382, #1385, #1388, #1409, #1412, #1418. Screen each against drydock orders and live briefs first.
5. Route the unrouted insights one at a time. Two were carried by the predecessor: the dead anchor in arb-middleware.md (#attestation--worked-example), and gz task start ignoring --seq beside a task_id.

## Pending Work / Open Loops

- #1365 is blocked on OBPI-0.35.0-20 (Draft, PENDING, Heavy, ADR-0.35.0). The three stale passages still ship: SKILL.md:41, stage-4-present-evidence.md:154, obpi-pipeline-control-rationale.md:1535.
- #1418 is open: its renormalization risk needs an operator ruling.
- An independent finding from #1415 [settled] that waits on the operator: the chore id coverage-40pct embeds the value 40.
- The Dependency currency workflow failure on d4dea64c5 has not been examined.
- The other open issues are outside the queue: 178 open, by search total_count, at 2026-11-28. The campaign plan rules which of them are pulled.
- MX hangar debt: the session has carried advisory debt for over 1000h. gz mx exit will refuse the four demoted guards until their findings are repaired.
- Whether anything calls render_rule_for_copilot in src/gzkit/rules/__init__.py is unclaimed.

## Verification Checklist

- uv run gz handoff resume, then book the operator's ruling with uv run gz handoff decide.
- gh run list --branch main --limit 3: CI on the synced head, including the coverage-floor job.
- uv run unittest-parallel -t . -s tests --buffer: expect 14469+ tests OK.
- git add -A, then uv run gz check: read the [MX advisory] lines. Only tautological-debt, sensitivity, hexagon_tests and tautological_test_audit are expected.
- GZKIT_MX_FULL_STRENGTH=1 uv run gz validate --tautological-test-audit: only test_advances_decorator, test_skill_self_close_drift and test_plan_command remain.
- uv run gz validate --size-limit-citations (and each of the nine #1370 scopes): 0 findings.

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/prose_fence.py`
- `src/gzkit/governance/trust_audits/size_limit_citations.py`
- `src/gzkit/governance/trust_audits/dependency_currency_citations.py`
- `src/gzkit/governance/trust_audits/tidy_verdict_citations.py`
- `src/gzkit/governance/trust_audits/moved_fact_citations.py`
- `src/gzkit/governance/trust_audits/agents_md_numbering_citations.py`
- `src/gzkit/governance/trust_audits/campaign_credit_citations.py`
- `src/gzkit/governance/trust_audits/harness_session_single_source.py`
- `src/gzkit/governance/trust_audits/related_skill_citations.py`
- `src/gzkit/governance/trust_audits/canon_relative_links.py`
- `docs/user/manpages/validate.md`
- `.github/workflows/ci.yml`
- `src/gzkit/pipeline_procedure.py`
- `data/obpi_pipeline_control_inventory.json`
- `data/guard_canaries.json`
- `src/gzkit/commands/ledger.py`

## Settled Rulings

2664 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
