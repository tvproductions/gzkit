"""Build-verification members of the smoke/BVT tier (GHI #724).

`.gzkit/rules/tests.md` binds a 60s ceiling to a "Smoke/BVT" suite covering
"current-scope surfaces only". These are that suite's seed members, and they are
deliberately shaped so nobody has to maintain a roster: coverage is enumerated
from the LIVE parser, so a newly registered verb is smoke-covered the moment it
is registered. A hand-kept membership list is the thing that rots.

A smoke test asks "does this surface answer at all", not "is it correct". The
REQ-derived tests elsewhere prove correctness; these prove the build is not
fundamentally broken, fast enough that the answer is cheap to have.
"""

from __future__ import annotations

import argparse
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from gzkit.cli.main import _get_parser
from gzkit.config import GzkitConfig
from gzkit.smoke import smoke


def _top_level_verbs() -> list[str]:
    """Enumerate registered top-level verbs from the live parser."""
    parser = _get_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return sorted(action.choices)
    raise AssertionError("the gz parser registered no subcommands at all")


class CliAnswers(unittest.TestCase):
    """Every registered verb must respond to `--help` and exit 0."""

    @smoke
    def test_every_registered_verb_answers_help(self) -> None:
        verbs = _top_level_verbs()
        self.assertGreater(len(verbs), 1, msg="parser enumeration returned almost nothing")

        broken: list[tuple[str, object]] = []
        for verb in verbs:
            out, err = io.StringIO(), io.StringIO()
            try:
                with redirect_stdout(out), redirect_stderr(err):
                    _get_parser().parse_args([verb, "--help"])
            except SystemExit as exc:
                if exc.code not in (0, None):
                    broken.append((verb, exc.code))
                continue
            except Exception as exc:  # noqa: BLE001 - a verb must not explode on --help
                broken.append((verb, repr(exc)))
                continue
            broken.append((verb, "--help did not exit"))

        self.assertEqual(
            broken,
            [],
            msg=(
                "Registered verbs failed the build-verification sweep. A verb whose "
                "`--help` errors or does not exit is unreachable for operators.\n"
                + "\n".join(f"  gz {verb}: {why}" for verb, why in broken)
            ),
        )


class ProjectLoads(unittest.TestCase):
    """The config surface every command reads must parse."""

    @smoke
    def test_project_config_loads(self) -> None:
        config = GzkitConfig.load()
        self.assertIn(config.mode, ("lite", "heavy"))


if __name__ == "__main__":
    unittest.main()
