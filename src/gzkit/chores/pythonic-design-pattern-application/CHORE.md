# CHORE: Pythonic Design Pattern Application

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `pythonic-design-pattern-application`

---

## Why this chore exists

`pythonic-design-pattern-detection` surfaces structural refactor candidates. This chore is its **evidence pair**: when a candidate is applied, capture the before/after with mechanical-delta proof. The two together form the post-post-implementation feedback loop the operator named when authoring this set — *"I want to take purposeful action, almost always."*

A candidate detected and applied without evidence is invisible to the audit trail. A candidate applied with evidence joins the corpus the team can learn from — same shape as ARB receipts for QA claims (AGENTS.md § Attestation), but for refactor moves.

## What "evidence" means here

Every applied candidate writes an evidence file under `.gzkit/chores/pythonic-design-pattern-application/proofs/application-YYYY-MM-DD-HHMMSS-<short-slug>.md` containing:

1. **Pattern named** — Pythonic form chosen, e.g. *"Strategy class -> first-class function"*
2. **Source candidate** — file:line + class name from the detection report
3. **Python example witness** — the local archive path read, e.g. `Python/src/Strategy/Conceptual/main.py`
4. **Example-derived role map** — the pattern roles observed in that Python example and which roles the rewrite collapses
5. **Before / After** — both forms shown with at least the function/class signature; full body if <=20 lines
6. **Cyclomatic complexity delta** — xenon ranks before/after for the affected module
7. **SLOC delta** — radon raw before/after; positive deltas require explicit rationale
8. **Tests cited** — list of tests that pinned semantics across the rewrite (Red-Green-Refactor evidence)
9. **TDD receipt** — `arb-step-unittest-*` receipt ID from the GREEN run (per AGENTS.md § Attestation)
10. **Disposition link** — back-reference to the entry in the detection chore's candidates report

The mechanical-delta requirement is the binding part: the rewrite must not regress xenon's complexity grade for the affected module, and SLOC must non-positive (or be justified inline).

## Python example corpus requirement

Before applying a rewrite, read the matching Python example from the local
examples archive when present:

```bash
export DESIGN_PATTERNS_ARCHIVE="/Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/Design_Patterns_Book/design-patterns-en.zip"
unzip -p "$DESIGN_PATTERNS_ARCHIVE" Python/src/Strategy/Conceptual/main.py | sed -n '1,220p'
unzip -p "$DESIGN_PATTERNS_ARCHIVE" Python/src/Strategy/Conceptual/Output.txt
```

The archive example is not source material to copy into gzkit. It is a witness
for the pattern's roles. The application evidence must show that the rewrite
understood those roles and either collapsed them into Python constructs
(`Callable`, generator, `functools.partial`, `contextlib.contextmanager`,
`functools.cache`, `weakref`, `match`, `singledispatch`) or preserved the class
shape with a concrete reason.

## Policy and Guardrails

- **Lane:** Lite — internal refactor, no external contract change
- **One file per applied candidate** — never bundle multiple refactors into one evidence file
- **TDD discipline binding** — Red-Green-Refactor per `.gzkit/rules/tests.md`; cite the GREEN receipt
- **Complexity non-regression** — xenon C/C/C must hold post-rewrite (matches `complexity-reduction-xenon`)
- **Detection back-link required** — the evidence file references the detection report row that flagged the candidate; orphan applications (no detection trail) are a defect
- **Pythonic-target faithfulness** — if the detection row says "first-class function", the after-form must actually be a first-class function (or a documented deviation explaining why that target was wrong for this case)

## Workflow

### 1. Pick a candidate from the detection report

```bash
ls .gzkit/chores/pythonic-design-pattern-detection/proofs/candidates-*.md
```

Open the most recent report; pick a row marked `_[applied | deferred | not-pythonic-rewrite]_` and decide *applied*.

### 2. Read the Python example witness

Open the candidate's `Python/src/<Pattern>/Conceptual/main.py` and `Output.txt`
from `design-patterns-en.zip`. Record the example path and role map before
editing code. If the detection report does not name the archive path, look it
up in `pythonic-design-pattern-detection/CHORE.md` and update the report row
before continuing.

### 3. Capture before-state metrics

```bash
uvx xenon --max-absolute C --max-modules C --max-average C src/ > /tmp/xenon-before.txt 2>&1 || true
uvx radon raw src/ -s > /tmp/radon-before.txt 2>&1 || true
```

### 4. Apply the rewrite under TDD

Per `.gzkit/rules/tests.md` Red-Green-Refactor:

- Write a test that pins the **operator-facing semantics** of the code, not the class shape
- Run it; observe RED if any
- Apply the Pythonic rewrite
- Run the test; observe GREEN
- Refactor for clarity if needed; tests stay GREEN

The semantics test is the load-bearing artifact. A pattern rewrite that is semantically equivalent must pass the same test — which means the test must be written against the *purpose*, not the *shape*.

### 5. Capture after-state metrics + GREEN receipt

```bash
uvx xenon --max-absolute C --max-modules C --max-average C src/ > /tmp/xenon-after.txt 2>&1
uvx radon raw src/ -s > /tmp/radon-after.txt 2>&1
uv run gz arb step --name unittest -- uv run -m unittest -q
```

The ARB step run produces the GREEN receipt cited in the evidence file.

### 6. Author the evidence file

Path: `.gzkit/chores/pythonic-design-pattern-application/proofs/application-YYYY-MM-DD-HHMMSS-<short-slug>.md`

Template (copy and fill):

```markdown
# Application: <Pattern> -> <Pythonic target> (<short-slug>)

- **Date:** YYYY-MM-DD HH:MM:SS
- **Pattern:** <e.g. "Strategy class -> first-class function">
- **Source candidate:** `<src/path/to/file.py:LINE>` (class `<ClassName>`)
- **Detection report:** `.gzkit/chores/pythonic-design-pattern-detection/proofs/candidates-YYYY-MM-DD.md`
- **Python example witness:** `Python/src/<Pattern>/Conceptual/main.py`
- **Python example output:** `Python/src/<Pattern>/Conceptual/Output.txt`
## Example-derived role map

- **Example roles observed:** <Context / Strategy / ConcreteStrategy, etc.>
- **Roles preserved:** <semantic roles still present after rewrite>
- **Roles collapsed:** <class roles replaced by callables/functions/data/etc.>
- **Reason this is Pythonic:** <stdlib/Python construct that carries the behavior with less structure>

## Before

\`\`\`python
<class form>
\`\`\`

## After

\`\`\`python
<pythonic form>
\`\`\`

## Mechanical deltas

| Metric | Before | After | Delta | Note |
|--------|--------|-------|-------|------|
| xenon (module rank) | <C/B/A> | <C/B/A> | <equal or improved> | |
| radon raw SLOC (module) | <N> | <M> | <M - N> | |

## Semantics tests cited

- `tests/<path>/test_<name>.py::Test<X>::test_<y>`
- `tests/<path>/test_<name>.py::Test<X>::test_<z>`

## TDD receipt

- GREEN: `arb-step-unittest-<timestamp>`

## Disposition

Pythonic target faithful: yes / no (with rationale)
```

### 7. Update the detection report row

Mark the candidate's `Disposition:` from `_[applied | deferred | not-pythonic-rewrite]_` to `applied: <evidence-file-path>` so the detection report becomes self-referential.

### 8. Validate

```bash
uv run -m unittest -q
uvx xenon --max-absolute C --max-modules C --max-average C src/
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |
| exitCodeEquals | `uvx xenon --max-absolute C --max-modules C --max-average C src/` | 0 |

The chore intentionally does **not** mechanically gate on "evidence file exists this period" — operators apply opportunistically; the gate is per-evidence-file faithfulness, not per-period activity. Period rhythm is owned by the detection chore via its candidate-disposition triage.

## Anti-patterns (do not do)

- Applying a rewrite without a corresponding entry in the detection report (orphan application)
- Skipping the before/after metric capture because *"the rewrite is obvious"* — the corpus is the product
- Bundling multiple refactors into one evidence file (one application = one file)
- Writing a string-shape semantics test instead of a behavior-pinning test (per `.gzkit/rules/tests.md` § Tests assert semantics, not strings — invariant 6f)
- Citing a fabricated receipt ID — same fabrication failure as ARB receipt fabrication, applies here
- Marking the rewrite "applied" when xenon regressed (the post-form is heavier than the pre-form by complexity)
- Letting the detection row's recommended target slip into a *"close enough"* shape — the rewrite is faithful to the named Pythonic answer, or it documents why that target is wrong for this case
- Applying from memory without reading the local Python example witness — this turns the pattern examples back into training-corpus recall instead of observed evidence

## Run Log

| Date | Pattern | Source | Evidence file | xenon delta | SLOC delta |
|------|---------|--------|---------------|-------------|------------|
| _YYYY-MM-DD_ | _Strategy -> function_ | _src/foo.py:42_ | _proofs/application-..._ | _equal_ | _-12_ |

---

**End of CHORE: Pythonic Design Pattern Application**
