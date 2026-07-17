"""Operator Authorization Gate for handoff resume — the RESUME half's teeth (GHI #574).

`.gzkit/skills/gz-session-handoff/SKILL.md` § RESUME declares a **universal**
Operator Authorization Gate:

    "Every resume requires explicit operator authorization before any execution,
    at every freshness level — Fresh included. ... no file mutation / `gz`
    ceremony / migration until the operator rules."

That was prose plus a template banner, enforced by nothing — it held only by the
model's goodwill. This module is the mechanism. It is the RESUME counterpart to
`validate_sections_populated` (GHI #692, the CREATE half): together they close
`gz-session-handoff`'s two declared-but-unenforced clauses, so the skill now binds
both what a handoff must CONTAIN and what an agent may DO on reading one.

Design notes that are load-bearing:

* **The decision lives here, not in the hook.** `.claude/hooks/*.py` are generated
  text (`src/gzkit/hooks/scripts/`), so logic embedded there is unreachable by
  `@enforces` and untestable as a unit. The hook is a thin adapter over
  :func:`decide` — the ports-and-adapters shape, and the only shape a live
  negative control can point an entrypoint at.

* **Session-scoped, not per-handoff.** Authorization cites the harness
  ``session_id``. Per-handoff arming would let `gz obpi complete`'s mechanically
  written completion handoff (GHI #619) re-arm the gate mid-session, blocking the
  operator right after a completion they just attested.

* **The allowlist is skill-derived, not taste-derived.** § Trust Model declares
  what RESUME must read before presenting — "Ledger and `gz` state surfaces
  (`gz obpi status`, `gz obpi lock list`, `gz gates`, `gz state`) to verify a
  handoff's claims against Layer-2". Blocking those would make the skill's own
  Claim Verification Gate unexecutable, so they are permitted while unauthorized.
  Everything else fails CLOSED.

* **The gate never blocks its own recovery.** `gz handoff authorize` is always
  permitted. A rule that forbids the command that lifts it is worse than the hole
  it plugs (operator ruling, 2026-07-16 permission-surface pass).

Coverage limits are declared, not hidden — see :data:`UNWITNESSABLE`.
"""

from __future__ import annotations

import json
import re
import shlex
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.handoff_validation import HandoffValidationError, parse_frontmatter

__all__ = [
    "MUTATING_TOOLS",
    "RESUME_GATE_CLAIM_IDS",
    "UNWITNESSABLE",
    "Verdict",
    "decide",
    "is_resume_authorized",
    "newest_handoff",
]

_LEDGER_REL = ".gzkit/ledger.jsonl"
_HANDOFFS_REL = ".gzkit/handoffs"
_AUTHORIZED_EVENT = "handoff_resume_authorized"

#: Tools whose use is "execution" under the § RESUME contract's "no file
#: mutation" clause. `Bash` is included because `gz` ceremony and migration —
#: both named in the contract — run through it; a `Write|Edit`-only gate would
#: enforce one third of the declared clause and call it done.
MUTATING_TOOLS = frozenset({"Write", "Edit", "NotebookEdit", "Bash"})

#: Read-only Bash prefixes permitted while unauthorized. Matched against the
#: command's leading tokens after `uv run` is stripped.
#:
#: Scoped from the skill's § Trust Model "Reads (RESUME only, read-only)" plus the
#: gate's own recovery path — and then WIDENED to plain shell reads on observed
#: evidence. The first version permitted only `gz` verbs, on the stated premise
#: that "Read, Grep, Glob are never gated, so Bash is not the read path". That was
#: false in the harness this skill actually runs in: `Grep`/`Glob` are not always
#: present, which makes Bash `grep`/`cat`/`git log` the ONLY way to satisfy the
#: § Claim Verification Gate this same skill mandates BEFORE presenting. A gate
#: that forbids the verification its own skill requires cannot be complied with,
#: and an un-compliable gate gets worked around — the failure mode gzkit exists to
#: close. Reads are not execution; the contract forbids MUTATION.
_PERMITTED_BASH: tuple[tuple[str, ...], ...] = (
    # The recovery path — must never be blocked by the gate it lifts.
    ("gz", "handoff", "authorize"),
    # § Trust Model: the Layer-2 surfaces RESUME must read to verify claims.
    ("gz", "obpi", "status"),
    ("gz", "obpi", "lock", "list"),
    ("gz", "gates"),
    ("gz", "state"),
    ("gz", "status"),
    ("gz", "adr", "status"),
    ("gz", "context"),
    # Reading the handoff corpus itself in order to present it.
    ("gz", "handoff", "list"),
    ("gz", "handoff", "resume"),
    # Plain shell reads — the § Claim Verification Gate's actual instrument when
    # the harness exposes no Grep/Glob tool. Each is read-only in these forms;
    # write-capable flags are rejected below (see _MUTATING_FLAGS).
    ("git", "status"),
    ("git", "log"),
    ("git", "diff"),
    ("git", "show"),
    ("git", "branch"),
    ("git", "rev-parse"),
    ("git", "ls-files"),
    ("grep",),
    ("rg",),
    ("ls",),
    ("cat",),
    ("head",),
    ("tail",),
    ("wc",),
    ("find",),
    ("jq",),
    ("pwd",),
)

#: Flags that turn an otherwise-read-only allowlisted command into a mutation.
#: `sed`/`find` are deliberately absent from the allowlist head where they are
#: write-capable; these catch the in-place forms of what IS allowlisted.
_MUTATING_FLAGS: frozenset[str] = frozenset({"-i", "--in-place", "-delete", "-exec", "--fix"})

#: Coverage this gate structurally cannot provide. Stated so a green is never
#: read as total (the Pass D `unwitnessable.md` precedent: a gate that reports a
#: clean run without its coverage limits advertises coverage it does not have).
UNWITNESSABLE: tuple[str, ...] = (
    "MCP tool calls: the harness routes them past the Write|Edit|Bash matchers, "
    "so a connector that writes is unseen by this gate.",
    "Harness-native mutation outside the tool layer (e.g. an IDE edit by the "
    "operator) is not a resuming agent's execution and is deliberately out of scope.",
)


class Verdict(BaseModel):
    """Gate decision for one tool call. ``blocked`` is the whole contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    blocked: bool = Field(..., description="True when the tool call must be refused")
    reason: str = Field(default="", description="Three-part guardrail prose; empty when allowed")


def newest_handoff(project_root: Path) -> Path | None:
    """Return the newest resumable session handoff, or None.

    Delegates selection to :func:`gzkit.handoff_api.list_handoffs` — the existing
    production newest-first projection — rather than re-deriving it. Recency is a
    frontmatter-``timestamp`` property, and ``list_handoffs`` already parses it,
    sorts by instant (offset-aware), and admits only documents carrying an
    ``adr_id``, which excludes the generated ``.gzkit/handoffs/AGENTS.md``
    subtree-rules file.

    A newest-by-FILENAME sort is wrong and was the first implementation's bug: 14
    of the 205 on-disk handoffs are not timestamp-prefixed, and ``OBPI-…`` sorts
    after ``20260716T…`` in ASCII, so the gate named a months-old handoff as the
    one to authorize. The "reading frontmatter is too slow for a PreToolUse hot
    path" premise that motivated it was also false: the walk measures ~33ms
    against a ~300ms ``uv run`` interpreter start the hook already pays.

    Abandoned register entries are skipped — a distinct document class
    (OBPI-0.0.72-02) describing a surrendered token, not context to resume.
    """
    from gzkit.handoff_api import list_handoffs  # noqa: PLC0415  (avoids an import cycle)

    for info in list_handoffs(base_path=project_root):
        path = Path(info.path)
        candidate = path if path.is_absolute() else project_root / path
        try:
            frontmatter = parse_frontmatter(candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, HandoffValidationError):
            continue
        if isinstance(frontmatter, dict) and frontmatter.get("abandoned"):
            continue
        return candidate
    return None


def is_resume_authorized(project_root: Path, session_id: str) -> bool:
    """True when this session carries an operator authorization on the ledger.

    Fails CLOSED (returns False) on an unreadable or absent ledger: a gate that
    opens when it cannot read its own evidence is not a gate. Scans raw JSONL
    rather than through the typed reader so a single malformed line elsewhere in
    the ledger cannot make the gate un-liftable.
    """
    if not session_id:
        return False
    ledger = project_root / _LEDGER_REL
    try:
        text = ledger.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    for line in text.splitlines():
        if _AUTHORIZED_EVENT not in line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("event") == _AUTHORIZED_EVENT and event.get("session_id") == session_id:
            return True
    return False


def _tokens(command: str) -> list[str]:
    """Split a Bash command into leading tokens, `uv run` stripped.

    `shlex` failures (unbalanced quotes) yield an empty token list, which matches
    no allowlist entry and therefore fails CLOSED.
    """
    try:
        parts = shlex.split(command)
    except ValueError:
        return []
    while parts[:2] == ["uv", "run"]:
        parts = parts[2:]
    return parts


def _bash_is_read_only(command: str) -> bool:
    """True only when the command is an allowlisted read-only invocation.

    Fail-closed by construction: an unrecognized command is NOT read-only. A
    compound command (``&&``, ``;``, ``|``, redirection, substitution) is never
    read-only regardless of its head — ``gz state && rm -rf x`` must not ride in
    on its prefix.
    """
    if re.search(r"[;&|><`]|\$\(", command):
        return False
    tokens = _tokens(command)
    if not any(tuple(tokens[: len(allowed)]) == allowed for allowed in _PERMITTED_BASH):
        return False
    # An allowlisted head does not license a write-capable flag: `grep -r x . --fix`,
    # `find . -delete`, `sed -i` are mutations wearing a read's name.
    return not any(token in _MUTATING_FLAGS for token in tokens)


def _block_prose(handoff: Path, tool_name: str, project_root: Path, session_id: str) -> str:
    """Three-part guardrail prose: what failed, why forbidden, governed next step.

    Per `.claude/rules/guardrail-feedback-prose.md` — the feedback IS the prompt
    the operator would otherwise have typed, so it names the exact recovery
    command rather than pointing at documentation.
    """
    try:
        rel = handoff.relative_to(project_root).as_posix()
    except ValueError:
        rel = handoff.as_posix()
    # --session-id is INTERPOLATED, not left as a placeholder: the agent cannot
    # read its own harness session id (the id lives in the hook payload, and the
    # commands that would reveal it are themselves gated). A recovery command the
    # blocked party cannot complete is not a recovery path — the first version
    # omitted this and bricked its own author (dogfooded 2026-07-16).
    return (
        f"BLOCKED: {tool_name} refused — this session resumed a handoff "
        f"({rel}) and the operator has not ruled on it.\n\n"
        "WHY: `gz-session-handoff` SKILL.md § RESUME declares a universal Operator "
        "Authorization Gate — 'Every resume requires explicit operator authorization "
        "before any execution, at every freshness level — Fresh included ... no file "
        "mutation / gz ceremony / migration until the operator rules.' A handoff "
        "ADVISES; it does not authorize. Freshness shortens re-verification; it never "
        "converts an advisory into a license.\n\n"
        "NEXT STEP: present the handoff's advised next steps to the operator and wait "
        "for a ruling. When they rule, book their VERBATIM words (copy this line; the "
        "session id is already filled in):\n"
        f"  uv run gz handoff authorize --handoff {rel} \\\n"
        f'    --session-id {session_id} --operator-text "<their exact words>"\n\n'
        "Run it BARE — a `cd ...;` prefix makes it a compound command, which this "
        "gate correctly refuses.\n"
        "Reading is permitted while unauthorized (gz state / gz gates / gz obpi status, "
        "and git/grep/cat reads) — the gate blocks execution, never the verification "
        "that precedes it, and never its own recovery."
    )


def decide(
    project_root: Path,
    *,
    session_id: str,
    tool_name: str,
    tool_input: dict | None = None,
) -> Verdict:
    """Decide whether a tool call is permitted under the Operator Authorization Gate.

    Blocks when ALL hold: the tool can mutate, a resumable handoff exists, and no
    operator authorization is on the ledger for this session. Read-only Bash named
    by the skill's § Trust Model is permitted so the mandated Claim Verification
    Gate can run before the operator is asked to rule.
    """
    if tool_name not in MUTATING_TOOLS:
        return Verdict(blocked=False)
    handoff = newest_handoff(project_root)
    if handoff is None:
        return Verdict(blocked=False)
    if is_resume_authorized(project_root, session_id):
        return Verdict(blocked=False)
    if tool_name == "Bash":
        command = str((tool_input or {}).get("command", ""))
        if _bash_is_read_only(command):
            return Verdict(blocked=False)
    return Verdict(blocked=True, reason=_block_prose(handoff, tool_name, project_root, session_id))


# ---------------------------------------------------------------------------
# Live negative controls — the floor's teeth for this gate (ADR-0.0.74 §5)
#
# ONE CLAIM PER DECLARED CLAUSE, deliberately. § RESUME names "no file mutation
# / gz ceremony / migration"; file mutation reaches the harness through
# Write|Edit|NotebookEdit, and gz ceremony/migration only through Bash. Splitting
# the claims means a gate that hooked only Write|Edit would leave
# `handoff-resume-unauthorized-bash` undischargeable — a FAILING claim in
# `gz check`, not a caveat an author can note and ship past. That is the whole
# point: you cannot write a negative control for a surface you did not hook.
# ---------------------------------------------------------------------------

RESUME_GATE_CLAIM_IDS: frozenset[str] = frozenset(
    {"handoff-resume-unauthorized-write", "handoff-resume-unauthorized-bash"}
)


def _build_unauthorized_resume_violation() -> Path:
    """Plant a resumable handoff and a RUNTIME-UNIQUE authorized session.

    Both session ids derive from the ``mkdtemp``-random root name, so they are
    unknowable at mutation-authoring time: a broken :func:`decide` cannot
    special-case a fixed sentinel to sneak past the control (the Step-4b facade
    attack — a FIXED sentinel proves only that the gate blocks THAT ONE string,
    never the general rule). Returns the temp ROOT so the runner's
    ``shutil.rmtree(fixture())`` cleans it without leaking the parent.
    """
    root = Path(tempfile.mkdtemp(prefix="gzkit-resume-nc-"))
    handoffs = root / ".gzkit" / "handoffs"
    handoffs.mkdir(parents=True, exist_ok=True)
    # `adr_id` and `timestamp` are REQUIRED for this to be a handoff at all —
    # recency is a frontmatter property and `adr_id` is what distinguishes a
    # handoff from the generated AGENTS.md. A fixture lacking them arms nothing,
    # so the control would report FACADE against a working gate (caught live
    # 2026-07-16 when this fixture omitted them).
    (handoffs / "20260716T000000Z-nc.md").write_text(
        "---\n"
        "adr_id: ADR-0.0.65\n"
        "branch: main\n"
        "timestamp: '2026-07-16T00:00:00Z'\n"
        "agent: g0\n"
        "---\n\n## Decisions Made\n\nnc\n",
        encoding="utf-8",
    )
    authorized = {
        "event": _AUTHORIZED_EVENT,
        "session_id": f"nc-auth-{root.name}",
        "handoff_path": ".gzkit/handoffs/20260716T000000Z-nc.md",
        "operator_text": "negative control",
    }
    (root / ".gzkit" / "ledger.jsonl").write_text(json.dumps(authorized) + "\n", encoding="utf-8")
    return root


def _ep_resume_gate_differential(root: Path, tool_name: str, tool_input: dict) -> int:
    """Assert the DIFFERENTIAL: refuse unauthorized AND permit authorized.

    Truthy only when BOTH hold, which proves the verdict tracks AUTHORIZATION
    (the general rule) rather than any fixed answer. An always-block mutation
    fails the permit pole; an always-allow mutation fails the refuse pole; a
    sentinel special-case fails the refuse pole on the unknowable session id.
    The verdict is COMPUTED by production :func:`decide` with no forcing kwarg
    pre-bound (§ Boundary Invariants #7).
    """
    refused = decide(
        root, session_id=f"nc-unauth-{root.name}", tool_name=tool_name, tool_input=tool_input
    ).blocked
    permitted = not decide(
        root, session_id=f"nc-auth-{root.name}", tool_name=tool_name, tool_input=tool_input
    ).blocked
    return 1 if (refused and permitted) else 0


def _ep_resume_gate_write(root: Path) -> int:
    """Production entrypoint: the "no file mutation" clause, over both poles."""
    return _ep_resume_gate_differential(root, "Write", {"file_path": "src/x.py"})


def _ep_resume_gate_bash(root: Path) -> int:
    """Production entrypoint: the "gz ceremony / migration" clause, over both poles.

    `gz obpi complete` is ceremony, not one of the § Trust Model reads — so it
    must be refused while unauthorized and permitted once the operator rules.
    """
    return _ep_resume_gate_differential(root, "Bash", {"command": "gz obpi complete OBPI-x"})


def _resume_gate_marker() -> None:
    """Inert carrier for the resume-gate ``@enforces`` registrations."""


def _ensure_resume_gate_claims_registered() -> None:
    """(Re)register the resume-gate enforcement claims (idempotent, reset-safe).

    Mirrors the airlock live-NC registration. MUST stay wired into
    ``_ensure_production_claims_registered`` — a registration authored but
    un-wired there is an ORPHAN whose floor membership is a facade (the §5
    failure class these NCs exist to prevent).
    """
    from gzkit.airlock.enter import _AIRLOCK_CLAIM_IDS  # noqa: PLC0415
    from gzkit.enforcement import (  # noqa: PLC0415
        enforces,
        get_enforcement_registry,
        set_known_claims,
    )
    from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
        _KNOWN_QC_CLAIM_IDS,
    )

    set_known_claims(_KNOWN_QC_CLAIM_IDS | _AIRLOCK_CLAIM_IDS | RESUME_GATE_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if "handoff-resume-unauthorized-write" not in existing:
        enforces(
            "handoff-resume-unauthorized-write",
            _build_unauthorized_resume_violation,
            _ep_resume_gate_write,
        )(_resume_gate_marker)
    if "handoff-resume-unauthorized-bash" not in existing:
        enforces(
            "handoff-resume-unauthorized-bash",
            _build_unauthorized_resume_violation,
            _ep_resume_gate_bash,
        )(_resume_gate_marker)
