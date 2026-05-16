"""Public parse entrypoint — ADR-0.0.34 § Decision item #3.

Whitespace normalizations applied during parsing (modulo: render output is canonical form):
  - Blank-line runs between sections are treated as section separators regardless of count.
  - Trailing whitespace on each line is ignored.
  - Trailing newlines at end of document are ignored.
"""

from .markdown_parser import parse

__all__ = ["parse"]
