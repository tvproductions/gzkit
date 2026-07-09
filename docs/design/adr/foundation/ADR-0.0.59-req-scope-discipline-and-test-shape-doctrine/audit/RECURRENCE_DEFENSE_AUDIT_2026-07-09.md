# ADR-0.0.59 Recurrence-Defense Audit — Unit-Testing Doctrine

**Date:** 2026-07-09
**Tracker:** GHI #571 (umbrella recurrence-defense tracker)
**Supersedes the findings of:** `FOLLOW_UP_UNIT_TESTING_DOCTRINE_2026-05-31.md` (six weeks stale; three of its findings have changed status)
**Method:** every claim below re-verified against the working tree at commit `969cce84`. Prior-receipt claims were treated as hypotheses, not evidence.

---

## Executive finding

The doctrine (ADR-0.0.59) is correct and the *growth* gate holds. Recurrence defense is **not** proven end to end, but the gap is narrower and different from what the 2026-05-31 receipt described.

Three of that receipt's six findings do not survive contact with today's code:

| Finding | 2026-05-31 status | 2026-07-09 verified status |
|---|---|---|
| F1 — ADR-0.0.59 is the right design | holds | **holds** |
| F2 — hot-path rule weaker than doctrine | open | **partially open** (see § F2) |
| F3 — `gz-obpi-pipeline` pressures misuse | open | **open, and now self-contradictory** (see § F3) |
| F4 — completion layer ignores REQ kind | open | **STALE — the allegation is false today** (see § F4) |
| F4b (new) — `--accept-uncovered` waives BEHAVIOR | not identified | **CONFIRMED, and it is GHI #537's real core** |
| F5 — scanner has no inventory mode | open | **open; its stated evidence was fictional** (see § F5) |
| F6 — no output/render advisory scanner | open | **open, ABSENT** (see § F6) |

**The single most important correction:** the previous receipt reasoned from a `by_disposition` inventory containing "hundreds of `convert`, `replace-with-ledger`, and `fold-to-validator` candidates," and from an "1,846-hit output/render screen." **`by_disposition` does not exist anywhere in this codebase**, and no output/render scanner exists to have produced 1,846 hits. Those numbers were never derivable from the shipped scanner. Acting on them would have sized a cleanup campaign against a phantom.

The real numbers, measured today, are an order of magnitude smaller (§ 2).

---

## 1. Control-surface audit (GHI #571 deliverable 1)

Scope read: `.gzkit/rules/tests.md` (v0.10.0), `docs/governance/tests-rationale.md`, `docs/governance/req-scope-discipline.md`, `AGENTS.md`, `.gzkit/skills/**`.

### F2 — hot-path rule vs. doctrine

The four wording blocks the prior receipt recommended, judged against **today's** `.gzkit/rules/tests.md`:

| Block | Status | Evidence |
|---|---|---|
| (a) Unit-test purpose | **PARTIAL** | `tests.md:48` carries "Tests assert semantics, not strings"; the clause that a unit test does not preserve implementation *structure* or *prose* exists only in `req-scope-discipline.md:35-38` |
| (b) No pytest | **PARTIAL** | `tests.md:16` — "Use stdlib `unittest`; no pytest." The enumerated forms (fixtures, parametrization, plugins, bare pytest asserts) appear nowhere |
| (c) Proof-channel routing | **PRESENT** for routing; **PARTIAL** for the negative | `tests.md:106-110` + `122-126` carry the taxonomy and matrix. The prohibition `tests.md:133-134` names **SUPPORT only**: "no `@covers` test is required or appropriate for them — authoring one is the anti-pattern this rule names." **STRUCTURAL-FENCE is never joined to that prohibition.** |
| (d) String/output assertions | **PARTIAL** | `tests.md:52` carries the fixture-class carve-out. The positive enumeration (structured fields, domain objects, state transitions, exception types, ledger fields, parsed values) is absent |

**The load-bearing defect is not missing prose — it is a missing classifier.** `tests.md` states the categories; the *operational discriminator an agent would actually apply* lives only in the governance doc:

- `req-scope-discipline.md:81-82` — "A test that `grep`s a production doc for the presence of a substring is NOT a BEHAVIOR proof."
- `req-scope-discipline.md:111` — the concrete `subprocess.run(["grep", "-q", ...])` "is NOT a SUPPORT proof" example.
- `req-scope-discipline.md:144-160` — the disposition matrix (`grep for presence of subsection heading → Delete`; `Render-form fixture test → Keep`).

`tests.md:48` "Tests assert semantics, not strings" is **slogan-shaped**: memorable, and supplying no test by which an agent decides whether a given assertion is a string-echo or a semantic check. That is exactly F2's claim, and it survives — but the remedy is to lift the *classifier*, not to add more prose.

Neither v0.9.0 (GHI #636) nor v0.10.0 (GHI #647) touched (a), (b), (d), or the STRUCTURAL-FENCE negative. Both revisions addressed the behave gate and the SUPPORT ledger arm.

### F3 — skill-layer pressure, now self-contradictory

`.gzkit/skills/gz-obpi-pipeline/SKILL.md` (v6.27.0) contains **three mutually inconsistent statements** about which REQs need a `@covers` test:

| Line | Text | Implies |
|---|---|---|
| 434 (Phase 1b) | "Every REQ defined in the brief MUST be reachable from a `@covers` reference in the test tree." | every REQ |
| 641 (Stage 4) | "The `@covers location` column is **not** optional." | every REQ |
| 456 (Phase 1c) | "For each **BEHAVIOR** REQ … (SUPPORT and STRUCTURAL-FENCE REQs are exempt by proof channel — they carry no `@covers` test)" | BEHAVIOR only |

Phase 1c was added on 2026-07-09 under GHI #642. It is correct and it agrees with ADR-0.0.59 — but it now sits beside two instructions that contradict it. **The contradiction did not originate with #642; #642 sharpened a latent inconsistency into an explicit one.** An agent reading Stage 4 will still fill a `@covers location` cell for a SUPPORT REQ, because the template says the cell is not optional.

`SKILL.md:633-635` also still offers a filesystem-existence check as a *Test Coverage* example:

```
# req-01:absence-check — REQ-X.Y.Z-NN-01 Test Coverage
test ! -e <path>
```

This is the exact shape ADR-0.0.59 exists to prohibit, presented as an exemplar.

The full three-channel doctrine *is* correctly authored — in a different skill (`gz-obpi-specify/SKILL.md:240-248`). The pipeline skill never learned it.

**Sibling offender:** `gz-tech-debt-review/SKILL.md:91,114` flags "REQs without `@covers`" as debt and "missing `@covers` on a Completed/Validated heavy brief" as a *Critical* finding — with no BEHAVIOR-only qualifier. It will report SUPPORT REQs as critical debt for correctly having no unit test.

---

## 2. Ineffective-test inventory (GHI #571 deliverable 2)

Measured with the shipped scanner (`gzkit.tautological_tests.scan_test_tree`) against `tests/` at `969cce84`:

```
tautological-shaped operations in tests/ : 70
   convert                  45
   fold-to-validator        14
   replace-with-ledger      11

baseline entries : 91
waived           : 3 ops across 2 files
```

Top-flagged files:

| Count | File |
|---|---|
| 7 | `tests/governance/test_security_surfaces_registry.py` |
| 6 | `tests/eval/test_datasets.py` |
| 6 | `tests/scripts/test_backfill_adr_taxonomy.py` |
| 5 | `tests/test_doc_coverage.py` |
| 4 | `tests/arb/test_schemas.py` |

### The baseline carries 21 slots of slack

```
current ops                       : 70
baseline entries                  : 91
stale (in baseline, absent on disk): 21
new (on disk, absent from baseline): 0
```

`data/tautological_test_baseline.json` is registered in `data/waiver_ratchet_registry.json` as a **shrink-ratchet** at `baseline_count: 91`. Only 70 operations exist. **Twenty-one entries are stale** (their tests were deleted or renamed), and the ratchet therefore permits 21 *new* tautological tests before it ever fires.

This is the precise failure the ratchet doctrine names — a baseline above the real count is slack an agent can grow into. The remedy is mechanical and lossless: regenerate the baseline from the current scan (91 → 70) and ratchet `baseline_count` to match. No protection is lost; every genuinely new operation is still flagged.

### Prior-receipt numbers, corrected

| Prior claim | Reality |
|---|---|
| "hundreds of `convert`, `replace-with-ledger`, `fold-to-validator` candidates" in `by_disposition` | 70 total. `by_disposition` **does not exist** in the codebase (zero grep hits) |
| "the broader 1,846-hit output/render screen" | No such screen exists. Today's raw counts: `result.output` 777, `.getvalue()` 188, `assertRegex` 97, `assertMultiLineEqual` 0, across 125 files |

---

## 3. REQ → `@covers` pressure analysis (GHI #571 deliverable 3)

**Does the taxonomy still push agents toward tautological tests?** At the runtime layer, no. At the skill layer, yes.

### F4 — the completion gate is fixed (allegation is stale)

`src/gzkit/commands/obpi_complete.py:597-604` filters by kind *before* discovery:

```python
for req in reqs:
    if req_kinds.get(req, "BEHAVIOR") in ("SUPPORT", "STRUCTURAL-FENCE"):
        continue
    refs = discover_covers(req, tests_root, features_root=features_root)
```

A tagged SUPPORT or STRUCTURAL-FENCE REQ with no `@covers` test does **not** block `gz obpi complete`. The defense is real but **tag-dependent**: `parse_brief_req_kinds` only maps REQs carrying an explicit inline `[kind]` tag, and the `.get(req, "BEHAVIOR")` default means an *untagged* SUPPORT REQ is still treated as BEHAVIOR and still demands a test. That default is fail-closed and correct; the residual pressure is on brief authors to tag.

### F4b — `--accept-uncovered` waives exactly the kind that must not be waivable

This was not identified in the prior receipt and is the sharper statement of GHI #537.

`_apply_uncovered_waivers` (`obpi_complete.py:487-540`) applies no kind check:

```python
accepted_set = set(accept_uncovered)
waivable = accepted_set & set(gaps)
```

Because SUPPORT and STRUCTURAL-FENCE REQs were already `continue`d out of the coverage loop at line 598, **the only REQs that can ever appear in `gaps` are BEHAVIOR REQs.** Therefore `--accept-uncovered` waives *precisely and exclusively* BEHAVIOR REQs — the one kind GHI #537 states must never be waivable. The heavy/foundation TTY `ACCEPT` confirmation (`_enforce_uncovered_acceptance_confirmation`, line 510) is a confirmation gate, not a kind gate.

This belongs to **GHI #537**, which remains open. It should be re-stated there in this sharper form.

---

## 4. Recommended wording changes (GHI #571 deliverable 4 — diagnosis only, not landed)

### 4.1 `.gzkit/rules/tests.md` — lift the *classifier*, not more prose

The rule already carries the taxonomy. What it lacks is the operational discriminator. Recommended additions, in the rule's existing register:

> **Unit-test purpose.** A gzkit unit test is a stdlib `unittest.TestCase` check of one required code behavior. It is fast, isolated, deterministic, and fails when the behavior contract breaks. It does not preserve current implementation structure, current prose, or current rendered output — unless that exact output form is the named behavior contract.
>
> **The discriminator.** Ask: *if the production code's behavior changed but its text did not, would this test fail?* If no, it is not a BEHAVIOR proof. A test that `grep`s a production doc for a substring, or asserts a file exists, proves content, not behavior.
>
> **Proof-channel routing.** BEHAVIOR REQs use `@covers` tests. SUPPORT REQs use ledger event plus structural validator proof. STRUCTURAL-FENCE REQs use parent-ADR boundary invariants. **Do not add a unit test merely to make a SUPPORT or STRUCTURAL-FENCE REQ appear covered.**
>
> **String/output assertions.** Prefer structured fields, domain objects, state transitions, exception types, ledger event fields, and parsed values. Assert exact strings or table markers only when rendering behavior is the named contract, and keep those tests in dedicated output-form fixture classes.
>
> **No pytest.** No pytest syntax, fixtures, parametrization, plugins, or bare pytest-style assertions. Use `unittest`, `unittest.mock`, and stdlib fixtures such as `tempfile.TemporaryDirectory()`.

The "discriminator" paragraph is the load-bearing addition. It is the one thing an agent can *apply*.

### 4.2 `gz-obpi-pipeline/SKILL.md` — resolve the contradiction

Phase 1b (line 434) and the Stage 4 evidence template (line 641) must become proof-channel-specific, matching Phase 1c (line 456):

> The proof-location column is proof-channel specific, not always `@covers`. For BEHAVIOR REQs, cite the `@covers` test location. For SUPPORT REQs, cite the ledger event type/path and the structural validator scope. For STRUCTURAL-FENCE REQs, cite the parent-ADR `## Boundary Invariants` anchor. A missing BEHAVIOR `@covers` location is a blocker; **a non-BEHAVIOR REQ must never be forced into a unit test to fill the cell.**

Delete the `test ! -e <path>` Test-Coverage exemplar (lines 633-635). It teaches the prohibited shape.

### 4.3 `gz-tech-debt-review/SKILL.md`

Qualify lines 91 and 114 with "BEHAVIOR REQs without `@covers`". As written the skill reports correct SUPPORT REQs as Critical debt.

---

## 5. Detection and gating recommendations (GHI #571 deliverable 5)

| # | Recommendation | Shape | Risk |
|---|---|---|---|
| R1 | **Ratchet the tautological baseline 91 → 70** and update `waiver_ratchet_registry.json` | mechanical, lossless | none — no protection lost, 21 phantom slots closed |
| R2 | **Resolve the `gz-obpi-pipeline` contradiction** (§ 4.2) | skill wording + sync | none |
| R3 | **Lift the discriminator into `.gzkit/rules/tests.md`** (§ 4.1) | control-surface wording + sync | none |
| R4 | **Add scanner inventory mode** — `gz tautological-inventory --json`, exposing per-op disposition and a `by_disposition` roll-up that does not currently exist | new read-only CLI surface | low; advisory, never gating |
| R5 | **Add an advisory output/render assertion screen** — start advisory-only; require an explicit `# output-contract: <reason>` marker or a dedicated fixture class name before any fail-close | new scanner | medium — 125 files hit; must not fail-close before markers exist |
| R6 | **Re-state GHI #537 in the F4b form** — `--accept-uncovered` waives exactly BEHAVIOR REQs because non-BEHAVIOR REQs never reach `gaps` | comment on #537 | none |

R1–R3 are safe to land immediately. R4 and R5 are new capability. R6 belongs to #537.

**Do not fail-close on output/render assertions before markers exist.** 777 `result.output` assertions are not 777 defects — many are legitimate CLI render-contract tests, permitted by `tests.md:52` and by `tool-skill-runbook-alignment.md` § Invariant 3. A fail-closed gate here would redden a green trunk against tests the doctrine explicitly allows. This is the prior receipt's F6 judgment, and it is correct.

---

## 6. Answers to the prior receipt's Operator Decisions Requested

1. **Cleanup wave order?** Neither, as stated. The inventory is 70 operations, not "hundreds." Wave 1 should be the *baseline ratchet* (R1), which is mechanical. Only then does a content sweep have a stable denominator.
2. **Output-contract marker?** Yes — but the marker must precede the scanner, not follow it. R5 without a marker convention is a gate with 125 files of false positives.
3. **Promote GHI #537 ahead of wording updates?** The premise has changed: F4 is fixed, so runtime no longer "forces the wrong proof channel." What survives is F4b, a narrower waiver defect. Wording (R2, R3) is now the *stronger* residual pressure and should land first.

---

## 7. What this audit does not claim

- It does not claim the 70 flagged operations are defects. `propose_disposition` is a heuristic; each needs a human read.
- It does not claim `@covers` parity is wrong. It claims the *pipeline skill* applies it to the wrong REQ kinds.
- It does not re-open GHI #531 or ADR-0.0.59. Both stand.
- It does not measure test *effectiveness* beyond the tautology heuristic. The RED-witness gate landed under GHI #642 is the first mechanical falsifiability proof this repo has; a suite-wide falsifiability inventory is a separate, larger question.
