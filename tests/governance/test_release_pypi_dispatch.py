"""A tag whose tag-push run failed can still be published to PyPI.

A tag push runs ``release.yml`` as it stands at the tag, so a fix landed on
main never reaches a re-run. v0.34.8 is the case: its tree carries Codex
runtime symlinks that ``uv build`` refuses, and the tag is immutable. The
``workflow_dispatch`` path runs the workflow from main against a named tag.
These tests assert what that path must guarantee: it builds the named tag
(not main), verifies that tag's own version, drops the scratch before
building, and leaves the binaries and release body to the tag-push run. Since
RO-9 tranche 3 the `dist` job builds and the `pypi` job publishes.
"""

import unittest
from pathlib import Path
from typing import Any

import yaml

_WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release.yml"


def _load() -> dict[Any, Any]:
    with _WORKFLOW.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _step_index(steps: list[dict[str, Any]], needle: str) -> int:
    for index, step in enumerate(steps):
        if needle in str(step.get("run") or ""):
            return index
    raise AssertionError(f"no step runs {needle!r}")


class TestPypiDispatch(unittest.TestCase):
    """Since RO-9 tranche 3, `dist` builds the named tag and `pypi` publishes it."""

    def setUp(self) -> None:
        self.workflow = _load()
        self.jobs = self.workflow["jobs"]
        self.dist = self.jobs["dist"]
        self.pypi = self.jobs["pypi"]
        self.steps = self.dist["steps"]

    def test_dispatch_requires_a_tag(self) -> None:
        # PyYAML reads the bare key `on` as True.
        triggers = self.workflow[True]
        self.assertTrue(triggers["workflow_dispatch"]["inputs"]["tag"]["required"])

    def test_dispatch_builds_and_publishes_the_named_tag_not_main(self) -> None:
        for job in (self.dist, self.pypi):
            with self.subTest(job=job["steps"][-1].get("name")):
                self.assertIn("inputs.tag", job["env"]["RELEASE_TAG"])
                checkout = job["steps"][0]
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
        self.assertIn("github.event_name == 'workflow_dispatch'", self.dist["if"])
        self.assertIn("needs.build.result == 'success'", self.dist["if"])
        self.assertEqual(self.pypi["needs"], "dist")


class TestPublishThroughUv(unittest.TestCase):
    """RO-9 tranche 3: the build holds no credential, and a published version is left alone."""

    def setUp(self) -> None:
        self.workflow = _load()
        self.jobs = self.workflow["jobs"]

    def test_only_the_publishing_job_holds_the_publishing_credential(self) -> None:
        self.assertNotIn("id-token", self.workflow["permissions"])
        holders = sorted(
            name
            for name, job in self.jobs.items()
            if (job.get("permissions") or {}).get("id-token") == "write"
        )
        self.assertEqual(holders, ["pypi"])
        self.assertFalse(
            [s for s in self.jobs["pypi"]["steps"] if "uv build" in str(s.get("run") or "")],
            msg="the job holding the credential runs no build",
        )

    def test_the_build_disables_sources(self) -> None:
        steps = self.jobs["dist"]["steps"]
        build = steps[_step_index(steps, "uv build")]
        self.assertIn("--no-sources", build["run"])

    def test_a_version_pypi_holds_is_neither_attested_nor_published(self) -> None:
        """Re-pushing a released tag stays a no-op (GHI #834)."""
        steps = self.jobs["pypi"]["steps"]
        guard = _step_index(steps, "pypi.org/pypi/py-gzkit")
        publish = _step_index(steps, "uv publish")
        attest = next(
            i for i, s in enumerate(steps) if str(s.get("uses", "")).startswith("astral-sh/attest")
        )
        self.assertLess(guard, attest)
        self.assertLess(attest, publish)
        for index in (attest, publish):
            self.assertEqual(steps[index]["if"], "steps.published.outputs.skip == 'false'")


if __name__ == "__main__":
    unittest.main()
