"""Function and module size are cited from the threshold table, never restated (GHI #1366).

`.gzkit/rules/pythonic.md` § Size Limits: function and module size are the
`lizard_nloc` and `lizard_file_nloc` bands of `.gzkit/rules/complexity-thresholds.json`,
"Cite the table, never a number copied from it" (operator, 2026-11-13, RP-7 H2).
When the table moved off the old numbers, the skills, a persona, a pool ADR and
twenty-seven docstrings kept restating them as the rule. This scope refuses a
restated number on every live surface it reads.

It reads prose, not code: a Markdown or JSONL file is split into blocks (paragraphs,
list items, table rows, headings), a Python file into its strings and comment runs,
and each block into sentences with whitespace collapsed, so a phrase wrapped across
lines is still seen. Underscore emphasis is dropped, and a code span is also read
alone, so a quoted bound followed by a word ("`Modules <=N` while") is still seen.

The test is proximity, not a phrasing list (#1367 review: an enumerated list kept
missing natural wordings). A sentence states a size limit when, inside one clause:

- a function, method, module or file is followed within sixty characters by a
  number and a line unit ("keep functions to N lines", "the module size limit is N
  lines", "split any function that reaches N lines of code", "no file should
  exceed N lines");
- a number and a line unit are followed within twenty characters, no bracket or dash
  between, by a function, method or module ("the N-line module cap", "a N LOC
  module", "N lines per function");
- any of the four is followed directly (after an optional "length", "size" or
  "body") by a symbol and a number ("functions >N get split", "file length <= N"), or
  by a comparison word and a number that ends the phrase or carries a unit ("files
  over N lines").

A file is not a subject after a number ("N lines across M files" counts a change),
nor as a path part, a placeholder, or an instruction, rule or skill file, whose
budget is in characters. Numbers count as digits (with "k" or "+"), or spelled out
("fifteen", "forty-five", "six hundred", "a thousand"); "e.g." and "i.e." split no
sentence. Not a limit: a subject naming what code prints ("module output", "function
logs") or a unit counting it ("N lines of log output"); a size attached to "this",
"that", "these", "those", "its" or "their", which names one measured unit ("this
87-line function"), unless a comparison or limit word makes the number a bound ("its
N-line cap"); a match is exempt only when every size in it is so attached, so a
separate limit beside a measured unit is still refused. A demonstrative before the
subject exempts nothing ("keep these
modules to N lines" is a limit). Classes stay out of scope, because `pythonic.md` owns
that one number itself. A general measurement ("the module is about N lines") is
refused like a limit; cite the measurement's source or date it.

Dated history passes only in an anchored form inside the same sentence: "then in
force", "then in" a path to `pythonic.md`, "at the time" closing a parenthesis,
"until" a commit hash, or
an ISO date followed by "census". A bare "then" is not history, so a conditional
("if ... then split it") is refused (#1367 F3). Dated records stay as written and are
not read: any path part carrying an ISO date, the `harbor-` records and the two
governance records the #1366 re-review placed in its boundary, chore proofs and
archives.

The pool ADRs are not read, by operator ruling on #1367 (2026-11-28, verbatim: "the
pool adr will be phased out and drained into the requirements catalog/backlog, why
bother? so much of what we are doing now is related to what we are trying to achieve
in the dry dock").

What it does not judge: a limit phrased with no number, a subject and size further
apart than the windows above or split across table cells, a sentence split by an
f-string placeholder, or a sentence a placeholder expression would complete. Reword
such a sentence to cite the table rather than widen the fence.

It began as the unit test `tests/policy/test_size_limits_cite_the_table.py`, which
the tautology audit classed as a content echo; under the operator's ruling on #1370
("A") it is this scope, and #1367 widened its phrasings, roots and history allowance.
"""

import io
import re
import tokenize
from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.prose_fence import live_files, missing_roots

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

_TYPE = "size_limit_citations"
_PREFIX = "[size-limit-citations]"
_SCOPE = "size-limit-citations"

ROOTS = (
    ".gzkit/skills",
    ".gzkit/rules",
    ".gzkit/personas",
    ".gzkit/agents",
    ".gzkit/templates",
    ".gzkit/chores",
    ".gzkit/corpus",
    "docs/user",
    "docs/governance",
    "src/gzkit",
)
ROOT_FILES = ("AGENTS.md", "CLAUDE.md", "README.md")
SUFFIXES = (".md", ".py", ".jsonl")
SKIPPED_PARTS = ("proofs", "archive")
#: A path part naming a dated record: an ISO date, or a drydock `harbor-` record.
DATED_RECORD = re.compile(r"\d{4}-\d{2}-\d{2}|^harbor-")
#: Dated records with no date in their name, from the #1366 re-review's boundary.
DATED_RECORD_FILES = (
    "docs/governance/rule-version-history.md",
    "docs/governance/rules-tools-audits-refactors-alignment.md",
)
#: The authority itself names its bands' numbers.
_AUTHORITY = "complexity-thresholds"

_UNITS_WORD = r"(?:one|two|three|four|five|six|seven|eight|nine)"
_SPELLED = (
    rf"(?:{_UNITS_WORD}[- ](?:hundred|thousand)|a (?:hundred|thousand)"
    rf"|(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[- ]{_UNITS_WORD})?"
    r"|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen"
    r"|hundred|thousand)"
)
_NUM = rf"(?:\d+(?:,\d{{3}})*(?!,?\d)(?:k\b)?\+?|{_SPELLED})"
_UNIT = r"(?:lines?|LOC|NLOC|SLOC)"
_SIZE = rf"(?<![\w-]){_NUM}[- ]?{_UNIT}\b"
#: A file names a module, except as a count ("M files"), a path or a placeholder.
_FILE = r"(?<![<\w/.-])(?<!\d )(?<!instruction )(?<!rule )(?<!skill )files?"
_SUBJECT = r"\b(?:functions?|modules?|methods?)\b"
_FORWARD_SUBJECT = rf"(?:\b(?:functions?|modules?|methods?)|{_FILE})\b"
_COMPARE = (
    r"(?:\bover\b|\bexceed\w*|\bunder\b|\bmax(?:imum)?\b|\bat most\b|\bup to\b"
    r"|\bfits? in\b|\b(?:longer|shorter|larger|bigger|more|fewer|less) than\b"
    r"|\babove\b|\bbeyond\b|\bpast\b|\bbelow\b|\bwithin\b|\babout\b|\baround\b"
    r"|\broughly\b|~|\b(?:length|size|limit|cap|ceiling)\s*:)"
)
_SYMBOL = r"(?:>=?|≥|<=?|≤)"
#: A bare number after a comparison word is a size only when the phrase ends there
#: ("over 5 parameters" is not); after a symbol any word may follow ("> N get split").
_BARE_END = r"(?=\s*(?:[,;:)|]|\.(?=\s|$)|$|\band\b|\bor\b))"
_HEAD = rf"{_FORWARD_SUBJECT}\s*(?:(?:length|size|bod(?:y|ies))\s*)?"
PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        rf"{_FORWARD_SUBJECT}[^.;|]{{0,60}}?{_SIZE}",
        rf"{_SIZE}[^.;|()\u2014\u2013]{{0,20}}?{_SUBJECT}",
        rf"{_HEAD}{_SYMBOL}\s*{_NUM}\b(?![>&%])",
        rf"{_HEAD}{_COMPARE}\s*(?:{_SIZE}|{_NUM}{_BARE_END})",
    )
)
#: "module output", "function logs": the subject names what code prints, not its size.
_NOT_SIZE = re.compile(
    rf"{_FORWARD_SUBJECT}\s+(?:output|logs?|stdout|stderr|diffs?)\b", re.IGNORECASE
)
#: "N lines of log output": the unit counts something that is not code.
_OF_NOT_SIZE = re.compile(
    r"\s+of\s+(?:\w+\s+){0,2}(?:output|logs?|stdout|stderr|diffs?)\b", re.IGNORECASE
)
#: A word that makes a measured unit's number a bound ("its N-line cap").
_BOUND = re.compile(
    rf"{_COMPARE}|{_SYMBOL}|\b(?:cap|limit|ceiling|budget|guidance|threshold)\b", re.IGNORECASE
)
#: One measured unit: a size attached to a demonstrative ("this N-line function").
_DEMONSTRATIVE = re.compile(r"\b(?:this|that|these|those|its|their)\s+$", re.IGNORECASE)
_SIZE_RE = re.compile(_SIZE, re.IGNORECASE)
HISTORY = re.compile(
    r"\bthen in force\b|\bthen in \S*pythonic\.md\b|\bat the time\)"
    r"|\b\d{4}-\d{2}-\d{2} census\b|(?-i:\buntil (?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b)",
    re.IGNORECASE,
)
_EMPHASIS = re.compile(r"(?<!\w)_+|_+(?!\w)")
#: "e.g." and "i.e." end no sentence and break no window.
_ABBREVIATION = re.compile(r"\b([ei])\.([ge])\.")
_CODE_SPAN = re.compile(r"`+([^`]+)`+")
_BLOCK = re.compile(r"\n\s*\n|\n(?=\s*(?:[-*+]|\d+\.|\||#)\s)")
_SENTENCE = re.compile(r"(?<!\be\.g)(?<!\bi\.e)[.;!?]\s+|\|")
_STRING_TOKENS = frozenset(
    getattr(tokenize, name)
    for name in ("STRING", "FSTRING_MIDDLE", "TSTRING_MIDDLE")
    if hasattr(tokenize, name)
)

_RECOVERY = (
    "states a function or module size limit as a number. `.gzkit/rules/pythonic.md` "
    "§ Size Limits: cite the lizard_nloc / lizard_file_nloc bands of "
    ".gzkit/rules/complexity-thresholds.json, never a number copied from it (GHI #1366). "
    'A dated record keeps one only in an anchored form ("then in force", "(... at the time)"; '
    "GHI #1367). Cite the table or date the sentence, then re-run "
    "`uv run gz validate --{scope}`."
)


def _sentences(block: str) -> list[str]:
    flat = re.sub(r"\s+", " ", block.replace("*", ""))
    return [s.strip() for s in _SENTENCE.split(flat) if s.strip()]


def states_size_limit(text: str) -> bool:
    """Return whether any sentence of *text* states a function or module size as a number."""
    return any(_limit_in(sentence) for sentence in _sentences(text))


def _limit_in(sentence: str) -> bool:
    """Return whether *sentence*, or a code span in it read alone, states a size limit."""
    text = _ABBREVIATION.sub(r"\1\2", _EMPHASIS.sub("", sentence))
    phrases = (text.replace("`", ""), *_CODE_SPAN.findall(text))
    return any(
        _states_limit(phrase, match)
        for phrase in phrases
        for pattern in PATTERNS
        for match in pattern.finditer(phrase)
    )


def _states_limit(phrase: str, match: re.Match[str]) -> bool:
    """Return whether *match* names a limit, not output or one measured unit."""
    if _NOT_SIZE.search(match.group(0)) or _OF_NOT_SIZE.match(phrase, match.end()):
        return False
    return not _measured(phrase, match) or bool(_BOUND.search(match.group(0)))


def _measured(phrase: str, match: re.Match[str]) -> bool:
    """Return whether every size in *match* is one measured unit's, never a separate limit."""
    sizes = list(_SIZE_RE.finditer(phrase, match.start(), match.end()))
    return bool(sizes) and all(_DEMONSTRATIVE.search(phrase[: size.start()]) for size in sizes)


def _markdown_blocks(text: str) -> Iterator[tuple[int, str]]:
    start = 0
    for match in _BLOCK.finditer(text):
        yield text.count("\n", 0, start) + 1, text[start : match.start()]
        start = match.end()
    yield text.count("\n", 0, start) + 1, text[start:]


def _python_blocks(text: str) -> Iterator[tuple[int, str]]:
    """Yield each string and each run of comment lines, with the line it starts on.

    The stream always ends in ENDMARKER, which flushes a comment run left open at the
    end of the file. Source that does not tokenize is read as Markdown blocks instead.

    Yields:
        (line, block) for each string token and each comment run.

    """
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except tokenize.TokenError, SyntaxError:
        yield from _markdown_blocks(text)
        return
    comments: list[str] = []
    first = 0
    for token in tokens:
        if token.type == tokenize.COMMENT:
            if not comments:
                first = token.start[0]
            comments.append(token.string.lstrip("#"))
            continue
        if token.type in {tokenize.NL, tokenize.NEWLINE} and comments:
            continue
        if comments:
            yield first, "\n".join(comments)
            comments = []
        if token.type in _STRING_TOKENS:
            yield token.start[0], token.string


def size_limit_sentences(text: str, *, python: bool = False) -> list[tuple[int, str]]:
    """Return (line, sentence) for each sentence of *text* stating a size limit undated."""
    blocks = _python_blocks(text) if python else _markdown_blocks(text)
    return [
        (line, sentence)
        for line, block in blocks
        for sentence in _sentences(block)
        if _limit_in(sentence) and not HISTORY.search(sentence.replace("`", ""))
    ]


def _paths(project_root: Path) -> list[Path]:
    return [
        path
        for path in live_files(
            project_root,
            ROOTS,
            suffixes=SUFFIXES,
            root_files=ROOT_FILES,
            skip_parts=SKIPPED_PARTS,
            exclude=DATED_RECORD_FILES,
            skip_part_matching=DATED_RECORD,
        )
        if _AUTHORITY not in path.name
    ]


def audit_size_limit_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on a function or module size limit restated as a number.

    Returns:
        One finding per offending sentence, plus one per declared root absent from
        gzkit's own tree.

    """
    errors = missing_roots(
        project_root, (*ROOTS, *ROOT_FILES), error_type=_TYPE, prefix=_PREFIX, scope=_SCOPE
    )
    paths = _paths(project_root)
    for path in paths:
        rel = path.relative_to(project_root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        errors.extend(
            ValidationError(
                type=_TYPE,
                artifact=f"{rel}:{line}",
                message=(
                    f"{_PREFIX} {rel}:{line}: {sentence[:200]!r} {_RECOVERY.format(scope=_SCOPE)}"
                ),
            )
            for line, sentence in size_limit_sentences(text, python=path.suffix == ".py")
        )
    return errors
