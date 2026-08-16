# gzkit CLI — comprehensive structural analysis

> **Status: design exploration.** Nothing booked, no ADR, no ledger event, no
> source change, campaign (Movement B) undisturbed. Measured against `main` /
> `8755af161` on 2026-08-16 by walking the **live `argparse` tree**, not by grep.
>
> **Baseline ruling (operator, 2026-08-16):** clig.dev is gzkit's declared CLI
> baseline; OpenStack `cliff` is guidance. Divergences from the baseline are
> therefore **corrections** under AGENTS.md § Operator Doctrine (*"discovering that
> more is needed to fulfil the intent of a feature is not an enhancement, it is a
> correction"*), not enhancements.
>
> Sources consulted directly: <https://clig.dev/> and
> <https://docs.openstack.org/cliff/latest/>.

---

## 0.1 The governing finding: gzkit already declared this standard

`docs/design/cli-standards-v3.md` § Command Structure declares the house grammar
in gzkit's own words:

> "Commands use **grouped subcommands** (git-style): `projectname <group>
> <command> [options] [arguments]`"

and its § Output Modes declares `--json` as a standing mode, and its § Output Rules
declares a single chokepoint:

> "**Never call `print()` directly for user-facing output.** Always go through the
> formatter. **Never call `rich.print()` or `console.print()` outside of the
> formatter.**"

**The shipped CLI does not meet its own declared standard on three independent
axes**, measured 2026-08-16:

| Declared in `cli-standards-v3.md` | Shipped | Gap |
|---|---|---|
| `<group> <command>` grammar | 35 of 136 leaves are bare verbs at root, no group | § 3 G1/G2 |
| `--json` as a standing output mode | 63 of 136 leaves have no `--json` | § 3 G6 |
| formatter is the sole output chokepoint | **1,230 `console.print(` call sites** in `src/gzkit`, against **1** `OutputFormatter` class | new — § 3 G10 |

This removes the ambiguity flagged in earlier drafts about whether grammar work is
correction or enhancement. **The intent was declared, in-repo, and is unmet.** It is
correction work under the owning design doc, independently of clig.dev.

### 0.2 The standards doc is itself duplicated

`docs/design/CLI_PRINCIPLES.md` and `docs/design/cli-standards-v3.md` are
**byte-identical** (md5 `93e5751eeeee7fa97605f3396e4693b3`, 1037 lines each). Two
filenames, one content, no pointer between them and no statement of which is
source-of-truth. A reader citing "the CLI principles doc" cannot know which they
mean, and an edit to one silently diverges from the other.

This is the same defect class the repo's own § Architectural Boundaries names —
derived/duplicate surfaces becoming ambiguous authorities. **Resolve before citing
either as the standard.**

### 0.3 Known-stale content in the standards doc

The doc carries a retirement banner of its own: the `ports/` + `adapters/` +
`tests/fakes/` facade it describes was retired (2026-07-06 injection-seam ruling),
and its § Project Structure therefore describes a layout gzkit does not have. Its
§ Spectrum Summary classifies a "Platform CLI" as *"Multiple domains, 60+
commands"* — which is precisely gzkit (59 root verbs, 136 leaves), so the
platform-column guidance is the applicable one, not the utility default the
document leads with.

**Consequence for planning: the standards doc needs a freshness pass before it can
govern.** Parts are canon, parts are retired, and nothing marks which is which
except one banner about the facade.

---

> Reproduce the inventory: `introspect_cli.py` → `cli_inventory.json` →
> `analyze_cli.py` (session scratchpad).

---

## 0. Verdict — precise, and split by layer

The claim "grammar and structuring logic are not consistent in shape or behavior"
is **confirmed for grammar and for behavior; it is *not* confirmed for dispatch.**
That distinction is load-bearing for planning, because the consistent layer is the
one a refactor is most likely to damage.

| Layer | Consistent? | Evidence |
|---|---|---|
| **Dispatch mechanism** | **YES — uniformly** | 0 `args.command ==` chains; 150 `set_defaults(func=…)`; single `main()` dispatch at `main.py:138`; 108 of 113 handler bindings through one `_lazy` resolver; fenced by `test_handler_manifest_resolves.py` (both directions) |
| **Command grammar** | **NO** | 8 distinct inconsistency classes, § 3 |
| **Output behavior** | **NO** | 63/136 leaves lack `--json`; 9 groups have mixed sibling coverage, § 3 G6 |
| **Structural placement** | **PARTIALLY** | one registration idiom, but 2 of 8 registrars sit in the wrong package and defeat a documented invariant, § 3 G9 |

**So: the plumbing is sound and uniform. The surface it exposes is not.** Any plan
should protect the first while correcting the second — they are separable, and
conflating them is the main risk in this work.

---

## 1. Method

The inventory is derived by importing `gzkit.cli.main`, calling `_get_parser()`, and
walking `parser._actions` / `_SubParsersAction.choices` recursively. This measures
what the CLI **actually exposes**, not what any doc claims. Common flags
(`-h/--help/--quiet/--verbose/--debug/--version`) are excluded from all counts since
`_propagate_common_flags` puts them on every node.

---

## 2. Baseline inventory

| Metric | Value |
|---|---|
| Total parser nodes | 164 |
| Leaf commands (have `func`) | 136 |
| Group nodes (have subparsers) | 28 |
| Max depth | 3 |
| Leaves at depth 1 / 2 / 3 | **35 / 95 / 6** |
| Aliases | 0 |
| Leaves with `--json` | 73 / 136 |
| Leaves with `--dry-run` | 32 / 136 |
| Leaves taking **zero positionals** | 58 / 136 |

---

## 3. Inconsistency classes

### G1 — Grammar bifurcation: 35 bare verbs vs 28 nouns

Two incompatible grammars are live at the root simultaneously.

*Noun-verb (clig.dev-conformant):* `adr`, `obpi`, `task`, `arb`, `content`,
`handoff`, `ontology`, `chores`, `skill`, `plan`, `personas`, `complexity`, …

*Bare verb, no noun:* `attest`, `audit`, `check`, `closeout`, `context`, `covers`,
`drift`, `gates`, `implement`, `interview`, `justify`, `preflight`, `roles`,
`smoke`, `specify`, `state`, `status`, `test-shape`, `tidy`, `validate`, …

There is no rule separating the two sets. `gz obpi complete` is noun-scoped;
`gz closeout` and `gz attest`, which act on the same artifacts at the same
lifecycle stage, are not.

**Severity: high (root cause of G2).** Effort: large — this is the rename corpus.

---

### G2 — Verb shadowing: the same verb means different things at different nodes

| Verb | Occurrences | Paths |
|---|---|---|
| `audit` | **7** | `gz audit`, `chores audit`, `cli audit`, `obpi audit`, `plan audit`, `readiness audit`, `skill audit` |
| `list` | **7** | `chores`, `content`, `handoff`, `obpi lock`, `personas`, `skill`, `task` |
| `status` | 3 | `gz status`, `adr status`, `obpi status` |
| `validate` | 3 | `gz validate`, `arb validate`, `obpi validate` |
| `check` | 3 | `gz check`, `obpi lock check`, `parity check` |
| `advise` | 3 | `arb advise`, `chores advise`, `complexity advise` |

`list` recurring 7× is **correct** — it is the same operation over different nouns.
That is what noun-verb grammar is for.

`audit` recurring 7× is **not** the same operation: `gz cli audit` checks doc
coverage, `gz plan audit` checks ADR/brief alignment, `gz audit` runs the ADR audit
routine and writes proof artifacts. Three different contracts under one word.

The sharpest instance: **`gz audit` is the ADR audit routine but is not under
`gz adr`** — while `gz adr audit-begin`, `gz adr audit-check`, `gz adr audit-end`
all are. One conceptual family split across two grammatical levels.

13 depth-2 leaves shadow a bare root verb of the same name:

```
gz adr status      shadows  gz status        gz obpi audit      shadows  gz audit
gz obpi status     shadows  gz status        gz plan audit      shadows  gz audit
gz arb validate    shadows  gz validate      gz readiness audit shadows  gz audit
gz obpi validate   shadows  gz validate      gz skill audit     shadows  gz audit
gz arb typecheck   shadows  gz typecheck     gz chores audit    shadows  gz audit
gz parity check    shadows  gz check         gz cli audit       shadows  gz audit
gz personas drift  shadows  gz drift
```

**Severity: high — this is the discoverability defect.** A user who learns
`gz audit` has learned nothing transferable about the other six.

---

### G3 — Morphological drift

- **Singular/plural pair as two verbs:** `gz flags` (leaf, list-all) vs `gz flag`
  (group, `explain`). Same noun, two nodes, two numbers.
- **Group nouns disagree on number:** plural `chores`, `personas`, `insights`,
  `content` vs singular `skill`, `task`, `adr`, `obpi`, `plan`, `flag`.
- 10 plural-named root nodes overall: `check-config-paths`, `chores`, `covers`,
  `flags`, `gates`, `insights`, `personas`, `register-adrs`, `roles`, `status`.

**Severity: medium.** Effort: small per verb, but each is a corpus rename.

---

### G4 — Kebab-compounds encoding a noun-verb pair the tree already supports

Six at root: `check-config-paths`, `git-sync`, `migrate-semver`, `permitted-entry`,
`register-adrs`, `test-shape`.

Each hyphenates precisely the relationship subcommands express:

Proposed forms below are **unregistered** — each carries the speculative marker so
`gz validate --cli-alignment` skips it (`.claude/rules/governance-core.md`
§ Operator-doc verb resolution).

<!-- gz-validate-skip: command-shape -->
- `register-adrs` → `gz adr register` — the `adr` group already exists
<!-- gz-validate-skip: command-shape -->
- `check-config-paths` → `gz config check-paths` — no `config` noun yet
<!-- gz-validate-skip: command-shape -->
- `permitted-entry` → `gz airlock permitted-entry` — `airlock` group already exists; same subsystem
<!-- gz-validate-skip: command-shape -->
- `migrate-semver` → `gz adr migrate-semver`
<!-- gz-validate-skip: command-shape -->
- `test-shape` → `gz test shape` — but `test` is a **leaf**, which blocks the group
<!-- gz-validate-skip: command-shape -->
- `git-sync` → `gz git sync`

**And the same class recurs at depth 2:** `gz adr audit-begin / audit-check /
audit-end / covers-check` are kebab-flattened where `gz obpi lock {check, claim,
list, release}` is a real depth-3 group. **Two different solutions to the identical
shape problem, both live.**

**Severity: medium.** Note `gz test-shape` cannot become `gz test shape` without
resolving G8-style leaf/group collision on `test`.

---

### G5 — Target expressed as flag rather than argument

58 of 136 leaves take **zero positionals**. Worst:

| Command | Flags | of which boolean |
|---|---|---|
| `gz validate` | 101 | **93** |
| `gz handoff create` | 17 | 1 |
| `gz git-sync` | 13 | 11 |
| `gz state` | 6 | 6 |
| `gz status` | 5 | 4 |

**Correction (2026-08-16, after fetching clig.dev).** An earlier draft of this
document justified positionals by asserting "clig.dev: arguments name the thing
acted upon, flags modify how." **clig.dev does not say that.** It says the
opposite as its default:

> "Prefer flags to args. It's a bit more typing, but it makes it much clearer what
> is going on. It also makes it easier to make changes to how you accept input in
> the future."

with a narrow exception this case plausibly fits:

> "Multiple arguments are fine for simple actions against multiple files. For
> example, `rm file1.txt file2.txt file3.txt`."

So `gz validate manifest ledger briefs` is defensible as *homogeneous multiple
targets* (the `rm` shape), **not** as clig.dev conformance. The surviving arguments
for W3 are: the 45-line usage block collapses; ~280 lines and 2 now-subjectless
parity tests are deleted; typo UX improves via `difflib` suggestions. Those stand
on their own. "clig.dev requires it" does not.

The finding here is that flag-as-target is a **class**, not a one-off — `git-sync`'s
11 booleans are mode selectors, and `state`/`status` select *what to report* via
flags. Whether that is a defect depends on a house rule gzkit has not written down.

**Severity: medium for `validate` (down from high — the grounding weakened),
low elsewhere pending a house rule.**

---

### G6 — Output-contract drift (this is the *behavioral* inconsistency)

`.claude/rules/cli.md` § Output Contracts requires `--json` for machine
consumption. **63 of 136 leaves lack it**, and the gaps are not principled — nine
groups have *mixed sibling coverage*:

| Group | has `--json` | lacks it |
|---|---|---|
| `adr` | audit-check, covers-check, demote, evaluate, promote, status | audit-begin, audit-end, emit-receipt, fidelity, report |
| `obpi` | audit, brief-drift, complete, precomplete, present-evidence, status, sync | emit-receipt, pipeline, repudiate, supersede, validate, withdraw |
| `arb` | advise, archive, patterns, validate | coverage, red, ruff, step, ty, typecheck |
| `content` | list, show | advise-rendition, commit, compose, edit, import, remember, render, retire |
| `chores` | doctor | advise, audit, list, plan, propose-ghi, run, show |
| `complexity` | advise, guide | distill |
| `skill` | audit, list | new |
| `plan` | audit | create |
| root | 15 verbs | 20 verbs |

`gz adr emit-receipt` has no `--json` while `gz obpi audit` does — both produce
structured governance evidence that agents consume.

**Severity: high, and highest-value-per-unit-effort.** This is additive: adding
`--json` breaks no existing invocation, needs no corpus rename, and is
independently verifiable. It is also the only class that changes *behavior* rather
than spelling.

---

### G7 — Group/leaf decision uncorrelated with cardinality

Eleven groups wrap exactly one verb:

```
gz agent sync (→ control-surfaces)   gz insights remember
gz cli audit                         gz issue file
gz flag explain                      gz parity check
gz frontmatter reconcile             gz patch release
gz governance render                 gz task envelope diagnose
```

Simultaneously, 35 verbs sit bare at root with no noun. So `audit` gets a `cli`
noun for one command, while `attest`, `closeout`, and `implement` — a coherent
lifecycle family — get none. `gz agent sync control-surfaces` is a group-of-one
wrapping a group-of-one, three levels deep for a single operation.

**Severity: medium (cosmetic, but it is the visible symptom of "no rule exists").**

---

### G8 — `gz mx` is simultaneously a leaf and a group

`mx` carries a `func` default **and** subparsers (`enter`, `exit`) — the only node
in the tree with both contracts. `gz mx` does one thing; `gz mx enter` does another.
Unique in 164 nodes; either a deliberate default-subcommand or an accident, and
nothing in the tree distinguishes those cases.

**Severity: low, but it is a genuine one-off.** Worth a deliberate ruling.

---

### G9 — Registration placement violates the invariant `main.py` documents

Eight `register_*_parsers` functions. **Six** live in `src/gzkit/cli/parser_*.py`.
**Two** — `content`, `insights` — live in `src/gzkit/commands/`, and are imported
eagerly at [`main.py:18-19`](../../src/gzkit/cli/main.py).

Consequence, measured at parser-build time:

```
gzkit modules loaded : 82   (of which gzkit.commands.*: 5)
heavy deps present   : pydantic, rich, yaml
gzkit.commands.common: 69ms cumulative — LOADED
```

Chain: `main.py:19` → `gzkit.commands.insights` → [`insights.py:19`](../../src/gzkit/commands/insights.py) `from gzkit.commands.common import get_project_root` → yaml + pydantic.

`main.py:22-26` states the invariant being violated in its own words — keep
`commands.common → sync → yaml` out of every `gz --help` (GHI #180). The `__getattr__`
lazy-export guard defends a *different* door than the one standing open.

Mitigating fact: `gz --help` still runs in **0.12s**. The invariant is breached; the
consequence is currently not painful.

**Severity: medium. Effort: smallest in this document — two edits.** This is the
only class that is a straightforward defect rather than a design question.

---

### G10 — The declared output chokepoint is bypassed 1,230 times

`cli-standards-v3.md` § Output Rules: *"Never call `rich.print()` or
`console.print()` outside of the formatter. The formatter is the single chokepoint
for all user-facing output."*

Measured in `src/gzkit`:

| | Count |
|---|---|
| `console.print(` call sites | **1,230** |
| `OutputFormatter` class definitions | 1 |

`gz`'s own entry point does it — [`main.py:153`](../../src/gzkit/cli/main.py) prints
errors via `console.print(f"[red]{exc}[/red]")`.

This is the structural cause of **G6**: `--json` cannot be a reliable mode when
1,230 sites emit human-formatted text directly. Adding a `--json` flag to a command
whose body calls `console.print` produces a flag that does not fully work — so
**W2 must be scoped as "route through the formatter", not "add a flag"**, or it
will produce exactly the shape-graded green the repo's doctrine refuses.

**Severity: high — it is the precondition for G6.** Effort: large, and the true
size of the `--json` workstream. Note this is a scaffold-layer finding, not a
grammar one; it is independent of every rename.

---

## 3.5 The overall trend — doctrine holds exactly where a witness exists

Requested by the operator, 2026-08-16: *"gzkit is mature enough to run a fresh
evaluation on what overall trends exist."*

Scoring every CLI-layer rule declared in `cli-standards-v3.md` and
`.claude/rules/cli.md` against what ships:

| Declared rule | Shipped | Has a mechanical arm or shared helper? |
|---|---|---|
| 4-code exit map (0/1/2/3) | **Fully implemented** — `EXIT_*` constants, `exit_code_for()`, shared epilog | **Yes** — `cli/helpers/exit_codes.py` |
| "Include at least one example" per command | **151 of 166** `add_parser` calls carry `epilog=` (91%) | **Yes** — `cli/helpers/epilog.py` |
| Manpage / index coverage per verb | enforced, fail-closed | **Yes** — `gz cli audit` |
| Every verb has a wielding skill | enforced, 20 explicit waivers | **Yes** — `gz validate --skill-alignment` |
| `--json` as a standing mode | **73 of 136** leaves (54%) | **No** |
| `--plain` as a standing mode | 13 call sites | **No** |
| `NO_COLOR` / `isatty` degradation | 12 sites each | **No** |
| Formatter is sole output chokepoint | **1,230 bypasses** vs 1 formatter | **No** |
| structlog logging stack + correlation IDs | **2 imports, 1 `get_logger`** | **No** |
| `--log-file` flag | **0 occurrences — does not exist** | **No** |

**The correlation is near-total.** Every rule with a mechanical arm or a shared
helper that makes conformance the path of least resistance is at or near 100%.
Every rule that exists only as prose is at or near 0%. Nothing in the middle except
`--json`, which is precisely the rule with a *convention* but no helper.

### The sharpest instance: the logging stack is built but unwired

`src/gzkit/cli/logging.py` is 156 lines implementing the declared stack —
structlog, correlation IDs, JSON-to-stderr, dual handlers. `configure_logging`
appears in exactly one place outside its own module: the lazy-export map in
`cli/__init__.py`. **`main.py` never calls it.** Debug mode instead does:

```python
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(name)s: %(message)s")
```

— stdlib logging, not structlog. `structlog` is a declared runtime dependency in
`pyproject.toml` supporting one real consumer (`commands/chores.py`).

This is the identical failure the standards doc's own retirement banner describes
for the ports/adapters facade: *"it was wired into zero production code."* **The
same class recurred in the same document's other half, and nothing caught it** —
because the ports facade was retired by an operator ruling, not by a check.

### Why this matters more than the grammar findings

This is gzkit's own thesis, reproduced inside gzkit's own CLI layer. AGENTS.md
§ MAKE LLM STOCHASTIC VIBES INERT, operative claim 3: *"Doctrine drift is invariant
drift. Silent rule/threshold changes without a witness are the root failure."*
`docs/governance/advisory-rules-audit.md` scores governance rules
Mechanical/Promotable/Judgment on exactly this axis.

**The CLI layer has never been scored that way.** Applying the repo's existing
scorecard method to `cli-standards-v3.md` would have surfaced every row above.
That is a cheaper and more durable move than any individual workstream here: it
converts a 1,037-line prose standard into a ranked list of what is witnessed, what
is promotable, and what is judgment — and it composes with machinery that already
exists (`gz validate --advisory-scorecard`).

**Planning consequence: prefer building the witness to fixing the instance.**
Adding `--json` to 63 commands without a check leaves the 64th to drift. The
ordering that follows from this table is: score the doctrine, build the arm, then
sweep.

---

## 4. What is consistent — protect this

1. **Dispatch is uniform and total.** Every leaf routes via `set_defaults(func=…)`;
   `main()` does `getattr(args, "func", None)`. No conditional dispatch anywhere.
2. **Handler resolution is single-sourced and fenced.**
   `parser_handler_manifest.py` holds one `_LAZY_HANDLERS` map + one resolver;
   `test_handler_manifest_resolves.py` asserts both directions (every entry
   resolves; every call site names a known key).
3. **`gz validate`'s internals are already registry-driven.** `VALIDATOR_REGISTRY`
   is the single source for runners, tier split, and `_resolve_scopes`, with parity
   fences.
4. **Zero aliases**, so no hidden second grammar to reconcile.

**Planning consequence: a "Command pattern refactor" of the dispatch layer would
replace a fenced, uniform, working mechanism. The defects are all in naming, output
contracts, and placement — none in dispatch.**

---

## 5. Blast radius

Live vs sealed references (sealed = inside `docs/design/adr/**`, which includes
`audit/proofs/*.txt`). Indicative counts — prose citations inflate them:

| Verb | Live | Sealed |
|---|---|---|
| `validate` | 8202 | 4162 |
| `covers` | 991 | 469 |
| `status` | 680 | 264 |
| `git-sync` | 651 | 51 |
| `register-adrs` | 224 | 73 |
| `check-config-paths` | 188 | 41 |
| `audit` | 182 | 83 |
| `permitted-entry` | 165 | 24 |
| `drift` | 135 | 80 |
| `flags` | 89 | 55 |
| `test-shape` | 37 | 0 |
| `migrate-semver` | 33 | 1 |

Plus 21 skills declaring `gz_command:` frontmatter.

**Binding constraint: sealed references must never be rewritten.** They record what
was actually executed. `governance-core.md` applies exactly this reasoning to
terminal OBPI briefs ("sealed historical records"). Therefore **every rename must
retain its old spelling permanently as a hidden alias** — not on a deprecation
timer. Compatibility here is a correctness property, not a courtesy.

Mechanical consumers that must move in the same commit as any structural change
(AGENTS.md § DO IT RIGHT 1a):

- `gz cli audit` — manpage/index coverage + usage-line agreement (GHI #693)
- `gz validate --cli-alignment` — every `gz <verb>` in operator docs must resolve
- `gz validate --skill-alignment` — every root verb needs a wielding skill
- `gzkit.doc_coverage.scanner` — **AST-scans `cli/parser_*.py` for `_LAZY_HANDLERS`
  dict literals and standalone `p_foo.set_defaults(func=…)`**

That last one is the trap: a move to declarative `Command` objects would leave
these scanners **green while blind**.

---

## 6. Recommended workstreams

Ordered by value ÷ risk, not by conceptual appeal.

| # | Workstream | Classes | Breaks callers? | Effort | Value |
|---|---|---|---|---|---|
| **W0** | Resolve the duplicated standards doc; freshness-pass its retired sections | § 0.2, 0.3 | No | S | **Gates everything** — nothing can cite a standard that exists twice |
| **W1** | Fix eager-import leak (move 2 registrars; defer `common` import) | G9 | No | XS | Restores a documented invariant |
| **W2** | Route output through the formatter, *then* `--json` parity | G6, **G10** | No (additive) | **L** (was M) | Highest — behavioral, agent-consumed |
| **W3** | `gz validate` positional grammar + hidden `append_const` aliases | G5 | No (aliased) | S–M | Deletes ~280 lines + 2 now-subjectless parity tests |
| **W4** | Alias infrastructure: hidden-alias helper + `gz cli audit` awareness | all renames | No | S | Prerequisite for W5/W6 |
| **W5** | Kebab-compound → noun-verb (6 root + 4 `adr audit-*`) | G4 | No (aliased) | M | Grammar coherence |
| **W6** | Root-verb nouning + shadow resolution (`audit` → `adr audit`, `flag`/`flags` collapse) | G1,G2,G3,G7 | No (aliased) | **L** | Largest coherence win, largest corpus cost |
| **W7** | Rule the `gz mx` leaf+group anomaly | G8 | Maybe | XS | Removes a one-off |

**W1 and W2 are worth doing on their own merits regardless of whether any grammar
work ever happens.** W4 gates W5/W6 — without a hidden-alias mechanism, renames
either break sealed-proof truthfulness or require a 1,700+ reference sweep.

Deliberately **not** recommended:

- **Typed `Command` protocol replacing `_lazy`** — argparse needs the whole tree
  eagerly, so the string seam survives *inside* the Command; it buys adjacency, not
  safety (the seam is already fenced), and blinds the AST scanners.
- **Lazy subtree construction (cliff-style)** — architecturally the interesting
  option and the one that would dissolve the `parser._actions` private-API walk in
  `_propagate_common_flags`, but it is justified by a startup cost that measurement
  shows is 0.12s. Revisit only if that changes.

---

## 7. Routing

Every workstream except W1 is a CLI contract change. `.claude/rules/cli.md`
§ Heavy Lane Trigger covers *"subcommands, flags, exit codes, output schemas"*;
AGENTS.md § Defect-fix routing sends contract-bearing CLI work to `gz obpi
pipeline` under an ADR.

W1 alone plausibly meets the direct-fix thresholds (≤10 source lines, ≤2 files,
single surface, defect surfaced in flight) — it restores a stated invariant rather
than changing a contract.

W6 crosses enough surfaces that it would need decomposition into per-family OBPIs.

---

## 8. Decisions needed before any of this leaves exploration

1. **Does grammar work happen at all**, given Movement B is Magna Carta topmost?
2. **Is the hidden-permanent-alias posture accepted** as the answer to sealed
   proofs — i.e. old spellings never removed?
3. **Is `--json` parity (W2) separable** and worth running on its own? It has no
   grammar dependency and is the only behavioral defect here.
4. **`gz mx`:** deliberate default-subcommand, or accident?
5. **Scope of nouning:** full G1 correction, or only the shadowed verbs (G2), which
   is ~13 renames instead of ~35?
