# Rule-pair audit — partition 1

Snapshot: `464dd4ff8fa2ee12d98afe99a867280e1b82b431`. Persona: spec-reviewer. Read all 29 files; reviewed all 203 assigned unordered pairs. Existing GHI numbers are provenance references, not assertions of current issue status.

Two conflict families identified (three pair entries because a subtree import repeats R01). This is a bounded reading, not proof that no other conflict exists. Implementation soundness is not inferred from rule agreement.

## R01 — blocking

Rule A: `.gzkit/rules/chores.md:25,116-117` — Canonical (package) | `src/gzkit/chores/<slug>/` | Authoritative templates

Rule B: `.gzkit/rules/skill-surface-sync.md:35-41,129` — **canonical** | Operator-authored content present at `.gzkit/<surface>/` — the source of truth

Amend CHORE.md for an existing canonical-class chore in gzkit. The chore authoring section names the package as canonical and .gzkit as an override; the sync table names .gzkit as the edit source. Doctor can copy package bytes over the project edit, while sync copies the project bytes to the package. Project-local chores are exempt and are not this case.

Mechanical review: Conflicting writers, not one trustworthy winner: src/gzkit/commands/chores.py:494-513 copies package to project; :577-578 invokes it for DAMAGED slugs. src/gzkit/sync_surfaces.py:905-926 copies canonical-class project files to package. Both code paths opened; no mutation performed.

Evidence: GHI #448; source snapshot 464dd4ff8fa2ee12d98afe99a867280e1b82b431

Recommendation: Reconcile chore authoring instructions with the canonical-class sync contract and explicitly distinguish bootstrap/doctor repair from authoring. Follow-up is corrective; no implementation authorized by this audit.

## R12 — theoretical

Rule A: `.gzkit/rules/chores.md:44,101-105` — **Lite by default** | Run `uv run -m unittest -q` (unit tier only); no `behave`, no network, no external services.

Rule B: `.gzkit/rules/tests.md:136` — `gz test` runs `unittest` over `tests/` then `behave` over `features/`. Both gates must pass for `gz check`.

An ordinary Lite chore follows its own Correct Evidence section and runs uv run gz check. That invokes behave despite the same chore rule forbidding behave on this default lane. This is specifically the Lite case; a deliberately Heavy chore does not establish this conflict.

Mechanical review: src/gzkit/quality.py:687-703 run_all_checks calls run_behave unconditionally. Read code, no suite invoked by this subagent.

Evidence: GHI #607; source snapshot 464dd4ff8fa2ee12d98afe99a867280e1b82b431

Recommendation: Make the Lite chore evidence guidance identify its permissible validation scope and specify when escalation to full quality checks changes that scope. Do not remove BDD from the general full-check contract to repair a chore-specific contradiction.

## Prior even-row dispositions

### R02: refuted

The old example silently equated "Implement one OBPI increment" with "edit source directly". governance-core.md:26-37 scopes a high-level planned-OBPI workflow; it never orders bypassing the pipeline. AGENTS.md:235 and :373-374 supply the execution mechanism and operator-initiation constraint. Missing a pipeline pointer may mislead, but the two instructions can both be satisfied.

- .gzkit/rules/governance-core.md:34: "Implement one OBPI increment"
- AGENTS.md:374: "NEVER work an OBPI without running it through the gz-obpi-pipeline skill"

.claude/hooks/pipeline-gate.py:130-185 inspected: candidate receipts/locks, allowed-path scope, stage guard, absent-marker block. This enforces the pipeline; it does not prove the workflow list prescribes freeform editing.

Evidence: GHI #606; GHI #127

### R04: refuted

Shared producers do not make disagreement impossible: authored Task trailers suppress auto-stamping, hand-authored tasks remain valid, and @advances is optional. The old claim "divergence can no longer arise" is false. task-discovery.md:146 now explicitly distinguishes crossing sets from nested/lagging channels. The stale "Witness status unruled" phrase at :109 conflicts with the same file's settled producer-fed explanation at :31-42, but is stale status prose, not the old impossible-gate claim.

- .gzkit/rules/task-discovery.md:107-108: "an authored **`Task:`** trailer of any form suppresses it"
- .gzkit/rules/task-discovery.md:146: "Drift is contradiction, never shortfall"

.gzkit/hooks/prepare-commit-msg-task-trailers:61-71 preserves authored trailers; src/gzkit/commands/task.py:559-582 appends a task declaration; src/gzkit/commands/validate_task_envelope.py:925-955 implements crossing-set comparison. All opened.

Evidence: GHI #752; GHI #820; GHI #731

### R06: retired

Remains retired. The prescribed fixed xhigh default is absent; the current tuning paragraph explicitly calls effort workload-dependent. No model-performance assertion was revalidated in this local pass.

- CLAUDE.md:13: "Effort is a dial to re-baseline per workload, never a fixed default"
- .gzkit/rules/model-selection.md:70: "Defaulting subagents to `effort: xhigh` when `effort: light` would suffice"

No mechanical winner claimed: matching current prose resolves the old contradiction.

Evidence: Prior matrix cites 1ddbfaaa1; current source snapshot 464dd4ff8fa2ee12d98afe99a867280e1b82b431

### R08: refuted

The explicitly linked bootstrap carve-out supplies the exception the prior row disregarded. Its full rationale says percentile names a band-ladder position, not a corpus measurement while bootstrapped. Therefore the claim that these rows necessarily fabricate corpus facts cannot be carried. This does not establish that bootstrap measurement defects have been repaired.

- .gzkit/rules/complexity-thresholds.md:86-87: "Three metrics in the data file carry bootstrap absolutes not derived from the cited corpus distillation"
- docs/governance/complexity/complexity-thresholds-rationale.md:63-69: "the percentile names a position in the canonical band ladder, not a corpus measurement, while the metric is in bootstrap"

Read the complete rationale, data JSON, and src/gzkit/complexity/thresholds.py. _check_percentile (:46-50) validates enum membership and _every_metric_has_block_band (:63-73) validates block-band presence; neither is asserted to prove empirical calibration here.

Evidence: GHI #404; GHI #405

### R10: refuted

Not requiring a Gate-3 run is not a directive to omit documentation. A Lite change can update its affected docs and satisfy Gates 1 and 2. The original row describes an enforcement-coverage concern, not mutually opposing instructions. Also a changed external CLI output contract is Heavy under current AGENTS lane rules; an alleged Lite example must establish that it does not change such a contract.

- .gzkit/rules/gate5-runbook-code-covenant.md:15: "Documentation is a first-class deliverable and must track behavior changes in the same patch set."
- AGENTS.md:202: "**lite**: Gates 1, 2 required"

src/gzkit/commands/gates.py:367-384 resolves lane then reads its gate list; code has no instruction to omit docs. No competing mechanical winner is necessary.

Evidence: GHI #705

### R12: carried

See conflict finding R12: the concrete Lite chore follows its own allowed full-check evidence command, which executes behave.

- **Lite by default** | Run `uv run -m unittest -q` (unit tier only); no `behave`, no network, no external services.
- `gz test` runs `unittest` over `tests/` then `behave` over `features/`. Both gates must pass for `gz check`.

src/gzkit/quality.py:687-703 run_all_checks calls run_behave unconditionally. Read code, no suite invoked by this subagent.

Evidence: GHI #607

### R14: refuted

The sensitivity rule itself has an explicit MX exception immediately after the default fail-close. A reader stopping before the exception is not a rule-pair contradiction. The rule states the exception is deliberate.

- .gzkit/rules/security-sensitivity.md:29: "The floor demotes to advisory inside the MX hangar"
- .gzkit/rules/security-sensitivity.md:29: "The 'escape is fail-closed' language in clause 2 does not hold in the hangar."

src/gzkit/mx/invariants.py:28-36 names five floor members, without sensitivity. src/gzkit/mx/checkpoint.py:21-37 preserves named floor and CRITICAL levels and demotes non-CRITICAL under-marker findings. Current mx-mode.md:40-61 also states level pinning, so old "only five names stay fatal" paraphrases would now be incomplete.

Evidence: GHI #682; GHI #843

### R16: retired

The obsolete 560 B headroom/fail-close promise was replaced with the advisory witness and pointer to live values. Its former wording is mentioned only as a dated error history. No live cap or actual Codex delivery measurement is claimed by this review.

- .gzkit/rules/agents-md-map-doctrine.md:34: "That witness is advisory and never fail-closed"
- .gzkit/rules/agents-md-map-doctrine.md:30: "The live enforced budgets are the values in data/instructions_files_budget.json"

src/gzkit/governance/trust_audits/surface_delivery_witness.py:129-159 emits advisory headroom/overrun observations, rather than failing on vendor-cap overrun. Read the function body.

Evidence: GHI #815; GHI #962

### R18: retired

Remains retired: the governing rule explicitly excludes operator-authored repository canon from its externally-authored-tool-output restriction.

- .gzkit/rules/governance-core.md:21: "Scope carve-out (binding): operator-authored repo canon is NOT covered"
- AGENTS.md:362: "GHIs are AUTHORIZED for direct repair, always."

No mechanical winner claimed; this is an explicit authority/scope carve-out in the rule.

Evidence: Prior matrix cites 1c36e0c4b; current source snapshot 464dd4ff8fa2ee12d98afe99a867280e1b82b431

### R20: refuted

The old row conflates choosing a candidate within a known exchange operation with classifying a cited artifact's system. Shape checks for admissibility do not by themselves conflict with using event type to determine subject. The stronger old code claim, "No code path reads an event type", is demonstrably false: the coupling auditor selects obpi_lock_released first. This refutes the submitted pairwise argument; it is not proof the candidate finder or historical exchange corpus is sound.

- AGENTS.md:364: "Never infer system membership from a shared field name, path, or directory: the citing EVENT type is the discriminator."
- .gzkit/rules/token-block-discipline.md:111: "gz validate --lock-exchange-coupling remains the ledger-replay backstop"

src/gzkit/exchange_records.py:441-463 checks CREATE/non-abandoned; :466-512 chooses from the exchange directory for a supplied OBPI. src/gzkit/governance/trust_audits/lock_exchange_coupling.py:61-69 first selects obpi_lock_released then reads handoff_path, independently of directory spelling. Both paths opened. No relocated-directory hypothetical was represented as an observed production failure.

Evidence: GHI #756; GHI #763

## Other observations — excluded from unresolved conflict counts

- **resolved-prescription-drift**, pairs [79]: adr-audit.md:29 still prescribes the retired serial unittest command as canonical. AGENTS.md:285 and canonical_steps.py:110 prescribe unittest-parallel. adr-audit.md:24 explicitly points to the canonical table, so authority is already settled; repair the stale example, do not ask the operator to choose a runner. Evidence: GHI #856; 464dd4ff8fa2ee12d98afe99a867280e1b82b431. src/gzkit/arb/validator.py:240-269 validates exact provenance, with timestamp-based retired-command exceptions.
- **resolved-terminology-drift**, pairs [107, 173]: changelog-release-notes.md:50 calls release-narrative review "attested at Gate 5"; agents-md-map-doctrine.md:59 and AGENTS.md:370 confine that name to OBPI/ADR completion. Root canon determines the scope; no new attestation gate should be inferred for a GHI release. Evidence: 464dd4ff8fa2ee12d98afe99a867280e1b82b431.
- **resolved-authority-with-live-mechanism**, pairs [401]: token-block-discipline.md:87 gives any starting agent implicit authority to reap; AGENTS.md:373 later explicitly reserves OBPI lock release to operator-initiated work. The explicit supersession resolves agent authority, but scripts/session_orientation.py:928 still invokes the reaper on entry. Distinguish runtime automatic cleanup from authorization for an agent to initiate lock operations; implementation assessment needs the owning session-entry context, not a new rule-pair ruling. Evidence: GHI #603; 464dd4ff8fa2ee12d98afe99a867280e1b82b431. Read scripts/session_orientation.py:908-940 and src/gzkit/lock_manager.py:308-373. Reaper writes an exchange, deletes the expired lock, and then emits release when a ledger sink is supplied.
- **unproven-prior-candidate**, pairs [213]: Prior R09: cli.md:81 says default human-readable and :82 describes --json; it does not expressly forbid readable JSON by default. tool-skill-runbook-alignment.md:29 includes JSON among forms. A concrete routing skill/default mismatch would establish the relevant defect; the generic JSON token alone does not prove opposite directives. No matching runtime surface was sampled during this pass. Evidence: GHI #202; 464dd4ff8fa2ee12d98afe99a867280e1b82b431.
- **stale-pointer-risk-not-conflict**, pairs [313]: governance-core.md:26-37 omits a direct pointer to the pipeline skill, but AGENTS explicit mechanism remains applicable. R02 should not recur as a claim that the word implement means freeform editing. Evidence: GHI #606; 464dd4ff8fa2ee12d98afe99a867280e1b82b431.

## Complete pair coverage

The JSON sibling records every assigned index, input path/hash inventory, individual disposition, findings, and prior-row accounting. Reviewed indices:

1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 93, 95, 97, 99, 101, 103, 105, 107, 109, 111, 113, 115, 117, 119, 121, 123, 125, 127, 129, 131, 133, 135, 137, 139, 141, 143, 145, 147, 149, 151, 153, 155, 157, 159, 161, 163, 165, 167, 169, 171, 173, 175, 177, 179, 181, 183, 185, 187, 189, 191, 193, 195, 197, 199, 201, 203, 205, 207, 209, 211, 213, 215, 217, 219, 221, 223, 225, 227, 229, 231, 233, 235, 237, 239, 241, 243, 245, 247, 249, 251, 253, 255, 257, 259, 261, 263, 265, 267, 269, 271, 273, 275, 277, 279, 281, 283, 285, 287, 289, 291, 293, 295, 297, 299, 301, 303, 305, 307, 309, 311, 313, 315, 317, 319, 321, 323, 325, 327, 329, 331, 333, 335, 337, 339, 341, 343, 345, 347, 349, 351, 353, 355, 357, 359, 361, 363, 365, 367, 369, 371, 373, 375, 377, 379, 381, 383, 385, 387, 389, 391, 393, 395, 397, 399, 401, 403, 405
