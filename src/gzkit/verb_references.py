"""One `gz <verb>` reference extractor and resolver, shared by every verb-checker.

gzkit carried two of these. ``hooks/obpi.py`` (GHI #194 / #432) read fenced
blocks, multi-word chains, and a speculative-skip marker; the operator-doc
checker in ``governance/trust_audits/cli.py`` read none of the three — and it
guarded the wider surface, the whole operator-doc corpus that
``.gzkit/rules/governance-core.md`` § Operator-doc verb resolution declares.

Each of the weaker copy's three gaps had already been filed separately (#745
fenced blocks, #588 multi-word, #748 the marker). That is the signature of **a
capability implemented correctly once and reimplemented weakly elsewhere**, and
patching the copy three times would leave the fourth gap to be found the same
way. This module is the convergence: both call sites extract and resolve here,
so the next gap is fixed once (GHI #748).

Two seams are deliberately parameters rather than constants:

* **Segments** — which prose contexts count as an invocation. Briefs quote
  commands in backticks; feature files carry them in quoted step fixtures.
  Sharing a core must not make either call site inherit the other's false
  positives, so the caller passes its own segment recognizers.
* **The parser** — :func:`verify_gz_chain` imports ``gzkit.cli.main`` lazily.
  The CLI imports governance surfaces, so a module-level import would close a
  cycle. This is the cycle-avoidance carve-out in ``.gzkit/rules/pythonic.md``
  § Imports, not a style lapse.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ANCHORED_INLINE_CODE",
    "BRIEF_SEGMENTS",
    "DOC_BARE_SEGMENTS",
    "DOC_SEGMENTS",
    "GZ_CHAIN_PATTERN",
    "INLINE_CODE",
    "QUOTED_INVOCATION",
    "SPECULATIVE_MARKER",
    "STEP_FIXTURE",
    "VerbReference",
    "extract_verb_references",
    "verify_gz_chain",
]

#: A ``(uv run )?gz <verb> [<verb>…]`` invocation. Whitespace is ``[ \t]`` — not
#: ``\s`` — so a chain can never span newlines: one prescribed command is one
#: line. Digits are admitted in verb tokens because the operator-doc checker has
#: always allowed them; the resolver, not the regex, decides what is real.
GZ_CHAIN_PATTERN = re.compile(
    r"(?:uv[ \t]+run[ \t]+)?\bgz[ \t]+([a-z][a-z0-9-]*(?:[ \t]+[a-z][a-z0-9-]*)*)",
)

#: Speculative-skip marker. ONE marker across every governed verb-checker: the
#: suppression means the same thing everywhere ("this names a planned surface
#: that cannot resolve yet"), and a per-checker token would make the recovery
#: `governance-core.md` promises depend on which validator happened to fire.
#: Mirrors the shape in ``complexity_doctrine_links.py`` (GHI #432).
SPECULATIVE_MARKER = "<!-- gz-validate-skip: command-shape -->"

#: Prose contexts whose captured text CONTAINS a full `gz …` invocation. Briefs
#: embed commands mid-span (``\`then run gz obpi complete\```), so the whole
#: span is scanned.
INLINE_CODE = re.compile(r"`([^`\n]+)`")
#: The same context, anchored. Operator docs put output TEMPLATES in backticks
#: — ``\`Filed from <slug> running gz vX.Y.Z\``` — where a mid-span scan reads
#: the version literal `vX.Y.Z` as a verb `v`. Requiring the span to open with
#: the command separates a prescribed invocation from a rendered string.
ANCHORED_INLINE_CODE = re.compile(r"`((?:uv[ \t]+run[ \t]+)?gz[ \t][^`\n]*)`")
#: A quoted string is an invocation only when it OPENS with the command. Without
#: that anchor, `"…running gz v"` in a `.feature` assertion reads as a reference
#: to a verb `v` — six such false hits in `features/` on the first corpus run.
QUOTED_INVOCATION = re.compile(r'"((?:uv[ \t]+run[ \t]+)?gz[ \t][^"\n]*)"')

#: Behave step fixtures whose captured text IS a bare chain — no `gz` prefix.
#: `When I run the gz command "justify GHI-232"` puts the verb in the step name,
#: not in the quotes. A recognizer that required a literal `gz` inside the quotes
#: would match nothing and drop every `.feature` file from the audit silently.
STEP_FIXTURE = re.compile(r'the gz command\s+"([^"\n]+)"')

#: Briefs quote commands in backticks only — prose mentions are descriptive.
#: Unanchored: a brief's inline span is authored prose wrapping a real command.
BRIEF_SEGMENTS: tuple[re.Pattern[str], ...] = (INLINE_CODE,)
#: Operator docs carry rendered output alongside commands, so both delimited
#: contexts are anchored. This is not a weaker check — it is the same check on a
#: corpus that contains strings the brief corpus does not.
DOC_SEGMENTS: tuple[re.Pattern[str], ...] = (ANCHORED_INLINE_CODE, QUOTED_INVOCATION)
#: `.feature` step fixtures, whose capture is already a bare chain.
DOC_BARE_SEGMENTS: tuple[re.Pattern[str], ...] = (STEP_FIXTURE,)

_FENCE_DELIMITER = re.compile(r"^(?:```|~~~)")

#: A fenced line is a COMMAND when it opens with the invocation, optionally
#: behind a transcript `$ ` prompt or the canonical `uv run`. Fenced blocks in
#: operator docs carry captured output as often as commands, and scanning output
#: for `gz <word>` reads ordinary English ("no file mutation / gz ceremony /
#: migration") as a prescribed verb. Anchoring picks the command lines; scanning
#: the whole of such a line still catches a second invocation after `&&`.
_COMMAND_LINE = re.compile(r"^[ \t]*(?:\$[ \t]*)?(?:uv[ \t]+run[ \t]+)?gz[ \t]")
_VERB_TOKEN = re.compile(r"^[a-z][a-z0-9-]*$")


class VerbReference(BaseModel):
    """One extracted ``gz`` invocation and where it was written."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    chain: tuple[str, ...] = Field(..., description="Verb tokens after `gz`, in order")
    lineno: int = Field(..., description="1-indexed line the reference was found on")


def _chains_in(text: str) -> list[tuple[str, ...]]:
    """Return every ``gz`` chain in one already-narrowed span of text."""
    return [tuple(match.group(1).split()) for match in GZ_CHAIN_PATTERN.finditer(text)]


def _leading_verb_tokens(text: str) -> tuple[str, ...]:
    """Read a bare chain's leading verb tokens, stopping at the first argument.

    ``"justify --draft 'pre-decision text'"`` yields ``("justify",)`` — flags,
    ids, and quoted text are arguments, and only the verb prefix is resolvable.
    """
    chain: list[str] = []
    for token in text.split():
        if not _VERB_TOKEN.match(token):
            break
        chain.append(token)
    return tuple(chain)


def extract_verb_references(
    content: str,
    *,
    segments: Sequence[re.Pattern[str]] = BRIEF_SEGMENTS,
    bare_segments: Sequence[re.Pattern[str]] = (),
) -> list[VerbReference]:
    """Extract every prescriptive ``gz <verb> [<verb>…]`` reference from markdown.

    Inside a fenced block the delimiter-bound recognizers cannot fire — fenced
    commands carry no per-command backticks and no quotes — so a line that
    *opens* with the invocation is scanned whole. Outside one, only text matched
    by ``segments`` (which contains a full ``gz …``) or ``bare_segments`` (whose
    capture is already a chain) is scanned, so prose that merely mentions a verb
    is not read as prescribing it.

    :data:`SPECULATIVE_MARKER` on its own line suppresses the reference that
    follows: the next line when that line is prose, or the entire block when the
    next line opens a fence.
    """
    references: list[VerbReference] = []
    in_fence = False
    skip_block = False
    pending_marker = False

    for lineno, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()

        if _FENCE_DELIMITER.match(stripped):
            if in_fence:
                in_fence = False
                skip_block = False
            else:
                in_fence = True
                skip_block = pending_marker
            pending_marker = False
            continue

        if in_fence:
            if not skip_block and _COMMAND_LINE.match(line):
                references.extend(
                    VerbReference(chain=chain, lineno=lineno) for chain in _chains_in(line)
                )
            continue

        if stripped == SPECULATIVE_MARKER:
            pending_marker = True
            continue

        if pending_marker:
            pending_marker = False
            continue

        for pattern in segments:
            for segment in pattern.finditer(line):
                references.extend(
                    VerbReference(chain=chain, lineno=lineno)
                    for chain in _chains_in(segment.group(1))
                )
        for pattern in bare_segments:
            for segment in pattern.finditer(line):
                chain = _leading_verb_tokens(segment.group(1))
                if chain:
                    references.append(VerbReference(chain=chain, lineno=lineno))
    return references


def verify_gz_chain(verbs: Sequence[str]) -> tuple[bool, str]:
    """Walk a verb chain through the live ``gz`` parser tree.

    Returns ``(ok, reason)``. The walk advances through subparser levels; when
    the current level has no further subparsers (a leaf verb), the remaining
    tokens are treated as positional arguments — e.g. ``gz chores run
    frontmatter-ledger-coherence`` resolves at ``run`` and the slug is a
    positional. Verbs at intermediate levels MUST be registered choices, so
    typos fail closed.
    """
    import argparse  # noqa: PLC0415

    from gzkit.cli.main import _get_parser  # noqa: PLC0415

    current: argparse.ArgumentParser = _get_parser()
    walked: list[str] = []
    for verb in verbs:
        sub_action = next(
            (a for a in current._actions if isinstance(a, argparse._SubParsersAction)),  # noqa: SLF001
            None,
        )
        if sub_action is None:
            # Current parser is a leaf; remaining tokens are positional args.
            return True, f"resolved 'gz {' '.join(walked)}'"
        if verb not in sub_action.choices:
            return False, _unregistered_reason(verb, walked, sorted(sub_action.choices))
        walked.append(verb)
        # argparse _SubParsersAction.choices values are ArgumentParser at runtime
        # but the stub types them as object; safe cast based on the isinstance above.
        next_parser = sub_action.choices[verb]
        if not isinstance(next_parser, argparse.ArgumentParser):
            return True, f"resolved 'gz {' '.join(walked)}' (leaf choice)"
        current = next_parser
    return True, f"resolved 'gz {' '.join(walked)}'"


def _unregistered_reason(verb: str, walked: list[str], available: list[str]) -> str:
    """Build the three-part failure prose for an unregistered verb.

    Near-matches lead the sample so the likely-intended verb (e.g. the plural
    `chores` for a `chore` typo) always appears even when the list is truncated.
    Prefix overlap is checked in both directions.
    """
    near = [v for v in available if v.startswith(verb[:3]) or verb.startswith(v[:3])]
    ordered = near + [v for v in available if v not in near]
    sample = ", ".join(ordered[:8])
    suffix = "..." if len(available) > 8 else ""
    prefix = f"'gz {' '.join(walked)}'" if walked else "'gz'"
    return (
        f"{prefix} — '{verb}' is not a registered subcommand at "
        f"this level (available: {sample}{suffix})"
    )
