"""Constitutional-invariant witness resolution (GHI #623).

A ``ConstitutionalInvariant`` declares, in ``structural_witness``, the command that
mechanically enforces its claim. Nothing checked that the command exists. That is the
structural-witness theater ADR-0.0.37's audit named, one layer up: the registry asserts
an invariant is enforced, the named enforcer is vapor, and no gate disagrees.

Caught live by this scope: ``foundation-adr-registers-invariant.json`` named
``gz validate --foundation-registers-invariant``, a scope that has never existed.

Resolution accepts the two witness shapes the registry actually uses:

- ``gz validate --<scope>`` — resolved against ``VALIDATOR_REGISTRY`` stems
- ``gz <verb> [<subverb>...]`` — resolved against registered parser leaf paths

A trailing parenthetical is documentation, not part of the command, and is stripped
before resolution (``gz obpi complete (stage 5)`` → ``gz obpi complete``).
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.core.validation_rules import ValidationError

_ANNOTATION_RE = re.compile(r"\s*\([^)]*\)\s*$")
_VALIDATE_FLAG_RE = re.compile(r"^gz validate --(?P<flag>[a-z0-9-]+)$")


def _strip_annotation(witness: str) -> str:
    """Drop a trailing ``(...)`` documentation tail from a witness string."""
    return _ANNOTATION_RE.sub("", witness.strip())


def _known_validate_scopes() -> frozenset[str]:
    """Return every registered ``gz validate`` scope stem."""
    from gzkit.commands.validate_cmd import VALIDATOR_REGISTRY  # noqa: PLC0415

    return frozenset(entry.stem for entry in VALIDATOR_REGISTRY)


def _known_verb_paths() -> frozenset[str]:
    """Return every registered CLI leaf command path (e.g. ``skill audit``)."""
    from gzkit.governance.trust_audits.cli import _known_cli_verb_paths  # noqa: PLC0415

    return _known_cli_verb_paths()


def _resolves(witness: str) -> bool:
    """Return True when *witness* names a command this CLI actually registers."""
    command = _strip_annotation(witness)

    flag_match = _VALIDATE_FLAG_RE.match(command)
    if flag_match is not None:
        return flag_match.group("flag").replace("-", "_") in _known_validate_scopes()

    if not command.startswith("gz "):
        return False
    path = command[len("gz ") :].strip()
    return path in _known_verb_paths()


def _recovery_prose(invariant_id: str, witness: str) -> str:
    """Three-part recovery message (.claude/rules/guardrail-feedback-prose.md)."""
    return (
        f"Invariant {invariant_id!r} declares structural witness {witness!r}, which "
        f"resolves to no registered command. An invariant whose witness does not exist "
        f"claims mechanical enforcement it does not have — the structural-witness theater "
        f"ADR-0.0.37's closeout audit named (GHI #623). Either register the command that "
        f"enforces the claim, or correct the witness to name the gate that already does "
        f"(list registered scopes with `uv run gz validate --help`); if nothing enforces "
        f"the claim, the entry is asserting an invariant that is not in force and must be "
        f"retired rather than left standing."
    )


def validate_invariant_witnesses(root: Path) -> list[ValidationError]:
    """Fail closed when any registered invariant's structural witness does not resolve.

    Every witness of every entry is checked — a resolvable first witness does not
    excuse a vapor second one. Bootstrap-safe: no registry directory yields no findings.
    """
    from gzkit.governance.invariants import load_invariants  # noqa: PLC0415

    inv_dir = root / ".gzkit" / "invariants"
    if not inv_dir.exists():
        return []

    errors: list[ValidationError] = []
    for invariant_id, invariant in sorted(load_invariants(root).items()):
        for witness in invariant.structural_witness:
            if not _resolves(witness):
                errors.append(
                    ValidationError(
                        type="invariant_witness",
                        artifact=f".gzkit/invariants/{invariant_id}.json",
                        message=_recovery_prose(invariant_id, witness),
                    )
                )
    return errors
