---
id: ADR-pool.ledger-identity-redaction
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: 2026-08-20 operator-PII sweep
---

# ADR-pool.ledger-identity-redaction: Ledger Identity Redaction

## Status

Pool

## Date

2026-08-20

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Close the **Layer-2 write-side gap**. `docs/governance/state-doctrine.md` § Layer 2
canonizes the invariant — *"Each line is a timestamped, immutable event. Lines are
never edited or deleted"* — and `forbid_manual_ledger_edits`
(`src/gzkit/hooks/guards.py`, GHI #207) enforces it fail-closed against any staged
non-append diff. `AGENTS.md` § Behavior Rules — Never #2 and
`.gzkit/rules/governance-core.md` say the same in prose.

The enforcement is correct and should stay. What is missing is the **sanctioned
alternative it routes to**. `gz ledger` exposes exactly one subcommand,
`merge-driver`; there is no governed path by which even the operator may correct a
ledger identity. The rule forbidding hand-edits therefore points at nothing, which
is the shape this repository elsewhere calls doctrine drift: a prohibition with no
discharge mechanism is discharged by bypass.

**Why the existing precedent does not cover it.** `ADR-0.0.71-completion-repudiation`
already solved one instance of correcting ledger-recorded state under operator
authority, and solved it *without* mutation: the fraudulent receipt stays in
append-only history and `obpi_completion_repudiated` is the machine-readable
counter-marker. That pattern is correct whenever the defect is that a **claim is
wrong**. It cannot reach the case where the **content itself is the harm** —
appending a marker saying "this identity was not permitted" leaves the identity
sitting in the file. Personally-identifying information is the canonical member of
that class, and plausibly its only one.

**Live instance (2026-08-20).** The operator-PII rule (`AGENTS.md` § Local Agent
Rules) requires operator authorship to be recorded as `g0` in every attestor/author
identity field. A history sweep corrected commit metadata and blobs; a follow-up
sweep corrected 136 files of current content. `.gzkit/ledger.jsonl` held 169
occurrences across six JSON paths — `by` (98), `attestor` (63), `operator` (4), and
four inside evidence payloads. The operator ruled the scrub authorized; the guard
refused the commit; no governed route existed; the change could not land. That
deadlock is this ADR's subject.

## Decision

_(Pool — the discriminating principle is settled; mechanization surface decisions
are deferred to promotion.)_

### The discriminating principle

> The append-only invariant yields **only** where the recorded value is itself the
> harm and no counter-marker can neutralize it. Every other correction to
> ledger-recorded state remains an append — a counter-marker, never a mutation.

Redaction is therefore a **narrow, witnessed exception**, not a general edit
capability. If a defect can be expressed as "this claim was wrong", it routes to
repudiation or a counter-marker event and never to this verb.

### 1. CLI verb `gz ledger redact`

Named `redact`, never `rewrite`. The noun is load-bearing: `rewrite` invites the
unbounded mutation the guard exists to stop, and this repository has ruled once
already (GHI #822) that a governance verb must not be named after the artifact it
writes when that name asserts the wrong subject.

Operator-gated on the `gz obpi repudiate` pattern — `--attestor`, `--reason`, and a
closed `--cause` enum, each failing closed (exit 1, no write) when empty. Only a
human may redact.

### 2. Closed field allowlist

Redaction reaches **only identity fields** — `by`, `attestor`, `operator`, and
identity-bearing evidence sub-fields — as a closed set extensible only by amendment
ADR, on the model of the `--cause` enum in `ADR-0.0.71` and the abandon-category
enum in `.gzkit/rules/token-block-discipline.md`. It may never alter event types,
`ts`, ids, parentage, gate results, or evidence payloads. A redaction that changes
what an event *asserts* is out of bounds by construction.

### 3. The redaction witnesses itself

Appends a `ledger_redacted` event recording: fields touched, occurrence count,
`attestor`, `reason`, `cause`, and a digest of the post-image. The mutation and its
authorization live in the same append-only log, so an auditor reading forward sees
that a redaction occurred, who authorized it, and why — even though the redacted
value is gone. **This is the property that distinguishes redaction from
tampering.**

### 4. The guard gains one verified exception, and is not otherwise weakened

`forbid_manual_ledger_edits` today rejects any `-` line in a staged ledger diff.
It would instead admit a non-append diff **iff** the same commit appends a
`ledger_redacted` event whose recorded digest matches the post-image. Every other
manual edit stays fail-closed exactly as today.

The exception is itself mechanically checked, which is what keeps this governance
rather than a bypass: an unwitnessed carve-out decays into "agents edit the ledger
sometimes", and `.claude/rules/governance-core.md` § Non-negotiable rules already
records what an advisory rule with no mechanical witness costs.

### 5. Scope boundary

Redaction corrects the **working file** only. Git history retains prior values
until an operator-ruled history rewrite, which is a separate act with separate
costs (every pre-sweep SHA across the governance corpus goes dangling). This ADR
neither performs nor requires one, and must not be read as making the ledger's
history clean.

### Open surface decisions (resolve at promotion)

- **Digest shape and coverage** — whole-file digest vs. per-redacted-line digests.
  Whole-file is simpler to verify in a pre-commit hook; per-line survives an
  interleaved legitimate append in the same commit.
- **Where the field allowlist is encoded** — a validator constant, a schema
  annotation on the event models, or a JSON data file. `.claude/rules/governance-core.md`
  § Non-negotiable rules binds here: execution reads the roster from JSON or code,
  never from prose.
- **Whether redaction is scriptable in bulk** or strictly one invocation per field
  set. The 2026-08-20 instance touched 169 occurrences; a per-occurrence verb would
  have been unusable.
- **Whether `gz init` scaffolds the verb for adopters.** ADR-0.34.0's project-local
  carve-out is the precedent for deciding this deliberately rather than by default.

## Alternatives Considered

1. **Counter-marker / identity-supersession event** — append an
   `identity_superseded` event mapping old to new and resolve through it in derived
   views. **Rejected:** preserves append-only perfectly and does not solve the
   problem. The prohibited value remains in the file, which is the entire harm for
   the PII class. This is the `ADR-0.0.71` pattern reaching past its domain.
2. **`git filter-repo` pass over the ledger** — sweep history as the 2026-08-20
   name/address sweep did. **Rejected as the primary mechanism:** it re-dangles
   every SHA across the governance corpus a second time, and it does not address
   the working-tree rule at all — the next `gz`-emitted identity would re-introduce
   the value with no verb to correct it.
3. **Operator commits with `--no-verify`** — the guard is a pre-commit hook, so the
   operator can always bypass it personally. **Rejected as doctrine:** it works and
   is unwitnessed. Nothing records who authorized the mutation or why, which is
   precisely the audit property the ledger exists to provide. `AGENTS.md` § Never
   #10 forbids agents from taking this path at all.
4. **Widen the guard to permit non-append ledger diffs generally.** **Rejected:**
   removes the fail-closed property GHI #207 was filed to install, in exchange for a
   capability needed rarely and only under operator authority.
5. **No verb — keep per-incident operator judgment.** The status quo. **Rejected:**
   this *is* the defect. The 2026-08-20 instance produced an authorized change that
   could not land by any governed route, and the fallback available to an agent was
   a prohibited one.

## Notes

**Relationships:**

- **Sibling** to `ADR-pool.attested-record-edit-doctrine`, which owns the write-side
  admissibility ruling for **Layer-1 attested records** (briefs, ADR metadata) via
  its admit / re-attest / forbid buckets. This ADR's subject is **Layer-2**, under a
  different invariant. The two compose by reference and must not be merged: a
  Layer-1 semantics-preservation test says nothing about whether a Layer-2 line may
  be mutated.
- **Extends the pattern of** `ADR-0.0.71-completion-repudiation` (operator-gated,
  fail-closed on empty attestation, ledger-recorded) while explicitly departing from
  its append-only-preserving mechanism, for the reason given in § Intent.
- **Consumes** `forbid_manual_ledger_edits` (GHI #207) as the surface it amends.

**Promotion criteria:** before promotion, resolve the four § Open surface decisions
with operator preference. Promotes as **`gz adr promote --kind feature`** —
`foundation` is CLOSED to new authoring by ADR-0.34.0 (Foundation Sunset) and is
refused at the command layer. Heavy lane: it changes a CLI surface, a ledger event
schema, and a pre-commit guard. Security-sensitive on the `ADR-0.0.71` § Negative #3
reading — it mutates the audit log, so its own OBPIs carry Gate-5 attestation.

**Sibling routing receipts (on promotion):** the 2026-08-20 PII-sweep insight
records in `.gzkit/insights/agent-insights.jsonl` are the originating evidence; no
GHI was filed for the instance because a public issue describing an operator-PII
leak would itself be a disclosure.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree is performed via `gz adr promote`. In gzkit the
reachable target is `feature`; the wheel-shipped template's "foundation or feature"
wording is correct for adopters, whose foundation kind stays OPEN by ADR-0.34.0's
project-local carve-out.
