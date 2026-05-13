"""Surface-only refresh of .gzkit/<surface>/ from installed wheel package data.

Simpler than ``gz init --update``: no manifest mutation, no scaffolder hooks,
no agent sync. Just surface content refresh.
"""

import argparse
import sys

from gzkit.commands.common import console, get_project_root

# Re-export so tests can patch them at gzkit.commands.upgrade.*
from gzkit.commands.init_cmd import (
    _iter_canonical_surface_files,
    _refresh_one_artifact,
)

# Imported so test-isolation patches of this name succeed (REQ-0.0.32-14-08).
# This function is NEVER called by upgrade_cmd — see the invariant block below.
from gzkit.skills import scaffold_core_skills as scaffold_core_skills  # noqa: F401

KNOWN_SURFACES = ("skills", "rules", "templates", "personas", "hooks")

SURFACE_PKG_MAP: dict[str, str] = {
    "skills": "gzkit.skills",
    "rules": "gzkit.rules",
    "templates": "gzkit.templates",
    "personas": "gzkit.personas",
    "hooks": "gzkit.hooks",
}


def _validate_surfaces(raw: str) -> list[str] | None:
    """Parse and validate a comma-separated surface list.

    Returns the validated list, or calls ``sys.exit(1)`` if any token is
    unknown (printing the bad token to stdout before exiting).

    Returns ``None`` when the caller should use all surfaces (empty/None raw).
    """
    if not raw:
        return None
    tokens = [t.strip() for t in raw.split(",") if t.strip()]
    if not tokens:
        return None
    for token in tokens:
        if token not in KNOWN_SURFACES:
            print(f"Unknown surface: {token!r}. Known surfaces: {', '.join(KNOWN_SURFACES)}")
            sys.exit(1)
    return tokens


def _print_summary(
    *,
    identical: int,
    stale_refreshed: int,
    edited_conflicts: list[str],
    forced_overwrites: list[str],
    dry_run: bool,
) -> None:
    """Print a one-line upgrade summary."""
    prefix = "[dry-run] " if dry_run else ""
    parts = [f"{identical} identical", f"{stale_refreshed} refreshed"]
    if edited_conflicts:
        parts.append(f"{len(edited_conflicts)} EDITED (conflict)")
    if forced_overwrites:
        parts.append(f"{len(forced_overwrites)} force-overwritten")
    console.print(f"{prefix}Upgrade complete: {', '.join(parts)}.")
    if edited_conflicts:
        console.print("EDITED conflicts (not overwritten — use --force to override):")
        for path_str in edited_conflicts:
            console.print(f"  {path_str}")


def upgrade_cmd(args: argparse.Namespace) -> None:
    """Refresh .gzkit/<surface>/ from installed wheel package data."""
    surfaces = _validate_surfaces(args.surface or "")
    surfaces_to_process: list[str] = list(surfaces) if surfaces else list(KNOWN_SURFACES)

    project_root = get_project_root()

    identical = 0
    stale_refreshed = 0
    edited_conflicts: list[str] = []
    forced_overwrites: list[str] = []

    for surface in surfaces_to_process:
        pkg = SURFACE_PKG_MAP[surface]
        try:
            pairs = list(_iter_canonical_surface_files(pkg))
        except (ModuleNotFoundError, FileNotFoundError, AttributeError) as exc:
            console.print(f"Note: skipping surface {surface!r} ({exc})")
            continue

        for canonical, rel_path in pairs:
            project_path = project_root / ".gzkit" / surface / rel_path
            display = project_path.relative_to(project_root).as_posix()

            if args.dry_run:
                # Detect state without writing; still classify for the summary
                state = _refresh_one_artifact(
                    canonical=canonical,
                    project_path=project_path,
                    dry_run=True,
                )
                if state == "IDENTICAL":
                    identical += 1
                elif state == "STALE":
                    console.print(f"[dry-run] STALE: {display}")
                    stale_refreshed += 1
                elif state == "EDITED":
                    console.print(f"[dry-run] EDITED (conflict): {display}")
                    edited_conflicts.append(display)
            elif args.force:
                # Force path: detect state first, then emit overwrite line, then write.
                # Print BEFORE the write so output is recorded even if write fails in tests.
                state = _refresh_one_artifact(
                    canonical=canonical,
                    project_path=project_path,
                    dry_run=True,
                )
                if state in ("EDITED", "STALE"):
                    console.print(f"force overwrite ({state}): {display}")
                    forced_overwrites.append(display)
                    canonical_bytes = canonical.read_bytes()
                    project_path.parent.mkdir(parents=True, exist_ok=True)
                    project_path.write_bytes(canonical_bytes)
                else:
                    identical += 1
            else:
                # Normal path: refresh STALE, skip IDENTICAL, report EDITED
                state = _refresh_one_artifact(
                    canonical=canonical,
                    project_path=project_path,
                    dry_run=False,
                )
                if state == "IDENTICAL":
                    identical += 1
                elif state == "STALE":
                    stale_refreshed += 1
                elif state == "EDITED":
                    console.print(f"EDITED conflict (skipped): {display}")
                    edited_conflicts.append(display)

    _print_summary(
        identical=identical,
        stale_refreshed=stale_refreshed,
        edited_conflicts=edited_conflicts,
        forced_overwrites=forced_overwrites,
        dry_run=args.dry_run,
    )

    if edited_conflicts and not args.force:
        sys.exit(3)
    sys.exit(0)
