"""Policy test: data interpolated into Rich markup must not be parsed as markup.

This test NEVER imports or executes application code. It parses source files
with the `ast` module.

Rich treats ``[...]`` in a printed string as console markup and consumes any
bracket whose content begins with ``[a-z#/@]`` (``rich.markup.RE_TAGS``). An
f-string that interpolates a *data* value into that position therefore renders
as nothing at all — the value is silently deleted from the operator's terminal.

Measured 2026-09-04 (GHI #944): every ``gz validate`` failure had been printing
``   →  path/to/artifact`` instead of ``   → [ownership_declaration] path/to/
artifact`` for as long as the line had existed. The error type is the operator's
only handle on *which* validator scope refused, and the ``exit 1`` vs ``exit 3``
routing in ``_POLICY_BREACH_ERROR_TYPES`` is keyed on it.

The benign case is a swallowed token. The hazard is a value that *collides*
with a real style name — ``bold``, ``dim``, ``red`` — which Rich applies,
silently restyling the remainder of the line instead of dropping a token.

Why a policy test rather than per-site unit tests: this is a class, and the
class had already been half-discovered. ``validate_cmd.py`` carried a correct
``\\[`` escape 400 lines above two unescaped siblings in the same file — someone
hit this bug, fixed the line in front of them, and did not sweep. Per-site tests
would have re-created exactly that outcome. The ratchet is what makes the 15th
site impossible rather than merely unobserved.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "gzkit"

#: Number of unescaped data brackets permitted in Rich-rendered f-strings.
#: This is a one-way ratchet: it goes to 0 and stays there. Raising it means
#: an operator-facing value is being deleted from the terminal at runtime.
MAX_UNESCAPED_DATA_BRACKETS = 0

#: Identifiers whose value is free-form text — prose a human or a subprocess
#: wrote, which can contain anything, brackets included. A path, an ID, a
#: semver or a count cannot; those are left alone rather than escaped for
#: appearance. This roster is the check's declared subject: a value named
#: outside it still reaches Rich unescaped, so the check is honest about
#: covering the family it names and not "all data". Extend the roster when a
#: new free-text field appears; do not extend the exceptions below to dodge it.
FREE_TEXT_NAMES = frozenset(
    {
        "blocker",
        "blockers",
        "body",
        "comment",
        "description",
        "detail",
        "details",
        "err",
        "error",
        "finding",
        "issue",
        "line",
        "message",
        "msg",
        "note",
        "output",
        "prose",
        "reason",
        "stderr",
        "stdout",
        "summary",
        "text",
        "title",
        "violation",
        "warning",
    }
)

#: Calls whose result is a number, so it cannot carry markup.
NUMERIC_CALLS = frozenset({"len", "sum", "int", "float", "abs", "min", "max", "round"})

#: `str` methods that return a string derived from their receiver. Resolving
#: through them is not a nicety: `result.stdout.rstrip("\n")` is the CI-relay
#: site, and a resolver that stopped at the method call read it as unnamed and
#: passed it. The mutation pass caught that; without this set the guard was
#: green over the exact line it exists to hold.
STRING_METHODS = frozenset(
    {
        "strip",
        "rstrip",
        "lstrip",
        "format",
        "join",
        "replace",
        "lower",
        "upper",
        "title",
        "casefold",
        "expandtabs",
        "removeprefix",
        "removesuffix",
        "decode",
        "splitlines",
    }
)

#: Expressions whose free-text-looking name holds a structurally bracket-free
#: value. `row['line']` is `line_no`, an int (`adr_coverage.py:321`) — escaping
#: it would be both noise and a type error.
NUMERIC_EXCEPTIONS = frozenset({"row['line']"})

#: Free-text values reaching Rich unescaped. Ratchets to 0 alongside the
#: bracket count above.
MAX_UNESCAPED_FREE_TEXT = 0

#: `console.print(x)` sites where `x` is a whole value rather than an
#: f-string. These are the highest-consequence shape in the family: 14 of them
#: relayed captured subprocess stdout/stderr, so every child command's
#: diagnostics lost their bracketed tokens on the way through `gz check` — the
#: surface whose own docstring says it exists because of "28 consecutive
#: unreadable red CI runs". Fixed with `markup=False`, since child output is
#: never markup.
MAX_UNESCAPED_BARE_ARGS = 0

#: The one API that legitimately prints caller-supplied markup. `OutputFormatter`
#: is the CLI's styling surface: callers pass `"[green]✓ done[/green]"` and
#: expect it rendered. Its `debug()` sibling escapes, because a debug payload is
#: data — the class already draws the line, and this records where.
INTENDED_MARKUP_SITES = frozenset(
    {
        ("src/gzkit/cli/formatters.py", "message"),
        # `line` is assembled two statements up with authored markup
        # (`[yellow]![/yellow]`) and every data field escaped at construction
        # (`escape(q.ghi.title)`, `escape(q.warning)`). An entry here rather
        # than a rename to something outside the roster: an exception you can
        # read and review beats a name chosen to slip past the check.
        ("src/gzkit/commands/patch_release.py", "line"),
    }
)


def _is_rich_print(node: ast.Call) -> bool:
    """True when the call is ``<something>console.print(...)``.

    Builtin ``print``, ``sys.stdout.write`` and file writes do not parse
    markup, so they are out of scope by construction: they are ``Name`` calls
    or write to a stream, never an attribute access on a Rich console.
    """
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr != "print":
        return False
    return "console" in ast.unparse(func.value).lower()


def _closing_tag_expressions(values: list[ast.expr]) -> set[str]:
    """Source of every expression appearing in a ``[/{expr}]`` closing tag.

    ``f"[{style}]text[/{style}]"`` is *intended* markup — the interpolated
    value is a style name and must reach Rich unescaped. The presence of a
    matching closing tag is what distinguishes it from a data bracket.
    """
    closing: set[str] = set()
    for index, node in enumerate(values):
        if not isinstance(node, ast.FormattedValue) or index == 0:
            continue
        previous = values[index - 1]
        if isinstance(previous, ast.Constant) and str(previous.value).endswith("[/"):
            closing.add(ast.unparse(node.value))
    return closing


def _unescaped_data_brackets(joined: ast.JoinedStr) -> list[str]:
    """Expressions interpolated into a bare ``[{expr}]`` with no closing tag."""
    values = list(joined.values)
    closing = _closing_tag_expressions(values)
    found: list[str] = []

    for index, node in enumerate(values):
        if not isinstance(node, ast.FormattedValue) or index == 0:
            continue
        previous = values[index - 1]
        following = values[index + 1] if index + 1 < len(values) else None
        if not isinstance(previous, ast.Constant):
            continue
        before = str(previous.value)
        after = str(following.value) if isinstance(following, ast.Constant) else ""

        # `\[` is the literal-bracket escape; Rich renders it as a plain `[`.
        if not before.endswith("[") or before.endswith("\\["):
            continue
        # `[{step}/{total}]` is not a tag — Rich only consumes a bracket whose
        # content starts with [a-z#/@], and a digit or the interpolation of one
        # does not. Requiring the very next literal to close the bracket keeps
        # the check on the shape that actually renders as markup.
        if not after.startswith("]"):
            continue
        expression = ast.unparse(node.value)
        if expression in closing:
            continue
        found.append(expression)

    return found


def _terminal_name(node: ast.expr) -> str | None:
    """Innermost identifier an expression resolves to, or None.

    `issue.message` -> "message"; `row["text"]` -> "text"; `detail[:200]` ->
    "detail". A call resolves to None: its result is not named, so the roster
    cannot speak to it.
    """
    while True:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Subscript):
            index = node.slice
            if isinstance(index, ast.Constant) and isinstance(index.value, str):
                return index.value
            node = node.value
            continue
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in STRING_METHODS
        ):
            node = node.func.value
            continue
        return None


def _is_escape_call(node: ast.expr) -> bool:
    """True for `escape(...)` — including `escape(str(...))`."""
    return (
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "escape"
    )


def _is_numeric_call(node: ast.expr) -> bool:
    """True for `len(...)` and friends, whose result cannot carry markup."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in NUMERIC_CALLS
    )


def _unescaped_free_text(joined: ast.JoinedStr) -> list[str]:
    """Free-text-named values interpolated into Rich output without `escape`."""
    found: list[str] = []
    for node in joined.values:
        if not isinstance(node, ast.FormattedValue):
            continue
        expression = node.value
        if _is_escape_call(expression) or _is_numeric_call(expression):
            continue
        if isinstance(expression, ast.Constant):
            continue
        if ast.unparse(expression) in NUMERIC_EXCEPTIONS:
            continue
        name = _terminal_name(expression)
        # An ALL-CAPS name is a module constant: authored here, not free text.
        if name is None or name.isupper():
            continue
        if name.lower() in FREE_TEXT_NAMES:
            found.append(ast.unparse(expression))
    return found


def _unescaped_bare_args(call: ast.Call, relative: str) -> list[str]:
    """Free-text values printed whole, with markup parsing left on."""
    if any(keyword.arg == "markup" for keyword in call.keywords):
        return []
    found: list[str] = []
    for argument in call.args:
        if isinstance(argument, ast.JoinedStr | ast.Constant) or _is_escape_call(argument):
            continue
        name = _terminal_name(argument)
        if name is None or name.isupper() or name.lower() not in FREE_TEXT_NAMES:
            continue
        if (relative, name) in INTENDED_MARKUP_SITES:
            continue
        found.append(ast.unparse(argument))
    return found


def _scan_bare_args() -> list[str]:
    """Every whole free-text value printed through Rich with markup enabled."""
    violations: list[str] = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative = path.relative_to(SRC_ROOT.parent.parent).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not _is_rich_print(node):
                continue
            for expression in _unescaped_bare_args(node, relative):
                violations.append(f"{relative}:{node.lineno}: console.print({expression})")
    return violations


def _scan_free_text() -> list[str]:
    """Every free-text value reaching Rich's markup parser unescaped."""
    violations: list[str] = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not _is_rich_print(node):
                continue
            for argument in node.args:
                if not isinstance(argument, ast.JoinedStr):
                    continue
                for expression in _unescaped_free_text(argument):
                    relative = path.relative_to(SRC_ROOT.parent.parent)
                    violations.append(f"{relative}:{node.lineno}: {{{expression}}}")
    return violations


def _scan() -> list[str]:
    """Every unescaped data bracket in a Rich-rendered f-string under src/."""
    violations: list[str] = []
    for path in sorted(SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not _is_rich_print(node):
                continue
            for argument in node.args:
                if not isinstance(argument, ast.JoinedStr):
                    continue
                for expression in _unescaped_data_brackets(argument):
                    relative = path.relative_to(SRC_ROOT.parent.parent)
                    violations.append(f"{relative}:{node.lineno}: [{{{expression}}}]")
    return violations


class TestRichMarkupEscaping(unittest.TestCase):
    """Data interpolated into a Rich bracket must be escaped, never parsed."""

    def test_no_unescaped_data_brackets_in_console_output(self) -> None:
        """A data value in `[{...}]` position is deleted from the terminal."""
        violations = _scan()

        self.assertLessEqual(
            len(violations),
            MAX_UNESCAPED_DATA_BRACKETS,
            "Rich will consume these interpolated values, printing nothing in "
            "their place (or applying them as a style when the value collides "
            "with a real style name). Escape the literal bracket as `\\\\[` so "
            "Rich renders it as text:\n  " + "\n  ".join(violations),
        )

    @staticmethod
    def _joined_str_in(source: str) -> ast.JoinedStr:
        """Extract the f-string argument of one ``console.print`` statement."""
        statement = ast.parse(source).body[0]
        assert isinstance(statement, ast.Expr)
        call = statement.value
        assert isinstance(call, ast.Call)
        assert _is_rich_print(call), source
        argument = call.args[0]
        assert isinstance(argument, ast.JoinedStr)
        return argument

    def _brackets_in(self, source: str) -> list[str]:
        """Scan one ``console.print`` statement for unescaped data brackets."""
        return _unescaped_data_brackets(self._joined_str_in(source))

    def test_no_unescaped_free_text_reaches_rich(self) -> None:
        """Prose can contain a bracket; Rich will parse it when it does.

        The bracket arm above covers brackets the author wrote. This covers
        brackets the *data* brought — a validator message, a subprocess line,
        a blocker built three modules away.
        """
        violations = _scan_free_text()

        self.assertLessEqual(
            len(violations),
            MAX_UNESCAPED_FREE_TEXT,
            "These interpolate free-form text straight into Rich's markup "
            "parser. Wrap each in `escape(...)` at the print site, where the "
            "value is known to be data:\n  " + "\n  ".join(violations),
        )

    def test_no_bare_free_text_value_is_printed_as_markup(self) -> None:
        """Printing a whole value hands Rich the data itself to parse.

        The f-string arms above catch a bracket beside an interpolation. This
        catches the shape with no f-string at all — `console.print(result.stdout)`
        — which is how captured subprocess output was reaching Rich's parser.
        """
        violations = _scan_bare_args()

        self.assertLessEqual(
            len(violations),
            MAX_UNESCAPED_BARE_ARGS,
            "These hand a whole free-text value to Rich's markup parser. Pass "
            "`markup=False` when the value is not markup (captured process "
            "output never is), or `escape(...)` when the line also carries "
            "styling:\n  " + "\n  ".join(violations),
        )

    def test_bare_arg_detector_is_not_vacuous(self) -> None:
        """The bare-arg scanner flags an unguarded print and admits both guards."""
        cases = [
            ("console.print(result.stdout)", ["result.stdout"]),
            ("console.print(result.stdout, markup=False)", []),
            ("console.print(escape(result.stdout))", []),
            ("console.print(adr_id)", []),
        ]

        for source, expected in cases:
            statement = ast.parse(source).body[0]
            assert isinstance(statement, ast.Expr)
            call = statement.value
            assert isinstance(call, ast.Call)
            self.assertEqual(_unescaped_bare_args(call, "src/gzkit/x.py"), expected)

    def test_free_text_detector_is_not_vacuous(self) -> None:
        """The free-text scanner flags an unescaped message and admits an escaped one."""
        cases = [
            ('console.print(f"  {issue.message}")', ["issue.message"]),
            ('console.print(f"  {escape(issue.message)}")', []),
            ('console.print(f"  {len(errors)} found")', []),
        ]

        for source, expected in cases:
            self.assertEqual(_unescaped_free_text(self._joined_str_in(source)), expected)

    def test_detector_flags_a_known_bad_shape(self) -> None:
        """The scanner is not vacuously green — it catches the GHI #944 shape."""
        flagged = self._brackets_in(
            'console.print(f"   [red]→[/red] [{error.type}] {error.artifact}")'
        )

        self.assertEqual(flagged, ["error.type"])

    def test_detector_admits_the_escaped_and_the_intended_shapes(self) -> None:
        """`\\[` escapes and `[{style}]…[/{style}]` style pairs are not violations."""
        self.assertEqual(
            self._brackets_in(r'console.print(f"   \\[{error.type}] {error.artifact}")'),
            [],
        )
        self.assertEqual(
            self._brackets_in('console.print(f"[{style}]{text}[/{style}] {label}")'),
            [],
        )


if __name__ == "__main__":
    unittest.main()
