---
name: gz-obpi-simplify
description: Review code quality for an OBPI implementation unit. Resolves scope from the brief's Allowed Paths, spawns 3 parallel review agents (reuse, quality, efficiency), and applies fixes. Use when reviewing OBPI work or when the user says "simplify OBPI-X.Y.Z-NN".
argument-hint: "<OBPI-ID> [focus]"
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Agent Edit
---

# simplify

OBPI-scoped code review: resolve scope from the brief, review in parallel, fix issues.

---

## Step 1: Resolve OBPI Scope

Parse `$ARGUMENTS` — the first token is the OBPI ID (e.g., `OBPI-0.5.0-01` or short-form `0.5.0-01`). Remaining tokens are the optional focus directive.

1. Find the brief file:
   ```
   docs/design/adr/**/obpis/OBPI-{id}*.md
   ```
2. Read the brief and extract the `## Allowed Paths` section.
3. Expand those glob patterns against `git ls-files` to produce the concrete file list.
4. If the brief also has an `### Implementation Summary` section with explicit file paths, include those too — they capture files actually touched.
5. Filter to files that exist on disk and are source/test code (`.py`, `.md` in docs/, config files). Exclude binary artifacts.

If no brief is found, abort with an error message.

**The file list is the review scope. Do not review files outside it.**

---

## Step 2: Spawn 3 Review Agents in Parallel

Launch three agents simultaneously using the Agent tool. Each agent receives the same file list but reviews from a different lens.

Pass the full file list and the optional focus directive (if provided) to each agent.

### Agent 1: Reuse

> Review these files for code reuse opportunities:
> {file list}
>
> Look for:
> - Duplicate logic across files that should be extracted to a shared function
> - Copy-pasted patterns with minor variations
> - Opportunities to use existing project utilities instead of inline implementations
> - DRY violations within the OBPI scope
>
> {focus directive if provided}
>
> For each finding: fix it directly via Edit. Skip false positives silently.

### Agent 2: Quality

> Review these files for code quality issues:
> {file list}
>
> Look for:
> - Unused imports, dead code, unreachable branches
> - Poor naming (unclear abbreviations, misleading names)
> - Overly complex conditionals that should be simplified
> - Missing or incorrect type hints
> - Functions exceeding 50 lines or modules exceeding 600 lines
> - Mutable default arguments
> - Bare except clauses
>
> {focus directive if provided}
>
> For each finding: fix it directly via Edit. Skip false positives silently.

### Agent 3: Efficiency

> Review these files for efficiency issues:
> {file list}
>
> Look for:
> - Unnecessary repeated computation (e.g., re-parsing the same file in a loop)
> - Inefficient data structures (list where set/dict would be better)
> - Unnecessary string concatenation in loops
> - File I/O that could be batched
> - Redundant validation or transformation passes
>
> {focus directive if provided}
>
> For each finding: fix it directly via Edit. Skip false positives silently.

---

## Step 3: Aggregate and Report

After all three agents complete:

1. Collect findings from each agent.
2. If any fixes were applied, run `uv run ruff check . --fix && uv run ruff format .` to ensure formatting consistency.
3. Report a concise summary:
   - Number of issues found per category
   - What was fixed
   - Any findings that were flagged but not auto-fixed (ambiguous cases)
4. If no issues found, confirm: "Code is clean across all three review dimensions."

---

## Constraints

- **Scope is sacred.** Only review and edit files within the OBPI's Allowed Paths.
- **No new features.** This is review, not enhancement. Do not add functionality.
- **No style-only changes.** Ruff handles formatting. Focus on semantic issues.
- **Preserve behavior.** Every fix must be behavior-preserving. If uncertain, flag instead of fixing.
