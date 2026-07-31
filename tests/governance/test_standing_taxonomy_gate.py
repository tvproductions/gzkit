"""Tests for OBPI-0.34.0-05: the standing taxonomy gate wired into gz check.

REQ-0.34.0-05-01 [support]: proved by its structural validator
    (`gz validate --adr-status-fresh`) plus the on-disk index artifact — NOT by
    `@covers`. TestStatusIndexReconciled below is undecorated regression
    coverage guarding future index drift; it is deliberately not this REQ's
    proof channel (ADR-0.0.59).
REQ-0.34.0-05-02 [behavior]: the "ADR taxonomy" step is present in the gz check
    aggregate and the taxonomy audit passes on the terminal post-migration tree.
REQ-0.34.0-05-03 [behavior]: no staging/fail-closed flag gates the taxonomy step —
    it resolves through the real gz check runner dispatch (anti-staging-flag doctrine).
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.traceability import covers

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STATUS_INDEX = _REPO_ROOT / "docs" / "governance" / "GovZero" / "adr-status.md"
_MANIFEST = _REPO_ROOT / "data" / "foundation_grandfather.json"


def _foundation_row_ids() -> set[str]:
    """Return the ADR ids the Layer-3 status index renders with `Kind == foundation`."""
    ids: set[str] = set()
    for line in _STATUS_INDEX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) < 5 or cells[3] != "foundation":
            continue
        link = cells[1]
        if link.startswith("["):
            ids.add(link[1 : link.index("]")])
    return ids


class TestStatusIndexReconciled(unittest.TestCase):
    """Regression coverage for the reconciled Layer-3 index.

    Undecorated by design: REQ-0.34.0-05-01 is a SUPPORT REQ whose proof channel
    is the structural validator plus the on-disk artifact. These tests guard
    against future drift; they are not the REQ's proof (ADR-0.0.59, GHI #571).
    """

    def test_status_index_matches_on_disk_canon(self) -> None:
        """The committed index must agree with on-disk ADR canon."""
        from gzkit.governance.trust_audits.taxonomy import audit_adr_status_fresh

        errors = audit_adr_status_fresh(_REPO_ROOT)
        self.assertEqual(
            [error.message for error in errors],
            [],
            "adr-status.md drifted from canon; recover with `uv run gz register-adrs`",
        )

    def test_no_ungrandfathered_foundation_rows(self) -> None:
        """Demoted foundations must not reappear as foundation rows in the index.

        Every `Kind == foundation` row must be a member of the closed grandfather
        manifest — the observable shape of "the 23 demoted foundations are gone".
        """
        from gzkit.models.foundation_grandfather import load_manifest

        grandfathered = {entry.id for entry in load_manifest(_MANIFEST)}
        self.assertEqual(
            sorted(_foundation_row_ids() - grandfathered),
            [],
            "index renders a foundation row absent from the closed manifest",
        )


class TestTaxonomyStepWiring(unittest.TestCase):
    """REQ-0.34.0-05-02: "ADR taxonomy" is a registered gz check step."""

    @covers("REQ-0.34.0-05-02")
    def test_taxonomy_step_in_check_steps(self) -> None:
        """The gz check aggregate must include the ADR taxonomy step."""
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn(
            "ADR taxonomy",
            step_names,
            "gz check must run --taxonomy permanently (OBPI-0.34.0-05, REQ-02)",
        )

    @covers("REQ-0.34.0-05-02")
    def test_taxonomy_runner_invokes_taxonomy_validator(self) -> None:
        """The runner must delegate to the --taxonomy validator scope."""
        from gzkit.quality import run_taxonomy_audit

        with patch("gzkit.quality.run_command") as mock_run:
            run_taxonomy_audit(Path("/tmp/fake-root"))

        mock_run.assert_called_once_with(
            "uv run gz validate --taxonomy", cwd=Path("/tmp/fake-root")
        )

    @covers("REQ-0.34.0-05-02")
    def test_taxonomy_runner_propagates_failure(self) -> None:
        """A failing `--taxonomy` result must surface as a failing step result.

        Asserting only the dispatched command leaves the aggregate half of the
        REQ unproven: a runner that dispatched correctly but swallowed a
        returncode=3 would keep `gz check` green over a dirty tree.
        """
        from gzkit.quality import QualityResult, run_taxonomy_audit

        failing = QualityResult(
            success=False,
            command="uv run gz validate --taxonomy",
            stdout="foundation_kind_closed",
            stderr="",
            returncode=3,
        )
        with patch("gzkit.quality.run_command", return_value=failing):
            result = run_taxonomy_audit(Path("/tmp/fake-root"))

        self.assertFalse(result.success, "a failing taxonomy audit must not report success")
        self.assertEqual(result.returncode, 3, "the policy-breach exit code must propagate")

    @covers("REQ-0.34.0-05-02")
    def test_taxonomy_step_is_last(self) -> None:
        """The closure gate lands LAST — wiring equals a terminal tree."""
        from gzkit.commands.quality import _build_check_steps

        self.assertEqual(
            _build_check_steps()[-1][0],
            "ADR taxonomy",
            "ADR-0.34.0 sequences the closure gate as the final act of the Sunset",
        )


class TestGateHonorsConfiguredAdrRoot(unittest.TestCase):
    """The gate must scan the CONFIGURED ADR root, not a hard-coded one.

    Regression: both taxonomy scanners resolved `docs/design/adr` literally and
    returned empty when it was absent, so a project on the default `design/adr`
    layout got a green `--taxonomy` while an un-grandfathered foundation sat on
    disk. A gate that fails OPEN is worse than no gate (Step-4b finding).
    """

    @covers("REQ-0.34.0-05-02")
    def test_ungrandfathered_foundation_caught_under_configured_root(self) -> None:
        """An un-grandfathered foundation under the configured root must be flagged."""
        from gzkit.config import GzkitConfig
        from gzkit.governance.trust_audits.taxonomy import audit_foundation_closure
        from tests.commands.common import CliRunner, _quick_init

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_dir = Path(config.paths.adrs) / "foundation" / "ADR-0.0.98-unlisted"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.0.98-unlisted.md").write_text(
                "---\nid: ADR-0.0.98-unlisted\nlane: lite\nkind: foundation\n"
                "semver: 0.0.98\n---\n\n# ADR-0.0.98: unlisted\n",
                encoding="utf-8",
            )
            Path("data").mkdir(parents=True, exist_ok=True)
            Path("data/foundation_grandfather.json").write_text("[]", encoding="utf-8")

            errors = audit_foundation_closure(Path().resolve())

        self.assertTrue(
            errors,
            "the closure gate must fail closed on the configured ADR root, not only "
            "on a hard-coded docs/design/adr",
        )

    @covers("REQ-0.34.0-05-02")
    def test_configured_root_outside_project_is_refused(self) -> None:
        """A configured ADR root escaping the project must never be scanned.

        Union-scanning the configured root would otherwise let `paths.adrs:
        ../outside` send every `gz check` walking outside the repository.
        """
        import json

        from gzkit.governance.trust_audits.taxonomy import _adr_roots
        from tests.commands.common import CliRunner, _quick_init

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            project = Path().resolve()
            outside = project.parent / "outside-adrs"
            outside.mkdir(parents=True, exist_ok=True)

            config = json.loads(Path(".gzkit.json").read_text(encoding="utf-8"))
            config["paths"]["adrs"] = "../outside-adrs"
            Path(".gzkit.json").write_text(json.dumps(config), encoding="utf-8")

            roots = [r.resolve() for r in _adr_roots(project)]

        self.assertNotIn(
            outside.resolve(),
            roots,
            "a configured ADR root outside the project must be refused, not scanned",
        )

    @covers("REQ-0.34.0-05-02")
    def test_file_symlink_escaping_project_is_not_scanned(self) -> None:
        """A symlinked ADR file targeting outside the project must not be read.

        Containment on roots alone is insufficient: a file symlink INSIDE a
        contained root can still point anywhere on the filesystem.
        """
        from gzkit.governance.trust_audits.taxonomy import _iter_adr_files
        from tests.commands.common import CliRunner, _quick_init

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            project = Path().resolve()
            outside_dir = project.parent / "outside-adr-target"
            outside_dir.mkdir(parents=True, exist_ok=True)
            external = outside_dir / "ADR-0.0.97-external.md"
            external.write_text(
                "---\nid: ADR-0.0.97-external\nkind: foundation\nsemver: 0.0.97\n---\n",
                encoding="utf-8",
            )

            adr_dir = project / "docs" / "design" / "adr" / "foundation"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.0.97-external.md").symlink_to(external)

            scanned = [p.resolve() for p in _iter_adr_files(project)]

        self.assertNotIn(
            external.resolve(),
            scanned,
            "a symlink escaping the project must not be scanned",
        )


class TestNoStagingFlagGuard(unittest.TestCase):
    """REQ-0.34.0-05-03: the step resolves through the real runner dispatch."""

    @covers("REQ-0.34.0-05-03")
    def test_taxonomy_step_binds_runner_directly(self) -> None:
        """The step tuple must bind run_taxonomy_audit itself, not a flag-guard wrapper.

        Anti-staging-flag doctrine: a conditional or feature-flag indirection here
        would let the gate be silently disabled over a non-terminal tree.
        """
        from gzkit.commands.quality import _build_check_steps
        from gzkit.quality import run_taxonomy_audit

        bound = dict(_build_check_steps()).get("ADR taxonomy")
        self.assertIs(
            bound,
            run_taxonomy_audit,
            "ADR taxonomy must bind run_taxonomy_audit directly (no flag-guard indirection)",
        )

    @covers("REQ-0.34.0-05-03")
    def test_taxonomy_step_uses_standard_guard_meta(self) -> None:
        """The step registers in _STEP_GUARD_META like every sibling audit."""
        from gzkit.commands.quality import _STEP_GUARD_META
        from gzkit.mx import levels as mx_levels

        self.assertEqual(_STEP_GUARD_META.get("ADR taxonomy"), ("taxonomy", mx_levels.ERROR))


if __name__ == "__main__":
    unittest.main()
