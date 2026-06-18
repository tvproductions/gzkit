# Plan: OBPI-0.0.73-08 Fidelity-Presence Enforcement

**OBPI:** OBPI-0.0.73-08-fidelity-presence-enforcement
**Parent:** ADR-0.0.73-verification-layer-binding-audit (checklist item #8, mechanizes Boundary Invariant #4)
**Lane:** heavy | **Sensitivity:** security (additive; discharge floor at completion if false-positive)

## Destination-in-mind (plan-audit disclosure)

The OBPI-04 adversarial audit proved an ADR with no `## Fidelity Assertions` block
reaches VALIDATED through closeout AND audit on a stderr warning — so BI #4 is
prose-only and "VALIDATED = thesis exercised" is false for every block-less ADR.
The fix: a new `gz validate --fidelity-presence` scope, fail-closed, wired into
`gz check`, grandfathering today's block-less ADRs so the gate goes green now while
fail-closing on NEW ones.

## Rejected alternatives

1. **Make presence a closeout-only check** (extend OBPI-04's ceremony gate) — rejected: closeout runs once per ADR and the absence policy already swallows it; a `gz check` validator scope catches it on every run and across the whole corpus, which is where the bypass lives.
2. **Hard-fail all block-less ADRs immediately (no grandfather)** — rejected: flips `gz check` red across the entire existing foundation corpus at once. The grandfather-cutover precedent (sensitivity-floor) is the honest path: visible debt, fail-closed on new.
3. **Park the new gz-check step in `_NEGATIVE_CONTROL_DEBT`** — rejected: this scope has a clean negative control (a block-less fixture ADR it MUST flag). Parking it in debt would make OBPI-08 itself green-by-emptiness — the exact thing we just spent the session killing. Wire a genuine NC; make it the 2nd honestly-bound step.

## Steps (TDD per increment)

### Step 1: Validator module — `src/gzkit/governance/trust_audits/fidelity_presence.py`
- `audit_fidelity_presence(project_root, *, grandfather=None) -> list[ValidationError]`
- Walk non-pool ADR Decisions: `docs/design/adr/{foundation,pre-release}/**/ADR-*.md` (exclude `docs/design/adr/pool/**`).
- For each, attempt `parse_fidelity_assertions` (reuse `src/gzkit/fidelity.py`). "Parseable block" = returns ≥1 assertion without raising. Absent/empty/malformed → finding, UNLESS the ADR id is in the grandfather set.
- Three-part recovery prose per `.gzkit/rules/guardrail-feedback-prose.md`.
- RED first: `tests/governance/test_fidelity_presence.py` asserting block-less fixture → 1 finding; compliant fixture → 0; grandfathered block-less → 0; new block-less (not grandfathered) → 1.

### Step 2: Grandfather data file — `data/fidelity_presence_grandfather.json`
- Compute today's block-less non-pool ADR ids (run the validator with empty grandfather, collect findings) and enumerate them with a header comment routing to the back-fill sweep (ADR-0.0.73 Consequences #3).

### Step 3: CLI registration — `src/gzkit/commands/validate_cmd.py`
- Add `--fidelity-presence` flag + `_run_fidelity_presence_scope`, mirroring `_run_qc_binding_scope`: print findings, `sys.exit(3)` on any, exit 0 clean.

### Step 4: Wire into `gz check` — `src/gzkit/commands/quality.py`
- Add `("Fidelity presence", run_fidelity_presence_audit)` to `_build_check_steps()`; `run_fidelity_presence_audit` shells `uv run gz validate --fidelity-presence` (mirror `run_qc_binding_audit`).

### Step 5: Classify + wire NC — `src/gzkit/qc_binding.py` + `trust_audits/qc_binding.py`
- Add `"Fidelity presence": ("audit", "docs/", "bound", "python_function")` to `_STEP_CLASSIFICATION` (else `build_qc_registry()` KeyErrors).
- Register a genuine NC: callable runs `audit_fidelity_presence` against a block-less fixture ADR and returns non-zero (caught) → bound. NOT added to `_NEGATIVE_CONTROL_DEBT`.

### Step 6: ADR template stub — `.gzkit/templates/adr.md`
- Seed a `## Fidelity Assertions` section with a one-row example table so new ADRs carry the block by construction.

### Step 7: ADR fidelity-assertion row — the ADR file
- Add a row: `| Fidelity-presence enforcement exists and is wired into gz check, fail-closed (OBPI-08). | uv run gz validate --fidelity-presence | 0 |` so verb + assertion land together and `gz adr fidelity ADR-0.0.73` stays green.

### Step 8: Manpage — `docs/user/manpages/validate.md`
- Document `--fidelity-presence`. Confirm `gz cli audit` green.

### Step 9: BDD scenario — `features/`
- One `@REQ-0.0.73-08-01` scenario: block-less ADR fixture → `gz validate --fidelity-presence` exits 3.

## Verification
```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --fidelity-presence
uv run gz validate --qc-binding
uv run gz adr fidelity ADR-0.0.73-verification-layer-binding-audit
uv run gz cli audit
uv run -m behave --tags=@REQ-0.0.73-08-01 features/
```

## Notes
- Grandfather honesty (REQ-08-03 NEVER clause): the file enumerates EXISTING block-less ADRs only; a new block-less ADR must fail, never be added to silence it.
- Coupling: Step 5 ties into OBPI-01's `_STEP_CLASSIFICATION` (the hand dict the audit flagged) — adding the classification entry is required for the new gz-check step; the OBPI-01 classifier-is-hand-authored finding is a separate tracked correction, not re-litigated here.
