"""Uncalled-gate inventory and disclosure (GHI #785).

A gate can exist, be correct, have teeth, and never be asked. Two observed
instances in one week came from that population: the ``module-sloc-cap-radon``
shrink ratchet had teeth from its 2026-08-01 cutover and no caller, so a
297-SLOC breach shipped in v0.34.2 with every gate green; and
``gz validate --sensitivity`` was red on a live brief while ``gz check`` stayed
green, surfacing only because someone ran the scope by hand.

**The class.** Every reachability mechanism here polices its OWN membership. The
QC registry fail-closes on an unclassified ``gz check`` step -- but only for steps
already in ``_build_check_steps()``. ``run_enforcement_floor_audit`` fail-closes on
an enrolled claim with no negative control -- but only for enrolled claims.
``test_every_default_tier_scope_runs_in_the_gate`` fail-closes on a default-tier
scope outside the gate -- but only for the default tier. Each is sound; none can
ask *"what exists that is in none of us?"*, and that is where both instances came
from. The failure is silent by construction: an uncalled gate reports nothing, so
its evidence of absence is indistinguishable from a green run.

**What this module is, and is not.** It is INVENTORY AND DISCLOSURE, not
enrollment. Enrolling every unreached scope into ``gz check`` would be wrong --
several are deliberately explicit because they are expensive or single-artifact
scoped. Which of them deserve callers is a separate per-scope ruling. This makes
"this gate has no automatic caller" a counted, visible fact with an accepted-list
that can only shrink, on the ``data/module_size_grandfather.json`` pattern.

**Caller surfaces are plural, and that is load-bearing.** GHI #785's own
measurement scanned ``src/gzkit/quality.py`` alone and reported 41 unreached
scopes. Four of them -- ``authorship``, ``bullet_retention``, ``pointer_anchors``,
``surface_weight`` -- are invoked by ``.pre-commit-config.yaml`` on every commit.
Scanning one caller surface reproduces, one level up, the single-membership
blindness the issue names; the real figure against all automatic surfaces is 38.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import NamedTuple

from gzkit.core.validation_rules import ValidationError

ACCEPTED_REL = Path("data") / "uncalled_gate_grandfather.json"
_ENTRIES_KEY = "accepted_gates"
_RECOVER = "uv run gz validate --gate-callers"

# The `gz check` half of the question is ALREADY declared and already enforced:
# `data/check_scope_membership.json` (GHI #744) splits every registered validate
# scope into in_check / out_of_check, and `test_check_scope_parity` fail-closes
# when that declaration disagrees with `_build_check_steps()`. This module DERIVES
# its validate-scope population from that file rather than re-deriving it by
# scanning `quality.py` (operator ruling 2026-08-09). Two hand-maintained lists of
# the same membership is the parallel model `.claude/rules/hexagonal-architecture.md`
# rule 8 forbids -- and the second reader would be free to disagree with the first.
_MEMBERSHIP_REL = Path("data") / "check_scope_membership.json"

# A surface that invokes a gate WITHOUT a human choosing that specific gate.
# `gz check` is delegated to _MEMBERSHIP_REL above, so what remains to scan is the
# pre-commit hook set and CI. A chore an operator runs by hand is not automatic,
# which is why chore scripts are a population here rather than a caller surface --
# and `quality.py` IS scanned for them, because that is where a wired chore's slug
# appears (`_resolve_chore_dir("module-sloc-cap-radon")`).
_QUALITY_REL = Path("src") / "gzkit" / "quality.py"
_PRECOMMIT_REL = Path(".pre-commit-config.yaml")
_WORKFLOWS_REL = Path(".github") / "workflows"
_CHORES_REL = Path(".gzkit") / "chores"

_FLAG_RE = re.compile(r"--([a-z0-9][a-z0-9-]*)")


class GateStatus(NamedTuple):
    """One gate's caller verdict.

    ``gate`` is the population-qualified id (``validate:<stem>`` or
    ``chore:<slug>``) so the two populations share one accepted-list and one
    shrink baseline.
    """

    gate: str
    called: bool
    surfaces: tuple[str, ...]


def _err(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="gate-callers", artifact=artifact, message=message)


def _caller_surfaces(project_root: Path, *, include_gz_check: bool) -> list[Path]:
    """Automatic caller surfaces to scan.

    ``include_gz_check`` adds ``quality.py``. It is False for validate scopes
    (that half is delegated to ``_MEMBERSHIP_REL``) and True for chores, whose
    only wiring point is a slug reference in ``quality.py``.
    """
    surfaces = [project_root / _PRECOMMIT_REL]
    if include_gz_check:
        surfaces.insert(0, project_root / _QUALITY_REL)
    workflows = project_root / _WORKFLOWS_REL
    if workflows.is_dir():
        surfaces.extend(sorted(workflows.glob("*.yml")))
        surfaces.extend(sorted(workflows.glob("*.yaml")))
    return [s for s in surfaces if s.is_file()]


def _surface_texts(project_root: Path, *, include_gz_check: bool) -> list[tuple[str, str]]:
    texts: list[tuple[str, str]] = []
    for surface in _caller_surfaces(project_root, include_gz_check=include_gz_check):
        try:
            body = surface.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        texts.append((surface.relative_to(project_root).as_posix(), body))
    return texts


def _cited_scope_flags(texts: list[tuple[str, str]]) -> dict[str, list[str]]:
    """Map validate-scope stem -> caller surfaces citing it.

    Only lines mentioning ``gz validate`` are read, so an unrelated ``--flag``
    elsewhere in a workflow cannot forge a caller.
    """
    cited: dict[str, list[str]] = {}
    for name, body in texts:
        for line in body.splitlines():
            if "gz validate" not in line:
                continue
            for flag in _FLAG_RE.findall(line):
                cited.setdefault(flag.replace("-", "_"), []).append(name)
    return cited


def _chore_gate_scripts(project_root: Path) -> list[str]:
    chores = project_root / _CHORES_REL
    if not chores.is_dir():
        return []
    slugs: list[str] = []
    for d in sorted(p for p in chores.iterdir() if p.is_dir()):
        if any(f.suffix == ".py" for f in d.iterdir() if f.is_file()):
            slugs.append(d.name)
    return slugs


def _gz_check_uncalled_scopes(project_root: Path) -> list[str] | None:
    """Read ``out_of_check`` — the scopes `gz check` does not invoke (GHI #744).

    Returns ``None`` when the declaration is missing or unparseable, which the
    audit turns into a fail-closed finding: with no population there is nothing
    to inventory, and reporting green would be the silence this gate exists to
    break.
    """
    try:
        payload = json.loads((project_root / _MEMBERSHIP_REL).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    entries = payload.get("out_of_check") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return None
    return [str(e) for e in entries]


def uncalled_gates(
    project_root: Path,
    *,
    gz_check_uncalled_scopes: list[str] | None = None,
) -> list[GateStatus]:
    """Return every CANDIDATE gate with its caller verdict.

    This is the disclosure half — it reports a verdict per gate, called or not,
    so the count is readable without inferring it from an absence of errors.

    The population is deliberately NOT every registered scope. A scope in
    ``in_check`` is called by definition, and GHI #744's parity test already
    fail-closes if that declaration disagrees with ``_build_check_steps()``.
    Re-deriving it here would be a second reader free to disagree with the
    first. So the candidates are ``out_of_check`` plus the chore gate scripts,
    and the only remaining question is whether pre-commit or CI reaches them.

    ``gz_check_uncalled_scopes`` is injected for tests; ``None`` reads
    ``data/check_scope_membership.json``.
    """
    scopes = (
        _gz_check_uncalled_scopes(project_root) or []
        if gz_check_uncalled_scopes is None
        else gz_check_uncalled_scopes
    )
    scope_texts = _surface_texts(project_root, include_gz_check=False)
    cited = _cited_scope_flags(scope_texts)

    report: list[GateStatus] = []
    for stem in scopes:
        surfaces = tuple(dict.fromkeys(cited.get(stem, [])))
        report.append(GateStatus(f"validate:{stem}", bool(surfaces), surfaces))

    chore_texts = _surface_texts(project_root, include_gz_check=True)
    for slug in _chore_gate_scripts(project_root):
        surfaces = tuple(name for name, body in chore_texts if slug in body)
        report.append(GateStatus(f"chore:{slug}", bool(surfaces), surfaces))
    return report


def _load_accepted(project_root: Path) -> tuple[list[dict[str, object]], ValidationError | None]:
    path = project_root / ACCEPTED_REL
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return [], _err(
            ACCEPTED_REL.as_posix(),
            f"The uncalled-gate accepted-list {ACCEPTED_REL.name} is missing or unparseable, so "
            f"every gate with no automatic caller would pass unreported — the silent-bypass this "
            f"inventory exists to close (GHI #785). Author {ACCEPTED_REL.as_posix()} with an "
            f"'{_ENTRIES_KEY}' list. Re-run `{_RECOVER}`.",
        )
    entries = payload.get(_ENTRIES_KEY) if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return [], _err(
            ACCEPTED_REL.as_posix(),
            f"The uncalled-gate accepted-list {ACCEPTED_REL.name} carries no '{_ENTRIES_KEY}' "
            f"list, so no gate can be accepted and no count is visible (GHI #785). Add the key. "
            f"Re-run `{_RECOVER}`.",
        )
    return [e for e in entries if isinstance(e, dict)], None


def audit_gate_callers(
    project_root: Path,
    *,
    gz_check_uncalled_scopes: list[str] | None = None,
) -> list[ValidationError]:
    """Flag every gate with no automatic caller that is not accepted, and vice versa.

    Returns one ``ValidationError`` per finding (non-empty → caller exits 3).
    Four arms, each closing a different way the inventory could rot:

    1. an uncalled gate absent from the accepted-list — the new hole;
    2. an accepted gate that has since gained a caller — the stale acceptance
       that would otherwise sit in the file forever, keeping the shrink-ratchet
       baseline propped up while claiming debt that no longer exists;
    3. an accepted gate that no longer exists — a pointer to a deleted scope;
    4. the derived-from population itself being unreadable — with no population
       there is nothing to inventory, and a green run would be the silence this
       gate exists to break.
    """
    accepted, load_error = _load_accepted(project_root)
    if load_error is not None:
        return [load_error]

    if gz_check_uncalled_scopes is None and _gz_check_uncalled_scopes(project_root) is None:
        return [
            _err(
                _MEMBERSHIP_REL.as_posix(),
                f"{_MEMBERSHIP_REL.as_posix()} is missing, unparseable, or carries no "
                f"'out_of_check' list. This inventory DERIVES its scope population from that "
                f"declaration (GHI #744/#785), so without it no gate can be inventoried and a "
                f"green run would assert something never measured. Repair the file. Re-run "
                f"`{_RECOVER}`.",
            )
        ]

    report = uncalled_gates(project_root, gz_check_uncalled_scopes=gz_check_uncalled_scopes)
    status = {g.gate: g for g in report}

    errors: list[ValidationError] = []
    accepted_ids: set[str] = set()

    for entry in accepted:
        gate = str(entry.get("gate", "")).strip()
        if not gate:
            errors.append(
                _err(
                    ACCEPTED_REL.as_posix(),
                    f"An entry in {ACCEPTED_REL.name} has no 'gate' id, so it accepts nothing "
                    f"and cannot be audited (GHI #785). Give it a 'validate:<stem>' or "
                    f"'chore:<slug>' id. Re-run `{_RECOVER}`.",
                )
            )
            continue
        accepted_ids.add(gate)
        if not str(entry.get("reason", "")).strip():
            errors.append(
                _err(
                    gate,
                    f"Accepted gate {gate} carries no 'reason'. An acceptance without a stated "
                    f"reason records that somebody noticed, not why it is tolerable, so it can "
                    f"never be reviewed or drained (GHI #785). State why this gate has no "
                    f"automatic caller. Re-run `{_RECOVER}`.",
                )
            )
        found = status.get(gate)
        if found is None:
            errors.append(
                _err(
                    gate,
                    f"Accepted gate {gate} no longer exists in either population — the scope was "
                    f"renamed or the chore removed, so the acceptance is a dead pointer holding "
                    f"the shrink-ratchet baseline up (GHI #785). Remove the entry from "
                    f"{ACCEPTED_REL.as_posix()} and lower 'baseline_count' in "
                    f"data/waiver_ratchet_registry.json. Re-run `{_RECOVER}`.",
                )
            )
        elif found.called:
            errors.append(
                _err(
                    gate,
                    f"Accepted gate {gate} now has an automatic caller "
                    f"({', '.join(found.surfaces)}), so its acceptance is stale (GHI #785). The "
                    f"accepted-list is shrink-only: surrender the entry in "
                    f"{ACCEPTED_REL.as_posix()} and lower 'baseline_count' in "
                    f"data/waiver_ratchet_registry.json. Re-run `{_RECOVER}`.",
                )
            )

    for gate in report:
        if gate.called or gate.gate in accepted_ids:
            continue
        errors.append(
            _err(
                gate.gate,
                f"Gate {gate.gate} has no automatic caller: nothing in `gz check`, "
                f"`.pre-commit-config.yaml`, or `.github/workflows/**` invokes it, so it can be "
                f"red indefinitely while every gate reports green — evidence of absence is "
                f"indistinguishable from a passing run (GHI #785). Either wire a caller, or "
                f"record it in {ACCEPTED_REL.as_posix()} with a reason and raise "
                f"'baseline_count' in data/waiver_ratchet_registry.json in the same commit. "
                f"Re-run `{_RECOVER}`.",
            )
        )
    return errors
