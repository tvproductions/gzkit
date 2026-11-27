"""Every `gz content` help example names a consumer the vendor manifest routes (GHI #1399).

A help example that names `--consumer <c>` for a surface is a claim that the
invocation runs. The routing authority is `data/vendor-manifest.json`, read
through `gzkit.content.vendors`; `compose` refuses a consumer the surface's
content type does not route (`UndeclaredConsumerRouteError`). These tests read
the examples from the live parser tree and hold each one to that routing, so an
example restating a route the manifest dropped fails here rather than teaching
the operator a refused command.
"""

import argparse
import re
import unittest
from pathlib import Path

from gzkit.cli.main import _build_parser
from gzkit.content.vendors import content_type_for_surface, routes_for

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXAMPLE = re.compile(r"gz content (?P<verb>\S+) (?P<surface>[^\s-]\S*)(?P<rest>[^\n]*)")
_CONSUMER = re.compile(r"--consumer (?P<consumer>\S+)")


def _content_parsers() -> dict[str, argparse.ArgumentParser]:
    """Return the `gz content` subcommand parsers keyed by verb."""
    root = _build_parser()
    content = _subparsers(root)["content"]
    return _subparsers(content)


def _subparsers(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    return {}


def _examples() -> list[tuple[str, str, str]]:
    """Return ``(verb, surface, consumer)`` for every help example naming a consumer."""
    found: list[tuple[str, str, str]] = []
    for verb, parser in _content_parsers().items():
        text = f"{parser.description or ''}\n{parser.epilog or ''}"
        for match in _EXAMPLE.finditer(text):
            consumer = _CONSUMER.search(match.group("rest"))
            if consumer is not None:
                found.append((verb, match.group("surface"), consumer.group("consumer")))
    return found


_RENDITION_VERBS = ("compose", "commit", "land", "advise-rendition")


def _rendition_example_surfaces() -> list[tuple[str, str]]:
    """Return ``(verb, surface)`` for each example of a verb taking a corpus surface."""
    parsers = _content_parsers()
    return [
        (verb, match.group("surface"))
        for verb in _RENDITION_VERBS
        for match in _EXAMPLE.finditer(parsers[verb].epilog or "")
    ]


class TestContentHelpExamplesNameOwnedSurfaces(unittest.TestCase):
    """A rendition verb's help example names a surface the manifest gives a content type."""

    def test_every_rendition_example_surface_is_owned(self) -> None:
        # given each rendition verb's help examples
        examples = _rendition_example_surfaces()
        self.assertTrue(examples, "no rendition-verb help example names a surface")
        for verb, surface in examples:
            with self.subTest(verb=verb, surface=surface):
                # when the vendor manifest is asked who owns the surface
                owner = content_type_for_surface(surface, project_root=_REPO_ROOT)
                # then the surface has a content type, so the example can run
                self.assertIsNotNone(owner, f"{surface!r} has no content type in the manifest")


class TestContentHelpExamplesNameRoutedConsumers(unittest.TestCase):
    """A `--consumer` in a content help example is one the surface's content type routes."""

    def test_examples_naming_a_consumer_exist(self) -> None:
        # given the live content parser tree
        # when its help examples are read
        examples = _examples()
        # then some name a consumer, so the routing check below is not vacuous
        self.assertTrue(examples, "no `gz content` help example names --consumer")

    def test_every_example_consumer_is_routed_for_its_surface(self) -> None:
        # given each help example's surface and consumer
        for verb, surface, consumer in _examples():
            with self.subTest(verb=verb, surface=surface, consumer=consumer):
                # when the vendor manifest is asked who owns the surface and where it routes
                owner = content_type_for_surface(surface, project_root=_REPO_ROOT)
                # then the surface is owned and the consumer is one of its routes
                self.assertIsNotNone(owner, f"{surface!r} has no content type in the manifest")
                assert owner is not None
                self.assertIn(consumer, routes_for(owner, project_root=_REPO_ROOT))


if __name__ == "__main__":
    unittest.main()
