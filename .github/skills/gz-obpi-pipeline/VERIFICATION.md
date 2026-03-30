# REQ-Level Verification Dispatch (Stage 3 Phase 2)

This file contains the detailed REQ-level verification dispatch protocol for Stage 3.
Referenced by SKILL.md Stage 3. Do not read unless Stage 3 Phase 2 is active.

---

## REQ-Level Verification Dispatch

**Check the `--no-subagents` flag first.** If set, skip to the Inline Verification Fallback below.

After baseline checks pass, dispatch parallel verification subagents for the brief's requirements:

1. **Extract verification scopes** from the brief using `prepare_stage3_verification(brief_content, test_paths)`. Each numbered `REQUIREMENT:` line becomes one `VerificationScope`.

2. **Analyze path overlap** — the `VerificationPlan` partitions requirements into independent groups:
   - Requirements with **non-overlapping test paths** are placed in **separate groups** (can run in parallel).
   - Requirements with **overlapping test paths** are merged into the **same group** (must run sequentially within a single subagent).
   - **NEVER dispatch parallel verification for overlapping file paths** — data corruption risk.

3. **Dispatch strategy selection:**
   - `parallel` — all groups are singletons (fully parallel dispatch)
   - `mixed` — some groups have multiple REQs (parallel between groups, sequential within)
   - `sequential` — single group or no test paths (fall back to inline)

4. **For each independent group** (concurrent dispatch using `run_in_background: true`):

   a. **Compose verification prompt** via `compose_verification_prompt(group_scopes, group_label=...)`. Each subagent receives:
      - Requirement text for each REQ in the group
      - Test file paths to run
      - Expected pass criteria
      - Current branch state (included in prompt context)

   b. **Dispatch verification subagent:**
      ```
      Agent tool call:
        subagent_type: "general-purpose"
        isolation: "worktree"
        run_in_background: true
        prompt: <verification prompt from step a>
        description: "Verify REQ group N"
      ```

   c. Worktree cleanup is **automatic** — the Agent tool cleans up the worktree when the subagent completes or fails. No orphaned worktrees.

5. **Wait for all verification subagents to complete.** All subagents MUST finish before Stage 3 advances.

6. **Parse and aggregate results:**
   - Parse each subagent output via `parse_verification_results(agent_output)`.
   - Aggregate via `aggregate_verification_results(results, expected_req_indices)`.
   - Create dispatch records via `create_verification_dispatch_records(plan, results)` and persist in the pipeline marker.

7. **Record timing metrics** via `compute_verification_timing(start_ns, end_ns, strategy, group_count)`. Always record wall-clock time savings from parallel vs sequential execution.

8. **Handle aggregate results:**
   - All REQs pass → advance to Stage 4.
   - Any REQ fails → attempt fix and re-verify once. If still failing, create handoff, release lock, and stop.

## Inline Verification Fallback

When `--no-subagents` is set, or when the verification plan strategy is `sequential`:

1. Run each brief-specific verification command sequentially inline.
2. Run any commands from the brief's Verification section.
3. Record all outputs as evidence.

No subagent dispatch, no worktree isolation, no parallel execution.

**Abort if:** Any verification fails. Attempt fix, re-verify once. If still failing, create handoff, release lock, and stop.
