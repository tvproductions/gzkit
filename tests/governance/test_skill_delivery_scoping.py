"""Skills delivered to adopters exclude those only gzkit can run (GHI #915).

gzkit fences what it delivers at three tiers and, until this change, fenced two
of them. Canonical rules scope their `paths:` per delivery target
(`_scope_rule_for_delivery`, GHI #911); chores withhold `projectLocal` slugs
(`_prune_unshippable_chores`, GHI #783); skills had NO filter at all. Measured
2026-08-29 at `2fcba2d5`: 70 canonical skill slugs, 70 delivered, difference
empty.

THE PREDICATE IS A DECLARATION, NOT A CONTENT SCAN, and the census is why. A
scan for the framework-internal path prefixes GHI #911 settled on -- `src/gzkit/`,
`scripts/`, `data/` -- hits 23 of the 70 skills, nearly all of them falsely:
`gz-check`, `gz-plan` and `ghi-author` merely cite a gzkit path as an example,
and `gz-competitor-radar`'s `scripts/` hits are its OWN skill-local directory.
Scanning for `airlineops` hits 8, of which 6 are provenance notes or router
rows. That is precisely the drift `_prune_unshippable_chores` refuses in its own
docstring: *"a glob would restate one shape of it and then drift."* The class is
declared per-slug and the classifier reads the declaration.

TWO SLUGS QUALIFY, and each for a stated reason rather than a keyword:

- `airlineops-parity-scan` scans `../airlineops` against gzkit. Its
  preconditions require a sibling checkout an adopter has never heard of.
- `gz-competitor-radar` judges candidates by whether they name a "gzkit-relevant
  strength, rejection, or route" and recommends gzkit ADR/GHI/pool moves. Its
  subject is gzkit's own competitive position. It is also broken on arrival: the
  wheel includes only `src/gzkit/skills/**/*.md`, so the four scripts its steps
  invoke never ship at all.

TWO CANDIDATES WERE MEASURED AND REJECTED, because "inert on an adopter tree" is
a weaker claim than "only gzkit can have this subject". `gz-flighttest` settles
itself in its own body -- *"It is authored and versioned in gzkit and ships via
distribution, but it runs on the ground in the target"* -- and
`gz-complexity-distill` reads a corpus through `load_corpus(path)`, which takes
the path as an argument, so an adopter who curates their own corpus gets a real
distillation. That is the GHI #913 ruling applied one tier over: an adopter who
supplies the config gets the capability.

`gz-foundation-triage` ships for a canon reason, not a measured one. The
foundation kind is CLOSED in gzkit and `gz init` scaffolds adopters OPEN
(AGENTS.md § Kinds), so an adopter can hold a foundation backlog gzkit cannot.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.skills import _classify_skill_file

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Slugs declared project-local. Read from the canonical tree rather than
#: transcribed, so a new declaration cannot leave this test asserting the old set.
DECLARED_LOCAL = {"airlineops-parity-scan", "gz-competitor-radar"}


def _write_skill(root: Path, slug: str, *, project_local: bool) -> Path:
    """Create a canonical skill slug, optionally declaring it project-local."""
    skill_dir = root / ".gzkit" / "skills" / slug
    skill_dir.mkdir(parents=True)
    local_line = "project_local: true\n" if project_local else ""
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {slug}\ndescription: Fixture.\nlifecycle_state: active\n"
        f"{local_line}---\n\n# {slug}\n",
        encoding="utf-8",
    )
    return skill_dir


class TestSkillClassDeclaration(unittest.TestCase):
    """The class is declared in SKILL.md frontmatter and read by the classifier."""

    def test_undeclared_skill_is_canonical(self) -> None:
        """A skill that declares nothing ships, as every skill did before."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = _write_skill(root, "gz-ordinary", project_local=False)
            self.assertEqual(
                _classify_skill_file(skill_dir / "SKILL.md", project_root=root),
                "canonical",
            )

    def test_declared_skill_is_project_local(self) -> None:
        """`project_local: true` is the contract; the classifier reads it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = _write_skill(root, "gz-internal", project_local=True)
            self.assertEqual(
                _classify_skill_file(skill_dir / "SKILL.md", project_root=root),
                "project_local",
            )

    def test_declaration_withholds_the_whole_slug(self) -> None:
        """A skill's assets follow its SKILL.md, or the fence leaks around it.

        `gz-competitor-radar` carries four scripts under its own `scripts/`. A
        per-file class would ship those while withholding the SKILL.md that
        explains them -- the inverse of the chores ruling, whose classifier
        checks the per-slug declaration FIRST for exactly this reason.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = _write_skill(root, "gz-internal", project_local=True)
            asset = skill_dir / "scripts" / "run.py"
            asset.parent.mkdir()
            asset.write_text("# fixture\n", encoding="utf-8")
            self.assertEqual(
                _classify_skill_file(asset, project_root=root),
                "project_local",
            )

    def test_sibling_slug_is_unaffected(self) -> None:
        """The declaration binds one slug, never its neighbours."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root, "gz-internal", project_local=True)
            neighbour = _write_skill(root, "gz-ordinary", project_local=False)
            self.assertEqual(
                _classify_skill_file(neighbour / "SKILL.md", project_root=root),
                "canonical",
            )


class TestSkillDeliveryBoundary(unittest.TestCase):
    """Sync must both decline to add and converge by removing (GHI #783's missing direction)."""

    def _project(self, root: Path) -> None:
        """Establish the package-side skills surface sync requires."""
        pkg = root / "src" / "gzkit" / "skills"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")

    def _sync(self, root: Path) -> list[str]:
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_pkg_surfaces

        return sync_pkg_surfaces(root, GzkitConfig())

    def _delivered(self, root: Path) -> set[str]:
        """Return the slug names the package tree carries after a sync."""
        pkg = root / "src" / "gzkit" / "skills"
        return {entry.name for entry in pkg.iterdir() if entry.is_dir()}

    def test_sync_delivers_the_canonical_set_less_the_declarations(self) -> None:
        """The delivered catalogue is a SET, so over-delivery fails too.

        Two presence probes would pass a sync that also shipped a third slug
        from nowhere; the property being defended is which skills an adopter
        ends up with, which only a set equality states.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root)
            _write_skill(root, "gz-internal", project_local=True)
            _write_skill(root, "gz-ordinary", project_local=False)
            written = self._sync(root)
            self.assertEqual(self._delivered(root), {"gz-ordinary"})
            # Sync's RETURN VALUE is its own account of what it did. A delivery
            # it performs but does not report is invisible to every caller that
            # renders the change set.
            self.assertIn("src/gzkit/skills/gz-ordinary/SKILL.md", written)
            self.assertNotIn("src/gzkit/skills/gz-internal/SKILL.md", written)

    def test_package_side_residue_is_removed_and_accounted_for(self) -> None:
        """Sync walks the canonical side, so declining to copy cannot remove.

        This is the direction `_prune_unshippable_chores` was written for: a
        slug that shipped before it was declared stays in the wheel tree until
        something deletes it. Every skill declared here shipped for the life of
        the project, so on the first run this path is the whole fix.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root)
            _write_skill(root, "gz-internal", project_local=True)
            residue = root / "src" / "gzkit" / "skills" / "gz-internal" / "SKILL.md"
            residue.parent.mkdir(parents=True)
            residue.write_text("stale\n", encoding="utf-8")
            written = self._sync(root)
            self.assertEqual(self._delivered(root), set(), "residue survived the prune")
            # A silent deletion is the failure mode the chores prune's own
            # `updated.append` guards against: the removal must be reported.
            self.assertIn("src/gzkit/skills/gz-internal/SKILL.md", written)


class TestDeliveredCatalogue(unittest.TestCase):
    """The end-to-end property, asserted against this repository's real trees."""

    def test_declared_slugs_are_absent_from_the_wheel_tree(self) -> None:
        """What the canonical side declares local, the package side does not carry."""
        canonical = REPO_ROOT / ".gzkit" / "skills"
        declared = {
            d.name
            for d in canonical.iterdir()
            if d.is_dir()
            and (d / "SKILL.md").is_file()
            and _classify_skill_file((d / "SKILL.md"), project_root=REPO_ROOT) == "project_local"
        }
        self.assertEqual(
            declared,
            DECLARED_LOCAL,
            "the declared set moved; update the census in this module's docstring",
        )
        pkg = REPO_ROOT / "src" / "gzkit" / "skills"
        for slug in declared:
            self.assertFalse((pkg / slug).exists(), f"{slug} still ships")

    def test_the_distribution_gate_accepts_the_withheld_slugs(self) -> None:
        """Run the real consumer rather than imitating its manifest check.

        `_is_package_only` exempts `project_local` from ON_DISK_NOT_INCLUDED and
        ON_DISK_NOT_BASELINE, but BASELINE_NOT_ON_DISK is unconditional: a
        manifest entry naming a slug the prune removed fails the gate outright.
        Scanning the manifest for the slug names would restate that rule in a
        second place and then drift from it; calling `audit_distribution` asks
        the rule itself. Scoped to these slugs so an unrelated distribution
        failure does not masquerade as a regression of this fix.
        """
        from gzkit.governance.trust_audits.distribution import audit_distribution

        offenders = [
            error.artifact
            for error in audit_distribution(REPO_ROOT)
            if any(slug in error.artifact for slug in DECLARED_LOCAL)
        ]
        self.assertEqual(offenders, [], "the distribution gate rejects the withheld slugs")


if __name__ == "__main__":
    unittest.main()
