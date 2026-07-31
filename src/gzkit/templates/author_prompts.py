"""Author-prompt values for scaffolding variables a command cannot compute (GHI #741).

``render_template`` is strict: every template variable needs a value. Most are
computed by the calling command (id, semver, lane, dates). The rest are sections
a human must write — intent, decision, rejected alternatives — and the command
has nothing to put there at scaffold time.

The wrong answer is an empty string, and the worse answer is the leniency that
preceded this module: ``SafeDict`` rendered an omitted variable as its own
literal ``{token}``, which reads as prose to every string-based check. That is
how 44 ADRs reached ``data/persona_grandfather.json``, and it was never
persona-specific — a fresh ``gz plan create`` ADR carried six such tokens and a
fresh ``gz init`` PRD carried four.

An ``_[Author: ...]_`` prompt is the right answer because it is *catchable*:
``gzkit.governance.trust_audits.adr_sections.is_placeholder_body`` strips the
bracket form before testing for substance, so a section left unfilled reports as
unauthored instead of passing as prose. The scaffold tells the human what to
write and tells the gate the writing has not happened yet.

Merge these under the command's computed values, never over them::

    render_template("prd", **AUTHOR_PROMPTS["prd"], id=prd_id, title=title)
"""

from __future__ import annotations

AUTHOR_PROMPTS: dict[str, dict[str, str]] = {
    "adr": {
        "intent": "_[Author: What problem forces this decision? State it against "
        "measured evidence, not anticipated need.]_",
        "decision": "_[Author: What is being decided? State the commitment, not the "
        "options considered.]_",
        "positive_consequences": "_[Author: What becomes true, or possible, once this lands?]_",
        "negative_consequences": "_[Author: What cost does this impose, and on whom? "
        "An ADR with no negative consequences has not been thought through.]_",
        "alternatives": "_[Author: What was rejected, and on what grounds? Name the "
        "alternative that was closest to winning.]_",
        "qa_transcript": "_[Author: Paste the design-dialogue Q&A that produced this "
        "decision, or state that none was held.]_",
    },
    "prd": {
        "problem_statement": "_[Author: Whose problem is this, and what does it cost "
        "them today? Describe the current state, not the wished-for one.]_",
        "north_star": "_[Author: What single outcome would tell you this succeeded? "
        "One sentence, observable, not a list of features.]_",
        "invariants": "_[Author: What must remain true no matter how the product "
        "evolves? These outlive every release; a list of current behaviors is not "
        "a list of invariants.]_",
        "qa_transcript": "_[Author: Paste the interview Q&A that produced this PRD, "
        "or state that none was held.]_",
    },
}

PERSONA_PROMPT = (
    "_[Author: Name the behavioral identity for agents working on this ADR — values "
    'and craftsmanship standards, never generic expertise claims ("You are an expert '
    'X developer"). Start from a reusable definition: `uv run gz personas list`.]_'
)
