---
id: ADR-0.0.69-channels-first-closeout-proof
status: Completed
kind: foundation
semver: 0.0.69
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-06-09
---

# ADR-0.0.69-channels-first-closeout-proof: Channels-First Closeout Proof

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
Treats governance not as overhead but as the discipline that keeps work honest.
The operative stance for this ADR: **proof is computed, never stored**. A closeout
proof that lives in a hand-maintained frontmatter block is a copy of evidence, and a
copy drifts; the work here is to delete the copy and recompute the proof from the live
three-channel evidence surface every run, so a broken channel can never hide behind a
stale stored block.

## Why foundation tier?

Without a channels-first closeout proof, gzkit's REQ-kind discipline (ADR-0.0.59) is
only half-enforced: two of its three proof channels — SUPPORT and STRUCTURAL-FENCE —
are silently advisory today (`req_kind.py:182` hardcodes `"advisory-support"`; the FENCE
arm reports `"grandfathered"`), and the `ln:` closeout-proof-binding block stores a
redundant copy of evidence that already lives in the ledger, in `@covers` tests, and in
parent-ADR Boundary Invariants. The invariance test resolves **yes**: gzkit's identity
**is** governance integrity / anti-vibe enforcement, and a closeout gate that waves two
of three channels through — or reads proof from a drift-prone stored block instead of
recomputing it — is not that project. The proof surface is identity-shaping, not a
feature.

Port-vs-adapter: this ADR is a **port**. "Closeout proof is computed from the live
three-channel evidence surface, never read from a stored artifact" is the abstract
contract; the specific `trust_audits/closeout_proof.py` view, the `--closeout-proof`
flag, and the ceremony gate `_gate_closeout_proof` are adapters behind it. Retiring the
`ln:` adapter and adding the derived-view adapter leaves the port unchanged — and, by
design (ADR-0.0.68 REQ-0.0.68-02-04), requires ZERO rewiring of the session-green gate
because that gate asserts `gz check` *delegation*, not a frozen validator list.

## Intent

Closeout proof must be COMPUTED from the live three-channel REQ-kind evidence surface,
never read from a stored, hand-maintained frontmatter block. Today the `ln:`
closeout-proof-binding block is a redundant, drift-prone copy of evidence that already
exists in the ledger, in `@covers` tests, and in parent-ADR Boundary Invariants. This
ADR retires the `ln:` surface entirely and replaces it with a derived
`gz validate --closeout-proof` view that recomputes per-REQ proof for in-closeout ADRs
over the three REQ-kind channels every run: BEHAVIOR proves through at least one passing
`@covers` test; SUPPORT proves through a cited ledger event found AND a cited validator
scope dispatched exit 0; STRUCTURAL-FENCE proves through a parent-ADR
`## Boundary Invariants` anchor. The view JOINS the `gz check` default set so closeout
proof can never silently become a Layer-3 stored artifact that masks a broken channel.

**Target state (after this lands).** Today a SUPPORT REQ passes closeout because
`req_kind.py` hardcodes `"advisory-support"` without querying the ledger or dispatching
the cited validator (#543); a STRUCTURAL-FENCE REQ passes because the FENCE arm reports
`"grandfathered"` without checking for a real Boundary-Invariants anchor (#538); and the
`ln:` block stores a copy of receipt evidence that 19 briefs carry as drift-prone
frontmatter. After this ADR lands, the target state is: `gz validate --closeout-proof`
recomputes every in-closeout ADR's per-REQ proof from live evidence on every `gz check`
run, the two masked channels are load-bearing, and the `ln:` surface — schema, model,
producer, flag, and 19 stale blocks — is gone. The before-state is "two channels waved
through and proof stored as a stale copy"; the after-state is "all three channels proven
from live evidence, recomputed every run."

## Decision

Retire the stored `ln:` closeout-proof-binding surface and replace it with a derived,
channels-first `gz validate --closeout-proof` view, decomposed into exactly four OBPIs
(the surface boundaries split the two masked-channel fixes from the derived-view wiring
from the `ln:` retirement):

1. **SUPPORT channel made load-bearing (OBPI-0.0.69-01, Heavy).** The SUPPORT branch in
   `req_kind.py` (today hardcoding `"advisory-support"` at line 182) and `_check_support_req`
   actually query the ledger for the cited event AND dispatch the cited validator scope,
   propagating the real `proof_status`. A SUPPORT REQ whose cited ledger event is not
   found OR whose cited validator exits non-zero reports unproven (fail-close). Closes #543.

2. **STRUCTURAL-FENCE channel made load-bearing (OBPI-0.0.69-02, Heavy).** The FENCE arm
   (today reporting `"grandfathered"`) asserts that a parent-ADR `## Boundary Invariants`
   anchor is present for the FENCE REQ; a missing anchor reports unproven. ADR-0.0.59
   itself gains a `## Boundary Invariants` heading anchoring its own FENCE REQs so it stays
   provable. Closes #538.

3. **Derived `gz validate --closeout-proof` view (OBPI-0.0.69-03, Heavy).** A new
   `trust_audits/closeout_proof.py` view computes per-REQ proof for in-closeout ADRs over
   the three channels and JOINS the `gz check` default set (always dispatched, memoized
   per scope per run — ruling 6.1-A). The ceremony gate `_gate_proof_binding`
   (`closeout_ceremony.py:264-290`, wired at `_commit_advance:336`) is replaced by
   `_gate_closeout_proof` on the **same EXECUTE->ATTESTATION edge**, same fail-close shape;
   ADR-0.0.68's session-green gate is left untouched (honoring REQ-0.0.68-02-04's
   zero-rewiring fence). The fail-open seam at `trust_audits/cli.py:222-225` (bare
   `except` -> `return []` in `audit_skill_alignment`) is fixed to surface `ValidationError`,
   with a covering test. ADR-0.0.41 OBPI-02/03 verification text is repointed from the
   removed flag to `--closeout-proof` (else `--cli-alignment` exits 3), and the manpage is
   added. Output is a frozen `CloseoutProofReport` reusing the existing `ReqCoverageRecord`:
   per-REQ table + `--json`; exit 0 (all proven) / 3 (any unproven) / 2 (dispatch I/O
   error). The output MUST print the exact re-run command per failed SUPPORT REQ
   (e.g. the cited `uv run gz validate --<scope>`) so a 2am on-call operator can reproduce
   the failing channel in one paste; full stderr inlining is explicitly out of scope
   (ruling 6.2-A). Before the ceremony-gate repoint lands, OBPI-03 runs the new view
   READ-ONLY against all 19 `ln`-carrying briefs and surfaces/fixes any unprovable REQs
   (ruling 6.1-A pre-audit) so no real closeout goes red on first contact.

4. **Retire the `ln:` surface (OBPI-0.0.69-04, Heavy).** Delete the
   `closeout_proof_binding.py` module (270 lines), the `ReqEvidence` model and
   `BriefStructure.ln` field (`brief_structure.py`), the schema `ln` property
   (`obpi_brief_structure.json:61-85`), the `--closeout-proof-binding` flag
   (`parser_maintenance.py:601-602`, `validate_cmd.py:386-387`), and the #599 producer
   (`_inject_ln_block` / `_render_ln_block` / `_strip_existing_ln` in `obpi_complete.py` +
   tests). One-time strip `ln:` from the 19 briefs (reusing `_strip_existing_ln` before
   deleting it); leftover `ln:` then fails `gz validate --documents` mechanically via the
   schema's `extra="forbid"`. Update docs (manpage, `gz-adr-closeout-ceremony` SKILL.md,
   restore-health roadmap, ADR-0.0.63 package); supersede #599; strike the #593 premise.

5. **Explicit [kind] tags required at closeout (ruling 6.2-A).** Every Acceptance-Criteria
   REQ must carry exactly one inline `[kind]` tag before an ADR can close; kind inference
   stays authoring-time advisory only. ADR-0.0.41's untagged REQs get tagged during OBPI-03's
   pre-audit pass.

**Rationale (why this shape).** The named defect is the *drift surface*, not the producer:
the 2026-06-09 sunset ratification (recorded in `ultraplan-brief.md` section 3) rejected
keeping the `ln:` block even auto-populated, because storing derived evidence as canon is
the Layer-3-as-source-of-truth anti-pattern Architectural Boundary 6 forbids. The two
masked channels (#543 SUPPORT, #538 FENCE) are fixed in the same pass because a proof view
that closes one channel and waves another through is not a proof view (the rejected Option
C). Numbered parts are sequenced so the channel arms (1, 2) become load-bearing before the
view (3) joins `gz check`, and the `ln:` retirement (4) lands last so the strip reuses the
producer's own `_strip_existing_ln` before deleting it.

**Precedent and integration points.** This follows the `--adr-status-fresh` /
`--session-green-gate` precedent exactly: a `run_*_audit` function wired into the `gz check`
default scope that recomputes a derived view rather than reading a stored one. The
`--closeout-proof` scope is added as a `trust_audits/closeout_proof.py` module, registered
on the `gz validate` parser, dispatched in `validate_cmd.py`, and added to the same
`_build_check_steps()` audit set ADR-0.0.68 wired the session-green gate into. Because that
gate asserts delegation (REQ-0.0.68-02-04), adding this scope and retiring the
`--closeout-proof-binding` scope requires zero rewiring of it.

Lane: heavy (new `gz validate` scope, removed `gz validate` scope, ceremony-gate behavior
change, schema change, new manpage). Foundation kind per the invariance test. Hexagonal
lens: **port** ("closeout proof is computed from the live three-channel surface, never
stored"); the view, flag, and ceremony gate are adapters. Reversibility: one-way for the
`ln:` retirement (re-establishing the contract is re-implementation), two-way for the
additive stateless view. Essential core is OBPI-03 (the derived view) plus OBPI-01/02 (the
channels it computes over); OBPI-04 removes the redundant surface the view replaces.

## Boundary Invariants

These are the structural fences this ADR establishes. They are audited at ADR closeout
(STRUCTURAL-FENCE proof channel), not by per-OBPI behavior tests.

1. **The STRUCTURAL-FENCE proof arm is load-bearing — it never reports "grandfathered" or
   advisory** (REQ-0.0.69-02-04). The FENCE arm MUST assert a real parent-ADR
   `## Boundary Invariants` anchor for the FENCE REQ and report unproven when the anchor is
   absent. A future edit that re-introduces a `"grandfathered"`/advisory pass-through —
   re-opening #538 — is a fail-close drift-back signal verified at this ADR's closeout.

2. **The derived `--closeout-proof` view is never persisted as source-of-truth**
   (REQ-0.0.69-03-06). The view MUST recompute per-REQ proof from the live three-channel
   evidence surface on every run and MUST NOT write its `CloseoutProofReport` to disk as a
   stored artifact that a gate reads back. Persisting the report and reading it at gate time
   re-imports the exact Layer-3-as-source-of-truth anti-pattern (Architectural Boundary 6)
   this ADR exists to retire — a fail-close drift-back signal verified at closeout.

3. **ADR-0.0.68's session-green gate is left untouched** (honoring REQ-0.0.68-02-04). The
   ceremony-gate swap (`_gate_proof_binding` -> `_gate_closeout_proof`) rides the
   EXECUTE->ATTESTATION edge of `closeout_ceremony.py` only; it MUST NOT touch
   `.pre-commit-config.yaml` or the `gz check` session-green wiring. Because the
   session-green gate asserts `gz check` delegation, adding the `--closeout-proof` scope and
   removing the `--closeout-proof-binding` scope require zero rewiring of it. Verified at
   this ADR's closeout by inspection that no ADR-0.0.68 surface was modified.

## Consequences

### Positive

1. Closes #543 (SUPPORT channel stops hardcoding `"advisory-support"` at `req_kind.py:182`
   and actually queries the ledger + dispatches the cited validator).
2. Closes #538 (STRUCTURAL-FENCE stops reporting `"grandfathered"`; the FENCE arm becomes
   load-bearing instead of advisory).
3. Supersedes #599 (its landed auto-populate producer from `3c1695eb` is deleted;
   supersession noted on the issue).
4. Removes the redundant, drift-prone `ln:` surface the 2026-06-09 sunset ratification
   rejected: dead schema + 19 stale frontmatter blocks gone.
5. Closeout proof is recomputed from live evidence every run, so it can never silently
   become a Layer-3 stored source-of-truth (Architectural Boundary 6).
6. Unblocks ADR-0.0.41 (currently Pending / `pre_closeout` / BLOCKED 2/5).
7. Both masked channels (SUPPORT and FENCE) are closed in one pass; no channel remains
   advisory behind the derived view.

### Negative

1. **Largest-blast-radius option on the table:** schema removal, CLI flag removal,
   ceremony-gate behavior change, 19 brief rewrites, and docs all land together.
2. **Stricter req-kind-discipline output:** SUPPORT/FENCE REQs that previously passed under
   advisory now fail-close at closeout, so older in-closeout ADRs may surface as unproven on
   first run (mitigated by OBPI-03's READ-ONLY 19-brief pre-audit before the gate repoint
   lands).
3. `gz check` grows one more dispatched scope; per-run cost increases (mitigated by
   per-scope memoization under ruling 6.1-A).
4. Schema re-add is a non-trivial reversal cost if the derived approach proves wrong (the
   deleted model/schema/producer are git-recoverable, but re-wiring is real work).
5. The explicit-`[kind]`-tag requirement is a new gate that can block closeout of any ADR
   whose REQs were authored before tagging discipline existed.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 0
- Dimension Total: 6
- Baseline Range: 3-3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.69-01: SUPPORT channel — real ledger query + validator dispatch in `req_kind.py` SUPPORT branch and `_check_support_req`, propagating real `proof_status` (closes #543) (Heavy)
- [ ] OBPI-0.0.69-02: STRUCTURAL-FENCE channel — Boundary-Invariants anchor assertion + add the `## Boundary Invariants` heading to ADR-0.0.59 itself (closes #538) (Heavy)
- [ ] OBPI-0.0.69-03: Derived `gz validate --closeout-proof` view (new `trust_audits/closeout_proof.py`) printing the per-failed-SUPPORT-REQ re-run command (no stderr inlining) + READ-ONLY pre-audit of all 19 `ln`-carrying briefs before the ceremony-gate repoint lands + ceremony-gate repoint + fail-open seam fix + repoint ADR-0.0.41 OBPI-02/03 verification text + manpage (Heavy)
- [ ] OBPI-0.0.69-04: Retire `ln:` surface — model, schema, producer + tests, 19-brief strip, docs (manpage, `gz-adr-closeout-ceremony` SKILL.md, restore-health roadmap, ADR-0.0.63 package), supersede #599, strike #593 premise (Heavy)

## Q&A Transcript

<!-- Interview conducted 2026-06-09; answers ratified by operator (kind: foundation) with two rulings amended in. Full design content lives in the sections above; this transcript records pointers. -->

**Problem / Intent:** see § Intent — the `ln:` block stores a drift-prone copy of evidence;
two of three REQ-kind channels (SUPPORT #543, FENCE #538) are silently advisory.

**Decision:** see § Decision — make the two channels load-bearing (OBPI-01/02), add a derived
`gz validate --closeout-proof` view wired into `gz check` and swap the ceremony gate
(OBPI-03), retire the `ln:` surface (OBPI-04). Two operator rulings amended in: (6.1-A)
view JOINs `gz check` memoized per scope per run + OBPI-03 runs a READ-ONLY 19-brief
pre-audit before the gate repoint; (6.2-A) explicit `[kind]` tags required at closeout +
the view prints the exact per-failed-SUPPORT-REQ re-run command (no stderr inlining).

**Consequences:** see § Consequences — closes #543/#538, supersedes #599, unblocks ADR-0.0.41;
largest-blast-radius option; stricter output may surface older in-closeout ADRs as unproven.

**Alternatives:** see § Alternatives Considered — Option B (keep `ln:` deprecated-inert),
Option C (SUPPORT-only), keep+auto-populate (#599's original direction), each rejected.

**Forcing functions (load-bearing):** see § Stress-test forcing functions. Shakiest condition
(WWHTBT): all 19 briefs' REQs prove cleanly today — mitigated by the pre-audit ruling.
Reversibility: one-way for the retirement, two-way for the additive view.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Channel arm (OBPI-01): `req_kind.py` SUPPORT branch + `_check_support_req` query the
  ledger and dispatch the cited validator; fail-close test for missing event / non-zero exit
- [ ] Channel arm (OBPI-02): FENCE arm asserts a parent-ADR `## Boundary Invariants` anchor;
  ADR-0.0.59 gains the heading; fail-close test for missing anchor
- [ ] View (OBPI-03): `gz validate --closeout-proof` wired into the `gz check` default scope;
  re-run-command output per failed SUPPORT REQ; fail-open seam fixed; ADR-0.0.41 repointed;
  manpage added
- [ ] Retirement (OBPI-04): `closeout_proof_binding.py` / `ReqEvidence` / `BriefStructure.ln`
  / schema `ln` / `--closeout-proof-binding` flag / #599 producer deleted; 19 briefs stripped;
  `gz validate --documents` green; #599 superseded
- [ ] Four Gates: Gate 1 (this ADR), Gate 2 (TDD), Gate 3 (docs, heavy), Gate 4 (BDD scope per
  OBPI), Gate 5 (human attestation)

## Alternatives Considered

1. **Option B — keep the `ln:` schema as deprecated-inert.** REJECTED. Retains the redundant
   drift surface the 2026-06-09 sunset ratification rejected; leaves dead schema plus 19 stale
   frontmatter blocks in place. The drift surface, not the producer, was the named defect.

2. **Option C — SUPPORT-only scope (fix #543, leave the FENCE arm advisory).** REJECTED.
   Leaves the STRUCTURAL-FENCE arm advisory, so the derived view still masks one channel —
   which is #538's exact failure. A proof view that closes one channel and waves through
   another is not a proof view. (This is also the scope-minimization "half-time version" —
   held off precisely because the operator ruled both channels in.)

3. **Keep + auto-populate (GHI #599's original direction).** REJECTED upstream. Operator ruled
   Option A SUNSET on 2026-06-09 (recorded in `ultraplan-brief.md` section 3). Auto-populating
   a stored block still stores derived evidence as canon — the Layer-3-as-source-of-truth
   anti-pattern Architectural Boundary 6 forbids.

## Stress-test forcing functions (Tier 2)

**Pre-mortem (failed in 18 months, why):** (1) dispatch-cost creep — the `--closeout-proof`
scope made `gz check` slow enough that operators habitually `--no-verify`'d, so the proof was
declared-but-skipped. (2) per-run memoization lied because a dispatched validator scope was
not idempotent within a run, so the cached proof_status diverged from a fresh run. (3) sloppy
`[kind]` backfill mis-tagged a REQ into the wrong channel, masking a real gap behind a passing
arm. (4) someone persisted the `CloseoutProofReport` to disk and a gate read the cache —
re-importing the Layer-3 violation (fenced by Boundary Invariant 2). (5) the gate swap left a
mid-closeout ADR-0.0.41 in a state neither gate fully validated.

**What-would-have-to-be-true:** all 19 briefs' REQs prove cleanly under the new view today —
this is the SHAKIEST condition and the biggest risk, mitigated by OBPI-03's READ-ONLY 19-brief
pre-audit run BEFORE the ceremony-gate repoint lands (ruling 6.1-A). For Option C (SUPPORT-only)
to have been the better choice, the FENCE arm's advisory pass-through would have to be harmless
— contradicted by #538, which is exactly that pass-through surfacing as a masked channel.

**Constraint archaeology:** the receipt-binding constraint is INHERITED from ADR-0.0.63 and is
retired here. "gz check must stay fast" is REAL but unmeasured (watch wall-time; memoize per
scope per run). "Layer-3 is never source-of-truth" (Architectural Boundary 6) is the
load-bearing constraint and the reason the stored block is retired rather than auto-populated.

**Assumption surfacing:** (a) the ledger actually contains the cited events; (b) every REQ maps
to exactly one channel; (c) `ReqCoverageRecord` is reusable as-is for the new report; (d)
`## Boundary Invariants` is the universal FENCE anchor; (e) validator scopes are pure within a
run (the assumption per-scope memoization depends on). If (e) is false, memoization lies — the
pre-mortem's scenario (2).

**2am operator:** the closeout gate blocks an attestation because a SUPPORT REQ's cited
validator exits non-zero. The operator needs to reproduce the failing channel in one paste —
so the view MUST print the exact `uv run gz validate --<scope>` re-run command per failed
SUPPORT REQ (ruling 6.2-A). Full stderr inlining is explicitly out of scope: the re-run command
is the reproduction handle, not a log dump.

**Reversibility:** one-way door for the `ln:` retirement (the schema/model/producer are
git-recoverable, but re-establishing the stored contract is re-implementation); two-way door for
the additive, stateless `--closeout-proof` view.

**Scope minimization:** the smallest version is SUPPORT-only (Option C) — explicitly rejected
because it leaves the FENCE arm advisory. The full scope is held because the operator ruled both
channels in; the essential core is OBPI-03 (the derived view) over the OBPI-01/02 channel arms.

**Closing — downstream ADRs/work forced:** (a) ADR-0.0.41 closeout is re-driven through the new
gate; (b) req-kind `[kind]`-tag backfill for other old in-closeout ADRs; (c) a pool-entry
annotation (`ADR-pool.attested-record-edit-doctrine`, #593 premise struck); (d) the #599
supersession note; (e) a 4th-REQ-kind extension point (the `LEDGER_PLUS_VALIDATOR` constant at
`req_kind.py:35`) is now the natural seam for any future proof channel.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.69 | Completed | g0 | 2026-06-11 | Completed |
