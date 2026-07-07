"""Unit tests for the @covers same-commit-window backfill heuristic.

OBPI-0.0.23-05 — Heuristic core, REQ-derived behavior.

Every git boundary call is mocked at the ``git_runner`` callable per
REQ-0.0.23-05-08. No test reaches the live repository's git history.

@covers REQ-0.0.23-05-01
@covers REQ-0.0.23-05-02
@covers REQ-0.0.23-05-03
@covers REQ-0.0.23-05-04
@covers REQ-0.0.23-05-05
@covers REQ-0.0.23-05-06
@covers REQ-0.0.23-05-07
@covers REQ-0.0.23-05-08
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from gzkit.commands.adr_audit_covers_backfill import (
    AuditThresholds,
    BackfillFinding,
    BackfillResult,
    CoverIntroduction,
    ReqClosingReceipt,
    compute_backfill_findings,
    determine_severity,
    evaluate_backfill_for_audit,
    find_covers_decorator_introductions,
    format_backfill_finding,
    load_audit_thresholds,
    resolve_req_closing_receipts,
)
from gzkit.commands.common import GzCliError
from gzkit.traceability import covers

# --------------------------------------------------------------------------- #
# FakeGit — single mock boundary for every git call (REQ-0.0.23-05-08).        #
# --------------------------------------------------------------------------- #


class FakeGit:
    """Test double for the ``git_runner`` callable boundary.

    Two dispatch shapes:

    - ``list`` of ``(rc, stdout, stderr)`` triples popped left-to-right per call.
    - ``dict`` keyed by the args tuple, returning ``(rc, stdout, stderr)``;
      missing keys return ``(1, "", "no fixture")`` so tests fail loudly when
      the production code makes an unanticipated call.

    Records every ``(args_tuple, cwd)`` it observes in ``self.calls``.
    """

    def __init__(
        self,
        responses: list[tuple[int, str, str]] | dict[tuple[str, ...], tuple[int, str, str]],
    ) -> None:
        self.responses = list(responses) if isinstance(responses, list) else dict(responses)
        self.calls: list[tuple[tuple[str, ...], Path]] = []

    def __call__(self, args: list[str], cwd: Path) -> tuple[int, str, str]:
        self.calls.append((tuple(args), cwd))
        if isinstance(self.responses, dict):
            return self.responses.get(tuple(args), (1, "", "no fixture"))
        return self.responses.pop(0) if self.responses else (1, "", "exhausted")


# --------------------------------------------------------------------------- #
# Helpers                                                                       #
# --------------------------------------------------------------------------- #


def _write_thresholds(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _make_intro(
    *,
    target: str = "REQ-0.0.23-05-01",
    file: str = "tests/governance/test_thing.py",
    line: int = 10,
    sha: str = "aaaaaaa",
    on: date = date(2026, 4, 1),
) -> CoverIntroduction:
    return CoverIntroduction(target=target, file=file, line=line, commit_sha=sha, commit_date=on)


def _make_receipt(
    *,
    req_id: str = "REQ-0.0.23-05-01",
    receipt_id: str = "evt-receipt-1",
    sha: str | None = "bbbbbbb",
    on: date = date(2026, 4, 2),
) -> ReqClosingReceipt:
    return ReqClosingReceipt(req_id=req_id, receipt_id=receipt_id, commit_sha=sha, commit_date=on)


# --------------------------------------------------------------------------- #
# AuditThresholds (Pydantic model contract — REQ-0.0.23-05-06)                  #
# --------------------------------------------------------------------------- #


class TestAuditThresholds(unittest.TestCase):
    """The threshold model is frozen, forbids extras, rejects negatives."""

    @covers("REQ-0.0.23-05-06")
    def test_valid_thresholds_construct_frozen_instance(self) -> None:
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        self.assertEqual(thresholds.max_covers_backfill_commits, 3)
        self.assertEqual(thresholds.max_covers_backfill_days, 7)
        with self.assertRaises(ValidationError):
            thresholds.max_covers_backfill_commits = 5  # type: ignore

    @covers("REQ-0.0.23-05-06")
    def test_extra_keys_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            AuditThresholds(
                max_covers_backfill_commits=3,
                max_covers_backfill_days=7,
                bonus_field=42,  # type: ignore
            )

    @covers("REQ-0.0.23-05-06")
    def test_negative_values_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            AuditThresholds(max_covers_backfill_commits=-1, max_covers_backfill_days=7)
        with self.assertRaises(ValidationError):
            AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=-1)


# --------------------------------------------------------------------------- #
# load_audit_thresholds (REQ-0.0.23-05-05)                                      #
# --------------------------------------------------------------------------- #


class TestLoadAuditThresholds(unittest.TestCase):
    """Threshold loading never silently falls back to compiled-in defaults."""

    @covers("REQ-0.0.23-05-05")
    def test_missing_file_raises_with_path_in_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            absent = Path(tmp) / "nope.json"
            with self.assertRaises(GzCliError) as ctx:
                load_audit_thresholds(absent)
            self.assertIn(str(absent), str(ctx.exception))

    @covers("REQ-0.0.23-05-05")
    def test_invalid_json_raises_with_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thresholds.json"
            path.write_text("{not-json", encoding="utf-8")
            with self.assertRaises(GzCliError) as ctx:
                load_audit_thresholds(path)
            self.assertIn(str(path), str(ctx.exception))

    @covers("REQ-0.0.23-05-05")
    def test_validation_failure_raises_with_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thresholds.json"
            _write_thresholds(path, {"max_covers_backfill_commits": -1})
            with self.assertRaises(GzCliError) as ctx:
                load_audit_thresholds(path)
            self.assertIn(str(path), str(ctx.exception))

    @covers("REQ-0.0.23-05-05")
    def test_valid_payload_returns_frozen_instance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thresholds.json"
            _write_thresholds(
                path, {"max_covers_backfill_commits": 3, "max_covers_backfill_days": 7}
            )
            thresholds = load_audit_thresholds(path)
            self.assertEqual(thresholds.max_covers_backfill_commits, 3)
            self.assertEqual(thresholds.max_covers_backfill_days, 7)


# --------------------------------------------------------------------------- #
# find_covers_decorator_introductions (REQ-0.0.23-05-01, REQ-0.0.23-05-07)      #
# --------------------------------------------------------------------------- #


class TestFindCoversDecoratorIntroductions(unittest.TestCase):
    """Resolve introducing commit + commit date for each (target, file, line)."""

    @covers("REQ-0.0.23-05-01")
    def test_parses_short_sha_and_iso_date_from_log_l_output(self) -> None:
        # Realistic `git log -L` output: header line followed by hunk noise.
        stdout = (
            "abcdef1234567890|2026-04-01T12:00:00+00:00\n"
            "diff --git a/tests/x.py b/tests/x.py\n"
            "--- a/tests/x.py\n"
            "+++ b/tests/x.py\n"
            "@@ -10,1 +10,1 @@\n"
            '+@covers("REQ-0.0.23-05-01")\n'
        )
        fake = FakeGit([(0, stdout, "")])
        intros, unresolvable = find_covers_decorator_introductions(
            Path("/repo"),
            covers_locations=[("REQ-0.0.23-05-01", "tests/x.py", 10)],
            git_runner=fake,
        )
        self.assertEqual(unresolvable, ())
        self.assertEqual(len(intros), 1)
        intro = intros[0]
        self.assertEqual(intro.target, "REQ-0.0.23-05-01")
        self.assertEqual(intro.file, "tests/x.py")
        self.assertEqual(intro.line, 10)
        self.assertEqual(intro.commit_sha, "abcdef1")  # short form
        self.assertEqual(intro.commit_date, date(2026, 4, 1))

    @covers("REQ-0.0.23-05-07")
    def test_git_failure_yields_unresolvable_diagnostic_not_exception(self) -> None:
        fake = FakeGit([(128, "", "fatal: bad object")])
        intros, unresolvable = find_covers_decorator_introductions(
            Path("/repo"),
            covers_locations=[("REQ-0.0.23-05-01", "tests/x.py", 10)],
            git_runner=fake,
        )
        self.assertEqual(intros, ())
        self.assertEqual(len(unresolvable), 1)
        self.assertIn("tests/x.py", unresolvable[0])

    @covers("REQ-0.0.23-05-07")
    def test_empty_stdout_yields_unresolvable(self) -> None:
        fake = FakeGit([(0, "", "")])
        intros, unresolvable = find_covers_decorator_introductions(
            Path("/repo"),
            covers_locations=[("REQ-0.0.23-05-01", "tests/x.py", 10)],
            git_runner=fake,
        )
        self.assertEqual(intros, ())
        self.assertEqual(len(unresolvable), 1)

    @covers("REQ-0.0.23-05-08")
    def test_only_git_runner_invoked_never_raw_subprocess(self) -> None:
        fake = FakeGit([(0, "deadbee|2026-04-01T00:00:00+00:00\n", "")])
        find_covers_decorator_introductions(
            Path("/repo"),
            covers_locations=[("REQ-0.0.23-05-01", "tests/x.py", 10)],
            git_runner=fake,
        )
        self.assertGreaterEqual(len(fake.calls), 1)
        # Every call is a list-form arg list whose first element is "log".
        for args, _cwd in fake.calls:
            self.assertEqual(args[0], "log")


# --------------------------------------------------------------------------- #
# resolve_req_closing_receipts (REQ-0.0.23-05-01, REQ-0.0.23-05-07)             #
# --------------------------------------------------------------------------- #


class TestResolveReqClosingReceipts(unittest.TestCase):
    """REQs map to their parent OBPI's closing receipt event or fallback."""

    @covers("REQ-0.0.23-05-01")
    def test_attested_completed_receipt_is_picked_up(self) -> None:
        events = [
            {
                "event": "obpi_receipt_emitted",
                "id": "OBPI-0.1.0-01",
                "ts": "2026-04-02T12:00:00+00:00",
                "extra": {
                    "receipt_event": "attested_completed",
                    "anchor": {"commit": "fedcba9"},
                },
            }
        ]
        receipts = resolve_req_closing_receipts(
            ["REQ-0.1.0-01-01"],
            obpi_completion_events=events,
            project_root=Path("/repo"),
            git_runner=FakeGit([]),
        )
        self.assertIn("REQ-0.1.0-01-01", receipts)
        receipt = receipts["REQ-0.1.0-01-01"]
        self.assertEqual(receipt.commit_sha, "fedcba9")
        self.assertEqual(receipt.commit_date, date(2026, 4, 2))

    @covers("REQ-0.0.23-05-01")
    def test_completed_receipt_event_also_recognized(self) -> None:
        events = [
            {
                "event": "obpi_receipt_emitted",
                "id": "OBPI-0.1.0-01",
                "ts": "2026-03-15T00:00:00+00:00",
                "extra": {
                    "receipt_event": "completed",
                    "anchor": {"commit": "1234567"},
                },
            }
        ]
        receipts = resolve_req_closing_receipts(
            ["REQ-0.1.0-01-01"],
            obpi_completion_events=events,
            project_root=Path("/repo"),
            git_runner=FakeGit([]),
        )
        self.assertIn("REQ-0.1.0-01-01", receipts)

    @covers("REQ-0.0.23-05-01")
    def test_most_recent_receipt_wins_when_multiple(self) -> None:
        events = [
            {
                "event": "obpi_receipt_emitted",
                "id": "OBPI-0.1.0-01",
                "ts": "2026-03-01T00:00:00+00:00",
                "extra": {"receipt_event": "completed", "anchor": {"commit": "aaaaaaa"}},
            },
            {
                "event": "obpi_receipt_emitted",
                "id": "OBPI-0.1.0-01",
                "ts": "2026-04-15T00:00:00+00:00",
                "extra": {"receipt_event": "attested_completed", "anchor": {"commit": "bbbbbbb"}},
            },
        ]
        receipts = resolve_req_closing_receipts(
            ["REQ-0.1.0-01-01"],
            obpi_completion_events=events,
            project_root=Path("/repo"),
            git_runner=FakeGit([]),
        )
        self.assertEqual(receipts["REQ-0.1.0-01-01"].commit_sha, "bbbbbbb")
        self.assertEqual(receipts["REQ-0.1.0-01-01"].commit_date, date(2026, 4, 15))

    @covers("REQ-0.0.23-05-01")
    def test_req_without_receipt_omitted_from_result(self) -> None:
        # No events for OBPI-0.1.0-99; fallback also fails (git rc != 0).
        fake = FakeGit([(128, "", "no commits")])
        receipts = resolve_req_closing_receipts(
            ["REQ-0.1.0-99-01"],
            obpi_completion_events=[],
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertNotIn("REQ-0.1.0-99-01", receipts)


# --------------------------------------------------------------------------- #
# determine_severity (REQ-0.0.23-05-02, REQ-0.0.23-05-03)                       #
# --------------------------------------------------------------------------- #


class TestDetermineSeverity(unittest.TestCase):
    """Severity escalation across (lane, kind, strict) axes."""

    @covers("REQ-0.0.23-05-03")
    def test_heavy_lane_escalates_to_blocking(self) -> None:
        self.assertEqual(determine_severity("heavy", "feature", strict=False), "blocking")

    @covers("REQ-0.0.23-05-03")
    def test_foundation_kind_escalates_to_blocking(self) -> None:
        self.assertEqual(determine_severity("lite", "foundation", strict=False), "blocking")

    @covers("REQ-0.0.23-05-03")
    def test_strict_escalates_to_blocking_on_lite_feature(self) -> None:
        self.assertEqual(determine_severity("lite", "feature", strict=True), "blocking")

    @covers("REQ-0.0.23-05-03")
    def test_strict_escalates_to_blocking_on_heavy_lane(self) -> None:
        self.assertEqual(determine_severity("heavy", "feature", strict=True), "blocking")

    @covers("REQ-0.0.23-05-03")
    def test_strict_escalates_to_blocking_on_foundation_kind(self) -> None:
        self.assertEqual(determine_severity("lite", "foundation", strict=True), "blocking")

    @covers("REQ-0.0.23-05-02")
    def test_lite_feature_without_strict_is_warning(self) -> None:
        self.assertEqual(determine_severity("lite", "feature", strict=False), "warning")


# --------------------------------------------------------------------------- #
# compute_backfill_findings (REQ-0.0.23-05-01, -02 fire-on-either, -04 inverse) #
# --------------------------------------------------------------------------- #


class TestComputeBackfillFindings(unittest.TestCase):
    """The same-commit-window heuristic fires on either gap, never on both clear."""

    @covers("REQ-0.0.23-05-01")
    def test_flags_when_commits_gap_at_threshold(self) -> None:
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 4, 1))
        receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 30))  # 29 days > 7
        fake = FakeGit([(0, "2\n", "")])  # commits gap = 2, <= 3
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="warning",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].gap_commits, 2)
        self.assertEqual(findings[0].gap_days, 29)
        self.assertEqual(findings[0].severity, "warning")

    @covers("REQ-0.0.23-05-01")
    def test_flags_when_days_gap_at_threshold(self) -> None:
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 4, 1))
        receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 5))  # 4 days <= 7
        fake = FakeGit([(0, "100\n", "")])  # commits gap = 100, > 3
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="blocking",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "blocking")

    @covers("REQ-0.0.23-05-04")
    def test_does_not_flag_when_both_gaps_exceed(self) -> None:
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 1, 1))
        receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 30))  # ~119 days
        fake = FakeGit([(0, "50\n", "")])  # commits gap = 50, > 3
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="warning",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(findings, ())

    @covers("REQ-0.0.23-05-01")
    def test_introduction_with_no_receipt_is_skipped(self) -> None:
        intro = _make_intro()
        fake = FakeGit([])
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro], {}, thresholds, severity="warning", project_root=Path("/repo"), git_runner=fake
        )
        self.assertEqual(findings, ())
        self.assertEqual(fake.calls, [])  # never reached git

    @covers("REQ-0.0.23-05-01")
    def test_rev_list_failure_skips_finding(self) -> None:
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 4, 1))
        receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 1))
        # rev-list fails -> commits gap is math.inf, days gap is 0 (<=7).
        # Days <=7 still flags via OR — verify the days path still fires
        # even when rev-list is broken.
        fake = FakeGit([(128, "", "missing object")])
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="warning",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(len(findings), 1)
        # commits gap rendered as a sentinel large int when rev-list failed.
        self.assertGreater(findings[0].gap_days, -1)


class TestTimezoneConsistentCommitDates(unittest.TestCase):
    """Commit dates (git ``%cI``, local offset) and receipt dates (ledger ts, UTC)
    MUST be compared in a consistent timezone.

    Regression for a latent time-of-day flake: a same-instant cosmetic-backfill
    triple committed in the evening (local) emits its receipt event in UTC —
    already past midnight — so a naive ``.date()`` on each put them on different
    calendar days near the UTC boundary. That made ``receipt_after_intro`` True,
    wrongly exempting the triple, so the heuristic silently stopped firing after
    ~19:00 US-Central every day. Both parsers normalize to the UTC date.
    """

    @covers("REQ-0.0.23-05-01")
    def test_git_local_and_ledger_utc_same_instant_yield_same_date(self) -> None:
        from gzkit.commands.adr_audit_covers_backfill import (
            _parse_first_log_header,
            _ts_to_date,
        )

        # The SAME instant: 2026-07-06T20:55:32-05:00 == 2026-07-07T01:55:32+00:00.
        parsed = _parse_first_log_header("8bd1e7e|2026-07-06T20:55:32-05:00\n")
        self.assertIsNotNone(parsed)
        assert parsed is not None
        _sha, commit_date = parsed
        receipt_date = _ts_to_date("2026-07-07T01:55:32+00:00")
        self.assertEqual(commit_date, receipt_date)
        self.assertEqual(commit_date, date(2026, 7, 7))


# --------------------------------------------------------------------------- #
# Legitimate-authoring guard (GHI #386 — ceremony trailer, file-creation)       #
# --------------------------------------------------------------------------- #


class TestLegitimateAuthoringExemption(unittest.TestCase):
    """Same-commit-window decorators introduced under ceremony-bundling or
    file-creation are legitimate authoring, not cosmetic backfill (GHI #386).

    The cosmetic-backfill anti-pattern (GHI #272) is a *later* commit adding
    ``@covers`` to a *pre-existing* test without re-deriving assertions.
    Same-commit creation and ``Ceremony: <name>`` bundling are structurally
    distinct and must not trip the heuristic.
    """

    @covers("REQ-0.0.23-05-01")
    def test_ceremony_trailer_commit_is_not_flagged(self) -> None:
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 4, 1))
        receipt = _make_receipt(sha="aaaaaaa", on=date(2026, 4, 1))
        # intro_sha == receipt_sha short-circuits rev-list. Calls in order:
        # file-creation log (different SHA -> no creation match),
        # ceremony trailer log (returns 'gz-git-sync').
        fake = FakeGit(
            [
                (0, "ffffff0000000000000000000000000000000000\n", ""),
                (0, "gz-git-sync\n", ""),
            ]
        )
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="blocking",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(findings, ())

    @covers("REQ-0.0.23-05-01")
    def test_file_creation_same_commit_as_receipt_is_flagged(self) -> None:
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 4, 1))
        receipt = _make_receipt(sha="aaaaaaa", on=date(2026, 4, 1))
        # intro_sha == receipt_sha == file-creation SHA: the triple
        # (file-create + @covers + receipt all in one commit) is the GHI #309
        # cosmetic-backfill pattern regardless of file-creation status
        # (ADR-0.0.25 refinement of GHI #382). The file-creation exemption is
        # suppressed when receipt SHA matches; ceremony-trailer check fires
        # next and returns empty (no trailer), so the finding IS added.
        fake = FakeGit(
            [
                (0, "aaaaaaa1234567890abcdef0123456789abcdef\n", ""),
                (0, "", ""),
            ]
        )
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="blocking",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(len(findings), 1)

    @covers("REQ-0.0.23-05-01")
    def test_later_commit_decoration_on_preexisting_file_still_flags(self) -> None:
        # Cosmetic-backfill anti-pattern (GHI #272): a later commit decorates
        # a pre-existing test. Introducing SHA differs from the file-creation
        # SHA, and the introducing commit has no ceremony trailer — heuristic
        # MUST flag.
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 4, 5))
        receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 6))  # 1d gap
        fake = FakeGit(
            [
                (0, "1\n", ""),
                (0, "deadbee0000000000000000000000000000000000\n", ""),
                (0, "\n", ""),
            ]
        )
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="blocking",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, "blocking")

    @covers("REQ-0.0.23-05-01")
    def test_pre_trailer_subject_marker_exempts_legitimate_authoring(self) -> None:
        """Pre-GHI #201 ceremony commits (before the `Ceremony:` git trailer was
        introduced) carry the ceremony marker only in the parenthesized subject
        suffix, e.g. ``chore: update ... (gz git-sync)``. The trailer-only
        check would miss them entirely and flag the bundled @covers as
        cosmetic backfill (GHI #390 Case B). The subject-suffix fallback maps
        the historical marker to the same canonical exempt set.
        """
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 4, 18))
        receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 17))
        fake = FakeGit(
            [
                (0, "1\n", ""),  # rev-list: 1-commit gap
                (0, "deadbee0000000000000000000000000000000000\n", ""),  # creation: different SHA
                (0, "\n", ""),  # trailer: empty (pre-trailer-convention commit)
                (
                    0,
                    "chore: update .claude (2 files), .gzkit (3 files) +5 more (gz git-sync)\n",
                    "",
                ),  # subject: carries historical marker at end
            ]
        )
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="blocking",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(findings, ())

    @covers("REQ-0.0.23-05-01")
    def test_subject_marker_must_be_at_subject_end_to_exempt(self) -> None:
        """The historical marker pattern is anchored to subject end so a
        future commit titled e.g. ``fix: stop bypassing (gz git-sync) trailer
        check`` cannot accidentally exempt itself by mentioning the suffix
        mid-line.
        """
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 4, 18))
        receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 17))
        fake = FakeGit(
            [
                (0, "1\n", ""),
                (0, "deadbee0000000000000000000000000000000000\n", ""),
                (0, "\n", ""),
                (0, "fix: stop bypassing (gz git-sync) trailer check (GHI #999)\n", ""),
            ]
        )
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="blocking",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(len(findings), 1)

    @covers("REQ-0.0.23-05-01")
    def test_unregistered_ceremony_trailer_does_not_exempt(self) -> None:
        intro = _make_intro(sha="aaaaaaa", on=date(2026, 4, 1))
        receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 1))
        fake = FakeGit(
            [
                (0, "1\n", ""),
                (0, "deadbee0000000000000000000000000000000000\n", ""),
                (0, "experimental-bundle\n", ""),
            ]
        )
        thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
        findings = compute_backfill_findings(
            [intro],
            {intro.target: receipt},
            thresholds,
            severity="warning",
            project_root=Path("/repo"),
            git_runner=fake,
        )
        self.assertEqual(len(findings), 1)


# --------------------------------------------------------------------------- #
# Same-commit BLOCK creation + inline overlay marker (GHI #466)                 #
# --------------------------------------------------------------------------- #


class TestBlockCreationAndOverlayMarker(unittest.TestCase):
    """Two new legitimate-authoring shapes added under GHI #466.

    - **Same-commit BLOCK creation (Component B):** the function body and its
      ``@covers`` decorator are authored in the same commit, even though the
      file pre-existed. Structurally identical to GHI #382 same-commit FILE
      creation — the assertion came into existence WITH the decorator, no
      later "silencing" pass is possible.
    - **Inline regression-invariant overlay marker (Component A):** a
      ``# audit-exempt: regression-invariant-overlay <reason>`` token on
      the decorator line. Source-side opt-in for cases where a
      regression-invariant ``REQ`` is being claimed against an existing test
      whose assertion structurally IS that invariant (e.g. byte-parity
      tests covering a regression-invariant REQ).

    Both shapes preserve the GHI #272 cosmetic-backfill detection (decorator
    added later to a pre-existing test with no body change in the same SHA
    must still flag).
    """

    @staticmethod
    def _write_test_file(project_root: Path, rel_path: str, content: str) -> Path:
        target = project_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    @covers("REQ-0.0.23-05-01")
    def test_same_commit_block_creation_in_existing_file_exempt(self) -> None:
        """Decorator + def line co-authored in same SHA on a pre-existing file is exempt."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")\ndef test_thing(self) -> None:\n    self.assertTrue(True)\n',
            )
            intro = _make_intro(file="tests/x.py", line=1, sha="aaaaaaa", on=date(2026, 4, 1))
            receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 1))
            fake = FakeGit(
                {
                    ("rev-list", "--count", "aaaaaaa..bbbbbbb"): (0, "1\n", ""),
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                    # Block-creation: def line at line 2, intro SHA matches decorator SHA.
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "aaaaaaa1234567890abcdef0123456789abcdef\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(findings, ())

    @covers("REQ-0.0.23-05-01")
    def test_same_commit_block_creation_with_same_commit_receipt_still_flagged(self) -> None:
        """GHI #309 protection preserved: block-creation + same-commit receipt = flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")\ndef test_thing(self) -> None:\n    self.assertTrue(True)\n',
            )
            intro = _make_intro(file="tests/x.py", line=1, sha="aaaaaaa", on=date(2026, 4, 1))
            receipt = _make_receipt(sha="aaaaaaa", on=date(2026, 4, 1))
            # intro_sha == receipt_sha short-circuits rev-list (count = 0). After
            # file-creation check (different SHA, would have exempted but receipt
            # coupled), block-creation check (SHA matches, would have exempted
            # but receipt coupled), then ceremony trailer (empty), then subject
            # marker (no marker) → finding stands.
            fake = FakeGit(
                {
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "aaaaaaa1234567890abcdef0123456789abcdef\n",
                        "",
                    ),
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "aaaaaaa"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "aaaaaaa"): (
                        0,
                        "feat: add stuff\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(len(findings), 1)

    @covers("REQ-0.0.23-05-01")
    def test_same_commit_block_creation_with_later_ceremony_receipt_exempt(self) -> None:
        """GHI #667: receipt anchored to impl commit but emitted LATER is exempt.

        Contrast with ``..._with_same_commit_receipt_still_flagged`` (same sha AND
        same date — the cosmetic triple, stays flagged). Here the receipt anchors
        to the same impl commit (``aaaaaaa``) but its event ts is a day later: the
        completion ceremony post-dates the implementation, so the same-commit
        block-creation is genuine and the GHI #309 receipt-coupling guard must NOT
        suppress the exemption.
        """
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")\ndef test_thing(self) -> None:\n    self.assertTrue(True)\n',
            )
            intro = _make_intro(file="tests/x.py", line=1, sha="aaaaaaa", on=date(2026, 4, 1))
            # Same anchor sha as intro, but event ts is a day LATER (later ceremony).
            receipt = _make_receipt(sha="aaaaaaa", on=date(2026, 4, 2))
            fake = FakeGit(
                {
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                    # Block-creation: def line at line 2, intro SHA matches decorator SHA.
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "aaaaaaa1234567890abcdef0123456789abcdef\n",
                        "",
                    ),
                    # Reached only pre-fix (block-creation guard still suppressed);
                    # harmless as unused fixtures post-fix.
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "aaaaaaa"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "aaaaaaa"): (
                        0,
                        "feat: add stuff\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(findings, ())

    @covers("REQ-0.0.23-05-01")
    def test_inline_audit_exempt_marker_exempts_decorator(self) -> None:
        """``# audit-exempt: regression-invariant-overlay <reason>`` exempts the line."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")  # audit-exempt: regression-invariant-overlay '
                "REQ-X is regression-invariant for OBPI-Y\n"
                "def test_existing(self) -> None:\n    self.assertTrue(True)\n",
            )
            intro = _make_intro(file="tests/x.py", line=1, sha="aaaaaaa", on=date(2026, 4, 1))
            receipt = _make_receipt(sha="aaaaaaa", on=date(2026, 4, 1))
            # Marker exemption fires BEFORE ceremony-trailer checks, so only
            # file-creation + block-creation git calls are reached. Both miss
            # (different SHA / different SHA), but marker check intervenes
            # before the ceremony trailer call → no flag, no further git.
            fake = FakeGit(
                {
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(findings, ())

    @covers("REQ-0.0.23-05-01")
    def test_inline_audit_exempt_marker_requires_reason_text(self) -> None:
        """The marker keyword alone (no reason text after) does not exempt."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")  # audit-exempt: regression-invariant-overlay\n'
                "def test_existing(self) -> None:\n    self.assertTrue(True)\n",
            )
            intro = _make_intro(file="tests/x.py", line=1, sha="aaaaaaa", on=date(2026, 4, 1))
            receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 2))
            fake = FakeGit(
                {
                    ("rev-list", "--count", "aaaaaaa..bbbbbbb"): (0, "1\n", ""),
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "aaaaaaa"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "aaaaaaa"): (
                        0,
                        "feat: add stuff\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(len(findings), 1)

    @covers("REQ-0.0.23-05-01")
    def test_inline_audit_exempt_marker_must_be_on_decorator_line(self) -> None:
        """A marker on a sibling line (not the decorator line itself) does not exempt."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                "# audit-exempt: regression-invariant-overlay decoy reason\n"
                '@covers("REQ-X")\n'
                "def test_existing(self) -> None:\n    self.assertTrue(True)\n",
            )
            # Decorator is now on line 2, not line 1 (line 1 carries the decoy comment).
            intro = _make_intro(file="tests/x.py", line=2, sha="aaaaaaa", on=date(2026, 4, 1))
            receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 2))
            fake = FakeGit(
                {
                    ("rev-list", "--count", "aaaaaaa..bbbbbbb"): (0, "1\n", ""),
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "--reverse", "--format=%H", "-L3,3:tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "aaaaaaa"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "aaaaaaa"): (
                        0,
                        "feat: add stuff\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(len(findings), 1)

    @covers("REQ-0.0.23-05-01")
    def test_cosmetic_backfill_on_preexisting_test_still_flagged(self) -> None:
        """GHI #272 anti-pattern preserved: decorator added later to a pre-existing
        test (def line authored in an OLDER SHA, no marker) still flags.
        """
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")\ndef test_existing(self) -> None:\n    self.assertTrue(True)\n',
            )
            intro = _make_intro(file="tests/x.py", line=1, sha="aaaaaaa", on=date(2026, 4, 5))
            receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 6))
            fake = FakeGit(
                {
                    ("rev-list", "--count", "aaaaaaa..bbbbbbb"): (0, "1\n", ""),
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "deadbee0000000000000000000000000000000000\n",
                        "",
                    ),
                    # Def line authored in an OLDER SHA → no block-creation exemption.
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "0123456000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "aaaaaaa"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "aaaaaaa"): (
                        0,
                        "fix: silence audit warning\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].severity, "blocking")


# --------------------------------------------------------------------------- #
# Ambiguous-attribution blame re-anchor (content-identical decorator lines)     #
# --------------------------------------------------------------------------- #


class TestAmbiguousAttributionBlameReanchor(unittest.TestCase):
    """``git log -L`` vs ``git blame`` cross-pairing on identical decorator lines.

    When a commit inserts a new ``@covers``-decorated test block adjacent to an
    existing test carrying a content-identical decorator line, ``git log -L``
    and ``git blame`` can attribute the two physical lines to OPPOSITE commits.
    The heuristic's ``log -L`` intro then cross-pairs the inserting commit's
    SHA with the pre-existing test's def line, defeating every legitimacy
    exemption and producing a false-positive backfill finding (observed on
    ADR-0.0.68 audit: the GHI #600 fix commit was cross-paired with a test
    authored in an exempt ``(gz git-sync)`` ceremony commit).

    Remedy under test: when the finding is otherwise about to flag, re-anchor
    the intro at ``git blame``'s attribution for the decorator line and re-run
    the same legitimacy ladder (receipt-coupling guard included, preserving the
    GHI #309 triple). Blame agreement or blame failure changes nothing.
    """

    @staticmethod
    def _write_test_file(project_root: Path, rel_path: str, content: str) -> Path:
        target = project_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    # Exactly 40 hex chars, as real `git blame --porcelain` emits.
    _BLAME_CCCCCCC = (
        0,
        "ccccccc000000000000000000000000000000000 1 1 1\nfiller header noise\n",
        "",
    )

    @covers("REQ-0.0.23-05-01")
    def test_blame_reanchor_exempts_cross_paired_decorator(self) -> None:
        """Blame disagrees with log -L; re-anchored SHA is legitimate → no flag."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")\ndef test_existing(self) -> None:\n    self.assertTrue(True)\n',
            )
            # log -L attributed the decorator to fffffff (the inserting fix
            # commit); blame attributes it to ccccccc, the commit that also
            # created the file — the file-creation exemption fires on re-anchor.
            intro = _make_intro(file="tests/x.py", line=1, sha="fffffff", on=date(2026, 4, 1))
            receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 1))
            fake = FakeGit(
                {
                    ("rev-list", "--count", "fffffff..bbbbbbb"): (0, "0\n", ""),
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "ccccccc0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "ccccccc0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "fffffff"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "fffffff"): (
                        0,
                        "fix(session-green-gate): harden token match (GHI #600)\n",
                        "",
                    ),
                    ("blame", "--porcelain", "-L1,1", "--", "tests/x.py"): self._BLAME_CCCCCCC,
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(findings, ())

    @covers("REQ-0.0.23-05-01")
    def test_blame_agreement_keeps_finding(self) -> None:
        """Blame agrees with log -L (unambiguous attribution) → finding stands."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")\ndef test_existing(self) -> None:\n    self.assertTrue(True)\n',
            )
            intro = _make_intro(file="tests/x.py", line=1, sha="fffffff", on=date(2026, 4, 1))
            receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 1))
            fake = FakeGit(
                {
                    ("rev-list", "--count", "fffffff..bbbbbbb"): (0, "0\n", ""),
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "ccccccc0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "ccccccc0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "fffffff"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "fffffff"): (
                        0,
                        "fix: silence audit warning\n",
                        "",
                    ),
                    ("blame", "--porcelain", "-L1,1", "--", "tests/x.py"): (
                        0,
                        "fffffff000000000000000000000000000000000 1 1 1\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(len(findings), 1)

    @covers("REQ-0.0.23-05-01")
    def test_blame_failure_keeps_finding(self) -> None:
        """Blame boundary failure degrades to no exemption (fail-soft) → finding stands."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")\ndef test_existing(self) -> None:\n    self.assertTrue(True)\n',
            )
            intro = _make_intro(file="tests/x.py", line=1, sha="fffffff", on=date(2026, 4, 1))
            receipt = _make_receipt(sha="bbbbbbb", on=date(2026, 4, 1))
            # No blame fixture: FakeGit dict-mode returns (1, "", "no fixture").
            fake = FakeGit(
                {
                    ("rev-list", "--count", "fffffff..bbbbbbb"): (0, "0\n", ""),
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "ccccccc0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "ccccccc0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "fffffff"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "fffffff"): (
                        0,
                        "fix: silence audit warning\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(len(findings), 1)

    @covers("REQ-0.0.23-05-01")
    def test_reanchor_to_receipt_commit_still_flagged(self) -> None:
        """GHI #309 triple survives re-anchor: blame SHA == receipt SHA → flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            self._write_test_file(
                project_root,
                "tests/x.py",
                '@covers("REQ-X")\ndef test_existing(self) -> None:\n    self.assertTrue(True)\n',
            )
            intro = _make_intro(file="tests/x.py", line=1, sha="fffffff", on=date(2026, 4, 1))
            receipt = _make_receipt(sha="ccccccc", on=date(2026, 4, 1))
            fake = FakeGit(
                {
                    ("rev-list", "--count", "fffffff..ccccccc"): (0, "0\n", ""),
                    ("log", "--diff-filter=A", "--format=%H", "--", "tests/x.py"): (
                        0,
                        "ccccccc0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "--reverse", "--format=%H", "-L2,2:tests/x.py"): (
                        0,
                        "ccccccc0000000000000000000000000000000000\n",
                        "",
                    ),
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "fffffff"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "fffffff"): (
                        0,
                        "fix: silence audit warning\n",
                        "",
                    ),
                    ("blame", "--porcelain", "-L1,1", "--", "tests/x.py"): self._BLAME_CCCCCCC,
                    # Re-anchored ladder: file/block exemptions suppressed by the
                    # receipt-coupling guard; ceremony checks on ccccccc miss too.
                    ("log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", "ccccccc"): (
                        0,
                        "",
                        "",
                    ),
                    ("log", "-1", "--format=%s", "ccccccc"): (
                        0,
                        "feat: add stuff\n",
                        "",
                    ),
                }
            )
            thresholds = AuditThresholds(max_covers_backfill_commits=3, max_covers_backfill_days=7)
            findings = compute_backfill_findings(
                [intro],
                {intro.target: receipt},
                thresholds,
                severity="blocking",
                project_root=project_root,
                git_runner=fake,
            )
            self.assertEqual(len(findings), 1)


# --------------------------------------------------------------------------- #
# format_backfill_finding (REQ-0.0.23-05-01, REQ-0.0.23-05-03 remediation hint) #
# --------------------------------------------------------------------------- #


class TestFormatBackfillFinding(unittest.TestCase):
    """Diagnostic format carries every operator-required field (substring asserts)."""

    @covers("REQ-0.0.23-05-01")
    def test_diagnostic_contains_each_required_field(self) -> None:
        finding = BackfillFinding(
            req_id="REQ-0.0.23-05-01",
            file="tests/governance/test_thing.py",
            line=42,
            introducing_commit_sha="abcdef1",
            closing_receipt_id="evt-receipt-99",
            gap_commits=1,
            gap_days=0,
            severity="blocking",
        )
        text = format_backfill_finding(finding)
        self.assertIn("tests/governance/test_thing.py:42", text)
        self.assertIn("REQ-0.0.23-05-01", text)
        self.assertIn("abcdef1", text)
        self.assertIn("evt-receipt-99", text)
        self.assertIn("1c", text)
        self.assertIn("0d", text)

    @covers("REQ-0.0.23-05-03")
    def test_diagnostic_carries_invariant_6f_remediation_hint(self) -> None:
        finding = BackfillFinding(
            req_id="REQ-0.0.23-05-01",
            file="tests/x.py",
            line=1,
            introducing_commit_sha="aaaaaaa",
            closing_receipt_id="r1",
            gap_commits=0,
            gap_days=0,
            severity="blocking",
        )
        text = format_backfill_finding(finding)
        self.assertIn("Invariant 6f", text)


# --------------------------------------------------------------------------- #
# evaluate_backfill_for_audit — orchestrator exit-code semantics                #
# --------------------------------------------------------------------------- #


class TestEvaluateBackfillForAudit(unittest.TestCase):
    """Orchestrator pipeline assembles findings + exit code per REQ-02/03/05/07."""

    def _write_thresholds_file(self, tmp: Path) -> Path:
        path = tmp / "thresholds.json"
        _write_thresholds(path, {"max_covers_backfill_commits": 3, "max_covers_backfill_days": 7})
        return path

    @covers("REQ-0.0.23-05-04")
    def test_no_decorators_yields_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_thresholds_file(Path(tmp))
            result = evaluate_backfill_for_audit(
                Path(tmp),
                adr_lane="lite",
                adr_kind="feature",
                strict=False,
                covers_locations=[],
                obpi_completion_events=[],
                thresholds_path=path,
                git_runner=FakeGit([]),
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.findings, ())
            self.assertEqual(result.unresolvable, ())

    @covers("REQ-0.0.23-05-02")
    def test_warning_severity_findings_exit_zero(self) -> None:
        # Lite-feature, !strict ⇒ severity warning ⇒ exit 0 even with findings.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_thresholds_file(Path(tmp))
            # Stage responses: introductions log, then rev-list count.
            log_stdout = "abcdef1|2026-04-01T00:00:00+00:00\n"
            fake = FakeGit([(0, log_stdout, ""), (0, "1\n", "")])
            events = [
                {
                    "event": "obpi_receipt_emitted",
                    "id": "OBPI-0.0.23-05",
                    "ts": "2026-04-02T00:00:00+00:00",
                    "extra": {
                        "receipt_event": "completed",
                        "anchor": {"commit": "bbbbbbb"},
                    },
                }
            ]
            result = evaluate_backfill_for_audit(
                Path(tmp),
                adr_lane="lite",
                adr_kind="feature",
                strict=False,
                covers_locations=[("REQ-0.0.23-05-01", "tests/x.py", 1)],
                obpi_completion_events=events,
                thresholds_path=path,
                git_runner=fake,
            )
            self.assertEqual(len(result.findings), 1)
            self.assertEqual(result.findings[0].severity, "warning")
            self.assertEqual(result.exit_code, 0)

    @covers("REQ-0.0.23-05-03")
    def test_blocking_findings_exit_three(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_thresholds_file(Path(tmp))
            log_stdout = "abcdef1|2026-04-01T00:00:00+00:00\n"
            fake = FakeGit([(0, log_stdout, ""), (0, "1\n", "")])
            events = [
                {
                    "event": "obpi_receipt_emitted",
                    "id": "OBPI-0.0.23-05",
                    "ts": "2026-04-02T00:00:00+00:00",
                    "extra": {
                        "receipt_event": "attested_completed",
                        "anchor": {"commit": "bbbbbbb"},
                    },
                }
            ]
            # Per GHI #385: only --strict escalates to blocking now;
            # foundation-kind alone no longer fails-closed pending the
            # heuristic learning gz-git-sync ceremony semantics.
            result = evaluate_backfill_for_audit(
                Path(tmp),
                adr_lane="lite",
                adr_kind="foundation",
                strict=True,
                covers_locations=[("REQ-0.0.23-05-01", "tests/x.py", 1)],
                obpi_completion_events=events,
                thresholds_path=path,
                git_runner=fake,
            )
            self.assertEqual(len(result.findings), 1)
            self.assertEqual(result.findings[0].severity, "blocking")
            self.assertEqual(result.exit_code, 3)

    @covers("REQ-0.0.23-05-07")
    def test_unresolvable_with_strict_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_thresholds_file(Path(tmp))
            # `git log` for the introduction returns rc != 0 ⇒ unresolvable.
            fake = FakeGit([(128, "", "shallow clone")])
            result = evaluate_backfill_for_audit(
                Path(tmp),
                adr_lane="lite",
                adr_kind="feature",
                strict=True,
                covers_locations=[("REQ-0.0.23-05-01", "tests/x.py", 1)],
                obpi_completion_events=[],
                thresholds_path=path,
                git_runner=fake,
            )
            self.assertEqual(len(result.unresolvable), 1)
            self.assertEqual(result.exit_code, 2)

    @covers("REQ-0.0.23-05-07")
    def test_unresolvable_without_strict_exits_zero_with_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_thresholds_file(Path(tmp))
            fake = FakeGit([(128, "", "shallow clone")])
            result = evaluate_backfill_for_audit(
                Path(tmp),
                adr_lane="lite",
                adr_kind="feature",
                strict=False,
                covers_locations=[("REQ-0.0.23-05-01", "tests/x.py", 1)],
                obpi_completion_events=[],
                thresholds_path=path,
                git_runner=fake,
            )
            self.assertEqual(len(result.unresolvable), 1)
            self.assertEqual(result.exit_code, 0)

    @covers("REQ-0.0.23-05-03")
    def test_blocking_findings_outrank_unresolvable_strict(self) -> None:
        # Blocking findings + unresolvable + strict ⇒ exit 3 (policy beats system).
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_thresholds_file(Path(tmp))
            # First call resolves the introduction; second call (rev-list) succeeds;
            # third call (introduction for the unresolvable decorator) fails.
            log_stdout = "abcdef1|2026-04-01T00:00:00+00:00\n"
            fake = FakeGit(
                [
                    (0, log_stdout, ""),  # introduction A: ok
                    (128, "", "missing"),  # introduction B: unresolvable
                    (0, "1\n", ""),  # rev-list for A
                ]
            )
            events = [
                {
                    "event": "obpi_receipt_emitted",
                    "id": "OBPI-0.0.23-05",
                    "ts": "2026-04-02T00:00:00+00:00",
                    "extra": {
                        "receipt_event": "completed",
                        "anchor": {"commit": "bbbbbbb"},
                    },
                }
            ]
            result = evaluate_backfill_for_audit(
                Path(tmp),
                adr_lane="heavy",
                adr_kind="feature",
                strict=True,
                covers_locations=[
                    ("REQ-0.0.23-05-01", "tests/a.py", 1),
                    ("REQ-0.0.23-05-01", "tests/b.py", 1),
                ],
                obpi_completion_events=events,
                thresholds_path=path,
                git_runner=fake,
            )
            self.assertEqual(len(result.findings), 1)
            self.assertEqual(result.exit_code, 3)

    @covers("REQ-0.0.23-05-05")
    def test_missing_thresholds_file_propagates_gzcli_error(self) -> None:
        # REQ-3 binds when there is actual heuristic work; an empty
        # covers_locations list short-circuits the eager-load to keep
        # init-fresh fixtures from tripping the contract. Pass a real
        # decorator location so the threshold-load path runs.
        with tempfile.TemporaryDirectory() as tmp:
            absent = Path(tmp) / "nope.json"
            with self.assertRaises(GzCliError):
                evaluate_backfill_for_audit(
                    Path(tmp),
                    adr_lane="lite",
                    adr_kind="feature",
                    strict=False,
                    covers_locations=[("REQ-0.0.23-05-01", "tests/x.py", 10)],
                    obpi_completion_events=[],
                    thresholds_path=absent,
                    git_runner=FakeGit([(0, "deadbee|2026-04-01T00:00:00+00:00\n", "")]),
                )


# --------------------------------------------------------------------------- #
# Result-model defaults                                                         #
# --------------------------------------------------------------------------- #


class TestBackfillResult(unittest.TestCase):
    @covers("REQ-0.0.23-05-06")
    def test_defaults_are_empty_and_zero(self) -> None:
        result = BackfillResult()
        self.assertEqual(result.findings, ())
        self.assertEqual(result.unresolvable, ())
        self.assertEqual(result.exit_code, 0)


# --------------------------------------------------------------------------- #
# TestCliSurfaceCoverage — REQ-0.0.23-05-10 / REQ-0.0.23-05-11 traceability    #
# --------------------------------------------------------------------------- #


class TestCliSurfaceCoverage(unittest.TestCase):
    """Surface-level parity assertions complementing the wiring tests."""

    @covers("REQ-0.0.23-05-10")
    def test_strict_flag_registered_on_parser(self) -> None:
        """The --strict flag must reach the parser layer, not just the doc
        (REQ-10 mechanical surface)."""
        import argparse

        from gzkit.cli.parser_artifacts import register_artifact_parsers

        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        register_artifact_parsers(sub)
        ns = parser.parse_args(["adr", "audit-check", "ADR-0.1.0", "--strict"])
        self.assertTrue(getattr(ns, "strict", False))

    @covers("REQ-0.0.23-05-11")
    def test_canonical_arb_step_commands_cover_heavy_gates(self) -> None:
        """REQ-11: ARB receipts must exist for every heavy-lane gate. The
        canonical step commands the ARB validator accepts is the witness
        surface — assert the heavy-gate commands are registered there so
        Stage 3 verification can mint receipts under canonical names."""
        from gzkit.arb.validator import CANONICAL_STEP_COMMANDS

        names = set(CANONICAL_STEP_COMMANDS.keys())
        # Heavy-lane gates per AGENTS.md § Attestation. `ruff` ships as a
        # dedicated `gz arb ruff` verb (not `arb step --name ruff`), so it's
        # not in this dict; the rest are `arb step --name <X>` invocations.
        for required in ("typecheck", "unittest", "coverage", "mkdocs"):
            self.assertIn(required, names, f"canonical step '{required}' not registered")


# --------------------------------------------------------------------------- #
# TestAdrAuditCheckIntegration — wiring tests (REQ-0.0.23-05 CLI integration)  #
# --------------------------------------------------------------------------- #


class TestAdrAuditCheckIntegration(unittest.TestCase):
    """Wiring-level tests: adr_audit_check calls the heuristic correctly.

    Every git boundary and every gzkit infrastructure dependency is mocked.
    These tests cover the *wiring* layer (correct arguments forwarded, correct
    exit-code precedence) — not the heuristic internals (covered above).
    """

    def setUp(self) -> None:
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        self._stdout_redirect = contextlib.redirect_stdout(io.StringIO())
        self._stdout_redirect.__enter__()

    def tearDown(self) -> None:
        # Backstop: halt every patcher started in this test, including any
        # unmanaged ``patch(...).start()`` calls that don't pair with a
        # ``stop()``. Prevents patch leakage into sibling test modules
        # (caught when test_runtime sees stubbed adr_audit internals).
        from unittest.mock import patch as _patch

        _patch.stopall()
        self._stdout_redirect.__exit__(None, None, None)

    # Shared patch targets at the adr_audit module's import-site namespace.
    _HEURISTIC_PATCH = "gzkit.commands.adr_audit.evaluate_backfill_for_audit"
    _ENSURE_INIT_PATCH = "gzkit.commands.adr_audit.ensure_initialized"
    _PROJECT_ROOT_PATCH = "gzkit.commands.adr_audit.get_project_root"
    _LEDGER_PATCH = "gzkit.commands.adr_audit.Ledger"
    _RESOLVE_ADR_FILE_PATCH = "gzkit.commands.adr_audit.resolve_adr_file"
    _RESOLVE_LEDGER_ID_PATCH = "gzkit.commands.adr_audit.resolve_adr_ledger_id"
    _REJECT_POOL_PATCH = "gzkit.commands.adr_audit._reject_pool_adr_for_lifecycle"
    _COLLECT_OBPI_PATCH = "gzkit.commands.adr_audit._collect_obpi_files_for_adr"
    _COLLECT_FINDINGS_PATCH = "gzkit.commands.adr_audit._collect_obpi_findings"
    _COMPUTE_COVERAGE_PATCH = "gzkit.commands.adr_audit._compute_adr_coverage"
    _PARTITION_COVERAGE_PATCH = "gzkit.commands.adr_audit._partition_coverage_findings"

    def _make_base_patches(
        self,
        adr_id: str = "ADR-0.1.0",
        *,
        obpi_findings: list[Any] | None = None,
        coverage_blocking: list[Any] | None = None,
    ) -> list[unittest.mock.patch]:  # type: ignore
        """Build the standard infrastructure patches so the heuristic path is reachable."""
        from unittest.mock import MagicMock, patch

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)

        # Write a minimal thresholds file the heuristic (if reached) can load.
        # For wiring tests the heuristic is mocked so this is a placeholder.
        mock_config = MagicMock()
        mock_config.paths.ledger = ".gzkit/ledger.jsonl"
        mock_config.paths.adrs = "docs/design/adr"

        mock_ledger = MagicMock()
        mock_ledger.canonicalize_id.side_effect = lambda x: x
        mock_ledger.get_artifact_graph.return_value = {}
        mock_ledger.query.return_value = []

        mock_adr_path = MagicMock()
        mock_adr_path.read_text.return_value = "---\nlane: lite\nkind: feature\n---\n# ADR\n"

        return [
            patch(self._ENSURE_INIT_PATCH, return_value=mock_config),
            patch(self._PROJECT_ROOT_PATCH, return_value=project_root),
            patch(self._LEDGER_PATCH, return_value=mock_ledger),
            patch(self._RESOLVE_ADR_FILE_PATCH, return_value=(mock_adr_path, adr_id)),
            patch(self._RESOLVE_LEDGER_ID_PATCH, return_value=adr_id),
            patch(self._REJECT_POOL_PATCH),
            patch(self._COLLECT_OBPI_PATCH, return_value=({}, [])),
            patch(self._COLLECT_FINDINGS_PATCH, return_value=(obpi_findings or [], [])),
            patch(
                self._COMPUTE_COVERAGE_PATCH,
                return_value={
                    "total_reqs": 0,
                    "covered_reqs": 0,
                    "coverage_percent": 0.0,
                    "by_obpi": [],
                    "uncovered": [],
                },
            ),
            patch(
                self._PARTITION_COVERAGE_PATCH,
                return_value=([], coverage_blocking or [], []),
            ),
        ]

    def _apply_patches(self, patches: list) -> list:
        started = []
        for p in patches:
            started.append(p.start())
        return started

    def _stop_patches(self, patches: list) -> None:
        for p in patches:
            p.stop()

    @covers("REQ-0.0.23-05-02")
    def test_audit_check_calls_heuristic_with_warning_severity_on_lite_feature_adr(
        self,
    ) -> None:
        """lite lane + feature kind + strict=False → heuristic called with severity=warning."""
        from unittest.mock import patch

        from gzkit.commands.adr_audit import adr_audit_check

        patches = self._make_base_patches("ADR-0.1.0")
        self._apply_patches(patches)
        try:
            with patch(self._HEURISTIC_PATCH, return_value=BackfillResult()) as mock_heuristic:
                adr_audit_check(adr="ADR-0.1.0", as_json=False, strict=False)
                self.assertTrue(mock_heuristic.called)
                _args, kwargs = mock_heuristic.call_args
                # lite + feature + strict=False → warning severity flows via
                # adr_lane='lite', adr_kind='feature', strict=False
                self.assertEqual(kwargs.get("adr_lane"), "lite")
                self.assertEqual(kwargs.get("adr_kind"), "feature")
                self.assertFalse(kwargs.get("strict", True))
        finally:
            self._stop_patches(patches)

    @covers("REQ-0.0.23-05-03")
    def test_audit_check_calls_heuristic_with_blocking_severity_on_foundation_adr(
        self,
    ) -> None:
        """foundation ADR (0.0.x) → adr_kind='foundation' passed to heuristic."""
        from unittest.mock import MagicMock, patch

        from gzkit.commands.adr_audit import adr_audit_check

        # Override the ADR path mock to return foundation-kind frontmatter.
        mock_adr_path = MagicMock()
        mock_adr_path.read_text.return_value = "---\nlane: lite\nkind: foundation\n---\n# ADR\n"
        patches = self._make_base_patches("ADR-0.0.23")
        self._apply_patches(patches)
        # Override the adr_file return for foundation kind.
        patch(self._RESOLVE_ADR_FILE_PATCH, return_value=(mock_adr_path, "ADR-0.0.23")).start()
        patch(self._RESOLVE_LEDGER_ID_PATCH, return_value="ADR-0.0.23").start()
        try:
            with patch(self._HEURISTIC_PATCH, return_value=BackfillResult()) as mock_heuristic:
                adr_audit_check(adr="ADR-0.0.23", as_json=False, strict=False)
                self.assertTrue(mock_heuristic.called)
                _args, kwargs = mock_heuristic.call_args
                # ADR-0.0.23 is a foundation ADR → kind must be "foundation".
                self.assertEqual(kwargs.get("adr_kind"), "foundation")
        finally:
            self._stop_patches(patches)

    @covers("REQ-0.0.23-05-03")
    def test_audit_check_calls_heuristic_with_blocking_severity_on_heavy_adr(
        self,
    ) -> None:
        """heavy lane → adr_lane='heavy' passed to heuristic."""
        from unittest.mock import MagicMock, patch

        from gzkit.commands.adr_audit import adr_audit_check

        mock_adr_path = MagicMock()
        mock_adr_path.read_text.return_value = "---\nlane: heavy\nkind: feature\n---\n# ADR\n"
        patches = self._make_base_patches("ADR-0.1.0")
        self._apply_patches(patches)
        patch(self._RESOLVE_ADR_FILE_PATCH, return_value=(mock_adr_path, "ADR-0.1.0")).start()
        patch(self._RESOLVE_LEDGER_ID_PATCH, return_value="ADR-0.1.0").start()
        try:
            with patch(self._HEURISTIC_PATCH, return_value=BackfillResult()) as mock_heuristic:
                adr_audit_check(adr="ADR-0.1.0", as_json=False, strict=False)
                self.assertTrue(mock_heuristic.called)
                _args, kwargs = mock_heuristic.call_args
                self.assertEqual(kwargs.get("adr_lane"), "heavy")
        finally:
            self._stop_patches(patches)

    @covers("REQ-0.0.23-05-02")
    def test_audit_check_calls_heuristic_with_strict_flag_threaded(self) -> None:
        """strict=True propagates to the heuristic call."""
        from unittest.mock import patch

        from gzkit.commands.adr_audit import adr_audit_check

        patches = self._make_base_patches("ADR-0.1.0")
        self._apply_patches(patches)
        try:
            with patch(self._HEURISTIC_PATCH, return_value=BackfillResult()) as mock_heuristic:
                adr_audit_check(adr="ADR-0.1.0", as_json=False, strict=True)
                _args, kwargs = mock_heuristic.call_args
                self.assertTrue(kwargs.get("strict", False))
        finally:
            self._stop_patches(patches)

    @covers("REQ-0.0.23-05-03")
    def test_audit_check_exits_3_on_blocking_findings(self) -> None:
        """BackfillResult.exit_code == 3 → SystemExit(3)."""
        from unittest.mock import patch

        from gzkit.commands.adr_audit import adr_audit_check

        finding = BackfillFinding(
            req_id="REQ-0.1.0-01-01",
            file="tests/x.py",
            line=1,
            introducing_commit_sha="aaaaaaa",
            closing_receipt_id="r1",
            gap_commits=0,
            gap_days=0,
            severity="blocking",
        )
        blocking_result = BackfillResult(findings=(finding,), exit_code=3)

        patches = self._make_base_patches("ADR-0.1.0")
        self._apply_patches(patches)
        try:
            with patch(self._HEURISTIC_PATCH, return_value=blocking_result):
                with self.assertRaises(SystemExit) as ctx:
                    adr_audit_check(adr="ADR-0.1.0", as_json=False, strict=False)
                self.assertEqual(ctx.exception.code, 3)
        finally:
            self._stop_patches(patches)

    @covers("REQ-0.0.23-05-07")
    def test_audit_check_exits_2_on_unresolvable_with_strict(self) -> None:
        """BackfillResult.exit_code == 2 → SystemExit(2)."""
        from unittest.mock import patch

        from gzkit.commands.adr_audit import adr_audit_check

        unresolvable_result = BackfillResult(
            unresolvable=("tests/x.py:1 unresolvable",), exit_code=2
        )

        patches = self._make_base_patches("ADR-0.1.0")
        self._apply_patches(patches)
        try:
            with patch(self._HEURISTIC_PATCH, return_value=unresolvable_result):
                with self.assertRaises(SystemExit) as ctx:
                    adr_audit_check(adr="ADR-0.1.0", as_json=False, strict=True)
                self.assertEqual(ctx.exception.code, 2)
        finally:
            self._stop_patches(patches)

    @covers("REQ-0.0.23-05-02")
    def test_audit_check_exits_0_on_warning_findings(self) -> None:
        """Warning-severity findings (exit_code=0) → no SystemExit from heuristic path."""
        from unittest.mock import patch

        from gzkit.commands.adr_audit import adr_audit_check

        finding = BackfillFinding(
            req_id="REQ-0.1.0-01-01",
            file="tests/x.py",
            line=1,
            introducing_commit_sha="aaaaaaa",
            closing_receipt_id="r1",
            gap_commits=0,
            gap_days=0,
            severity="warning",
        )
        warning_result = BackfillResult(findings=(finding,), exit_code=0)

        patches = self._make_base_patches("ADR-0.1.0")
        self._apply_patches(patches)
        try:
            with patch(self._HEURISTIC_PATCH, return_value=warning_result):
                # Must not raise SystemExit for exit_code=0
                try:
                    adr_audit_check(adr="ADR-0.1.0", as_json=False, strict=False)
                except SystemExit as exc:
                    self.fail(f"adr_audit_check raised SystemExit({exc.code}) for warning findings")
        finally:
            self._stop_patches(patches)

    @covers("REQ-0.0.23-05-05")
    def test_audit_check_json_output_includes_backfill_keys(self) -> None:
        """--json output includes covers_backfill_findings and covers_backfill_unresolvable."""
        import io
        from contextlib import redirect_stdout
        from unittest.mock import patch

        from gzkit.commands.adr_audit import adr_audit_check

        finding = BackfillFinding(
            req_id="REQ-0.1.0-01-01",
            file="tests/x.py",
            line=5,
            introducing_commit_sha="aaaaaaa",
            closing_receipt_id="r1",
            gap_commits=1,
            gap_days=0,
            severity="warning",
        )
        result_with_findings = BackfillResult(
            findings=(finding,), unresolvable=("diag1",), exit_code=0
        )

        patches = self._make_base_patches("ADR-0.1.0")
        self._apply_patches(patches)
        buf = io.StringIO()
        try:
            with (
                patch(self._HEURISTIC_PATCH, return_value=result_with_findings),
                redirect_stdout(buf),
            ):
                adr_audit_check(adr="ADR-0.1.0", as_json=True, strict=False)
        finally:
            self._stop_patches(patches)

        output = json.loads(buf.getvalue())
        self.assertIn("covers_backfill_findings", output)
        self.assertIn("covers_backfill_unresolvable", output)
        self.assertIsInstance(output["covers_backfill_findings"], list)
        self.assertEqual(len(output["covers_backfill_findings"]), 1)
        self.assertEqual(output["covers_backfill_findings"][0]["req_id"], "REQ-0.1.0-01-01")
        self.assertIsInstance(output["covers_backfill_unresolvable"], list)
        self.assertEqual(output["covers_backfill_unresolvable"], ["diag1"])


if __name__ == "__main__":
    unittest.main()
