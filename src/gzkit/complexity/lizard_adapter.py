"""Lizard adapter: native per-function scores as domain types (RO-9 tranche 4, GHI #1183).

The one module that imports ``lizard`` in-process (`.gzkit/rules/hexagonal-architecture.md`
rule 1). Callers receive :class:`FunctionScore` records, never Lizard's own
``FunctionInfo`` objects (rule 3), and take the scorer as a parameter (rule 4).

Lizard reports a function at its ``def`` line, decorators excluded. It skips a
function whose body sits on the ``def`` line (an inline suite), and such a suite
can hide the functions that follow it, so a caller that needs a complete
population compares these scores against the source's own function definitions.
"""

import lizard
from pydantic import BaseModel, ConfigDict

__all__ = ["FunctionScore", "file_nloc", "score_functions"]


class FunctionScore(BaseModel):
    """One function as Lizard measured it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    line: int
    cyclomatic: int
    nloc: int


def score_functions(source: str, filename: str) -> list[FunctionScore]:
    """Return Lizard's native score for every function it finds in *source*."""
    info = lizard.analyze_file.analyze_source_code(filename, source)
    return [
        FunctionScore(
            name=function.name,
            line=function.start_line,
            cyclomatic=function.cyclomatic_complexity,
            nloc=function.nloc,
        )
        for function in info.function_list
    ]


def file_nloc(source: str, filename: str) -> int:
    """Return Lizard's non-comment line count for the whole of *source* (module size)."""
    return lizard.analyze_file.analyze_source_code(filename, source).nloc
