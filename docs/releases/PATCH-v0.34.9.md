# Patch Release: v0.34.9

**Date:** 2026-10-11
**Previous Version:** 0.34.8
**Tag:** v0.34.8

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 997 | eval-feedback-cluster: the chore runs fixtures, not live clustering | qualified |  |
| 1039 | skills audit: fresh audit-first import fails on circular dependency | qualified |  |
| 1154 | gate tests: negatives feed only absence; stand-in inputs pass | open_upstream | GHI #1154 qualifies on commit markers but is still OPEN upstream; confirm this release closes it before counting it |
| 1155 | enforcement floor: 9 of 12 hollow gates had no registered control | open_upstream | GHI #1155 qualifies on commit markers but is still OPEN upstream; confirm this release closes it before counting it |
| 1156 | fidelity gate: closeout demo assertions run in the live checkout | qualified |  |
| 1157 | obpi verify-packet: replay runs in and can mutate the live checkout | qualified |  |
| 1158 | stage4_evidence: uncalled validate_stage4_evidence claims to gate | qualified |  |
| 1159 | red-parity: provenance-less error erases a standing 'none' RED | qualified |  |
| 1160 | brief-reconcile: path:symbol discovery citation reads as missing path | qualified |  |
| 1161 | guard canaries: operator review is a hand-edited field, not witnessed | qualified |  |
| 1162 | citation resolver: parked phantom siblings make live OBPIs unknown | qualified |  |
| 1163 | gz obpi complete: five Step-4b flags are accepted and ignored | qualified |  |
| 1164 | verify-packet: a replay timeout hides the masked-verifier refusal | qualified |  |
| 1165 | gz check: the 900s hang bound has 6% headroom on windows-latest | qualified |  |
| 1166 | gz obpi pipeline: --no-subagents is parsed and never read | qualified |  |
| 1167 | pipeline skill: abort path prescribes a lock release that exits 3 | diff_only | GHI #1167 has commits touching src/gzkit/ but no 'runtime' label |
| 1168 | session orientation: pipeline section is hard-coded empty | excluded |  |
| 1169 | pipeline skill: precomplete step cites #196, the issue is #195 | diff_only | GHI #1169 has commits touching src/gzkit/ but no 'runtime' label |
| 1170 | gz obpi status: uncompleted OBPI reads Attestation State not_required | qualified |  |
| 1177 | tautological debt: ceiling reads the local date, so CI and local disagree | qualified |  |
| 1178 | file_lock: on Windows a contended writer fails after ten seconds | qualified |  |
| 1179 | arb red: a mutant that hangs its tests crashes the run, no receipt | qualified |  |
| 1180 | registries: non-UTF-8 registry escapes as raw UnicodeDecodeError | qualified |  |
| 1181 | obpi complete: completed receipts carry no scope_audit since June | qualified |  |
| 1182 | security registry: deserialization entry names a deleted file | label_only | GHI #1182 has 'runtime' label but no commits touching src/gzkit/ |
| 1185 | airlock-out: exit never compares changed files with Allowed Paths | open_upstream | GHI #1185 qualifies on commit markers but is still OPEN upstream; confirm this release closes it before counting it |

## Operator Approval

Approved by gz patch release
