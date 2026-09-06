"""Policy tests: architectural import boundary enforcement via AST scanning.

These tests NEVER import or execute application code. They parse source files
with the `ast` module to verify hexagonal architecture boundaries are respected.
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "gzkit"

CORE_DIR = SRC_ROOT / "core"

# Modules that core/ must never import from. `gzkit.adapters` is retained as a
# forward-fence: the ports/adapters facade was retired (2026-07-06 ruling — see
# docs/governance/hexagonal-architecture.md), but the deps-behind-adapters
# directive keeps `adapters` a live architectural concept, so core purity from
# any future adapter package still holds.
CORE_FORBIDDEN_PREFIXES = (
    "gzkit.cli",
    "gzkit.adapters",
    "gzkit.commands",
)
#: Top-level modules core/ may import despite not being stdlib.
#:
#: `.gzkit/rules/hexagonal-architecture.md` rule 1 says core imports "stdlib +
#: Pydantic ONLY", and rule 2 names Pydantic the single ratified exception. That
#: is an ALLOWLIST, and it cannot be expressed as a denylist: the previous
#: `("rich", "argparse")` pair enforced "not these two", so every third-party
#: dependency the project has added since — networkx, radon, lizard, cohesion —
#: was free to enter core, and a dependency added tomorrow would be too. A check
#: whose subject is narrower than its name is the validator-side arm of the
#: doctrine-declared-without-mechanism family (GHI #537).
CORE_ALLOWED_THIRD_PARTY = frozenset({"pydantic"})

#: Stdlib modules core/ must still refuse. `argparse` is stdlib, so the
#: stdlib test admits it — but it is the CLI layer's technology, and rule 4
#: ("never name the technology in the core") fences it regardless of who ships it.
CORE_FORBIDDEN_STDLIB = frozenset({"argparse"})

COMMANDS_DIR = SRC_ROOT / "commands"

# Env vars permitted anywhere in commands/
COMMAND_ENV_ALLOWLIST: frozenset[str] = frozenset({"NO_COLOR", "FORCE_COLOR"})

# Per-file exceptions for env-var access beyond COMMAND_ENV_ALLOWLIST.
# Each entry maps filename -> frozenset of additionally-allowed var names,
# with a comment explaining the rationale.
COMMAND_ENV_EXCEPTIONS: dict[str, frozenset[str]] = {
    # sync.py reads SKIP to detect CI/hook bypass tokens, mirroring the same
    # guard used in git_sync; this is a deliberate policy-enforcement read,
    # not a configuration lookup that should move to core.
    "sync.py": frozenset({"SKIP"}),
    # obpi_lock_cmd.py reads agent identity env vars for lock ownership.
    "obpi_lock_cmd.py": frozenset({"CLAUDE_CODE", "CODEX_SANDBOX", "CLAUDE_SESSION_ID"}),
    # gz content edit (OBPI-0.0.34-04) resolves the operator's preferred
    # editor via $VISUAL / $EDITOR. This is the standard POSIX editor-
    # invocation contract; routing it through core/ports would be a
    # premature abstraction over a stable shell convention.
    "edit.py": frozenset({"EDITOR", "VISUAL"}),
    # validate_cmd.py reads CI to decide whether the session-green gate's
    # delivery arm binds: a developer worktree must have the pre-push hook
    # installed, a fresh CI checkout legitimately has none (CI *is* the gate
    # there and does not push). Like SKIP above, this is a policy-enforcement
    # read of the execution context, not a configuration lookup — there is no
    # value for core to supply, only a fact about where the process is running
    # (GHI #715).
    "validate_cmd.py": frozenset({"CI"}),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_py_files(directory: Path) -> list[Path]:
    """Return all .py files under *directory* (recursive)."""
    return sorted(directory.rglob("*.py"))


def _parse_file(path: Path) -> ast.Module:
    """Parse a Python source file and return its AST."""
    source = path.read_text(encoding="utf-8")
    return ast.parse(source, filename=str(path))


def _collect_imports(tree: ast.Module) -> list[tuple[str, str]]:
    """Return (import_kind, module_name) pairs for all import statements.

    import_kind is "import" for `import X` and "from" for `from X import Y`.
    module_name is the top-level dotted name being imported.
    """
    imports: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(("import", alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(("from", module))
    return imports


def _top_level_module(dotted_name: str) -> str:
    """Return the first component of a dotted module name."""
    return dotted_name.split(".")[0]


def _is_os_attr(node: ast.expr, attr: str) -> bool:
    """Return True if *node* is `os.<attr>` (Attribute access on bare `os` name)."""
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "os"
        and node.attr == attr
    )


def _string_value(node: ast.expr) -> str | None:
    """Return the string value of a Constant string node, or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _collect_command_env_violations(
    tree: ast.Module, allowlist: frozenset[str]
) -> list[tuple[int, str, str]]:
    """Walk *tree* and return env-var violations outside *allowlist*.

    Returns a list of (line_number, access_form, var_name) triples for each
    usage of an env var not in *allowlist*.

    Detected patterns:
    - ``os.getenv("VAR")``
    - ``os.environ.get("VAR")``
    - ``os.environ["VAR"]``
    """
    violations: list[tuple[int, str, str]] = []

    for node in ast.walk(tree):
        # os.getenv("VAR", ...) — ast.Call
        if isinstance(node, ast.Call) and _is_os_attr(node.func, "getenv"):
            if node.args:
                var_name = _string_value(node.args[0])
                if var_name is not None and var_name not in allowlist:
                    violations.append((node.lineno, "os.getenv", var_name))

        # os.environ.get("VAR", ...) — ast.Call on a chained Attribute
        elif isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "get"
                and _is_os_attr(func.value, "environ")
                and node.args
            ):
                var_name = _string_value(node.args[0])
                if var_name is not None and var_name not in allowlist:
                    violations.append((node.lineno, "os.environ.get", var_name))

        # os.environ["VAR"] — ast.Subscript
        elif isinstance(node, ast.Subscript) and _is_os_attr(node.value, "environ"):
            var_name = _string_value(node.slice)
            if var_name is not None and var_name not in allowlist:
                violations.append((node.lineno, "os.environ[...]", var_name))

    return violations


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def _core_violations(path: Path) -> list[str]:
    """Return every core/ import-boundary violation in *path*.

    Extracted from the assertion so the predicate can be exercised against a
    synthetic module. A boundary check that is only ever run over a tree that
    already satisfies it cannot distinguish "enforces the rule" from "returns
    the empty list" -- and the denylist this replaced had been in exactly that
    state, admitting four third-party dependencies while passing every run.
    """
    tree = _parse_file(path)
    imports = _collect_imports(tree)
    violations: list[str] = []

    for _kind, module in imports:
        # Check forbidden gzkit sub-package prefixes
        for forbidden_prefix in CORE_FORBIDDEN_PREFIXES:
            if module == forbidden_prefix or module.startswith(forbidden_prefix + "."):
                violations.append(
                    f"{path.name}: imports '{module}' (forbidden prefix '{forbidden_prefix}')"
                )

        # Core purity, stated as the allowlist the rule actually declares:
        # stdlib + Pydantic + gzkit internals, and nothing else.
        top = _top_level_module(module)
        if top in CORE_FORBIDDEN_STDLIB:
            violations.append(f"{path.name}: imports '{module}' (forbidden top-level module)")
        elif not (
            top in sys.stdlib_module_names or top in CORE_ALLOWED_THIRD_PARTY or top == "gzkit"
        ):
            violations.append(
                f"{path.name}: imports '{module}' — core/ is stdlib + Pydantic ONLY "
                "(.gzkit/rules/hexagonal-architecture.md rules 1-2); put the dependency "
                "behind an adapter and take it as a parameter"
            )

    return violations


class CorePurityIsAnAllowlist(unittest.TestCase):
    """The core-purity check refuses any non-stdlib import, not a fixed pair.

    These exercise the predicate against synthetic modules because `core/` is
    clean: a test that only reads the real tree passes identically whether the
    check enforces the rule or returns nothing.
    """

    def _violations(self, source: str) -> list[str]:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.py"
            path.write_text(source, encoding="utf-8")
            return _core_violations(path)

    def test_every_declared_runtime_dependency_is_refused(self) -> None:
        """The four deps added after the denylist was written are now fenced.

        `networkx`, `radon`, `lizard` and `cohesion` all entered `pyproject.toml`
        while `CORE_FORBIDDEN_TOP_LEVEL` still read `("rich", "argparse")`, so
        each could have been imported into core without failing a single test.
        """
        for dep in ("networkx", "radon", "lizard", "cohesion", "jinja2", "structlog"):
            with self.subTest(dependency=dep):
                self.assertTrue(self._violations(f"import {dep}\n"))

    def test_a_dependency_nobody_has_added_yet_is_refused(self) -> None:
        """The allowlist binds by construction, so it needs no upkeep.

        This is the property a denylist cannot have: enforcement must not depend
        on someone remembering to add a name when a dependency lands.
        """
        self.assertTrue(self._violations("import some_future_dependency\n"))

    def test_stdlib_pydantic_and_gzkit_are_admitted(self) -> None:
        clean = "import enum\nimport re\nfrom typing import Any\nfrom pydantic import BaseModel\n"
        self.assertEqual(self._violations(clean), [])

    def test_argparse_stays_refused_although_it_is_stdlib(self) -> None:
        """Rule 4 fences the CLI's technology out of core regardless of shipper."""
        self.assertTrue(self._violations("import argparse\n"))

    def test_the_message_names_the_rule_and_the_recovery(self) -> None:
        """Three-part recovery prose (`.gzkit/rules/guardrail-feedback-prose.md`)."""
        message = self._violations("import networkx\n")[0]
        self.assertIn("networkx", message)
        self.assertIn("hexagonal-architecture.md", message)
        self.assertIn("behind an adapter", message)


class TestCoreImportBoundaries(unittest.TestCase):
    """core/ imports stdlib + Pydantic only, and never the CLI/commands layers."""

    def _assert_file_clean(self, path: Path) -> None:
        violations = _core_violations(path)
        if violations:
            self.fail("core/ import boundary violations:\n" + "\n".join(violations))

    def test_core_files_exist(self) -> None:
        """Sanity check: core/ directory contains at least one .py file."""
        files = _collect_py_files(CORE_DIR)
        self.assertGreater(len(files), 0, f"No .py files found in {CORE_DIR}")

    def test_core_no_cli_imports(self) -> None:
        """core/ must not import from gzkit.cli."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertFalse(
                        module == "gzkit.cli" or module.startswith("gzkit.cli."),
                        f"{path.name}: forbidden import from gzkit.cli — '{module}'",
                    )

    def test_core_no_adapters_imports(self) -> None:
        """core/ must not import from gzkit.adapters."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertFalse(
                        module == "gzkit.adapters" or module.startswith("gzkit.adapters."),
                        f"{path.name}: forbidden import from gzkit.adapters — '{module}'",
                    )

    def test_core_no_commands_imports(self) -> None:
        """core/ must not import from gzkit.commands."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertFalse(
                        module == "gzkit.commands" or module.startswith("gzkit.commands."),
                        f"{path.name}: forbidden import from gzkit.commands — '{module}'",
                    )

    def test_core_no_rich_imports(self) -> None:
        """core/ must not import from rich (UI layer)."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertNotEqual(
                        _top_level_module(module),
                        "rich",
                        f"{path.name}: forbidden import from rich — '{module}'",
                    )

    def test_core_no_argparse_imports(self) -> None:
        """core/ must not import argparse (CLI layer)."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertNotEqual(
                        _top_level_module(module),
                        "argparse",
                        f"{path.name}: forbidden import from argparse — '{module}'",
                    )

    def test_core_all_files_pass_boundary_check(self) -> None:
        """Aggregate: all core/ files pass the full boundary check in one sweep."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                self._assert_file_clean(path)


class TestCommandLayerSanity(unittest.TestCase):
    """commands/ presence sanity.

    The former "commands must not import gzkit.adapters" rule was retired
    (2026-07-06 injection-seam ruling): the command layer IS gzkit's
    configurator (Cockburn Fig 2.1), so it is precisely where driven adapters
    are instantiated — forbidding that import contradicts the blessed pattern.
    Core purity from any adapter package is still enforced by
    TestCoreImportBoundaries.
    """

    def test_commands_files_exist(self) -> None:
        """Sanity check: commands/ directory contains at least one .py file."""
        files = _collect_py_files(COMMANDS_DIR)
        self.assertGreater(len(files), 0, f"No .py files found in {COMMANDS_DIR}")


class TestCommandEnvUsage(unittest.TestCase):
    """Command handlers must not call os.getenv() outside a narrow allowlist.

    Only terminal-color env vars (NO_COLOR, FORCE_COLOR) are permitted in the
    commands layer.  Any additional env-var reads indicate configuration that
    should be routed through core services or explicit CLI flags instead.

    Known exceptions are listed in COMMAND_ENV_EXCEPTIONS with explanations.
    """

    def test_commands_no_unapproved_env_access(self) -> None:
        """Scan all files in src/gzkit/commands/ for unapproved env-var reads."""
        all_violations: list[str] = []

        for path in _collect_py_files(COMMANDS_DIR):
            # Per-file exceptions: {filename: frozenset of allowed extra var names}
            extra_allowed = COMMAND_ENV_EXCEPTIONS.get(path.name, frozenset())
            effective_allowlist = COMMAND_ENV_ALLOWLIST | extra_allowed

            with self.subTest(file=path.name):
                tree = _parse_file(path)
                violations = _collect_command_env_violations(tree, effective_allowlist)
                for lineno, form, var_name in violations:
                    rel = path.relative_to(COMMANDS_DIR.parent.parent)
                    all_violations.append(
                        f"{rel}:{lineno}: {form}({var_name!r}) — not in allowlist "
                        f"(allowlist for this file: {sorted(effective_allowlist)})"
                    )

        if all_violations:
            self.fail(
                "Unapproved env-var access in commands/ detected:\n" + "\n".join(all_violations)
            )


# ---------------------------------------------------------------------------
# Private-symbol cross-package imports (GHI #956)
# ---------------------------------------------------------------------------

#: Frozen baseline of every import of a private (single-underscore) name from a
#: module in a DIFFERENT package directory. Shrink-only: the test below asserts
#: set EQUALITY, so a new edge fails and a repaired edge must be pruned here.
#:
#: A leading underscore is the owning module's declaration that the symbol is
#: not part of its contract. Reached from another package, that contract is
#: enforced by nothing — ruff's `PLC2701` exempts same-package imports and fires
#: on 1 of 351 private-name imports in this tree, so enabling it would read
#: green over the rest (measured 2026-09-04, ruff 0.16.2). This roster is the
#: witness that does not exist otherwise.
#:
#: SAME-DIRECTORY imports are deliberately OUT OF SCOPE. 247 of them exist and
#: they are a different disposition: sibling files of one logically-split module
#: (`status.py` / `status_obpi.py` / `status_render.py`), where the underscore
#: means "not outside this cluster" and the cluster IS the directory. Folding
#: them in would inflate the roster fivefold and route a refactor at code that
#: is working as designed.
#:
#: This roster is pass 1 of an operator-ruled two-pass repair (GHI #956,
#: 2026-09-04: "roster now, repair after"). It stops the class GROWING today;
#: it does not bless the 100 entries. Pass 2 adjudicates each edge and either
#: promotes the symbol to a public name in a home both callers can reach — as
#: GHI #945 did for the advisory-lock primitive — or relocates it. Every entry
#: removed here is one edge repaired.
#: Grouped by IMPORTER so the roster reads as "what does this file reach for",
#: which is the question a repair pass asks. Paths are relative to src/gzkit/
#: and owner modules drop their gzkit. prefix; both are constant noise, and
#: dropping them is what keeps every entry inside the line budget.
PRIVATE_CROSS_PACKAGE_IMPORT_BASELINE: dict[str, tuple[str, ...]] = {
    "airlock/enter.py": ("governance.trust_audits._qc_negative_controls._KNOWN_QC_CLAIM_IDS",),
    "chores/__init__.py": ("commands.common._confirm",),
    "chores/control-surface-validator-reachability/check_reachability.py": (
        "cli.main._build_parser",
    ),
    "commands/ceremony_data.py": ("cli.main._build_parser",),
    "commands/cli_audit.py": (
        "cli.main._build_parser",
        "rules._is_framework_tree",
    ),
    "commands/covers.py": (
        "traceability._obpi_sort_key",
        "traceability._rollup",
        "traceability._semver_sort_key",
    ),
    "commands/init_cmd.py": (
        "chores._classify_chore_file",
        "chores._iter_canonical_chore_slugs",
        "personas._iter_canonical_persona_slugs",
        "rules._iter_canonical_rule_slugs",
        "skills._iter_canonical_skill_slugs",
        "skills._parse_frontmatter",
        "templates._iter_canonical_template_slugs",
    ),
    "commands/obpi_complete.py": (
        "pipeline_runtime._extract_brief_allowlist",
        "pipeline_runtime._find_drifted_path",
    ),
    "commands/obpi_precomplete.py": (
        "governance.trust_audits.adversarial_validation._STEP_4B_RE",
        "governance.trust_audits.briefs._ACCEPTANCE_SECTION",
        "governance.trust_audits.briefs._BRIEF_EVIDENCE_H3_HEADINGS",
        "governance.trust_audits.briefs._LANE_IN_FRONTMATTER",
        "governance.trust_audits.briefs._REQ_ID_IN_BRIEF",
        "governance.trust_audits.briefs._load_behave_coverage_waivers",
        "governance.trust_audits.briefs._scan_one_brief_headings",
    ),
    "commands/register.py": ("ledger._extract_bare_adr_semver",),
    "commands/sync.py": (
        "git_sync._compute_git_sync_state",
        "git_sync._git_status_lines",
        "git_sync._head_is_merge_commit",
        "git_sync._skip_disables_xenon",
        "git_sync._skip_tokens",
    ),
    "commands/upgrade.py": (
        "personas._classify_persona_file",
        "rules._classify_rule_file",
        "skills._classify_skill_file",
        "templates._classify_template_file",
    ),
    "commands/validate_frontmatter.py": (
        "governance.frontmatter_coherence._is_pool_artifact",
        "ledger_semantics._derive_obpi_runtime_state",
    ),
    "commands/validate_inventory_scopes.py": (
        "governance.trust_audits.exemption_controls._registry_declarations",
    ),
    "commands/validate_req_kind.py": (
        "req_kind_fence._boundary_invariants_section",
        "req_kind_fence._fence_obpi_anchored",
        "req_kind_fence._is_enforcement_asserting",
    ),
    "commands/validate_sensitivity.py": (
        "governance.trust_audits.sensitivity._SENSITIVITY_REGISTRY_REL",
        "governance.trust_audits.sensitivity._extract_sensitivity_allowed_paths",
        "governance.trust_audits.sensitivity._iter_sensitivity_briefs",
        "governance.trust_audits.sensitivity._load_floor_grandfather",
        "governance.trust_audits.sensitivity._load_sensitivity_registry",
        "governance.trust_audits.taxonomy._parse_adr_frontmatter",
    ),
    "enforcement.py": (
        "airlock.enter._ensure_airlock_claims_registered",
        "governance.trust_audits._qc_negative_controls._KNOWN_QC_CLAIM_IDS",
        "mx.invariants._ensure_gate5_claims_registered",
        "mx.proxy_reality._ensure_grader_gaming_registered",
    ),
    "foundation/sunset_migrate.py": (
        "commands.adr_demote._apply_demote",
        "commands.adr_demote._build_demote_plan",
        "commands.adr_demote._derive_pool_slug_from_adr_id",
    ),
    "governance/brief_reconcile.py": ("governance.trust_audits.cli._known_cli_verbs",),
    "governance/frontmatter_coherence.py": ("commands.common._is_pool_adr_id",),
    "governance/obpi_park_backfill.py": ("governance.trust_audits.taxonomy._live_adr_ids",),
    "governance/trust_audits/_qc_nc_entrypoints.py": (
        "commands.chores._resolve_chore_dir",
        "commands.validate_briefs._validate_interviews",
        "commands.validate_cmd._collect_errors",
        "commands.validate_req_kind._validate_req_kind_discipline",
        "commands.validate_task_envelope._validate_task_envelope_coherence",
    ),
    "governance/trust_audits/cli.py": ("cli.main._build_parser",),
    "governance/trust_audits/exemption_controls.py": (
        "enforcement._ensure_production_claims_registered",
    ),
    "governance/trust_audits/qc_binding.py": ("enforcement._run_single_claim",),
    "governance/trust_audits/release.py": ("enforcement._ensure_production_claims_registered",),
    "governance/trust_audits/vendor_manifest.py": (
        "content.vendors._FALLBACK_ROUTES",
        "content.vendors._FALLBACK_SURFACE_CONTENT_TYPES",
    ),
    "handoff_resume_gate.py": (
        "airlock.enter._AIRLOCK_CLAIM_IDS",
        "governance.trust_audits._qc_negative_controls._KNOWN_QC_CLAIM_IDS",
    ),
    "hooks/claude.py": (
        "hooks.scripts.ghi._ghi_triage_chat_silence_script",
        "hooks.scripts.mx._mx_awareness_script",
        "hooks.scripts.pipeline._pipeline_completion_reminder_script",
        "hooks.scripts.pipeline._plan_audit_gate_script",
        "hooks.scripts.pipeline._session_staleness_check_script",
        "hooks.scripts.quality._post_edit_ruff_script",
        "hooks.scripts.quality._stop_turn_feedback_script",
        "hooks.scripts.quality._verifier_pipe_gate_script",
        "hooks.scripts.routing._instruction_router_script",
        "hooks.scripts.routing._pipeline_gate_script",
        "hooks.scripts.routing._pipeline_router_script",
        "hooks.scripts.session_exit._session_exit_bookmark_script",
        "hooks.scripts.session_exit._session_start_advisement_script",
        "hooks.scripts.validation._control_surface_sync_script",
        "hooks.scripts.validation._ledger_writer_script",
        "hooks.scripts.validation._obpi_completion_validator_script",
    ),
    "mx/invariants.py": (
        "commands.adr_audit._requires_human_obpi_attestation",
        "commands.adr_audit._validate_obpi_human_attestation_fields",
        "governance.trust_audits._qc_negative_controls._KNOWN_QC_CLAIM_IDS",
    ),
    "mx/proxy_reality.py": ("governance.trust_audits._qc_negative_controls._KNOWN_QC_CLAIM_IDS",),
    "qc_binding.py": ("commands.quality._build_check_steps",),
    "quality.py": ("commands.chores._resolve_chore_dir",),
    "red_witness.py": ("commands.quality._test_name_from_record",),
    "req_kind_support.py": (
        "commands.validate_cmd._default_scope_runners",
        "commands.validate_cmd._explicit_scope_runners",
    ),
    "verb_references.py": ("cli.main._get_parser",),
    "verifier_pipe_gate.py": (
        "airlock.enter._AIRLOCK_CLAIM_IDS",
        "governance.trust_audits._qc_negative_controls._KNOWN_QC_CLAIM_IDS",
    ),
}


def _baseline_edges() -> set[str]:
    """Flatten the importer-keyed baseline into comparable edge strings."""
    return {
        f"{importer} -> {symbol}"
        for importer, symbols in PRIVATE_CROSS_PACKAGE_IMPORT_BASELINE.items()
        for symbol in symbols
    }


def _collect_private_cross_package_imports(src_root: Path) -> set[str]:
    """Return every `<importer> -> <owner>.<_symbol>` edge under *src_root*.

    An edge is counted when a module imports a single-underscore name from a
    `gzkit.` module whose file sits in a DIFFERENT directory. Dunder names are
    not private in this sense and are excluded. Relative imports fall out for
    free: `from .status import _x` records `node.module == "status"`, which the
    absolute-prefix test already refuses -- an explicit `node.level` guard was
    written here first and removed as dead, since no mutation of it could
    change a result.

    Both sides are reduced to REPO-RELATIVE paths before the directory
    comparison. Comparing an absolute importer path against a relative owner
    path never matches, which silently admits all 247 same-directory imports
    and makes the roster measure a class four times larger than the one it
    names -- observed while authoring this, caught by the baseline count.
    """
    edges: set[str] = set()
    for path in _collect_py_files(src_root):
        try:
            tree = _parse_file(path)
        except SyntaxError:  # pragma: no cover - a syntax error is another test's finding
            continue
        rel = path.relative_to(src_root)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if not node.module or not node.module.startswith("gzkit."):
                continue
            owner = Path(node.module[len("gzkit.") :].replace(".", "/"))
            if owner.parent == rel.parent:
                continue
            for alias in node.names:
                if alias.name.startswith("_") and not alias.name.startswith("__"):
                    edges.add(
                        f"{rel.as_posix()} -> {owner.as_posix().replace('/', '.')}.{alias.name}"
                    )
    return edges


class TestPrivateCrossPackageImportCollector(unittest.TestCase):
    """The collector's semantics, pinned on a synthetic tree.

    The ratchet tests below assert against the real repository, so a guard
    whose triggering input does not currently exist there is asserted by
    nothing. Measured while authoring: the tree contains ZERO dunder
    cross-module imports, so removing the dunder exclusion changed no result
    and the real-tree tests stayed green. These fixtures supply the inputs the
    repository happens not to have.
    """

    def _collect(self, files: dict[str, str]) -> set[str]:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, body in files.items():
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding="utf-8")
            return _collect_private_cross_package_imports(root / "src" / "gzkit")

    def test_a_reach_into_another_package_is_counted(self) -> None:
        """The GHI #945 shape: a private name taken from a different directory."""
        edges = self._collect(
            {"src/gzkit/content/ownership.py": "from gzkit.store.corpus import _lock\n"}
        )
        self.assertEqual(edges, {"content/ownership.py -> store.corpus._lock"})

    def test_a_sibling_in_the_same_directory_is_not_counted(self) -> None:
        """Scope. A split module's siblings are a different disposition.

        247 of these exist. Counting them would inflate the roster fivefold and
        point a refactor at code that is working as designed, where the
        underscore means "not outside this cluster" and the cluster IS the
        directory.
        """
        edges = self._collect(
            {"src/gzkit/commands/status_render.py": "from gzkit.commands.status import _inspect\n"}
        )
        self.assertEqual(edges, set())

    def test_a_dunder_is_not_a_private_reach(self) -> None:
        """`__all__` and friends are not a module's private contract.

        No instance exists in the tree today, which is exactly why this is
        asserted here rather than left to the real-tree ratchet.
        """
        edges = self._collect(
            {"src/gzkit/commands/thing.py": "from gzkit.core.model import __all__\n"}
        )
        self.assertEqual(edges, set())

    def test_a_public_name_is_not_counted(self) -> None:
        """Only the underscore-marked contract is the subject."""
        edges = self._collect(
            {"src/gzkit/commands/thing.py": "from gzkit.core.model import Corpus\n"}
        )
        self.assertEqual(edges, set())

    def test_a_relative_import_is_not_counted(self) -> None:
        """A relative import cannot cross a package directory as defined here."""
        edges = self._collect({"src/gzkit/commands/thing.py": "from .status import _inspect\n"})
        self.assertEqual(edges, set())

    def test_a_non_gzkit_private_import_is_not_counted(self) -> None:
        """Third-party internals are another project's contract, not gzkit's."""
        edges = self._collect(
            {"src/gzkit/commands/thing.py": "from pydantic._internal import _fields\n"}
        )
        self.assertEqual(edges, set())


class TestPrivateCrossPackageImportRatchet(unittest.TestCase):
    """The private-symbol reach across packages may shrink, never grow.

    GHI #945 was one edge of this class: `content/ownership.py` reached
    `corpus_store._exclusive_store_lock`, and nothing would have signalled
    breakage if a later refactor had renamed or inlined it. Fixing that one edge
    left the class open by construction, which is what this ratchet closes.
    """

    def _current(self) -> set[str]:
        return _collect_private_cross_package_imports(SRC_ROOT)

    def test_no_new_private_cross_package_import(self) -> None:
        """A reach not in the baseline is a new edge and must be justified."""
        added = sorted(self._current() - _baseline_edges())
        self.assertEqual(
            added,
            [],
            "New import of a private symbol from another package:\n  "
            + "\n  ".join(added)
            + "\n\nThe leading underscore is the owning module's statement that the "
            "symbol is not part of its contract, and nothing but this test enforces "
            "it. Promote the symbol to a public name in a home both callers can "
            "reach (see `gzkit.file_lock`, GHI #945), or import a public entry "
            "point instead. Adding the edge to the baseline is the wrong fix: the "
            "roster is shrink-only.",
        )

    def test_baseline_carries_no_repaired_edge(self) -> None:
        """A repaired edge must be pruned, so the roster measures real debt.

        Without this, the baseline would slowly become fiction — a roster of
        edges that no longer exist reads as debt that was never paid, and the
        count stops meaning anything.
        """
        stale = sorted(_baseline_edges() - self._current())
        self.assertEqual(
            stale,
            [],
            "These baseline entries no longer exist and must be removed from "
            "PRIVATE_CROSS_PACKAGE_IMPORT_BASELINE:\n  " + "\n  ".join(stale),
        )


class TestPolicyTestIsolation(unittest.TestCase):
    """Policy tests themselves must not import from src/gzkit/."""

    def test_this_module_imports_no_gzkit(self) -> None:
        """This test file must not import any gzkit application module."""
        this_file = Path(__file__)
        tree = _parse_file(this_file)
        for _kind, module in _collect_imports(tree):
            self.assertFalse(
                module == "gzkit" or module.startswith("gzkit."),
                f"Policy test file imports gzkit module: '{module}'",
            )


if __name__ == "__main__":
    unittest.main()
