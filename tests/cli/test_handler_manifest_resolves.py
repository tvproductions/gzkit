"""Resolution guard for the lazy CLI handler manifests (GHI #617).

Every ``gz`` verb dispatches through a string-keyed lazy resolver: ``_lazy(name)``
(the command-group parsers, and the collapsed ``parser_handler_manifest``) and
``_arb(name)`` (``parser_arb``) resolve a handler via
``getattr(import_module(manifest[name]), name)``. The coupling is a string plus a
``getattr`` — invisible to ``ty`` and to the unittest suite. A handler rename that
misses its manifest key, or a ``_lazy("typo")`` call-site, passes lint, type-check,
and the full suite green and fails only at the first runtime invocation of that one
verb: correct by author discipline, not by construction. That is the exact "vibing
surface held correct by convention" the doctrine names (AGENTS.md § MAKE LLM
STOCHASTIC VIBES INERT) and the failure class GHI #617 exists to fence.

This guard pins both directions of the coupling:

  (A) every manifest entry resolves to a real callable (no DUD / renamed handler);
  (B) every ``_lazy(...)`` / ``_arb(...)`` call-site names a known manifest key
      (no typo'd call-site, no dead manifest entry).

It is deliberately introspection-based (import the manifests, AST-scan the
call-sites) rather than a brittle golden count — the assertion derives from the
resolution contract, not from today's entry total, so it stays meaningful as
verbs are added or removed.

It is also the in-scope-now fence that must stay GREEN across the GHI #617 collapse
of the three byte-identical ``_lazy`` resolvers into one shared
``parser_handler_manifest``: any collapse that drops or mis-maps an entry turns one
of these two assertions red. Sibling of the #618 validate-dispatch fences
(``test_validate_dispatch_consistency`` / ``test_validate_registry_parity``).
"""

from __future__ import annotations

import ast
import importlib
import unittest
from importlib import import_module
from pathlib import Path

_CLI_DIR = Path("src/gzkit/cli")

# The two single-underscore lazy resolvers used in the parser modules. Both take
# a single string-constant handler name and resolve it through a string->module
# manifest. parser_arb's `_arb` hardcodes the module but its manifest still maps
# every handler name, so it obeys the same key->callable contract.
_RESOLVER_NAMES = frozenset({"_lazy", "_arb"})


def _parser_paths() -> list[Path]:
    """Every ``src/gzkit/cli/parser_*.py`` source file (scanner-glob parity)."""
    return sorted(_CLI_DIR.glob("parser_*.py"))


def _collect_manifests() -> dict[str, str]:
    """Merge every parser module's ``_LAZY_HANDLERS`` into one name->module map.

    Discovers the manifest wherever it lives, so the assertion is invariant to
    the #617 collapse (three per-parser dicts before; one shared dict after).
    """
    merged: dict[str, str] = {}
    for path in _parser_paths():
        module = importlib.import_module(f"gzkit.cli.{path.stem}")
        manifest = getattr(module, "_LAZY_HANDLERS", None)
        if isinstance(manifest, dict):
            merged.update(manifest)
    return merged


def _collect_call_sites() -> set[str]:
    """AST-scan parser sources for ``_lazy("x")`` / ``_arb("x")`` string args."""
    names: set[str] = set()
    for path in _parser_paths():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in _RESOLVER_NAMES
                and len(node.args) == 1
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                names.add(node.args[0].value)
    return names


class TestHandlerManifestResolves(unittest.TestCase):
    """Every lazy CLI handler reference resolves to a real callable (GHI #617)."""

    def test_every_manifest_entry_resolves_to_a_callable(self) -> None:
        # Direction A: a manifest key whose handler was renamed or removed is a
        # DUD — `gz <verb>` would AttributeError only at first invocation.
        manifest = _collect_manifests()
        self.assertTrue(manifest, "no _LAZY_HANDLERS manifests discovered under cli/parser_*.py")
        unresolved: list[str] = []
        for name, module_path in sorted(manifest.items()):
            try:
                impl = getattr(import_module(module_path), name)
            except (ImportError, AttributeError):
                unresolved.append(f"{name} -> {module_path}")
                continue
            if not callable(impl):
                unresolved.append(f"{name} -> {module_path} (resolved, not callable)")
        self.assertEqual(
            unresolved,
            [],
            "these manifest entries do not resolve to a callable handler — the "
            f"verb dispatches to nothing at runtime: {unresolved}",
        )

    def test_every_call_site_names_a_known_manifest_key(self) -> None:
        # Direction B: a `_lazy("typo")` call-site (or a dead manifest entry) has
        # no key -> KeyError only at first invocation of that one verb.
        manifest = _collect_manifests()
        call_sites = _collect_call_sites()
        self.assertTrue(call_sites, "no _lazy/_arb call-sites discovered under cli/parser_*.py")
        unknown = sorted(name for name in call_sites if name not in manifest)
        self.assertEqual(
            unknown,
            [],
            "these _lazy/_arb call-sites name no manifest key (call-site typo or "
            f"dead entry) — the verb raises KeyError at runtime: {unknown}",
        )


if __name__ == "__main__":
    unittest.main()
