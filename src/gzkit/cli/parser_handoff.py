"""Subparser registrations for the ``gz handoff`` sub-command group.

Registers: handoff list, resume, create, decide, authorize (deprecated alias),
archive — the session-handoff lifecycle of ADR-0.0.65.

Extracted from ``parser_maintenance.py``, which breached its shrink-only
module-size ceiling. This family is what grew: the GHI #757 transit-decision
work added net +73 of the +85 overage.

The module name is load-bearing. ``gzkit.doc_coverage.scanner`` discovers CLI
verbs by globbing ``parser_*.py`` under ``src/gzkit/cli/`` and reading the
literal string argument of each ``add_parser`` call via AST. A module outside
that glob is invisible to manpage coverage, which is the same orphaning trap
recorded in ``_add_handoff_decide_arguments``' docstring below.

Command handlers are resolved on demand via ``_lazy`` so ``gz --help`` avoids
pulling heavy handler dependencies.
"""

from __future__ import annotations

import argparse

from gzkit.cli.helpers import (
    add_json_flag,
    build_epilog,
)
from gzkit.cli.parser_handler_manifest import _lazy


def _handoff_decide_description(verb: str) -> str:
    """Return the shared description for `decide` and its `authorize` alias."""
    return (
        "Record the operator's decision on a resumed handoff. A handoff "
        "ADVISES and gates nothing — the resume gate was retired 2026-08-15 "
        "(gz-session-handoff SKILL.md § RESUME); booking puts the ruling on "
        "Layer-2 so the decision has a record. This is an "
        "acknowledge-and-decide transit decision, NOT a completion "
        "attestation — ADR-0.0.33 reserves that register for completed "
        "planned work. --operator-text still carries the operator's VERBATIM "
        "words: never a paraphrase, and never words they did not say."
        + (" `authorize` is a deprecated alias for `decide`." if verb == "authorize" else "")
    )


def _handoff_decide_epilog(verb: str) -> str:
    """Return the shared epilog examples for `decide` and its `authorize` alias."""
    return build_epilog(
        [
            f"gz handoff {verb} --handoff .gzkit/handoffs/20260716T204012Z-work.md "
            '--session-id abc123 --operator-text "focus on handoff first"',
            f"gz handoff {verb} --handoff .gzkit/handoffs/20260716T204012Z-work.md "
            '--session-id abc123 --decision hold --operator-text "not yet"',
        ]
    )


def _add_handoff_decide_arguments(p: argparse.ArgumentParser) -> None:
    """Add the shared flag surface for `decide` and its `authorize` alias (GHI #757).

    The FLAGS are single-sourced because they are what drifts — a hand-copied
    second parser is exactly how a flag lands on one verb and not the other.
    The parser NAMES stay literal at the two call sites on purpose: the doc
    scanner (`gzkit.doc_coverage.scanner`) reads source via AST and extracts the
    string argument of `add_parser`, so a dynamically-named parser is invisible
    to manpage coverage. Registering both names through a loop variable silently
    dropped BOTH verbs from the audit's discovered set.
    """
    p.add_argument("--handoff", required=True, help="Resumed handoff the ruling covers")
    p.add_argument(
        "--operator-text",
        dest="operator_text",
        required=True,
        help="The operator's verbatim ruling words (never paraphrased)",
    )
    p.add_argument(
        "--session-id",
        dest="session_id",
        required=True,
        help="Harness session the ruling binds to (the gate's block message interpolates it)",
    )
    p.add_argument(
        "--decision",
        choices=("proceed", "pause", "hold", "revert"),
        default="proceed",
        help="Transit decision; only proceed lifts the gate (default: proceed)",
    )
    p.add_argument(
        "--set-aside",
        dest="set_aside",
        action="append",
        default=None,
        metavar="STEP",
        help="An advised step this ruling declines (repeatable); the amendment record",
    )
    add_json_flag(p)


def register_handoff_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the ``gz handoff`` sub-command group (ADR-0.0.65 OBPI-03)."""
    p_handoff = commands.add_parser(
        "handoff",
        help="Author and resume session handoffs through the validation gate",
        description=(
            "Create, list, and resume session handoffs. `create` routes authoring "
            "through the fail-closed validate_handoff_document gate; `list` and "
            "`resume` are read-only projections over .gzkit/handoffs/."
        ),
        epilog=build_epilog(
            [
                "gz handoff list",
                "gz handoff list --adr ADR-0.0.65 --json",
                "gz handoff resume --adr ADR-0.0.65",
                "gz handoff create --adr ADR-0.0.65 --slug my-work --agent g0 "
                '--decisions "Chose X over Y"',
            ]
        ),
    )
    handoff_sub = p_handoff.add_subparsers(dest="handoff_command")
    handoff_sub.required = True

    p_list = handoff_sub.add_parser(
        "list",
        help="List handoffs newest-first (optionally scoped by ADR)",
        description="List frontmatter-filtered handoffs newest-first.",
        epilog=build_epilog(["gz handoff list", "gz handoff list --adr ADR-0.0.65 --json"]),
    )
    p_list.add_argument("--adr", default=None, help="Scope the listing to one ADR id")
    add_json_flag(p_list)
    p_list.set_defaults(func=lambda a: _lazy("handoff_list_cmd")(adr=a.adr, as_json=a.as_json))

    p_resume = handoff_sub.add_parser(
        "resume",
        help="Resume the newest handoff for an ADR with staleness classification",
        description="Report the newest handoff for an ADR, its staleness, and first next step.",
        epilog=build_epilog(
            [
                "gz handoff resume --adr ADR-0.0.65",
                "gz handoff resume --adr ADR-0.0.65 --json",
            ]
        ),
    )
    p_resume.add_argument(
        "--adr",
        default=None,
        help="ADR id to resume the newest handoff for (omit for newest overall)",
    )
    add_json_flag(p_resume)
    p_resume.set_defaults(func=lambda a: _lazy("handoff_resume_cmd")(adr=a.adr, as_json=a.as_json))

    p_rulings = handoff_sub.add_parser(
        "rulings",
        help="Read the settled-ruling corpus carried across sessions",
        description=(
            "Read `.gzkit/handoffs/rulings.jsonl`, the append-only settled-ruling "
            "corpus. Rulings moved out of the handoff documents when they reached "
            "91.4% of them (GHI #838); a handoff now carries a count and a pointer, "
            "and this is the verb that reads what it points at. Read-only — rulings "
            "are booked by `gz handoff create` composing them from the predecessor."
        ),
        epilog=build_epilog(
            [
                "gz handoff rulings",
                "gz handoff rulings --limit 20",
                'gz handoff rulings --search "attest"',
                "gz handoff rulings --json",
            ]
        ),
    )
    p_rulings.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Show only the newest N rulings (default: all)",
    )
    p_rulings.add_argument(
        "--search",
        default=None,
        help="Show only rulings containing this text (case-insensitive)",
    )
    add_json_flag(p_rulings)
    p_rulings.set_defaults(
        func=lambda a: _lazy("handoff_rulings_cmd")(
            limit=a.limit, search=a.search, as_json=a.as_json
        )
    )

    p_create = handoff_sub.add_parser(
        "create",
        help="Author a handoff, fail-closed through the validation gate",
        description=(
            "Author a handoff document. The document is validated before it is "
            "written; on any violation nothing is written and the verb exits 1. "
            "All seven required sections must be populated: an unsupplied "
            "section is a refusal, not an empty heading (GHI #692)."
        ),
        epilog=build_epilog(
            [
                "gz handoff create --adr ADR-0.0.65 --slug my-work --agent g0 "
                '--summary "Landed X" --context "Y constrains Z" '
                '--decisions "Chose X over Y" --next-steps "1. Review W" '
                '--pending "GHI #123 open" --verification "uv run gz check" '
                '--evidence "`src/gzkit/x.py`"',
            ]
        ),
    )
    p_create.add_argument(
        "--adr",
        default=None,
        help="Parent ADR id (ADR-X.Y.Z); omit for work with no parent ADR",
    )
    p_create.add_argument("--slug", required=True, help="Filename slug for the handoff")
    p_create.add_argument("--agent", required=True, help="Authoring agent identity")
    p_create.add_argument("--decisions", required=True, help="Decisions Made section body")
    p_create.add_argument("--branch", default=None, help="Branch (default: current git branch)")
    p_create.add_argument("--summary", default=None, help="Current State Summary section body")
    p_create.add_argument("--context", default=None, help="Important Context section body")
    p_create.add_argument(
        "--next-steps", dest="next_steps", default=None, help="Immediate Next Steps section body"
    )
    p_create.add_argument("--pending", default=None, help="Pending Work / Open Loops section body")
    p_create.add_argument(
        "--verification", default=None, help="Verification Checklist section body"
    )
    p_create.add_argument("--evidence", default=None, help="Evidence / Artifacts section body")
    p_create.add_argument("--obpi", default=None, help="OBPI id this handoff scopes to")
    p_create.add_argument(
        "--continues-from",
        dest="continues_from",
        action="append",
        default=None,
        metavar="REF",
        help="Prior handoff reference (repeatable; repeat to collapse a forked chain)",
    )
    p_create.add_argument("--session-id", dest="session_id", default=None, help="Session id")
    p_create.add_argument(
        "--settled",
        action="append",
        default=None,
        metavar="RULING",
        help="Seat a late settled ruling (repeatable); unions with carried entries",
    )
    p_create.add_argument(
        "--mode",
        choices=("CREATE", "RESUME", "CHECKPOINT"),
        default="CREATE",
        help="Register-entry class; CHECKPOINT is a mid-flight bookmark, not a surrender",
    )
    add_json_flag(p_create)
    p_create.set_defaults(
        func=lambda a: _lazy("handoff_create_cmd")(
            adr=a.adr,
            slug=a.slug,
            agent=a.agent,
            decisions=a.decisions,
            settled=a.settled,
            branch=a.branch,
            summary=a.summary,
            context=a.context,
            next_steps=a.next_steps,
            pending=a.pending,
            verification=a.verification,
            evidence=a.evidence,
            obpi=a.obpi,
            continues_from=a.continues_from,
            session_id=a.session_id,
            mode=a.mode,
            as_json=a.as_json,
        )
    )

    # `decide` is the canonical verb (GHI #757); `authorize` is retained as an
    # alias because it is named across skills, runbooks, hook block prose, and
    # every handoff in the corpus. The flag surface is single-sourced through
    # `_add_handoff_decide_arguments`; the names are literal so the AST-based
    # doc scanner can still discover both.
    p_decide = handoff_sub.add_parser(
        "decide",
        help="Book the operator's transit decision on a resumed handoff",
        description=_handoff_decide_description("decide"),
        epilog=_handoff_decide_epilog("decide"),
    )
    _add_handoff_decide_arguments(p_decide)
    # `set_defaults` is repeated per verb rather than shared: the doc scanner
    # discovers a command only from a standalone `p_foo.set_defaults(func=...)`
    # whose lambda it can read via AST (`_handle_set_defaults`). Hoisting it
    # into the shared helper made both verbs undiscoverable and orphaned the
    # manpage. The flags — what actually drifts — stay single-sourced above.
    p_decide.set_defaults(
        func=lambda a: _lazy("handoff_authorize_cmd")(
            handoff=a.handoff,
            operator_text=a.operator_text,
            session_id=a.session_id,
            decision=a.decision,
            set_aside=a.set_aside,
            as_json=a.as_json,
        )
    )

    p_authorize = handoff_sub.add_parser(
        "authorize",
        help="Deprecated alias for `decide`",
        description=_handoff_decide_description("authorize"),
        epilog=_handoff_decide_epilog("authorize"),
    )
    _add_handoff_decide_arguments(p_authorize)
    p_authorize.set_defaults(
        func=lambda a: _lazy("handoff_authorize_cmd")(
            handoff=a.handoff,
            operator_text=a.operator_text,
            session_id=a.session_id,
            decision=a.decision,
            set_aside=a.set_aside,
            as_json=a.as_json,
        )
    )

    p_archive = handoff_sub.add_parser(
        "archive",
        help="Move handoffs older than a threshold into .gzkit/handoffs/archive/",
        description=(
            "Relocate (move-not-delete) handoffs older than --older-than into "
            ".gzkit/handoffs/archive/, honoring the lock-coupling, chain-integrity, "
            "and migration-floor guards. --dry-run reports the would-move set and "
            "mutates nothing."
        ),
        epilog=build_epilog(
            [
                "gz handoff archive --older-than 30d --dry-run",
                "gz handoff archive --older-than 30d",
            ]
        ),
    )
    p_archive.add_argument(
        "--older-than",
        dest="older_than",
        required=True,
        help="Age threshold, e.g. 30d — handoffs older than this are eligible",
    )
    p_archive.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Report the would-move set without moving anything",
    )
    add_json_flag(p_archive)
    p_archive.set_defaults(
        func=lambda a: _lazy("handoff_archive_cmd")(
            older_than=a.older_than,
            dry_run=a.dry_run,
            as_json=a.as_json,
        )
    )
