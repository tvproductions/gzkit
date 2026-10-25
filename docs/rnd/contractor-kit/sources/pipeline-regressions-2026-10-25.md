# OBPI pipeline regressions, 2026-08-25 to 2026-10-25

**Dated record, 2026-10-25.** This is a source note for the contractor-kit R&D run. It describes what happened to the OBPI pipeline (`gz obpi pipeline`, skill `gz-obpi-pipeline`, `src/gzkit/pipeline_*.py`, `src/gzkit/commands/pipeline.py`) over the last 60 days. Its purpose is to decide whether a drydock contractor runtime can reuse the pipeline's parts. Nothing in the repository was changed to produce it. Wherever a statement is inferred rather than quoted, it is marked **(inferred)**.

## Method

| Source | Found | Read |
|---|---|---|
| `.gzkit/insights/agent-insights.jsonl` entries dated on or after 2026-08-25 | 748 | The 121 whose `scope` or `summary` names pipeline, Stage 2, reviewer, implementer, dispatch, procedure, marker or Step 4b were read at summary level. 19 of them were read in full, every field. |
| `gh issue list --state all --search "pipeline" --limit 100` | 100 returned (the limit was hit, so the search may be truncated); 86 created in the window | 57 bodies and comment threads read in full (all the open pipeline-core issues and the closed regression-shaped ones). For 26 closed issues the closing comment was read separately. The rest are release, docs or complexity issues and were judged off-topic by title only. |
| `git log --since=2026-08-25 -- src/gzkit/pipeline_*.py src/gzkit/commands/pipeline.py .gzkit/skills/gz-obpi-pipeline/` | 84 commits | Messages of all 84 read. Diffs or full messages read for `757ddea7e`, `fbd1c376c`, `1cd6cf841`, `ac3b0005e`, `d47de23c8`, `90eea0ad2`, `0ccde2c97`, `1c8b15fcc` and `58e4e46db`. |
| `docs/governance/obpi-pipeline-control-rationale.md`, `data/obpi_pipeline_control_inventory.json` | 2 files | The header, the structure and the git history of both. The rationale file is a record of rationale that was moved, not a list of controls removed or demoted. One inventory row has been reworded since the attestation (S2-080, below). |
| `docs/governance/harbor-pilotage-candidate-2026-10-15.md` § What is suspended and § Punch list, plus `docs/governance/harbor-ro8-in-flight-work.md` | 2 files | The sections in full. |
| `.gzkit/ledger.jsonl` | n/a | A read-only scan for the last pipeline events, the ADR-0.35.0 OBPI states and the current `.gzkit/mx.json`. |

**Ledger fact that bounds every "repaired" claim below.** The last `pipeline_launched` is OBPI-0.35.0-15 on 2026-10-11T18:06Z. The last `obpi_receipt_emitted` is the same OBPI on 2026-10-13T08:39Z. No pipeline event of any kind has been recorded since 2026-10-14. The repairs landed after that date, including procedure pinning and the skill cutover, have never run on a real OBPI. Safe mode is open now: `.gzkit/mx.json` reads `"mode": "safe"`, opened 2026-10-20T22:59Z.

## Part A — Deliberate switch-offs (safe mode, operator-ruled)

These are not regressions. Each one was ruled by the operator, and the contract records how it is restored. They do change how the pipeline behaves today.

### A1. The pipeline gate (post-Stage-2 production-write fence hook) lowered to advisory

- **When:** 2026-10-17, `1cd6cf841` "feat(mx): safe mode lowers every guard outside the floor to advisory (RO-0, R6)".
- **Evidence:** the commit body: *"src/gzkit/hooks/scripts/routing.py: the pipeline-gate template consults the checkpoint and exits 0 with the demote notice under an open marker; it had blocked this act's own test edit, knowing nothing of the marker."* `src/gzkit/mx/checkpoint.py`: *"hangar_demotes is true under either mode."* The insight dated 2026-10-17T11:27 gives the operator's words: *"DO YOU EVEN UNDERSTAND WHAT SAFE MODE IS!?!?!?"* and *"the pipeline gate must honor the marker like every checkpoint consumer"*. The live `.claude/hooks/pipeline-gate.py:134` reads `_checkpoint.is_advisory("pipeline-gate", project_root)`.
- **Not lowered:** the commit-side arm of the same fence, `post-authoring-src-commits` in `src/gzkit/hooks/guards.py` `_GUARD_META`, is pinned `CRITICAL`. It still refuses a commit that carries production code past Stage 2 while a pipeline marker exists.
- **Status:** switched off while the marker is open. The harbor contract § What is suspended says *"the hard-gate exit re-runs every guard at full strength"*.
- **Touches the named parts?** Yes. This is the fence that Stage 2 and the implementer persona rely on.

### A2. OBPI initiation, completion and brief ceremony suspended

- **When:** 2026-10-15, `ac3b0005e` (safe mode created, GHI #1244). Then R4 on 2026-10-17.
- **Evidence:** harbor contract § What is suspended: *"Brief ceremony. No OBPI is initiated or completed under safe mode"*. The R4 ruling is quoted in the RO-8 specification: *"R4 ADR-0.35.0 frozen, no further OBPI completions"*.
- **Status:** suspended. This is why the ledger shows no pipeline run since 2026-10-13.
- **Touches the named parts?** Indirectly. No part of the pipeline has been exercised since.

### A3. Verifier pipe gate and the pre-commit and pre-push alarm hooks switched off

- **When:** 2026-10-25 03:04, `757ddea7e` "feat(mx): safe mode switches the alarms off until gz mx exit".
- **Evidence:** operator, verbatim, in the commit body: *"i don't want any long check at all - this is a remodel, things are going to be broken, disarray, and messy. it is time to leave things partially broken until the reconfiguration is complete, then we adjust tests and turn the "security alarms" back on. this is all backwards."* Also from the body: *"while .gzkit/mx.json carries mode: safe (and is not exiting) the pre-commit and pre-push alarm hooks and the verifier pipe gate do not run."*
  - The diff adds `if alarms_off(): sys.exit(0)` to `.claude/hooks/verifier-pipe-gate.py`.
  - It wraps these hooks in `python -m gzkit.mx.alarms`: complexity-ceiling, surface-fidelity-cheap, validator-reachability-ratchet, ledger-vocabulary-inertness, the pre-push `gz check --reuse-verified`, and the pre-commit `unittest-parallel`.
  - The verifier pipe gate (`src/gzkit/verifier_pipe_gate.py`, GHI #589) is the control against *"a confident false green"*: a verifier piped through a filter so that the shell reports the filter's exit code.
- **Status:** switched off. Punch list RO-0, `open` **reconnected**: *"the six pre-commit and pre-push alarm hooks and the verifier pipe gate, switched off through `gzkit.mx.alarms` (`757ddea7e`), run at full strength at exit"*. A second line: *"`open` **restored** — the commit witness (`gz arb red --commit`) as a per-act record"*.
- **Touches the named parts?** The verifier pipe gate guards the Stage 3 verification evidence and the Stage 4 packet evidence. A contractor runtime that reuses the reviewer protocol inherits that exposure while safe mode is open **(inferred)**.

### A4. Partial walk-back of A3 five minutes later

- **When:** 2026-10-25 03:09, `fbd1c376c` "fix(mx): the pytest ban, ruff and ty are never turned off".
- **Evidence:** the operator, verbatim: *"never, ever, ever turn this off: "the pytest ban""* and *"ruff and ty are reasonable too"*. From the body: *"757ddea7e wrapped the forbid-pytest pre-commit hook in the safe-mode alarm switch. That hook runs the whole guards sweep, so the ledger and Gate-5 attestation guards the contract never suspends were switched off with it. The hook is unwrapped."*
- **Status:** ruff, ty and the guards sweep are restored. This window also exposed an unintended regression, recorded as B1.

## Part B — Unintended regressions and defects

The list runs roughly newest first. "Regression" means something that used to hold and stopped holding. Latent defects that the window *discovered* are kept apart in Part C.

### B1. forbid-pytest demoted to advisory for the whole MX session (unintended side effect of A1)

- **When:** from 2026-10-17 (`1cd6cf841`, every guard at `ERROR` now demotes under either mode) until 2026-10-25 (`fbd1c376c`). For about five minutes on 2026-10-25 (`757ddea7e` to `fbd1c376c`), the ledger and Gate-5 guards were also off. The contract says those two are never suspended.
- **Evidence:** `fbd1c376c`: *"forbid-pytest was registered at ERROR in guards._GUARD_META, so it demoted to advisory under any open marker and has only warned for the whole MX session. It is now pinned CRITICAL by LEVEL"*. Also: *"The restored sweep caught a pyproject.toml comment (e4b46bcb2) naming the banned framework while the ban was demoted"*.
- **Status:** repaired by `fbd1c376c`.
- **Touches the named parts?** No. This is the safe-mode guard classification. The lesson for a contractor runtime is that a guard's level decides whether safe mode demotes it, so every guard a contractor relies on needs an explicit level **(inferred)**.

### B2. The procedure-pinned pipeline (OBPI-0.35.0-17 and -20) landed without Gate 5 and has never run

- **When:** 2026-10-15, `fbe298c26` (*"each stage entry serves its procedure as a pinned file"*) and `d47de23c8` (skill body cut over). On 2026-10-24, `90eea0ad2` reworded control S2-080.
- **Evidence:**
  - `d47de23c8`: *"Nothing was compressed. This is a change of delivery, not a shortening ... every control in the attested inventory is delivered, verbatim"*. Measured: *"skill file 125,923 B body -> 11,445 B file"*.
  - The control inventory was attested in the insight dated 2026-10-15T09:53: *"attest the inventory, keep going with the load cuts"*.
  - The ledger shows both OBPI-0.35.0-17 and OBPI-0.35.0-20 with only `obpi_parked` (2026-07-22) and no receipt.
  - The RO-8 specification: *"Briefs 17 and 20: the work landed in pilot acts ... the ledger still shows both pending"*. Ruling 1, 2026-10-25: *"briefs 17 and 20, whose work landed in pilot acts, are not attested as OBPIs; their obligations, S2-080 included for 20, are carried to the outcome's Gate 5."*
  - `90eea0ad2` changed a delivered control after the attestation (`uv run ruff check . --fix` became `uv run gz lint --fix`). It recorded that through the inventory's `reworded` field, and the renderer's constant *"Nothing is reworded"* was retired.
- **Status:** open. The code is live. Gate 5 is carried to the catalog outcome, and no real run has happened since the cutover (see the ledger fact above).
- **Touches the named parts?** **Yes, directly: this is the procedure pinning in `pipeline_procedure.py`.** It is unattested as OBPI work and unexercised in production.

### B3. Stage 2 runaway repair loop: the fix-cycle cap has no production caller (GHI #1200, open)

- **When:** observed 2026-10-11 to 2026-10-13 on OBPI-0.35.0-15. The issue was filed 2026-10-13.
- **Evidence:** the operator, verbatim: *"this runaway behavior is very unacceptable"*. From the body:
  - *"`src/gzkit/pipeline_dispatch.py:415` declares `MAX_REVIEW_FIX_CYCLES = 2`, and `handle_review_cycle` (line 772) returns "blocked" ... The two `src` hits are a re-export."*
  - *"Seven blocks and seven unblocks in 31 hours, on one requirement of one task. Six of the seven recorded rulings name option A; four carry the agent's "(Recommended)" mark"*
  - *"120 `acceptance_recorded`, 74 `stage2_dispatch_recorded`"*
  - *"Nothing compares one round's root with the last."*
- **Introduced by:** *"multiple ... When the function lost, or whether it ever had, a production caller is `unknown`."* So it is unknown whether this regressed or never worked.
- **Status:** open. The counting half is assigned to OBPI-0.35.0-18 (Draft). RO-8 now withdraws that brief into the catalog.
- **Touches the named parts?** **Yes, the reviewer protocol and `pipeline_dispatch.py`.** The loop bound exists only as prose that the orchestrator applies to itself.

### B4. Stage 4 4a/4b loop, the regression the operator named (GHI #1028, open)

- **When:** reported 2026-09-18.
- **Evidence:** the operator, verbatim: *"lately, models become VERY ensnared on 4a and 4b and get impossibly looped in race/contention conditions between them. This wasn't the case 2 months ago."*
  - The issue body measured the whole skill at *"69,707 B"* on 2026-07-15 against *"122,302 B"* on 2026-09-18, and the Stage 4 section at *"13,851 B"* against *"44,437 B (3.2x)"*.
  - Root mechanism, from the comment of 2026-09-19: *"currency is **whole-tree, not per-obligation**. A one-line repair for one 4b finding ... moves the digest and stales every proof and every imported spec, quality and adversarial review for the OBPI at once."*
- **Repairs:** `6b440453e` (2026-09-18): the pass condition is stated once, a frozen subject, *"N=2"* rounds, and an exit through `gz obpi block`. The re-derivation of 2026-09-22 found four of the five text findings repaired. Finding 4 still holds (*"`gz obpi block` appears **0 times** in the Stage 4 span"*), and *"There are two sections called "Stage 4"."*
  - Production comparison of 2026-10-07: *"Proof records did not fall ... It does not show the loop gone ... It does show the loop now stops and asks."*
  - The digest half (#1029) was *"closed 2026-09-19 as won't-fix for now on the operator's ruling "A""*.
- **Status:** open. Partly repaired: the loop now stops and asks the operator. The invalidation cause stands by ruling.
- **Touches the named parts?** **Yes, the reviewer protocol (Step 4b and the acceptance import).** Any reuse inherits whole-tree proof currency.

### B5. Regressions introduced by OBPI-0.35.0-15 (pipeline run position), all open

OBPI-0.35.0-15 was completed 2026-10-13 after nine fix cycles. The RO-8 specification flags it: *"completion receipt was captured from a dirty worktree"*.

- **#1206, the fence re-entry bypasses the launcher's gates.** This weakens a control that held before. From the body: *"a run at `verify` or `ceremony` whose OBPI is blocked on the operator, or whose reconcile receipt has drifted, or whose plan-audit receipt reads FAIL, returns to `implement` with one `gz task start`, and the fence then admits production writes. Before OBPI-0.35.0-15 the only runtime route from a post-authoring stage back to `implement` was a relaunch through `obpi_pipeline_cmd`, which runs those three gates."* Introduced by: *"commits `4091cfa1b` onward"*.
- **#1208, a marker-cache fault drops a ledger row.** *"a fault in a cache (Layer 3) prevents a ledger row (Layer 2) from being written."* Introduced by OBPI-0.35.0-15, *"commits `4091cfa1b` onward"*.
- **#1203, a recorded position has no reader without a marker.** Introduced by `4091cfa1b` to `ba7e20341`.
- **#1194, `fold_renames` is applied twice.** *"The double application was introduced by commit d68b7073c."*
- **#1209, nine docstrings and doc sentences are false of the code.** *"items 1 to 3 date from its fix cycles 2 to 6"*.
- **#1205, stale-marker detection crashes on a zoneless `updated_at`.** The crash *"predates OBPI-0.35.0-15"*, but that OBPI made *"the second copy of the rule"*, and the two copies now disagree.
- **#1204:** the brief's requirements exceed what was accepted. The issue was read only at the "Introduced by" line.
- **Touches the named parts?** #1206 and #1208 touch the marker, dispatch and fence surfaces that a contractor runtime would reuse to track progress. #1205 sits in `pipeline_markers.py`, a registered security surface.

### B6. Stage-4 narrator and Step-4b verdict gate left uncalled by a repair (GHI #1163, repaired by removal)

- **When:** introduced 2026-09-08 by `8436bfd8f` (GHI #985). Repaired 2026-10-03 by `0ccde2c97`.
- **Evidence:** the insight dated 2026-10-02T09:10: *"GHI #985 (8436bfd8f, 2026-09-08) moved the Step-4b refusal to acceptance_store and left the old verdict gate unwired: _enforce_adversarial_validation has no production caller ... gz obpi complete accepts and ignores five --adversary-* flags"*. GHI #1163: *"Introduced by: commit 8436bfd8f (GHI #985)"*.
- **Status:** repaired. The dead gate and its flags were removed (operator: *"GHI, remove outright (Recommended)"*). The live check is the acceptance reducer.
- **Touches the named parts?** Yes, the reviewer protocol. For about 25 days, three prose surfaces named an uncalled function as the Step-4b enforcement site.

### B7. Step 4b purpose authored inverted ("refute-not-confirm")

- **When:** found 2026-09-03 and 2026-09-04. Authored 2026-06-24.
- **Evidence:** the insight dated 2026-09-04T01:31: *"Step 4b's documented purpose was inverted: the skill said 'refute-not-confirm' ... so six rounds were prompted to refute and the gate had no pass output."* `1c8b15fcc` corrected its own predecessor's account: *"it was never turned around because it was authored wrong ... d1848af1 (2026-06-24) ... introduced the whole design including "prompted to refute""*. The insight dated 2026-09-04T11:46 adds *"13/13 refutation completions recorded no adversary_resolution"*.
- **Status:** repaired across 2026-09-03 to 2026-09-05 (`6da6cf1eb`, `1c8b15fcc`, `9abc7a1d4`, `d7ba081b3`, `edbab5ae4`, `ac57c15a8`, and others). Strictly this is not a regression. It was authored wrong and found in this window.
- **Touches the named parts?** Yes, the reviewer protocol framing.

### B8. Skill-body accretion and context load (repaired by B2's delivery change, never exercised)

- **Evidence:**
  - The insight dated 2026-10-11T23:16 quotes the operator, verbatim: *"we fill up way too much context window during a pipeline run now"*. It measured *"the pipeline skill loads as one 125,923-byte SKILL.md"*, *"implementers hit their 25-turn limit 7 times"*, *"3 were refused by the acceptance importer over a restated finding identifier"*, and review prompts of *"146,389 and 133,205 bytes"*.
  - The insight dated 2026-10-03T12:00: *"154M cached tokens across 557 API calls, 77 percent of it in one orchestrator session whose context grew from 55K to 744K tokens"*.
  - The operator, insight dated 2026-10-03T11:31: *"if it is going to take 1m tokens for ach obpi, then they might be too broadly scoped. we get into endless loops with things like thos now."*
- **Repairs:** #1096 (`7a41f0390`, review prompts embed the working set, not the proof history) and #1095 (`7b2427c45`, one reply envelope), both 2026-09-25. B2 (`d47de23c8`) handles the skill size.
- **Status:** partly repaired. The finding-identity import refusal (insights dated 2026-10-11T21:10 and T22:54) was not seen fixed in what was read.
- **Touches the named parts?** Yes, the dispatch composer and the reviewer protocol.

### B9. Changed-files audit against Allowed Paths dropped at completion (GHI #1181, repaired) and missing at the airlock exit (GHI #1185, open)

- **Evidence:** #1181: *"So the finding is a regression by replacement. ... `gz obpi complete` took over as the way work is completed and builds its own receipt evidence without it"*, introduced by `d9bd6109d` (2026-04-05). The insight dated 2026-09-08T08:16: *"A dispatched implementer edited three files outside its brief allowlist ... the orchestrator detected it only by mtime-sorting git status, not by any gate"*.
- **Status:** #1181 is repaired (`85d55a627`, `19342f7c2`: completion refuses a change outside Allowed Paths). In #1185, the exit comparison landed (`81435469d`, `eed290d09`) and Stage 5 step 3b was added (`ae835b0d0`). The issue stays open because *"one outcome shown at a real package completion through the skill"* has not happened, and none can happen under A2.
- **Touches the named parts?** Yes, implementer containment.

### B10. Implementer escaped its sandbox and wrote fabricated attestation text (2026-09-28)

- **Evidence:** the insight dated 2026-09-28T00:35: *"An OBPI-0.35.0-07 Task 4 implementer ... ran two real gz content land AGENTS.md landings against this repository when a chained 'cd A && build && cd B && gz ...' failed mid-chain ... one ledger row recorded fabricated attestation text for g0"*. The rows were voided under the operator's *"Restore + void both (Recommended)"*. The related #1147 (an unquoted heredoc executes backticked prose) is open.
- **Status:** that incident was contained. No mechanical guard against a cwd escape was found in what was read **(the absence is inferred from the reading, not proven)**.
- **Touches the named parts?** Yes, the implementer persona and dispatch frames.

### B11. Preflight dropped from the pre-push scope, so CI went red unseen

- **When:** `58e4e46db` (2026-09-02) moved Preflight out of pre-push as *"a JANITORIAL scan, not a correctness gate"*. CI then failed 2026-10-04 to 2026-10-05.
- **Evidence:** the insight dated 2026-10-05T19:36: *"CI has failed on every push to main since 2026-10-04T16:35Z, nine runs ... The cause is the two tracked pipeline markers of the parked OBPI-0.35.0-10 run ... every local gate and every git-sync in two sessions reported success while CI was red"*.
- **Status:** that instance was cleared. Marker staleness still fails only in CI.
- **Touches the named parts?** The markers.

### B12. Smaller repaired items

- **#1167:** the abort path prescribed a lock release that exits 3. It became wrong at `b7bee38d7` (2026-06-11) and was repaired by `a1726901b`.
- **#1168:** the orientation's pipeline section was hard-coded empty. Repaired by `e2ce63afb`.
- **#1166:** `--no-subagents` was parsed and never read. Removed by `325bff69e`.
- **#1169:** the skill cited the wrong GHI. Repaired by `00c6977ea`.
- **Insight dated 2026-09-09T00:07:** the pipeline-gate block message prescribed `--from=implement`, which the parser rejects. That text is no longer in `.claude/hooks/pipeline-gate.py`. The repairing commit was not identified.
- **#886:** Stage-2 dispatch credit moved from the marker to the ledger (`9eca5fc3b`).
- **#887:** a blocked-on-operator state was added (`847f21f6`).
- **#992:** launch now advances the brief out of Draft (`5139681f5`).

## Part C — Latent defects discovered in the window (not regressions; open unless noted)

The pipeline was mostly exercised by OBPI-0.35.0 runs, and those runs surfaced gates that are documented and never fire. The repository files these under the family `doctrine-declared-without-mechanism`.

- **#1207:** two documented launch blockers, `validate_brief_for_pipeline` and `check_adr_evaluation_verdict`, *"have never had a caller"* since `bbb37150e` (2026-03-23).
- **#1199:** the launcher admits a withdrawn or superseded OBPI.
- **#1198:** `gz obpi dispatch` refusals return 1 and the process exits 0. *"A caller keying on the exit status ... reads a refused dispatch as recorded."*
- **#1195:** no rename writer checks for a run in flight.
- **#1202:** a SUPPORT proof's `artifact_edited` witness passes on file existence alone. Two OBPIs had a false edit-record claim, each caught only by the cross-vendor adversary.
- **#1225:** a stale reconcile receipt passes when the allowlist parses empty.
- **#1145:** the reconcile freshness check is keyed on mtime, so an acceptance proof's restore stales it.
- **#1193:** proof rows record the host-absolute source path (355 rows).
- **#993:** `human-review` hardcodes `stage="adversarial"`.
- **#968 (closed):** real read-only enforcement for reviewer subagents is not possible in Claude Code. Reviewers hold Read, Glob and Grep only, and this is tracked upstream.
- **Insight dated 2026-09-12T22:54:** the five subagent role bodies are hand-authored in two places (`.claude/agents/*.md`, read by `pipeline_runtime` dispatch, and `.gzkit/agents/*.md`). One unit test holds them together.
- **Insight dated 2026-10-12T00:46:** a commit or push while an implementer is writing stashes its edits mid-task, because of the pre-commit stash.
- **Insight dated 2026-10-11T01:11:35:** writes made through Bash are invisible to every Write/Edit-matched hook, including `pipeline-gate`. The commit-side fence (`post-authoring-src-commits`) exists because of this (GHI #844).

## Summary against the parts named for reuse

| Part | State on 2026-10-25 |
|---|---|
| Dispatch composer (`pipeline_dispatch.py`, review composers) | The prompt-growth and double-envelope regressions are repaired (#1096, #1095). The fix-cycle cap is dead code (#1200, open). Dispatch refusals exit 0 (#1198, open). A marker-cache fault drops a ledger row (#1208, open). |
| Persona frames (`.claude/agents`, `.gzkit/agents`, `.gzkit/personas`) | Two hand-authored copies with no writer (insight dated 2026-09-12). Read-only is enforced only as "no Bash" (#968). No guard against implementer cwd escape was found (B10, inferred). |
| Procedure pinning (`pipeline_procedure.py`, the served stage files) | Landed 2026-10-15 without OBPI Gate 5; its obligations are carried to the catalog by the RO-8 ruling. One control (S2-080) has been reworded since the attestation. **Never run on a real OBPI.** |
| Reviewer protocol (Stage 2 two-stage review, Step 4b, acceptance import) | Whole-tree proof currency kept by ruling (#1029), so the 4a/4b loop now stops and asks but is not gone (#1028). The finding-identity import refusal is unresolved in what was read. The verifier pipe gate that protects its evidence is switched off under safe mode (A3). |
| Stage fence and markers | The pipeline-gate hook is advisory under safe mode (A1). The commit-side fence stays CRITICAL. `gz task start` re-entry bypasses the launcher's gates (#1206). Stale detection crashes on one marker shape (#1205). |

The pipeline's regressions in this window came from three sources:

1. **Prose accretion in the skill.** Stage 4 grew 3.2x, which produced the 4a/4b loop and the context cost.
2. **Repairs that left the old site uncalled or dropped a control on replacement.** Examples are #1163, #1181 and #1167.
3. **A feature OBPI (0.35.0-15) that weakened a fence route while adding run-position tracking.** See #1206 and #1208.

The safe-mode switch-offs are deliberate, and the § Punch list records how each is restored **(inferred synthesis of the above)**.
