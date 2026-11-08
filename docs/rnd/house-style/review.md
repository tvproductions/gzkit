# House style — review account

A readable view over [the run's record](../house-style.md), rewritten at the second close
(2026-11-08) for the operator's review before sign-off. It holds no authority; the record does, and
every ruling there is quoted verbatim. Names are marked **ruled**, **sourced**, **contradicted** or
**unsourced**. Inventory numbers refer to
[the candidate inventory](sources/candidate-inventory-2026-11-08.md).

## The problem

You asked how to express hexagonal design intent strongly and make the model aware of it during any
code work. What existed was weak: a 7 KB rule loading on every Python file read, a canon page, and
one gate that checks only `core/` and runs only in `gz check --full` and CI (**sourced**). When the
run widened to the house style as a whole, an inventory found 108 candidate preferences, 14
borderline items and 13 contradictions in canon. Most preferences are rule text only, and `gz init`
copies rule text to adopters but none of gzkit's witnesses (**sourced**).

## The model

- **A house style** is a set of preferences, each admitted only by your ruling against a stated test
  (does it shape how every project built with gzkit is designed?), each carried the RP-9 way wherever
  a check can catch a violation (**ruled**, Q1 and Q6). Presence in gzkit admits nothing (**ruled**,
  your correction).
- **One place:** a data register of members, each with its statement, family, enforcement moment,
  named check, adopter delivery and owner; a validator fails a member whose check does not exist or
  runs on no gate; one page is generated from it; rules and `AGENTS.md` cite members by id (**ruled**).
- **Four enforcement moments** (**ruled**, Q9 and F8): as code is written (the post-edit Ruff hook,
  already built), at the start of work (the airlock's brief), at review (an independent reviewer with
  the house style as its rubric), and in a sweep (chores).
- **MAXX Astral for gzkit and every adopter** (**ruled**, F4): Ruff `ALL`, ty at full strength, the
  uv project model, exceptions only with strong justification.
- **Where facts live** (**ruled**, Q8, Q15, F13 item 86): code-design facts in `pyproject.toml`
  `[tool.py-gzkit]`; tool configuration in each tool's `[tool.*]` table; gzkit's governance settings in
  `.gzkit.json`; registers and baselines in `data/*.json`; schemas generated from Pydantic models;
  YAML only for front matter and files a third party dictates; no value authoritative in Markdown.

## Hexagonal, the foundation

- **The whole system, not the core** (**ruled**, your correction): core, ports, driving and driven
  adapters, the composition root.
- **An upfront map,** every module placed in a region, approved once as a classic ADR, changed only
  through a new one (**ruled**, Q12); gzkit's whole package held to it, out-of-place imports on a
  baseline owned to zero (**ruled**, Q4 and F6 item 43).
- **A signal at intake** from each outcome's `modules`, **enforced at the work package freeze**: no
  baseline freezes until every module is placed and any map change cites a Current classic ADR
  (**ruled**, Q10 and Q13). Ad hoc work is reached by the airlock's guidance and the chore.
- **Admitted from F1:** the primary directive, to be strengthened with a better specification and
  strong adoption by every adopter; stdlib first with Pydantic the core's one exception; "why is this
  here?"; the DDD, HA, BDD, TDD cascade, with constraints before the first red test (**ruled**).
- **Sent to a hexagonal specification run:** domain-typed ports, Protocol and composition, the
  second-adapter rule, parameter injection and config loaded once at the boundary, separation of
  concerns, implicit globals beyond `global`, folder layout (you now disagree with canon rule 7),
  what subsumption into one typed model means, the DDD and ontology relation, and layered state with
  an append-only event log (**ruled**, F1, F8, F11, borderline).

## The families, as ruled

1. **F1 Architecture:** as above.
2. **F2 Dependency posture:** stdlib first; five-year aging (its value into data); the exception
   register, hostile to anything non-Astral; argparse; pyyaml necessary, its reason stressed;
   jsonschema retired for Pydantic models; jinja2 kept for the control-surface pipeline only, the
   justify walkthrough moved to plain Python; rich kept as the CLI's human-mode renderer behind a
   corrected, domain-typed output port.
3. **F3 Data models:** Pydantic for every model, no dataclasses; frozen and `extra="forbid"`; field
   descriptions; TypedDict (stdlib) for shapes; models hold data, logic lives in services.
4. **F4 Typing:** modern syntax; deferred annotations, and a new Python version's idioms adopted
   strictly; ty suppression syntax; full annotation.
5. **F5 Errors and suppression:** no finding closed by suppression, anywhere; suppressions Ruff-native
   (PGH004, RUF100, RUF105 lifted, 1,613 `noqa` comments to convert); typed errors; a typed exception
   per raise.
6. **F6 Astral toolchain:** RP-9's rulings, with the scaffold obeying its own witness, `uv version` the
   version's one home, adopters given the curated test exceptions, SHA-pinned actions and publishing;
   every shrink-only baseline owned to zero with a target date (6 of 35 are at zero today).
7. **F7 Project structure:** RP-15's maximal structure (mostly uv's, three gzkit additions);
   `gz init` follows uv's default application shape; binary-or-wheel offered to adopters, to define.
8. **F8 Code craft:** Ruff-held items at write time; context managers and EAFP partly Ruff, partly
   review; simplicity first at review. Not admitted: clarity over cleverness (carried by the
   complexity gates) and surgical changes (an agent rule, kept in `AGENTS.md`).
9. **F9 Complexity:** the tools are the authority (Ruff `C901`, Lizard, gzkit's cognitive scorer,
   cohesion); the rule's 50 and 600 numbers give way to the threshold table; cognitive ceiling on by
   default for adopters.
10. **F10 Cross-platform and I/O:** all eleven; encoding and path rules moved onto Ruff (`PLW1514`,
    `PTH`).
11. **F11 CLI shape:** all twelve, for projects with a CLI; `--json` closed on every leaf; the
    subcommand obligations binding gzkit and suggested to adopters.
12. **F12 Testing:** all eleven; no pytest ever, the hook delivered to adopters; the coverage floor
    into data and its chore renamed; no network and the 200 ms limit enforced by the runner.
13. **F13 Docs and config as code:** all six, the config formats made explicit.
14. **Borderline:** constraints before tests and layered state worked in; twelve governance items not
    admitted, their placement owned by RP-7's change order.

**Contradicted:** the inventory's 13 contradictions, among them the hexagonal canon page calling
itself *"influence, not wholesale adoption"*, are reconciled under row 4(i).

**Caveats:** the airlock's `parent_invariants` channel is empty in production and its reach is the
ontology, not imports (row 7(b)); whether `gz init` delivers the post-edit hook, the reviewer and the
`forbid-pytest` hook is untraced (row 7(d)).

## What each row would produce

1. **ADR (proposed; you initiate):** the whole-system map as a classic ADR once the classic ADR form
   lands on RP-6; the new machinery admitted at civil rule as catalog outcomes.
2. **Direct fixes:** H1 and F22 under RP-7; the scaffold's corrections (Ruff `ALL`, `app` default,
   cognitive ceiling on, `forbid-pytest` delivered), owner to rule, no tracking item yet.
3. **Chores (advised):** the hexagonal tidying chore; the `cli-standards-v3` hygiene chore.
4. **Drafts, on your go per item:** (a) the register and its page; (b) the hexagonal rule cut to its
   judgment part; (c) the canon page's contradiction; (d) the design-time imperative; (e) every
   baseline owned to zero; (f) the reviewer's rubric; (g) the pythonic rule's numbers; (h) coverage
   and runner limits; (i) the 13 contradictions; (j) the exception register's reasons.
5. **Refactoring program (you select its route):** imports to the map; the cognitive ceiling into
   `[tool.py-gzkit]`; jsonschema retired; rich behind the output port; `noqa` to `ruff: ignore`;
   `--json` on every leaf; the justify walkthrough to plain Python.
6. **No action:** no PyPI registration of `gzkit`; twelve governance items not admitted.
7. **Further research (you open each):** (b) the airlock's intent trace; (c) the hexagonal
   specification run; (d) what `gz init` delivers.

## How the rulings went

You ruled every family yourself, item by item where you chose to. You corrected the run five times
(candidates not members; the config home; the whole system, not the core; an option set built as
subsets; the deferral of the other candidates), went against a recommendation several times (five-year
aging, `[tool.py-gzkit]`, plain Python for the walkthrough) and turned several recommendations
stronger (MAXX for adopters, jsonschema retired, every baseline owned to zero).
