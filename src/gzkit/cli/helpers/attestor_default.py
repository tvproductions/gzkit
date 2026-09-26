"""Fill an omitted `--attestor` from the configured handle (GHI #1036).

A marked verb's `--attestor` defaults to `.gzkit.json`
§ `authorship.attestor_handle`. Operator ruling on GHI #1036, verbatim: "All but
the 7 human-act (Recommended)". Only verbs whose attestor is an identity are
marked; the seven whose own contract declares the attester's act (repudiate,
withdraw, supersede, mx enter and exit, ledger correct, obpi acceptance) keep
a typed attestor.

The marker swaps the argument's default for a sentinel, so after parsing an
omission is told apart from any explicit value, whitespace included, which is
never replaced. The configuration is read after parsing, in `main()`, so
building the parser tree reads no file and `gz --help` pays nothing for it.
Help strings are left as they are (the 80-character help limit); each verb's
manpage documents the default.
"""

import argparse

_OMITTED = object()
_DEST_KEY = "attestor_default_dest"
_PARSER_KEY = "attestor_default_parser"
_REQUIRED_KEY = "attestor_default_required"
_FALLBACK_KEY = "attestor_default_fallback"


def default_attestor_from_config(parser: argparse.ArgumentParser) -> None:
    """Mark ``parser``'s ``--attestor`` to default to the configured handle.

    The argument keeps its former required-ness and default for the case where
    no handle is configured; argparse no longer enforces them, so
    :func:`apply_configured_attestor` restores them after parsing.
    """
    action = next(a for a in parser._actions if "--attestor" in a.option_strings)
    parser.set_defaults(
        **{
            _DEST_KEY: action.dest,
            _PARSER_KEY: parser,
            _REQUIRED_KEY: action.required,
            _FALLBACK_KEY: action.default,
        }
    )
    action.required = False
    action.default = _OMITTED


def apply_configured_attestor(args: argparse.Namespace) -> None:
    """Resolve an omitted ``--attestor`` on a marked verb; leave every other value alone."""
    dest = getattr(args, _DEST_KEY, None)
    if not isinstance(dest, str) or getattr(args, dest, None) is not _OMITTED:
        return
    from gzkit.attestor import configured_attestor_handle  # noqa: PLC0415

    handle = configured_attestor_handle()
    if handle:
        setattr(args, dest, handle)
    elif getattr(args, _REQUIRED_KEY):
        getattr(args, _PARSER_KEY).error("the following arguments are required: --attestor")
    else:
        setattr(args, dest, getattr(args, _FALLBACK_KEY))
