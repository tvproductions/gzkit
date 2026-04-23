---
name: ghi-author
persona: main-session
description: Author a GitHub Issue (GHI) for a defect, enhancement, or investigation surfaced in flight. Use when a defect cannot be fixed in the current patch, when scope expansion would violate the active brief's boundaries, or when a finding deserves a trackable home before routing.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-23
metadata:
  skill-version: "1.0.1"
---

# ghi-author

## Invocation

```
ghi-author
```

No ID argument. `gh issue create` assigns the next available issue number on
the remote; the skill records the assigned number into session evidence
after creation (step 6). Passing an ID would conflict with GitHub's
auto-assignment and corrupt cross-references.

Author a GitHub Issue so a surfaced defect, enhancement, or investigation
becomes trackable. This is the mechanical counterpart to `AGENTS.md` §
Prime Directive #6 ("every defect must be trackable") and the upstream of
AGENTS.md § Defect-fix routing (the routing decision consumes the
GHI's evidence — it does not substitute for authoring one).

A GHI that exists only in session memory is not a GHI. The ledger-of-truth
doctrine applies: if the finding has no `gh issue` number, downstream
commits cannot cite it, `fix(<scope>): ... (GHI #N)` trailers cannot form,
and the ARB receipt chain has no anchor.

## Trigger

- A defect surfaces during work on an unrelated brief and cannot be fixed in-scope
- AGENTS.md § Defect-fix routing resolves to "ceremony" or "ambiguous" and the operator needs a trackable artifact before deciding
- Pre-existing defect discovered during audit, reconcile, or review
- Template/doc drift, schema inconsistency, or invariant weakness that needs a home
- Operator says "file a GHI for that" or equivalent

## Behavior

Produce a GHI whose body contains enough evidence for a future agent or
reviewer to re-apply the routing matrix without re-investigating. The
authoring pass does **not** decide direct-fix vs. OBPI ceremony — that is
AGENTS.md § Defect-fix routing's job at fix time. It does produce the evidence the
routing matrix will consume.

## Prerequisites

- `gh auth status` reports authenticated (see `.claude/rules/gh-cli.md` allowed commands)
- Working tree is in a known state (uncommitted scratch work should not leak into the evidence block)
- You have read the surface the defect touches — authoring a GHI without reading the code is vibe-tracking and produces cargo-cult issues

## Steps

1. **Classify the GHI** using the table below. Pick exactly one; a single GHI is one class.

   | Class | Label | When |
   |-------|-------|------|
   | Defect | `defect` | Something observable is wrong, drifted, or inconsistent with canonical intent |
   | Enhancement | `enhancement` | Surface works as designed; the design could be tighter |
   | Investigation | `investigation` | Unknown root cause; the GHI is to find it, not fix it |

2. **Gather evidence.** For a defect, the minimum is:
   - The exact command run and its observed output (paste, don't paraphrase)
   - The canonical source of truth the output contradicts (file path + line, or rule citation)
   - The class of failure (not just the instance — see `AGENTS.md` § DO IT RIGHT #1)

3. **Draft the title.** Format: `<surface>: <symptom>`. Keep under 70 characters; the body carries detail.

   | Good | Bad |
   |------|-----|
   | `validator: pool ADRs skip frontmatter check inconsistently` | `validator broken` |
   | `gz-adr-status: skill routes to adr report, not adr status` | `skill has wrong command` |

4. **Draft the body** using the template below. Omit sections that don't apply (e.g. investigations skip "Expected vs. observed"; enhancements skip "Canonical contradiction").

   ```markdown
   ## Observed

   <exact command + observed output, verbatim>

   ## Expected

   <what the canonical source says should happen, with file:line or rule citation>

   ## Canonical contradiction

   <paste of the rule / schema / doc the observed behavior violates>

   ## Class of failure

   <one sentence: what family of inputs produces this? Not just this instance.>

   ## Scope hint (advisory, for routing)

   - Estimated diff: <≤10 lines / ≤100 lines / larger>
   - Surfaces touched: <module paths>
   - In-flight vs. new feature: <in-flight / planned / unknown>

   ## Related

   - <linked GHIs, ADRs, briefs, rule files>
   ```

5. **Create the issue.**

   ```bash
   gh issue create \
     --label <defect|enhancement|investigation> \
     --title "<surface>: <symptom>" \
     --body "$(cat <<'EOF'
   ...body from step 4...
   EOF
   )"
   ```

6. **Record the issue number** in the session evidence so downstream commits and briefs can cite `(GHI #N)`. If the GHI was filed during an OBPI pipeline run, add it to the brief's evidence section.

## Examples

### Example 1 — Defect surfaced mid-pipeline

**Input**: During OBPI-0.0.16-04 implementation, `uv run gz validate --documents` flagged a pool ADR for drifted frontmatter. Pool ADRs are supposed to skip that check per schema.

**Output**: File `defect` GHI titled `validator: frontmatter check does not skip pool ADRs`. Body includes the exact `gz validate` command output, citation of the pool-skip rule in `src/gzkit/schemas/adr.json`, and a scope hint of "≤10 lines, single file, in-flight." Routing decision deferred — operator applies AGENTS.md § Defect-fix routing at fix time. Trailer candidate: `fix(validator): skip pool ADRs in validate_frontmatter (GHI #192)`.

### Example 2 — Enhancement for a working surface

**Input**: `gz adr status` renders a Rich table correctly, but the lane column abbreviates "heavy" to "H" which operators consistently misread.

**Output**: File `enhancement` GHI titled `gz adr status: lane column abbreviation hurts legibility`. Body includes a screenshot/paste, the operator feedback, and a proposal ("spell out heavy/lite; alignment issue only, no schema change"). Not a defect — the verb does what it says; the taste is off.

### Example 3 — Investigation, root cause unknown

**Input**: Reconciliation caches are regenerating at 3x the expected rate across sessions. No specific failure observed; the cost signal is what surfaced it.

**Output**: File `investigation` GHI titled `reconcile: cache regenerates more often than expected`. Body skips "Expected vs. observed" (no canonical baseline yet); includes the cost signal, the observation window, and candidate hypotheses. The GHI is the home for the investigation itself — closing it will produce either a defect GHI with a known fix or a documentation update explaining the observed rate as correct.

## Constraints

- **Never author a GHI with the user's personal email in the body, title, or evidence block.** Use GitHub noreply or just a name; see `AGENTS.md` § Local Agent Rules.
- **Never paraphrase observed output.** Paste verbatim or cite the file:line. Narrative reconstruction is the reporting-pathway drift `AGENTS.md` § DO IT RIGHT 6h exists to prevent.
- **Never bundle unrelated defects into one GHI.** One GHI, one class of failure. Bundling creates a routing ambiguity the matrix cannot resolve.
- **Never author a GHI to substitute for fixing something you could fix now.** The Prime Directive #4 (scope expansion is not scope creep) takes precedence — file a GHI only when the fix genuinely cannot land in-patch.

## Common Rationalizations

These thoughts mean STOP — you are about to produce a low-quality GHI:

| Thought | Reality |
|---------|---------|
| "I'll just file it and fill in the body later" | A GHI with a thin body is worse than no GHI — it guarantees the next agent re-investigates. Author the evidence block now. |
| "The title is enough; reviewers will figure it out" | Reviewers are not clairvoyant. The body consumes the evidence the routing matrix needs. |
| "This defect is obvious; I don't need to cite the rule" | The canonical contradiction is what makes it a defect rather than a taste call. Cite the rule, schema, or doc. |
| "I'll combine both issues into one GHI to save numbers" | GHI numbers are free. Combining couples two routing decisions into one and corrupts the fix's scope boundary. |
| "I can write 'see session log for details'" | Session logs are Layer-3 derived state and are not canonical. Paste the evidence into the GHI body. |

## Red Flags

- GHI title is a bare noun or a vague verb ("broken", "issue", "problem")
- Body contains "TODO add evidence" or equivalent placeholder
- Multiple unrelated defects bundled into one GHI
- No label applied (breaks `gh issue list --label <class>` triage)
- Personal email or other PII in the body
- Filed as a replacement for a fix that was in-scope and skipped

## Related Skills

- `ghi-close` — evaluate and close a GHI (the downstream surface)
- `gz-obpi-specify` — when routing resolves to OBPI ceremony, the brief consumes this GHI's evidence
- `git-sync` — commits citing `(GHI #N)` trailers flow through sync

## Related Rules

- `AGENTS.md` § Prime Directive #6 (every defect must be trackable)
- `AGENTS.md` § DO IT RIGHT #1 (fix the class, not the instance — the GHI must name the class)
- `AGENTS.md` § DO IT RIGHT 6h (verbatim quotes, not narrative reconstruction)
- `.claude/rules/gh-cli.md` (allowed `gh` commands)
- AGENTS.md § Defect-fix routing (the routing decision this GHI's evidence will feed)
- `AGENTS.md` § Local Agent Rules (operator PII — never in the GHI body)
