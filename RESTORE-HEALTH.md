# Restore-Health Backlog

Operator-owned running list of health-restoration items deferred from in-flight
direct-fix. Booked here — **not** as GHI/ADR/OBPI — under the 2026-06-01
DIRECT-FIX MORATORIUM: capture, don't ceremonialize. Drain when capacity allows.

---

## RH-1 — Central config-first store (gzkit has no SSOT for its own tuning values)

- **Booked:** 2026-06-01 · **Status:** deferred (architecture; "can't afford design now") · **Trigger:** the AGENTS.md budget bump this session.

**Problem.** gzkit polices single-source-of-truth obsessively for *governance
state* (ledger, ADRs, "derived views never source-of-truth") but has **none**
for its own operational scalars. They're inlined literals scattered across data
files, code, tests, and prose docs; the copies drift silently.

**Live evidence.** The AGENTS.md char budget exists in **4 places**:
`data/instructions_files_budget.json` (source, now `33000`), two hand-edited
test literals (`tests/governance/test_agents_md_map_doctrine_obpi01.py:148`,
`...obpi04.py:145`), and the `.gzkit/rules/agents-md-map-doctrine.md` Budget
table — which still says `15000` and has been wrong since OBPI-0.0.54-01.

**Inventory (representative; `grep -E '^_[A-Z_]+ *= *[0-9]' src/gzkit`):**
`_PIPELINE_MARKER_STALE_HOURS=4` (adr_audit.py), `_SECURITY_RECEIPT_MAX_AGE_HOURS=24`
(obpi_complete.py), `_RECONCILE_GRACE_SECONDS=86400` + `_DRIFT_THRESHOLD_HOURS=24`
+ `_GREEN_CEILING=1800` / `_YELLOW_CEILING=2200` (trust_audits), `_MAX_LEDGER_EVENTS_IN_COMMIT=12`
(sync.py), `_MIN_MATCH_WORDS=4` (markdown_parser.py), complexity timeouts `30.0s`
(duplicated across 4 files), foundation rubric weights `3/2/5`, eval-cluster
`3 / 3.0`; plus prose-coupled scalars — coverage floor `40.00%`, lock TTL `120m`,
the instructions budgets `32000/33000/4000/15000`, defect-fix thresholds
`≤10 lines / ≤2 files / ≥3 precedents / 60-day window`.

**Fix shape (when drained, NOT now).** One typed `gzkit.config` source (Pydantic
frozen, loaded once) that code, tests, **and doc-table generation** all read
from; rule-doc tables rendered like AGENTS.md (never hand-kept); a
`gz validate --config-ssot` fail-close flagging any literal copy that drifts.
Tests assert behavior against `config.X`, not re-hardcoded literals. Internal
operational scalars only — **not** a runtime feature-flag / user-config system.

**Why deferred.** Cross-cutting (~25+ sites across 15+ files) + needs the
generation/validator design. Exceeds one coherent commit, so the moratorium's
own carve-out fires. Hand-patching the stale `15000` now would just mint copy #5.
