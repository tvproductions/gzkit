# Commands

All command surfaces use `gz [subcommand] [*] [*]`.

Command reference pages are operator manpages and part of Gate 3 proof.

---

## Governance

| Command | Description |
|---------|-------------|
| [`gz init`](init.md) | Initialize gzkit in a repository |
| [`gz upgrade`](upgrade.md) | Surface-only refresh of `.gzkit/<surface>/` from the installed wheel |
| [`gz prd`](prd.md) | Create a Product Requirements Document |
| [`gz constitute`](constitute.md) | Create a constitution artifact |
| [`gz specify`](specify.md) | Create an implementation brief (including OBPIs) |
| [`gz plan create`](plan-create.md) | Create an ADR |
| [`gz plan audit`](plan-audit.md) | Structural prerequisite check for plan-OBPI alignment |
| [`gz justify`](justify.md) | Produce a pre-execution reasoning scaffold (8 sections) |
| [`gz knowledge`](knowledge.md) | Generate/refresh OKF knowledge bundle |
| [`gz knowledge generate`](knowledge-generate.md) | Emit the OKF knowledge bundle |
| [`gz knowledge refresh`](knowledge-refresh.md) | Re-generate the bundle idempotently from current sources |
| [`gz context`](context.md) | Render focused-context Markdown payload (ADR + OBPIs + covering tests + governance) for one ADR |
| [`gz implement`](implement.md) | Run Gate 2 and record results |
| [`gz gates`](gates.md) | Run lane-required gates |
| [`gz status`](status.md) | Show multi-ADR OBPI progress and lifecycle status |
| [`gz state`](state.md) | Show artifact graph and readiness filters |
| [`gz adr status`](adr-status.md) | Show focused OBPI progress for one ADR |
| [`gz adr report`](adr-report.md) | Deterministic tabular report (summary or single ADR) |
| [`gz adr promote`](adr-promote.md) | Promote a pool ADR into canonical ADR package structure |
| [`gz adr demote`](adr-demote.md) | Demote a feature/foundation ADR back to pool (inverse of promote) |
| [`gz adr evaluate`](adr-evaluate.md) | Evaluate ADR/OBPI quality (deterministic scoring with verdict) |
| [`gz adr audit-check`](adr-audit-check.md) | Verify OBPI completeness/evidence for one ADR |
| [`gz adr fidelity`](adr-fidelity.md) | Run ADR Fidelity Assertions against the running system |
| [`gz adr covers-check`](adr-covers-check.md) | Verify ADR/OBPI @covers traceability in tests |
| [`gz flags`](flags.md) | Display all registered feature flags with current values |
| [`gz flag explain`](flag-explain.md) | Inspect one flag: metadata, resolved value, staleness, linked ADR |
| [`gz closeout`](closeout.md) | Present closeout paths/commands and record closeout initiation |
| [`gz patch release`](patch-release.md) | Run the GHI-driven patch release ceremony |
| [`gz attest`](attest.md) | Record human attestation with prerequisite enforcement |
| [`gz audit`](audit.md) | Run strict post-attestation audit reconciliation |
| [`gz adr emit-receipt`](adr-emit-receipt.md) | Emit completed/validated receipt with optional evidence scope |
| [`gz obpi status`](obpi-status.md) | Show focused runtime status for one OBPI |
| [`gz obpi pipeline`](obpi-pipeline.md) | Launch the OBPI pipeline runtime surface |
| [`gz obpi dispatch`](obpi-dispatch.md) | Record a Stage-2 subagent dispatch, or declare a single-driver run |
| [`gz obpi validate`](obpi-validate.md) | Validate OBPI brief(s) for authored, scaffold, and completion readiness |
| [`gz obpi sync`](obpi-sync.md) | Fail-closed reconciliation for one OBPI (receipt + ADR table) |
| [`gz obpi brief-drift`](obpi-brief-drift.md) | Check an OBPI brief against project state across five drift dimensions |
| [`gz obpi emit-receipt`](obpi-emit-receipt.md) | Emit completed/validated receipt for one OBPI |
| [`gz obpi repudiate`](obpi-repudiate.md) | Repudiate a fraudulent or erroneous OBPI completion without retiring the OBPI |
| [`gz obpi supersede`](obpi-supersede.md) | Supersede one OBPI by another |
| [`gz obpi block`](obpi-block.md) | Record that an OBPI is waiting on an operator ruling |
| [`gz obpi unblock`](obpi-unblock.md) | Record the operator ruling that releases a blocked OBPI |
| [`gz obpi withdraw`](obpi-withdraw.md) | Record an OBPI withdrawal event |
| [`gz obpi lock claim`](obpi-lock-claim.md) | Claim an OBPI work lock |
| [`gz obpi lock release`](obpi-lock-release.md) | Release an OBPI work lock |
| [`gz obpi lock check`](obpi-lock-check.md) | Check if an OBPI is locked |
| [`gz obpi lock list`](obpi-lock-list.md) | List active OBPI work locks |
| [`gz obpi audit`](obpi-audit.md) | Gather evidence for OBPI brief and record in audit ledger |
| [`gz obpi complete`](obpi-complete.md) | Atomically complete an OBPI (validate, write evidence, emit receipt) |
| [`gz git-sync`](git-sync.md) | Run guarded sync ritual |
| [`gz ledger correct`](ledger-correct.md) | Append a corrective action against a prior ledger row |
| [`gz ledger corrections`](ledger-corrections.md) | List every ledger row currently under a correction |
| [`gz ledger merge-driver`](ledger-merge-driver.md) | Reconcile a conflicted append-only JSONL file (invoked by git) |
| [`gz chores list`](chores-list.md) | List declared chores from the config registry |
| [`gz chores plan`](chores-plan.md) | Show deterministic plan details for one chore |
| [`gz chores run`](chores-run.md) | Execute one chore and append a dated log |
| [`gz chores audit`](chores-audit.md) | Audit chore log presence for one/all chores |
| [`gz chores doctor`](chores-doctor.md) | Re-scaffold missing or damaged canonical chores; preserve `proofs/` |
| [`gz chores propose-ghi`](chores-propose-ghi.md) | File GitHub issues for unfiled cluster proposal records in a chore's `proofs/` |
| [`gz migrate-semver`](migrate-semver.md) | Record SemVer ID rename events |
| [`gz mx enter`](mx-enter.md) | Open the Maintenance Hangar (MX) mode |
| [`gz mx exit`](mx-exit.md) | Close the Maintenance Hangar — hard gate (re-run every guard at full strength) |
| [`gz permitted-entry`](permitted-entry.md) | Airlock permitted-entry door — ad-hoc reconnaissance, light repair at most |
| [`gz register-adrs`](register-adrs.md) | Register existing ADR packages and linked OBPIs into ledger |
| [`gz personas drift`](personas-drift.md) | Report persona trait adherence from behavioral proxies |
| [`gz personas list`](personas-list.md) | Enumerate persona files from `.gzkit/personas/` |
| [`gz ontology sense`](ontology-sense.md) | Sweep the current structural shape and surface STRUCTURAL seams |
| [`gz ontology trace`](ontology-trace.md) | Walk one node's vertical lineage + lateral proof with edge provenance |
| [`gz ontology resense`](ontology-resense.md) | Diff the current shape versus the last sweep (the airlock re-sense gate) |
| [`gz ontology seams`](ontology-seams.md) | Fast contacts-only STRUCTURAL seam check |
| [`gz ontology reach`](ontology-reach.md) | Return one node's downstream blast-radius (transitive dependents) |
| [`gz airlock in`](airlock-in.md) | Run the airlock-IN preflight membrane for a target OBPI (diagnostic-only) |
| [`gz airlock out`](airlock-out.md) | Run the airlock-OUT exit drift-diff for a target OBPI (diagnostic-only) |
| [`gz handoff list`](handoff-list.md) | List session handoffs newest-first, optionally scoped by ADR |
| [`gz handoff resume`](handoff-resume.md) | Report the newest handoff for an ADR, its staleness, and first next step |
| [`gz handoff create`](handoff-create.md) | Author a handoff, fail-closed through the validation gate |
| [`gz handoff rulings`](handoff-rulings.md) | Read the append-only settled-ruling corpus carried across sessions |
| [`gz handoff decide`](handoff-decide.md) | Book the operator's transit decision on a resumed handoff (advisory record; it gates nothing) |
| [`gz handoff authorize`](handoff-authorize.md) | Deprecated alias for `gz handoff decide` |
| [`gz handoff archive`](handoff-archive.md) | Move handoffs older than a threshold into `.gzkit/handoffs/archive/` (move-not-delete) |
| [`gz roles`](roles.md) | List pipeline agent roles and handoff contracts |
| [`gz task list`](task-list.md) | List tasks for an OBPI with status |
| [`gz task start`](task-start.md) | Start or resume a task |
| [`gz task complete`](task-complete.md) | Complete a task |
| [`gz task block`](task-block.md) | Block a task with reason |
| [`gz task escalate`](task-escalate.md) | Escalate a task with reason |
| [`gz task fanout`](task-fanout.md) | Show TASK fan-out for a REQ-ID |
| [`gz task envelope diagnose`](task-envelope-diagnose.md) | Show per-channel TASK declarations side-by-side for an OBPI |
| [`gz issue file`](issue-file.md) | Cross-repo defect/enhancement filing wrapper (provenance auto-stamp; routes to `tvproductions/gzkit`) |

---

## Validation And Maintenance

| Command | Description |
|---------|-------------|
| [`gz check`](check.md) | Run full quality checks (lint, typecheck, test) in one pass |
| [`gz drift`](drift.md) | Detect spec-test-code governance drift |
| [`gz lint`](lint.md) | Run code linting checks |
| [`gz format`](format.md) | Auto-format code |
| [`gz smoke`](smoke.md) | Run the smoke/BVT tier against its declared time budget |
| [`gz test`](test.md) | Run unit tests |
| [`gz typecheck`](typecheck.md) | Run static type checks |
| [`gz validate`](validate.md) | Validate governance artifacts |
| [`gz governance render`](governance-render.md) | Render a governance surface (AGENTS.md) from the constitutional invariant registry |
| [`gz complexity distill`](complexity-distill.md) | Run a complexity distillation pass and emit a distilled-characteristics document |
| [`gz complexity advise`](complexity-advise.md) | Run the trigger-time complexity advisor against a file or directory and emit AdvisorDiagnosis output |
| [`gz complexity guide`](complexity-guide.md) | Surface authoring-time complexity hints for functions approaching the warn threshold (advise-band only, never blocks) |
| [`gz skill audit`](skill-audit.md) | Audit skill lifecycle metadata and mirror parity |
| [`gz skill list`](skill-list.md) | List all discovered skills and their metadata |
| [`gz skill new`](skill-new.md) | Create a new skill scaffold |
| [`gz parity check`](parity-check.md) | Run deterministic parity regression checks |
| [`gz readiness audit`](readiness-audit.md) | Audit agent-readiness maturity across core disciplines |
| [`gz readiness evaluate`](readiness-evaluate.md) | Run instruction architecture eval suite with positive/negative controls |
| [`gz check-config-paths`](check-config-paths.md) | Validate configured + manifest path coherence |
| [`gz cli audit`](cli-audit.md) | Validate CLI docs/manpage coverage |
| [`gz agent sync control-surfaces`](agent-sync-control-surfaces.md) | Regenerate control surfaces |
| [`gz covers`](covers.md) | Report requirement coverage from @covers annotations |
| [`gz test-shape`](test-shape.md) | Advisory inventory of test-shape debt (tautological + output assertions) |
| [`gz preflight`](preflight.md) | Detect and clean stale markers, orphan receipts, expired locks |
| [`gz tidy`](tidy.md) | Run maintenance checks and cleanup |
| [`gz interview`](interview.md) | Run interactive governance interviews |
| [`gz chores advise`](chores-advise.md) | Dry-run acceptance criteria for one chore |
| [`gz chores show`](chores-show.md) | Display CHORE.md content for one chore |
| [`gz frontmatter reconcile`](frontmatter-reconcile.md) | Rewrite drifted ADR/OBPI frontmatter to match ledger (ledger-wins) |

---

## ARB (Agent Self-Reporting)

| Command | Description |
|---------|-------------|
| [`gz arb ruff`](arb-ruff.md) | Run ruff via ARB and emit a lint receipt |
| [`gz arb step`](arb-step.md) | Wrap an arbitrary command and emit a step receipt |
| [`gz arb red`](arb-red.md) | Witness a BEHAVIOR REQ's test failing against the base tree |
| [`gz arb ty`](arb-ty.md) | Run `uvx ty` via ARB step wrapper |
| [`gz arb typecheck`](arb-typecheck.md) | Canonical Heavy-lane type-check receipt — wraps `gz typecheck` scope |
| [`gz arb coverage`](arb-coverage.md) | Run `coverage` via ARB step wrapper |
| [`gz arb validate`](arb-validate.md) | Validate recent receipts against JSON schemas |
| [`gz arb advise`](arb-advise.md) | Summarize recent receipts into recommendations |
| [`gz arb patterns`](arb-patterns.md) | Extract recurring anti-patterns from receipts |
| [`gz arb archive`](arb-archive.md) | Move aged, uncited receipts into `artifacts/receipts/archive/` |

---

## Operator Sequences

Primary daily loop (OBPI-first, pipeline-governed):

1. Orientation and ADR/OBPI context (`gz status`, `gz adr status`, `gz obpi status`)
2. Plan the OBPI, then execute it through `uv run gz obpi pipeline` (wrapper skill `/gz-obpi-pipeline` remains available and defers to the same shared runtime)
3. Present the Heavy-lane acceptance ceremony when required
4. Run guarded sync (`gz git-sync --apply --lint --test`)
5. Emit final OBPI completion accounting from the synced state (`gz obpi emit-receipt`)
6. Reconcile/update brief and ADR state (`gz obpi sync`, `gz adr status`)

ADR closeout loop (after OBPI batch completion):

1. ADR/OBPI reconciliation (`gz adr audit-check`)
2. Spec-test traceability reconciliation (`gz adr covers-check`)
3. Closeout presentation (`gz closeout`)
4. Human attestation (`gz attest`)
5. Post-attestation audit (`gz audit`)
6. ADR-level receipt/accounting (`gz adr emit-receipt`)

---

## Global Options

All commands support:

- `--help`
- `--version`
