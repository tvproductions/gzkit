---
id: ADR-pool.handoff-resume-assessment
status: Pool
parent: ADR-0.0.65-handoff-system-consolidation
lane: heavy
enabler: null
---

# ADR-pool.handoff-resume-assessment: Handoff Resume Assessment

## Status

Pool

## Intent

**Correction, not enhancement.** ADR-0.0.65 (`Validated`) built the handoff API so CREATE and
RESUME would run as code rather than as documentation, and kept the skill's RESUME "chain-traversal
and staleness gate" because they are "genuinely useful". The shipped RESUME path does not deliver
that intent. Operator doctrine, verbatim: *"discovering that more is needed to fulfill the intent of
a feature is not an enhancement, it is a correction."* A `Validated` ADR is never reopened, so the
residual is re-homed here (campaign § Amendments 2026-09-29). Operator ruling 2026-09-29, verbatim:
*"this could ONLY be a pool adr at this point"*. It takes a feature semver at promotion.

Observed on `main`, 2026-09-29:

1. **RESUME never validates the document it loads.** `validate_handoff_document` runs inside
   `create_handoff` (`src/gzkit/handoff_api.py`) and in the `gz check` corpus gate
   (`src/gzkit/quality.py`), never in `resume_handoff`.
2. **Freshness is clock-only.** `_classify_staleness` buckets age at 24h / 72h / 7d.
   `StalenessLevel` has no member for "could not verify", so a handoff under 24 hours old reads
   `Fresh` whatever changed under it: commits, a branch switch, edits to the files it cites.
3. **Documented code that does not exist.** The `gz-session-handoff` skill's RESUME steps and
   acceptance rules name `verify_context()` ("detects branch mismatches and missing referenced
   files"). No such function exists in `src/`. This is the vaporware-API defect ADR-0.0.65 was
   created to remove (its Problem 3), surviving in the resume path.

The agent is told to do all of this by hand (the skill's Claim Verification Gate). That is a
discipline declared without a mechanism.

Sources: tech-debt dossier findings `governance-resume-contract-not-mechanized` (Critical) and
`governance-time-only-staleness` (High), `.gzkit/audits/tech-debt/2026-08-23/findings.json`,
re-verified 2026-09-29.

## Decision

`resume_handoff` produces one structured **resume assessment**:

1. Re-run `validate_handoff_document` on the selected document and report its violations.
2. Reconcile recorded against current state: branch, commits since the HEAD recorded at creation,
   and changes to the files the handoff cites.
3. Classify each factor `verified`, `drifted` or `UNVERIFIED` (could not be checked). A handoff
   written before HEAD was recorded is `UNVERIFIED` for commit drift, worded as a missing
   baseline rather than a failed check.
4. Freshness is driven by the worst verified factor, with age kept as one factor among them.

The assessment is **advisory and gates nothing**, consistent with the retirement of the resume gate
(operator rulings 2026-08-14 and 2026-08-15: *"the handoff should be an advisor, not a
gate-keeping nanny"*). The skill documents only what exists: `verify_context` is either built here
or struck.

### Proposed checklist (1:1 OBPIs at promotion)

1. Validate the loaded document on resume and surface its violations.
2. Record HEAD at creation; reconcile branch, commits and cited files on resume.
3. Add `UNVERIFIED` to `StalenessLevel`; classify freshness from the worst verified factor.
4. Render the assessment in `gz handoff resume` and session orientation.
5. Bring `gz-session-handoff`, the `handoff*` manpages and the runbook to what ships; build or
   strike `verify_context`.

## Alternatives Considered

1. **Leave verification to the agent** through the skill's Claim Verification Gate. Rejected: a
   declared discipline with no mechanism, which is the family this campaign is closing.
2. **Fail closed on drift.** Rejected: it re-arms the resume gate the operator retired.
3. **Add `UNVERIFIED` to the enum only.** Rejected: a label with no evidence behind it.

## Consequences

**Positive**

- A resuming agent gets checked facts instead of an age bucket.
- "Could not verify" becomes representable instead of reading as `Fresh`.
- The skill stops documenting absent code.

**Negative**

- `StalenessLevel` and `ResumeResult` change shape, affecting every consumer, including session
  orientation and the settled-citation checker.
- Resume becomes slower because it reads git state.
- Pre-existing handoffs carry no recorded HEAD and report commit drift `UNVERIFIED`.

## Forcing Functions

- **Pre-mortem:** `UNVERIFIED` appears everywhere because old handoffs lack a baseline, and agents
  learn to ignore it. Mitigation: distinct wording for a missing baseline versus a failed check.
- **What would have to be true:** git state is readable at resume time. Where it is not, the factor
  is `UNVERIFIED`, never assumed clean.
- **Reversibility:** two-way door. The output is advisory and the fields are additive.
- **Scope minimization:** checklist items 1 to 3 without the orientation rendering.
- **Forces next:** whether session orientation, `gz airlock in` and resume share one drift model.
  The dossier recommends unifying them; that may be a later ADR.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

Interview answers: `docs/design/adr/pool/handoff-resume-assessment-interview.json`.
