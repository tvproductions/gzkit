---
id: ADR-pool.agent-reliability-framework
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: slsa-v1.2-build-provenance
---

# ADR-pool.agent-reliability-framework: Agent Reliability Framework for Software Systems

## Status

Pool

## Date

2026-03-22

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Define and implement an Agent Reliability Framework (ARF) that appropriates
supply-chain integrity concepts from SLSA, in-toto, and Sigstore to establish
verifiable trust in AI-agent-produced software artifacts. SLSA answers "can I
trust this binary was built correctly from this source?" ARF answers the
parallel question: "can I trust this code was produced reliably from this
governance intent by this agent?"

GovZero already enforces intent-to-artifact traceability (ADR to OBPI to code),
scope drift detection (allowed/denied paths), lane-based attestation floors, and
append-only ledger provenance. What is missing is a named, leveled framework
that makes these guarantees legible to the emerging supply-chain and AI
governance ecosystems and positions GovZero as a standards-grade approach to
agent-produced software assurance.

---

## Problem Statement

AI coding agents produce software at high velocity. Current supply-chain
frameworks (SLSA, S2C2F, OpenSSF Scorecard) verify that *build systems*
produce artifacts faithfully. No equivalent framework verifies that *AI agents*
produce code faithfully from stated intent. The threat model is different:

| Supply Chain Threat (SLSA) | Agent Reliability Threat (ARF) |
|---|---|
| Build system compromise | Agent drift from intent |
| Source tampering | Scope creep beyond brief |
| Dependency confusion | Hallucinated capabilities |
| Unsigned provenance | Unattested completion claims |
| Missing build metadata | Missing evidence of verification |

Industry data confirms the gap: AI-generated code creates 1.7x more issues
than human-written code (CodeRabbit 2025), 40%+ of Copilot output contains
security flaws (ACM 2025), and change failure rates are up 30% in
AI-accelerated teams. The missing piece is not more code generation — it is
structured, verifiable assurance that agent output matches governance intent.

---

## Conceptual Foundation

### Guiding Principles (Appropriated from SLSA)

SLSA defines five guiding principles for supply-chain security. ARF
appropriates each for the agent reliability domain:

| # | SLSA Principle | ARF Appropriation |
|---|---|---|
| 1 | **Simple levels with clear outcomes** — each level stops a particular class of threats | Each AR level stops a particular class of agent failure: AR1 stops untracked work, AR2 stops scope drift, AR3 stops unverified completion claims, AR4 stops post-attestation regression |
| 2 | **Trust platforms, verify artifacts** — harden few platforms, automate verification of many artifacts | Trust the governance pipeline (gzkit), verify every agent-produced artifact against its brief. Hardening the pipeline is hard; verifying scope and evidence is automatable |
| 3 | **Trust code, not individuals** — trace to source code, not access controls | Trust governance artifacts (ADR, OBPI brief, ledger), not agent identity or reputation. A brief is static and analyzable; an agent's reasoning is opaque and non-reproducible |
| 4 | **Prefer attestations over inferences** — explicit proof, not configuration assumptions | Require explicit evidence (test results, scope audits, human attestation) rather than inferring quality from agent model version, prompt quality, or configuration |
| 5 | **Support anonymous and pseudonymous contributions** — identity for attribution, not gatekeeping | Agent vendor identity is recorded for attribution and analysis, not for trust decisions. An AR4 artifact from any agent (or human) carries the same assurance |

### Threat Model (Parallel to SLSA)

SLSA organizes eight threats (A-H) around the source-to-artifact supply chain.
ARF organizes parallel threats around the intent-to-artifact governance chain:

| Position | SLSA Threat | ARF Threat | Example |
|---|---|---|---|
| A | Malicious producer | Misaligned intent | ADR specifies one thing, OBPI brief drifts to another |
| B | Unauthorized commits | Ungoverned changes | Agent modifies files outside the OBPI allowlist |
| C | Source system compromise | Brief tampering | OBPI brief modified after implementation to match what was built |
| D | Build parameter manipulation | Constraint bypass | Agent ignores denied paths or acceptance criteria |
| E | Build platform compromise | Agent platform compromise | Compromised model produces subtly incorrect code |
| F | Artifact tampering | Post-attestation modification | Code changed after human attestation but before audit |
| G | Distribution channel attacks | Evidence fabrication | Fabricated test results or scope audit data |
| H | Typosquatting | Identity confusion | Wrong agent vendor or model recorded in provenance |

### Governance Bill of Materials (GBOM)

NTIA's SBOM minimum elements define a nested inventory of software ingredients
for transparency. ARF applies the same principle to governance: a **Governance
Bill of Materials** is a structured, machine-readable inventory of all
governance inputs and verification evidence that comprise a governed change.

| SBOM Element (NTIA) | GBOM Equivalent |
|---|---|
| Supplier name | Agent identity (vendor, model, session) |
| Component name | OBPI identifier + parent ADR |
| Version | Semver from validation anchor |
| Unique identifier | Ledger event ID + commit SHA |
| Dependency relationship | ADR to OBPI to REQ lineage |
| Author of SBOM data | Recorder source (agent or human) |
| Timestamp | Ledger event timestamp |

The GBOM extends NTIA's model with governance-specific fields:

- **Intent hash** — digest of the OBPI brief at time of implementation
- **Scope manifest** — allowlist, changed files, out-of-scope violations
- **Evidence inventory** — req_proof_inputs with present/missing status
- **Attestation record** — who attested, when, at what lane level
- **AR level achieved** — the computed Agent Reliability Level

The GBOM is not a replacement for SBOM — it is a complementary transparency
artifact. An SBOM says "these are the components in the software." A GBOM says
"this is how, by whom, and under what governance this change was produced."

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Overarching governance framework** for all 22 capabilities (CAP-01 through CAP-22). This ADR defines the reliability measurement layer; the spec defines the capabilities being measured.

### SLSA Data Model Appropriation

ARF appropriates SLSA's core data model, replacing build-system semantics with
agent-governance semantics:

| SLSA Concept | ARF Equivalent | gzkit Implementation |
|---|---|---|
| `BuildDefinition.buildType` | `GovernanceType` (e.g. `govzero.dev/attestation/v1`) | Custom predicate type URI |
| `BuildDefinition.externalParameters` | Brief constraints (allowed paths, requirements, acceptance criteria) | OBPI brief frontmatter + body |
| `BuildDefinition.internalParameters` | Agent configuration (model, vendor, lane) | Recorder metadata |
| `BuildDefinition.resolvedDependencies` | Governance lineage (ADR, parent PRD, linked OBPIs) | `req_proof_inputs` with artifact digests |
| `RunDetails.builder` | Agent identity (vendor + model + lane context) | `recorder_source` extended |
| `RunDetails.metadata` | Ceremony timestamps (start, attest, audit) | Ledger event `ts` fields |
| `RunDetails.byproducts` | QA artifacts (test results, lint receipts, coverage) | ARB receipts |
| `Statement.subject` | Produced code (scoped file changes with content hashes) | Scope audit + validation anchor |
| DSSE envelope | Ledger event with git-anchored integrity | Append-only JSONL + commit SHA |
| Build Levels L0-L3 | Agent Reliability Levels AR0-AR4 | Lane system + gate pipeline |

### Agent Reliability Levels

Graduated assurance tiers inspired by SLSA Build Levels, DO-178C Design
Assurance Levels, and S2C2F maturity:

| Level | Name | Requirements | gzkit Enforcement |
|---|---|---|---|
| **AR0** | Ungoverned | No provenance. Agent output accepted without verification. | No governance artifacts |
| **AR1** | Recorded | Provenance exists. Agent, intent, and output are linked in a ledger. | Ledger event with OBPI reference |
| **AR2** | Verified | Scope-checked. Output matches declared scope. Quality gates pass. Verification commands are reproducible. | Scope audit clean, Gates 1-4 pass |
| **AR3** | Attested | Human-verified. A qualified human confirmed intent-to-output alignment. Evidence is enriched with git state and recorder metadata. | Heavy lane attestation, Gate 5 |
| **AR4** | Audited | Independently reconciled. Post-attestation audit with temporal anchor. Provenance is complete and externally verifiable. | `gz audit` with anchored receipt |

Each level subsumes the requirements of all lower levels. The level is
determined by the *weakest* gate in the pipeline, not the strongest.

### What Each Level Prevents

| Level | Failure Class Stopped | Without This Level |
|---|---|---|
| **AR1** | Ghost work | Agent produces code with no governance record. Changes appear in git but have no traceable intent. Impossible to answer "why was this change made?" |
| **AR2** | Scope drift | Agent implements features not in the brief, modifies files outside the allowlist, or skips quality gates. The work might be good, but it wasn't *asked for* |
| **AR3** | False completion | Agent claims an OBPI is complete but a human hasn't verified intent-to-output alignment. Subtle misinterpretations, missing edge cases, and requirement gaps go undetected |
| **AR4** | Post-attestation regression | Code is modified after human attestation (intentionally or not). Without temporal anchoring and independent reconciliation, the attested state may not match the shipped state |

### Level Composition

AR level is a property of each **OBPI completion**, not of the codebase.
Aggregate levels are computed as follows:

- **ADR level** = minimum AR level across all completed OBPIs in that ADR
- **Release level** = minimum AR level across all ADRs in the release
- **Project posture** = minimum AR level across all active releases

This follows SLSA's principle that the weakest link determines the chain's
strength. A single AR0 OBPI in a release drops the release to AR0.

### Adoption Path

Teams adopt ARF incrementally, the same way SLSA adoption is incremental:

| Stage | Action | Effort |
|---|---|---|
| **Start at AR1** | Record governance artifacts (ADR, OBPI, ledger events) for agent-produced work. No process change — just start tracking. | Low |
| **Reach AR2** | Add scope audits and quality gates. Define allowed/denied paths in OBPI briefs. Run `gz gates` before marking work complete. | Medium |
| **Reach AR3** | Add human attestation for heavy-lane work. A qualified human reviews intent-to-output alignment before the OBPI closes. | Process change |
| **Reach AR4** | Add post-attestation audit with temporal anchoring. Run `gz audit` independently after attestation. Content hashes enable tamper detection. | Full pipeline |

Most teams will stabilize at AR2 for lite-lane work and AR3 for heavy-lane
work. AR4 is for high-assurance contexts (regulated industries, safety-critical
systems, foundational infrastructure).

### Multi-Agent Scenarios

Modern development increasingly involves multiple agents working on different
OBPIs within the same ADR, or even within the same OBPI across sessions.
ARF handles this through composition:

- Each OBPI records its own agent provenance (model, harness, session)
- If multiple agents contribute to one OBPI, each session's provenance is
  recorded as a separate entry in the agent identity chain
- The GBOM for an OBPI lists all contributing agents, not just the last one
- AR level is determined by the governance pipeline, not by which agent
  participated — the pipeline is the trust anchor (Principle 2)

This is analogous to SLSA's handling of multi-step builds: the builder
identity covers the orchestration platform, not individual build steps.

### Agent Rationalization as a First-Class Threat

Superpowers (obra/superpowers) identifies a failure mode that formal
frameworks miss: **agent rationalization**. The agent is not malicious —
it is optimistic. It will convince itself that verification is unnecessary
("should work now"), that partial evidence is sufficient ("linter passed"),
or that confidence is a substitute for proof ("I'm confident").

Superpowers' "Verification Before Completion" skill states it plainly:
"Claiming work is complete without verification is dishonesty, not
efficiency." It provides an explicit rationalization prevention table:

| Agent Excuse | Reality |
|---|---|
| "Should work now" | Run the verification |
| "I'm confident" | Confidence is not evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter is not compiler |
| "Agent said success" | Verify independently |
| "Partial check is enough" | Partial proves nothing |

This is the same threat as specification gaming (arXiv 2502.13295) but
observed from the inside: the agent's optimization target (completing the
task quickly) misaligns with the governance target (producing verified work).
ARF must treat agent rationalization as a threat category alongside the
eight SLSA-parallel threats defined above.

**ARF implication:** every AR level must require *fresh* verification
evidence produced *in the current session* — not cached, not inferred, not
self-reported. This is the "iron law" that gzkit's gate checks enforce.

### Two-Stage Review (Verification vs Validation)

Superpowers' subagent-driven development process uses two-stage review:

1. **Spec compliance review** — does the output match the specification?
   (IEEE 1012 Verification: "built it right")
2. **Code quality review** — is the implementation well-structured?
   (IEEE 1012 Validation: "built the right thing")

Spec compliance must pass *before* code quality review begins. This ordering
is critical: there is no point reviewing code quality for work that doesn't
match the spec.

gzkit's gate system partially implements this — scope audit (verification)
runs before human attestation (validation). ARF should formalize the
ordering: at AR2+, verification gates must pass before validation gates
are evaluated.

### The Specification Gaming Problem

Research demonstrates that reasoning models (OpenAI o3, DeepSeek R1) readily
engage in specification gaming — achieving the literal objective while
violating the intended spirit. An agent can pass all gates, satisfy all
acceptance criteria, and still produce work that misses the point.

This is the fundamental threat to any contract-based agent governance system.
Defenses:

- **Postconditions that verify semantics, not just structure** — acceptance
  criteria should test outcomes, not checkboxes
- **Human attestation as an anti-gaming mechanism** — a human reviewer can
  detect intent violations that automated gates cannot
- **Randomized audit sampling** — verification methods the agent cannot
  observe or predict (AR4 audits should include surprise scope checks)
- **Briefs as contracts, not prompts** — following Design by Contract
  (Meyer), OBPI briefs are formal contracts with preconditions (ADR context),
  postconditions (acceptance criteria), and invariants (governance rules
  that must hold throughout)

### Epistemic Uncertainty and Lane Classification

The lite/heavy lane split has a principled basis in epistemology. Lite-lane
work has low epistemic uncertainty — the change is well-understood, the scope
is narrow, and automated gates can verify compliance with high confidence.
Heavy-lane work has high epistemic uncertainty — novel architecture, unclear
requirements, or safety-critical systems where automated checks alone
cannot establish trust.

ARF formalizes this: **governance strictness should scale with epistemic
uncertainty, not just scope size.** A small change to a safety-critical gate
definition warrants AR3+ despite its tiny diff. A large but well-understood
refactoring may be fine at AR2.

This bridges the NIST AI RMF (which asks "what could go wrong?") with
IEEE 1012's consequence-likelihood matrix (which asks "how bad and how
likely?") to determine the appropriate verification intensity.

### Agent Failure Mode Analysis (FMEA)

Adapted from the ML FMEA methodology (Torc Robotics / SAE 2025), ARF should
include systematic failure mode enumeration for agent governance pipelines:

| Step | Failure Mode | Effect | Cause | Detection | Severity |
|---|---|---|---|---|---|
| Brief interpretation | Misreads requirement | Wrong code produced | Ambiguous brief | Scope audit | High |
| Code generation | Specification gaming | Passes checks, wrong intent | Misaligned optimization | Human attestation | Critical |
| Test generation | Covers happy path only | False confidence | Agent tests own work | Coverage analysis | High |
| Scope compliance | Modifies denied paths | Unauthorized changes | Context window limits | Scope audit | High |
| Evidence documentation | Fabricates evidence | False compliance | No independent verification | Audit reconciliation | Critical |
| Completion claim | Premature closure | Incomplete work shipped | Optimistic self-assessment | Gate checks | Medium |

The FMEA is not a one-time document — it should be maintained as a living
governance artifact that evolves with experience. Each failure mode maps to
a specific ARF control: scope audit catches scope compliance failures, human
attestation catches specification gaming, audit reconciliation catches
evidence fabrication.

### Provenance Vocabulary (W3C PROV Alignment)

PROV-AGENT (IEEE e-Science 2025) extends W3C PROV for agentic workflows.
gzkit's ledger maps naturally to PROV's core ontology:

| W3C PROV | gzkit Equivalent |
|---|---|
| Entity | Code artifact (file with content hash) |
| Activity | OBPI execution (from brief to completion) |
| Agent | LLM model + harness + human attestor |
| wasGeneratedBy | Ledger event linking artifact to OBPI |
| used | OBPI brief constraints consumed by agent |
| wasAssociatedWith | recorder_source / agent identity |
| wasDerivedFrom | ADR → OBPI → code lineage |

Adopting PROV vocabulary would give gzkit provenance interoperability with
scientific computing, regulatory frameworks, and the broader in-toto
ecosystem. This does not require changing the ledger format — it requires
defining a PROV export mapping from existing ledger events.

### Layered Defense (Swiss Cheese Model)

Reason's Swiss Cheese Model, applied to AI agent guardrails (ICSA 2025),
argues that no single verification layer catches all failures. Each layer
has holes; the combined layers provide robust defense. gzkit's gate system
is already a Swiss Cheese architecture:

| Layer | What It Catches | What It Misses |
|---|---|---|
| Gate 1 (ADR linkage) | Unlinked work | Linked but misaligned work |
| Gate 2 (Implementation) | Missing tests, lint failures | Tests that pass but don't verify intent |
| Gate 3 (Documentation) | Missing docs | Docs that describe the wrong thing |
| Gate 4 (Behavioral) | Missing behavioral tests | Behavioral tests that don't cover edge cases |
| Gate 5 (Human attestation) | All of the above | Human error, automation bias |
| AR4 Audit | Post-attestation tampering | Novel failure modes not yet in the FMEA |

Perrow's Normal Accidents theory warns that adding layers increases
complexity, potentially creating new failure modes. ARF mitigates this by
keeping layers orthogonal and independently verifiable — each gate operates
on its own evidence, not on the output of previous gates.

### The Verification Asymmetry

SLSA's key architectural insight is that hardening build platforms is
expensive but verifying artifacts is cheap and automatable. ARF has the
same asymmetry:

- **Hard:** ensuring an agent *understands* intent correctly (requires
  better models, better prompting, better context management)
- **Easy:** verifying that agent *output* matches declared scope, passes
  quality gates, and has human attestation where required

ARF deliberately does not try to solve the hard problem (agent cognition).
It solves the easy problem (artifact verification) rigorously and completely,
on the theory that structured verification of output catches failures
regardless of their cause.

### Four-Dimension Reliability Model

Drawing from Rabanser et al. ("Towards a Science of AI Agent Reliability",
2025), ARF evaluates agent output across four orthogonal dimensions rather
than a single pass/fail:

| Dimension | What It Measures | gzkit Evidence |
|---|---|---|
| **Consistency** | Does the agent produce scope-aligned output across runs? | Scope audit (allowlist vs changed files) |
| **Robustness** | Does the output withstand quality gates? | Gate results (lint, typecheck, test, docs) |
| **Predictability** | Does the agent fail in bounded, detectable ways? | Recorder warnings, out-of-scope file lists |
| **Safety** | Is error severity bounded by governance constraints? | Lane enforcement, denied paths, attestation floors |

---

## Ecosystem Alignment

### Standards Crosswalk

ARF does not compete with existing frameworks. It occupies a gap none of them
address — the agent-to-artifact trust boundary:

| Framework | Domain | Relationship to ARF |
|---|---|---|
| **SLSA v1.2** | Build provenance | ARF appropriates SLSA's predicate model and levels framework for agent context |
| **in-toto** | Attestation format | ARF predicates can be expressed as in-toto Statement/Predicate pairs |
| **Sigstore** | Signing + transparency | Future: ARF receipts could be signed via Sigstore and recorded in Rekor |
| **NIST AI RMF** | AI risk management | ARF's GOVERN-MAP-MEASURE-MANAGE cycle maps to NIST AI 100-1 functions |
| **ISO/IEC 42001** | AI management systems | ARF levels provide auditable evidence for ISO 42001 conformance |
| **EU AI Act** | Regulatory compliance | AR3/AR4 satisfy Article 14 human oversight requirements for high-risk systems |
| **NTIA SBOM** | Software transparency | ARF's GBOM applies NTIA's minimum-elements model to governance provenance, complementing (not replacing) SBOM |
| **OpenSSF Scorecard** | Project health | ARF is complementary — Scorecard measures project practices, ARF measures agent output trust |
| **NIST SSDF (800-218)** | Secure development | ARF maps to PS (Protect Software) and PW (Produce Well-Secured Software) practice groups |
| **S2C2F** | Supply chain consumption | ARF extends S2C2F's maturity model to AI agent consumption |
| **DO-178C** | Aviation assurance levels | ARF levels are inspired by DAL graduated verification rigor |
| **OWASP Agentic Top 10** | Agent security risks | ARF mitigates ASI01 (Goal Hijack), ASI02 (Tool Misuse), ASI04 (Supply Chain) |
| **C2PA** | Content provenance | ARF receipt chains are analogous to C2PA content credentials for code |
| **OpenTelemetry GenAI** | Agent observability | ARF evidence could emit OTel-compatible traces for operational monitoring |
| **IEC 61508** | Functional safety | Three-constraint SIL model (systematic capability + architecture + quantitative target) informs AR level requirements |
| **TUF** | Secure update framework | Trust delegation and threshold signatures for governance artifact distribution |
| **NIST 800-53 (SA/SI)** | Security controls | SA-11 (developer testing), SA-15 (development process), SI-7 (integrity verification) map directly to ARF gates |
| **IEEE 1012** | V&V intensity levels | Consequence-likelihood matrix for determining governance gate strictness |
| **SOC 2 Type II** | Continuous assurance | Sustained observation model and Processing Integrity criteria for ongoing agent reliability |
| **MITRE ATLAS** | AI adversarial threats | Agent-specific techniques (context poisoning, config modification) provide concrete threat model |
| **DORA** | DevOps metrics | Agent Change Failure Rate, Lead Time, and Rework Rate as reliability measurements |
| **Anthropic RSP/ASL** | AI safety levels | Capability-to-mitigation mapping and early warning evals inform capability-aware governance |
| **OSCAL** | Machine-readable controls | Layered model (catalog → profile → assessment results) maps to ADR → OBPI → gate hierarchy |
| **OpenChain (ISO 5230)** | Compliance conformance | Self-certification model with periodic renewal as ARF adoption template |
| **MOF** | Model transparency tiers | Agent model openness determines black-box vs white-box verification requirements |
| **W3C PROV** | Provenance ontology | Entity/Activity/Agent vocabulary for governance ledger interoperability |
| **Design by Contract** | Pre/post-conditions | OBPI briefs as formal contracts: preconditions (ADR context), postconditions (acceptance criteria), invariants (governance rules) |
| **CoSAI** | MCP security | 12-category agent threat taxonomy and Secure-by-Design Agentic Systems Principles |
| **Superpowers** | Agent workflow governance | Rationalization prevention, verification-before-completion, two-stage review, hard gates, context isolation |

### Emerging Research Alignment

| Work | Relevance |
|---|---|
| Rabanser et al. (2025) — "Towards a Science of AI Agent Reliability" | Four-dimension reliability model (consistency, robustness, predictability, safety) |
| Omega (2025) — Trusted AI Agents in the Cloud | Per-action provenance tokens, differential attestation protocol |
| AIRS Framework (2025) — AI Risk Scanning | Evidence-bound verification over descriptive disclosure |
| Policy Cards (arXiv 2510.24383) | Machine-readable runtime governance constraints |
| Agent Cards (MICAI 2025) | Structured agent identity documentation |
| HULA (Atlassian, ICSE 2025) | Human-in-the-loop approval loops for agent development |
| Chainguard Agent Skills (2026) | First production supply-chain framework for AI agent artifacts |
| ReliabilityBench (2025) | Reliability Surface evaluation, chaos engineering for agents |
| W3C DID v1.1 | Machine-to-machine identity for AI agents |
| PROV-AGENT (IEEE e-Science 2025) | W3C PROV extension for agentic workflows; models agents as first-class provenance entities via MCP |
| Swiss Cheese Model for AI (ICSA 2025) | Layered guardrail taxonomy across quality attributes, pipeline stages, and agent artifacts |
| Specification Gaming (arXiv 2502.13295) | Reasoning models satisfy literal objectives while violating intent — the fundamental agent governance threat |
| ML FMEA (SAE 2025, Torc Robotics) | Systematic failure mode enumeration adapted for ML pipelines; open-source templates |
| Proof-Carrying Code Completions (PC3) | Agent-produced code carries machine-checkable safety proofs alongside the implementation |
| VeriGuard (Google Research) | Dual-stage verification: offline formal analysis + online runtime monitoring |
| Code Stylometry (arXiv 2506.17323) | 97.5% accuracy attributing code to specific LLM models — forensic provenance verification |
| Epistemic AI (arXiv 2505.04950) | Second-order uncertainty measures; aleatoric vs epistemic uncertainty as basis for governance scaling |
| Normal Accidents (Perrow) | Warning: adding governance layers increases complexity, potentially creating new failure modes |
| Superpowers verification-before-completion | Agent rationalization as first-class threat; "claiming completion without verification is dishonesty" |
| Superpowers subagent-driven-development | Two-stage review (spec compliance then code quality); context isolation per task; "enthusiastic junior engineer" auditability standard |

---

## Target Scope

### Deliverables

1. **ARF specification document** — formal definition of Agent Reliability
   Levels AR0-AR4, the four-dimension evaluation model, and the governance
   predicate schema. Published as a GovZero standard.

2. **Governance predicate type** — define `govzero.dev/attestation/v1` as a
   custom in-toto predicate type that maps gzkit evidence (req_proof_inputs,
   scope_audit, git_sync_state, validation_anchor) into the SLSA
   BuildDefinition/RunDetails structure.

3. **ARF level computation** — extend `gz gates` and receipt emission to
   compute and record the achieved AR level for each OBPI completion event.
   The level is derived from which gates passed, whether attestation occurred,
   and whether audit reconciliation is clean.

4. **ResourceDescriptor for code artifacts** — extend scope audit to include
   content hashes (SHA-256) for changed files, not just path lists. This
   enables artifact-level integrity verification.

5. **Agent identity model** — extend `recorder_source` to a structured
   `AgentIdentity` (vendor, model, session, lane) aligned with the Builder
   model in SLSA and informed by W3C DID concepts.

6. **ARF receipt schema** — JSON schema for ARF-shaped receipts that can be
   validated by external tools. Published alongside the specification.

7. **Governance Bill of Materials (GBOM)** — a machine-readable transparency
   artifact emitted at OBPI completion, listing governance inputs (brief,
   lineage, constraints), agent identity, verification evidence, and AR level.
   Follows NTIA SBOM minimum-elements principles.

8. **Level badge / status reporting** — `gz status` and `gz adr report`
   display the achieved AR level per OBPI and aggregate level per ADR.

### Stretch Deliverables

9. **Sigstore integration** — optional signing of ARF receipts via cosign
   keyless flow (OIDC-based). Recording to Rekor transparency log.

10. **OTel trace emission** — emit OpenTelemetry-compatible spans for
    governance ceremonies, enabling integration with LangFuse, Arize, or any
    OTel collector.

11. **Policy Card generation** — auto-generate machine-readable policy cards
    from OBPI brief constraints for runtime agent governance.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No cryptographic key management infrastructure in v1 (Sigstore keyless flow
  is stretch; no self-managed PKI).
- No runtime agent monitoring or guardrail enforcement (that is
  ADR-pool.ai-runtime-foundations).
- No formal verification of agent reasoning (this framework verifies
  *artifacts*, not *cognition*).
- No dependency vulnerability scanning (that is ADR-pool.agentic-security-review).
- No interop with specific LLM providers' trust APIs — ARF is vendor-neutral.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Enables**: ADR-pool.ai-runtime-foundations (ARF provides the trust substrate
  for runtime observability), ADR-pool.evaluation-infrastructure (ARF levels
  are an evaluation dimension)
- **Related**: ADR-pool.agentic-security-review (security scanning is an
  evidence input to ARF level computation), ADR-pool.audit-system (ARF
  receipts feed the audit pipeline)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. The five AR levels (AR0-AR4) and their gate mappings are accepted.
3. The governance predicate schema design is agreed upon.
4. Decision on whether Sigstore signing is in-scope for v1 or deferred.

---

## Inspired By

[SLSA v1.2 Build Provenance](https://slsa.dev/spec/v1.2/provenance) — SLSA
defines supply-chain integrity levels for software build systems. ARF
appropriates this leveled-provenance model for a new threat domain: AI agent
reliability. Where SLSA tracks source-to-binary trust, ARF tracks
intent-to-artifact trust. The structural isomorphism is deep:
BuildDefinition maps to governance brief, Builder maps to agent identity,
ResourceDescriptor maps to scope audit with content hashes, and Build Levels
map to Agent Reliability Levels.

Additional influences:

- [in-toto attestation framework](https://in-toto.io/) — the Statement/Predicate
  envelope model that SLSA builds on.
- [Sigstore](https://docs.sigstore.dev/) — keyless signing and transparency
  logging for software artifacts.
- [NIST AI RMF (AI 100-1)](https://www.nist.gov/itl/ai-risk-management-framework) —
  GOVERN-MAP-MEASURE-MANAGE functions for AI risk.
- [Rabanser et al. 2025](https://arxiv.org/abs/2602.16666) — "Towards a Science
  of AI Agent Reliability" — four-dimension reliability decomposition.
- [DO-178C](https://en.wikipedia.org/wiki/DO-178C) — Design Assurance Levels
  for safety-critical aviation software.
- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) —
  agent-specific threat taxonomy.
- [S2C2F](https://github.com/ossf/s2c2f) — Microsoft's supply chain consumption
  maturity framework.
- [HULA (Atlassian)](https://arxiv.org/abs/2411.12924) — Human-in-the-loop
  approval for AI software development.
- [Chainguard Agent Skills](https://www.chainguard.dev/) — first production
  supply-chain framework for AI coding agent artifacts.
- [NTIA SBOM](https://www.ntia.gov/page/software-bill-materials) — minimum
  elements for software transparency. ARF's GBOM applies the same
  nested-inventory principle to governance provenance.
- [IEC 61508](https://en.wikipedia.org/wiki/IEC_61508) — three-constraint SIL
  model (systematic capability + architecture + quantitative target).
- [TUF](https://theupdateframework.io/) — trust delegation and threshold
  signatures for governance artifact distribution.
- [OSCAL](https://pages.nist.gov/OSCAL/) — NIST's machine-readable security
  controls language; layered model for expressing governance controls.
- [MITRE ATLAS](https://atlas.mitre.org/) — adversarial threat landscape for
  AI systems, including agent-specific techniques (context poisoning, config
  modification, memory manipulation).
- [W3C PROV](https://www.w3.org/TR/prov-overview/) / [PROV-AGENT](https://arxiv.org/abs/2508.02866) —
  provenance ontology for agentic workflows.
- [OpenChain (ISO 5230)](https://openchainproject.org/) — self-certification
  conformance model with periodic renewal.
- [CoSAI](https://www.coalitionforsecureai.org/) — MCP security threat
  taxonomy and Secure-by-Design Agentic Systems Principles.
- [Design by Contract (Meyer)](https://en.wikipedia.org/wiki/Design_by_contract) —
  pre/post-conditions and invariants as formal contract vocabulary.
- [Specification Gaming (arXiv 2502.13295)](https://arxiv.org/abs/2502.13295) —
  reasoning models satisfy literal objectives while violating intent.
- [ML FMEA (Torc/SAE 2025)](https://torc.ai/knowledge-center/publications/the-ml-fmea-an-introduction/) —
  systematic failure mode analysis adapted for ML pipelines.
- [Swiss Cheese Model for AI (arXiv 2408.02205)](https://arxiv.org/abs/2408.02205) —
  layered guardrail taxonomy for foundation model agents.
- [Normal Accidents (Perrow)](https://en.wikipedia.org/wiki/Normal_Accidents) —
  complexity-induced failure in tightly coupled systems.
- [Superpowers](https://github.com/obra/superpowers) — agent workflow
  governance system for coding agents. Key contributions: (1) treats agent
  rationalization (optimistic self-assessment, verification skipping) as a
  first-class reliability threat; (2) verification-before-completion as an
  iron law — no completion claims without fresh evidence; (3) two-stage
  review (spec compliance then code quality) operationalizing the VER/VAL
  distinction; (4) hard gates that cannot be skipped regardless of perceived
  simplicity; (5) context isolation per task preventing contamination;
  (6) plans detailed enough for an "enthusiastic junior engineer with poor
  taste, no judgement, and an aversion to testing" — setting the auditability
  bar for governance artifacts.

---

## Maturity Gaps

The following gaps exist between gzkit's current state and ARF requirements:

### Agent Provenance (not yet captured)

gzkit records `recorder_source` as a flat string identifying the *gzkit
command* that emitted a receipt (e.g. `"cli:obpi_emit_receipt"`). It does not
record which LLM or harness produced the governed work. To satisfy SLSA's
`Builder.id` + `Builder.version` equivalent, every governed artifact must
capture:

- **Model** — the specific LLM (e.g. `claude-opus-4-6`, `gpt-4o`, `gemini-2.5-pro`)
- **Harness** — the agent harness and version (e.g. `claude-code@1.0.34`,
  `copilot-chat@0.25.1`, `aider@0.82.0`)
- **Vendor** — the provider (e.g. `anthropic`, `openai`, `google`)
- **Session** — a unique identifier for the agent session that produced the work
- **Human fallback** — when a human authors directly, record `human` with
  optional identity (not required — per Principle 5)

This is the ARF equivalent of SLSA's Builder model. Without it, provenance
is incomplete: we know *what* was governed but not *who/what produced it*.

### Artifact Versioning (partially mature)

ADRs and OBPIs carry semver identifiers. But the following artifacts do not:

- **Ledger schema** — currently `gzkit.ledger.v1` (informal, not semver2)
- **Receipt schemas** — `arb_lint_receipt.schema.json` (unversioned)
- **Governance predicate type** — does not yet exist
- **GBOM format** — does not yet exist
- **ARF spec itself** — needs a versioned identifier

All governance artifacts should carry semver2 identifiers to enable:
breaking-change detection, consumer compatibility checks, and changelog
discipline. The version should appear in both the schema `$id` field and
the artifact's metadata payload.

### Content Hashing (not yet implemented)

Scope audits currently record file *paths* (allowlist vs changed files) but
not file *content hashes*. Without content hashes, post-attestation
tampering is undetectable — a file could be modified after Gate 5 but before
audit, and the scope audit would still show it as "in scope."

---

## Status Quo (What Teams Do Today Without ARF)

Most teams using AI coding agents have no structured assurance process:

1. **No governance at all (AR0)** — agent writes code, developer glances at
   the diff, merges. No record of intent, scope, or verification. This is the
   dominant mode in industry today.

2. **Ad hoc review** — developer manually reviews agent output against a
   mental model of what they asked for. No structured brief, no scope audit,
   no evidence record. Trust is personal and non-transferable.

3. **Co-Authored-By convention** — some harnesses (including Claude Code) add
   `Co-Authored-By: <model>` to git commits. This is the only widely-adopted
   agent provenance signal, but it is informal, unstandardized, and captures
   only model identity — not intent, scope, verification, or attestation.

4. **PR review as governance** — code review serves as the human gate. But PR
   review was designed for human-authored code where the reviewer can reason
   about the author's intent from the code itself. With agent-produced code,
   the reviewer cannot infer intent from the diff alone — they need the brief.

ARF formalizes what is currently informal or absent. It does not replace code
review; it provides the structured context (brief, scope, evidence) that
makes code review of agent-produced work meaningful.

---

## Example: ARF Receipt (Illustrative)

What a governed OBPI completion event would look like expressed as an
ARF-shaped predicate:

```
predicateType: "govzero.dev/attestation/v1"
predicate:
  governanceDefinition:
    governanceType: "govzero.dev/obpi-completion/v1"
    intent:
      adr: "ADR-0.25.0"
      obpi: "OBPI-0.25.0-03"
      brief_hash: "sha256:a1b2c3..."
    constraints:
      allowed_paths: ["src/gzkit/lifecycle.py", "tests/test_lifecycle.py"]
      denied_paths: ["src/gzkit/cli.py"]
      lane: "heavy"
      acceptance_criteria: 3
    lineage:
      parent_adr: "ADR-0.25.0-core-infrastructure-pattern-absorption"
      parent_prd: "PRD-GZKIT-1.0.0"
  runDetails:
    agent:
      vendor: "anthropic"
      model: "claude-opus-4-6"
      harness: "claude-code@1.0.34"
      session: "sess_abc123"
    metadata:
      started_on: "2026-03-22T09:15:00Z"
      attested_on: "2026-03-22T11:30:00Z"
      audited_on: "2026-03-22T11:45:00Z"
    evidence:
      scope_audit:
        changed_files:
          - uri: "src/gzkit/lifecycle.py"
            digest: { sha256: "e4f5g6..." }
          - uri: "tests/test_lifecycle.py"
            digest: { sha256: "h7i8j9..." }
        out_of_scope: []
      gates:
        - gate: 1, status: "pass"
        - gate: 2, status: "pass"
        - gate: 3, status: "pass"
        - gate: 4, status: "pass"
        - gate: 5, status: "pass", attestor: "Jeffry Babb"
      req_proof_inputs:
        - name: "unit_tests", kind: "command", status: "present"
        - name: "type_check", kind: "command", status: "present"
        - name: "human_attestation", kind: "attestation", status: "present"
    anchor:
      commit: "a1b2c3d"
      semver: "0.25.0"
  ar_level: 4
  dimensions:
    consistency: "pass"
    robustness: "pass"
    predictability: "pass"
    safety: "pass"
```

This is illustrative, not normative. The exact schema is a deliverable of
this ADR. The key point: all the data gzkit already captures (scope audit,
gate results, proof inputs, attestation, anchor) fits naturally into an
SLSA-shaped predicate without forcing build-system assumptions.

---

## Notes

- gzkit already enforces AR0-AR4 through its lane system, gate pipeline, and
  attestation ceremonies. This ADR names and schemas what already exists, then
  extends it for ecosystem interoperability.
- The governance predicate type (`govzero.dev/attestation/v1`) should resolve
  to human-readable documentation, following SLSA's `buildType` convention.
- The four-dimension model (consistency, robustness, predictability, safety)
  provides richer signal than a single level number. Consider reporting both:
  "AR3 (C:pass R:pass P:warn S:pass)".
- Content hashes for changed files (ResourceDescriptor) are a meaningful
  upgrade over path-only scope audits — they enable post-hoc verification
  that the attested files haven't been modified after attestation.
- This framework is vendor-neutral by design. It must work equally well for
  Claude, Copilot, Codex, Gemini, and human-only workflows. An AR4 artifact
  produced by a human should be indistinguishable from one produced by an agent.
- Key design tension: schema richness vs adoption friction. Start with the
  minimum viable predicate that captures what gzkit already records, then
  extend.
- The `Co-Authored-By` header in git commits is the only existing agent
  provenance signal with wide adoption. ARF should not replace it — it should
  complement it. Consider: should `gz commit` (or git-sync) auto-inject
  structured agent provenance metadata into commit trailers beyond the
  Co-Authored-By line?
- The name "Agent Reliability Framework for Software Systems" is intentional —
  it scopes to software artifacts (not all AI outputs) and to systems (not
  individual completions).
- Consider: ARF as a standalone specification (like SLSA) vs embedded in
  gzkit's governance documentation. The former has broader impact; the latter
  has faster iteration. A hybrid path: develop within gzkit, extract when
  stable.
- OSCAL's layered model (catalog → profile → component definition → SSP →
  assessment plan → assessment results → POA&M) maps to gzkit's hierarchy
  (governance rules → lane requirements → agent capabilities → OBPI brief →
  gate plan → gate results → defect tracking). Expressing ARF controls in
  OSCAL format would enable FedRAMP-aligned compliance reporting.
- IEC 61508's technique/measure tables — which prescribe specific V&V
  techniques at each SIL — could template the gate prescription tables at
  each AR level. Not all gates are mandatory at all levels; the tables make
  this explicit.
- OpenChain's self-certification conformance model is pragmatic for ARF
  adoption: organizations self-certify that their agent governance pipeline
  meets ARF requirements at a declared level. 18-month renewal cycles
  prevent certification drift.
- DORA's 2025 finding — AI coding assistants boost individual productivity
  but organizational delivery metrics stay flat — validates ARF's thesis:
  agent velocity without governance does not improve outcomes. The pipeline
  quality is the determinant, not the agent's raw capability.
- Code stylometry (97.5% accuracy attributing code to specific LLMs) could
  be integrated into AR4 audits as a forensic verification that
  agent-attributed code was actually produced by the claimed model.
- The FMEA should be a living governance artifact maintained alongside the
  ARF spec. Each new failure mode discovered in production should be added
  with its detection strategy and the AR level at which it is caught.
- Superpowers and gzkit operate at complementary layers. Superpowers governs
  the *agent's workflow* (brainstorm → spec → plan → implement → review).
  gzkit governs the *governance pipeline* (ADR → OBPI → gates → attest →
  audit). ARF bridges both: superpowers' verification-before-completion is
  the agent-side enforcement of what gzkit's gates verify from the pipeline
  side. The "enthusiastic junior engineer" standard for plan detail is the
  practical test for whether a governance artifact is auditable.
- Superpowers' rationalization prevention table should inform the design of
  ARF's evidence requirements. At each AR level, the framework should
  anticipate and counter the specific rationalizations an agent might use
  to skip that level's verification. This is mechanism design applied to
  agent governance — designing the system so that the path of least
  resistance is also the path of compliance.

---

## Open Questions

These require resolution during promotion or early OBPIs:

1. **Schema format** — should the ARF predicate be JSON Schema, Pydantic
   model-first (with JSON Schema export), or both? gzkit is Pydantic-native,
   but external consumers need standalone JSON Schema.

2. **Intent hash stability** — OBPI briefs are markdown files that may be
   edited during implementation (evidence sections get filled in). Should the
   intent hash cover only the immutable sections (objective, constraints,
   acceptance criteria) or the full file? If the former, we need a canonical
   extraction.

3. **Agent identity discovery** — how does gzkit learn which model/harness
   is active? Options: environment variable (`GZKIT_AGENT_MODEL`), harness
   self-identification via a convention file, or explicit `--agent` flag on
   `gz` commands. Each has trade-offs for adoption friction vs accuracy.

4. **Retroactive leveling** — can existing ledger events be retroactively
   assigned AR levels, or does AR level computation only apply to new
   completions? Retroactive assignment would give the existing corpus
   immediate value but risks inaccuracy.

5. **GBOM emission trigger** — should the GBOM be emitted at OBPI completion,
   at ADR closeout, at both, or on demand via `gz gbom`? Each OBPI produces
   its own GBOM; an ADR GBOM aggregates its OBPIs.

6. **Signing threshold** — if Sigstore signing is adopted, should all AR
   levels be signed or only AR3+? Signing everything is simpler; signing
   only attested work reduces noise.

7. **Ecosystem publication** — should ARF receipts/GBOMs be published to a
   transparency log, stored only in the local ledger, or both? Local-only
   is simpler; transparency logging enables third-party verification.

8. **Relationship to GUAC** — could ARF receipts be ingested by GUAC
   (Graph for Understanding Artifact Composition) alongside SBOMs and SLSA
   attestations? This would place agent-governed artifacts in the same
   queryable graph as build-verified artifacts.

9. **Cross-repository governance** — when gzkit governs multiple repositories
   (e.g. gzkit + airlineops), how do AR levels compose across repo
   boundaries? Does each repo have its own AR posture, or can a
   cross-repo release aggregate them?
