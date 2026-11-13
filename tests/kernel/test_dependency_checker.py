"""The dependency checker's semantics, proven on synthetic trees.

Each case plants one breach in a throwaway project and asserts the finding, so a
rule the real tree happens not to exercise is still witnessed. The rules are read
from `docs/governance/hexagonal-architecture.md` § The dependency rules and
§ Messages and decorators; the change order's three named controls are the
out-of-region import, the `Entity` outside `core/domain`, and the handler with no
use-case `Protocol` (RP-15 tranche 6, § Witness).
"""

import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.kernel.dependency_checker import (
    PackageMapError,
    Region,
    Rule,
    check,
    compare,
    load_package_map,
)

PYPROJECT = """
[tool.py-gzkit.hexagon]
package = "app"
source-root = "src"
kernel = ["app.kernel"]
domain = ["app.core.domain"]
driving-ports = ["app.core.ports.driving"]
driven-ports = ["app.core.ports.driven"]
handlers = ["app.core.handlers"]
driving-adapters = ["app.cli"]
repository-adapters = ["app.store"]
driven-adapters = ["app.git", "app.mail"]
configurator = ["app.configurator"]
"""

KERNEL = {
    "app/__init__.py": "",
    "app/kernel/__init__.py": "from app.kernel.bases import Command, Entity\n",
    "app/kernel/bases.py": "import pydantic\nclass Entity(pydantic.BaseModel): ...\n"
    "class Command(pydantic.BaseModel): ...\n",
    "app/core/__init__.py": "",
    "app/core/domain/__init__.py": "",
    "app/core/ports/__init__.py": "",
    "app/core/ports/driving/__init__.py": "",
    "app/core/ports/driven/__init__.py": "",
    "app/core/handlers/__init__.py": "",
}


RECORD = "from app.kernel import Entity\nclass Record(Entity): ...\n"


def _findings(files: dict[str, str]) -> set[str]:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
        for rel, body in {**KERNEL, **files}.items():
            target = root / "src" / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(textwrap.dedent(body), encoding="utf-8")
        package_map = load_package_map(root / "pyproject.toml")
        return {f.key for f in check(package_map, root)}


class TheConformingSkeletonIsClean(unittest.TestCase):
    def test_a_conforming_tree_has_no_finding(self) -> None:
        files = {
            "app/core/domain/record.py": (
                "from app.kernel import Entity\nclass Record(Entity): ...\n"
            ),
            "app/core/ports/driving/rename.py": """
                from typing import Protocol
                from app.kernel import Command
                class Rename(Command): ...
                class RenameUseCase(Protocol):
                    def handle(self, command: Rename) -> None: ...
            """,
            "app/core/handlers/rename.py": """
                from app.core.domain.record import Record
                from app.core.ports.driving.rename import RenameUseCase
                class RenameHandler(RenameUseCase): ...
            """,
            "app/cli/main.py": (
                "import argparse\nimport rich\nfrom app.core.ports.driving import rename\n"
            ),
            "app/store/records.py": "import sqlite3\nfrom app.core.domain.record import Record\n",
            "app/configurator.py": "from app.cli import main\nfrom app.store import records\n",
        }
        self.assertEqual(_findings(files), set())


class ImportsOutsideTheTableAreFound(unittest.TestCase):
    def test_a_planted_out_of_region_import_is_found(self) -> None:
        found = _findings({"app/core/domain/record.py": "from app.cli import main\n"})
        self.assertEqual(found, {"import app.core.domain.record -> app.cli"})

    def test_a_driving_adapter_never_sees_the_domain(self) -> None:
        found = _findings({"app/cli/main.py": "from app.core.domain import record\n"})
        self.assertEqual(found, {"import app.cli.main -> app.core.domain"})

    def test_no_adapter_imports_another_adapter(self) -> None:
        found = _findings({"app/git/repo.py": "from app.mail import send\n"})
        self.assertEqual(found, {"import app.git.repo -> app.mail"})

    def test_an_adapter_may_import_itself(self) -> None:
        found = _findings({"app/git/repo.py": "from app.git import util\n", "app/git/util.py": ""})
        self.assertEqual(found, set())

    def test_inner_regions_take_pydantic_and_no_other_library(self) -> None:
        found = _findings({"app/core/domain/graph.py": "import pydantic\nimport networkx\n"})
        self.assertEqual(found, {"import app.core.domain.graph -> networkx (third-party)"})

    def test_a_relative_import_is_resolved_before_it_is_judged(self) -> None:
        found = _findings({"app/core/handlers/rename.py": "from ...cli import main\n"})
        self.assertEqual(found, {"import app.core.handlers.rename -> app.cli"})

    def test_reaching_an_unmapped_module_is_a_breach(self) -> None:
        found = _findings({"app/core/domain/record.py": "import app.legacy\n", "app/legacy.py": ""})
        self.assertEqual(
            found, {"import app.core.domain.record -> app.legacy", "unmapped app.legacy"}
        )

    def test_a_function_local_import_is_judged(self) -> None:
        body = "def late():\n    from app.cli import main\n"
        found = _findings({"app/core/domain/record.py": body})
        self.assertEqual(found, {"import app.core.domain.record -> app.cli"})

    def test_an_import_under_type_checking_is_judged(self) -> None:
        body = "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    import app.cli\n"
        found = _findings({"app/core/domain/record.py": body})
        self.assertEqual(found, {"import app.core.domain.record -> app.cli"})

    def test_a_planted_chain_fails_at_its_first_hop(self) -> None:
        # The domain reaches the driving adapter through a helper: the domain's own edge breaches.
        files = {
            "app/core/domain/record.py": "from app.helper import fmt\n",
            "app/helper.py": "from app.cli import main\n",
        }
        self.assertEqual(
            _findings(files), {"import app.core.domain.record -> app.helper", "unmapped app.helper"}
        )

    def test_a_submodule_named_in_a_from_import_is_the_target(self) -> None:
        # `from app.core import domain` reaches the domain package, not the container.
        found = _findings({"app/cli/main.py": "from app.core import domain\n"})
        self.assertEqual(found, {"import app.cli.main -> app.core.domain"})

    def test_a_relative_import_in_a_package_init_resolves_from_the_package(self) -> None:
        body = "from ..domain import record\nfrom ...cli import main\n"
        found = _findings({"app/core/handlers/__init__.py": body, "app/core/domain/record.py": ""})
        self.assertEqual(found, {"import app.core.handlers -> app.cli"})

    def test_the_configurator_imports_everything(self) -> None:
        found = _findings(
            {"app/configurator.py": "import app.legacy\nimport networkx\n", "app/legacy.py": ""}
        )
        self.assertEqual(found, {"unmapped app.legacy"})


class UnmappedCodeIsAFinding(unittest.TestCase):
    def test_a_package_no_region_names_is_one_finding(self) -> None:
        found = _findings(
            {"app/legacy/__init__.py": "", "app/legacy/deep/mod.py": "import networkx\n"}
        )
        self.assertEqual(found, {"unmapped app.legacy"})

    def test_a_module_loose_in_a_container_is_named_itself(self) -> None:
        found = _findings({"app/core/models.py": ""})
        self.assertEqual(found, {"unmapped app.core.models"})


class KernelBasesStayInTheirRegion(unittest.TestCase):
    def test_an_entity_outside_the_domain_is_found(self) -> None:
        found = _findings(
            {"app/git/repo.py": "from app.kernel import Entity\nclass Repo(Entity): ...\n"}
        )
        self.assertEqual(found, {"base app.git.repo.Repo -> Entity subclassed in driven-adapters"})

    def test_a_base_reached_through_its_module_alias_is_found(self) -> None:
        found = _findings(
            {"app/core/domain/cmd.py": "import app.kernel as k\nclass Go(k.Command): ...\n"}
        )
        self.assertEqual(found, {"base app.core.domain.cmd.Go -> Command subclassed in domain"})

    def test_an_unmapped_subclass_is_found_too(self) -> None:
        found = _findings(
            {"app/legacy.py": "from app.kernel import Entity\nclass Old(Entity): ...\n"}
        )
        self.assertEqual(
            found, {"base app.legacy.Old -> Entity subclassed in no region", "unmapped app.legacy"}
        )

    def test_a_subclass_of_a_domain_entity_outside_the_domain_is_found(self) -> None:
        files = {
            "app/core/domain/record.py": RECORD,
            "app/store/rows.py": (
                "from app.core.domain.record import Record\nclass StoredRecord(Record): ...\n"
            ),
        }
        self.assertEqual(
            _findings(files),
            {"base app.store.rows.StoredRecord -> Entity subclassed in repository-adapters"},
        )

    def test_a_base_re_exported_by_a_package_is_followed(self) -> None:
        files = {
            "app/core/domain/__init__.py": "from app.core.domain.record import Record\n",
            "app/core/domain/record.py": RECORD,
            "app/store/rows.py": "from app.core.domain import Record\nclass Row(Record): ...\n",
        }
        self.assertEqual(
            _findings(files),
            {"base app.store.rows.Row -> Entity subclassed in repository-adapters"},
        )

    def test_a_subclass_of_a_domain_entity_inside_the_domain_is_clean(self) -> None:
        files = {
            "app/core/domain/record.py": RECORD,
            "app/core/domain/draft.py": (
                "from app.core.domain.record import Record\nclass Draft(Record): ...\n"
            ),
        }
        self.assertEqual(_findings(files), set())


class HandlersTakeOneUseCaseAndItsName(unittest.TestCase):
    PORT = """
        from typing import Protocol
        class RenameUseCase(Protocol): ...
        class ArchiveUseCase(Protocol): ...
        class NotAUseCase: ...
    """

    def _handler(self, body: str) -> set[str]:
        return _findings(
            {"app/core/ports/driving/uc.py": self.PORT, "app/core/handlers/h.py": body}
        )

    def test_a_handler_with_no_use_case_protocol_is_found(self) -> None:
        found = self._handler("class RenameHandler: ...\n")
        self.assertEqual(len(found), 1)
        self.assertTrue(
            next(iter(found)).startswith("handler app.core.handlers.h.RenameHandler -> inherits 0")
        )

    def test_a_handler_with_two_use_cases_is_found(self) -> None:
        body = "from app.core.ports.driving.uc import RenameUseCase, ArchiveUseCase\n"
        body += "class RenameHandler(RenameUseCase, ArchiveUseCase): ...\n"
        found = self._handler(body)
        self.assertTrue(any("inherits 2" in key for key in found))

    def test_a_handler_must_take_its_name_from_its_use_case(self) -> None:
        body = "from app.core.ports.driving.uc import RenameUseCase\n"
        body += "class Renamer(RenameUseCase): ...\n"
        found = self._handler(body)
        self.assertEqual(
            found, {"handler app.core.handlers.h.Renamer -> named for RenameUseCase: RenameHandler"}
        )

    def test_a_non_protocol_named_like_a_use_case_does_not_count(self) -> None:
        body = "from app.core.ports.driving.uc import NotAUseCase\n"
        body += "class NotAHandler(NotAUseCase): ...\n"
        found = self._handler(body)
        self.assertTrue(any("inherits 0" in key for key in found))

    def test_a_class_nested_in_a_handler_is_not_a_handler(self) -> None:
        body = "from app.core.ports.driving.uc import RenameUseCase\n"
        body += "class RenameHandler(RenameUseCase):\n    class Settings: ...\n"
        self.assertEqual(self._handler(body), set())

    def test_a_private_helper_class_is_not_a_handler(self) -> None:
        self.assertEqual(self._handler("class _Helper: ...\n"), set())


class ThePackageMapIsRefusedWhenMalformed(unittest.TestCase):
    def _load(self, table: str) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "pyproject.toml"
            path.write_text(table, encoding="utf-8")
            load_package_map(path)

    def test_a_missing_map_is_refused(self) -> None:
        with self.assertRaises(PackageMapError):
            self._load("[project]\nname = 'x'\n")

    def test_an_unknown_region_is_refused(self) -> None:
        with self.assertRaises(PackageMapError):
            self._load('[tool.py-gzkit.hexagon]\npackage = "app"\nadapters = ["app.x"]\n')

    def test_a_package_in_two_regions_is_refused(self) -> None:
        table = '[tool.py-gzkit.hexagon]\npackage = "app"\nkernel = ["app.k"]\ndomain = ["app.k"]\n'
        with self.assertRaises(PackageMapError):
            self._load(table)

    def test_a_part_outside_the_package_is_refused(self) -> None:
        with self.assertRaises(PackageMapError):
            self._load('[tool.py-gzkit.hexagon]\npackage = "app"\nkernel = ["other.k"]\n')

    def test_every_region_is_a_known_key(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "pyproject.toml"
            path.write_text(PYPROJECT, encoding="utf-8")
            package_map = load_package_map(path)
        self.assertEqual(set(package_map.parts.values()), set(Region))

    def test_a_map_with_no_package_is_refused(self) -> None:
        with self.assertRaises(PackageMapError):
            self._load('[tool.py-gzkit.hexagon]\nsource-root = "src"\n')

    def test_a_part_that_is_not_a_name_is_refused(self) -> None:
        with self.assertRaises(PackageMapError):
            self._load('[tool.py-gzkit.hexagon]\npackage = "app"\nkernel = [1]\n')

    def test_a_region_that_is_not_a_list_is_refused(self) -> None:
        with self.assertRaises(PackageMapError):
            self._load('[tool.py-gzkit.hexagon]\npackage = "app"\nkernel = "app.k"\n')


class ThePackageMustBeOnDisk(unittest.TestCase):
    """A map naming a package the source root does not hold is refused, never a clean pass."""

    def _check(self, table: str, files: dict[str, str]) -> list[str]:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(table, encoding="utf-8")
            for rel, body in files.items():
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding="utf-8")
            return [f.key for f in check(load_package_map(root / "pyproject.toml"), root)]

    def test_a_misspelt_package_is_refused(self) -> None:
        table = '[tool.py-gzkit.hexagon]\npackage = "acmee"\nsource-root = "src"\n'
        with self.assertRaises(PackageMapError):
            self._check(table, {"src/acme/__init__.py": "import networkx\n"})

    def test_a_wrong_source_root_is_refused(self) -> None:
        table = '[tool.py-gzkit.hexagon]\npackage = "acme"\nsource-root = "lib"\n'
        with self.assertRaises(PackageMapError):
            self._check(table, {"src/acme/__init__.py": ""})

    def test_a_dotted_package_is_read_from_its_nested_directory(self) -> None:
        table = (
            '[tool.py-gzkit.hexagon]\npackage = "acme.app"\nsource-root = "src"\n'
            'domain = ["acme.app.domain"]\ndriving-adapters = ["acme.app.cli"]\n'
        )
        files = {
            "src/acme/app/__init__.py": "",
            "src/acme/app/domain/__init__.py": "from acme.app.cli import main\n",
            "src/acme/app/cli/__init__.py": "",
        }
        self.assertEqual(self._check(table, files), ["import acme.app.domain -> acme.app.cli"])


class TheBaselineOnlyShrinks(unittest.TestCase):
    def test_compare_splits_new_from_repaired(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
            for rel, body in {**KERNEL, "app/legacy.py": ""}.items():
                target = root / "src" / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding="utf-8")
            findings = check(load_package_map(root / "pyproject.toml"), root)
        new, repaired = compare(findings, frozenset({"unmapped app.gone"}))
        self.assertEqual(new, ["unmapped app.legacy"])
        self.assertEqual(repaired, ["unmapped app.gone"])
        self.assertEqual({f.rule for f in findings}, {Rule.UNMAPPED})


if __name__ == "__main__":
    unittest.main()
