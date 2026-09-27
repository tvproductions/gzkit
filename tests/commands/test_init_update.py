"""Tests for `gz init --update` mode (OBPI-0.0.32-05).

Covers:
- Three-state detection function `_detect_refresh_state` (IDENTICAL/STALE/EDITED)
- `--update` dispatch routing (mutually exclusive with `--force`)
- Content-hash edit detection composing with version markers (REQ-06)
- Manpage documents three modes + detection contract + exit codes (REQ-08)

REQ derivation: REQ-0.0.32-05-02 (three-state detection), REQ-0.0.32-05-03
(refresh dispatch), REQ-0.0.32-05-01 (flag mutual exclusivity),
REQ-0.0.32-05-06 (edit-detection mechanism documented and composing with
existing markers), REQ-0.0.32-05-08 (manpage docs).
"""

from __future__ import annotations

import hashlib
import importlib.resources
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.canonical_history import (
    CANONICAL_SURFACES,
    HISTORY_FILE,
    load_canonical_history,
    record_canonical_history,
)
from gzkit.chores import scaffold_core_chores
from gzkit.commands import upgrade
from gzkit.commands.init_cmd import (
    RefreshResult,
    _detect_refresh_state,
    _iter_canonical_surface_files,
    _refresh_canonical_surfaces,
    _refresh_one_artifact,
    init,
)
from gzkit.skills import delivered_skill_body, scaffold_core_skills
from gzkit.surface_write import capture_surface_writes, write_if_changed
from gzkit.traceability import covers


def _hash(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


@covers("REQ-0.0.32-05-02")
class TestDetectRefreshState(unittest.TestCase):
    """Three-state detection for `gz init --update` (REQ-0.0.32-05-02).

    The project copy is compared with the wheel's bytes and with the hashes of
    every version of that file the wheel has shipped (OBPI-0.0.32-05 requirement
    4(b); operator ruling on GHI #1122). A copy matching a shipped version is
    unedited and safe to refresh; any other difference is an operator edit.
    """

    CANONICAL = b"# Skill v2\n\nNew body.\n"
    OLDER = b"# Skill v1\n\nOld body.\n"

    def test_identical_bytes_returns_identical(self) -> None:
        """Equal bytes -> IDENTICAL, whatever the history holds."""
        state = _detect_refresh_state(
            project_bytes=self.CANONICAL, canonical_bytes=self.CANONICAL, known_hashes=frozenset()
        )
        self.assertEqual(state, "IDENTICAL")

    def test_previously_shipped_version_returns_stale(self) -> None:
        """Bytes equal to an older shipped version -> STALE: unedited, refresh it."""
        state = _detect_refresh_state(
            project_bytes=self.OLDER,
            canonical_bytes=self.CANONICAL,
            known_hashes=frozenset({_hash(self.OLDER), _hash(self.CANONICAL)}),
        )
        self.assertEqual(state, "STALE")

    def test_bytes_no_version_ever_had_return_edited(self) -> None:
        """Bytes matching no shipped version -> EDITED: never overwrite."""
        edited = self.OLDER + b"Operator addition.\n"
        state = _detect_refresh_state(
            project_bytes=edited,
            canonical_bytes=self.CANONICAL,
            known_hashes=frozenset({_hash(self.OLDER), _hash(self.CANONICAL)}),
        )
        self.assertEqual(state, "EDITED")

    def test_path_with_no_history_is_edited_when_it_differs(self) -> None:
        """No recorded version for the path -> a differing copy is protected, not refreshed."""
        state = _detect_refresh_state(
            project_bytes=self.OLDER, canonical_bytes=self.CANONICAL, known_hashes=frozenset()
        )
        self.assertEqual(state, "EDITED")

    def test_emptied_file_is_edited(self) -> None:
        """An emptied project copy is no shipped version, so it is protected."""
        state = _detect_refresh_state(
            project_bytes=b"",
            canonical_bytes=self.CANONICAL,
            known_hashes=frozenset({_hash(self.OLDER)}),
        )
        self.assertEqual(state, "EDITED")


@covers("REQ-0.0.32-05-06")
class TestContentHashComposesWithVersionMarkers(unittest.TestCase):
    """The edit signal composes with `skill-version` / `rule-version` (REQ-0.0.32-05-06).

    The content hash lives in the shipped history, never in the file, so an
    author's version marker is ordinary content: a copy that differs only in its
    `skill-version:` line is STALE when that copy shipped and EDITED when it did
    not. A refresh writes the wheel's bytes exactly and adds no marker of its own.
    """

    SHIPPED = b'---\nname: demo\nmetadata:\n  skill-version: "1.0.0"\n---\nBody.\n'
    CURRENT = b'---\nname: demo\nmetadata:\n  skill-version: "1.1.0"\n---\nBody.\n'
    BUMPED = b'---\nname: demo\nmetadata:\n  skill-version: "9.9.9"\n---\nBody.\n'

    def test_shipped_older_skill_version_refreshes(self) -> None:
        state = _detect_refresh_state(
            project_bytes=self.SHIPPED,
            canonical_bytes=self.CURRENT,
            known_hashes=frozenset({_hash(self.SHIPPED)}),
        )
        self.assertEqual(state, "STALE")

    def test_operator_bumped_skill_version_is_an_edit(self) -> None:
        state = _detect_refresh_state(
            project_bytes=self.BUMPED,
            canonical_bytes=self.CURRENT,
            known_hashes=frozenset({_hash(self.SHIPPED)}),
        )
        self.assertEqual(state, "EDITED")

    def test_refresh_writes_the_wheel_bytes_and_nothing_more(self) -> None:
        source, rel = next(
            (s, r) for s, r in _iter_canonical_surface_files("gzkit.skills") if r.name == "SKILL.md"
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "SKILL.md"
            target.write_bytes(b"shipped long ago\n")
            state = _refresh_one_artifact(
                canonical_bytes=source.read_bytes(),
                project_path=target,
                dry_run=False,
                known_hashes=frozenset({_hash(b"shipped long ago\n")}),
            )
            self.assertEqual(state, "STALE")
            self.assertEqual(target.read_bytes(), source.read_bytes(), rel)


@covers("REQ-0.0.32-05-08")
class TestInitManpageDocumentsUpdateMode(unittest.TestCase):
    """Manpage `docs/user/manpages/init.md` documents the three modes
    (REQ-0.0.32-05-08): default/repair, ``--force``, ``--update``;
    the edit-detection contract; and the exit-code contract
    (0 success, 1 usage error, 3 unresolved conflicts).
    """

    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        cls.manpage_text = (repo_root / "docs" / "user" / "manpages" / "init.md").read_text(
            encoding="utf-8",
        )

    def test_documents_update_mode_section(self) -> None:
        """The manpage carries a dedicated `Update Mode` section."""
        self.assertIn("Update Mode (Version-Aware Refresh)", self.manpage_text)

    def test_documents_three_modes(self) -> None:
        """The three modes (default, --force, --update) are enumerated."""
        # The "three modes" framing is concretely surfaced in the comparison table.
        self.assertRegex(self.manpage_text, r"\bdefault\b")
        self.assertIn("--force", self.manpage_text)
        self.assertIn("--update", self.manpage_text)

    def test_documents_three_state_detection(self) -> None:
        """IDENTICAL / STALE / EDITED state names appear in the manpage."""
        for state in ("IDENTICAL", "STALE", "EDITED"):
            self.assertIn(state, self.manpage_text)

    def test_documents_detection_contract(self) -> None:
        """The manpage names the shipped hash history that decides EDITED."""
        self.assertIn("canonical_history.json", self.manpage_text)

    def test_documents_exit_code_contract(self) -> None:
        """Exit codes 0, 1, 3 are documented for --update."""
        # Per CLI doctrine: 0 success, 1 usage error, 3 policy breach.
        self.assertRegex(self.manpage_text, r"`?0`?\s*\|\s*Success")
        self.assertRegex(self.manpage_text, r"`?1`?\s*\|\s*Usage error")
        self.assertRegex(self.manpage_text, r"`?3`?\s*\|\s*Policy breach")


def _reported(result: RefreshResult) -> set[str]:
    return {*result.identical, *result.stale_refreshed, *result.edited_conflicts}


def _files_under(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


class TestUpdateWritesOnlyWhatDeliveryDefines(unittest.TestCase):
    """`gz init --update` writes into `.gzkit/` only what delivery defines (GHI #1123).

    The per-surface classifiers and the chores registry merge are the delivery
    contract (`.gzkit/rules/skill-surface-sync.md` § class-classifier; GHI #728).
    Each test runs the refresh against a temp adopter tree with no `src/gzkit/`.
    """

    def test_shared_surfaces_match_what_gz_upgrade_classifies_canonical(self) -> None:
        """Skills, rules, templates and personas: the same population as `gz upgrade`."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            result = _refresh_canonical_surfaces(root, dry_run=True)
            for surface in upgrade.KNOWN_SURFACES:
                classify = upgrade._SURFACE_CLASSIFIERS[surface]
                expected = {
                    f".gzkit/{surface}/{rel.as_posix()}"
                    for _, rel in _iter_canonical_surface_files(upgrade.SURFACE_PKG_MAP[surface])
                    if classify(Path("src/gzkit") / surface / rel, project_root=root) == "canonical"
                }
                reported = {p for p in _reported(result) if p.startswith(f".gzkit/{surface}/")}
                self.assertEqual(reported, expected, surface)

    def test_package_only_templates_are_never_written(self) -> None:
        """A package-only template never lands in `.gzkit/templates/` (REQ-0.0.32-11-04)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            _refresh_canonical_surfaces(root)
            templates = root / ".gzkit" / "templates"
            self.assertFalse((templates / "author_prompts.py").exists())
            self.assertFalse((templates / "skills").exists())

    def test_chores_match_what_first_init_scaffolds(self) -> None:
        """New slugs, their scripts and the surface files arrive exactly as `gz init` delivers."""
        with tempfile.TemporaryDirectory() as tmp:
            scaffolded, refreshed = Path(tmp) / "a", Path(tmp) / "b"
            for root in (scaffolded, refreshed):
                (root / ".gzkit").mkdir(parents=True)
            scaffold_core_chores(scaffolded)
            _refresh_canonical_surfaces(refreshed, yes=True)
            chores = Path(".gzkit") / "chores"
            self.assertEqual(_files_under(refreshed / chores), _files_under(scaffolded / chores))

    def test_registry_merge_keeps_project_local_entries(self) -> None:
        """A project's own registry entries survive; shipped entries still arrive."""
        canonical = json.loads(
            importlib.resources.files("gzkit.chores").joinpath("registry.json").read_text("utf-8")
        )
        shipped = {entry["slug"] for entry in canonical["chores"]}
        local_entry = {"slug": "my-local-chore", "projectLocal": True, "title": "Local"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / ".gzkit" / "chores" / "registry.json"
            registry.parent.mkdir(parents=True)
            local = dict(canonical, chores=[*canonical["chores"][1:], local_entry])
            registry.write_text(json.dumps(local, indent=4) + "\n", encoding="utf-8")
            before = registry.read_bytes()
            _refresh_canonical_surfaces(root, dry_run=True, yes=True)
            self.assertEqual(registry.read_bytes(), before)
            _refresh_canonical_surfaces(root, yes=True)
            slugs = {e["slug"] for e in json.loads(registry.read_text("utf-8"))["chores"]}
            self.assertIn("my-local-chore", slugs)
            self.assertLessEqual(shipped, slugs)

    def test_init_update_forwards_yes_to_the_refresh(self) -> None:
        """`gz init --update --yes` accepts the registry merge without a prompt."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            with (
                mock.patch("gzkit.commands.init_cmd.get_project_root", return_value=root),
                mock.patch(
                    "gzkit.commands.init_cmd._refresh_canonical_surfaces",
                    return_value=RefreshResult(),
                ) as refresh,
            ):
                init("lite", force=False, dry_run=False, yes=True, update=True)
            self.assertIs(refresh.call_args.kwargs["yes"], True)

    def test_missing_canonical_file_is_still_delivered(self) -> None:
        """Control: a canonical file absent from the project is written with the wheel bytes."""
        source, rel = next(
            (s, r) for s, r in _iter_canonical_surface_files("gzkit.rules") if r.suffix == ".md"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            _refresh_canonical_surfaces(root, yes=True)
            target = root / ".gzkit" / "rules" / rel
            self.assertEqual(target.read_bytes(), source.read_bytes())


class TestUpdatePreservesOperatorEdits(unittest.TestCase):
    """An operator edit survives `gz init --update` (REQ-0.0.32-05-03; GHI #1122)."""

    def _scaffold_rule(self, root: Path) -> tuple[Path, bytes]:
        source, rel = next(
            (s, r) for s, r in _iter_canonical_surface_files("gzkit.rules") if r.suffix == ".md"
        )
        target = root / ".gzkit" / "rules" / rel
        target.parent.mkdir(parents=True)
        return target, source.read_bytes()

    def test_edited_scaffolded_file_is_a_conflict_and_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target, shipped = self._scaffold_rule(root)
            edited = shipped + b"\nAn operator's own clause.\n"
            target.write_bytes(edited)
            result = _refresh_canonical_surfaces(root, yes=True)
            display = target.relative_to(root).as_posix()
            self.assertIn(display, result.edited_conflicts)
            self.assertEqual(target.read_bytes(), edited)

    def test_file_holding_an_older_shipped_version_is_refreshed(self) -> None:
        older = b"a version this path shipped in an earlier release\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target, shipped = self._scaffold_rule(root)
            target.write_bytes(older)
            key = f"rules/{target.relative_to(root / '.gzkit' / 'rules').as_posix()}"
            history = {key: frozenset({_hash(older)})}
            with mock.patch("gzkit.commands.init_cmd.load_canonical_history", return_value=history):
                result = _refresh_canonical_surfaces(root, yes=True)
            self.assertIn(target.relative_to(root).as_posix(), result.stale_refreshed)
            self.assertEqual(target.read_bytes(), shipped)


class TestUpdateAgreesWithSkillDelivery(unittest.TestCase):
    """Skill routers are delivered scoped (GHI #915); `--update` compares and writes that form."""

    def test_fresh_scaffold_is_identical_under_update(self) -> None:
        """An untouched scaffold holds no conflicts and nothing to refresh."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scaffold_core_skills(root)
            result = _refresh_canonical_surfaces(root, dry_run=True, yes=True)
            skills = [
                p for p in (*result.edited_conflicts, *result.stale_refreshed) if "/skills/" in p
            ]
            self.assertEqual(skills, [])

    def test_refreshed_router_equals_what_scaffold_delivers(self) -> None:
        """A restored router carries no route to a skill the wheel withholds."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scaffold_core_skills(root)
            routers = [
                p
                for p in (root / ".gzkit" / "skills").glob("*/SKILL.md")
                if p.read_bytes()
                != (
                    Path(__file__).parents[2]
                    / "src"
                    / "gzkit"
                    / "skills"
                    / p.parent.name
                    / "SKILL.md"
                ).read_bytes()
            ]
            self.assertTrue(routers, "no scoped router to exercise")
            delivered = {p: p.read_bytes() for p in routers}
            for path in routers:
                path.unlink()
            _refresh_canonical_surfaces(root, yes=True)
            for path, expected in delivered.items():
                self.assertEqual(path.read_bytes(), expected, path.parent.name)


class TestCanonicalHistory(unittest.TestCase):
    """The shipped history records every version sync has shipped (GHI #1122)."""

    def _pkg(self, root: Path, files: dict[str, bytes]) -> Path:
        pkg = root / "src" / "gzkit"
        for rel, payload in files.items():
            path = pkg / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        (pkg / HISTORY_FILE).write_text('{"files": {}}\n', encoding="utf-8")
        return pkg

    def _recorded(self, pkg: Path) -> dict[str, list[str]]:
        return json.loads((pkg / HISTORY_FILE).read_text(encoding="utf-8"))["files"]

    def test_record_appends_new_versions_and_never_drops_old_ones(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = self._pkg(root, {"rules/a.md": b"v1\n"})
            record_canonical_history(pkg, root, [])
            (pkg / "rules" / "a.md").write_bytes(b"v2\n")
            record_canonical_history(pkg, root, [])
            self.assertEqual(
                set(self._recorded(pkg)["rules/a.md"]), {_hash(b"v1\n"), _hash(b"v2\n")}
            )

    def test_package_internal_files_are_not_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = self._pkg(root, {"rules/a.md": b"v1\n", "rules/__init__.py": b"x = 1\n"})
            record_canonical_history(pkg, root, [])
            self.assertEqual(set(self._recorded(pkg)), {"rules/a.md"})

    def test_capture_records_the_bytes_sync_would_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = self._pkg(root, {"rules/a.md": b"v1\n"})
            with capture_surface_writes() as sink:
                write_if_changed(pkg / "rules" / "a.md", b"v2\n")
                record_canonical_history(pkg, root, [])
            planned = json.loads(sink.written[(pkg / HISTORY_FILE).resolve()])["files"]
            self.assertIn(_hash(b"v2\n"), planned["rules/a.md"])
            self.assertEqual(self._recorded(pkg), {})

    def test_router_history_holds_its_scoped_delivered_form(self) -> None:
        """A router scoped at delivery is recorded in that form too, so older adopters match."""
        router = (
            b"---\nname: gz-router\n---\n| Intent | Skill |\n|---|---|\n"
            b"| a | `gz-kept` |\n| b | `gz-retired` |\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = self._pkg(
                root,
                {
                    "skills/gz-router/SKILL.md": router,
                    "skills/gz-kept/SKILL.md": b"---\nname: gz-kept\n---\nBody.\n",
                    "skills/gz-retired/SKILL.md": (
                        b"---\nname: gz-retired\nlifecycle_state: retired\n---\n"
                    ),
                },
            )
            record_canonical_history(pkg, root, [])
            scoped = delivered_skill_body(router, {"gz-router", "gz-kept"})
            self.assertNotEqual(scoped, router)
            self.assertIn(_hash(scoped), self._recorded(pkg)["skills/gz-router/SKILL.md"])

    def test_shipped_history_holds_every_current_canonical_file(self) -> None:
        """Completeness witness: what the wheel ships now is in the history it ships."""
        history = load_canonical_history()
        missing = [
            f"{surface}/{rel.as_posix()}"
            for surface in CANONICAL_SURFACES
            for source, rel in _iter_canonical_surface_files(f"gzkit.{surface}")
            if _hash(source.read_bytes()) not in history.get(f"{surface}/{rel.as_posix()}", ())
        ]
        self.assertEqual(missing, [], "run `uv run gz agent sync control-surfaces`")


if __name__ == "__main__":
    unittest.main()
