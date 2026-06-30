"""REQ-derived tests for the OKF progressive-disclosure path (OBPI-0.30.0-05).

These tests verify the one working progressive-disclosure path: a control
surface names the bundle root, and the bundle's link graph is reachable
end-to-end from that root.

Assertions derive from the brief's Requirements (FAIL-CLOSED), NOT from a
run of the implementation (.gzkit/rules/tests.md § "Tests assert semantics,
not strings").
"""

import re
import subprocess
import unittest
from pathlib import Path

import yaml

from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).parents[2]
_BUNDLE_ROOT = _PROJECT_ROOT / ".gzkit" / "governance" / "knowledge" / "index.md"
_CONTROL_SURFACE = _PROJECT_ROOT / "docs" / "user" / "concepts" / "okf-navigation.md"


def _parse_md_links(text: str) -> list[str]:
    """Return relative link targets from markdown link syntax."""
    return re.findall(r"\[.*?\]\((\./[^)]+)\)", text)


class TestBundleRootReachability(unittest.TestCase):
    """REQ-0.30.0-05-01: bundle link graph walks from root to canonical source."""

    @covers("REQ-0.30.0-05-01")
    def test_all_tracer_slice_concepts_reachable(self) -> None:
        """index.md -> each concept doc -> resource link -> canonical source all exist."""
        self.assertTrue(_BUNDLE_ROOT.exists(), f"Bundle root missing: {_BUNDLE_ROOT}")
        body = _BUNDLE_ROOT.read_text(encoding="utf-8")
        links = _parse_md_links(body)
        self.assertGreater(len(links), 0, "Bundle root index.md has no concept links")

        bundle_dir = _BUNDLE_ROOT.parent
        for link in links:
            concept_path = (bundle_dir / link).resolve()
            self.assertTrue(
                concept_path.exists(),
                f"Concept doc linked from index.md does not exist: {link}",
            )
            concept_text = concept_path.read_text(encoding="utf-8")
            frontmatter: dict = {}
            if concept_text.startswith("---"):
                parts = concept_text.split("---", 2)
                if len(parts) >= 2:
                    frontmatter = yaml.safe_load(parts[1]) or {}
            # `resource` is OPTIONAL in the OKF model: a tracer-slice concept
            # mirrors a source and carries a resource edge that must resolve;
            # an authored leaf node (e.g. content-boundary.md doctrine) IS
            # canonical and carries none — a valid terminal of the walk. Follow
            # the edge when present; do not require it on every linked node.
            resource = frontmatter.get("resource")
            if resource is not None:
                canonical = _PROJECT_ROOT / resource
                self.assertTrue(
                    canonical.exists(),
                    f"Canonical source '{resource}' linked from {concept_path.name} does not exist",
                )


class TestControlSurfacePointer(unittest.TestCase):
    """REQ-0.30.0-05-03: control surface names the OKF bundle root as entry point."""

    @covers("REQ-0.30.0-05-03")
    def test_concept_doc_names_bundle_root(self) -> None:
        """docs/user/concepts/okf-navigation.md names the bundle root path."""
        self.assertTrue(
            _CONTROL_SURFACE.exists(),
            f"Control surface concept doc missing: {_CONTROL_SURFACE}",
        )
        content = _CONTROL_SURFACE.read_text(encoding="utf-8")
        self.assertIn(
            ".gzkit/governance/knowledge/index.md",
            content,
            "Control surface does not name the OKF bundle root as navigation entry point",
        )


class TestCLIAlignmentAfterDocUpdates(unittest.TestCase):
    """REQ-0.30.0-05-04: no unresolvable gz <verb> references in new/updated docs."""

    @covers("REQ-0.30.0-05-04")
    def test_cli_alignment_passes(self) -> None:
        """gz validate --cli-alignment exits 0 after progressive-disclosure docs land."""
        result = subprocess.run(
            ["uv", "run", "gz", "validate", "--cli-alignment"],
            capture_output=True,
            text=True,
            cwd=_PROJECT_ROOT,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"gz validate --cli-alignment failed:\n{result.stdout}\n{result.stderr}",
        )
