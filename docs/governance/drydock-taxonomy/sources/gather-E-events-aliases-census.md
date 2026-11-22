# Gather E: ledger events, alias mechanisms, identifier census

Drydock taxonomy § 9, items 9 (event names), 13 (alias stores and grammars) and 14 (identifier census, sizing T9).
Gathered 2026-11-22, read-only: no repo file edited, no `gz` write command run. Counts are measurements
of the working tree's `.gzkit/ledger.jsonl` (20,827 rows, 0 unparseable, 78 distinct event types present;
the file shows ` M` in git status, so the counts are of the uncommitted tree).

Status marks: **RULED** (operator words quoted, with date), **SOURCED** (a canon page or code states it,
no operator ruling found in what was read), **CONTRADICTED** (two sources disagree, both quoted),
**UNSOURCED**, **UNBUILT** (ruled or specified, no code).

## 1. Events (item 9)

`src/gzkit/events.py` defines **107** event types, each a `Literal` discriminator on a Pydantic model, and the
discriminated union `TypedLedgerEvent` (`events.py:2372-2481`) admits exactly those 107 (no model is outside
the union, and no event type in the ledger is outside it). 29 of the 107 have **zero** rows in the ledger,
among them every order, tag, entry, discrepancy and dispatch event, `work_package_changed`,
`outcome_transitioned` and `req_proof_recorded`.

Every event carries `id`, `ts`, `schema`, and optional `parent` (`_EventBase`, `events.py:31-82`). The meaning
of `id` differs per type (column "`id` names"). The four TASK events extend `_TaskEventBase`
(`events.py:675-681`), which makes `task_id`, `obpi_id` and `adr_id` **required**: a TASK cannot be recorded
against a work package or order without naming an OBPI and an ADR.

Level column: the § 1 level table (Epic / Story / Order / Action), construction or repair, drydock record,
ADR/OBPI legacy, or not a work/repair record. 78 of the 107 record work or repair at some level; 29 are
marked not a work/repair record (control surfaces, corpus, handoff, airlock, session, insight, canary,
report and similar).

| # | Event | Model | Identifier fields (beyond `id`, `parent`) | `id` names | Level | Ledger count | path:line |
|---|---|---|---|---|---|---|---|
| 1 | `project_init` | `ProjectInitEvent` | none | the subject artifact | Intent records (above Epic) | 1 | `src/gzkit/events.py:85` |
| 2 | `prd_created` | `PrdCreatedEvent` | none | the subject artifact | Intent records (above Epic) | 1 | `src/gzkit/events.py:92` |
| 3 | `constitution_created` | `ConstitutionCreatedEvent` | none | the subject artifact | Intent records (above Epic) | 0 | `src/gzkit/events.py:98` |
| 4 | `obpi_created` | `ObpiCreatedEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 969 | `src/gzkit/events.py:104` |
| 5 | `adr_created` | `AdrCreatedEvent` | none | the subject artifact | ADR/OBPI legacy: ADR | 306 | `src/gzkit/events.py:111` |
| 6 | `artifact_edited` | `ArtifactEditedEvent` | task_id, commit | the subject artifact | Not a work record; carries TASK attribution | 5502 | `src/gzkit/events.py:119` |
| 7 | `attested` | `AttestedEvent` | task_id | the subject artifact | ADR/OBPI legacy: gates and Gate 5 (ADR- or OBPI-keyed) | 103 | `src/gzkit/events.py:132` |
| 8 | `gate_checked` | `GateCheckedEvent` | task_id | the subject artifact | ADR/OBPI legacy: gates and Gate 5 (ADR- or OBPI-keyed) | 943 | `src/gzkit/events.py:142` |
| 9 | `closeout_initiated` | `CloseoutInitiatedEvent` | none | the subject artifact | ADR/OBPI legacy: ADR | 142 | `src/gzkit/events.py:154` |
| 10 | `audit_receipt_emitted` | `AuditReceiptEmittedEvent` | receipt_event, task_id | the subject artifact | ADR/OBPI legacy: ADR | 471 | `src/gzkit/events.py:163` |
| 11 | `obpi_receipt_emitted` | `ObpiReceiptEmittedEvent` | receipt_event, obpi_completion | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 664 | `src/gzkit/events.py:174` |
| 12 | `artifact_renamed` | `ArtifactRenamedEvent` | new_id, task_id, ghi | the subject artifact | Alias layer: ADR/OBPI renames (semver migration, demotion, promotion) | 187 | `src/gzkit/events.py:185` |
| 13 | `foundation_grandfathered` | `FoundationGrandfatheredEvent` | task_id | slugged ADR | ADR/OBPI legacy: ADR | 51 | `src/gzkit/events.py:203` |
| 14 | `adr_annotated` | `AdrAnnotatedEvent` | none | the subject artifact | ADR/OBPI legacy: ADR | 9 | `src/gzkit/events.py:251` |
| 15 | `lifecycle_transition` | `LifecycleTransitionEvent` | none | the subject artifact | ADR/OBPI legacy: ADR | 81 | `src/gzkit/events.py:260` |
| 16 | `agent_sync_completed` | `AgentSyncCompletedEvent` | none | the subject artifact | Not a work/repair record | 1644 | `src/gzkit/events.py:269` |
| 17 | `adr_eval_completed` | `AdrEvalCompletedEvent` | none | the subject artifact | ADR/OBPI legacy: ADR | 237 | `src/gzkit/events.py:277` |
| 18 | `adr-evaluation` | `AdrEvaluationEvent` | artifact_id | the subject artifact | ADR/OBPI legacy: ADR | 168 | `src/gzkit/events.py:287` |
| 19 | `audit_generated` | `AuditGeneratedEvent` | none | the subject artifact | ADR/OBPI legacy: ADR | 18 | `src/gzkit/events.py:301` |
| 20 | `obpi_lock_claimed` | `ObpiLockClaimedEvent` | session_id | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 403 | `src/gzkit/events.py:310` |
| 21 | `obpi_lock_released` | `ObpiLockReleasedEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 384 | `src/gzkit/events.py:320` |
| 22 | `obpi_lock_ttl_warning` | `ObpiLockTtlWarningEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 133 | `src/gzkit/events.py:329` |
| 23 | `obpi_lock_lease_expired` | `ObpiLockLeaseExpiredEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 0 | `src/gzkit/events.py:338` |
| 24 | `obpi_withdrawn` | `ObpiWithdrawnEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 48 | `src/gzkit/events.py:352` |
| 25 | `legacy_unit_withdrawn` | `LegacyUnitWithdrawnEvent` | none | legacy unit (OBPI) | Bridge: retires an ADR/OBPI legacy unit through `gz wp` | 0 | `src/gzkit/events.py:360` |
| 26 | `obpi_parked` | `ObpiParkedEvent` | parked_to | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 377 | `src/gzkit/events.py:372` |
| 27 | `obpi_unparked` | `ObpiUnparkedEvent` | unparked_from, ghi | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 6 | `src/gzkit/events.py:392` |
| 28 | `obpi_blocked_on_operator` | `ObpiBlockedOnOperatorEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 17 | `src/gzkit/events.py:402` |
| 29 | `obpi_unblocked` | `ObpiUnblockedEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 17 | `src/gzkit/events.py:428` |
| 30 | `acceptance_recorded` | `AcceptanceRecordedEvent` | none | the subject artifact | Story or Order (WP/ORD acceptance) and legacy OBPI acceptance | 702 | `src/gzkit/events.py:443` |
| 31 | `stage2_dispatch_recorded` | `Stage2DispatchRecordedEvent` | task_id (int) | the subject artifact | ADR/OBPI legacy: OBPI pipeline run | 221 | `src/gzkit/events.py:451` |
| 32 | `stage2_single_driver_declared` | `Stage2SingleDriverDeclaredEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI pipeline run | 3 | `src/gzkit/events.py:479` |
| 33 | `obpi_superseded` | `ObpiSupersededEvent` | superseded_by | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 0 | `src/gzkit/events.py:498` |
| 34 | `obpi_completion_repudiated` | `ObpiCompletionRepudiatedEvent` | repudiated_receipt | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 11 | `src/gzkit/events.py:513` |
| 35 | `ledger_event_corrected` | `LedgerEventCorrectedEvent` | subject_event, subject_id, subject_ts | the SUBJECT row's id | Corrective action over any event (unlevelled) | 4 | `src/gzkit/events.py:523` |
| 36 | `security_floor_overridden` | `SecurityFloorOverriddenEvent` | obpi_id | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 6 | `src/gzkit/events.py:579` |
| 37 | `obpi_completion_uncovered_accept` | `ObpiCompletionUncoveredAcceptEvent` | obpi_id, req_id, task_id | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 74 | `src/gzkit/events.py:589` |
| 38 | `patch-release` | `PatchReleaseEvent` | version, tag | the subject artifact | Release Package (the version) | 35 | `src/gzkit/events.py:601` |
| 39 | `pipeline_marker_purged` | `PipelineMarkerPurgedEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI pipeline run | 17 | `src/gzkit/events.py:613` |
| 40 | `pipeline_launched` | `PipelineLaunchedEvent` | nonce | the subject artifact | ADR/OBPI legacy: OBPI pipeline run | 323 | `src/gzkit/events.py:621` |
| 41 | `pipeline_stage_transition` | `PipelineStageTransitionEvent` | none | the subject artifact | ADR/OBPI legacy: OBPI pipeline run | 90 | `src/gzkit/events.py:636` |
| 42 | `task_started` | `TaskStartedEvent` | task_id, obpi_id, adr_id | the subject artifact | Action: TASK (legacy-keyed: requires obpi_id, adr_id) | 685 | `src/gzkit/events.py:684` |
| 43 | `task_completed` | `TaskCompletedEvent` | task_id, obpi_id, adr_id | the subject artifact | Action: TASK (legacy-keyed: requires obpi_id, adr_id) | 666 | `src/gzkit/events.py:690` |
| 44 | `task_blocked` | `TaskBlockedEvent` | task_id, obpi_id, adr_id | the subject artifact | Action: TASK (legacy-keyed: requires obpi_id, adr_id) | 18 | `src/gzkit/events.py:696` |
| 45 | `task_escalated` | `TaskEscalatedEvent` | task_id, obpi_id, adr_id | the subject artifact | Action: TASK (legacy-keyed: requires obpi_id, adr_id) | 0 | `src/gzkit/events.py:703` |
| 46 | `intrinsic-complexity-attestation` | `IntrinsicComplexityAttestationEvent` | task_id | the subject artifact | Not a work/repair record; carries optional TASK attribution | 0 | `src/gzkit/events.py:716` |
| 47 | `distribution_baseline_regenerated` | `DistributionBaselineRegeneratedEvent` | none | the subject artifact | Not a work/repair record | 116 | `src/gzkit/events.py:738` |
| 48 | `composition_rendered` | `CompositionRenderedEvent` | task_id | the subject artifact | Not a work/repair record; carries optional TASK attribution | 129 | `src/gzkit/events.py:753` |
| 49 | `composition_drift_detected` | `CompositionDriftDetectedEvent` | none | the subject artifact | Not a work/repair record | 143 | `src/gzkit/events.py:764` |
| 50 | `chore_decommission_processed` | `ChoreDecommissionProcessedEvent` | obpi_id, task_id | the subject artifact | Not a work/repair record; carries optional TASK attribution | 7 | `src/gzkit/events.py:773` |
| 51 | `corpus_entry_appended` | `CorpusEntryAppendedEvent` | entry_id (corpus entry, not ENT) | the subject artifact | Not a work/repair record | 527 | `src/gzkit/events.py:783` |
| 52 | `corpus_entry_retired` | `CorpusEntryRetiredEvent` | retired_entry_id, retraction_entry_id, floor_moved_ids | the subject artifact | Not a work/repair record | 208 | `src/gzkit/events.py:798` |
| 53 | `corpus_retirement_reconciled` | `CorpusRetirementReconciledEvent` | retired_entry_id, retraction_entry_id | the subject artifact | Not a work/repair record | 7 | `src/gzkit/events.py:845` |
| 54 | `composition_candidate_emitted` | `CompositionCandidateEmittedEvent` | task_id | the subject artifact | Not a work/repair record; carries optional TASK attribution | 79 | `src/gzkit/events.py:875` |
| 55 | `rendition_committed` | `RenditionCommittedEvent` | task_id | the subject artifact | Not a work/repair record; carries optional TASK attribution | 53 | `src/gzkit/events.py:893` |
| 56 | `rendition_landed` | `RenditionLandedEvent` | landing_id, task_id | rendition-landed-<landing_id> | Not a work/repair record; carries optional TASK attribution | 14 | `src/gzkit/events.py:932` |
| 57 | `rendition_advisor_verdict` | `RenditionAdvisorVerdictEvent` | receipt_id, task_id | the subject artifact | Not a work/repair record; carries optional TASK attribution | 22 | `src/gzkit/events.py:975` |
| 58 | `brief_reconciled` | `BriefReconciledEvent` | brief_id, task_id | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 859 | `src/gzkit/events.py:991` |
| 59 | `brief_reconcile_drift_detected` | `BriefReconcileDriftDetectedEvent` | brief_id | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 416 | `src/gzkit/events.py:1011` |
| 60 | `brief_reconcile_drift_overridden` | `BriefReconcileDriftOverriddenEvent` | brief_id, original_receipt_id | the subject artifact | ADR/OBPI legacy: OBPI (legacy order) | 21 | `src/gzkit/events.py:1026` |
| 61 | `enforcement_claim_verified` | `EnforcementClaimVerifiedEvent` | claim_id | the subject artifact | Not a work/repair record | 90 | `src/gzkit/events.py:1038` |
| 62 | `mx_session_opened` | `MxSessionOpenedEvent` | session_id | the subject artifact | Drydock: out-of-service condition (no package level) | 4 | `src/gzkit/events.py:1054` |
| 63 | `mx_session_closed` | `MxSessionClosedEvent` | session_id | the subject artifact | Drydock: out-of-service condition (no package level) | 3 | `src/gzkit/events.py:1079` |
| 64 | `mx_session_lease_expired` | `MxSessionLeaseExpiredEvent` | session_id | the subject artifact | Drydock: out-of-service condition (no package level) | 21 | `src/gzkit/events.py:1092` |
| 65 | `mx_session_lease_renewed` | `MxSessionLeaseRenewedEvent` | session_id | the subject artifact | Drydock: out-of-service condition (no package level) | 29 | `src/gzkit/events.py:1112` |
| 66 | `mx_marker_repaired` | `MxMarkerRepairedEvent` | session_id | the subject artifact | Drydock: out-of-service condition (no package level) | 0 | `src/gzkit/events.py:1127` |
| 67 | `mx_contract_amended` | `MxContractAmendedEvent` | session_id, commit | the subject artifact | Drydock: out-of-service condition (no package level) | 229 | `src/gzkit/events.py:1142` |
| 68 | `insight_recorded` | `InsightRecordedEvent` | insight_ts, supersedes | the subject artifact | Not a work/repair record | 447 | `src/gzkit/events.py:1160` |
| 69 | `blocks` | `BlocksEvent` | blocker, blocked | the subject artifact | Work-domain edges between any ids (unlevelled) | 0 | `src/gzkit/events.py:1186` |
| 70 | `blocked_by` | `BlockedByEvent` | blocked, blocker | the subject artifact | Work-domain edges between any ids (unlevelled) | 0 | `src/gzkit/events.py:1194` |
| 71 | `discovered_from` | `DiscoveredFromEvent` | discovered, origin | the subject artifact | Work-domain edges between any ids (unlevelled) | 0 | `src/gzkit/events.py:1202` |
| 72 | `validates` | `ValidatesEvent` | validator, validated | the subject artifact | Work-domain edges between any ids (unlevelled) | 0 | `src/gzkit/events.py:1210` |
| 73 | `adversarial_validation` | `AdversarialValidationEvent` | obpi_id, job_id, adversary_receipt, acceptance_review_ids | the subject artifact | ADR/OBPI legacy: OBPI pipeline run | 29 | `src/gzkit/events.py:1218` |
| 74 | `red_receipt_emitted` | `RedReceiptEmittedEvent` | req_id, receipt_id, base_commit, obpi_id | the subject artifact | Construction proof: BEHAVIOR REQ falsifiability (legacy REQ) | 306 | `src/gzkit/events.py:1273` |
| 75 | `red_commit_receipt_emitted` | `RedCommitReceiptEmittedEvent` | commit, receipt_id | the subject artifact | Repair proof: direct GHI fix commit (ghi-close) | 411 | `src/gzkit/events.py:1322` |
| 76 | `airlock_in` | `AirlockInEvent` | none | the subject artifact | Not a work/repair record | 88 | `src/gzkit/events.py:1341` |
| 77 | `airlock_out` | `AirlockOutEvent` | none | the subject artifact | Not a work/repair record | 34 | `src/gzkit/events.py:1364` |
| 78 | `surface_weight_recalibrated` | `SurfaceWeightRecalibratedEvent` | none | the subject artifact | Not a work/repair record | 1 | `src/gzkit/events.py:1390` |
| 79 | `session_exit_bookmark_skipped` | `SessionExitBookmarkSkippedEvent` | session_id | the subject artifact | Not a work/repair record | 252 | `src/gzkit/events.py:1423` |
| 80 | `handoff_resume_authorized` | `HandoffResumeAuthorizedEvent` | session_id | the subject artifact | Not a work/repair record | 107 | `src/gzkit/events.py:1452` |
| 81 | `handoff_resume_decided` | `HandoffResumeDecidedEvent` | session_id | the subject artifact | Not a work/repair record | 309 | `src/gzkit/events.py:1476` |
| 82 | `handoff_resume_blocked` | `HandoffResumeBlockedEvent` | session_id | the subject artifact | Not a work/repair record | 1 | `src/gzkit/events.py:1509` |
| 83 | `guard_canary_reviewed` | `GuardCanaryReviewedEvent` | none | the subject artifact | Not a work/repair record | 105 | `src/gzkit/events.py:1540` |
| 84 | `section_ownership_genesis` | `SectionOwnershipGenesisEvent` | none | the subject artifact | Not a work/repair record | 2 | `src/gzkit/events.py:1562` |
| 85 | `unowned_ratchet_updated` | `UnownedRatchetUpdatedEvent` | predecessor_event_id, covering_entry_ids | the subject artifact | Not a work/repair record | 10 | `src/gzkit/events.py:1591` |
| 86 | `section_ownership_unowned` | `SectionOwnershipUnownedEvent` | none | the subject artifact | Not a work/repair record | 0 | `src/gzkit/events.py:1654` |
| 87 | `section_ownership_reanchored` | `SectionOwnershipReanchoredEvent` | predecessor_event_id | the subject artifact | Not a work/repair record | 1 | `src/gzkit/events.py:1682` |
| 88 | `report_published` | `ReportPublishedEvent` | predecessor | the subject artifact | Not a work/repair record | 3 | `src/gzkit/events.py:1719` |
| 89 | `outcome_transitioned` | `OutcomeTransitionedEvent` | outcome, evidence | outcome code | Catalog: outcome lifecycle (below Epic, above Story) | 0 | `src/gzkit/events.py:1751` |
| 90 | `req_proof_recorded` | `ReqProofRecordedEvent` | req, commit, evidence | REQ (catalog or repair) | Catalog: REQ proof (catalog or repair REQ) | 0 | `src/gzkit/events.py:1767` |
| 91 | `work_package_transitioned` | `WorkPackageTransitionedEvent` | work_package, baseline[].req, review_receipt, order_decisions{ORD}, held_reqs | WP | Story: work/repair package (construction and repair) | 5 | `src/gzkit/events.py:1806` |
| 92 | `work_package_changed` | `WorkPackageChangedEvent` | work_package, supplement (WP id), item | WP | Story: work/repair package (construction and repair) | 0 | `src/gzkit/events.py:1844` |
| 93 | `work_package_issue_closed` | `WorkPackageIssueClosedEvent` | work_package, issue, commit | WP | Story: repair package (repair); the GHI close against it | 2 | `src/gzkit/events.py:1869` |
| 94 | `work_package_dispatched` | `WorkPackageDispatchedEvent` | work_package, order, subject, dispatch_id | WP | Action: one dispatch on a package or order (construction and repair) | 0 | `src/gzkit/events.py:1896` |
| 95 | `dispatch_claimed` | `DispatchClaimedEvent` | dispatch_id, agent_id | D- | Action: the dispatch record (drydock) | 0 | `src/gzkit/events.py:1926` |
| 96 | `dispatch_ended` | `DispatchEndedEvent` | dispatch_id, agent_id | D- | Action: the dispatch record (drydock) | 0 | `src/gzkit/events.py:1948` |
| 97 | `dispatch_voided` | `DispatchVoidedEvent` | dispatch_id, work_package | D- | Action: the dispatch record (drydock) | 0 | `src/gzkit/events.py:1967` |
| 98 | `work_package_blocked` | `WorkPackageBlockedEvent` | work_package, order | WP or ORD | Story, or Order when `order` is set (construction and repair) | 0 | `src/gzkit/events.py:1984` |
| 99 | `work_package_unblocked` | `WorkPackageUnblockedEvent` | work_package, order, req | WP or ORD | Story, or Order when `order` is set (construction and repair) | 0 | `src/gzkit/events.py:2013` |
| 100 | `order_transitioned` | `OrderTransitionedEvent` | order, work_package, baseline[].req, superseded_by (ORD), review_receipt, carried[].tag_id/.discrepancy_id | ORD | Order: work or repair order; Gate 5 at closed | 0 | `src/gzkit/events.py:2051` |
| 101 | `tag_issued` | `TagIssuedEvent` | tag_id, order, work_package, mx_session_id | TAG | Drydock record: tag-out log (on an order) | 0 | `src/gzkit/events.py:2125` |
| 102 | `tag_hung` | `TagHungEvent` | tag_id, dispatch_id, order, work_package, issued_by_session, mx_session_id | TAG | Drydock record: tag-out log (on an order) | 0 | `src/gzkit/events.py:2158` |
| 103 | `tag_clearance_authorized` | `TagClearanceAuthorizedEvent` | tag_id, order, work_package, hanging_dispatch_id, mx_session_id | TAG | Drydock record: tag-out log (on an order) | 0 | `src/gzkit/events.py:2198` |
| 104 | `tag_cleared` | `TagClearedEvent` | tag_id, order, work_package, dispatch_id, hanging_dispatch_id, authorized_by_session, mx_session_id | TAG | Drydock record: tag-out log (on an order) | 0 | `src/gzkit/events.py:2231` |
| 105 | `entry_booked` | `EntryBookedEvent` | entry_id (ENT), order, work_package, dispatch_id, mx_session_id | ENT | Drydock record: maintenance-record entry (an Action on an order) | 0 | `src/gzkit/events.py:2267` |
| 106 | `discrepancy_recorded` | `DiscrepancyRecordedEvent` | discrepancy_id, order, work_package, tag_id, dispatch_id, mx_session_id | DSC | Drydock record: list of discrepancies (on an order) | 0 | `src/gzkit/events.py:2299` |
| 107 | `discrepancy_cleared` | `DiscrepancyClearedEvent` | discrepancy_id, order, work_package, entry_id (ENT), tag_id, ghi, mx_session_id | DSC | Drydock record: list of discrepancies (on an order) | 0 | `src/gzkit/events.py:2335` |

### 1a. What the event table shows

- **No Epic-level event.** No event records a return to service package or a feature package; § 2's "none"
  for both is confirmed at the ledger level (T6, T7). `outcome_transitioned` (0 rows) is the nearest, an
  outcome being below the feature package. **UNBUILT.**
- **Work and repair share every package and order event.** No event name says `repair_` or `work_`; kind
  is read from the package record (`WorkPackage.kind`), as RO-5 ruling 6 and RP-12 ruling 43 rule. **RULED**
  (RO-5 ruling 6, selection *"A"*, `docs/governance/harbor-ro5-work-packages.md:29`; RP-12 ruling 43,
  *"a"*, 2026-11-05, `docs/governance/harbor-ro12-contractor-kit.md:501`).
- **The `work_package_` prefix covers orders too.** `work_package_dispatched`, `work_package_blocked` and
  `work_package_unblocked` act on an order when their `order` field is set, and the block's `id` is then
  the **order's** id (`events.py:1984-2030`), while `work_package_dispatched`'s `id` is always the
  package's (`events.py:1901`). One event name, two levels.
- **Only one package has events:** `WP-01-astral-toolchain`, 5 `work_package_transitioned` rows
  (`initiated → frozen → commenced → accepted → closed`, 2026-10-28 to 2026-10-29, `decision: proceed`)
  and 2 `work_package_issue_closed` rows (#1183, #1184). It is a repair package run through all five
  states, before RP-12 ruling 44 (2026-11-05) cut a repair package to `initiated → closed`; ruling 44
  names this case itself (*"`WP-01-astral-toolchain`, closed 2026-10-29 through all five p[hases]…"*,
  `harbor-ro12-contractor-kit.md:503`). **RULED**, not a contradiction.
- **`TASK` events are keyed to the legacy chain.** `_TaskEventBase` requires `obpi_id` and `adr_id`
  (`events.py:679-680`). An order's tasks "bind by their own ledger events naming the order" (RP-12
  ruling 46, *"b"*, 2026-11-05, `harbor-ro12-contractor-kit.md:507`), but no TASK event has an `order`
  field. **CONTRADICTED** (see Contradictions, C4).
- **`entry_id` names two things.** `corpus_entry_appended.entry_id` (`events.py:794`) is a corpus row id;
  `entry_booked.entry_id` and `discrepancy_cleared.entry_id` (`events.py:2284`, `2352`) are `ENT-<NN>-<slug>`.
- **`task_id` has two types.** `stage2_dispatch_recorded.task_id: int` (`events.py:476`); every other
  `task_id` is a `str` TASK id.
- **`session_id` names two things.** Harness session (`obpi_lock_claimed`, handoff events,
  `session_exit_bookmark_skipped`) and MX session (`mx_session_*`; `mx_session_id` on the drydock records,
  minted `str(uuid.uuid4())` at `src/gzkit/commands/mx_cmd.py:335`).
- **The MX open event keeps the retired vocabulary.** `mx_session_opened.mode: Literal["mx", "safe"]`
  (`events.py:1068-1070`), while the marker reads `level` (hangar | drydock) with `mode` as its alias
  (`src/gzkit/mx/marker.py:80-88`). The ledger event was never given `level`. See C7.
- **The order's own fields are unpatterned.** Every `order` field on an event is `str, min_length=1`
  (e.g. `events.py:2060`, `2138`, `2285`), never `ORDER_ID_PATTERN`; every `work_package` field likewise
  is never `WORK_PACKAGE_ID_PATTERN`. Only `tag_id`, `entry_id`, `discrepancy_id` and `dispatch_id` carry
  their pattern on the event.
- **The forward rule's registry** `data/catalog/delivery_events.json` names nine delivery event types read
  after its cutover `2026-10-22T08:14:40+00:00`: `task_started`, `task_completed`, `obpi_receipt_emitted`,
  `gate_checked`, `attested`, `acceptance_recorded`, `red_receipt_emitted`, `stage2_dispatch_recorded`,
  `closeout_initiated`. **RULED** (operator 2026-10-22, *"All nine (Rec.)"*, *"Timestamp in registry
  (Rec.)"*, quoted in the file's `_doc`). None of the drydock events is in it.
- Closed sets on these events beyond § 5 of the draft: `OrderState` (`events.py:2035`), `LifecycleState`
  plus `SideState` (`events.py:1732-1746`, ten states and `blocked`, `deferred`), `ReqVerdict`
  (`SATISFIED | UNSATISFIED | UNKNOWN`, `events.py:1748`), `WorkPackageChangedEvent.approver`
  (`operator | coordinator`), `.form` (`deviation | waiver`), `.duration` (`temporary | permanent`)
  (`events.py:1855-1865`), `DispatchClaimedEvent.source` (`stamp | agent_returned`, `events.py:1943`),
  `DispatchOver` (`ended | voided`, `events.py:2112`), `TagPositionFound` (adds `on`, `events.py:2115`),
  `tag_clearance_authorized.repair_activity` (`not-available` only, `events.py:2220`),
  `PipelineStageTransitionEvent.stage` (`implement | verify | ceremony | sync`) and `.position_kind`
  (`task | phase | round | step`) (`events.py:654-660`), `AdversarialValidationEvent.verdict` (four,
  `events.py:1237-1242`), `RedReceiptEmittedEvent.failure_class` (four) and `.base_provenance` (two),
  `RedCommitReceiptEmittedEvent.verdict` (five), `ObpiCompletionRepudiatedEvent.cause` (three),
  `LedgerEventCorrectedEvent.disposition` (three) and `.cause` (four), `HandoffResumeDecidedEvent.decision`
  (`proceed | pause | hold | revert`, a fourth decision set beside Gate 5's and the exits).
- **Specified, not built.** RO-5's amended row 6 names a `catalog_edited` event and `withdrawn` in
  `LifecycleState` (`docs/governance/harbor-ro5-work-packages.md:94`). Neither exists in `events.py`.
  **UNBUILT.**

## 2. Alias mechanisms (item 13)

| # | Store / grammar | Applies to | Grammar | Resolved by | path:line | Instances in store |
|---|---|---|---|---|---|---|
| A1 | `WorkPackage.aliases: tuple[str, ...]` | work and repair packages | **none**: free text. Help says `RO-<n>` | **nothing.** `gz wp` lookup is an exact `wp.id == work_package` match (`src/gzkit/commands/wp.py:103-104`); airlock likewise (`src/gzkit/commands/airlock.py:89-91`) | `src/gzkit/models/catalog.py:212`; CLI `gz wp new --alias` `src/gzkit/cli/parser_wp.py:272`; uniqueness across the store `src/gzkit/governance/trust_audits/catalog.py:325`, `338-340`; rendered only on GitHub, `package_mark` `src/gzkit/work_package_github.py:25-32` (`WP-01-astral-toolchain (RO-9)`), and in `gz wp show --json` | 1: `RO-9` on `WP-01-astral-toolchain` (`data/catalog/work_packages.json`) |
| A2 | `Order.aliases` with `ORDER_ALIAS_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._-]*$"` | work and repair orders | one word; refused if shaped as an `ORD-` or `WP-` id | **nothing.** `gz wp order` lookup is exact (`src/gzkit/commands/wp_order.py:59-60`) | `src/gzkit/models/catalog.py:52`, `245`; CLI `--alias` `src/gzkit/cli/parser_wp_order.py:81` (help `O<n>`); unique within its package and not id-shaped `src/gzkit/governance/trust_audits/catalog.py:377-404`; rendered `gz wp order show` `src/gzkit/commands/wp_order.py:341` | 0 (`data/catalog/orders.json` has no orders) |
| A3 | The `artifact_renamed` fold (`fold_renames`) | ADR and OBPI ids: semver migration (`gz migrate-semver`), demotion to pool, promotion | `(id, new_id)` pairs folded in time order, idempotent | `src/gzkit/obpi_lifecycle.py:210-258`; read by `Ledger` (`src/gzkit/ledger.py:21`, `894`, `929-933` `canonicalize_id`) and the seam (`src/gzkit/core/id_resolver.py:137`, `327-332`) | events `events.py:185-200` | 187 `artifact_renamed` rows (156 from `ADR-…` ids, 31 from `OBPI-…`), folding to 182 renamed ids |
| A4 | Short-form prefix expansion (`active_prefix_matches`) | ADR and OBPI short ids → the one active slugged id | match on `<id>-`, never a bare prefix | `src/gzkit/artifact_prefix.py:32`; used `id_resolver.py:144-157`, `255-265` | n/a | derived, no store |
| A5 | Bare-input normalization | operator input `0.1.0` → `ADR-0.1.0`; `0.1.0-01` → `OBPI-…`; slug → `ADR-pool.<slug>` | prefix added when absent | `src/gzkit/core/models.py:239-251` | n/a | no store |
| A6 | ADR short form as identity (`ADR-X.Y.Z` for `ADR-X.Y.Z-<slug>`) | ledger idempotency without a rename event (GHI #279) | `_ADR_SEMVER_RE` → `compose_adr_id` | `src/gzkit/ledger.py:83-100` | n/a | derived |
| A7 | Catalog REQ supersession `supersedes` | catalog and repair REQs | `REQ_ID_PATTERN` | not an alias: a new REQ superseding the prior, which stays whole (RP-12 ruling 31) | `src/gzkit/models/catalog.py:115-117` | 0 REQs |
| A8 | Field-value alias: marker `mode` read as `level` | the out-of-service marker `.gzkit/mx.json` | `AliasChoices("level", "mode")`, `mx`/`safe` mapped to `hangar`/`drydock` | `src/gzkit/mx/marker.py:80-88` | n/a | the marker |
| A9 | CLI verb and flag aliases | `gz handoff authorize` → `decide`; `--lock-handoff-coupling` | argparse, shared `dest` | `src/gzkit/cli/parser_handoff.py:43-58`, `299-328`; `src/gzkit/cli/parser_maintenance.py:808-819` | n/a | n/a |
| A10 | Acceptance proof aliases (`proof_aliases`) | proof ids within an acceptance history (consecutive witnessed successes share an alias) | computed | `src/gzkit/acceptance.py:60-78` | n/a | derived |

Prose-only short names, with **no grammar, store or resolver in code**: `RP-n` (no `RP-` regex anywhere
under `src/gzkit`), `RO-n` (only the A1 instance and the help string), `O1` to `O9` (none stored; A2 would
admit them), `WO-n` (none). A search over `src/gzkit` for `RP-[`, `RO-[`, `"RP-`, `"RO-` and `WO-<digit>`
returned only ruling citations in messages.

Status of the alias rulings:

- **RO-n resolves through the identity seam: RULED, not built (CONTRADICTED by the code).** RO-5 ruling 6,
  selection *"A"*: *"the drydock's `RO-n` names stay as aliases resolved through RO-2's identity seam"*
  (`docs/governance/harbor-ro5-work-packages.md:29`). Operator 2026-11-03, *"A"*: *"`RP-n` replaces `RO-n`
  in the contract and specifications by contract amendment, keeping the numbers, `RO-n` staying an alias
  through the identity seam, …, the record id staying `WP-<NN>-<slug>`"*
  (`docs/rnd/repair-work-organization.md:400`); commissioned *"2 — the `RP-n` alias in the identity seam,
  by GHI"* (line 402). Code: A1 has no grammar and no resolver; `IdKind` has no `RP`/`RO` kind. GHI #1302
  (OPEN, labels `defect`, `runtime`) tracks it.
- **Order aliases: RULED and built as ruled.** RP-12 ruling 43 (*"a"*, 2026-11-05): *"A short name used in
  a specification, such as this page's `O2`, is kept as an alias"*; ruling 49 (*"b"*, 2026-11-05):
  *"Two orders in one package may not share an alias; orders in two packages may."* Code matches
  (`trust_audits/catalog.py:377-404`). Neither ruling says an order alias **resolves**; ruling 49 says
  *"`O2` … resolves with the package beside it"*, and nothing resolves it. **CONTRADICTED** in part (C2).
- **Legacy ids resolve through the rename layer: SOURCED.** Requirements model § 2: *"Legacy `ADR-`,
  `OBPI-`, `REQ-<semver>-NN-MM` and `TASK-` identifiers are frozen and resolve through the ledger's
  `artifact_renamed` alias layer, which `gz migrate-semver` already writes"*
  (`docs/governance/ieee/requirements-model.md:57-59`). Built for ADR and OBPI (A3); the 187 rename rows
  rename only ADR and OBPI ids, so no REQ or TASK has ever been renamed.
- **Package aliases are unique across the store; order aliases only within a package.** Two different
  uniqueness scopes for the two alias stores (`trust_audits/catalog.py:339` "An alias resolves to one
  package (RO-5 ruling 6)" against `:387-391`, ruling 49). **SOURCED** for both.
- **GHI #1302's cited lines are stale.** It cites `models/catalog.py:171`, `parser_wp.py:190` and
  `trust_audits/catalog.py:219-243`; today they are `:212`, `:272` and `:314-340`.

## 3. Identifier census (item 14)

"Via IdKind": whether `gzkit.core.models.id_kind` (`core/models.py:95-110`) classifies the id and
`gzkit.core.id_resolver.resolve` (`id_resolver.py:221-236`) can resolve it. `IdKind` has four members,
`ADR, OBPI, REQ, TASK` (`core/models.py:86-92`). Note that `id_kind` reads only the leading token, so
`REQ-<n>` and `TASK-<slug>` are classified too.

| Identifier | Pattern constant | Minted at | Parsed at | Rendered at | Via IdKind? |
|---|---|---|---|---|---|
| PRD `PRD-<SLUG>-<semver>` | `PrdFrontmatter.id` pattern `^PRD-[A-Z0-9]+-[0-9]+\.[0-9]+\.[0-9]+$` (`core/models.py:402`); loose `ARTIFACT_PREFIX_BODY` (`:51`), `ADR_PRD_PREFIX_BODY` (`:61`) | `_canonicalize_prd_id` `src/gzkit/commands/init_cmd.py:1622-1644` (`gz init prd`, `prd()` at `:1647`); event `prd_created` (1 row) | `core/models.py:402`; registry glob `src/gzkit/registry.py:202`; `src/gzkit/sync.py:232` | `gz init prd` (`init_cmd.py:1647`) | **No**: `id_kind` raises for `PRD-` |
| Family code | `Family.code` pattern `^[A-Z]$` (`src/gzkit/models/catalog.py:60`); no named constant | not minted: seeded from `src/gzkit/catalog_seed.json` by `gz init` (`src/gzkit/catalog_seed.py:35`), and held in `data/catalog/families.json` (11: `X H C M P D R G A L Q`) | `models/catalog.py:60`; as the first letter of `OUTCOME_CODE_PATTERN` (`:40`) | no CLI renders it | No |
| Capability `SES1` | **none** | none | none | none | No. **UNBUILT** (requirements model § 2, ruled 2026-10-29) |
| Outcome `H1.4` | `OUTCOME_CODE_PATTERN = r"^[A-Z][1-9][0-9]*(\.[1-9][0-9]*)*$"` (`models/catalog.py:40`) | no verb mints one; `outcomes.json` is empty and its `_doc` says *"created by RO-11's entry verb"* | `models/catalog.py:73`, `124` (`member_of`), `206` (`WorkPackage.outcome`); event `outcome_transitioned.outcome` (`events.py:1760`, unpatterned) | `gz wp show` `src/gzkit/commands/wp.py:572` (`delivers:`) | No |
| Catalog REQ `REQ-<n>` (both specializations) | `CATALOG_REQ_ID_BODY = r"REQ-[1-9][0-9]*"` (`core/models.py:71`); `REQ_ID_PATTERN` (`models/catalog.py:43`) | `next_req_id` `src/gzkit/req_store.py:36-48` → `compose_catalog_req_id` `core/models.py:187-194`; called by `gz wp req new` `src/gzkit/commands/wp_req.py:106` (repair REQs only; catalog REQs are RP-11's intake, unbuilt) | `core/models.py:197-211`; `models/catalog.py:106`, `116`, `138`, `187`; `id_resolver.py:59`, `209-214`; `src/gzkit/traceability.py:58`; `src/gzkit/governance/trust_audits/catalog_forward.py:34`; `src/gzkit/acceptance_package.py:85`; `trust_audits/catalog.py:546` | `gz wp req new` `wp_req.py:128`; `gz wp order show` baseline/holds `wp_order.py:339-340` | **Yes**, `IdKind.REQ`; resolves only from the catalog, parent = outcome or, for a repair REQ, its `WP-` package (`id_resolver.py:200-218`, `309-310`). The portable `ReqId` model (`core/models.py:517-534`) **rejects** it (legacy form only) |
| Legacy REQ `REQ-<semver>-<NN>-<NN>` | `REQ_ID_BODY`, `REQ_ID_BODY_PLAIN`, `REQ_SHORT_ID_BODY` (`core/models.py:62-68`) | authored in OBPI briefs; composed by `compose_req_id` `core/models.py:182-184` (`src/gzkit/triangle.py:79`) | `core/models.py:146`, `260-263`, `525`; `src/gzkit/tasks.py:155`; `traceability.py:55` (`@covers`); `catalog_forward.py:34` | throughout the OBPI and TASK commands (e.g. `gz task list`) | **Yes**, `IdKind.REQ`; resolves through the brief that lists it, else a parked/withdrawn OBPI by spelling (`id_resolver.py:160-197`) |
| Work / repair package `WP-<NN>-<slug>` | `WORK_PACKAGE_ID_PATTERN = r"^WP-[0-9]{2,}-[a-z0-9]+(-[a-z0-9]+)*$"` (`models/catalog.py:46`) | `next_id` `src/gzkit/work_package_store.py:24-32`, called `gz wp new` `commands/wp.py:181`. Reads the **store only**, not the ledger | `models/catalog.py:134`, `203`, `243`; `acceptance_package.py:55`; `commands/airlock.py:89`; `split("-")[1]` at `work_package_store.py:31`, `37` and `trust_audits/catalog.py:323`; alias shape check `:397` | `gz wp new` `wp.py:195`; `gz wp attach` `:217`; transitions `:292`; `gz wp show` `:571`; `gz wp runs` `:604`; GitHub comment `work_package_github.py:32` | **No** |
| Work / repair order `ORD-<NN>-<slug>` | `ORDER_ID_PATTERN = r"^ORD-[0-9]{2,}-[a-z0-9]+(-[a-z0-9]+)*$"` (`models/catalog.py:49`) | `next_order_id` `src/gzkit/order_store.py:40-51` (store **and** ledger, `booked_order_ids`), called `gz wp order new` `commands/wp_order.py:191` | `models/catalog.py:241`; `acceptance_package.py:65`; `order_store.py:36-37` (split); `trust_audits/catalog.py:397`, `418` (split); CLI positionals `src/gzkit/cli/parser_wp_order.py:116`, `162`, `194`, `228`, `271`; `parser_wp_tag.py:107` | `gz wp order new` `wp_order.py:221`; `gz wp order show` `:337`; `gz wp dispatch` `wp.py:723-724`; `gz wp tag issue` `wp_tag.py:109`; `gz wp runs` `wp.py:604` | **No** |
| TASK, numeric `TASK-<semver>-<NN>-<NN>-<NN>` | `TASK_ID_BODY`, `TASK_ID_BODY_PLAIN` (`core/models.py:72-77`) | `derive_req_task_id` `src/gzkit/tasks.py:189-207` → `compose_task_id` `core/models.py:214-216` (`gz task start`) | `tasks.py:39`, `253`, `266`, `322`; `core/models.py:147`, `545` (`TaskId`) | `gz task list` `src/gzkit/commands/task.py:349-354`, `397`; commit trailers | **Yes**, `IdKind.TASK`; resolves only when a `task_started` row names it (`id_resolver.py:229-235`) |
| TASK, slug `TASK-<slug>[-#<ghi>]` | `TASK_SLUG_ID_BODY` (`core/models.py:79`) | not minted: authored by hand in a `Task:` trailer | `tasks.py:266` (`_ANY_TASK_TRAILER_RE`) | commit trailers only | Classified `TASK` by `id_kind`, but **never resolves** (no `task_started` row); `TaskId` rejects it |
| ADR `ADR-x.y.z-<slug>`, `ADR-pool.<slug>` | `ADR_*_BODY` (`core/models.py:32-60`), `ADR_FRONTMATTER_ID_PATTERN` (`:82`) | `compose_adr_full_id` via `src/gzkit/commands/plan.py:116` and `src/gzkit/commands/adr_promote.py:169`; `compose_pool_adr_id` via `src/gzkit/commands/adr_demote.py:356` and `src/gzkit/foundation/sunset_migrate.py:392`, `667`, `722` | `core/models.py:120`, `148-149`, `352`, `483`; `ledger.py:83-100` | `gz status`, `gz adr status` (e.g. `src/gzkit/commands/status_render.py:373`) | **Yes**, `IdKind.ADR`, with renames (A3) and prefix expansion (A4) |
| OBPI `OBPI-x.y.z-NN-<slug>` | `OBPI_*_BODY` (`core/models.py:35-48`), `OBPI_FRONTMATTER_ID_PATTERN` (`:83`) | `compose_obpi_id` via `src/gzkit/commands/specify_cmd.py:675` | `core/models.py:145`, `377`, `504`; `tasks.py:321` | `gz obpi …` (e.g. `src/gzkit/commands/obpi_cmd.py:135-137`) | **Yes**, `IdKind.OBPI`, with A3 and A4 |
| Tag `TAG-<NN>-<slug>` | `TAG_ID_PATTERN` (`events.py:1889`), `SLUG_PATTERN` (`:1887`) | `next_tag_id` `src/gzkit/mx/tag_out.py:159-169` → `next_series_id` `src/gzkit/mx/series.py:17-33` (ledger history) | slug `tag_out.py:102`; `series.py:27`; event fields `events.py:2043`, `2137`, `2171`, `2212`, `2247`, `2325`, `2356`; CLI `--tag` `src/gzkit/cli/parser_wp_discrepancy.py:143`, `180` | `gz wp tag issue` `src/gzkit/commands/wp_tag.py:109`; hang `:146`; clearance `:183-187`; log `:362-366`; order accept `wp_order.py:309` | **No** |
| Maintenance-record entry `ENT-<NN>-<slug>` | `ENTRY_ID_PATTERN` (`events.py:1891`) | `next_entry_id` `src/gzkit/mx/entries.py:250-260` → `series.py` | slug `entries.py:60`; commit-subject citation `entries.py:62`, read by `src/gzkit/mx/git_commits.py:94`; events `events.py:2284`, `2353`; CLI `--entry` `parser_wp_discrepancy.py:177` | `gz wp entry book` `src/gzkit/commands/wp_entry.py:90-92`; `gz wp entry show` `:145-148` | **No** |
| Discrepancy `DSC-<NN>-<slug>` | `DISCREPANCY_ID_PATTERN` (`events.py:1893`) | `next_discrepancy_id` `src/gzkit/mx/discrepancies.py:125-132` → `series.py` | slug `discrepancies.py:57`; events `events.py:2046`, `2314`, `2348` | `gz wp discrepancy record` `src/gzkit/commands/wp_discrepancy.py:170`; clear `:223` | **No** |
| Dispatch `D-<16 hex>` | `DISPATCH_ID_PATTERN = "D-[0-9a-f]{16}"` (`events.py:1885`) | `f"D-{secrets.token_hex(8)}"` `src/gzkit/work_package_run.py:630` (`record_work_package_dispatch`) | prompt line `work_package_run.py:108-111` (`GZKIT-DISPATCH: `); events `events.py:1916`, `1940`, `1962`, `1978`, `2173`, `2217`, `2251`, `2254`, `2288`, `2329` | `gz wp dispatch` `wp.py:723-727` and its `dispatch_line` | **No** |
| `RP-n` | none | none (prose) | none | none (prose; contract, specifications) | No. **RULED** to resolve (2026-11-03, *"A"*), **UNBUILT** (#1302) |
| `RO-n` | none | stored once as an A1 alias | none | GitHub comment via `package_mark` | No. Same ruling; **UNBUILT** |
| `O1`-`O9` | `ORDER_ALIAS_PATTERN` would admit | none stored | none | none | No |
| `WO-n` | none | none | none | none | No (retired 2026-10-16) |
| Return to service package | none | none | none | none | No. **UNBUILT** (T6) |
| Feature package | none | none | none | none | No. **UNBUILT** (T7) |

Identifiers found that the draft's §§ 2-4 do not list:

| Identifier | Where | Via IdKind? |
|---|---|---|
| Evidence `EV-x.y.z-NN-SSS` | `EvidenceId` `core/models.py:559-578`, in `IDENTITY_MODELS` (`:581-587`) beside the four kinds | **No**: `IDENTITY_MODELS` has five entries, `IdKind` four |
| Constitution `CONSTITUTION-<UPPER>-<semver>` | pattern `core/models.py:413`; minted `init_cmd.py:1686-` | No |
| MX session id (UUID4) | minted `mx_cmd.py:335`; carried as `session_id` / `mx_session_id` / `issued_by_session` / `authorized_by_session` | No |
| Landing id `landing-<stamp>-<8 hex>` | `src/gzkit/content/landing.py:160` | No |
| Pipeline nonce (32 hex) | `src/gzkit/pipeline_markers.py:349`; `events.py:630` | No |
| ARB receipt ids `arb-…` | e.g. `src/gzkit/commands/obpi_complete.py:329` | No |

### 3a. What the census sizes for T9

- **The seam governs the legacy four and the catalog REQ; nothing of the drydock.** Of the 22 identifier rows
  in the census table, `IdKind` classifies five (ADR, OBPI, catalog REQ, legacy REQ, numeric TASK) plus
  slug TASK, which it classifies but cannot resolve. WP, ORD, TAG, ENT, DSC, D-, outcome, family, PRD
  and every short name fall outside it. The draft's § 2 line *"No work, repair or drydock identifier
  resolves through it"* is right for WP and ORD but misses that a **repair REQ** (`REQ-<n>`,
  `specialization: repair`) does resolve through it, with its `WP-` package as parent.
- **The seam's witness cannot see the drydock grammars.** `gz validate --id-seam` scans for grammar copies
  of the `IdKind` kinds only (`src/gzkit/governance/trust_audits/id_seam.py:73-76`, `_KINDS` built from
  `IdKind`), and its baseline `data/id_seam_baseline.json` holds **0** sites. Grammar copies of the drydock
  ids sit outside any witness: `WP-` in `acceptance_package.py:55`, `airlock.py:89`, three
  `split("-")[1]` parsers; `ORD-` in `acceptance_package.py:65`, `order_store.py:37`,
  `trust_audits/catalog.py:418`; the `TAG/ENT/DSC` prefix strings passed to `next_series_id`.
- **Three grammar homes.** `core/models.py` (legacy four, catalog REQ, PRD, constitution, EV),
  `models/catalog.py` (WP, ORD, order alias, outcome, family), `events.py` (TAG, ENT, DSC, D-, slug).
- **Two slug grammars and two width rules.** `SLUG_BODY = [a-z0-9-]+` (`core/models.py:29`, admits a
  leading, trailing or doubled hyphen) against `SLUG_PATTERN = [a-z0-9]+(-[a-z0-9]+)*` (`events.py:1887`),
  which `WORK_PACKAGE_ID_PATTERN` and `ORDER_ID_PATTERN` spell again inline rather than import. The seam
  pins item width at exactly two digits (`ITEM_BODY = \d{2}`, `core/models.py:30`); every drydock id takes
  `[0-9]{2,}`. `TASK_SLUG_ID_BODY` is a third slug form (`[a-z][a-z0-9-]*`).
- **Three mint policies.** WP from the store alone (`work_package_store.py:24-32`); ORD from store and
  ledger (`order_store.py:40-51`); TAG, ENT, DSC from ledger history, voided rows included
  (`mx/series.py`); catalog REQ from store and ledger (`req_store.py:36-48`). See C3.
- **No id spells its parent.** WP, ORD, TAG, ENT, DSC and D- carry no parent in their spelling, as
  requirements model § 2 rules (*"Codes are never derived into parentage"*); the legacy four still do, and
  `spelled_parent` (`core/models.py:280-293`) remains their marked fallback.
- **Sizing.** A single seam covering § 2-4 would add at least these kinds to `IdKind`: WP, ORD, TAG, ENT,
  DSC, D (dispatch), outcome, family, PRD, plus an alias kind or resolution for `RP-n`/`RO-n` and order
  aliases; capability, feature package and return to service package have no grammar to move. The
  grammar constants to move: 9 (`WORK_PACKAGE_ID_PATTERN`, `ORDER_ID_PATTERN`, `ORDER_ALIAS_PATTERN`,
  `OUTCOME_CODE_PATTERN`, the family pattern, `TAG_ID_PATTERN`, `ENTRY_ID_PATTERN`,
  `DISCREPANCY_ID_PATTERN`, `DISPATCH_ID_PATTERN`) plus `SLUG_PATTERN`. Mint functions: 6
  (`next_id`, `next_order_id`, `next_series_id` and its three callers, the dispatch mint). Unwitnessed
  parse sites found: at least 9 (listed above). Resolution today for every drydock id is an exact-string
  match in its own module.

## Contradictions

- **C1. RO-n / RP-n resolution: ruled, unbuilt.** Ruled: RO-5 ruling 6 (*"A"*), *"the drydock's `RO-n`
  names stay as aliases resolved through RO-2's identity seam"* (`docs/governance/harbor-ro5-work-packages.md:29`);
  operator 2026-11-03, *"A"*, *"`RO-n` staying an alias through the identity seam"*
  (`docs/rnd/repair-work-organization.md:400`). Code: `aliases: tuple[str, ...] = Field(..., description="Drydock
  names such as `RO-9`.")` (`src/gzkit/models/catalog.py:212`), with no grammar and no resolver; `class IdKind`
  has `ADR, OBPI, REQ, TASK` only (`src/gzkit/core/models.py:86-92`). GHI #1302 is open on it, and its cited
  line numbers have gone stale.
- **C2. Order alias "resolves" by ruling, is never resolved in code.** RP-12 ruling 49 (*"b"*,
  2026-11-05): *"`O2` reads as the second order of its package and resolves with the package beside it"*
  (`harbor-ro12-contractor-kit.md:514`). Code: `held = next((order for order in catalog.orders if order.id ==
  order_id), None)` (`src/gzkit/commands/wp_order.py:60`); no reader takes an alias.
- **C3. The WP id series can reissue a number the ledger holds.** Code message: *"One id series: a number
  names one package, never reused (RO-5 ruling 6)."* (`src/gzkit/governance/trust_audits/catalog.py:330`), and
  requirements model § 2, *"A retired code is never reused."* (`requirements-model.md:57`). Code: `next_id`
  reads `catalog.work_packages` only (`src/gzkit/work_package_store.py:31`), unlike `next_order_id`, which adds
  *"every order id the ledger names … so an id is never reused even if the store has lost a record (ruling 52)"*
  (`order_store.py:43-44`), and `next_series_id`, which reads ledger history (ruling 176). A package dropped
  from the store would free its number while 7 ledger rows still name `WP-01-…`. Ruling 176 itself scopes
  out only the order series (*"The order series, minted from its store as well as the ledger, is not changed
  by this ruling"*, `harbor-ro12-contractor-kit.md:772`); it is silent on WP. A defect candidate: it needs a
  GHI or a ruling, and this gathering files neither.
- **C4. Tasks bind to orders by ruling, but TASK events cannot name an order.** RP-12 ruling 46 (*"b"*,
  2026-11-05): *"A task binds to its order by its own ledger events naming the order"*
  (`harbor-ro12-contractor-kit.md:507`). Code: `_TaskEventBase` requires `task_id`, `obpi_id`, `adr_id` and
  `agent`, and has no `order` field (`src/gzkit/events.py:675-681`); the TASK grammar is semver/OBPI-keyed
  or a free slug. Whether the drydock's maintenance-record entry (`entry_booked`, which does carry `order`) is
  meant as the order's action record in place of the TASK is not stated in what was read.
- **C5. Outcome codes: the ruled form is three levels and three letters; the pattern is one letter and any
  depth.** Requirements model § 2: *"`SES` is a family, `SES1` a capability, `SES1.4` an outcome, exactly
  three levels"* (operator 2026-10-29, *"A"*; `requirements-model.md:50-52`), and § 8.3 amended 2026-10-30
  to *"a fixed three letters"* (`:190-191`). Code: `OUTCOME_CODE_PATTERN = r"^[A-Z][1-9][0-9]*(\.[1-9][0-9]*)*$"`
  (`src/gzkit/models/catalog.py:40`) takes one letter and admits `H1` (a capability's shape) and `H1.4.2`
  (four levels) as outcomes. `Family.code` is `^[A-Z]$` (`:60`), and the seed shipped to adopters
  (`src/gzkit/catalog_seed.json`) holds the single letters too. Extends T8: the recode also has to reach the
  wheel's seed and the depth rule.
- **C6. The `--alias` help still says `RO-<n>`.** Code: `help="RO-<n>"` (`src/gzkit/cli/parser_wp.py:272`).
  Ruled 2026-11-03, *"A"*: *"`RP-n` replaces `RO-n` in the contract and specifications"* (the ruling covers
  live text in the contract and specifications; whether CLI help counts as live text is not stated).
- **C7. The MX open event keeps `mode: mx | safe`.** Code: `mode: Literal["mx", "safe"]`
  (`src/gzkit/events.py:1068`). The draft's § 5 and the marker: *"one state, level `hangar | drydock` (the
  marker's older `mode` `mx | safe` reads as its alias)"* (`drydock-taxonomy.md:83-84`; `mx/marker.py:80-88`).
  The marker was migrated and the ledger event was not, so the event is the one record that still writes
  the older vocabulary.
- **C8. The draft understates what the seam covers.** Draft § 2: *"No work, repair or drydock identifier
  resolves through it (T9)"* (`drydock-taxonomy.md:47-48`). Code: a repair REQ (`REQ-<n>`, `specialization:
  repair`, held on a `WP-` package) resolves as `IdKind.REQ`, with the package as its parent
  (`src/gzkit/core/id_resolver.py:209-214`, `309-310`, `366`). A narrower claim, not a reversal.
- **C9. Two identity registries disagree on the number of kinds.** `IdKind` docstring: *"The four identifier
  kinds the seam governs"* (`core/models.py:87`). `IDENTITY_MODELS` holds five, `ADR, OBPI, REQ, TASK, EV`
  (`core/models.py:581-587`). `EV-` is in neither the draft nor `IdKind`.
- **C10. The dispatch id's attribution.** Draft § 3: *"`D-<16 hex>` … `DISPATCH_ID_PATTERN`; RP-12 O1"*.
  Code: *"A dispatch id as the runtime mints it (RP-12 ruling 1)"* (`events.py:1884`), and the kit's ruling 1
  is the dispatch-record ruling (*"Dispatch record (Recommended)"*, `harbor-ro12-contractor-kit.md:426`).
  Only the citation differs (O1 is where it was built, ruling 1 is what ruled it). Minor.

## Files read in full (line counts)

| File | Lines |
|---|---|
| `docs/governance/drydock-taxonomy.md` | 149 |
| `src/gzkit/events.py` | 2488 |
| `src/gzkit/models/catalog.py` | 429 |
| `src/gzkit/core/models.py` | 754 |
| `src/gzkit/core/id_resolver.py` | 366 |
| `data/catalog/delivery_events.json` | 15 |
| `data/catalog/externals.json` | 4 |
| `data/catalog/families.json` | 71 |
| `data/catalog/orders.json` | 4 |
| `data/catalog/outcomes.json` | 4 |
| `data/catalog/reqs.json` | 4 |
| `data/catalog/work_packages.json` | 65 |
| `src/gzkit/mx/series.py` | 33 |
| `src/gzkit/work_package_github.py` | 83 |
| `src/gzkit/work_package_store.py` | 71 |
| `src/gzkit/order_store.py` | 89 |
| `src/gzkit/req_store.py` | 85 |
| GHI #1302 (`gh issue view 1302`: body; no comments) | n/a |

Read in part (named ranges only, so nothing here rests on their absence of a thing): `src/gzkit/governance/trust_audits/catalog.py`
280-430 of 666; `src/gzkit/commands/wp.py` 95-140, 545-650, 718-730 of 840; `src/gzkit/commands/wp_order.py`
45-65, 300-345 of 442; `src/gzkit/governance/trust_audits/id_seam.py` 1-120 of 430; `src/gzkit/obpi_lifecycle.py`
200-280 of 419; `src/gzkit/acceptance_package.py` 45-90 of 248; `src/gzkit/commands/airlock.py` 80-100 of 210;
`src/gzkit/catalog_seed.py` 1-40 of 64 and `catalog_seed.json` (summarized by script); `src/gzkit/ledger.py`
79-102; `src/gzkit/mx/tag_out.py` 159-169, `entries.py` 55-66 and 250-260, `discrepancies.py` 125-132,
`git_commits.py` 85-97; `src/gzkit/work_package_run.py` 100-120, 620-640; `src/gzkit/tasks.py` 189-207 and its
pattern lines; `src/gzkit/commands/init_cmd.py` 1622-1646; `src/gzkit/mx/marker.py` 78-90;
`docs/rnd/repair-work-organization.md` 70-95, 395-403, 593; `docs/governance/harbor-ro12-contractor-kit.md`
rulings 1, 5, 8, 43, 44, 46, 47, 49, 52, 111, 169, 176 (lines 426-433, 501-520, 639, 758, 772);
`docs/governance/harbor-ro5-work-packages.md` lines 29, 77-78, 94; `docs/governance/ieee/requirements-model.md`
29-33, 48-60, 186-196. Grep sweeps (string searches, not reads) located the mint and render sites and the
absence of any `RP-`/`RO-`/`WO-` grammar under `src/gzkit`. Each site cited above was then read at its lines.
