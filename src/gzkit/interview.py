"""Interview mode for Q&A document creation.

Provides structured interviews for creating PRDs, ADRs, and other governance documents.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Question:
    """A question in an interview."""

    id: str
    prompt: str
    section: str  # Which document section this populates
    required: bool = True
    validator: Callable[[str], bool] | None = None
    example: str = ""


@dataclass
class Answer:
    """An answer to a question."""

    question_id: str
    value: str


@dataclass
class InterviewResult:
    """Result of an interview session."""

    document_type: str
    answers: dict[str, str]
    complete: bool
    missing: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_type": self.document_type,
            "answers": self.answers,
            "complete": self.complete,
            "missing": self.missing,
        }


# PRD Interview Questions
PRD_QUESTIONS = [
    Question(
        id="id",
        prompt="What is the PRD identifier? (e.g., PRD-PROJECT-1.0.0)",
        section="frontmatter",
        example="PRD-MYPROJECT-1.0.0",
    ),
    Question(
        id="title",
        prompt="What is the title of this PRD?",
        section="frontmatter",
        example="User Authentication System",
    ),
    Question(
        id="semver",
        prompt="What is the semantic version? (e.g., 1.0.0)",
        section="frontmatter",
        example="1.0.0",
    ),
    Question(
        id="problem_statement",
        prompt="What problem does this solve? Who has this problem?",
        section="Problem Statement",
        example="Users cannot securely log in to the application...",
    ),
    Question(
        id="north_star",
        prompt="What does success look like? How will we know when we've achieved it?",
        section="North Star",
        example="All users can authenticate securely with < 2s latency...",
    ),
    Question(
        id="invariants",
        prompt="What must always be true? List 2-3 key invariants.",
        section="Invariants",
        example="1. Passwords are never stored in plaintext\n2. Sessions expire after 24 hours",
    ),
]


# ADR Interview Questions
ADR_QUESTIONS = [
    Question(
        id="id",
        prompt="What is the ADR identifier? (e.g., ADR-0.1.0)",
        section="frontmatter",
        example="ADR-0.1.0",
    ),
    Question(
        id="title",
        prompt="What is the title of this ADR?",
        section="frontmatter",
        example="Use JWT for Authentication",
    ),
    Question(
        id="semver",
        prompt="What is the semantic version?",
        section="frontmatter",
        example="0.1.0",
    ),
    Question(
        id="lane",
        prompt="Which lane? (lite or heavy)",
        section="frontmatter",
        example="lite",
        validator=lambda x: x.lower() in ("lite", "heavy"),
    ),
    Question(
        id="parent",
        prompt="What is the parent brief ID?",
        section="frontmatter",
        example="BRIEF-auth-system",
    ),
    Question(
        id="intent",
        prompt="What are we trying to achieve? What problem does this solve?",
        section="Intent",
        example="We need a stateless authentication mechanism that scales...",
    ),
    Question(
        id="decision",
        prompt="What did we decide? Be specific about the approach.",
        section="Decision",
        example="We will use JWT tokens with RS256 signing...",
    ),
    Question(
        id="positive_consequences",
        prompt="What good things result from this decision?",
        section="Consequences",
        example="1. Stateless auth scales horizontally\n2. Standard format for interop",
    ),
    Question(
        id="negative_consequences",
        prompt="What tradeoffs or downsides come with this decision?",
        section="Consequences",
        example="1. Token size larger than session cookies\n2. Cannot revoke individual tokens",
    ),
    Question(
        id="obpis",
        prompt="What are the Observable Behavior Performance Indicators?",
        section="OBPIs",
        example="1. Auth latency < 100ms\n2. Token validation < 10ms",
    ),
]


# Brief Interview Questions
BRIEF_QUESTIONS = [
    Question(
        id="id",
        prompt="What is the brief identifier? (e.g., BRIEF-feature-name)",
        section="frontmatter",
        example="BRIEF-user-auth",
    ),
    Question(
        id="title",
        prompt="What is the title of this brief?",
        section="frontmatter",
        example="Implement User Authentication",
    ),
    Question(
        id="parent",
        prompt="What is the parent PRD or constitution ID?",
        section="frontmatter",
        example="PRD-MYPROJECT-1.0.0",
    ),
    Question(
        id="lane",
        prompt="Which lane? (lite or heavy)",
        section="frontmatter",
        example="lite",
        validator=lambda x: x.lower() in ("lite", "heavy"),
    ),
    Question(
        id="objective",
        prompt="What specific outcome does this brief target? Be concrete.",
        section="Objective",
        example="Implement secure user login with email/password...",
    ),
    Question(
        id="allowed_paths",
        prompt="What approaches are permitted?",
        section="Allowed Paths",
        example="1. Use existing auth library\n2. Store users in PostgreSQL",
    ),
    Question(
        id="denied_paths",
        prompt="What approaches are explicitly forbidden?",
        section="Denied Paths",
        example="1. Rolling custom crypto\n2. Storing passwords in plaintext",
    ),
    Question(
        id="acceptance_criteria",
        prompt="When is this brief complete? List specific, testable criteria.",
        section="Acceptance Criteria",
        example="1. User can register with email/password\n2. User can log in/out",
    ),
]


INTERVIEWS = {
    "prd": PRD_QUESTIONS,
    "adr": ADR_QUESTIONS,
    "brief": BRIEF_QUESTIONS,
}


def get_interview_questions(document_type: str) -> list[Question]:
    """Get interview questions for a document type.

    Args:
        document_type: Type of document (prd, adr, brief).

    Returns:
        List of questions for the interview.

    Raises:
        ValueError: If document type is not supported.
    """
    if document_type not in INTERVIEWS:
        raise ValueError(f"Unknown document type: {document_type}")
    return INTERVIEWS[document_type]


def validate_answer(question: Question, answer: str) -> bool:
    """Validate an answer against question constraints.

    Args:
        question: The question being answered.
        answer: The provided answer.

    Returns:
        True if valid, False otherwise.
    """
    if question.required and not answer.strip():
        return False

    if question.validator:
        return question.validator(answer)

    return True


def check_interview_complete(
    document_type: str,
    answers: dict[str, str],
) -> InterviewResult:
    """Check if an interview has all required answers.

    Args:
        document_type: Type of document.
        answers: Dictionary of question_id -> answer.

    Returns:
        InterviewResult with completion status.
    """
    questions = get_interview_questions(document_type)
    missing = []

    for question in questions:
        if question.required:
            answer = answers.get(question.id, "")
            if not validate_answer(question, answer):
                missing.append(question.id)

    return InterviewResult(
        document_type=document_type,
        answers=answers,
        complete=len(missing) == 0,
        missing=missing,
    )


def format_answers_for_template(
    document_type: str,
    answers: dict[str, str],
) -> dict[str, str]:
    """Format interview answers for template rendering.

    Args:
        document_type: Type of document.
        answers: Dictionary of question_id -> answer.

    Returns:
        Dictionary suitable for template rendering.
    """
    # Start with the raw answers
    template_vars = dict(answers)

    # Add derived/computed values based on document type
    if document_type == "adr" and "lane" in template_vars:
        # Ensure lane is lowercase
        template_vars["lane"] = template_vars["lane"].lower()

    if document_type == "brief" and "lane" in template_vars:
        template_vars["lane"] = template_vars["lane"].lower()
        # Set gate requirements based on lane
        is_heavy = template_vars["lane"] == "heavy"
        template_vars["docs_required"] = "Yes" if is_heavy else "No"
        template_vars["bdd_required"] = "Yes" if is_heavy else "No"

    return template_vars
