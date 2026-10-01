# Audit C: did past work pass through the #849, #927 or #1057 gaps while they were open?

Record dated 2026-09-30. Diagnosis only: nothing was repaired, and no ledger rows, receipts, labels or commits were written. The scripts are in this evidence directory (`audit1057.py`, `touch3.py`, `tier.py`, `red849.py`), and so are the raw outputs (`audit1057.json`, `touch3.json`, `tier.json`, `red849.json`, `obpi849.json`). Nothing ran `gz arb red` or a mutation sweep. The only code imported was the current read-only predicates (`_extract_plan_paths`, `_path_within_allowed`, `extract_allowed_paths`, `red_parity._collect`).

Classes:
- **EXPLOITED**: work went through the open gap, and the gate reported green on a condition it existed to catch.
- **EXPOSED-CLEAN**: the work ran while the gap was open, but the evidence shows the gap did not affect the result.
- **UNDETERMINABLE**: evidence named in the row is missing.

---

## 1. GHI #1057: plan-audit containment passed every out-of-scope path

**Defect (isolated from the shared commit `cc5ed5bfa`).** The #1057 part of `cc5ed5bfa` is confined to four files: `src/gzkit/commands/plan_audit_cmd.py` (`_extract_plan_paths`, `_path_within_allowed`), `tests/test_plan_audit_scope.py` (new, 110 lines), `tests/test_plan_audit_cmd.py` and `docs/user/manpages/plan-audit.md`. The other changes in the commit (smoke, adr_promote, config paths and so on) belong to #960 and #1047–#1061. Before the fix, the predicate ended with `return True  # If we can't determine, don't block`, so `_gather_brief_path_gaps` could never produce the gap "Plan references path outside brief scope". The old unit test asserted that permissive result (`test_no_match_returns_true`). The fix inverts it to `test_no_match_is_outside_scope`.

**Window.** It opens at `d773bcfb7` (2026-04-01T10:35Z). `git log -S "If we can't determine, don't block"` gives only `d773bcfb7` (added) and `cc5ed5bfa` (removed), so the predicate had the fallback from the day it was created. It closes at `cc5ed5bfa` (2026-09-19T23:23Z). The one receipt older than the CLI (2026-03-16) was written by the skill, not by this code, and is excluded.

**Population.** Plan-audit writes no ledger event (the ledger has no plan-audit event type). Its evidence is `.claude/plans/.plan-audit-receipt-<OBPI>.json`, which is tracked in git and overwritten on each run. Every committed version was recovered with `git log --diff-filter=AM -- '.claude/plans/.plan-audit-receipt*'`, which gave 507 file versions. After deduplicating on (obpi_id, timestamp), the window holds **421 receipts, 401 of them PASS, covering 307 OBPIs** whose PASS could be replayed, plus 10 OBPIs whose plan file was not in git at the receipt commit. Receipts that were overwritten between commits are not visible, so this count is a lower bound.

**Method.**
1. For each PASS receipt, read the plan (`git show <receipt-commit>:.claude/plans/<plan_file>`) and the brief as they stood at the commit that carried the receipt. Take the allowlist from the brief with `extract_allowed_paths`.
2. Extract the plan's paths with the **pre-fix** extractor (reproduced verbatim from the diff) and test them with the **post-fix** predicate. The result is the set of paths the old gate saw and should have rejected. 306 of the 307 plans name at least one such path, but most are read-only references (briefs, ADRs, context files). The fixed gate also rejects references (manpage: "checks referenced as well as modified explicit paths"). So "named" alone is not treated as exploitation.
3. **Exploitation test.** A `src/` or `tests/` path that the plan named, that sits outside the brief allowlist, and that a commit modified between the PASS receipt and the OBPI's first `obpi_receipt_emitted` after it (plus 30 minutes). Commits that name a different OBPI were excluded. `docs/` paths were not scored, because plans routinely edit their own brief and ADR.
4. Spot-checks by hand against the plan text and the commit diff, all confirmed:
   - OBPI-0.0.26-01: the plan lists `src/gzkit/events.py`, `src/gzkit/commands/adr_promote.py` and `src/gzkit/ledger.py` as files to modify. The brief allowlist names none of them; it names a stale `src/gzkit/governance/ledger_events.py`. Commit `32adb990c` modified all three, and the receipt carries `"verdict": "PASS", "gaps_found": 0`.
   - OBPI-0.0.33-05: the plan lists `src/gzkit/commands/validate_cmd.py` and `src/gzkit/quality.py`, neither is allowlisted, and `f6af0e6a5` modified both.
   - OBPI-0.35.0-09: the plan names `tests/governance/test_rendition_*.py`, which is outside `tests/test_sync_surfaces.py`. Commits `0f666fa94` and `521decc75` modified them.

**Result.**

| Class | OBPIs | Evidence basis |
|---|---|---|
| EXPLOITED (substantive `src/` or `tests/` file) | **56** | Table rows 1–56 |
| EXPLOITED (only a package `__init__.py` outside the allowlist) | 10 | Rows 57–66. Out of scope by the letter of the brief, trivial in substance |
| UNDETERMINABLE: the allowlist uses a `<slug>` placeholder (OBPI-0.0.17-05, 0.0.32-08, 0.0.32-09, 0.0.34-02) | 4 | The predicate cannot decide whether the placeholder covers the file |
| UNDETERMINABLE: 12.1 h window with untagged commits only (OBPI-0.35.0-04) | 1 | Attribution not provable |
| UNDETERMINABLE: plan file missing from git at the receipt commit (OBPI-0.0.12-07, 0.0.13-06, 0.0.15-02, -03, -04, 0.25.0-02, -04, -08, -13, -21) | 10 | The plan text cannot be recovered |
| EXPOSED-CLEAN: no out-of-scope `src/` or `tests/` path both named and modified | 223 | `touch3.json` |
| EXPOSED, never completed after the PASS (no completion went through) | 13 | `touch3.json` (`completed: null`) |

Caveats. Only 3 of the 71 candidate briefs were later amended so that their allowlist now covers the touched file. In many rows the brief's allowlist was stale and the plan corrected it: the scope breach was real, but the work was arguably what the intent required. The gate should have surfaced these for a brief amendment, and it did not. Out-of-scope modifications that the plan never named are not #1057 exploitation, because containment could not have caught them, so they are not counted here.

| # | OBPI | Class | PASS receipt (ts, commit carrying it) | Plan file | Out-of-scope path(s) named in plan and modified | Modifying commit(s) |
|---|---|---|---|---|---|---|
| 1 | OBPI-0.0.17-02 | EXPLOITED | 2026-04-19T15:09Z, `70853ae23` | `sunny-booping-lecun.md` | `src/gzkit/cli/parser_governance.py`, `src/gzkit/templates/adr_pool.md` | `dd63c3b45` |
| 2 | OBPI-0.0.17-06 | EXPLOITED | 2026-04-19T20:06Z, `70853ae23` | `enchanted-munching-hollerith.md` | `src/gzkit/templates/agents.md`, `src/gzkit/templates/copilot.md` | `d8f05c449` |
| 3 | OBPI-0.0.18-04 | EXPLOITED | 2026-04-20T11:58Z, `6764d94b7` | `swirling-beaming-manatee.md` | `src/gzkit/cli/parser_governance.py` | `6764d94b7` |
| 4 | OBPI-0.0.20-01 | EXPLOITED | 2026-04-22T12:29Z, `a2a92d173` | `adaptive-squishing-lovelace.md` | `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/commands/quality.py`, `src/gzkit/commands/validate_cmd.py` | `a2a92d173` |
| 5 | OBPI-0.0.20-02 | EXPLOITED | 2026-04-22T13:09Z, `b2ae1c06f` | `OBPI-0.0.20-02-fold-agent-contract.md` | `src/gzkit/templates/agents.md`, `tests/AGENTS.md`, `tests/governance/test_agent_contract_fold.py` | `b2ae1c06f` |
| 6 | OBPI-0.0.20-04 | EXPLOITED | 2026-04-23T11:54Z, `efc46535e` | `compressed-painting-kernighan.md` | `tests/governance/test_attestation_fold.py`, `tests/governance/test_defect_fix_routing_fold.py` | `efc46535e` |
| 7 | OBPI-0.0.21-04 | EXPLOITED | 2026-04-25T00:34Z, `d7080b945` | `glistening-sauteeing-gizmo.md` | `src/gzkit/cli/parser_maintenance.py` | `d7080b945` |
| 8 | OBPI-0.0.21-09 | EXPLOITED | 2026-04-27T11:59Z, `e6ce59a2d` | `OBPI-0.0.21-09-chores-doctor-command-plan.md` | `src/gzkit/cli/parser_maintenance.py` | `e6ce59a2d` |
| 9 | OBPI-0.0.22-01 | EXPLOITED | 2026-04-29T01:13Z, `bfa3d57b1` | `OBPI-0.0.22-01-schema-frontmatter-field.md` | `src/gzkit/core/models.py` | `bfa3d57b1` |
| 10 | OBPI-0.0.22-03 | EXPLOITED | 2026-04-29T02:01Z, `7576c746e` | `OBPI-0.0.22-03-validate-sensitivity-scope.md` | `src/gzkit/commands/validate_cmd.py` | `7576c746e` |
| 11 | OBPI-0.0.22-04 | EXPLOITED | 2026-04-29T07:04Z, `78cb44508` | `OBPI-0.0.22-04-requires-security-review-attestation.md` | `src/gzkit/commands/obpi_complete.py`, `tests/test_adr_audit_predicates.py`, `tests/test_obpi_complete_cmd.py` | `78cb44508`, `c817a24a2` |
| 12 | OBPI-0.0.22-05 | EXPLOITED | 2026-04-29T07:32Z, `c817a24a2` | `OBPI-0.0.22-05-gate5-walkthrough-arb-slot.md` | `src/gzkit/commands/obpi_complete.py` | `c817a24a2` |
| 13 | OBPI-0.0.24-01 | EXPLOITED | 2026-05-02T14:39Z, `b27f42c92` | `OBPI-0.0.24-01-validator-scope.md` | `src/gzkit/commands/validate_cmd.py` | `b27f42c92` |
| 14 | OBPI-0.0.24-02 | EXPLOITED | 2026-05-02T15:29Z, `b4f552151` | `OBPI-0.0.24-02-wire-into-completion.md` | `src/gzkit/commands/adr_audit.py`, `src/gzkit/commands/obpi_cmd.py`, `src/gzkit/commands/obpi_complete.py`, `tests/commands/test_adr_emit_receipt.py` | `b4f552151` |
| 15 | OBPI-0.0.25-01 | EXPLOITED | 2026-05-02T23:45Z, `70853ae23` | `OBPI-0.0.25-01-implement-coverage-gate.md` | `src/gzkit/commands/obpi_complete.py`, `tests/commands/test_obpi_complete.py` | `6162f61a0` |
| 16 | OBPI-0.0.25-02 | EXPLOITED | 2026-05-03T00:32Z, `f97ac8a26` | `staged-percolating-seahorse.md` | `src/gzkit/events.py` | `f97ac8a26` |
| 17 | OBPI-0.0.26-01 | EXPLOITED | 2026-05-03T10:16Z, `32adb990c` | `OBPI-0.0.26-01-persist-evaluation-events.md` | `src/gzkit/commands/adr_promote.py`, `src/gzkit/events.py`, `src/gzkit/governance/trust_audits/events.py`, `src/gzkit/ledger.py` (+2) | `32adb990c` |
| 18 | OBPI-0.0.27-02 | EXPLOITED | 2026-05-04T09:37Z, `833988852` | `plan-OBPI-0.0.27-02-initial-corpus-authoring.md` | `src/gzkit/commands/validate_cmd.py`, `tests/governance/test_exemplar_corpus.py` | `833988852` |
| 19 | OBPI-0.0.27-03 | EXPLOITED | 2026-05-04T22:38Z, `da8e2714a` | `plan-OBPI-0.0.27-03-measurement-pipeline.md` | `tests/complexity/__init__.py`, `tests/complexity/test_aggregator.py`, `tests/complexity/test_baseline.py` | `da8e2714a` |
| 20 | OBPI-0.0.29-02 | EXPLOITED | 2026-05-06T09:46Z, `d5cdc33d6` | `diagnosis-engine-OBPI-0.0.29-02.md` | `tests/complexity/advisor/test_archetype_rules.py` | `d5cdc33d6` |
| 21 | OBPI-0.0.29-07 | EXPLOITED | 2026-05-08T00:45Z, `4f11bf49b` | `silly-herding-mist.md` | `src/gzkit/commands/validate_cmd.py`, `src/gzkit/governance/trust_audits/__init__.py`, `src/gzkit/governance/trust_audits/intrinsic_attestation.py`, `src/gzkit/ledger_events.py` (+2) | `4f11bf49b` |
| 22 | OBPI-0.0.30-05 | EXPLOITED | 2026-05-10T01:38Z, `13d9b89e8` | `OBPI-0.0.30-05-justify-integration.md` | `tests/skills/test_gz_justify_complexity_amendment.py` | `13d9b89e8` |
| 23 | OBPI-0.0.32-04 | EXPLOITED | 2026-05-12T10:09Z, `8f3ca6dfe` | `OBPI-0.0.32-04-rules-scaffolder-authoring.md` | `tests/commands/test_init.py` | `8f3ca6dfe` |
| 24 | OBPI-0.0.32-05 | EXPLOITED | 2026-05-13T01:30Z, `4e4f8c167` | `OBPI-0.0.32-05-init-update-flag.md` | `tests/commands/test_init_update.py` | `4e4f8c167` |
| 25 | OBPI-0.0.32-07 | EXPLOITED | 2026-05-13T08:42Z, `a93f13ac5` | `OBPI-0.0.32-07-validate-distribution.md` | `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/commands/validate_cmd.py`, `src/gzkit/governance/trust_audits/__init__.py`, `src/gzkit/governance/trust_audits/distribution.py` | `a93f13ac5` |
| 26 | OBPI-0.0.32-10 | EXPLOITED | 2026-05-12T11:15Z, `8bf2aea57` | `OBPI-0.0.32-10-personas-scaffolder-authoring.md` | `tests/commands/test_init.py` | `8bf2aea57` |
| 27 | OBPI-0.0.32-15 | EXPLOITED | 2026-05-14T01:42Z, `45dcdf811` | `OBPI-0.0.32-15-t0-maintenance-surfaces.md` | `tests/test_personas.py`, `tests/test_skills.py`, `tests/test_templates.py` | `45dcdf811`, `80142c0b2` |
| 28 | OBPI-0.0.33-02 | EXPLOITED | 2026-05-15T13:06Z, `ab244b077` | `OBPI-0.0.33-02-surface-weight-validator.md` | `src/gzkit/commands/validate_cmd.py` | `ab244b077` |
| 29 | OBPI-0.0.33-03 | EXPLOITED | 2026-05-15T13:27Z, `bfd891be5` | `OBPI-0.0.33-03-pointer-integrity-validator.md` | `src/gzkit/commands/validate_cmd.py` | `bfd891be5` |
| 30 | OBPI-0.0.33-04 | EXPLOITED | 2026-05-15T23:30Z, `7c5dc526a` | `OBPI-0.0.33-04-scenario-reachability-validator.md` | `src/gzkit/commands/validate_cmd.py` | `7c5dc526a` |
| 31 | OBPI-0.0.33-05 | EXPLOITED | 2026-05-15T23:48Z, `f6af0e6a5` | `OBPI-0.0.33-05-surface-fidelity-composite.md` | `src/gzkit/commands/quality.py`, `src/gzkit/commands/validate_cmd.py`, `src/gzkit/quality.py` | `f6af0e6a5` |
| 32 | OBPI-0.0.34-03 | EXPLOITED | 2026-05-16T14:40Z, `f70d9d4c9` | `obpi-0.0.34-03-reverse-parse-migration.md` | `src/gzkit/cli/main.py` | `f70d9d4c9` |
| 33 | OBPI-0.0.35-03 | EXPLOITED | 2026-05-17T15:36Z, `70853ae23` | `OBPI-0.0.35-03-why-foundation-tier-convention.md` | `tests/commands/test_plan.py` | `c943bc1e5` |
| 34 | OBPI-0.0.35-04 | EXPLOITED | 2026-05-17T17:50Z, `70853ae23` | `kind-invariance-validator-OBPI-0.0.35-04.md` | `src/gzkit/commands/quality.py`, `src/gzkit/governance/trust_audits/__init__.py`, `src/gzkit/governance/trust_audits/kind_invariance.py`, `src/gzkit/quality.py` | `aa91cae35` |
| 35 | OBPI-0.0.36-03 | EXPLOITED | 2026-05-18T00:39Z, `0a8afc844` | `OBPI-0.0.36-03-receipt-shape-validator.md` | `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/commands/validate_cmd.py`, `src/gzkit/governance/trust_audits/__init__.py`, `src/gzkit/governance/trust_audits/receipt_shape.py` (+1) | `0a8afc844` |
| 36 | OBPI-0.0.37-05 | EXPLOITED | 2026-05-20T01:39Z, `a8e195880` | `brief-reconcile-engine-OBPI-0.0.37-05.md` | `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/commands/validate_cmd.py` | `a8e195880` |
| 37 | OBPI-0.0.37-06 | EXPLOITED | 2026-06-04T10:40Z, `329c33ffd` | `OBPI-0.0.37-06-brief-reconcile-cli.md` | `src/gzkit/ledger_events.py` | `664b1c5b0` |
| 38 | OBPI-0.0.37-07 | EXPLOITED | 2026-06-06T06:48Z, `5a2c352fb` | `pipeline-stage1-gate-OBPI-0.0.37-07.md` | `src/gzkit/commands/obpi_cmd.py` | `5a2c352fb` |
| 39 | OBPI-0.0.37-13 | EXPLOITED | 2026-06-01T22:57Z, `70853ae23` | `OBPI-0.0.37-13-reverse-parse-migration.md` | `tests/content/test_migration_layer.py` | `34989b6c8` |
| 40 | OBPI-0.0.37-24 | EXPLOITED | 2026-06-15T02:16Z, `169f89923` | `OBPI-0.0.37-24-advisor-panel-info-retention-qc-loop.md` | `src/gzkit/skills/gz-advisor-qc/SKILL.md` | `169f89923` |
| 41 | OBPI-0.0.54-03 | EXPLOITED | 2026-05-25T21:09Z, `e969a33c1` | `quiet-dazzling-starfish.md` | `src/gzkit/templates/agents.md` | `e969a33c1` |
| 42 | OBPI-0.0.57-01 | EXPLOITED | 2026-05-23T09:02Z, `5a7443ef8` | `cozy-leaping-bonbon.md` | `src/gzkit/governance/trust_audits/taxonomy.py` | `5a7443ef8` |
| 43 | OBPI-0.0.57-02 | EXPLOITED | 2026-05-23T11:32Z, `c3dd7721e` | `OBPI-0.0.57-02-gz-adr-create-nominal-allocator.md` | `tests/test_taxonomy_validator_nominal.py` | `c3dd7721e` |
| 44 | OBPI-0.0.59-05 | EXPLOITED | 2026-05-27T07:01Z, `3119a3b37` | `first-sweep-wave-top-5-offenders-OBPI-0.0.59-05.md` | `tests/governance/test_token_block_discipline.py` | `3119a3b37` |
| 45 | OBPI-0.0.63-02 | EXPLOITED | 2026-05-29T05:45Z, `b9fc4f78e` | `demo-and-arb-receipt-discipline-OBPI-0.0.63-02.md` | `tests/fixtures/ceremony_demos/multiline_demo.md` | `b9fc4f78e` |
| 46 | OBPI-0.0.64-01 | EXPLOITED | 2026-05-28T06:44Z, `c0c0bf7ce` | `OBPI-0.0.64-01-task-id-worklog-schema-additive.md` | `tests/governance/test_task_id_worklog_field.py` | `c0c0bf7ce` |
| 47 | OBPI-0.0.64-02 | EXPLOITED | 2026-05-28T07:15Z, `e9265da90` | `OBPI-0.0.64-02-advances-decorator-and-discovery-convention.md` | `tests/governance/test_advances_decorator.py` | `e9265da90` |
| 48 | OBPI-0.0.64-03 | EXPLOITED | 2026-05-28T08:07Z, `6ef884daa` | `OBPI-0.0.64-03-subdivision-driven-seq-advancement.md` | `src/gzkit/cli/parser_artifacts.py`, `src/gzkit/commands/task.py`, `tests/test_tasks.py` | `6ef884daa` |
| 49 | OBPI-0.0.64-04 | EXPLOITED | 2026-05-28T09:27Z, `ad187cde5` | `velvety-sauteeing-hickey.md` | `src/gzkit/cli/parser_artifacts.py`, `src/gzkit/cli/parser_maintenance.py` | `ad187cde5` |
| 50 | OBPI-0.0.68-02 | EXPLOITED | 2026-06-09T11:26Z, `4b97c2463` | `OBPI-0.0.68-02-session-green-gate-validator.md` | `src/gzkit/governance/trust_audits/__init__.py`, `src/gzkit/governance/trust_audits/session_green_gate.py` | `4b97c2463` |
| 51 | OBPI-0.0.69-01 | EXPLOITED | 2026-06-10T05:16Z, `3d59f60d6` | `OBPI-0.0.69-01-support-channel-plan.md` | `src/gzkit/commands/validate_req_kind.py` | `3d59f60d6` |
| 52 | OBPI-0.0.74-05 | EXPLOITED | 2026-06-25T23:34Z, `bd9c8abb6` | `OBPI-0.0.74-05-mx-exit-hard-gate.md` | `src/gzkit/cli/parser_governance.py` | `bd9c8abb6` |
| 53 | OBPI-0.32.0-02 | EXPLOITED | 2026-07-06T08:53Z, `3fbc3e072` | `OBPI-0.32.0-02-networkx-substrate-and-corpus-projection.md` | `src/gzkit/events.py` | `e1dc58c34` |
| 54 | OBPI-0.34.0-03 | EXPLOITED | 2026-07-29T00:02Z, `be26cef18` | `plan-OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement.md` | `src/gzkit/commands/validate_cmd.py` | `be26cef18` |
| 55 | OBPI-0.35.0-05 | EXPLOITED | 2026-09-09T00:07Z, `417154bd4` | `glittery-kindling-dongarra.md` | `tests/commands/test_content_compose.py`, `tests/content/test_lineage.py` | `2c32d6de8` |
| 56 | OBPI-0.35.0-09 | EXPLOITED | 2026-08-18T01:22Z, `51545dbae` | `OBPI-0.35.0-09-codex-playback-wiring.md` | `tests/governance/test_rendition_floor_coherence.py`, `tests/governance/test_rendition_freshness.py`, `tests/governance/test_surface_delivery_witness.py` | `0f666fa94`, `3d7641718`, `521decc75` |
| 57 | OBPI-0.0.16-04 | EXPLOITED (package `__init__.py` only) | 2026-04-18T09:57Z, `3af3d717c` | `sorted-soaring-cerf.md` | `tests/chores/__init__.py` | `bbb032a0d` |
| 58 | OBPI-0.0.16-05 | EXPLOITED (package `__init__.py` only) | 2026-04-18T02:12Z, `a1ab0fce2` | `sharded-pondering-gem.md` | `src/gzkit/governance/__init__.py` | `a1ab0fce2` |
| 59 | OBPI-0.0.19-04 | EXPLOITED (package `__init__.py` only) | 2026-04-22T09:45Z, `19e95ae52` | `eager-snacking-perlis.md` | `tests/skills/__init__.py` | `19e95ae52` |
| 60 | OBPI-0.0.21-05 | EXPLOITED (package `__init__.py` only) | 2026-04-25T07:06Z, `414061ca0` | `snuggly-watching-waterfall.md` | `src/gzkit/chores/__init__.py` | `414061ca0` |
| 61 | OBPI-0.0.29-01 | EXPLOITED (package `__init__.py` only) | 2026-05-06T09:03Z, `f79163f76` | `advisor-diagnosis-schema-OBPI-0.0.29-01.md` | `tests/complexity/advisor/__init__.py` | `6c2fe10a5` |
| 62 | OBPI-0.0.29-05 | EXPLOITED (package `__init__.py` only) | 2026-05-07T01:38Z, `03385a5b2` | `plan-OBPI-0.0.29-05-auto-chain-hook.md` | `tests/hooks/__init__.py` | `03385a5b2` |
| 63 | OBPI-0.0.30-03 | EXPLOITED (package `__init__.py` only) | 2026-05-09T18:34Z, `31b09332c` | `OBPI-0.0.30-03-authoring-hint-engine.md` | `tests/complexity/authoring/__init__.py` | `31b09332c` |
| 64 | OBPI-0.0.32-06 | EXPLOITED (package `__init__.py` only) | 2026-05-13T08:13Z, `8624adb50` | `OBPI-0.0.32-06-t0-smoke-test.md` | `tests/distribution/__init__.py` | `8624adb50` |
| 65 | OBPI-0.0.34-01 | EXPLOITED (package `__init__.py` only) | 2026-05-16T12:13Z, `a830aaf39` | `OBPI-0.0.34-01-content-model-registry.md` | `src/gzkit/content/__init__.py`, `tests/content/__init__.py` | `a830aaf39` |
| 66 | OBPI-0.0.69-04 | EXPLOITED (package `__init__.py` only) | 2026-06-10T23:09Z, `8dc4f335f` | `retire-ln-surface-OBPI-0.0.69-04.md` | `src/gzkit/governance/trust_audits/__init__.py` | `8dc4f335f` |
| 67 | OBPI-0.0.17-05 | UNDETERMINABLE (allowlist uses `<slug>`-style placeholder) | 2026-04-19T19:24Z, `70853ae23` | `glittery-baking-wall.md` | `src/gzkit/core/models.py`, `tests/scripts/__init__.py`, `tests/scripts/test_backfill_adr_taxonomy.py` | `c88068394` |
| 68 | OBPI-0.0.32-08 | UNDETERMINABLE (allowlist uses `<slug>`-style placeholder) | 2026-05-13T09:37Z, `a1865ac51` | `OBPI-0.0.32-08-mirror-sync.md` | `src/gzkit/sync_surfaces.py`, `tests/test_sync_surfaces.py` | `a1865ac51` |
| 69 | OBPI-0.0.32-09 | UNDETERMINABLE (allowlist uses `<slug>`-style placeholder) | 2026-05-12T07:44Z, `560d76c3e` | `OBPI-0.0.32-09-personas-physical-migration.md` | `src/gzkit/personas/implementer.md`, `src/gzkit/personas/main-session.md`, `src/gzkit/personas/narrator.md`, `src/gzkit/personas/pipeline-orchestrator.md` (+2) | `560d76c3e` |
| 70 | OBPI-0.0.34-02 | UNDETERMINABLE (allowlist uses `<slug>`-style placeholder) | 2026-05-16T13:17Z, `64ac378d1` | `plan-OBPI-0.0.34-02-rendering-pipeline.md` | `src/gzkit/content/templates/bullet/claude.md.j2`, `src/gzkit/content/templates/chore/claude.md.j2`, `src/gzkit/content/templates/handoff/claude.md.j2`, `src/gzkit/content/templates/persona/claude.md.j2` (+3) | `64ac378d1` |
| 71 | OBPI-0.35.0-04 | UNDETERMINABLE (12 h window, untagged commits) | 2026-09-05T06:33Z, `428eb35d0` | `section-ownership-and-ratchet-OBPI-0.35.0-04.md` | `tests/commands/test_content_unown.py` | `18454c906`, `31a448039`, `40fd9994e` |

---

## 2. GHI #849: the arb red witness was inert on landed work, so `--from=verify` gated nothing

**Defect.** `resolve_base_commit` returned HEAD. Once work had landed, HEAD already carried the implementation, so the experiment had no premise. There were two failure shapes before `ca5670e50`:
- **2a** (before `48b61fd58`): a false `none`. This is #839's member of the class.
- **2b** (from `48b61fd58` on): `not-applicable`.

The #849 body names a third hole, which is the one that matters here. When the base is reconstructed (at that time, only by passing `--base <old sha>` by hand), an `error` on the old tree is banked as a weak RED. The fix `ca5670e50` added `base_provenance` and made `error` on a `reconstructed` base void in `red_parity._is_void_witness`. Its comment also rules that a *missing* `base_provenance` reads as `working-tree`: "every witness banked before this field ran against HEAD".

**Window.** `227971a08` (2026-07-09T11:16Z, witness born, GHI #642) to `ca5670e50` (2026-09-06T15:37Z). Sub-window 2a runs 07-09 to 08-22 and sub-window 2b runs 08-22 to 09-06.

**Population.** 203 `red_receipt_emitted` ledger events in the window, covering 22 OBPIs, plus 12 `pipeline_launched` events with `entry: verify` covering 9 OBPIs. Every verify OBPI except 0.35.0-03 also has red receipts.

**Method.**
1. For each receipt, find the commit that introduced its REQ's covering test with `git log -S '@covers("<REQ>")' --reverse -- tests`, the resolver #849 itself validated. Then test with `git merge-base --is-ancestor` whether that commit is in the receipt's `base_commit`.
   - Twenty base shas no longer exist as objects. For those, the receipt timestamp is compared with the test commit's time.
   - If the base predates the test, the work was in flight and the premise held.
   - If the base carries the test, the run was on landed work (or on a WIP commit), and was checked by hand.
2. Explicit `--base` runs show up as 8- or 9-character `base_commit` values (24 events). The default path stores 40 characters (179 events).
3. The effective witness today was read with the live `red_parity._collect` (read-only). `audit_red_parity` currently returns 0 errors.

**Result.** 2 EXPLOITED, 20 EXPOSED-CLEAN, 0 UNDETERMINABLE (22 OBPIs).

| OBPI | `--from=verify` launch in window | Red receipts in window (class / base vs. covering-test commit) | Class | Evidence |
|---|---|---|---|---|
| OBPI-0.34.0-02 | — | assertion (base predates test) ×3, error (base predates test) ×4, none (base carries test) ×5, error (base carries test) ×5 | **EXPLOITED** | Completed 2026-07-20T10:54Z. At 11:01, after completion, 5 × `none` on HEAD `9fff4e7ef` (landed work). At 11:03, 5 × `error` on explicit `--base 1c0f5251` overwrote them (`…5d16d7ee`, `…fa288c1a`, `…18453070`, `…ac7fc763`, `…63f3dfe4`). REQ-01..03 also have an in-flight `assertion` at 01:20, and REQ-04 an in-flight `error` at 08:50. **REQ-0.34.0-02-05** has no witness except the post-completion explicit-base `error`. |
| OBPI-0.35.0-09 | 2026-08-18T01:13Z, 2026-08-21T01:07Z, 2026-08-21T04:44Z | none (base predates test) ×2, error (base predates test) ×15, none (base carries test) ×10, assertion (base carries test) ×4, not-applicable (base carries test) ×1 | **EXPLOITED** | Completed 2026-08-21T08:23Z. Before completion: 10 × `none` on HEAD `558e80996` (#839 false accusations on landed work) and 9 × `error` on explicit `--base 422aecad2` (object not in repo). At 08:34, **after completion**, 6 × `error` on explicit `--base 4f6f5884`. Today, red-parity clears **REQ-0.35.0-09-01/02/04/05/06/10** with those rows (for example `arb-red-REQ-0.35.0-09-01-…ed26c527`), which carry no `base_provenance` and so read as `working-tree` weak RED. REQ-09-03/08/09/11 rest on `assertion` against `94d2efa0`, which lacks the reimplementation `0f666fa94`, so they are conclusive and clean. |
| OBPI-0.0.65-02 | 2026-07-13T01:14Z | error (base predates test) ×14 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.0.65-03 | — | error (base predates test) ×7 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.0.65-04 | 2026-07-14T23:54Z | assertion (base predates test) ×6 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.0.65-05 | — | error (base predates test) ×8 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.0.72-03 | — | error (base predates test) ×9 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.0.72-04 | 2026-07-13T23:24Z | error (base predates test) ×12 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.33.0-02 | — | error (base predates test) ×12 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.33.0-03 | — | error (base predates test) ×6 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.33.0-04 | — | error (base predates test) ×3, assertion (base predates test) ×1 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.33.0-05 | — | error (base predates test) ×6 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.34.0-01 | — | error (base predates test) ×4 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.34.0-03 | — | assertion (base predates test) ×7, error (base predates test) ×1 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.34.0-04 | — | error (base predates test) ×2 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.34.0-05 | — | none (base carries test) ×1, error (base predates test) ×2, assertion (base predates test) ×1 | EXPOSED-CLEAN | The `none` belongs to REQ-0.34.0-05-01, which has no `@covers` string and is not a BEHAVIOR REQ in the current brief, so it has no gate effect. The BEHAVIOR REQs 02–04 were witnessed in flight. |
| OBPI-0.35.0-01 | 2026-08-24T09:22Z | assertion (base predates test) ×1, error (base predates test) ×9 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |
| OBPI-0.35.0-02 | 2026-08-26T01:35Z, 2026-08-26T01:38Z | assertion (base predates test) ×12, none (base predates test) ×1, assertion (base carries test) ×1, error (base carries test) ×7 | EXPOSED-CLEAN | Receipts on 08-25 on HEAD `cbc5c0c13` with a dirty tree. The covering test was committed in the WIP commit `d3fa949dc`, and the production change landed **afterwards** in `665254a5b` (08-26T02:03Z), so it was withheld: in flight, premise held. |
| OBPI-0.35.0-03 | 2026-09-05T19:17Z | none | EXPOSED-CLEAN | Verify launch with no red receipts. The brief has **no BEHAVIOR REQs** (`_behavior_reqs` is empty), so it is outside the witness by construction. |
| OBPI-0.35.0-04 | 2026-09-05T17:58Z | error (base predates test) ×7, error (base carries test) ×2, assertion (base carries test) ×1 | EXPOSED-CLEAN | Receipts on 09-02/03 on HEAD `600f7fd54` / `e962b01aa` with a dirty tree. Artifacts `…510400bc` and `…d29ecb5b` show `AssertionError` against missing unown behaviour, and rework landed afterwards (`18454c906`, `40fd9994e`, `d2280608f`). In flight. |
| OBPI-0.35.0-08 | — | not-applicable (base predates test) ×5, assertion (base predates test) ×2 | EXPOSED-CLEAN | 5 × `not-applicable`: the witness did not run. **No completion** exists, and the OBPI is not in red-parity scope, so no completion went through. |
| OBPI-0.44.0-01 | 2026-07-10T09:15Z | error (base predates test) ×4 | EXPOSED-CLEAN | All receipts on the default HEAD base and emitted before the covering test was committed, so the work was in flight and the premise held. Some base shas are no longer in the repo; the premise is inferred from timestamps. |

**What makes the two rows EXPLOITED.** In both, the gate went green because of an `error` produced on a hand-reconstructed base, which is exactly the fail-open hole #849 named. The rows are still counted as RED today, because they predate `base_provenance` and the fix's backfill rule reads absence as `working-tree`. **That rule is false for these 20 events** (`--base` 1c0f5251 ×5, 422aecad2 ×9, 4f6f5884 ×6). Under the post-fix semantics they would be void, and red-parity would report missing witnesses for **11 BEHAVIOR REQs**:
- REQ-0.35.0-09-01, -02, -04, -05, -06, -10
- REQ-0.34.0-02-01..05 (after its in-flight rows, only REQ-02-05 stays uncovered in substance)

Substance may still be fine: the post-fix reconstructed re-run of REQ-0.35.0-09-01 (`…4cd30f33`, 09-06) failed with `TypeError: sync_agents_md() got an unexpected keyword argument 'consumer'`, which is the missing implementation. That verdict is still classed inconclusive by design. What was never witnessed conclusively is the claim.

**Defects found while auditing (not repaired; the operator routes them):**
- **D1.** `red_parity._is_void_witness` reads a missing `base_provenance` as `working-tree`. The 24 short-sha explicit-`--base` events contradict that assumption: 20 of them are `error` and void in substance.
- **D2.** `red_parity.audit_red_parity`'s comment says *"A `none` RED is a finding that no other evidence erases."* But `_collect` keeps the **last** non-void event per REQ (`witnesses[req_id] = event`), so a later `error` or `assertion` overwrites a `none`. It happened 15 times: 0.34.0-02 ×5 and 0.35.0-09 ×10. In those cases the `none` rows were themselves #839 false accusations, so the overwrite was right in substance. The invariant as stated is still not held.
- **D3 (local only).** `artifacts/receipts/arb-red-REQ-0.35.0-09-01-…415a9202.json` is the known-false `none` that #849's close comment says was dropped from the ledger. It and `…5ad6c8aa.json` still sit in the working copy with no ledger row. `artifacts/` is gitignored, and no arb-red receipt is tracked, so they are not in the repo.

---

## 3. GHI #927: direct-fix guards were outside every falsifiability gate

**Nature.** This was a coverage gap, not a false pass. No gate claimed to witness direct fixes. `gz arb red` required `--req`, and `red_parity._brief_is_in_scope` needs a heavy-lane terminal brief. The fix `79ae773f2` (2026-09-29T09:49Z) added `gz arb red --commit`. Its close comment says, under "Not claimed", that commit mode wrote no receipt or ledger event, and that no gate runs it automatically: it is wielded by `ghi-close` step 7c. Receipts arrived later with #1152 (`a76bc6a48`, `f8a2cb302`, 2026-09-30T03:02–03:09Z).

**Window.** `227971a08` (2026-07-09, when a falsifiability gate first existed for the REQ path) to `79ae773f2` (2026-09-29). Structurally the gap goes back to project start, since before 07-09 no path had a witness.

**Population (measured):**
- `git log --since=2026-07-09T06:16:11-05:00 --until=2026-09-29T04:49:09-05:00 --grep='^fix(' -- src/gzkit` gives **599** direct-fix commits touching `src/gzkit`.
- **108** of those touch no `tests/` file.
- 719 `fix(` commits in the window in total.

**Receipts.** The ledger holds 9 `red_commit_receipt_emitted` events, each matched by an `artifacts/receipts/arb-red-commit-*.json` file (local only; `artifacts/` is gitignored). **None of the 9 is for a commit inside the #927 window.** `git merge-base --is-ancestor <c> 79ae773f2` is false for every witnessed commit.

| Witnessed commit | Commit time | Receipt(s) | Verdict (hunks) | Status |
|---|---|---|---|---|
| `92f64debc` fix(justify-binding) (GHI #1150) | 2026-09-29T23:02Z | `…7f7213a1` | undriven (1 survived, 6 killed, 10 inconclusive, 2 invalid) | Driven by `57a94bd58` (validate_cmd.py:618-619 event-type filter) |
| `73aaab093` fix(commit-witness) | 2026-09-30T01:07Z | `…e87323a0` (inconclusive), `…fdeb89df` | undriven (4 survived, 9 killed, 2 inconclusive) | `57a94bd58` says it drives **two** guards in this commit; the receipt lists **4** survived hunks. Whether all 4 are now driven was not verified (that needs a re-sweep, forbidden here) |
| `a76bc6a48` / `f8a2cb302` fix(arb-red) (GHI #1152) | 2026-09-30T03:02Z / 03:09Z | `…93451943`, `…a7f5234e` / `…a66314e0` | undriven (7 / 6 survived) | No later commit subject in `git log 9f9403b61..HEAD` claims to drive these |
| `c124fd5ee` / `89da191e1` / `9f9403b61` fix(commit-witness) (GHI #1153) | 2026-09-30T03:34–03:46Z | `…81171dac` / `…b79aa9ef` / `…5fca105b` | undriven (4 / 2 / 2 survived) | No later commit subject claims to drive these |

**Classification of the #927 window population:**
- **599 commits UNDETERMINABLE.** No commit-mode witness has ever run on any of them. Running one is the missing evidence: `gz arb red --commit <sha>`, excluded by this audit's rules.
- **0 EXPLOITED.** No gate claimed coverage, so no gate reported green falsely. The known instance `3c255459` (the missing test for `_forbidden_mirror_names`) was closed by `41646443` before the fix.
- **0 EXPOSED-CLEAN.**

The undriven receipts above all come from post-fix commits in the #1152 no-receipt window. They show that the direct-fix route kept producing undriven guards up to the witness's own commits. All five of those commits carry survivors, and the covering tests have been confirmed only for `92f64debc` and part of `73aaab093`.

---

## What the release notes can truthfully say

- **Plan-audit containment (#1057).**
  - From 2026-04-01 (`d773bcfb7`) to 2026-09-19 (`cc5ed5bfa`), `gz plan audit` returned PASS on every plan regardless of scope.
  - Replaying the 401 committed PASS receipts from that period against the fixed predicate: in **at least 56 OBPIs** the plan named a `src/` or `tests/` file outside its brief's Allowed Paths, the audit passed it, and the file was then modified. Another 10 touched only a package `__init__.py`, and 15 cannot be decided (placeholder allowlists, missing plan files, attribution).
  - Many of these fixed a stale brief allowlist rather than drifting from intent. None of them triggered the brief amendment the gate existed to force.
- **Falsifiability witness (#849).**
  - Between 2026-07-09 and 2026-09-06, the RED witness could not test landed work. Two completed heavy-lane OBPIs, **OBPI-0.35.0-09** and **OBPI-0.34.0-02**, were cleared by `error` verdicts from hand-reconstructed `--base` runs made after completion, which is the fail-open case #849 named.
  - Those rows still satisfy `gz validate --red-parity` today, because pre-fix rows are read as `working-tree`. 11 BEHAVIOR REQs therefore have no conclusive falsifiability witness.
  - The other 20 OBPIs witnessed in that window ran in flight, with the premise intact.
- **Direct-fix route (#927).**
  - Before 2026-09-29, no falsifiability witness existed for direct fixes: 599 `fix(` commits touched `src/gzkit` in the 2026-07-09→09-29 window, 108 of them with no test change. None has been witnessed since, so how many carried undriven guards is **unknown, not zero**.
  - The first witnessed commits (after the fix, 09-29/30) include seven with undriven guards. Tests for those in `73aaab093` and `92f64debc` were added in `57a94bd58`.
