# Memory review — 2026-10-10 (maintenance visit A)

A dated record. Steps 1–2 of CHORE.md ran (scan, classify). Step 3 is operator-only-repair:
nothing below was migrated or removed. The witness `check_memory_drift.py` read 52 memories,
none newer than the last pass (clean). Every file dates from 2026-03-15 to 2026-04-05; none
has been written since, so the shadow-persistence failure the chore watches for is absent.
What the scan found instead is **decay**: the memories are six months old and several now
contradict canon ratified after they were written.

## Population

| Type | Count | Disposition per § Policy |
|---|---|---|
| `feedback` | 41 | review — migrate if it encodes process, remove if stale |
| `project` | 9 | review — remove if outdated or encoded in code (one file, `project_schema_driven_cms.md`, has no frontmatter) |
| `reference` | 1 | keep |
| index `MEMORY.md` | 1 | rewrite after any removal |

## Candidates, by what canon now says

**A. Contradict canon — recommend removal (they would steer a session wrong if read).**

| Memory | What it says | What canon says |
|---|---|---|
| `feedback_attestor_name.md` | attestor `jeff`, display name `Jeffry` | operator identity is `g0` in every attestor/author field (AGENTS.md § Execution Rules, operator directive 2026-06-10) |
| `feedback_audit_attestation.md` | Gate 5 audit attestation is agent-driven (`agent:claude`) | Gate 5 is universal and human-only (ADR-0.0.36; AGENTS.md § Gate Covenant) |
| `feedback_parent_lane_attestation.md` | lite OBPIs under heavy ADRs need human attestation because the parent lane sets the floor | superseded in the other direction: every OBPI needs it, lane is irrelevant (ADR-0.0.36) |
| `feedback_rules_are_guardrails.md` | do not recommend pruning `.claude/rules/` | the `instructions-files-diet` chore exists to trim them under operator ruling (3.4.0); `.claude/rules/` is a generated mirror, not the surface |
| `feedback_h3_evidence_format.md`, `feedback_h3_evidence_sections.md` | evidence sections must be H3 — hook enforces | duplicated pair; the hook and `gz validate --brief-reconcile` are the witness; if the rule still holds it lives in the brief template, not memory |
| `project_claude_primary.md`, `project_harness_priority.md` | Claude-primary; five vendor-alignment pool ADRs | root `AGENTS.md` is the sole AgentContract for every harness (Operator Doctrine); `vendor-alignment-copilot` is Superseded in the pool |
| `project_superbook_removed.md`, `feedback_superpowers_disabled.md` | superbook/superpowers removed 2026-03-23 | encoded in the repository's absence of them; a six-month-old removal note steers nothing |
| `project_ghi35_triage.md`, `project_pool_health.md` | triage results of 2026-03/04 | superseded by `ADR-pool.pool-management` and the `pool-triage` chore |

**B. Encode process already in a governed source — recommend removal after confirming the source carries it** (the memory is a stale copy; the governed source is the edit target per § Migration targets).

`feedback_auto_invoke_pipeline`, `feedback_canon_first_editing`, `feedback_canon_in_gzkit`,
`feedback_ceremony_burden_of_proof`, `feedback_ceremony_is_design`,
`feedback_ceremony_stop_and_wait`, `feedback_closeout_unified`, `feedback_descriptive_commits`,
`feedback_evaluate_before_implementing`, `feedback_evidence_before_status`,
`feedback_fix_the_source`, `feedback_instant_skill_execution`, `feedback_just_run_skills`,
`feedback_ledger_is_truth`, `feedback_no_auto_implement`, `feedback_no_double_print`,
`feedback_no_env_config`, `feedback_no_pythonutf8_macos`, `feedback_no_raw_json`,
`feedback_no_skip_hooks`, `feedback_no_vibe_lifecycle`, `feedback_obpi_full_slug`,
`feedback_one_question_at_a_time`, `feedback_operator_value_docs`,
`feedback_plan_before_pipeline`, `feedback_review_before_next_task`,
`feedback_run_commands_cli_mode`, `feedback_silent_failures`, `feedback_single_sync`,
`feedback_skills_override_memories`, `feedback_specify_blank_templates`,
`feedback_specify_model_authoring`, `feedback_use_adr_report`, `feedback_write_for_multi_import`.

Each names a rule that `AGENTS.md`, a `.gzkit/rules/*.md` file, a skill, or a hook now carries
(for example: `--no-verify` is never used; `PYTHONUTF8=1` is never prefixed and
`gz validate --utf8-prefix` witnesses it; only the operator initiates OBPI work; one git-sync
in Stage 5; imports land with their usage because the ruff hook strips unused imports).
Recommended check before removal: for each, grep the named rule in canon; any rule NOT found is
a migration candidate for `gz content remember` or the owning rule file, and is the one case
where the memory still carries something canon lost.

**C. Keep.** `reference_subagent_capabilities.md` (reference), `project_four_tier_hierarchy.md`
and `project_xml_injection_pattern.md` (architecture notes that are still true), and
`project_persona_control_surface.md` (true; personas are a control surface under
`.gzkit/personas/`). `project_schema_driven_cms.md` needs frontmatter before it can be
classified; its content (gzkit as a headless governance CMS) is still true.

## Recommended operator ruling

Rule per band: remove band A now (nine files, every one actively wrong); remove band B after
the grep confirms canon carries each rule (34 files); keep band C (five files). Then rewrite
`MEMORY.md` to index what remains. The removals are on the operator's machine, outside the
repository; the proof of the pass is this record and the next run of `check_memory_drift.py`.
