# Patch Release: v0.34.1

**Date:** 2026-08-04
**Previous Version:** 0.34.0
**Tag:** v0.34.0

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 582 | subprocess: text-mode reads lack errors=, crash on non-UTF-8 output | qualified |  |
| 615 | schema: structured governance docs regex-scraped, not schema-enforced (briefs 597/600 bypass BriefStructure) | qualified |  |
| 650 | mx: agent-facing marker path (.gzkit/mx-active) drifts from code (.gzkit/mx.json) | qualified |  |
| 728 | chores: sync and init export project-local slugs to adopters | qualified |  |
| 730 | tautological-tests: @covers decorator satisfies the production-code exemption (217 of 290 ops masked) | qualified |  |
| 731 | task-envelope Signature (c): layer-drift gate compares 6 of 776 OBPIs (two channels always empty) | qualified |  |
| 732 | handoff-resume-gate: git read allowlist omits rev-list (3rd narrow miss) | qualified |  |
| 734 | register_adr_in_ledger: third adr_created ingress bypasses the foundation membrane | qualified |  |
| 735 | parse_frontmatter_value: a leading BOM silently hides the whole frontmatter block | qualified |  |
| 736 | frontmatter ingress: three ad-hoc decoders disagree; no shared tri-state reader | qualified |  |
| 738 | closeout-walkthrough: demo discovery cannot surface refusal/negative demos | qualified |  |
| 739 | closeout: minor-release ceremony deadlocks on the rule-11 tag audit | qualified |  |
| 740 | taxonomy: foundation closure is framework-wide, not project-local as decided | qualified |  |
| 741 | adr template: {persona} renders as literal text; no validator enforces ## Persona | qualified |  |
| 742 | validate --documents: no-frontmatter ADRs are silently exempt, not validated | qualified |  |
| 743 | chores: acceptance criteria don't gate the chore's own subject | qualified |  |
| 744 | gz check: registering a validate scope does not enroll it in the gate | qualified |  |
| 745 | cli-alignment: fenced code blocks escape all three verb detectors | qualified |  |
| 746 | invariant-witness: validator function has no CLI wiring; prose claims a flag that never existed | qualified |  |
| 748 | cli-alignment reimplements a weaker verb extractor than obpi.py already ships | qualified |  |
| 749 | GovZero runbook documents a gz superbook bridge that has never existed | qualified |  |
| 750 | doctrine: GPT-5.6 System Card evidence not yet incorporated | diff_only | GHI #750 has commits touching src/gzkit/ but no 'runtime' label |
| 752 | task-envelope: two of four discovery channels structurally unused (Signature (c) compares 7 of 534) | qualified |  |
| 753 | task-envelope: tasks: channel has no schema enforcement; the deferral names an OBPI that never scoped it | qualified |  |

## Operator Approval

Approved by gz patch release
