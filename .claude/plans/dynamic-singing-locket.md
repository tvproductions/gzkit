# B.1 Increment 1 — Genuinely re-complete OBPI-0.0.37-22's mechanism (staged warn→fail)

## Context

The Magna Carta campaign's topmost pull is **B.1 — ADR-0.0.37 real corpus rebuild**
(ADR-0.0.73 closed/attested 2026-06-19). B.1 is **REPUDIATED-IN-PART**: OBPIs
02/03/21/22 were repudiated 2026-06-16 for `model-induced-fabrication` — the CMS
pipeline (`corpus → compress → rendition → playback`) did not render AGENTS.md from
the corpus; its gates were tautologies.

State has moved since that snapshot (GHI #623 landed a *real*
`--rendition-floor-coherence` gate; the composer now emits
`composition_candidate_emitted`; all four CMS validators exit 0 at HEAD). But two
OBPI-22 substance gaps remain, both verified directly:

1. **No governed candidate→committed promotion (REQ-22-01).** `save_rendition`
   (`src/gzkit/content/rendition_store.py:47`) has **zero production callers** — only
   tests/BDD steps. The on-disk renditions (`.gzkit/renditions/AGENTS.md/{claude,codex}.md`)
   were hand-placed by a *docs* commit (`f3d8f586`), exactly the repudiation's complaint.
2. **Freshness gate is an mtime tautology (REQ-22-03).** `rendition_freshness.py:44-48`
   compares `st_mtime`, not content — a `touch` passes, a content-edit can pass. The
   repudiation rejects it by name.

Deeper truth surfaced during design: the corpus holds **9 entries / 6.3 KB** vs. a
~30 KB `AGENTS.md`; the floor gate checks invariant *presence*, not *derivation*, so
**no committed rendition is yet genuinely "the corpus played back."** Enriching the
corpus to carry the surface's content (OBPI-19 lineage) is a separate, larger B.1
piece. **Operator ruling:** land the OBPI-22 *mechanism* now with the freshness gate
**staged in warn mode** (green-first preserved, OBPI-0.0.41 precedent); flip it
fail-closed in a later increment once the corpus is enriched and the renditions are
re-seeded under genuine Gate-5 attestation. **Disposition of 02/03** (operator ruling):
re-point to the corpus mechanism + re-attest — handled in a later increment, not here.

This increment delivers the mechanism honestly and does **not** mark OBPI-22 complete
(it stays `repudiated` until the fail-closed flip + attested re-seed in Increment 2).

## Scope of THIS increment

Re-complete OBPI-0.0.37-22's mechanism (Heavy/foundation). No corpus enrichment, no
re-attestation of OBPI-22, no 02/03 work. End state: `gz check` green; the real
content-freshness gate live in warn mode; a governed, operator-attested commit seam.

## Design

### 1. Corpus fingerprint + provenance sidecar — `src/gzkit/content/rendition_store.py` (EDIT)
- `corpus_fingerprint(corpus: Corpus) -> str` = `sha256(Corpus.dumps().encode("utf-8")).hexdigest()`.
  Hashing the **canonical model serialization** (`Corpus.dumps()`, `content/models/corpus.py:64`)
  — not raw file bytes — makes it cross-platform stable (`load_corpus`→`splitlines()` absorbs
  CRLF/LF; `dumps()` re-emits `\n`). Pure function → trivially unit-testable.
- `RenditionProvenance(BaseModel)` frozen, `extra="forbid"` (per `.claude/rules/models.md`):
  `algorithm="sha256"`, `corpus_fingerprint`, `corpus_entry_count`, `committed_ts`,
  `attestor`, `attestation_text`.
- `fingerprint_path(root, surface, consumer)` → `.gzkit/renditions/<surface>/<consumer>.corpus.json`
  (invisible to the `*.md` globs in `rendition_freshness.py` / `rendition_floor_coherence.py`).
- `save_fingerprint(...)`, `load_fingerprint(...) -> RenditionProvenance | None`.

### 2. Content-based freshness gate, STAGED — `src/gzkit/governance/trust_audits/rendition_freshness.py` (rewrite)
- Signature unchanged: `validate_rendition_freshness(root) -> list[ValidationError]` (callers at
  `validate_cmd.py:438`, `quality.py:590`, `trust_audits/__init__.py` unaffected).
- Per `<consumer>.md`: skip if corpus absent (bootstrap-safe); else compare
  `corpus_fingerprint(load_corpus(...))` vs `load_fingerprint(...).corpus_fingerprint`.
  - Missing sidecar → drift (can't prove derivation). Corpus fingerprint mismatch → drift.
  - Both emit `composition_drift_detected` (reused verbatim — `governance/events.py:34`,
    `schemas/ledger.json`; **no schema change**) and a three-part recovery message
    (`.claude/rules/guardrail-feedback-prose.md`): what / why (the repudiation's "no gate
    asserts the rendition derives from the corpus") / next step (`gz content compose … && gz content commit …`).
- **Staging flag `_FRESHNESS_FAIL_CLOSED = False`** (Increment 1): drift detections emit the
  ledger event + a WARNING to stderr but return `[]` (exit 0 — `gz check` stays green).
  Increment 2 flips the flag to `True` (drift → `ValidationError`, exit 3). Tests exercise
  **both** modes now, so the fail-closed semantics are proven before they go live (mirrors
  OBPI-0.0.41-02 warn-only → -03 fail-closed).
- Kills both named tautologies: `touch`/zero-byte-restore (identical content) → identical
  digest → no drift; real content edit/append → different digest → drift.

### 3. Governed commit seam — `src/gzkit/commands/content/commit.py` (CREATE) + `commands/content/__init__.py` (EDIT)
- `gz content commit <surface> --consumer <c> --attestor <name> --attestation-text <text>`:
  read `candidate_path(...)` via `read_text` then `.encode("utf-8")` (normalizes CRLF→LF
  into `save_rendition`'s `write_bytes`) → `save_rendition` → `corpus_fingerprint(load_corpus(...))`
  → `save_fingerprint` → emit `rendition_committed` → print.
- Fail-closed (exit 1, nothing written) on empty `--attestor`/`--attestation-text`, absent
  candidate, or absent/empty corpus; exit 2 on IO error. Operator-gated like
  `gz obpi repudiate` (`.claude/rules/governance-core.md`): the operator's `--attestation-text`
  **is** Gate 5; promotion is explicit, never automatic. (`sync`/`render --commit` rejected —
  unattested + re-conflates playback with commit, the repudiated facade.)

### 4. New ledger event `rendition_committed`
- `ledger_events.py` (factory) + `governance/events.py` (`emit_rendition_committed`) +
  `events.py` (read-path model + `TypedLedgerEvent` union) + `schemas/ledger.json` (required-fields) +
  `tests/test_schemas.py` (`_EVENT_MODELS`) + `trust_audits/events.py` (`_NO_GRAPH_IMPACT` waiver,
  like `composition_candidate_emitted`). Carries `surface, consumer, corpus_fingerprint, attestor, ts`.

### 5. Coupled / governance surfaces
- **Brief** `OBPI-0.0.37-22-…md`: correct line ~50 "mutation-timestamp comparison" →
  "corpus content-fingerprint comparison" (a *correction* fulfilling REQ-22-03's intent, per
  operator doctrine); add **REQ-0.0.37-22-07 [BEHAVIOR]** for the governed promotion seam +
  `req_atomic`. Reconcile via `gz validate --brief-reconcile` (operator-attested allowlist
  amendment for `commit.py`, the new-event surfaces, `docs/user/manpages/content.md`,
  `config/doc-coverage.json`).
- **Sensitivity floor:** OBPI-22 edits `quality.py`/`commands/quality.py` (registered surface,
  incidental overlap). Resolve at brief re-open — narrow paths, grandfather-check, or
  `gz obpi complete --accept-security-floor` at the eventual completion. Do not add a fresh
  grandfather entry.
- **Docs:** `docs/user/manpages/validate.md` (mtime→fingerprint + warn-staging note),
  `docs/user/manpages/content.md` (new `commit` verb), `docs/user/runbook.md`
  (recompose-then-commit flow). `gz cli audit` must exit 0 with `content commit` covered.
- **Pre-existing one-line defect (fix in same patch):** `trust_audits/__init__.py:210-211`
  lists `validate_rendition_freshness` twice in `__all__`.

## TDD plan (RED first; assertions derive from REQ semantics, `.gzkit/rules/tests.md`)
- `tests/content/test_rendition_store.py`: fingerprint determinism; content-sensitivity;
  **cross-platform stability** (CRLF vs LF corpus → equal digest); commit writes BOTH rendition
  + sidecar with matching fingerprint; CRLF candidate → committed bytes contain no `\r`.
- `tests/governance/test_rendition_freshness.py` (both staging modes):
  **regression-lock** — `os.utime` mtime-bump, identical content → exit 0 (*fails the old
  mtime gate, passes the new*); zero-byte content-restore → exit 0; corpus content-edit with
  frozen rendition → drift; missing sidecar → drift (three-part prose asserted); corpus absent
  → exit 0. In warn mode drift returns `[]`+event; in fail-closed mode drift returns one
  `ValidationError`.
- `tests/commands/test_content_commit.py`: empty `--attestor`/`--attestation-text`/absent
  candidate → exit 1, nothing written; success emits `rendition_committed` with `attestor` +
  `corpus_fingerprint`.
- BDD `features/rendition_playback.feature` (+steps): `@REQ-0.0.37-22-03` (content-drift),
  `@REQ-0.0.37-22-07` (commit promotes candidate + freezes provenance).

## Verification (end-to-end)
1. `uv run -m unittest -q` green (new tests pass; full suite ~265s).
2. `uv run gz validate --rendition-freshness` exit 0 (warn mode); warnings printed for the two
   un-sidecared renditions; `composition_drift_detected` events present in ledger.
3. Manual: `gz content compose AGENTS.md --consumer claude --candidate <f>` →
   `gz content commit AGENTS.md --consumer claude --attestor "g0" --attestation-text "<verbatim>"`
   → assert `<consumer>.md` + `<consumer>.corpus.json` written, fingerprint matches corpus,
   `gz validate --rendition-freshness` now clean for that pair.
4. `uv run gz cli audit` exit 0 (`content commit` covered). `uv run gz validate --documents --surfaces` clean.
5. `uv run gz check` **green** (warn-staged gate). `uv run gz git-sync --apply --lint --test`.

## Governed path & boundaries
- This is TDD implementation toward re-completing the **repudiated** OBPI-22; it does **not**
  run `gz obpi complete` and does **not** clear `repudiated` (that is Increment 2, after the
  fail-closed flip + corpus enrichment + attested re-seed).
- Heavy/foundation: eventual completion requires Gate-5 human attestation. Commit to `main`
  (no feature branch — operator directive); each commit passes the full pre-commit gate.

## Follow-on (NOT this increment)
- **Increment 2:** corpus enrichment (capture AGENTS.md content, OBPI-19 lineage) → attested
  real `gz content compose`+`commit` of the renditions → flip `_FRESHNESS_FAIL_CLOSED = True`
  → `gz obpi complete` OBPI-22 (clears repudiation).
- **Later B.1:** re-point + re-attest OBPI-02/03 to the corpus mechanism; OBPI-21 honest
  re-verification; B.2 (registry-projected <15k codex surface, #519); B.3 (play back queued
  corpus entries).
