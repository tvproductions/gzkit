r"""Shared tri-state frontmatter reader (GHI #736).

Three surfaces decoded ADR frontmatter independently with different rules:

===========================================  ==================  =====================
Surface                                      Splits on           Detects
===========================================  ==================  =====================
``ledger.parse_frontmatter_value``           ``splitlines()``    ``lines[0] == "---"``
``sync._parse_frontmatter``                  ``split("\\n")``     ``lines[0] == "---"``
``taxonomy._parse_adr_frontmatter``          ``splitlines()``    ``_frontmatter_block``
===========================================  ==================  =====================

They disagree on real inputs. Given ``"\\x0b" + <canonical frontmatter>``,
``sync`` extracted ``id`` successfully while ``ledger`` reported no frontmatter
at all — same bytes, two answers. The mechanism is that ``str.splitlines()``
treats VT/FF/NEL/U+2028 as line boundaries and ``str.split("\\n")`` does not,
while ``str.strip()`` removes them either way.

**Absence and permission were the same answer.** Every membrane guard is shaped
``if parse(...) != "<forbidden>": allow``, so any input that defeated detection
was admitted. Neither surface knew it had failed, so neither could emit the
refusal prose ``.claude/rules/guardrail-feedback-prose.md`` requires.

This module is the single strict reader. It returns THREE states — ``valid``,
``absent``, ``malformed`` — so a caller can refuse what it could not read
instead of silently reading it as empty.

Deliberately does NOT tolerate leading whitespace before the opening marker.
``lstrip()``-ing first made a pool document whose first non-blank element is a
``---`` horizontal rule parse as a frontmatter block (OBPI-0.34.0-05 Step-4b
round 5, reverted). Normalization that CREATES frontmatter is a worse defect
than the one it closes.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

#: Characters ``str.splitlines()`` treats as line boundaries but ``str.split("\n")``
#: does not. This is not a blocklist of "suspicious" characters — it is exactly the
#: set on which two line-splitting strategies must disagree, which is what let one
#: decoder see a block where another saw none. Membership is decided by that
#: predicate, never by whether a character already appears in this tuple.
SPLIT_DIVERGENT_SEPARATORS: tuple[str, ...] = (
    "\x0b",  # VT       LINE TABULATION
    "\x0c",  # FF       FORM FEED
    "\x1c",  # FS       FILE SEPARATOR
    "\x1d",  # GS       GROUP SEPARATOR
    "\x1e",  # RS       RECORD SEPARATOR
    "\x85",  # NEL      NEXT LINE
    " ",  # LS     LINE SEPARATOR
    " ",  # PS     PARAGRAPH SEPARATOR
)

_BOM = "﻿"
_MARKER = "---"

FrontmatterState = Literal["valid", "absent", "malformed"]


class FrontmatterRead(BaseModel):
    """The outcome of reading one artifact's frontmatter.

    ``state`` is the load-bearing field. A caller that only asks "did I get a
    value" collapses ``absent`` and ``malformed`` back into the permissive
    single answer this module exists to split apart.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    state: FrontmatterState = Field(..., description="valid | absent | malformed.")
    fields: dict[str, str] = Field(
        default_factory=dict, description="Parsed key/value pairs; empty unless state is valid."
    )
    reason: str | None = Field(
        None, description="Why the block was rejected; set only when state is malformed."
    )

    @property
    def is_readable(self) -> bool:
        """True only for ``valid``. ``malformed`` is never quietly readable."""
        return self.state == "valid"


def _malformed(reason: str) -> FrontmatterRead:
    return FrontmatterRead(state="malformed", reason=reason)


def read_frontmatter(content: str) -> FrontmatterRead:
    """Read *content*'s frontmatter block, distinguishing absent from malformed.

    Rejection order matters: encoding damage is checked before block shape,
    because a BOM-less UTF-16 document has a well-formed block that simply
    cannot be seen through a UTF-8 lens.
    """
    if "\x00" in content:
        return _malformed(
            "content contains NUL, which indicates a BOM-less UTF-16/32 artifact "
            "decoded as UTF-8; the block cannot be read through this encoding"
        )

    normalized = content.replace(_BOM, "")

    leading_separator = next(
        (sep for sep in SPLIT_DIVERGENT_SEPARATORS if normalized.startswith(sep)), None
    )
    if leading_separator is not None:
        return _malformed(
            f"content begins with U+{ord(leading_separator):04X}, an invisible line "
            "separator that hides the frontmatter block from some readers and not "
            "others; remove it rather than relying on reader-specific tolerance"
        )

    if not normalized.startswith(_MARKER):
        return FrontmatterRead(state="absent")

    lines = normalized.splitlines()
    if not lines or lines[0].strip() != _MARKER:
        # `---` present but not alone on its own first line (e.g. `---foo`).
        return FrontmatterRead(state="absent")

    closing = next(
        (i for i, line in enumerate(lines[1:], start=1) if line.strip() == _MARKER), None
    )
    if closing is None:
        return _malformed(
            "an opening `---` marker was found with no closing `---`; a truncated "
            "block is refused rather than read as an empty one"
        )

    fields: dict[str, str] = {}
    for raw in lines[1:closing]:
        if ":" not in raw:
            continue
        key, _, value = raw.partition(":")
        fields[key.strip()] = value.strip().strip("\"'")
    return FrontmatterRead(state="valid", fields=fields)


def read_frontmatter_bytes(raw: bytes) -> FrontmatterRead:
    """Read frontmatter from undecoded *raw* bytes.

    Callers holding bytes should prefer this over decoding themselves: a
    ``UnicodeDecodeError`` is a ``malformed`` verdict, never an ``absent`` one.
    Catching the decode error and returning "no frontmatter" is the precise
    fail-open this module closes.
    """
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return _malformed(f"content is not decodable as UTF-8 ({exc.reason})")
    return read_frontmatter(content)


__all__ = [
    "SPLIT_DIVERGENT_SEPARATORS",
    "FrontmatterRead",
    "FrontmatterState",
    "read_frontmatter",
    "read_frontmatter_bytes",
]
