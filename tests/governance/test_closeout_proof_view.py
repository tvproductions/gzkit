"""RED-phase tests for closeout-proof derived view (OBPI-0.0.69-03).

All tests in this file MUST fail until
``gzkit.governance.trust_audits.closeout_proof`` is authored (RED phase).
The top-level import raises ``ImportError``, which fails every test at
module-load time.

Covers:
    REQ-0.0.69-03-01 — exit semantics: [] (exit 0) when all proven,
        non-empty (exit 3) when any unproven; no reading from stored blocks.
    REQ-0.0.69-03-02 — failed SUPPORT REQ message includes exact re-run
        command (``uv run gz validate --<scope>``); does NOT inline stderr.
    REQ-0.0.69-03-03 — --closeout-proof in gz check default pipeline;
        dispatched at most once per run.
    REQ-0.0.69-03-07 — REQ with no [kind] tag is reported unproven.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC
from pathlib import Path

# This import raises ImportError until closeout_proof.py is created.
# Every test in this file fails RED as required.
from gzkit.governance.trust_audits.closeout_proof import validate_closeout_proof
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write_ceremony(project_root: Path, adr_id: str, *, completed: bool = False) -> None:
    """Write a ceremony state file; completed=False signals closeout in progress.

    The ``updated_at`` is stamped to now so the gz-check sweep treats this as an
    *active* closeout (the freshness gate excludes parked ceremonies older than
    ``_ACTIVE_CLOSEOUT_WINDOW_HOURS``).
    """
    from datetime import datetime

    ceremonies_dir = project_root / ".gzkit" / "ceremonies"
    ceremonies_dir.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(UTC).isoformat()
    path = ceremonies_dir / f"{adr_id}.ceremony.json"
    path.write_text(
        json.dumps(
            {
                "adr_id": adr_id,
                "current_step": 6,
                "started_at": now_iso,
                "updated_at": now_iso,
                "completed_at": "2026-01-02T00:00:00Z" if completed else None,
            }
        ),
        encoding="utf-8",
    )


def _make_adr_dir(project_root: Path, adr_id: str) -> Path:
    adr_dir = project_root / "docs" / "design" / "adr" / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    return adr_dir


def _write_brief(adr_dir: Path, obpi_id: str, ac_lines: list[str]) -> None:
    """Write a brief whose Acceptance Criteria section contains ac_lines."""
    import yaml  # noqa: PLC0415 — yaml is a transitive pydantic dependency

    obpis_dir = adr_dir / "obpis"
    obpis_dir.mkdir(parents=True, exist_ok=True)
    brief_path = obpis_dir / f"{obpi_id}.md"

    fm: dict = {"id": obpi_id, "parent": adr_dir.name, "lane": "Heavy", "status": "Draft"}
    fm_text = yaml.dump(fm, default_flow_style=False)
    ac_block = "\n".join(f"- [ ] {line}" for line in ac_lines)
    body = f"# {obpi_id}\n\n## Acceptance Criteria\n\n{ac_block}\n"
    brief_path.write_text(f"---\n{fm_text}---\n\n{body}", encoding="utf-8")


def _write_covers_test(project_root: Path, req_id: str) -> None:
    """Write a minimal test file that declares @covers for req_id."""
    tests_dir = project_root / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    slug = req_id.replace("-", "_").replace(".", "_").lower()
    (tests_dir / f"test_{slug}.py").write_text(
        f"from gzkit.traceability import covers\n\n"
        f'@covers("{req_id}")\n'
        f"def test_placeholder(): pass\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# REQ-0.0.69-03-01: exit semantics
# ---------------------------------------------------------------------------


class TestCloseoutProofExitCodes(unittest.TestCase):
    """REQ-0.0.69-03-01 — validate_closeout_proof exit-code semantics.

    Returns [] (maps to exit 0) when all REQs are proven.
    Returns non-empty list (exit 3) when any REQ is unproven.
    Never reads from stored proof blocks — result is always freshly computed.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.69-03-01")
    def test_no_in_closeout_ceremony_returns_empty_list(self) -> None:
        """No in-progress ceremony → no in-closeout ADRs → empty list (exit 0)."""
        errors = validate_closeout_proof(self.root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.69-03-01")
    def test_unproven_behavior_req_returns_errors_exit_3(self) -> None:
        """BEHAVIOR REQ without a @covers test → unproven → non-empty list (exit 3)."""
        adr_id = "ADR-0.0.99-exit-codes"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-test",
            ["REQ-0.0.99-01-01 [BEHAVIOR]: system does X"],
        )
        # No test file cites this REQ, so it is unproven. Phrased without the
        # decorator spelling on purpose: the covers scanner honors comment form,
        # so a comment naming the decorator reads as a citation (GHI #729).

        errors = validate_closeout_proof(self.root)

        self.assertGreater(len(errors), 0, "Unproven BEHAVIOR REQ must produce non-empty list")
        self.assertIn("closeout_proof", {e.type for e in errors})

    @covers("REQ-0.0.69-03-01")
    def test_proven_behavior_req_returns_empty_list(self) -> None:
        """BEHAVIOR REQ with a @covers test present → proven → empty list (exit 0)."""
        adr_id = "ADR-0.0.99-exit-codes"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-test",
            ["REQ-0.0.99-01-01 [BEHAVIOR]: system does X"],
        )
        _write_covers_test(self.root, "REQ-0.0.99-01-01")

        errors = validate_closeout_proof(self.root)

        self.assertEqual(errors, [], f"Proven BEHAVIOR REQ must return empty list; got: {errors}")

    @covers("REQ-0.0.69-03-01")
    def test_result_independent_of_stored_proof_blocks(self) -> None:
        """Proof is freshly recomputed — no stored proof blocks exist or are consulted.

        Calling validate_closeout_proof twice on the same root without any
        stored .closeout_proof.json blocks must produce consistent results,
        confirming that computation is live-channel-driven, not read from disk.
        """
        adr_id = "ADR-0.0.99-exit-codes"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-test",
            ["REQ-0.0.99-01-01 [BEHAVIOR]: system does X"],
        )
        stored = list(self.root.rglob("*.closeout_proof.json"))
        self.assertEqual(stored, [], "Precondition: no stored proof blocks in temp root")

        first = validate_closeout_proof(self.root)
        second = validate_closeout_proof(self.root)

        self.assertEqual(
            [e.type for e in first],
            [e.type for e in second],
            "Without stored blocks, result must be reproducible across calls",
        )

    @covers("REQ-0.0.69-03-01")
    def test_parked_ceremony_excluded_from_gz_check_sweep(self) -> None:
        """A stale/parked in-closeout ceremony is excluded from the no-adr_id sweep.

        The gz-check path (no explicit adr_id) must not fail on a ceremony left
        untouched beyond the active window — but the explicit-adr_id ceremony-gate
        path MUST still enforce on that same ADR (operator ruling 2026-06-10).
        """
        import json as _json
        from datetime import datetime, timedelta

        adr_id = "ADR-0.0.99-parked"
        ceremonies_dir = self.root / ".gzkit" / "ceremonies"
        ceremonies_dir.mkdir(parents=True, exist_ok=True)
        stale = (datetime.now(UTC) - timedelta(hours=72)).isoformat()
        (ceremonies_dir / f"{adr_id}.ceremony.json").write_text(
            _json.dumps(
                {
                    "adr_id": adr_id,
                    "current_step": 6,
                    "started_at": stale,
                    "updated_at": stale,
                    "completed_at": None,
                }
            ),
            encoding="utf-8",
        )
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-test",
            ["REQ-0.0.99-01-01 [BEHAVIOR]: system does X"],  # unproven (no @covers)
        )

        # gz-check sweep (no adr_id): parked ceremony excluded → empty.
        self.assertEqual(
            validate_closeout_proof(self.root),
            [],
            "Parked ceremony (72h stale) must be excluded from the gz-check sweep",
        )
        # ceremony-gate path (explicit adr_id): freshness bypassed → still enforces.
        gated = validate_closeout_proof(self.root, adr_id=adr_id)
        self.assertGreater(
            len(gated),
            0,
            "Explicit-adr_id ceremony gate must enforce regardless of ceremony age",
        )


# ---------------------------------------------------------------------------
# REQ-0.0.69-03-02: re-run command in SUPPORT REQ failure message
# ---------------------------------------------------------------------------


class TestCloseoutProofRerunCommand(unittest.TestCase):
    """REQ-0.0.69-03-02 — failed SUPPORT REQ message format.

    The error message must contain the exact re-run command
    (``uv run gz validate --<scope>``). It must NOT inline raw stderr output.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.69-03-02")
    def test_failed_support_req_message_contains_rerun_command(self) -> None:
        """Failed SUPPORT REQ error message includes 'uv run gz validate --<scope>'."""
        adr_id = "ADR-0.0.99-rerun-cmd"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-test",
            ["REQ-0.0.99-01-01 [SUPPORT]: docs cover topic X -- uv run gz validate --documents"],
        )

        errors = validate_closeout_proof(self.root)

        self.assertGreater(len(errors), 0, "SUPPORT REQ without ledger proof must be unproven")
        combined = " ".join(e.message for e in errors)
        self.assertIn(
            "uv run gz validate",
            combined,
            "SUPPORT REQ failure message must include the re-run command",
        )

    @covers("REQ-0.0.69-03-02")
    def test_failed_support_req_message_excludes_raw_stderr_dump(self) -> None:
        """Error message must be concise — no Python tracebacks or raw stderr."""
        adr_id = "ADR-0.0.99-rerun-cmd"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-test",
            ["REQ-0.0.99-01-01 [SUPPORT]: docs cover topic X -- uv run gz validate --documents"],
        )

        errors = validate_closeout_proof(self.root)

        for e in errors:
            self.assertNotIn("Traceback", e.message, "Error must not inline Python tracebacks")
            line_count = len(e.message.splitlines())
            self.assertLessEqual(
                line_count,
                5,
                f"Error message must be concise (≤ 5 lines); got {line_count}: {e.message!r}",
            )


# ---------------------------------------------------------------------------
# REQ-0.0.69-03-03: gz check default scope; dispatched at most once
# ---------------------------------------------------------------------------


class TestCloseoutProofInCheckScope(unittest.TestCase):
    """REQ-0.0.69-03-03 — --closeout-proof in gz check default pipeline.

    The scope must appear exactly once (memoized — dispatched at most once
    per gz check run).
    """

    @covers("REQ-0.0.69-03-03")
    def test_gz_check_steps_includes_closeout_proof_runner(self) -> None:
        """gz check step list must include a closeout-proof runner."""
        from gzkit.commands.quality import gz_check_cmd

        step_names = [name for name, _ in gz_check_cmd.steps]
        closeout_names = [n for n in step_names if "closeout" in n.lower() or "proof" in n.lower()]
        self.assertGreater(
            len(closeout_names),
            0,
            f"gz check must include a closeout-proof step. Found steps: {step_names}",
        )

    @covers("REQ-0.0.69-03-03")
    def test_closeout_proof_step_appears_at_most_once(self) -> None:
        """Dispatched at most once per run — the step must not be duplicated."""
        from gzkit.commands.quality import gz_check_cmd

        step_names = [name for name, _ in gz_check_cmd.steps]
        closeout_names = [n for n in step_names if "closeout" in n.lower() or "proof" in n.lower()]
        self.assertLessEqual(
            len(closeout_names),
            1,
            f"Closeout-proof step must appear at most once; found: {closeout_names}",
        )


# ---------------------------------------------------------------------------
# REQ-0.0.69-03-07: REQ without [kind] tag is unproven
# ---------------------------------------------------------------------------


class TestCloseoutProofKindTagRequired(unittest.TestCase):
    """REQ-0.0.69-03-07 — in-closeout REQ with no inline [kind] tag is unproven.

    An Acceptance-Criteria REQ that carries no [BEHAVIOR], [SUPPORT], or
    [STRUCTURAL-FENCE] tag cannot be dispatched to any proof channel and
    must be reported as unproven (exit 3).
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.69-03-07")
    def test_req_without_kind_tag_is_unproven(self) -> None:
        """REQ with no [kind] tag → unproven → error references the REQ."""
        adr_id = "ADR-0.0.99-kind-tag"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-test",
            ["REQ-0.0.99-01-01: system does X with no kind tag"],
        )

        errors = validate_closeout_proof(self.root)

        self.assertGreater(
            len(errors),
            0,
            "REQ with no [kind] tag must be reported as unproven (exit 3)",
        )
        combined = " ".join(e.message for e in errors)
        self.assertIn("REQ-0.0.99-01-01", combined, "Error must reference the untagged REQ")

    @covers("REQ-0.0.69-03-07")
    def test_req_with_valid_kind_tag_proceeds_to_proof_channel(self) -> None:
        """REQ with [BEHAVIOR] tag is not blocked by the tag check — it proceeds
        to proof-channel evaluation. Without a @covers test it is unproven via
        the proof channel (not via the tag check).
        """
        adr_id = "ADR-0.0.99-kind-tag"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-test",
            ["REQ-0.0.99-01-01 [BEHAVIOR]: system does X"],
        )
        # No @covers test → unproven via proof channel, not tag check.

        errors = validate_closeout_proof(self.root)

        self.assertGreater(len(errors), 0, "No @covers → unproven; tag itself must not block")
        self.assertIn(
            "closeout_proof",
            {e.type for e in errors},
            "Error type must be closeout_proof (proof-channel failure), not a tag error",
        )


class TestCloseoutProofFailOpenSeams(unittest.TestCase):
    """Fail-open seams (GHI #601 follow-up): the explicit-adr_id gate path must
    fail-CLOSE on an unreadable brief or a corrupt ceremony file; the adr_id=None
    sweep path (gz check) tolerates one bad file so a stray corruption does not
    break the whole check.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_gate_path_corrupt_ceremony_fails_close(self) -> None:
        """An explicit-adr_id gate against a corrupt ceremony file must error."""
        adr_id = "ADR-0.0.99-corrupt"
        ceremonies_dir = self.root / ".gzkit" / "ceremonies"
        ceremonies_dir.mkdir(parents=True, exist_ok=True)
        (ceremonies_dir / f"{adr_id}.ceremony.json").write_text("{not valid json", encoding="utf-8")

        errors = validate_closeout_proof(self.root, adr_id=adr_id)
        self.assertTrue(
            errors,
            "gate path must fail-close on a corrupt ceremony file, not silently pass",
        )
        self.assertEqual({e.type for e in errors}, {"closeout_proof"})

    def test_gate_path_unreadable_brief_fails_close(self) -> None:
        """An explicit-adr_id gate must error when a discovered brief is unreadable."""
        adr_id = "ADR-0.0.99-unreadable"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        # A directory named like a brief satisfies the *.md glob but raises
        # IsADirectoryError (an OSError) on read_text — a deterministic,
        # cross-platform stand-in for an unreadable brief.
        (adr_dir / "obpis").mkdir(parents=True, exist_ok=True)
        (adr_dir / "obpis" / "OBPI-0.0.99-01-unreadable.md").mkdir()

        errors = validate_closeout_proof(self.root, adr_id=adr_id)
        self.assertTrue(
            errors,
            "gate path must fail-close when a discovered brief cannot be read",
        )
        self.assertEqual({e.type for e in errors}, {"closeout_proof"})

    def test_sweep_path_corrupt_ceremony_tolerated(self) -> None:
        """The adr_id=None sweep path tolerates a corrupt ceremony (no error, no raise)."""
        ceremonies_dir = self.root / ".gzkit" / "ceremonies"
        ceremonies_dir.mkdir(parents=True, exist_ok=True)
        (ceremonies_dir / "ADR-0.0.99-corrupt.ceremony.json").write_text(
            "{not valid json", encoding="utf-8"
        )

        # Must not raise; the corrupt sibling is skipped, not promoted to a failure.
        errors = validate_closeout_proof(self.root)
        self.assertEqual(
            [],
            errors,
            "sweep path must tolerate a corrupt ceremony rather than fail the whole check",
        )


class TestCloseoutProofSupportGrandfatherMalformed(unittest.TestCase):
    """GHI #660 — a malformed support_proof_grandfather.json must surface as a
    closeout_proof finding, not crash the sweep with an unhandled
    pydantic.ValidationError (regression guard for the GHI #660 fail-close fix).
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_malformed_grandfather_file_reported_not_raised(self) -> None:
        adr_id = "ADR-0.0.99-grandfather-malformed"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-test",
            [
                "REQ-0.0.99-01-01 [SUPPORT]: doc updated. Witnessed by "
                "`artifact_edited` citing "
                "`src/gzkit/nonexistent_fixture_file.py` + "
                "`uv run gz validate --documents`"
            ],
        )
        data_dir = self.root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "support_proof_grandfather.json").write_text("not valid json", encoding="utf-8")

        # Must not raise pydantic.ValidationError -- it must convert to a finding.
        errors = validate_closeout_proof(self.root)

        self.assertGreater(
            len(errors), 0, "malformed grandfather file must be reported as unproven"
        )
        combined = " ".join(e.message for e in errors)
        self.assertIn("REQ-0.0.99-01-01", combined)
        self.assertIn(
            "uv run gz validate",
            combined,
            "finding must include a governed re-run command per guardrail-feedback-prose",
        )
        for e in errors:
            self.assertNotIn("Traceback", e.message)


def _write_ledger_withdrawn(project_root: Path, obpi_id: str) -> None:
    """Append an obpi_withdrawn event for obpi_id to the project ledger."""
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "schema": "gzkit.ledger.v1",
        "event": "obpi_withdrawn",
        "id": obpi_id,
        "ts": "2026-06-11T00:00:00+00:00",
        "reason": "superseded by sibling ADR (test fixture)",
    }
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def _write_behave_waiver(project_root: Path, obpi_id: str, waived_reqs: list[str]) -> None:
    """Write a behave_coverage_waivers.json waiving the given REQs for obpi_id."""
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "default_rationale": {"test-rationale": "waived for test"},
        "waivers": {
            obpi_id: {
                "rationale": "test-rationale",
                "waived_reqs": waived_reqs,
            }
        },
    }
    (data_dir / "behave_coverage_waivers.json").write_text(json.dumps(payload), encoding="utf-8")


class TestCloseoutProofExemptions(unittest.TestCase):
    """closeout_proof honors obpi_withdrawn events and waived REQs.

    Regression context: a foundation ADR closeout went red because the
    validator demanded @covers for REQs that are legitimately uncovered — a
    withdrawn OBPI (superseded by a sibling ADR, never built) and a REQ whose
    covering test was removed by a superseding OBPI (recorded as a coverage
    waiver). The fix: skip withdrawn OBPIs' briefs and waived REQs. (REQ ids
    are kept out of this docstring on purpose so the brief-reconcile
    neighborhood scanner does not associate this test with those briefs.)
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.69-03-01")
    def test_withdrawn_obpi_brief_is_skipped(self) -> None:
        """A withdrawn OBPI's uncovered BEHAVIOR REQ does NOT produce an error."""
        adr_id = "ADR-0.0.99-withdrawn"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-05-withdrawn-surface",
            ["REQ-0.0.99-05-01 [BEHAVIOR]: system does X"],
        )
        # No @covers test — but the OBPI is withdrawn, so it must be skipped.
        _write_ledger_withdrawn(self.root, "OBPI-0.0.99-05-withdrawn-surface")

        errors = validate_closeout_proof(self.root)

        self.assertEqual(
            errors, [], f"Withdrawn OBPI's REQ must be skipped, not flagged; got: {errors}"
        )

    @covers("REQ-0.0.69-03-01")
    def test_waived_req_is_skipped(self) -> None:
        """A REQ in behave_coverage_waivers.json waived_reqs does NOT produce an error."""
        adr_id = "ADR-0.0.99-waived"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-02-primitives",
            ["REQ-0.0.99-02-07 [BEHAVIOR]: superseded staging behavior"],
        )
        # No @covers test — but the REQ is waived, so it must be skipped.
        _write_behave_waiver(self.root, "OBPI-0.0.99-02-primitives", ["REQ-0.0.99-02-07"])

        errors = validate_closeout_proof(self.root)

        self.assertEqual(errors, [], f"Waived REQ must be skipped, not flagged; got: {errors}")

    @covers("REQ-0.0.69-03-01")
    def test_non_exempt_uncovered_req_still_flagged(self) -> None:
        """Control: an uncovered REQ that is neither withdrawn nor waived still errors.

        Guards against the exemption logic over-suppressing genuine gaps.
        """
        adr_id = "ADR-0.0.99-control"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            _make_adr_dir(self.root, adr_id),
            "OBPI-0.0.99-01-real",
            ["REQ-0.0.99-01-01 [BEHAVIOR]: system does X"],
        )
        # Withdraw a DIFFERENT OBPI and waive a DIFFERENT REQ — neither covers this one.
        _write_ledger_withdrawn(self.root, "OBPI-0.0.99-99-other")
        _write_behave_waiver(self.root, "OBPI-0.0.99-88-other", ["REQ-0.0.99-88-01"])

        errors = validate_closeout_proof(self.root)

        self.assertGreater(
            len(errors), 0, "A genuinely uncovered, non-exempt BEHAVIOR REQ must still flag"
        )
        self.assertIn("closeout_proof", {e.type for e in errors})


class TestCloseoutProofEnforcementFence(unittest.TestCase):
    """GHI #649 — the closeout STRUCTURAL-FENCE proof must apply the OBPI-18
    enforcement-asserting upgrade, not resolve 'pass' on anchor presence alone.

    An enforcement-asserting fence (REQ text says X is enforced / fail-closes /
    has a live NC) resolves 'pass' only when its named ``@enforces`` claim is
    registered (ADR-0.0.74 BI#10). The closeout proof surface previously called
    ``resolve_fence_proof(req_id, project_root)`` with no ``req_text``, so the
    upgrade never fired and ANY enforcement fence passed closeout on a
    ``## Boundary Invariants`` heading alone — the facade this test forbids.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_adr_with_anchor(self, adr_id: str) -> Path:
        """ADR package whose Boundary Invariants entry carries the OBPI anchor token.

        The invariant names OBPI-01 and OBPI-02 — the OBPIs this class's fences
        belong to — so a state-property fence resolves on the anchor (GHI #538).
        Enforcement fences here still fail-close on their unregistered @enforces
        claim; the OBPI token does not rescue them.
        """
        adr_dir = _make_adr_dir(self.root, adr_id)
        (adr_dir / f"{adr_id}.md").write_text(
            f"# {adr_id}\n\n## Boundary Invariants\n\n- Invariant 1 (OBPI-01, OBPI-02)\n",
            encoding="utf-8",
        )
        return adr_dir

    def test_enforcement_fence_unregistered_claim_is_unproven_at_closeout(self) -> None:
        """Facade case: enforcement fence + anchor present + claim NOT registered
        → MUST be unproven at closeout (anchor presence is not sufficient)."""
        adr_id = "ADR-0.0.99-enf-fence"
        _write_ceremony(self.root, adr_id)
        adr_dir = self._write_adr_with_anchor(adr_id)
        _write_brief(
            adr_dir,
            "OBPI-0.0.99-01-enf",
            [
                "REQ-0.0.99-01-01 [STRUCTURAL-FENCE]: the `nonexistent-claim-xyz` "
                "guard fail-closes via a live negative control"
            ],
        )

        errors = validate_closeout_proof(self.root)

        combined = " ".join(e.message for e in errors)
        self.assertIn(
            "REQ-0.0.99-01-01",
            combined,
            "An enforcement-asserting structural-fence naming an UNREGISTERED "
            "@enforces claim must be unproven at closeout — the heading anchor "
            "alone is not proof (GHI #649; ADR-0.0.74 BI#10).",
        )

    def test_state_property_fence_still_passes_on_anchor(self) -> None:
        """No regression: a state-property fence (no enforcement keywords) still
        resolves 'pass' on the ## Boundary Invariants anchor."""
        adr_id = "ADR-0.0.99-state-fence"
        _write_ceremony(self.root, adr_id)
        adr_dir = self._write_adr_with_anchor(adr_id)
        _write_brief(
            adr_dir,
            "OBPI-0.0.99-02-state",
            ["REQ-0.0.99-02-01 [STRUCTURAL-FENCE]: the marker is the single state source"],
        )

        errors = validate_closeout_proof(self.root)

        fence_errors = [e for e in errors if "REQ-0.0.99-02-01" in e.message]
        self.assertEqual(
            fence_errors,
            [],
            f"State-property fence must still pass on the anchor; got: {fence_errors}",
        )


class TestCloseoutProofMetaPropertyDeferral(unittest.TestCase):
    """A meta-property enforcement fence (enforcement vocabulary, no single
    bindable claim) defers to the OBPI-19 enforcement floor at closeout: proven
    iff the floor is green. A single-claim fence keeps the OBPI-18 teeth
    regardless of floor state. (ADR-0.0.74 corrective fix — the closeout-proof
    consumer implements the 'prove via the floor at ADR closeout' deferral that
    resolve_fence_proof's own contract documents but never wired.)
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_adr_with_anchor(self, adr_id: str) -> Path:
        adr_dir = _make_adr_dir(self.root, adr_id)
        (adr_dir / f"{adr_id}.md").write_text(
            f"# {adr_id}\n\n## Boundary Invariants\n\n- Invariant 1\n", encoding="utf-8"
        )
        return adr_dir

    _META_REQ = (
        "REQ-0.0.99-01-01 [STRUCTURAL-FENCE]: the enforcement-claim registry has "
        "no `_NEGATIVE_CONTROL_DEBT`-style escape; the runner fail-closes if a claim "
        "lacks a passing un-forced NC"
    )

    def test_meta_property_fence_passes_when_floor_green(self) -> None:
        from unittest import mock

        adr_id = "ADR-0.0.99-meta-green"
        _write_ceremony(self.root, adr_id)
        _write_brief(self._write_adr_with_anchor(adr_id), "OBPI-0.0.99-01-meta", [self._META_REQ])
        with mock.patch(
            "gzkit.governance.trust_audits.closeout_proof._enforcement_floor_green",
            return_value=True,
        ):
            errors = validate_closeout_proof(self.root)
        fence_errors = [e for e in errors if "REQ-0.0.99-01-01" in e.message]
        self.assertEqual(
            fence_errors, [], f"meta-property fence must defer to a green floor; got {fence_errors}"
        )

    def test_meta_property_fence_fails_when_floor_red(self) -> None:
        from unittest import mock

        adr_id = "ADR-0.0.99-meta-red"
        _write_ceremony(self.root, adr_id)
        _write_brief(self._write_adr_with_anchor(adr_id), "OBPI-0.0.99-01-meta", [self._META_REQ])
        with mock.patch(
            "gzkit.governance.trust_audits.closeout_proof._enforcement_floor_green",
            return_value=False,
        ):
            errors = validate_closeout_proof(self.root)
        fence_errors = [e for e in errors if "REQ-0.0.99-01-01" in e.message]
        self.assertGreater(
            len(fence_errors), 0, "meta-property fence must fail when the enforcement floor is RED"
        )

    def test_single_claim_fence_not_floor_deferred(self) -> None:
        """Teeth: a single-claim fence naming an unregistered claim fails even with
        a green floor — the floor proves the system, never a missing named claim."""
        from unittest import mock

        adr_id = "ADR-0.0.99-single-claim"
        _write_ceremony(self.root, adr_id)
        _write_brief(
            self._write_adr_with_anchor(adr_id),
            "OBPI-0.0.99-01-single",
            [
                "REQ-0.0.99-01-01 [STRUCTURAL-FENCE]: the `nonexistent-claim-xyz` "
                "guard fail-closes via a live negative control"
            ],
        )
        with mock.patch(
            "gzkit.governance.trust_audits.closeout_proof._enforcement_floor_green",
            return_value=True,
        ):
            errors = validate_closeout_proof(self.root)
        fence_errors = [e for e in errors if "REQ-0.0.99-01-01" in e.message]
        self.assertGreater(
            len(fence_errors),
            0,
            "single-claim unregistered fence must NOT be floor-deferred (OBPI-18 teeth)",
        )


if __name__ == "__main__":
    unittest.main()
