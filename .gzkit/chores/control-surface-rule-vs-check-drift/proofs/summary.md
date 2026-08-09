# Pass C Summary — Rule Prose vs. Promoted Check Drift

> Chore: `control-surface-rule-vs-check-drift` (Lite lane, audit-only)
> Date: **2026-08-09** (prior run: 2026-08-01)
> Inputs: `promoted-inventory.md`, `prose-assertions.md`, `check-behaviors.md`, `parity-diff.md`
> Trigger: `scripts/check_proof_freshness.py` failed closed — both audited surfaces
> moved: `.gzkit/rules` (18 files) and `src/gzkit/governance/trust_audits`
> (13 files, **+1951 lines**).

Method: three independent readers plus a first-party verification pass. Every
`file:line` in the parity ledger was re-opened; no line number was copied forward.

## Counts

| Measure | 2026-08-01 | **2026-08-09** |
|---|---|---|
| Registered validator scopes | — | **89** |
| Promoted (rule, scope) pairs | — | **44** |
| Prior rows accounted for | — | **43 of 43** |
| `carried` | — | 35 |
| `closed` | — | 6 |
| `refuted` | — | 1 |
| `not re-verified` (recorded, not dropped) | — | 1 |

## Headline 1: the drift class is exit-code contracts, and it has five instances

Four carried rows and one new one, all the same shape — a surface claims exit 3
(Policy Breach) and the code exits 1:

| Scope | Claim | Reality |
|---|---|---|
| `--cli-alignment` | `governance-core.md:53` *"Exit 3 on any unresolvable reference"* | `type="cli_alignment"` not in `_POLICY_BREACH_ERROR_TYPES` → exit 1 |
| `--brief-headings` | manpage *"Exits 3"* | not in the breach set → exit 1 |
| `--changelog` | rule *"fails closed"* | not in the breach set → exit 1 |
| `gz cli audit` | `cli.md` names it a *"Mechanical check"* under a map where 3 = Policy Breach | `cli_audit.py:243` — exit 1, the module's only non-zero exit |
| **`--transcribed-adr-counts`** *(new this run)* | flag help *"Exit 3 on any (#768)"*, **and it IS registered** at `validate_cmd.py:1153` | emits `type="surface"` (`transcribed_counts.py:165, :182`), which is not in the set → **the registration matches nothing** |

The last one inverts the others: the rule is right, the registration is right, and
they never meet because the emitted `type` string is a third, unchecked fact.

## Headline 2: the audit caught a false claim this session authored

Scorecard row **17e** — added hours earlier under `1c36e0c4b` — asserted
*"exit 3 on any unresolvable reference"* for `--cli-alignment`, copied from the
rule rather than read from the code. Corrected in place, with the correction
recorded in the row rather than silently applied.

**Why this matters beyond the one row:** the scorecard has an arm built for exactly
this class — `_missing_witness_path_errors` (`release.py:463-552`), which fails a
**Mechanical** row citing a witness path that does not exist. Row 17e cited a real
flag, a real module, and a real registration. **Every path resolved. The behavior
claim was still false.** A presence check cannot verify behavior, and this chore is
the only surface in the repository that reads the implementation instead of the
claim.

## Headline 3: 54 of 89 registered scopes bind no rule

The scorecard answers *"is this rule enforced?"*. The inverse — *"does this
enforcement correspond to a rule?"* — has no owner. **All five scopes registered
since the last audit landed with zero scorecard citations**: `--pool-interview`,
`--invariant-witness`, `--transcribed-adr-counts`, `--status-writer-coverage`, and
the renamed `--lock-exchange-coupling`. Four of the five shipped in v0.34.2.

A validator can be built, registered, wired into `gz check`, and released without
any surface recording which rule it enforces.

## The pattern: assertion rots, disclosure does not

Sorting the 43 rows by what the prose *does* rather than what it says:

| Prose shape | Rows | Drift |
|---|---|---|
| **Asserts** a mechanism (flag, exit code, scope, "enforced by") | 19 | all 19 drifted |
| **Points at** a gate by flag name only | — | breaks loudly when the flag is renamed |
| **Discloses** it has no gate | 6 | **zero drift, ever** |

Every `parity` verdict belongs to a rule that discloses its posture or names its
mechanism precisely. Every `prose-wider` verdict belongs to a rule that described a
gate's *behavior* in prose. Nothing re-reads that prose when the gate moves.

This is the same conclusion the Pass A walk reached independently the same day, by
a different route. Two audits, different subjects, one finding.

## Six rows closed — what fixing this looks like

`P1` (`08289b87f`), `P2` (`7290bde62`, GHI #746), `S0` and `S1` (`0f671b31c`,
GHI #744), `M1` (GHI #588/#748), `M7` (GHI #754). Re-derived at `S0`: **52 check
steps** (was 47), **88 registered scopes**, and **zero of 13 default-tier scopes
now unreachable** — the gap that let a real marker mismatch survive eight days of
green commits is closed.

Five of the six were closed by shipping a *mechanism*, not by editing prose.

## One row refuted, and it is a lesson about this ledger

Row **=4** was scored `parity` at the prior run. Re-reading found `AGENTS.md:360`
claims `--invariant-coherence` *"re-renders the registry and byte-compares"*, while
`render_agents_md` (`compose.py:8-30`) *"loads the committed rendition … and returns
its bytes verbatim"*. The registry-render parameters were deleted in `4f9c7d2bd`
(GHI #623) **two weeks before the prior ledger was written**.

The prior run scored the byte-compare and scope halves, both true, and did not read
the mechanism clause. **A row can be `parity` on the parts examined and wrong
overall** — which is why the accounting commitment requires re-opening every
citation rather than confirming a verdict.

## Known incompleteness

Row **M6** (`model_config` presence checked, contents not) could not be re-verified
— the expected module path returned no match this run. It is recorded as
`not re-verified`, **not** as carried or closed. An unverified row is not a clean
one, and the stability commitment forbids it disappearing quietly. Next run: locate
the `--pydantic-models` implementation and give it a verdict.

## Prioritized follow-up

Operator canon: a GHI-tracked repair routes to direct fix.

| # | Route | Target | Fix | Rows |
|---|---|---|---|---|
| 1 | direct-fix | `src/gzkit/governance/trust_audits/transcribed_counts.py` | Emit `type="transcribed_adr_counts"` so the existing policy-breach registration binds. **One string.** | new |
| 2 | direct-fix | `.gzkit/rules/governance-core.md:53`, `cli.md`, `changelog-release-notes.md`, manpage | Correct four exit-3 claims to exit 1 — **or** add the four types to `_POLICY_BREACH_ERROR_TYPES` if 3 is the intent. **Rule the direction once, apply to all four.** | M2, M4, M5, M15 |
| 3 | direct-fix | `quality.py` step list | Give `--cli-alignment` and `--commit-trailers` real `gz check` steps. Four rules name `--commit-trailers` as the enforcer; it runs in no gate an operator or CI executes. | S2, S3 |
| 4 | direct-fix | `AGENTS.md:360` | Drop the *"re-renders the registry"* clause — stale since `4f9c7d2bd`. | =4 |
| 5 | direct-fix | `.gzkit/rules/pythonic.md:50-51` | Delete the accusation that the scorecard miscodes rows 19/20; it now scores them Judgment. A citation loop where each surface describes a stale version of the other. | D3 |
| 6 | direct-fix | `.gzkit/rules/task-discovery.md:107, :130, :140` | Repoint the dead GHI #752 pointer; reconcile the eight-event list with `_TASK_WORKLOG_TYPES`; drop the Heavy/Lite promise or implement the lane read. | D6, M12, M13 |
| 7 | direct-fix | `AGENTS.md:212` | Drop *"`semver`"* from the pool clause, or make `_check_pool_taxonomy` inspect it. | M11 |
| 8 | direct-fix | `.gzkit/rules/tests.md:18` | Qualify the empty-tier claim with `smoke.required`. **Ships in the wheel — it is false for every adopter that has not opted in.** | M16 |
| 9 | **operator ruling** | scorecard ↔ validator registry | 54 of 89 scopes bind no rule. Decide whether the inverse direction gets an owner, or record that it deliberately has none. | inventory |
| 10 | next run | `--pydantic-models` | Locate the implementation and give M6 a verdict. | M6 |

## Audit posture

- **Lane:** Lite — audit-only. This run edited exactly five files, all under this
  chore's `proofs/`. No rule, validator, or source file was modified **by the
  audit**; the one correction it prompted (scorecard row 17e) was applied as a
  separate, deliberate edit and is disclosed above rather than folded in silently.
- **Read-only on the validator** (§ Policy and Guardrails): every
  `src/gzkit/commands/validate*` and check implementation was read, none modified.
- **First-party verification:** the two exit-code drifts in Headline 1 were
  re-verified directly by the session — the policy-breach set read verbatim, and
  the emitted `type=` strings grepped — not accepted from the readers that
  surfaced them.
- **Convergence:** the `--cli-alignment` exit-code drift was found independently by
  the check-behavior reader and by the prior-row reader (as M2), and confirmed a
  third time first-party. The `transcribed_counts` inversion came from a single
  reader and was verified before landing.
