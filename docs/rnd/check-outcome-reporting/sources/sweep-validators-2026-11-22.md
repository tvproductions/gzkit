# Sweep report: `gz validate` scopes and validators

Research subagent report, read-only, returned 2026-11-22 to the session that opened this run
(`e870dccc-bfdb-48be-baa8-a327a1e81cb8`), landed verbatim as delivered. A subagent's claim is
not evidence until re-derived (`.gzkit/rules/model-selection.md` claim 5); the claims this run
relies on are re-read in the record's `source` entries.

---

## Report: false-green validators in the `gz validate` track

I edited nothing in the repository. I made a scratch copy under /tmp to run `gz validate` in isolation. The repo's guard refused it ("this call is stamped as a dispatched subagent's … RP-12 ruling 17"), so I did not work around it, and I deleted the copy. Instead I ran non-writing scopes in the real repo. `.gzkit/ledger.jsonl` had 20809 lines before and after.

### Coverage
- **Registry:** `VALIDATOR_REGISTRY` (`src/gzkit/commands/validate_cmd.py:171`) holds 109 scopes: 23 default-tier and 6 CRITICAL (authorship, session_green_gate, bullet_retention, surface_weight, pointer_anchors, complexity_ceiling).
- **Dispatch:** I read all of it: `_run_scope_checks`, `_print_validation_result`, `_exit_for_errors`, the solo early-return handlers, the `--audits` umbrella and the four inventory handlers.
- **Validators read to the function body:** about 45 of 109, including every default-tier scope except `version` and `surfaces` (partial).
- **Pattern scan:** I inspected every `return []` site in context across 80 files in `trust_audits/`, `validate_pkg/` and `commands/validate_*.py`. I listed every swallowed exception (`except …: continue/pass/return None/{}`) and read about 15 of them.
- **Not read in depth:** event_*, type_ignores, utf8_prefix, test_tiers, class_size, version_release, pool_*, behave_req_tags, skill_alignment, advisory_scorecard, complexity_doctrine_links/thresholds, insights_shape, adr_status_fresh, obpi_lifecycle_coherence, adversarial_validation, the brief_* shape scopes, absorption_duplicates, distribution, changelog, surface_fidelity, vendor_manifest, setpoint_coherence, kind_invariance, persona_witness, mx_hardening, id_seam, status_writer_coverage, ontology_purity, brief_command_shape, tautological_test_audit, okf_conformance, deprecated_verb_prescription.

### Findings, most dangerous first

| # | Where | Class | What is printed | Tells "clean" from "did not check"? | Deliberate? |
|---|---|---|---|---|---|
| 1 | `validate_cmd.py:1057-1069` (`_route`), result at 1349-1353, JSON at 1913-1918 | (d) | stdout `✓ All validations passed (N scopes)`, exit 0, JSON `{"valid": true, "errors": []}`; findings go to stderr only | **No.** Observed now: `--hexagon-tests` and six other default scopes print `✓ All validations passed (7 scopes)` with exit 0 while 139 findings sit in stderr. With `GZKIT_MX_FULL_STRENGTH=1` it reports `valid=False, errors=139`. Safe mode is open (`.gzkit/mx.json` has `mode: safe`). Every default-tier scope is ERROR level, and only `ledger` is pinned (by name, in `GATE5_INVARIANTS`), so 22 of 23 default scopes are demoted right now, `commit_trailers` and `sensitivity` included. | Demotion is ruled: GHI #843 "Demoted, never discarded"; ADR-0.0.74; operator ruling 2026-10-17 R6. The green summary and `"valid": true` sitting beside demoted findings is **undocumented**. |
| 1b | `validate_cmd.py:968-987` `_sensitivity_exit_code` | (d) | Findings printed in red, then exit 0 | Partly: the findings are visible, the exit code is not | "demoted, never discarded (GHI #843; security-sensitivity clause 3)" |
| 2 | `closeout_proof.py:97-100` (`_find_obpi_briefs` globs `docs/design/adr/**/{adr_id}/obpis/*.md`), used at 448-454; gate caller `closeout_ceremony.py:290` | (c) | No findings, so the EXECUTE→ATTESTATION gate passes | No. Measured: `.gzkit/ceremonies/ADR-0.0.16.ceremony.json` (bare id) finds 0 briefs, so 0 REQs are checked (1 of 48 ceremonies). Two more paths to zero REQs: a missing ceremonies directory (`:412`), and a brief without an exact `## Acceptance Criteria` heading (`:50-52`; 0 of 563 briefs today). | Undocumented |
| 3 | `validate_req_kind.py:211-214` | (c) | `✓` | No. Measured: 10 briefs that are not finished (2 Active, 7 Draft, 1 in_progress, e.g. OBPI-0.39.0-02/03/06, OBPI-0.0.26-02) have REQs with no `[kind]` tag at all and pass. | The docstring says "legacy/grandfathered" but sets no date or status bound and cites no ruling. AGENTS.md says every REQ "MUST declare exactly one of three kinds". These contradict each other. |
| 4 | `surface_weight.py:53-55` with `_load_floor` at 231-235 (CRITICAL) | (b) | `✓` | No: a corrupt `data/surface_weight_floor.json` is read as None and the scope returns []. Unreadable rule files are also silently left out of the line count (`:228`). | Only "Bootstrap: no floor yet" is documented. The parse-error pass is undocumented. |
| 5 | `validate_commit_trailers.py:24-37, 58-66` (default) | (a)/(b) | `✓` | No: if git fails or is missing, each commit is skipped (`continue`), so zero commits are checked. | Undocumented (the docstring covers only the no-upstream case). This is the gate the stamping hook relies on (GHI #1017 comment). |
| 5b | same file `:127-142` `_issue_labels` | (a) | `✓` | No: if gh is unauthenticated, offline or rate-limited it returns [], and the Eval-feedback-source check never fires. | The docstring says "or [] when gh cannot answer". No ruling. |
| 6 | `hexagon_dependencies.py:61-67`, `hexagon_tests.py:186-192` (default) | (a) | `✓` | No: a missing pyproject, a missing `[tool.py-gzkit.hexagon]` table, or a misspelt one raises `PackageMapMissingError`, which returns []. | Undocumented in the audits; only the "Raises" doc of `load_package_map` mentions it. It reads as intended for adopters. |
| 7 | `complexity_ceiling.py:257-261` (CRITICAL); cognitive leg at 244-246 | (c)/(a) | `✓` | No: an empty wheel prediction (build backend not uv_build, or no module dir) returns []. Dropping `complexity.cognitive_ceiling` from `.gzkit.json` silently skips the cognitive leg. | `distribution.py:176` documents that it "returns the empty set" for a non-uv_build project. The consequence for complexity_ceiling, and for default-tier `wheel_path_literals`, is not stated. |
| 8 | `validate_frontmatter.py:274-283` (default) | (a)/(b) | `--frontmatter` alone prints nothing on success (`validate_cmd.py:1347-1349`) | No: "clean" and "did not check" are both empty output with exit 0. JSONDecodeError, KeyError or ValueError while building the graph returns []. Its docstring says the reconciliation chore receipt uses it. | The docstring says "or the ledger cannot be read". The CRITICAL `ledger` scope catches JSON faults in the default run, but not graph-build KeyError or ValueError. |
| 9 | `invariant_coherence.py:70-72` (default) | (a) | `✓` | No: if the resolved AgentContract consumer has no rendition, `render_agents_md` returns b"" and the scope returns []. A vendor-manifest routing change would silently turn off the composition-drift check. | "Bootstrap-safe" is documented. |
| 10 | `receipt_shape.py:36-61, 314-320` | (a) | `✓` | No: if the hard-coded glob `docs/design/adr/foundation/ADR-0.0.36-*/…` or its `date:` parse misses, the whole scope returns []. It resolves today (2026-04-26). | Docstring: "empty list if the ADR … cannot be located". |
| 11 | `lock_exchange_coupling.py:52-54, 170-181` | (c) | `✓` | No: the cutover comes from the OBPI-0.0.41-02/03 receipts. Without them, as in every adopter repo, nothing is ever checked. | The module docstring documents the derivation, not the consequence. |
| 12 | `validate_task_envelope.py:881-895` (git fails or 30 s timeout → {}); `:718` and `:842` (`except Exception` → empty) | (b) | `✓` | No. The code admits an empty channel is dropped from the comparison: "the failure is a quiet wrong verdict" (comment near :735, GHI #946). `git log --all` measured 0.05 s, so this is latent. | The broad excepts are commented "defensive; best-effort". The git path is undocumented. |
| 13 | `red_parity.py:99-104, 262-264` | (a)/(c) | `✓` | No: an unreadable ledger means no completions, so every brief is skipped. Completions are keyed by `brief.stem`, so a renamed brief drops out (1 of 29 post-cutover completions has no matching brief: OBPI-0.44.0-01-codex-config-generation). | Undocumented |
| 14 | `brief_reconcile.py:50-61` | (b) | `✓` | No: a brief that fails to parse for any reason is classed "legacy" and skipped. | Documented in code. The sibling `brief_structure` scope reports parse failures, but only when that scope is run. |
| 15 | `instructions_files_budget.py:242-260`; surface_delivery_witness and codex_delivery_witness (`:263-267`); agents_md_map criterion (d); `astral_discipline.py:668-672` (no baseline) | (e) observe-only | `✓`, notes on stderr | Only on stderr ("delivery unobserved … unverified, not confirmed") | Ruled: operator 2026-08-17, verbatim *"temporary stay of all control surface budget limits until version 1.0 … no blockers"*; the vendor-cap ruling of 2026-07-06 |
| 16 | 23 audit files hard-code `docs/design/adr` and return [] when it is not a directory; only 4 read `.gzkit.json` paths | (a)/(c), latent | `✓` | No, for an adopter whose ADR path differs (gzkit's own config matches) | Undocumented |
| 17 | Documented fail-open cases: reconcile_freshness without git (`reconcile.py:88-92`, "fail open per Architectural Boundary 4"); session_green_gate outside a worktree or under `CI` (`session_green_gate.py:223-227`, GHI #715); pending_renames on OSError/ValueError (comment: the ledger scope reports it); authorship with no suffix (gzkit sets one); how_coverage with no gz-how hub; `audit_attestation_receipts` (a no-op that is in no scope); a manifest artifact dir that does not exist is skipped (`validate_cmd.py:1232`) | (a) | `✓` | No | Documented |

### Amplifier
`dispatch_validator_scope` (`validate_cmd.py:654-674`) counts zero findings as proven, and it is not demoted. So every vacuous pass above (items 4–13) also proves any SUPPORT REQ citing that scope at closeout (via closeout_proof).

### Hardened examples to copy
- `taxonomy.py:309-324` and `validate_pkg/document.py:341-366` (GHI #736 and #742) turn a malformed or absent input into a finding.
- bullet_retention reports an absent scorecard when row identities are pinned.
- The hexagon audits report an unreadable baseline as a finding.
- `_refuse_combined_solo_scopes` (GHI #704).
- Only the solo handlers print counts on a green run: unscoped_rules ("N rule file(s) checked"), sensitivity ("N brief(s) checked"), and the four inventory scopes. The aggregate path's `✓ All validations passed (N scopes)` never says how many artifacts were checked, so no aggregate-path scope can tell "checked, clean" from "did not check".

### Defect tracking
None of these are filed. The ones with a live impact are #1 (observed now, 139 hidden findings), #2 (one ceremony resolves to zero briefs) and #3 (10 untagged briefs that are not finished). They need GHIs through `/ghi-author`, which I did not do because this track is read-only.

### Key paths
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py`
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/mx/checkpoint.py`
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/closeout_proof.py`
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_req_kind.py`
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/surface_weight.py`
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py`
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/hexagon_dependencies.py`
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/hexagon_tests.py`
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/complexity_ceiling.py`
- `/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_frontmatter.py`
- `/Users/jeff/Documents/Code/gzkit/.gzkit/ceremonies/ADR-0.0.16.ceremony.json`
