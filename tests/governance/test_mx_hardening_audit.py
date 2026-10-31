"""Tests for the MX hardening scope (GHI #1257).

`ttl_max_open_status`, `debt_aging_status` and `dangling_state_status` shipped with
no runtime caller, so the hangar's bounds bounded nothing. `gz validate
--mx-hardening` runs all three in `gz check`, and the session orientation announces
the same findings. A finding grounds only where its guard's own route grounds:
dangling state outside the hangar and more than one open session. A session past
its lease is announced and never grounds, in or out of exit (operator ruling
2026-10-18).
"""

import io
import json
import unittest
from contextlib import redirect_stderr
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.advisory import ADVISORY_MARKER
from gzkit.governance.trust_audits.mx_hardening import audit_mx_hardening
from gzkit.mx import marker
from gzkit.mx.marker import Marker

_REPO = Path(__file__).resolve().parents[2]
_NOW = datetime(2026, 1, 3, 0, 0, 0, tzinfo=UTC)


def _opened(session_id: str, ts: datetime) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "mx_session_opened",
        "id": session_id,
        "ts": ts.isoformat(),
        "session_id": session_id,
        "reason": "test",
        "attestor": "g0",
    }


def _root(tmp: str, events: list[dict], held: Marker | None = None) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    (root / ".gzkit" / "ledger.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in events), encoding="utf-8"
    )
    if held is not None:
        marker.write(held, root)
    return root


def _run(root: Path) -> tuple[list, list[str]]:
    stderr = io.StringIO()
    with redirect_stderr(stderr):
        errors = audit_mx_hardening(root, now=_NOW)
    advisories = [ln for ln in stderr.getvalue().splitlines() if ln.startswith(ADVISORY_MARKER)]
    return errors, advisories


class TestMxHardeningScope(unittest.TestCase):
    def test_no_open_session_reports_nothing(self) -> None:
        with TemporaryDirectory() as tmp:
            errors, advisories = _run(_root(tmp, []))
        self.assertEqual(errors, [])
        self.assertEqual(advisories, [])

    def test_a_hangar_past_its_lease_is_announced_and_grounds_nothing(self) -> None:
        """Today's live case: safe mode open past its lease, marker held."""
        opened = _NOW - timedelta(hours=30)
        for label, held in {
            "hangar open": Marker(session_id="s1", level="drydock"),
            "exit re-run": Marker(session_id="s1", level="drydock", exiting=True),
        }.items():
            with self.subTest(state=label), TemporaryDirectory() as tmp:
                errors, advisories = _run(_root(tmp, [_opened("s1", opened)], held))
                self.assertEqual(errors, [])
                lease = [ln for ln in advisories if "past its lease" in ln]
                debt = [ln for ln in advisories if "advisory debt" in ln]
                self.assertEqual(len(lease), 1, advisories)
                self.assertEqual(len(debt), 1, advisories)
                self.assertIn("s1", lease[0])

    def test_the_lease_announcement_names_the_renewal_as_its_recovery(self) -> None:
        # output-contract: the recovery step in guardrail prose is the contract (GHI #1261)
        with TemporaryDirectory() as tmp:
            held = Marker(session_id="s1", level="drydock")
            _, advisories = _run(_root(tmp, [_opened("s1", _NOW - timedelta(hours=30))], held))
        lease = [ln for ln in advisories if "past its lease" in ln]
        self.assertEqual(len(lease), 1, advisories)
        self.assertIn("gz mx renew", lease[0])

    def test_a_session_inside_its_lease_and_fresh_reports_nothing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _root(tmp, [_opened("s1", _NOW - timedelta(hours=1))], Marker(session_id="s1"))
            errors, advisories = _run(root)
        self.assertEqual(errors, [])
        self.assertEqual(advisories, [])

    def test_a_dangling_session_grounds_outside_the_hangar(self) -> None:
        with TemporaryDirectory() as tmp:
            errors, _ = _run(_root(tmp, [_opened("s1", _NOW - timedelta(hours=1))]))
        self.assertEqual([e.type for e in errors], ["mx_hardening"])
        self.assertIn("s1", errors[0].artifact)
        self.assertIn("gz mx exit", errors[0].message)

    def test_more_than_one_open_session_grounds_even_in_the_hangar(self) -> None:
        events = [_opened("s1", _NOW - timedelta(hours=1)), _opened("s2", _NOW)]
        with TemporaryDirectory() as tmp:
            errors, _ = _run(_root(tmp, events, Marker(session_id="s1")))
        self.assertEqual([e.type for e in errors], ["mx_hardening"])
        self.assertIn("max-open", errors[0].message)


class TestDispatch(unittest.TestCase):
    """The flag reaches the scope, a grounding finding exits 3, and gz check runs it."""

    def _invoke(self, with_marker: bool):
        from gzkit.cli import main
        from tests.commands.common import CliRunner, _quick_init

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger = Path(".gzkit") / "ledger.jsonl"
            with ledger.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(_opened("s1", datetime.now(UTC))) + "\n")
            if with_marker:
                marker.write(Marker(session_id="s1"), Path.cwd())
            return runner.invoke(main, ["validate", "--mx-hardening"])

    def test_a_dangling_session_is_a_policy_breach_through_the_flag(self) -> None:
        result = self._invoke(with_marker=False)
        self.assertEqual(result.exit_code, 3, result.output)
        self.assertIn("s1", result.output)
        self.assertIn("gz mx repair", " ".join(result.output.split()))

    def test_an_open_hangar_inside_its_lease_passes_through_the_flag(self) -> None:
        result = self._invoke(with_marker=True)
        self.assertEqual(result.exit_code, 0, result.output)

    def test_the_audit_is_part_of_the_packages_declared_surface(self) -> None:
        from gzkit.governance import trust_audits

        self.assertIn("audit_mx_hardening", trust_audits.__all__)
        self.assertIs(trust_audits.audit_mx_hardening, audit_mx_hardening)

    def test_gz_check_shells_the_scope_as_its_own_bound_step(self) -> None:
        from gzkit import quality
        from gzkit.commands.quality import _STEP_GUARD_META, _build_check_steps
        from gzkit.qc_binding import build_qc_registry

        runner = dict(_build_check_steps())["MX hardening"]
        with patch.object(quality, "run_command", return_value="ran") as shelled:
            self.assertEqual(runner(_REPO), "ran")
        self.assertEqual(shelled.call_args.args[0], "uv run gz validate --mx-hardening")
        self.assertEqual(_STEP_GUARD_META["MX hardening"][0], "mx-hardening")
        step = {s.name: s for s in build_qc_registry()}["MX hardening"]
        self.assertEqual((step.binding, step.subject), ("bound", ".gzkit/"))


class TestNegativeControl(unittest.TestCase):
    def test_the_control_catches_a_dangling_session_for_its_own_reason(self) -> None:
        from gzkit.enforcement import (
            EXEMPTS_NONE,
            _run_single_claim,
            production_enforcement_registry,
        )

        record = {r.claim_id: r for r in production_enforcement_registry()}["mx-hardening"]
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertEqual(record.exempts, EXEMPTS_NONE)
        self.assertIsNotNone(record.population)

    def test_the_entrypoint_reports_no_catch_when_another_finding_fires(self) -> None:
        """A gate that grounds anything but the dangling session cannot pass the control."""
        from gzkit.governance.trust_audits import _qc_nc_entrypoints as ep

        now = datetime.now(UTC)
        with TemporaryDirectory() as tmp:
            caught = ep._ep_mx_hardening(_root(tmp, [_opened("s1", now)]))
        with TemporaryDirectory() as tmp:
            # Two open sessions and no marker: dangling AND over max-open both fire.
            decoy = ep._ep_mx_hardening(_root(tmp, [_opened("s1", now), _opened("s2", now)]))
        self.assertEqual(len(caught), 1)
        self.assertIn("mx-dangling-state", caught[0].message)
        self.assertEqual(decoy, [])


if __name__ == "__main__":
    unittest.main()
