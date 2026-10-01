# Patch Release: v0.34.8

**Date:** 2026-10-01
**Previous Version:** 0.34.7
**Tag:** v0.34.7

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 533 | agents-md-budget: 5k recovery target requires ADR-0.0.37 completion + registry-projection migration | diff_only | GHI #533 has commits touching src/gzkit/ but no 'runtime' label |
| 611 | governance: no general append-only corrective-action primitive to undo agent/human error (repudiate is a point-solution) | open_upstream | GHI #611 qualifies on commit markers but is still OPEN upstream; confirm this release closes it before counting it |
| 802 | docs: gzkit.org serves stale docs from a hand-deployed VPS | excluded |  |
| 803 | docs-build: mkdocs validation downgrades withdraw the dead-link enforcement run_mkdocs claims | qualified |  |
| 808 | decommission-tautological-tests: criteria gate the ratchet, not the debt | qualified |  |
| 815 | agents-md: must-survive section renders past the Codex cap, undelivered | qualified |  |
| 818 | governance: Architectural Boundaries rest on a memo, not an ADR | diff_only | GHI #818 has commits touching src/gzkit/ but no 'runtime' label |
| 820 | task-envelope Signature (c): a channel SUBSET is reported as layer-drift, so the gate is satisfiable only by falsifying attribution | qualified |  |
| 832 | release-tags: 22 of 34 grandfathered releases are repairable, not stuck | qualified |  |
| 837 | pool ADRs: 5 promotion criteria route through the sealed foundation kind | excluded |  |
| 838 | handoff: Settled Rulings is 85% of the document and re-adjudication still happens | qualified |  |
| 849 | arb red: witness is inert on landed work, so --from=verify gates nothing | qualified |  |
| 851 | session-green-gate: delivery witness covers 1 of 4 declared hook types | qualified |  |
| 856 | arb: canonical unittest invocation is serial while every gate runs it parallel (3.05x) | qualified |  |
| 870 | handoff: continues_from is traversed on resume, but ResumeResult.chain is read by nobody | qualified |  |
| 871 | adr-routing: corrective re-home collides with ascending-semver order | qualified |  |
| 873 | corpus fold: superseding an amendment republishes the original wording | qualified |  |
| 874 | corpus: entry ids are unenforced, so a content row can silently leave canon | qualified |  |
| 877 | ledger: typed union rejects ~300 committed rows the JSON schema accepts | qualified |  |
| 888 | req_kind_support: SUPPORT proof events are substring-scanned, so a denial reads as a citation | qualified |  |
| 889 | obpi precomplete: arb_receipts counts receipts, never reads exit_status | qualified |  |
| 894 | ledger validator: attestor guard is weaker than the gate it witnesses | qualified |  |
| 920 | enforcement: NC runner rmtree's any fixture path it is handed | qualified |  |
| 921 | instruction surfaces: .gzkit/rules/** is uncorpused, and fans out to all 26 generated AGENTS.md | open_upstream | GHI #921 qualifies on commit markers but is still OPEN upstream; confirm this release closes it before counting it |
| 922 | agents-md-map-conformance: 26 nested AGENTS.md are checked by nothing | unclassified_reference | GHI #922 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 923 | agent sync: nested subtree rules reach Codex only, not Claude | qualified |  |
| 924 | vendors: gz init regenerates the whole Copilot surface the drop removed | qualified |  |
| 925 | skill mirror: generated CLAUDE.md is copied into Codex's own surface root | qualified |  |
| 927 | red-witness: direct-fix guards are outside every falsifiability gate | qualified |  |
| 928 | adr-checklist: the tick mark is parsed away and read by nothing | qualified |  |
| 929 | config: 44 registries, 93 readers, no owner, loader, or coherence gate | qualified |  |
| 931 | pointer-integrity: relative lift pointers are resolved against the repo root, so correct links fail | qualified |  |
| 932 | pointer-integrity: back-pointer check is a bare substring test, so any lifted-from satisfies every pointer | qualified |  |
| 933 | pointer-integrity: Invariant 3's witness checks 4 of 17 lift pointers | qualified |  |
| 934 | doctrine: Fable/Mythos 5.1 card supersedes registry; 9 surfaces sole-source the old card | unclassified_reference | GHI #934 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 935 | frontier-model-card-currency: criteria check registry shape, never currency | qualified |  |
| 936 | chore currency gates are only readable by running the chore they gate | qualified |  |
| 937 | comparison-doc: adopter table advertises branch-per-ADR isolation | excluded |  |
| 938 | check-config-paths: every .github/ path literal is unmappable | qualified |  |
| 939 | advisory-scorecard: skill-declared doctrine is structurally unscorable | unclassified_reference | GHI #939 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 940 | verifier-pipe-gate: a trailing statement masks a verifier's exit status | qualified |  |
| 941 | obpi-pipeline review gate: reviewers cannot execute, so unrunnable asks degrade the verdict | qualified |  |
| 942 | obpi-pipeline Stage 4a: pasted command output is unverified, and Step 4b does not check it | qualified |  |
| 943 | Claude tuning: universal pressure miscalibrates Opus 5 and Fable 5.1 | unclassified_reference | GHI #943 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 944 | gz validate: Rich markup swallows every error type in validation output | qualified |  |
| 945 | content: advisory-lock primitive is a private cross-module import | qualified |  |
| 946 | gz task envelope diagnose: the frontmatter tasks: channel always reads empty | qualified |  |
| 947 | task-envelope: tool-locus artifact_edited rows also have no attribution channel (sibling of #869) | qualified |  |
| 948 | tautological-test-audit: scanner flags behavior tests it cannot see through helpers, value-loads, or artifacts | qualified |  |
| 949 | gz check: --reuse-verified passes a tree the full gate fails, and it is the pre-push gate | label_only | GHI #949 has 'runtime' label but no commits touching src/gzkit/ |
| 950 | task-envelope: no roster member meets the roster's task_id criterion | qualified |  |
| 951 | session-exit: bookmark writes the absolute transcript path into a repo-bound artifact | qualified |  |
| 953 | ledger: append has no transaction boundary across writers or crashes | qualified |  |
| 955 | test_ownership: a top-level fcntl import costs 68 tests their Windows run | excluded |  |
| 956 | imports: 104 cross-package private-symbol reaches, and ruff sees 1 | unclassified_reference | GHI #956 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 957 | gz check is red on main: behave fixture seeds a floor_event_id the guard now refuses | label_only | GHI #957 has 'runtime' label but no commits touching src/gzkit/ |
| 958 | ownership tests: fixture writes CRLF on Windows, so 23 byte-span assertions fail | qualified |  |
| 959 | obpi-complete: refuted-with-caveats clears the gate with no resolution | qualified |  |
| 960 | obpi-complete: a refutation is accepted as a terminal completion state | qualified |  |
| 961 | codex adversary: adversarial-review is hardcoded read-only, so Step 4b can never execute | qualified |  |
| 962 | codex config: .codex/config.toml is never read, so GHI #815's doc cap is undelivered | qualified |  |
| 963 | mutation sweeps: byte-identical mutations collide in the pyc cache, so a sweep can report a false PASS | qualified |  |
| 964 | obpi precomplete: a discharged refutation in Step 4b history fails the preflight forever | qualified |  |
| 965 | obpi present-evidence: multi-line Demo command is split into per-line commands | qualified |  |
| 966 | adr status: a closed GHI still renders as a live tracked defect | qualified |  |
| 967 | preflight: a FAIL audit receipt orphans itself, and cleanup unlinks it | qualified |  |
| 968 | reviewer personas: "read-only" is enforced as "no Bash", and no surface expresses the difference | qualified |  |
| 970 | stage4-packet: a || suffix lets the failure branch's output be omitted | qualified |  |
| 971 | verifier-pipe-gate: an && chain is masked by whatever catches it | qualified |  |
| 972 | gh-cli: whole-queue counts use gh issue list's default 30-row cap | diff_only | GHI #972 has commits touching src/gzkit/ but no 'runtime' label |
| 974 | content ownership: no governed transition from unowned to corpus-owned | qualified |  |
| 975 | test_corpus_model: fingerprint pin asserts 'no capture since re-pin', not REQ-0.35.0-01-01 | qualified |  |
| 976 | ownership prose: growth refusal and unown help each prescribe a path that refuses | qualified |  |
| 977 | tests: git fixtures inherit the hook's GIT_DIR and rewrite the hosting repo's config from a linked worktree | diff_only | GHI #977 has commits touching src/gzkit/ but no 'runtime' label |
| 978 | ownership prose: 13 sibling witness-chain refusals prescribe a refused step | open_upstream | GHI #978 qualifies on commit markers but is still OPEN upstream; confirm this release closes it before counting it |
| 979 | ownership loader: a witness need not be the chain tip, so an attested raise silently reverts | qualified |  |
| 980 | GHI workflow: repair and review lack a bounded closure contract | diff_only | GHI #980 has commits touching src/gzkit/ but no 'runtime' label |
| 981 | stage4 replay: /bin/sh is dash on Linux, so the pipefail escape the gate sanctions is rejected | qualified |  |
| 982 | CI: windows-latest has been red for 4+ pushes, so the leg witnesses nothing | qualified |  |
| 984 | obpi pipeline: repair and evidence obligations drift across review instructions | qualified |  |
| 985 | acceptance: preserve proof obligations and verified finding closure | qualified |  |
| 986 | acceptance prove: a covering test with a docstring reads as a red baseline | qualified |  |
| 987 | gz arb step: docs mandate --max-output-chars, the CLI rejects it | qualified |  |
| 989 | acceptance: input_digest hashes os.environ, so an independent review can never import | qualified |  |
| 990 | acceptance/mutation fixtures: CRLF writes make mutation targets unfindable on Windows | qualified |  |
| 991 | arb step fixture: child stdout uses the locale encoding, so a CJK payload dies on Windows | qualified |  |
| 992 | obpi pipeline: launch never invokes the reconciler it declares | qualified |  |
| 994 | acceptance review: a non-executing reviewer can record a confirmation it could not have made | qualified |  |
| 995 | gz validate --json exits 0 on failure, so every scope reports success to callers | qualified |  |
| 996 | justify binding: an empty filename discharges required reasoning | qualified |  |
| 999 | chores: no chore declares class or rung, so posture is unchecked | qualified |  |
| 1000 | handoff rulings: a handoff's own rulings stay unsearchable until a successor | qualified |  |
| 1001 | cli exit codes: usage error exits 2, which help and cli.md call System/IO | qualified |  |
| 1002 | chores: CHORE.md duplicates criteria and version, and 17 have drifted | qualified |  |
| 1003 | handoff rulings: a successor restating an inherited ruling books a second copy | unclassified_reference | GHI #1003 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 1004 | handoff decide: output, help and manpages still report a retired gate | qualified |  |
| 1005 | chores sync: surface-level files resolve as slugs, so the registry never ships | qualified |  |
| 1006 | cli-alignment: chore docs are unscanned, and 8 gz chains in 4 chores do not resolve | qualified |  |
| 1007 | enforcement floor: a claim declares no population, so a subset witness passes its own control | qualified |  |
| 1008 | verifier-pipe-gate: a verifier inside a ( ) or { } group is not recognized | qualified |  |
| 1010 | cli logging: structlog writes to stdout, corrupting --json output | qualified |  |
| 1011 | chores: 4 CHORE.md files describe mechanisms or paths that don't exist | diff_only | GHI #1011 has commits touching src/gzkit/ but no 'runtime' label |
| 1014 | closeout: from_state is hardcoded and bypasses transition validation | qualified |  |
| 1016 | vendors: gemini is still declared in config and schema after its surfaces were removed | qualified |  |
| 1017 | commit-trailers: the mandatory Task: trailer has no automated witness | qualified |  |
| 1019 | doctrine: GPT-6 Astra card (2026-09-03) supersedes the GPT-5.6 registry entry | diff_only | GHI #1019 has commits touching src/gzkit/ but no 'runtime' label |
| 1021 | agent sync: Claude receives every subtree rule twice — .claude/rules and the nested CLAUDE.md import | qualified |  |
| 1022 | templates/agents.md: adopter Gate Covenant rows name gz lint and a manual check for Gates 3 and 4 | diff_only | GHI #1022 has commits touching src/gzkit/ but no 'runtime' label |
| 1024 | src: 12 modules cite governance-core.md as a rule home; one is a user-facing error message | qualified |  |
| 1025 | skills: Confidence Gate and gz-justify route on the retired 90% framing | diff_only | GHI #1025 has commits touching src/gzkit/ but no 'runtime' label |
| 1026 | arb validate: 38 of gzkit's own receipts fail — writers outran the schemas | qualified |  |
| 1027 | arb: coverage is the last serial full-suite run — 493 s vs 307 s parallel, same totals | qualified |  |
| 1028 | gz-obpi-pipeline Stage 4: 4a and 4b invalidate each other with no bound and no exit | open_upstream | GHI #1028 qualifies on commit markers but is still OPEN upstream; confirm this release closes it before counting it |
| 1029 | acceptance: proof currency is a whole-tree digest, so any edit stales every proof and review | unclassified_reference | GHI #1029 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 1031 | attestor placeholders: docs and CLI remedies prompt for a real name | qualified |  |
| 1033 | ghi-triage chat-silence hook: a backslash-newline command never matches | qualified |  |
| 1035 | runtime messages: 25 sites cite AGENTS.md rule numbers that no longer exist | qualified |  |
| 1036 | config: no configured attestor handle, so every remedy shows a fill-in token | qualified |  |
| 1040 | model-selection: skill example prescribes an invisible version field | qualified |  |
| 1044 | chore rules: canonical authoring and damaged-slug recovery name opposing sources | qualified |  |
| 1045 | three pillars: measure uncued obligation discovery | unclassified_reference | GHI #1045 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 1047 | smoke docs: empty-tier failure omits adopter opt-in | qualified |  |
| 1048 | three pillars: test explicit obligation tracing | unclassified_reference | GHI #1048 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 1049 | brief paths: relative prefix bypasses generated-mirror refusal | qualified |  |
| 1052 | three pillars: measure bounded source-impact views | unclassified_reference | GHI #1052 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 1053 | three pillars: route advisory impact design and implementation | unclassified_reference | GHI #1053 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 1054 | ontology: default source discovery ignores configured root | qualified |  |
| 1057 | plan audit: out-of-scope paths always pass containment | qualified |  |
| 1063 | registries: 51 validator scopes and 10 event types are never invoked | qualified |  |
| 1064 | transcribed-counts: the registry scans a superseded campaign, so the live plan is unscanned | label_only | GHI #1064 has 'runtime' label but no commits touching src/gzkit/ |
| 1066 | config-registry: ownership is exhaustive, derivation and module constants are not | qualified |  |
| 1067 | config: no single read seam — 30 modules reach into data/ directly | qualified |  |
| 1068 | test_report_publication: write_text fixture writes CRLF on Windows | qualified |  |
| 1069 | line-endings audit: scope excludes the write_text hazard it names | qualified |  |
| 1070 | settings sync: enabledPlugins is replaced wholesale, so no project can enable a plugin | qualified |  |
| 1071 | settings.local backup vault resolves INSIDE the repo on Windows | qualified |  |
| 1072 | settings vault is written but never read, so the backup guarantee has no witness | qualified |  |
| 1074 | ledger: ts stamped outside append's lock, so writers land out of order | qualified |  |
| 1075 | ledger merge-driver: additive ts-ordered insertion read as a rewrite | qualified |  |
| 1076 | handoff resume: ADR and OBPI citations never resolve, only GHI does | qualified |  |
| 1077 | gz check: step cost record has no consumer and no refresh mechanism | qualified |  |
| 1078 | handoff resume: ADR citations stay UNKNOWN on a deferral the operator has now ruled | qualified |  |
| 1079 | citation resolver: reads exact graph ids, but handoffs cite prefixes | qualified |  |
| 1080 | ledger: canonicalize_id re-reads the whole ledger per call, costing 55s in gz check | qualified |  |
| 1081 | git-sync: commit anchors are shape-checked but never resolved | qualified |  |
| 1082 | handoff resume: inline next steps after a preamble extract as zero | qualified |  |
| 1083 | cli-alignment: the code-citation arm excludes docs/governance prose | qualified |  |
| 1084 | git-sync: an anchor the commit only discusses is emitted as touched | qualified |  |
| 1085 | behave: a @wip block's tracking reference is prose, so a met deferral never expires | label_only | GHI #1085 has 'runtime' label but no commits touching src/gzkit/ |
| 1086 | budget: a 2026-06 test blocks on limits the 2026-08 stay made advisory | excluded |  |
| 1087 | rulings: a booked stay names no enforcement sites, so its sweep cannot be verified | unclassified_reference | GHI #1087 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 1088 | gz check: the default sweep runs Behave on every per-change run | qualified |  |
| 1089 | doctrine: Opus 5.5 card supersedes the Opus 5 registry entry | unclassified_reference | GHI #1089 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 1090 | AGENTS.md: REQ-coverage line drops the lane scope ADR-0.0.25 attests | qualified |  |
| 1091 | control surfaces: 2026-09-17 compression dropped 23 binding conditions | diff_only | GHI #1091 has commits touching src/gzkit/ but no 'runtime' label |
| 1092 | commit-locus recorder: pre-commit stash rollback discards its row | qualified |  |
| 1093 | present-evidence: brief Demo runs in the live checkout and can attest | qualified |  |
| 1094 | red-parity: ignores acceptance proofs, unsatisfiable on landed code | qualified |  |
| 1095 | review composers: two JSON envelopes per reply, so imports keep failing | qualified |  |
| 1096 | review context: carries all proof history, so prompts grow unbounded | qualified |  |
| 1097 | opus-tuning: fallback and thinking-control doctrine misstate Opus 5.5 card | qualified |  |
| 1098 | gz init repair: rewrites canonical skills its dry run never lists | qualified |  |
| 1099 | skills audit: wall-clock review age fails tests and aged wheel installs | qualified |  |
| 1100 | sync entry points: tidy --fix and init repair skip the canonical preflight | qualified |  |
| 1101 | attestor examples: --help and manpages model a person's name | qualified |  |
| 1102 | complexity advise: neither intrinsic-attestation path suppresses a diagnosis | qualified |  |
| 1103 | complexity advisor: unmatched crossings are all labelled long_parameter_list | qualified |  |
| 1104 | complexity guide: hint line range is usually the def line alone | qualified |  |
| 1105 | complexity auto-chain: timeout ignores its config key; hook runs uvx xenon | qualified |  |
| 1106 | skills: no flow guide answers how do I / what can I; router is stale | qualified |  |
| 1107 | skills: no skill encodes how to review a skill | diff_only | GHI #1107 has commits touching src/gzkit/ but no 'runtime' label |
| 1108 | skill sync: wheel gets SKILL.md only, so references/ never ship | qualified |  |
| 1109 | content commit: retention sidecar written with no trailing newline | qualified |  |
| 1111 | skill docs pages: 3 Purpose lines quote an overview the skill dropped | excluded |  |
| 1112 | skills: 8 skill bodies are still the scaffold template | unclassified_reference | GHI #1112 is cited in range by a commit whose type is not a closure type; no closure commit claims it. Adjudicate per SKILL.md § Step 1c before publishing |
| 1114 | chores: 8 shipped chores' criteria run scripts adopters never get | qualified |  |
| 1115 | obpi brief-drift: --apply writes into a sealed brief | qualified |  |
| 1116 | obpi brief-drift: --dry-run hides the amendments it would write | qualified |  |
| 1117 | validate manpage: Scopes Reference omits 28 of 99 scopes, unchecked | excluded |  |
| 1118 | migrate-semver: 21 bare-id renames pending; nothing runs the detector | qualified |  |
| 1122 | gz init --update: EDITED detection needs a marker nothing writes | qualified |  |
| 1123 | gz init --update: refresh skips classifiers, overwrites chore registry | qualified |  |
| 1124 | gz tidy: --check is a no-op and findings never set the exit code | qualified |  |
| 1134 | constitution type: registry, transitions, model and schema disagree | qualified |  |
| 1139 | pool ADRs: worktree, ledger and ghi-triage premises falsified by later canon | excluded |  |
| 1141 | ghi-triage: route shows authority, not readiness, so nothing sorts what to pull | label_only | GHI #1141 has 'runtime' label but no commits touching src/gzkit/ |
| 1142 | commit-trailers: refusal prescribes -#<ghi> that canon makes optional | qualified |  |
| 1143 | gz check: a hung unit tier blocks the pre-push gate with no timeout | qualified |  |
| 1150 | evaluation-justify-binding: scan-all grades terminal ADRs and raw ids | qualified |  |
| 1151 | ledger: freed feature slots fold onto demoted pool ADRs | qualified |  |
| 1152 | arb red --commit: verdict leaves no receipt, so GHI closes cite nothing | qualified |  |
| 1153 | arb red --commit: restructuring fixes read inconclusive, not graded | qualified |  |

## Operator Approval

Approved by gz patch release
