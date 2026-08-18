"""gz content subparser registrations.

Registers the `gz content` subcommand group with the `import` verb.

ADR-0.0.34 § Decision item #3 — reverse-parse migration tooling.
"""

from __future__ import annotations

import argparse
from typing import Any


def _build_epilog(examples: list[str]) -> str:
    from gzkit.cli.helpers import build_epilog  # noqa: PLC0415

    return build_epilog(examples)


def _content(module_name: str, attr_name: str) -> Any:
    """Resolve a content command handler lazily from gzkit.commands.content.<module_name>."""
    from importlib import import_module  # noqa: PLC0415

    module = import_module(f"gzkit.commands.content.{module_name}")
    return getattr(module, attr_name)


def register_content_parsers(commands: argparse._SubParsersAction) -> None:
    """Register the ``gz content`` sub-command group."""
    p_content = commands.add_parser(
        "content",
        help="Content model import and management commands",
        description=(
            "Commands for importing hand-authored markdown files into canonical "
            "Pydantic content models. Part of the ADR-0.0.34 rendering substrate."
        ),
        epilog=_build_epilog(
            [
                "gz content import AGENTS.md --as AgentContract",
                "gz content import .gzkit/rules/tests.md --as Rule --write /tmp/out.md",
                "gz content list",
            ]
        ),
    )
    content_commands = p_content.add_subparsers(dest="content_command")
    content_commands.required = True

    _register_import(content_commands)
    _register_list(content_commands)
    _register_show(content_commands)
    _register_render(content_commands)
    _register_edit(content_commands)
    _register_remember(content_commands)
    _register_retire(content_commands)
    _register_compose(content_commands)
    _register_commit(content_commands)
    _register_advise_rendition(content_commands)


def _register_import(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "import",
        help="Import a markdown file into a canonical content model",
        description=(
            "Read a hand-authored or canonical markdown file, parse it into a Pydantic "
            "content model instance, and emit JSON to stdout. "
            "Use --write to persist a re-rendered canonical form."
        ),
        epilog=_build_epilog(
            [
                "gz content import AGENTS.md --as AgentContract",
                "gz content import .gzkit/rules/tests.md --as Rule",
                "gz content import AGENTS.md --as AgentContract --write /tmp/agents-canonical.md",
            ]
        ),
    )
    p.add_argument("file", help="Path to the markdown file to import.")
    p.add_argument(
        "--as",
        dest="as_type",
        required=True,
        help="Content type name (e.g. AgentContract, Rule, Skill).",
    )
    p.add_argument(
        "--write",
        dest="write_path",
        default=None,
        help="Write re-rendered canonical form to this path.",
    )
    p.set_defaults(
        func=lambda a: _content("import_", "content_import_cmd")(
            file=a.file,
            as_type=a.as_type,
            write_path=a.write_path,
        )
    )


def _register_list(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "list",
        help="List registered content model types",
        description=(
            "List the registered content model types from the CONTENT_MODELS registry. "
            "Default output is a human-readable table; use --json for machine consumption."
        ),
        epilog=_build_epilog(
            [
                "gz content list",
                "gz content list --type Rule",
                "gz content list --json",
            ]
        ),
    )
    p.add_argument(
        "--type",
        dest="type_filter",
        default=None,
        help="Filter to a specific content type (e.g. Rule, Skill).",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit JSON to stdout instead of a human-readable table.",
    )
    p.add_argument(
        "--plain",
        dest="plain",
        action="store_true",
        help="Force plain text output even on a TTY (disables Rich table).",
    )
    p.set_defaults(
        func=lambda a: _content("list", "content_list_cmd")(
            type_filter=a.type_filter,
            as_json=a.as_json,
            plain=a.plain,
        )
    )


def _register_show(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "show",
        help="Show a prose summary of a content model file",
        description=(
            "Parse a canonical content file and display a human-readable prose summary. "
            "Use --json for machine consumption."
        ),
        epilog=_build_epilog(
            [
                "gz content show AGENTS.md --as AgentContract",
                "gz content show .gzkit/rules/tests.md --as Rule --json",
            ]
        ),
    )
    p.add_argument("file", help="Path to the markdown file to inspect.")
    p.add_argument(
        "--as",
        dest="as_type",
        required=True,
        help="Content type name (e.g. AgentContract, Rule, Skill).",
    )
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit JSON to stdout instead of prose summary.",
    )
    p.add_argument(
        "--plain",
        dest="plain",
        action="store_true",
        help="Force plain text output even on a TTY (disables Rich panel).",
    )
    p.set_defaults(
        func=lambda a: _content("show", "content_show_cmd")(
            file=a.file,
            as_type=a.as_type,
            as_json=a.as_json,
            plain=a.plain,
        )
    )


def _register_render(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "render",
        help="Render a content model file to canonical markdown",
        description=(
            "Parse a canonical content file and emit the rendered markdown to stdout. "
            "Output is byte-identical to gzkit.content.render.render(model, vendor)."
        ),
        epilog=_build_epilog(
            [
                "gz content render AGENTS.md --as AgentContract",
                "gz content render .gzkit/rules/tests.md --as Rule --vendor claude",
            ]
        ),
    )
    p.add_argument("file", help="Path to the markdown file to render.")
    p.add_argument(
        "--as",
        dest="as_type",
        required=True,
        help="Content type name (e.g. AgentContract, Rule, Skill).",
    )
    p.add_argument(
        "--vendor",
        dest="vendor",
        default="claude",
        help="Target vendor template (default: claude).",
    )
    p.set_defaults(
        func=lambda a: _content("render", "content_render_cmd")(
            file=a.file,
            as_type=a.as_type,
            vendor=a.vendor,
        )
    )


def _register_edit(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "edit",
        help="Edit a content model file via $EDITOR with re-validation",
        description=(
            "Open the content model file in $EDITOR (or $VISUAL). On editor save, "
            "re-parse and re-validate the edited content. Invalid input aborts with "
            "the validator diagnostic; the original file is never partially written."
        ),
        epilog=_build_epilog(
            [
                "gz content edit AGENTS.md --as AgentContract",
                "gz content edit .gzkit/rules/tests.md --as Rule --vendor claude",
            ]
        ),
    )
    p.add_argument("file", help="Path to the markdown file to edit.")
    p.add_argument(
        "--as",
        dest="as_type",
        required=True,
        help="Content type name (e.g. AgentContract, Rule, Skill).",
    )
    p.add_argument(
        "--vendor",
        dest="vendor",
        default="claude",
        help="Target vendor template for re-rendering on save (default: claude).",
    )
    p.set_defaults(
        func=lambda a: _content("edit", "content_edit_cmd")(
            file=a.file,
            as_type=a.as_type,
            vendor=a.vendor,
        )
    )


def _register_remember(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "remember",
        help="Append an addressed entry to a surface's append-only corpus store",
        description=(
            "Append one addressed, provenanced entry to the append-only corpus store at "
            ".gzkit/corpus/<surface>.jsonl and emit a corpus_entry_appended ledger event. "
            "NEVER edits a rendered surface (AGENTS.md, CLAUDE.md, mirrors) — capture writes "
            "the source of truth; deterministic playback is the sole writer of rendered "
            "surfaces. Fails closed when the surface is unknown or --section resolves to no "
            "template-defined section of that surface."
        ),
        epilog=_build_epilog(
            [
                'gz content remember AGENTS.md --section "Behavior Rules" '
                '--text "Prefer stdlib JSONL for append-only stores."',
                "gz content remember AGENTS.md --section prime-directive "
                '--text "YOU OWN THE WORK COMPLETELY." --tier invariant',
            ]
        ),
    )
    p.add_argument("surface", help="Control surface to capture against (e.g. AGENTS.md).")
    p.add_argument(
        "--section",
        required=True,
        help="Target section id or title; normalized to the surface's kebab-case Pillar id.",
    )
    p.add_argument("--text", required=True, help="The entry prose to remember.")
    p.add_argument(
        "--tier",
        choices=["invariant", "compressible"],
        default="compressible",
        help="invariant = verbatim at every setpoint; compressible = condensable (default).",
    )
    p.add_argument(
        "--classification",
        choices=["Mechanical", "Promotable", "Judgment", "Ambiguous"],
        default="Ambiguous",
        help="Advisory-scorecard class for the entry (default: Ambiguous).",
    )
    p.add_argument(
        "--origin",
        default="cli:content-remember",
        help="HOW the capture arrived, e.g. a GHI or session id.",
    )
    p.add_argument(
        "--witness",
        default="",
        help="WHO vouches for this entry; recorded provenance, never a gate.",
    )
    p.set_defaults(
        func=lambda a: _content("remember", "content_remember_cmd")(
            surface=a.surface,
            section=a.section,
            text=a.text,
            tier=a.tier,
            classification=a.classification,
            origin=a.origin,
            witness=a.witness,
        )
    )


def _register_retire(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "retire",
        help="Retire a superseded corpus entry via an append-only retraction",
        description=(
            "Append a retraction row naming a superseded entry id, and emit a "
            "corpus_entry_retired ledger event. Nothing is deleted — the retired entry "
            "stays on disk with its provenance — but it stops binding the invariant "
            "floor, so a rendition no longer has to carry its text verbatim. Retirement "
            "only ever shrinks the floor, so committed renditions stay valid and no "
            "recomposition is implied. Fails closed on an unknown or already-retired id."
        ),
        epilog=_build_epilog(
            [
                "gz content retire AGENTS.md --entry corpus-prime-directive-2026-06-13T12:34:39 "
                '--reason "superseded by the 2026-06-19 single-quote canon entry"',
            ]
        ),
    )
    p.add_argument("surface", help="Control surface the entry belongs to (e.g. AGENTS.md).")
    p.add_argument("--entry", required=True, help="Id of the corpus entry to retire.")
    p.add_argument(
        "--reason",
        required=True,
        help="Why the entry is superseded; stored as the retraction row's text.",
    )
    p.add_argument(
        "--origin",
        default="cli:content-retire",
        help="Provenance of the retirement, e.g. a GHI or session id.",
    )
    p.set_defaults(
        func=lambda a: _content("retire", "content_retire_cmd")(
            surface=a.surface,
            entry_id=a.entry,
            reason=a.reason,
            origin=a.origin,
        )
    )


def _register_compose(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "compose",
        help="Validate and stage a candidate rendition from the corpus",
        description=(
            "Accept an agent-supplied candidate rendition, validate invariant-tier "
            "verbatim preservation, compute per-tier byte evidence, write the candidate "
            "to .gzkit/renditions/<surface>/<consumer>.candidate.md, and emit a "
            "composition_candidate_emitted ledger event. "
            "The tool is deterministic: NO LLM call, NO network I/O. "
            "The compression judgment (drop/combine/rewrite) is the agent's. "
            "NEVER writes a rendered surface (AGENTS.md, CLAUDE.md, mirrors)."
        ),
        epilog=_build_epilog(
            [
                "gz content compose AGENTS.md --consumer codex --candidate /tmp/candidate.md",
                "gz content compose AGENTS.md --consumer claude --candidate /tmp/candidate.md",
            ]
        ),
    )
    p.add_argument("surface", help="Control surface to compose for (e.g. AGENTS.md).")
    p.add_argument(
        "--consumer",
        required=True,
        help="Target vendor consumer (e.g. codex, claude).",
    )
    p.add_argument(
        "--candidate",
        default=None,
        help="Path to the candidate rendition file (reads from stdin when omitted).",
    )
    p.set_defaults(
        func=lambda a: _content("compose", "content_compose_cmd")(
            surface=a.surface,
            consumer=a.consumer,
            candidate=a.candidate,
        )
    )


def _register_commit(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "commit",
        help="Promote a staged candidate to the committed rendition under attestation",
        description=(
            "Promote the staged candidate rendition "
            "(.gzkit/renditions/<surface>/<consumer>.candidate.md) to the durable committed "
            "rendition (<consumer>.md), freeze the corpus content-fingerprint in a provenance "
            "sidecar (<consumer>.corpus.json), and emit a rendition_committed ledger event. "
            "Operator-attested (corpus attestation, NOT Gate 5): --attestor and "
            "--attestation-text fail closed when empty IF the corpus moved since this "
            "consumer's last committed rendition; a re-render of UNCHANGED canon needs "
            "none and carries the standing attestation forward (GHI #821) — attestation "
            "attaches to the canon change, never to this Layer-3 re-render. The frozen "
            "fingerprint is what `gz validate --rendition-freshness` checks the corpus against."
        ),
        epilog=_build_epilog(
            [
                "gz content commit AGENTS.md --consumer codex "
                '--attestor "g0" --attestation-text "attest completed"',
                "gz content commit AGENTS.md --consumer claude "
                '--attestor "g0" --attestation-text "recompose attested"',
            ]
        ),
    )
    p.add_argument("surface", help="Control surface to commit for (e.g. AGENTS.md).")
    p.add_argument(
        "--consumer",
        required=True,
        help="Target vendor consumer (e.g. codex, claude).",
    )
    p.add_argument(
        "--attestor",
        default="",
        help="Operator attesting the corpus delta; required only if canon moved.",
    )
    p.add_argument(
        "--attestation-text",
        dest="attestation_text",
        default="",
        help="Operator's verbatim corpus-attestation token; same conditional requirement.",
    )
    p.set_defaults(
        func=lambda a: _content("commit", "content_commit_cmd")(
            surface=a.surface,
            consumer=a.consumer,
            attestor=a.attestor,
            attestation_text=a.attestation_text,
        )
    )


def _register_advise_rendition(content_commands: argparse._SubParsersAction) -> None:
    p = content_commands.add_parser(
        "advise-rendition",
        help="Record an advisory info-retained-per-byte verdict for a candidate rendition",
        description=(
            "Record an agent-supplied advisor-QC verdict (information-retained-per-byte) "
            "for a candidate rendition as an ARB receipt the operator cites at Gate 5. "
            "The tool is deterministic: NO LLM call, NO network I/O — the judgment is the "
            "wielding gz-advisor-qc skill's (the agent's). It is ADVISORY, NEVER gating: any "
            "score is recorded and the command exits 0 (ADR-0.0.39 Evidentiary invariant). "
            "The only non-zero exit is a malformed verdict (empty --explanation), which "
            "writes no receipt — explanation-before-verdict is the receipt-shape contract."
        ),
        epilog=_build_epilog(
            [
                "gz content advise-rendition AGENTS.md --consumer codex --score 0.94 "
                '--explanation "All Mechanical bullets retained; two Promotable combined."',
                "gz content advise-rendition CLAUDE.md --score 0.6 "
                '--explanation "One Judgment bullet compressed with measurable loss."',
            ]
        ),
    )
    p.add_argument("surface", help="Control surface scored (e.g. AGENTS.md).")
    p.add_argument(
        "--consumer",
        default=None,
        help="Target vendor consumer (e.g. codex, claude). Omit for surface-wide scoring.",
    )
    p.add_argument(
        "--score",
        required=True,
        type=float,
        help="Information-retained-per-byte verdict value (advisory; never gates).",
    )
    p.add_argument(
        "--explanation",
        required=True,
        help="Advisor reasoning, recorded before the verdict; empty fails closed.",
    )
    p.set_defaults(
        func=lambda a: _content("advise_rendition", "content_advise_rendition_cmd")(
            surface=a.surface,
            consumer=a.consumer,
            explanation=a.explanation,
            score=a.score,
        )
    )
