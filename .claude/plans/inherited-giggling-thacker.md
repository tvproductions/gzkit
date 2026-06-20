# Plan — OBPI-0.0.74-01 · MX Marker File

## Context

The Magna Carta campaign (build-to-1.0) was amended 2026-06-20 to seat
**ADR-0.0.74 — MX Mode (Maintenance Hangar)** as the topmost **P0** pull,
pausing B.1. The hangar is one mechanism: a filesystem **marker** meaning
"in the hangar," read by both enforcement surfaces (code guards + agents).
OBPI-01 is the foundation stone the other nine OBPIs build on — the marker
module itself.

**ADR Decision item #1 (verbatim, the contract):** "The marker file. A dumb
filesystem truth-file; its presence means MX==TRUE. Read with stdlib only so it
opens even when gz itself is the patient. Valid ONLY when bound to a real
mx_session_opened ledger event the tool wrote — a hand-created marker with no
matching event is void (anti-contrivance)."

**Outcome:** a stdlib-only `gzkit.mx.marker` module whose presence is the single
MX truth-source, with a ledger-binding validity gate that voids hand-forged
markers, plus unit tests pinning both rules.

## Grounded facts (read first-hand this session)

- `src/gzkit/mx/` and `tests/mx/` do **not** exist — clean CREATE.
- `mx_session_opened` appears **nowhere** in code or ledger → OBPI-01 ships only
  the *reader/validity* logic; the event *writer* is OBPI-04 (`gz mx enter`) /
  OBPI-06. OBPI-01 declares the binding contract the writer must honor.
- Raw ledger lines key the event type under `"event"` (e.g.
  `{"schema":…,"event":"artifact_edited","id":…,"ts":…,"path":…}`). The marker's
  binding check reads `.gzkit/ledger.jsonl` line-by-line with stdlib `json` and
  matches `event == "mx_session_opened"`. It must NOT import `gzkit.ledger`
  (Pydantic) — that would break "reads when gz is the patient."
- `.gzkit/` convention: ledger at `.gzkit/ledger.jsonl`; subdirs `.gzkit/locks/`,
  `.gzkit/handoffs/`, etc. → marker lives at **`.gzkit/mx.json`** (a single
  truth-file at the `.gzkit` root, sibling of `ledger.jsonl`).
- `find_project_root()` exists in `src/gzkit/hooks/core.py:412`, and the hook
  *scripts* deliberately define a self-contained inline `find_project_root`
  (`hooks/scripts/validation.py:34`, `routing.py:246` — walk up for `.gzkit/`).
  The marker mirrors that self-contained pattern rather than importing hooks, to
  stay dependency-free.
- Every `tests/` subdir carries `__init__.py` for unittest discovery
  (`tests/adr/__init__.py`, `tests/cli/__init__.py`, …). Tests are `unittest`,
  not pytest (`forbid-pytest` hook + `.gzkit/rules/tests.md`).

## Files (per brief Allowed Paths)

- **CREATE** `src/gzkit/mx/__init__.py` — `gzkit.mx` package init; re-exports the
  marker surface.
- **CREATE** `src/gzkit/mx/marker.py` — the module (below).
- **CREATE** `tests/mx/test_marker.py` — unittest cases.
- ⚠️ **CREATE** `tests/mx/__init__.py` — **NOT in the brief's Allowed Paths**, but
  required by the tests-package convention (every subdir has one; unittest
  discovery imports `tests.mx.test_marker`). See *Brief gap* below — must be
  reconciled before completion or the completion validators flag an
  out-of-allowlist file.

## Module design — `src/gzkit/mx/marker.py` (stdlib only: `json`, `pathlib`, `dataclasses`, `datetime`)

- `MARKER_RELPATH = (".gzkit", "mx.json")` + `marker_path(project_root=None) -> Path`
  — **the single MX truth-source path** (ADR Boundary Invariant #1). Every future
  consumer (OBPI-02 checkpoint, -04 enter, -05 exit) imports this one helper, so
  no surface invents its own path.
- `_find_project_root(start=None) -> Path` — minimal stdlib walk-up for `.gzkit/`,
  mirroring `hooks/scripts/validation.py`'s self-contained finder. Deliberately
  does not import `gzkit.hooks` (keeps the read working when gz is broken).
- `@dataclass(frozen=True) Marker` — fields the ADR names in Decision items 4–5:
  `session_id: str`, `opened_at: str`, `reason: str`, `attestor: str`,
  `inspection_scope: list[str]`. `to_dict()` / `from_dict()` via stdlib.
  (Not Pydantic — stdlib-only mandate. Load-bearing field for OBPI-01 is
  `session_id`; the rest are the schema `gz mx enter` will populate.)
- `is_active(project_root=None) -> bool` — marker file exists → **MX==TRUE**
  (REQ-01-01). The cheap truth-file read code-guards use.
- `read(project_root=None) -> Marker | None` — stdlib `json` parse; returns `None`
  on absent/malformed (robust, never raises into a guard).
- `is_valid(project_root=None, ledger_path=None) -> bool` — `is_active()` **AND**
  the ledger contains an `mx_session_opened` event whose `session_id` matches the
  marker's, with no later `mx_session_closed` for that session. Hand-created
  marker (no matching event) → **void → False** (REQ-01-02). Reads the ledger raw
  with stdlib; tolerant of malformed lines.
- `write(marker, project_root=None) -> Path` — stdlib `json` write of the payload
  (the objective requires read **and** write). Low-level persist only; the
  coupled ledger event is OBPI-04's `gz mx enter` (events.py is denied here).

**Semantics decision (baked in — flag for ratification):** `is_active()` =
*presence* (ADR: "presence means MX==TRUE"); `is_valid()` = presence + ledger
binding (ADR: "valid ONLY when bound"). Real consumers gate on `is_valid()`;
guards that just need the cheap signal use `is_active()`. This split maps the two
REQs 1:1 and is grounded in the ADR's two distinct clauses.

**Cross-OBPI contract declared here (DO IT RIGHT 1a):** the `mx_session_opened`
ledger event MUST carry a `session_id` field equal to `marker.session_id`.
OBPI-04/06 (the writer) implement to honor this; OBPI-05 (exit) removes the
marker via `marker_path().unlink()` and writes `mx_session_closed`. OBPI-01 does
**not** add `remove()`/the events (deferred, not speculative).

## Tests — `tests/mx/test_marker.py` (unittest, tmp project root via `tempfile`)

- **REQ-01-01 [behavior]:** marker present → `is_active()` True; `write`→`read`
  round-trip preserves fields; **plus** a structural stdlib-only-imports test:
  AST-parse `marker.py` and assert no `gzkit.*` / third-party imports — the honest
  proof of "reads even when gz is the patient."
- **REQ-01-02 [behavior]:** `is_valid()` is False when (a) no ledger event, (b)
  ledger has only a *different* `session_id`, (c) matching open *then a later
  close*; and True when a matching open has no close. Ledger lines written as raw
  JSONL into the tmp root (no `gzkit.ledger` dependency).
- **REQ-01-03 [structural-fence]:** no test asserts it directly — proof channel is
  parent ADR § Boundary Invariants #1 (single MX truth-source), per ADR-0.0.59.
  A light test confirms all path access flows through `marker_path()` (one source).

## Brief gap to reconcile (surface before implementing)

The brief Allowed Paths omits `tests/mx/__init__.py`, which the unittest-package
convention requires. Resolution: reconcile the brief (`gz-brief-reconcile`,
operator-attested) to add `tests/mx/__init__.py` to Allowed Paths + "Creates
These Files," **or** operator authorizes the one-file allowlist expansion inline.
This is the only scope deviation; flagging per AGENTS.md Always #9 rather than
silently expanding.

## Governed entry sequence (post plan-approval)

1. **ADR status:** ADR-0.0.74 is `Draft`. Confirm the Draft→Accepted transition
   (or that `gz obpi pipeline` handles it) before OBPI work opens.
2. **Lock:** claim the OBPI lock for OBPI-0.0.74-01 (`gz-obpi-lock`).
3. **Reconcile** the brief allowlist gap above.
4. **Pipeline:** this is contract-bearing/heavy → run
   `uv run gz obpi pipeline OBPI-0.0.74-01` (TDD red→green → `gz check` → ceremony
   → guarded git-sync → completion). Gate 5 human attestation is **universal**
   for this heavy/foundation OBPI.
5. **gz-plan-audit** before implementation (ADR-intent ↔ brief ↔ plan alignment).

## Parent-ADR defects to track (out of OBPI-01 scope — flag, do not fix here)

- ADR body line 19 `{persona}` placeholder is unfilled.
- ADR `## Fidelity Assertions` table is still the scaffold example row
  (`uv run gz --version | 0`) — will fail `gz validate --fidelity-presence`
  (ADR-0.0.73 BI#4) at closeout; needs real per-Decision assertions.
- HEAD commit `465d2863` has a malformed message (raw git editor template).
  History on `origin/main`; fixing means rewrite+force-push — operator call only.

These route per AGENTS.md (in-scope→fix; out-of-scope→GHI/insight). They belong
to the ADR closeout, not OBPI-01.

## Verification (end-to-end)

```bash
uv run gz test                 # green incl. new tests/mx
uv run gz lint                 # clean
uv run gz typecheck            # clean
test -f src/gzkit/mx/marker.py && test -f src/gzkit/mx/__init__.py \
  && test -f tests/mx/test_marker.py && test -f tests/mx/__init__.py
# Demo (brief): stdlib-only read works with gz "down"
uv run python -c "from gzkit.mx import marker; print('MX==TRUE' if marker.is_active() else 'MX==FALSE')"
```

Success = both REQ behaviors pinned by passing tests, `gz check` green, demo
prints `MX==FALSE` with no marker and `MX==TRUE` with a valid marker present.
