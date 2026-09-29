"""Name-plausibility floor for attestor fields (GHI #894).

Moved out of ``gzkit.commands.content.retire`` so the runtime gate
(``gz content retire``) and its Layer-2 witness (``gz validate --ledger``'s
``named`` rule predicate) apply ONE predicate: the validator once asserted only
non-empty while the gate asserted named, so a row the gate would refuse still
validated (operator ruling 2026-09-28, "Authorize the move (Recommended)").
Pure and stdlib-only, so ``validate_pkg`` can import it without reaching a
command module.
"""

from __future__ import annotations

import unicodedata

# Unicode's Default_Ignorable_Code_Point property (DerivedCoreProperties.txt) names
# code points a conformant renderer draws at ZERO advance width regardless of
# General_Category. Almost every one is already Cs/Cn/Cc/Cf and excluded below; these
# four are the entire exception -- Unicode classifies them General_Category=Lo
# (letter) even though they are placeholders for an EMPTY Hangul syllable-composition
# slot, never a script character a human is named with. A tier-1 cross-vendor
# adversary found the letter-category bar admitted them, one of which (U+3164) still
# NFKC-normalizes to another member of this same set (U+1160).
#
# Only two of the four are ever tested at the `is_named` call site below: NFKC
# normalization runs BEFORE the membership check, and U+3164 -> U+1160 and
# U+FFA0 -> U+1160 under NFKC (measured against UCD 15.1.0), so `ch` is never
# U+3164 or U+FFA0 by the time this set is consulted there. All four stay --
# as a complete, readable statement of the class, and as defense-in-depth for a
# future caller that tests a pre-normalization string.
#
# This is the complete Lo-category subset of Default_Ignorable_Code_Point for UCD
# 15.1.0 -- the Unicode version bundled with CPython's `unicodedata` at the time
# this set was derived -- not the three code points the adversary happened to
# probe. stdlib `unicodedata` has no accessor for Default_Ignorable_Code_Point
# (the `regex` module's `\p{Default_Ignorable_Code_Point}` would need an
# ADR-level STDLIB-FIRST departure), so this literal set IS the compliant shape;
# `ucd_currency_warning` below is the drift witness for the one thing a literal
# set cannot self-check -- that the UCD it was derived against is still the UCD
# in use. It WARNS on the retire path and asserts hard only in the test suite
# (operator ruling 2026-08-25): a maintainer in CI can re-derive the set, an
# operator mid-retirement cannot.
DEFAULT_IGNORABLE_LETTERS_UCD_VERSION = "15.1.0"

DEFAULT_IGNORABLE_LETTERS = frozenset(
    {
        "ᅟ",  # HANGUL CHOSEONG FILLER
        "ᅠ",  # HANGUL JUNGSEONG FILLER
        "ㅤ",  # HANGUL FILLER
        "ﾠ",  # HALFWIDTH HANGUL FILLER
    }
)


def ucd_currency_warning(version: str | None = None) -> str:
    """Return the UCD-drift warning text, or ``""`` when the bundled UCD is current.

    ``DEFAULT_IGNORABLE_LETTERS`` is a hand-transcribed subset of
    DerivedCoreProperties.txt: stdlib exposes no accessor for
    ``Default_Ignorable_Code_Point``, so a literal set is the compliant shape
    under STDLIB-FIRST, but a literal set cannot self-check its own currency.
    A future CPython bundling a newer UCD would silently change which code
    points this set excludes, and ``is_named`` would resume accepting an
    invisible glyph as a named attestor with nothing to signal it.

    This WARNS; it does not raise. An earlier revision asserted here and the
    module-level call site therefore aborted ``gz content retire`` at import on
    any runtime whose UCD differed -- and ``pyproject.toml`` declares
    ``requires-python >=3.13`` with NO upper bound, so a declared-SUPPORTED
    CPython (3.14 bundles UCD 16.0.0) crashed the command outright. A tier-1
    cross-vendor adversary found it 2026-08-25; the operator ruled warn-not-raise
    the same day. The reasoning is where the witness has to land: a maintainer in
    CI can re-derive the set, while an operator mid-retirement cannot, so the
    HARD failure belongs in the test suite (``unidata_version`` is asserted there)
    and the runtime gets a line on stderr it can act on or ignore.
    """
    actual = unicodedata.unidata_version if version is None else version
    if actual == DEFAULT_IGNORABLE_LETTERS_UCD_VERSION:
        return ""
    return (
        f"warning: unicodedata.unidata_version is {actual!r}, but "
        "DEFAULT_IGNORABLE_LETTERS (gzkit.core.attestor_names) was derived against UCD "
        f"{DEFAULT_IGNORABLE_LETTERS_UCD_VERSION!r}. An invisible attestor "
        "admitted by the newer UCD would not be refused. Re-derive "
        "DEFAULT_IGNORABLE_LETTERS from DerivedCoreProperties.txt for the new "
        "UCD (the full General_Category=Lo subset of "
        "Default_Ignorable_Code_Point), then update "
        "DEFAULT_IGNORABLE_LETTERS_UCD_VERSION to match."
    )


def is_named(value: str) -> bool:
    """Return True when *value* is plausibly a human name.

    "At least one visible character" was the first fix here and it was too weak:
    an independent review retired invariant-tier canon with an attestor of ``.``,
    ``7``, a lone combining mark, and a lone surrogate, each recorded as the human
    who authorized the change (2026-08-25). The audit record this gate protects
    asks WHO, so punctuation and digits do not answer it.

    The bar is at least one Unicode LETTER after NFKC normalization, with
    surrogates, unassigned code points, controls and formats excluded. That bar was
    still too weak: General_Category alone cannot tell letter from glyph -- a code
    point can be category Lo and STILL be `Default_Ignorable_Code_Point`, meaning a
    renderer draws it with no visible mark at all (`DEFAULT_IGNORABLE_LETTERS`).
    This is a plausibility floor, not identity verification -- ``gz`` has no
    operator registry to check a name against. It rejects the values that are
    certainly not names; it cannot confirm that a name is the person's.
    """
    try:
        normalized = unicodedata.normalize("NFKC", value)
    except (TypeError, ValueError):
        return False
    for ch in normalized:
        category = unicodedata.category(ch)
        if category in {"Cs", "Cn", "Cc", "Cf"}:
            # Surrogate, unassigned, control, format -- never name content, and a
            # lone surrogate cannot even round-trip through the ledger's UTF-8.
            continue
        if category.startswith("L") and ch not in DEFAULT_IGNORABLE_LETTERS:
            return True
    return False
