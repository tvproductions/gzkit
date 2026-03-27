"""Tests for port Protocol definitions.

Verifies that:
- All four Protocols are importable from gzkit.ports
- Protocols use typing.Protocol (structural subtyping)
- Protocol methods have correct signatures
- ports/ imports only typing and stdlib
"""

import ast
import inspect
import unittest
from pathlib import Path
from typing import Protocol

from gzkit.traceability import covers


class TestProtocolImports(unittest.TestCase):
    """Verify all four Protocols are importable from gzkit.ports."""

    @covers("REQ-0.0.3-01-01")
    def test_filestore_importable(self) -> None:
        from gzkit.ports import FileStore

        self.assertTrue(issubclass(FileStore, Protocol))

    @covers("REQ-0.0.3-01-02")
    def test_processrunner_importable(self) -> None:
        from gzkit.ports import ProcessRunner

        self.assertTrue(issubclass(ProcessRunner, Protocol))

    @covers("REQ-0.0.3-01-03")
    def test_ledgerstore_importable(self) -> None:
        from gzkit.ports import LedgerStore

        self.assertTrue(issubclass(LedgerStore, Protocol))

    @covers("REQ-0.0.3-01-04")
    def test_configstore_importable(self) -> None:
        from gzkit.ports import ConfigStore

        self.assertTrue(issubclass(ConfigStore, Protocol))


class TestFileStoreProtocol(unittest.TestCase):
    """Verify FileStore Protocol signature matches ADR spec."""

    def setUp(self) -> None:
        from gzkit.ports import FileStore

        self.protocol = FileStore

    @covers("REQ-0.0.3-01-01")
    def test_has_read_text(self) -> None:
        sig = inspect.signature(self.protocol.read_text)
        params = list(sig.parameters.keys())
        self.assertIn("path", params)
        self.assertEqual(sig.return_annotation, str)

    @covers("REQ-0.0.3-01-01")
    def test_has_write_text(self) -> None:
        sig = inspect.signature(self.protocol.write_text)
        params = list(sig.parameters.keys())
        self.assertIn("path", params)
        self.assertIn("content", params)

    @covers("REQ-0.0.3-01-01")
    def test_has_exists(self) -> None:
        sig = inspect.signature(self.protocol.exists)
        params = list(sig.parameters.keys())
        self.assertIn("path", params)
        self.assertEqual(sig.return_annotation, bool)

    @covers("REQ-0.0.3-01-01")
    def test_has_iterdir(self) -> None:
        sig = inspect.signature(self.protocol.iterdir)
        params = list(sig.parameters.keys())
        self.assertIn("path", params)


class TestProcessRunnerProtocol(unittest.TestCase):
    """Verify ProcessRunner Protocol signature matches ADR spec."""

    def setUp(self) -> None:
        from gzkit.ports import ProcessRunner

        self.protocol = ProcessRunner

    @covers("REQ-0.0.3-01-02")
    def test_has_run(self) -> None:
        sig = inspect.signature(self.protocol.run)
        params = list(sig.parameters.keys())
        self.assertIn("cmd", params)
        self.assertIn("cwd", params)


class TestLedgerStoreProtocol(unittest.TestCase):
    """Verify LedgerStore Protocol signature matches ADR spec."""

    def setUp(self) -> None:
        from gzkit.ports import LedgerStore

        self.protocol = LedgerStore

    @covers("REQ-0.0.3-01-03")
    def test_has_append(self) -> None:
        sig = inspect.signature(self.protocol.append)
        params = list(sig.parameters.keys())
        self.assertIn("event", params)

    @covers("REQ-0.0.3-01-03")
    def test_has_read_all(self) -> None:
        sig = inspect.signature(self.protocol.read_all)
        self.assertEqual(sig.return_annotation, list[dict])


class TestConfigStoreProtocol(unittest.TestCase):
    """Verify ConfigStore Protocol signature matches ADR spec."""

    def setUp(self) -> None:
        from gzkit.ports import ConfigStore

        self.protocol = ConfigStore

    @covers("REQ-0.0.3-01-04")
    def test_has_load(self) -> None:
        sig = inspect.signature(self.protocol.load)
        self.assertEqual(sig.return_annotation, dict)

    @covers("REQ-0.0.3-01-04")
    def test_has_save(self) -> None:
        sig = inspect.signature(self.protocol.save)
        params = list(sig.parameters.keys())
        self.assertIn("data", params)


class TestPortsBoundaryConstraints(unittest.TestCase):
    """Verify ports/ imports only typing and stdlib."""

    @covers("REQ-0.0.3-01-08")
    def test_ports_interfaces_imports_only_stdlib(self) -> None:
        interfaces_path = Path("src/gzkit/ports/interfaces.py")
        self.assertTrue(interfaces_path.exists(), "interfaces.py must exist")
        source = interfaces_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        allowed_modules = {"typing", "pathlib", "__future__"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    self.assertIn(
                        root,
                        allowed_modules,
                        f"ports/interfaces.py imports forbidden module: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                self.assertIn(
                    root,
                    allowed_modules,
                    f"ports/interfaces.py imports forbidden module: {node.module}",
                )

    @covers("REQ-0.0.3-01-05")
    def test_ports_init_imports_only_from_ports(self) -> None:
        init_path = Path("src/gzkit/ports/__init__.py")
        self.assertTrue(init_path.exists(), "__init__.py must exist")
        source = init_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                self.assertTrue(
                    node.module.startswith("gzkit.ports"),
                    f"ports/__init__.py imports from outside ports: {node.module}",
                )


class TestSkeletonDirectories(unittest.TestCase):
    """Verify three-layer directory structure exists."""

    @covers("REQ-0.0.3-01-06")
    def test_core_init_exists(self) -> None:
        self.assertTrue(Path("src/gzkit/core/__init__.py").exists())

    @covers("REQ-0.0.3-01-07")
    def test_adapters_init_exists(self) -> None:
        self.assertTrue(Path("src/gzkit/adapters/__init__.py").exists())

    @covers("REQ-0.0.3-01-10")
    def test_ports_init_exists(self) -> None:
        self.assertTrue(Path("src/gzkit/ports/__init__.py").exists())

    @covers("REQ-0.0.3-01-10")
    def test_ports_interfaces_exists(self) -> None:
        self.assertTrue(Path("src/gzkit/ports/interfaces.py").exists())


if __name__ == "__main__":
    unittest.main()
