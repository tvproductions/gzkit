---
id: OBPI-0.35.0-02-content-withdraw-verb
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 2
lane: Heavy
status: Draft
allowlist:
- src/gzkit/commands/content/withdraw.py
- src/gzkit/commands/content/__init__.py
- src/gzkit/cli/**
- src/gzkit/governance/events.py
- tests/commands/test_content_withdraw.py
- features/content_withdraw.feature
- features/steps/**
- docs/user/manpages/content.md
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-02-content-withdraw-verb.md
reqs:
- REQ-0.35.0-02-01
- REQ-0.35.0-02-02
- REQ-0.35.0-02-03
- REQ-0.35.0-02-04
- REQ-0.35.0-02-05
- REQ-0.35.0-02-06
- REQ-0.35.0-02-07
- REQ-0.35.0-02-08
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz cli audit
- uv run gz validate --cli-alignment
- uv run gz validate --req-kind-discipline
- uv run mkdocs build --strict
---

# OBPI-0.35.0-02-content-withdraw-verb: Content Withdraw Verb

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #2 - "gz content withdraw verb; Gate 5 fail-closed on invariant tier (`--attestor` / `--reason` refused when empty)"

**Status:** Draft

## Objective

Ship the new verb gz content withdraw, taking `<surface> --entry <id> --attestor <name> --reason <text>` — the operator surface that appends an OBPI-0.35.0-01 tombstone. Retirement is keyed to the entry id and NEVER to the entry text; retiring an `invariant`-tier entry is Gate 5 fail-closed on empty `--attestor` or `--reason`, mirroring `gz obpi repudiate` (ADR-0.0.71).

**Dependency order (ADR-0.35.0 § Scope Minimization):** 02 depends on 01 (the tombstone fields and the fold must exist before a verb can append one) and is the prerequisite for 03. 01 -> 02 -> 03 is the minimum shippable slice and alone discharges GHI #635.

<!-- gz-validate-skip: command-shape -->
> **PARTIALLY PRE-LANDED, AND THE VERB NAME COLLIDES — read before implementing
> (reconciled 2026-08-07).** A retirement verb already ships. It landed ahead of
> this chain as the GHI #635 direct fix (`852e8a25`) on 2026-07-22, ONE DAY after
> this brief was authored, and it is named **`gz content retire`**
> (`src/gzkit/commands/content/retire.py`) — not `gz content withdraw`. Implementing
> this brief as written would stand up a SECOND verb doing one job. Measured at
> HEAD `6863f0555`:
>
> | Requirement | Target | Observed in `retire.py` | State |
> |-------------|--------|--------------------------|-------|
> | 1 — never accept a `--text` selector | id-keyed only | `--entry <id>` keyed; no text selector | **landed** |
> | 2 — Gate 5 fail-closed on `invariant` tier | empty `--attestor`/`--reason` exits non-zero, writes nothing | **no `--attestor` parameter at all**; `reason` is not empty-checked (`retire.py:31`) | **open** |
> | 3 — never require Gate 5 for `compressible` | tier discrimination | **no tier discrimination anywhere** | **open** |
> | 4 — always append, never shrink | append-only | appends a retraction row via `corpus_store.append_entry` (`retire.py:74`) | **landed** |
> | 5 — fail closed on unknown / already-retired / absent store | exit non-zero, write nothing | exit 1 on both unknown (`:47`) and already-retired (`:55`) | **landed** |
> | 6 — emit BOTH `corpus_entry_appended` and `corpus_entry_retired` | two events | only `corpus_entry_retired_event` (`:80`); `append_entry` emits none | **half open** |
> | 7 — three-part recovery prose on every fail-closed exit | what failed, cited rule, runnable next step | messages name what failed and that nothing was written, but carry **no runnable next step and no rule citation** | **open** |
>
> **Allowlist drift the reconciler cannot see.** This brief's allowlist names
> `src/gzkit/governance/events.py` as the home of the `corpus_entry_retired` ledger
> event. The shipped event is `corpus_entry_retired_event` in
> **`src/gzkit/ledger_events.py`**; `governance/events.py` carries no corpus-retirement
> helper (its only `corpus` hits are `corpus_fingerprint`). `gz obpi brief-drift`
> reports allowlist=0 because the named file EXISTS — existence is not
> relevance (GHI #581).
>
> **BLOCKING DECISION — do not resolve this by implementing.** Two routes, and they
> are not equivalent:
>
> 1. **Extend `retire` in place** — add `--attestor`, the empty-check, tier
>    discrimination, the second event, and the recovery prose to the shipped verb;
>    amend the parent ADR § Decision item 2 and its Fidelity Assertion row to say
>    `retire`. Smaller diff, no duplicate surface, but edits an ADR Decision.
> 2. **Rename `retire` → `withdraw`** — a CLI contract change (Heavy; `.claude/rules/cli.md`
>    § Heavy Lane Trigger), carrying the manpage, `gz cli audit` coverage, and any
>    existing callers. Keeps the ADR's word; costs a rename of a shipped verb.
>
> The parent ADR's Fidelity Assertion invokes
> `gz content withdraw ... --attestor "" --reason "probe"` expecting exit 1 — a
> command that does not exist. It is invisible to `gz validate --cli-alignment`
> because the row carries `<!-- gz-validate-skip: command-shape -->`: the marker
> that lets a planned verb be documented is also what hid this collision.
>
> Note: `uv run gz obpi brief-drift OBPI-0.35.0-02-content-withdraw-verb` reports
> **clean across all five dimensions**. This note is authored, never computed.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/commands/content/withdraw.py` — new command module **CREATE**
- `src/gzkit/commands/content/__init__.py` — command export
- `src/gzkit/cli/**` — parser registration for the `withdraw` subcommand only
- `src/gzkit/governance/events.py` — the `corpus_entry_retired` ledger event
- `tests/commands/test_content_withdraw.py` — new covering tests **CREATE**
- `features/content_withdraw.feature`, `features/steps/**` — Gate 4 scenarios **CREATE**
- `docs/user/manpages/content.md` — the `withdraw` section
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-02-content-withdraw-verb.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/content/models/corpus.py`, `src/gzkit/content/tier_policy.py` — schema and fold are OBPI-0.35.0-01 and are consumed read-only here
- `.gzkit/corpus/AGENTS.md.jsonl` — appending the eight production tombstones is OBPI-0.35.0-03; this OBPI writes only test-fixture corpora
- `src/gzkit/commands/content/commit.py`, `compose.py`, `remember.py` — sibling verbs are out of scope (`remember` is OBPI-0.35.0-08)
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. NEVER accept a `--text` selector. Retirement is per-entry-id, full stop. Six of the seven byte-identical duplicate groups address the same text to TWO DIFFERENT sections, so a text key silently elects a section winner — a question text identity cannot see (ADR § Alternatives D).
2. ALWAYS fail closed on Gate 5 for `invariant`-tier targets: an empty or whitespace-only `--attestor` or `--reason` MUST exit non-zero and write NOTHING — no corpus append, no ledger event, no partial file. Mirror `commit.py:47-54` and `gz obpi repudiate`.
3. NEVER require Gate 5 for a `compressible`-tier target. The 0-Kelvin floor is what human attestation protects; compressible retirement is routine.
4. ALWAYS append. The verb appends a tombstone row through `corpus_store.append_entry`; the raw log's row count MUST grow and MUST NEVER shrink (alternatives E and F).
5. ALWAYS fail closed on an unknown `--entry` id, an already-retired target, or an absent corpus store — exit non-zero, write nothing.
6. ALWAYS emit BOTH ledger events on a successful retirement: `corpus_entry_appended` for the tombstone row (a tombstone IS an appended corpus row and goes through `corpus_store.append_entry` like any other), and a new `corpus_entry_retired` carrying the retired entry id, the tombstone row id, the surface, the tier, the attestor, and the reason. The pair is the SUPPORT proof channel for OBPI-0.35.0-03's batch.
7. ALWAYS emit three-part recovery prose on every fail-closed exit per `.claude/rules/guardrail-feedback-prose.md`: what failed, the cited rule, the runnable next step.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- [ ] `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md` — pre-mortem, WWHTBT, constraint archaeology, 2am-operator, reversibility, scope minimization.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — the three-kind proof-channel matrix this brief's Acceptance Criteria are tagged against

**Context:**

- [ ] ADR § Decision item 2 — per-entry-id retirement and its recorded rationale.
- [ ] ADR § Alternatives D — text-keyed dedup, rejected on two counts; do not re-litigate.
- [ ] `.claude/rules/governance-core.md` § Withdraw vs Repudiate (ADR-0.0.71) — the verb-semantics precedent this surface mirrors.
- [ ] OBPI-0.35.0-01 — the fold this verb feeds; a tombstone this verb writes must satisfy Algebra 2, 3, and 7.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.35.0-01 landed: `CorpusEntry.retires` exists and `effective_corpus()` folds it
- [ ] `src/gzkit/commands/content/commit.py` exists (the Gate-5 fail-closed pattern to mirror, lines 47-54)
- [ ] `src/gzkit/content/corpus_store.py::append_entry` exists
- [ ] `src/gzkit/governance/events.py` exists and carries the emit-helper pattern for corpus events
- [ ] `docs/user/manpages/content.md` exists

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/content/commit.py:39-55` — the canonical empty-attestation fail-closed shape
- [ ] `src/gzkit/commands/content/remember.py` — the sibling capture verb's argument and normalization conventions
- [ ] `uv run gz obpi repudiate --help` — the `--attestor` / `--reason` operator-gated shape being mirrored
- [ ] `tests/commands/test_content_commit.py` — the test style for a fail-closed content verb

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. -->

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run gz validate --cli-alignment
uv run gz validate --req-kind-discipline
uv run mkdocs build --strict
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz content withdraw --help
uv run gz content withdraw AGENTS.md --entry corpus-prime-directive-ownership-2026-06-13T12:34:39.169495+00:00 --attestor "" --reason "probe"
uv run gz content withdraw AGENTS.md --entry does-not-exist --attestor "g0" --reason "probe"
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-02-01 [behavior]: Given the invocation `AGENTS.md --entry <invariant-tier id> --attestor "" --reason "probe"` passed to gz content withdraw, when the command runs, then it exits non-zero, the corpus file is byte-unchanged, and NO ledger event is written — Gate 5 is fail-closed on the invariant tier.
- [ ] REQ-0.35.0-02-02 [behavior]: Given the same invocation with a non-empty `--reason` but a whitespace-only `--attestor` (and the symmetric case), when the command runs, then it exits non-zero and writes nothing — whitespace is not attestation.
- [ ] REQ-0.35.0-02-03 [behavior]: Given `--entry` naming a `compressible`-tier entry and NO `--attestor`/`--reason`, when the command runs, then it exits 0 and appends the tombstone — Gate 5 guards the 0-Kelvin floor, not routine retirement.
- [ ] REQ-0.35.0-02-04 [behavior]: Given a valid invariant-tier retirement with a non-empty attestor and reason, when the command runs, then the raw corpus GROWS by exactly one row, the target entry is absent from `effective_corpus()`, and the target row itself is still present verbatim in the raw log.
- [ ] REQ-0.35.0-02-05 [behavior]: Given `--entry` naming an unknown id, an already-retired id, or a surface with no corpus store, when the command runs, then it exits non-zero, writes nothing, and its stderr carries all three recovery parts (what failed, the cited rule, a runnable next step).
- [ ] REQ-0.35.0-02-06 [behavior]: Given the registered parser, when gz content withdraw --help is invoked, then the option set contains `--entry` and contains NO text-valued selector — text-keyed retirement is unreachable from the CLI, not merely discouraged.
- [ ] REQ-0.35.0-02-07 [behavior]: Given a successful retirement, when the ledger is read, then a `corpus_entry_appended` event exists for the tombstone row AND a `corpus_entry_retired` event exists carrying the retired entry id, the tombstone row id, the surface, the tier, the attestor, and the reason.
- [ ] REQ-0.35.0-02-08 [support]: `docs/user/manpages/content.md` carries a `withdraw` section documenting the per-entry-id contract and the invariant-tier Gate-5 fail-close, — witnessed by an `artifact_edited` ledger event citing `docs/user/manpages/content.md` — and `gz validate --cli-alignment` resolves every gz content withdraw reference it prescribes.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
