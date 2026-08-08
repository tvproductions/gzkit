"""Writer-coverage audit for OBPI-brief ``status:`` writes (GHI #669).

``ADR-0.31.0`` § Decision item 4 declares *"A single invariant monitor. Every
read or write to the artifact graph passes through one monitor."* GHI #668
routed every writer that existed at the time through that monitor and an
independent audit confirmed it COHERENT — but the routing was enforced by
CONVENTION. Nothing discovered writers, so a future one could bypass the
monitor and silently reintroduce the GHI #348 terminal-clobber class.

This audit closes that. It walks ``src/gzkit/**`` for calls that reach a
frontmatter ``status:`` key and requires each to either consult the monitor or
carry a REGISTERED reason. The register is the deliverable as much as the
refusal: a writer that legitimately does not consult the monitor still has to
say why and at what scope, which is the *"record the objective and scope"*
discipline GHI #727 named after two validators enforced one rule with
different reach and nothing made the disagreement visible.

Engine note: AST, deliberately. The regex enforcer in GHI #607 broke an
adopter's build for two months because a substring match cannot see structure.
"""

from __future__ import annotations

import ast
from pathlib import Path

from gzkit.validate import ValidationError

#: Primitives that reach a frontmatter ``status:`` scalar.
_STATUS_WRITE_PRIMITIVES = frozenset(
    {"_upsert_frontmatter_value", "rewrite_governed_keys_in_place"}
)

#: Consulting ANY of these satisfies the monitor obligation.
#:
#: ``obpi_status_write_refusal`` is the monitor itself;
#: ``guarded_obpi_status_write`` wraps it with the write;
#: ``_should_refuse_rewrite`` is the reconcile path's STRICTER gate — it
#: enforces the whole ``CANONICAL_TRANSITIONS`` table, which subsumes the
#: terminal rule. Admitting it is not a loophole: a superset of the monitor's
#: refusals is a stronger guarantee, not a weaker one.
_SANCTIONED_MONITORS = frozenset(
    {"obpi_status_write_refusal", "guarded_obpi_status_write", "_should_refuse_rewrite"}
)

#: Writers that do NOT consult the monitor, with the reason they need not.
#:
#: Keyed ``<repo-relative path>::<enclosing function>``. Every entry states a
#: SCOPE — which artifact kind it writes — because scope is precisely what was
#: unrecorded in the class of failure this audit belongs to. An entry with an
#: empty reason is refused (mirrors the ``AdvisorDiagnosis.proof``
#: ``min_length=1`` precedent): a one-token escape hatch is not a record.
_REGISTERED_WRITERS: dict[str, str] = {
    "src/gzkit/commands/obpi_cmd.py::_reset_brief_status_after_repudiation": (
        'Scope: OBPI brief. Exempt by construction — the `current == "completed"` '
        "guard above the write proves the source status is Completed, a non-terminal "
        "ATTESTED state, so the terminal-clobber class is unreachable here. "
        "Analyzed, not missed."
    ),
    "src/gzkit/commands/obpi_complete.py::_build_completed_brief": (
        "Scope: OBPI brief. Pure content builder — it returns a string and writes "
        "no file. Its only caller, `obpi_complete_cmd`, consults the monitor before "
        "invoking it. The seam is deliberate: the verdict is shared, the consequence "
        "(exit 1) belongs to the command."
    ),
    "src/gzkit/commands/adr_promote_utils.py::_mark_pool_adr_promoted": (
        "Scope: pool ADR, not an OBPI brief. OBPIState and its terminal rule do not "
        "govern ADR status; `_is_obpi_artifact` excludes these paths at the reconcile "
        "chokepoint for the same reason."
    ),
    "src/gzkit/commands/closeout.py::_complete_closeout_pipeline": (
        "Scope: the ADR's own `status:` frontmatter, not an OBPI brief. The same "
        "function auto-fixes OBPI rows via `auto_fix_obpi_rows`, which DOES route "
        "through the monitor; only the ADR-side write is exempt."
    ),
}


def _function_spans(tree: ast.Module) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    """Map each function's QUALIFIED name to its node.

    Qualified — ``Class.method``, ``outer.inner`` — rather than bare, because
    bare names collide. Two classes with a same-named method would let the
    monitor consultation in one mask a bypass in the other, which is a hole in
    a guard whose whole purpose is closing holes.
    """
    spans: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                qualified = f"{prefix}.{child.name}" if prefix else child.name
                if not isinstance(child, ast.ClassDef):
                    spans[qualified] = child
                walk(child, qualified)
            else:
                walk(child, prefix)

    walk(tree, "")
    return spans


def _enclosing_functions(tree: ast.Module) -> dict[int, str]:
    """Map each line number to the innermost enclosing function's qualified name."""
    owner: dict[int, str] = {}
    for qualified, node in sorted(
        _function_spans(tree).items(), key=lambda item: item[0].count(".")
    ):
        end = node.end_lineno or node.lineno
        for line in range(node.lineno, end + 1):
            owner[line] = qualified
    return owner


def _touches_status_key(call: ast.Call) -> bool:
    """Return True when this call plausibly reaches a ``status:`` scalar.

    Two shapes count, and the second is deliberately conservative:

    1. A ``"status"`` string literal anywhere in the arguments — the
       ``_upsert_frontmatter_value(content, "status", ...)`` and
       ``rewrite_governed_keys_in_place(path, {"status": ...})`` shapes.
    2. A ``rewrite_governed_keys_in_place`` call whose edits argument is NOT a
       literal. An opaque edits mapping *may* carry ``status``, and the audit
       cannot prove it does not — so it must consult the monitor. Assuming the
       benign reading of an unprovable case is how a convention-only guard
       decays in the first place.
    """
    for arg in [*call.args, *(kw.value for kw in call.keywords)]:
        if isinstance(arg, ast.Constant) and arg.value == "status":
            return True
        if isinstance(arg, ast.Dict) and any(
            isinstance(key, ast.Constant) and key.value == "status" for key in arg.keys
        ):
            return True
    if _called_name(call) == "rewrite_governed_keys_in_place" and len(call.args) >= 2:
        return not isinstance(call.args[1], ast.Dict)
    return False


def _called_name(call: ast.Call) -> str | None:
    """Return the bare callee name for ``f(...)`` and ``mod.f(...)`` alike."""
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def _consults_monitor(
    spans: dict[str, ast.FunctionDef | ast.AsyncFunctionDef], qualified_name: str
) -> bool:
    """Return True when the named function references a sanctioned monitor."""
    node = spans.get(qualified_name)
    if node is None:
        return False
    for inner in ast.walk(node):
        if isinstance(inner, ast.Name) and inner.id in _SANCTIONED_MONITORS:
            return True
        if isinstance(inner, ast.Attribute) and inner.attr in _SANCTIONED_MONITORS:
            return True
        if isinstance(inner, ast.ImportFrom) and any(
            alias.name in _SANCTIONED_MONITORS for alias in inner.names
        ):
            return True
    return False


def _audit_module(rel: str, tree: ast.Module) -> tuple[list[ValidationError], set[str]]:
    """Audit one module; return (findings, register keys this module justified)."""
    findings: list[ValidationError] = []
    justified: set[str] = set()
    owner = _enclosing_functions(tree)
    spans = _function_spans(tree)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _called_name(node)
        if name not in _STATUS_WRITE_PRIMITIVES or not _touches_status_key(node):
            continue

        function_name = owner.get(node.lineno, "<module>")
        key = f"{rel}::{function_name}"
        if _consults_monitor(spans, function_name):
            continue
        if key in _REGISTERED_WRITERS:
            justified.add(key)
            if not _REGISTERED_WRITERS[key].strip():
                findings.append(
                    ValidationError(
                        type="status_writer_coverage",
                        artifact=f"{rel}:{node.lineno}",
                        message=(
                            f"Registered writer `{key}` carries an empty reason. "
                            "A register entry must state what it writes and at what "
                            "scope; an empty reason is an escape hatch, not a record."
                        ),
                    )
                )
            continue

        findings.append(
            ValidationError(
                type="status_writer_coverage",
                artifact=f"{rel}:{node.lineno}",
                message=(
                    f"`{function_name}` writes a frontmatter `status:` key without "
                    "consulting the single invariant monitor. ADR-0.31.0 Decision "
                    "item 4 requires every governed-key write to pass through one "
                    "monitor (the GHI #348 terminal-clobber class). Route the write "
                    "through `guarded_obpi_status_write`, or consult "
                    "`obpi_status_write_refusal` directly and supply your own "
                    "consequence, or — if this writer does not touch an OBPI brief — "
                    f"add `{key}` to `_REGISTERED_WRITERS` in "
                    "`src/gzkit/governance/trust_audits/status_writer_coverage.py` "
                    "with a reason naming its scope."
                ),
            )
        )
    return findings, justified


def audit_status_writer_coverage(project_root: Path) -> list[ValidationError]:
    """Assert every OBPI-brief ``status:`` writer consults the single monitor."""
    src_root = project_root / "src" / "gzkit"
    if not src_root.is_dir():
        return []

    findings: list[ValidationError] = []
    justified: set[str] = set()
    for py_file in sorted(src_root.rglob("*.py")):
        rel = py_file.relative_to(project_root).as_posix()
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        module_findings, module_justified = _audit_module(rel, tree)
        findings.extend(module_findings)
        justified |= module_justified

    # Stale-register check. GHI #727 found the sole `_DATACLASS_WAIVERS` entry
    # inert because its staleness predicate asked *does this class still exist*
    # rather than *does it still need the exemption*. This asks the stronger
    # question: an entry is stale unless a live writer would have failed
    # without it.
    for key in sorted(set(_REGISTERED_WRITERS) - justified):
        findings.append(
            ValidationError(
                type="status_writer_coverage",
                artifact=key,
                message=(
                    f"Registered writer `{key}` is inert — no live call site needs "
                    "it. Either the writer was removed or it now consults the "
                    "monitor. Drop the entry so the register records only live "
                    "exemptions."
                ),
            )
        )
    return findings


__all__ = ["audit_status_writer_coverage"]
