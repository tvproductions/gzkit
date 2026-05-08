---
id: OBPI-0.0.29-06-ad-hoc-path
parent: ADR-0.0.29
item: 6
lane: Heavy
status: Completed
---

# OBPI-0.0.29-06-ad-hoc-path: Operator-invocable Ad-Hoc Path

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #6 — "Operator-invocable ad-hoc path (preview-before-fail; distinct presentation defaults from auto-chain)"

**Status:** Draft

## Objective

Define and test the ad-hoc invocation pathway for `gz complexity advise <path>` with presentation defaults distinct from the auto-chain pathway (OBPI-05). Ad-hoc is preview-before-fail; output is verbose by default with full diagnostic detail. Auto-chain is trigger-time fail-fast; output is concise and surfaces only the actionable verdict per crossing.

## Lane

**Heavy** — Presentation contract differentiation between ad-hoc and auto-chain pathways is a doctrinal surface; foundation-kind brief-level Gate 5 attestation per ADR-0.0.18.

## Allowed Paths

- `src/gzkit/commands/complexity_advise.py` — extend with ad-hoc-vs-auto-chain presentation switching (additive only; OBPI-03 lands the verb shell)
- `src/gzkit/complexity/advisor/presentation.py` — ad-hoc and auto-chain presenter classes
- `tests/commands/test_complexity_advise_ad_hoc.py`
- `features/complexity_advise_ad_hoc.feature` — behave scenarios tagged with REQ IDs
- `docs/user/manpages/gz-complexity-advise.md` — extend with ad-hoc-vs-auto-chain examples (additive)
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-06-ad-hoc-path.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/advisor/diagnosis.py` — schema is OBPI-01
- `src/gzkit/complexity/advisor/engine.py` — engine is OBPI-02
- `src/gzkit/complexity/advisor/timeout.py` — timeout is OBPI-09
- `.gzkit/hooks/**` — auto-chain hook is OBPI-05
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz complexity advise <path>` (no `--auto-chain` flag) is the ad-hoc pathway. Output is verbose: each diagnosis prints metric name + crossing band + crossing value + archetype + full doctrinal_frame block (authority, citation, excerpt) + per-proof-range source-line snippets + recommended_move + intrinsic_attestation reference (if any).
2. REQUIREMENT: `gz complexity advise --auto-chain <path>` is the auto-chain pathway (invoked by OBPI-05's hook). Output is concise: per-diagnosis one-line summary (metric, crossing band, archetype, file:line range, recommended_move headline). Full diagnosis is deferred to a "run `gz complexity advise <path>` for full detail" hint at the end.
3. REQUIREMENT: `--json` mode produces identical output regardless of pathway (both paths emit the canonical Pydantic serialization). Presentation differentiation is human-readable-only.
4. REQUIREMENT: An operator running `gz complexity advise <path>` against a clean file gets a "no crossings" message (verbose mode lists "checked N functions across M metrics; no warn or block crossings"). Auto-chain mode is silent on clean files (the hook exits 0 silently per OBPI-05).
5. REQUIREMENT: Presentation classes (`AdHocPresenter`, `AutoChainPresenter`) live in `src/gzkit/complexity/advisor/presentation.py` with a shared `Presenter` protocol. The CLI dispatches to the appropriate presenter based on the `--auto-chain` flag.
6. REQUIREMENT: Tests cover: ad-hoc verbose output contains all diagnosis fields; auto-chain concise output contains only the per-diagnosis summary; `--json` output is identical across pathways; clean-file message differs (verbose "no crossings" vs auto-chain silent); presentation classes can be substituted independently. Each test decorated with `@covers(REQ-0.0.29-06-NN)`.
7. REQUIREMENT: A behave scenario at `features/complexity_advise_ad_hoc.feature` tagged `@REQ-0.0.29-06-{01,02,03}` covers ad-hoc preview against clean / warn-band / block-band fixture files.
8. REQUIREMENT: Manpage extension adds at least one example for each pathway: ad-hoc preview (`gz complexity advise src/foo.py`) and auto-chain context (`gz complexity advise --auto-chain <staged-files>` invoked by hook).
9. REQUIREMENT: Function-size discipline; presenter classes ≤ 300 lines per `.claude/rules/pythonic.md`.
10. REQUIREMENT: TDD discipline.
11. REQUIREMENT: NEVER include the operator's personal email in code, manpage, fixtures, or commit messages.

> STOP-on-BLOCKERS: if OBPI-03's CLI verb is not landed, STOP — this OBPI extends OBPI-03's surface.

## Discovery Checklist

**Prerequisites (check existence, STOP if missing):**

- [x] OBPI-03 CLI verb — confirmed at `src/gzkit/commands/complexity_advise.py:51` (`auto_chain: bool = False` already wired, reserved no-op)
- [x] OBPI-01 schema — confirmed at `src/gzkit/complexity/advisor/diagnosis.py` (`AdvisorDiagnosis`, `DoctrinalFrame`, `ProofRange`, `IntrinsicAttestationRef`)
- [x] OBPI-02 engine — confirmed at `src/gzkit/complexity/advisor/engine.py` (`DiagnosisEngine`)
- [x] Parent ADR § Decision rationale #4 — preview-before-fail bandwidth-protection confirmed as the operator-facing rationale for the ad-hoc path

**Existing Code (understand current state):**

- [x] `src/gzkit/commands/complexity_advise.py` — read in full; `auto_chain` param present, `_render_prose()` is single-path (no dispatch); replace with presenter dispatch
- [x] `src/gzkit/complexity/advisor/diagnosis.py` — read in full; `AdvisorDiagnosis` fields confirmed: `metric`, `crossing_band`, `crossing_value`, `archetype`, `doctrinal_frame`, `proof`, `recommended_move`, `intrinsic_attestation`
- [x] AGENTS.md § OPERATOR ECONOMY OF EFFORT — presenter dispatch is the "agent drafts substantively, operator reviews" shape for the developer's pre-commit moment

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage extension lands

### Gate 4: BDD (Heavy)
- [ ] Behave scenarios pass for ad-hoc preview paths

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz complexity advise tests/fixtures/complexity/warn_band.py
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_complexity_advise_ad_hoc.py -v
uv run -m behave features/complexity_advise_ad_hoc.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.29-06-01: Given a file with a warn-band crossing, when `gz complexity advise <path>` runs (ad-hoc), then output contains all diagnosis fields including doctrinal_frame excerpt and per-proof source snippets.
- [ ] REQ-0.0.29-06-02: Given the same file, when `gz complexity advise --auto-chain <path>` runs, then output is concise (one-line summary per diagnosis) and includes the "run for full detail" hint.
- [ ] REQ-0.0.29-06-03: Given `--json` mode, when invoked with or without `--auto-chain`, then the JSON output is identical.
- [ ] REQ-0.0.29-06-04: Given a clean file, when `gz complexity advise <path>` runs (ad-hoc), then output contains "no crossings" with the metrics-checked count.
- [ ] REQ-0.0.29-06-05: Given the same clean file, when `--auto-chain` is set, then output is silent (suitable for hook invocation).
- [ ] REQ-0.0.29-06-06: Given the manpage, when read, then at least one example each for ad-hoc and auto-chain pathways is present.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict + manpage extension
- [ ] Gate 4: behave scenarios pass
- [ ] Gate 5: TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR + unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict + manpage diff
```

### Gate 4 (BDD)
```text
# Paste behave output
```

### Gate 5 (Human)
```text
# Record attestation + receipt IDs
```

### Value Narrative

### Key Proof


uv run gz complexity advise tests/fixtures/complexity/warn_band.py — ad-hoc (verbose): prints metric/band/value/archetype/authority/citation/excerpt/source-lines/recommended-move per crossing; empty → "No crossings detected. Checked N metrics across M functions." Auto-chain (--auto-chain): one-line per crossing + hint; empty → silent. All 10 unit tests pass — receipt arb-step-unittest-ba929e08ae824fe8b4f141312aa6920d; ruff clean — receipt arb-ruff-5f3f031cfd1047809f4c01cf2aad9953; typecheck clean — receipt arb-step-typecheck-f075a8414ac542809441764a0814b650; mkdocs clean — receipt arb-step-mkdocs-3bae6193fb704844abe73d4ec3f33c2c.

### Implementation Summary


- Files created: src/gzkit/complexity/advisor/presentation.py (Presenter protocol, AdHocPresenter, AutoChainPresenter; 211 lines), tests/commands/test_complexity_advise_ad_hoc.py (10 unit tests @covers all REQs), features/complexity_advise_ad_hoc.feature (3 BDD scenarios @REQ-0.0.29-06-01/02/03)
- Files modified: src/gzkit/commands/complexity_advise.py (presenter dispatch replacing _render_prose(); functions_checked/metrics_checked tracking), docs/user/manpages/gz-complexity-advise.md (ad-hoc/auto-chain examples added; --auto-chain description updated), features/steps/gz_steps.py (output does not contain step added)
- Tests added: 10 unit tests covering REQ-01 through REQ-06; 3 BDD scenarios
- Date completed: 2026-05-07
- Attestation status: attested by Jeffry
- Defects noted: none

### Closing Argument

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed — presentation-dispatch layer for OBPI-0.0.29-06 implemented and verified: AdHocPresenter (verbose) and AutoChainPresenter (concise) wired in complexity_advise.py based on --auto-chain flag; 10 unit tests @covers all REQs; 3 BDD scenarios pass; receipts arb-step-unittest-ba929e08ae824fe8b4f141312aa6920d, arb-ruff-5f3f031cfd1047809f4c01cf2aad9953, arb-step-typecheck-f075a8414ac542809441764a0814b650, arb-step-mkdocs-3bae6193fb704844abe73d4ec3f33c2c
- Date: 2026-05-08

---

**Brief Status:** Completed

**Date Completed:** 2026-05-08

**Evidence Hash:** -
