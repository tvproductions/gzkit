"""Rules delivered to adopters scope to paths an adopter can have (GHI #911).

`gz init` scaffolds gzkit's canonical rules into adopter projects, and their
`paths:` frontmatter names gzkit's OWN source tree -- `src/gzkit/mx/awareness.py`,
`src/gzkit/lock_manager.py`, `src/gzkit/commands/**`. An adopter installs
py-gzkit as a dependency and never has that tree, so those globs match nothing
there, forever. Measured 2026-08-28 on a freshly initialized and synced tree:
`gz readiness audit` exit 1, 33 unreachable applyTo patterns.

The audit already refuses this class in the other direction. `_FOREIGN_INDICATORS
= {"airlineops", "opsdev"}` scans for references to the project gzkit was
extracted FROM; the hygiene rule is that an extracted surface must not carry its
origin's identifiers. gzkit had begun doing to adopters what airlineops did to
gzkit, and the existing check could not see it because the foreign token is
`gzkit`, which is the local name here.

THE FIX IS A DELIVERY-TIME CLASSIFIER, not a scrub of the canonical frontmatter.
A scrub is lossy in both directions: these rules serve two consumers and `paths:`
can only say one thing, so removing `src/gzkit/mx/**` from mx-mode.md would stop
gzkit scoping that rule to the code it governs. The classifier keeps the
canonical rule whole and filters at the boundary where the two consumers
diverge. That is the same shape as `_prune_unshippable_chores` (GHI #783), whose
docstring already argues the design: *"Keying on the classifier rather than a
`proofs/` glob is deliberate: the class definition is the contract, and a glob
would restate one shape of it and then drift."*

`.gzkit/**` IS ADOPTER-REAL, and getting that wrong is the trap. A first pass at
classifying these matched the literal `gzkit` and reported four rules as wholly
framework-internal; three of those four were false, because `.gzkit/locks/
exchange/**` and `.gzkit/handoffs/**` are the ADOPTER's own governance
directories. Measured correctly: 14 rules carry framework-internal paths and
exactly one (`cli.md`) has no adopter-real path at all.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.instruction_audit import audit_instruction_reachability
from gzkit.rules import (
    CanonicalRule,
    RuleFrontmatter,
    _is_framework_internal_path,
    render_rules_to_dir,
)

REPO = Path(__file__).resolve().parents[2]


def _rule(rule_id: str, paths: list[str]) -> CanonicalRule:
    return CanonicalRule(
        frontmatter=RuleFrontmatter(id=rule_id, paths=paths, description="fixture rule"),
        body="Rule body.",
        source_path=f".gzkit/rules/{rule_id}.md",
    )


def _adopter_tree(name: str) -> Path:
    """A tree with no `src/gzkit/` — i.e. any project that is not the framework."""
    root = Path(name)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


class TestFrameworkInternalPredicate(unittest.TestCase):
    """The boundary is the gzkit PACKAGE, not the string 'gzkit'."""

    def test_package_source_is_framework_internal(self) -> None:
        for path in (
            "src/gzkit/mx/awareness.py",
            "src/gzkit/lock_manager.py",
            "src/gzkit/commands/**",
            "src/gzkit/hooks/**",
        ):
            self.assertTrue(_is_framework_internal_path(path), path)

    def test_the_adopters_own_governance_dirs_are_not_framework_internal(self) -> None:
        """`.gzkit/` belongs to whoever runs gz — this is the trap in this class."""
        for path in (
            ".gzkit/locks/exchange/**",
            ".gzkit/handoffs/**",
            ".gzkit/rules/**",
            ".claude/hooks/mx-awareness.py",
            ".github/instructions/**",
            "docs/design/adr/**",
            "tests/**",
            "**/*",
        ):
            self.assertFalse(_is_framework_internal_path(path), path)


class TestDeliveryScoping(unittest.TestCase):
    """Rendering into an adopter tree drops what an adopter cannot have."""

    def test_a_mixed_rule_keeps_only_its_adopter_real_paths(self) -> None:
        rule = _rule(
            "token-block-discipline",
            ["src/gzkit/lock_manager.py", ".gzkit/locks/exchange/**", ".gzkit/handoffs/**"],
        )
        with tempfile.TemporaryDirectory(prefix="gzkit-deliver-") as name:
            root = _adopter_tree(name)
            target = root / ".github" / "instructions"

            render_rules_to_dir([rule], target, "copilot", project_root=root)

            rendered = (target / "token_block_discipline.instructions.md").read_text(
                encoding="utf-8"
            )
            self.assertIn(".gzkit/locks/exchange/**", rendered)
            self.assertIn(".gzkit/handoffs/**", rendered)
            self.assertNotIn("src/gzkit/lock_manager.py", rendered)

    def test_the_framework_tree_keeps_every_path(self) -> None:
        """gzkit itself must not lose the scoping that governs its own code."""
        rule = _rule("mx-mode", ["src/gzkit/mx/**", ".gzkit/skills/gz-mx/**"])
        with tempfile.TemporaryDirectory(prefix="gzkit-deliver-") as name:
            root = Path(name)
            (root / "src" / "gzkit").mkdir(parents=True)
            (root / "src" / "gzkit" / "__init__.py").write_text("", encoding="utf-8")
            target = root / ".github" / "instructions"

            render_rules_to_dir([rule], target, "copilot", project_root=root)

            rendered = (target / "mx_mode.instructions.md").read_text(encoding="utf-8")
            self.assertIn("src/gzkit/mx/**", rendered)
            self.assertIn(".gzkit/skills/gz-mx/**", rendered)

    def test_a_wholly_internal_rule_is_not_delivered_at_all(self) -> None:
        """`cli.md` scopes only `src/gzkit/commands/**`; scoped to nothing it is noise."""
        rules = [_rule("cli", ["src/gzkit/commands/**"]), _rule("tests", ["tests/**"])]
        with tempfile.TemporaryDirectory(prefix="gzkit-deliver-") as name:
            root = _adopter_tree(name)
            target = root / ".github" / "instructions"

            written = render_rules_to_dir(rules, target, "copilot", project_root=root)

            self.assertFalse((target / "cli.instructions.md").exists())
            self.assertTrue((target / "tests.instructions.md").exists())
            self.assertEqual(len(written), 1, "an undeliverable rule must not be reported written")

    def test_claude_rules_are_scoped_on_the_same_terms(self) -> None:
        """Both vendor mirrors render from the same canonical rule."""
        rule = _rule("mx-mode", ["src/gzkit/mx/**", ".claude/hooks/mx-awareness.py"])
        with tempfile.TemporaryDirectory(prefix="gzkit-deliver-") as name:
            root = _adopter_tree(name)
            target = root / ".claude" / "rules"

            render_rules_to_dir([rule], target, "claude", project_root=root)

            rendered = (target / "mx-mode.md").read_text(encoding="utf-8")
            self.assertIn(".claude/hooks/mx-awareness.py", rendered)
            self.assertNotIn("src/gzkit/mx/**", rendered)


class TestDeliveredRulesAreReachable(unittest.TestCase):
    """The end-to-end property: no delivered pattern names the framework."""

    def test_no_delivered_pattern_names_the_gzkit_package(self) -> None:
        """Render every real canonical rule into an adopter tree and audit it.

        This is the property GHI #911 states, asserted against the actual rule
        corpus rather than fixtures — a classifier that passes on invented rules
        and leaks on the real ones would be worse than none.
        """
        from gzkit.rules import load_rules

        rules = load_rules(REPO / ".gzkit" / "rules")
        self.assertTrue(rules, "no canonical rules loaded; the corpus path moved")

        with tempfile.TemporaryDirectory(prefix="gzkit-deliver-") as name:
            root = _adopter_tree(name)
            render_rules_to_dir(
                rules, root / ".github" / "instructions", "copilot", project_root=root
            )

            leaked = [
                error.message
                for error in audit_instruction_reachability(root)
                if "src/gzkit/" in error.message
            ]

        self.assertEqual(leaked, [], "a delivered rule still scopes gzkit's own source tree")


if __name__ == "__main__":
    unittest.main()
