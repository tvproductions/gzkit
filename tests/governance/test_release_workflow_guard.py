"""The release workflow must never rewrite a release that is already served.

`.github/workflows/release.yml` fires on every `v*` tag push, and a tag push is
not the same event as a first release. Tag repair, a workflow re-run, a
force-pushed tag, or a mis-typed ``git push --tags`` all re-enter the workflow
with the release already published. The publishing step used to rewrite
whatever it was handed and *succeed* while doing it, so the destructive half
was the silent half (GHI #834).

Two measurements, both 2026-08-19, fix which property is the right one to
assert — and they rule out the guard that looks obvious:

* **A release already exists on the normal path.** The ceremony in
  `docs/developer/release_process.md` creates it with curated notes before the
  tag is pushed: `v0.34.4` published at 12:14:23Z, its workflow run started at
  12:14:25Z. So "skip when a release exists" would mean no release ever
  receives binaries again.
* **Assets are this workflow's alone, and a re-push replaced them.** The
  re-push of `v0.18.1` and `v0.24.1` overwrote their March/April binaries with
  fresh builds — asset `created_at` moved to `2026-08-19T01:34Z` — alongside
  appending a generated changelog line to each body.

So the two writes have two different gates: a **body** write is legitimate only
when no release exists, and an **asset** write only when the release does not
already carry every artifact the build produces. These tests assert those as
properties of the workflow rather than as the wording of any step, so the guard
can be re-expressed without the witness going quiet.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any

import yaml

_WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release.yml"

#: Ways to write a release BODY. The marketplace action manages the body on
#: every invocation, and the two `gh` verbs below set it explicitly. The family
#: is named by effect so a re-implementation is covered without editing this.
_BODY_WRITE_ACTION = "softprops/action-gh-release"
_BODY_WRITE_VERBS = ("gh release create", "gh release edit")

#: Ways to write release ASSETS.
_ASSET_WRITE_VERBS = ("gh release upload", "gh release delete-asset")

#: The read that tells the workflow what this tag has already been given.
_EXISTENCE_PROBE = "gh release view"


def _steps(workflow: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Return every ``(job_name, step)`` pair declared in the workflow."""
    return [
        (job_name, step)
        for job_name, job in (workflow.get("jobs") or {}).items()
        for step in (job.get("steps") or [])
    ]


def _label(job_name: str, step: dict[str, Any]) -> str:
    """Return a human locator for a step, for use in assertion messages."""
    return f"{job_name}/{step.get('name') or step.get('uses') or step.get('id') or '<unnamed>'}"


def _writes(step: dict[str, Any], action: str | None, verbs: tuple[str, ...]) -> bool:
    """Return True when this step performs the write named by ``action``/``verbs``."""
    uses = str(step.get("uses") or "")
    run = str(step.get("run") or "")
    return bool(action and uses.startswith(action)) or any(verb in run for verb in verbs)


def _probe_ids(workflow: dict[str, Any]) -> set[str]:
    """Return the ids of steps that read what this tag's release already holds."""
    return {
        str(step["id"])
        for _, step in _steps(workflow)
        if step.get("id") and _EXISTENCE_PROBE in str(step.get("run") or "")
    }


def ungated_writes(
    workflow: dict[str, Any], *, action: str | None, verbs: tuple[str, ...]
) -> list[str]:
    """Return labels of steps performing this write without consulting the probe.

    A write is gated only when its ``if:`` reads an output of a step that
    actually queried the release. ``if: always()``, a literal, or a condition on
    an unrelated step all leave the write reachable on a re-push, so referencing
    the probe is the property — not merely carrying some condition.
    """
    probes = _probe_ids(workflow)
    return [
        _label(job_name, step)
        for job_name, step in _steps(workflow)
        if _writes(step, action, verbs)
        and not any(f"steps.{probe}.outputs." in str(step.get("if") or "") for probe in probes)
    ]


def _body_writes(workflow: dict[str, Any]) -> list[str]:
    return ungated_writes(workflow, action=_BODY_WRITE_ACTION, verbs=_BODY_WRITE_VERBS)


def _asset_writes(workflow: dict[str, Any]) -> list[str]:
    return ungated_writes(workflow, action=None, verbs=_ASSET_WRITE_VERBS)


def _probe_step(workflow: dict[str, Any]) -> dict[str, Any] | None:
    """Return the step that queries release state, or None when there is none."""
    for _, step in _steps(workflow):
        if _EXISTENCE_PROBE in str(step.get("run") or ""):
            return step
    return None


def _built_artifact_names(workflow: dict[str, Any]) -> list[str]:
    """Return the artifact filenames the build matrix produces, sorted."""
    build = (workflow.get("jobs") or {}).get("build") or {}
    include = ((build.get("strategy") or {}).get("matrix") or {}).get("include") or []
    return sorted(str(entry["artifact"]) for entry in include if entry.get("artifact"))


class TestGatePredicate(unittest.TestCase):
    """The predicate must be able to fail, on inputs that deserve failure."""

    def test_an_unconditional_body_write_is_reported(self) -> None:
        workflow = {
            "jobs": {
                "release": {
                    "steps": [
                        {"name": "Create GitHub Release", "uses": "softprops/action-gh-release@v2"}
                    ]
                }
            }
        }
        self.assertEqual(
            _body_writes(workflow),
            ["release/Create GitHub Release"],
            "a body write with no condition is exactly the GHI #834 shape",
        )

    def test_a_condition_that_is_not_a_release_probe_is_reported(self) -> None:
        """`if: always()` is a condition, and it guards nothing."""
        workflow = {
            "jobs": {
                "release": {
                    "steps": [
                        {"name": "Publish", "run": "gh release create v1.0.0", "if": "always()"}
                    ]
                }
            }
        }
        self.assertEqual(
            _body_writes(workflow),
            ["release/Publish"],
            "carrying any condition is not the property; consulting release state is",
        )

    def test_a_write_gated_on_a_probe_output_is_not_reported(self) -> None:
        workflow = {
            "jobs": {
                "release": {
                    "steps": [
                        {"id": "existing", "run": 'gh release view "$GITHUB_REF_NAME"'},
                        {
                            "name": "Publish",
                            "run": "gh release create v1.0.0 --generate-notes",
                            "if": "steps.existing.outputs.create == 'true'",
                        },
                    ]
                }
            }
        }
        self.assertEqual(_body_writes(workflow), [])

    def test_asset_writes_are_judged_separately_from_body_writes(self) -> None:
        """The two writes have different gates, so one being safe must not excuse the other."""
        workflow = {
            "jobs": {
                "release": {
                    "steps": [
                        {"id": "existing", "run": 'gh release view "$GITHUB_REF_NAME"'},
                        {
                            "name": "Create",
                            "run": "gh release create v1 --generate-notes",
                            "if": "steps.existing.outputs.create == 'true'",
                        },
                        {"name": "Upload", "run": "gh release upload v1 --clobber a b"},
                    ]
                }
            }
        }
        self.assertEqual(_body_writes(workflow), [], "the body write is properly gated")
        self.assertEqual(
            _asset_writes(workflow),
            ["release/Upload"],
            "an ungated upload replaces published binaries on a re-push",
        )


class TestShippedReleaseWorkflow(unittest.TestCase):
    """The real workflow must carry both gates."""

    def setUp(self) -> None:
        self.workflow = yaml.safe_load(_WORKFLOW.read_text(encoding="utf-8"))

    def test_the_workflow_writes_a_release_at_all(self) -> None:
        """Guard the guard: an empty write set would pass the assertions vacuously."""
        writes = [
            _label(job, step)
            for job, step in _steps(self.workflow)
            if _writes(step, _BODY_WRITE_ACTION, _BODY_WRITE_VERBS)
            or _writes(step, None, _ASSET_WRITE_VERBS)
        ]
        self.assertTrue(writes, "no release write found — the gate assertions would be vacuous")

    def test_no_body_write_can_run_against_an_existing_release(self) -> None:
        self.assertEqual(
            _body_writes(self.workflow),
            [],
            "a re-pushed tag would reach this step and rewrite a published "
            "release body while reporting success (GHI #834)",
        )

    def test_no_asset_write_can_run_against_an_already_served_release(self) -> None:
        self.assertEqual(
            _asset_writes(self.workflow),
            [],
            "a re-pushed tag would replace the binaries published with that "
            "version, as the 2026-08-19 re-push did to v0.18.1 and v0.24.1",
        )

    def test_the_probe_resolves_the_pushed_tag(self) -> None:
        """The probe must ask about *this* tag, or it answers about the wrong release."""
        probe = _probe_step(self.workflow)
        self.assertIsNotNone(probe, "nothing consults release state")
        assert probe is not None
        self.assertIn(
            "GITHUB_REF_NAME",
            str(probe.get("run") or ""),
            "a probe against a hardcoded tag would gate on some other release",
        )

    def test_the_gate_serves_only_the_version_main_declares(self) -> None:
        """A historical tag re-pushed for reachability repair must be left alone.

        The artifact check alone cannot tell "the ceremony just created this
        release and it is still owed binaries" from "this is a 2026-03 release
        that never had any" — several tags in GHI #832's repair set carry no
        assets at all. Only the version `main` declares separates them, so the
        decision must read it.
        """
        probe = _probe_step(self.workflow)
        assert probe is not None
        run = str(probe.get("run") or "")
        self.assertIn("origin main", run, "the gate must read main, not the checked-out tag")
        self.assertIn(
            "pyproject.toml",
            run,
            "the declared version is the only signal separating a repair push "
            "from a release still owed its binaries",
        )
        self.assertIn(
            "GITHUB_REF_NAME",
            run,
            "the declared version must be compared against the pushed tag",
        )

    def test_the_probe_expects_exactly_what_the_build_produces(self) -> None:
        """The gate compares against a literal artifact set; drift would disarm it.

        The asset gate asks whether the release already carries every artifact
        this workflow builds. That comparison restates the build matrix, so
        adding a platform to the matrix without updating the gate would leave
        the gate permanently unsatisfied — and adding one to the gate without
        building it would leave it permanently satisfied, silently restoring
        the ungated behaviour this issue is about.
        """
        probe = _probe_step(self.workflow)
        assert probe is not None
        expected = ",".join(_built_artifact_names(self.workflow))
        self.assertTrue(expected, "the build matrix declares no artifacts")
        self.assertIn(
            expected,
            str(probe.get("run") or ""),
            f"the gate must compare against the built set {expected!r}",
        )
