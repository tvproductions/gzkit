---
name: gz-pythonic-pattern-apply
persona: main-session
description: Capture before/after evidence with mechanical-delta proof when a Pythonic-pattern rewrite is applied. Use after `gz-pythonic-pattern-detect` flagged a candidate marked `applied` — the rewrite must be backed by a semantics-pinning test, a TDD GREEN receipt, and non-regressing xenon/radon deltas, written to `.gzkit/chores/pythonic-design-pattern-application/proofs/`.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-26
metadata:
  skill-version: "1.0.0"
gz_command: chores run pythonic-design-pattern-application
---

# pythonic-pattern-apply

## Purpose

Apply a Pythonic-pattern rewrite to a single candidate flagged by `gz-pythonic-pattern-detect`, then capture the before/after as a structured evidence file. The chore behind this skill (`pythonic-design-pattern-application`) records the corpus the team learns from — same shape as ARB receipts for QA claims (AGENTS.md § Attestation), but for refactor moves.

## Inputs

- `candidate`: a row from the most recent `pythonic-design-pattern-detection` candidates report (file:line + class name)
- `pattern_target`: the Pythonic refactor target named in the report (e.g. *"first-class function"*, *"`@functools.singledispatch`"*)
- `guru_url`: the canonical `refactoring.guru/design-patterns/<slug>/python/example` URL cited in the row
- `python_example`: the local archive path (`Python/src/<Pattern>/Conceptual/main.py`) used as the role-map witness

## Outputs

- One evidence file at `.gzkit/chores/pythonic-design-pattern-application/proofs/application-YYYY-MM-DD-HHMMSS-<short-slug>.md`
- One ARB GREEN receipt (`arb-step-unittest-<timestamp>`) cited inline
- The candidate's row in the detection report flipped from `_[applied | deferred | not-pythonic-rewrite]_` to `applied: <evidence-file-path>`
- `CHORE-LOG.md` entry recording the chore execution

## Procedure

1. Open the chosen candidate's row in the most recent detection report. Note the `refactoring.guru/design-patterns/<slug>/python/example` URL and the local archive example path (`Python/src/<Pattern>/Conceptual/main.py`). Open both as absorption references for the rewrite shape.

2. Read the local Python example and matching `Output.txt` from `design-patterns-en.zip`. Record the example's role map before editing: roles observed, roles preserved, roles collapsed, and the Python construct that will carry the behavior.

3. Capture before-state metrics:

   ```bash
   uvx xenon --max-absolute C --max-modules C --max-average C src/ > /tmp/xenon-before.txt 2>&1 || true
   uvx radon raw src/ -s > /tmp/radon-before.txt 2>&1 || true
   ```

4. Write a **semantics-pinning test** for the candidate's behavior — *not* its shape. The test must derive from the operator-facing purpose the code serves, per `.gzkit/rules/tests.md` § Tests assert semantics, not strings (invariant 6f). Run it; observe RED for any genuinely new behavior coverage, GREEN for behavior that was already covered.

5. Apply the Pythonic rewrite. Match the target named in the candidate row. If the catalogue's recommended target turns out to be wrong for this case, do NOT settle for "close enough" — either pick a different catalogue target with an explicit rationale, or escalate to operator review.

6. Run the test under ARB to produce the GREEN receipt:

   ```bash
   uv run gz arb step --name unittest -- uv run -m unittest -q
   ```

   Capture the receipt ID printed (`arb-step-unittest-<timestamp>`).

7. Capture after-state metrics:

   ```bash
   uvx xenon --max-absolute C --max-modules C --max-average C src/ > /tmp/xenon-after.txt 2>&1
   uvx radon raw src/ -s > /tmp/radon-after.txt 2>&1
   ```

   Confirm xenon did not regress (still C/C/C). If it did, the rewrite has compounded complexity rather than reduced it — revert and re-design.

8. Author the evidence file at `.gzkit/chores/pythonic-design-pattern-application/proofs/application-YYYY-MM-DD-HHMMSS-<short-slug>.md` per the template in `src/gzkit/chores/pythonic-design-pattern-application/CHORE.md`. Include:

   - Pattern named (Pythonic form chosen)
   - Source candidate file:line + class
   - Detection report back-reference
   - Local Python example witness and `Output.txt` path
   - Example-derived role map
   - `refactoring.guru` URL
   - Before / After code blocks
   - xenon + radon deltas with notes
   - Tests cited (file:Test::test_method)
   - GREEN receipt ID
   - Pythonic-target faithfulness note (yes / no with rationale)

9. Update the detection report row from `_[applied | deferred | not-pythonic-rewrite]_` to `applied: .gzkit/chores/pythonic-design-pattern-application/proofs/<filename>.md`.

10. Mark the chore as run:

   ```bash
   uv run gz chores run pythonic-design-pattern-application
   ```

## Failure Modes

- **xenon regresses post-rewrite:** the Pythonic form is heavier than the class form by complexity. Revert and pick a different target — or accept the candidate is `not-pythonic-rewrite` after all and update the detection row accordingly.
- **Semantics test rewrites the assertion to match new output:** that is a string-shape assertion, not a semantics test. The whole point of the test is that it pins purpose across the rewrite — if it has to change, the rewrite changed behavior.
- **GREEN receipt missing:** ran `unittest` directly instead of through `gz arb step`. The corpus needs the receipt ID, not a narrative claim. Re-run under ARB.
- **Detection report row not updated:** orphan evidence file. Run an audit grep for the evidence-file path inside `candidates-*.md` files and back-link manually.
- **Bundled refactors (multiple patterns in one evidence file):** split into one file per applied candidate. The corpus loses signal on bundles.
- **Python example witness missing:** evidence was authored from memory or URL-only review. Read the archive example, add the role map, and update the detection row before continuing.

## Acceptance Rules

- One evidence file per applied candidate; never bundled
- Semantics test is behavior-pinning (per invariant 6f), not string-shape
- xenon C/C/C non-regression confirmed before authoring evidence
- GREEN receipt ID is real (not fabricated) and corresponds to a passing run
- Local Python example witness and role map are present
- Detection report row back-linked to the evidence file path
- `refactoring.guru` URL cited matches the catalogue entry from the detection report
- Pythonic-target faithfulness is named explicitly: "yes" or "no with rationale"

## Common Rationalizations

These thoughts mean STOP — you are about to ship an evidence file that broke its own discipline:

| Thought | Reality |
|---------|---------|
| "I'll skip the semantics test — the rewrite is obviously equivalent" | Without a behavior-pinning test, the rewrite is unverified. The corpus is the product; un-evidence-able rewrites add noise, not signal. |
| "xenon regressed by one rank, but the after-form is cleaner" | Cleaner-by-eye + heavier-by-metric is the precise failure mode this chore catches. Revert; pick a different target. |
| "I'll bundle three Strategy-class rewrites into one file to save time" | One file per applied candidate is the canon. Bundles lose per-candidate signal. |
| "I'll cite `unittest -q` exit-zero in lieu of an ARB receipt" | Same fabrication failure as ARB receipt fabrication elsewhere — the receipt ID is the proof, not the claim. |
| "The catalogue says 'first-class function' but I made it a `@cache`d method" | Faithfulness to the catalogue target is the rule. If the catalogue is wrong for this case, name *why* in the rationale; do not silently deviate. |
| "I'll mark the detection row `applied` without back-linking the evidence" | Orphan applications break the audit trail. The two reports are paired; neither stands alone. |
| "I already know Strategy/Visitor/etc.; I don't need the example" | The local Python example is the witness for role mapping. Without it, the evidence is narrative recall. |

## Red Flags

- Evidence file path outside `.gzkit/chores/pythonic-design-pattern-application/proofs/`
- xenon delta showing rank regression
- Test cited that has no `assert` body matching operator-facing purpose
- GREEN receipt ID with `exit_status=1` (an authored RED receipt is itself a defect — see AGENTS.md § Attestation anti-patterns)
- Candidate row in detection report not updated
- Missing `Python/src/<Pattern>/Conceptual/main.py` witness in the evidence file
- *"Pythonic-target faithful: yes"* without naming which target was met
- *"Pythonic-target faithful: no"* without naming why the catalogue was wrong here

## Reference

- Chore canon: `src/gzkit/chores/pythonic-design-pattern-application/CHORE.md`
- Pair skill: `gz-pythonic-pattern-detect` (candidate surfacing)
- Catalogue: `https://refactoring.guru/design-patterns/python`
- Local example corpus: `design-patterns-en.zip` `Python/src/<Pattern>/Conceptual/main.py`
- Doctrine: AGENTS.md § Attestation (receipt-vs-narrative discipline applied to refactors), `.gzkit/rules/tests.md` § Tests assert semantics, not strings (invariant 6f), `.gzkit/rules/tests.md` § Red-Green-Refactor TDD
- Related: `complexity-reduction-xenon` (the non-regression check this skill cites), `gz-arb` (the receipt-emitting wrapper)
