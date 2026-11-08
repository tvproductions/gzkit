# Rule validity review: batch C (2026-11-08)

Read-only review. Canon is `.gzkit/rules/*.md`. The `.claude/rules/` mirror and `src/gzkit/rules/` package copy have bodies byte-identical to canon for all eight rules (checked with diff after stripping frontmatter).
Validity: TRUE / STALE / UNVERIFIABLE. Usefulness: NEEDED / REDUNDANT / NO-OP.

---

## 1. agent-failure-modes.md (3,820 B; glob `AGENTS.md`, `.gzkit/rules/**`, `docs/governance/**`)

| # | Clause | Validity (evidence) | Usefulness |
|---|---|---|---|
| A1 | The patterns track the current frontier cards in `data/frontier_model_cards.json`: Fable 5.1/Mythos 5.1 §§ 2.3.3, 6.2.1, 6.4.2–6.4.5, 6.6.1; Opus 5.5 §§ 6.3.1, 6.4.1, 6.4.3–6.4.5, 6.5.1; GPT-6 Astra §§ 8.3.1, 8.6–8.8, 9.1–9.2 | TRUE. The registry has these three cards, all `status: current`. The Fable notes say "SS 2.3.3, 2.3.4.1, 3.2, 5.2, 6.1.2, 6.2.1, 6.2.2, 6.3.1, 6.4.2-6.4.5, 6.5.4, 6.6.1, 8.4, 8.5 consumed". The Opus sections are cited in `docs/governance/opus-5-5-system-card-analysis-2026-09-23.md:19,21,47`. The GPT-6 notes say "Source of failure-mode pattern 9". All three PDFs are present in `data/system_cards/`. | REDUNDANT: the registry, the `frontier-model-card-currency` chore and `agent-contract-rationale.md` carry this. |
| A2 | Cite patterns by name when reviewing, filing defects or extending the scorecard | TRUE. Scorecard row 49 uses this vocabulary, and `gz-issue-file/SKILL.md:82` and `gz-obpi-specify/SKILL.md:126` point at the rule. | NEEDED: the names exist nowhere else in an agent's context (root AGENTS.md has none). |
| A3 | Loading posture: advisory vocabulary, not a mechanical gate | TRUE | NO-OP |
| P1 | Safeguard circumvention: definition and backstop (ledger-and-hooks rule; ARB; Gate 5 universal) | TRUE. All three backstops exist in root AGENTS.md (Behavior Rules "Write the ledger only through `gz` commands. A blocking hook means…"; Attestation; Gate Covenant "Gate 5 is universal"). | Definition NEEDED; backstop REDUNDANT (AGENTS.md) |
| P2 | Reckless action: backstop is "DO IT RIGHT #1 (fix the class, not the instance); brief-boundary anti-pattern" | **STALE.** AGENTS.md DO IT RIGHT 1 reads "Fix the class of failure, not the instance.", which does not guard against an unauthorized hard-to-reverse action. "brief-boundary anti-pattern" is defined nowhere in canon. `docs/governance/behavior-rules.md:12-15` says the old Always/Never numbering is gone, and line 35 maps Never #5 to "pipeline stages, Step 4b". The term survives only in old `.claude/plans/*.md` ("brief-boundary discipline (Behavior Rules — Never #5)"). The real backstops are AGENTS.md Behavior Rules "Ask when unsure of direction…" and the brief allowed paths, which `agent-contract-rationale.md` names for this case ("actions are denied unless the brief names them"). | Definition NEEDED |
| P3 | Fabrication: ARB; § Attestation | TRUE (AGENTS.md § Attestation: "A fabricated receipt ID is a fabricated claim.") | Definition NEEDED; backstop REDUNDANT |
| P4 | Skipped cheap verification: DO IT RIGHT 6g, #4 | TRUE (AGENTS.md DO IT RIGHT 8 "(6g) Before recommending a command, run it…"; 4 "Verify observed behavior…") | Definition NEEDED; backstop REDUNDANT |
| P5 | Correction fails: insights rule; T1/T2/T3 | TRUE (AGENTS.md "When the operator course-corrects in flight, record an `improvement`…"; T1–T3 in `docs/governance/trust-doctrine.md`, cited at `agent-contract-rationale.md:334`) | Definition NEEDED; backstop REDUNDANT |
| P6 | Dishonest when caught: DO IT RIGHT 6h | TRUE (AGENTS.md DO IT RIGHT 9 "(6h) When a rule and a directive conflict, quote both verbatim.") | Definition NEEDED; backstop REDUNDANT |
| P7 | Hallucinated authorization: Gate 5 `--attestor` plus a non-empty `evidence.attestation_text`, written to the ledger | TRUE. `src/gzkit/ledger_semantics.py:69-77` `_human_attestation_is_valid` requires `attestation_text.strip()`; `order_ledger.py:408` refuses an empty attestor or attestation text. | Definition NEEDED; backstop REDUNDANT |
| P8 | Security shortcut: commit-through-hooks rule; push-back rule | TRUE (AGENTS.md "Commit and push through the configured hooks; `--no-verify` is not used."; "Push back when an approach has a clear problem…") | Definition NEEDED; backstop REDUNDANT |
| P9 | Metagaming: DO IT RIGHT #6; ledger-and-hooks; ARB plus the Layer-2 ledger | TRUE (AGENTS.md DO IT RIGHT 6 "Tests assert semantics derived from the REQ…") | Definition NEEDED; backstop REDUNDANT |

Counts (12 clauses): TRUE 11, STALE 1, UNVERIFIABLE 0. NEEDED 10, REDUNDANT 1, NO-OP 1. The Backstop column is redundant in every row.
**Verdict: KEEP-PARTIAL.** Keep the Pattern and Definition columns plus the A2 sentence, about 1,170 B measured for the two columns. Drop the card-section enumeration, which lives in the registry, and the Backstop column, which AGENTS.md already carries. Repair or drop the P2 backstop.
Side finding (not this rule): `docs/governance/agent-contract-rationale.md:541` names "the TTY+`ATTEST` authenticity gate" as a live defense. That gate was removed (`src/gzkit/commands/adr_audit.py:1153-1155`: "that gate was removed (GHI #1308), so the flag is accepted and inert").

---

## 2. gate5-runbook-code-covenant.md (3,049 B; glob `docs/**`, `src/gzkit/**`, so it loads on nearly every read)

| # | Clause | Validity | Usefulness |
|---|---|---|---|
| G1 | Docs must track behavior changes in the same patch set | TRUE | REDUNDANT: AGENTS.md PRIME DIRECTIVE 2 says "Code change with output format change → update ALL doc examples; commit together" |
| G2 | Three-layer table (runbook, governance runbook, manpages) | TRUE: all three paths exist | REDUNDANT: `cli.md` § New Subcommand obligations 2, 4 and 5; `gz cli audit` |
| G3 | Update command docs and examples | TRUE | REDUNDANT (G1, `cli.md`) |
| G4 | Update runbook flows and verification commands | TRUE | REDUNDANT (`cli.md` obligations 4 and 5) |
| G5 | Keep attestation language explicit where required | UNVERIFIABLE: "where required" names no target | NO-OP |
| G6 | Cite ARB-wrapped invocations; bare commands emit no receipt | TRUE | REDUNDANT: AGENTS.md § Attestation says "use the `gz-arb` skill… Bare lint, test or docs commands produce no receipt." |
| G7 | Heavy lane and foundation kind fail closed on missing receipts (exit 3 before attestation) | TRUE: `src/gzkit/commands/obpi_complete.py:366-396` matrix "heavy / any … exit 3", "any / foundation … exit 3"; `adr_audit.py:1047` calls it | REDUNDANT: AGENTS.md "Missing receipts warn on Lite and fail closed on Heavy." |
| G8 | Locked by `CANONICAL_STEP_COMMANDS` in `src/gzkit/canonical_steps.py` | TRUE (`canonical_steps.py:50`) | REDUNDANT |
| G9 | Bundle: `gz arb ruff`; `gz validate --documents --surfaces`; `gz arb step --name mkdocs -- …` | TRUE: the commands exist (`gz arb --help`, `gz validate --help`). But the bundle contradicts its own lead sentence: `gz validate --documents --surfaces` is not ARB-wrapped and emits no receipt. It also omits the typecheck and unittest steps that `gz-arb/SKILL.md:82-86` lists as canonical. | REDUNDANT: `gz-arb/SKILL.md` lines 38-88 is the authority AGENTS.md names |
| G10 | Do not leave placeholder output examples (plus the 2026-08-08 measurement narrative) | TRUE as a dated record | NO-OP: a model does not ship placeholders by default, and most of the clause is history |
| G11 | Do not update code without docs when command output changes | TRUE | REDUNDANT (PRIME DIRECTIVE 2) |
| G12 | Do not declare completion without human attestation; it is universal | TRUE | REDUNDANT: AGENTS.md Gate Covenant "Gate 5 is universal…" |
| G13 | Do not cite bare `gz lint` or `mkdocs build --strict` as evidence | TRUE | REDUNDANT (AGENTS.md § Attestation) |

Counts (13): TRUE 12, STALE 0, UNVERIFIABLE 1. NEEDED 0, REDUNDANT 11, NO-OP 2.
**Verdict: RETIRE.** Its doctrine already lives in AGENTS.md (PRIME DIRECTIVE 2, Gate Covenant, § Attestation), `cli.md` § New Subcommand, and `gz-arb/SKILL.md`. Because of its broad glob it adds 3,049 B to almost every session.
Scorecard: row 50a cites "`CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py`". The table moved to `canonical_steps.py` on 2026-08-22, and `validator.py` only re-exports it. That is a stale citation in the scorecard, not in the rule.

---

## 3. changelog-release-notes.md (3,743 B; glob `CHANGELOG.md`, `RELEASE_NOTES.md`)

| # | Clause | Validity | Usefulness |
|---|---|---|---|
| C1 | Two distinct artifacts, one source (closed GHIs), two projections | TRUE (`gz-patch-release/SKILL.md:282-283`, `:357-363`) | REDUNDANT (`gz-patch-release` Steps 4b and 4b-bis) |
| C2 | Conform to the template; the category set and its order; omit empty categories | TRUE for the set (`src/gzkit/validate_pkg/changelog.py:20-30`). The validator does not check order. | REDUNDANT (template plus validator) |
| C3 | SemVer, ISO dates, header `## {version} ({date})` | TRUE (`changelog.py:36` `_VERSION_RE`; `CHANGELOG.md:20` `## v0.34.9 (2026-10-11)`) | REDUNDANT (the validator message) |
| C4 | Every entry cites `GHI #N`; never invent a PR link | TRUE (`changelog.py:37,96-103`). "Every entry" is slightly broader than the code: Release highlights are exempt (`changelog.py:34`). | REDUNDANT (witness) |
| C5 | Coverage reconciled fail-closed at release time by `gz-patch-release` | TRUE as skill prose (`SKILL.md:370-373` "A discovered GHI with no changelog entry blocks the release"). No code enforces it. | REDUNDANT (the skill) |
| C6 | Release notes: follow the template, plain language, past tense, never "Fixed the bug" | TRUE (`.gzkit/templates/release_notes.md:19`; `SKILL.md:281`) | REDUNDANT |
| C7 | Keep `### Gate Evidence` | TRUE (`release_notes.md:54`; `SKILL.md:290,354`) | REDUNDANT |
| C8 | Author both files through `gz-patch-release`, never by hand | TRUE (`SKILL.md:87-88`) | **NEEDED**: the glob fires exactly when an agent opens the file to hand-edit it, the skill is not running then, and AGENTS.md is silent on this |
| C9 | Enforcement split; release approval is not Gate 5 | TRUE (`validate_cmd.py:418` explicit tier; AGENTS.md "Gate 5 names completed OBPI/ADR work only") | REDUNDANT |
| C10 | `--changelog` is not in the default `gz check` | TRUE (`_ScopeEntry("changelog", "explicit", …)`) | REDUNDANT |

Counts (10): TRUE 10, STALE 0, UNVERIFIABLE 0. NEEDED 1, REDUNDANT 9, NO-OP 0.
**Verdict: KEEP-PARTIAL.** Only C8 survives, plus a one-line pointer to `gz-patch-release` and the templates: about 250 B. Before slimming, re-point `gz-patch-release/SKILL.md:88,283,355` and `cli.md`, which cite this rule.

---

## 4. weaponeering.md (2,464 B; glob pipeline_dispatch/runtime, `gz-obpi-pipeline/**`, OBPI briefs)

| # | Clause | Validity | Usefulness |
|---|---|---|---|
| W1 | The REQ kind fixes the sortie set (behavior: constraints, red, green; support: one documentary sortie; fence: none) | UNVERIFIABLE. No sortie layer exists. `pipeline_dispatch.py` and `pipeline_runtime.py` contain no "sortie", `order_ledger.py` models no sortie set, and briefs 16–18 of ADR-0.35.0 are `status: Draft`. Only the fence half has a witness (`--req-kind-discipline`). | NEEDED (no other home) |
| W2 | The constraints sortie lands contracts before red, so red fails on an assertion | TRUE as doctrine | REDUNDANT: `gz-obpi-pipeline/references/stage-2-implement.md:44-52` says "create the importable skeleton (define the symbol as a no-op stub…), then watch each test fail on its OWN assertion" |
| W3 | Subtraction cites evidence (the red and constraints skip grounds) | UNVERIFIABLE: scorecard 98b says "no order carries a skip citation today" | NEEDED |
| W4 | Addition is free | UNVERIFIABLE (a permission) | NO-OP |
| W5 | Green and assessment are never waived | TRUE: the REQ-coverage gate and Step 4b exist | REDUNDANT: AGENTS.md § OBPI Acceptance Protocol (REQ-coverage gate) and the pipeline skill's Step 4b |
| W6 | The runtime checks it and the planner never decides; advisory until then | TRUE (no runtime exists) | NO-OP (self-description) |
| W7 | Witness: none; 207 of 282 red receipts failed on `error` (2026-10-05) | TRUE as a dated record | NO-OP (history) |
| W8 | Do not skip red because it would obviously fail | TRUE | REDUNDANT: `tests.md` Red ("A test that passes on first run is not Red"); stage-3 `gz arb red` |
| W9 | Do not fold constraints into red | TRUE as glossed. There is a tension with stage-2, where the implementer builds the stub inside the red step, but the result is still an assertion red, so the gloss holds. | REDUNDANT: `stage-3-verify.md:90` reports an `error` red as "a constraints sortie not flown" |
| W10 | No planner, skill or session chooses the sortie set | UNVERIFIABLE | NEEDED (restates W1/W6) |

Counts (10): TRUE 6, STALE 0, UNVERIFIABLE 4. NEEDED 3, REDUNDANT 4, NO-OP 3.
**Verdict: RETIRE as a rule.** No clause is both TRUE and NEEDED: the needed clauses (W1, W3, W10) describe a runtime layer that does not exist yet. Move claims 1, 3, 5 and 6 to the design artifact for the sortie layer (ADR-0.35.0 briefs 15–20 / the run `renewing-vows` row 1) or to a `docs/governance/` doctrine page. Re-point `stage-3-verify.md:90` and `.gzkit/rules/model-selection.md:65-67`, which cite this rule.

---

## 5. gh-cli.md (5,251 B; glob `.github/**`, `docs/design/adr/**`, `issue_cmd.py`)

**Reach:** `gh` runs through Bash, and a path-scoped rule never loads on Bash. This rule reaches the agent only when an earlier Read or Edit matched its glob, usually any ADR doc under `docs/design/adr/**`. In practice it arrives as 5.2 KB on ADR reads, and is absent at the moment someone counts issues.

| # | Clause | Validity | Usefulness |
|---|---|---|---|
| H1 | Use `gh` for defect tracking, closeout, release, or an active brief / explicit request | TRUE (scorecard 51) | NO-OP |
| H2 | `gh issue create` is forbidden as a direct call; use `/ghi-author`; cross-repo via `gz issue file` | TRUE | REDUNDANT: AGENTS.md "Author GHIs through `ghi-author`… from another repository use `gz issue file`"; `ghi-author/SKILL.md:342` |
| H3 | The ban is on the caller, not the string; ghi-author Step 5 calls `gh issue create` | TRUE (`ghi-author/SKILL.md:298`) | REDUNDANT |
| H4 | Allowed list/close/comment/reopen/release commands; release notes take the newest block only (GHI #710) | TRUE (`ghi-close/SKILL.md:396,456`; `ghi-author/SKILL.md:167`; `gz-patch-release/SKILL.md:392-400`) | REDUNDANT (each command's owning skill) |
| H5 | A comment carries a relationship, not a transcribed state; write the bare `#N` | TRUE (`ghi-author/SKILL.md:282-284,363,368`; chore `ghi-cross-reference-staleness` exists) | REDUNDANT (ghi-author Step 4) |
| H6 | `gh <noun> list` returns one page (default 30) with exit 0 | TRUE, observed today: `gh issue list --state open --json number --jq 'length'` printed `30`, and the search total printed `142` | NEEDED: no skill carries it (grep for `total_count`/`incomplete_results` hits only `rule-version-history.md` and `advisory-rules-audit.md`) |
| H7 | A scoped search never supports "no such issue exists" | TRUE | NEEDED |
| H8 | Count from search `total_count` together with `incomplete_results` | TRUE: the command printed `142` | NEEDED |
| H9 | Inventory: paginate, or verify against the total | TRUE | NEEDED |
| H10 | An explicit `--limit` alone is insufficient | TRUE (follows from H6) | NEEDED |
| H11 | Book the method beside the figure | UNVERIFIABLE | NEEDED |
| H12 | Prohibited without approval: settings, secrets, force push, merging | TRUE | REDUNDANT: the harness permission and safety rules; scorecard 52 says "Permission model lives in `.claude/settings.json`" |
| H13 | gzkit-surface defects from consumers go to tvproductions/gzkit via `gz issue file`; the wrapper stamps, validates and hard-rejects | TRUE (`src/gzkit/commands/issue_cmd.py:4-6,136-145`) | REDUNDANT: AGENTS.md, the `gz-issue-file` skill, and the wrapper's rejection message (`issue_cmd.py:45-47`) |
| H14 | PII: the wrapper stamps only the slug and gz version | TRUE (`issue_cmd.py:4-5`) | NO-OP |

Counts (14): TRUE 13, STALE 0, UNVERIFIABLE 1. NEEDED 6, REDUNDANT 6, NO-OP 2.
**Verdict: KEEP-PARTIAL.** Only the census section (H6–H11, about 2,050 B) survives. Its glob never fires when the census runs, so its proper home is the skills that count issues: `ghi-triage`, `gz-status`, `gz-session-handoff` (and the handoff chain that booked 30 as the queue, GHI #972). Moving it there and retiring the rule would put the doctrine where it binds.

---

## 6. security-sensitivity.md (5,359 B; glob OBPI briefs, `data/security_surfaces.json`)

**Load-bearing file.** `src/gzkit/commands/obpi_complete.py:84-127` reads this rule at runtime for the walkthrough checklist; `_load_security_checklist` raises `GzCliError` when the file is missing. `tests/governance/test_security_sensitivity_rule.py` (REQ-0.0.22-06-01..06) asserts its headings. AGENTS.md and the `--sensitivity` validator message both cite it.

| # | Clause | Validity | Usefulness |
|---|---|---|---|
| S1 | Security work gets heightened review; attestation is universal; the axis is additive | TRUE | REDUNDANT: AGENTS.md "`security` sensitivity adds security-scan requirements to Gate 5"; "Gate 5 is universal" |
| S2 | The registry is `data/security_surfaces.json`; editing it requires a brief declaring security | TRUE (the file exists) | NEEDED (no witness message says so) |
| S3 | Direct-fix path: no brief, so the declaration is a discipline obligation (state the sensitivity in the commit body, cite the GHI) | Substance TRUE. Citation **STALE**: the rule says "`validate_cmd.py`: `declared = frontmatter.get("sensitivity")`", but that line is at `src/gzkit/commands/validate_sensitivity.py:74` (also `trust_audits/sensitivity.py:165`) | NEEDED |
| S4 | Auto-detect floor: overlap without a declaration exits 3 | TRUE, observed: `uv run gz validate --sensitivity` gave `exit=3` with two `[sensitivity-floor-violation]` findings (OBPI-0.39.0-01, OBPI-0.39.0-02) | REDUNDANT: the witness message names the fix ("Declare 'sensitivity: security'; or if the overlap is an incidental false positive, narrow the Allowed Paths or discharge at completion via 'gz obpi complete --accept-security-floor'.") |
| S5 | Escalate, never escape; both the omitted and the wrong declaration exit 3 (GHI #625) | TRUE (`trust_audits/sensitivity.py:184,212`; both types are in `_POLICY_BREACH_ERROR_TYPES`) | REDUNDANT (witness) |
| S6 | Inside the MX hangar the floor demotes to advisory: "When `.gzkit/mx.json` exists … `checkpoint.resolve("sensitivity", …)` returns ADVISORY and the exit-3 errors above are dropped from the exit code"; see GHI #682, "two post-cutover briefs currently failing"; "do not do it without first discharging #682" | **STALE.** (a) Observed with the condition on: `marker.condition()` printed `cause='on'` (level `drydock`), yet `gz validate --sensitivity` exited 3. The dedicated handler `_run_sensitivity_scope` (`validate_cmd.py:894-917`) ends `if any(f.type in _POLICY_BREACH_ERROR_TYPES for f in findings): raise SystemExit(3)` and never consults `checkpoint`. Demotion happens only on the `_run_scope_checks` umbrella path (`validate_cmd.py:981-995`). (b) `gh issue view 682` reports `CLOSED`, so "currently failing" and "first discharging #682" are out of date. (c) The trigger is `marker.condition(...).on` (`mx/checkpoint.py:53-70`), not mere existence of `mx.json`. | NEEDED (if it were true) |
| S7 | Grandfather cutover: 87 briefs; new briefs must declare; narrow the paths or use `--accept-security-floor`; do not add grandfather entries | TRUE (`data/sensitivity_floor_grandfather.json` `grandfathered_briefs: 87`) | "Do not add entries" NEEDED; the rest REDUNDANT (witness message) |
| S8 | Heightened walkthrough: surface enumeration, `arb-step-security-scan-*` receipt confirmation, classification confirmation, co-presence proxy gate; scanner-unavailable is fail-closed | **STALE** on several counts. (a) The receipt glob is `_SECURITY_RECEIPT_GLOB = "arb-step-security-*.json"` (`obpi_complete.py:89`), not `-scan-*`. (b) No scanner exists: `canonical_steps.py:135` has `"security": []`, so every `sensitivity: security` completion exits 3 ("Security-scan canonical slot … is unfilled") unless `--accept-security-floor` is passed. That flag returns before the receipt checks and the walkthrough (`obpi_complete.py:227-238`), and it downgrades the sensitivity so "the security walkthrough is skipped" (`:1216-1219`). (c) The checklist is parsed from this file under a heading matching `^\s*#{2,3}\s+walkthrough\s+checklist\s*$` (`obpi_complete.py:85-88`). This rule has no such heading (its headings: Invariant, Registry contract, `gz validate --sensitivity`, Grandfather cutover, Heightened walkthrough, Do Not), so the rendered checklist is empty. The unit test passes only because it uses a synthetic body containing `## Walkthrough Checklist` (`tests/commands/test_obpi_complete_security.py:122`). (d) `_render_security_walkthrough` prints only OBPI, parent ADR and checklist items: no surface enumeration, no classification confirmation. (e) The co-presence/TTY gate was removed (`adr_audit.py:1153-1155`, GHI #1308). Only "scanner-unavailable is fail-closed" holds, by accident: the empty slot exits 3. | NEEDED (if repaired) |
| S9 | Do Not: declare `sensitivity: absent` while touching a surface | TRUE | REDUNDANT (witness) |
| S10 | Do Not: edit the registry without declaring security | TRUE | NEEDED (= S2) |
| S11 | Do Not: narrative substitution for the scan receipt | UNVERIFIABLE (no scanner exists) | REDUNDANT: AGENTS.md "A fabricated receipt ID is a fabricated claim." |
| S12 | Do Not: bundle security work into a non-security parent OBPI | UNVERIFIABLE | NEEDED |

Counts (12): TRUE 7, STALE 3, UNVERIFIABLE 2. NEEDED 7 (S6 and S8 only if repaired), REDUNDANT 5, NO-OP 0.
**Verdict: KEEP-PARTIAL. It cannot be retired without code changes.** Survivors: S2/S10 (about 200 B), S3 with the path corrected (about 920 B), S7's "do not add grandfather entries" sentence (about 200 B), and S12. S6 and S8 need repair or deletion. If the operator wants a checklist to render, S8 must gain a `## Walkthrough Checklist` section.
Live defects: (1) the walkthrough checklist is always empty in production. (2) No scanner is wired into the security slot. (3) `--sensitivity` ignores the MX demotion that canon claims. (4) `--sensitivity` is an explicit-tier scope run by no `gz check` step (`src/gzkit/commands/quality.py:700-770` has none), so two live floor violations on ADR-0.39.0 briefs go unseen. AGENTS.md says "`uv run gz check` runs every registered validator", which is false for this scope.
Scorecard rows that score STALE clauses:
- Row 48a: "with `.gzkit/mx.json` present `checkpoint.resolve("sensitivity", …)` returns ADVISORY and clause 2's exit-3 errors drop out of the exit code" (S6).
- Row 48b: "`validate_cmd.py`: `declared = frontmatter.get("sensitivity")`" (S3 path).
- `advisory-rules-audit.md:779`: "reserved `arb-step-security-scan-*` ARB s…" (S8).
- Row 48 scores the invariant **Mechanical** while nothing in `gz check` runs the scope.

---

## 7. complexity-doctrine.md (6,235 B; glob `docs/governance/complexity/**`, `data/exemplar_corpus.json`, `src/gzkit/complexity/**`)

Load-bearing: `trust_audits/complexity_doctrine_links.py:71` scans this file, and `tests/governance/test_complexity_doctrine_rule.py` has 11 tests that read it.

| # | Clause | Validity | Usefulness |
|---|---|---|---|
| D1 | Calibrate against an operator-curated corpus; ADRs 0.0.28, 0.0.29 and 0.0.30 cite the doctrine | TRUE (all four foundation ADR dirs exist; `--complexity-doctrine-links` passes: "✓ All validations passed (1 scopes).") | REDUNDANT: AGENTS.md "Complexity calibration is grounded in an empirically-measured exemplar corpus — `gz validate --complexity-doctrine-links` (ADR-0.0.27)." |
| D2 | A learning relationship, not adoption (click) | TRUE: click is not in `[project] dependencies` | NEEDED |
| D3 | Selection criteria 1–7 | Criterion 7 TRUE (all 13 corpus entries carry a pinned SHA); the rest are judgment (scorecard 50a) | NEEDED (when editing `exemplar_corpus.json`) |
| D4 | Disqualifiers 1–7 | UNVERIFIABLE (scorecard 50b: post-hoc fitting "leaves no trace in the artifact") | NEEDED |
| D5 | Cadence: annual, signal (>25% verdict drift, 6-month guard), judgment | UNVERIFIABLE: no code implements the signal trigger (grep for verdict-frequency in `src/` finds only the AGENTS.md and rule copies) | REDUNDANT (`gz-complexity-distill/SKILL.md:29-44`) |
| D6 | Distillation steps 1–6 (percentiles, practitioner eye, >10% diff narration, dated output, never overwrite) | TRUE (`src/gzkit/complexity/distillation.py:47,197-269`; both `distilled-characteristics-2026-05-04.md` and `-2026-10-22.md` preserved; the 10-22 doc has "Boundaries that moved by more than 10%") | REDUNDANT (`gz-complexity-distill/SKILL.md:84-92`; `gz complexity distill`) |
| D7 | Cite the distilled doc, never the raw corpus | TRUE | REDUNDANT (witness in `gz check`, the "Complexity-doctrine links" step) |
| D8 | Canonical tuple: frozen Pydantic `Citation`, extra=forbid; schema additionalProperties false | TRUE (`complexity/citation.py:25,28`; `schemas/complexity_citation.json:8`) | REDUNDANT (the model rejects) |
| D9 | Canonical string example `distilled-characteristics-2026-05-04.md § radon-cc (corpus revision 1)` | **STALE.** Radon is retired: `pyproject.toml:45-46` "Radon retired in RO-9 tranche 4 (GHI #1183)"; `complexity-thresholds.md` "Radon's seven (`radon_cc`, …) retired with Radon in RO-9 tranche 4 (GHI #1183)". The binding doc is now 2026-10-22, whose sections are `lizard_*` and `cohesion_lcom4`; `complexity-thresholds.json` cites `"section_anchor": "lizard-ccn"`. | REDUNDANT |
| D10 | Field constraints (path, anchor, revision) | TRUE (`citation.py` parse) | REDUNDANT |
| D11 | Percentile and absolute pairing, "(e.g. p90 = 7)" | Rule TRUE (validator row 51). The example is **STALE**: p90 = 7 was `radon_cc`; `complexity-thresholds-rationale.md:136` says "the warn band is Lizard's p90 of 8 where `radon_cc`'s was 7" | REDUNDANT (validator) |
| D12 | Refresh portability: two-revision window | TRUE (`citation.py:14` `DEFAULT_SUPPORTED_WINDOW: int = 2`) | REDUNDANT (validator flags) |

Counts (12): TRUE 8, STALE 2, UNVERIFIABLE 2. NEEDED 3, REDUNDANT 9, NO-OP 0.
**Verdict: KEEP-PARTIAL.** Keep the learning/adoption paragraph, the Selection Criteria and the Disqualifiers (about 1,900 B). Replace the radon example with the lizard-ccn form. Cadence, procedure and citation are carried by `gz-complexity-distill`, the `Citation` model and the links validator. The `test_complexity_doctrine_rule.py` assertions must be reconciled before any section is removed.
Side observations: both distilled docs carry `corpus_revision: 1` even though a re-distillation happened. The 2026-05-04 doc's own example ("§ Cyclomatic Complexity (corpus_revision 1)", line 189) does not match the canonical form. `--complexity-doctrine-links` passes while the rule cites a retired-metric anchor.

---

## 8. complexity-thresholds.md (5,846 B; plus the JSON, 3,031 B)

Load-bearing: the validator reads the `## Bootstrap absolutes` heading of this `.md` (`trust_audits/complexity_thresholds.py:36-39`); `tests/governance/test_complexity_thresholds_rule.py` has 12 tests.
Threshold check: the JSON bands match the rule's description: six metrics (`measurement.py:50-57` `CANONICAL_METRICS`), each with a block band (`lizard_file_nloc` p99 3130.24, `lizard_nloc` p95 37, `lizard_param_count` p95 5, `lizard_nesting_depth` p95 7, `lizard_ccn` p95 11, `cohesion_lcom4` p99 8). Two other live ceilings exist: `pyproject.toml:168-169` `max-complexity = 20` and `.gzkit.json` `complexity.cognitive_ceiling: 15`. The rule names no xenon or radon except as retired.

| # | Clause | Validity | Usefulness |
|---|---|---|---|
| T1 | Data lives in the JSON; Pydantic loader; schema mirror | TRUE (`thresholds.py:97-118`) | REDUNDANT: loader error "The markdown rule body carries narrative only; data lives in JSON (GHI #426)" |
| T2 | Binds the 2026-10-22 doc, revision 1, `§ lizard-ccn` | TRUE (the JSON `citation`) | REDUNDANT (the JSON) |
| T3 | One canonical table; the advisor and guide consume it; any other threshold authority is drift | Normative half TRUE. Descriptive half **STALE.** The live gates read other authorities: pre-commit runs `gz validate --complexity-ceiling` at "Ruff's max-complexity, cognitive at .gzkit.json's" (`.pre-commit-config.yaml:75-77`), i.e. 20 and 15, against the table's `lizard_ccn` block at 11. The advisor consumes `lizard_ccn` only: `complexity_advise.py:132` `metrics_checked = 1  # currently only lizard_ccn`; `functions.py:36` `METRIC_KEY = "lizard_ccn"`. `pythonic.md` concedes "a *third* ceiling, matching neither authority". | NEEDED (normative half) |
| T4 | Every metric must carry a block band | TRUE (`thresholds.py:62-71`) | REDUNDANT (loader error) |
| T5 | Exactly three trigger values; amendment needs ADR-0.0.28 | TRUE (`thresholds.py:29,41`; schema enum) | REDUNDANT |
| T6 | block: "`gz complexity advise` exits 3 and the auto-chain hook refuses the commit" | Exit 3 TRUE (`complexity_advise.py:234-236`). Hook half **STALE in this repo**: the committed pre-commit runs `complexity-ceiling`, and `.pre-commit-config.yaml:72-74` says "The auto-chain installer (`python -m gzkit.hooks.install_complexity_advisor`) replaces this entry". Scorecard 51e: "The hook is opt-in and not installed in this repository". Only the `lizard_ccn` block band reaches `advise`. | NEEDED |
| T7 | warn: advisor recommendation | TRUE for `lizard_ccn` only | NEEDED |
| T8 | advise: authoring guide only | TRUE (`complexity_guide.py:4` "Emits `AuthoringHint` blocks for `advise`-band crossings only") | NEEDED |
| T9 | A fourth value is forbidden | TRUE (Literal and enum) | REDUNDANT |
| T10 | Six canonical metrics; Radon's seven retired | TRUE (`measurement.py:50-57`) | REDUNDANT |
| T11 | "the loader fails closed when a canonical metric is missing a block-band row" | TRUE combined, attribution imprecise: the loader checks block bands only for metrics present; canonical presence is the validator's check ("asserts every canonical metric has at least one band") | REDUNDANT |
| T12 | Bootstrap carve-out: `cohesion_lcom4` (GHI #1265) | TRUE | NEEDED (and the validator reads this heading) |
| T13 | Amendment protocol; "Silent edits are forbidden by the validator (… `gz validate --complexity-thresholds`)" | **STALE / overclaim.** The validator's docstring lists its checks (load, canonical coverage, citation parse, bootstrap notice). Nothing detects an unannounced band edit, and scorecard 51d scores the protocol **Judgment**. `gz validate --complexity-thresholds` printed "✓ All validations passed". | NEEDED (normative) |

Counts (13): TRUE 10, STALE 3, UNVERIFIABLE 0. NEEDED 6, REDUNDANT 7, NO-OP 0.
**Verdict: KEEP-PARTIAL.** Keep the Invariant (normative), the vocabulary table, the Bootstrap section and the amendment-protocol pointer: about 1,725 B (Invariant + Vocabulary) plus about 1,250 B (Bootstrap + Amendment), about 3,000 B. Repair T3's consumer claim, T6's hook claim and T13's "forbidden by the validator".
Scorecard: row 51e scores T6 as Promotable and discloses the uninstalled hook, so the row is accurate about the gap while the rule clause stays stale.
