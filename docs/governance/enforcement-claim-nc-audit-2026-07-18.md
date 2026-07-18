# Enforcement-claim negative-control audit — 2026-07-18

> **Status:** evidence artifact. Not doctrine, not a ruling. Produced in-session
> as the sizing diagnostic behind GHI #698 and the class-level GHI that follows
> it. Consumed by campaign **Movement B item 5** (*"Bind with a §4 live NC on
> each widened door"*), which cannot be discharged honestly until the findings
> below are repaired.

## What was audited

All **47** enforcement claims registered through `_ensure_production_claims_registered()`
(`src/gzkit/enforcement.py`), against the standard the campaign sets for them
(`docs/governance/build-to-1.0-campaign-2026-06-30.md` §5):

> Any place gzkit asserts something is **enforced / validated / fail-closed /
> gated / blocked** — in code, an ADR, a doc, or an agent's claim — there MUST
> exist a paired **live negative-control** test that (a) constructs a known
> violation of **that exact claim**, (b) runs the real path in its **production**
> configuration, and (c) asserts it **fails**.

## Method — and its limits

Each claim was assessed by a falsification test:

> **If someone deleted the specific logic this claim names, would this NC still PASS?**

YES → the NC is not proving what it claims. NO → the NC is load-bearing.

**The method was informal and must not become the mechanism.** It was five
parallel agent passes making judgment calls — a stochastic surface auditing a
stochastic surface, which is the shape this entire finding is about. It is
defensible as a *sizing diagnostic* and indefensible as a *control*. The
falsification test above is textbook **mutation testing** (statement-block
removal; a surviving mutant is an NC that still passes). That it had to be run
by hand is itself the finding: the right question existed and no machine was
asking it.

Load-bearing findings were re-opened and verified directly rather than relayed
from the audit passes; those are marked **[verified]** below.

## Result

| Verdict | Count | Meaning |
|---|---:|---|
| **ADEQUATE** | 14 | deleting the named logic flips the NC to FACADE |
| **UNDER-SCOPED** | 25 | fixture violates something narrower or other than the claim asserts |
| **TRIVIAL** | 7 | violation-by-absence; fails for a reason unrelated to the claim |
| **UNCLEAR** | 1 | needs one execution to settle |

**32 of 47 claims do not prove what they assert.** `gz check` reports 47/47 verified.

## Per-claim verdicts

### ADEQUATE (14)

| Claim | Why it holds |
|---|---|
| `airlock-in-unaccounted-seam` | two-pole differential over a runtime-unique id; both poles falsifying. Caveat: proves the primitive, not the three doors |
| `handoff-resume-unauthorized-write` | two-pole differential; refused-when-unauthorized AND permitted-when-authorized |
| `handoff-resume-unauthorized-bash` | same differential over the ceremony clause. Converse read-only-permit limb unprobed |
| `gate5-attestation-absence` | every other field valid, so the empty-`attestation_text` check is solely load-bearing |
| `gate5-ledger` | real `validate_ledger` on a genuinely corrupt ledger; narrowing to schema conformance disclosed in-line |
| `rendition-floor-coherence` | both tier-selection and verbatim-containment individually falsifying |
| `unscoped-rules` | asserts the *specific* exit code 3, explicitly excluding the trivial exit-2 path — **the template for the rest** |
| `interview-transcripts` | fixture clears every short-circuit; pass turns solely on the named regex |
| `kind-invariance` | real foundation ADR missing the required section. `_is_placeholder_body` unreached |
| `instructions-files-budget` | char-count comparison genuinely exercised. `globs` branch and packaged-defaults fallback unreached |
| `tautological-test-audit` | real tautological op planted. Baseline/waiver drift semantics (GHI #632) untested |
| `waiver-ratchet` | shrink-ratchet growth check falsifying. Closed-set-lock, dated-cutover, silent-bypass guard unexercised |
| `test` | genuinely red unittest; stdlib runner, no launch-failure confound |
| `typecheck` | **conditional** — depends on `ty` resolving via ambient PATH; on a runner without it, degrades silently to TRIVIAL |

### UNDER-SCOPED (25)

| Claim | Deletable while green |
|---|---|
| `qc-binding` **[verified]** | entrypoint is `_check_theater_signatures`, not `audit_qc_binding` — the entire behavioral channel + live source scan |
| `enforcement-floor` **[verified]** | `run_meta_validator(registry=records, …)` skips production discovery — the ORPHAN class is invisible |
| `theater-signature-scan` | 1 of 3 signatures planted; `copy-vs-self` + `skip-if-PASS` detectors, and `scan_validator_tree` |
| `handoff-documents` **[verified]** | six *missing* sections, zero *empty* — `validate_sections_populated` (GHI #698) |
| `rendition-freshness` | the corpus-fingerprint content comparison that replaced the repudiated mtime tautology, plus the GHI #694 integrity arm |
| `closeout-proof` | SUPPORT and STRUCTURAL-FENCE branches — the two channels ADR-0.0.69 exists to fix |
| `red-parity` | the `failure_class == "none"` unfalsifiable-test arm |
| `receipt-shape` | any two of the three ADR-0.0.36 prohibitions, including `attestor: ^agent:` |
| `req-kind-discipline` | the headline kind-tagging/mixed-state check, plus SUPPORT and FENCE checkers |
| `adversarial-validation` | either half — `bool()` makes the two-arm fixture an OR, not an AND |
| `lock-handoff-coupling` | handoff existence, timestamp, and all four Sub-Invariant 2 min-info fields |
| `surface-fidelity` | 3 of 4 invariants (bullet retention, surface weight, scenario reachability) |
| `task-envelope-coherence` | 3 of 4 signatures, including layer-drift — the doctrine's headline invariant |
| `agents-md-map-conformance` | 3 of 4 named criteria (paragraph shape, link resolution, budget) |
| `complexity-doctrine-links` | anchor resolution and corpus-portability — a `continue` short-circuits both |
| `adr-status-freshness` | the field-signature drift loop — the doctrine's own worked example |
| `invariant-coherence` | the byte-compare only ever sees `x != b""`; real drift detection unproven |
| `insights-shape` | the entire `InsightRecord` schema lock (GHI #358) |
| `session-green-gate` | the `stages: [pre-push]` + `_runs_gz_check` logic, including the GHI #600 fix |
| `fidelity-presence` | 2 of 3 named limbs (empty, malformed) |
| `grader-gaming` | the never-relax floor-membership property; NC proves only a ledger counter |
| `orientation-freshness` | all four wiring-regression checks |
| `line-endings` | `_scan_crlf_surfaces` — self-disables outside a git tree |
| `parity-check` | the template-marker block; pass over-determined by absence findings |
| `format` | gzkit's bound step — entrypoint re-types the ruff command literal |

### TRIVIAL (7)

`skill-audit` · `readiness-audit` · `cli-audit` · `preflight` · `complexity-thresholds` · `dispatch-attestation` · `behave`

Every one returns at a first-guard existence check — `ensure_initialized()`,
a missing manifest, a missing data file — before the named logic runs.
`preflight`, `cli-audit`, `readiness-audit`, and `behave` were empirically
confirmed to exit non-zero for reasons unrelated to their claims.

### UNCLEAR (1)

`lint` — the pass may come from `uv` project/executable resolution failure
rather than from F401. Settle by running the fixture's command in a scratch dir
with a *clean* `.py`: exit 0 confirms ADEQUATE-narrow; non-zero makes it TRIVIAL.

## The five generators

These are not 32 authoring lapses. They are five structural facts.

1. **`_command_fails` accepts any non-zero exit** (`_qc_nc_entrypoints.py:27-31`).
   Cannot distinguish "caught the violation" from "the tool never launched."
   Eight claims route through it.
2. **`_build_empty` supplies a bare directory as the violation**
   (`_qc_negative_controls.py:58`). Eight claims. All audited came back TRIVIAL.
3. **The runner reduces the entrypoint to `bool()`** (`enforcement.py:236`).
   Cannot tell *which* error fired, so a two-arm fixture proves neither arm.
4. **One claim per composite validator.** `surface-fidelity` (4 invariants),
   `task-envelope-coherence` (4 signatures), `waiver-ratchet` (3 mechanisms)
   each register one claim exercising one branch.
5. **Subprocess NCs test the installed wheel, not the working tree** **[verified]**.
   `gz` → `/Users/jeff/.local/share/uv/tools/py-gzkit/bin/gz`. Gutting
   `src/gzkit/` leaves those NCs green.

## The two findings that explain the rest

**`qc-binding`** — the meta-claim covering the NC engine. Registered
(`qc_binding.py:262`) with `_check_theater_signatures` as its entrypoint, not
`audit_qc_binding`. Its fixture returns a `QCStep` self-declaring
`theater_flags=["copy-vs-self"]`, and `THEATER_SIGNATURES` contains
`"copy-vs-self"` — a set-membership test between two literals in the same
module. That module defines `copy-vs-self` as *"Fixture compares content to
itself — tautological assertion."* **The negative control for the theater
detector enacts the theater signature it detects.**

ADR-0.0.73 predicted this in its own pre-mortem — *"detection stayed
declarative… Mitigation baked in: detection is behavioral, not static-shape
matching"* — and the behavioral channel is the one with no NC.

**`enforcement-floor`** — `run_meta_validator(registry=records, root=None)`
passes the registry explicitly, so `_ensure_production_claims_registered()` is
skipped. The ORPHAN class — a claim source that exists but is never discovered,
which is exactly what GHI #648 is open about — is structurally invisible to the
NC that certifies the floor.

## Adjacent finding

`_COVERS_REF_PATTERN` (`traceability.py:47`) matches the `@covers` **decorator**.
The un-waivable REQ-coverage gate confirms a test is *tagged* with a REQ;
nothing inspects whether the test body encodes it. Same present-vs-populated
shape as GHI #692, inside the gate that AGENTS.md says cannot be waived
"because BEHAVIOR's only proof channel is a `@covers` test."

## Prior art

The technique is not novel and should cite its ancestors.

- **Mutation testing** — Lipton 1971; DeMillo, Lipton & Sayward, *"Hints on Test
  Data Selection,"* IEEE Computer 11(4), 1978. The falsification test above is
  statement-block-removal mutation. The floor scores roughly **30%**.
- **Proof testing of safety instrumented systems** (IEC 61508/61511) — the
  closest conceptual ancestor. A guard delivers zero value in normal operation;
  its feared failure is the *dangerous undetected failure*, where every green
  indicator is consistent with a dead guard. The remedy is identical: you cannot
  infer liveness from silence, so supply a real demand in the real installed
  configuration.
- **Detection engineering validation** (Atomic Red Team, MITRE ATT&CK adversary
  emulation) — the closest *software* match, one-to-one with (a)/(b)/(c).

**Naming defect.** In experimental science a *negative control* is a
known-negative that must produce **no** response. A known-violation that must
produce a **detection** is a **positive control**. The current vocabulary uses
one word for both poles, which is why the second pole — known-clean must not
trip — was never expressible. Every claim rated ADEQUATE for a strong reason in
this audit is a two-pole differential.

**What is genuinely novel** and worth claiming narrowly: no prior art asserts,
as a documented invariant, that every "enforced/fail-closed" claim in a
governance surface must carry a paired violation test. The technique is
borrowed; the bookkeeping obligation over a project's own enforcement claims is
gzkit's.

## Routing

Split by the correction-vs-enhancement intent test (operator ruling, 2026-07-18):

| Finding | Route | Why |
|---|---|---|
| The five generators; the 32 fixtures | **GHI — correction** | The shipped apparatus does not fulfil §5's own clauses (a), (b), (c). No new capability. |
| Negative-control pole; cosmic-ray; predicate-as-data; loop attachment; adversarial authoring | **ADR — feature** | Never declared. Belongs to **Movement B**'s feature ADR extending `ADR-0.33.0`. |

Existing cuts: **#698** is the symptom GHI (one reproduction). **#648** is the
enrollment cut (a member with no entry). The generator GHI is the class cut (an
entry that proves less than it appears to). All three may legitimately close
`superseded` against one destination.

**Tooling note for the ADR:** `mutmut` hardcodes pytest (`PytestRunner`
constructed directly, no runner config key) and is therefore disqualified under
the stdlib-first doctrine and the operator's standing "never pytest" ruling.
`cosmic-ray` takes an arbitrary shell command and ships
`test-command = "python -m unittest discover tests"` as its own canonical
example. Adopt it **scoped to enforcement modules as a diagnostic, with no
repo-wide score floor** — Google's *Practical Mutation Testing at Scale* (IEEE
TSE 2022) reports 85% of raw mutants judged unproductive, and warns that a
kill-every-mutant mandate manufactures change-detector tests, which
AGENTS.md § DO IT RIGHT #6 already forbids.
