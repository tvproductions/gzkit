# OKF + RAG Hybrid Design Note - 2026-06-27

Status: design note. Captures the operator-preferred OKF+RAG hybrid analysis
discussed 2026-06-27. It is a companion to
[`okf-cms-knowledge-structure-note-2026-06-23.md`](okf-cms-knowledge-structure-note-2026-06-23.md)
and **does not amend it**: that note's ratified first-pass scope (OKF as
documentation-knowledge orientation; RAG out of scope) stands unchanged. This
note records the hybrid reasoning and the gates any future RAG work must clear.
It is not a steering surface and does not supersede the campaign; it is not an
ADR.

## Operator signal

The operator favors the OKF + RAG hybrid architecture (curated OKF spine + RAG
reach + a thin router) described in
[`research_sources/okf-rag-hybrid-knowledge-stack-cloud-code-transcript.md`](research_sources/okf-rag-hybrid-knowledge-stack-cloud-code-transcript.md).
This note translates that preference into gzkit terms rather than adopting the
video's framing wholesale.

## How the hybrid maps onto gzkit

The 80/20 split nearly describes what gzkit already is.

OKF spine = the curated core.
: Control surfaces (`AGENTS.md`, `CLAUDE.md`, rules, skills) plus the
  doctrine/rationale docs are already the answers that cannot be wrong: git
  versioned, diffable in a PR, owned by an accountable human. The OKF/CMS work
  only makes the pointed-to docs self-describing (type, description, links) so
  agents traverse instead of grepping blind. This needs no RAG.

The long tail already exists.
: `docs/governance/research_sources/`, the handoff archive,
  `.gzkit/insights/agent-insights.jsonl`, closed-GHI history, and the ledger are
  the messy 20% nobody will hand-curate. Today agents navigate it with `rg` and
  filename guesses — the exact gap the hybrid names.

Two of the video's "magic" pieces, gzkit already has in stronger form.
: "OKF gives RAG ground truth — trust it over a fuzzy chunk" is a weaker version
  of gzkit's Layer-1/Layer-2 doctrine: canon and ledger always beat inference.
  "Progressive disclosure via index files" is the compact-pointer model
  `AGENTS.md` is built on. So the novel surface for gzkit is only the *reach*
  tier and the *router* — not the spine.

## The doctrinal collision

A vector store (pgvector, Pinecone, Chroma, …) plus an embedding model is a
heavyweight **runtime dependency**. Under STDLIB-FIRST DOCTRINE the default is
stdlib, and any runtime dependency requires an ADR or OBPI naming what stdlib
cannot do and why the third-party surface is worth its cost. "Everyone uses
RAG" and "RAG is the modern choice" are named *anti*-rationales. The RAG layer
must clear the same bar Pydantic cleared; it cannot be adopted because the
framing is persuasive.

## The sizing question (answer this before any RAG work)

The video's own dividing line: "the moment your corpus is too big or too fuzzy
to curate by hand, vector search wins." gzkit's doc corpus is on the order of
hundreds of markdown files in one repo, all `rg`-reachable in milliseconds —
not the 40,000-ticket regime RAG exists for.

There is a stdlib-first reach tier hiding here: **OKF index files + ripgrep is
itself a deterministic retrieval layer** over the long tail. No embeddings, no
vector DB, no re-indexing pipeline, fully diffable. For this corpus size it
plausibly delivers most of RAG's reach at zero doctrinal cost. The
cosine-distance vector layer only earns its keep once the corpus outgrows what
structured grep can serve.

## Recommended sequencing

1. **Ship the OKF spine.** Already campaigned (Movement II "CMS OKF
   documentation knowledge structure"); highest value, lowest risk; stands on
   its own.
2. **Treat "reach" as stdlib-first first.** Make OKF index files + ripgrep the
   initial retrieval tier over the long tail; measure how far it gets before
   reaching for embeddings.
3. **Gate the vector/RAG layer behind two things:** a concrete corpus-size
   trigger (the demonstrated point where curation + grep stops working) *and* a
   foundation ADR naming what stdlib/ripgrep cannot do.

## The router is a trust boundary, not plumbing

The video's "put OKF in the vector index behind one interface so the agent
doesn't care which is which" is a trap in gzkit. Architectural Boundary 6 — do
not let derived views silently become source-of-truth — means the agent **must**
care which is which: canon/ledger answers are provable, retrieved answers are
not. RAG belongs in the orientation/reach tier and **never** the authority tier,
because RAG is probabilistic by design and gzkit's truth is deterministic by
design. Any router gzkit builds is enforcing that boundary, not hiding it.

## Relationship to the ratified note

This note keeps RAG out of the ratified first pass. It records that *if* gzkit
later adds reach over the long tail, the stdlib-first (ripgrep) tier is tried
first, and a vector/RAG tier is a foundation-ADR-gated departure — not a default.
The OKF spine work proceeds unchanged regardless of whether RAG is ever added.

## References

- [OKF CMS knowledge structure note (ratified)](okf-cms-knowledge-structure-note-2026-06-23.md)
- [Google OKF + RAG: The Ultimate AI Agent Architecture — Cloud Codes video transcript](research_sources/okf-rag-hybrid-knowledge-stack-cloud-code-transcript.md)
- [Build-to-1.0 campaign](build-to-1.0-campaign-2026-06-20.md)
- [State doctrine (Layer-3 derived views are never source-of-truth)](state-doctrine.md)
