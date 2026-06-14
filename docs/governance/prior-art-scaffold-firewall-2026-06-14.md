# Prior-Art Research: Scaffold Firewall + Skills-First Enforcement

> **Provenance.** Background research deep-dive commissioned 2026-06-14 during the
> Magna Carta design dialogue that booked the **Firewall foundation ADR** and the
> **skills-first enforcement** follow-on (see the 2026-06-14 amendments in
> `build-to-1.0-campaign-2026-06-10.md` and `vocabulary-config-first-exorcism-GHI-615.md`).
> This is a **research artifact**, not canon — it exists to be cited by the two
> ADRs when authored. Findings inform the **mechanical face** (per-surface
> destiny classification + validate-time fail-close) and **communicative face**
> (CMS-rendered scaffold-boundary surface) of the firewall, and the skills-first
> deny gate. Rooted in GHI #607 (the `models.md` adopter-boundary leak) and
> GHI #615 (the vocabulary substrate).

Research basis: full clone of **obra/superpowers** @ v5.1.0 (commit on `main`, fetched 2026-06-14) read concretely; three parallel cross-tool surveys verified against live official docs. Every nontrivial claim is cited to a repo file path or URL.

---

## 1. superpowers teardown

**Lead finding (load-bearing): progressive disclosure is a SessionStart hook that injects exactly ONE skill body, and every other skill is metadata-only until the `Skill` tool fires.** The scaffold boundary is declared by an explicit `EXCLUDES` allowlist in a delivery script, not by prose.

### 1a. Progressive disclosure — the actual mechanism

Three-tier lazy load, mechanically driven:

- **Tier 0 (always in context): one bootstrap skill, injected by a hook.** The `SessionStart` hook (`hooks/hooks.json:3-14`, matcher `"startup|clear|compact"`) runs `hooks/session-start`, which `cat`s **only** `skills/using-superpowers/SKILL.md` and injects it as `additionalContext` (`hooks/session-start:17-18,35`). Nothing else is preloaded. The injected wrapper says verbatim: *"Below is the full content of your 'superpowers:using-superpowers' skill... **For all other skills, use the 'Skill' tool**"* (`hooks/session-start:35`).
- **Tier 1 (metadata only): every other skill is just `name` + `description` frontmatter** until triggered. The bootstrap skill instructs: *"Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you... **Never use the Read tool on skill files**"* (`skills/using-superpowers/SKILL.md:30`). The 14 skills' `description` fields are uniformly written as triggering conditions ("Use when...") — `skills/brainstorming/SKILL.md:3`, `skills/test-driven-development/SKILL.md:3`, etc.
- **Tier 2 (on-demand subfiles): heavy reference files load only when the skill body points to them.** Example: the `pptx/` skill ships `pptxgenjs.md` (600 lines) + `ooxml.md` (500 lines) loaded only when implementing (`skills/writing-skills/SKILL.md:364-372`).

The disclosure discipline is **explicitly anti-eager-load**, and this is the single most transferable doctrine for gzkit's CMS:
> *"`@` syntax force-loads files immediately, consuming 200k+ context before you need them"* — `skills/writing-skills/SKILL.md:288`. The `description` field rule: *"Claude reads description to decide which skills to load... Make it answer: 'Should I read this skill right now?'"* (`:146`), and *"NEVER summarize the skill's process or workflow"* in the description (`:102`) — keep the trigger lean so the body stays deferred. Token budget is enforced as doctrine: *"getting-started workflows: <150 words... Frequently-loaded skills: <200 words total"* (`:218-219`).

Cross-skill references are deliberately **name-only, never path/@-links**, to preserve laziness: *"✅ `**REQUIRED SUB-SKILL:** Use superpowers:test-driven-development`"* vs *"❌ `@skills/.../SKILL.md` (force-loads, burns context)"* (`:283-288`). A referenced skill is named so the agent can *choose* to invoke it — disclosure stays on-demand.

### 1b. Scaffold-boundary declaration — where "my scaffold ends / this is yours"

**The boundary is an explicit machine-readable `EXCLUDES` array in the delivery script `scripts/sync-to-codex-plugin.sh:54-77`.** This is superpowers' firewall, and it is the closest direct precedent for the gzkit Firewall. When syncing the repo into the *delivered* Codex plugin, it strips everything that is framework-internal rigging:

```
EXCLUDES: /.claude/  /.claude-plugin/  /.github/  /.gitattributes  /.gitignore
          /AGENTS.md  /CLAUDE.md  /GEMINI.md  /CHANGELOG.md  /RELEASE-NOTES.md
          /package.json  /commands/  /docs/  /hooks/  /lib/  /scripts/  /tests/
```

What ships to adopters: `skills/` + committed `.codex-plugin/` + `assets/`. What stays in the lab: contributor guidelines, dev docs, the build/sync scripts, tests, and the hooks. The script header states the intent: *"rsyncs tracked upstream plugin content... preserves OpenAI-owned marketplace metadata"* (`scripts/sync-to-codex-plugin.sh:7-9`). The path-anchoring comment (`:48-52`) shows the boundary is engineered carefully — `/scripts/` is anchored so it won't catch the legitimate *shipped* `skills/brainstorming/scripts/`.

Note the limits of this precedent: the boundary lives in **one delivery script**, is **not** declared per-surface (no frontmatter flag on each file saying "I am a jig"), and is **not** validated — nothing fail-closes if a jig leaks. It is a denylist in a build tool, not a structural property of each surface. This is exactly the gap gzkit's Firewall must close.

### 1c. Self-explanation to the adopting project

Two distinct artifacts, **split by audience** — and the split is itself the boundary signal:

- **`README.md` (for the human adopter):** install per-harness, "How it works" narrative, "The Basic Workflow" list of the 7 skills with their auto-trigger moments (`README.md:154-170`). It is a **one-time static doc**, not a rendered/live surface. Its key self-explanation: *"because the skills trigger automatically, you don't need to do anything special. Your coding agent just has Superpowers"* (`:19`).
- **`CLAUDE.md` (for the contributing agent — NOT shipped):** opens *"## If You Are an AI Agent / Stop. Read this section before doing anything"* (`CLAUDE.md:3-5`). This file is in the `EXCLUDES` list (1b) — it explains the *lab*, never reaches adopters.

The operator's praise ("explains where its scaffold ends") resolves to: the **`using-superpowers` bootstrap is the live self-explanation to the adopter's agent** (injected every session via the hook), while the README is the static self-explanation to the adopter's human. The boundary is communicated by *which file each audience gets* — agents get the injected bootstrap, adopters get skills+README, contributors get CLAUDE.md. It is **implied by partition**, not stated as an explicit "scaffold ends here" sentence.

### 1d. Skills-first enforcement — hook-injected goodwill, NOT a tool gate

**Superpowers does NOT structurally force routing through skills. It uses a SessionStart context injection plus maximal prompt pressure — strong goodwill, not a fail-closed gate.** Be plain about this: there is **no `PreToolUse` hook that denies `Edit`/`Write`** anywhere in the repo. The only hook is `SessionStart` (`hooks/hooks.json`).

The enforcement is entirely prompt-level, but engineered hard:
- The bootstrap is injected inside `<EXTREMELY_IMPORTANT>` tags (`hooks/session-start:35`) and the skill body itself uses `<EXTREMELY-IMPORTANT>`: *"If you think there is even a 1% chance a skill might apply... you ABSOLUTELY MUST invoke the skill. IF A SKILL APPLIES... YOU DO NOT HAVE A CHOICE"* (`skills/using-superpowers/SKILL.md:10-16`).
- A **Red Flags rationalization table** pre-empts every evasion ("This is just a simple question" → "Questions are tasks. Check for skills.") — `:82-95`.
- A decision **flowchart** routes "User message received" → "Might any skill apply?" → "Invoke Skill tool" *before* responding (`:48-76`).

The README claims it is mandatory — *"The agent checks for relevant skills before any task. Mandatory workflows, not suggestions"* (`README.md:170`) — but mechanically this is honor-system: a model that ignores the injected context faces no tool-level block. Their own meta-skill concedes the boundary between prompt and enforcement: *"Mechanical constraints (if it's enforceable with regex/validation, automate it — save documentation for judgment calls)"* (`skills/writing-skills/SKILL.md` "Don't create for" list). They classify skills-routing as a judgment call, deliberately, and shape it with prompt pressure rather than a gate.

### 1e. Framework-internal vs delivered separation

**Yes — superpowers distinguishes "skills I use to build superpowers" from "skills I ship," but only via the delivery-script `EXCLUDES` denylist (1b), not via any per-skill flag.** Mechanisms observed:
- `writing-skills` is shipped (it's a general-purpose skill adopters use), but the *contributor process* that governs how superpowers builds itself lives in the **non-shipped** `CLAUDE.md` (PR rules, eval requirements, `dev`-branch rule).
- The build/test apparatus (`scripts/`, `tests/`, `hooks/`, `docs/`) is excluded from delivery (1b).
- **There is no `provenance:`/`destiny:` field on individual skills.** A skill's destiny is decided wholesale by directory (`skills/` ships; `scripts/`,`tests/`,`docs/` don't), enforced once at sync-time. There is no validate-time check that a jig hasn't leaked into `skills/`. This is precisely the weakness gzkit's leak (an internal `models.md` rule escaping as an adopter gate) demonstrates is unsafe at gzkit's governance weight.

---

## 2. Cross-tool mechanism catalog

| Tool | Mechanism | What it separates / declares | Machine-enforceable? | Citation |
|---|---|---|---|---|
| **superpowers** | `EXCLUDES` array in `sync-to-codex-plugin.sh` | Lab rigging (CLAUDE.md, hooks, scripts, tests, docs) vs delivered (`skills/`, assets) | Partial — denylist in one build script; no per-surface flag, no validate-time check | `scripts/sync-to-codex-plugin.sh:54-77` |
| **superpowers** | SessionStart hook injects bootstrap skill body | Tier-0 always-load vs Tier-1 metadata-only skills | Yes (which body loads); No (whether agent obeys) | `hooks/session-start`, `hooks/hooks.json` |
| **copier** | `.copier-answers.yml` + `_commit` + `_exclude` + 3-way `copier update` | Template-owned vs user-edited files; records template version/provenance | **Yes** — full reproducible 3-way merge | [copier updating](https://copier.readthedocs.io/en/stable/updating/), [configuring](https://copier.readthedocs.io/en/stable/configuring/) |
| **cookiecutter** | replay file (answers only) | Nothing — no generated-file tracking, no native update | **No** | [replay docs](https://cookiecutter.readthedocs.io/en/stable/advanced/replay.html) |
| **create-react-app** | `npm run eject` — one-way op | Framework-owned config → user-owned config; irreversible handoff | **Yes** — enforced by dependency structure | [CRA available-scripts](https://create-react-app.dev/docs/available-scripts/) |
| **Yeoman / Rails-Thor** | write-time conflict prompt (`identical`/overwrite/skip) | Divergence detected at write; no persisted manifest | Partial — ephemeral, interactive | [Yeoman fs](https://yeoman.io/authoring/file-system.html), [Rails generators](https://guides.rubyonrails.org/generators.html) |
| **oclif** | none | Does not mark generated code at all | **No** | [oclif generator](https://oclif.io/docs/generator_commands/) |
| **Go toolchain** | `^// Code generated .* DO NOT EDIT\.$` first-line regex | Generated vs hand-authored source; published canonical regex | **Yes** — consumed by gofmt/vet/Linguist | [go generate](https://pkg.go.dev/cmd/go), [golang#13560](https://github.com/golang/go/issues/13560) |
| **GitHub Linguist** | `.gitattributes` `linguist-generated=true` | Generated surface — diff collapsed, excluded from lang stats | **Yes** — GitHub + Graphite honor it | [GitHub docs](https://docs.github.com/en/repositories/working-with-files/managing-files/customizing-how-changed-files-appear-on-github) |
| **git** | `.gitattributes` `export-ignore` | Excludes path from `git archive` release tarballs | **Yes** — `git archive` | [gitattributes manpage](https://git-scm.com/docs/gitattributes) |
| **Phabricator/Meta** | `@generated` sentinel substring | Machine-generated, auto-collapse in review | Partial — Phabricator only; GitHub/Graphite ignore the bare token | [T8527](https://secure.phabricator.com/T8527) |
| **protoc-gen-go** | `// Code generated by protoc-gen-go. DO NOT EDIT.` header | Codegen output (satisfies Go regex) | **Yes** (via Go rule) | [protobuf go-generated](https://protobuf.dev/reference/go/go-generated/) |
| **hatchling** | `[tool.hatch.build.targets.{wheel,sdist}]` include/exclude/`force-include` | Repo files vs shipped wheel/sdist; `exclude` beats `include` | **Yes** — at build time, both boundaries uniformly | [hatch build config](https://hatch.pypa.io/latest/config/build/) |
| **setuptools** | `MANIFEST.in` (sdist) + `[tool.setuptools.packages.find]` (wheel) | sdist vs wheel contents (asymmetric — MANIFEST.in ≠ wheel) | **Yes** | [setuptools misc](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html), [pkg discovery](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html) |
| **npm** | `files` allowlist + `.npmignore`; non-overridable floors | Repo vs published tarball; always-include `package.json`/README/LICENSE | **Yes** — `npm pack`/`publish` | [npm package.json](https://docs.npmjs.com/cli/v10/configuring-npm/package-json/) |
| **Docker** | `.dockerignore` (`!` negation, last-match-wins) | Repo vs build context sent to daemon | **Yes** | [Docker context](https://docs.docker.com/build/concepts/context/) |
| **pre-commit** | `repo:` field — Git URL vs `local` vs `meta` | Hook provenance: external framework vs project-authored vs built-in | **Yes** — reserved literals, schema-validated, greppable | [pre-commit.com](https://pre-commit.com/) |
| **ESLint** | `extends` (legacy) / array-position + `import` (flat) | Rule from shared preset vs project override; later-wins precedence | **Yes** — deterministic resolution | [shareable configs](https://eslint.org/docs/latest/extend/shareable-configs), [combine configs](https://eslint.org/docs/latest/use/configure/combine-configs) |
| **EditorConfig** | `root = true` | "Stop looking upward — this is the boundary"; seals from parent configs | **Yes** — reserved property, every impl halts | [editorconfig.org](https://editorconfig.org/) |
| **OPA / conftest** | `package` namespace + bundle `roots` (fail-closed overlap) | Per-rule ownership; which path-space a bundle exclusively owns | **Yes** — overlapping `roots` is a fail-closed error | [OPA bundles](https://www.openpolicyagent.org/docs/management-bundles), [conftest sharing](https://www.conftest.dev/sharing/) |
| **Claude Code Skills** | SKILL.md `description` frontmatter; body loads on invoke | Discovery-metadata vs full body (progressive disclosure, 3 levels) | Partial — `paths` glob + `disable-model-invocation` are mechanical; trigger is judgment | [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), [skills docs](https://code.claude.com/docs/en/skills) |
| **Claude Code hooks** | `PreToolUse` → `permissionDecision: "deny"` (or exit 2) on matcher `"Edit\|Write"` | Structurally blocks a tool call → forces routing | **Yes — fully deterministic, fail-closed** | [hooks reference](https://code.claude.com/docs/en/hooks) |
| **MCP** | `tools/list` (names+desc) then `tools/call` (full result) | Advertised metadata vs full payload — list-then-fetch disclosure | **Yes** — wire protocol | [MCP tools](https://modelcontextprotocol.io/docs/concepts/tools) |
| **devcontainer Features** | reference-by-OCI-ID in `features`, pulled on demand | "Scaffold ends here; reference the rest by ID + version" | **Yes** — resolver pulls/installs | [containers.dev features](https://containers.dev/implementors/features/) |
| **Diátaxis** | four quadrants (tutorial/how-to/reference/explanation) | Disclosure by reader need (acquisition↔application, action↔cognition) | **No** — authoring discipline | [diataxis.fr](https://diataxis.fr/) |

---

## 3. Patterns distilled (mechanisms, not tools)

Six reusable mechanisms recur across the corpus:

1. **Explicit generated-file sentinel (in-file, first-line, published regex).** Go's `^// Code generated .* DO NOT EDIT\.$` is the gold standard: a *canonical, documented regex* that any consumer can scan for. Makes "rendered output, do not hand-edit" machine-detectable from the file's own content.

2. **Out-of-band path-attribute marker.** `.gitattributes linguist-generated` / `export-ignore` — marks a surface as generated/non-shipped *without* touching file content, honored by external tooling (GitHub, Graphite, `git archive`). Decouples the marker from the rendered body.

3. **Provenance as a single inspectable discriminator field.** pre-commit `repo:` (`local`/`meta`/URL), ESLint `extends` vs array-position, EditorConfig `root`, OPA `package`/`roots`. Every robust provenance system reduces "where did this rule come from?" to **one greppable, schema-validated field** — not narrative.

4. **Boundary-sealing flag with directional cascade.** EditorConfig `root = true` ("stop looking upward") and OPA `roots` (exclusive path-space, fail-closed on overlap). A surface can declare "the inheritance boundary is *here*," and overlap is a structural error, not a warning.

5. **Eject as the one-way handoff event.** CRA `npm run eject` — irreversible transfer of ownership enforced by structure (dependency removed, config copied in), documented as "you can't go back." The boundary is an *event*, binary and non-drifting, vs continuous reconciliation.

6. **Lazy router + on-demand body load (metadata-first disclosure).** SKILL.md `description`-only until invoked; MCP `tools/list`→`tools/call`; devcontainer reference-by-ID. A thin always-loaded index reveals *what exists and when to reach for it*; the heavy body/result/artifact loads only on demand. superpowers' anti-`@`-link rule (`writing-skills:288`) is the disciplined enforcement of this.

A seventh, weaker pattern — **denylist in a build/delivery script** (superpowers `EXCLUDES`, `.dockerignore`, npm `files`) — separates repo-vs-shipped but lives in *one place* and carries *no per-surface declaration*; it cannot answer "is THIS file a jig?" by inspecting the file.

---

## 4. Recommendations for gzkit, split by ADR

### 4a. Firewall ADR — mechanical face

**Borrow pattern 3 (single provenance discriminator) + pattern 1/2 (sentinel) + pattern 4 (fail-closed boundary). Do NOT rely on pattern 7 (build-script denylist) alone — that is exactly superpowers' weakness and the cause of gzkit's `models.md` leak.**

Concrete design:
- **Per-surface `destiny:` frontmatter flag, closed enum, on every governed surface** (rules, skills, hooks, invariants). Model it on pre-commit's `repo:` discriminator and OPA's `package`: a single greppable, **schema-validated** field, e.g. `destiny: lab-only | delivered | shared`. `lab-only` = self-construction jig (the `models.md`-class rule); `delivered` = portable WAY shipped to adopters; `shared` = used both places. This is the missing per-file declaration superpowers lacks — its boundary is wholesale-by-directory, which is too coarse for gzkit's governance weight where a *single rule file* can leak.
- **Scaffold-time split honors `destiny:`.** `gz init` must scaffold ONLY `destiny: delivered|shared` surfaces into the adopting project — the mechanical analog of superpowers' `EXCLUDES`, but driven by the per-file flag instead of a hand-maintained path list. A `lab-only` rule is *structurally incapable* of reaching an adopter because the scaffolder filters on the flag.
- **Validate-time fail-close (the part superpowers entirely lacks).** Add a `gz validate --firewall` scope (sibling to the existing `--distribution` check) that fail-closes if: (a) any surface lacks a `destiny:` flag; (b) any `delivered` surface *references* a `lab-only` surface (the coupled-surface coherence rule — a delivered gate must not depend on a jig); (c) the rendered `gz init` output contains any `lab-only`-derived content (byte-compare, mirroring the existing ADR-0.0.31 distribution byte-equivalence check). gzkit already has `gz validate --distribution` enforcing wheel byte-equivalence — extend that same fail-closed muscle to destiny-classification.
- **Borrow the OPA `roots` fail-closed-on-overlap idea** for the firewall's exclusivity: a surface may not be simultaneously claimed by two destinies; ambiguity is an error, not a default.

**What does NOT transfer:** CRA's `eject` one-way event does not map — gzkit's relationship to adopters is *continuous governance delivery*, not a one-time config dump the user then owns forever. The adopter never "ejects" the WAY; the WAY is the product. copier's 3-way `update` merge is closer to gzkit's repeated-`gz init` reality, but copier tracks *user edits to preserve them* — gzkit's delivered governance surfaces are mostly **not** meant to be user-edited (they are rendered output), so gzkit needs sentinel pattern 1/2 ("DO NOT EDIT — rendered by gz") on delivered surfaces *more* than it needs copier's edit-preservation merge. Use a Go-style first-line sentinel on every rendered control surface so an adopter's agent knows not to hand-edit it.

### 4b. Firewall ADR — communicative face

**Borrow pattern 6 (lazy router + on-demand body) and map it onto gzkit's existing CMS (corpus → compress → rendition → playback).** superpowers' communicative win is that the boundary is *delivered as a live injected surface* (the SessionStart bootstrap), not a static README an agent may never read.

Concrete design:
- **A rendered, disclosed "scaffold boundary" surface — not hand-written prose.** gzkit's CMS already does progressive disclosure of control surfaces. Author the boundary self-explanation as **corpus entries** (via `gz content remember`, the existing append-only corpus path), compressed/rendered into a delivered surface that says, mechanically and per-section: *"This is the WAY (delivered). This is yours to extend (your project's authored rules). Here is where the gzkit scaffold ends (lab-only, not present in your repo)."* The content is **generated from the `destiny:` classification** (4a), so the communicative face is a *rendition of the mechanical face* — they cannot drift, because the explanation is derived from the same flags the scaffolder and validator read. This directly answers the operator's "mechanically explain, NOT hand-written prose."
- **Inject it at the adopter's session start, superpowers-style.** gzkit already ships a SessionStart hook (`scripts/session_orientation.py`, per AGENTS.md "Always #1"). Extend it to surface the boundary disclosure — the adopter's agent learns "what is the WAY vs what is yours" every session, lazily (metadata-first: a short index, full section on demand), the way superpowers injects `using-superpowers` and nothing else.
- **Mark provenance on each delivered rule so the adopter's agent can answer "did this gate come from gzkit or from us?"** — exactly pre-commit's `repo:` and ESLint's `extends` provenance. A `provenance: gzkit-canon | project-authored` field renders into the disclosed surface so a downstream agent knows a gate's origin (the communicative dual of the mechanical `destiny:` flag).

**What does NOT transfer:** superpowers' *lightness* — its README is a one-time static doc and its self-explanation is ~150-word skill bodies (`writing-skills:218`). gzkit is far heavier governance; its boundary surface will carry more, and the token-budget discipline (<150/<200 words) cannot be copied verbatim. But the *mechanism* (metadata-first, lazy-loaded, injected-at-session-start, derived-not-authored) transfers fully. Diátaxis is a useful *organizing* lens for the disclosed surface (separate the "how the WAY works" tutorial from the "where the boundary is" reference) but is authoring discipline only — not a gate.

### 4c. Skills-First Enforcement ADR

**The strongest enforceable pattern in all the prior art is the Claude Code `PreToolUse` hook returning `permissionDecision: "deny"` — and superpowers does NOT use it.** Be explicit with the operator: superpowers' "mandatory skills" claim (`README.md:170`) is **prompt-pressure goodwill**, not enforcement. Its entire apparatus is a `SessionStart` context injection + `<EXTREMELY-IMPORTANT>` framing + a rationalization-rebuttal table (`using-superpowers:82-95`). A model that ignores the injected bootstrap hits no wall. That is *exactly* the "goodwill, not enforced" state gzkit says it wants to leave behind.

What actually forces skills-first vs what is convention:
- **Convention/goodwill (superpowers, and gzkit today):** SessionStart injection + prompt framing + decision flowchart. Effective but not fail-closed.
- **Structural enforcement (the transferable mechanism):** A `PreToolUse` hook on matcher `"Edit|Write"` that returns `permissionDecision: "deny"` (or exit code 2) with a `permissionDecisionReason` directing the agent to invoke the matching skill first ([hooks reference](https://code.claude.com/docs/en/hooks)). This is the *only* mechanism in the corpus that converts skills-routing from judgment into a deterministic gate. Anthropic's own skills doc defers to it: when prose stops shaping behavior, *"use hooks to enforce behavior deterministically."*

Recommended design: a gzkit `PreToolUse` hook that, when an `Edit`/`Write` targets a governed surface (e.g. anything under `.gzkit/**`, `src/gzkit/**`, rules dirs) with no active skill/pipeline context in the ledger, **denies the call** with a reason naming the skill to route through. This is the structural version of gzkit's existing "Invariant 10a — skill-tool-invoke-same-turn" and AGENTS.md "SKILLS FIRST" — today those are *contract text* (goodwill); the hook makes them *fail-closed*. gzkit already uses blocking hooks (AGENTS.md "Never #6: Do not work around hook blocks"), so the enforcement primitive is already in the toolbox — this ADR extends it from gate-state to skills-routing.

**What does NOT transfer:** superpowers gives you the *prompt-pressure* layer (the rationalization table and 1%-rule framing are genuinely well-tuned and worth porting into the deny-reason text), but it gives you **zero** structural enforcement to copy — you must build the `PreToolUse` deny gate yourself. Also, gzkit's deny must be *scoped* (govern only governed surfaces, not all edits) or it will block routine work — superpowers' all-or-nothing session injection doesn't model this scoping problem because it never gates tools at all.

---

## 5. Open questions / gaps the prior art does NOT answer for gzkit

1. **Per-surface destiny classification at gzkit's granularity is unprecedented.** Every prior-art boundary is either wholesale-by-directory (superpowers `EXCLUDES`, npm `files`) or per-rule-*provenance* (pre-commit `repo:`) — but none combine *per-file destiny* (lab vs delivered) *with* fail-closed validate-time leak detection. gzkit is inventing the synthesis; no template to copy.

2. **Edit-preservation vs render-only delivery is unresolved.** copier preserves user edits via 3-way merge; gzkit's delivered surfaces are mostly rendered output (DO-NOT-EDIT). But gzkit *also* wants adopters to author their *own* project rules alongside delivered ones. No prior tool cleanly separates "rendered-by-framework, do not touch" from "yours to author" *within the same rules directory* — gzkit must define how a `project-authored` rule coexists with a `delivered` rule without the firewall flagging the former as a leak.

3. **Scoping the skills-first deny gate without blocking routine work.** superpowers never gates tools, so it offers no precedent for *which* edits trigger a deny vs pass. gzkit must define the matcher scope (governed surfaces only) and the "active context" predicate (what ledger/pipeline state proves a skill is already in play) — entirely gzkit-specific, no prior art.

4. **Multi-harness firewall parity.** superpowers ships per-harness mirrors (Claude/Codex/Gemini/Copilot/Cursor) but its boundary lives in one Codex-specific sync script; the `PreToolUse` deny primitive is **Claude-Code-specific**. gzkit mirrors skills across `.claude`/`.agents`/`.github` — how the firewall (mechanical) and the skills-first deny (enforcement) behave on harnesses that lack a `PreToolUse`-equivalent hook is unanswered. On those harnesses, gzkit may be back to goodwill-only, and the ADR must say so explicitly rather than claim uniform enforcement.

5. **Does the communicative surface itself ship as delivered or lab-only?** The boundary-explanation surface describes the firewall — is it `destiny: delivered` (the adopter sees gzkit explaining itself) or partly `lab-only`? Self-reference (the firewall classifying the artifact that explains the firewall) has no prior-art precedent; gzkit must resolve the bootstrap circularity.

---

*Repo evidence: `/tmp/superpowers` (obra/superpowers v5.1.0). Load-bearing files: `scripts/sync-to-codex-plugin.sh:54-77` (the EXCLUDES firewall), `hooks/session-start` + `hooks/hooks.json` (SessionStart injection — the only hook; no PreToolUse), `skills/using-superpowers/SKILL.md` (bootstrap, prompt-pressure enforcement), `skills/writing-skills/SKILL.md:146,218,278-288` (progressive-disclosure doctrine, anti-@-link rule), `README.md:19,170` (static self-explanation), `CLAUDE.md` (contributor-only, not shipped).*
