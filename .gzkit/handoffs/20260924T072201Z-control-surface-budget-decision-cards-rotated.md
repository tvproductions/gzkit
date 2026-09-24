---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-24T07:22:01Z'
agent: claude-code
session_id: 0eb7c8c4-6481-4566-ab9a-b082d3bc8232
continues_from: .gzkit/handoffs/20260923T112420Z-behave-lane-canon-landed-two-mechanism-ghis-filed.md
---

## Current State Summary

Three governance changes landed and two frontier cards were consumed. (1) GHI #1088 CLOSED: plain gz check is now the per-change gate (the change scope, without Behave and Preflight) and records the pre-push reuse fingerprint; gz check --full is the full sweep and CI runs it (a0eb2c90b, 01bc422d4); the AGENTS.md Execution Rules entry was replaced under operator attestation. tests.md reached 0.26.5 on the way (ae43835e3 reconciled Two runners first). (2) GHI #1089 CLOSED: the Claude Opus 5.5 System Card consumed from a Codex analysis that was verified against the PDF first (4cef615ef), and the AGENTS.md source-boundary bullet widened to text the operator pastes in (293baeecb). (3) GHI #1019: the GPT-6 System Card (updated 2026-09-22, family now GPT-6 Astra / Sol / Luna) consumed in 1d580a0c1; the adversarial-review reframe of gpt-tuning.md lands in this handoff's sync commit. Also aa7218d67: consequence-bands.md kept PROVISIONAL, F-022 status corrected. main was level with origin before this handoff's sync; per-change gz check exit 0 on the tree this handoff describes.

## Important Context

THE CONTROL-SURFACE BUDGET IS THE OPEN DECISION. AGENTS.md is 21792 chars against the 20000-char budget in data/instructions_files_budget.json, 1792 over and advisory only under the 2026-08-17 stay (uv run gz validate --instructions-files-budget warns, exit 0). It was 21569 at session start; this session's two attested invariant entries added 223. The latest composition_candidate_emitted ledger event measures invariant_bytes 20984 and compressible_bytes 105 at setpoint lite: the invariant floor ALONE exceeds the budget, so no diet pass can reach it. The instructions-files-diet chore stops at exactly this gap (its section 2(c)) and an ordinary session may not trim canon. Closing it is an operator act: re-tier, retire or merge invariant canon, change the budget with a recorded witness, or hold under the stay until ADR-0.35.0 Decision 3 (corpus-owned sections, unowned-byte ratchet, 15000 destination) lands. CLAUDE.md (2167 chars) and the rule files are inside their budgets. REQ-0.0.54-01-03 still asserts the retired values 15000 / 4000 / 16000 and is the same subject.

gz check SEMANTICS CHANGED THIS SESSION: plain gz check drops Behave and Preflight; any change to a CLI help string, output or other external contract is heavy-lane and needs gz check --full before push. a0eb2c90b went red in CI for exactly that reason: a --help rewrite dropped a phrase REQ-0.0.54-03-04's scenario asserts.

PARALLEL SESSIONS SHARE THIS CHECKOUT. A Codex session wrote files mid-session; gz git-sync's default auto-add staged them and a whitespace hook altered one. Use gz git-sync --apply --no-auto-add whenever another session may be writing, and check git status for files you did not write before any commit.

GPT FAMILY RENAME: GPT-5.6 Sol was the flagship; GPT-6 Sol is the lower-cost tier. Name GPT models by generation and name, never by name alone.

Standing cautions carried unchanged: D-01 and D-05 are UNRESOLVED on load-bearing findings; an OPEN finding row is settled under Q-14 but not confirmed; Phase 4 is unauthorised.

## Decisions Made

- [operator-ruled] Reconcile tests.md section Two runners with the behave-lane canon (verbatim: "go with step 4, fix tests.md"). Booked via gz handoff decide.
- [operator-ruled] Keep consequence-bands.md PROVISIONAL and decide the lift when Phase 4 is authorised (verbatim: "A. Keep PROVISIONAL").
- [operator-ruled] Make plain gz check the per-change gate and add --full, fixing it in the same session (verbatim: "B and fix now"), chosen over scope-keyed reuse and a canon-only change.
- [operator-ruled] Attest the replacement AGENTS.md Execution Rules entry for gz check scopes (verbatim: "I attest to that wording, land it").
- [operator-ruled] Work the three suggestions in the pasted Codex report (verbatim: "do the codex suggestions"), given in the operator's own words after the paste.
- [operator-ruled] Attest the widened AGENTS.md Behavior Rules source-boundary bullet covering pasted text (verbatim, a second time for a second entry: "I attest to that wording, land it").
- [operator-ruled] Download the GPT-6 Astra card PDF for retention (verbatim: "yes, download it").
- [operator-ruled] GPT-6 Sol is the default GPT model and GPT-6 Astra is used only by explicit selection (verbatim: "If we default to astra, I find that it is too token hungry" and "yes, explicit selection").
- [operator-ruled] gzkit skills stay Anthropic-first and GPT runs bounded adversarial review; no catalog remap to GPT-6 (verbatim: "A."), confirming the insight another session recorded at 07:04.
- [agent-chose] Row 37a scored Promotable, not Mechanical: a unit test is not a registered negative control, and the scorecard validator refused the Mechanical claim.
- [agent-chose] No tenth failure-mode pattern for either card: the Opus 5.5 unverifiable-authorization regression is incoming-content doctrine, and GPT-6 oversight gaming is pattern 9.
- [agent-chose] Kept another session's files and records out of this session's commits until the operator ruled on them.
- [agent-chose] Retired, rather than carried forward, quotations the outgoing doctrine attributed to the Opus 5 and GPT-5.6 cards that the retained PDFs' text does not contain.

## Immediate Next Steps

1. Rule on the AGENTS.md budget condition. The invariant floor (20984 B) already exceeds the 20000-char budget, so trimming compressible canon cannot close it. Options: (A) re-tier named invariant entries to compressible, then run the instructions-files-diet chore; (B) retire or merge invariant entries, each removal attested; (C) change the budget in data/instructions_files_budget.json with a recorded witness, which is doctrine change; (D) hold under the 2026-08-17 advisory stay until ADR-0.35.0 Decision 3 lands. The largest invariant section is operator-doctrine-verbatim-canon.
2. Close GHI #1019 once CI passes on 1d580a0c1 and on this handoff's sync commit, citing both SHAs and docs/governance/gpt-6-system-card-analysis-2026-09-24.md in the ghi-close evidence comment.
3. Escalate REQ-0.0.54-01-03, which asserts retired budget values; it rides on the step-1 ruling.
4. From the predecessor handoff, still unworked: rule on GHI #1087's shape and GHI #1085's remedy, then choose the next IEEE measurement from M-A to M-G (M-D stays blocked on its method).

## Pending Work / Open Loops

GHI #1085 and GHI #1087 remain OPEN and unselected. GHI #1019 is open only until its CI witness; the close is evidence-ready.

Findings recorded, not filed: gz git-sync's default auto-add stages files another session wrote into the same checkout, and the pre-commit whitespace hook then rewrites them. That is a hazard whenever parallel sessions share a checkout; whether it is a defect is the operator's call. Scorecard row 37a stays Promotable until a negative control pins Behave in the change scope's skips.

REGISTER QUESTIONS carried: whether to author a finding for D-08 now that M-F has run. consequence-bands.md lift is booked to Phase 4 authorisation.

Frontier registry: three current cards, none unconsumed. The Sonnet tier's frontier scope is still unruled (scan record).

## Verification Checklist

uv run gz check exits 0 on the tree this handoff describes. It is now the per-change scope; run uv run gz check --full before pushing any CLI or external-contract change.

uv run gz validate --instructions-files-budget exits 0 and warns AGENTS.md 21792 chars over 20000. That warning is the expected state until step 1 is ruled.

python3 -c with json over data/frontier_model_cards.json lists Fable 5.1 / Mythos 5.1, Opus 5.5 and GPT-6 (Astra / Sol / Luna), all current; data/system_cards/ holds exactly their three PDFs.

grep -rnE for Opus 5 and GPT-5.6 over .gzkit/rules, .gzkit/skills, docs/governance and CLAUDE.md hits only dated records and current-card comparison quotations.

CI: a0eb2c90b red (fixed by 01bc422d4); 01bc422d4, 4cef615ef, 293baeecb green on ubuntu and windows. Re-check 1d580a0c1 and the sync commit with gh run list --branch main --workflow CI.

## Evidence / Artifacts

Commits: aa7218d67, ae43835e3, a0eb2c90b, 01bc422d4, 4cef615ef, 293baeecb, 1d580a0c1. Issues: #1088 and #1089 CLOSED with evidence comments; #1019 evidence-ready.

Card analyses: `docs/governance/opus-5-5-system-card-analysis-2026-09-23.md` (Codex draft plus this session's Review) and `docs/governance/gpt-6-system-card-analysis-2026-09-24.md`. Retained PDFs: `data/system_cards/anthropic-claude-opus-5-5-2026-09-22.pdf`, `data/system_cards/openai-gpt-6-astra-2026-09-03.pdf`. Registry: `data/frontier_model_cards.json`.

Doctrine: `docs/governance/untrusted-content.md` (pasted-content boundary and worked example), `docs/governance/opus-tuning.md`, `docs/governance/gpt-tuning.md`, `.gzkit/rules/agent-failure-modes.md` (0.8.2), `.gzkit/rules/model-selection.md` (0.6.2), `.gzkit/rules/tests.md` (0.26.5).

gz check change: `src/gzkit/commands/quality.py`, `src/gzkit/check_fingerprint.py`, `data/check_step_scopes.json`, `tests/governance/test_check_step_scopes.py`, `tests/test_check_fingerprint.py`, `docs/user/manpages/check.md`.

Budget authority: `data/instructions_files_budget.json`; chore log `.gzkit/chores/frontier-model-card-currency/proofs/CHORE-LOG.md`.

## Settled Rulings

1044 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
