# Reachability Matrix — Skill ↔ Rule (Pass B)

> Chore: `control-surface-skill-rule-reachability` (Lite lane, audit-only)
> Run: **2026-08-09**. Supersedes the 2026-08-01 matrix.
> Surface: **68 skills** under `.gzkit/skills/**` × 26 canonical rules.
> Vendor mirrors are derivatives and were not audited.

**Applicability test** (CHORE.md): a rule applies when (a) `paths:` frontmatter
overlaps, (b) the skill's procedure invokes a CLI verb the rule governs, or (c) the
skill modifies files the rule's `paths:` covers.

**Honors test:** the skill body cites the rule by filename **or** enforces its
invariant mechanically. Absence of both is a reachability gap.

**Admission bar:** a `no` row requires a **concrete worked example** — a specific
point in the procedure where following it violates the rule. "The skill doesn't
mention the rule" is not a gap.

## Counts

| Measure | Value |
|---|---|
| Skills audited | **68** |
| Applicable pairs | **624** (618 by path overlap, +6 by CLI-verb basis) |
| Honored by citation | 21 — **4 of which resolve only through a `.claude/rules/` mirror** |
| Honored mechanically | 8 |
| **Gaps with a worked example** | **11** (9 known-blocking, 2 latent) |

The citation rate is 21 of 624 applicable pairs. That number is not itself the
finding — most pairs are trivially applicable via a broad `paths:` glob. The finding
is the 11 rows below, each of which has a procedure that can actually collide.

---

## Gaps — known-blocking

### N1 · `gz-agent-sync` (1.1.1) ↛ `skill-surface-sync.md` § Non-negotiable #6 · GHI #492

**Basis:** path-overlap + file-modification — the skill's entire subject is
propagating skill surfaces.

§ Common Rationalizations answers *"I bumped `last_reviewed` instead of
`skill-version`"* with *"Version mismatch is the conflict-resolution signal…
**Bump the version.**"* An agent taking that remedy lands `skill-version`
incremented with `last_reviewed` unchanged — **exactly the state rule #6 forbids**
(*"Any commit that increments `skill-version:` … MUST also set `last_reviewed:` to
today's date"*). § Red Flags reinforces the asymmetry: it lists *"Skill edits
without a `skill-version` bump"* and never the `last_reviewed` half.

**No mechanical arm exists.** `gz validate --skill-version-review-coupling` was
never built; it is parked in the unpromoted `ADR-pool.skill-version-review-coupling`.
`skills_audit._validate_last_reviewed` checks only 90-day staleness in isolation, so
it cannot see the coupling.

### N2 · `gz-obpi-pipeline` (6.35.0) ↛ `model-selection.md` § Operative claims #4 · GHI #284

**Basis:** path-overlap — the rule's `paths:` names `.gzkit/skills/**/SKILL.md` and
`src/gzkit/pipeline_runtime.py`, which the skill declares as its runtime.

Stage 2 step b (`:273-276`) selects `simple → haiku / standard → sonnet /
complex → opus`, and step d (`:290-297`) passes `model: <selected tier from step b>`
into the Agent call — **a model name**. The rule: *"Subagents use effort directives,
not model names. The Agent tool maps effort → model"*; claim 4: *"Subagent prompts
specify effort level, not model name."* Repeats at the review dispatch (`:313`,
`:327-338`). No skill in the catalog cites `model-selection.md`; no validator arm.

### N3 · `gz-obpi-pipeline` (6.35.0) ↛ `model-selection.md` § Operative claims #5 · GHI #643

**Basis:** path-overlap + procedure — the skill dispatches all four personas and
relays their output into Gate 5.

Stage 4 (`:551`) dispatches a `narrator` subagent to *"render the final attestation
surface"*, and that template is immediately called *"the human's attestation surface.
They cannot provide attestation without seeing this output."* **No step instructs
the orchestrator to re-derive** the narrator's Value Narrative / Key Proof /
files-created rows before presenting. Claim 5: *"Never relay a subagent's factual
assertion into ceremony, attestation, or an operator-facing conclusion on the
subagent's word — cite the ARB receipt, the file, or re-run the command yourself."*

The `gz validate --pipeline-review-receipts` the skill names at `:40`/`:551` would
attest only that the dispatch happened — and both mentions say it awaits pool-ADR
promotion. **The flag is not registered in `validate_cmd.py` today.**

### N4 · `gz-obpi-lock` (6.2.0) ↛ `token-block-discipline.md` § Binding Sub-Invariant 5 · GHI #619

**Basis:** cli-verb (`gz obpi lock release`, named verbatim in the rule) +
path-overlap (`.gzkit/locks/exchange/**`).

§ Procedure → Release (`:105-110`) prescribes
`uv run gz obpi lock release OBPI-X.Y.Z-NN --force` with the comment
*"abort/handoff — bypass ownership check"* and asserts *"Exit code 0 = released
(or no lock found)"*. But `--force` bypasses **only** the ownership check: Sub-Invariant
5 refuses release unless a valid exchange register entry exists **or** the caller
passes `--abandon <category>:<reason>` — a real registered flag
(`obpi_lock.py:130-156`, whose docstring reads *"Releasing without `--abandon` AND
without a matching register entry is [refused]"*).

**The strings `--abandon`, `exchange`, and `register entry` appear zero times in the
skill.** Compounding: `:82` teaches *"**Release** deletes the lock file"* and `:84`
*"locks older than TTL are automatically released on next claim attempt"* — the
latter is verbatim the rule's § Sub-Invariant 3 anti-pattern.

### N7 · `gz-check` (1.5.0) ↛ `gate5-runbook-code-covenant.md` § Do Not · GHI #317

**Basis:** path-overlap + cli-verb.

§ Full Quality Evidence Sequence (`:75-84`) is headed *"When deterministic receipts
are needed (e.g., for audit evidence):"* and then prescribes **bare** `uv run gz lint`,
`uv run gz typecheck`, `uv run gz test --bdd`, `uv run gz check`. The rule's § Do Not:
*"Do not cite bare `uv run gz lint` … as attestation evidence — they produce no
`arb-*` receipt"*; § Validation bundle: bare commands *"**do not satisfy** the Gate-5
evidence requirement"*.

An agent following the skill — per its own § When to Use, *"Pre-merge /
pre-attestation"* — carries a **zero-receipt sequence into attestation.**

### N8 · `gz-tidy` (1.1.1) and `gz-check` (1.5.0) ↛ `agents-md-map-doctrine.md` § Budget · GHI #373

**One class, two instances.** Basis: path-overlap + file-modification.

`gz-tidy:45` — *"**CLAUDE.md budget**: Check CLAUDE.md line count. If over 200
lines, flag for pruning"* (reinforced `:79`); `gz-check:70-73` repeats it. The rule
(`:30`): *"The **live enforced budgets are the values in
`data/instructions_files_budget.json`** … This doctrine never duplicates those
numbers into prose: a duplicated number drifts from what is enforced."*

**The enforced value is `"CLAUDE.md": 15000` chars — not 200 lines.** Neither skill
references the JSON, `gz validate --instructions-files-budget`, or `/gz-context-diet`
(grep count 0 in both). This is the doctrine's own prohibition, violated by two
skills, in the exact way it predicts.

### N9 · `ghi-close` (2.7.0) ↛ `task-discovery.md` § Invariant · GHI #552

**Basis:** file-modification — the skill's Phase 2 authors commits touching
`src/gzkit/**` and `tests/**`; its own worked example (`:384`) names
`src/gzkit/governance/trust_audits.py`, `src/gzkit/schemas/adr.json`, and two new
unit tests.

Step 6 (`:255`) — *"**Commit with the trailer.** Every closing commit body MUST
contain `(GHI #N)` or a `Closes #N` / `Fixes #N` trailer"* — presents the GHI form
as the **complete** trailer contract, and Step 7a's verification (`:261`) greps only
those three forms. The rule's floor: *"any commit touching `src/**` or `tests/**`
MUST additionally carry a `Task:` trailer"*, fail-closed by
`gz validate --commit-trailers`.

**`Task:` appears zero times in `ghi-close/SKILL.md`**, and the direct-fix path it
prescribes has no in-progress TASK for the `prepare-commit-msg-task-trailers`
producer to stamp from.

### N10 · `gz-obpi-simplify` (6.1.0) ↛ `complexity-thresholds.md` § Invariant · GHI #652

**Basis:** file-modification.

Dimension 2 (`:144`) flags *"Functions exceeding 50 lines or modules exceeding 600
lines"*; `:158` says *"For each finding: fix it directly."* The rule: *"A new
threshold authority appearing anywhere else is doctrine drift by another name."*
The canonical table blocks `lizard_nloc` at **37.00** and `radon_raw_nloc` at
**1031.90** — so the skill **rewrites modules the table does not warn on and passes
functions the table blocks**, in both directions.

`pythonic.md:29` already carries the resolution and the skill does not follow it:
*"treat <=300 as binding (it gates), <=50 and <=600 as guidance, and **cite the
table — not this rule — for any threshold claim**."* The sibling chore
`module-sloc-cap-radon` was repointed off these identical numbers on 2026-08-01
quoting this same Invariant; `gz-obpi-simplify` (`last_reviewed: 2026-07-26`) was
not swept.

### N11 · `gz-cli-audit` (0.1.1) ↛ `cli.md` § Core Principles — Consistency · GHI #353

**Basis:** cli-verb — `cli.md:15` declares *"**Mechanical check:** `uv run gz cli
audit`"*, and the skill's entire Workflow is that one verb.

The skill's terminal step (`:23`) is *"Summarize results, including evidence and any
follow-up gates."* The rule binds: *"If coverage is missing, author the missing
artifacts in the same patch — the audit is the mechanical check, not operator
taste."* **The skill has no remediation step and no exit-code contract**, so a red
`gz cli audit` legitimately terminates it with a report plus a deferral — which is
how the 48-item per-flag documentation backlog accumulated.

## Gaps — latent

### N5 · `gz-adr-audit` (6.13.0) ↛ `adr-audit.md` § Audit sequence steps 2 and 4

Step 2's re-verification block (`:168-169`) runs **bare** `uv run -m unittest -q`
and `uv run mkdocs build -q`, redirecting into
`docs/design/adr/…/audit/proofs/*.txt`, which Step 4 (`:201`) indexes as
*"Evidence index"*. Rule step 2: *"Run quality checks via the **ARB-wrapped
canonical invocations**. Bare commands emit no receipt; step 4 then fail-closes at
exit 3."* (`mkdocs build -q` is not even the canonical `--strict` form.) Step 8.3
(`:259-263`) emits `--evidence-json` with **no `receipts` key**, and the skill's own
"Recommended evidence fields" table (`:317-323`) never lists `receipts` — the exact
zero-citation payload the rule says fail-closes.

### N6 · `gz-adr-audit` (6.13.0) ↛ `adr-audit.md` § Rules

The rule states flatly *"Do not run `gz audit` before attestation."* The skill
instructs `uv run gz audit <adr-id>` at `:92`, `:146`, and `:156` — all preceding
Step 7 "Mark VALIDATED" and Step 8 "Emit Validation Receipt". Nothing cites
`adr-audit.md`; the ordering has no validator arm.

---

## Prior-row accounting — all 25 rows plus the six structural notes

Every prior row has a verdict. **Carried: 23. Closed: 2. Refuted: 1 premise.**

| Prior row | Verdict | Basis |
|---|---|---|
| 1 `adr-audit.md` | carried | Zero skill cites; `gz-adr-audit` cites `tests.md` and never the audit rule |
| 2 `agent-failure-modes.md` | carried | Cites rose 1→2 (`gz-issue-file:82`, `gz-obpi-specify:127`); 66 of 68 skills still never name it |
| 3 `agents-md-map-doctrine.md` | carried | `gz-context-diet:39` still the only mechanical arm; `--agents-md-map-conformance` invoked by zero skills |
| 4 `brief-heading-conventions.md` | carried | Zero cites; `--brief-headings` invoked by zero skill bodies |
| 5 `changelog-release-notes.md` | carried (non-gap) | `gz-patch-release` cites at `:226`/`:298` and invokes `--changelog` at `:310`/`:316` |
| 6 `chores.md` | carried | Zero cites; rule § Related names `gz-chore-runner`, which does not name it back |
| 7 `cli.md` | carried | Zero cites — the prior run's four apparent hits were `gh-cli.md` substring matches; a boundary-anchored grep returns none |
| 8 `complexity-doctrine.md` | carried (non-gap) | `gz-complexity-distill:55, :152` |
| 9 `complexity-thresholds.md` | carried | Zero cites; now has a worked example (N10) |
| 10 `cross-platform.md` | carried | Zero cites; no ruff arm |
| 11 `gate5-runbook-code-covenant.md` | carried | Rule 0.2.0→0.3.0; reachability unchanged; § Do Not now has a worked example (N7) |
| 12 `gh-cli.md` | carried | 4 cites; `git-sync` still cites nothing |
| 13 `governance-core.md` | carried | Sole cite is the **mirror** path (`gz-adr-create:113, :270`) |
| 14 `guardrail-feedback-prose.md` | carried (posture re-based) | Rule 0.1.0→0.2.0 replaced § Mechanical promotion path with § Enforcement posture — the row's "no mechanical arm" is now the rule's **settled disposition**, not a pending promotion |
| 15 `hexagonal-architecture.md` | carried | `gz-design:137`, `gz-patch-release:65` both point at the `docs/governance/` copy; the rule file is named by zero skills |
| 16 `model-selection.md` | carried | Path-bound to all 68 skills; zero cites. Rule 0.3.0→0.5.1 added two new binding clauses no skill routes to (N2, N3) |
| 17 `models.md` | carried | `gz-deps-upgrade` cites AGENTS.md § STDLIB-FIRST and never `models.md` |
| 18 `mx-mode.md` | **closed** (rule-internal) + carried (reachability) | Marker/blockquote mismatch closed at `afa215257`; a repo-wide comparison now returns zero mismatches |
| 19 `pythonic.md` | carried | Sole cite is the **mirror** (`gz-tech-debt-review:197`) |
| 20 `security-sensitivity.md` | carried | Sole cite `ghi-author:149`; `--sensitivity` invoked by zero skills |
| 21 `skill-surface-sync.md` | carried | `gz-agent-sync` — the rule's own wielder — still doesn't name it; now has a worked example (N1) |
| 22 `task-discovery.md` | carried | `grep -cniE "task:\|trailer\|@advances\|TASK-" git-sync/SKILL.md` → **0**, unchanged |
| 23 `tests.md` | carried | Best-cited; same 5 skills |
| 24 `token-block-discipline.md` | carried (arm renamed) | Mechanical arm moved with GHI #763 — `gz-session-handoff:101` now invokes `--lock-exchange-coupling`. The `gz-obpi-lock` release arm is still unrouted (N4) |
| 25 `tool-skill-runbook-alignment.md` | carried | Rule 0.2.0→0.3.0 added § Enforcement posture (Inv 1 mechanical, Inv 2/3 advisory **by design**) |
| D1 dangling `§ Commit-message discipline` | carried (worsened) | No such section exists in the rule; content lives in the rationale doc. `ghi-close` cite sites grew 2→3, all on the mirror path |
| D2 `gz ledger tail` | **closed** | `6a4620985` (GHI #745) — replaced by a `grep` at `gz-content-compose:56`; root cause also gone (extraction consolidated into `verb_references.py`, with `.gzkit/skills/**/SKILL.md` now in `_cli_alignment_sources`) |
| D3 `gz-deps-upgrade` H1 | carried | `SKILL.md:14` is still `# gz deps-upgrade`; a markdown H1 matches none of the four recognizers in `verb_references.py`, so it escapes `--cli-alignment` |
| D4 `tests.md § Tests assert semantics` | carried | Still a bold lead-in at `tests.md:65`, not a heading; five call sites unchanged |
| D5 `.claude/rules/arb.md` | carried (not a defect) | `ghi-close:350` quotes GHI #291's title; sealed record |
| Mirror-path table | carried | Five mirror cites unchanged in kind |
| Name-collision hazard | carried | `.gzkit/rules/hexagonal-architecture.md` ↔ `docs/governance/hexagonal-architecture.md` and `.gzkit/rules/AGENTS.md` ↔ `docs/governance/AGENTS.md` both still exist; both skill cites resolve to the docs copy |

### Refuted premise — the row set was never single

**`src/gzkit/chores/control-surface-skill-rule-reachability/proofs/` is a second,
stale copy shipped in the wheel.** Its `reachability-matrix.md` is 24 KB, dated
2026-05-08, skill-centric, 50 rows — a different document from the project copy
this ledger accounts for.

Verified this run, and the scope is wider than one chore:

```
$ ls -d src/gzkit/chores/*/proofs | wc -l
29
$ find src/gzkit/chores -path '*/proofs/*' -type f | wc -l
71
$ grep -n "always project-local" .gzkit/rules/chores.md
35:`proofs/` is **always project-local, never canonical** — execution evidence is
$ python3 -c "…json.load(open('data/distribution_baseline_manifest.json'))…"
proofs mentions in baseline manifest: 0
```

**29 chore directories ship a `proofs/` folder into the wheel surface — 71 files —
from a location two rules declare carries no proofs content**
(`chores.md` § Two-Surface Layout; `skill-surface-sync.md` § class-classifier). The
distribution baseline manifest does not mention `proofs` at all, so
`gz validate --distribution` has nothing to compare against.

Consequence: the 50 rows the 2026-08-01 pass dropped did not disappear — **they are
still shipping to adopters**, alongside 70 other stale evidence files, from a
surface that is supposed to be regenerated-only. Routed as a defect below; not
fixed here (this chore is read-only on everything but its own `proofs/`).
