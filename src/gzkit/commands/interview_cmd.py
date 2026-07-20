"""Interview command implementation."""

import json
from datetime import date
from pathlib import Path

from gzkit.commands.common import (
    GzCliError,
    _confirm,
    _prompt_text,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
)
from gzkit.commands.plan import (
    CANONICAL_ADR_ID_RE,
    FOUNDATION_SEMVER_RE,
    register_adr_in_ledger,
)
from gzkit.interview import (
    check_interview_complete,
    format_answers_for_template,
    get_interview_questions,
)
from gzkit.ledger import Ledger, obpi_created_event, prd_created_event
from gzkit.templates import render_template


def run_interview(document_type: str) -> dict[str, str]:
    """Run a mandatory Q&A interview for document creation.

    Args:
        document_type: Type of document (prd, adr, obpi).

    Returns:
        Dictionary of question_id -> answer.

    Raises:
        KeyboardInterrupt: If user cancels the interview.

    """
    console.print(f"\n[bold]Q&A Interview for {document_type.upper()}[/bold]")
    console.print("The interview shapes the document. Answer each question.\n")
    console.print("[dim]Press Enter for empty, Ctrl+C to cancel.[/dim]\n")

    questions = get_interview_questions(document_type)
    answers: dict[str, str] = {}

    for q in questions:
        # Show example if available
        if q.example:
            console.print(f"[dim]Example: {q.example}[/dim]")

        # For multiline questions, show hint
        if q.multiline:
            console.print("[dim](Multi-line: separate items with newlines)[/dim]")

        while True:
            try:
                answer = _prompt_text(q.prompt, default="")
            except KeyboardInterrupt:
                console.print("\n[yellow]Interview cancelled.[/yellow]")
                raise

            if q.validator and answer and not q.validator(answer):
                console.print("[red]Invalid answer. Please try again.[/red]")
                continue
            break

        answers[q.id] = answer
        console.print()  # Spacing between questions

    return answers


def _load_answers_from_file(from_file: str, document_type: str) -> dict[str, str]:
    """Load and validate interview answers from a JSON file.

    Args:
        from_file: Path to the JSON answers file.
        document_type: Type of document (prd, adr, obpi).

    Returns:
        Dictionary of question_id -> answer.

    Raises:
        GzCliError: If file is missing, invalid JSON, or contains unknown keys.

    """
    path = Path(from_file)
    if not path.exists():
        msg = f"BLOCKERS:\n- Answers file not found: {from_file}"
        raise GzCliError(msg)  # noqa: TRY003

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"BLOCKERS:\n- Invalid JSON in {from_file}: {exc.msg}"
        raise GzCliError(msg) from exc  # noqa: TRY003

    if not isinstance(raw, dict):
        msg = f"BLOCKERS:\n- Answers file must be a JSON object, got {type(raw).__name__}"
        raise GzCliError(msg)  # noqa: TRY003

    questions = get_interview_questions(document_type)
    valid_ids = {q.id for q in questions}
    unknown = set(raw.keys()) - valid_ids
    if unknown:
        msg = f"BLOCKERS:\n- Unknown answer keys for {document_type}: {', '.join(sorted(unknown))}"
        raise GzCliError(msg)  # noqa: TRY003

    # Validate typed answers
    answers: dict[str, str] = {}
    for q in questions:
        value = raw.get(q.id, "")
        if not isinstance(value, str):
            value = str(value)
        if q.validator and value and not q.validator(value):
            msg = f"BLOCKERS:\n- Invalid answer for '{q.id}': failed validation"
            raise GzCliError(msg)  # noqa: TRY003
        answers[q.id] = value

    return answers


def _resolve_adr_doc(
    answers: dict[str, str],
    template_vars: dict[str, str],
    adrs_root: Path,
) -> tuple[Path, str]:
    """Resolve the canonical slug-package path for an interview-created ADR.

    Validates the ``id`` answer is canonical slug-form, derives kind and
    foundation/pre-release routing from the semver embedded in the id, and
    seats the derived ``kind`` / ``semver`` / ``why_foundation_tier`` into
    *template_vars*. Returns ``(doc_dir, doc_id)`` for the slug-package
    layout ``<adrs>/{foundation,pre-release}/<id>/<id>.md`` (GHI #505).

    Raises:
        GzCliError: If the ``id`` answer is not canonical slug-form.

    """
    doc_id = answers.get("id", "").strip()
    if not CANONICAL_ADR_ID_RE.match(doc_id):
        msg = (
            "BLOCKERS:\n"
            f"- ADR id {doc_id!r} is not canonical slug-form. The interview "
            "scaffolds non-pool ADRs only; the id must match "
            "ADR-<semver>-<slug> (e.g. ADR-0.1.0-jwt-authentication). A bare "
            "id (ADR-0.1.0) emits an unslugged adr_created event and a "
            "flat-directory ADR that diverges from the canonical slug-package "
            "layout (GHI #279 / #344 / #494 / #505). For a pool ADR use "
            "`gz plan create <slug> --kind pool`."
        )
        raise GzCliError(msg)  # noqa: TRY003
    # The canonical id embeds the semver; it is the single source of truth
    # for kind and directory routing. foundation <=> 0.0.x is the ADR-0.0.17
    # taxonomy binding enforced by `gz validate --taxonomy`.
    embedded_semver = doc_id.split("-")[1]
    if FOUNDATION_SEMVER_RE.match(embedded_semver):
        msg = (
            f"--kind foundation was requested (ADR id {doc_id!r} embeds semver "
            f"{embedded_semver!r}, which routes to the foundation kind), but the "
            "foundation kind is closed to new authoring by ADR-0.34.0 (Foundation "
            "Sunset). It remains a valid schema value only for the existing "
            "grandfathered kind: foundation ADRs already on disk.\n"
            "Re-run `gz interview adr` with a release-carrying semver embedded in "
            "the id (e.g. ADR-0.36.0-<slug>, which routes to the feature kind), or "
            "author via `gz plan create <slug> --kind feature` (release-carrying "
            "work) or `gz plan create <slug> --kind pool` (backlog)."
        )
        raise GzCliError(msg)  # noqa: TRY003
    template_vars["semver"] = embedded_semver
    template_vars["kind"] = "feature"
    template_vars["why_foundation_tier"] = ""
    return adrs_root / "pre-release" / doc_id, doc_id


def interview(document_type: str, from_file: str | None = None) -> None:
    """Q&A mode for document creation.

    When *from_file* is provided, answers are loaded from a JSON file
    (agent-driven mode). Otherwise, an interactive stdin session runs.
    """
    config = ensure_initialized()
    project_root = get_project_root()

    if from_file:
        console.print(f"\n[bold]Creating {document_type.upper()} from {from_file}[/bold]\n")
        answers = _load_answers_from_file(from_file, document_type)
    else:
        console.print(f"\n[bold]Creating {document_type.upper()} via interview[/bold]\n")
        console.print("Answer each question. Press Enter for empty, Ctrl+C to cancel.\n")

        questions = get_interview_questions(document_type)
        answers = {}

        try:
            for q in questions:
                if q.example:
                    console.print(f"[dim]Example: {q.example}[/dim]")

                while True:
                    answer = _prompt_text(q.prompt, default="")
                    if q.validator and answer and not q.validator(answer):
                        console.print("[red]Invalid answer. Please try again.[/red]")
                        continue
                    break

                answers[q.id] = answer

        except KeyboardInterrupt:
            console.print("\n[yellow]Interview cancelled.[/yellow]")
            return

    # Check completion
    result = check_interview_complete(document_type, answers)

    if not result.complete:
        console.print(f"\n[yellow]Missing required fields: {result.missing}[/yellow]")
        if not _confirm("Create document anyway?"):
            return

    # Format and create document
    template_vars = format_answers_for_template(document_type, answers)
    template_vars["date"] = date.today().isoformat()
    template_vars["status"] = "Draft"

    # Determine output path
    ledger = Ledger(project_root / config.paths.ledger)
    resolved_obpi_parent = answers.get("parent", "")

    if document_type == "prd":
        doc_dir = project_root / config.paths.prd
        doc_id = answers.get("id", "PRD-DRAFT")
    elif document_type == "adr":
        doc_dir, doc_id = _resolve_adr_doc(answers, template_vars, project_root / config.paths.adrs)
    else:
        parent_input = answers.get("parent", "").strip()
        if not parent_input:
            msg = "OBPI interview requires a parent ADR ID."
            raise GzCliError(msg)  # noqa: TRY003
        parent_adr = parent_input if parent_input.startswith("ADR-") else f"ADR-{parent_input}"
        canonical_parent = ledger.canonicalize_id(parent_adr)
        adr_file, resolved_parent = resolve_adr_file(project_root, config, canonical_parent)
        template_vars["parent"] = resolved_parent
        template_vars["parent_adr"] = resolved_parent
        template_vars["parent_adr_path"] = adr_file.relative_to(project_root).as_posix()
        resolved_obpi_parent = resolved_parent
        doc_dir = adr_file.parent / "obpis"
        doc_id = answers.get("id", "OBPI-DRAFT")

    content = render_template(document_type, **template_vars)

    doc_dir.mkdir(parents=True, exist_ok=True)
    doc_file = doc_dir / f"{doc_id}.md"
    doc_file.write_text(content, encoding="utf-8")

    # Record event
    if document_type == "prd":
        ledger.append(prd_created_event(doc_id))
    elif document_type == "adr":
        # Emit through the shared on-disk-derived registration helper so the
        # interview path and `gz plan create` cannot diverge on the bare-id
        # `adr_created` class (GHI #494 / #505). The helper derives the event
        # id from `doc_file.parent.name` — the canonical slug-package
        # directory validated above — and is idempotent on re-run.
        register_adr_in_ledger(
            canonical_parent=answers.get("parent", ""),
            lane=answers.get("lane", "lite").lower(),
            adr_file=doc_file,
            ledger_path=project_root / config.paths.ledger,
        )
    else:
        ledger.append(obpi_created_event(doc_id, resolved_obpi_parent))

    console.print(f"\n[green]Created {document_type.upper()}: {doc_file}[/green]")
