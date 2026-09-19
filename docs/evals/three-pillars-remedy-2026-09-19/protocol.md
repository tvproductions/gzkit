# Obligation-tracing comparison — frozen protocol

Dated 2026-09-19. GHI #1048. Persona: main-session.
Code baseline: `f4a0395a711157406504c85f6cc62664aafddb33`.

Question: does the procedure in candidate.md improve necessary relationship
discovery in bounded current-code assessments? Two independently curated tasks,
three repetitions per task and condition, twelve fresh subjects total. This
compares an added procedure with the same base assessment prompt. It does not
test runtime correctness, native instruction delivery or model internals.

Before dispatch: independent oracle challenge, freeze candidate/cases/prompts
and their hashes. Candidate author does not choose the tasks. Oracle reviewer
does not see candidate text. No post-result criterion edits. Separate later
adjudication retains disagreements. Subjects receive no parent history, other
answers, oracle, labels, network or Git access. Model settings inherited without
override; no provider build fingerprint available.

Source population: the identical 1,939-file bounded corpus in corpus.json,
archived from the named commit. It contains source, tests, data, current rules,
primary skill bodies, user documentation and selected root configuration and
instructions. Historical evaluations, handoffs and ADR directories are not
supplied. A curator confirms required witnesses are included. This bounds the
claim to the supplied corpus, not the whole repository. Access to other local
files is still technically possible; the instruction boundary and observed
traces are checked, not described as a sandbox guarantee.

Each subject: maximum 16 shell/read calls including task read and sole permitted
response-file write; maximum 850 answer words including read inventory. No tests,
source edits, dependency installation, governance execution or delegation.
Use only the supplied corpus and designated task/answer files. Both arms have
identical tasks and budgets; candidate receives only the added procedure.
Interleave tasks and conditions in dispatch order. Record actual traces, words,
bytes, elapsed time when available, and deviations. Cost proxies are not tokens
or monetary cost. Preserve every run; contamination disqualifies a clean benefit
claim rather than inviting selective replacement.

Each criterion gets D (discovery), R (correct relationship), A (consistent
proposed application), each 0/1. Complete requires all three. Semantic equivalents
count; optional regressions and particular vocabulary do not become requirements.
Independent scorer receives raw responses by neutral IDs, frozen oracle and
source witnesses, but no assignment key or candidate text. Wording may reveal
the treatment; report this limit rather than claiming perfect blinding. Each
zero needs missing-evidence reasoning, each credit a source answer excerpt.
Score unsafe policy decisions, unsupported expansion and false execution claims
separately; a list of files or a filled trace earns no automatic credit.

Decision rule: candidate complete-criterion totals must improve on baseline
for BOTH tasks, introduce no unsafe policy or false execution claim, and show
no repeated new criterion regression (candidate misses in at least two runs
where baseline has none). Report call/word distributions and deviations.
This is a pilot screening rule, not statistical significance or automatic canon
adoption. If it fails or contamination prevents interpretation, leave canon
unchanged and record the result. If it passes, review integration into the
existing workflow and remaining generalization risk before any doctrine edit.
An unresolved policy decision requires the operator; routine negative disposition
does not. No generic framework or unrelated repair follows from these runs.

Exit: retained raw evidence, independent scoring and report review, justified
disposition, required full staged repository check, commit and guarded sync.
GHI #1048 closes against that deliverable. Existing #1028/#1029 work is separate.
