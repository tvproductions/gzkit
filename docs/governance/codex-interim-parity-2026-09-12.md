# Codex interim parity — 2026-09-12

Operator: g0. Request: “special mission: get me codex parity. is there an adr for
it? can you do best effort parity until we can get to that adr?”

## Ownership and disposition

[ADR-pool.vendor-alignment-codex](../design/adr/pool/ADR-pool.vendor-alignment-codex.md)
owns full Codex alignment. Formerly numbered ADR-0.44.0, it was returned to pool
with its six children parked. The campaign's August 8 ruling preserves the
implemented Codex surface while retiring the unsanctioned decomposition. This
repair improves that retained delivery under the operator's present request;
it does not promote the pool, initiate OBPI work, or change campaign sequencing.

## Delivered repair

| Surface | Repair | Authority |
|---|---|---|
| Session orientation | Native matcher/handler registration; startup, resume, clear, compact | Existing `scripts/session_orientation.py`, including the four workflow fronts |
| Handoff advisement | Native SessionStart context adapter, bounded by the shared advisement budget | `gzkit.session_start.build_advisement`; advises without authorizing work |
| Verification control | Native PreToolUse shell adapter returns supported deny JSON for masked verifier exits | `gzkit.verifier_pipe_gate.decide`; no duplicate policy predicate |
| Role instructions | Five canonical role bodies render into native Codex TOML; implementer and both reviewers gain missing witnessed-RED and review requirements | `.gzkit/agents/roles.json` and Markdown bodies, with capture provenance |
| Recovery | Normal control-surface sync recreates hooks and registered roles; capture planning stays read-only | `gzkit.hooks.codex`, `gzkit.codex_roles`, shared surface-write sink |
| Validation | Orientation check rejects obsolete command arrays and matchers that omit required session starts | Existing `--orientation-freshness`; generated surfaces participate in `--surfaces` |

The single root AGENTS.md, existing document cap, model choices, sandbox policy,
skills, and personas retain their existing delivery. Native role metadata and
unrelated operator hooks are preserved. Hook status labels identify owned
handlers; unmarked custom role bodies remain user-owned. Claude role content is
unchanged, with a coherence test against the captured canonical bodies.

## Runtime evidence and activation

Installed runtime: `codex-cli 0.154.0`. The app-server `config/read` probe confirms
that the project `.codex` layer is active. Before repair, `hooks/list` returned
zero project hooks despite the existing orientation file. After repair it
recognizes all three project handlers without project configuration errors.
Each is enabled and `untrusted`, awaiting native review.

The native instruction-delivery witness also reports all 48,511 bytes of root
AGENTS.md delivered, against the preserved 65,536-byte cap. That check required
running the read-only Codex probe outside this session's filesystem sandbox;
the sandboxed attempt was correctly reported as unobserved.

Direct execution of the generated commands from the repository's `src/`
directory returned exit 0 for all three: orientation emitted 19,505 bytes and
included the workflow fronts; handoff advisement emitted 1,114 context characters;
the masked-verifier payload returned native `permissionDecision: deny` JSON.
The unit tests also verify ordinary commands and exit-preserving pipelines are
allowed, so the guard is not an unconditional denial.

Verification: 343 relevant unit tests pass; the seven scoped validators
(`surfaces`, `invariant_coherence`, `cli_alignment`, `skill_alignment`,
`insights_shape`, `orientation_freshness`, `distribution`) pass; strict MkDocs
build passes. Independent review caught the matcher-coverage gap, now covered by
failing-before/fixed-after tests. The mission also reproduced and repaired a
skill mirror copy that bypassed the capture sink: previews now record that copy
without changing its bytes, mtimes, or directory inventory.

Codex requires review and trust of each exact hook definition before automatic
execution. Review the project definitions using `/hooks`, then reopen or resume
the task to observe orientation and handoff context. Registration and direct
handler execution are separate evidence from trusted lifecycle dispatch; this
repair does not claim the latter without observing it. No hook-trust bypass is
used. The inspection process starts no model task and uses temporary SQLite state.

The native shape and payload contract were checked against the installed runtime
and [official Codex hooks documentation](https://learn.chatgpt.com/docs/hooks).
Native shell hooks use canonical `Bash` and `tool_input.command`; the adapter
also accepts raw unified-exec `cmd` arguments. Both SessionStart handlers may run
concurrently because neither depends on the other's effects.

## Remaining full-parity work

The pool still owns comprehensive lifecycle coverage, file-edit adapters,
ExitPlanMode substitutes, and harness-neutral pipeline plan/state authority.
The existing Claude Stop/transcript and SessionEnd adapters have not been copied
blindly: Codex transcript semantics and the native exit-time budget need their own
behavioral evidence. This repair supplies no automatic OBPI initiation and does
not claim Claude's whole hook catalog is active in Codex.

## Four-front placement

- **Handoff:** carry this record and pending native hook review into the next session.
- **GHI triage:** treat defects in retained Codex delivery as direct repairs; this
  mission does not create an issue solely to manufacture ceremony.
- **ADR/OBPI campaign:** keep the pool in its governed order; interim delivery is
  not evidence that its parked decomposition has been completed.
- **R&D:** evaluate unsupported lifecycle and transcript mappings against current
  native capabilities when the full alignment work is drawn.
