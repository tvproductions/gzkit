"""Interview mode for Q&A document creation.

Provides structured interviews for creating PRDs, ADRs, and other governance documents.
Q&A is MANDATORY for PRD and ADR creation - the interview shapes the document.
"""

from collections.abc import Callable
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.decomposition import build_checklist_seed, compute_scorecard, default_dimension_scores


class Question(BaseModel):
    """A question in an interview."""

    model_config = ConfigDict(extra="forbid")

    id: str
    prompt: str
    section: str  # Which document section this populates
    required: bool = True
    validator: Callable[[str], bool] | None = None
    example: str = ""
    multiline: bool = False  # Whether to expect multi-line input


class Answer(BaseModel):
    """An answer to a question."""

    model_config = ConfigDict(extra="forbid")

    question_id: str
    value: str
    timestamp: str = ""


class InterviewResult(BaseModel):
    """Result of an interview session."""

    model_config = ConfigDict(extra="forbid")

    document_type: str
    answers: dict[str, str]
    complete: bool
    missing: list[str] = Field(default_factory=list)
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
        prompt="What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)",
        section="frontmatter",
        example="ADR-0.1.0-jwt-authentication",
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
    # Forcing functions — the seven techniques `gz-adr-create` SKILL.md declares
    # non-negotiable. They were mandated by the skill and asked in practice, but had
    # no channel in this question set, no section in the ADR template, and no reader:
    # 2 of 25 interview records captured them, under an invented `forcing_functions`
    # key nothing consumed. The doctrine said "ask"; nothing said "keep".
    # Agent drafts each against session evidence; the operator audits and confirms
    # (AGENTS.md § OPERATOR ECONOMY OF EFFORT #4) — these are not operator typing.
    Question(
        id="pre_mortem",
        prompt=(
            "Pre-mortem (Klein): it is 18 months from now and this decision has "
            "failed spectacularly. Why? Name the mitigation."
        ),
        section="Forcing Functions",
        # Not `required`: an unanswered forcing function must never depend on an
        # interactive confirm. `check_interview_complete` routes missing REQUIRED
        # fields through `_confirm("Create document anyway?")`, which has no answer
        # in an agent or CI context — it exits 130. Operator canon forbids gating
        # work on a TTY. The forcing lives on channels that do not need one: the
        # skill mandates asking, the template always renders the section, and an
        # unfilled `_[Author: ...]_` prompt is caught downstream by the placeholder
        # detector in `gzkit.governance.trust_audits.adr_sections`.
        required=False,
        example=(
            "Failed because the 'no Layer-2 writes until merge' rule was never "
            "mechanically gated, so a duplicate attested completion reached the "
            "ledger. Mitigation: checklist item 4 (fail-closed validator) is not "
            "optional."
        ),
        multiline=True,
    ),
    Question(
        id="wwhtbt",
        prompt=(
            "What would have to be true (Martin) for this to be the right decision — "
            "and which of those conditions is shakiest?"
        ),
        section="Forcing Functions",
        # Not `required`: an unanswered forcing function must never depend on an
        # interactive confirm. `check_interview_complete` routes missing REQUIRED
        # fields through `_confirm("Create document anyway?")`, which has no answer
        # in an agent or CI context — it exits 130. Operator canon forbids gating
        # work on a TTY. The forcing lives on channels that do not need one: the
        # skill mandates asking, the template always renders the section, and an
        # unfilled `_[Author: ...]_` prompt is caught downstream by the placeholder
        # detector in `gzkit.governance.trust_audits.adr_sections`.
        required=False,
        example=(
            "Must be true that no legitimate parallel mode needs a Layer-2 fact "
            "before merge. Shakiest: a long parallel run an operator wants to "
            "observe mid-flight. Judged rare because the primary use case is "
            "read-only."
        ),
        multiline=True,
    ),
    Question(
        id="constraint_archaeology",
        prompt=(
            "Constraint archaeology: is each constraint here real, inherited, or "
            "assumed? When was it last tested?"
        ),
        section="Forcing Functions",
        # Not `required`: an unanswered forcing function must never depend on an
        # interactive confirm. `check_interview_complete` routes missing REQUIRED
        # fields through `_confirm("Create document anyway?")`, which has no answer
        # in an agent or CI context — it exits 130. Operator canon forbids gating
        # work on a TTY. The forcing lives on channels that do not need one: the
        # skill mandates asking, the template always renders the section, and an
        # unfilled `_[Author: ...]_` prompt is caught downstream by the placeholder
        # detector in `gzkit.governance.trust_audits.adr_sections`.
        required=False,
        example=(
            "The single-writer constraint is real (SQLite WAL). The 'no branches' "
            "constraint is inherited from operator doctrine, last restated "
            "2026-06-16, still load-bearing."
        ),
        multiline=True,
    ),
    Question(
        id="assumption_surfacing",
        prompt=(
            "Assumption surfacing: which assumptions are implicit and undocumented? "
            "What if the opposite of the core assumption were true?"
        ),
        section="Forcing Functions",
        # Not `required`: an unanswered forcing function must never depend on an
        # interactive confirm. `check_interview_complete` routes missing REQUIRED
        # fields through `_confirm("Create document anyway?")`, which has no answer
        # in an agent or CI context — it exits 130. Operator canon forbids gating
        # work on a TTY. The forcing lives on channels that do not need one: the
        # skill mandates asking, the template always renders the section, and an
        # unfilled `_[Author: ...]_` prompt is caught downstream by the placeholder
        # detector in `gzkit.governance.trust_audits.adr_sections`.
        required=False,
        example=(
            "Assumes agents read the ledger before writing. If they do not, the "
            "guard is advisory and the invariant rests on goodwill."
        ),
        multiline=True,
    ),
    Question(
        id="operator_2am",
        prompt=(
            "The 2am operator question: you are on-call at 2am and this is broken. "
            "What do you need that the design does not provide?"
        ),
        section="Forcing Functions",
        # Not `required`: an unanswered forcing function must never depend on an
        # interactive confirm. `check_interview_complete` routes missing REQUIRED
        # fields through `_confirm("Create document anyway?")`, which has no answer
        # in an agent or CI context — it exits 130. Operator canon forbids gating
        # work on a TTY. The forcing lives on channels that do not need one: the
        # skill mandates asking, the template always renders the section, and an
        # unfilled `_[Author: ...]_` prompt is caught downstream by the placeholder
        # detector in `gzkit.governance.trust_audits.adr_sections`.
        required=False,
        example=(
            "A half-emitted merge leaves no single command that says which side "
            "won. Needs a `--explain` that replays the decision."
        ),
        multiline=True,
    ),
    Question(
        id="reversibility",
        prompt=(
            "Reversibility: one-way door or two-way? If this must be reversed in "
            "12 months, what does that cost?"
        ),
        section="Forcing Functions",
        # Not `required`: an unanswered forcing function must never depend on an
        # interactive confirm. `check_interview_complete` routes missing REQUIRED
        # fields through `_confirm("Create document anyway?")`, which has no answer
        # in an agent or CI context — it exits 130. Operator canon forbids gating
        # work on a TTY. The forcing lives on channels that do not need one: the
        # skill mandates asking, the template always renders the section, and an
        # unfilled `_[Author: ...]_` prompt is caught downstream by the placeholder
        # detector in `gzkit.governance.trust_audits.adr_sections`.
        required=False,
        example=(
            "Two-way door. The daemon alternative can be adopted later without "
            "unwinding this — the merge lane simply becomes one client."
        ),
        multiline=True,
    ),
    Question(
        id="scope_minimization",
        prompt=(
            "Scope minimization: what is the smallest version that delivers value? "
            "If you had half the time, what would you cut?"
        ),
        section="Forcing Functions",
        # Not `required`: an unanswered forcing function must never depend on an
        # interactive confirm. `check_interview_complete` routes missing REQUIRED
        # fields through `_confirm("Create document anyway?")`, which has no answer
        # in an agent or CI context — it exits 130. Operator canon forbids gating
        # work on a TTY. The forcing lives on channels that do not need one: the
        # skill mandates asking, the template always renders the section, and an
        # unfilled `_[Author: ...]_` prompt is caught downstream by the placeholder
        # detector in `gzkit.governance.trust_audits.adr_sections`.
        required=False,
        example=(
            "Smallest: the read-only review mode alone. Cut the merge lane; it is "
            "the half that carries the Layer-2 risk."
        ),
        multiline=True,
    ),
    # The skill's closing question — "always ask last". Forward-looking, so it is
    # not one of the seven techniques, but it is captured on the same channel and
    # both surviving interview records carried it.
    Question(
        id="downstream_adrs",
        prompt=(
            "Closing question: what subsequent decisions does this force? What ADRs "
            "will we need to write because of this one?"
        ),
        section="Forcing Functions",
        # Not `required`: an unanswered forcing function must never depend on an
        # interactive confirm. `check_interview_complete` routes missing REQUIRED
        # fields through `_confirm("Create document anyway?")`, which has no answer
        # in an agent or CI context — it exits 130. Operator canon forbids gating
        # work on a TTY. The forcing lives on channels that do not need one: the
        # skill mandates asking, the template always renders the section, and an
        # unfilled `_[Author: ...]_` prompt is caught downstream by the placeholder
        # detector in `gzkit.governance.trust_audits.adr_sections`.
        required=False,
        example=(
            "Forces ADR-pool.worktree-parallel-agents (the capability that consumes "
            "this). May force a state-doctrine amendment naming the "
            "parallel=Layer-3-until-merge boundary."
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
        msg = f"Unknown document type: {document_type}"
        raise ValueError(msg)
    return INTERVIEWS[document_type]


def answer_payload_problems(document_type: str, raw: object) -> list[str]:
    """Return every grammar problem in a decoded interview-answers payload.

    An empty list means *raw* is a well-formed answers object for
    *document_type*. This is the answers **grammar** only — key membership and
    per-question validators — deliberately not completeness: whether the
    required set is filled is :func:`check_interview_complete`'s question, and
    the two callers want different answers to it (the CLI offers to scaffold
    anyway; a committed pool record does not get that latitude).

    Extracted so the pool-interview audit and ``gz interview <type> --from``
    answer to ONE authority (GHI #719). ``ADR_QUESTIONS`` already is the schema
    for this artifact; a second JSON-schema file would be a parallel model free
    to drift from it, which ``.claude/rules/hexagonal-architecture.md`` rule 8
    forbids. Same shape as the ``tasks:`` channel, where every reader derives
    from ``TaskId.parse`` rather than restating the grammar.

    Args:
        document_type: Type of document (prd, adr, obpi).
        raw: The already-decoded payload. Decoding and IO belong to the caller
            — this function is pure so both readers can share it.

    Returns:
        Human-readable problem descriptions, one per defect, in report order.

    """
    if not isinstance(raw, dict):
        return [f"Answers payload must be a JSON object, got {type(raw).__name__}"]

    questions = get_interview_questions(document_type)
    problems: list[str] = []

    unknown = set(raw) - {q.id for q in questions}
    if unknown:
        problems.append(f"Unknown answer keys for {document_type}: {', '.join(sorted(unknown))}")

    for q in questions:
        if not q.validator:
            continue
        value = raw.get(q.id, "")
        # Coerce before validating, matching the loader's long-standing
        # behaviour: a JSON number in a validated slot must still be judged
        # against the validator rather than slipping past it untyped. The
        # pool audit reports the type defect separately.
        text = value if isinstance(value, str) else str(value)
        if text and not q.validator(text):
            problems.append(f"Invalid answer for '{q.id}': failed validation")
    return problems


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
        semver = str(template_vars.get("semver", "0.1.0"))
        lane = str(template_vars.get("lane", "lite"))
        defaults = default_dimension_scores(lane, semver)
        scorecard = compute_scorecard(
            data_state=defaults["data_state"],
            logic_engine=defaults["logic_engine"],
            interface=defaults["interface"],
            observability=defaults["observability"],
            lineage=defaults["lineage"],
            split_single_narrative=0,
            split_surface_boundary=0,
            split_state_anchor=0,
            split_testability_ceiling=0,
        )
        template_vars.setdefault("decomposition_scorecard", scorecard.to_markdown())
        template_vars.setdefault(
            "checklist", build_checklist_seed(semver, scorecard.final_target_obpi_count)
        )
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
