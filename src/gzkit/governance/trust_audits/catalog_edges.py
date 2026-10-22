"""Requirements catalog scope, edges, coverage and BDD alignment (drydock RO-3 tranche 3).

`docs/governance/harbor-ro3-requirements-store.md` § The witness. Every check is a
pure function over parsed inputs; `gzkit.governance.trust_audits.catalog` gathers
them from the project and runs these after the structure checks pass.

* **Edges**: `depends_on` names an outcome code, `gate:<n>` for a gate the
  manifest declares, or `external:<slug>` from the catalog's roster (operator,
  "Declared prefixes (Rec.)", 2026-10-22), and the outcome edges are acyclic;
  `governed_by` resolves to an ADR through the RO-2 seam; `member_of` names an
  outcome; `derives_from` names a live PRD FR or a § 7 attribute as `NFR-<slug>`
  derived from its heading (operator, "Derive from heading (Rec.)").
* **Coverage report**: the PRD needs no REQ derives from, advisory until the
  catalog is populated.
* **BDD alignment**: a user-facing outcome names a feature file carrying its code
  as a tag, and each BEHAVIOR REQ under it has a scenario tagged with its id there
  and an `@covers` test (operator, "Widen both bindings (Rec.)").

The freeze lock is RO-5's (operator, "Leave to RO-5 (Rec.)").
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence

from gzkit.core.validation_rules import ValidationError
from gzkit.models.catalog import CATALOG_FILES, Catalog
from gzkit.traceability import CatalogBindings

_TYPE = "catalog"
_RECOVER = (
    "The catalog's edges are ruled in docs/governance/harbor-ro3-requirements-store.md "
    "(The witness). Correct the entry, then re-run `uv run gz validate --catalog`."
)

_SECTION = re.compile(r"^## (?P<title>.+?)\s*$")
_HEADING = re.compile(r"^### (?P<title>.+?)\s*$")
_FR = re.compile(r"^(?P<id>FR-\d{3}[a-z]?):")
_RETIRED = re.compile(r"^\*\*Retired\b")


def _err(kind: str, check: str, message: str) -> ValidationError:
    return ValidationError(
        type=_TYPE,
        artifact=f"data/{CATALOG_FILES[kind]}",
        message=f"{message} {_RECOVER}",
        field=check,
    )


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def prd_needs(text: str) -> tuple[str, ...]:
    """Return the PRD's live FR ids and its § 7 attributes as `NFR-<slug>`, in order.

    An FR is live unless the first prose under its heading marks it `**Retired`.
    """
    needs: list[str] = []
    section = ""
    pending: str | None = None
    for line in text.splitlines():
        if (match := _SECTION.match(line)) is not None:
            section = match["title"]
            pending = None
            continue
        if (match := _HEADING.match(line)) is not None:
            fr = _FR.match(match["title"])
            pending = fr["id"] if fr is not None else None
            if pending is None and section.startswith("7."):
                needs.append(f"NFR-{_slug(match['title'])}")
            continue
        if pending is not None and line.strip():
            if not _RETIRED.match(line.strip()):
                needs.append(pending)
            pending = None
    if pending is not None:
        needs.append(pending)
    return tuple(needs)


def _cycle_members(edges: dict[str, list[str]]) -> list[str]:
    """Return the outcome codes on a dependency cycle, sorted."""
    on_cycle: set[str] = set()
    state: dict[str, int] = {}

    def visit(code: str, path: list[str]) -> None:
        state[code] = 1
        for target in edges.get(code, []):
            if state.get(target) == 1:
                on_cycle.update(path[path.index(target) :])
            elif state.get(target) is None:
                visit(target, [*path, target])
        state[code] = 2

    for code in sorted(edges):
        if code not in state:
            visit(code, [code])
    return sorted(on_cycle)


def _depends_on_findings(catalog: Catalog, gates: frozenset[int]) -> list[ValidationError]:
    codes = {outcome.code for outcome in catalog.outcomes}
    externals = {external.slug for external in catalog.externals}
    unresolved: list[str] = []
    edges: dict[str, list[str]] = {}
    for outcome in catalog.outcomes:
        for target in outcome.depends_on:
            prefix, _, name = target.partition(":")
            if not name:
                resolves = target in codes
                edges.setdefault(outcome.code, []).append(target)
            elif prefix == "gate":
                resolves = name.isdigit() and int(name) in gates
            else:
                resolves = prefix == "external" and name in externals
            if not resolves:
                unresolved.append(f"{outcome.code} -> {target}")
    errors: list[ValidationError] = []
    if unresolved:
        errors.append(
            _err(
                "outcomes",
                "depends_on",
                f"depends_on names nothing it may: {', '.join(unresolved)}. An entry is an "
                "outcome code, gate:<n> for a gate .gzkit/manifest.json declares, or "
                f"external:<slug> from data/{CATALOG_FILES['externals']}.",
            )
        )
    if cycle := _cycle_members(edges):
        errors.append(
            _err(
                "outcomes",
                "depends_on",
                f"Outcomes {', '.join(cycle)} depend on each other in a cycle; readiness "
                "derives only from these edges, so they must be acyclic.",
            )
        )
    return errors


def edge_findings(
    catalog: Catalog,
    *,
    needs: frozenset[str],
    gates: frozenset[int],
    governs: Callable[[str], bool],
) -> list[ValidationError]:
    """Check that every edge resolves: `depends_on`, `governed_by`, `member_of`, `derives_from`."""
    errors = _depends_on_findings(catalog, gates)
    ungoverned = [
        f"{outcome.code} -> {adr}"
        for outcome in catalog.outcomes
        for adr in outcome.governed_by
        if not governs(adr)
    ]
    if ungoverned:
        errors.append(
            _err(
                "outcomes",
                "governed_by",
                f"governed_by names no ADR the identity seam resolves: {', '.join(ungoverned)}.",
            )
        )
    codes = {outcome.code for outcome in catalog.outcomes}
    orphans = [f"{req.id} -> {req.member_of}" for req in catalog.reqs if req.member_of not in codes]
    if orphans:
        errors.append(
            _err(
                "reqs",
                "member_of",
                f"member_of names no outcome in data/{CATALOG_FILES['outcomes']}: "
                f"{', '.join(orphans)}.",
            )
        )
    underived = [
        f"{req.id} -> {need}"
        for req in catalog.reqs
        for need in req.derives_from
        if need not in needs
    ]
    if underived:
        errors.append(
            _err(
                "reqs",
                "derives_from",
                f"derives_from names no live PRD FR or section 7 attribute (NFR-<slug>): "
                f"{', '.join(underived)}.",
            )
        )
    return errors


def coverage_gaps(catalog: Catalog, needs: Sequence[str]) -> list[str]:
    """Return the PRD needs no REQ derives from, in the PRD's order."""
    derived = {need for req in catalog.reqs for need in req.derives_from}
    return [need for need in needs if need not in derived]


def bdd_findings(catalog: Catalog, bindings: CatalogBindings) -> list[ValidationError]:
    """Check each user-facing outcome's feature tag and its BEHAVIOR REQs' two bindings."""
    errors: list[ValidationError] = []
    for outcome in catalog.outcomes:
        if not outcome.user_facing or outcome.retired:
            continue
        feature = outcome.feature
        if feature is None or outcome.code not in bindings.feature_tags.get(feature, ()):
            errors.append(
                _err(
                    "outcomes",
                    "feature",
                    f"User-facing outcome {outcome.code} names no feature file carrying "
                    f"@{outcome.code} as a feature tag (feature: {feature!r}).",
                )
            )
            continue
        tagged = bindings.scenario_reqs.get(feature, frozenset())
        members = [
            r.id for r in catalog.reqs if r.member_of == outcome.code and r.kind == "BEHAVIOR"
        ]
        if untagged := [req for req in members if req not in tagged]:
            errors.append(
                _err(
                    "reqs",
                    "scenario",
                    f"BEHAVIOR REQs {', '.join(untagged)} of {outcome.code} have no scenario "
                    f"tagged with their id in {feature}.",
                )
            )
        if uncovered := [req for req in members if req not in bindings.covered_reqs]:
            errors.append(
                _err(
                    "reqs",
                    "covers",
                    f"BEHAVIOR REQs {', '.join(uncovered)} of {outcome.code} have no @covers test.",
                )
            )
    return errors
