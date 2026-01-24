"""Interview mode for Q&A document creation.

Provides structured interviews for creating PRDs, ADRs, and other governance documents.
Q&A is MANDATORY for PRD and ADR creation - the interview shapes the document.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
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
    multiline: bool = False  # Whether to expect multi-line input


@dataclass
class Answer:
    """An answer to a question."""

    question_id: str
    value: str
    timestamp: str = ""


@dataclass
class InterviewResult:
    """Result of an interview session."""

    document_type: str
    answers: dict[str, str]
    complete: bool
    missing: list[str] = field(default_factory=list)
    transcript: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_type": self.document_type,
            "answers": self.answers,
            "complete": self.complete,
            "missing": self.missing,
            "transcript": self.transcript,
        }


# PRD Interview Questions - shapes the PRD document
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
        prompt="What problem does this solve? Who has this problem? Why does it matter?",
        section="Problem Statement",
        example=(
            "Users cannot securely log in to the application. "
            "This affects all users who need authenticated access."
        ),
        multiline=True,
    ),
    Question(
        id="north_star",
        prompt="What does success look like? How will we know when we've achieved it?",
        section="North Star",
        example="All users can authenticate securely with < 2s latency. Zero breaches.",
        multiline=True,
    ),
    Question(
        id="invariants",
        prompt="What must ALWAYS be true? What must NEVER happen? List key invariants.",
        section="Invariants",
        example=(
            "1. Passwords are NEVER stored in plaintext\n"
            "2. Sessions ALWAYS expire after 24 hours\n"
            "3. Failed logins ALWAYS rate-limited"
        ),
        multiline=True,
    ),
    Question(
        id="out_of_scope",
        prompt="What is explicitly OUT OF SCOPE for this PRD?",
        section="Out of Scope",
        example="1. Social login (OAuth) - future PRD\n2. Multi-factor authentication - future PRD",
        multiline=True,
    ),
]


# ADR Interview Questions - shapes the ADR document
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
        prompt="Which lane? (lite = internal changes, heavy = external contracts)",
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
        prompt="What problem are we solving? What is the specific goal of this ADR?",
        section="Intent",
        example=(
            "We need a stateless authentication mechanism "
            "that scales horizontally without shared session state."
        ),
        multiline=True,
    ),
    Question(
        id="decision",
        prompt="What did we decide? Be specific about the approach, libraries, patterns.",
        section="Decision",
        example=(
            "We will use JWT tokens with RS256 signing. "
            "Tokens issued by auth service, validated by API gateway."
        ),
        multiline=True,
    ),
    Question(
        id="positive_consequences",
        prompt="What good things result from this decision? List benefits.",
        section="Consequences",
        example=(
            "1. Stateless auth scales horizontally\n"
            "2. Standard format enables third-party integration\n"
            "3. No session storage required"
        ),
        multiline=True,
    ),
    Question(
        id="negative_consequences",
        prompt="What tradeoffs or downsides come with this decision?",
        section="Consequences",
        example=(
            "1. Token size larger than session cookies\n"
            "2. Cannot revoke individual tokens without blacklist\n"
            "3. Clock skew can cause validation issues"
        ),
        multiline=True,
    ),
    Question(
        id="checklist",
        prompt="What are the implementation checklist items? Each becomes an OBPI.",
        section="Checklist",
        example=(
            "1. Set up JWT library and key management\n"
            "2. Create token generation endpoint\n"
            "3. Implement token validation middleware\n"
            "4. Add token refresh mechanism\n"
            "5. Write integration tests"
        ),
        multiline=True,
    ),
    Question(
        id="alternatives",
        prompt="What alternatives were considered and why were they rejected?",
        section="Alternatives",
        example=(
            "Session-based auth: Rejected because it requires "
            "sticky sessions or shared session store."
        ),
        multiline=True,
    ),
]


# OBPI Interview Questions
OBPI_QUESTIONS = [
    Question(
        id="id",
        prompt="What is the OBPI identifier? (e.g., OBPI-feature-name)",
        section="frontmatter",
        example="OBPI-user-auth",
    ),
    Question(
        id="title",
        prompt="What is the title of this OBPI?",
        section="frontmatter",
        example="Implement User Authentication",
    ),
    Question(
        id="parent",
        prompt="What is the parent ADR ID?",
        section="frontmatter",
        example="ADR-0.1.0",
    ),
    Question(
        id="item",
        prompt="Which checklist item number from the parent ADR?",
        section="frontmatter",
        example="1",
    ),
    Question(
        id="lane",
        prompt="Which lane? (lite = internal, heavy = external contracts)",
        section="frontmatter",
        example="lite",
        validator=lambda x: x.lower() in ("lite", "heavy"),
    ),
    Question(
        id="objective",
        prompt="What specific outcome does this OBPI target? Be concrete.",
        section="Objective",
        example=(
            "Implement secure user login with email/password. "
            "Users can register, log in, and log out."
        ),
        multiline=True,
    ),
    Question(
        id="allowed_paths",
        prompt="What approaches are ALLOWED? What CAN be done?",
        section="Allowed Paths",
        example=(
            "1. Use existing auth library (e.g., passlib)\n"
            "2. Store users in PostgreSQL\n"
            "3. Use bcrypt for password hashing"
        ),
        multiline=True,
    ),
    Question(
        id="denied_paths",
        prompt="What approaches are FORBIDDEN? What must NOT be done?",
        section="Denied Paths",
        example=(
            "1. Rolling custom crypto\n"
            "2. Storing passwords in plaintext\n"
            "3. Using MD5 or SHA1 for passwords"
        ),
        multiline=True,
    ),
    Question(
        id="acceptance_criteria",
        prompt="When is this OBPI complete? List specific, testable criteria.",
        section="Acceptance Criteria",
        example=(
            "1. User can register with email/password\n"
            "2. User can log in with valid credentials\n"
            "3. User can log out\n"
            "4. Invalid credentials are rejected with proper error"
        ),
        multiline=True,
    ),
]


INTERVIEWS = {
    "prd": PRD_QUESTIONS,
    "adr": ADR_QUESTIONS,
    "obpi": OBPI_QUESTIONS,
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


def format_transcript(
    document_type: str,
    answers: dict[str, str],
) -> str:
    """Format interview Q&A as a markdown transcript.

    Args:
        document_type: Type of document.
        answers: Dictionary of question_id -> answer.

    Returns:
        Formatted markdown transcript.
    """
    questions = get_interview_questions(document_type)
    lines = []
    timestamp = datetime.now().isoformat()

    lines.append(f"*Interview conducted: {timestamp}*\n")

    for question in questions:
        answer = answers.get(question.id, "")
        if answer:
            lines.append(f"### Q: {question.prompt}\n")
            lines.append(f"**A:** {answer}\n")

    return "\n".join(lines)


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

    transcript = format_transcript(document_type, answers)

    return InterviewResult(
        document_type=document_type,
        answers=answers,
        complete=len(missing) == 0,
        missing=missing,
        transcript=transcript,
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

    # Add the Q&A transcript
    template_vars["qa_transcript"] = format_transcript(document_type, answers)

    # Add derived/computed values based on document type
    if document_type == "adr" and "lane" in template_vars:
        # Ensure lane is lowercase
        template_vars["lane"] = template_vars["lane"].lower()

        # Format checklist items with checkboxes
        checklist = template_vars.get("checklist", "")
        if checklist:
            items = checklist.strip().split("\n")
            formatted = []
            for item in items:
                # Remove existing numbering and add checkbox
                item = item.strip()
                if item:
                    # Remove leading number/bullet if present
                    if item[0].isdigit():
                        item = item.lstrip("0123456789.)-: ")
                    elif item[0] in "-*":
                        item = item[1:].strip()
                    formatted.append(f"- [ ] {item}")
            template_vars["checklist"] = "\n".join(formatted)

    if document_type == "obpi" and "lane" in template_vars:
        template_vars["lane"] = template_vars["lane"].lower()
        # Set gate requirements based on lane
        is_heavy = template_vars["lane"] == "heavy"
        template_vars["docs_required"] = "Yes" if is_heavy else "No"
        template_vars["bdd_required"] = "Yes" if is_heavy else "No"

    # Ensure all expected fields have defaults
    if document_type == "prd":
        template_vars.setdefault("problem_statement", "")
        template_vars.setdefault("north_star", "")
        template_vars.setdefault("invariants", "")

    if document_type == "adr":
        template_vars.setdefault("intent", "")
        template_vars.setdefault("decision", "")
        template_vars.setdefault("positive_consequences", "")
        template_vars.setdefault("negative_consequences", "")
        template_vars.setdefault("checklist", "")
        template_vars.setdefault("alternatives", "")

    return template_vars


def parse_checklist_items(checklist_text: str) -> list[str]:
    """Parse checklist text into individual items.

    Args:
        checklist_text: Raw checklist text from interview.

    Returns:
        List of checklist item descriptions.
    """
    items = []
    for line in checklist_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Remove numbering, bullets, checkboxes
        if line[0].isdigit():
            line = line.lstrip("0123456789.)-: ")
        elif line[0] in "-*":
            line = line[1:].strip()
        if line.startswith("[ ]") or line.startswith("[x]"):
            line = line[3:].strip()
        if line:
            items.append(line)
    return items
