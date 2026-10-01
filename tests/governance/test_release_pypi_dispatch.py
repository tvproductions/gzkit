"""A tag whose tag-push run failed can still be published to PyPI.

A tag push runs ``release.yml`` as it stands at the tag, so a fix landed on
main never reaches a re-run. v0.34.8 is the case: its tree carries Codex
runtime symlinks that ``uv build`` refuses, and the tag is immutable. The
``workflow_dispatch`` path runs the workflow from main against a named tag.
These tests assert what that path must guarantee: it builds the named tag
(not main), verifies that tag's own version, drops the scratch before
building, and leaves the binaries and release body to the tag-push run.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

import yaml

_WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release.yml"


def _load() -> dict[str, Any]:
    with _WORKFLOW.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _step_index(steps: list[dict[str, Any]], needle: str) -> int:
    for index, step in enumerate(steps):
        if needle in str(step.get("run") or ""):
            return index
    raise AssertionError(f"no step runs {needle!r}")


class TestPypiDispatch(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = _load()
        self.jobs = self.workflow["jobs"]
        self.pypi = self.jobs["pypi"]
        self.steps = self.pypi["steps"]

    def test_dispatch_requires_a_tag(self) -> None:
        # PyYAML reads the bare key `on` as True.
        triggers = self.workflow[True]
        self.assertTrue(triggers["workflow_dispatch"]["inputs"]["tag"]["required"])

    def test_dispatch_builds_the_named_tag_not_main(self) -> None:
        self.assertIn("inputs.tag", self.pypi["env"]["RELEASE_TAG"])
        checkout = self.steps[0]
        self.assertTrue(str(checkout["uses"]).startswith("actions/checkout"))
        self.assertEqual(checkout["with"]["ref"], "refs/tags/${{ env.RELEASE_TAG }}")

    def test_version_check_reads_the_dispatched_tag(self) -> None:
        check = self.steps[_step_index(self.steps, "Refusing to publish")]
        self.assertIn("RELEASE_TAG", check["run"])
        self.assertNotIn("GITHUB_REF_NAME", check["run"])

    def test_codex_scratch_is_dropped_before_build(self) -> None:
        self.assertLess(
            _step_index(self.steps, "rm -rf .codex/tmp"), _step_index(self.steps, "uv build")
        )

    def test_dispatch_leaves_binaries_and_release_to_the_tag_push(self) -> None:
        self.assertEqual(self.jobs["build"]["if"], "github.event_name == 'push'")
        # `release` needs `build` and has no override, so a skipped build skips it.
        self.assertEqual(self.jobs["release"]["needs"], "build")
        self.assertNotIn("if", self.jobs["release"])
        self.assertIn("github.event_name == 'workflow_dispatch'", self.pypi["if"])
        self.assertIn("needs.build.result == 'success'", self.pypi["if"])


if __name__ == "__main__":
    unittest.main()
