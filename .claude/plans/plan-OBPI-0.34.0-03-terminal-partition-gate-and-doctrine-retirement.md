# Plan — OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement

**OBPI:** `OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement`
**Parent ADR:** `ADR-0.34.0-foundation-sunset`
**Lane:** Heavy

## Context

Parent ADR § Decision item #3 (verbatim): "terminal-partition-gate-and-doctrine-retirement:
Add the terminal-partition assertion to gz validate --taxonomy reading the Layer-2
foundation_grandfathered ledger event (never frontmatter): every grandfathered
foundation is terminal, none in Pending-with-attested-work limbo -> finding
foundation_limbo, whose prose states it reads the ledger and points at gz closeout /
gz adr demote. Retire ADR-0.0.18's choose-foundation guidance (record stays frozen).
Execute the coupled-surface coherence sweep (gz-design Step 5, plan/promote help +
parser choices, AGENTS.md/CLAUDE.md Kinds table, foundation-feature-invariance-test.md,
ADR-0.0.35 review). (heavy lane: new validator behavior + doc coherence)."

This OBPI ships the *mechanism*; OBPI-04 populates the data it reads. The
manifest is currently `[]` and no `foundation_grandfathered` event exists
anywhere in the ledger, so the new assertion iterates an empty set and
contributes **zero** findings. That is the anti-staging-flag posture the parent
ADR § Decision demands (REQ-7): green by construction, never green by a hand-set
flag.

**Pre-existing red, inherited not caused.** `uv run gz validate --taxonomy`
already exits 3 with **74 `foundation_kind_closed` findings** (observed
2026-07-28) — OBPI-01's closed-kind assertion firing over the empty manifest,
resolved by OBPI-04's populate. This OBPI must add zero findings and remove
zero findings from that count. The brief's Verification block lists
`uv run gz validate --taxonomy`, which will exit 3 for that inherited reason;
the honest evidence is the finding-type census (74 `foundation_kind_closed`,
0 `foundation_limbo`), not a green exit code. Surface this at Stage 4 rather
than narrowing the REQ.

## Files

**Modified (in brief Allowed Paths):**

- `src/gzkit/governance/trust_audits/taxonomy.py` — add
  `_grandfathered_event_ids` (raw-line ledger replay, mirroring
  `audit_pool_adr_isolation` lines 63–93) and fold the `foundation_limbo`
  findings into `audit_foundation_closure`.
- `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
  — superseded marker on the choose-foundation guidance (`## Why foundation
  tier?`, `## Decision`); record stays whole.
- `.gzkit/skills/gz-design/SKILL.md` — Step 5 kind question (line 137) stops
  offering `foundation` as a selectable kind; bump `metadata.skill-version` +
  `last_reviewed` per `.claude/rules/skill-surface-sync.md` rule #6.
- `docs/user/concepts/adr-taxonomy.md` — closure note.
- `docs/user/concepts/foundation-feature-invariance-test.md` — closure note.
- `.claude/`, `.agents/`, `.github/` — **generated only**, via
  `uv run gz agent sync control-surfaces`. Never hand-edited.

**Created:**

- `tests/test_foundation_limbo_gate.py` — REQ-0.34.0-03-01, -02.
- `tests/test_foundation_doctrine_retirement.py` — REQ-0.34.0-03-03, -04.

**Explicitly NOT touched (brief Denied Paths):**

- `AGENTS.md` / `CLAUDE.md` — rendered from `.gzkit/corpus/AGENTS.md.jsonl`;
  the Kinds-table update routes through `gz content remember` at the
  migration/compose movement, per the brief's own deferral.
- `src/gzkit/commands/validate_cmd.py` — `_taxonomy_runner` already calls
  `audit_foundation_closure`; folding the new finding in there needs no wiring.
- `data/foundation_grandfather.json` — read-only here; OBPI-04 populates.
- `src/gzkit/cli/parser_*.py` — OBPI-02's scope.
- `docs/design/adr/foundation/ADR-0.0.35-*` — review-only.

## Composition point — a brief-vs-code drift, resolved

The brief's Allowed Paths says the assertion is "a helper composed into
`audit_adr_taxonomy`". That instruction is **stale relative to what OBPI-01
actually landed**: `audit_adr_taxonomy`'s docstring (taxonomy.py:270-275) now
declares the ADR-0.34.0 closure assertions "scope-mates, not callees … merging
the two would make every existing caller's result depend on the grandfather
manifest's population state."

Folding `foundation_limbo` into `audit_adr_taxonomy` would violate that
invariant on the very commit that OBPI-01 attested it. The plan therefore
composes into **`audit_foundation_closure`** — the ADR-0.34.0 closure family,
already summed into `_taxonomy_runner` — which satisfies every constraint the
brief actually cares about (same `--taxonomy` scope, no `validate_cmd.py` edit,
Layer-2 read) without breaking a sibling OBPI's attested separation. No brief
amendment is needed: the Allowed Path (`taxonomy.py`) is unchanged and the REQs
are silent on which function hosts the helper.

## Steps

### Step 1 — RED: `foundation_limbo` fires on a manifest entry with no ledger event (REQ-0.34.0-03-01)

Write `TestFoundationLimboGate` against a `tmp_path` fixture project carrying
one on-disk `kind: foundation` ADR, a manifest declaring it, and a ledger with
**no** `foundation_grandfathered` event for it. Assert `audit_foundation_closure`
returns a `ValidationError` with `type == "foundation_limbo"` naming that ADR.

Because the manifest declares the ADR, `foundation_kind_closed` must NOT fire —
so the assertion isolates the new finding rather than riding a sibling's.

The symbol `audit_foundation_closure` already exists and imports cleanly, so
this is an **assertion-level red**, not an ImportError. Watch it fail on the
missing `foundation_limbo`.

### Step 2 — RED: ledger-not-frontmatter (REQ-0.34.0-03-01 companion)

Second assertion in the same class: take the Step-1 fixture, rewrite the ADR's
frontmatter `status:` to `Validated`, re-run, and assert `foundation_limbo`
**still** fires. This is the negative control that proves terminal state is
computed from Layer-2 and cannot be hand-edited green — the exact failure class
the ADR-0.0.37 investigation exposed. A test that passes when frontmatter is
consulted would be tautological.

Third assertion: seed the ledger with a `foundation_grandfathered` event naming
the ADR and assert the finding **clears**. Without this the test cannot
distinguish "reads the ledger" from "always fires".

### Step 3 — GREEN: implement the assertion

Add to `taxonomy.py`:

- `_grandfathered_event_ids(project_root) -> set[str]` — replay
  `.gzkit/ledger.jsonl` raw lines via `json.loads`, filter
  `event == "foundation_grandfathered"`, collect the ADR id from `id` /
  `adr_id` (same key-tolerance as `_pool_violation_key`). Returns an empty set
  when the ledger is absent.
- In `audit_foundation_closure`, after the two containment families, extend
  with one `foundation_limbo` error per `declared - grandfathered`, sorted.

Note the predicate operates on `declared` (manifest ids), not `on_disk` — a
foundation absent from the manifest is already `foundation_kind_closed`, and
double-reporting it would make the 74-finding census unreadable.

### Step 4 — RED/GREEN: three-part recovery prose (REQ-0.34.0-03-02)

Assert the `foundation_limbo` message satisfies
`.claude/rules/guardrail-feedback-prose.md`:

- (a) what failed — names the ADR id and the missing `foundation_grandfathered` event
- (b) why forbidden — cites ADR-0.34.0 and states **it reads the ledger, not
  frontmatter**, so `status:` cannot be hand-edited to pass
- (c) governed next step — names both `gz closeout` and `gz adr demote`

Assertions derive from the REQ's own wording, not from the string I am about to
write.

### Step 5 — RED/GREEN: ADR-0.0.18 frozen-historic (REQ-0.34.0-03-03)

`TestFoundationDoctrineRetirement` asserts the ADR-0.0.18 file **exists** (the
frozen-not-deleted half) and contains a superseded marker naming `ADR-0.34.0`.
Both halves in one test — a marker on a deleted file is not the requirement.

Then add the marker to ADR-0.0.18 as a block quote at `## Why foundation tier?`
and `## Decision`, phrased as *void as instruction, preserved as history*. Do
not alter the Decision text itself — retirement is annotation, not redaction.

### Step 6 — RED/GREEN: coupled-surface closure (REQ-0.34.0-03-04)

Assert `gz-design` SKILL.md Step 5 and
`foundation-feature-invariance-test.md` each carry a kind-closed note
referencing `ADR-0.34.0`, and that Step 5 no longer presents `foundation` as a
selectable kind for a new ADR.

The assertion must be able to fail for the right reason: a bare `"ADR-0.34.0"
in text` check would pass on any incidental mention. Assert on the closure
semantics — the note text — and separately that the kind question's offered
choices are `feature` / `pool`.

Then edit:

- `.gzkit/skills/gz-design/SKILL.md:137` — reframe the kind question to
  `feature`/`pool` with a one-line note that `foundation` is closed
  (ADR-0.34.0) and grandfathered-only. Bump `metadata.skill-version` (minor —
  procedure change) and `last_reviewed` to today.
- `docs/user/concepts/foundation-feature-invariance-test.md` — closure note
  near the top: the test remains valid doctrine for reading the grandfathered
  set and for adopters (whose `gz init` scaffolds open), but gzkit authors no
  new foundations.
- `docs/user/concepts/adr-taxonomy.md` — same closure note at the kind table.

Then `uv run gz agent sync control-surfaces` to regenerate the vendor mirrors.

### Step 7 — REFACTOR + review

- `uv run ruff check . --fix` and `uv run ruff format .`
- ADR-0.0.35 review (read-only): confirm it teaches nothing stale about
  foundation authoring. Record the observation in evidence; edit nothing.
- Confirm the finding-type census is unchanged except for the intended zero:
  74 `foundation_kind_closed`, 0 `foundation_limbo`, 0 `grandfather_dangling`.

## Verification

```bash
uv run gz validate --documents
uv run gz validate --taxonomy
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
```

Plus per-REQ RED witnesses (`uv run gz arb red --req ... --obpi ...`) and
`uv run gz covers OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement --json`.

## Step 6a — Plan-Before-Exploration Disclosure

**Destination-in-mind.** Before writing this plan I had already concluded the
assertion would be a set-difference between manifest ids and
`foundation_grandfathered` ledger ids, reusing the raw-line replay pattern. The
brief handed me that destination outright — it names the pattern, the source
lines (taxonomy.py 63–93), and the finding name. So the plan is a
reconstruction of a supplied conclusion, and I should say so plainly.

The exploration afterward was not purely confirmatory, and changed two things.
First, it surfaced that the brief's named composition point
(`audit_adr_taxonomy`) contradicts a separation invariant OBPI-01 attested in
that function's own docstring — resolved above by composing into
`audit_foundation_closure` instead. Second, it established that `--taxonomy` is
*already* red at 74 findings, which the brief's Verification block does not
acknowledge; without observing that I would have chased a green exit code that
this OBPI cannot and must not produce.

**Rejected alternatives.**

1. *Read terminal state from ADR frontmatter `status:`.* Rejected — REQ-1
   forbids it and the ADR-0.0.37 investigation proved frontmatter lies about
   repudiated OBPIs. This is the whole point of the gate.
2. *Compute the predicate over `on_disk` foundations rather than manifest
   entries.* Rejected — every on-disk foundation is currently absent from the
   manifest, so this would emit 74 `foundation_limbo` findings on top of the 74
   `foundation_kind_closed` ones, doubling a red the OBPI is supposed to leave
   untouched. The parent ADR scopes terminality to *"every manifest entry"*.
3. *Fold the assertion into `audit_adr_taxonomy` as the brief's Allowed Paths
   literally says.* Rejected — breaks OBPI-01's attested scope-mates-not-callees
   separation. See § Composition point.
4. *Add a third function and sum it in `_taxonomy_runner`.* Rejected —
   `validate_cmd.py` is a brief Denied Path, and the ADR-0.34.0 closure family
   already has a home.
5. *Use the typed `Ledger` reader instead of raw-line replay.* Rejected — the
   `foundation_grandfathered` event type has no model yet (OBPI-04 introduces
   it), so a typed read would either fail or require widening a schema outside
   this brief's scope. The brief explicitly permits the raw read so this gate
   does not hard-depend on the typed model.
6. *Delete ADR-0.0.18's guidance sections rather than annotate them.*
   Rejected — REQ-4 requires the record stay present. Frozen-historic means
   void as instruction, preserved as history.
7. *Hand-edit the AGENTS.md/CLAUDE.md Kinds table in this sweep.* Rejected —
   they are rendered surfaces; the brief's Denied Paths routes that through the
   corpus, and the brief defers the corpus write to the compose movement.
