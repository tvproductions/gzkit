"""Observed-delivery witness for the Codex project-doc cap (GHI #962).

Every other check on this surface compares an authored number to another
authored number. ``CodexDocCapCoherenceTest`` fail-closes when the generated
``.codex/config.toml`` and ``data/vendor-manifest.json`` disagree with *each
other*; :mod:`~gzkit.governance.trust_audits.surface_delivery_witness` measures
rendered bytes against the cap the manifest *declares*. Both stay green while
delivery is zero — the shape ``AGENTS.md`` names outright: *"A PRESENCE CHECK
ANSWERS 'is something armed', NEVER 'did the governed procedure run'. Do not
build or trust a gate whose only witness is that an artifact exists."*

This module asks the missing question — **how many bytes did Codex actually
hand the model?** — and it is answerable: ``codex debug prompt-input`` renders
the model-visible prompt list as JSON, project doc included.

Why it is owed (GHI #962, 2026-09-04 → 2026-09-05). ``codex doctor`` names one
config source, the global ``$CODEX_HOME/config.toml``, and never enumerates the
project-local overlay. Read as proof of absence, that silence became the finding
*"Codex never reads it"*, which licensed lowering the generated cap from 65536
to Codex's own 32768 default and propagating *"gzkit has no route to set it"*
into five surfaces. The setting had been working the whole time: trusting a
directory is precisely what loads its ``.codex/config.toml`` (Codex's own trust
prompt, verbatim: *"Trusting the directory allows project-local config, hooks,
and exec policies to load"*), and that file wins over the global one. Measured
2026-09-05, holding trust constant and varying only the repo-local value: 32768
→ 32768 B delivered, 65536 → 46876 B delivered (the whole surface), 12000 →
12000 B delivered.

**Advisory, never fail-closed**, on two independent grounds. A vendor's byte cap
must not gate the core contract (operator ruling 2026-07-06, *"an adapter limit
must not gate the core contract"*), and the observation depends on local state —
whether Codex is installed, whether the operator has trusted this directory —
which is environment rather than repository truth. ``ValidationError`` carries
no severity field and ``gz validate`` treats every returned entry as
exit-code-changing, so a non-gating finding must be emitted as a side effect.

**An unavailable witness reports itself as unobserved and never as a pass.** A
check that falls silent when it could not run reads, to the next author, exactly
like a check that ran and found nothing — which is the defect this module exists
to close, re-created one layer up.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.advisory import emit_advisory
from gzkit.content.vendors import delivery_cap_for
from gzkit.validate import ValidationError

_PREFIX = "[codex-delivery-witness]"
_SURFACE_REL = "AGENTS.md"
_CONTENT_TYPE = "AgentContract"
_VENDOR = "codex"

#: Codex frames the loaded project doc with this header and an ``INSTRUCTIONS``
#: element. The bytes *between* the element's tags are exactly the bytes it read
#: from the file — verified 2026-09-05 against a 32768 B cap (32768 B inner,
#: 32862 B payload) and an uncapped read (46876 B inner, matching the file).
#: Counting the wrapper would overstate delivery by a constant.
_HEADER_PREFIX = "# AGENTS.md instructions for "
_BLOCK = re.compile(r"<INSTRUCTIONS>\n(.*)\n</INSTRUCTIONS>\s*\Z", re.DOTALL)

_PROBE_ARGS = ("debug", "prompt-input")
# Bounded and stdin-less on purpose: in an UNTRUSTED directory Codex asks the
# trust question interactively, and a witness that can block `gz check` on a
# prompt is worse than no witness. With stdin closed the probe fails fast and
# reports itself unobserved.
_PROBE_TIMEOUT_S = 30

_TRUNCATION_REMEDY = (
    "Raise project_doc_max_bytes in the generated .codex/config.toml "
    "(src/gzkit/sync_surfaces.py render_codex_config) and data/vendor-manifest.json "
    "content_type_delivery_caps together, or shorten the surface — canon past the "
    "cut is not in force for a Codex session."
)
_DISPUTE_REMEDY = (
    "Codex loads a project's .codex/config.toml only in a directory the operator "
    "has trusted, and that file wins over ~/.codex/config.toml. Check the trust "
    "state before assuming the declared cap is wrong (GHI #962)."
)
_ABSENT_REMEDY = (
    "Codex assembles the project doc only for a trusted directory; an untrusted "
    "one receives no AGENTS.md at all."
)


class DeliveryProbe(BaseModel):
    """One attempt to observe what Codex assembled.

    The two fields are mutually exclusive by construction: a probe either
    carries what Codex returned or says why it could not be asked. An
    unavailable probe is reported rather than swallowed, so the absence of an
    observation never reads as a clean one.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    payload: Any = Field(
        None, description="Parsed `codex debug prompt-input` output; None when unobserved."
    )
    unavailable_reason: str | None = Field(
        None, description="Why the observation could not be made at all."
    )


def delivered_contract_bytes(payload: object) -> int | None:
    """Return the UTF-8 byte count Codex loaded from root ``AGENTS.md``.

    ``None`` means Codex assembled no project-doc block at all — a different
    state from a truncated delivery, and reporting it as ``0`` would read as a
    measurement rather than an absence.
    """
    if not isinstance(payload, list):
        return None
    for item in payload:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            text = part.get("text") if isinstance(part, dict) else None
            if not isinstance(text, str) or not text.startswith(_HEADER_PREFIX):
                continue
            match = _BLOCK.search(text)
            if match is not None:
                return len(match.group(1).encode("utf-8"))
    return None


def diagnose_delivery(
    *,
    relpath: str,
    surface_bytes: int,
    delivered_bytes: int | None,
    declared_cap: int | None,
) -> list[tuple[str, str]]:
    """Return ``(severity, message)`` findings for one observation.

    Three distinct states, deliberately not collapsed:

    * the surface arrived whole — a ``NOTE``, because a silent green path cannot
      be told apart from a witness that never ran;
    * the surface was cut short — a ``WARNING`` naming the undelivered bytes;
    * the delivery stopped *below the cap gzkit declares* — a second, separate
      ``WARNING``, because that is the declaration itself being disputed by
      observation, and it is the only finding here no authored-number check can
      reach.

    The dispute requires truncation. A surface smaller than a correctly applied
    cap also delivers fewer bytes than the cap, and calling that a disputed
    declaration would send the reader to the wrong remedy.
    """
    if delivered_bytes is None:
        return [
            (
                "WARNING",
                f"{relpath}: Codex assembled no project-doc block — the contract "
                f"reached the agent not at all. {_ABSENT_REMEDY}",
            )
        ]

    if delivered_bytes >= surface_bytes:
        return [
            (
                "NOTE",
                f"{relpath}: {delivered_bytes} B of {surface_bytes} B delivered by "
                f"Codex — the whole surface reaches the agent.",
            )
        ]

    findings = [
        (
            "WARNING",
            f"{relpath}: {surface_bytes} B on disk, {delivered_bytes} B delivered by "
            f"Codex — {surface_bytes - delivered_bytes} B never reach the agent. "
            f"{_TRUNCATION_REMEDY}",
        )
    ]
    if declared_cap is not None and delivered_bytes < declared_cap:
        findings.append(
            (
                "WARNING",
                f"{relpath}: gzkit declares a {declared_cap} B {_VENDOR} delivery cap "
                f"but Codex delivered {delivered_bytes} B — the declared cap is not "
                f"the cap in force. {_DISPUTE_REMEDY}",
            )
        )
    return findings


def _default_probe(project_root: Path) -> DeliveryProbe:
    """Ask the installed Codex CLI what it would send, from *project_root*."""
    executable = shutil.which("codex")
    if executable is None:
        return DeliveryProbe(unavailable_reason="codex CLI is not on PATH")
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, resolved executable
            [executable, *_PROBE_ARGS],
            cwd=project_root,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            # Binding: src/AGENTS.md § Subprocess reads. Without it a non-UTF-8
            # locale raises UnicodeDecodeError, a ValueError the except clause
            # below does not catch, aborting the whole validate run.
            errors="replace",
            timeout=_PROBE_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return DeliveryProbe(unavailable_reason=f"codex debug prompt-input did not run: {exc}")
    if completed.returncode != 0:
        return DeliveryProbe(
            unavailable_reason=f"codex debug prompt-input exited {completed.returncode}"
        )
    try:
        return DeliveryProbe(payload=json.loads(completed.stdout))
    except json.JSONDecodeError as exc:
        return DeliveryProbe(unavailable_reason=f"codex debug prompt-input output unparsed: {exc}")


def audit_codex_delivery_witness(
    project_root: Path,
    *,
    probe: Callable[[Path], DeliveryProbe] = _default_probe,
) -> list[ValidationError]:
    """Observe Codex's actual delivery of root ``AGENTS.md``.

    Always returns an empty list: every finding here is advisory, for the two
    reasons the module docstring states. The return type is kept so the scope
    composes with the other trust audits rather than needing a special case.
    """
    surface = project_root / _SURFACE_REL
    if not surface.is_file():
        return []

    observation = probe(project_root)
    if observation.payload is None:
        emit_advisory(
            f"NOTE {_PREFIX} {_SURFACE_REL}: delivery unobserved "
            f"({observation.unavailable_reason}) — the declared cap is unverified, "
            f"not confirmed."
        )
        return []

    for severity, message in diagnose_delivery(
        relpath=_SURFACE_REL,
        surface_bytes=len(surface.read_bytes()),
        delivered_bytes=delivered_contract_bytes(observation.payload),
        declared_cap=delivery_cap_for(_CONTENT_TYPE, _VENDOR, project_root=project_root),
    ):
        emit_advisory(f"{severity} {_PREFIX} {message}")
    return []
