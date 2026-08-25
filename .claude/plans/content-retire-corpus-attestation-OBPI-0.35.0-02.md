# Plan — OBPI-0.35.0-02-content-withdraw-verb (Content Retire: Corpus Attestation)

## Context

**Brief:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-02-content-withdraw-verb.md`
**Parent ADR:** `ADR-0.35.0-canon-entry-corpus-landing`
**Lane:** Heavy · **Sensitivity:** security

**Parent ADR § Checklist item 2, verbatim:**

> `gz content retire` — corpus-attestation extension of the shipped verb: fail-closed on invariant tier (`--attestor` / `--reason` refused when empty). Amended 2026-08-07 from the `content withdraw` name; see § Decision item 2.

The verb SHIPPED under GHI #635 (`852e8a25`, 2026-07-22). Four of the seven brief-tracked
behaviors already land (id-keyed selector, append-only, fail-closed on unknown/already-retired,
one retraction row). This plan closes the **corpus-attestation half**: attestor capture, tier
discrimination, the second ledger event, and three-part recovery prose.

**GHI #873 is NOT a blocker here** (ruled 2026-08-25, comment `#issuecomment-5403903863`):
`retire.py:71` emits `retires=`, never `supersedes=`. No producer of `supersedes` exists in
`src/gzkit/**`, and no ADR-0.35.0 checklist item adds one. The `supersedes`-chain shape stays
unreachable after this OBPI lands.

## Destination-in-Mind (Step 6a disclosure)

Before writing this plan I had already formed the conclusion that **`retire.py` gets extended
in place rather than re-implemented**, and that **tier discrimination reads `target.tier`
directly off the resolved `CorpusEntry`** rather than routing through `tier_policy`. Both were
formed while reading `retire.py:41-72` — `corpus.entry(entry_id)` already returns the target
with its `tier` field populated, so the discriminator is one attribute access away and
introducing a policy indirection would be an abstraction over a single call site
(AGENTS.md § DO IT RIGHT #10).

## Rejected Alternatives

1. **Make `--attestor` unconditionally required.** Rejected — REQ-0.35.0-02-03 forbids it
   explicitly ("NEVER require corpus attestation for a `compressible`-tier target"), and the
   ADR's reasoning is that the corpus attestation guards the 0-Kelvin invariant floor, not
   routine bookkeeping. Unconditional requirement would also break every existing
   `gz content retire` invocation, a Heavy CLI contract break for no gain.
2. **Route the tier check through `tier_policy.invariant_entries()`.** Rejected — that helper
   folds the whole corpus to answer a question already answered by `target.tier`. It would also
   couple this verb to the OBPI-0.35.0-01 fold on a path where the fold's answer is not needed,
   widening the blast radius of a future algebra change (GHI #873 is live on that algebra).
3. **Emit only `corpus_entry_retired` and let the appended-row witness be implied.** Rejected —
   REQ-0.35.0-02-06 requires BOTH, and the brief names the pair as the SUPPORT proof channel for
   OBPI-0.35.0-03's batch. An implied witness is the presence-check anti-pattern
   (AGENTS.md § PRESENCE CHECK).
4. **Add a `--text` selector for convenience.** Rejected on the ADR's own recorded grounds
   (§ Alternatives D): six of seven byte-identical duplicate groups address the same text to two
   different sections, so a text key silently elects a section winner. REQ-01 forbids it.
5. **New `retire2` verb / rename to `withdraw`.** Rejected by standing operator ruling
   (2026-08-07, brief § DECISION RULED) — extend in place.

## Files

**Modify (all inside the brief allowlist):**

| Path | Change |
|---|---|
| `src/gzkit/ledger_events.py` | `corpus_entry_retired_event` gains `tier` + `attestor` params in its `extra` payload |
| `src/gzkit/commands/content/retire.py` | `attestor` param; tier-discriminated fail-close; three-part prose on every exit; emit `corpus_entry_appended` alongside `corpus_entry_retired` |
| `src/gzkit/commands/content/__init__.py` | Register `--attestor`; relax `--reason` from `required=True` to default `""`; thread both through |
| `tests/commands/test_content_retire.py` | EXTEND with covering tests for REQ-01..07 |
| `features/content_retire.feature` | CREATE — Gate 4 scenarios |
| `features/steps/**` | Step definitions for the new feature |
| `docs/user/manpages/content.md` | EXTEND `### retire` (line 127) with the attestation contract |
| `docs/design/adr/.../OBPI-0.35.0-02-content-withdraw-verb.md` | Evidence sections at Stage 5 |

**Read-only (Denied Paths — consumed, never edited):**
`src/gzkit/content/models/corpus.py` (`effective_corpus`), `src/gzkit/content/corpus_store.py`
(`append_entry`), `src/gzkit/commands/content/commit.py:88-117` (the fail-closed pattern mirrored).

## Steps

### Step 1 — Extend the ledger event payload (REQ-07)

`ledger_events.py::corpus_entry_retired_event` gains `tier: str` and `attestor: str`, both
written into `extra`. The existing `surface` / `retired_entry_id` / `retraction_entry_id` /
`reason` keys are unchanged — this is additive, so no existing ledger reader breaks.

RGR: test asserts the emitted event's `extra` carries all six keys → watch it fail on the
assertion (`KeyError`/`assertIn` on `tier`), not on an import → add the params.

### Step 2 — Tier-discriminated corpus attestation in `retire.py` (REQ-01, -02, -03)

Signature becomes `content_retire_cmd(*, surface, entry_id, reason, origin, attestor="")`.

After the target resolves and BEFORE any write:

```
if target.tier == "invariant" and not (attestor.strip() and reason.strip()):
    <three-part prose to stderr>; sys.exit(1)
```

Placement is load-bearing: the check sits after `corpus.entry()` (the tier is unknowable
before) and before `append_entry` (REQ-01 demands the corpus file be byte-unchanged and NO
ledger event written). This mirrors `commit.py:88-117`'s fail-closed arm — never its
unchanged-canon exemption, because retirement IS a canon change.

RGR per behavior: empty attestor (REQ-01) → whitespace-only attestor (REQ-02) →
whitespace-only reason (REQ-02 symmetric) → compressible passes without either (REQ-03).
Four cycles, each watched red on its own assertion.

### Step 3 — Three-part recovery prose on every fail-closed exit (REQ-05, -07)

Per `.claude/rules/guardrail-feedback-prose.md` § Invariant, each of the four exits emits
**what failed · cited rule · runnable next step**. Today's messages carry the first part
and "nothing written" but no citation and no runnable step. The four exits:
unknown entry (`:42`), already-retired (`:50`), the new invariant-tier attestation refusal,
and the `OSError` write path (`:76`).

RGR: assert each stderr carries a rule citation token and a `gz ` runnable → red on the
assertion → author the prose.

### Step 4 — Emit both ledger events (REQ-07)

`append_entry` emits nothing, so `retire.py` emits `corpus_entry_appended_event(surface,
section=retraction.section, entry_id=retraction.id, tier=retraction.tier)` immediately after
the successful append, then `corpus_entry_retired_event(...)` with the extended payload.
Order: appended-then-retired, so a reader replaying the ledger never sees a retirement whose
row has not yet been witnessed.

### Step 5 — Parser registration (REQ-03, -06)

`__init__.py::_register_retire`: add `--attestor` (default `""`), relax `--reason` to
`default=""` (REQ-03 requires a compressible retirement with NEITHER flag to exit 0). Update
the description/epilog to state the invariant-tier fail-close. No `--text` selector is added —
REQ-06 asserts the option set contains `--entry` and no text-valued selector.

### Step 6 — Gate 4 BDD (`features/content_retire.feature`)

CREATE. Scenarios tagged `@REQ-0.35.0-02-01` … `@REQ-0.35.0-02-07` so Stage 3's scoped behave
resolves them. Reuse existing step definitions where they exist; add only what is missing.

### Step 7 — Manpage (REQ-08, support)

`docs/user/manpages/content.md` `### retire`: document `--attestor`, the invariant-tier
fail-close, and that `--reason` is now optional for compressible targets. The synopsis line
gains `[--attestor <name>]`. Proof channel is a path-citing `artifact_edited` ledger event plus
`gz validate --cli-alignment`, NOT a unit test (ADR-0.0.59 — never author a test to make a
SUPPORT REQ look covered).

## Verification

```
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run gz validate --cli-alignment
uv run gz validate --req-kind-discipline
uv run mkdocs build --strict
```

Plus Stage-3 pipeline gates: `gz covers OBPI-0.35.0-02-content-withdraw-verb --json`
(BEHAVIOR parity) and `gz arb red --req <REQ> --obpi <slug>` per BEHAVIOR REQ.

## Notes

- REQ-08 is the only `[support]` REQ; REQ-01..07 are `[behavior]`. No STRUCTURAL-FENCE REQ in
  this brief, so no parent-ADR `## Boundary Invariants` entry is added here.
- `--reason` relaxing from required to optional is additive at the CLI: every existing
  invocation still parses. `gz cli audit` and `--cli-alignment` are in the verification set to
  catch any manpage/parser divergence this introduces.
- The brief's allowlist names `src/gzkit/ledger_events.py` correctly; its Discovery Checklist
  still points at `src/gzkit/governance/events.py`, which carries no corpus-retirement helper.
  That is authored-note drift already recorded in the brief's own reconciliation banner — no
  code follows the stale pointer.
