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
        # No test file with @covers("REQ-0.0.99-01-01") — unproven.

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


if __name__ == "__main__":
    unittest.main()
