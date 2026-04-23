# OBPI-0.0.20-04-fold-defect-fix-routing

Canonical OBPI slug: `OBPI-0.0.20-04-fold-defect-fix-routing`
Parent ADR: `ADR-0.0.20-agent-rule-placement-invariant`

## Context

`.gzkit/rules/defect-fix-routing.md` is the **last** universal (`paths: "**"`)
always-on rule still living under `.gzkit/rules/` after OBPI-0.0.20-02 folded
`agent-contract.md` and OBPI-0.0.20-03 folded `attestation-enrichment.md`.
ADR-0.0.20 made unscoped rules under vendor mirrors a fail-closed violation;
this file survives only via a transition allow-list entry in
`.gzkit/manifest.json` tagged `tracking_ref: ADR-0.0.20 / OBPI-04`.

This OBPI completes the migration: the binding content (two threshold tables
+ 5-step decision protocol) moves to a new **AGENTS.md § Defect-fix routing**,
the pedagogy (anti-patterns, GHI #195 origin, related-rules) moves to a new
**`docs/governance/defect-fix-routing.md`**, the canonical rule file is
deleted, the manifest allow-list is emptied, and every live inbound reference
is rewritten. Vendor mirrors regenerate away via
`gz agent sync control-surfaces`.

The implementation template is already proven: sibling OBPI-0.0.20-03
(`tests/governance/test_attestation_fold.py`) ships a 9-test suite mirroring
exactly this shape. This OBPI reuses that pattern.

## Parent ADR / Sibling Status

- Parent ADR: `ADR-0.0.20-agent-rule-placement-invariant` (foundation, Lite)
- OBPI-0.0.20-01: **Completed** (validator + allow-list mechanism)
- OBPI-0.0.20-02: **Completed** (agent-contract fold — AGENTS.md + rationale doc)
- OBPI-0.0.20-03: **Completed** (attestation-enrichment fold — AGENTS.md § Attestation + arb-middleware doc)
- **OBPI-0.0.20-04** (this brief): Draft → target Completed
- OBPI-0.0.20-05: Downstream closeout (unblocked by this OBPI)

## Approach

TDD-driven, Lite lane, self-closeable at ADR closeout.

### Step 1 — Red: author the REQ-derived test suite

Create `tests/governance/test_defect_fix_routing_fold.py` modeled on
`tests/governance/test_attestation_fold.py`. Nine tests, each
`@covers("REQ-0.0.20-04-NN")` derived from Acceptance Criteria. All MUST fail
at Red (pre-migration).

| Test | REQ | Assertion |
|------|-----|-----------|
| `test_defect_fix_routing_rule_file_deleted` | REQ-03 | `.gzkit/rules/defect-fix-routing.md` does not exist |
| `test_agents_md_has_defect_fix_routing_section` | REQ-01 | `AGENTS.md` contains `## Defect-fix routing` with semantic markers: both table headers ("Direct fix is the right route", "OBPI ceremony is required"), all 5 direct-fix criteria names (Diff size / Scope / Precedent / Trigger / Coverage), all 5 ceremony-trigger phrases (brief boundaries / CLI schema / operator directs / feature work / exceeds thresholds), and 5-step decision protocol markers |
| `test_governance_doc_exists_with_three_sections` | REQ-02 | `docs/governance/defect-fix-routing.md` exists with Anti-patterns, origin GHI #195, Related sections |
| `test_manifest_allowlist_is_empty` | REQ-04 | `manifest.rules.unscoped_allowlist` contains no `defect-fix-routing.md` entry (`assertNotIn` — avoids brittle count per test_agent_contract_fold.py precedent) |
| `test_no_inbound_references_to_legacy_paths_in_live_files` | REQ-05 | No Bucket-1 file references `.gzkit/rules/defect-fix-routing.md`, `.claude/rules/defect-fix-routing.md`, `.github/instructions/defect_fix_routing.instructions.md`, or `.agents/rules/defect-fix-routing.md`. `BUCKET_3_ROOTS` mirrors test_attestation_fold.py plus this test file itself |
| `test_vendor_mirrors_of_defect_fix_routing_rule_were_removed_by_sync` | REQ-06 | `.claude/rules/defect-fix-routing.md` and `.github/instructions/defect_fix_routing.instructions.md` absent |
| `test_unscoped_rules_validator_passes_with_empty_allowlist` | REQ-07 | `run_unscoped_rules(REPO_ROOT)` returns `result="pass"`, `exit_code=0`, `len(allowlist_entries) == 0` |
| `test_no_new_deps_or_shell_true_or_dataclass` | REQ-11 | governance doc is prose (no `@dataclass` / `shell=True` / `from dataclasses`); test file imports only stdlib + gzkit (matches OBPI-03 pattern) |
| `test_agents_md_defect_fix_routing_links_to_governance_doc` | REQ-01+02 | AGENTS.md § Defect-fix routing references `docs/governance/defect-fix-routing.md` for baseline precedent / anti-patterns pointer |

Run `uv run -m unittest tests.governance.test_defect_fix_routing_fold -v` and
confirm all nine fail for the right reasons (file absent / section missing /
allowlist still populated).

### Step 2 — Green: migrate content

**2a. Create `docs/governance/defect-fix-routing.md`** (NEW) with three
sections matching test assertions:

- `## Anti-patterns` — three bullets from current canonical lines 62-66 verbatim (OBPI brief, Surface Boundary ceremony for 5-line filter, stylistic-preference framing)
- `## When this rule was authored` — GHI #195, 2026-04-18, OBPI-0.0.16-04 → OBPI-0.0.16-06 → revert precedent (verbatim from canonical lines 68-74)
- `## Related` — canonical lines 76-81 verbatim, updated so AGENTS.md cross-references point at the folded sections (no longer cross-reference the deleted rule file)

Add a short top-of-file pointer: "Binding content lives in AGENTS.md
§ Defect-fix routing; this page carries the deep-dive rationale."

**2b. Add § Defect-fix routing to `AGENTS.md`** — placement: after § Attestation and before § Control Surfaces (last major binding section before the generated footer). Content:

- H2 heading `## Defect-fix routing`
- Intro paragraph (canonical lines 10-16, the "default failure mode is over-applying ceremony" narrative)
- `### Direct fix is the right route when ALL hold` H3 with the 5-row threshold table (canonical lines 20-26) verbatim
- `### OBPI ceremony is required when ANY hold` H3 with the 5-row trigger table (canonical lines 42-48) verbatim
- `### Decision protocol` H3 with the 5-step list (canonical lines 52-60) verbatim
- Closing note: "For baseline precedent examples (GHI #186-#189, #191, #192), anti-patterns, origin-GHI history, and related-rules cross-references, see [`docs/governance/defect-fix-routing.md`](docs/governance/defect-fix-routing.md)."

**2c. Update AGENTS.md line 93 self-reference** (Invariant 6c in § DO IT RIGHT) — change `.gzkit/rules/defect-fix-routing.md thresholds` → `§ Defect-fix routing thresholds` (anchor to the new same-file section).

**2d. Delete `.gzkit/rules/defect-fix-routing.md`** (canonical only).

**2e. Remove the allow-list entry from `.gzkit/manifest.json`** — the
`unscoped_allowlist` array goes from 1 entry → 0 entries (empty list).

### Step 3 — Green: rewrite live inbound references

All references in canonical (`.gzkit/skills/**`, `.gzkit/rules/**`) files.
Vendor mirrors (`.claude/skills/**`, `.agents/skills/**`, `.claude/rules/**`)
regenerate via sync in Step 5; edits here would be discarded.

| Canonical file | Line | Rewrite target |
|----------------|------|----------------|
| `.gzkit/rules/governance-core.md` | 21 | `AGENTS.md § Defect-fix routing` |
| `.gzkit/skills/ghi-close/SKILL.md` | 33, 55, 100, 219, 255 | `AGENTS.md § Defect-fix routing` for routing citations; `docs/governance/defect-fix-routing.md` for the "Related" pointer on line 255 |
| `.gzkit/skills/ghi-author/SKILL.md` | 29, 40, 50, 131, 185 | Same pattern — routing cites → AGENTS.md § Defect-fix routing; "Related" cite → governance doc |
| `.gzkit/skills/gz-skill-router/SKILL.md` | 57 | `AGENTS.md § Defect-fix routing` |
| `.gzkit/skills/gz-justify/SKILL.md` | 110 | `AGENTS.md § Defect-fix routing` |
| `.gzkit/skills/gz-design/SKILL.md` | 62 | `AGENTS.md § Defect-fix routing` |
| `.gzkit/skills/gz-plan/SKILL.md` | 22 | `AGENTS.md § Defect-fix routing` |
| `.gzkit/skills/gz-obpi-pipeline/SKILL.md` | 70 | `AGENTS.md § Defect-fix routing` |

Bump `skill-version` (patch) on each edited canonical skill per
`.gzkit/rules/skill-surface-sync.md`.

### Step 4 — Green: update sibling test's co-state assertion

`tests/governance/test_attestation_fold.py::test_manifest_allowlist_has_one_entry`
asserts `len(allowlist) == 1` and `entry_files == {".gzkit/rules/defect-fix-routing.md"}`. After this OBPI the allowlist is empty — those assertions will fail.

The fix is semantic, not cosmetic: OBPI-03's REQ is "attestation-enrichment.md
is removed from the allowlist" (absence assertion), not "exactly one entry
remains" (co-state that OBPI-04 changes). Rewrite the test body to follow the
`test_agent_contract_fold.py::test_manifest_allowlist_removes_agent_contract_entry`
pattern:

```python
self.assertNotIn(
    ".gzkit/rules/attestation-enrichment.md",
    entry_files,
    "attestation-enrichment.md allow-list entry must be removed",
)
```

Drop the `assertEqual(len(allowlist), 1, …)` and the set-equality check
entirely. Update the docstring accordingly ("manifest no longer contains
attestation-enrichment.md" instead of "shrinks from 2 to 1").

Justified as inbound-reference correction (OBPI brief Allowed Paths includes
"Inbound-reference updates"); this is a live test-file reference to the
legacy co-state.

### Step 5 — Sync + validate

```bash
uv run gz agent sync control-surfaces    # regenerates mirrors; drops
                                         #   .claude/rules/defect-fix-routing.md
                                         #   .github/instructions/defect_fix_routing.instructions.md
                                         #   .agents/rules/defect-fix-routing.md (if present)
                                         # and re-emits edited canonical skills to their mirrors
uv run gz validate --unscoped-rules      # exits 0 with empty allow-list
uv run gz validate --all                 # broader governance checks pass
uv run gz lint                           # ruff clean
uv run mkdocs build --strict             # no broken internal links; new
                                         #   docs/governance/ doc resolves
uv run -m unittest tests.governance.test_defect_fix_routing_fold -v
uv run -m unittest tests.governance.test_attestation_fold -v
uv run -m unittest tests.governance.test_agent_contract_fold -v
```

## Critical Files

**Created:**
- `docs/governance/defect-fix-routing.md` (new pedagogy doc)
- `tests/governance/test_defect_fix_routing_fold.py` (new REQ-pinned test suite)

**Modified:**
- `AGENTS.md` (add § Defect-fix routing; update Invariant 6c self-reference on line 93)
- `.gzkit/manifest.json` (empty `unscoped_allowlist`)
- `.gzkit/rules/governance-core.md` (line 21 reference rewrite)
- `.gzkit/skills/ghi-close/SKILL.md` (5 refs + skill-version bump)
- `.gzkit/skills/ghi-author/SKILL.md` (5 refs + skill-version bump)
- `.gzkit/skills/gz-skill-router/SKILL.md` (1 ref + skill-version bump)
- `.gzkit/skills/gz-justify/SKILL.md` (1 ref + skill-version bump)
- `.gzkit/skills/gz-design/SKILL.md` (1 ref + skill-version bump)
- `.gzkit/skills/gz-plan/SKILL.md` (1 ref + skill-version bump)
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (1 ref + skill-version bump)
- `tests/governance/test_attestation_fold.py` (soften allowlist-count assertion to `assertNotIn`)

**Deleted:**
- `.gzkit/rules/defect-fix-routing.md`

**Regenerated by sync (do not edit directly):**
- `.claude/rules/defect-fix-routing.md` (removed)
- `.github/instructions/defect_fix_routing.instructions.md` (removed)
- `.agents/rules/defect-fix-routing.md` (removed if present)
- `.claude/skills/*`, `.agents/skills/*`, `.github/skills/*` (mirror refreshed)

## Bucket-3 Preservation (left untouched)

Reuse OBPI-03's `BUCKET_3_ROOTS` list verbatim, plus this test file itself:

- `RELEASE_NOTES.md`, `.git/`, `.claude/plans/`
- `artifacts/audits/**` (historical GHI drafts)
- Closed ADR narratives: ADR-0.0.16, ADR-0.0.17, ADR-0.0.19, ADR-0.0.20, pool/pre-release ADRs
- `docs/governance/agent-contract-rationale.md`, `advisory-rules-audit.md`, `model-regression-taxonomy.md`, `trust-doctrine.md`, `governance_runbook.md`, `arb-middleware.md`
- `docs/user/manpages/arb.md` (HISTORY section)
- `ops/chores/`, `site/`, `.venv/`, `dist/`, `build/`
- `tests/governance/test_attestation_fold.py`, `tests/governance/test_agent_contract_fold.py`, `tests/governance/test_defect_fix_routing_fold.py`, `tests/validators/test_unscoped_rules.py` (validator fixture legitimately uses the legacy path)

## Verification (end-to-end)

All acceptance criteria mechanically verified:

```bash
# REQ-03 — canonical deleted
test ! -f .gzkit/rules/defect-fix-routing.md

# REQ-01 — AGENTS.md section exists with both tables
grep -q "Direct fix is the right route" AGENTS.md
grep -q "OBPI ceremony is required" AGENTS.md
grep -q "## Defect-fix routing" AGENTS.md

# REQ-02 — governance doc exists
test -f docs/governance/defect-fix-routing.md

# REQ-04 — allow-list empty
python -c "import json,sys; m=json.load(open('.gzkit/manifest.json')); \
  sys.exit(0 if not m['rules']['unscoped_allowlist'] else 1)"

# REQ-06 — vendor mirrors gone
test ! -f .claude/rules/defect-fix-routing.md
test ! -f .github/instructions/defect_fix_routing.instructions.md

# REQ-07/08/09 — validators pass
uv run gz validate --unscoped-rules
uv run gz validate --all
uv run mkdocs build --strict

# REQ-10 — test suite green
uv run -m unittest tests.governance.test_defect_fix_routing_fold -v

# REQ-11 — no new deps / shell=True / dataclass enforced by test_no_new_deps_or_shell_true_or_dataclass
```

## Lane & Attestation

- **Lite** (content migration + rule deletion + reference rewrites; no CLI / schema / runtime contract change)
- Parent ADR is `foundation` kind → **Gate 5 human attestation required at brief level** per OBPI Acceptance Protocol (foundation-kind rigor applies across lanes). OBPI-0.0.20-02 and -03 were self-closeable per brief frontmatter; this OBPI's brief frontmatter line 194 says "Lite lane; OBPI self-closeable". Present full evidence at Stage 4 regardless; the operator determines attestation mode at ceremony time.

## Risks / Rollback

- **Low blast radius.** Changes are content migration + reference rewrites. If `gz validate --unscoped-rules` or mkdocs strict build fails, the diff is fully reversible via a single `git restore` before commit.
- **Sibling test coupling.** Step 4's edit to `test_attestation_fold.py` is the only non-obvious live-file touch. Justification is explicit in the commit body; the rewrite converts a co-state assertion to an absence assertion (strengthens the test's semantic alignment with OBPI-03's REQ).
- **Skill version drift.** Failing to bump `skill-version` on edited canonical skills will cause `gz agent sync control-surfaces` to refuse or flag drift. Bump on every edit.
