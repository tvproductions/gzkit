"""Static theater-signature analyzer — channel 1 of the qc-binding antibody.

ADR-0.0.73 designed the antibody with two channels: behavioral negative-control
execution (channel 2, the primary), and a static theater-signature scan "layered
on top" (channel 1). Channel 1 was inert because the analyzer that detects
signatures in real source was deferred to the repudiated OBPI-0.0.73-02 and never
built. This module is the correction (GHI #657): it scans validator source via
``ast`` and reports the three structurally-decidable theater signatures.

Detected (structurally decidable; each calibrated on a named real facade):

* ``copy-vs-self`` — tautological self-equality (``a == a`` / ``assertEqual(x, x)``)
  that can never fail. Calibrated on the ADR-0.0.37 fixture==fixture facade.
* ``mtime-where-name-says-content`` — a content/freshness-named function whose body
  reads ``st_mtime``/``getmtime`` instead of content. Calibrated on the repudiated
  ``rendition_freshness`` mtime tautology.
* ``skip-if-PASS`` — a clean early-return gated on persisted PASS state (the check
  never runs the second time).

Deliberately NOT detected — owned by channel 2 (a static detector for these would
itself grade by keyword/prose shape, reintroducing the GHI #624 facade):
``prose-graded-by-nothing``, ``shape-graded-not-substance``, ``empty-input-passes``,
``fixture-only``.

Pattern reuse: ``ast.parse`` + ``ast.walk`` + ``isinstance`` per
``gzkit.tautological_tests`` (the established convention). Stdlib ``ast`` only.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path

from gzkit.models.theater_signatures import TheaterSignatureFinding

# The "plant violations on purpose" infrastructure is never its own subject:
# the analyzer (references signature strings) and the NC fixture modules (build
# planted-violation source) must not be scanned, or the analyzer would flag its
# own scaffolding.
_SELF_EXCLUSION: frozenset[str] = frozenset(
    {
        "src/gzkit/governance/trust_audits/theater_signature_scan.py",
        "src/gzkit/governance/trust_audits/_qc_negative_controls.py",
        "src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py",
    }
)

# mtime-where-name-says-content: the function name must imply content/freshness
# semantics. This is a NARROWING filter applied on top of a concrete mtime AST
# node — never the grading basis (the node is the fact; the name only reduces
# scope), so it is not shape-grading.
_CONTENT_NAME_TOKENS: frozenset[str] = frozenset(
    {"content", "fresh", "coher", "hash", "equal", "match", "verify", "drift"}
)

# skip-if-PASS: a clean early-return gated on one of these persisted states.
_PASS_STATES: frozenset[str] = frozenset({"PASS", "PASSED", "GREEN", "VALIDATED"})


def _is_pure_operand(node: ast.expr) -> bool:
    """Return True if the operand contains no call (``f() == f()`` may be non-deterministic).

    The copy-vs-self purity guard: only flag self-equality over call-free operands,
    so a legitimate (possibly side-effecting / non-deterministic) ``now() == now()``
    is never flagged.
    """
    return not any(isinstance(child, ast.Call) for child in ast.walk(node))


def _detect_copy_vs_self(
    fn: ast.FunctionDef | ast.AsyncFunctionDef, rel: str
) -> list[TheaterSignatureFinding]:
    """Flag tautological self-equality: ``a == a``, ``a is a``, ``assertEqual(x, x)``.

    Calibrated on the ADR-0.0.37 fixture==fixture facade (an assertion that can
    never fail). Guards: only ``Eq``/``Is`` (``!=`` is the NaN idiom), only
    call-free operands (purity).
    """
    out: list[TheaterSignatureFinding] = []
    for child in ast.walk(fn):
        # Match A: assertEqual(x, x) / assertIs(x, x)
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr in {"assertEqual", "assertIs"}
            and len(child.args) >= 2
            and _is_pure_operand(child.args[0])
            and _is_pure_operand(child.args[1])
            and ast.dump(child.args[0]) == ast.dump(child.args[1])
        ):
            out.append(
                TheaterSignatureFinding(
                    signature="copy-vs-self",
                    file_path=rel,
                    line_number=child.lineno,
                    function_name=fn.name,
                    evidence=f"{child.func.attr}(x, x): operands are identical — can never fail",
                )
            )
            continue
        # Match B: a == a / a is a
        if (
            isinstance(child, ast.Compare)
            and len(child.ops) == 1
            and isinstance(child.ops[0], (ast.Eq, ast.Is))
            and _is_pure_operand(child.left)
            and _is_pure_operand(child.comparators[0])
            and ast.dump(child.left) == ast.dump(child.comparators[0])
        ):
            out.append(
                TheaterSignatureFinding(
                    signature="copy-vs-self",
                    file_path=rel,
                    line_number=child.lineno,
                    function_name=fn.name,
                    evidence="self-comparison (x == x): tautological, can never fail",
                )
            )
    return out


def _is_mtime_node(node: ast.AST) -> bool:
    """Return True for ``<expr>.st_mtime`` attribute access or a ``getmtime(...)`` call.

    Inspects Attribute/Call nodes ONLY — never ``ast.Constant`` — so an ``st_mtime``
    mention inside a docstring is structurally invisible (the load-bearing FP guard).
    """
    if isinstance(node, ast.Attribute) and node.attr == "st_mtime":
        return True
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "getmtime":
            return True
        if isinstance(func, ast.Name) and func.id == "getmtime":
            return True
    return False


def _detect_mtime_content(
    fn: ast.FunctionDef | ast.AsyncFunctionDef, rel: str
) -> list[TheaterSignatureFinding]:
    """Flag a content/freshness-named function that reads mtime instead of content.

    Calibrated on the repudiated ``rendition_freshness`` mtime tautology. The name
    token is a narrowing filter on top of the concrete mtime node, so a docstring
    mention (Constant) and a non-content reader (``rotate_logs``) are not flagged.
    """
    name = fn.name.lower()
    if not any(token in name for token in _CONTENT_NAME_TOKENS):
        return []
    for child in ast.walk(fn):
        if isinstance(child, (ast.Attribute, ast.Call)) and _is_mtime_node(child):
            return [
                TheaterSignatureFinding(
                    signature="mtime-where-name-says-content",
                    file_path=rel,
                    line_number=child.lineno,
                    function_name=fn.name,
                    evidence=(
                        f"{fn.name!r} implies content/freshness but reads mtime "
                        "(name-says-content, body-checks-mtime)"
                    ),
                )
            ]
    return []


def _locally_assigned_names(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> frozenset[str]:
    """Names assigned via ``=`` anywhere in the function body (freshly computed)."""
    names: set[str] = set()
    for child in ast.walk(fn):
        if isinstance(child, ast.Assign):
            for target in child.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return frozenset(names)


def _root_name(node: ast.expr) -> str | None:
    """Root ``Name`` id of an attribute/subscript chain (``a.b.c`` / ``a[0]`` -> ``a``)."""
    while isinstance(node, (ast.Attribute, ast.Subscript)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _is_clean_early_return(stmt: ast.stmt) -> bool:
    """Return True for a single clean/empty early return.

    Matches ``return []`` / ``0`` / ``None`` / ``True``.
    """
    if not isinstance(stmt, ast.Return):
        return False
    value = stmt.value
    if value is None:
        return True
    if isinstance(value, ast.List) and not value.elts:
        return True
    return isinstance(value, ast.Constant) and value.value in (0, None, True)


def _detect_skip_if_pass(
    fn: ast.FunctionDef | ast.AsyncFunctionDef, rel: str
) -> list[TheaterSignatureFinding]:
    """Flag a clean early-return gated on a persisted PASS state.

    The guarded value must be persisted/external state (an Attribute/Subscript whose
    root is NOT locally assigned) — a locally-computed ``status = run_check()`` is a
    legitimate early-return and is not flagged.
    """
    local = _locally_assigned_names(fn)
    out: list[TheaterSignatureFinding] = []
    for child in ast.walk(fn):
        if not (isinstance(child, ast.If) and len(child.body) == 1):
            continue
        test = child.test
        if not (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value in _PASS_STATES
        ):
            continue
        left = test.left
        # Persisted state only: a read off external/param state, not a fresh local.
        if not isinstance(left, (ast.Attribute, ast.Subscript)):
            continue
        if _root_name(left) in local:
            continue
        if _is_clean_early_return(child.body[0]):
            out.append(
                TheaterSignatureFinding(
                    signature="skip-if-PASS",
                    file_path=rel,
                    line_number=child.lineno,
                    function_name=fn.name,
                    evidence=(
                        "clean early-return gated on persisted PASS state — "
                        "the check never runs the second time"
                    ),
                )
            )
    return out


def scan_source_for_signatures(source_path: Path, *, rel: str) -> list[TheaterSignatureFinding]:
    """Scan one ``.py`` file for the three detected theater signatures.

    Unparseable or unreadable files yield no findings (``(SyntaxError, OSError)``),
    matching the tautological-test scanner's posture.
    """
    try:
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    except (SyntaxError, OSError):
        return []
    out: list[TheaterSignatureFinding] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.extend(_detect_copy_vs_self(node, rel))
            out.extend(_detect_mtime_content(node, rel))
            out.extend(_detect_skip_if_pass(node, rel))
    return out


def scan_validator_tree(project_root: Path, files: Iterable[Path]) -> list[TheaterSignatureFinding]:
    """Scan the given validator-source files, skipping the self-exclusion set.

    ``project_root`` anchors the posix relative path used for findings and for the
    ``_SELF_EXCLUSION`` membership test.
    """
    out: list[TheaterSignatureFinding] = []
    for py_file in sorted(files):
        try:
            rel = py_file.relative_to(project_root).as_posix()
        except ValueError:
            rel = py_file.as_posix()
        if rel in _SELF_EXCLUSION:
            continue
        out.extend(scan_source_for_signatures(py_file, rel=rel))
    return out
