---
name: gz-tech-debt-review
persona: quality-reviewer
description: Survey the codebase for technical debt and recommend resolutions. Synthesizes signals from existing gzkit chores, audits, and complexity tools (xenon, radon, ruff, ty, gz cli audit, gz validate, gz-pythonic-pattern-detect, doc-coverage, dependency-currency) into a single prioritized debt report with file:line evidence and recommended fixes. Use when the user asks to "review code for tech debt", "find tech debt", "audit the codebase for debt", "what's rotting", "where is the debt", or wants a debt assessment for an ADR/OBPI scope or a touched-files set. Also use proactively when an operator asks "what should we clean up next" or "is there debt accumulating in X". Distinct from `gz-obpi-simplify` (which fixes craft inside an active OBPI scope) and `gz-check` (which gates a single change) — this skill produces a *report* across many debt classes that the operator can route into GHIs, OBPIs, or chores.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-29
metadata:
  skill-version: "1.0.0"
---

# gz-tech-debt-review

Survey the codebase for technical debt across multiple debt classes,
synthesize the findings into one prioritized report, and recommend a
resolution path for each finding.

This skill is a **synthesizer**, not a new analyzer. The gzkit surface
already runs the analyses (chores, validators, ruff, ty, xenon, radon).
The skill's job is to wield those tools, normalize their outputs, rank
by impact, and produce one operator-facing report — so debt findings
end up in GHIs, OBPI briefs, or chore runs instead of dying on a
terminal scrollback.

## Position in the gzkit surface

| Surface | Role | Boundary |
|---------|------|----------|
| `gz-obpi-simplify` | Craft gate *inside* an active OBPI scope | Reuse/quality/efficiency on Allowed Paths only |
| `gz-check` | Pre-merge / pre-attestation gate on a single change | Pass-fail, not a debt inventory |
| `gz-pythonic-pattern-detect` | One specific debt class (Java-shaped Python) | Single chore, one signal |
| **`gz-tech-debt-review`** | **Cross-class debt inventory across many signals** | **Report-shaped, routes to GHIs/OBPIs/chores** |
| `gz-chore-runner` | Executes one chore at a time | Mechanical lane |

## Invocation

```text
/gz-tech-debt-review                          # default: touched-files scope
/gz-tech-debt-review --scope all              # whole repository sweep
/gz-tech-debt-review --scope touched          # current branch's diff vs main
/gz-tech-debt-review --scope adr ADR-0.1.0    # ADR-scoped paths
/gz-tech-debt-review --scope obpi OBPI-0.1.0-01  # brief Allowed Paths
/gz-tech-debt-review --scope path src/gzkit/commands  # explicit subtree
/gz-tech-debt-review --draft-ghis             # also draft GHI bodies for High/Critical
```

The first positional token after `--scope` selects scope mode. The
`--draft-ghis` flag is opt-in: by default the skill diagnoses only.
With the flag it drafts `gh issue create --label tech-debt` bodies for
Critical and High findings the operator can route as a follow-up.

---

## Scope resolution

Resolve the file list before running any analysis. The scope mode
determines how:

| Mode | Resolution |
|------|------------|
| `all` | All `.py` under `src/` and `tests/`; all `.md` under `docs/`. |
| `touched` (default) | `git diff --name-only main...HEAD` plus staged + unstaged. Filter to source/test/doc. |
| `adr <ID>` | Read `docs/design/adr/**/<ID>*/*.md` frontmatter `paths:` if present; otherwise the ADR's directory plus its OBPIs' Allowed Paths unioned. |
| `obpi <ID>` | Brief's `## Allowed Paths` section, expanded against the working tree. Same shape as `gz-obpi-simplify` Step 1. |
| `path <subtree>` | Glob-expand the subtree, restricted to source/test/doc. |

If the resolved file list is empty, abort with a clear message rather
than scanning the whole repo silently.

**The file list is the audit scope.** Findings outside it are noted
but not graded.

---

## Debt classes (binding)

A "debt class" is a named family of failure shapes with one or more
signal sources. The skill surveys all classes by default. Operators
can narrow with `--class <name>` (repeatable) when they want a focused
read.

| Class | Signal sources | What it catches |
|-------|----------------|-----------------|
| `size-cap` | radon raw / `module-sloc-cap-radon` chore | Functions >50 LOC, modules >600 LOC, classes >300 LOC |
| `complexity` | xenon / `complexity-reduction-xenon` chore | Cyclomatic complexity hot-spots above the configured band |
| `lint` | `uv run ruff check .` | Unfixed ruff diagnostics (excluding cosmetic) |
| `types` | `uvx ty check .` | Unresolved type errors, suppressed-but-still-firing `# type: ignore[code]` (the GHI #197 class) |
| `pythonic` | `gz-pythonic-pattern-detect` candidates report | Java-shaped Python (Strategy classes, Singletons, Visitor ladders) |
| `tests` | coverage report + `gz validate --requirements` + `gz validate --behave-req-tags` | <40% coverage, REQs without `@covers`, heavy OBPIs without `@REQ-*` BDD tags |
| `dead-code` | ruff `F401`/`F841`, `vulture` if available, grep for unreferenced exports | Unused imports, unreferenced symbols, orphan modules |
| `cli-drift` | `uv run gz cli audit`, `gz validate --cli-alignment` | Unregistered verbs in docs, undocumented verbs in code |
| `doc-drift` | `doc-coverage` chore, `gz validate --documents --surfaces`, `mkdocs build --strict` | Stale examples, drifted manpages, broken links |
| `frontmatter-drift` | `gz validate --frontmatter`, `frontmatter-ledger-coherence` chore | Brief/ADR frontmatter out of sync with ledger |
| `dep-currency` | `dependency-currency` chore | Outdated runtime deps (>5y aging policy) |
| `todo-rot` | grep `TODO|FIXME|XXX|HACK` with git-blame age | TODOs older than 90 days, FIXMEs without GHI refs |
| `governance` | `gz validate --advisory-scorecard`, rule version markers | Promotable rules still advisory, unversioned rule edits |
| `evidence-integrity` | `evidence-integrity-audit` chore | ARB receipts cited but missing, status frontmatter without ledger backing |

Adding a class is additive: extend the table, add a probe in Step 2,
extend the severity matrix below.

---

## Severity rubric (binding)

Every finding is graded **Critical / High / Medium / Low**. Severity
is a function of (a) blast radius and (b) reversibility — never of how
big the diff is to fix.

| Severity | Definition | Examples |
|----------|------------|----------|
| **Critical** | Violates a Prime-Directive invariant, a Gate Covenant rule, or a published external contract. Operator should stop and route now. | Unsuppressed `# type: ignore[code]` (GHI #197 class), missing `@covers` on a Completed/Validated heavy brief, `gz` verb prescribed in runbook but unregistered, ledger reference to a missing receipt, security-sensitivity finding. |
| **High** | Breaks a binding rule but not Gate-Covenant. Will block the next operator touching the surface. | Module >600 LOC, function >50 LOC in a hot path, xenon hot-spot above configured band, ruff/ty error not suppressed, doc example drifted from CLI output, frontmatter/ledger disagreement. |
| **Medium** | Drift that compounds silently. Worth scheduling but won't block a near-term change. | Pythonic-pattern candidate, dead code with no tests pinning it, TODO older than 90 days, dependency >2y stale (not yet 5y), CLI verb registered but undocumented. |
| **Low** | Stylistic or cosmetic, fixed by autotools or one-line edits. Bundle into the next opportunistic touch. | ruff-fixable warning, missing docstring, single-line dead import. |

If a finding could be graded two ways, grade up — debt's main failure
mode is being underweighted and ignored.

---

## Step 1: Resolve scope

1. Parse the invocation: scope mode, classes, flags.
2. Resolve the file list per the table above.
3. Save the file list to `.gzkit/audits/tech-debt/<YYYY-MM-DD>/scope.txt`.
   This makes the audit replayable; an operator running the same scope
   later can diff the lists.
4. If `git diff --name-only` returns nothing on `--scope touched`,
   fall back to the most recent commit's files and tell the operator
   you did so.

---

## Step 2: Run the probes

Run probes for every class in scope. **Wield existing tools — do not
re-implement analysis.** Each probe writes its raw output to
`.gzkit/audits/tech-debt/<YYYY-MM-DD>/probes/<class>.txt` so the
report can cite line-grounded evidence.

For each class, the canonical probe:

| Class | Canonical command | Notes |
|-------|-------------------|-------|
| `size-cap` | `uv run radon raw -s <files>` | Filter to functions >50, modules >600, classes >300. |
| `complexity` | `uv run xenon --max-absolute B --max-modules B --max-average A <subtree>` | Capture stderr; non-zero exit IS the signal. |
| `lint` | `uv run ruff check <files> --output-format=json` | JSON for grouping. |
| `types` | `uvx ty check <files>` | Capture stdout; cross-reference `tests/governance/test_type_ignore_syntax.py` for the suppression class. |
| `pythonic` | `uv run gz chores run pythonic-design-pattern-detection` (only on `--scope all` or paths overlap; expensive) | Skip if scope is small and last run is <7 days old. |
| `tests` | `uv run gz arb coverage run -m unittest discover -s tests -t .` then `uv run gz validate --requirements` and `uv run gz validate --behave-req-tags` | Coverage delta + REQ gaps. |
| `dead-code` | `uv run ruff check --select F401,F811,F841 <files>` plus a `vulture` pass if installed | Vulture is best-effort; ruff's the hard floor. |
| `cli-drift` | `uv run gz cli audit` and `uv run gz validate --cli-alignment` | Both must exit 0 to clear the class. |
| `doc-drift` | `uv run gz chores run doc-coverage` and `uv run mkdocs build --strict` | Strict build catches link rot. |
| `frontmatter-drift` | `uv run gz validate --frontmatter`, `uv run gz chores run frontmatter-ledger-coherence` | |
| `dep-currency` | `uv run gz chores run dependency-currency` | |
| `todo-rot` | `git grep -n -E '\b(TODO\|FIXME\|XXX\|HACK)\b' -- <files>` then `git blame` for age on each hit | Skip hits with a `(GHI #N)` reference — those are tracked. |
| `governance` | `uv run gz validate --advisory-scorecard` | Promotable rules are flagged High. |
| `evidence-integrity` | `uv run gz chores run evidence-integrity-audit` | |

**Wrap probes that produce attestable output under ARB** so the report
can cite receipts: `uv run gz arb step --name <class> -- <command>`.
This is required when `--draft-ghis` is set, optional otherwise.

If a probe errors (tool not installed, scope empty, etc.), record
"probe-error: <reason>" as a Medium finding under a `probe-health`
class — never silently drop it. A missing probe is itself debt.

---

## Step 3: Synthesize and rank

For every probe hit, produce a **finding record**:

```
finding_id: <class>-<short-slug>
class: <one of the debt classes>
severity: <Critical|High|Medium|Low>
location: <file>:<line> (or <file> for whole-file findings)
evidence: <one or two lines of probe output, verbatim>
recommendation: <fix shape — see § Recommendation discipline>
route: <one of: in-flight | GHI | OBPI | chore | discard>
```

Save the full finding list to
`.gzkit/audits/tech-debt/<YYYY-MM-DD>/findings.json`.

### Recommendation discipline

The recommendation field names the **fix shape**, not the code.
Diagnose, don't write the patch. Phrase as imperative:

- *"Split `_render_table` (87 LOC) into `_format_rows` and `_emit_table`."*
- *"Replace `# type: ignore[union-attr]` at status.py:412 with `# ty: ignore[unresolved-attribute]` per `.claude/rules/pythonic.md`."*
- *"Drop the `Strategy` class in `cli/parser_artifacts.py:64` to a module-level dispatch dict."*
- *"Doc example at `docs/user/runbook.md:148` shows `gz status` output that drifted from current rendering — paste fresh output."*

**Anti-patterns:**

- Recommendations that say "improve" / "clean up" / "make better"
  without naming the fix shape
- Recommendations that propose adding a feature (debt review never
  expands scope — that's `gz-plan` or `ghi-author`'s job)
- Recommendations that route to "discuss with the team" — operator
  attention is the scarce resource; route concretely or downgrade

### Route discipline

| Route | When |
|-------|------|
| `in-flight` | Severity Low/Medium AND inside the operator's current change scope AND fix is <10 lines AND meets `AGENTS.md § Defect-fix routing` thresholds. Fold into current commit. |
| `GHI` | Severity High/Critical OR fix crosses brief boundaries OR fix is single-issue. Default for cross-cutting findings. |
| `OBPI` | Cluster of related findings (≥3) under one capability or surface. The audit *is* the brief skeleton. |
| `chore` | The class already has a chore (`module-sloc-cap-radon`, `pep257-docstring-compliance`, etc.) — recommend running it on the affected paths. |
| `discard` | Probe-flagged but verified false positive. Note the reason in evidence. |

---

## Step 4: Render the report

Two-section render. Save to
`.gzkit/audits/tech-debt/<YYYY-MM-DD>/report.md`. Print path to chat
along with the table summary; do **not** dump the full report into
chat — operators review the file.

### Section A — Table summary (top)

One table grouping by class, one row per finding, columns:
`Severity | Class | Location | Recommendation | Route`. Sort by
severity descending, then by class. Counts at the bottom: `Critical:
N | High: N | Medium: N | Low: N | Total: N`.

### Section B — Per-finding detail

For each finding (Critical and High only in the body; Medium and Low
collapsed under a `<details>` block), one subsection:

```markdown
### [Severity] <class>: <location>

**Evidence**
> <verbatim probe excerpt>

**Why this is debt**
<one paragraph: which rule / invariant / contract this drift violates,
grounded in a citation to AGENTS.md §, a rule under .gzkit/rules/, or
the chore's CHORE.md>

**Recommended fix**
<imperative fix shape>

**Route:** `<route>` — <one-line rationale>
```

If `--draft-ghis` is set, append a § *Draft GHI bodies* section with
ready-to-paste `gh issue create --label tech-debt` bodies for every
Critical and High finding routed to GHI.

---

## Step 5: Operator handoff

After rendering, print to chat:

1. The report path
2. The Critical/High/Medium/Low counts
3. The top three findings by severity (one line each)
4. The recommended next operator action — one of:
   - *"Route N Critical findings to GHIs now"* (if any Critical present)
   - *"Run chore X on Y findings"* (if a chore-routable cluster dominates)
   - *"Open OBPI for the X cluster"* (if a cluster ≥3 share a capability)
   - *"Bundle Low findings into next opportunistic commit"* (if all-Low)

Do **not** auto-execute the next action. The skill diagnoses; the
operator routes.

---

## Constraints

- **Diagnose, do not patch.** Per the user's choice (option A on
  recommendation style): name the fix shape, do not write the code.
  `gz-obpi-simplify` is the patching skill; this one is the surveying
  skill. The boundary is intentional.
- **Wield existing tools.** Do not re-implement complexity scoring,
  coverage measurement, or pattern detection. The chore/validator
  surface is canonical; the skill's value is synthesis.
- **Cite line-grounded evidence.** Every finding has a probe output
  excerpt. No narrative-only findings — that's the
  `MAKE LLM STOCHASTIC VIBES INERT` failure.
- **Severity grade-up on ambiguity.** Underweighting is the dominant
  failure mode for debt review.
- **Save artifacts under `.gzkit/audits/tech-debt/<date>/`.** The
  audit must be replayable without re-running the model.
- **Respect `simplify-ignore` annotations** (same convention as
  `gz-obpi-simplify`). Code in protected regions is excluded from
  review and reported separately.

---

## Common rationalizations

These thoughts mean STOP — you are about to ship a hollow review:

| Thought | Reality |
|---------|---------|
| "The code looks clean to me" | Spot-reading is not a probe. Run the canonical commands; cite the output. |
| "All the chores already cover this — no point running them again" | The chores cover it *if run*. The probes' purpose is to confirm current state, not to replace the chores. |
| "Severity is subjective; I'll grade them all Medium" | The rubric is binding. Grade per blast radius and reversibility, not per gut. |
| "This finding feels off-scope — I'll skip it" | If the probe surfaced it inside the resolved scope, grade it. Off-scope decision belongs to the route field, not to silent suppression. |
| "I don't have time to write recommendations for all of them" | The recommendation is the deliverable. A finding without a fix shape is noise, not signal. |

---

## Red flags

- Report rendered without any line:column references — synthesis without evidence
- Every finding routed to "GHI" — the skill became a GHI-spammer; route discipline broken
- No Critical findings ever surface — severity grade-up rule is not being applied
- Report rendered before all probes completed — partial audits are not audits
- Recommendations that read "review this" or "consider X" — diagnostic discipline broken

---

## Related skills

| Skill | Relationship |
|-------|--------------|
| `gz-obpi-simplify` | Patching counterpart; runs after this skill identifies a cluster. |
| `gz-pythonic-pattern-detect` | One probe source for the `pythonic` class. |
| `gz-chore-runner` | Wields individual chores; this skill consumes their output. |
| `ghi-author` | Drafts the GHI bodies when `--draft-ghis` is set. |
| `gz-check` | Pre-merge gate; does not produce the cross-class debt report. |
| `gz-plan` / `gz-design` | Where High/Critical clusters route when they need an ADR. |
