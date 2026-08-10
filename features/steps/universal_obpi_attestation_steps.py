"""BDD steps for ADR-0.0.36 universal OBPI attestation scenarios.

Handles JSON evidence payloads that cannot be passed through Gherkin's
double-quoted step strings (the inner quotes break the parser).

@covers REQ-0.0.36-02-01..05
"""

from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout

from behave import when

from gzkit.cli import main


def _invoke(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


@when('I emit-receipt for OBPI "{obpi_id}" with attestor "{attestor}" and evidence')
def step_emit_receipt_with_evidence(context, obpi_id: str, attestor: str) -> None:
    """Invoke ``gz obpi emit-receipt --dry-run`` with evidence from docstring.

    The JSON evidence payload is supplied as a Gherkin multiline string
    (docstring) attached to the step. Avoids the Gherkin-double-quotes
    collision with JSON property-name quoting.
    """
    evidence = context.text.strip()
    context.exit_code, context.output = _invoke(
        [
            "obpi",
            "emit-receipt",
            obpi_id,
            "--event",
            "completed",
            "--attestor",
            attestor,
            "--evidence-json",
            evidence,
            "--dry-run",
        ]
    )
