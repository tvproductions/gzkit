"""Flag inspection CLI commands (gz flags, gz flag explain).

Read-only inspection of the feature flag registry: list all flags with
resolved values, filter to stale flags, and explain individual flag state.

@covers ADR-0.0.8-feature-toggle-system
@covers OBPI-0.0.8-05-cli-surface
"""

from __future__ import annotations

import json
import sys
from datetime import date

from rich.table import Table

from gzkit.commands.common import console
from gzkit.flags import (
    UnknownFlagError,
    explain_flag,
    get_stale_flags,
    load_registry,
)
from gzkit.flags.service import FlagService


def _build_flag_service() -> FlagService:
    """Load registry and create a FlagService instance."""
    return FlagService(load_registry())


def _days_label(deadline: date, today: date) -> str:
    """Format a days-until string with Rich styling for overdue dates."""
    days = (deadline - today).days
    text = f"{days}d"
    if days < 0:
        return f"[red]{text}[/red]"
    return text


def flags_list_cmd(*, stale: bool = False, as_json: bool = False) -> None:
    """List all flags (or only stale flags) as a Rich table or JSON.

    When *stale* is True, only flags past their review_by or remove_by
    dates are shown.  An empty stale set prints "No stale flags." and
    exits 0.
    """
    svc = _build_flag_service()
    registry = svc._registry

    if stale:
        stale_specs = get_stale_flags(registry)
        if not stale_specs:
            if as_json:
                print(json.dumps([], indent=2), file=sys.stdout)  # noqa: T201
            else:
                console.print("No stale flags.")
            return
        keys = {s.key for s in stale_specs}
        evaluations = [svc.evaluate(k) for k in sorted(keys)]
    else:
        evaluations = svc.list_flags()

    today = date.today()

    if as_json:
        rows = []
        for ev in evaluations:
            spec = registry[ev.key]
            rows.append(
                {
                    "key": ev.key,
                    "category": spec.category.value,
                    "default": spec.default,
                    "current_value": ev.value,
                    "source": ev.source,
                    "owner": spec.owner,
                    "days_until_review": (spec.review_by - today).days if spec.review_by else None,
                    "days_until_removal": (spec.remove_by - today).days if spec.remove_by else None,
                }
            )
        print(json.dumps(rows, indent=2), file=sys.stdout)  # noqa: T201
        return

    title = "Feature Flags (stale only)" if stale else "Feature Flags"
    table = Table(title=title)
    table.add_column("Key")
    table.add_column("Category")
    table.add_column("Default")
    table.add_column("Value")
    table.add_column("Source")
    table.add_column("Owner")
    table.add_column("Review/Remove")

    for ev in evaluations:
        spec = registry[ev.key]
        parts: list[str] = []
        if spec.review_by:
            parts.append(f"review: {_days_label(spec.review_by, today)}")
        if spec.remove_by:
            parts.append(f"remove: {_days_label(spec.remove_by, today)}")
        days_str = ", ".join(parts) if parts else "-"

        table.add_row(
            ev.key,
            spec.category.value,
            str(spec.default),
            str(ev.value),
            ev.source,
            spec.owner,
            days_str,
        )

    console.print(table)


def flag_explain_cmd(*, key: str, as_json: bool = False) -> None:
    """Display full metadata for a single flag.

    Exits with code 1 when *key* is not in the registry.
    """
    svc = _build_flag_service()

    try:
        explanation = explain_flag(key, svc)
    except UnknownFlagError:
        console.print(f"[red]Unknown flag: {key!r}[/red]")
        raise SystemExit(1) from None

    spec = svc._registry[key]

    if as_json:
        data = explanation.model_dump()
        data["linked_adr"] = spec.linked_adr
        data["linked_issue"] = spec.linked_issue
        print(json.dumps(data, indent=2, default=str), file=sys.stdout)  # noqa: T201
        return

    console.print(f"\n[bold]{explanation.key}[/bold]")
    console.print(f"  Category:      {explanation.category}")
    console.print(f"  Description:   {explanation.description}")
    console.print(f"  Owner:         {explanation.owner}")
    console.print(f"  Default:       {explanation.default}")
    console.print(f"  Current value: {explanation.current_value}")
    console.print(f"  Source:        {explanation.source}")

    if explanation.review_by:
        style = "red" if (explanation.days_until_review or 0) < 0 else ""
        review_str = f"{explanation.review_by} ({explanation.days_until_review}d)"
        if style:
            console.print(f"  Review by:     [{style}]{review_str}[/{style}]")
        else:
            console.print(f"  Review by:     {review_str}")

    if explanation.remove_by:
        style = "red" if (explanation.days_until_removal or 0) < 0 else ""
        remove_str = f"{explanation.remove_by} ({explanation.days_until_removal}d)"
        if style:
            console.print(f"  Remove by:     [{style}]{remove_str}[/{style}]")
        else:
            console.print(f"  Remove by:     {remove_str}")

    if explanation.is_stale:
        console.print("  [red bold]STALE[/red bold]")

    if spec.linked_adr:
        console.print(f"  Linked ADR:    {spec.linked_adr}")
    if spec.linked_issue:
        console.print(f"  Linked issue:  {spec.linked_issue}")

    console.print()
