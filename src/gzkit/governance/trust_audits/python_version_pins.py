"""Interpreter-pin coherence audit — one Python version, declared in many places.

The project's interpreter version is declared in ``.python-version`` and again
in every CI workflow that stands one up. Nothing held those copies in
agreement, so a patch bump that moved one and not the others left CI testing a
different interpreter than the one the operator tested locally — silently, and
with a green tree either side of the gap.

Measured at authoring (2026-08-19): five declarations across four files, all
hand-maintained. That is the shape ``.claude/rules/governance-core.md``
§ Non-negotiable rules names — a value that binds, restated in prose, with no
witness holding the restatements together.

**``.python-version`` is the authority.** uv reads it to resolve the project
interpreter, so it is the file that actually decides what ``uv run`` executes.
Every other declaration is a restatement and must match it exactly.

**``requires-python`` is deliberately NOT compared for equality.** It is a
floor (``>=3.13``), not a pin, and lowering it to a patch level would break
adopters resolving on an older patch. The audit checks only that the pinned
interpreter satisfies the floor — a pin below the project's own floor is
incoherent in the other direction.

Known limitation, stated rather than designed around: a workflow that
deliberately tests a MATRIX of interpreters would trip this audit, because
every declaration is compared against the single pin. No such matrix exists
today. Adding one is the point at which this audit needs an exemption
mechanism, and building that mechanism before the case exists would be
speculative (AGENTS.md § DO IT RIGHT 10).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

from gzkit.core.validation_rules import ValidationError

_AUDIT_TYPE = "python_version_pins"
_PIN_FILE = ".python-version"

#: ``python-version: "3.13.15"`` as actions/setup-python takes it. Quotes are
#: optional in YAML, so they are optional here.
_SETUP_PYTHON_RE = re.compile(r"""python-version:\s*["']?(\d+\.\d+(?:\.\d+)?)["']?""")

#: ``uv python install 3.13.15`` as the release workflow runs it.
_UV_INSTALL_RE = re.compile(r"uv python install\s+(\d+\.\d+(?:\.\d+)?)")

#: ``requires-python = ">=3.13"`` — a floor, never an equality target.
_REQUIRES_PYTHON_RE = re.compile(r"""^requires-python\s*=\s*["']>=\s*(\d+\.\d+(?:\.\d+)?)["']""")


def _as_tuple(version: str) -> tuple[int, ...]:
    """Return a comparable tuple for a dotted numeric version."""
    return tuple(int(part) for part in version.split("."))


def _satisfies_floor(pinned: str, floor: str) -> bool:
    """Return True when ``pinned`` is at or above ``floor``, padding shorter forms."""
    pin, base = _as_tuple(pinned), _as_tuple(floor)
    width = max(len(pin), len(base))
    return pin + (0,) * (width - len(pin)) >= base + (0,) * (width - len(base))


def evaluate_python_version_pins(
    pinned: str | None,
    declarations: Sequence[tuple[str, str]],
    requires_python_floor: str | None,
) -> list[ValidationError]:
    """Judge every interpreter declaration against the authoritative pin.

    Pure: takes already-parsed values rather than reading the tree, so the
    decision is exercisable without a repository (hexagonal § Operative rule 4).

    Args:
        pinned: The version in ``.python-version``, or ``None`` when absent.
        declarations: ``(site, version)`` pairs, where ``site`` is a
            human-readable ``path:line`` locator for the message.
        requires_python_floor: The ``>=`` floor from ``pyproject.toml``, or
            ``None`` when it declares none.

    Returns:
        One ``ValidationError`` per disagreeing declaration, plus one when the
        pin sits below the project's own floor. Empty when everything agrees.

    """
    if pinned is None:
        return [] if not declarations else [_missing_pin_error(declarations)]

    errors = [
        _mismatch_error(site, found, pinned) for site, found in declarations if found != pinned
    ]
    if requires_python_floor and not _satisfies_floor(pinned, requires_python_floor):
        errors.append(_below_floor_error(pinned, requires_python_floor))
    return errors


def _missing_pin_error(declarations: Sequence[tuple[str, str]]) -> ValidationError:
    """Report declarations that have no authority to agree with."""
    sites = ", ".join(site for site, _ in declarations)
    return ValidationError(
        type=_AUDIT_TYPE,
        artifact=_PIN_FILE,
        message=(
            f"{len(declarations)} interpreter declaration(s) exist ({sites}) but "
            f"`{_PIN_FILE}` is absent, so nothing is authoritative and they cannot "
            "be held in agreement. Next step: `uv python pin <version>` to declare "
            "the project interpreter."
        ),
    )


def _mismatch_error(site: str, found: str, pinned: str) -> ValidationError:
    """Report one declaration disagreeing with the authoritative pin."""
    return ValidationError(
        type=_AUDIT_TYPE,
        artifact=site,
        message=(
            f"Declares Python {found} but `{_PIN_FILE}` pins {pinned}. uv resolves "
            f"the project interpreter from `{_PIN_FILE}`, so this site tests a "
            "different interpreter than `uv run` uses locally — a divergence that "
            "leaves both sides green. Next step: change this declaration to "
            f"{pinned}, or move the pin and every other declaration together."
        ),
    )


def _below_floor_error(pinned: str, floor: str) -> ValidationError:
    """Report a pin that its own project floor would reject."""
    return ValidationError(
        type=_AUDIT_TYPE,
        artifact=_PIN_FILE,
        message=(
            f'Pins Python {pinned}, below the `requires-python = ">={floor}"` floor '
            "in pyproject.toml. The floor is the tested baseline for adopters; a pin "
            "beneath it means the project cannot install itself. Next step: raise the "
            "pin, or lower the floor deliberately."
        ),
    )


def _collect_workflow_declarations(project_root: Path) -> list[tuple[str, str]]:
    """Scan every workflow for interpreter declarations, in file then line order.

    Scans the directory rather than a hardcoded file list so a workflow added
    later is covered without editing this audit.
    """
    workflows = project_root / ".github" / "workflows"
    if not workflows.is_dir():
        return []
    found: list[tuple[str, str]] = []
    for path in sorted(workflows.glob("*.yml")) + sorted(workflows.glob("*.yaml")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in (_SETUP_PYTHON_RE, _UV_INSTALL_RE):
                match = pattern.search(line)
                if match:
                    rel = path.relative_to(project_root).as_posix()
                    found.append((f"{rel}:{lineno}", match.group(1)))
    return found


def _read_pin(project_root: Path) -> str | None:
    """Return the version in ``.python-version``, or None when absent or empty."""
    path = project_root / _PIN_FILE
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace").strip() or None


def _read_requires_python_floor(project_root: Path) -> str | None:
    """Return the ``>=`` floor from pyproject.toml, or None when it declares none."""
    path = project_root / "pyproject.toml"
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = _REQUIRES_PYTHON_RE.match(line.strip())
        if match:
            return match.group(1)
    return None


def audit_python_version_pins(project_root: Path) -> list[ValidationError]:
    """Assert every interpreter declaration agrees with ``.python-version``.

    Adapter around :func:`evaluate_python_version_pins`: reads the pin, the
    workflow declarations, and the pyproject floor, then delegates the judgment.
    """
    return evaluate_python_version_pins(
        _read_pin(project_root),
        _collect_workflow_declarations(project_root),
        _read_requires_python_floor(project_root),
    )
