# gz content

Authoring CLI for the canonical content model substrate (ADR-0.0.34). The
`gz content` command group lets operators import, list, inspect, render, and
edit per-turn agent control surface files (rules, skills, personas, chores,
handoffs, scenarios, bullets, agent contracts) as canonical Pydantic models.

## Synopsis

```bash
gz content <subcommand> [OPTIONS]
```

## Description

`gz content` is the operator surface for the ADR-0.0.34 rendering substrate.
Per the headless-CMS doctrine, every per-turn agent control surface file is
rendered byte-stably from a canonical Pydantic model via a Jinja2 template.
Operators interact with these models through `gz content`; output is
human-readable prose by default, machine-readable JSON behind `--json`.

The content type registry exposes eight model types:

| Type | Surface |
|------|---------|
| `AgentContract` | `AGENTS.md`, `CLAUDE.md` |
| `Rule` | `.gzkit/rules/*.md` |
| `Skill` | `.gzkit/skills/*/SKILL.md` |
| `Chore` | `.gzkit/chores/*/CHORE.md` |
| `Persona` | `.gzkit/personas/*.md` |
| `Handoff` | `.gzkit/handoffs/*.md` |
| `Scenario` | BDD scenario records |
| `Bullet` | Single-bullet evidence rows |

Round-trip fidelity is binding: `model == parse(render(model))` for every type.

## Subcommands

### import

Read a hand-authored or canonical markdown file, parse it into a Pydantic
content model, and emit JSON to stdout. Optionally re-render the canonical
form to a target path.

```bash
gz content import <file> --as <type> [--write <path>]
```

`--write` persists the re-rendered canonical form to the named path; useful
for the OBPI-0.0.34-03 reverse-parse migration workflow.

### list

Enumerate the registered content model types from the `CONTENT_MODELS`
registry. Default output is a human-readable two-column table; `--json`
emits a machine-readable array.

```bash
gz content list [--type <content-type>] [--json]
```

`--type` filters output to a single type (e.g. `gz content list --type Rule`).

### show

Parse a canonical content file and display a prose summary (type, title,
field-by-field breakdown). The operator-facing surface is always
human-readable; pass `--json` for the canonical `model_dump_json()` form.

```bash
gz content show <file> --as <type> [--json]
```

### render

Parse a canonical content file and emit the re-rendered markdown to stdout.
Output is byte-identical to `gzkit.content.render.render(model, vendor)` for
the same input (round-trip stability per OBPI-0.0.34-02).

```bash
gz content render <file> --as <type> [--vendor <vendor>]
```

`--vendor` defaults to `claude`; other vendors render their respective
templates.

### edit

Open the canonical-form file in `$EDITOR` (or `$VISUAL`). On editor save,
the temp file is re-parsed and re-validated. **Invalid input aborts with
the validator diagnostic and never writes a partial file.** On successful
validation, the original file is atomically replaced with the re-rendered
canonical form via `Path.replace()`.

```bash
gz content edit <file> --as <type> [--vendor <vendor>]
```

The atomic-replace contract means a failed validation (or a non-zero editor
exit) leaves the original file byte-identical to its pre-edit state. There
is no partial-write state.

### remember

Append one addressed, provenanced entry to a surface's **append-only corpus**
store at `.gzkit/corpus/<surface>.jsonl` and emit a `corpus_entry_appended`
ledger event. This is the write path of the ADR-0.0.37 corpus pipeline
(`corpus → compress → rendition → playback`): capture grows the source of
truth; deterministic playback remains the sole writer of rendered surfaces.
**`remember` NEVER edits a rendered surface** (`AGENTS.md`, `CLAUDE.md`, or
any mirror) — that is its load-bearing invariant.

```bash
gz content remember <surface> --section <id> --text <text> \
  [--tier invariant|compressible] \
  [--classification Mechanical|Promotable|Judgment|Ambiguous] \
  [--origin <provenance>]
```

The `--section` value is normalized to the surface's kebab-case section id
(so `"Behavior Rules"` resolves to `behavior-rules`). The command **fails
closed** (non-zero exit, no entry written) when the surface is unknown or the
section resolves to no template-defined section of that surface — an
unaddressable entry is never stored. `--tier invariant` marks entries emitted
verbatim at every compression setpoint; `--tier` defaults to `compressible`.

### retire

Retire a superseded corpus entry by appending a **retraction row** whose
`retires` field names the id it supersedes, and emit **two** ledger events:
`corpus_entry_appended` for the tombstone row, and `corpus_entry_retired` for
the retirement itself. The corpus has exactly one mutation — append — and no
delete, so before this verb a superseded operator directive bound the invariant
floor permanently and the only escape was hand-editing the append-only store.

```bash
gz content retire <surface> --entry <id> --reason <text> [--attestor <name>] [--origin <provenance>]
```

**Nothing is deleted.** The retired row stays on disk with its provenance
intact; `tier_policy.invariant_entries` simply stops returning it, so a
rendition no longer has to carry its text verbatim.

**Which way the floor moves is a before/after DELTA over invariant-tier
liveness — never a property of what kind of row was named.** Four outcomes are
possible, and the command reports which one occurred:

| Outcome | When | Consequence for a committed rendition |
|---------|------|----------------------------------------|
| unchanged | no invariant entry's liveness moved — the usual case for a routine `compressible` retirement | still satisfies the floor |
| shrank | an invariant entry stopped binding | still SATISFIES it |
| GREW | retiring a tombstone revived the entry that tombstone had retired, **and that revived entry is invariant-tier** (Algebra 6) | may now FAIL it |
| CHANGED | both at once — some revived while others stopped binding | may now FAIL it |

Reading the outcome off the row's tier is the mistake this table exists to
prevent: a `compressible` tombstone over an invariant target GROWS the floor,
and an ordinary `compressible` row moves it not at all.

The command reports which way the floor actually moved, and raises the
floor-coherence warning when it grew. Read that line before deciding whether a
recompose is needed — the older guarantee that retirement "only ever shrinks
the floor" was false for the tombstone case. `retire` never touches a rendered
surface either way.

Retiring a tombstone requires an `--attestor` **only when the entry it revives is
invariant-tier** — then floor-tier liveness moves, even though the tombstone
itself is `compressible`. A tombstone over `compressible` content revives nothing
that binds the floor, needs no attestor, and reports the floor unchanged. The gate
asks what a retirement **does** to the floor, never what tier the row it names
carries.

#### Corpus attestation (OBPI-0.35.0-02)

A retirement that **moves invariant-tier liveness** — the 0-Kelvin floor every
rendition must carry verbatim — requires a named `--attestor`. That covers the
common case of retiring a `tier=invariant` entry directly, and it also covers
retiring a `compressible` **tombstone** whose target is invariant, because that
retirement revives the invariant row (see above). Un-binding or reviving
floor-tier canon is a canon change either way, and `AGENTS.md` § Operator
Doctrine's ATTESTATION GRANULARITY FOR THE CONTENT SURFACE ruling makes
removing an entry attested. Routine retirement that does **not** move
invariant-tier liveness needs no attestor; the attestation guards the floor,
not bookkeeping.

`--reason` is required on **every** tier. It becomes the retraction row's text
and the `corpus_entry_retired` event's `reason`, and both surfaces reject an
empty one — an empty reason fails `gz validate --ledger` and leaves a canon row
that says nothing. A whitespace-only `--attestor` or `--reason` is refused on
every tier: whitespace is not attestation.

A retirement that moves invariant-tier liveness without a named attestor fails
closed, writing nothing:

```console
$ gz content retire AGENTS.md --entry corpus-attestation-2026-06-06T06:20:27.327411+00:00 --reason "probe"
Error: retiring 'corpus-attestation-2026-06-06T06:20:27.327411+00:00' moves the liveness of invariant-tier entry corpus-attestation-2026-06-06T06:20:27.327411+00:00 — the 0-Kelvin floor every rendition must carry verbatim — un-binding floor canon is a canon change, so it requires a named --attestor (AGENTS.md § Operator Doctrine; the ATTESTATION GRANULARITY FOR THE CONTENT SURFACE ruling); nothing written.
  Retry with `gz content retire AGENTS.md --entry corpus-attestation-2026-06-06T06:20:27.327411+00:00 --reason "<why>" --attestor "<your name>"`.
$ echo $?
1
```

#### Fail-closed paths

The command **fails closed** (exit 1, nothing written) when `--entry` names no
row in the surface's corpus, when that row is already retired, or when a
retirement that MOVES invariant-tier liveness carries no named attestor. Double retirement refuses rather than
appending a second retraction, so the ledger carries exactly one retirement
witness per retired entry.

Every refusal carries three-part recovery prose — what failed, the cited rule,
and a runnable next step. Because no `gz` verb lists corpus entries for a
surface, the command answers that question itself rather than naming one:

```console
$ gz content retire AGENTS.md --entry does-not-exist --reason "probe"
Error: no corpus entry 'does-not-exist' in surface 'AGENTS.md'. Retirement targets an existing entry (append-only corpus store, GHI #635); nothing written.
  Live entry ids include: 'corpus-attestation-2026-06-06T06:20:27.327411+00:00', 'corpus-behavior-rules-2026-06-10T07:53:55.264205+00:00', 'corpus-behavior-rules-2026-06-10T08:12:41.048588+00:00' (+52 more).
  Retry with `gz content retire AGENTS.md --entry <id> --reason "<why>" --attestor "<your name>"`.
$ echo $?
1
```

#### Ledger witnesses

A successful retirement emits both events, appended before retired, so a replay
never sees a retirement whose row is not yet witnessed:

| Event | Carries |
|-------|---------|
| `corpus_entry_appended` | the tombstone row's surface, section, entry id, tier |
| `corpus_entry_retired` | the retired entry id, the tombstone row id, the surface, the **retired entry's** tier, the attestor, the reason, and the invariant-liveness delta: `floor_direction` and `floor_moved_ids` |

**`floor_direction` is the fact an auditor needs**, not `tier`. The attestor gate
authorizes on whether the retirement MOVED invariant-tier liveness, and `tier` is
only a proxy for that: a `compressible` tombstone whose target is invariant grows
the floor, so an auditor reading `tier` alone cannot tell an unattested floor
revival from a routine retirement. `floor_direction` is one of `unchanged`,
`shrank`, `grew`, `changed`; `floor_moved_ids` names the exact invariant entries
whose liveness moved. `tier` remains recorded as the retired row's own tier.
`attestor` is empty on a retirement that moves nothing, which is why the schema
declares it without a length floor.

### unown

Un-own a `corpus-owned` section, the one legitimate move that RAISES the
decrease-only unowned-byte ratchet (ADR-0.35.0 § Decision item 3: *"an
undefined reversal path is the one agents invent"*). Same corpus-attestation
shape as `gz content retire`, with one deliberate difference: un-owning a
section is a canon change **every time**, so it never reaches the
unchanged-canon exemption `gz content commit` carries forward a standing
attestation through — `--attestor` and `--reason` are unconditionally
required, never conditional on what moved.

```bash
gz content unown <surface> --section <id> --attestor <name> --reason <text>
gz content unown AGENTS.md --section attestation --attestor "g0" --reason "materialized as prose doc instead"
```

#### Corpus attestation (OBPI-0.35.0-04)

Empty or whitespace-only `--attestor` or `--reason` fails closed (exit 1),
writing nothing — the declaration on disk stays byte-unchanged and no
`section_ownership_unowned` ledger event is emitted (REQ-0.35.0-04-04):

```console
$ gz content unown AGENTS.md --section attestation --attestor "" --reason "probe"
Error: --attestor is empty or whitespace-only.
Why forbidden: un-owning a section is a canon change with the same corpus-attestation shape as `gz content retire` -- it always requires a named attestor and a reason, fail-closed, with no unchanged-canon exemption (REQ-0.35.0-04-04; AGENTS.md § Operator Doctrine). Nothing written.
  Retry with `gz content unown AGENTS.md --section attestation --attestor "<your name>" --reason "<why>"`.
$ echo $?
1
```

Given a non-empty attestor and reason against a `corpus-owned` section, the
section flips to `unowned` and the decrease-only ratchet floor RISES by
exactly that section's measured byte span (REQ-0.35.0-04-05):

```console
$ gz content unown AGENTS.md --section governance-doctrine-surfaces --attestor "g0" --reason "materialized as prose doc instead"
Un-owned section 'governance-doctrine-surfaces' of 'AGENTS.md'. Unowned-byte floor rose from 8637 to 10977 (+2340 B). Attested by g0: materialized as prose doc instead
$ echo $?
0
```

#### Fail-closed paths

Every refusal prints what failed, why it is forbidden (citing the binding
REQ), and a governed next step. **Exit 1** reports a precondition refusal or
recovery of a different pending section; that recovery can write stores, and an
earlier orphan sweep can remove files. Read the diagnostic for what this run
did. **Exit 2** reports a storage failure or an outstanding recovery obligation;
a failed initial durability boundary can refuse before any new transaction
starts. Preserve the reported recovery material and follow the named next step.

| Exit | Refused when |
|------|--------------|
| 1 | `--attestor` or `--reason` is empty or whitespace-only |
| 1 | `<surface>` does not resolve to the identity its ownership declaration declares — a different file, a missing file, or a declaration that does not declare itself |
| 1 | the surface cannot be read, or is not UTF-8 |
| 1 | the ownership declaration is missing, unreadable, malformed, or fails `load_declaration` |
| 1 | `--section` names no id in the declaration |
| 1 | the named section is already `unowned` — there is nothing to raise the floor by |
| 1 | the surface's bytes changed between measurement and the commit, checked before either store is touched |
| 1 | a pending transition for a DIFFERENT section was completed by this run; the requested section is a separate run |
| 2 | the measured source could not be retained, or the journal could not be written |
| 2 | the declaration could not be written, or its durability barrier failed |
| 2 | the ledger witness could not be appended |
| 2 | the surface changed DURING the un-owning, after the declaration and the witness were both durable |
| 2 | a pending journal cannot be proven to continue the declaration on disk |
| 2 | the surface no longer carries the bytes a pending transition was measured against — recovery state E below |
| 2 | the transition was witnessed by an EARLIER run and the source is unreconciled — the state D+E pair; the witness stands, the claim of clean completion does not |
| 2 | THIS transaction's recovery cleanup could not complete — one of its own retained artifacts could not be removed for a reason other than already being gone |
| 2 | the journal's absence could not be made DURABLE after this run removed it — its dependent recovery material is preserved untouched |
| 2 | the journal's absence could not be made DURABLE on an entry that found none — every orphaned artifact is preserved and no new transaction starts |
| 2 | a declaration snapshot consumed under the lock declares a different identity than the transaction's target |

#### Recovery protocol

`gz content unown` updates two stores — a mutable declaration and the
append-only ledger — and neither order is safe alone, so the pending
transition is journalled before either is touched. The atomic writer renames
and *then* syncs the parent directory, so **every** write has a window where
the swap landed and its durability barrier did not. Re-running the same
command is what completes an interrupted move. Below is what each interrupted
state means; every refusal names the state its instruction was derived from.

| State | What is established | Re-running does |
|-------|---------------------|-----------------|
| A | the journal persisted; the declaration is still the predecessor | re-validates the journal against the declaration on disk, writes the successor, witnesses it, clears the journal |
| B | the declaration carries the new floor and its `floor_event_id`; no witness; **durability UNCONFIRMED** | re-establishes the durability barrier BEFORE witnessing or clearing; a persistent barrier failure keeps refusing with the journal retained |
| C | the same shape on disk as B — the two are **indistinguishable by inspection** | the same action; the retry does not guess between them |
| D | the ledger carries the transition's `event_id` | clears the journal and the retained material — **only when the source axis is also reconciled** |
| E | the surface no longer matches the journalled digest | refuses, extracts the retained measured bytes beside the surface, and names the reconciliation |
| **D+E** | the witness is durable AND the source has moved | **refuses** — the witness is preserved unduplicated, every retained artifact is kept, your edit is untouched, and the exit is non-zero |

**Three obligations, established separately (operator ruling, 2026-09-05).** A
transition is *witnessed*, its source is *reconciled*, and its recovery material
is *cleaned* — and establishing one never discharges the others. `E` is an
ORTHOGONAL axis, not a fifth state: a transition in any of `A`–`D` may also have
a moved source, and the `D+E` pair is reported as the pair. A durable witness
does not mean the source is reconciled; an attempted unlink does not mean
cleanup is complete.

Consequences worth stating plainly:

- **Never delete the journal because the ledger carries no `section_ownership_unowned` row.** States B and C both have an absent witness with the declaration already replaced, so an absent witness does not establish that nothing landed — deleting on that signal destroys the only record able to complete the transition.
- **Never hand-edit the ownership declaration.** Its floor must stay witnessed by a real ledger event, and an edited one is refused on the next load.
- **The command never rewrites the surface.** In state E it copies the retained measured bytes to `<surface>.unowning-recovery` and leaves your edit alone.
- **A refusal never hands you a step it cannot keep.** When the measured bytes could not be verified and fully extracted, the numbered reconcile sequence is withheld. A failed extract write may leave an older file or a visible replacement whose durability is unconfirmed; the diagnostic names the failed path and the verified retained source rather than claiming the extract is absent.
- **An unreadable or non-UTF-8 live source does not discard pending recovery.** The early refusal identifies the journal and retained-snapshot path without claiming it has read or verified that snapshot. Before changing the source, save its raw bytes outside the repository, restoring read access first if needed. Verify the retained snapshot's SHA-256 against the journal's `surface_digest` before deliberately restoring it, then retry. If verification fails, preserve the evidence and do not overwrite the source.
- **Recovery ends at the restored measured version and a successful retry.** Keep newer edits saved outside the repository. Un-owning another section adds the same span to the floor and the live unowned total, so it cannot create headroom for an oversized edit in an already-unowned section.

```console
$ gz content unown Doc.md --section alpha-section --attestor "g0" --reason "probe"
Error: the un-owning of section 'alpha-section' of 'Doc.md' was witnessed by an earlier run, but the surface no longer carries the bytes its floor was measured against: its bytes changed.
Why forbidden: THREE OBLIGATIONS ARE SEPARATE HERE and exactly one is discharged -- transition witnessed; source reconciliation pending; recovery cleanup pending. THE STORES ARE IN § Recovery Protocol state D and the SOURCE IS IN state E -- the two are orthogonal axes, and this exit is the pair. THE TRANSITION DID LAND: the declaration carries the new floor and the ledger carries its witness, and neither is retracted -- an append-only witness is a truthful record of what was committed. But the floor was measured against the surface as it was journalled, so the committed declaration may record a byte span the surface no longer has, and `load_declaration` fails closed while the live span exceeds the floor (REQ-0.35.0-04-05). A durable witness does NOT establish that the source was reconciled, so what is refused here is the claim that this completed cleanly. The journal is RETAINED at '.../.gzkit/ownership/Doc.md.json.journal'. Your edit to the surface is untouched and was NOT reverted.
  The bytes this transition measured are extracted to '.../Doc.md.unowning-recovery', and the immutable original is retained at '.../.gzkit/ownership/Doc.md.json.journal.source'. Reconcile in this order, which preserves your edit and ends with a declaration `load_declaration` accepts: 1. save your current work -- copy '.../Doc.md' to a path OUTSIDE this repository; those bytes stay yours and nothing below reads them; 2. diff that copy against '.../Doc.md.unowning-recovery' to see what moved; 3. restore the measured bytes over '.../Doc.md'; 4. re-run the same command, which clears the journal and the retained material once the surface matches what was measured. Your saved copy is untouched by every step above. RE-APPLYING IT IS A SEPARATE DECISION about the coverage claim and is never part of this recovery: an edit that grows an unowned section past the recorded floor is still refused. Un-owning another section increases the floor and live unowned span equally, so it does not create headroom for that edit. Keep the saved copy outside the repository while deciding how to revise it within the ratchet. Do NOT delete the journal and do NOT hand-edit the ownership declaration -- its floor must stay witnessed by a real ledger event, and an edited one is refused on the next load.
$ echo $?
2
```

Captured against a small fixture surface by running the command; project-root-absolute
paths are elided to `...`. This is the **D+E pair** — the transition was witnessed by an
earlier run and the source then moved — which is the state that previously reported clean
success and destroyed the recovery material.

#### Recovery artifacts

An interrupted run leaves these behind. They are cleared together once the
transition is complete AND its source is reconciled — cleanup is its own
obligation, and it is bounded by a durability barrier: the journal's absence is
made durable BEFORE any file that depends on it is deleted or reused, and a
barrier that cannot be established preserves everything and refuses.

An unsupported or invalid required directory sync (`EINVAL`, `ENOSYS`,
`ENOTSUP`, or `EOPNOTSUPP`) also preserves dependent recovery files and exits 2,
including on a fresh entry or a retry that finds no journal. No new transaction
starts past that failed boundary. The diagnostic names the attempted location
and error; the errno alone does not identify a particular filesystem. Repeating
under unchanged conditions cannot establish durability: preserve the recovery
material and use an environment where the required directory sync succeeds
before retrying. Ordinary transient storage faults retain their repair-and-retry
guidance. Equivalent Windows directory durability remains unproved; the current
Windows helper returns without establishing this guarantee.

Past that boundary the two kinds of failure part company. A removal failure
among **this transaction's own** material keeps what remains and reports the
storage fault rather than reporting success. A removal failure on **unrelated
orphan residue** — material that outlived some earlier episode's journal —
**warns and lets fresh work proceed**, because blocking a new transaction on an
old leftover reports a fault the new run did not cause. The warning stays
attached to the orphan through finalization, so the same leftover is never
re-reported as the new transaction's cleanup failing. A warning buys no
shortcut: the declaration is still validated and the new transaction's own
recovery snapshot is still persisted.

A directory-listing failure leaves its staging-file family **unknown**, not
empty. The diagnostic names the directory, literal filename family, and storage
error. Current-transaction cleanup remains non-success. A journal-absent entry
may warn and continue, but unknown files cannot be treated as an observed list
of old leftovers exempt from the new transaction's cleanup. Restore directory
read access and storage health, then retry the inspection.

| Path | Holds |
|------|-------|
| `.gzkit/ownership/<surface>.json.journal` | the pending transition — both floors, the section, the attestor, the reason, the deterministic `event_id`, the parent it chains from, and the serialized successor declaration |
| `.gzkit/ownership/<surface>.json.journal.source` | the MEASURED SOURCE BYTES, immutable for the life of the journal. A digest names the bytes recovery needs; only the bytes supply them |
| `<surface>.unowning-recovery` | written by a state-E refusal, beside the surface, for you to diff and restore from |
| `.<name>.<random>.tmp` beside any of the above | the atomic writer's staging file. An interruption mid-write leaves one holding the MEASURED SOURCE BYTES; recovery sweeps them, and `.gitignore` covers the whole family — final and staging, at every depth, because a surface does not only live at the repository root |

The retained source is recovery material, never a second copy of canon —
nothing loads from it, and the source surface is never rewritten from it.

#### Ledger witnesses

A successful raise emits exactly one `section_ownership_unowned` event, after
the declaration write succeeds:

| Event | Carries |
|-------|---------|
| `section_ownership_unowned` | the surface, the section id, the digest of the complete section map that landed, the prior and new `unowned_byte_floor`, the attestor, and the reason |

The event `id` is DETERMINISTIC — derived from the transition's own content and
the floor it chains from — so a retry re-mints the same id and completing an
interrupted append is idempotent by construction:

```console
$ tail -1 .gzkit/ledger.jsonl
{"schema":"gzkit.ledger.v1","event":"section_ownership_unowned","id":"section-ownership-unowned-Doc.md-alpha-section-ff1301bc5136427b","ts":"2026-09-05T10:01:23.556123+00:00","surface":"Doc.md","section":"alpha-section","sections_digest":"9b85bce39e25102c6cc439ef0ad84664","prior_unowned_byte_floor":26,"new_unowned_byte_floor":63,"attestor":"g0","reason":"materialized as prose doc instead"}
```

### reconcile-retirements

Append a Layer-2 witness for corpus retirements that have none. This is the
repair arm of `gz validate --corpus-retirement-witness` (GHI #885, GHI #878).

```
gz content reconcile-retirements <surface> [--reason <text>] [--dry-run]
```

A retraction row **is** a canon change: `Corpus.retired_ids()` folds the on-disk
pointer and the target leaves the effective corpus. Two paths leave that change
with no ledger witness — a row appended by hand, so `gz content retire` never
runs (GHI #885), or the verb dying between its corpus write and its ledger
appends (GHI #878). Both leave the same signature, and this verb repairs both.

**It emits `corpus_retirement_reconciled`, never `corpus_entry_retired`.** That
distinction is the point. Backfilling the governed type would stamp today's
timestamp — and, on the invariant floor, an attestor — onto a procedure nobody
performed, which `AGENTS.md` § Attestation calls a fabricated receipt.
Re-running the governed verb is not available either: `retire` fails closed on
an already-retired id. So the only honest record is a different sentence — *a
tombstone was found without a witness and accounted for on this date* — and that
is the only sentence this verb writes. Because the two types stay separate, an
auditor reading Layer 2 can still tell a governed retirement from a reconciled
one long afterwards.

**Idempotent.** It emits only for tombstones the witness gate still reports, so
a second run over a reconciled surface writes nothing and exits 0.

Observed on the gzkit repository, 2026-08-26, repairing the seven rows GHI #885
found (elided to two for length):

```
$ gz content reconcile-retirements AGENTS.md --dry-run
AGENTS.md: 7 unwitnessed retirement(s) would be reconciled:
  corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:19.779516+00:00
    via row corpus-retraction-...-2026-08-22T20:21:54.365168+00:00  origin='GHI #862; operator ruling 2026-08-22'
  ...

$ gz content reconcile-retirements AGENTS.md
reconciled corpus-operator-doctrine-verbatim-canon-2026-06-19T22:54:19.779516+00:00
...

AGENTS.md: 7 reconciled, 0 still unwitnessed.
```

The retraction row's `origin` prose is carried onto the event: it is the only
surviving forensic difference between a governed and a hand-written tombstone,
so the repair preserves it rather than overwriting it with its own provenance.

Exit 0 when the surface is fully witnessed (before or after the run), 1 when the
surface has no corpus store, 3 when a row selected for repair survives its own
repair — a state that means the event did not bind to the subject the gate
reads, and is reported loudly rather than as a clean exit over a still-red gate.

### compose

Validate and stage a **candidate rendition** from the corpus. This is the
**compress** stage of the ADR-0.0.37 CMS pipeline
(`corpus → compress → rendition → playback`): the agent wielding the
`gz-content-compose` skill supplies the candidate text; the tool validates
invariant-tier verbatim preservation, computes per-tier byte evidence, writes
the candidate to `.gzkit/renditions/<surface>/<consumer>.candidate.md`, and
emits a `composition_candidate_emitted` ledger event.

**`compose` is deterministic** — NO LLM call, NO network I/O. The
drop/combine/rewrite compression judgment is the agent's.
**`compose` NEVER writes a rendered surface** (`AGENTS.md`, `CLAUDE.md`,
or any mirror) — only the candidate artifact and ledger change.

```bash
gz content compose <surface> --consumer <vendor> --candidate <file>
gz content compose AGENTS.md --consumer root --candidate /tmp/candidate.md
cat /tmp/candidate.md | gz content compose AGENTS.md --consumer root
```

The command **fails closed** (non-zero exit, no candidate written) when:
- the corpus store for `<surface>` does not exist,
- the `(surface, consumer)` setpoint is undeclared in `data/vendor-manifest.json`, or
- the candidate drops or rewrites any `tier: invariant` corpus entry (0-Kelvin floor).

### commit

Promote a staged **candidate** to the durable **committed rendition** under
operator attestation. This is the governed candidate→committed seam of the
ADR-0.0.37 CMS pipeline: `compose` stages `<consumer>.candidate.md`; `commit`
writes `<consumer>.md` AND freezes the corpus content-fingerprint in a
provenance sidecar `<consumer>.corpus.json`, then emits a `rendition_committed`
ledger event.

**`commit` carries the corpus attestation (NOT Gate 5)** — and the attestation
attaches to the **canon change**, never to this Layer-3 re-render. `--attestor`
and `--attestation-text` **fail closed when empty only if the corpus moved**
since this consumer's last committed rendition; a re-render of **unchanged
canon** needs no attestation and carries the standing one forward (GHI #821).
The discriminator is the corpus fingerprint the sidecar already froze. A first
commit — no sidecar — is always attested: an absent sidecar is not evidence that
canon is unchanged. The operator's verbatim `--attestation-text` IS the corpus
attestation (mirrors `gz obpi repudiate`). The frozen fingerprint is exactly what
`gz validate --rendition-freshness` compares the live corpus against: when the
corpus drifts from the committed rendition, the freshness gate flags it and the
recovery is to recompose and re-commit.

**`commit` is not the last step.** It writes the *rendition* — playback is the
sole writer of the rendered surface itself, so a canon change is only applied
once `gz agent sync control-surfaces` runs. Until it does,
`gz validate --invariant-coherence` fails closed (exit 3) with the pending diff
as its message: the committed rendition and the played-back `AGENTS.md` disagree.
The command's success output names this next step.

```bash
gz content commit <surface> --consumer <vendor> --attestor "<name>" --attestation-text "<verbatim>"
gz content commit AGENTS.md --consumer root \
  --attestor "g0" --attestation-text "attest completed"

# Re-render of unchanged canon (a trim, a recompose): no attestation needed.
gz content commit AGENTS.md --consumer root
```

The command **fails closed** (non-zero exit, nothing written) when:
- `--attestor` or `--attestation-text` is empty or whitespace **and** the corpus
  fingerprint differs from this consumer's committed sidecar, or no sidecar exists,
- no staged candidate exists for `(surface, consumer)`, or
- no corpus store exists for `<surface>` (nothing to fingerprint).

### advise-rendition

Record an advisory **information-retained-per-byte** verdict for a candidate
rendition. This is the **advisor-QC** stage of the ADR-0.0.37 CMS pipeline
(`corpus → compress → advisor-QC → operator attest → committed rendition → playback`):
the agent wielding the `gz-advisor-qc` skill judges how much information the
candidate retains per byte, and records that verdict as an ARB receipt the
operator cites at Gate 5.

**`advise-rendition` is deterministic** — NO LLM call, NO network I/O. The
LLM-as-judge read is the agent's; the tool validates the verdict shape
(explanation-before-verdict), writes the `arb-step-judge-<hash>` ARB receipt,
and emits a `rendition_advisor_verdict` ledger event.

**`advise-rendition` is advisory, never gating** (ADR-0.0.39 Evidentiary
invariant): ANY score is recorded and the command exits 0 — a low retention
score is evidence for the operator, never a fail-closed gate.

```bash
gz content advise-rendition <surface> [--consumer <vendor>] --score <0.0-1.0> --explanation "<reasoning>"
gz content advise-rendition AGENTS.md --consumer root --score 0.94 \
  --explanation "All Mechanical bullets retained; two Promotable bullets combined without information loss."
```

The command **fails closed** (non-zero exit, no receipt written) only when the
`--explanation` is empty or whitespace — a structurally malformed verdict. The
verdict value itself is never the fail-closed trigger.

## Options

| Flag | Applies To | Description |
|------|-----------|-------------|
| `--as <type>` | import, show, render, edit | Content type name (required for these subcommands) |
| `--type <type>` | list | Filter list output to a single registered type |
| `--json` | list, show | Emit JSON to stdout instead of human-readable prose |
| `--write <path>` | import | Write re-rendered canonical form to this path |
| `--vendor <vendor>` | render, edit | Target vendor template for re-rendering (default: `claude`) |
| `--section <id>` | remember | Target section id or title; normalized to the surface's kebab-case Pillar id (required) |
| `--text <text>` | remember | The entry prose to remember (required) |
| `--tier <tier>` | remember | `invariant` (verbatim at every setpoint) or `compressible` (default) |
| `--classification <c>` | remember | Advisory-scorecard class: `Mechanical`/`Promotable`/`Judgment`/`Ambiguous` (default `Ambiguous`) |
| `--origin <provenance>` | remember, retire | HOW the capture/retirement arrived, e.g. a GHI or session id (default `cli:content-remember`/`cli:content-retire`) |
| `--witness <who>` | remember | WHO vouches for the entry. Recorded provenance, never a gate — capture is never blocked for want of one (GHI #821) |
| `--entry <id>` | retire | Id of the corpus entry to retire (required) |
| `--reason <text>` | retire | Why the entry is superseded; becomes the retraction row's text (required on every tier) |
| `--consumer <vendor>` | compose, commit, advise-rendition | Target vendor consumer (e.g. `codex`, `claude`); optional for advise-rendition (surface-wide when omitted) |
| `--candidate <file>` | compose | Path to the candidate rendition file (reads from stdin when omitted) |
| `--attestor <name>` | retire, commit | Operator retiring (retire) or attesting the corpus delta this promotion renders (commit); empty fails closed **only when** the retirement moves invariant-tier liveness (retire) or the corpus moved since the last commit (commit) |
| `--attestation-text <text>` | commit | Operator's verbatim corpus-attestation token; same conditional requirement as `--attestor` |
| `--score <float>` | advise-rendition | Information-retained-per-byte verdict value; advisory, never gates (required) |
| `--explanation <text>` | advise-rendition | The advisor's reasoning, recorded before the verdict; empty value fails closed (required) |
| `--quiet`, `-q` | global | Suppress non-error output |
| `--verbose`, `-v` | global | Enable verbose output |
| `--debug` | global | Enable debug mode with full tracebacks |
| `--help`, `-h` | global | Show help and exit |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (unknown type, missing `$EDITOR`, parse error, validation error, missing file) |
| 2 | System/IO error (filesystem unreadable, atomic-replace failed) |
| 3 | Policy breach (reserved; not currently emitted by `gz content`) |

## Examples

```bash
# Enumerate registered content types (human-readable table)
uv run gz content list

# Filter to a single type
uv run gz content list --type Rule

# Machine-readable form
uv run gz content list --json

# Inspect a rule file (prose summary)
uv run gz content show .gzkit/rules/tests.md --as Rule

# Machine-readable inspection
uv run gz content show .gzkit/rules/tests.md --as Rule --json

# Render the canonical form of a file to stdout
uv run gz content render AGENTS.md --as AgentContract

# Render against a specific vendor template
uv run gz content render .gzkit/rules/tests.md --as Rule --vendor claude

# Edit a rule with validation guard (invalid edits never land)
EDITOR=vim uv run gz content edit .gzkit/rules/tests.md --as Rule

# Reverse-parse a hand-authored file and write canonical output (OBPI-0.0.34-03)
uv run gz content import AGENTS.md --as AgentContract --write /tmp/agents-canonical.md

# Capture a compressible note into the AGENTS.md corpus (never touches AGENTS.md itself)
uv run gz content remember AGENTS.md --section "Behavior Rules" \
  --text "Prefer stdlib JSONL for append-only stores." --tier compressible

# The append landed in the corpus store, not the rendered surface:
#   .gzkit/corpus/AGENTS.md.jsonl  ← new entry
#   AGENTS.md                       ← byte-unchanged

# Record an advisory info-retained-per-byte verdict for a candidate rendition (advisory, never gating)
uv run gz content advise-rendition AGENTS.md --consumer root --score 0.94 \
  --explanation "All Mechanical bullets retained; two Promotable bullets combined without information loss."

# The verdict is witnessed in the ledger and written as an ARB receipt cited at Gate 5:
grep "rendition_advisor_verdict" .gzkit/ledger.jsonl
```

## Files

| Path | Role |
|------|------|
| `src/gzkit/content/models/` | Canonical Pydantic model definitions (`AgentContract`, `Rule`, `Skill`, …) |
| `src/gzkit/content/templates/` | Jinja2 templates per (content type × vendor) |
| `src/gzkit/content/render.py` | Render pipeline (OBPI-0.0.34-02) |
| `src/gzkit/content/parse.py` | Reverse-parse pipeline (OBPI-0.0.34-03) |
| `src/gzkit/commands/content/` | Operator CLI surface (this OBPI-0.0.34-04) |
| `src/gzkit/content/corpus_store.py` | Append-only per-surface corpus persistence (`remember`, OBPI-0.0.37-19) |
| `.gzkit/corpus/<surface>.jsonl` | Append-only corpus store written by `gz content remember` |
| `src/gzkit/content/advisor_qc.py` | Deterministic advisor-QC verdict-record engine (`advise-rendition`, OBPI-0.0.37-24) |
| `artifacts/receipts/arb-step-judge-<hash>.json` | Advisor-QC verdict ARB receipt cited at Gate 5 |

## Related

- ADR-0.0.34 — Agent Control Surface Rendering Substrate (`docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/`)
- Doctrine — `docs/governance/agent-control-surface-rendering-substrate.md`
- OBPI-0.0.34-01 — Content model registry generalization
- OBPI-0.0.34-02 — Rendering pipeline
- OBPI-0.0.34-03 — Reverse-parse migration tooling
- OBPI-0.0.34-04 — Authoring CLI (this manpage)
- OBPI-0.0.34-05 — Light TUI affordances (forthcoming)
- OBPI-0.0.34-06 — Validation hooks (forthcoming)
- ADR-0.0.37 — Constitutional Invariant Composition; the `remember` corpus-capture write path (OBPI-0.0.37-19)
- `.gzkit/skills/gz-content-remember/SKILL.md` — the capture skill that wields `gz content remember`
