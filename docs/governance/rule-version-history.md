# Rule Version History (lifted)

Verbatim version-history chains lifted out of `.gzkit/rules/**` by the
`instructions-files-diet` chore on 2026-08-02, under the operator ruling
*"rule on the surface-weight ceiling: do the diet pass"*.

**Why these moved.** `.gzkit/rules/skill-surface-sync.md` § Non-negotiable
rules specifies the marker shape as *"a visible `> **Rule version:** `X.Y.Z``
block quote with a one-sentence rationale."* Accumulated multi-version chains
had grown to 6–29 lines each on the per-turn surface, exceeding the contract
they were written against. Each rule now carries its current-version rationale
plus a pointer here; the chains below are the lifted text, unedited.

**Nothing binding moved.** Only narrative provenance is here. Every binding
bullet, invariant, and table stayed in its rule — per the chore's own
anti-pattern guard, *"lighter ceremony is not a tradeoff axis."*

## `governance-core.md`

Lifted at version `0.8.0` (rule now at `0.8.1`).

> **Rule version:** `0.8.0` — adds the instruction-source boundary to
> § Non-negotiable rules. gzkit's canon carried NO prompt-injection or
> untrusted-content doctrine at any surface: the only such rule in force came
> from the Claude Code harness, so adopters on the `.agents/`/`.github/`
> mirrors ran governed agents with no boundary at all. Doctrine at
> `docs/governance/untrusted-content.md` (Claude Opus 5 System Card § 5.2).
> Prior `0.7.0` — extended § Operator-doc verb resolution to bind
> `docs/user/manpages/<verb>.md` filename references, not only `gz <verb>`
> strings (GHI #532). 174 references to a non-existent `gz-<verb>.md` manpage
> convention had accumulated across 60 briefs/skills/docs with no gate catching
> them; `audit_manpage_alignment` (under the same `--cli-alignment` flag) now
> fail-closes on the `gz-` prefix, terminal briefs exempt. Prior `0.6.0` —
> repointed § Required workflow order step 5 off
> `gz gates`, which announces its own deprecation at runtime, onto <!-- deprecated-verb-ok: version history records the repoint, does not prescribe it -->
> `gz closeout --dry-run` (GHI #705). The rule prescribed a retired verb on the
> only rule scoped `paths: "**/*"` — loaded on every edit in every session — so
> an agent following it literally was routed onto a deprecated surface with no
> signal that the correct move was a different verb. The inverse of
> `tool-skill-runbook-alignment.md` Invariant 2 is now mechanical:
> `gz validate --deprecated-verb-prescription` fails closed on any governed
> surface that prescribes a deprecated verb. (Entries `0.5.0`–`0.3.0`
> condensed 2026-08-02 to seat `0.8.0` under the surface-weight ceiling; full
> text in git history.) Prior `0.5.0` — reconciled two bullets that
> contradicted AGENTS.md (Pass A rows 14/16): the defect-tracking bullet named
> the exact `gh issue create` and raw-jsonl invocations Always #13/#11 forbid,
> and the Gate-5 bullet carried a lane conditional collapsed at ADR-0.0.36.
> Prior `0.4.0` — withdraw-vs-repudiate disambiguation (ADR-0.0.71): repudiate
> reverses a completion, withdraw is permanent retirement. Prior `0.3.0` —
> enshrined the canon-owner human-attestation directive.


### Lifted 2026-08-29 at version `0.13.0` (rule now at `0.14.0`)

Second diet pass under GHI #921, operator ruling *"we are compressing everything and anything that the agent can consume"*. The `0.9.0`–`0.13.0` chain below is the lifted text, unedited. Bullet narrative from the same pass lives in [Governance Core — Rationale](governance-core-rationale.md).

Prior `0.12.0` — the MD-values bullet's remaining carve-out is **measured rather than assumed** (operator ruling 2026-08-16). It had named the advisory scorecard's classification cells as an open defect awaiting the same treatment the campaign pointer got; measurement said otherwise, and the bullet now records the result instead of the assumption. That instance has ONE parser rather than two, written defensively against failures it already survived (rows 22/27/52 carry `\|` inside code spans, which a naive split once dropped — *"a three-row undercount that looks exactly like a correct answer"*), its Summary roll-up already fenced against its own rows, and **zero silent dropouts across 118 rows**. Migrating it would separate each verdict from its justifying rationale and leave JSON + prose + a fence where one parser suffices. The residual — a malformed Score cell leaving a row invisible to every count, which `_summary_drift_errors` cannot catch because correcting the Summary moves both numbers together — is closed by `_silent_dropout_errors` in the same validator as its siblings. The operative lesson is the asymmetry: *unavoidable* is a claim requiring evidence, and the two instances measured differently. Prior `0.11.0` — the campaign-`Status:` carve-out is **discharged, not merely restated** (operator ruling 2026-08-16, *"move ACTIVE out of prose into JSON"*). The bullet had named campaign `Status:` as a place where prose *"is unavoidably the state"* — and unavoidable was wrong: `data/active_campaign.json` now declares which plan governs, `scripts/session_orientation.py` and `gzkit.knowledge.generate` both read it, and the `^Status:\s*\*\*ACTIVE` regex is gone from production. It had been maintained in two copies on opposite sides of the wheel boundary, over text one character from ambiguity — every superseded edition reads `**SUPERSEDED — was ACTIVE**` and missed only because ACTIVE is not adjacent to the asterisks, so `**ACTIVE (superseded)**` would have silently flipped the governing plan of the whole repository. The banner survives as a restatement, held in agreement by `tests/governance/test_active_campaign_registry.py`, which also fails closed on an edition the registry does not declare — the property neither prior shape had, since a hardcoded pointer and a prose scan both fail silently. Scorecard classification cells remain the open instance. Prior `0.10.0` — adds § Non-negotiable rules bullet: **a value in a Markdown doc is illustrative, never authoritative** (operator ruling 2026-08-16, verbatim: *"we should never allow a hard-coded value in an md doc to be anything other than illustrated lest some rg/grep finds it and gets confused"*). Grounded in a measured instance, not a principle: `.gzkit/rules/pythonic.md` carries `Modules <=600` while the execution authority is `.gzkit/rules/complexity-thresholds.json`, read by `chores/module-sloc-cap-radon/check_module_size.py:56` — whose own docstring calls the 600 *"the drift"*. A 2026-08-16 census against the prose number counted **51** oversized modules that **no gate rejects**, and an agent proposed a census box against an authority the codebase does not enforce. The failure is `rg`-shaped: a number in prose is indistinguishable from a number that binds, so the next reader adopts whichever they find first. Prior `0.9.0` — scopes the instruction-source boundary to **externally-authored** content and carves out operator-authored repo canon. As written in `0.8.0` the bullet was unscoped, and it sat in a **Non-negotiable** section of the only rule scoped `paths: "**/*"` — loaded on every edit in every session — where it contradicted two operator-verbatim canon bullets: `AGENTS.md:342` (*"GHIs are AUTHORIZED for direct repair, always … the GHI is the work order and the receipt"*) and `AGENTS.md:338` (the campaign plan *"rules every session"*). A GHI body is tool output; a campaign plan is file content. One rule mandated autonomous execution, the other suspension, for the two most common session decisions in the repo, and neither side had a mechanical arm (`docs/governance/untrusted-content.md` § Relationship to the hook layer: *"A mechanical incoming-data probe … remains unbuilt"*). Surfaced as blocking rows R18/R19 of the 2026-08-09 `control-surface-rule-conflicts` Pass A walk, whose own session was the worked example — it acted on GHI bodies, a `CHORE.md` workflow, and a checker's remediation instruction without an operator ruling on any. The threat model is external content, not canon the operator authors; scoping preserves every bit of the defense while restoring the direct-repair path. Prior `0.8.1` — adds the instruction-source boundary to § Non-negotiable rules (`0.8.0`); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#governance-coremd).

## `cli.md`

Lifted at version `0.5.0` (rule now at `0.5.1`).

> **Rule version:** `0.5.0` — § Adding CLI Features — New Subcommand now enumerates all seven mechanically-checked obligations, read out of the validators rather than transcribed from memory. The prior list named four surfaces and omitted three that fail closed: the `config/doc-coverage.json` manifest entry, the handler docstring, and the wielding skill. Measured 2026-08-22 on the `gz handoff rulings` registration — the first full suite run returned **21 failures, every one a deterministic consequence of adding ONE verb**, against a 136s unit tier invoked three times. None was a surprise to the gates; all three were a surprise to the checklist. The gap is not enforcement — every obligation here already fails closed — it is that the pre-flight list disagreed with the post-flight check, so the cheapest surfaces in the repo were discovered by its slowest gate. Scoped deliberately to **per-verb** obligations: § New Subcommand's closing paragraph names what a fixed list structurally cannot catch, so this is not read as a completeness claim. Prior `0.4.0` — GHI #810: links the canonical specification, and adds § Command shape so this file can be scored for real. This rule declared clig.dev as its baseline while the 1,037-line specification elaborating it — `docs/design/cli-standards-v3.md`, named canonical by ADR-0.0.4 (Validated, foundation, heavy) — was cited by that ADR and by **no rule or governance surface**, so the per-turn contract never reached it. Meanwhile this file sat in `data/advisory_scorecard_grandfather.json` pinned at `0.3.1` — pre-ledger debt, never scored. The two facts compound: measured 2026-08-16, every CLI rule with a mechanical arm holds at or near 100% (exit codes, epilogs, manpage coverage, skill alignment) and every rule that is prose only sits at or near 0% (`--json` 73/136, formatter chokepoint 1,230 bypasses, structlog 1 `get_logger`, `--log-file` absent). This edit drops the pin by construction, which per `docs/governance/advisory-rules-audit.md` compels the scoring pass. Prior `0.3.1` — reconciled § Core Principles — Consistency to the mechanism it names, so the audit checks usage-line agreement (`0.3.0`, GHI #693); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#climd).


> **Rule version:** `0.3.0` — reconciled § Core Principles — Consistency to the
> mechanism it names (GHI #693, operator ruling 2026-07-17: this is a
> *correction*, not an enhancement — the rule's promise WAS the audit's declared
> intent). "The audit is the mechanical check" read as a promise that the
> documented flag contract is verified; the audit mechanized *presence* only, so
> a manpage could contradict its parser and ship green — observed live on
> `gz handoff authorize --session-id`, which documented a required flag as
> optional under a fully green `gz check`. The audit now checks usage-line
> agreement (required-ness, value-taking) and the rule says so. The § Adding CLI
> Features caveat also claimed the audit "audits verbs, not flags", which stopped
> being true at GHI #350; scoped it to the lane claim it was actually making.
> Prior `0.2.0` — resolved a self-contradiction and a release-notes
> conflict (Pass A conflict-matrix rows 17 and 25, run 2026-07-16); adds the
> body-level version marker this file never carried. § Adding CLI Features
> declared "New Flag (Additive = Lite Lane)" while § Heavy Lane Trigger, 65
> lines above, named *flags* explicitly as Heavy — and `AGENTS.md` § Lane
> Rules agrees with the latter. Step 5 prescribed hand-authoring release
> notes, the one artifact `changelog-release-notes.md` forbids hand-editing.
> Prior: unversioned since authoring.

## `gate5-runbook-code-covenant.md`

Lifted at version `0.3.0` (rule now at `0.3.1`).

> **Rule version:** `0.3.0` — Movement C family closure, rules arm: the placeholder-output-examples prohibition now states its advisory posture in its own text, with the measurement behind it. Scored **Promotable** on a proposed regex scan; the probe that would have justified building it found zero placeholder tokens in scope and eight legitimate elision lines that a scan would have demanded be edited. Re-scored `Judgment` at `docs/governance/advisory-rules-audit.md` row 49; re-scoring without this text edit would have been laundering (operator ruling 2026-08-08). Prior `0.2.1` — reconciled to ADR-0.0.24/ADR-0.0.36 — attestation is universal and the validation bundle must cite ARB-wrapped invocations (`0.2.0`); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#gate5-runbook-code-covenantmd). Binding rules unchanged.


> **Rule version:** `0.2.0` — reconciled to ADR-0.0.24 and ADR-0.0.36 (Pass A
> conflict-matrix rows 15 and 19, run 2026-07-16). § Do Not scoped attestation
> to "heavy/foundation scope", describing lane branching collapsed at
> ADR-0.0.36 — an agent on a Lite+feature OBPI read it as permission to
> self-close. § Validation bundle prescribed bare commands that emit no ARB
> receipt, making the sequence mechanically unrunnable on the foundation ADRs
> this rule governs (`gz adr emit-receipt` exits 3 on zero receipt citations).
> The same drift was caught and fixed on the skill side at
> `gz-adr-closeout-ceremony/SKILL.md:317`; the rule side was never reconciled.
> Prior `0.1.0` — initial shape conformance pass; renamed prohibited heading
> (OBPI-0.0.54-04).

## `chores.md`

Lifted at version `0.3.2` (rule now at `0.3.3`).

> **Rule version:** `0.3.2` — marks this version-history line `deprecated-verb-ok`, matching the precedent already set at [Rule Version History](../../docs/governance/rule-version-history.md#choresmd). `0.3.1` repointed § Correct Evidence off `gz gates`, and recording *which* verb it repointed away from made this line the file's only remaining `gz gates` occurrence — so `gz validate --deprecated-verb-prescription`, the checker shipped alongside that repoint under GHI #705, failed the file for describing the fix it shipped. The escape marker exists for exactly this: a line that documents a deprecation rather than prescribing one. Nothing caught it for the same reason `--audits` sat broken — the scope is not in `gz check`. Binding rules unchanged. Prior `0.3.1` — repointed § Correct Evidence onto `gz check` (`0.3.0`, GHI #705); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#choresmd). <!-- deprecated-verb-ok: version history records the repoint, does not prescribe it -->


> **Rule version:** `0.3.0` — § Correct Evidence prescribed `gz gates`, which <!-- deprecated-verb-ok: version history records the repoint, does not prescribe it -->
> announces its own deprecation at runtime; repointed to `gz check` (GHI #705).
> Evidence commands are the one place a retired verb is most costly — the
> operator runs them to *produce* attestation evidence. Enforced going forward
> by `gz validate --deprecated-verb-prescription`. Prior `0.2.0` — bumped under
> OBPI-0.0.21-06 to capture the
> two-surface layout, project-first → package-fallback resolution, and the
> `--explain` / `doctor` / `--chores-layout` surfaces. Prior unversioned
> content treated as `0.1.0`.

## `adr-audit.md`

Lifted at version `0.2.0` (rule now at `0.2.1`).

> **Rule version:** `0.2.0` — reconciled to ADR-0.0.24 and ADR-0.0.59 (Pass A
> conflict-matrix rows 18 and 19, run 2026-07-16); adds the body-level version
> marker this file never carried, which is how both drifts survived unnoticed.
> § Audit sequence step 2 prescribed bare commands that emit no ARB receipt,
> making step 4 fail closed at exit 3 on every foundation ADR this rule
> governs. § Rules offered only two diagnosis branches, the first of which
> (`author a @covers test`) is the anti-pattern `tests.md` § REQ Scope
> Discipline names for SUPPORT and STRUCTURAL-FENCE REQs. Prior: unversioned
> since authoring.

### Lifted 2026-08-30 at version `0.2.1` (rule now at `0.3.0`)

> **Rule version:** `0.2.1` — reconciled to ADR-0.0.24/ADR-0.0.59 — ARB-wrapped audit commands and per-REQ-kind diagnosis branches (`0.2.0`); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#adr-auditmd). Binding rules unchanged.

## `gh-cli.md`

Lifted at version `0.3.0` (rule now at `0.3.1`).

> **Rule version:** `0.3.0` — reconciled to AGENTS.md § Always #13 (Pass A
> conflict-matrix row 13, run 2026-07-16). § Allowed commands listed
> `gh issue create --label defect` as its first entry, under an allowlist
> heading, in the rule an agent greps for on any `gh` question — affirmatively
> sanctioning the invocation Always #13 forbids, and shipping that instruction
> in the wheel. The `0.2.0` diet pass predates the `/ghi-author` mandate and
> never reconciled to it. The invocation is retained (annotated) rather than
> deleted: it is load-bearing inside `/ghi-author`. Prior `0.2.0` — diet pass
> under GHI #327; compressed cross-repo filing section.

### Lifted 2026-08-30 at version `0.3.1` (rule now at `0.4.0`)

> **Rule version:** `0.3.1` — reconciled § Allowed commands to AGENTS.md § Always #13, annotating the `/ghi-author`-only invocation (`0.3.0`); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#gh-climd). Binding rules unchanged.

## `task-discovery.md`

<!-- lifted-from: .claude/rules/task-discovery.md#task-discoverymd -->

Lifted at version `0.7.1` (rule now at `0.9.0`).

> **Rule version:** `0.9.0` — GHI #820 (reopened): § Layer-drift fail-close now states
> explicitly that drift is CONTRADICTION and never shortfall, and binds consumers to the
> single `_crossing_channels` predicate. #820 corrected the validator on 2026-08-18 but the
> carve-out was recorded only in that function's docstring, so `gz task envelope diagnose`
> kept computing `len({frozenset(s) for s in populated}) > 1` — the overturned
> any-inequality-is-drift reading — for 19 more days. The coupling is not incidental: the
> validator's own failure text sends the operator to the disagreeing view, and the
> diagnostic was the STRICTER side, so it reported drift where the gate reported none and
> invited the falsified attribution #820 exists to prevent. Measured at repair
> (`OBPI-0.35.0-04`): ch3 a strict subset of ch2, ch2 == ch4, validator crossing `[]`,
> diagnostic `drift: True`.

> **Rule version:** `0.8.0` — operator ruling 2026-09-01 (verbatim *"never"*) CLOSED the
> commit-trailer set to `Task:`, `Ceremony:`, and `Eval-feedback-source:`, and corrected the
> auto-stamp's suppression clause. **Why the question kept recurring:** it had been argued
> across five sessions from a 30-day average that straddles a step change, so each session
> sampled a different slice and reached a different answer — the last framing was "the repo
> is 21% consistent (149 of 705)". Measured per-day at the ruling, it is not a consistency
> rate at all: `Claude-Session:` appears in **0 of 26** commits on 2026-08-19, first appears
> 2026-08-20 (`3ac1c7d0`), reaches **7 of 7** on 2026-08-30, and is **0 of 19** across
> 2026-08-31 and 2026-09-01. That is an 11-day window tracking a per-session agent-harness
> reminder, not repo doctrine — `Claude-Session` occurs nowhere in `src/`, `data/`, `docs/`,
> or `.gzkit/rules/`, and is validated and read by nothing. **The "always" option was
> costed and rejected:** 196 of 700 commits in the window are `gz git-sync` ceremony commits
> whose trailers come from the fixed `_SYNC_COMMIT_TRAILERS` constant
> (`src/gzkit/commands/sync.py`), so adopting it would require changing that producer *plus*
> a new validator arm, or it re-drifts the instant the harness setting flips — which the
> window proves it does. Against that, the trailer's only asset is a session URL that
> resolves for one account and ships dead to wheel adopters. The counter-argument was
> recorded rather than suppressed: session forensics is genuinely valuable here, and Layer-2
> session provenance is only ~17% populated (87 of 500 recent ledger rows carry
> `session_id`), so the redundancy case is not airtight — the ruling rests on the harness
> provenance and the producer cost, not on redundancy. **Suppression correction:** the rule
> had claimed since `0.5.0` that "an authored trailer of ANY form suppresses" the
> `prepare-commit-msg-task-trailers` stamp. False — the hook returns early only when
> `has_task_trailer()` is true, and that matches `Task:` specifically. Verified against
> `gzkit.tasks.has_task_trailer`: a `Claude-Session:`-only message returns `False` (stamp
> still fires); `Task:` in either order returns `True`.

> **Rule version:** `0.7.1` — diet pass under GHI #921 (operator ruling 2026-08-30, *"do 1 and 2"*): the superseded `0.7.0`–`0.5.1` version chain is lifted here, restoring the one-sentence shape `skill-surface-sync.md` § Non-negotiable rules #2 requires. Binding rules unchanged; scoped `src/gzkit/**`, this rule loads on every source edit, so narrative is the most expensive thing it can carry.

> **Rule version:** `0.7.0` — GHI #753: `tasks:` schema enforcement is LIVE, and the deferral that promised it is retired. From `0.2.0` this rule declared the check "deferred to OBPI-0.0.64-04" in three places (the channel table, § Convention: Frontmatter `tasks:`, and the `BriefStructure.tasks` field docstring). That OBPI's seven REQs never scoped it — they cover signatures (a)/(b)/(c), `req_atomic`, `gz task envelope diagnose`, the `gz check` join, and a structural fence — so it reached `attested_completed` correctly on its own scope while the deferral became permanent, because nothing couples "X is deferred to Y" to "Y's REQ set contains X". Both arms now ship: `BriefStructure._validate_tasks` on the model path and signature (e) on the corpus path, each delegating to `TaskId.parse` rather than restating the grammar. Latent until #752 made the channel producer-populated; corpus-safe because zero briefs carried a `tasks:` entry at landing. Prior `0.6.0` — GHI #752: the `tasks:` channel is now PRODUCER-STAMPED by `gz task start`, and `@advances` is DEMOTED to advisory. Two of the four channels produced zero keys repo-wide, so Signature (c) compared 7 of 534 OBPIs. The two were not symmetric: `task_start` already resolves the OBPI id when it mints the TASK, so `tasks:` is runtime-known and was merely being asked of an author (the convention that decayed to ~15% on the trailer channel and to 0% here); `@advances` names the function an author judges materially advances a TASK, which no runtime can determine. Narrowing the envelope to `ledger` x `commit_trailer` was rejected — since `0.5.0` the trailer is stamped *from* the ledger, so those two are partly one source and their agreement is partly tautological. A brief-authored `tasks:` restores an independent witness. Prior `0.5.2` — repointed the unruled witness question from GHI #731 (closed) to #752. Prior `0.5.1` — commit-trailer channel is producer-stamped (`0.5.0`, GHI #731); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#task-discoverymd).


> **Rule version:** `0.5.0` — commit-trailer channel is now PRODUCER-STAMPED
> (GHI #731; ~15% authored adherence left Signature (c) skipping 96 of 102
> OBPIs). See § Convention: Commit trailer. Prior `0.4.0` — reconciled to `tests.md`:
> the channels are cumulative-with-a-floor (an `@advances` decorator never
> discharges the `Task:` obligation, GHI #552), and the slug form's `-#<ghi>`
> anchor is optional (operator moratorium 2026-06-01). Prior `0.3.0` — ADR-0.0.64
> closeout reconciliation.

## `pythonic.md`

Lifted at version `0.5.0` (rule now at `0.5.1`).

> **Rule version:** `0.5.0` — § Type-check suppression syntax gains the two forms ty actually honors that this rule had never listed: `# type: ignore[ty:<code>]` and the interop `# type: ignore[<foreign-code>, ty:<ty-code>]`. The omission was not cosmetic — the rule's own enforcement regex matched *any* bracketed `type: ignore[`, so `gz validate --type-ignores` flagged two **working** suppressions as violations, and a reader following the two-row table would delete a live suppression to satisfy the gate. The prohibition is unchanged and now stated at its real cause: ty skips codes lacking a `ty:` prefix, so an all-foreign directive suppresses nothing — which is *also* why a shared comment works, making deletion the wrong fix whenever another checker reads the line. Verified against ty 0.0.69 rather than inferred from this file (`# type: ignore[misc]` left an `invalid-assignment` error standing; both `ty:`-bearing forms suppressed it). Scope widened with the corrected predicate: `src` alone had let 512 inert markers accumulate across `tests` and `features`. Prior `0.4.0` — § Imports records the PLC0415 posture as **accepted** rather than deferred (operator ruling 2026-08-08, "record deferred postures as accepted"). "Deferred" named a queue nothing was advancing, and the clause had been carried as an open loop across five handoffs on that word alone; the honest state is a measured, disclosed advisory whose reclassifying evidence is now named. Re-measured at the acceptance: still 138 sites. No binding rule changed. Prior `0.3.0` — Movement C family closure, rules arm. Scoring this rule's clauses for real found **four advisory-scorecard rows asserting enforcement that did not exist**, which is a worse state than the Promotable rows the campaign box counts: a Promotable row honestly says "no witness yet", while a false **Mechanical** row reports green while blind and is invisible to the criterion. Row 18 claimed "ruff BLE001 enforces" with `BLE` absent from `[tool.ruff.lint] select` (6 live violations, one behind a `# noqa: BLE0001` typo that suppressed nothing); row 23 claimed PLC0415 was "partially enforced" with `PL` equally absent (138 live violations); rows 19 and 20 claimed line-count enforcement that § Size Limits has said was unbacked since `0.2.0`. `BLE001` is now enabled and the six sites fixed with cited justifications (operator ruling 2026-08-08); PLC0415 is deferred because its 138 sites need per-site readings against this rule's own optional-dependency and cycle-avoidance carve-outs. Rows 19/20/23 re-scored `Judgment` with the measurements recorded here. Prior `0.2.1` — names the unreconciled three-way threshold conflict in § Size Limits & Refactoring (`0.2.0`); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#pythonicmd).


> **Rule version:** `0.2.0` — names the unreconciled three-way threshold conflict
> in § Size Limits & Refactoring (Pass A conflict-matrix row 11, run 2026-07-16);
> adds the body-level version marker this file never carried, which is how a
> competing threshold authority survived `complexity-thresholds.md` § Invariant's
> explicit prohibition on exactly that. No number changed — resolution needs a
> class-size corpus band that does not exist yet, and is routed for operator
> decision rather than guessed. Prior: unversioned since authoring.

## `hexagonal-architecture.md`

Lifted at version `0.2.0` (rule now at `0.2.1`).

> **Rule version:** `0.2.0` — seats HA inside the DDD → HA → BDD → TDD spine and
> adds the binding cohesion doctrine (domain modeled as the ontology, not a folder
> tree; `core/` stays; subsumption over parallel models; "why is this here?" is a
> required answer). `0.1.0` enshrined Cockburn Ports & Adapters as the primary
> code-architecture directive (deps behind adapters, stdlib + Pydantic core,
> parameterize every external dependency).

### Lifted 2026-08-30 at version `0.2.1` (rule now at `0.3.0`)

> **Rule version:** `0.2.1` — seats HA inside the DDD → HA → BDD → TDD spine and adds the binding cohesion doctrine (`0.2.0`); prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#hexagonal-architecturemd). Binding rules unchanged.

## `agent-failure-modes.md`

Lifted at version `0.6.0` (rule now at `0.6.1`, re-sourced to current-card-only
citations under the 2026-08-02 operator ruling against retaining superseded-model
references in live rules). Origin provenance for the pattern set, preserved
verbatim:

> Patterns 1–6 from the Opus 4.7 System Card (§ 2.3.6) and GPT-5.5 System Card
> (§ 9.2); patterns 7–8 from the Claude Opus 5 System Card (§§ 6.4.4, 6.6.1);
> pattern 9 from the GPT-5.6 System Card (§§ 7.4, 9.1.3.6, 9.2.2, 2026-07-09),
> whose §§ 7.1–7.2 also corroborate patterns 2, 3, 7, 8 from a second vendor's
> internal agentic-coding traffic.

> **Rule version:** `0.6.0` — extended 8 → 9 patterns (operator ruling
> 2026-08-02; GHI #750 lineage; ADR-0.0.23 § Consequences pre-authorizes
> extension). Adds **Metagaming / gaming the gate** from the GPT-5.6 System
> Card: § 7.4 defines metagaming as reasoning "about how it will be graded,
> rewarded, or monitored"; § 9.1.3.6 records METR discarding a capability
> measurement over the detected cheating rate; § 9.2.2 records UK AISI
> observing anticipation of monitors and user-facing summaries that omit what
> the reasoning admits. Prior `0.5.1` — citation refresh (GHI #750): GPT-5.6
> §§ 7.1–7.2 supplies second-vendor observations for patterns 2, 3, 7, 8.
> Prior `0.5.0` — re-sourced to the Claude Opus 5 System Card (2026-07-24) and
> extended 6 → 8 patterns. Adds **Hallucinated authorization** (Opus 5 § 6.6.1
> measured the model internally representing "user consent that was never
> given" before a destructive action) and **Security shortcut for expedience**
> (§ 6.4.4, one of two dimensions Anthropic newly introduced). The ADR that
> authored this rule pre-authorized the revision: ADR-0.0.23 § Consequences —
> *"treating the rule as living: future system cards may rename or extend
> patterns."* Prior `0.4.0` — repointed the Safeguard-circumvention and
> Fabrication backstops off the removed TTY `ATTEST` authenticity gate onto
> AGENTS.md § Never #1 (operator-verbatim attestation + audit), per the
> canon-owner attestation declaration.

### Lifted 2026-08-30 at version `0.6.2` (rule now at `0.7.0`)

> **Rule version:** `0.6.2` — Fable/Mythos 5 card consumed (GHI #751): patterns 1–6 now carry direct current-generation observations — the card's own § 2.3.3 failure tags use this taxonomy's vocabulary (`Safeguard circumvention` / `Fabrication` / `Skipped cheap verification` / `Reckless action` / `Correction fails`) with real-usage cluster frequencies — and pattern 9 gains Anthropic-side corroboration (§§ 6.1.2, 6.4.1.2: grader-satisfying reasoning, almost never verbalized). Prior `0.6.1` — re-sourced to current-card-only citations; origin lineage lifted to [Rule Version History](../../docs/governance/rule-version-history.md#agent-failure-modesmd). Patterns and backstops unchanged since `0.6.0` (nine patterns).

## `agents-md-map-doctrine.md`

### 0.11.0 — 2026-09-05

**Withdraws `0.10.0` entirely. Its finding was false and the commit it justified was a regression.**

`0.10.0` asserted that gzkit has *no route to deliver* `project_doc_max_bytes`, inferring it from `codex doctor` naming a single config source, `$CODEX_HOME/config.toml`. Doctor does not enumerate the project-local overlay, so its silence was read as absence — the failure `AGENTS.md` names verbatim: *"A search is not a read — never report that something is absent, undocumented, or unruled on the strength of keyword queries."*

Codex loads a project's `.codex/config.toml` in any directory the operator has trusted, and that file wins over the global one. Its own trust prompt states the mechanism: *"Trusting the directory allows project-local config, hooks, and exec policies to load."* Measured 2026-09-05 via `codex debug prompt-input`, holding trust constant and varying only the repo-local value: `32768` → 32768 B delivered, `65536` → 46876 B (the whole surface), `12000` → 12000 B.

The cost of the false finding: `344f7189` (GHI #815) had set the cap to `65536` and it was working. `e43c55c9` lowered it to Codex's `32768` default on `0.10.0`'s reasoning, re-introducing the truncation #815 had fixed, and `b90d0484` propagated the claim into three more live surfaces. For roughly a day the tail of `AGENTS.md` — 14108 B, the IRON LAW included — reached no Codex session.

The structural lesson, and why this is more than a value correction: every check on this surface compared one authored number to another. `CodexDocCapCoherenceTest` pinned the generated config to the manifest; the surface-delivery witness measured rendered bytes against the manifest's declared cap. All of them stayed green while delivery was capped 14108 B short, because none of them ever asked the vendor. `gz validate --instructions-files-budget` now carries a codex-delivery witness (`src/gzkit/governance/trust_audits/codex_delivery_witness.py`) that reads what Codex actually assembled, reports *unobserved* rather than passing when it cannot run, and is advisory on the standing 2026-07-06 ruling that an adapter limit must not gate the core.

### 0.10.0 — 2026-09-05 (WITHDRAWN by 0.11.0 — recorded as authored; its finding does not hold)

§ Budget's transitional-window paragraph asserted that `project_doc_max_bytes` is *"a Codex **setting** gzkit writes into the `.codex/config.toml` it generates"*. Measured 2026-09-04 under GHI #962: Codex reads `$CODEX_HOME/config.toml` and never the project-local file gzkit generates, so gzkit has never written that setting anywhere Codex looks. Both remedies are closed — writing to `~/.codex/` is an adopter's global surface the operator ruled out 2026-09-04 (*"such locations are global to an adopter's project, i think the right answer is no"*), and repointing `CODEX_HOME` moves `auth.json` with it, leaving the tier-1 adversary unauthenticated. The paragraph now records the cap as Codex's own default, in force and unraisable from here.

This is the doctrine arm of `e43c55c9`, which corrected the same false claim in `render_codex_config`'s docstring and `CodexDocCapCoherenceTest` and set both numeric surfaces to `32768`. The claim survived in two further live surfaces — this rule (with its wheel mirror) and `src/gzkit/schemas/vendor_manifest.json`'s `content_type_delivery_caps` description — which is why the witness could still be read as reporting headroom gzkit controlled. Binding budget values unchanged; the correction is to what the cap *is*.

### 0.9.0 — 2026-09-01

Dead-pointer sweep under GHI #533. The § Budget destination pointed at `GHI #533 → ADR-0.35.0 § Decision 3`; #533 closed `superseded` into that ADR the same day, so the rule now cites the ADR directly. This is the second dead-pointer repair on the same sentence — `0.3.0` repointed it off terminal `ADR-0.0.37` under the same GHI (`fcff7b49`, `9c1c1230`). Binding rules unchanged; only the destination pointer moved.

Lifted 2026-08-29 at version `0.7.0` (rule now at `0.8.0`).

> **Rule version:** `0.7.0` — § Attestation granularity's build-step bullet now NAMES the replacement (CORPUS ATTESTATION) instead of only prohibiting the collision, and records the prohibition as discharged rather than pending. `0.6.0` stated the rule as an open defect — *"`gz content commit --help` currently claims the name"* — which is the shape that decays: a rule whose only content is "X is wrong" leaves the next author to invent a replacement, and the locally obvious invention is `rendition attestation`, which re-asserts the inversion the same section exists to record. Operator ruling 2026-08-18 (GHI #822) fixed the noun as `corpus`, on the ground this section already carries: the attestable subject is the corpus, and the rendition is the Layer-3 projection that is *"never the thing attested."* Swept the same day across `content/commit.py`, `content/__init__.py`, `docs/user/manpages/content.md`, `ADR-0.35.0` and seven of its OBPI briefs, and `instructions-files-diet` v3.2.0 — leaving every genuine "cite at Gate 5" reference and every `### Gate 5 (Human)` gate-covenant section untouched. Prior `0.6.0` — adds § Attestation granularity, which the `0.5.0` division of labour needed and did not have. `0.5.0` ruled that the chore is the only phase that trims and that ordinary sessions never resize a render surface — but it said nothing about who authorizes the resulting rendition, so the undifferentiated reading held: *every* recompose routes to Gate 5. `instructions-files-diet` v3.0.0 § 5a encodes that reading verbatim (*"STOP THERE … It stops at the candidate to attest. It never lands canon itself"*), which made the chore structurally unable to finish the job `0.5.0` assigned it. Operator ruling 2026-08-17, verbatim: *"a rerender of unhanged canon doesn't require my attestation. adding to cms entries would. removing items would. trims and compressions to render within budget might invite a review"* (spelling preserved), preceded by *"I only attest to completed obpi/adr work"*. The discriminator is the corpus fingerprint, not the fact of a write. **The current implementation is measurably backwards** and this rule now says so: `gz content remember` and `gz content retire` accept no attestor, while `gz content commit` fail-closes without one — gating the Layer-3 derived view and leaving the Layer-1 canon changes ungated. Prior `0.5.0` — **the `EXIT CONDITION: restore fail-closed at 1.0` is RETIRED, not deferred** (operator ruling 2026-08-17, ratified in design dialogue). `0.4.0` read the stay as a waiting room: budgets advisory *until* a mechanism arrived, then re-armed at 1.0. The mechanism arrived and turned out to be a **cadence, not a gate**, which dissolves the condition rather than satisfying it. Operator verbatim: *"permit exceedances of accumulated render sources, then, let the chore handle overages"*; *"let the chore manage the limits. let normal discovery and operations add to or suggest modifications to sources. then, the chore is what gets render surfaces back into shape. otherwise, we churn"*; *"I can't be stopping to trim them at every turn."* The division of labour is now binding: ordinary sessions **add to sources** and never resize a render surface; `instructions-files-diet` (v3.0.0) is the only phase that trims, and it recommends rather than decides; operator-on-demand is a first-class trigger. **A hard gate has nothing to bite on here, and that is structural rather than a concession.** The per-turn surface is not live-rendered — it is played back verbatim from a Gate-5-attested rendition (`sync_agents_md`, `.gzkit/renditions/AGENTS.md/<consumer>.md` + a `<consumer>.corpus.json` manifest carrying `corpus_fingerprint`, `corpus_entry_count`, `committed_ts`, `attestor`). `gz content remember` appends to the corpus and moves nothing; only `gz content commit` changes the rendered build, under human attestation. So the rendered surface **cannot drift on its own**, and a gate on it can only fire repeatedly about a build the operator already approved — measured 2026-08-17 as exactly that: approved `corpus_entry_count` 59, corpus on disk 59, zero pending drift, and the witness nonetheless reporting the frozen 34354 B build against the codex cap on every `gz check`. That is alarming about the release instead of about unreleased accumulation. **The tracked signal moves accordingly:** drift between the corpus and the last approved build, which is `gz validate --rendition-lineage` (`OBPI-0.35.0-06-validate-rendition-lineage`, Draft) — the campaign's own item #6, so this is a sequencing note, not new scope. Reminder channels are the handoff at session boundaries and one quiet line in `gz check`; the remedy catalogue belongs to the chore. Budget VALUES remain unchanged and every file is still measured. Prior `0.4.0` — the per-file char budgets are **ADVISORY until 1.0** (operator ruling 2026-08-17, verbatim: *"temporary stay of all control surface budget limits until version 1.0. I want to be warned, and we may lift the limits as needed, but no blockers."*). Budget VALUES are unchanged and every file is still measured, with each overrun reported to stderr carrying its distance and the `/gz-context-diet` pointer — the stay suspends the consequence, never the observation, which is what keeps *"we may lift the limits as needed"* a per-file decision rather than a blanket amnesty. **Two** arms were fail-closed, not one: `audit_instructions_files_budget` and `agents_md_map_conformance` criterion (d), the second discoverable only through this rule's § Shape enforcement list. Criteria (a)/(b)/(c) — paragraph shape, prohibited titles, link resolution — are untouched and remain fail-closed; the stay is scoped to budget limits, never to shape. The flip also made the scope internally consistent: its sibling `surface_delivery_witness` has been observe-only on the vendor cap since the 2026-07-06 decoupling, so `gz validate --instructions-files-budget` had been strict about the project's own soft budget while merely warning about the harder cap that can actually TRUNCATE the surface. The `instructions-files-budget` negative control was repointed at the scope's surviving fail-closed property (survival-declaration drift) the same day — a control asserting enforcement that no longer happens is worse than no control. Supersedes the original assertion of `REQ-0.0.54-03-01d` ("must be rejected"); `ADR-0.0.54` is Validated and stays SEALED as the record of what was decided on its date, with the live posture held by the LAST dated entry in `data/instructions_files_budget.json` per that file's own reading convention. EXIT CONDITION: restore fail-closed at 1.0, on the standing 2026-07-28 ground that strictness is earned by the mechanism that discharges it — `ADR-0.35.0` § Decision 3 is where that mechanism lands. Prior `0.3.0` — repointed § Budget's deferral target off `ADR-0.0.37`, which went terminal 2026-07-18 (§ Terminal Disposition, "Split-and-Supersede") with its registry-spine OBPIs permanently withdrawn, onto the live successor `ADR-0.35.0-canon-entry-corpus-landing` § Decision 3 (section ownership + decrease-only ratchet). The dead pointer sat in a rule scoped to `AGENTS.md` / `CLAUDE.md` / `.claude/rules/*.md`, so every agent editing those surfaces was aimed at a destination that can no longer accept work (GHI #533). Also records that the transitional window is no longer slack: the GHI #712 delivered-surface witness is now in the default `gz check` scope and AGENTS.md sits 560 B under the Codex `project_doc_max_bytes` default. Prior `0.2.0` — corrected the § Budget section to read the live `data/instructions_files_budget.json` source of truth instead of duplicating stale enforced numbers, and marked the 15000-char AGENTS.md weight target as deferred to GHI #533 / ADR-0.0.37 (ADR-0.0.54 closed Completed-Partial: shape enforcement delivered; weight-halving deferred). Prior `0.1.0` — authored under OBPI-0.0.54-01; establishes the shape invariant and budget contract. OBPI-0.0.54-02 lifts AGENTS.md sections. OBPI-0.0.54-03 ships `gz validate --agents-md-map-conformance`.

## `cross-platform.md`

Lifted 2026-08-29 at version `0.6.0` (rule now at `0.7.0`).

> **Rule version:** `0.6.0` — added § Delivered path literals (GHI #900), and widened `paths:` to `src/gzkit/**/*.md` so the rule loads where that defect is authored. The platform-co-equality posture below was already contradicted by a path rooted at one machine, but no clause enforced the posture against a literal, so four wheel-shipped files told adopters to open a path that existed on one laptop while `gz validate --distribution` read green -- byte-equivalent delivery of an instruction that cannot resolve. Prior `0.5.0` — added § Subprocess reads (GHI #582): text-mode subprocess captures MUST pass `errors="replace"`, since `encoding="utf-8"` alone still raises `UnicodeDecodeError` (a `ValueError` that `except OSError` misses) on non-UTF-8 tool/git output. Prior `0.4.0` — corrected the platform framing: removed the inaccurate "Windows (primary)" label and the miscited `Doctrine: ADR-0.0.1` reference (ADR-0.0.1 is canonical-govzero-parity; no cross-platform ADR exists). gzkit targets all platforms co-equally (operator directive 2026-06-28). Prior `0.3.0` — diet pass under GHI #327; lifted helper patterns and scope-boundary details to `docs/governance/cross-platform-rationale.md`.

## `guardrail-feedback-prose.md`

Lifted 2026-08-29 at version `0.2.0` (rule now at `0.3.0`).

> **Rule version:** `0.2.0` — Movement C family closure, rules arm: § Mechanical
> promotion path is replaced by § Enforcement posture, which states the advisory
> disposition **in the rule's own text** and names what would reclassify it. The
> section had declared *"This rule is **Promotable**"* while describing, in the
> same paragraph, why the mechanism it promised was deliberately not built — a
> discipline declared with no witness and no statement that none is coming, which
> is the third state the family-closure criterion forbids. Nothing is being
> weakened: the per-surface covering-test channel that actually enforces this bar
> is now named as the enforcement rather than as an interim measure. Re-scored
> `Judgment` at `docs/governance/advisory-rules-audit.md` row 61; re-scoring
> without this text edit would have been laundering (operator ruling 2026-08-08).
> Prior `0.1.0` — initial authoring under ADR-0.0.70 (Buetow
> adoption): the feedback text IS the prompt a human would otherwise have
> typed; engineer it as one.

## `model-selection.md`

Lifted 2026-08-29 at version `0.5.1` (rule now at `0.6.0`).

> **Rule version:** `0.5.1` — discharges the fable-calibration pending note via the card consumption (GHI #751); routing unchanged. Prior `0.5.0` — adds the `fable` tier (operator ruling 2026-08-02: "It seems like we should incorporate fable for the cases and times"): Mythos-class judgment work — doctrine evaluation, design dialogues, adversarial review, system-card evaluation — under operator supervision. Fable is NOT the pipeline or mechanical default; initial effort calibration landed with the card consumption (GHI #751) — see `docs/governance/opus-tuning.md` § Fable (Mythos-class) calibration: start `high` not `max`, expect prompt-steerable overeagerness, and treat cyber-classifier fallback to a prior Opus tier as silent degradation. `skill_model` Literal and router test extended in the same commit. Prior `0.4.0` — adds operative claim 5 (subagent claims are relayed only with independent evidence), closing the relay gap the Claude Opus 5 System Card § 6.1.3 named: *"the model can relay claims from subagents to users without verifying them"*, with multi-agent coverage acknowledged as an unmeasured limitation of that card's whole audit. gzkit dispatches `narrator`/`implementer`/`quality-reviewer`/`spec-reviewer` and relays their output into ceremony evidence, so the gap was live here. Also retires the two-generations-stale model mapping (`opus` → `claude-opus-4-7`) and compresses it to one line. Prior `0.3.0` — renamed prohibited headings; lifted Rationale to expansion doc (OBPI-0.0.54-04 shape conformance pass).

## `mx-mode.md`

Lifted 2026-08-29 at version `1.3.0` (rule now at `1.4.0`).

> **Rule version:** `1.3.0` — adds § Opting a guard into the floor, which names the two opt-in mechanisms and the choice between them. `1.2.0` said only that *"a new guard inherits demotion by default and must opt into the floor explicitly"* and never said HOW — while `checkpoint.resolve` offers two routes that differ in reversibility: NAME (`GATE5_INVARIANTS` membership, a Boundary Invariant #3 one-way door, forbidden for a narrower proxy per § Consequences/Negative #7) and LEVEL (emit CRITICAL, reversible). Measured 2026-08-22 against `_GUARD_META`: four of six pre-commit guards survive an open hangar and they do it BOTH ways — `ledger` and `gate5-attestation` by name, `post-authoring-src-commits` and `enforcement-floor` by level — so the roster could not be read without tracing the resolver. The reasoning existed and was correct; it lived in a commit body. `84519da5` (GHI #852) derived it at fix time and recorded it there, which is the settled-twice-recorded-nowhere shape `governance-core.md` `0.13.0` names: both wrong answers are locally plausible, so re-deriving it is a coin flip rather than a delay. Also records the operator ruling of 2026-08-22 that the Stage-2 production-code fence's pin is permanent (GHI #855), and that an unregistered guard name resolves CRITICAL rather than advisory. Prior `1.2.0` — § Honor the marker now names BOTH enforcement surfaces, and
> `paths:` reaches the second one. The clause said "most guards drop to advisory" without
> qualification while the demotion reached only `gz validate` scopes and the `gz check` step
> layer; the pre-commit guards in `src/gzkit/hooks/guards.py` each self-decided fatality with a
> bare `return 1`, which is verbatim the "named coverage defect" of ADR-0.0.74 BI#2. Measured
> 2026-08-22: **zero** checkpoint consumers anywhere under `src/gzkit/hooks/`, so an open hangar
> had no authority over one of the two surfaces governance is enforced on — while `gz mx --help`
> advertised the hangar so "the operator can repair governance itself" and offered
> `gz mx enter --reason "repair ledger"` as its worked example. Third recurrence of one class:
> GHI #638 (the `gz check` step layer), GHI #651 (the enforcement floor demoting inside the
> hangar), now GHI #843. The root is an inventory gap ADR-0.0.74 Negative #6 predicted in its own
> words — *"a funnel that forgets it silently stays hard"* — because the funnel inventory
> OBPI-0.0.74-02 shipped enumerates `validate_cmd` and nothing else. Closed by GHI #843: one seam
> over one registered inventory in `guards.py`, fenced by
> `tests/test_hooks_guards.py::TestMxCheckpointSeam`, which fails when a `forbid_*` guard is added
> without a checkpoint entry. Prior `1.1.0` — Movement C family closure, rules arm: § Honor the marker now
> names the mechanical witness it has had since OBPI-0.0.74-17/-20. The scorecard scored this
> clause **Promotable** on the premise that "the marker-check is structural (file exists/not)"
> and liveness was advisory — a description of the rule's state *before* `checkpoint.resolve`,
> `disposition`, and 45 covering tests across five modules landed. Nothing was built to close
> this row; the score had simply not been revisited when its own mechanism arrived, which is
> how a Promotable row outlives the reason it was Promotable. Re-scored **Mechanical** at
> `docs/governance/advisory-rules-audit.md` row 62. Prior `1.0.1` — marker path aligned to
> `.gzkit/mx.json`; `e2d38c3c0` bumped the
> HTML marker only (GHI #650). Prior `1.0.0` — initial authoring under ADR-0.0.74 (OBPI-0.0.74-08).

## `security-sensitivity.md`

Lifted 2026-08-29 at version `0.5.1` (rule now at `0.6.0`).

> **Rule version:** `0.5.1` — aligned the MX-marker path in § 3 to code truth: the hangar marker file is `.gzkit/mx.json` (`src/gzkit/mx/marker.py:29`), not `.gzkit/mx-active` (GHI #650). Prior `0.5.0` — named two unenforced surfaces the rule had been asserting as binding (Pass A conflict-matrix rows 22 and 23, run 2026-07-16). The auto-detect floor's "escape is fail-closed" language silently does not hold inside the MX hangar — `sensitivity` is not in `GATE5_INVARIANTS`, so the scope resolves ADVISORY and its exit-3 errors are dropped; the demotion is deliberate (a fail-closed sensitivity scope would lock the hangar against the briefs an operator enters it to repair — GHI #682) but was unannounced. The § Registry contract's self-bootstrapping clause presupposes an editing brief, which the operator-canon direct-fix path never has, leaving the floor unenforced on the path canon mandates. Both are now stated rather than implied. Prior `0.4.0` — GHI #625: the auto-detect floor now fails closed (`sensitivity-floor-violation`, exit 3) on an *omitted* declaration over a registered overlap, not only on a *wrong* one; pre-cutover briefs are grandfathered via `data/sensitivity_floor_grandfather.json`. Prior `0.3.2` — renamed prohibited `## Anti-patterns` heading → `## Do Not` (OBPI-0.0.54-04 shape conformance pass).

## `skill-surface-sync.md`

Lifted 2026-08-29 at version `0.11.0` (rule now at `0.12.0`).

> **Rule version:** `0.11.0` — GHI #728: adds the chores-only `project_local` content class and the declaration protocol. `.gzkit/chores/AGENTS.md` declared project-local-only slugs as a real category (REQ-0.0.21-09-06) but nothing implemented it, so a chore authored only under `.gzkit/chores/` was copied into the wheel by sync and scaffolded into every adopter by `gz init`. The property is now DECLARED in `registry.json` rather than inferred from absence — the inference `gz chores doctor` used is the exact state sync overwrites. Prior `0.10.1` — diet pass (operator ruling 2026-08-02): lifted bootstrap-semantics narrative, retirement-policy rationale, and the class-classifier reference tables to `docs/governance/skill-surface-sync-rationale.md`; every non-negotiable rule and binding core retained verbatim. Prior `0.10.0` — names `metadata.skill-version` as the canonical spelling and records that presence is now enforced. Rule #2 said only "`skill-version:` in YAML frontmatter (validated by the skill schema)", which was true of neither half: no skill schema exists, the audit checked *format when present* and never presence, and the unstated nesting let two spellings coexist — 57 skills nested under `metadata:`, 11 at top level, where both validators were blind to them. The rule's own conflict-resolution procedure names the version as "the primary signal", so the drift disarmed the procedure the same rule prescribes. Prior `0.9.0` — renamed prohibited headings; lifted Rationale to expansion doc (OBPI-0.0.54-04 shape conformance pass).

## `tests.md`

Lifted 2026-08-29 at version `0.18.0` (rule now at `0.19.0`).

> **Rule version:** `0.18.0` — GHI #856: refreshes § Full unit tier's measured figures and scopes the parallelism sentence to the budget it governs. The old figures (268.1s / 7497 tests serial, 71.4s across 32 processes) dated from `0.13.0` and were **two generations stale on both halves** — re-measured 2026-08-27 at `2c81cb7d` on a 10-core host: 144.23s serial and 41.34s parallel over 8,912 tests. Worse than stale, the sentence *"parallelism does not rescue it"* was routinely read as a general ruling against parallel execution, which it never was: it justifies why the **60s smoke budget** belongs to a subset, and says nothing about attestation. That misreading is now load-bearing in the other direction — `CANONICAL_STEP_COMMANDS["unittest"]` runs `unittest-parallel` as of the same GHI, so a rule read as forbidding parallelism would contradict the canonical "Tests pass" invocation. Figures are restated as a DATED RECORD per `.claude/rules/governance-core.md` § Non-negotiable rules (a value in a Markdown doc is illustrative, never authoritative); the enforced budget stays `uv run gz smoke`. No binding rule changed. Prior `0.17.0` — operator ruling 2026-08-11: settles the repo-wide `[kind]` tag case. Both readers have always been `re.IGNORECASE`, so the split was never a correctness defect — but three documenting surfaces disagreed and one contradicted *itself*: `docs/governance/req-scope-discipline.md` gave lowercase at § The invariant and UPPERCASE at § Tag syntax, so an agent consulting the canonical expansion got both answers from one document and the question recurred per brief. Case-insensitivity is now stated where it binds, UPPERCASE is named as the authored form (597 of 967 tags, the `gz-obpi-specify` authoring skill, and AGENTS.md prose all already use it), and the 370 lowercase tags across 55 briefs are declared correct and explicitly out of scope for rewriting — a ~970-tag sweep for zero mechanical gain is what DO IT RIGHT #11 forbids. No binding rule changed; a question that had no authority now has one. Prior `0.16.0` — GHI #567 Move 2(b): adds the horizontal-slicing prohibition to § Red-Green-Refactor. The section already prescribed the vertical rhythm ("One test → one observed RED → …") but never named the shape that violates it, so the most common real-world deviation — author every test for a brief, then every implementation — had no name in the rule an agent could be held to. Articulates WHY the batch shape fails rather than only that it does: assertions written against an implementation you are about to write record intent rather than REQ semantics, and a RED arriving with ten other REDs is not evidence about any one of them. Framed as § The discriminator applied at authoring time, so the two clauses reinforce rather than restate. Advisory, and no mechanical witness is planned — authoring order leaves no artifact to inspect, and the RED witness that could prove it (`gz arb red`) is per-REQ by construction. Adopted from Matt Pocock's `tdd` skill via the external-catalog alignment scan. Prior `0.15.0` — Movement C family closure, rules arm: § Eval-awareness corollary and § Output-form fixture carve-out now state their advisory posture **in their own text**, and are re-scored `Judgment` at `docs/governance/advisory-rules-audit.md` rows 71 and 69. Both had sat in the forbidden third state — a discipline declared with no mechanical witness and no statement that none is coming — which is the family GHI #537 named. Neither is being demoted for convenience: the corollary's promotion path (a name-shape scan over `tests/**`) was scored tractable for months and never built because nothing has been observed for it to catch, and the carve-out's path ("flip the `gz test-shape` arm closed once the declared-marker backlog drains") would fail-close the whole legacy corpus at once, which is why the arm was left open. Under the scorecard's § Recommended promotion order freeze (2026-06-08, opt-in-with-justification) a backlog draining is not the observed-drift evidence a new fail-closed check requires. Re-scoring without this text edit would have been laundering (operator ruling 2026-08-08). Prior `0.14.0` — GHI #589: § Verification exit-code integrity is now MECHANICAL, not prose. It had been binding since `0.8.0` and enforced by nothing — scored **Promotable, unenforced** at `docs/governance/advisory-rules-audit.md` row 66, and the highest-frequency observed violation class in agent sessions, whose failure mode is a confident false green that then gets relayed as attestation evidence. The `verifier-pipe-gate.py` PreToolUse hook over `Bash` now refuses a verifier in any non-final pipeline stage; `set -o pipefail` and `${PIPESTATUS[0]}` opt out. Scoped by predicate rather than by the clause's named filters: the shell reports the last stage's exit whatever that stage is, so a `tail|head|grep` allowlist would have waved `gz check | cat` through — the enumerate-the-examples miss this codebase has now made three times on the resume gate's own allowlist. Prior `0.13.0` — GHI #724: the 60s ceiling now names the suite it governs, and that suite exists. It bound a "Smoke/BVT" tier — subset language for a subset that was never built — so it was read against the full unit tier and breached 4.5x (268.1s / 7497 tests) with no consumer reading the number. Adds § Smoke tier membership, declares the full tier explicitly unbounded (its runtime ratchets with the REQ set by design, so a constant ceiling over it can only be breached), and points the budget at `uv run gz smoke`, which fails closed on breach AND on an empty tier — an empty subset satisfies any budget trivially. Parallelism is ruled out by measurement, not preference: 71.4s across 32 processes is still over. Prior `0.12.0` — GHI #538: pins the STRUCTURAL-FENCE proof-channel matrix row to the explicit OBPI-combination anchor token `(OBPI-NN[, OBPI-MM, …])`, making the parent-ADR `## Boundary Invariants` binding mechanical rather than heading-presence-only. The row previously said only "Parent-ADR `## Boundary Invariants` entry", which the resolver read as heading presence — a fence REQ passed while no invariant named its OBPI, so the proof could not say *which* invariant proved *which* fence. Syntax detail lives in `docs/governance/req-scope-discipline.md` § STRUCTURAL-FENCE; enforced by `resolve_fence_proof`. Prior `0.11.0` — GHI #571: lifts the *operational discriminator* into the hot-path rule rather than adding more prose. § 6f ("tests assert semantics, not strings") was slogan-shaped: memorable, with no test an agent could apply — the discriminating question lived only in `docs/governance/req-scope-discipline.md`. Adds § Unit-test purpose, § The discriminator (*if behavior changed but text did not, would this test fail?*), § Prefer structured assertion targets, the enumerated no-pytest forms, and the `# output-contract:` marker convention that `gz test-shape` reads. Extends the non-BEHAVIOR `@covers` prohibition to STRUCTURAL-FENCE (it previously named SUPPORT alone). Reconciles § RED evidence with the `arb-red-*` witness schema (GHI #642). Prior `0.10.0` — GHI #647: the SUPPORT proof channel's ledger arm is now path-specific. A bare event of the cited type no longer proves; an event must *cite the path*, or for `artifact_edited` (content authorship, never emitted for source `.py` files) the cited artifact must *exist on disk*. Closes the hollow gate where 4295 unrelated `artifact_edited` events satisfied any SUPPORT proof. 81 pre-cutover REQs snapshotted in `data/support_proof_grandfather.json` (shrink-only, waiver-ratchet-registered); 62 drained by the artifact-existence proof, 19 tolerated as `grandfathered-support`. Prior `0.9.0` — § Behave scenario tagging is now REQ-kind-aware (GHI #636): only BEHAVIOR REQs can require behave, and a BEHAVIOR REQ is satisfied by a scenario tag OR an `@covers` unit test; SUPPORT / STRUCTURAL-FENCE REQs are exempt by proof channel. This drains the deadlock where the gate demanded a `behave_coverage_waivers.json` entry that ADR-0.0.73's shrink-only waiver-ratchet forbids growing. Prior `0.8.0` — added § Verification exit-code integrity (GHI #589): never pipe a verifier through `tail`/`head`/`grep`; the shell reports the filter's exit, not the verifier's — read the ARB receipt `exit_status`. Prior `0.7.0` — producer reconciled to GHI #552: `gz git-sync` now stamps `Task: TASK-gz-git-sync` (previously only `Ceremony:`, which #552 stopped accepting on src/tests scope — leaving every sync commit silently non-compliant), and the direct-fix slug's `-#<ghi>` anchor is now OPTIONAL (operator moratorium on reflexive GHI-filing, 2026-06-01). Prior `0.6.0`: GHI #552 strict-mode — src/tests commits MUST carry `Task:`; `Ceremony:`/`Eval-feedback-source:` no longer substitute. Surfaces TASK as the leaf vertebra of the PRD → Constitution → ADR → OBPI → REQ → TASK → Attestation governance spine (per AGENTS.md § Workflow).

## `token-block-discipline.md`

Lifted 2026-08-29 at version `0.6.0` (rule now at `0.7.0`).

> **Rule version:** `0.6.0` — GHI #764: adds § Binding Sub-Invariant 7 (the exchange record carries an observation report). The record is two things by operator canon — the fact of block vacation AND an observation report of what happened during possession — and only the first half was implemented: the completion writer had three content inlets for seven sections, so four sections emitted boilerplate byte-identical across all 33 records on disk, and those four are the observation report's own subject matter. The implementation summary was also filed under `## Pending Work / Open Loops`, a prospective heading for retrospective content. Inlets are OPTIONAL and sourced from the brief, so GHI #619's input-free floor is unchanged. Prior `0.5.0` — GHI #763: the token block's register entry is an **exchange record**, named and stored as one. It lived in `.gzkit/handoffs/` under session-handoff identifiers, so system membership had to be *inferred* from a shared word, path, and directory rather than read from a discriminator — and was inferred wrongly twice in one session. Records now live in `.gzkit/locks/exchange/` (location types membership), the writers/finder are `exchange`-named in `gzkit.exchange_records`, and `--lock-handoff-coupling` survives as a deprecated alias of `--lock-exchange-coupling`. § Sub-Invariant 5's predicate is now **default-deny**: it admits only the shape an exchange writer emits, so a document kind nobody admitted is refused without having to be enumerated first. The ledger payload key `handoff_path` is FROZEN on the wire — 204 append-only events carry it. Prior `0.4.0` — GHI #756: § Binding Sub-Invariant 5 now names `mode: CHECKPOINT` as a third disqualifier alongside `abandoned: true`. `mode` was `Literal["CREATE", "RESUME"]` and `find_exchange_for_release` never read it, so once the mid-flight bookmark mode existed, a bookmark postdating the claim would have satisfied the release precondition — a token surrendered on the evidence of a session that never departed. The predicate now skips checkpoints at the live gate and `gz validate --lock-exchange-coupling` backstops it on ledger replay. Prior `0.3.1` — diet pass (operator ruling 2026-08-02): lifted § Vocabulary, § Cross-Links, and § Audit Path to `docs/governance/token-block-doctrine.md` (correcting the retired "5:1 governance ratio" citation in transit); binding sub-invariants unchanged. Prior `0.3.0` — added § Binding Sub-Invariant 6 (completion surrender is mechanical): `gz obpi complete` (and the `gz obpi pipeline` sync stage that invokes it) writes the register-entry handoff and releases any held lock automatically (GHI #619), so the token's exit edge no longer requires an operator-authored handoff or a manual `gz obpi lock release`. This does NOT relax Sub-Invariant 5 — completion produces the register entry mechanically rather than demanding the operator author one; the fail-closed manual release path is unchanged for mid-traversal surrender. Prior `0.2.0` — Sub-Invariant 2 minimum-information channels are now named per-field: items 1/2/4 are frontmatter keys, item 3 is the `## Decisions Made` body section. Resolves the rule↔validator↔producer drift where the prose said "frontmatter or body" but both `gz validate --lock-exchange-coupling` and the machine-generated reaping handoff already use frontmatter. Prior `0.1.1` — trimmed railway-history pedagogy while preserving all lock-release and handoff invariants.

## `tool-skill-runbook-alignment.md`

Lifted 2026-08-29 at version `0.4.0` (rule now at `0.5.0`).

> **Rule version:** `0.4.0` — § When to apply — *Authoring a new CLI verb* now names the wielding skill as **one of seven** obligations and points at `.gzkit/rules/cli.md` § Adding CLI Features — New Subcommand as the authority, instead of reading as the whole requirement. Measured 2026-08-22: the new-verb obligation set was described in three places and no two agreed — this row named 1 obligation, `cli.md` § Consistency named 3, and `cli.md` § New Subcommand named 4, against 7 that fail closed. An author who found this row first shipped a skill and nothing else. This is GHI #787's class recurring on a second surface: a point-of-use coupling checklist that undercounts its own obligations, discovered by the slowest gate rather than the cheapest. One authority, others point at it. Prior `0.3.0` — Movement C family closure, rules arm: adds § Enforcement posture, which states in the rule's own text that Invariant 1 is mechanical while Invariants 2 and 3 are advisory by design. The scorecard carried rows 29 and 30 as **Promotable** for months on the premise that the skill→runbook cross-reference and output-form fixtures were merely unbuilt. They are not merely unbuilt: both invariants turn on *"the same operator moment"*, and no repository surface represents an operator moment as a comparable object — the runbook prescribes verbs in prose, so a checker would have to score the agreement of two prose surfaces, which is grading by shape. The section also names the mechanical witness that DOES exist nearby (`gz validate --cli-alignment`, which catches the renamed-verb half of Invariant 2) so the advisory scope is the residue, not the whole. Re-scored `Judgment` at `docs/governance/advisory-rules-audit.md` rows 29 and 30; re-scoring without this text edit would have been laundering (operator ruling 2026-08-08). Prior `0.2.0` — lifted pedagogy, canonical violations, and enforcement details to rationale doc under GHI #327.

## `brief-heading-conventions.md`

Lifted 2026-08-30 at version `0.1.0` (rule now at `0.2.0`).

> **Rule version:** `0.1.0` — adds the body-level version marker required by
> `skill-surface-sync.md` § Non-negotiable rules #2, which this file never
> carried (Pass A run 2026-07-16 marker sweep). Content unchanged; no conflict
> row was raised against this rule.

## `changelog-release-notes.md`

Lifted 2026-08-30 at version `1.1.0` (rule now at `1.2.0`).

> **Rule version:** `1.1.0` — the hermetic `gz validate --changelog` structural scope landed; corrected the release-notes enforcement wording (no mechanical release-notes validator exists) (GHI #685).

## `complexity-doctrine.md`

Lifted 2026-08-30 at version `0.3.1` (rule now at `0.4.0`).

> **Rule version:** `0.3.1` — renamed prohibited `## Corpus Anti-Patterns` heading → `## Corpus Disqualifiers` (OBPI-0.0.54-04 shape conformance pass).

## `complexity-thresholds.md`

Lifted 2026-08-30 at version `0.4.0` (rule now at `0.5.0`).

> **Rule version:** `0.4.0` — GHI #469: corrected `> See [...]` pointer paths from file-relative `../../docs/...` to repo-root-relative `docs/...` so `gz validate --pointer-anchors` resolves them correctly (ADR-0.0.33 Invariant 3).

## `models.md`

Lifted 2026-08-30 at version `0.1.0` (rule now at `0.2.0`).

> **Rule version:** `0.1.0` — initial shape conformance pass; renamed prohibited heading (OBPI-0.0.54-04).
