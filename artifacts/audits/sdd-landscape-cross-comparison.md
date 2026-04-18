# SDD Landscape Cross-Comparison — gzkit vs. April 2026 Top 10

**Date:** 2026-04-15
**Status:** Working analysis — not a decision record
**Purpose:** Resume point for evaluating gzkit's position in the SDD landscape and deciding which foreign ideas (if any) are worth importing without corrupting gzkit's core philosophy.

---

## 1. Framing

gzkit is **not** an SDD toolkit in the same genre as most of the April 2026 top ten. It is closer to an *accounting system for software governance* that happens to use spec-like artifacts (ADR, OBPI brief, REQ, TASK) as its chart of accounts. Every comparison in this document is shaped by that distinction.

### gzkit's load-bearing primitives

- **Append-only ledger** (`.gzkit/ledger.jsonl`) as the only source of proof. Events emitted via CLI, never hand-edited.
- **Three-layer state doctrine**: L1 canon (ADR/brief files) → L2 ledger (events) → L3 derived views (status tables, pipeline markers). Only L1/L2 can block gates.
- **Four-tier traceability**: `task → req → obpi → adr`, with commit-trailer enforcement (`Task: TASK-X.Y.Z-NN-MM-PP`).
- **Five gates with receipt-bound attestation**: ARB receipts (`artifacts/receipts/*.json`) are the only faithful record of a QA step. Heavy lane fails closed without receipt IDs.
- **One-way canonical sync** from `.gzkit/` to `.claude/` and `.github/` mirrors, with version + commit-hash conflict detection.
- **Pipeline lifecycle**: plan → implement → verify → present → sync, hook-gated to prevent stage-skipping.
- **Human-anchored Gate 5** for Heavy lane attestation.

---

## 2. The April 2026 Top 10 (as supplied)

1. **GSD (Get Shit Done)** — Context Isolation. Fresh clean agent per atomic task to prevent hallucination spikes.
2. **Intent** — Enterprise living-spec platform. Bidirectional sync between code and spec.
3. **GitHub Spec Kit** — Agent-agnostic markdown schema (spec.md, plan.md, tasks.md).
4. **BMAD-METHOD** — Role-based orchestration with up to 12 specialized agents. Developer agent cannot see codebase until Architect approves spec.
5. **Kiro** — Spec-to-Infrastructure (S2I) using EARS syntax. Spec generates AWS/Azure infra + scaffolded logic.
6. **OpenSpec** — Brownfield specialist. Delta markers define only what is changing in a spec.
7. **Traycer** — Passive SDD. Vibe-code normally, Traycer validates against charter in background.
8. **Levo.ai** — Reverse SDD. Observes production traffic and reverse-engineers the spec.
9. **Cursor + .cursorrules** — Lite SDD via global architectural invariants in rules file.
10. **Agentic Goal-Steering** — Outcome-driven. Agents iterate autonomously until verification suite passes 100%.

---

## 3. Point-by-point comparison

### 1. GSD (Context Isolation)
- **gzkit mapping:** Tactical, not methodological. Agent subagent types (Explore, Plan, implementer, spec-reviewer, quality-reviewer) exist. Structural equivalent is pipeline stage separation — each stage has defined inputs/outputs, so drift is bounded by the brief.
- **Verdict:** Convergent but orthogonal. GSD protects against memory drift; gzkit protects against *evidence drift* via the ledger. Compatible — could run GSD-style isolation inside gzkit.

### 2. Intent (Bidirectional Sync)
- **gzkit mapping:** **Actively rejected.** `.gzkit/rules/skill-surface-sync.md` exists because mirrors diverging from canon is what gzkit calls drift and treats as a defect. Intent's core feature is gzkit's core anti-feature.
- **Verdict:** Philosophically opposed. Intent optimizes for *liveness*; gzkit optimizes for *provenance*. If forensic trail matters (audit, compliance, accounting), gzkit wins. If "docs just reflect reality" matters more, Intent wins.

### 3. GitHub Spec Kit
- **gzkit mapping:** gzkit has its own opinionated schema (ADR frontmatter, OBPI brief template, REQ IDs, gate manifests) rather than Spec Kit's lean `spec.md`/`plan.md`/`tasks.md`. `.github/instructions/` gestures at agent-agnosticism but `.claude/` is the primary surface. `AGENTS.md` is the nearest universal contract.
- **Verdict:** gzkit is heavier and more locked-in. Spec Kit could slot underneath gzkit as a transport format, but gzkit's semantics (ledger events, receipt citations, gate covenants) are outside Spec Kit's scope.

### 4. BMAD-METHOD
- **gzkit mapping:** Closest peer. gzkit has 60+ skills playing role-like parts (`gz-plan`, `gz-implement`, `gz-arb`, `quality-reviewer`, `spec-reviewer`), and plan-audit-gate enforces "implementer can't proceed without plan approval" — a direct parallel to BMAD's Architect→Developer gate.
- **Key difference:** BMAD enforces role separation at the *agent-identity* layer; gzkit enforces it at the *artifact* layer (you need a plan receipt, a ledger event, a gate pass — regardless of which agent produces them). gzkit's invariant is on the proof, not the producer.
- **Verdict:** Same problem, different epistemology. BMAD is more ceremonial; gzkit is more auditable. A BMAD-style role split could run inside gzkit without changing gzkit's contracts.

### 5. Kiro (EARS, Spec-to-Infrastructure)
- **gzkit mapping:** No overlap. gzkit does not provision infra and has no EARS-style structured requirements syntax. REQs are plain markdown identifiers decorated with `@covers`. gzkit is entirely a *repository discipline* tool.
- **Verdict:** Different domain. Kiro is greenfield cloud-native; gzkit is "we need this repo to be governable forever."

### 6. OpenSpec (Delta Markers)
- **Initial take (wrong):** Interesting capability gap. gzkit could learn from OpenSpec here.
- **Correction:** **gzkit already has delta markers — they live as GHIs (GitHub Issues).** GHI-160's multi-phase structure (Phase 2 `--include-doc` flag, Phase 3 REQ backfill across 260 briefs, Phase 4 retroactive `@covers`, Phase 6 TASK-driven workflow, Phase 7 task backfill) is exactly delta-marker work. Each phase is a scoped "what is changing in this revision" artifact. Same for GHI #141/#149/#150/#151 — drift audit, invariant addition, sweep, commit discipline follow-up as a coordinated delta chain.

#### Topology comparison

| Surface | OpenSpec | gzkit |
|---|---|---|
| Delta artifact | Inline in spec file | GitHub Issue (GHI-NNN) |
| Binding to code | Delta block in markdown | `Task:` commit trailer + ledger event |
| Scope carrier | Paragraph-level markers | Phase-structured GHI body + REQ/TASK IDs |
| Review surface | Spec diff | PR + GHI comment thread |

- **Revised verdict:** Not a capability gap — a different topology. OpenSpec couples delta to spec file; gzkit decouples delta to issue + ledger. gzkit's version is arguably stronger because the delta carries its own lifecycle (open → phases → closed) and its own evidence chain (commits, receipts, attestation) without mutating canon until the change lands.
- **Smaller borrow worth considering:** A `gh` query or `gz` verb that surfaces "which REQs does GHI-NNN touch" so the delta-to-REQ mapping is queryable without reading the issue body. Would make GHIs first-class delta markers in the tooling.

### 7. Traycer (Passive Guardian)
- **gzkit mapping:** Strong structural match. `.claude/hooks/` directory (`pipeline-gate.py`, `plan-audit-gate.py`, `obpi-completion-validator.py`, `pipeline-completion-reminder.py`, `post-edit-ruff.py`) is a guardian-angel system.
- **Key difference:** Traycer markets "vibe-code normally, we'll catch you." gzkit is the inverse: formal is default, hooks enforce the default. "No vibe coding" is an explicit invariant (6b).
- **Verdict:** Same mechanism, opposite defaults. gzkit's hook surface is arguably more mature; the UX is heavier.

### 8. Levo.ai (Reverse SDD)
- **gzkit mapping:** No overlap. `gz adr recon` reconciles state from emitted events, but cannot observe runtime traffic.
- **Verdict:** Different lifecycle moment. Levo onboards legacy; gzkit governs ongoing work. Complementary — could Levo a legacy system to produce seed ADRs, then drop into gzkit.

### 9. Cursor + .cursorrules
- **gzkit mapping:** gzkit's `.claude/rules/**` with frontmatter `paths:` globs is a more sophisticated version. Rules are path-gated, versioned, mirror-synced. Same pattern, much more infrastructure.
- **Verdict:** gzkit is `.cursorrules` scaled up an order of magnitude. Lite version is a strip-down of gzkit's rules surface.

### 10. Agentic Goal-Steering (Verification Spec)
- **gzkit mapping:** Partial alignment. ARB receipts, coverage floor, and Invariant 6f ("tests assert semantics, not strings") gesture toward verification-driven development. Heavy lane's ARB receipt requirement is a bounded form of "gates are the spec."
- **Key difference:** gzkit keeps the human in the loop for Gate 5 attestation. Fully autonomous iteration until verification passes is explicitly *not* what gzkit does — Invariant 11 says "if <90% sure, ask the human." gzkit trusts verification *as evidence*, not as *terminal authority*.
- **Verdict:** gzkit is goal-steering with a human anchor. If Goal-Steering is the successor to SDD, gzkit is the conservative branch.

---

## 4. Where gzkit stands out vs. all ten

Three things none of the listed approaches have:

1. **Append-only ledger as source of proof.** Every other approach treats the spec file as ground truth. gzkit treats the *event history* as ground truth and the spec as canon. This is the accounting-system move. The Lindsey et al. circuit-separation argument cited in `.claude/rules/attestation-enrichment.md` is the sharpest defense: narrative reconstruction and execution are separate pathways in the model, so the only faithful QA record is the wrapped-command receipt.
2. **Receipt-bound attestation.** Heavy lane fails closed without ARB receipt IDs inline in the attestation. No other approach in the list binds spec closure to machine-verifiable evidence artifacts.
3. **L1/L2/L3 state doctrine.** The explicit rule that derived views can *never* block a gate is unique. It prevents the class of failure where `status: Completed` in YAML frontmatter is treated as proof when the ledger says otherwise.

## 5. Where gzkit is weak vs. the list

1. **No bidirectional sync** (Intent) — defensible but real; if code drifts from spec, nothing forces the brief to update.
2. **No spec-to-infra** (Kiro) — out of scope but a real greenfield gap.
3. **No reverse SDD** (Levo) — cannot onboard undocumented legacy.
4. **Heavy ceremony** (vs. Cursor/Traycer) — high floor for small teams.
5. **Not truly agent-agnostic** (vs. Spec Kit) — `.claude/` is first-class, others are mirrors.
6. **Human-gated Gate 5** (vs. Goal-Steering) — correctness feature, velocity cost.

## 6. The honest identity

gzkit is best understood as **"BMAD's governance + Traycer's hooks + a ledger nobody else has."** Built for a specific failure mode — agents rationalizing completion claims without evidence — and its ceremony is proportional to that concern. If that failure mode isn't your top risk, something lighter on the list (Cursor, Traycer, Spec Kit) will feel faster. If it is, nothing on the list gives you the evidence floor gzkit does.

---

## 7. Evaluation rubric (sketch, not yet formalized)

**Problem:** Without a rubric, every "should we borrow X" question becomes a fresh debate with no anchor. Risk: adopting something that reads well in isolation but silently violates a core invariant.

### Part A — Invariant preservation (fail-closed gates)

A candidate borrow fails here if it violates any of these, regardless of other merits:

1. **Ledger primacy** — Does it preserve the ledger as the only source of proof, or introduce a parallel truth surface?
2. **L1/L2/L3 separation** — Does any new artifact sit cleanly in canon, ledger, or derived? Anything promoting an L3 view to authoritative is a fail.
3. **Evidence-bound attestation** — Does it strengthen or weaken the receipt-citation requirement?
4. **One-way sync** — Does it introduce bidirectional coupling between canon and mirrors?
5. **Human anchor at Gate 5** — Does it displace the human attestation gate?
6. **Trace chain** — Does it preserve `task → req → obpi → adr`, or break/bypass it?
7. **Commit-trailer binding** — Can changes still be mechanically linked to a TASK?

### Part B — Value delta (scored, not gated)

For candidates that pass Part A:

- **Velocity cost** — ceremony added or removed
- **Defect-class coverage** — which failure modes does it catch that gzkit currently misses?
- **Receipt generation** — does it produce new evidence artifacts, or just prose?
- **Scope** — does it cover a lifecycle moment gzkit handles weakly (onboarding legacy, cross-agent portability, large-delta re-processing)?
- **Portability** — can it be stripped out later without leaving scar tissue?

### The core test question

For any candidate borrow: **"Can this be expressed as ledger events + canonical artifacts + derived views, or does it require something else?"** If the answer is "something else," that is the interesting case — either gzkit's three-layer model is incomplete, or the borrow is incompatible.

### Open questions before formalizing the rubric

1. **Are invariants 1–7 above actually the right list?** Derived from loaded rules, but may miss something or promote implementation details to invariant status.
2. **Where does the rubric belong?**
   - As an **ADR** — treats "how gzkit evaluates foreign ideas" as an architectural decision
   - As a **rule file** — makes it binding on agents evaluating proposals
   - As a **skill** — makes it a procedure

---

## 8. Which players are actually consequential

**Caveat:** Knowledge cutoff is May 2025; the list is framed as April 2026. This section reasons from pre-cutoff signal plus structural logic, not current market share. Treat as "what to verify first," not "what is true today."

"Consequential" splits into two axes that do not correlate as much as people assume:

- **Distribution power** — will this still be around in two years because someone with reach is backing it?
- **Idea originality** — does it contain a thought gzkit would be strictly weaker for ignoring?

### Distribution tier (matters regardless of merit)

1. **GitHub Spec Kit** — GitHub backing + agent-agnostic schema is the interop play. Whoever owns the common format owns the coordination layer. gzkit will eventually have to decide whether to emit Spec Kit-compatible artifacts or stay proprietary. Track closest for strategic reasons, not philosophical ones.
2. **Cursor + .cursorrules** — Not really a methodology, but Cursor's reach makes `.cursorrules`-style lite SDD the *de facto* default for millions of developers. gzkit's `.claude/rules/` is the richer cousin; question is whether that richness ever reaches those users.
3. **Kiro** — If AWS-backed (verify), distribution alone makes it consequential for cloud-native greenfield. Orthogonal to gzkit's domain.

### Idea tier (matters because of what they are saying)

1. **BMAD-METHOD** — Role-based orchestration with hard separation is a serious architectural claim about agent governance. Pushes further than gzkit's plan-gate. Pre-cutoff had real open-source traction. Worth studying.
2. **Agentic Goal-Steering** — Even as a framing more than a product, "verification spec as primary artifact" is where the field is probably heading. gzkit's ARB receipts are a partial move; the full move would treat the verification suite as *the* spec. **Philosophical challenger to gzkit's human-anchored Gate 5.**
3. **OpenSpec** — Delta markers formalization. Already covered by gzkit's GHI pattern, but worth watching.

### Cannot confidently place

**GSD, Intent, Traycer, Levo.ai** — No strong pre-cutoff signal that these are established players versus pattern-labels or early-stage projects. Several descriptions read like "the obvious idea, productized." Would want to see GitHub stars, actual user reports, and verify tooling exists before treating as serious peers.

### Recommendation for gzkit's attention

**Two matter most:**

- **BMAD-METHOD** — nearest sibling. Studying its role-separation model would sharpen gzkit's thinking about *who* vs. *what* enforcement.
- **Agentic Goal-Steering** — philosophical position gzkit will eventually have to answer. Either gzkit defends human-anchored Gate 5 explicitly, or it opens a path to verification-terminal completion. Right now the position is implicit.

Everything else is distribution-watching (Spec Kit, Cursor, Kiro) or noise to verify before spending cycles on.

---

## 9. Open threads to resume on

1. **Verify the top-10 list against current reality.** Use WebSearch to replace reasoned speculation with grounded read on which projects are real, staffed, and gaining traction as of 2026-04.
2. **Finalize the invariant list (Part A of rubric).** Review invariants 1–7 against loaded rules and decide if any are implementation details misclassified as invariants.
3. **Decide the rubric's home** — ADR vs. rule file vs. skill. Each has different enforcement consequences.
4. **Formalize the GHI-as-delta-marker pattern.** Add a `gz` verb or `gh` query that surfaces REQ/OBPI scope of a given GHI. Would make the pattern queryable and first-class.
5. **Articulate gzkit's position on Agentic Goal-Steering explicitly.** Is human-anchored Gate 5 a forever-invariant or a current-phase safety anchor that relaxes as verification maturity grows?
6. **Decide whether to emit Spec Kit-compatible artifacts** as a second-class export to preserve optionality on cross-agent portability.
7. **Study BMAD-METHOD in detail** and map its role-separation primitives to gzkit's artifact-separation primitives. Write up where they converge and diverge.

---

## 10. Session artifacts referenced

- `.gzkit/ledger.jsonl` — append-only event log
- `.claude/rules/arb.md` — ARB receipt middleware doctrine
- `.claude/rules/attestation-enrichment.md` — receipt-binding requirement with Lindsey et al. circuit-separation citation
- `.claude/rules/behavioral-invariants.md` — Invariants 1–16 (ownership, craftsmanship, process, judgment, efficiency)
- `.claude/rules/constraints.md` — negative constraints across TDD, models, surface sync, documentation covenant, pipeline lifecycle, OBPI completion, ADR closeout, state doctrine, storage tiers, architectural boundaries
- `.claude/rules/skill-surface-sync.md` — one-way canon → mirror sync doctrine
- `.claude/rules/tool-skill-runbook-alignment.md` — three-layer alignment invariants (tools / skills / runbooks)
- `.claude/rules/tests.md` — TDD discipline and TASK-driven workflow (GHI-160 Phase 6)
- `CLAUDE.md` — architectural boundaries from Architecture Planning Memo § 12
- Recent GHIs referenced: GHI-160 (phases 2–7), GHI #141 (status drift audit), GHI #149 (Invariant 3 addition), GHI #150 (Output Contract audit sweep), GHI #151 (commit-message discipline)
