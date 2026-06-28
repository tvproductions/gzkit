# Plan: Build the static theater-signature analyzer (ADR-0.0.73 channel 1, GHI #657)

## Context

ADR-0.0.73 ("verification-layer-binding-audit") is gzkit's antibody against
*theater* QC steps — checks that look like they enforce something but don't. It
was designed with **two channels** (`ADR-0.0.73...md:59`):

- **Channel 2 (behavioral, primary):** each bound step ships a negative-control
  fixture it MUST fail on; `--qc-binding` runs it in production config and flags
  any step that doesn't catch its own violation. This works today (verified this
  session: meta-validator = 41 claims, 0 facades).
- **Channel 1 (static, "layered on top"):** scan source for the 7 theater
  signatures calibrated on the ADR-0.0.37 facade. This is **inert** —
  `_check_theater_signatures` (`trust_audits/qc_binding.py:100-119`) iterates
  `step.theater_flags`, but every production step is built with
  `theater_flags=[]` (`qc_binding.py:149,198`). The static analyzer that would
  populate flags from real source was deferred to OBPI-0.0.73-02, which was
  **repudiated and never rebuilt**.

Per the operator's correction-vs-enhancement doctrine ("discovering that more is
needed to fulfil the intent of a feature is not an enhancement, it is a
correction"), the gap is a **correction**: build the missing analyzer so channel
1 fires on real source, fulfilling ADR-0.0.73's deliberate two-layer design.
Tracked by **GHI #657**; direct-fix path under the owning ADR (no new OBPI).

**Outcome:** `theater_flags` becomes a *derived* value (scanned from source, not
self-declared), channel 1 catches the structurally-decidable facade shapes, and
the analyzer is bound by its own §5 live negative control so it cannot rot.

## Scope decision (operator-ratified 2026-06-28)

**Detect 3 signatures statically; defer 4 to channel 2.** A static detector for
the semantic signatures would itself grade by keyword/prose shape — reintroducing
the exact GHI #624 facade the antibody exists to kill.

| Signature | Disposition | Reason |
|---|---|---|
| `copy-vs-self` | **DETECT** | Tautological self-equality is a pure AST fact (`ast.dump(left)==ast.dump(right)`). |
| `mtime-where-name-says-content` | **DETECT** | Concrete node anchor (`.st_mtime`/`getmtime`); provably 0 FP on current tree. |
| `skip-if-PASS` | **DETECT** (gated on 0-FP regression) | Structurally describable; ship only if real-tree scan yields zero false positives. |
| `prose-graded-by-nothing` | **DEFER → channel 2** | "Prose never machine-verified" is a whole-program reachability property; static heuristic flags every formatter. |
| `shape-graded-not-substance` | **DEFER → channel 2** | Static detection = keyword-matching the source = the GHI #624 facade itself. |
| `empty-input-passes` | **DEFER → channel 2** | Behavioral; already proven by `_build_empty(...)` NC fixtures (`_qc_negative_controls.py:58`). |
| `fixture-only` | **DEFER → channel 2** | Genuineness already structurally enforced by channel 2's un-forced-NC contract. |

## Files to change

**New:**
- `src/gzkit/models/theater_signatures.py` — frozen `TheaterSignatureFinding`
  Pydantic model `{signature, file_path, line_number, function_name, evidence}`.
  Mirror `src/gzkit/models/tautological_tests.py` conventions.
- `src/gzkit/governance/trust_audits/theater_signature_scan.py` — the analyzer.
  `ast.parse` + `ast.walk` + `isinstance` (reuse `tautological_tests.py` pattern,
  stdlib `ast` only). Contains: `_SELF_EXCLUSION` (the detector, the NC fixture
  modules — they plant violations on purpose), one `_detect_<sig>(fn_node, rel)`
  per detected signature (each ≤50 lines), `scan_source_for_signatures(path, rel)`,
  `scan_validator_tree(root, files)`, and `_STEP_SUBJECT_SOURCE` (bound
  python_function step-id → validator source path(s); subprocess steps → `()`;
  fail-closed coverage like the `KeyError` sentinel at `qc_binding.py:182`).

**Edit:**
- `src/gzkit/governance/trust_audits/qc_binding.py` — in `audit_qc_binding`
  (`:166-192`), replace the bare `_check_theater_signatures(step)` call (`:168`)
  with: scan the step's subject source → `step.model_copy(update={"theater_flags":
  [...]})` → run the existing renderer (now LIVE) + emit file:line findings as
  three-part guardrail-feedback prose. Remove the `ARG001` noqa on `project_root`
  (`:128`) — it's now used. Channel 2 (`_run_single_claim`, `:184-191`) untouched.
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — add
  `_build_theater_signature_scan()` fixture (plants a realistic violation:
  `def verify_content_freshness(p): return p.stat().st_mtime`) and a table tuple
  `("theater-signature-scan", _build_theater_signature_scan, _ep._ep_theater_signature_scan)`
  to `_QC_NEGATIVE_CONTROL_TABLE` (`:486`). `_KNOWN_QC_CLAIM_IDS` auto-grows.
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` — add
  `_ep_theater_signature_scan(root) -> list[TheaterSignatureFinding]` running the
  scanner on the planted file; non-empty = PASS-on-violation.

**Tests (TDD — RED first):**
- New: `tests/governance/test_theater_signature_scan.py` — per-signature detect
  tests + FP guards: `a==a` flagged, `a!=a` not (NaN idiom), `f()==f()` not
  (purity guard), `.st_mtime` in a `verify_content_freshness` flagged,
  **`st_mtime` in a docstring NOT flagged** (models `rendition_freshness.py:8`),
  `.st_mtime` in `rotate_logs` not flagged (name-narrowing). Plus the
  **load-bearing real-tree zero-FP regression**: `scan_validator_tree` over the
  current trust_audits tree → `[]`.
- Edit `tests/governance/test_qc_binding.py::test_theater_flags_empty_for_all_steps`
  (`:159`) — keep the build-time `[]` assertion, drop the "OBPI-02 not yet"
  docstring, add a sibling asserting audit-time derivation (planted source →
  populated `theater_flags`).
- Edit `tests/governance/test_facade_regression_corpus.py` — add source-level
  fixtures for the 3 detected signatures (existing 7 renderer fixtures stay).
- Edit `tests/governance/test_enforcement_meta_validator.py:511` — bump expected
  claim count (`>= 37` → `>= 38`).

## Key risk + mitigation

**The analyzer's own theater failure mode:** detectors tuned so tightly (to force
0 FP on the clean tree) that they match only the planted NC and nothing real —
every gate green, zero protection (the ADR's own pre-mortem, `:133`). Mitigations:
(1) NC fixture plants the *real facade shape*, not a degenerate one; (2) each
detector's pattern cites a *named real exemplar* (mtime ← the repudiated
`rendition_freshness` tautology; copy-vs-self ← the ADR-0.0.37 fixture==fixture
facade) — no detector ships without one; (3) the four semantic signatures are
scoped OUT in code comments, refusing to build the keyword-grader facade.

## Verification

```bash
uv run -m unittest -q                                          # all green, RED→GREEN per signature
uv run gz arb step --name unittest -- uv run -m unittest -q    # attestation receipt
uv run gz validate --qc-binding                                # exit 0 on clean tree
uv run python -c "from gzkit.enforcement import run_meta_validator; r=run_meta_validator(); print(r.verified_count, r.facade_count)"  # 42, 0
uv run gz check                                                # full floor green
```

Then: `fix(qc-binding): build static theater-signature analyzer (GHI #657)` with
`Task:` trailer + ARB receipt IDs; close GHI #657 `fixed` citing the SHA; update
the GHI framing from "retire" to "build analyzer" before close.

## Out of scope

- Removing the `theater_flags` field or retiring channel 1 (the original
  state-of-gzkit framing — superseded by the operator's build ruling).
- The 4 deferred semantic signatures (owned by channel 2).
- Any change to channel 2 / `_run_single_claim`.
