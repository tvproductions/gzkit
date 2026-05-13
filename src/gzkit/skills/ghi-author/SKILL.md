---
name: ghi-author
persona: main-session
description: Author a GitHub Issue (GHI) for a defect, enhancement, or investigation surfaced in flight. Use when a defect cannot be fixed in the current patch, when scope expansion would violate the active brief's boundaries, or when a finding deserves a trackable home before routing.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-12
metadata:
  skill-version: "1.3.0"
model: sonnet
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

## Doctrine — A GHI's purpose is observation routing, not implementation tracking (binding)

A GHI exists to **route an observation to a durable governance artifact**.
Once the finding has been homed in a registered destination (a commit SHA,
a foundation/feature ADR, a pool ADR, an OBPI brief, or a higher-numbered
GHI that absorbs the scope), the GHI's purpose is **fulfilled** and the
GHI is closable. Implementation lifecycle thereafter belongs to the
destination artifact, not to the GHI.

This rule closes a failure mode where GHIs accumulate as long-lived
"wait-around trackers" that shadow-track work already owned by an ADR or
OBPI. A pool ADR has its own promotion ceremony; a foundation ADR has its
own gate covenant; an OBPI has its own pipeline. None of those need a
GHI sitting open to remind anyone that they exist — the artifact graph
already does that.

**Operative consequences for the authoring pass:**

1. **When a finding's right home is a pool ADR or OBPI brief, author the
   destination in the same session as the GHI** — using `gz plan create
   --kind pool ...` or `gz-design` → `gz-plan` → `gz-obpi-specify`. The
   GHI then closes immediately with `superseded` disposition citing the
   destination ID. One observation, one routing pass, one terminal state.
2. **Pool ADRs count as registered destinations.** A pool ADR visible in
   `uv run gz adr report` (Pool table) is a valid `superseded` upstream
   under `ghi-close`'s rules — it is registered in the artifact graph
   even if not yet promoted to foundation or feature kind. Promotion is
   the destination's lifecycle, not the GHI's.
3. **Multiple GHIs may share one destination.** A symptom GHI (concrete
   reproduction), a class-of-failure GHI (broader pattern), and an
   architectural-absence GHI (the missing artifact) can all close
   `superseded` against one pool ADR — each GHI is a different cut into
   the same finding, and the ADR carries them collectively.
4. **GHIs that cannot be routed in-session stay open with a blocker
   comment.** This is the inverse of dead-lettering (see `ghi-close` §
   Doctrine — NEVER, EVER, EVER dead-letter a GHI). Open-with-blocker is
   the honest state when the destination cannot yet be authored;
   closed-with-route-promise is the corrupted-audit-trail state.

**Anti-pattern:** Filing a GHI and treating it as a long-lived tracker
that "closes when the work ships." The work shipping is the destination
artifact's responsibility (its own gates, its own attestation, its own
ledger events). A GHI that waits around to mirror the destination's
status is duplicate state — the same shape Layer-3 derived views become
when they silently shadow Layer-2 truth.

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

0. **Prior-art lookup (binding pre-flight — MANDATORY).** Before drafting anything, search for adjacent open GHIs and recent closes. Skipping this step is a process defect; resulting duplicates are withdrawable on discovery under `ghi-close`'s `withdrawn` disposition with a one-line "duplicate of #N" comment.

   Two queries — keyword search PLUS recent-by-date skim. Keyword search alone misses semantic neighbors that share root cause without sharing surface words.

   ```bash
   # Keyword search across open + recent closes (last 30 days).
   # Use 2–3 surface keywords from the observed symptom, not narrative phrasing.
   gh issue list --state all --search "<keywords> created:>=$(date -v-30d +%Y-%m-%d)" --limit 20 \
     --json number,title,state,labels,createdAt

   # Recent open by date — catches semantic neighbors keyword search misses.
   gh issue list --state open --limit 20 --json number,title,labels,createdAt
   ```

   Read every title in both result sets (titles are cheap; read bodies only on candidate hits). Decide which branch you are on:

   | Result | Action |
   |--------|--------|
   | An open GHI already covers this exact finding | **Do not file.** Add a comment to the existing GHI with this session's new evidence; record the issue number in session evidence; stop. Duplicate-filing is the failure mode this step closes. |
   | An open GHI covers an adjacent / sibling-cut of the same root cause | Author this GHI but include `Related: #N` in the body's `## Related` section AND post a cross-link comment on the sibling GHI naming the relationship (root vs. symptom, per-skill vs. catalog-wide, etc.) at authoring time, not as a follow-up |
   | A recently-closed GHI (≤30 days) addressed this exact finding | Re-open it (`gh issue reopen <N>`) with a comment citing the regression evidence — never file a fresh GHI for the same root cause |
   | No prior or adjacent GHI exists | Proceed to Step 1 |

   **Canonical sibling-cut regression:** GHIs #459 and #460 (2026-05-12) shared the T1→T2 doctrine-drift root cause (skill prose declares an agent action with no mechanical fail-close) but shared no title keywords — #459 named the per-skill Stage 2 dispatch gap, #460 named the catalog-wide skill-body-as-procedural-script surface. #460 was filed ~17 minutes after #459 without cross-link at authoring time; the relationship was only recorded in a follow-up comment after the operator noticed the overlap. The recent-by-date skim catches this class even when keywords disagree.

   The pre-flight is **defense, not guarantee** — semantic neighbors may evade both queries. When in doubt, surface the candidate matches to the operator with the routing facts (open GHI numbers + one-line title-summaries + relationship hypothesis) before proceeding to Step 1.

1. **Classify the GHI** using the table below. Pick exactly one; a single GHI is one class.

   | Class | Label | When |
   |-------|-------|------|
   | Defect | `defect` | Something observable is wrong, drifted, or inconsistent with canonical intent |
   | Enhancement | `enhancement` | Surface works as designed; the design could be tighter |
   | Investigation | `investigation` | Unknown root cause; the GHI is to find it, not fix it |

   **Secondary labels (binding — additive, not exclusive):** apply each label below whose predicate fires. Multiple secondary labels may co-apply with one primary class.

   | Label | Apply when | Why it matters |
   |-------|------------|----------------|
   | `runtime` | The GHI's evidence cites a path under `src/gzkit/`, OR the symptom is observable behavior change at the `gz` CLI / runtime surface, OR the prescribed remedy is a `fix(...)` commit landing under `src/gzkit/` | `gz patch release --dry-run` qualifies behavior-level GHIs by `runtime` label ∩ src diff. A runtime-touching GHI without this label lands in the `diff_only` bucket and silently drops out of the patch-release narrative — the strict qualifier returns 0 even when 16 substantive runtime fixes have shipped (canonical violation: GHI #402, 2026-05-05) |
   | `tech-debt` | The fix is a remediation of accumulated drift rather than a new defect | Routes the GHI into tech-debt sweeps and chore plans |
   | `security` | The surface is registered in `data/security_surfaces.json` or the symptom has an attack-surface dimension | Triggers heightened Gate 5 walkthrough per `.gzkit/rules/security-sensitivity.md` |
   | `eval-feedback` | The GHI was authored from an evaluation-feedback loop event | Required for the `Eval-feedback-source:` commit trailer per ADR-0.0.26 |

   **Predicate heuristics for `runtime`** (any one fires the label): GHI body contains `src/gzkit/` as a path; the "Affected surfaces" section names a Python module under `src/`; the symptom block shows `uv run gz <verb>` output disagreeing with canonical intent; the prescribed remedy is shaped as `fix(<scope>): … (GHI #N)`. If the predicate fires, `--label runtime` is mandatory at `gh issue create` time, not deferrable to later operator triage.

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

5. **Create the issue.** Include the primary class label AND every secondary label whose Step-1 predicate fired. Repeat `--label` per label; a runtime-touching defect that also remediates accumulated drift would carry `--label defect --label runtime --label tech-debt`.

   ```bash
   gh issue create \
     --label <defect|enhancement|investigation> \
     [--label runtime] \
     [--label tech-debt] \
     [--label security] \
     [--label eval-feedback] \
     --title "<surface>: <symptom>" \
     --body "$(cat <<'EOF'
   ...body from step 4...
   EOF
   )"
   ```

6. **Record the issue number** in the session evidence so downstream commits and briefs can cite `(GHI #N)`. If the GHI was filed during an OBPI pipeline run, add it to the brief's evidence section.

7. **Route to a destination, then close.** Per § Doctrine — A GHI's purpose is observation routing, decide whether the finding has a same-session destination:

   | Finding shape | Destination | Same-session action |
   |---|---|---|
   | Direct-fix candidate (passes AGENTS.md § Defect-fix routing thresholds) | Commit SHA | Apply the fix, commit `fix(<scope>): … (GHI #N)`, close `fixed` citing the SHA |
   | Architectural absence / new-capability finding | Pool ADR | `uv run gz plan create <slug> --kind pool --lane <lite|heavy> --title …`, then close `superseded` citing `ADR-pool.<slug>` |
   | Bounded planned-increment finding under an existing active ADR | OBPI brief | `gz-obpi-specify` against the parent ADR, then close `superseded` citing the new OBPI ID |
   | No same-session destination yet (genuinely needs operator design conversation) | None yet | Leave the GHI **open** with a blocker comment naming the next concrete operator action — see `ghi-close` § Doctrine — NEVER, EVER, EVER dead-letter a GHI |

   Routing-and-closing is the normal completion path. Filing-and-leaving-open is the exception, not the default. A GHI sitting open without a blocker comment is a tracker waiting for a destination — author the destination or surface the blocker.

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

### Example 4 — Architectural absence, route to pool ADR + close in same session

**Input**: During OBPI-0.0.21-08 closeout, the operator surfaced that gzkit's governance surface is "choreographed not state-machined" — there is no canonical state machine, no runtime invariant monitor, and silent state demotions go unnoticed (concrete symptom: `gz frontmatter reconcile` rewrote a hand-marked `Withdrawn` brief to `pending` because no withdrawal transition exists).

**Output**: This is two findings — a concrete observed symptom and a class-level architectural absence. File **two GHIs**, one per finding shape:
1. A `defect` GHI for the silent demotion (concrete reproduction, expected vs. observed, citation of ADR-0.0.9 Rule 1 the reconciler was honoring).
2. An architectural-absence GHI listing the symptom-class with citations across `STATUS_VOCAB_MAPPING`, GHI #290/#292 bolted-on guards, reconcile-then-precomplete loops, frontmatter rewrite cascades.

**Same-session routing:** the right destination is a pool ADR (the design conversation is genuinely architectural, but no existing ADR absorbs it). Author it via `uv run gz plan create obpi-state-machine --kind pool --lane heavy --title "OBPI State Machine and Runtime Invariant Monitor"`, populate Intent / Decision / four rejected alternatives / ADR relationship matrix / OBPI promotion plan grounded in the GHIs' evidence, commit. Then close **both** GHIs `superseded` citing the pool ADR ID. The GHIs' purpose (route the observations to a durable home) is fulfilled; the pool ADR's lifecycle (promotion → foundation gates → OBPI ceremony) owns implementation.

**Anti-pattern this example replaces:** filing the architectural-absence GHI with an acceptance criterion of "closes when state machine ships" and leaving it open for months as a stale tracker. The pool ADR is the tracker; the GHI was the routing artifact, and routing is complete.

## Constraints

- **Never author a GHI with the user's personal email in the body, title, or evidence block.** Use GitHub noreply or just a name; see `AGENTS.md` § Local Agent Rules.
- **Never paraphrase observed output.** Paste verbatim or cite the file:line. Narrative reconstruction is the reporting-pathway drift `AGENTS.md` § DO IT RIGHT 6h exists to prevent.
- **Never bundle unrelated defects into one GHI.** One GHI, one class of failure. Bundling creates a routing ambiguity the matrix cannot resolve.
- **Never author a GHI to substitute for fixing something you could fix now.** The Prime Directive #4 (scope expansion is not scope creep) takes precedence — file a GHI only when the fix genuinely cannot land in-patch.
- **Never omit a secondary label whose Step-1 predicate fired.** Missing `runtime` on a runtime-touching GHI silently drops it from `gz patch release` qualification; missing `security` defeats the Gate-5 walkthrough trigger; missing `eval-feedback` breaks the commit-trailer requirement under ADR-0.0.26. Secondary labels are not optional triage hints — they are mechanical inputs to downstream gates.
- **Never call `gh issue create` outside this skill.** Bypassing `/ghi-author` skips Step 0's prior-art lookup, which is the only defense against sibling-cut duplicates (canonical regression: GHI #459/#460, 2026-05-12). The binding agent rule lives at `AGENTS.md` § Behavior Rules — Always #13; the skill is the mechanical home of the pre-flight. Cross-repo filing goes through `gz issue file`, which itself must run Step 0's pre-flight against the target repository before delegating to `gh issue create`.

## Common Rationalizations

These thoughts mean STOP — you are about to produce a low-quality GHI:

| Thought | Reality |
|---------|---------|
| "I'll just file it and fill in the body later" | A GHI with a thin body is worse than no GHI — it guarantees the next agent re-investigates. Author the evidence block now. |
| "The title is enough; reviewers will figure it out" | Reviewers are not clairvoyant. The body consumes the evidence the routing matrix needs. |
| "This defect is obvious; I don't need to cite the rule" | The canonical contradiction is what makes it a defect rather than a taste call. Cite the rule, schema, or doc. |
| "I'll combine both issues into one GHI to save numbers" | GHI numbers are free. Combining couples two routing decisions into one and corrupts the fix's scope boundary. |
| "I can write 'see session log for details'" | Session logs are Layer-3 derived state and are not canonical. Paste the evidence into the GHI body. |
| "I'll file this and let it track until the work ships" | A GHI is not an implementation tracker. The destination artifact (commit / ADR / OBPI) tracks implementation through its own lifecycle. File the GHI, route it to a destination in the same session, close it. If you cannot route in-session, open with a blocker comment — never open as a long-lived shadow tracker. |
| "This finding is too big for a fix and there's no ADR yet — I'll just leave it open" | If the right home is a pool ADR, **author the pool ADR in the same session** via `uv run gz plan create <slug> --kind pool --lane <lane> --title "..."` populated with Intent / Decision / rejected alternatives grounded in the GHI's evidence. Then close `superseded` citing the pool ADR. Pool ADRs are valid `superseded` destinations because they are registered in `gz adr report`. |
| "I already know this finding is novel — I'll skip the prior-art lookup and save the round-trip" | **Step 0 is mandatory, not advisory.** The canonical sibling-cut regression (#459/#460) was filed by an operator who had filed both issues themselves minutes apart — confidence in novelty is precisely the failure-state. The two `gh issue list` queries take seconds; skipping them produces duplicate-scoped GHIs that bypass `ghi-close`'s destination-routing rule and dilute triage. |
| "I'll call `gh issue create` directly — faster than going through the skill" | **Direct `gh issue create` invocations are a process defect** per `AGENTS.md` § Behavior Rules — Always #13. The skill is not optional ergonomics; it is the mechanical home of Step 0's prior-art lookup. Bypassing the skill bypasses the only defense against sibling-cut duplicates. |

## Red Flags

- GHI title is a bare noun or a vague verb ("broken", "issue", "problem")
- Body contains "TODO add evidence" or equivalent placeholder
- Multiple unrelated defects bundled into one GHI
- No label applied (breaks `gh issue list --label <class>` triage)
- Body cites `src/gzkit/` paths, `gz <verb>` runtime symptoms, or a `fix(...)` remedy shape but the `gh issue create` invocation omits `--label runtime` — this is the GHI #402 silent-qualifier-drift signature
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
