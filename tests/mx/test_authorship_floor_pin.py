"""The authorship guard enforces a floor concern and must never demote (GHI #852).

``gz validate --authorship`` and ``gz check``'s "Authorship policy" step both
enforce ``operator-pii`` -- a ``GATE5_INVARIANTS`` member -- but register under
the name ``authorship``.  ``checkpoint.resolve`` decides floor membership by
string match against ``GATE5_INVARIANTS``, so neither surface was seen by the
floor and both demoted to advisory inside an open hangar.  Measured on GHI #852
before the fix: a violating ``user.email`` produced a green.

The repair is by LEVEL, not by NAME -- the same lever ``guards.py`` uses for
``post-authoring-src-commits`` and ``quality.py`` uses for "Enforcement floor".
Renaming the scope into ``GATE5_INVARIANTS`` would assert that an email-suffix
check covers the whole operator-PII prohibition (commits, trailers, file
content, attestation text, ledger), which it does not -- the narrower-proxy
binding ADR-0.0.74 § Consequences/Negative #7 forbids.

The control case is load-bearing: pinning every scope would close this defect by
disabling the hangar, which is not a fix.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.mx import marker
from gzkit.mx.marker import Marker


def _hangar_root(tmp: str) -> Path:
    """Return a project root with an OPEN hangar marker."""
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    marker.write(Marker(session_id="ghi-852-test"), root)
    return root


def _registry_entry(stem: str):
    """Return the VALIDATOR_REGISTRY entry for *stem*."""
    from gzkit.commands.validate_cmd import VALIDATOR_REGISTRY

    for entry in VALIDATOR_REGISTRY:
        if entry.stem == stem:
            return entry
    raise AssertionError(f"no VALIDATOR_REGISTRY entry for {stem!r}")


class TestAuthorshipHoldsInsideHangar(unittest.TestCase):
    """An open hangar must not turn an operator-PII violation into a green."""

    def test_validate_scope_still_grounds_under_marker(self) -> None:
        """`gz validate --authorship` blocks inside the hangar, not merely outside.

        Asserts the composed semantic the GHI measured -- route and grounding --
        at the level the registry declares, never a level the test supplies.  A
        test that passed its own CRITICAL in would prove the checkpoint works and
        say nothing about how the authorship scope is registered, which is the
        entire defect.
        """
        from gzkit.mx import checkpoint, disposition

        with TemporaryDirectory() as tmp:
            root = _hangar_root(tmp)
            entry = _registry_entry("authorship")
            route = checkpoint.resolve("authorship", entry.level, root)

            self.assertNotEqual(
                route,
                disposition.Route.ADVISORY,
                "authorship enforces the operator-pii floor concern and must not "
                "demote inside an open hangar (GHI #852)",
            )
            self.assertTrue(
                disposition.grounds(route),
                "a demoted authorship finding lets a violating user.email reach a "
                "repo-bound artifact; AGENTS.md prices recovery at a filter-repo "
                "rewrite plus force-push",
            )

    def test_check_step_still_grounds_under_marker(self) -> None:
        """`gz check`'s "Authorship policy" step blocks inside the hangar.

        The sibling surface.  `quality.py` already carries a per-step level and
        pins "Enforcement floor" CRITICAL, so this cause is a value that was
        never set rather than a lever that was missing -- fixing only the
        validate scope would close the instance and leave the class open.
        """
        from gzkit.commands.quality import _STEP_GUARD_META, _apply_mx_seam
        from gzkit.quality import QualityResult

        with TemporaryDirectory() as tmp:
            root = _hangar_root(tmp)
            guard_name, emitted_level = _STEP_GUARD_META["Authorship policy"]
            breach = QualityResult(
                success=False,
                command="gz validate --authorship",
                stdout="commit author email violates required_email_suffix",
                stderr="",
                returncode=3,
            )

            seamed = _apply_mx_seam(breach, guard_name, emitted_level, root)

            self.assertEqual(
                seamed.returncode,
                3,
                "the authorship step's policy breach must survive the MX seam "
                "inside an open hangar (GHI #852)",
            )
            self.assertFalse(seamed.success, "a demoted breach reports success to the aggregator")


class TestHangarStillDemotesNonFloorScopes(unittest.TestCase):
    """The control: the fix must pin one concern, not disable the hangar."""

    def test_ordinary_scope_still_demotes_under_marker(self) -> None:
        """A scope with no floor concern still demotes, so the hangar still works.

        Without this, "pin every scope CRITICAL" would pass the two cases above
        while destroying the repair mode ADR-0.0.74 exists to provide.
        """
        from gzkit.mx import checkpoint, disposition

        with TemporaryDirectory() as tmp:
            root = _hangar_root(tmp)
            entry = _registry_entry("cli_alignment")

            self.assertEqual(
                checkpoint.resolve("cli_alignment", entry.level, root),
                disposition.Route.ADVISORY,
                "a non-floor scope must still demote inside the hangar; pinning "
                "everything would close GHI #852 by removing the hangar",
            )


if __name__ == "__main__":
    unittest.main()
