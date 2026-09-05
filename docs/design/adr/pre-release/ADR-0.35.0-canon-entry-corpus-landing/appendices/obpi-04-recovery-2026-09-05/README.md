# OBPI-04 recovery: read first

This archive belongs to [ADR-0.35.0](../../ADR-0.35.0-canon-entry-corpus-landing.md)
and [OBPI-0.35.0-04](../../obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md).
Persona: main-session. Preserved on 2026-09-05 at the operator's direction after
Codex lost the established execution context during conversation compaction.
This is an execution bookmark, not completion evidence or human attestation.

## Resume here

1. Read [EXECUTION.md](EXECUTION.md): the existing consolidated execution path.
2. Read [contract-assessment.md](contract-assessment.md): the A1–A20 acceptance
   matrix consolidates existing obligations; it is not twenty new work items.
3. Read the current-status distinctions below before following historical advice.
4. Reconcile remaining work with the live brief, plan, source, and ledger. Continue
   the authorized correction; do not restart design or ask the operator to repeat
   settled instructions.

The operator already directed execution and subsequently authorized commit/push.
The latest direction is to retain these materials with their ADR/OBPI. No scope
split, silent durability waiver, new recovery state, or general transaction manager
was authorized. Preserve the accepted ledger exceptions and the existing threat
boundary. Completion still requires the proper review and human attestation.

## Latest continuation

Read [final verification in progress](final/README.md) for the subsequent source,
mutation, and verification results. The dated preservation record below remains historical.

## Status at preservation

- Git HEAD was `18454c9066d54c8d14f61c5e43ff3241a45ee757`. Four production/test
  files had subsequent uncommitted changes; their exact hashes are recorded in
  [archive-manifest.json](archive-manifest.json). This archive does not validate
  those changes or record another commit.
- The historical assessments preceded the integrated lifecycle fixes. Their
  instructions to repair enumeration, preserve recovery material on unavailable
  barriers, strengthen parent-directory proof, and correct recovery advice must
  be reconciled against the existing changes rather than implemented again.
- [CORRECTION.md](CORRECTION.md) reports the first integration. Its statement
  that Codex had made no commit is historical and superseded by the HEAD above.
- [Full-check output](evidence.zip) records the earlier
  59-check pass. [Full-suite output](evidence.zip)
  records 9,406 tests passing. Both precede the final Windows implementation;
  neither establishes the final tree's acceptance.
- The standalone Windows capability probe succeeded in
  [run 33972482837](https://github.com/tvproductions/gzkit/actions/runs/33972482837).
  Its [captured log](evidence.zip) is retained.
  [Windows implementation notes](windows-native-implementation.md) explicitly
  distinguish that probe from the production implementation, which still requires
  real Windows integration verification. A native API result is not a physical
  power-cut experiment.
- The latest landed-recovery diagnostic has an observed
  [RED](evidence.zip) and
  [five-test GREEN](evidence.zip).
- [Mutation evidence](mutation-sweep/README.md) retains a 36-case manifest and
  representative results. The complete final-revision sweep has not run. Missing
  historical mutation targets are disclosed, not reconstructed by assertion.
- The standing independent-review verdict in the brief remains refuted. These
  reports do not replace a fresh acceptance review or permit completion.

## Remaining execution

1. Review the native Windows implementation and coupled documentation, then run
   the production tests on Windows using the already authorized repository workflow.
2. Retain final evidence and remove the temporary capability-probe workflow.
3. Bind the mutation manifest and required demonstrations to the final source;
   run the required quality checks and independent acceptance review.
4. Present verified evidence for human attestation, then finish governed accounting.

Use `UV_CACHE_DIR=/tmp/gzkit-health-uv-cache` and
`UV_TOOL_DIR=/tmp/gzkit-health-uv-tools` with `uv run` in this sandbox. The earlier
module-size failures were tool-directory access failures, not source defects.
Codex-primary versus Claude-primary reviewer attribution remains explicit: do not
call a Codex reviewer cross-vendor relative to Codex or fabricate fallback status.

## Historical record and supporting evidence

- [Identity justification](gzkit-obpi-04-identity-justify.md)
- [Consolidated justification](justification.md)
- [Protocol assessment](protocol-assessment.md)
- [Test evidence assessment](test-evidence.md)
- [Platform finding](PLATFORM-FINDING.md)
- [Correction evidence](correction-evidence.md),
  [spec review](correction-spec-review.md), and
  [quality review](correction-quality-review.md)
- [Diagnostic runner explanation](recovery-contract-runner.md)

Original files were copied byte for byte. The manifest inventories every retained
report, script, patch, log, and result with its original location and SHA-256.
All 131 originals are retained in [evidence.zip](evidence.zip); Markdown reports
are also directly readable here. Unzip the bundle into a fresh directory to
restore the original relative layout. Scripts are archived as evidence, not
introduced into the production source or test-discovery tree.
Temporary checkout trees, environments, bytecode, and the temporary Git index were
not copied. Recorded absolute temporary paths, snapshot line numbers, commands,
and old status claims remain historical provenance; they are not portable commands
or current source references. Use the local archive links and manifest to find
retained artifacts. Recreate a needed historical checkout from its recorded base
and patch rather than relying on the original temporary directory surviving.

The current brief and booked rulings govern; historical assessment prose cannot
silently change them. Do not turn this archive's presence into proof that any gate
ran. The associated checkpoint is linked from the OBPI brief.

Canonical checkpoint: `.gzkit/handoffs/20260905T154223Z-obpi-04-durable-recovery-context.md`.
