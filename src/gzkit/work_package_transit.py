"""The airlock on the work package (RO-14 act 6, GHI #1185).

A work package enters through the airlock when it commences and leaves when it is
accepted, and those verbs call this module, so the exit cannot go unreached as it
did for a brief. The airlock itself only reports (operator doctrine: it "is not a
verification gate"); the refusal is `gz wp accept`'s, as the same finding's is
`gz obpi complete`'s (#1181). Operator rulings 2026-11-01, by selection:

- "Repair declares (Recommended)": a repair package declares `modules`. A delivery
  package reads its outcome's, which RO-11 tranche 2 lands; until then its exit
  reports `undeclared`. The ledger holds a frozen footprint, so a hand edit of the
  store moves nothing.
- "Task trailer (Recommended)": a commit is the package's when its `Task:` trailer
  starts with the lowercased package id; uncommitted work counts too.
- "Refuse at accept (Recommended)": a file outside a declared footprint stops
  acceptance; an undeclared footprint is reported and not refused.
- "Hold at freeze (Recommended)": the operator's parity reminder, near-parity if not
  full between a work package and an OBPI, amends that for a repair package. As a
  brief must carry valid Allowed Paths, `gz wp freeze` refuses a repair package with
  none and the same check holds a module. A package has no CREATE marker, so a new
  file is declared by its existing parent directory.

The ontology holds no work-package node, so reach is empty and the footprint is the
whole of the exit's fact vein.

Mode contract: the refusal is on at the operational condition and at both standby
levels, reading no marker, as the acceptance gate does: a repair under safe mode is
the case it exists for. MEL: (M) none, the governed recovery is the refusal's own
next step; no (O) limitation, placard or restore deadline; self-test
`tests/commands/test_wp_airlock.py`, every change that touches it; accepted state,
on. The bookings refuse nothing and are on at all three.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from gzkit.airlock.enter import enter_slice
from gzkit.airlock.exit import ExitReport, exit_slice
from gzkit.airlock.model import Preflight, TransitObservation, TransitSlice
from gzkit.config import GzkitConfig
from gzkit.governance.brief_path_validity import (
    check_brief_path_validity,
    vendor_mirror_canonical,
)
from gzkit.governance.trust_audits.catalog import footprint_breaches
from gzkit.hooks.obpi import (
    allow_pattern,
    out_of_scope_files,
    path_is_allowlisted,
    read_changed_files,
)
from gzkit.models.catalog import CATALOG_FILES
from gzkit.registries import registry_path
from gzkit.utils import git_cmd
from gzkit.work_package_ledger import declared_modules

if TYPE_CHECKING:
    from gzkit.ledger import Ledger
    from gzkit.models.catalog import WorkPackage

_LISTED = 10

#: How a footprint names a file that does not exist yet.
NEW_FILE_ROUTE = "a new file by its existing parent directory ending `/`"
_COMMIT_MARK = "\x00"


def _no_reach(_target: str) -> list[str]:
    return []


def _own_records(project_root: Path) -> tuple[str, ...]:
    """Read the paths the verbs themselves write: the store and the configured ledger.

    Returns:
        The store, the ledger and the ledger's lock, relative to the project root.

    """
    store = registry_path(project_root, CATALOG_FILES["work_packages"])
    config = GzkitConfig.load(project_root / ".gzkit.json")
    ledger = Path(config.paths.ledger).as_posix()
    return (store.relative_to(project_root).as_posix(), ledger, f"{ledger}.lock")


def _generated_mirrors(changed: tuple[str, ...], allowlist: tuple[str, ...]) -> tuple[str, ...]:
    """Read the changed vendor mirrors of files inside the footprint.

    A mirror cannot be declared, because a footprint names the canonical surface, and
    syncing regenerates it, so it follows its canonical file. A mirror of a file outside
    the footprint stays a finding.

    Returns:
        The mirrors the footprint already covers.

    """
    return tuple(
        path
        for path in changed
        if (canonical := vendor_mirror_canonical(path)) is not None
        and path_is_allowlisted(canonical, list(allowlist))
    )


def package_slice(
    package: WorkPackage,
    ledger: Ledger | None = None,
    project_root: Path | None = None,
    changed: tuple[str, ...] = (),
) -> TransitSlice:
    """Read the slice a package declares.

    Returns:
        Its footprint, read from *ledger* when given, with the verbs' own files exempt
        when *project_root* locates them and the mirrors of files it covers exempt.

    """
    modules = declared_modules(ledger, package) if ledger is not None else package.modules
    allowlist = tuple(allow_pattern(module) for module in modules)
    records = _own_records(project_root) if project_root is not None else ()
    return TransitSlice(
        target=package.id,
        declaration=" ".join(modules),
        bodies=modules,
        allowlist=allowlist,
        own_paths=(*records, *_generated_mirrors(changed, allowlist)),
        undeclared=not modules,
        must_observe=True,
    )


def package_changes(project_root: Path, work_package: str) -> TransitObservation | None:
    """Read what a package changed: its attributed commits and the uncommitted tree.

    The id's grammar is lowercase letters, digits and hyphens once lowered, so it
    needs no escaping in the pattern. A following hyphen or line end is what stops
    `wp-01-loop` matching `wp-01-loopback`. Rename detection is off, so a file moved
    out of a footprint shows the path it left, and paths are not quoted, so a
    non-ASCII path matches its pattern.

    Returns:
        The changes, or None when git cannot show them, so that nothing is claimed
        about what was not seen.

    """
    if not project_root.is_dir():
        return None
    pattern = rf"^Task:[[:space:]]+TASK-{work_package.lower()}(-|$)"
    rc, output, _ = git_cmd(
        project_root,
        "-c",
        "core.quotePath=false",
        "log",
        "--extended-regexp",
        f"--grep={pattern}",
        "--no-renames",
        "--name-only",
        "--format=%x00",
    )
    uncommitted = read_changed_files(project_root)
    if rc != 0 or uncommitted is None:
        return None
    committed = {
        line.strip().replace("\\", "/")
        for line in output.splitlines()
        if line.strip() and _COMMIT_MARK not in line
    }
    return TransitObservation(
        files=tuple(sorted(committed | set(uncommitted))),
        commits=output.count(_COMMIT_MARK),
    )


def enter_package(package: WorkPackage, ledger: Ledger, *, book: bool = True) -> Preflight:
    """Cross the airlock inward; `book` writes `airlock_in`, and a dry run does not.

    Returns:
        The preflight.

    """
    return enter_slice(
        package_slice(package, ledger),
        reach_fn=_no_reach,
        ledger=ledger if book else None,
    )


def exit_package(
    project_root: Path, package: WorkPackage, ledger: Ledger, *, book: bool = True
) -> ExitReport:
    """Cross the airlock outward; `book` writes `airlock_out`, and a dry run does not.

    Returns:
        The exit's report; it reports and never refuses.

    """
    observed = package_changes(project_root, package.id)
    changed = observed.files if observed else ()
    return exit_slice(
        package.id,
        lambda: package_slice(package, ledger, project_root, changed),
        reach_fn=_no_reach,
        ledger=ledger if book else None,
        observed=observed,
    )


def module_gaps(
    project_root: Path, modules: tuple[str, ...], changed: frozenset[str] = frozenset()
) -> list[str]:
    """Hold modules to the check a brief's Allowed Paths take (GHI #393).

    A path in *changed* is exempt from existing, as a brief's created path is: a file
    the package moved or deleted is gone, and it is still a path the package touched.
    A directory must end `/`, because the comparison reads the bare name as a file.

    Returns:
        A gap for each module that does not hold.

    """
    gaps = check_brief_path_validity(project_root, list(modules), set(changed))
    bare = (m for m in modules if not m.endswith("/") and (project_root / m).is_dir())
    return [*gaps, *(f"Allowed path is a directory and must end `/`: {m}" for m in bare)]


def freeze_refusal(project_root: Path, package: WorkPackage) -> str | None:
    """Say why a freeze is refused, or None when the footprint holds.

    A delivery package reads its outcome's `modules`, which RO-11 tranche 2 lands, so
    it declares nothing here. The store is read as the freeze will seal it, so the
    store's own rule runs too: an edit there must not reach the ledger.

    Returns:
        What failed, why and the governed next step, or None.

    """
    if package.kind == "delivery":
        return None
    why = "A repair package carries a valid footprint, as a brief carries Allowed Paths"
    order = (
        f"`uv run gz wp change {package.id} --rung change_order --approver operator --change "
        "<text> --superseded <text> --work-stopped"
    )
    if not package.modules:
        return (
            f"Repair package {package.id} declares no footprint. {why} (RO-14 ruling 24). "
            f"Add one with {order} --module <path>`, then freeze again."
        )
    gaps = [*footprint_breaches(package), *module_gaps(project_root, package.modules)]
    if gaps:
        return (
            f"{package.id}'s footprint does not hold: {'; '.join(gaps)}. {why} (RO-14 ruling "
            f"24). Replace each path with {order} --drop-module=<path> --module=<path>`, "
            f"naming {NEW_FILE_ROUTE}, then freeze again."
        )
    return None


def footprint_refusal(project_root: Path, package: WorkPackage, ledger: Ledger) -> str | None:
    """Say why acceptance is refused, or None when the footprint holds or is undeclared.

    Returns:
        What failed, why and the governed next step, or None.

    """
    if package_slice(package, ledger).undeclared:
        return None
    changes = package_changes(project_root, package.id)
    if changes is None:
        return (
            f"{package.id} declares a footprint and git cannot show what it changed, so "
            "the comparison cannot run. Delivered work is held against its declared scope "
            "(GHI #1185). Run `git status` here, repair what it reports, and accept again."
        )
    declared = package_slice(package, ledger, project_root, changes.files)
    outside = out_of_scope_files(
        list(changes.files), list(declared.allowlist), own_paths=list(declared.own_paths)
    )
    if not outside:
        return None
    listed = ", ".join(outside[:_LISTED])
    if len(outside) > _LISTED:
        listed += f" (+{len(outside) - _LISTED} more)"
    return (
        f"{len(outside)} changed file(s) outside {package.id}'s footprint: {listed}. Delivered "
        "work is held against its declared scope, as at `gz obpi complete` (GHI #1185, #1181). "
        "An uncommitted file that is not this package's work is committed under its own "
        "`Task:` trailer or reverted. A file already committed under this package's trailer "
        "stays in its history, and a revert does not remove it, so the operator adds it, the "
        "path as listed even if it is gone, or its directory ending `/` when the name holds "
        f"glob characters: `uv run gz wp change {package.id} --rung change_order --approver "
        "operator --change <text> --superseded <text> --work-stopped --module <path>`. Then "
        "accept again."
    )
