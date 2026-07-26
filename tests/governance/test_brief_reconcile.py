"""Tests for the brief reconciliation engine (OBPI-0.0.37-05)."""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from pathlib import Path

from gzkit.governance.brief_reconcile import (
    AllowlistDelta,
    CitationDelta,
    DiscoveryDelta,
    ReconcileResult,
    ReqCountDelta,
    VerificationDelta,
    _compute_missing_in_brief,
    reconcile_brief,
)
from gzkit.governance.trust_audits.brief_reconcile import validate_brief_reconcile
from gzkit.traceability import covers

FIXTURES = Path(__file__).parent.parent / "fixtures" / "brief_reconcile"
PROJECT_ROOT = Path(__file__).parent.parent.parent  # repo root


def _write_structured_brief(
    path: Path,
    *,
    brief_id: str,
    parent: str,
    reqs: list[str],
    allowlist: list[str],
    acceptance_count: int | None = None,
    status: str = "Active",
) -> None:
    """Write a structured-frontmatter OBPI brief (parses as BriefStructure).

    Defaults to ``Active`` rather than ``Draft`` so drift-dimension tests are not
    confounded by lifecycle scoping: a Draft brief's Allowed Paths name its
    deliverables and deliberately do not gate (GHI #615). Tests about the Draft
    scoping itself pass ``status`` explicitly.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    n_acc = len(reqs) if acceptance_count is None else acceptance_count
    fm_allowlist = "\n".join(f"  - {p}" for p in allowlist)
    fm_reqs = "\n".join(f"  - {r}" for r in reqs)
    acceptance = "\n".join(f"- [ ] {reqs[i % len(reqs)]}: criterion" for i in range(n_acc))
    path.write_text(
        textwrap.dedent(f"""\
            ---
            id: {brief_id}
            parent: {parent}
            lane: Heavy
            status: {status}
            allowlist:
            {fm_allowlist}
            reqs:
            {fm_reqs}
            verification:
              - uv run gz validate
            citations: []
            ---
            # {brief_id}: Structured Test Brief
            ## Acceptance Criteria
            {acceptance}
            """),
        encoding="utf-8",
    )


def _write_legacy_brief(
    path: Path, *, brief_id: str, allowlist: list[str], status: str = "Active"
) -> None:
    """Write a legacy-frontmatter OBPI brief (parses as LegacyBriefShape).

    Same ``Active`` default and same reason as ``_write_structured_brief``.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    bullets = "\n".join(f"- `{p}`" for p in allowlist)
    path.write_text(
        textwrap.dedent(f"""\
            ---
            id: {brief_id}
            status: {status}
            ---
            # {brief_id}: Legacy Test Brief
            ## Allowed Paths
            {bullets}
            ## Acceptance Criteria
            - [ ] REQ-9.9.9-09-01: criterion
            """),
        encoding="utf-8",
    )


class TestReconcileBriefResult(unittest.TestCase):
    @covers("REQ-0.0.37-05-01")
    def test_returns_reconcile_result(self):
        result = reconcile_brief(FIXTURES / "passing.md", PROJECT_ROOT)
        self.assertIsInstance(result, ReconcileResult)
        self.assertEqual(result.brief_id, "OBPI-0.0.37-05-brief-reconcile-engine")
        self.assertIsInstance(result.allowlist_delta, AllowlistDelta)
        self.assertIsInstance(result.discovery_delta, DiscoveryDelta)
        self.assertIsInstance(result.verification_delta, VerificationDelta)
        self.assertIsInstance(result.req_count_delta, ReqCountDelta)
        self.assertIsInstance(result.citation_delta, CitationDelta)
        self.assertIsInstance(result.has_drift, bool)

    @covers("REQ-0.0.37-05-01")
    def test_no_drift_on_passing_fixture(self):
        result = reconcile_brief(FIXTURES / "passing.md", PROJECT_ROOT)
        self.assertFalse(result.has_drift)

    def test_req_count_drift_alone_does_not_set_has_drift(self):
        """GHI #581: req_count is the advisory crude heuristic — Requirements-section
        bullets vs Acceptance checkboxes are legitimately different counts (every
        real brief in ADR-0.0.72 tripped it). A req_count-only delta must NOT set
        has_drift: it fail-closed valid completions and broke reconcile idempotency
        (appending a duplicate drift note per run). Meaningful dimensions still drift."""
        result = reconcile_brief(FIXTURES / "req_count_drift.md", PROJECT_ROOT)
        self.assertNotEqual(result.req_count_delta.delta, 0)  # the advisory drift exists
        self.assertFalse(result.allowlist_delta.missing_on_disk)  # no meaningful drift
        self.assertFalse(result.allowlist_delta.missing_in_brief)
        self.assertFalse(result.discovery_delta.unresolved_paths)
        self.assertFalse(result.has_drift)  # but req_count alone must not block

    @covers("REQ-0.0.37-05-01")
    def test_discovery_checklist_unresolved_path_reported(self):
        # ReconcileResult.discovery_delta (REQ-01 shape) reports discovery-checklist
        # paths absent from the project tree.
        result = reconcile_brief(FIXTURES / "discovery_drift.md", PROJECT_ROOT)
        self.assertIn(
            "src/gzkit/governance/does_not_exist_at_all.py",
            result.discovery_delta.unresolved_paths,
        )
        self.assertTrue(result.has_drift)

    @covers("REQ-0.0.37-05-01")
    def test_discovery_glob_path_not_existence_checked(self):
        # GHI #626 Component 2 — a glob prerequisite (`.../**`) is a pattern, not a
        # literal path. `(project_root / "dir/**").exists()` is always False, so a
        # glob in the discovery checklist must NOT be reported as unresolved drift.
        from gzkit.governance.brief_reconcile import _compute_discovery_delta

        body = textwrap.dedent("""\
            ## Discovery Checklist

            - [ ] Required path exists or is created: `docs/design/adr/foundation/**`
            """)
        delta = _compute_discovery_delta(body, PROJECT_ROOT)
        self.assertEqual(delta.unresolved_paths, [])

    @covers("REQ-0.0.37-05-01")
    def test_discovery_create_declared_path_exempt_from_unresolved(self):
        # GHI #626 remaining variant — the CREATE exemption is asymmetric between
        # the two existence-checking dimensions. `_compute_allowlist_delta` takes
        # `creates_paths` and exempts a `**CREATE**`-declared path; the discovery
        # dimension never received the parameter, so the *same* declaration in the
        # *same* brief resolves differently depending on which section names it.
        # A first-implementation OBPI drifts by construction.
        from gzkit.governance.brief_reconcile import _compute_discovery_delta

        body = textwrap.dedent("""\
            ## Discovery Checklist

            - [ ] Required path exists or is created: `src/gzkit/net_new_zzz.py` **CREATE**
            """)
        delta = _compute_discovery_delta(
            body, PROJECT_ROOT, creates_paths={"src/gzkit/net_new_zzz.py"}
        )
        self.assertEqual(delta.unresolved_paths, [])

    @covers("REQ-0.0.37-05-01")
    def test_discovery_undeclared_missing_path_still_reported(self):
        # The exemption is scoped to declared creates — an undeclared missing path
        # must still drift, or the fix would blind the dimension entirely.
        from gzkit.governance.brief_reconcile import _compute_discovery_delta

        body = textwrap.dedent("""\
            ## Discovery Checklist

            - [ ] Required path exists or is created: `src/gzkit/undeclared_zzz.py`
            """)
        delta = _compute_discovery_delta(
            body, PROJECT_ROOT, creates_paths={"src/gzkit/net_new_zzz.py"}
        )
        self.assertEqual(delta.unresolved_paths, ["src/gzkit/undeclared_zzz.py"])

    @covers("REQ-0.0.37-05-01")
    def test_line_range_citation_is_not_a_path(self):
        # GHI #626 class — `path.py:36-66` cites a region of a file, not a file.
        # `(root / "common.py:36-66").exists()` is always False, so the citation
        # convention the briefs already use drifts by construction. Same family as
        # the `module.py::symbol` marker already rejected on the line above.
        from gzkit.governance.brief_reconcile import _looks_like_path

        self.assertFalse(_looks_like_path("src/gzkit/commands/common.py:36-66"))
        self.assertFalse(_looks_like_path("src/gzkit/core/models.py:19"))
        # The same file without the region suffix is a real path and must resolve.
        self.assertTrue(_looks_like_path("src/gzkit/core/models.py"))

    @covers("REQ-0.0.37-05-01")
    def test_template_placeholder_is_not_a_path(self):
        # GHI #626 class — `{adrs}/{adr_id}.md` is a config-substitution template,
        # not a literal path; it can never exist on disk under that spelling.
        from gzkit.governance.brief_reconcile import _looks_like_path

        self.assertFalse(_looks_like_path("{adrs}/{adr_id}.md"))
        self.assertTrue(_looks_like_path("docs/design/adr/real.md"))


class TestTerminalStatusScoping(unittest.TestCase):
    """A sealed brief is a historical record, not a live claim (GHI #707)."""

    _BODY = textwrap.dedent("""\
        ---
        id: OBPI-0.1.0-77-sealed
        parent: ADR-0.1.0-f
        item: 77
        lane: Lite
        status: {status}
        ---

        # OBPI-0.1.0-77-sealed: Sealed

        ## Allowed Paths

        - `src/gzkit/renamed_away_zzz.py` (modify)

        **Brief Status:** {status}
        """)

    def _reconcile(self, status: str):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = root / "brief.md"
            brief.write_text(self._BODY.format(status=status), encoding="utf-8")
            return reconcile_brief(brief, root)

    @covers("REQ-0.0.37-05-02")
    def test_terminal_brief_reports_deltas_but_does_not_gate(self):
        # The path is genuinely absent — the brief cited it before a rename. The
        # delta is still computed (archaeology is preserved), but a completed
        # brief cannot drift: there is no future work for the Stage-1 gate to
        # block, and the only "repair" would rewrite a sealed governance record
        # under an attestation no operator can honestly give.
        result = self._reconcile("attested_completed")
        self.assertEqual(result.allowlist_delta.missing_on_disk, ["src/gzkit/renamed_away_zzz.py"])
        self.assertFalse(result.has_drift)

    @covers("REQ-0.0.37-05-02")
    def test_live_brief_with_the_same_body_still_drifts(self):
        # Negative control: the scoping must key on status, not on the path. An
        # identical Active brief is a live claim and must fail closed.
        #
        # This drew its contrast on `Draft` until GHI #615. That over-reached:
        # a Draft brief's Allowed Paths name what the OBPI will CREATE, so their
        # absence is its expected state -- `OBPI-0.0.42-02-storybook-cli` cites
        # `gz storybook` because it is the OBPI that lands that verb. Measured
        # across the corpus, all 68 drifting briefs were Draft and every finding
        # was a brief naming its own unbuilt deliverable; none was drift.
        # `Active` carries the "work has begun, paths should now exist" claim
        # this control is actually about.
        result = self._reconcile("Active")
        self.assertEqual(result.allowlist_delta.missing_on_disk, ["src/gzkit/renamed_away_zzz.py"])
        self.assertTrue(result.has_drift)

    @covers("REQ-0.0.37-05-02")
    def test_unstarted_brief_does_not_gate_on_deliverable_paths(self):
        # The narrowing, stated positively: a Draft brief's missing Allowed Path
        # is still REPORTED (the delta is real information) but does not gate.
        result = self._reconcile("Draft")
        self.assertEqual(result.allowlist_delta.missing_on_disk, ["src/gzkit/renamed_away_zzz.py"])
        self.assertTrue(result.unstarted)
        self.assertFalse(result.has_drift)

    @covers("REQ-0.0.37-05-02")
    def test_unstarted_brief_still_gates_on_prerequisite_paths(self):
        # The fence on that narrowing: Discovery Checklist entries are genuine
        # prerequisites -- they must exist BEFORE work starts -- so a Draft brief
        # gates on them. Without this, "unstarted" would become the blanket
        # exemption `terminal` is, and the dimension distinction would be prose.
        body = textwrap.dedent("""\
            ---
            id: OBPI-0.1.0-78-unstarted
            parent: ADR-0.1.0-f
            item: 78
            lane: Lite
            status: Draft
            ---

            # OBPI-0.1.0-78-unstarted: Unstarted

            ## Discovery Checklist

            - [ ] Required path exists: `src/gzkit/absent_prerequisite_zzz.py`
            """)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = root / "brief.md"
            brief.write_text(body, encoding="utf-8")
            result = reconcile_brief(brief, root)
        self.assertEqual(
            result.discovery_delta.unresolved_paths, ["src/gzkit/absent_prerequisite_zzz.py"]
        )
        self.assertTrue(result.has_drift)


class TestAllowlistDimension(unittest.TestCase):
    @covers("REQ-0.0.37-05-02")
    def test_missing_on_disk_reported(self):
        result = reconcile_brief(FIXTURES / "allowlist_drift.md", PROJECT_ROOT)
        self.assertIn(
            "src/gzkit/governance/nonexistent_module.py",
            result.allowlist_delta.missing_on_disk,
        )
        self.assertTrue(result.has_drift)

    @covers("REQ-0.0.37-05-02")
    def test_allowlist_glob_path_not_existence_checked(self):
        # Sibling gap to GHI #626 Component 2: _compute_discovery_delta skips
        # glob metacharacter paths (test_discovery_glob_path_not_existence_checked
        # above), but _compute_allowlist_delta had no equivalent guard — an
        # Allowed Paths entry like `docs/design/adr/foundation/**` was falsely
        # reported as missing_on_disk, since `(root / "dir/**").exists()` is
        # always False for a literal glob string.
        from gzkit.governance.brief_reconcile import _compute_allowlist_delta

        delta = _compute_allowlist_delta(["docs/design/adr/foundation/**"], [], PROJECT_ROOT)
        self.assertEqual(delta.missing_on_disk, [])

    @covers("REQ-0.0.37-05-02")
    def test_creates_declared_path_exempt_from_missing_on_disk(self):
        """A net-new path declared under '## Creates These Files' is exempt from
        missing_on_disk (GHI #419 brief-creates exemption).

        The reconcile engine must honor the same creates-declaration that
        brief_path_validity already honors, so a net-new-file OBPI is not
        falsely flagged as drifted at Stage-2 entry (the deadlock this fix
        resolves).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brief = root / "brief.md"
            brief.write_text(
                textwrap.dedent("""\
                    ---
                    id: OBPI-0.0.99-02-creates-exempt
                    parent: ADR-0.0.37-constitutional-invariant-composition
                    lane: Heavy
                    status: Draft
                    allowlist:
                      - src/gzkit/governance/brand_new_module.py
                    reqs:
                      - REQ-0.0.99-02-01
                    verification:
                      - uv run gz validate
                    citations: []
                    ---
                    # Test Brief: Creates Exempt
                    ## Allowed Paths
                    - `src/gzkit/governance/brand_new_module.py`
                    ## Creates These Files
                    - `src/gzkit/governance/brand_new_module.py` — NEW module this OBPI creates
                    ## Verification
                    ```bash
                    uv run gz validate
                    ```
                    ## Requirements (FAIL-CLOSED)
                    REQUIREMENT: Test requirement one
                    ## Acceptance Criteria
                    - [ ] REQ-0.0.99-02-01: test
                    """),
                encoding="utf-8",
            )
            result = reconcile_brief(brief, root)
            self.assertNotIn(
                "src/gzkit/governance/brand_new_module.py",
                result.allowlist_delta.missing_on_disk,
            )
            self.assertFalse(result.has_drift)


class TestNonPathTokenRejection(unittest.TestCase):
    """GHI #626 sibling — reconcile existence-checks must reject backtick tokens
    that satisfy the crude `/`-and-`.` heuristic but are code, not filesystem
    paths: `Path("...")` call literals (allowlist-description FP) and
    `module.py::symbol` references (discovery Existing-Code FP). Both deadlock
    the Stage-2 reconcile gate on a convention-correct brief."""

    def test_looks_like_path_rejects_code_and_symbol_tokens(self):
        from gzkit.governance.brief_reconcile import _looks_like_path

        self.assertFalse(_looks_like_path('Path(".gzkit/handoffs")'))
        self.assertFalse(
            _looks_like_path("scripts/session_orientation.py::_candidate_handoff_dirs")
        )
        self.assertFalse(_looks_like_path("collect_handoff('x')"))
        # Regression guard: real project-relative paths still admitted.
        self.assertTrue(_looks_like_path("scripts/session_orientation.py"))
        self.assertTrue(_looks_like_path("src/gzkit/governance/brief_reconcile.py"))
        self.assertTrue(_looks_like_path("tests/scripts/test_session_orientation.py"))

    @covers("REQ-0.0.37-05-02")
    def test_allowlist_code_literal_in_description_not_extracted(self):
        # The Allowed Paths convention is "first backtick token is the path";
        # a `Path(".gzkit/handoffs")` code literal in the bullet DESCRIPTION must
        # not be extracted and existence-checked as a second allowlist path.
        from gzkit.governance.brief_reconcile import _ALLOWED_HEADING_RE, _extract_section_paths

        body = textwrap.dedent(
            """\
            ## Allowed Paths

            - `scripts/session_orientation.py` — collapse to `Path(".gzkit/handoffs")`
            - `tests/scripts/test_session_orientation.py` — extend the test module
            """
        )
        paths = _extract_section_paths(body, _ALLOWED_HEADING_RE)
        self.assertEqual(
            paths,
            ["scripts/session_orientation.py", "tests/scripts/test_session_orientation.py"],
        )

    @covers("REQ-0.0.37-05-01")
    def test_discovery_symbol_reference_not_existence_checked(self):
        # `module.py::symbol` in the Existing-Code discovery sub-section is a code
        # symbol, not a path; `(root / "x.py::func").exists()` is always False, so
        # it must not be reported as unresolved discovery drift.
        from gzkit.governance.brief_reconcile import _compute_discovery_delta

        body = textwrap.dedent(
            """\
            ## Discovery Checklist

            - [ ] Read `scripts/session_orientation.py::_candidate_handoff_dirs`
            - [ ] Read `scripts/session_orientation.py::collect_handoff`
            """
        )
        delta = _compute_discovery_delta(body, PROJECT_ROOT)
        self.assertEqual(delta.unresolved_paths, [])


class TestDiscoveryNonClaimRows(unittest.TestCase):
    """GHI #615 — a Discovery bullet is only drift evidence when it *claims the
    path exists*. The dimension existence-checks every backtick token in the
    section regardless of what the row says about it, so three row shapes the
    corpus already uses fail by construction: a row asserting the path is
    ABSENT, a row that is explicitly CONDITIONAL, and a row that explicitly
    HEDGES the location. Repairing the briefs to satisfy the scraper would
    encode the scraper's misreading into the governance artifact; the row
    semantics are what must be read."""

    @covers("REQ-0.0.37-05-01")
    def test_absence_assertion_row_not_reported(self):
        # `OBPI-0.0.49-01` states the OBPI is CREATING the skill directory, so the
        # row asserts the path does not exist. Reporting it as unresolved fails the
        # brief for being correct about its own starting state.
        from gzkit.governance.brief_reconcile import _compute_discovery_delta

        body = textwrap.dedent(
            """\
            ## Discovery Checklist

            - [ ] No existing `.gzkit/skills/gz-absent-zzz/` directory (the OBPI is creating it)
            """
        )
        delta = _compute_discovery_delta(body, PROJECT_ROOT)
        self.assertEqual(delta.unresolved_paths, [])

    @covers("REQ-0.0.37-05-01")
    def test_conditional_row_not_reported(self):
        # `(if present)` states the author does not know whether the artifact
        # exists — the row is a conditional read instruction, not an assertion.
        from gzkit.governance.brief_reconcile import _compute_discovery_delta

        body = textwrap.dedent(
            """\
            ## Discovery Checklist

            - [ ] `docs/governance/absent-doctrine-zzz.md` (if present)
            - [ ] Existing helpers (if any) under `src/gzkit/absent_pkg_zzz/`
            """
        )
        delta = _compute_discovery_delta(body, PROJECT_ROOT)
        self.assertEqual(delta.unresolved_paths, [])

    @covers("REQ-0.0.37-05-01")
    def test_hedged_location_row_not_reported(self):
        # `or equivalent` names a guess at the location, not the location. The
        # brief is instructing the implementer to go find it.
        from gzkit.governance.brief_reconcile import _compute_discovery_delta

        body = textwrap.dedent(
            """\
            ## Discovery Checklist

            - [ ] Persona schema in `src/gzkit/absent_module_zzz.py` (or equivalent)
            - [ ] Pipeline registration (find in `src/gzkit/absent_dir_zzz/` or equivalent)
            """
        )
        delta = _compute_discovery_delta(body, PROJECT_ROOT)
        self.assertEqual(delta.unresolved_paths, [])

    @covers("REQ-0.0.37-05-01")
    def test_multi_range_line_citation_is_not_a_path(self):
        # `_LINE_RANGE_SUFFIX_RE` anchors a SINGLE trailing range, so the
        # multi-range spelling the corpus uses (`config.py:26-60, 106-107`) falls
        # through and is existence-checked as a filename. Same class as the
        # single-range citation already rejected.
        from gzkit.governance.brief_reconcile import _looks_like_path

        self.assertFalse(_looks_like_path("src/gzkit/config.py:26-60, 106-107"))
        self.assertFalse(_looks_like_path("src/gzkit/config.py:26-60,106-107"))
        self.assertFalse(_looks_like_path("src/gzkit/config.py:26-60"))
        self.assertFalse(_looks_like_path("src/gzkit/config.py:26"))
        # Regression guard: a real path is still admitted.
        self.assertTrue(_looks_like_path("src/gzkit/config.py"))

    @covers("REQ-0.0.37-05-01")
    def test_plain_missing_row_still_reported(self):
        # Negative control — the narrowing is scoped to rows that disclaim the
        # existence assertion. An unqualified row naming a path that is not there
        # is exactly the dead citation the dimension exists to catch, and it must
        # keep failing closed. Without this the fix would blind the dimension.
        from gzkit.governance.brief_reconcile import _compute_discovery_delta

        body = textwrap.dedent(
            """\
            ## Discovery Checklist

            - [ ] `src/gzkit/cli/absent_validate_zzz.py` — existing flag registration
            """
        )
        delta = _compute_discovery_delta(body, PROJECT_ROOT)
        self.assertEqual(delta.unresolved_paths, ["src/gzkit/cli/absent_validate_zzz.py"])

    @covers("REQ-0.0.37-05-01")
    def test_non_claim_marker_does_not_leak_across_rows(self):
        # Negative control — the disclaimer is a property of the ROW that carries
        # it. A hedged row must not exempt an unhedged sibling row in the same
        # section, or one `(if present)` would silence a whole checklist.
        from gzkit.governance.brief_reconcile import _compute_discovery_delta

        body = textwrap.dedent(
            """\
            ## Discovery Checklist

            - [ ] `docs/governance/absent-doctrine-zzz.md` (if present)
            - [ ] `src/gzkit/absent_real_drift_zzz.py` — the helper this OBPI calls
            """
        )
        delta = _compute_discovery_delta(body, PROJECT_ROOT)
        self.assertEqual(delta.unresolved_paths, ["src/gzkit/absent_real_drift_zzz.py"])


class TestDeniedPathsAreNotAllowlistGaps(unittest.TestCase):
    """GHI #615 — `missing_in_brief` reports src/ modules a brief's REQ tests
    import but its Allowed Paths omit, as evidence the OBPI leaked into a
    neighbouring module. It reads `## Allowed Paths` alone, so a path the brief
    explicitly DENIES is reported as an allowlist gap: the author who wrote
    "NEVER touch this" is told they forgot to declare it. The adjacent section
    already answers the question."""

    @covers("REQ-0.0.37-05-02")
    def test_explicitly_denied_path_is_not_reported_as_gap(self):
        from gzkit.governance.brief_reconcile import _compute_allowlist_delta

        body = textwrap.dedent(
            """\
            ## Allowed Paths

            - `src/gzkit/governance/brief_reconcile.py` — the engine under change

            ## Denied Paths

            - `src/gzkit/quality.py` — the `gz check` pipeline is a sibling OBPI's scope
            """
        )
        delta = _compute_allowlist_delta(
            ["src/gzkit/governance/brief_reconcile.py"],
            [],
            PROJECT_ROOT,
            denied_paths={"src/gzkit/quality.py"},
        )
        self.assertNotIn("src/gzkit/quality.py", delta.missing_in_brief)
        self.assertIn("## Denied Paths", body)

    @covers("REQ-0.0.37-05-02")
    def test_undeclared_neighbour_still_reported(self):
        # Negative control — the exclusion is scoped to paths the brief DENIES.
        # A module that is neither allowed nor denied is the genuine leakage
        # signal this dimension exists to surface, and must keep reporting.
        from gzkit.governance.brief_reconcile import _extract_denied_paths

        body = textwrap.dedent(
            """\
            ## Allowed Paths

            - `src/gzkit/governance/brief_reconcile.py` — the engine under change

            ## Denied Paths

            - `src/gzkit/quality.py` — sibling OBPI scope
            """
        )
        denied = _extract_denied_paths(body)
        self.assertIn("src/gzkit/quality.py", denied)
        self.assertNotIn("src/gzkit/triangle.py", denied)


class TestVerificationVerbDimension(unittest.TestCase):
    @covers("REQ-0.0.37-05-03")
    def test_unregistered_verb_reported(self):
        result = reconcile_brief(FIXTURES / "verb_drift.md", PROJECT_ROOT)
        self.assertIn("nonexistentverb", result.verification_delta.unresolved_verbs)
        self.assertTrue(result.has_drift)

    @covers("REQ-0.0.37-05-03")
    def test_registered_verb_not_reported(self):
        result = reconcile_brief(FIXTURES / "passing.md", PROJECT_ROOT)
        self.assertNotIn("validate", result.verification_delta.unresolved_verbs)


class TestReqCountDimension(unittest.TestCase):
    @covers("REQ-0.0.37-05-04")
    def test_delta_non_zero_on_mismatch(self):
        result = reconcile_brief(FIXTURES / "req_count_drift.md", PROJECT_ROOT)
        self.assertNotEqual(result.req_count_delta.delta, 0)
        # GHI #581: the delta is reported (advisory) but req_count alone no longer
        # sets has_drift — it is the crude heuristic that fail-closed valid work.
        self.assertFalse(result.has_drift)

    @covers("REQ-0.0.37-05-04")
    def test_delta_zero_on_match(self):
        result = reconcile_brief(FIXTURES / "passing.md", PROJECT_ROOT)
        self.assertEqual(result.req_count_delta.delta, 0)

    @covers("REQ-0.0.37-05-04")
    def test_delta_zero_on_kind_tag_format(self):
        # REQUIREMENT [BEHAVIOR]: / REQUIREMENT [SUPPORT]: format (ADR-0.0.59
        # kind-discipline) must be counted the same as REQUIREMENT:
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                textwrap.dedent("""\
                    ---
                    id: OBPI-0.0.99-05-kind-tag
                    parent: ADR-0.0.37-constitutional-invariant-composition
                    status: Draft
                    ---
                    # Test Brief: Kind Tag REQ Format
                    ## Requirements (FAIL-CLOSED)
                    1. REQUIREMENT [BEHAVIOR]: behavior requirement
                    1. REQUIREMENT [SUPPORT]: support requirement
                    ## Acceptance Criteria
                    - [ ] REQ-0.0.99-05-01: criterion one
                    - [ ] REQ-0.0.99-05-02: criterion two
                    """),
                encoding="utf-8",
            )
            result = reconcile_brief(brief, PROJECT_ROOT)
            self.assertEqual(result.req_count_delta.delta, 0)

    @covers("REQ-0.0.37-05-04")
    def test_delta_zero_on_never_always_tags(self):
        # NEVER:/ALWAYS: FAIL-CLOSED lines are requirements too (GHI #664) —
        # a brief whose three-way taxonomy fully accounts for its Acceptance
        # Criteria must not report false drift.
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                textwrap.dedent("""\
                    ---
                    id: OBPI-0.0.99-06-never-always-tags
                    parent: ADR-0.0.37-constitutional-invariant-composition
                    status: Draft
                    ---
                    # Test Brief: NEVER/ALWAYS FAIL-CLOSED Tags
                    ## Requirements (FAIL-CLOSED)
                    1. REQUIREMENT: positive requirement
                    2. NEVER: prohibition
                    3. ALWAYS: invariant
                    ## Acceptance Criteria
                    - [ ] REQ-0.0.99-06-01: criterion one
                    - [ ] REQ-0.0.99-06-02: criterion two
                    - [ ] REQ-0.0.99-06-03: criterion three
                    """),
                encoding="utf-8",
            )
            result = reconcile_brief(brief, PROJECT_ROOT)
            self.assertEqual(result.req_count_delta.delta, 0)

    @covers("REQ-0.0.37-05-04")
    def test_delta_zero_on_checked_boxes(self):
        # A completed brief has its Acceptance Criteria boxes checked ([x]),
        # not unchecked ([ ]) — the dimension must still count them (GHI #664).
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                textwrap.dedent("""\
                    ---
                    id: OBPI-0.0.99-06-checked-boxes
                    parent: ADR-0.0.37-constitutional-invariant-composition
                    status: Completed
                    ---
                    # Test Brief: Checked Acceptance Criteria Boxes
                    ## Requirements (FAIL-CLOSED)
                    1. REQUIREMENT: req one
                    2. REQUIREMENT: req two
                    ## Acceptance Criteria
                    - [x] REQ-0.0.99-06-04: criterion one
                    - [X] REQ-0.0.99-06-05: criterion two
                    """),
                encoding="utf-8",
            )
            result = reconcile_brief(brief, PROJECT_ROOT)
            self.assertEqual(result.req_count_delta.delta, 0)

    @covers("REQ-0.0.37-05-04")
    def test_legacy_brief_is_unmeasurable_not_drifted(self):
        # GHI #664 round 2: a legacy brief declares REQ identity nowhere — its
        # Requirements section carries prose fences with no REQ-IDs (635 of 668
        # corpus briefs). Counting fence lines against checkboxes is a category
        # error: a `NEVER:` fence is not a declared REQ. With no independent
        # declaration to compare against, the dimension must report itself
        # unmeasurable rather than fabricate a numeric proxy.
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                textwrap.dedent("""\
                    ---
                    id: OBPI-0.0.99-07-legacy-fences
                    parent: ADR-0.0.37-constitutional-invariant-composition
                    status: Draft
                    ---
                    # Test Brief: Legacy Fences Outnumber REQs
                    ## Requirements (FAIL-CLOSED)
                    1. REQUIREMENT: positive requirement
                    2. NEVER: scope fence that maps to no REQ
                    3. NEVER: sibling-denial fence that maps to no REQ
                    4. ALWAYS: process fence that maps to no REQ
                    ## Acceptance Criteria
                    - [ ] REQ-0.0.99-07-01: the only real criterion
                    """),
                encoding="utf-8",
            )
            result = reconcile_brief(brief, PROJECT_ROOT)
            self.assertFalse(result.req_count_delta.measurable)
            self.assertEqual(result.req_count_delta.delta, 0)
            self.assertEqual(result.req_count_delta.missing_reqs, [])
            self.assertEqual(result.req_count_delta.unexpected_reqs, [])

    @covers("REQ-0.0.37-05-04")
    def test_structured_brief_reports_req_identity_not_line_counts(self):
        # GHI #664 round 2: for a structured brief, frontmatter `reqs:` IS an
        # independent declaration of REQ identity, so the dimension compares
        # id SETS. Counts alone cannot distinguish "declared A, accepted B"
        # from a correct 1:1 brief — identity can.
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                textwrap.dedent("""\
                    ---
                    id: OBPI-0.0.99-08-identity
                    parent: ADR-0.0.37-constitutional-invariant-composition
                    lane: Heavy
                    status: Draft
                    allowlist:
                      - src/gzkit/governance/brief_reconcile.py
                    reqs:
                      - REQ-0.0.99-08-01
                      - REQ-0.0.99-08-02
                    verification:
                      - uv run gz validate
                    citations: []
                    ---
                    # Test Brief: REQ Identity
                    ## Requirements (FAIL-CLOSED)
                    1. REQUIREMENT: declared two, accepted two — but not the same two
                    ## Acceptance Criteria
                    - [ ] REQ-0.0.99-08-01: matches a declared REQ
                    - [ ] REQ-0.0.99-08-99: was never declared
                    """),
                encoding="utf-8",
            )
            result = reconcile_brief(brief, PROJECT_ROOT)
            self.assertTrue(result.req_count_delta.measurable)
            # Counts are equal (2 vs 2) — only identity comparison catches this.
            self.assertEqual(result.req_count_delta.missing_reqs, ["REQ-0.0.99-08-02"])
            self.assertEqual(result.req_count_delta.unexpected_reqs, ["REQ-0.0.99-08-99"])
            self.assertNotEqual(result.req_count_delta.delta, 0)


class TestCitationDimension(unittest.TestCase):
    @covers("REQ-0.0.37-05-05")
    def test_stale_citation_reported(self):
        result = reconcile_brief(FIXTURES / "citation_drift.md", PROJECT_ROOT)
        artifact_paths = [c[0] for c in result.citation_delta.stale_citations]
        self.assertIn("docs/does-not-exist-anywhere.md", artifact_paths)
        self.assertTrue(result.has_drift)

    @covers("REQ-0.0.37-05-05")
    def test_no_stale_citation_on_empty_citations(self):
        result = reconcile_brief(FIXTURES / "passing.md", PROJECT_ROOT)
        self.assertEqual(result.citation_delta.stale_citations, [])


class TestEnginePurity(unittest.TestCase):
    @covers("REQ-0.0.37-05-07")
    def test_no_files_written(self):
        mtime_before = {
            f: os.path.getmtime(f)
            for f in [
                str(FIXTURES / "passing.md"),
            ]
        }
        reconcile_brief(FIXTURES / "passing.md", PROJECT_ROOT)
        for f, mtime in mtime_before.items():
            self.assertEqual(os.path.getmtime(f), mtime, f"File {f} was modified")

    @covers("REQ-0.0.37-05-07")
    def test_no_ledger_writes(self):
        # REQ-0.0.37-05-07 also forbids ledger emission; that belongs to OBPI-06.
        ledger = PROJECT_ROOT / ".gzkit" / "ledger.jsonl"
        mtime_before = os.path.getmtime(ledger) if ledger.exists() else None
        reconcile_brief(FIXTURES / "passing.md", PROJECT_ROOT)
        if mtime_before is not None:
            self.assertEqual(
                os.path.getmtime(ledger),
                mtime_before,
                "Engine wrote to the ledger; emission belongs to OBPI-06",
            )


class TestMissingInBrief(unittest.TestCase):
    """Allowlist dimension — missing_in_brief with the neighborhood filter."""

    def _build_tree(self, tmp: Path) -> Path:
        # src tree: foo/a.py (allowlisted), foo/b.py (sibling), util.py (cross-cutting)
        for rel in ("src/gzkit/foo/a.py", "src/gzkit/foo/b.py", "src/gzkit/util.py"):
            p = tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# stub\n", encoding="utf-8")
        # A REQ test importing a sibling-neighborhood module AND a cross-cutting one.
        test_file = tmp / "tests" / "test_x.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            textwrap.dedent("""\
                from gzkit.foo.b import thing  # sibling of allowlisted foo/a.py
                from gzkit.util import helper   # cross-cutting test utility

                @covers("REQ-9.9.9-01-01")
                def test_something():
                    pass
                """),
            encoding="utf-8",
        )
        brief = tmp / "docs/design/adr/foundation/ADR-9.9.9-x/obpis/OBPI-9.9.9-01-x.md"
        _write_structured_brief(
            brief,
            brief_id="OBPI-9.9.9-01-x",
            parent="ADR-9.9.9-x",
            reqs=["REQ-9.9.9-01-01"],
            allowlist=["src/gzkit/foo/a.py"],
        )
        return brief

    @covers("REQ-0.0.37-05-02")
    def test_sibling_module_reported_as_missing_in_brief(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            brief = self._build_tree(tmp)
            result = reconcile_brief(brief, tmp)
            self.assertIn("src/gzkit/foo/b.py", result.allowlist_delta.missing_in_brief)

    @covers("REQ-0.0.37-05-02")
    def test_cross_cutting_import_excluded_by_neighborhood_filter(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            brief = self._build_tree(tmp)
            result = reconcile_brief(brief, tmp)
            # util.py is in src/gzkit/, not a neighborhood of src/gzkit/foo/ —
            # the cross-cutting utility import must not be flagged.
            self.assertNotIn("src/gzkit/util.py", result.allowlist_delta.missing_in_brief)

    def _build_tree_toplevel_allowlist(self, tmp: Path) -> Path:
        """A brief allowlisting a TOP-LEVEL src/gzkit/*.py file, plus a REQ test
        importing the @covers infra from gzkit.traceability.

        This is the OBPI-0.0.74-06 shape: once a top-level src/gzkit/ module is
        allowlisted, src/gzkit/ becomes a neighborhood and the neighborhood
        filter alone leaks the cross-cutting @covers infra (traceability.py).
        """
        for rel in ("src/gzkit/events.py", "src/gzkit/traceability.py"):
            p = tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# stub\n", encoding="utf-8")
        test_file = tmp / "tests" / "test_y.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            textwrap.dedent("""\
                from gzkit.events import MxSessionOpenedEvent  # allowlisted top-level module
                from gzkit.traceability import covers          # cross-cutting @covers infra

                @covers("REQ-9.9.9-01-01")
                def test_something():
                    pass
                """),
            encoding="utf-8",
        )
        brief = tmp / "docs/design/adr/foundation/ADR-9.9.9-x/obpis/OBPI-9.9.9-01-x.md"
        _write_structured_brief(
            brief,
            brief_id="OBPI-9.9.9-01-x",
            parent="ADR-9.9.9-x",
            reqs=["REQ-9.9.9-01-01"],
            allowlist=["src/gzkit/events.py"],
        )
        return brief

    @covers("REQ-0.0.37-05-02")
    def test_traceability_infra_excluded_even_when_toplevel_module_allowlisted(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            brief = self._build_tree_toplevel_allowlist(tmp)
            result = reconcile_brief(brief, tmp)
            # gzkit.traceability is the @covers decorator infra — never a
            # subject-under-test. It must NOT be flagged even when a top-level
            # src/gzkit/*.py file is allowlisted (which makes src/gzkit/ a
            # neighborhood of traceability.py). GHI #645.
            self.assertNotIn("src/gzkit/traceability.py", result.allowlist_delta.missing_in_brief)

    def _build_infra_variant_tree(self, tmp: Path) -> None:
        """src stubs + a REQ test importing package-init infra (``gzkit.schemas``
        -> ``schemas/__init__.py``), the cross-cutting ``gzkit.config`` loader,
        AND a genuine domain sibling (``gzkit.ledger``). Mirrors OBPI-0.32.0-06's
        false-positive shape: with ``events.py`` (parent ``src/gzkit``) and an
        in-package file allowlisted, the neighborhood filter leaks the infra
        imports. Exercises ``_compute_missing_in_brief`` directly to isolate the
        exemption from unrelated brief-frontmatter parsing."""
        for rel in (
            "src/gzkit/events.py",
            "src/gzkit/config.py",
            "src/gzkit/ledger.py",
            "src/gzkit/schemas/__init__.py",
            "src/gzkit/schemas/work_edges.json",
        ):
            p = tmp / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# stub\n", encoding="utf-8")
        test_file = tmp / "tests" / "test_z.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            textwrap.dedent("""\
                from gzkit.events import MxSessionOpenedEvent  # allowlisted top-level
                from gzkit.schemas import load_schema          # package-init infra
                from gzkit.config import load_config           # cross-cutting loader
                from gzkit.ledger import Ledger                # GENUINE domain sibling

                @covers("REQ-9.9.9-01-01")
                def test_something():
                    pass
                """),
            encoding="utf-8",
        )

    # allowlist that makes both src/gzkit (via events.py) and src/gzkit/schemas
    # (via work_edges.json) neighborhoods, leaking the infra imports pre-fix.
    _INFRA_ALLOWLIST = ["src/gzkit/events.py", "src/gzkit/schemas/work_edges.json"]

    @covers("REQ-0.0.37-05-02")
    def test_package_init_marker_excluded_from_missing_in_brief(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            self._build_infra_variant_tree(tmp)
            missing = _compute_missing_in_brief(["REQ-9.9.9-01-01"], self._INFRA_ALLOWLIST, tmp)
            # A package __init__.py is never a subject-under-test — importing a
            # symbol FROM a package resolves to __init__.py, but the real subject
            # is defined elsewhere. It must not be flagged even in-neighborhood.
            self.assertNotIn("src/gzkit/schemas/__init__.py", missing)

    @covers("REQ-0.0.37-05-02")
    def test_config_loader_infra_excluded_from_missing_in_brief(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            self._build_infra_variant_tree(tmp)
            missing = _compute_missing_in_brief(["REQ-9.9.9-01-01"], self._INFRA_ALLOWLIST, tmp)
            # gzkit.config is a cross-cutting path/loader utility (a sibling of the
            # @covers infra) — imported for infra, never the OBPI's subject.
            self.assertNotIn("src/gzkit/config.py", missing)

    @covers("REQ-0.0.37-05-02")
    def test_genuine_domain_sibling_still_flagged_alongside_infra(self):
        # Negative control (surgical exemption): the infra exemption MUST NOT
        # suppress a genuine domain coupling. gzkit.ledger is a real subject —
        # it stays flagged even as config.py / schemas/__init__.py are excluded.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            self._build_infra_variant_tree(tmp)
            missing = _compute_missing_in_brief(["REQ-9.9.9-01-01"], self._INFRA_ALLOWLIST, tmp)
            self.assertIn("src/gzkit/ledger.py", missing)


class TestValidateBriefReconcile(unittest.TestCase):
    """Validator wrapper — structured-brief-only escalation (CIC-2 permissive mode)."""

    @covers("REQ-0.0.37-05-06")
    def test_clean_repo_tree_has_no_errors(self):
        # The live project tree's one structured brief (OBPI-0.0.37-04) is clean.
        errors = validate_brief_reconcile(PROJECT_ROOT)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.37-05-06")
    def test_structured_brief_with_drift_escalates(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            brief = tmp / "docs/design/adr/foundation/ADR-9.9.9-d/obpis/OBPI-9.9.9-02-d.md"
            _write_structured_brief(
                brief,
                brief_id="OBPI-9.9.9-02-d",
                parent="ADR-9.9.9-d",
                reqs=["REQ-9.9.9-02-01"],
                allowlist=["src/gzkit/does_not_exist.py"],
            )
            errors = validate_brief_reconcile(tmp)
            self.assertTrue(errors, "structured brief with drift must escalate")
            self.assertTrue(all(e.type == "brief_reconcile" for e in errors))

    @covers("REQ-0.0.37-05-06")
    def test_legacy_brief_with_drift_is_not_escalated(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            brief = tmp / "docs/design/adr/foundation/ADR-9.9.9-l/obpis/OBPI-9.9.9-09-l.md"
            _write_legacy_brief(
                brief,
                brief_id="OBPI-9.9.9-09-l",
                allowlist=["src/gzkit/also_missing.py"],
            )
            errors = validate_brief_reconcile(tmp)
            self.assertEqual(errors, [], "legacy briefs are exempt under CIC-2 permissive mode")


if __name__ == "__main__":
    unittest.main()
