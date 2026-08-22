---
id: mx-mode
description: >
  Binding rule for MX hangar sessions — honor the marker, PRIME DIRECTIVE
  binds the whole session (ADR-0.0.74 Decision item #8).
paths:
  - "src/gzkit/mx/**"
  - ".gzkit/skills/gz-mx/**"
  - ".claude/hooks/mx-awareness.py"
  - "src/gzkit/mx/awareness.py"
  - "src/gzkit/hooks/guards.py"
---
<!-- rule-version: 1.3.0 -->

# MX Mode (Maintenance Hangar) (gzkit)

> **Rule version:** `1.3.0` — adds § Opting a guard into the floor, which names the two opt-in mechanisms and the choice between them. `1.2.0` said only that *"a new guard inherits demotion by default and must opt into the floor explicitly"* and never said HOW — while `checkpoint.resolve` offers two routes that differ in reversibility: NAME (`GATE5_INVARIANTS` membership, a Boundary Invariant #3 one-way door, forbidden for a narrower proxy per § Consequences/Negative #7) and LEVEL (emit CRITICAL, reversible). Measured 2026-08-22 against `_GUARD_META`: four of six pre-commit guards survive an open hangar and they do it BOTH ways — `ledger` and `gate5-attestation` by name, `post-authoring-src-commits` and `enforcement-floor` by level — so the roster could not be read without tracing the resolver. The reasoning existed and was correct; it lived in a commit body. `84519da5` (GHI #852) derived it at fix time and recorded it there, which is the settled-twice-recorded-nowhere shape `governance-core.md` `0.13.0` names: both wrong answers are locally plausible, so re-deriving it is a coin flip rather than a delay. Also records the operator ruling of 2026-08-22 that the Stage-2 production-code fence's pin is permanent (GHI #855), and that an unregistered guard name resolves CRITICAL rather than advisory. Prior `1.2.0` — § Honor the marker now names BOTH enforcement surfaces, and
> `paths:` reaches the second one. The clause said "most guards drop to advisory" without
> qualification while the demotion reached only `gz validate` scopes and the `gz check` step
> layer; the pre-commit guards in `src/gzkit/hooks/guards.py` each self-decided fatality with a
> bare `return 1`, which is verbatim the "named coverage defect" of ADR-0.0.74 BI#2. Measured
> 2026-08-22: **zero** checkpoint consumers anywhere under `src/gzkit/hooks/`, so an open hangar
> had no authority over one of the two surfaces governance is enforced on — while `gz mx --help`
> advertised the hangar so "the operator can repair governance itself" and offered
> `gz mx enter --reason "repair ledger"` as its worked example. Third recurrence of one class:
> GHI #638 (the `gz check` step layer), GHI #651 (the enforcement floor demoting inside the
> hangar), now GHI #843. The root is an inventory gap ADR-0.0.74 Negative #6 predicted in its own
> words — *"a funnel that forgets it silently stays hard"* — because the funnel inventory
> OBPI-0.0.74-02 shipped enumerates `validate_cmd` and nothing else. Closed by GHI #843: one seam
> over one registered inventory in `guards.py`, fenced by
> `tests/test_hooks_guards.py::TestMxCheckpointSeam`, which fails when a `forbid_*` guard is added
> without a checkpoint entry. Prior `1.1.0` — Movement C family closure, rules arm: § Honor the marker now
> names the mechanical witness it has had since OBPI-0.0.74-17/-20. The scorecard scored this
> clause **Promotable** on the premise that "the marker-check is structural (file exists/not)"
> and liveness was advisory — a description of the rule's state *before* `checkpoint.resolve`,
> `disposition`, and 45 covering tests across five modules landed. Nothing was built to close
> this row; the score had simply not been revisited when its own mechanism arrived, which is
> how a Promotable row outlives the reason it was Promotable. Re-scored **Mechanical** at
> `docs/governance/advisory-rules-audit.md` row 62. Prior `1.0.1` — marker path aligned to
> `.gzkit/mx.json`; `e2d38c3c0` bumped the
> HTML marker only (GHI #650). Prior `1.0.0` — initial authoring under ADR-0.0.74 (OBPI-0.0.74-08).

## Non-negotiable rules

### Honor the marker

- Honor the marker: when `.gzkit/mx.json` exists, most guards drop to advisory

Before every action in a session where `.gzkit/mx.json` exists, confirm the
hangar is open. When the marker is present:

- `gate5_invariants` remain **fail-closed**. Gate 5 is never advisory.
- **Both enforcement surfaces honor the marker (GHI #843).** Governance is enforced on two
  surfaces, and the hangar reaches both: `gz validate` scopes plus the `gz check` step layer,
  and the pre-commit guards (`gzkit.hooks.guards`). A demoted pre-commit finding is still
  printed, followed by an `[MX advisory]` line — advisory means non-grounding, never discarded.
- **Demotion never reaches an integrity guard, on either surface.** `ledger` and
  `gate5-attestation` are `GATE5_INVARIANTS` members, so a hand-edit of `.gzkit/ledger.jsonl`
  and an unattested OBPI-completion commit are refused *inside* the hangar exactly as outside
  it. The hangar is therefore not the route out of a mis-ordered ledger; that route is an
  append-only corrective-action primitive (GHI #611), never a demoted guard.
- The MX awareness hook fires every turn to remind the agent of the open state.

### Opting a guard into the floor — two mechanisms, not interchangeable

A guard inherits demotion by default. There are exactly **two** ways to survive an open hangar, and `gzkit.mx.checkpoint.resolve` is the whole decision:

- **By NAME** — membership in `GATE5_INVARIANTS` (`src/gzkit/mx/invariants.py`). Pins CRITICAL in and out of the hangar (Boundary Invariant #3). This is a **one-way door**, and it is **forbidden when the guard is a narrower proxy for the floor concern** — ADR-0.0.74 § Consequences/Negative #7: *"it MUST NEVER bind a narrower proxy entrypoint and call the claim proved."*
- **By LEVEL** — emit `CRITICAL`. Reversible, leaves `GATE5_INVARIANTS` untouched. This is the route for a guard that must never demote but is not itself a Gate-5 invariant.

**Default to LEVEL.** Reach for NAME only when the guard enforces the floor concern *in full*, not a checkable slice of it. Worked precedent: `84519da5` (GHI #852) pinned the authorship guard by LEVEL rather than registering it as `operator-pii`, because an email-suffix check on the git identity does not cover the whole operator-PII prohibition — which also spans trailers, file content, attestation text, and the ledger.

Floor-pinned by LEVEL today: `post-authoring-src-commits` (the Stage-2 production-code fence) and `enforcement-floor`. The Stage-2 fence's pin was ruled permanent by the operator 2026-08-22 — an open hangar never demotes it (GHI #855).

**An unregistered guard name resolves CRITICAL, not advisory** — a name nothing declares is a name nothing vouched for (`84519da5`).

**This clause carries a mechanical witness — it is not authoring discipline.**
Demotion is decided in `gzkit.mx.checkpoint.resolve` / `gzkit.mx.disposition`,
and asserted by `tests/mx/test_checkpoint.py`, `test_disposition.py`,
`test_gate5_invariants.py`, `test_check_step_checkpoint_seam.py`, plus the live
un-forced negative controls in `test_gate5_invariants_live_nc.py`
(OBPI-0.0.74-17, REQ-0.0.74-20-03). Both directions are pinned: every
`gate5_invariants` member stays fatal *under* the marker, and stays fatal
*outside* it, so the carve-out cannot silently invert. A new guard inherits
demotion by default and must opt into the floor explicitly.

### PRIME DIRECTIVE binds the entire session

Guards dropping to advisory means the operator can repair the surfaces the
guards protect — it does NOT mean ownership relaxes. In the hangar:

- Fix what you know **AND** what you find.
- "Not my work" / "out of scope" stays **forbidden in the bay**.
- Defects visible in flight are still defects; advisory guards are not a
  license to defer them.

### Operate the skill, not the shell

The operator uses the `gz-mx` skill; the skill invokes `gz mx`; agents do not
shell out to `gz mx enter` or `gz mx exit` directly.

## Do Not

- Do not invoke `gz mx enter` or `gz mx exit` directly in a shell step — use the `gz-mx` skill
- Do not treat advisory guards as license to defer visible defects
- Do not conflate "guard dropped to advisory" with "PRIME DIRECTIVE suspended"
- Do not exit the hangar while any detectable defect remains unfixed

## Related

- `gz-mx` skill — the operator's interface (`.gzkit/skills/gz-mx/SKILL.md`)
- MX awareness hook — per-turn reminder (`.claude/hooks/mx-awareness.py`)
- Parent ADR — `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/`
