---
name: gz-obpi-simplify
description: OBPI-scoped code review for reuse, quality, and efficiency. Resolves scope from the brief's Allowed Paths, reviews across three dimensions, and applies fixes. Use after implementation, before reconcile.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-03
metadata:
  skill-version: "6.0.2"
---

# gz-obpi-simplify

OBPI-scoped code review: resolve scope from the brief, review across three
dimensions (reuse, quality, efficiency), fix issues found.

**Position in workflow:** After implementation (pipeline Stage 2-3), before
reconcile. This is the implementation quality gate — the pipeline verifies
correctness; simplify verifies craft.

### Common Rationalizations

These thoughts mean STOP — you are about to skip the craft gate:

| Thought | Reality |
|---------|---------|
| "The code is working fine, no simplification needed" | Working code that is hard to read will be hard to fix when it breaks. Simplification is about future maintainability. |
| "Changing this code is too risky" | Every fix is behavior-preserving and validated by tests. Risk is an excuse to leave technical debt. |
| "This is just formatting, ruff handles it" | Ruff handles syntax formatting. Semantic simplification (dead code, poor naming, unnecessary complexity) is this skill's domain. |
| "The OBPI is done, simplification is optional" | Simplification is the craft gate between pipeline completion and reconciliation. Skipping it ships unreviewed complexity. |
| "I don't understand this code well enough to simplify it" | Step 1 is "understand before touching." If you cannot understand it, that is a red flag for the code, not a reason to skip. |

### Red Flags

- Agent reports "no issues found" without reading the scoped files
- Review covers only one dimension (e.g., quality) while skipping reuse and efficiency
- Files outside the OBPI's Allowed Paths are modified
- Tests fail after simplification and agent proceeds anyway
- Agent adds new functionality under the guise of "simplification"

---

## When to Use

- After completing OBPI implementation (post-pipeline or standalone)
- When the user says "simplify OBPI-X.Y.Z-NN"
- Before closeout when you want a quality pass on the implementation
- As a periodic review on recently completed OBPIs

## When NOT to Use

- During implementation (let the pipeline finish first)
- On files outside the OBPI's Allowed Paths
- For adding features or changing behavior

---

## Invocation

```text
/gz-obpi-simplify OBPI-0.5.0-01
/gz-obpi-simplify 0.5.0-01
/gz-obpi-simplify OBPI-0.5.0-01 focus on error handling
```

The first token is the OBPI ID. Remaining tokens are an optional focus directive.

---

## Step 1: Resolve OBPI Scope

1. Find the brief file:
   ```bash
   find docs/design/adr -name "OBPI-{id}*.md" -path "*/obpis/*"
   ```
2. Read the brief and extract the `## Allowed Paths` section.
3. Expand those patterns against the working tree to produce the concrete file list.
4. If the brief has an `### Implementation Summary` section with explicit file paths,
   include those too — they capture files actually touched.
5. Filter to source/test code (`.py`, `.md` in `docs/`, config files). Exclude binaries.

If no brief is found, abort with an error message.

**The file list is the review scope. Do not review files outside it.**

### Protected Regions

Before reviewing, scan scoped files for `simplify-ignore` annotations. Code
within these annotations is excluded from all three review dimensions.

```python
# simplify-ignore-start: governance-critical
# ... code that must not be simplified ...
# simplify-ignore-end
```

Supported reasons:

| Reason | When to use |
|--------|-------------|
| `governance-critical` | Code that enforces governance invariants (ledger writes, gate checks) |
| `performance-sensitive` | Code where clarity was intentionally traded for performance |
| `external-contract` | Code that implements an external API or protocol exactly |
| `intentional-complexity` | Code where the complexity is inherent to the problem domain |

**Rules:**

- Do not modify code within annotated regions
- Do not remove or relocate the annotations themselves
- If a protected region looks like it no longer needs protection, flag it for human review instead of changing it
- Report protected regions in the Step 3 summary so the human knows what was excluded

---

## Step 2: Review Across Three Dimensions

Review the scoped files from three independent lenses. Agents that support
parallel dispatch should run all three concurrently. Sequential execution
is acceptable when parallel dispatch is not available.

### Dimension 1: Reuse

Look for:

- Duplicate logic across files that should be extracted to a shared function
- Copy-pasted patterns with minor variations
- Opportunities to use existing project utilities instead of inline implementations
- DRY violations within the OBPI scope

### Dimension 2: Quality

Look for:

- Unused imports, dead code, unreachable branches
- Poor naming (unclear abbreviations, misleading names)
- Overly complex conditionals that should be simplified
- Missing or incorrect type hints
- Functions exceeding 50 lines or modules exceeding 600 lines
- Mutable default arguments
- Bare except clauses

### Dimension 3: Efficiency

Look for:

- Unnecessary repeated computation (e.g., re-parsing the same file in a loop)
- Inefficient data structures (list where set/dict would be better)
- Unnecessary string concatenation in loops
- File I/O that could be batched
- Redundant validation or transformation passes

For each finding: fix it directly. Skip false positives silently.
Apply the optional focus directive (if provided) to weight review attention.

---

## Step 3: Validate and Report

After all reviews complete:

1. Run quality checks on changed files:
   ```bash
   uv run ruff check . --fix && uv run ruff format .
   uv run -m unittest -q
   ```
2. Report a concise summary:
   - Number of issues found per dimension
   - What was fixed
   - Any findings flagged but not auto-fixed (ambiguous cases)
3. If no issues found, confirm: "Code is clean across all three review dimensions."

---

## Constraints

- **Scope is sacred.** Only review and edit files within the OBPI's Allowed Paths.
- **No new features.** This is review, not enhancement. Do not add functionality.
- **No style-only changes.** Ruff handles formatting. Focus on semantic issues.
- **Preserve behavior.** Every fix must be behavior-preserving. If uncertain, flag instead of fixing.
- **Tests must still pass.** If a fix breaks tests, revert it.
- **Respect `simplify-ignore` annotations.** Do not modify code within annotated protected regions.

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `gz-obpi-pipeline` | Pipeline verifies correctness; simplify verifies craft |
| `gz-obpi-reconcile` | Run after simplify to catch any status drift |
| `gz-check` | Simplify runs quality checks as part of Step 3 |
