# Exemption-control triage (GHI #797 drain, 2026-08-14)

Companion to `data/exemption_control_grandfather.json`. That file counts the
disclosed absence of an `exempts` declaration; this file records **what was found
when the gates behind those absences were actually read**, so the next drain pass
starts from a reading rather than from a scan.

Authored under the operator ruling of 2026-08-14: *triage all 71, declare only the
honest `'none'`s.* Writing exemption controls was explicitly **not** in scope —
that remains the enrollment the 2026-08-12 inventory-not-enrollment ruling
declined, and the `advisory-rules-audit.md` § Recommended promotion order freeze
still governs (*"a new mechanical check is added only when a specific, observed
drift instance justifies it"*).

## Result

| | before | after |
|---|---|---|
| Claims declaring `exempts` | 5 | **13** |
| Disclosed undeclared | 71 | **63** |
| `baseline_count` (shrink-ratchet) | 71 | **63** |

Eight claims were read end-to-end, found to carry no exemption surface, declared
`exempts='none'` in `_QC_CLAIM_EXEMPTS`, surrendered from the accepted list, and
the ratchet baseline decremented in the same commit.

## The bar applied

A claim was declared `'none'` only when **no input makes the gate admit an item it
has judged in violation**. Qualifying admit paths — any one of these means the
gate has an exemption and stays disclosed:

- a waiver / grandfather table (`data/*_waivers.json`, `data/*_grandfather*.json`)
- an `excluded` / allowlist entry
- an escape marker or skip token in the scanned content
- an opt-in arm that is off by default, or an opt-out config that disables the check
- an authorization booking (the resume-gate shape)

**Not** exemption surfaces, and deliberately so: scope predicates (which artifacts
the gate examines), threshold parameters (a budget defines what a violation *is*),
artifact-absent returns (nothing to compare), and error-path returns.

This bar is calibrated against the two pre-existing declared exemplars, which are
the only place the line had been drawn before this pass:
`handoff-resume-unauthorized-{write,bash}` name the booking claim as their
exemption, and `verifier-pipe-gate` names the `pipefail`/`PIPESTATUS` escape. Both
controls assert the **differential** — refuse-without and permit-with, in one
function — which is the shape any control written from this triage owes.

## Declared `'none'` (8 — surrendered)

| Claim | Why nothing is owed |
|---|---|
| `adr-status-freshness` | Diffs on-disk ADR canon against the derived index; every drift entry is a finding and nothing suppresses one. |
| `instructions-files-budget` | Per-file char budget. Project-overridable, but a threshold defines the violation rather than admitting one. |
| `invariant-coherence` | Byte-compares rendition playback against committed `AGENTS.md`. Only non-finding return is "no committed rendition exists". |
| `kind-invariance` | Requires a substantive `## Why foundation tier?` on every foundation ADR. The sidecar filter selects which files are ADRs; it admits no failing ADR. |
| `line-endings` | Two fail-closed arms (`.gitattributes` LF directive; no tracked text surface committed CRLF). No per-file waiver. |
| `orientation-freshness` | Asserts the SessionStart hook stays wired in both harnesses. Every arm yields a finding; a missing script is an error, not a pass. |
| `waiver-ratchet-closed-set-lock` | Per-surface mechanism check. The registry's `excluded` list is consulted **only** by the unregistered-file scan, never here. |
| `waiver-ratchet-dated-cutover` | Same. |

## Exemption surface located — control owed (Tier A)

Each of these was read or its admit path located and named. None can honestly
declare `'none'`; each owes a control asserting the refuse/permit differential
across the named surface.

| Claim | Admit path |
|---|---|
| `waiver-ratchet`, `waiver-ratchet-silent-bypass` | registry `excluded` list |
| `handoff-documents`, `handoff-documents-populated-sections` | `data/handoff_section_grandfather.json` + pre-cutover legacy tolerance |
| `authorship-policy` | opt-in `authorship.required_email_suffix`; unset ⇒ whole audit is a no-op |
| `insights-shape` | `_INSIGHTS_SHAPE_WAIVERS`, keyed by content hash |
| `fidelity-presence` | `data/fidelity_presence_grandfather.json` |
| `persona-witness` | `data/persona_grandfather.json` |
| `rendition-floor-coherence`, `rendition-freshness` | MX hangar checkpoint downgrades the gate to advisory when the marker is present |
| `brief-structure` | `is_terminal_brief_status` carve-out — an authored `status:` flips a brief from judged to admitted |
| `module-size` | grandfathered roster (the control's own `expect_output` is `"not grandfathered"`) |
| `adr-taxonomy` | `data/foundation_grandfather.json` |
| `adversarial-validation` | `data/adversarial_validation_grandfather.json` |
| `advisory-scorecard-coverage`, `-summary-drift`, `-ruff-reachability` | `advisory_scorecard_grandfather.json`, `mechanical_witness_grandfather.json` |
| `closeout-proof` | `data/behave_coverage_waivers.json` |
| `complexity-doctrine-links` | `<!-- gz-validate-skip: complexity-doctrine-links -->` marker |
| `complexity-thresholds` | a declared "Bootstrap absolutes" section skips portability checks |
| `gate-callers` | `data/uncalled_gate_grandfather.json` |
| `status-writer-coverage` | `_DATACLASS_WAIVERS` |
| `qc-binding`, `theater-signature-scan` | `_SELF_EXCLUSION` set |
| `receipt-shape` | `data/historical_self_close_waivers.json` |
| `red-parity` | dated `CUTOVER` — pre-cutover completions skipped |
| `lock-exchange-coupling` | dated enforcement cutover grandfathering the warning-only transition |
| `unscoped-rules` | manifest `rules.unscoped_allowlist` |
| `session-green-gate` | `check_delivery` arm is opt-in and off by default |
| `smoke-tier` | empty tier passes unless the project declares `smoke.required` |
| `transcribed-adr-counts` | opt-in surface registry + `<!-- historical-count -->` opt-out marker |
| `req-kind-discipline` | all-untagged brief ⇒ legacy/grandfathered pass |
| `interview-transcripts` | `data/interview_transcript_waivers.json` |
| `tautological-test-audit` | waivers + self-exclusion + baseline |
| `validate-default-scopes` | `is_adr_shape_grandfathered` + waiver counting |
| `surface-fidelity-surface-weight`, `surface-fidelity` | `data/surface_weight_waivers.json` (the composite inherits it) |
| `exemption-controls` | its own `accepted_claims` list — this inventory is exempted by the surface it inventories |
| `lint`, `format`, `typecheck`, `test`, `behave` | the **external tool's** escape: `# noqa`/`per-file-ignores`, `# fmt: skip`, `# ty: ignore[...]`, `@unittest.skip`, skip tags |
| `task-envelope-coherence`, `-layer-drift`, `-obpi-divergence`, `-subdivision` | `_OBPI_ID_CANONICAL_CUTOVER` + per-signature grandfather sets + `req_atomic` exemption |

## Not reached this pass (Tier B — 17)

Read before declaring. No exemption surface was *located* for these, but absence
of a located surface is not a reading, and this file will not launder one into the
other:

`agents-md-map-conformance`, `obpi-lifecycle-coherence`, `pool-interview-schema`,
`gate5-attestation-absence`, `gate5-ledger`, `grader-gaming`,
`airlock-in-unaccounted-seam`, `enforcement-floor`, `dispatch-absorption-marker`,
`docs-build`, `readiness-audit`, `cli-audit`, `skill-audit`, `parity-check`,
`preflight`, `surface-fidelity-bullet-retention`, and the composite arm of
`surface-fidelity` not covered above.

## Observations (none of these is a defect)

Recorded because they shape what a future drain costs — **not** as tracked
defects. Read them as pricing, not as a backlog.

**1. The control-writing side is where the cost is.** Of 71 claims read or
located, 8 were declarable and ~46 carry a real admit path. The drain is not
gated on judgment — the judgment is cheap and now recorded — it is gated on
writing ~46 differential controls. That is the enrollment the 2026-08-12 ruling
declined, and this triage does not reverse it; it prices it.

**2. Five claims inherit their exemption from an external tool.** `lint`,
`format`, `typecheck`, `test`, and `behave` gate on ruff / ty / unittest / behave,
whose escapes (`# noqa`, `# fmt: skip`, `# ty: ignore`, `@skip`) are not gzkit
surfaces. A control for these asserts that gzkit's *invocation* still refuses
without the escape and admits with it — worth deciding once as a family rather
than five times.

**3. `gz validate --type-ignores` is the one Tier-A row whose control already
exists in substance** — it polices the `typecheck` gate's `# ty: ignore[...]`
escape (`.claude/rules/pythonic.md` § Type-check suppression syntax), which is the
refuse/permit differential an exemption control owes. It carries no enforcement
claim, so `typecheck` cannot name it.

> **Do not read that as a singular hole.** Measured 2026-08-14: the QC registry
> holds 56 steps (55 `bound`, 1 `advisory`) and `type-ignores` is not in it at
> all, but neither are `class-size`, `cli-alignment`, `commit-trailers`,
> `distribution`, `sensitivity`, `skill-alignment`, or `utf8-prefix` — dozens of
> explicit-only `gz validate` scopes carry no claim, and `type-ignores` is not in
> the `validate-default-scopes` blanket either (the default tier is 13 scopes).
> `--qc-binding` passes green over all of it because it audits only *enrolled*
> steps. That is the single-membership blindness
> `exemption_controls.py` already names one level up — a known posture, not a
> discovery, and enrolling one scope does not change it.

**4. `_ep_fidelity_presence` deliberately zeroes its own exemption, and this is
correct.** The control calls `audit_fidelity_presence(root, grandfather=frozenset())`
so the refuse arm genuinely fires against an unwaived corpus — a stronger control
than most in the table. It is recorded here only as a worked illustration of the
disclosed GHI #797 class (the admit half of a two-claim gate goes unexercised),
never as a criticism of the control.

## Verification

```bash
uv run gz validate --exemption-controls   # 76 inventoried, 13 declared, 63 disclosed
uv run gz validate --waiver-ratchet       # baseline_count 63 matches the live list
jq '.accepted_claims | length' data/exemption_control_grandfather.json   # 63
```
