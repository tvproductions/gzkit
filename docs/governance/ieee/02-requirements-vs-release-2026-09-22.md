<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# 02 — Requirements engineering versus release management

> **This is a dated record.** Every figure below was observed on the tree at
> `be663409a64a12b501c25bdf9e919606aa0b9937`. The values are ILLUSTRATIVE, never
> authoritative (`AGENTS.md` § Governance doctrine surfaces). The authority is
> the script: re-run
> [`02-requirements-vs-release-evidence/measure.py`](02-requirements-vs-release-evidence/measure.py)
> rather than trusting a number transcribed here. It carries no literals from
> this date, so it reports whatever tree it is run against.

**Origin.** Operator, 2026-09-22: *"the original motivation came more from my
dissatisfaction with how I have been conflating requirements engineering with
release management."* Piece 01 found that requirements have no durable owner.
This piece finds something more specific: **they have the wrong owner.**

---

## The finding

gzkit writes three different things in one notation. `ADR-0.35.0` is a decision
record wearing a release number. `REQ-0.35.0-04-01` is a requirement whose
identity contains that release number. And `v0.34.7` is an actual shipped
release. The first two are engineering information; the third is a
configuration item. They share a semver namespace and they have already
diverged.

```
shipped tags : 0.30.0 … 0.33.3  0.34.0  0.34.1 … 0.34.7
ADR ids      : 0.30.0 … 0.33.0  0.34.0  0.35.0  0.36.0  0.37.0  0.39.0
```

Seven releases (`0.34.1`–`0.34.7`) have no ADR. Four ADRs (`0.35.0`–`0.37.0`,
`0.39.0`) have no release. `0.29.0` shipped as a release but exists as no ADR;
`0.38.0` exists as neither. The two lines share a notation and mean different
things, which is the proof they were never the same thing.

The coupling is not decorative. It is eight lines of code.

## The mechanism

`src/gzkit/commands/version_sync.py:17-20` pulls a version out of an
identifier **string**:

```python
def _extract_adr_version(adr_id: str) -> str | None:
    """Extract the semver portion from an ADR ID like ``ADR-0.18.0-slug``."""
    m = re.match(r"^ADR-(\d+\.\d+\.\d+)", adr_id)
    return m.group(1) if m else None
```

`version_sync.py:283-290` compares it to the shipped package version, and
`closeout.py:499-506` acts on the answer:

```python
needs_bump = _parse_semver_tuple(adr_version) > _parse_semver_tuple(current)
...
if needs_bump and adr_ver is not None:
    version_updated = sync_project_version(project_root, adr_ver)
```

`sync_project_version` then rewrites `pyproject.toml`, `src/gzkit/__init__.py`
and the README badge (`version_sync.py:57-87`), and writes
`docs/releases/RELEASE-v{version}.md` naming the driving ADR.

**A decision record's filename is the product's release version.** There is no
`kind` guard: `grep -n 'kind\|foundation' src/gzkit/commands/version_sync.py`
returns nothing. Foundation ADRs escape only by arithmetic accident — `(0,0,73)
> (0,34,7)` is false. Close out a foundation ADR numbered above the current
release and it bumps the package.

## What the semver actually means, per layer

The conflation is not uniform, and the distinction matters for any future
repair. Measured by reading every consumer that decomposes an identifier:

| Layer | What the embedded semver does | Verdict |
|---|---|---|
| **REQ** `REQ-0.35.0-04-01` | A **foreign key**, never a version. Every decomposing site resolves it to an artifact: `req_kind_fence.py:162-169` globs `docs/design/adr/**/ADR-{semver}-*.md`; `traceability.py:680` builds `f"ADR-{parsed.semver}"` as a rollup bucket; `commands/task.py:464-470` hands the bare semver to the ledger's short-form resolver. No code compares a REQ semver to the package version | **Notational conflation.** It looks like a release number and functions as a join path |
| **ADR** `ADR-0.35.0-slug` | An **actual release number**, mechanically driving the package version at `version_sync.py:289` | **Semantic conflation.** This is the real seam |
| **Release** `v0.34.7` | The product version | Correct, but see § *Ceremony without approval* |

So the ADR layer is where requirements engineering and release management are
genuinely fused. REQ ids inherit the coupling transitively: they are bound to a
release-numbered parent, so a release-sequencing decision rewrites requirement
identity even though the requirement's own semver was never a version.

That inheritance is not theoretical. **75 of 165 `artifact_renamed` ledger
events carry `reason: semver_minor_sequence_migration`** — identifiers rewritten
because the release sequence changed.

## What the standards say instead

The corpus separates three counters that gzkit writes as one.

**A requirement carries an immutable identity and its own revision.** ISO/IEC/IEEE
29148:2018 § 5.2.8.2 lists eight requirement attributes. *Identification*:
"Once assigned, the identification is unique - it is never changed (even if the
identified requirement changes) nor is it reused." *Version Number* is
explicitly the requirement's own revision counter — the clause gives its purpose
as ensuring "the correct version of the requirement is being implemented" and
providing "an indication of the volatility of the requirement," with high churn
read as a project risk signal. **There is no product-version field anywhere in
the attribute list.**

gzkit inverted this exactly: it put the product's version *inside the identity*,
and carries no requirement revision counter at all.

**A version belongs to a configuration item, not to a requirement.** 12207:2026
§ 3.1.12: a baseline is a "formally approved version of a configuration item…
formally designated and fixed at a specific time." 24765:2017 § 3.3382: a
release is a "particular version of a configuration item."

**Requirements are not configuration items — they are information placed under
configuration control.** This precision matters and is easy to get wrong.
15288:2023 § 6.3.5.3 b) 1) NOTE 5 — *a NOTE, not normative* — says items under CM
"usually include requirements." 12207's parallel text is an EXAMPLE naming the
*specification*, not the requirement. 29148 § 6.6.2.2.2 is decisive and says
something different again: requirements "are identified as **information items**
for configuration control." CI-hood carries hardware/software identity;
baselining carries version fixing. They are not the same act.

**Identity, revision and release are separate facets, not one encoded string.**
24748-3:2020 § 6.3.5.4 (guidance): the identification scheme "should include the
version, revision and release status of each configuration item" — three fields
per item. **No clause anywhere prohibits a dual-purpose identifier.** I searched
the corpus for one and there is none; the principle is constructed from the
separation of attributes, not from a prohibition. Reporting it as a rule would
be a paraphrase.

**A correction to my own earlier citation.** I said in conversation that 29148
§ 6.6 carries "The requirements shall be configuration controlled." It does not.
That sentence is at **§ 6.4.3.5** (Manage requirements). The § 6.6 sentence is
§ 6.6.2.2.3, and it is weaker and differently scoped: "Requirements **shall** be
configuration managed, in accordance with project and organization configuration
management processes." Both are `shall`; they are not interchangeable.

**And a correction to piece 01.** Its § 9 filed 29148 § 6.6.2.2.2's four-baseline
scheme under *do not adopt — acquisition machinery*. That was too coarse, and it
discarded the answer to the operator's question. The split is:

- **Contractual, droppable** — the functional baseline as "a basis of agreement
  between parties"; the per-baseline "levels of authority needed for change
  approval"; 12207 § 6.3.5.3 b) 4)'s "acquirer and supplier agreement."
- **Transferable, and the part that answers the question** — that there are
  distinct fixed points at distinct levels of abstraction (intent, allocation,
  in-flight state, as-completed); that the allocated baseline is "reviewed and
  **versioned**", so versioning is an attribute of the *baseline*, not of the
  release; and that the **developmental baseline exists precisely to hold
  evolving state without acquirer ceremony**.

Piece 01's row is withdrawn.

---

## What the coupling has cost

**About 5% of this repository's recorded defect work.** Two independent measures
converge: **53 of 1,075 GHIs (4.9%)** by strict classification with every body
read, and **~49 of 1,137 distinct `fix(...)` commits (4.3%)**. Admitting 17
adjacent issues raises the GHI share to 6.5%. The figure counts each issue once
regardless of size, which flatters it — the class contains a 316-file demotion
sweep and a 2,600-line zero-behaviour renumber.

The 53 fall into four families, and the family boundaries are the mechanism
boundaries:

| Family | n | Mechanism | Recurrence |
|---|---|---|---|
| **A — bare semver vs. slugged id** | 13 | The id is `semver + slug`, so a writer emitting only the semver half creates a second artifact | Declared closed and recurred four times: `#279 → #305 → #344 → #468 → #494`, the last self-labelled *"regression #4 of the GHI #279 class"* |
| **B — short-form vs. full-slug** | 22 | The id is `semver + index + slug`, so readers key on a prefix and miss | GHI #187 calls itself *"the seventh instance of the short-form-vs-full-slug defect class"* and tabulates six priors |
| **C — a renamed id read as a vanished one** | 10 | Rename chains must be folded to resolve an identifier | GHI #557 exists to fold *cyclical* chains |
| **D — semver as sequence position** | 8 | Slot allocation, burned numbers, grammar width | `#871` is still **open** |

Three standing costs the percentage does not capture:

1. **Standing code.** 11 modules, **1,363 lines in `src/` plus 1,680 lines of
   dedicated tests**, of which ~880 src lines are fully dead if identifiers never
   change — `obpi_park_backfill.py` (294), `obpi_slug_rename.py` (142),
   `register.py`'s hand-curated `SEMVER_ID_RENAMES` table and `gz migrate-semver`
   (194), `ledger.py`'s `canonicalize_id` / `resolve_artifact_id` (133),
   `obpi_lifecycle.fold_renames` (56). Plus **62 module-level compiled regexes
   across 53 modules** re-spelling one grammar: the prefix `ADR-\d+\.\d+\.\d+`
   alone is independently spelled in **22 places**.
2. **Standing runtime.** GHI #1080 measures `canonicalize_id` at **55 seconds of
   every `gz check`**. The issue blames missing caching; the function exists only
   to fold rename chains. *(Interpretation, flagged: that is the price of
   keeping identifiers renameable.)*
3. **Standing namespace corruption.** **17 feature semver slots have carried two
   different pieces of work** — a direct violation of 29148 § 5.2.8.2's "never
   changed… nor is it reused." **122 work items have carried more than one
   identifier**, consuming 272 identifiers for 122 things. The worst chain is the
   chores system at **nine identifiers for one feature**:

```
ADR-0.2.1-pool.gz-chores-system  →  ADR-0.6.0-pool.gz-chores-system
  →  ADR-pool.gz-chores-system   →  ADR-0.8.0-gz-chores-system        [5 ids]
OBPI-0.2.1-01-chores-system-core →  OBPI-0.6.0-01-chores-system-core
  →  OBPI-0.8.0-01-chores-system-core → OBPI-0.8.0-01-chores-registry [4 ids]
```

The `0.29.0` and `0.38.0` gaps are **burned slots, not skips**: `0.29.0` held
`task-management-system-absorption`, was demoted, reallocated to
`precise-auth-boundaries`, and demoted again under GHI #686 — *"orphan feature
ADR occupies burned release number v0.29.0."* The `0.40.0–0.52.0` block was
demoted wholesale, and the insights ledger records the consequence: **three
separate sessions independently re-derived it as a suspected defect** because
`gz adr report` stops at 0.39.0 while ledger-derived consumers still surface the
higher ids.

### A correction to the framing

The operator's intuition — that release sequencing rewrites requirement identity
— is **half right, and the half that is wrong matters**.

Measured: of 61 git-detected brief renames, only **5 changed a REQ prefix**, and
all five are *foundation* ADRs whose ids are nominal integers, not semver. Those
renumbers are coupled to **decomposition**, not to release.

What release-scope decisions actually do to requirements is worse than renaming
them: **they delete them.** Pool demotion collapses an ADR directory into one
flat file, and the briefs go with it. Commit `993a16c11` (2026-05-23, "demote 25
Pending feature ADRs to pool") destroyed **1,180 feature-semver REQ identifiers
in a single operation**. Across sampled history, **1,676 REQ identifiers existed
and no longer do** — a lower bound.

So the accurate statement is: *a release-scope decision destroys requirement
specifications, and a decomposition decision renumbers them.* Only the second is
a rename, and it is the smaller effect.

## The traceability casualties

Silent breakage is **small and real**. 17 feature-tag REQ ids reference no brief
on disk, in three groups:

| n | Ids | Cause |
|---|---|---|
| 12 | `REQ-0.0.98-*` | Synthetic fixtures — foundation ADRs stop at `0.0.74`, so `ADR-0.0.98` never existed |
| 1 | `REQ-0.0.32-06-10` | **Off-by-one.** `OBPI-0.0.32-06-t0-smoke-test.md` declares `-01` through `-09`. `features/distribution_invariant.feature:35` tags `-10`, and `features/steps/distribution_invariant_steps.py:16` repeats it |
| 4 | `REQ-0.44.0-01-01…04` | **The thesis, demonstrated.** `ADR-0.44.0-vendor-alignment-codex` was created 2026-04-26, demoted to pool 2026-05-23, and its OBPIs parked 2026-07-22. `features/agent_sync.feature` still tags four scenarios against requirements whose brief was deleted |

`@covers` annotations in `tests/` are clean: their dangling ids are all synthetic
fixtures (`9.9.9`, `1.2.3`, `0.0.99`…). The ledger's 300 REQ citations are clean.

*Reconciling prose with the script:* `measure.py` counts citations from both
surfaces and reports **31 orphan citations — 26 synthetic fixtures, 5
casualties**. The 17 above are the `features/` share; `@covers` contributes the
other 14, all fixtures. The classifier took three attempts to get right, and the
failure mode is worth recording because it is the same one this piece is about:
judging "fixture" by absence from disk alone **misclassifies a demoted ADR as a
fixture**, hiding the `0.44.0` group entirely. The script now reads
`adr_created` and `artifact_renamed` event ids — never a raw line scan, because
tests write fixture payloads into the ledger and a substring match reports ids
like `ADR-9.9.9` that no ADR ever bore.

**None of this is caught.** `gz validate --behave-req-tags` verifies that every
BEHAVIOR REQ appears *somewhere*; it never verifies that a tag names a REQ that
exists. The direction is unchecked, so a scenario can claim to verify a
requirement that a release-scope decision deleted two months earlier, and the
gate stays green.

There is a second, larger breakage that is not a dangling citation: **165 parked
OBPI identifiers sit on 12 feature semver slots that a different live ADR now
occupies.** GHI #826 records the effect verbatim — `gz state --json` lists
`OBPI-0.35.0-01-arb-ruff` (parked, belonging to the demoted
`pre-commit-hook-absorption`) beside `OBPI-0.35.0-01-corpus-tombstone-schema-and-fold`
(live, belonging to `canon-entry-corpus-landing`). Same prefix, different work,
nothing distinguishing them.

## gzkit already built a baseline — and pointed it somewhere else

This is the most useful finding in the piece.

12207:2026 § 3.1.12 decomposes into four testable properties: it identifies a
configuration item, carries formal approval by a named authority, is fixed at a
specific time, and fixes a *set* whose membership is recorded. Measured against
every candidate in the repository:

| Candidate | Verdict |
|---|---|
| **git tags (74)** | **Not a baseline.** `git for-each-ref refs/tags --format='%(objecttype)'` → **73 commit, 1 tag**: 73 of 74 are lightweight refs with no tagger, date, message or signature, created server-side by `gh release create`. A pointer with no approval payload |
| **the ledger** | **Partial — an event log.** Records *that* approval happened, never *what content* was approved. `closeout_initiated` comes closest and enumerates `obpi_files` as **paths, not hashes** |
| **campaign § 5 "1.0 definition"** | **Not a baseline — an acceptance specification for the system**, not for a release. Its gates are prose predicates, two scoped to a census date rather than an artifact set |
| **`distribution_baseline_manifest.json`** | **Partial.** Enumerates 240 files across 5 surfaces with before/after manifest hashes, regenerated 105 times — but the event model has **no attestor field**, and it is regenerated *from on-disk truth*, so it records what **is**, not what was **approved** |
| **shrink-ratchets / grandfather files** | **Not a baseline, argued precisely.** A baseline fixes an approved configuration; a ratchet fixes a *high-water mark of known debt*, and its whole purpose is that the governed thing may still change, monotonically. A baseline expected to change is a bound, not a baseline |
| **ADR `Validated`** | **Not a baseline.** Frontmatter status is Layer 3 — derived, ephemeral, cannot block gates. 81 of 88 ADRs are Validated: near-universal, not selective approval |
| **`rendition_committed` + `<consumer>.corpus.json`** | **The one near-full baseline in the system** |

The rendition mechanism satisfies nearly every clause. `RenditionProvenance`
carries `corpus_fingerprint`, `corpus_entry_count`, `rendition_fingerprint`,
`committed_ts`, `attestor` and `attestation_text`. Approval is **fail-closed when
canon moved**: `commands/content/commit.py:98-117` requires `--attestor` and
`--attestation-text` unless the prior fingerprint is unchanged, in which case the
prior attestation carries forward. Post-commit edits are caught by fingerprint
comparison. A superseded baseline is retained, never deleted.

**It is pointed at the agent contract, not at requirements.**

One precise refutation keeps this honest: `corpus_entry_count: 372` is the **log
length**, not the **membership** — the composed set was 100 entries, a factor of
3.7 apart. The enumerating artifact exists as `ConsumerLineage.entry_ids`, but it
is written only to `<consumer>.candidate.lineage.json` at compose time;
`lineage_path()` — the committed location — **has no writer**, and
`lineage.py:127-129` says so verbatim. So the set is *recoverable by
recomputation* from a pinned digest, not *recorded*. Under § 3.1.12 the
configuration is identified by a hash of its generating history rather than an
enumeration of its items.

Meanwhile requirements are governed by the structural opposite of a baseline:
**continuous reconciliation to current reality**, 805 `brief_reconciled` events,
411 with drift detected, 68 of which widened the allowlist to fit what had
already been touched. The specification is re-fitted to the code.

## Ceremony without approval

If requirements have attestation without a baseline, releases have the mirror
defect: a manifest without attestation.

- **`patch_release.py:142`** declares `operator_approval: str = Field("Approved
  by gz patch release", …)`. `grep -rn 'operator_approval'` returns exactly two
  hits: the declaration, and line 653 writing it into the document under
  `## Operator Approval`. **Nothing ever assigns it**, and **33 of 38 release
  documents carry that identical canned string** — the tool naming itself as
  approver.

  *Stated fairly:* the operator's real approval exists. Their verbatim words
  ("Approved as drafted") are in the git commit and in
  `.gzkit/handoffs/rulings.jsonl:592`. The defect is not an absent human; it is
  that **the release record does not capture the approval it claims to record**,
  so the one artifact a reader would consult for it holds a constant instead.
  That is the same shape as a fabricated receipt id, arrived at by default value
  rather than by intent.
- **The `patch-release` ledger event records the previous tag.** `id=v0.34.7`
  carries `tag=v0.34.6`, consistent across all six recent releases, because
  `patch_release.py:891` reads the tag before the bump.
- **The ledger event is appended before the release exists.** `ledger.append` is
  line 983, `_confirm(...)` is 1012, `_create_gh_release` is 1034.
- **No event records what shipped.** Across all 33 `patch-release` events there
  is no commit SHA, no artifact digest, no captured operator approval, and no
  distinction between a *discovered* and an *approved* GHI — v0.34.7's event
  carries `#918 status: "excluded"` alongside the one shipped GHI.
- **`gz git-sync --apply` writes no ledger event at all.**

IEEE 1012-2024 § 7.5.3 (***shall***) names these as two distinct defects in one
sentence: issues indicate "configuration baselines are not established or
controlled, **or** … the configuration of released items is not controlled."
**gzkit has both**, and they are independent.

## The release record that does exist — and is load-bearing

`RELEASE_NOTES.md` is the surprise of this piece. The expectation going in was
that a 202 KB prose file duplicating an append-only ledger is waste. It is not.

**The ledger cannot reconstruct a release.** Of 67 event types, exactly **one**
carries version information — `patch-release`, 33 rows, **0.19% of 17,030**.
**41 of 74 tags have no ledger release event at all**, 30 of them minor
releases. What *is* reconstructible: the commit range, gate pass/fail with
command and return code, OBPI-level attestation text, receipt ids. What is
**not**: which ADR a release ships (v0.33.0's window contains three ADR ids, two
of them unrelated concurrent work), which GHIs closed, where release boundaries
fall, ADR-level attestation content (the `attested` event is `{id, status, by}`
— no text), and gate magnitude (`gate_checked` carries a return code, not
counts). For **12 tags nothing at all** is reconstructible: v0.25.0–v0.25.11 are
unreachable, orphaned by the 2026-04-19 filter-repo rewrite. **For those twelve,
the release notes are the only surviving record.**

And the file is a validator input, not an output: `release.py:201-203` —
*"Return every version `RELEASE_NOTES.md` declares as shipped"* — derives the
release roster **from the prose** and checks the tag set against it
bidirectionally. Both sets are 74.

**The derivable version is generated and discarded, 74 times out of 74.**
`patch_release.py:682-734` mechanically emits `- **GHI #{n}:** {title}` bullets
bucketed by GitHub label. Measured: `grep -cE '^[[:space:]]*- \*\*GHI #[0-9]+:\*\*'`
over `RELEASE_NOTES.md` returns **0** of 931 bullets. Not one survived. *(Interpretation,
flagged:* the ledger-derivable projection is produced and rejected as
insufficient every single time, which is evidence about what a release record
has to carry, not evidence of waste.*)*

`CHANGELOG.md` sits on the other side of the line and **is** derived: over
v0.34.1–v0.34.7 it cites **145 of 145** qualified GHIs. Its `## [Unreleased]`
section has been empty across 533 commits and ~128 cited GHIs, against a rule
requiring it — `gz validate --changelog` passes because it checks shape only,
and is scoped `explicit`, so it never runs under `gz check`.

**A ruling that lives only here.** `RELEASE_NOTES.md:1226`:

> The release line — not ADR frontmatter — is the source of truth for what
> shipped.

Repo-wide search returns that sentence in exactly one place. **The two-version-line
divergence this piece opens with is not an accident — it is a recorded
operator ruling**, made when `ADR-0.29.0` was dropped to pool to free the
number. That materially changes the reading: the ADR line and the release line
were *deliberately* decoupled at the top, while `version_sync.py:289` kept them
mechanically coupled underneath. **The doctrine and the code disagree, and the
doctrine is the later of the two.**

**The current stall is invisible.** Since v0.34.7 (2026-08-29): **533 commits,
1,938 files, +208,217/−34,032, 1,426 ledger events, 4 OBPI completions, zero ADR
attestations** — all unreleased, with `pyproject.toml` still at `0.34.7`.
`audit_version_release` only checks version↔tag agreement, so no gate can see it.

## What a decoupling would face

Stated as constraints, not as a design. Nothing here proposes a change.

**Consumers.** 71 sites in `src/**/*.py` decompose or construct an identifier —
29 extract the ADR semver, 22 the OBPI index, 14 construct an id, 6 sort by
semver — plus 26 outside `src/`. Twenty sites treat the id as an opaque token
and survive anything that keeps a matchable shape. Only **3 of the 17
non-canonical regex spellings** are bound to the canonical parser by
`tests/test_triangle.py:1521`; the other fourteen are unbound.

**What the REQ semver actually answers**, measured, is five questions: parent-ADR
file location, ledger artifact-id resolution, rollup grouping, TASK-id
derivation, and display order. Any substitute must answer the same five.

**Surfaces that cannot be rewritten.** 583 ledger events citing 300 distinct REQ
ids, append-only and hook-enforced (`hooks/guards.py:198-223` rejects any staged
ledger diff containing a `-` body line), 30 of those rows carrying operator
attestation text that doctrine forbids editing. 43 receipt **filenames** embed
REQ ids — `red_reporter.py:47` builds `run_id = f"arb-red-{req_id}-{uuid4}"` and
writes it as the filename, validated by a schema pattern over the composite. 293
REQ references across 3,836 commit messages. Dated records — a 715-id inventory,
2,336 ids in chore proof logs — are technically writable but are attested
snapshots; editing them falsifies what they witness.

**The existing translation mechanism does not cover REQ.** `Ledger.canonicalize_id`
folds `artifact_renamed` events, of which 119 exist: 117 ADR, 2 OBPI, **zero
REQ**. The static table in `register.py:137` holds 48 ADR and 36 OBPI entries, no
REQ.

**Import-time hard failure.** `traceability.covers` validates REQ existence *at
decoration time* and raises `ValueError` on an unknown id. 4,890 decorators
across 397 files import-fail together if brief ids and test citations diverge for
one commit. `adr_demote.py:230-235` records this happening: demoting one ADR
broke 36 decorators, and the only signal was the suite failing to import.

**Width divergence is live.** `obpi_brief_structure.json:40` requires `\d{2}`;
`core/models.py:202` allows `\d+`; `schemas/ledger.json:853,1938` declares
`req_id` as `{"type":"string","min_length":1}` — **no pattern at all**. Three
authorities, three widths, and the durable record admits any non-empty string.

**One worked precedent exists.** `OBPI-0.2.1-01-chores-system-core` →
`OBPI-0.6.0-01-chores-system-core`: REQ ids were rewritten on disk while three
ledger rows still name the old OBPI id, reconciled only through the rename map.
That is the shape of the residue any REQ decoupling inherits, at roughly 300×
the scale.

## Findings

| # | Finding | Class |
|---|---|---|
| 1 | The ADR identifier is the release version: `_extract_adr_version` regexes a semver out of a filename and `sync_project_version` writes it to `pyproject.toml`, `__init__.py` and the README badge, with **no `kind` guard** | **REFINE** |
| 2 | The REQ semver is a foreign key, not a version — five resolution questions, no comparison to the package version anywhere | **KEEP** (the function), **REFINE** (the notation) |
| 3 | No requirement revision counter exists. 29148 § 5.2.8.2 pairs an **immutable identity** with a **mutable Version Number** whose stated purpose is volatility signalling. gzkit has neither half: identity is mutable, revision absent | **ADD** |
| 4 | No requirements baseline exists. The approve-and-freeze mechanism was built, works, is fail-closed, and is pointed at the agent contract | **ADD** (point it at requirements too) |
| 5 | Requirements are governed by continuous reconciliation — 805 `brief_reconciled`, 411 with drift, 68 widening the allowlist to match what was already touched. This is the structural opposite of a baseline | **REFINE** |
| 6 | 17 feature semver slots have been reused, and 122 work items have carried 272 identifiers between them | **REFINE** |
| 7 | Release ceremony records no approval: `operator_approval` is a Pydantic default nothing assigns; 73 of 74 tags are lightweight; the ledger event carries the previous tag and is appended before the release is created | **REFINE** |
| 8 | No release record in the 15289 Table 3 sense — no event says "this set of artifacts is the approved content of version X" | **ADD** |
| 9 | `--behave-req-tags` checks only one direction, so 17 scenario tags name REQs that do not exist, 4 of them deleted by a pool demotion | **REFINE** |
| 10 | ~880 src lines and 1,680 test lines of rename machinery, 62 regexes across 53 modules, and 55s of every `gz check`, all existing because identifiers are renameable | **REMOVE** (contingent on 1 and 3) |
| 11 | `ADR-pool.feature-adr-semver-discipline.md` — 240 lines, authored 2026-05-28, `status: Pool` — already names all three drift surfaces and quotes *"Doctrine drift is invariant drift."* It has sat unpromoted for four months while the class produced two more commits today | **KEEP** (the diagnosis; the routing is an operator call) |
| 12 | `RELEASE_NOTES.md` is not duplication. It is a validator input (`release.py:201-203` derives the release roster from it), the only surviving record for 12 tags orphaned by the 2026-04-19 filter-repo rewrite, and the sole home of the ruling at `:1226`. The mechanically-derivable version is generated and discarded 74 times out of 74 | **KEEP** |
| 13 | The ledger cannot reconstruct a release: 1 of 67 event types carries version information, 33 rows, 0.19%; 41 of 74 tags have no release event | **ADD** (a release record, per 15289 Table 3) |
| 14 | `RELEASE_NOTES.md:1226` rules the release line authoritative over ADR frontmatter, while `version_sync.py:289` makes the ADR identifier the package version. **Doctrine and code disagree, and the doctrine is the later of the two** | **REFINE** |
| 15 | 533 commits and +208,217 lines sit unreleased since v0.34.7 with zero ADR attestations, and `audit_version_release` checks only version↔tag, so no gate can see the stall | **ADD** (a staleness signal) |

## Bureaucracy filter for this seam

Configuration management is the most over-specified area in the corpus. What to
leave behind:

- **Configuration control boards.** 15288 § 6.3.5.3 a) 1) g) and 12207's
  parallel — both appear in NOTEs and strategy sub-bullets, never as a standalone
  `shall`.
- **Acquirer/supplier agreement to establish a baseline** (12207 § 6.3.5.3 b) 4);
  29148 § 6.6.2.2.2's "basis of agreement between parties" and "levels of
  authority needed for change approval"). The *existence* of distinct baselines
  transfers; the *contractual assignment of change authority* does not.
- **Formal FCA/PCA as ceremonies** with sampling of production units.
- **A separate CM plan document** — 12207 NOTE 5 explicitly allows the strategy
  to live inside an existing plan. The strategy is required; the document is not.
- **Requests for variance / deviation / waiver**, which presuppose an external
  party to waive against.

What transfers, and is small:

1. **A designation act** — say which things are under configuration control
   (12207 § 6.3.5.3 b) 1)). CI-hood is conferred, not intrinsic.
2. **Identity ≠ revision** — immutable identifier plus a separate revision
   counter (29148 § 5.2.8.2).
3. **Facets, not encodings** — 24748-3 § 6.3.5.4: version, revision and release
   status as separate fields per item, rather than one encoded string. *(No
   clause prohibits an encoded identifier; the principle is constructed from the
   separation of attributes.)*
4. **Baselines defined through the life cycle**, with content authored by the
   technical processes and only *formalized* by CM. 12207 § 6.3.5.3 b) 3)
   NOTE 12: baseline content "is developed through the technical processes, but
   is formalised at a point in time through the configuration management
   process." **CM must not be where engineering meaning is decided.**
5. **At least two baseline kinds** — one for agreed intent, one for evolving
   in-flight state under local change authority. This is exactly the
   functional/developmental split, minus the acquirer.
6. **A release record distinct from the requirement record.** 15289 Table 3 makes
   them separate rows with **disjoint owning processes**; the Requirement record
   is the only one of the four not owned by configuration management or
   transition, and its contents list carries **no version and no release field**.
7. **A verifiable chain of evidence** — 32675 § 6.3.5.2 a) (***shall***): "The
   chain of evidence is verifiable from source code baselines through persisted
   derived objects to verifiable baselines", with immutable version IDs
   (§ 6.3.5.3 b) 2)) and a change manifest protected by checksums (c) 6)). This
   is the one-operator substitute for the audit-as-meeting, and gzkit is already
   most of the way there.

## Questions for the operator

1. **Which of the two rulings stands?** `RELEASE_NOTES.md:1226` rules that "the
   release line — not ADR frontmatter — is the source of truth for what
   shipped." `version_sync.py:289` does the opposite: it makes an ADR
   identifier the package version. The prose decoupled them; the code never
   did. Either the code owes a change, or the ruling owes a retraction. The
   missing `kind` guard is a latent defect under either answer.
2. **Should `ADR-pool.feature-adr-semver-discipline` be promoted, withdrawn, or
   superseded by this piece?** It has carried the diagnosis for four months
   while the defect class stayed open.
3. **Does a demoted ADR forfeit its requirements?** Piece 01 raised this for
   `shutil.rmtree`; this piece measures it at 1,180 REQ ids in one commit and
   four live scenario tags pointing at deleted briefs.
4. **What is the unit of approval for a release?** Today nothing says "this set
   is version X." Whether that should be a manifest, a ledger event, or an
   annotated tag is a design question; whether it should exist is not.

## What this changes in piece 01

- **§ 9 row withdrawn.** 29148 § 6.6.2.2.2's four baselines were filed under *do
  not adopt*. The contractual half stands; the four-fixed-points half is the
  answer to this piece's question and should not have been discarded.
- **§ 4.4 sharpened.** Piece 01 said requirements "have no durable owner." More
  precisely: the release plan owns them, and a release-scope decision destroys
  them.
- **§ 5.2 unchanged but re-motivated.** The proposed NEED → REQUIREMENT and
  REQUIREMENT → COMPONENT edges are still the minimum addition; this piece adds
  that requirement *identity* must stop encoding its parent's release number
  before either edge is durable.
- **A citation corrected.** "The requirements shall be configuration controlled"
  is 29148 § 6.4.3.5, not § 6.6.
