"""Multi-consumer landing transaction -- OBPI-0.35.0-07 (ADR-0.35.0 Decision 6).

``gz content land <surface>`` promotes the corpus-generated candidate of EVERY
consumer routed for a surface to its committed rendition, provenance sidecar,
lineage artifact and (when a block was removed) retention sidecar, under ONE
corpus attestation on the corpus DELTA.

This module owns the transaction's shape and its pure preflight:

* :class:`ArtifactTarget`, :class:`ConsumerPlan` and :class:`LandingJournal` are
  the durable, byte-free projection of a landing -- exact target paths, old/new
  artifact hashes, attestation evidence and per-file publication progress. The
  journal is what status and resume read, so its paths are validated to be the
  exact artifact paths of the surface's rendition directory and nothing else.
* :class:`LandingPlan` is the in-memory plan: the journal plus every artifact's
  new bytes.
* :func:`prepare_landing` builds a plan and WRITES NOTHING. Every refusal --
  an unrouted surface, a consumer with no committed rendition, a lineage
  problem, a missing attestation on a new delta, a retention-gate refusal --
  refuses the WHOLE landing before any byte of any consumer changes.
* :func:`publish_landing` publishes through the durable journal;
  :func:`resume_landing` continues an interrupted landing through the SAME
  publication path, reusing its recorded attestation; :func:`landing_status`
  classifies each consumer read-only by content hashes, never mtimes.

A single attestation over N consumers is structurally a BUNDLE, and ADR-0.0.71
gives repudiation only at OBPI granularity (ADR-0.35.0 Consequences, Negative
#3). The shared ``landing_id`` every sidecar carries is what keeps that bundle
legible; nothing here may obscure it.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.lineage import ConsumerLineage, SectionLineage, lineage_path
from gzkit.content.models import Corpus
from gzkit.content.ownership import (
    declaration_path,
    load_declaration,
    write_bytes_atomically,
)
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    load_fingerprint,
    rendition_fingerprint,
    rendition_path,
)
from gzkit.content.retention import RetentionMap, retention_path
from gzkit.content.vendors import content_type_for_surface, routes_for
from gzkit.durability import commit_directory_entry
from gzkit.events import LandedArtifact, LandedConsumer, RenditionLandedEvent
from gzkit.file_lock import exclusive_file_lock
from gzkit.governance.events import emit_rendition_landed
from gzkit.ledger import Ledger

ArtifactKind = Literal["rendition", "provenance", "lineage", "retention"]
LandingPhase = Literal["prepared", "publishing", "verified", "complete"]
ConsumerVerdict = Literal["new", "old", "indeterminate"]

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_LANDING_ID_RE = re.compile(r"^landing-\d{8}T\d{6}Z-[0-9a-f]{8}$")

# The file name each artifact kind is published under, per consumer. A journal
# path is valid only when it is EXACTLY this name inside the surface's rendition
# directory -- the tightest form of "reject `..`, absolute paths and other
# directories", because a hand-edited journal naming any other file must never
# steer publication or status at it.
_ARTIFACT_SUFFIX: dict[str, str] = {
    "rendition": ".md",
    "provenance": ".corpus.json",
    "lineage": ".lineage.json",
    "retention": ".retention.json",
}


class LandingRefusal(Exception):  # noqa: N818 - a refusal is the domain term, not an error class
    """A fail-closed preflight refusal: nothing was written for any consumer.

    ``message`` is three-part recovery prose (what failed / why forbidden /
    governed next step, ``.claude/rules/guardrail-feedback-prose.md``);
    ``exit_code`` follows ``gz content commit``: 1 user/config error, 2
    system/IO error, 3 retention-gate refusal.
    """

    def __init__(self, exit_code: int, message: str) -> None:
        """Carry the process *exit_code* and the three-part recovery *message*."""
        super().__init__(message)
        self.exit_code = exit_code
        self.message = message


def surface_rendition_dir(surface: str) -> PurePosixPath:
    """Return the project-relative rendition directory of *surface*."""
    return PurePosixPath(".gzkit", "renditions", surface)


def artifact_relpath(surface: str, consumer: str, kind: ArtifactKind) -> str:
    """Return the project-relative POSIX path of *consumer*'s *kind* artifact.

    Agrees with ``rendition_path``/``fingerprint_path``/``lineage_path``/
    ``retention_path`` -- pinned by a test, so the journal can never name a
    file the loaders and gates do not read.
    """
    return (surface_rendition_dir(surface) / f"{consumer}{_ARTIFACT_SUFFIX[kind]}").as_posix()


def sha256_hex(data: bytes) -> str:
    """Return the SHA-256 hex digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def provenance_bytes(provenance: RenditionProvenance) -> bytes:
    """Return the committed byte form of a provenance sidecar (``save_fingerprint``'s)."""
    return (provenance.model_dump_json(indent=2) + "\n").encode("utf-8")


def lineage_bytes(lineage: ConsumerLineage) -> bytes:
    """Return the committed byte form of *lineage* (``save_candidate_lineage``'s).

    The bare ``{section_id: {owned, entry_ids, byte_span}}`` map, LF-terminated
    and UTF-8 encoded -- the form the lineage loaders and gates read. Replicated
    rather than called because ``save_candidate_lineage`` writes to the STAGED
    path; byte equality with it is pinned by a test.
    """
    document = {
        section_id: section.model_dump(mode="json")
        for section_id, section in lineage.sections.items()
    }
    return (json.dumps(document, indent=2) + "\n").encode("utf-8")


def retention_bytes(retention_map: RetentionMap) -> bytes:
    """Return the committed byte form of a retention sidecar (``gz content commit``'s)."""
    return (retention_map.model_dump_json() + "\n").encode("utf-8")


def new_landing_id(now: datetime | None = None) -> str:
    """Mint a landing id: ``landing-<UTC yyyymmddThhmmssZ>-<8 hex>``."""
    stamp = (now or datetime.now(UTC)).strftime("%Y%m%dT%H%M%SZ")
    return f"landing-{stamp}-{secrets.token_hex(4)}"


def _check_sha(value: str | None) -> str | None:
    if value is not None and not _SHA256_RE.match(value):
        msg = f"{value!r} is not a lowercase SHA-256 hex digest"
        raise ValueError(msg)
    return value


class ArtifactTarget(BaseModel):
    """One file a landing publishes or removes -- path, kind, old/new hash, progress."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: ArtifactKind = Field(..., description="Which artifact of the consumer this file is")
    path: str = Field(..., description="Project-relative POSIX path of the committed artifact")
    old_sha256: str | None = Field(
        ..., description="SHA-256 of the committed bytes before landing; None when absent"
    )
    new_sha256: str | None = Field(
        ..., description="SHA-256 of the bytes to publish; None means the file is removed"
    )
    published: bool = Field(
        False, description="True once this target's new state is verified on disk"
    )

    @field_validator("path")
    @classmethod
    def _relative_posix_path(cls, value: str) -> str:
        pure = PurePosixPath(value)
        if (
            not value
            or "\\" in value
            or pure.is_absolute()
            or re.match(r"^[A-Za-z]:", value)
            or ".." in pure.parts
            or pure.as_posix() != value
        ):
            msg = (
                f"artifact path {value!r} is not a normalized project-relative POSIX path; "
                "a landing journal may only name files inside the surface's rendition directory"
            )
            raise ValueError(msg)
        return value

    @field_validator("old_sha256", "new_sha256")
    @classmethod
    def _sha(cls, value: str | None) -> str | None:
        return _check_sha(value)

    @property
    def changes(self) -> bool:
        """True when publishing this target changes the committed state."""
        return self.old_sha256 != self.new_sha256


class ConsumerPlan(BaseModel):
    """One consumer's slice of a landing: its old corpus fingerprint and artifact targets."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    consumer: str = Field(..., min_length=1, description="Routed vendor consumer (e.g. 'claude')")
    old_corpus_fingerprint: str | None = Field(
        ..., description="Corpus fingerprint of the prior sidecar; None when absent or unreadable"
    )
    artifacts: tuple[ArtifactTarget, ...] = Field(
        ..., min_length=1, description="Every artifact this consumer publishes or removes"
    )
    retention_payload: str | None = Field(
        None,
        description=(
            "The validated retention sidecar text to publish, recorded at preparation so a "
            "resume rebuilds it without re-running the retention gate (Requirement 12)"
        ),
    )

    @field_validator("old_corpus_fingerprint")
    @classmethod
    def _sha(cls, value: str | None) -> str | None:
        return _check_sha(value)

    @model_validator(mode="after")
    def _one_target_per_kind(self) -> ConsumerPlan:
        kinds = [artifact.kind for artifact in self.artifacts]
        if len(kinds) != len(set(kinds)):
            msg = f"consumer {self.consumer!r} names an artifact kind more than once: {kinds}"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _retention_payload_matches_its_target(self) -> ConsumerPlan:
        """Require a recorded payload to hash to the retention target's new_sha256.

        A removal (``new_sha256`` None) or a consumer with no retention target
        carries no payload. A publishing target without a payload is allowed:
        the ``rendition_landed`` manifest that status reads carries hashes only.
        """
        if self.retention_payload is None:
            return self
        target = next((a for a in self.artifacts if a.kind == "retention"), None)
        if target is None or target.new_sha256 is None:
            msg = f"consumer {self.consumer!r} records a retention payload it does not publish"
            raise ValueError(msg)
        if sha256_hex(self.retention_payload.encode("utf-8")) != target.new_sha256:
            msg = f"consumer {self.consumer!r}'s retention payload does not hash to its new_sha256"
            raise ValueError(msg)
        return self

    @property
    def published(self) -> bool:
        """True once every artifact of this consumer is published."""
        return all(artifact.published for artifact in self.artifacts)


class LandingJournal(BaseModel):
    """Durable, byte-free record of one landing -- what status and resume read.

    Holds everything needed to verify the landing without trusting any file's
    claims about itself: the old/new corpus fingerprints, the route and
    ownership digests the plan was prepared under, and every target's exact
    path with its old and new SHA-256.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    landing_id: str = Field(..., description="Shared id every landed sidecar carries")
    surface: str = Field(..., min_length=1, description="Control surface landed")
    phase: LandingPhase = Field(..., description="prepared -> publishing -> verified -> complete")
    new_corpus_fingerprint: str = Field(..., description="Corpus fingerprint being landed")
    corpus_entry_count: int = Field(..., ge=0, description="Entry count of the landed corpus")
    route_digest: str = Field(..., description="SHA-256 of the surface's resolved route")
    ownership_digest: str = Field(..., description="SHA-256 of the ownership declaration bytes")
    consumers: tuple[ConsumerPlan, ...] = Field(
        ..., min_length=1, description="The full intended consumer set, in route order"
    )
    attestor: str = Field(..., min_length=1, description="Operator whose attestation this carries")
    attestation_text: str = Field(..., min_length=1, description="The one corpus attestation")
    attestation_reused: bool = Field(
        ..., description="True when the attestation was reused from verified committed sidecars"
    )
    created_ts: str = Field(..., description="ISO-8601 UTC timestamp the plan was prepared")

    @field_validator("landing_id")
    @classmethod
    def _landing_id_shape(cls, value: str) -> str:
        if not _LANDING_ID_RE.match(value):
            msg = f"landing_id {value!r} is not 'landing-<yyyymmddThhmmssZ>-<8 hex>'"
            raise ValueError(msg)
        return value

    @field_validator("surface")
    @classmethod
    def _surface_is_one_name(cls, value: str) -> str:
        pure = PurePosixPath(value)
        if "\\" in value or pure.is_absolute() or ".." in pure.parts:
            msg = f"surface {value!r} would place renditions outside .gzkit/renditions/"
            raise ValueError(msg)
        return value

    @field_validator("new_corpus_fingerprint", "route_digest", "ownership_digest")
    @classmethod
    def _sha(cls, value: str) -> str:
        _check_sha(value)
        return value

    @model_validator(mode="after")
    def _targets_are_this_surfaces_artifacts(self) -> LandingJournal:
        names = [plan.consumer for plan in self.consumers]
        if len(names) != len(set(names)):
            msg = f"landing {self.landing_id} names a consumer more than once: {names}"
            raise ValueError(msg)
        for plan in self.consumers:
            for artifact in plan.artifacts:
                expected = artifact_relpath(self.surface, plan.consumer, artifact.kind)
                if artifact.path != expected:
                    msg = (
                        f"landing {self.landing_id} targets {artifact.path!r} for "
                        f"{plan.consumer!r}'s {artifact.kind}; the only permitted path is "
                        f"{expected!r} (unsafe or foreign journal path)"
                    )
                    raise ValueError(msg)
        return self


class LandingPlan(BaseModel):
    """In-memory landing plan: the journal plus every published artifact's new bytes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    journal: LandingJournal = Field(..., description="Durable projection of this plan")
    payloads: Mapping[str, bytes] = Field(
        ..., description="New bytes keyed by artifact path; absent for a removal"
    )
    notes: tuple[str, ...] = Field(
        default=(), description="Operator-facing report lines (e.g. retention correspondence)"
    )

    @field_validator("payloads", mode="after")
    @classmethod
    def _read_only(cls, value: Mapping[str, bytes]) -> Mapping[str, bytes]:
        # A frozen model with a mutable dict is frozen in name only: the bytes
        # published must be exactly the bytes whose hashes the journal records.
        return MappingProxyType(dict(value))

    @model_validator(mode="after")
    def _payloads_match_hashes(self) -> LandingPlan:
        expected: dict[str, str] = {}
        for plan in self.journal.consumers:
            for artifact in plan.artifacts:
                if artifact.new_sha256 is not None:
                    expected[artifact.path] = artifact.new_sha256
        actual = {path: sha256_hex(data) for path, data in self.payloads.items()}
        if actual != expected:
            msg = "landing payloads do not match the journal's new_sha256 manifest"
            raise ValueError(msg)
        return self


# --------------------------------------------------------------------------- #
# Preparation (pure: reads only)                                              #
# --------------------------------------------------------------------------- #


def _refusal(exit_code: int, what: str, why: str, next_step: str) -> LandingRefusal:
    return LandingRefusal(
        exit_code,
        f"Error: {what} Nothing was written for any consumer.\n"
        f"Why forbidden: {why}\n"
        f"Next: {next_step}",
    )


def _route_digest(surface: str, owner: str, consumers: Sequence[str]) -> str:
    document = {"surface": surface, "content_type": owner, "consumers": list(consumers)}
    return sha256_hex(json.dumps(document, sort_keys=True).encode("utf-8"))


def _read_optional(path: Path) -> bytes | None:
    """Return *path*'s bytes, or ``None`` when absent; an unreadable file is exit 2."""
    if not path.exists():
        return None
    try:
        return path.read_bytes()
    except OSError as exc:
        raise _refusal(
            2,
            f"could not read {path.as_posix()!r}: {exc}.",
            "a landing must hash every target's committed bytes before it may change them.",
            "restore read access to the file, then re-run `gz content land`.",
        ) from exc


class _Generated(BaseModel):
    """One consumer's verified candidate and the committed state it would replace."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    consumer: str
    candidate_text: str
    lineage: ConsumerLineage
    prior_rendition: bytes
    prior_sidecar: RenditionProvenance | None
    sidecar_problem: str | None


def _resolve_consumers(root: Path, surface: str) -> tuple[str, list[str]]:
    if not corpus_path(root, surface).exists():
        raise _refusal(
            1,
            f"no corpus for {surface!r} at {corpus_path(root, surface).as_posix()!r}.",
            "a landing publishes renditions generated FROM the corpus; with no corpus "
            "there is no delta to attest and nothing to generate.",
            f"capture canon with `gz content remember {surface}` first.",
        )
    owner = content_type_for_surface(surface, project_root=root)
    consumers = routes_for(owner, project_root=root) if owner is not None else []
    if owner is None or not consumers:
        raise _refusal(
            1,
            f"surface {surface!r} resolves to no routed consumer (content type {owner!r}).",
            "a landing lands every consumer routed for the surface's content type; "
            "guessing the set would publish a partial or foreign bundle.",
            "declare the surface in surface_content_types and its consumers in "
            "content_type_routes (data/vendor-manifest.json), then re-run `gz content land`.",
        )
    return owner, consumers


def _load_sidecar(
    root: Path, surface: str, consumer: str
) -> tuple[RenditionProvenance | None, str | None]:
    """Return ``(sidecar, problem)``; a missing or corrupt sidecar is a problem, never proof."""
    try:
        sidecar = load_fingerprint(root, surface, consumer)
    except (OSError, ValueError, ValidationError) as exc:
        return None, f"its provenance sidecar is unreadable or malformed ({type(exc).__name__})"
    if sidecar is None:
        return None, "it has no provenance sidecar"
    return sidecar, None


def _generate_and_verify(root: Path, surface: str, consumer: str) -> _Generated:
    # Deferred imports: the composer and the lineage gate pull the whole content
    # engine; keeping them local keeps `gz content land --help` light.
    from gzkit.content.composer import generate_candidate  # noqa: PLC0415
    from gzkit.governance.trust_audits.rendition_lineage import (  # noqa: PLC0415
        verify_candidate_against_declaration,
    )

    prior_path = rendition_path(root, surface, consumer)
    if not prior_path.exists():
        raise _refusal(
            1,
            f"routed consumer {consumer!r} has no committed rendition at "
            f"{prior_path.as_posix()!r}.",
            "a generated candidate carries unowned sections forward from the prior "
            "committed rendition; without one there is nothing to derive from, and "
            "landing the other consumers alone would split the bundle.",
            f"bootstrap it with `gz content compose {surface} --consumer {consumer}` and "
            f"`gz content commit {surface} --consumer {consumer}`, then re-run "
            "`gz content land`.",
        )
    prior_rendition = _read_optional(prior_path) or b""
    try:
        generated = generate_candidate(root, surface, consumer)
        prior_text = prior_rendition.decode("utf-8")
        declaration = load_declaration(declaration_path(root, surface), prior_text, root)
        problems = verify_candidate_against_declaration(
            generated.rendition.candidate_text,
            generated.rendition.candidate_text,
            generated.lineage,
            load_corpus(root, surface),
            declaration,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise _refusal(
            1,
            f"the candidate for {consumer!r} could not be generated: {exc}",
            "every consumer's candidate must be generated from the corpus and verified "
            "against the ownership declaration before any consumer is written.",
            "repair the refusal named above, then re-run `gz content land`.",
        ) from exc
    if problems:
        findings = "\n".join(f"- {problem}" for problem in problems)
        raise _refusal(
            1,
            f"the candidate for {consumer!r} fails lineage verification:\n{findings}\n",
            "ADR-0.35.0 BI-10 forbids publishing a candidate whose lineage disagrees "
            "with the ownership declaration or the effective corpus.",
            "repair the corpus or declaration the findings name, then re-run `gz content land`.",
        )
    sidecar, problem = _load_sidecar(root, surface, consumer)
    return _Generated(
        consumer=consumer,
        candidate_text=generated.rendition.candidate_text,
        lineage=generated.lineage,
        prior_rendition=prior_rendition,
        prior_sidecar=sidecar,
        sidecar_problem=problem,
    )


def _resolve_attestation(
    generated: Sequence[_Generated], fingerprint: str, attestor: str, attestation_text: str
) -> tuple[str, str, bool]:
    """Return ``(attestor, attestation_text, reused)`` or refuse (brief Requirement 5).

    The corpus delta is NEW when any consumer's sidecar is absent, unreadable,
    or frozen against a different corpus fingerprint. A new delta requires an
    explicit, non-blank attestor AND text. An unchanged corpus accepts explicit
    values, or reuses the committed evidence ONLY when every sidecar verifies:
    current fingerprint, a rendition fingerprint equal to the committed bytes'
    hash, and one shared attestor and text. Missing or corrupt evidence is never
    proof that canon is unchanged.
    """
    if attestor.strip() and attestation_text.strip():
        return attestor, attestation_text, False

    need = (
        'supply `--attestor <handle> --attestation-text "<the operator\'s verbatim words>"` '
        "and re-run `gz content land`."
    )
    moved = [
        f"{g.consumer!r}: {g.sidecar_problem}"
        if g.prior_sidecar is None
        else f"{g.consumer!r}: its sidecar is frozen against another corpus fingerprint"
        for g in generated
        if g.prior_sidecar is None or g.prior_sidecar.corpus_fingerprint != fingerprint
    ]
    if moved:
        raise _refusal(
            1,
            "--attestor and --attestation-text are required and may not be empty or "
            "whitespace: the corpus is a NEW delta, or its evidence is missing -- "
            + "; ".join(moved)
            + ".",
            "the corpus attestation attaches to the corpus delta (ADR-0.35.0 Decision 6); "
            "a new delta with no attestation would land canon nobody attested.",
            need,
        )

    unverified = [
        f"{g.consumer!r}: {g.sidecar_problem}"
        if g.prior_sidecar is None
        else f"{g.consumer!r}: its rendition_fingerprint does not match the committed bytes"
        for g in generated
        if g.prior_sidecar is None
        or g.prior_sidecar.rendition_fingerprint != rendition_fingerprint(g.prior_rendition)
    ]
    if unverified:
        raise _refusal(
            1,
            "the committed evidence cannot be reused -- " + "; ".join(unverified) + ".",
            "an unchanged-corpus re-render reuses the standing attestation only when every "
            "consumer's sidecar describes the bytes actually on disk; a sidecar next to "
            "edited bytes is not proof of unchanged canon.",
            need,
        )

    evidence = {
        (g.prior_sidecar.attestor, g.prior_sidecar.attestation_text)
        for g in generated
        if g.prior_sidecar is not None
    }
    if len(evidence) != 1:
        raise _refusal(
            1,
            "the consumers' committed sidecars carry disagreeing attestations.",
            "one landing carries exactly one corpus attestation; picking one of several "
            "would attribute the others' consumers to words they were not landed under.",
            need,
        )
    ((reused_attestor, reused_text),) = evidence
    return reused_attestor, reused_text, True


def _bind_retention_maps(
    surface: str, consumers: Sequence[str], retention_maps: Sequence[str]
) -> dict[str, str]:
    """Bind each ``--retention-map`` to its consumer by the map's own target.

    A malformed map or two maps for one consumer is a user error (exit 1), as in
    ``gz content commit``. A map naming another surface or no routed consumer
    fails the retention gate's own map-target binding (exit 3, like commit's
    ``check_map_target``): it accounts for no landed consumer's removal.
    """
    bound: dict[str, str] = {}
    for map_path in retention_maps:
        try:
            retention_map = RetentionMap.model_validate_json(
                Path(map_path).read_text(encoding="utf-8")
            )
        except (OSError, ValueError) as exc:
            raise _refusal(
                1,
                f"--retention-map {map_path!r} is unreadable or malformed: {exc}.",
                "a retention map is the operator-reviewed accounting of a removed block; "
                "an unreadable one accounts for nothing.",
                "repair the map file, then re-run `gz content land`.",
            ) from exc
        target = retention_map.consumer
        if retention_map.surface != surface or target not in consumers:
            raise _refusal(
                3,
                f"--retention-map {map_path!r} targets ({retention_map.surface!r}, "
                f"{target!r}), which is not a routed consumer of {surface!r} "
                f"({', '.join(consumers)}).",
                "each map binds to exactly one consumer through its own surface/consumer "
                "target; a map for no landed consumer would silently govern nothing.",
                "pass one --retention-map per consumer whose candidate removes a block, "
                "each naming this surface and that consumer.",
            )
        if target in bound:
            raise _refusal(
                1,
                f"two --retention-map files target consumer {target!r}: "
                f"{bound[target]!r} and {map_path!r}.",
                "one consumer's removed blocks are accounted for by exactly one map; "
                "choosing between two would be an unreviewed pick.",
                f"pass a single --retention-map for {target!r}, then re-run `gz content land`.",
            )
        bound[target] = map_path
    return bound


def _retention_gate(
    root: Path,
    surface: str,
    generated: _Generated,
    map_path: str | None,
    attestation_text: str,
) -> RetentionMap | None:
    """Run the OBPI-0.35.0-14 retention gate for one consumer (ADR-0.35.0 BI-10).

    Calls ``enforce_retention`` -- the complete gate, never ``validate_retention``
    alone -- against THIS invocation's raw attestation text, never a reused one.
    Returns the validated map to publish, or ``None`` when no block was removed.
    """
    # Deferred: commit.py is a command module that imports this layer's peers.
    from gzkit.commands.content.commit import enforce_retention  # noqa: PLC0415

    outcome = enforce_retention(
        root, surface, generated.consumer, generated.candidate_text, map_path, attestation_text
    )
    if outcome.ok:
        return outcome.retention_map
    findings = [line for line in (outcome.message or "").splitlines() if line.startswith("- [")]
    detail = "\n".join(findings) if findings else (outcome.message or "")
    raise LandingRefusal(
        outcome.exit_code or 3,
        f"Error: the retention gate refused consumer {generated.consumer!r}; the WHOLE "
        f"landing is refused. Nothing was written for any consumer.\n{detail}\n"
        "Why forbidden: a removed block with an unaccounted condition is an unreviewed "
        "meaning loss (ADR-0.35.0 Decision item 10, BI-10), and one refused consumer "
        "refuses the bundle.\n"
        f"Next: pass `--retention-map <file>` for {generated.consumer!r} accounting for "
        "every condition of each removed block (KEPT with its candidate span, or DROPPED "
        "with a reason), name every DROPPED condition id in THIS invocation's "
        "--attestation-text, then re-run `gz content land`.",
    )


def _retention_notes(consumer: str, retention_map: RetentionMap) -> list[str]:
    """Render the KEPT/DROPPED correspondence the tool cannot judge, for the operator."""
    lines = [f"Retention ({consumer}):"]
    for block in retention_map.blocks:
        for condition in block.conditions:
            if condition.disposition == "kept":
                lines.append(f'  {condition.id}: "{condition.quote}" -> "{condition.span}"')
            else:
                lines.append(f"  {condition.id}: DROPPED -- {condition.reason}")
    return lines


class _Frame(BaseModel):
    """The values every consumer slice of one landing shares."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    root: Path
    surface: str
    fingerprint: str
    entry_count: int
    attestor: str
    attestation_text: str
    landing_id: str
    created_ts: str


def _target(frame: _Frame, consumer: str, kind: ArtifactKind, new: bytes | None) -> ArtifactTarget:
    path = artifact_relpath(frame.surface, consumer, kind)
    old = _read_optional(frame.root / path)
    return ArtifactTarget(
        kind=kind,
        path=path,
        old_sha256=sha256_hex(old) if old is not None else None,
        new_sha256=sha256_hex(new) if new is not None else None,
    )


def _provenance(frame: _Frame, rendition: bytes) -> RenditionProvenance:
    """Build the sidecar every consumer shares: one attestation, one landing_id."""
    return RenditionProvenance(
        corpus_fingerprint=frame.fingerprint,
        corpus_entry_count=frame.entry_count,
        rendition_fingerprint=rendition_fingerprint(rendition),
        committed_ts=frame.created_ts,
        attestor=frame.attestor,
        attestation_text=frame.attestation_text,
        landing_id=frame.landing_id,
    )


def _new_frame(root: Path, surface: str, corpus: Corpus, attestation: tuple[str, str]) -> _Frame:
    """Mint the landing id and freeze the values every consumer slice shares."""
    now = datetime.now(UTC)
    return _Frame(
        root=root,
        surface=surface,
        fingerprint=corpus_fingerprint(corpus),
        entry_count=len(corpus.entries),
        attestor=attestation[0],
        attestation_text=attestation[1],
        landing_id=new_landing_id(now),
        created_ts=now.isoformat(),
    )


def _consumer_slice(
    frame: _Frame, g: _Generated, retention_map: RetentionMap | None
) -> tuple[ConsumerPlan, dict[str, bytes], list[str]]:
    """Build one consumer's targets, new bytes and report lines under the shared frame."""
    rendition = g.candidate_text.encode("utf-8")
    new_bytes: dict[ArtifactKind, bytes | None] = {
        "rendition": rendition,
        "provenance": provenance_bytes(_provenance(frame, rendition)),
        "lineage": lineage_bytes(g.lineage),
    }
    notes: list[str] = []
    if retention_map is not None:
        new_bytes["retention"] = retention_bytes(retention_map)
        notes = _retention_notes(g.consumer, retention_map)
    elif (frame.root / artifact_relpath(frame.surface, g.consumer, "retention")).exists():
        # No block removed this landing: a stale sidecar must never describe a
        # delta it did not govern, so its removal is journaled with the rest.
        new_bytes["retention"] = None
    plan = ConsumerPlan(
        consumer=g.consumer,
        old_corpus_fingerprint=(
            g.prior_sidecar.corpus_fingerprint if g.prior_sidecar is not None else None
        ),
        artifacts=tuple(_target(frame, g.consumer, kind, data) for kind, data in new_bytes.items()),
        retention_payload=(
            retention_bytes(retention_map).decode("utf-8") if retention_map is not None else None
        ),
    )
    payloads = {
        artifact_relpath(frame.surface, g.consumer, kind): data
        for kind, data in new_bytes.items()
        if data is not None
    }
    return plan, payloads, notes


def _route_digest_now(root: Path, surface: str) -> str:
    owner = content_type_for_surface(surface, project_root=root)
    consumers = routes_for(owner, project_root=root) if owner is not None else []
    return _route_digest(surface, str(owner), consumers)


def _ownership_digest(root: Path, surface: str) -> str:
    return sha256_hex(_read_optional(declaration_path(root, surface)) or b"")


def _assemble_journal(frame: _Frame, plans: Sequence[ConsumerPlan], reused: bool) -> LandingJournal:
    return LandingJournal(
        landing_id=frame.landing_id,
        surface=frame.surface,
        phase="prepared",
        new_corpus_fingerprint=frame.fingerprint,
        corpus_entry_count=frame.entry_count,
        route_digest=_route_digest_now(frame.root, frame.surface),
        ownership_digest=_ownership_digest(frame.root, frame.surface),
        consumers=tuple(plans),
        attestor=frame.attestor,
        attestation_text=frame.attestation_text,
        attestation_reused=reused,
        created_ts=frame.created_ts,
    )


def prepare_landing(
    root: Path,
    surface: str,
    *,
    attestor: str,
    attestation_text: str,
    retention_maps: Sequence[str] = (),
) -> LandingPlan:
    """Prepare the landing of *surface* across every routed consumer; write nothing.

    Order: the corpus exists; the routed consumer set is non-empty; each
    consumer's candidate is generated and its lineage verified; the attestation
    is resolved (Requirement 5); each candidate passes the retention gate; every
    artifact's bytes are built with ONE shared ``landing_id``.

    Raises:
        LandingRefusal: on any refusal; nothing has been written.

    """
    _owner, consumers = _resolve_consumers(root, surface)
    corpus = load_corpus(root, surface)
    generated = [_generate_and_verify(root, surface, consumer) for consumer in consumers]
    fingerprint = corpus_fingerprint(corpus)
    effective_attestor, effective_text, reused = _resolve_attestation(
        generated, fingerprint, attestor, attestation_text
    )
    bound_maps = _bind_retention_maps(surface, consumers, retention_maps)
    retained = {
        g.consumer: _retention_gate(root, surface, g, bound_maps.get(g.consumer), attestation_text)
        for g in generated
    }
    frame = _new_frame(root, surface, corpus, (effective_attestor, effective_text))
    payloads: dict[str, bytes] = {}
    notes: list[str] = []
    plans: list[ConsumerPlan] = []
    for g in generated:
        plan, data, lines = _consumer_slice(frame, g, retained[g.consumer])
        plans.append(plan)
        payloads.update(data)
        notes.extend(lines)
    journal = _assemble_journal(frame, plans, reused)
    return LandingPlan(journal=journal, payloads=payloads, notes=tuple(notes))


# --------------------------------------------------------------------------- #
# Publication (journaled, per-file atomic replacement; ratified amendment)    #
# --------------------------------------------------------------------------- #
#
# prepared -> publishing -> verified -> complete. The journal is written BEFORE
# the first artifact byte and cleared LAST, after the one completion event is
# durable. Replacement is atomic per FILE, never across the set: a crash
# mid-publication leaves mixed bytes that the retained journal describes.

_JOURNAL_NAME = ".landing.json"
_LOCK_NAME = ".landing"
_STAGING_PREFIX = ".landing-staging-"


def journal_path(root: Path, surface: str) -> Path:
    """Return the active landing journal of *surface* (inside its rendition directory)."""
    return root / surface_rendition_dir(surface) / _JOURNAL_NAME


def staging_path(root: Path, surface: str, landing_id: str) -> Path:
    """Return the staging directory landing *landing_id* stages its new bytes in."""
    return root / surface_rendition_dir(surface) / f"{_STAGING_PREFIX}{landing_id}"


def load_journal(root: Path, surface: str) -> LandingJournal | None:
    """Load *surface*'s active landing journal, or ``None`` when no landing is in flight.

    Raises:
        LandingRefusal: exit 1 when the journal is unreadable or malformed --
            malformed state is an error, never an absent landing.

    """
    path = journal_path(root, surface)
    if not path.exists():
        return None
    try:
        journal = LandingJournal.model_validate_json(path.read_bytes())
        if journal.surface != surface:
            msg = f"it records surface {journal.surface!r}, not {surface!r}"
            raise ValueError(msg)
    except (OSError, ValueError) as exc:
        raise LandingRefusal(
            1,
            f"Error: the landing journal {path.as_posix()!r} is unreadable or malformed: "
            f"{exc}.\n"
            "Why forbidden: the journal is the only common record of an interrupted "
            "landing; guessing its contents could overwrite files it never verified.\n"
            f"Next: restore the rendition, provenance and lineage artifacts of {surface!r} "
            "together with `git restore --source=<known-good-revision> --staged --worktree "
            f"-- {surface_rendition_dir(surface).as_posix()}/` (a pathspec checkout of that "
            "revision would leave newer lineage/retention sidecars behind), remove the "
            "journal, then re-run `gz content land`.",
        ) from exc
    return journal


def _write_journal(root: Path, journal: LandingJournal) -> None:
    data = (journal.model_dump_json(indent=2) + "\n").encode("utf-8")
    write_bytes_atomically(journal_path(root, journal.surface), data)


def _current_sha(root: Path, relpath: str) -> str | None:
    data = _read_optional(root / relpath)
    return sha256_hex(data) if data is not None else None


def _stage_artifact(path: Path, data: bytes) -> None:
    """Write and fsync one staged artifact (a named boundary for interruption tests)."""
    with path.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _replace_artifact(root: Path, staging: Path, artifact: ArtifactTarget) -> None:
    """Publish one artifact from its staged bytes, or remove it; atomic per file."""
    target = root / artifact.path
    if artifact.new_sha256 is None:
        target.unlink(missing_ok=True)
        commit_directory_entry(target.parent)
        return
    data = (staging / PurePosixPath(artifact.path).name).read_bytes()
    if sha256_hex(data) != artifact.new_sha256:
        msg = f"staged bytes for {artifact.path} no longer match the journal's new_sha256"
        raise OSError(msg)
    write_bytes_atomically(target, data)


def _clear_landing(root: Path, journal: LandingJournal) -> None:
    """Remove the staging directory, then the journal, then take the directory barrier."""
    staging = staging_path(root, journal.surface, journal.landing_id)
    if staging.exists():
        for child in staging.iterdir():
            child.unlink()
        staging.rmdir()
    path = journal_path(root, journal.surface)
    path.unlink(missing_ok=True)
    commit_directory_entry(path.parent)


def _refuse_active_landing(root: Path, surface: str) -> None:
    active = load_journal(root, surface)
    if active is None:
        return
    raise LandingRefusal(
        1,
        f"Error: landing {active.landing_id} of {surface!r} is still in flight (phase "
        f"{active.phase}, journal {journal_path(root, surface).as_posix()!r}). Nothing was "
        "written for any consumer.\n"
        "Why forbidden: a second landing would interleave writes with an unfinished one, "
        "and the retained journal is the only common record of what that landing intended.\n"
        f"Next: inspect it with `gz content land {surface} --status {active.landing_id}` and "
        f"resume it with `gz content land {surface}`; if it cannot be resumed, restore the "
        "rendition, provenance and lineage artifacts together with `git restore "
        f"--source=<known-good-revision> --staged --worktree -- "
        f"{surface_rendition_dir(surface).as_posix()}/`.",
    )


def _input_drift(root: Path, journal: LandingJournal) -> list[str]:
    """Return how the corpus, route or ownership inputs moved since *journal* was prepared."""
    surface = journal.surface
    problems: list[str] = []
    if corpus_fingerprint(load_corpus(root, surface)) != journal.new_corpus_fingerprint:
        problems.append("the corpus changed since the plan was prepared")
    if _route_digest_now(root, surface) != journal.route_digest:
        problems.append("the surface's consumer route changed")
    if _ownership_digest(root, surface) != journal.ownership_digest:
        problems.append("the ownership declaration changed")
    return problems


def _drift_problems(root: Path, journal: LandingJournal) -> list[str]:
    problems = _input_drift(root, journal)
    problems.extend(
        f"{artifact.path} changed on disk since preparation"
        for consumer in journal.consumers
        for artifact in consumer.artifacts
        if _current_sha(root, artifact.path) != artifact.old_sha256
    )
    return problems


def _refuse_drift(root: Path, journal: LandingJournal) -> None:
    try:
        problems = _drift_problems(root, journal)
    except (OSError, ValueError) as exc:
        problems = [f"the inputs could not be re-read: {exc}"]
    if problems:
        findings = "\n".join(f"- {problem}" for problem in problems)
        raise _refusal(
            1,
            f"the inputs of landing {journal.landing_id} changed after preparation:\n{findings}\n",
            "a landing publishes only the plan it prepared and verified; landing a plan over "
            "changed inputs would attest bytes nobody reviewed.",
            f"re-run `gz content land {journal.surface}` to prepare against the current inputs.",
        )


def _begin(root: Path, plan: LandingPlan) -> Path:
    """Write the journal (phase prepared), then stage and fsync every new artifact byte."""
    journal = plan.journal
    staging = staging_path(root, journal.surface, journal.landing_id)
    try:
        _write_journal(root, journal)
        staging.mkdir(parents=True, exist_ok=True)
        for consumer in journal.consumers:
            for artifact in consumer.artifacts:
                if artifact.new_sha256 is not None:
                    name = PurePosixPath(artifact.path).name
                    _stage_artifact(staging / name, plan.payloads[artifact.path])
        commit_directory_entry(staging)
    except OSError as exc:
        cleanup_problem = ""
        try:
            _clear_landing(root, journal)
        except OSError as cleanup_exc:
            cleanup_problem = (
                f" Cleanup also failed: {cleanup_exc}. The journal may remain at "
                f"{journal_path(root, journal.surface).as_posix()!r}; "
                f"`gz content land {journal.surface}` will resume it, or `--status "
                f"{journal.landing_id}` will classify it."
            )
        raise _refusal(
            2,
            f"staging landing {journal.landing_id} failed: {exc}.{cleanup_problem}",
            "every consumer's artifacts are staged and made durable before any committed "
            "file is replaced, so a staging failure must leave the committed set untouched.",
            "repair the IO condition named above, then re-run "
            f"`gz content land {journal.surface}`.",
        ) from exc
    return staging


def _foreign_edit(root: Path, journal: LandingJournal, path: str) -> LandingRefusal:
    surface, landing_id = journal.surface, journal.landing_id
    return LandingRefusal(
        2,
        f"Error: landing {landing_id} of {surface!r} detected a concurrent edit to "
        f"{path} -- it was NOT overwritten and the landing journal is retained.\n"
        "Why forbidden: a compare-and-swap at the replacement boundary protects against "
        "concurrent edits made during staging or after resume checks; a file whose bytes "
        "are neither the old committed state nor the new prepared state has been edited "
        "outside the landing transaction and must not be silently replaced.\n"
        f"Next: inspect the landing with `gz content land {surface} --status {landing_id}`; "
        f"discard the concurrent edit with `git restore --source=<known-good-revision> "
        f"--staged --worktree -- {surface_rendition_dir(surface).as_posix()}/`, "
        f"then resume with `gz content land {surface}`. To keep the edit, remove the journal "
        f"{journal_path(root, surface).as_posix()!r} only after a governed decision to "
        f"abandon landing {landing_id}, then run `gz content land {surface}` to prepare and "
        "attest a fresh landing.",
    )


def _incomplete(journal: LandingJournal, what: str) -> LandingRefusal:
    surface, landing_id = journal.surface, journal.landing_id
    return LandingRefusal(
        2,
        f"Error: landing {landing_id} of {surface!r} is incomplete -- {what}\n"
        "The landing journal is retained and no completion event was recorded; readers may "
        "observe mixed bytes until the landing completes.\n"
        "Why forbidden: publication replaces one file at a time (ratified Publication "
        "Amendment), so a landing whose every target is not verified against its recorded "
        "hash may not claim success.\n"
        f"Next: inspect each consumer with `gz content land {surface} --status {landing_id}`, "
        f"then resume with `gz content land {surface}`, which reuses the recorded attestation "
        "and never rewrites a verified file. Rollback is `git restore "
        f"--source=<known-good-revision> --staged --worktree -- "
        f"{surface_rendition_dir(surface).as_posix()}/`.",
    )


def _mark_published(journal: LandingJournal, index: int) -> LandingJournal:
    consumers = list(journal.consumers)
    done = consumers[index]
    consumers[index] = done.model_copy(
        update={
            "artifacts": tuple(a.model_copy(update={"published": True}) for a in done.artifacts)
        }
    )
    return journal.model_copy(update={"consumers": tuple(consumers)})


def _publish(root: Path, journal: LandingJournal, staging: Path) -> LandingJournal:
    """Replace every target from staging, persisting progress after each consumer.

    Compare-and-swap at the replacement boundary: for each artifact, read its current
    SHA-256 and compare against both the old committed state and the new prepared state.
    If current SHA equals new_sha256, skip (already correct). If current SHA equals old_sha256,
    replace (proceed with publication). Otherwise, a concurrent edit has been detected and
    the landing refuses with exit 2 without touching that file, keeping the journal and
    recording no event.

    Residual: a write in the instant between the hash read and the replacement is not detected.
    Other gz landings are excluded by the surface lock.
    """
    journal = journal.model_copy(update={"phase": "publishing"})
    _write_journal(root, journal)
    for index, consumer in enumerate(journal.consumers):
        for artifact in consumer.artifacts:
            current = _current_sha(root, artifact.path)
            # Skip if already at target state
            if current == artifact.new_sha256:
                continue
            # Replace if at old state
            if current == artifact.old_sha256:
                _replace_artifact(root, staging, artifact)
                continue
            # Foreign edit detected
            raise _foreign_edit(root, journal, artifact.path)
        journal = _mark_published(journal, index)
        _write_journal(root, journal)
    return journal


def _verify_sidecar(root: Path, journal: LandingJournal, consumer: str) -> list[str]:
    try:
        sidecar = load_fingerprint(root, journal.surface, consumer)
    except (OSError, ValueError) as exc:
        return [f"{consumer}: provenance sidecar is unreadable ({type(exc).__name__})"]
    if sidecar is None:
        return [f"{consumer}: provenance sidecar is missing"]
    expected = (
        journal.landing_id,
        journal.attestor,
        journal.attestation_text,
        journal.new_corpus_fingerprint,
    )
    actual = (
        sidecar.landing_id,
        sidecar.attestor,
        sidecar.attestation_text,
        sidecar.corpus_fingerprint,
    )
    if actual != expected:
        return [f"{consumer}: sidecar does not carry this landing's id, attestation and corpus"]
    return []


def _verify_lineage(root: Path, surface: str, consumer: str) -> list[str]:
    """Re-run the 06 lineage verification on the PUBLISHED rendition/lineage pair."""
    from gzkit.governance.trust_audits.rendition_lineage import (  # noqa: PLC0415
        verify_candidate_against_declaration,
    )

    try:
        text = rendition_path(root, surface, consumer).read_bytes().decode("utf-8")
        document = json.loads(lineage_path(root, surface, consumer).read_bytes())
        lineage = ConsumerLineage(
            surface=surface,
            consumer=consumer,
            sections={k: SectionLineage.model_validate(v) for k, v in document.items()},
        )
        declaration = load_declaration(declaration_path(root, surface), text, root)
        problems = verify_candidate_against_declaration(
            text, text, lineage, load_corpus(root, surface), declaration
        )
    except (OSError, ValueError) as exc:
        return [f"{consumer}: published lineage could not be verified: {exc}"]
    return [f"{consumer}: {problem}" for problem in problems]


def _verify(root: Path, journal: LandingJournal) -> list[str]:
    """Hash every target against its recorded new state, then check sidecars and lineage."""
    problems = [
        f"{artifact.path}: on-disk state does not match the recorded new_sha256"
        for consumer in journal.consumers
        for artifact in consumer.artifacts
        if _current_sha(root, artifact.path) != artifact.new_sha256
    ]
    if problems:
        return problems
    for consumer in journal.consumers:
        problems.extend(_verify_sidecar(root, journal, consumer.consumer))
        problems.extend(_verify_lineage(root, journal.surface, consumer.consumer))
    return problems


def landed_event(journal: LandingJournal) -> RenditionLandedEvent:
    """Build the one ``rendition_landed`` event, id ``rendition-landed-<landing_id>``."""
    return RenditionLandedEvent(
        event="rendition_landed",
        id=f"rendition-landed-{journal.landing_id}",
        surface=journal.surface,
        landing_id=journal.landing_id,
        corpus_fingerprint=journal.new_corpus_fingerprint,
        corpus_entry_count=journal.corpus_entry_count,
        attestor=journal.attestor,
        attestation_text=journal.attestation_text,
        attestation_reused=journal.attestation_reused,
        consumers=[
            LandedConsumer(
                consumer=consumer.consumer,
                old_corpus_fingerprint=consumer.old_corpus_fingerprint,
                artifacts=[
                    LandedArtifact(
                        kind=a.kind, path=a.path, old_sha256=a.old_sha256, new_sha256=a.new_sha256
                    )
                    for a in consumer.artifacts
                ],
            )
            for consumer in journal.consumers
        ],
    )


def complete_landing(root: Path, journal: LandingJournal) -> None:
    """Record the one completion event (idempotent by id), then clear the journal LAST.

    Safe to re-run after a crash between the event and the cleanup: the event
    is appended only when the ledger does not already hold its id.

    Raises:
        LandingRefusal: exit 2 when the event or the cleanup cannot be made durable.

    """
    try:
        event_id = emit_rendition_landed(root, landed_event(journal))
    except OSError as exc:
        raise _incomplete(journal, f"the completion event could not be recorded: {exc}") from exc
    try:
        _clear_landing(root, journal)
    except OSError as exc:
        raise LandingRefusal(
            2,
            f"Error: landing {journal.landing_id} is published and its completion event "
            f"{event_id} is recorded, but clearing the landing journal failed: {exc}.\n"
            "Why forbidden: the journal is cleared LAST so a crash can never lose the record "
            "of an unfinished landing; while it remains, new landings of this surface refuse.\n"
            f"Next: repair the IO condition, then re-run `gz content land {journal.surface}` to "
            "finish completion; the event is never recorded twice.",
        ) from exc


def publish_landing(root: Path, plan: LandingPlan) -> LandingJournal:
    """Publish *plan* through the durable landing journal; return the completed journal.

    Under the surface lock: refuse an in-flight landing and any input drift
    (exit 1, nothing written); write the journal, stage every artifact (a
    failure removes both, exit 2); replace per file, persisting progress (a
    failure keeps the journal, exit 2); verify every hash, sidecar and lineage
    (a mismatch keeps the journal, exit 2); then :func:`complete_landing`.

    Raises:
        LandingRefusal: on any refusal or incomplete publication.

    """
    journal = plan.journal
    directory = root / surface_rendition_dir(journal.surface)
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(directory / _LOCK_NAME):
        _refuse_active_landing(root, journal.surface)
        _refuse_drift(root, journal)
        staging = _begin(root, plan)
        return _finish(root, journal, staging)


def _finish(root: Path, journal: LandingJournal, staging: Path) -> LandingJournal:
    """Publish, verify, record ``verified``, then complete -- shared by land and resume.

    Publication skips every artifact already at its new hash, so a resumed
    landing never rewrites a verified file; completion is idempotent by event id.
    """
    try:
        journal = _publish(root, journal, staging)
    except OSError as exc:
        raise _incomplete(journal, f"publication stopped: {exc}") from exc
    problems = _verify(root, journal)
    if problems:
        findings = "\n".join(f"- {problem}" for problem in problems)
        raise _incomplete(journal, f"verification failed:\n{findings}")
    journal = journal.model_copy(update={"phase": "verified"})
    try:
        _write_journal(root, journal)
    except OSError as exc:
        raise _incomplete(journal, f"the verified phase could not be recorded: {exc}") from exc
    complete_landing(root, journal)
    return journal.model_copy(update={"phase": "complete"})


def _resume_problems(
    root: Path, journal: LandingJournal, staging: Path
) -> tuple[list[str], list[str]]:
    """Return ``(drift, staging)`` reasons the journaled landing may not simply continue.

    Drift -- moved inputs or a file at neither recorded hash -- always refuses.
    Missing or altered staged bytes are recoverable only in phase ``prepared``
    with nothing published (see :func:`_restage_prepared`).
    """
    try:
        problems = _input_drift(root, journal)
    except (OSError, ValueError) as exc:
        problems = [f"the inputs could not be re-read: {exc}"]
    staged_problems: list[str] = []
    for consumer in journal.consumers:
        for artifact in consumer.artifacts:
            current = _current_sha(root, artifact.path)
            if current not in (artifact.old_sha256, artifact.new_sha256):
                problems.append(
                    f"{artifact.path} matches neither its old nor its new manifest entry "
                    "(edited outside the landing)"
                )
            elif current != artifact.new_sha256 and artifact.new_sha256 is not None:
                staged = _read_optional(staging / PurePosixPath(artifact.path).name)
                if staged is None or sha256_hex(staged) != artifact.new_sha256:
                    staged_problems.append(
                        f"the staged bytes for {artifact.path} are missing or no longer hash "
                        "to its new manifest entry"
                    )
    return problems, staged_problems


def _nothing_published(root: Path, journal: LandingJournal) -> bool:
    return all(
        _current_sha(root, artifact.path) == artifact.old_sha256
        for consumer in journal.consumers
        for artifact in consumer.artifacts
    )


def _regenerate_payloads(root: Path, journal: LandingJournal) -> dict[str, bytes]:
    """Regenerate a ``prepared`` landing's bytes from the journal's own recorded values.

    The frame reuses the journal's landing_id, attestor, attestation text and
    ``created_ts`` -- the value every sidecar's ``committed_ts`` is built from
    on a fresh landing too -- so generation over unchanged inputs reproduces
    the exact bytes the journal hashed. A retention sidecar is never
    regenerated (the gate is never re-run on resume, Requirement 12): its
    reviewed text, recorded in the journal at preparation, is reused. Every
    payload must hash to the journal's ``new_sha256``, or the landing refuses
    (exit 1).
    """
    corpus = load_corpus(root, journal.surface)
    frame = _Frame(
        root=root,
        surface=journal.surface,
        fingerprint=corpus_fingerprint(corpus),
        entry_count=len(corpus.entries),
        attestor=journal.attestor,
        attestation_text=journal.attestation_text,
        landing_id=journal.landing_id,
        created_ts=journal.created_ts,
    )
    payloads: dict[str, bytes] = {}
    for consumer in journal.consumers:
        generated = _generate_and_verify(root, journal.surface, consumer.consumer)
        _plan, data, _notes = _consumer_slice(frame, generated, None)
        payloads.update(data)
        if consumer.retention_payload is not None:
            path = artifact_relpath(journal.surface, consumer.consumer, "retention")
            payloads[path] = consumer.retention_payload.encode("utf-8")
    mismatched = [
        artifact.path
        for consumer in journal.consumers
        for artifact in consumer.artifacts
        if artifact.new_sha256 is not None
        and (
            artifact.path not in payloads
            or sha256_hex(payloads[artifact.path]) != artifact.new_sha256
        )
    ]
    if mismatched:
        findings = "\n".join(f"- {path}" for path in mismatched)
        raise _refusal(
            1,
            f"landing {journal.landing_id} was interrupted while staging, and regenerating its "
            f"bytes does not reproduce the journal's new_sha256 for:\n{findings}\n",
            "resume publishes only the bytes the landing's one attestation covered; bytes "
            "that differ from the recorded manifest were never attested.",
            f"nothing was published, so the committed set is unchanged: remove the journal "
            f"{journal_path(root, journal.surface).as_posix()!r} after a governed decision to "
            f"abandon landing {journal.landing_id}, then run `gz content land "
            f"{journal.surface}` to prepare and attest a fresh landing.",
        )
    return payloads


def _restage_prepared(root: Path, journal: LandingJournal, staging: Path) -> None:
    """Re-stage every new artifact of a ``prepared`` landing from regenerated bytes."""
    payloads = _regenerate_payloads(root, journal)
    try:
        staging.mkdir(parents=True, exist_ok=True)
        for path, data in payloads.items():
            _stage_artifact(staging / PurePosixPath(path).name, data)
        commit_directory_entry(staging)
    except OSError as exc:
        raise _refusal(
            2,
            f"re-staging landing {journal.landing_id} failed: {exc}.",
            "every artifact is staged and made durable before any committed file is "
            "replaced; the journal is retained so the landing stays resumable.",
            f"repair the IO condition named above, then re-run `gz content land "
            f"{journal.surface}`.",
        ) from exc


def resume_landing(root: Path, surface: str) -> LandingJournal:
    """Resume *surface*'s interrupted landing; return the completed journal (REQ-07/08).

    Reuses the journal's recorded attestor, attestation text and landing id --
    the attestation is on the corpus delta, not on the write, so resume never
    asks for another. Under the surface lock it requires the same corpus, route
    and ownership inputs, every artifact at its old or new hash, and intact
    staged bytes for every artifact not yet at its new hash; anything else
    refuses automatic overwrite (exit 1, nothing written). The one exception is
    a landing killed while staging -- phase ``prepared``, nothing published --
    whose bytes are regenerated from the journal's recorded values and must
    reproduce its manifest exactly. Then it continues through the same
    publication path a fresh landing uses.

    Raises:
        LandingRefusal: on a missing, malformed or unresumable landing, or an
            incomplete publication.

    """
    directory = root / surface_rendition_dir(surface)
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(directory / _LOCK_NAME):
        journal = load_journal(root, surface)
        if journal is None:
            raise _refusal(
                1,
                f"no landing of {surface!r} is in flight to resume.",
                "resume continues only a landing whose journal records what it intended; "
                "with none there is nothing to continue.",
                f"start a landing with `gz content land {surface}`.",
            )
        staging = staging_path(root, surface, journal.landing_id)
        problems, staged_problems = _resume_problems(root, journal, staging)
        if (
            not problems
            and staged_problems
            and journal.phase == "prepared"
            and _nothing_published(root, journal)
        ):
            # Killed while staging: nothing published, so the attested plan is
            # regenerated from the unchanged inputs and re-staged (REQ-08).
            _restage_prepared(root, journal, staging)
            staged_problems = []
        problems += staged_problems
        if problems:
            findings = "\n".join(f"- {problem}" for problem in problems)
            raise _refusal(
                1,
                f"landing {journal.landing_id} of {surface!r} cannot be resumed "
                f"automatically:\n{findings}\n",
                "resume publishes only the plan the landing's one attestation covered, over "
                "files still at a recorded state; overwriting drifted inputs or foreign edits "
                "would land bytes nobody attested.",
                f"inspect each consumer with `gz content land {surface} --status "
                f"{journal.landing_id}`; restore the rendition, provenance and lineage "
                "artifacts together with `git restore --source=<known-good-revision> "
                f"--staged --worktree -- {surface_rendition_dir(surface).as_posix()}/` "
                "(committed renditions keep no prior version); remove the journal "
                f"{journal_path(root, surface).as_posix()!r} only after a governed decision "
                "to abandon this landing.",
            )
        return _finish(root, journal, staging)


# --------------------------------------------------------------------------- #
# Status (read-only; hashes and provenance, never mtimes)                     #
# --------------------------------------------------------------------------- #


class ConsumerStatus(BaseModel):
    """One consumer's verdict: which recorded manifest its CURRENT bytes match."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    consumer: str = Field(..., min_length=1, description="Routed vendor consumer")
    verdict: ConsumerVerdict = Field(..., description="new, old or indeterminate")
    findings: tuple[str, ...] = Field(
        default=(), description="Why the consumer is indeterminate; empty otherwise"
    )
    recovery: str | None = Field(
        None, description="Three-part recovery prose for an indeterminate verdict"
    )


class LandingStatus(BaseModel):
    """The read-only verdict of ``gz content land <surface> --status <landing_id>``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    landing_id: str = Field(..., description="The landing classified")
    surface: str = Field(..., description="Control surface of the landing")
    phase: LandingPhase = Field(..., description="Journal phase, or complete from the event")
    source: Literal["journal", "ledger"] = Field(
        ..., description="Where the old/new manifest was read from"
    )
    new_corpus_fingerprint: str = Field(..., description="Corpus fingerprint the landing lands")
    consumers: tuple[ConsumerStatus, ...] = Field(..., description="Verdict per consumer")


class _Manifest(BaseModel):
    """The old/new manifest of one landing, from its journal or its completion event."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    landing_id: str
    surface: str
    phase: LandingPhase
    source: Literal["journal", "ledger"]
    new_corpus_fingerprint: str
    consumers: tuple[ConsumerPlan, ...]


def _manifest_from_event(surface: str, landing_id: str, extra: Mapping[str, object]) -> _Manifest:
    """Rebuild the manifest from a ``rendition_landed`` row, validating every path."""
    try:
        records = extra["consumers"]
        if not isinstance(records, list) or not records:
            msg = "it carries no consumer manifest"
            raise ValueError(msg)
        consumers = tuple(ConsumerPlan.model_validate(record) for record in records)
        for plan in consumers:
            for artifact in plan.artifacts:
                if artifact.path != artifact_relpath(surface, plan.consumer, artifact.kind):
                    msg = f"path {artifact.path!r} is not {plan.consumer!r}'s {artifact.kind}"
                    raise ValueError(msg)
        fingerprint = str(extra["corpus_fingerprint"])
        _check_sha(fingerprint)
    except (KeyError, ValueError) as exc:
        raise LandingRefusal(
            1,
            f"Error: the rendition_landed event of landing {landing_id} is malformed: {exc}.\n"
            "Why forbidden: status classifies consumers only against a manifest whose every "
            "path is the surface's own artifact; a malformed manifest is no witness.\n"
            "Next: inspect the event in .gzkit/ledger.jsonl, and restore the rendition, "
            "provenance and lineage artifacts together with `git restore "
            f"--source=<known-good-revision> --staged --worktree -- "
            f"{surface_rendition_dir(surface).as_posix()}/` if their state is in doubt.",
        ) from exc
    return _Manifest(
        landing_id=landing_id,
        surface=surface,
        phase="complete",
        source="ledger",
        new_corpus_fingerprint=fingerprint,
        consumers=consumers,
    )


def _find_manifest(root: Path, surface: str, landing_id: str) -> _Manifest:
    journal = load_journal(root, surface)
    if journal is not None and journal.landing_id == landing_id:
        return _Manifest(
            landing_id=landing_id,
            surface=surface,
            phase=journal.phase,
            source="journal",
            new_corpus_fingerprint=journal.new_corpus_fingerprint,
            consumers=journal.consumers,
        )
    ledger_file = root / ".gzkit" / "ledger.jsonl"
    rows = Ledger(ledger_file).read_all() if ledger_file.exists() else []
    for row in rows:
        if (
            row.event == "rendition_landed"
            and row.extra.get("landing_id") == landing_id
            and row.extra.get("surface") == surface
        ):
            return _manifest_from_event(surface, landing_id, row.extra)
    raise _refusal(
        1,
        f"no landing {landing_id!r} of {surface!r} is in flight or recorded.",
        "status classifies consumers only against a landing's recorded old/new manifest; "
        "without one there is nothing to compare the files to.",
        "check the id against the `rendition_landed` events in .gzkit/ledger.jsonl or the "
        f"journal at {journal_path(root, surface).as_posix()!r}, then re-run "
        f"`gz content land {surface} --status <landing_id>`.",
    )


def _indeterminate_recovery(manifest: _Manifest, consumer: str) -> str:
    surface, landing_id = manifest.surface, manifest.landing_id
    return (
        f"Error: consumer {consumer!r} of landing {landing_id} is indeterminate -- its "
        "current bytes match neither the landing's old nor its new manifest as a whole.\n"
        "Why forbidden: only a consumer whose every artifact hashes to one recorded state "
        "can be called landed or untouched; mtimes and sidecar claims are no witness.\n"
        f"Next: restore the whole surface's rendition set with `git restore "
        f"--source=<known-good-revision> --staged --worktree -- "
        f"{surface_rendition_dir(surface).as_posix()}/` (committed renditions keep no prior "
        f"version) -- this repairs {consumer!r} too; a pathspec checkout of that revision "
        "leaves newer lineage/retention sidecars behind and reproduces this same mixed set. "
        f"Then re-run `gz content land {surface} --status {landing_id}`; resume with "
        f"`gz content land {surface}` only once no consumer is indeterminate."
    )


def _classify(root: Path, manifest: _Manifest, plan: ConsumerPlan) -> ConsumerStatus:
    """Classify one consumer by hashing every recorded artifact's CURRENT bytes."""
    findings: list[str] = []
    at_new = at_old = 0
    for artifact in plan.artifacts:
        current = _current_sha(root, artifact.path)
        at_new += current == artifact.new_sha256
        at_old += current == artifact.old_sha256
        if current not in (artifact.new_sha256, artifact.old_sha256):
            state = "absent" if current is None else f"sha256 {current[:12]}..."
            findings.append(
                f"{artifact.path}: {state} matches neither its old nor its new manifest entry"
            )
    if at_new == len(plan.artifacts):
        # The provenance sidecar is one of the hashed artifacts, and its bytes
        # carry the landing_id and corpus fingerprint, so a hash match already
        # proves the sidecar names this landing; no separate claim check can
        # disagree with it.
        return ConsumerStatus(consumer=plan.consumer, verdict="new")
    if at_old == len(plan.artifacts):
        return ConsumerStatus(consumer=plan.consumer, verdict="old")
    if not findings:
        findings.append(
            f"{plan.consumer}: some artifacts are at the new state and others at the old "
            "(publication stopped inside this consumer)"
        )
    return ConsumerStatus(
        consumer=plan.consumer,
        verdict="indeterminate",
        findings=tuple(findings),
        recovery=_indeterminate_recovery(manifest, plan.consumer),
    )


def landing_status(root: Path, surface: str, landing_id: str) -> LandingStatus:
    """Classify every consumer of landing *landing_id*; read-only (REQ-0.35.0-07-06).

    The manifest comes from the surface's active journal when it holds this
    landing, otherwise from the landing's ``rendition_landed`` event. A consumer
    is ``new`` when every artifact hashes to its new entry AND its provenance
    sidecar names the new corpus fingerprint and this landing, ``old`` when
    every artifact hashes to its old entry, and ``indeterminate`` otherwise.
    Takes no lock, writes nothing, emits nothing, and never reads an mtime.

    Raises:
        LandingRefusal: exit 1 for an unknown landing or a malformed record.

    """
    manifest = _find_manifest(root, surface, landing_id)
    return LandingStatus(
        landing_id=landing_id,
        surface=surface,
        phase=manifest.phase,
        source=manifest.source,
        new_corpus_fingerprint=manifest.new_corpus_fingerprint,
        consumers=tuple(_classify(root, manifest, plan) for plan in manifest.consumers),
    )


__all__ = [
    "ArtifactKind",
    "ArtifactTarget",
    "ConsumerPlan",
    "ConsumerStatus",
    "ConsumerVerdict",
    "LandingJournal",
    "LandingPhase",
    "LandingPlan",
    "LandingRefusal",
    "LandingStatus",
    "artifact_relpath",
    "complete_landing",
    "journal_path",
    "landed_event",
    "landing_status",
    "lineage_bytes",
    "lineage_path",
    "load_journal",
    "new_landing_id",
    "prepare_landing",
    "provenance_bytes",
    "publish_landing",
    "resume_landing",
    "retention_bytes",
    "retention_path",
    "sha256_hex",
    "staging_path",
    "surface_rendition_dir",
]
