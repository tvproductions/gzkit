"""The mandated tier-1 dispatch registry is the authority the wrapper set must cover.

`_RUNTIME_WRAPPERS` (`src/gzkit/commands/obpi_complete_adversarial.py`) exists
because the operator's 2026-08-25 directive made the Codex plugin the only
permitted tier-1 dispatch surface, so every conforming run is fronted by an
interpreter and a scan reading ``argv[0]`` refused it (GHI #884).

That fix replaced one unwitnessed anchor with another: the set enumerates nine
interpreters and nothing anywhere declares the universe they are drawn from, so
it cannot be measured (GHI #895). The failure is not hypothetical and not
fail-open -- the walk stops at the first non-wrapper and returns
``_is_cross_vendor_adversary(<that name>)``, so a mandated surface fronted by an
absent member REFUSES a claim its receipt genuinely proves. That is GHI #884's
own symptom recurring, which is why enumerating harder is not the repair.

`data/mandated_tier1_dispatch.json` declares what doctrine actually mandates.
Two properties have to hold or this just relocates the problem:

* **Nothing mandated may be uncovered.** Every argv the registry declares must
  prove cross-vendor through the real predicate. A future directive naming a
  runtime nobody added to the set fails closed HERE, at the coupling, instead of
  silently at an OBPI completion months later.
* **No wrapper may itself be a vendor name.** The walk SKIPS wrappers. A vendor
  prefix admitted into the set would make the scan step over the proof and read
  on toward the adversary's prompt -- reopening the fail-open the stop rule
  exists to close. This is the direction the first property cannot see.

The registry is a witness input, not a runtime authority: production behaviour is
the walk itself. That is the same division `tests/governance/test_active_campaign_registry.py`
draws, and the reason the prose-agreement assertion below audits the directive
rather than parsing state out of it (`.gzkit/rules/governance-core.md` -- execution
reads state from JSON, never from markdown).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.commands.obpi_complete_adversarial import (
    _RUNTIME_WRAPPERS,
    _is_cross_vendor_adversary,
    _receipt_proves_cross_vendor,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "data" / "mandated_tier1_dispatch.json"


def _surface_text(relpath: str) -> str:
    """Read a directive surface once, for the structured facts assembled in setUpClass."""
    path = REPO_ROOT / relpath
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _proves(argv: list[str]) -> bool:
    """Run the production predicate over *argv* exactly as a receipt would carry it."""
    return _receipt_proves_cross_vendor({"step": {"command": argv}})


class MandatedTier1DispatchCoherence(unittest.TestCase):
    """The registry, the wrapper set, and the directive must describe one state."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.entries = cls.registry["mandated"]
        # Resolve each directive surface ONCE into structured facts the assertions
        # read, rather than re-reading a file inside a test. Same division as
        # `test_active_campaign_registry.py`, and what
        # `.gzkit/rules/tests.md` § Prefer structured assertion targets asks for.
        cls.directives = [
            {
                "surface": entry["surface"],
                "path": entry["directive_path"],
                "binary": entry["binary"],
                "exists": (REPO_ROOT / entry["directive_path"]).is_file(),
                "names_binary": entry["binary"] in _surface_text(entry["directive_path"]),
            }
            for entry in cls.entries
        ]

    def test_registry_declares_at_least_one_mandated_dispatch(self) -> None:
        """An empty registry would satisfy every other assertion vacuously."""
        self.assertTrue(
            self.entries,
            "data/mandated_tier1_dispatch.json declares no dispatch, so the coverage "
            "assertion below passes over an empty set and witnesses nothing.",
        )

    def test_every_mandated_dispatch_proves_cross_vendor(self) -> None:
        """A dispatch doctrine MANDATES must be one the tier-1 gate can accept.

        This is the assertion GHI #895 exists for. It fails when a directive
        names a runtime that `_RUNTIME_WRAPPERS` does not cover -- the point at
        which the two rules stop composing.
        """
        for entry in self.entries:
            with self.subTest(surface=entry["surface"]):
                self.assertTrue(
                    _proves(entry["argv"]),
                    f"{entry['surface']} is mandated by {entry['directive']} but its "
                    f"argv does not resolve cross-vendor. The runtime fronting it "
                    f"({entry['runtime']!r}) is absent from _RUNTIME_WRAPPERS, so the "
                    f"gate refuses a conforming tier-1 claim (GHI #884's symptom).",
                )

    def test_a_dispatch_fronted_by_an_undeclared_runtime_does_not_prove(self) -> None:
        """Negative control: the assertion above can fail.

        Same predicate, same argv shape, one substitution -- an interpreter no
        one added to the set. Without this, a registry that happened to name only
        covered runtimes would look identical to a predicate that returns True
        unconditionally.
        """
        covered = ["node", "/x/codex-companion.mjs", "adversarial-review"]
        uncovered = [
            "definitely-not-a-declared-runtime",
            "/x/codex-companion.mjs",
            "adversarial-review",
        ]
        self.assertTrue(_proves(covered))
        self.assertFalse(_proves(uncovered))

    def test_no_runtime_wrapper_is_itself_a_cross_vendor_name(self) -> None:
        """The walk SKIPS wrappers, so a vendor in the set would skip the proof.

        `_receipt_proves_cross_vendor` continues past every member of
        `_RUNTIME_WRAPPERS` and only then reads a name. A member matching a
        vendor prefix would therefore be stepped over rather than accepted, and
        the scan would read on toward the adversary's PROMPT -- which routinely
        names vendors and is exactly the mention-vs-use fail-open the stop rule
        closes.
        """
        for wrapper in sorted(_RUNTIME_WRAPPERS):
            with self.subTest(wrapper=wrapper):
                self.assertFalse(
                    _is_cross_vendor_adversary(wrapper),
                    f"{wrapper!r} is both a skipped wrapper and a recognized vendor "
                    "prefix; the walk would step over the binary that proves the tier.",
                )

    def test_each_entry_names_a_directive_surface_that_carries_it(self) -> None:
        """The registry may not drift from the doctrine it claims to encode.

        Audits the human-facing directive against the authority, the way the
        campaign registry audits each plan's `Status:` banner. The directive is
        what an agent reads; a registry describing a dispatch that surface no
        longer mandates is a witness pinned to a rule nobody follows.
        """
        for directive in self.directives:
            with self.subTest(surface=directive["surface"]):
                self.assertTrue(
                    directive["exists"],
                    f"{directive['path']} does not exist, so the registry cites "
                    "a directive surface that cannot be read.",
                )
                self.assertTrue(
                    directive["names_binary"],
                    f"{directive['path']} no longer names {directive['binary']!r}; "
                    "the registry and the directive disagree about what is mandated.",
                )


class RuntimeWrapperSetCoversItsSiblingForms(unittest.TestCase):
    """A wrapper's primary invocation form is covered, not only its `x` sibling.

    `bunx` was in the set and `bun` was not (GHI #895). `bun script.mjs` is the
    primary way to run a `.mjs` under that runtime; admitting only the package
    -runner sibling covers the rarer form and refuses the common one.
    """

    def test_bun_fronting_the_plugin_runtime_proves_cross_vendor(self) -> None:
        self.assertTrue(_proves(["bun", "/x/codex-companion.mjs", "adversarial-review"]))

    def test_bun_fronting_a_same_vendor_binary_still_does_not_prove(self) -> None:
        """Widening the set must not widen what it accepts past the first binary."""
        self.assertFalse(_proves(["bun", "/x/claude-helper.mjs", "review"]))


if __name__ == "__main__":
    unittest.main()
