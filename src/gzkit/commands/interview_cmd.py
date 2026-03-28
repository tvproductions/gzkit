"""Interview command implementation."""

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
from gzkit.interview import (
    check_interview_complete,
    format_answers_for_template,
    format_transcript,
    get_interview_questions,
)
from gzkit.ledger import Ledger, adr_created_event, obpi_created_event, prd_created_event
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


def save_transcript(
    project_root: Path,
    document_type: str,
    document_id: str,
    answers: dict[str, str],
) -> Path:
    """Save the Q&A transcript as a separate artifact.

    Args:
        project_root: Project root directory.
        document_type: Type of document (prd, adr).
        document_id: The document identifier.
        answers: Interview answers.

    Returns:
        Path to the saved transcript.

    """
    transcript = format_transcript(document_type, answers)

    # Save in .gzkit/transcripts/
    transcript_dir = project_root / ".gzkit" / "transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcript_file = transcript_dir / f"{document_id}-interview.md"
    transcript_file.write_text(f"# Q&A Transcript: {document_id}\n\n{transcript}", encoding="utf-8")

    return transcript_file


def interview(document_type: str) -> None:
    """Interactive Q&A mode for document creation."""
    config = ensure_initialized()
    project_root = get_project_root()

    console.print(f"\n[bold]Creating {document_type.upper()} via interview[/bold]\n")
    console.print("Answer each question. Press Enter for empty, Ctrl+C to cancel.\n")

    questions = get_interview_questions(document_type)
    answers: dict[str, str] = {}

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
        doc_dir = project_root / config.paths.adrs
        doc_id = answers.get("id", "ADR-DRAFT")
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
        template_vars["parent_adr_path"] = str(adr_file.relative_to(project_root))
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
        parent = answers.get("parent", "")
        lane = answers.get("lane", "lite")
        ledger.append(adr_created_event(doc_id, parent, lane))
    else:
        ledger.append(obpi_created_event(doc_id, resolved_obpi_parent))

    console.print(f"\n[green]Created {document_type.upper()}: {doc_file}[/green]")
