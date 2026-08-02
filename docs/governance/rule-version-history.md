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

## `cli.md`

Lifted at version `0.3.0` (rule now at `0.3.1`).

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

Lifted at version `0.2.0` (rule now at `0.2.1`).

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

Lifted at version `0.3.0` (rule now at `0.3.1`).

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

## `task-discovery.md`

Lifted at version `0.5.0` (rule now at `0.5.1`).

> **Rule version:** `0.5.0` — commit-trailer channel is now PRODUCER-STAMPED
> (GHI #731; ~15% authored adherence left Signature (c) skipping 96 of 102
> OBPIs). See § Convention: Commit trailer. Prior `0.4.0` — reconciled to `tests.md`:
> the channels are cumulative-with-a-floor (an `@advances` decorator never
> discharges the `Task:` obligation, GHI #552), and the slug form's `-#<ghi>`
> anchor is optional (operator moratorium 2026-06-01). Prior `0.3.0` — ADR-0.0.64
> closeout reconciliation.

## `pythonic.md`

Lifted at version `0.2.0` (rule now at `0.2.1`).

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
