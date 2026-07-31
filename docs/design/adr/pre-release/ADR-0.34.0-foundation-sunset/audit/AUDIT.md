# AUDIT — ADR-0.34.0-foundation-sunset

**Date:** 2026-07-31
**Transition:** COMPLETED → VALIDATED
**Lane:** heavy · **Kind:** feature (0.34.0) · **Release:** v0.34.0
**Driver persona:** `pipeline-orchestrator`
**Operator acceptance:** `accept audit` (verbatim, 2026-07-31)

## Summary

| Dimension | Result |
|-----------|--------|
| Completeness | ✓ 5/5 OBPIs `attested_completed`; ledger proof PASS |
| Integrity | ✓ closure holds at every door; S1 and S2 remediated in-session |
| Alignment | ⚠ code/doc contradiction on adopter posture — S3, tracked at GHI #740 |
| Fidelity | ✓ 2 assertions, 2 pass, 0 fail |

**Verdict: VALIDATED.** Three shortfalls were surfaced by independent review and
verified against source by the driver. Two were remediated in-session (S1, S2);
the third is a design question routed to GHI #740.

The ADR's thesis holds against the running system: the `foundation` kind is
refused at every authoring and registration door in production configuration,
the grandfathered set still validates, and the partition is computed from
Layer-2. The shortfalls concerned what the *evidence* proved, not whether the
capability works — except S3, which is a genuine gap between what the Decision
section promised adopters and what the assembled system does to them.

**Disposition of shortfalls**

| # | Finding | Disposition |
|---|---------|-------------|
| S1 | 15 of 26 `@covers` decorations on REQ-0.34.0-03-01 were unrelated tests | **Remediated** — decorations stripped; both affected modules pass (15 tests OK); coverage holds at 18/20 on REQ-03-01's 11 legitimate tests |
| S2 | REQ-01-01/-01-02 mandate `exit 3`; no test asserted the registration | **Remediated** — `TestClosedKindExitContract` added, mutation-proven: removing both registrations fails 2 tests (RED), restoring them passes 7 (GREEN) |
| S3 | ADR promises adopters stay open; code closes them unconditionally | **Tracked** — GHI #740, cross-linked to siblings #607 and #728 (same adopter-boundary class) |

Note on ordering: the operator's `accept audit` was given with all three
shortfalls open and stated. The receipt records that state. S1 and S2 were
remediated after the receipt so that what was recorded matches what was
accepted, rather than fixing first and recording a cleaner picture than the one
the operator ruled on.

## Fidelity Gate (Step 3 — bound, `gz adr fidelity ADR-0.34.0`)

| Claim | Command | Expected | Observed | Result |
|-------|---------|----------|----------|--------|
| The foundation kind is closed to new authoring even for a well-formed next-free nominal semver | `uv run gz plan create sunset-fidelity-probe --kind foundation --semver 0.0.75 --dry-run` | 1 | 1 | ✓ PASS |
| Every on-disk `kind: foundation` ADR is grandfathered or demoted; none in Pending-with-attested-work limbo | `uv run gz validate --taxonomy` | 0 | 0 | ✓ PASS |

Summary: 2 pass, 0 fail. Proof: `proofs/fidelity.txt`.

## Execution Log

| Check | Command | Result | Proof |
|-------|---------|--------|-------|
| Ledger proof | `gz adr audit-check ADR-0.34.0` | ✓ PASS — 18/20 REQs covered; 2 `[SUPPORT]` proof-exempt by design | `proofs/audit-check.txt` |
| Fidelity gate | `gz adr fidelity ADR-0.34.0` | ✓ 2/2 | `proofs/fidelity.txt` |
| CLI/doc coverage | `gz cli audit` | ✓ 132/132 commands covered | `proofs/cli-audit.txt` |
| Config paths | `gz check-config-paths` | ✓ PASS | `proofs/config-paths.txt` |
| Unit suite | `gz arb step --name unittest` | ✓ 7685 tests OK | receipt `arb-step-unittest-f02e079a9c5c4fce83433f15d1ace4b1` |
| Typecheck | `gz arb typecheck` | ✓ PASS | receipt `arb-step-typecheck-4c8436dc00e842b8847ebcacb7dc866c` |
| Lint | `gz arb ruff` | ✓ PASS | receipt `arb-ruff-9b11bcbc647c4b9a9ddb6282f7fc34b4` |
| Docs build | `gz arb step --name mkdocs` | ✓ PASS | receipt `arb-step-mkdocs-3f31717e44a04a46821f35433f53b0c2` |
| BDD | `uv run behave features` | ✓ 66 features / 401 scenarios / 0 failed | closeout evidence |

## Claim verification

| # | Claim | Result | Evidence |
|---|-------|--------|----------|
| C1 | Foundation kind closed at every authoring door | ✓ | Four refusal probes run during closeout, all exit 1 with three-part prose, zero writes; newest `adr_created` in ledger unchanged at 2026-07-26 |
| C2 | Kind remains a valid schema value; grandfathered ADRs validate | ✓ | `gz validate --documents` exit 0 |
| C3 | Every foundation grandfathered or demoted; none in limbo | ✓ | `gz validate --taxonomy` exit 0 (was exit 3 / 74 findings at OBPI-01) |
| C4 | Partition computed from Layer-2, never frontmatter | ✓ | `taxonomy.py:408-412` ranges over ledger `foundation_grandfathered` events; attestor requirement enforced with live negative control at `test_foundation_limbo_gate.py:143-182` |
| C5 | Gate permanent, no staging flag | ⚠ | Wired as final step of `gz check`; qualified by N1 below |
| C6 | 23-node demotion preserved lineage, no orphans | ✓ | `gz ontology resense` 23 removed / 23 added, one-to-one; `anchor_integrity` + `rename_integrity` in `sunset_migrate.py:500-583` |

## Shortfalls

Independent review dispatched per skill § Persona Dispatch. Both `spec-reviewer`
and `quality-reviewer` returned **CONCERNS**; the driver independently verified
each finding below against the source rather than relaying the subagents'
claims.

### S1 — `@covers` attribution pollution on REQ-0.34.0-03-01 (non-blocking)

**Severity:** non-blocking · **Effort:** ≤10 lines · **Status:** REMEDIATED 2026-07-31 (15 stale decorations stripped; both modules still pass, 15 tests OK)

26 tests decorate `REQ-0.34.0-03-01`. Only 11 relate to it.

| File | Decorations | Subject |
|------|-------------|---------|
| `tests/test_foundation_limbo_gate.py` | 11 | the terminal-partition gate — correct |
| `tests/test_task_obpi_id_canonicalization.py` | 9 | `_resolve_obpi_id()`, GHI #653 — **unrelated** |
| `tests/test_task_trailer_autostamp.py` | 6 | commit-trailer autostamping, GHI #731 — **unrelated** |

Neither unrelated module imports `audit_foundation_closure` or anything in the
foundation-sunset surface; their only connection is fixture strings containing
`OBPI-0.34.0-03`. Delete `tests/test_foundation_limbo_gate.py` entirely and the
REQ still reports covered. Coverage reads 100% while 58% of it is inert.

**Proposed fix:** strip the 15 stale decorations.

### S2 — two attested REQs mandate `exit 3`; no test asserts it (non-blocking)

**Severity:** non-blocking · **Effort:** ≤20 lines · **Status:** REMEDIATED 2026-07-31 (`TestClosedKindExitContract` added; mutation-proven RED — removing both registrations fails 2 tests — then GREEN, 7 tests OK)

`REQ-0.34.0-01-01` and `REQ-0.34.0-01-02` each read *"emits finding … and exits
3."* The exit depends on membership in `_POLICY_BREACH_ERROR_TYPES`
(`src/gzkit/commands/validate_cmd.py:1113-1114`). The membership is present and
correct. No test guards it:

- `tests/test_foundation_limbo_gate.py:319-323` asserts membership — for
  `foundation_limbo` only
- `tests/governance/test_taxonomy_closed_kind.py`, covering
  `foundation_kind_closed` and `grandfather_dangling`, has **zero** `SystemExit`
  references and no membership assertion

Deleting the two registration lines leaves every REQ-01-01/-01-02 test green
while both REQs are violated. OBPI-03 found this exact defect for
`foundation_limbo` (a Step-4b Codex adversary caught a limbo-only validation
exiting 1 where the REQ required 3) and shipped three dedicated exit-contract
tests. The identical hole in the sibling REQs was never back-filled.

This is the campaign § 4 enforcement-claim rule failing inside the ADR whose
purpose is enforcement: the claim "exits 3" has no live negative control.

**Proposed fix:** add a membership assertion mirroring
`test_foundation_limbo_gate.py:319-323` for both types.

### S3 — the ADR promises adopters stay open; the code closes them (non-blocking, design)

**Severity:** non-blocking for gzkit's own closure · **Effort:** design conversation · **Status:** TRACKED at GHI #740

The ADR states the adopter carve-out in three places, including an explicitly
rejected alternative:

- § Decision (DATA FLOW): *"The mechanism … ships framework-wide; the DECISION
  to close is project-local — `gz init` scaffolds adopters OPEN."*
- § Consequences Positive #8: *"without crippling adopter projects for whom
  foundation-authoring is still appropriate."*
- § Alternatives **8. Framework-wide forced closure for all adopters.
  REJECTED** — *"over-reach … ship the mechanism but keep the closure decision
  project-local."*

What shipped, verified:

| Surface | Behavior |
|---------|----------|
| `plan.py:223-231` `_render_adr_by_kind` | raises unconditionally on `kind == "foundation"`; no config read |
| `adr_promote.py:71-81`, `:122-127` | unconditional refusal, both layers |
| `interview_cmd.py:161-173` | unconditional refusal on any `0.0.x`-embedding id |
| `register.py:29-37` `grandfathered_foundation_ids` | returns `frozenset()` when the manifest is absent — so for an adopter *every* foundation package is un-grandfathered and refused at `register.py:387` and `init_cmd.py:885` |
| config | no project-local key exists |
| `gz init` / templates | scaffold no adopter manifest |

The assembled system implements the alternative the ADR rejected.
`docs/user/concepts/adr-taxonomy.md:16` tells adopters the kind is *"open for
adopter projects"* — doc and code contradict.

Per operator doctrine (*"discovering that more is needed to fulfill the intent
of a feature is not an enhancement, it is a correction"*), this is a correction
owed under this ADR, not new-feature scope.

**Proposed fix:** operator design decision — either ship the project-local
carve-out the Decision promised, or amend the ADR and the concept doc to record
that closure is framework-wide.

## Notes (non-shortfall)

### N1 — the taxonomy gate demotes to advisory under an active MX hangar marker

`quality.py:483` registers `("ADR taxonomy", run_taxonomy_audit)`; `quality.py:508`
routes results through `_apply_mx_seam`; `quality.py:93` maps `"taxonomy"` to
`ERROR`, not `CRITICAL`, and `"taxonomy"` is not in `GATE5_INVARIANTS`
(`mx/invariants.py:23-31`). With a marker active, an exit-3 taxonomy breach is
rewritten to green in `gz check` (`quality.py:120-126`). Contrast
`"Enforcement floor"` at `quality.py:92`, pinned `CRITICAL` for this reason.

Direct `uv run gz validate --taxonomy` still exits 3 (no MX seam in that path),
and the authoring doors are hard refusals unaffected by MX. This qualifies the
ADR's "permanent standing gate" language; it does not void the closure. Seam
between OBPI-05's wiring choice and ADR-0.0.74's MX doctrine.

### N2 — GHI #734's framing is imprecise, not an undercount

Exactly three `adr_created` emission sites; no fourth was found:

| Site | Guard |
|------|-------|
| `plan.py:308` (inside `register_adr_in_ledger`, defined `plan.py:266`) | none at the emission site |
| `register.py:548` | guarded at `register.py:387` |
| `init_cmd.py:888` | guarded at `init_cmd.py:885` |

`register_adr_in_ledger` has exactly two callers and both are separately guarded
upstream (`plan.py:422` ← guarded at `plan.py:223`; `interview_cmd.py:269` ←
guarded at `interview_cmd.py:161-173`). So the helper is a **latent** surface —
a future third caller inherits no protection — not an open hole today. The
defect shape is guard-at-caller rather than guard-at-choke-point, the one place
the ADR's own fix-the-class discipline was not applied.

### N3 — REQ-0.34.0-05-01's BEHAVIOR→SUPPORT re-kinding is legitimate but mis-homed

The kind is correct by proof channel (a state assertion about a generated
Layer-3 artifact, proven by a structural validator — SUPPORT per ADR-0.0.59),
and the channel genuinely resolves. But the reason no test could fail is that
the work landed in OBPI-04 (`d521ace53`), not OBPI-05. The correct disposition
was to move the REQ or withdraw it; re-kinding preserved the credit. Disclosed
in the brief, so the operator-visible record is intact.

## Evidence Index

- `proofs/audit-check.txt` — ledger proof, REQ coverage
- `proofs/fidelity.txt` — bound fidelity gate, 2/2
- `proofs/cli-audit.txt` — 132/132 command coverage
- `proofs/config-paths.txt` — config-path coherence
- `AUDIT_PLAN.md` — claims, checks, risk focus, dispatch charges
- ARB receipts (closeout): `arb-ruff-9b11bcbc647c4b9a9ddb6282f7fc34b4`,
  `arb-step-unittest-f02e079a9c5c4fce83433f15d1ace4b1`,
  `arb-step-typecheck-4c8436dc00e842b8847ebcacb7dc866c`,
  `arb-step-mkdocs-3f31717e44a04a46821f35433f53b0c2`

## Open GHIs at audit time

| # | Title | Relationship |
|---|-------|--------------|
| 734 | third `adr_created` ingress bypasses the foundation membrane | Operator-accepted residual; qualified by N2 |
| 735 | leading BOM hides the whole frontmatter block | Deferred ingress hardening |
| 736 | three ad-hoc frontmatter decoders disagree | Deferred ingress hardening |
| 738 | closeout-walkthrough demo discovery cannot surface refusal demos | Filed from this ceremony |
| 739 | closeout minor-release ceremony deadlocks on the rule-11 tag audit | Filed from this ceremony |

## Attestation

Gate 5 human attestation was recorded per-OBPI at completion (all five, `g0`,
2026-07-19 through 2026-07-31) and at ADR closeout (`g0`, 2026-07-31,
verbatim *"attest completed"*).

Audit acceptance: operator verbatim **`accept audit`**, 2026-07-31, given after
the three shortfalls above were presented in full with their verification
evidence. The operator accepted the audit with shortfalls open and recorded.

Agent signs the audit execution: independent `spec-reviewer` and
`quality-reviewer` dispatches both returned CONCERNS; every finding was
independently re-verified against source by the driver before being recorded
here. No finding was accepted on a subagent's assertion alone.
