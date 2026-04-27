---
name: gz-pythonic-pattern-detect
persona: main-session
description: Surface Pythonic-design-pattern refactor candidates after ADR closeout. Use when ruff/ty are zeroed and complexity gates are green but the code shape still looks Java-flavored — Strategy classes that should be functions, Singletons that should be module-level constants, Visitor ladders that should be `match`. Wields the `pythonic-design-pattern-detection` chore. Pair with `gz-pythonic-pattern-apply` for the evidence side.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-26
metadata:
  skill-version: "1.0.0"
gz_command: chores run pythonic-design-pattern-detection
---

# pythonic-pattern-detect

## Purpose

Run the `pythonic-design-pattern-detection` chore to surface structural refactor candidates that mechanical metric chores (`pythonic-refactoring`, `complexity-reduction-xenon`, `module-sloc-cap-radon`) cannot catch. The chore's scanner walks `src/` AST-by-AST and flags class shapes whose Pythonic equivalent is cleaner — paired with the `refactoring.guru/design-patterns/python` catalogue and local `design-patterns-en.zip` Python examples as the absorption surface.

## Inputs

- `root`: source tree to scan (default `src`)
- `out`: markdown candidates report path (default `.gzkit/chores/pythonic-design-pattern-detection/proofs/candidates-YYYY-MM-DD.md`)
- `xenon_band` (optional): xenon hot-spot band to cross-reference, default `B`
- `DESIGN_PATTERNS_ARCHIVE` (optional): local Refactoring Guru archive, defaulting in this repo to `/Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/Design_Patterns_Book/design-patterns-en.zip`

## Outputs

- Candidates report at the `out` path enumerating every match with file:line, class name, AST signal, Pythonic refactor target, and the canonical `refactoring.guru/design-patterns/<slug>/python/example` URL
- Optional `xenon-hotspots-YYYY-MM-DD.txt` cross-reference under the same `proofs/`
- `CHORE-LOG.md` entry recording the chore execution

## Procedure

1. Confirm chore is registered:

   ```bash
   uv run gz chores show pythonic-design-pattern-detection
   ```

2. Run scanner self-test before scanning real source — proves the detector set still recognises its own fixtures:

   ```bash
   uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py --self-test
   ```

3. Run the scanner against `src`:

   ```bash
   uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py \
       --root src \
       --out .gzkit/chores/pythonic-design-pattern-detection/proofs/candidates-$(date +%Y-%m-%d).md
   ```

4. Cross-reference complexity hotspots:

   ```bash
   uvx xenon --max-absolute B src/ \
       > .gzkit/chores/pythonic-design-pattern-detection/proofs/xenon-hotspots-$(date +%Y-%m-%d).txt 2>&1 || true
   ```

5. Open the candidates report. For each candidate:

   - Open the cited `refactoring.guru/design-patterns/<slug>/python/example` URL as the public absorption reference
   - Read the matching local archive example (`Python/src/<Pattern>/Conceptual/main.py` plus `Output.txt` when present) as the role-map witness
   - Record `Example`, `Output`, `Role map`, and `Pythonic collapse` in the candidate row before deciding disposition
   - Decide one disposition: `applied`, `deferred`, or `not-pythonic-rewrite`
   - For `applied`: route to `gz-pythonic-pattern-apply` to capture evidence
   - For `deferred`: file or cite a tracking GHI, paste the issue number into the row
   - For `not-pythonic-rewrite`: name the concrete reason inline (the class shape genuinely fits — e.g. State machine with many transitions)

6. For reference-mode patterns (Bridge, Flyweight, Factory Method) — open the catalogue's Python example and the matching archive example side-by-side with any module ranked B-or-worse by xenon. Add an inline `## Reference-mode candidates` section to the report.

7. Mark the chore as run:

   ```bash
   uv run gz chores run pythonic-design-pattern-detection
   ```

## Failure Modes

- **Scanner self-test fails:** detector set has drifted from its fixtures. Read `scan.py` and the failing fixture; either fix the detector or update the fixture if the rewrite was intentional.
- **`--out` path missing parent directory:** the scanner creates the parent automatically, but if the project overlay was deleted, run `uv run gz chores doctor` to scaffold it.
- **Empty report (`NO_CANDIDATES_DETECTED`):** AST signals returned zero hits. Switch to reference-mode review against the catalogue and local Python examples; do not assume the codebase is Pythonic everywhere — Bridge, Flyweight, Factory Method are not detected mechanically.
- **Many candidates without xenon overlap:** the structural drift exists but is metric-invisible. Do not skip those — that is exactly the post-post-implementation gap this skill is designed to catch.

## Acceptance Rules

- Uses `uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py` — never a shadow scanner
- Self-test runs before any real scan
- Every flagged candidate gets a disposition (`applied`/`deferred`/`not-pythonic-rewrite`) before the chore is considered done for this period
- Every disposition row cites the local Python example path and records a role map
- Report path is under `.gzkit/chores/pythonic-design-pattern-detection/proofs/` — never elsewhere
- `applied` dispositions route to `gz-pythonic-pattern-apply` for evidence capture; orphan applications (no detection-report row) are a defect

## Common Rationalizations

These thoughts mean STOP — you are about to ship a detection pass that broke its own discipline:

| Thought | Reality |
|---------|---------|
| "I'll skip the self-test, the scanner worked yesterday" | Detector drift is silent. Self-test is a 1-second guard against authoring fake reports. |
| "I'll mark all candidates `not-pythonic-rewrite` to clear the queue" | The disposition is a per-candidate judgment, not a queue-clearer. False `not-pythonic-rewrite` is dishonest triage. |
| "The reference-mode patterns aren't detected, so I'll skip them" | Reference-mode exists *because* AST detection misses them. Skipping reference-mode collapses the chore to mechanical-only. |
| "AST said zero candidates, the codebase must be clean" | Bridge, Flyweight, Factory Method need eye-review against the catalogue. Trust the catalogue, not the absence of AST hits. |
| "The URL is enough; I know the pattern" | The local Python example is the observed role-map witness. Skipping it turns the chore back into memory-driven pattern matching. |
| "I'll run `gz chores run` before completing dispositions, log first" | The CHORE-LOG records execution, not completeness. Disposition triage must precede the run, or the log is a lie. |

## Red Flags

- Authoring an applied entry without routing to `gz-pythonic-pattern-apply`
- Mass-marking candidates without per-entry rationale
- Skipping `--self-test` before a real scan
- Writing the candidates file outside `.gzkit/chores/pythonic-design-pattern-detection/proofs/`
- Treating zero-AST-hits as evidence the codebase is Pythonic shape-wise (catalogue eye-review still required)
- Candidate rows without `Python/src/<Pattern>/Conceptual/main.py` evidence
- Running the scanner over `tests/` or `features/` (excluded by default — do not override without reason)

## Reference

- Chore canon: `src/gzkit/chores/pythonic-design-pattern-detection/CHORE.md`
- Scanner: `src/gzkit/chores/pythonic-design-pattern-detection/scan.py`
- Catalogue: `https://refactoring.guru/design-patterns/python` (per-pattern URLs cited in the candidates report)
- Local example corpus: `design-patterns-en.zip` `Python/src/<Pattern>/Conceptual/main.py`
- Pair skill: `gz-pythonic-pattern-apply` (evidence capture for applied refactors)
- Related chores: `pythonic-refactoring` (idiom-level), `complexity-reduction-xenon` (metric-level)
- Doctrine: AGENTS.md § Stdlib-First Doctrine (absorption relationship), `.gzkit/rules/tests.md` § Tests assert semantics, not strings
