# Google OKF + RAG: The Ultimate AI Agent Architecture (Cloud Codes video transcript)

> Source: "Google OKF + RAG: The Ultimate AI Agent Architecture" — Cloud Codes (YouTube), published 2026-06-27. Tags: #googleokf #rag #aiagents #vectordatabase #systemdesign. Channel socials: x.com/cloud_codes. (Direct watch URL not supplied; cite by title + channel + date.)
> Capture: auto-transcribed (ASR); lightly cleaned for proper nouns (Pinecone, Weaviate, Qdrant, Chroma, Milvus, Postgres/pgvector, Karpathy, cosine, CLAUDE.md). Wording otherwise preserved. Chapter timestamps below are the publisher's official chapter markers.
> Relevance: cited research source for [okf-cms-knowledge-structure-note-2026-06-23.md](../okf-cms-knowledge-structure-note-2026-06-23.md) and [okf-rag-hybrid-design-note-2026-06-27.md](../okf-rag-hybrid-design-note-2026-06-27.md). Orientation material only — not an authority or steering surface.

---

## Chapter 1 [0:00] — The Problem with RAG & Hallucinations

Ask even the smartest AI agent a question about your own business and watch closely. "What's our refund window?" It says "30 days" — instant, confident, and completely wrong. It never opened your policy. It just guessed from training data.

For the last few years, the fix has been one thing: RAG. Take every document you own, chop it into chunks, turn each chunk into a vector, and store it. Ask a question, pull the closest pieces, and hand them to the model. And RAG is genuinely powerful — until you look at what it did. It shredded your clean, structured policy into fragments, grabbed the three that look similar, and threw away the order that made them mean anything. The answer is now a guess dressed up as a citation.

But there's a second way. Now, in June 2026, Google Cloud shipped OKF — the Open Knowledge Format — curated knowledge written as plain markdown files.

## Chapter 2 [0:42] — The OKF Alternative

Ask it the same question and it answers exactly "14 days" with a link straight to the source policy. OKF has its own ceiling though. Someone has to write every word of it. It's precise and trustworthy and auditable, and on its own it will never cover a million messy, unpredictable documents.

So here's the question every team is asking right now: RAG, with its endless scale and fuzzy search, or OKF, with its precision and structure? Which one do you bet your agent on? Wrong question. The answer isn't one or the other — it's both. The architecture that actually wins puts OKF and RAG together and takes the best of each.

Watch it work. A high-stakes question routes to OKF: exact, cited, done. An open-ended one routes to RAG: search the entire archive. Two layers of knowledge, one agent on top. OKF carries the canonical 80% — the answers you simply can't get wrong. RAG handles the long tail, the messy 20% you could never sit down and curate by hand. Precision and scale, trust and reach, structure and search. That's the hybrid stack.

## Chapter 3 [2:03] — How RAG Actually Works

A document arrives, it gets split into chunks, usually a few hundred tokens each. An embedding model turns every chunk into a vector — a long list of numbers that captures its meaning. All of those vectors get stored in a vector database.

Then someone asks a question. The question becomes a vector too, and the database returns the chunks sitting nearest to it in that space. That's the real magic: it matches by meaning, not by keyword. Different words, same idea, and RAG still finds it.

This grew into a whole industry — Pinecone, Weaviate, Qdrant, Chroma, Milvus, Postgres with pgvector — systems storing billions of vectors and searching them in milliseconds. This is the thing OKF can't touch: raw, open-ended scale across everything you've got.

But chunking comes at a price. Cut a table, a step-by-step procedure, or a contract clause down the middle, and the halves stop making sense. The model gets three disconnected fragments and quietly fills the gaps between them — which is exactly how a confident hallucination is born. And retrieval is probabilistic by design. It hands back what's likely relevant, not guaranteed the one correct answer. That's wonderful for a fuzzy, exploratory question. It's genuinely dangerous when the exact refund window, the exact price, or the exact dosage is what matters.

And it's a black box. Change one policy and you rerun the entire ingestion pipeline. You can't diff it in a pull request. You can't easily audit what the agent actually knows. And outdated chunks sit in the index long after the truth has moved on.

## Chapter 4 [3:37] — How Google OKF Works

OKF takes the exact opposite bet. No pipeline, no embeddings, no vector store — just a folder of markdown files with a little YAML on top. The spec says it best: if you can `cat` a file, you can read OKF; if you can `git clone` a repo, you can ship it.

Each file is a single concept. The frontmatter carries a `type` — and that's the only required field — plus an optional title, description, tags, a timestamp, and a resource: a link pointing at the real asset. Underneath is structured markdown — headings, tables, lists — that a model reads cleanly. And concepts link to each other with ordinary markdown links. Follow them and your knowledge turns into a graph: a table points to its dataset, a playbook points to the table it repairs. You get real relationships, not a bag of disconnected chunks.

Because a human authored it, retrieval is deterministic. You decide exactly what the model sees. No cosine-distance lottery. The structure survives intact, and the whole thing lives in git, so you can diff it, review it in a pull request, assign an owner, and roll back a bad edit.

If this feels familiar, it should. It's the CLAUDE.md file. It's the LLM wiki Andrej Karpathy keeps pointing at — context you engineer deliberately, by hand. OKF's contribution is simply writing that pattern down as one shared, open, vendor-neutral spec everyone can target.

But here's the honest limit, and it matters: OKF does not scale itself. Every concept is somebody's curation work. It's perfect for the knowledge you can't afford to get wrong, and hopeless as a dumping ground for a decade of raw, unsorted documents.

## Chapter 5 [5:15] — The Hybrid Architecture (Router + OKF + RAG)

So you build both, and you put a router in front. A query comes in. Is it canonical and high-stakes? Send it to OKF for an exact, cited answer. Is it open-ended, exploratory, buried somewhere in the archive? Send it to RAG. Every query goes where it's strongest.

The cleanest way to picture it is an 80/20 split. OKF is the spine — the curated, structured, high-trust core of what your agent knows. RAG is the reach — the huge, messy, unbounded long tail you could never realistically hand-write.

Make it concrete. A support agent gets two questions. "What's our refund window?" That's canonical, so it hits OKF and answers "14 days" exactly, with the policy linked. "Has anyone hit this weird billing bug before?" That's open-ended, so it hits RAG and searches 40,000 old tickets. Same agent, two completely different knowledge paths.

And the two make each other better. OKF gives RAG ground truth: when a curated concept exists for a question, the agent trusts that over a fuzzy retrieved chunk — and that single rule makes a real, measurable dent in hallucinations. OKF also hands the agent a map: its index files list what knowledge exists before any search runs — progressive disclosure — so the agent drills into RAG only where the curated answer runs out, instead of blindly searching from zero every single time. And RAG gives OKF reach: point semantic search at the bundle itself and at everything sprawling beyond it. Curation covers the critical core; retrieval covers the endless rest. Neither one has to pretend it can do the other's job.

And the best part: the agent doesn't have to care which is which. Put the OKF bundle in the vector index behind one retrieval interface — even a single MCP server — and the model just asks for knowledge. All the routing and plumbing stays hidden underneath.

Now lay the scorecards side by side: precision from OKF, scale from RAG, trust and breadth, structure and fuzzy search, git-diff and auto-indexed. For the first time, you stop trading one good thing away just to get the other.

## Chapter 6 [7:18] — The True Cost of Vector Databases

And the economics line up too. An OKF bundle is just text and git: write it once, edit a line, done. RAG carries real running cost: embedding every document, re-embedding it when it changes, and hosting a vector database that never sleeps. Curate what's worth curating; pay to index the rest.

## Chapter 7 [7:36] — Decision Matrix: When to use OKF vs RAG

When do you reach for OKF on its own? Small curated knowledge bases, high-stakes answers that have to be exact, highly structured tables and procedures, and anything you want versioned in git and owned by a real, accountable human.

When is it RAG on its own? A huge unstructured pile of text, open-ended questions you can't predict in advance, contracts, support tickets, transcripts, PDFs — heterogeneous sources where "good enough" semantic matching is honestly good enough.

And when do you run both? Almost every serious agent headed for production. The high-stakes core lives in OKF, the long tail lives in RAG, and a thin router in the middle decides query by query who answers.

Now let's kill two myths. First, OKF does not make RAG obsolete. The moment your corpus is too big or too fuzzy to curate by hand, vector search wins, and it isn't close. RAG is not going anywhere. Second, no, you can't just dump everything into one giant context window and call it solved. Irrelevant knowledge actively degrades the answer and quietly burns tokens. Selective, routed retrieval still beats brute force, even at a million tokens of context.

## Chapter 8 [8:48] — The Future Ecosystem of AI Agents

In the real world, this is a team sport. Data owners curate the OKF bundles. Engineers index the archive into a vector store. Frameworks like LangChain and LlamaIndex wire the two together. And an agent — Claude, ChatGPT, or Gemini — quietly consumes both.

And it's moving fast. OKF is only weeks old and already thousands of GitHub stars deep, with agents now starting to write OKF bundles themselves. Curated structure and raw retrieval are converging — graph and vector, authored and searched, folding into one stack.

So that's the whole picture in one frame: a router up top, OKF as the curated spine, RAG for the long tail, one grounded agent sitting above both. It was never OKF versus RAG — it's OKF plus RAG.
