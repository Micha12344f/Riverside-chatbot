# Riverside Books Chatbot

A small command-line chatbot for the Riverside Books FAQ task. The main submission uses local semantic retrieval over the provided FAQ data, with a lexical fallback so the bot still runs safely if the embedding model is unavailable.

## Why I used Python

The brief mentions a preference for Node and TypeScript, but Python is the stronger tool for this specific job: local semantic search with sentence-transformers.

The `sentence-transformers` ecosystem is Python-first. It lets you download a 80 MB model, run embeddings entirely on CPU, and compute cosine similarity with NumPy — no API keys, no Docker GPUs, no ONNX wrappers. The equivalent path in Node would mean heavier dependencies (TensorFlow.js or ONNX Runtime) and more boilerplate for the same result.

This repository already had a partial Python scaffold, so rather than burn the time box on a stack migration, I finished the path that was already aligned with the problem domain. The result is a small, self-contained CLI that runs offline, tests cleanly with pytest, and ships in under 200 lines of core code.

## Approach

The main matcher uses `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` and embeds each FAQ as a combined document:

```text
Question: ...
Answer: ...
```

That lets the retrieval step use the answer text as extra context instead of relying on the question field alone.

I also add a lightweight question-fit reranking bonus after semantic retrieval. This helps short paraphrases like "where's the shop?" favour the FAQ whose canonical question best matches the user's intent, while still benefiting from answer-text context.

At runtime the chatbot:

1. Loads the FAQ data.
2. Precomputes FAQ embeddings once at startup.
3. Embeds each user query.
4. Ranks FAQs by cosine similarity, then applies a small question-fit reranking bonus.
5. Only answers when the top result clears both:
   - a minimum score threshold
   - a minimum margin over the second-best result

If the embedding stack cannot load, the app falls back once to a simpler lexical matcher instead of crashing.

## Why This Is the Right Default for 20 FAQs

For a fixed FAQ list this is a strong fit because it is:

- cheap: no API key or per-request model cost
- fast after startup: FAQ embeddings are cached in memory
- deterministic: the same question produces the same ranking behavior
- low hallucination risk: the bot returns stored answers or declines to answer

I deliberately did not make an LLM the default here. With only 20 canonical FAQs, generation would add cost, latency, and more ways to answer confidently from weak evidence.

## No-Match Protection

The bot should not bluff. It rejects weak matches if either:

- the top semantic score is too low
- the top result is too close to the runner-up

When that happens it returns:

`Sorry, I don't know that one — please ask a member of staff.`

## How To Run

From the project directory:

```bash
python -m pip install -r requirements.txt
python main.py
```

Useful flags:

```bash
python main.py --debug
python main.py --faq-path ./faqs.json
```

Notes:

- The first semantic run may download the sentence-transformers model.
- If that download fails, the chatbot will keep working in lexical fallback mode.

## Example

```text
You: when can I come in?
Bot: We're open 9am to 6pm Monday to Saturday, and 11am to 4pm on Sundays.

You: what is your phone number?
Bot: Sorry, I don't know that one — please ask a member of staff.
```

## Tests

Run:

```bash
pytest
```

The tests cover:

- semantic matcher caching FAQ embeddings instead of recomputing every turn
- weak-match rejection
- lexical fallback if embeddings fail
- CLI interaction flow
- a compact set of expected-match and reject cases

## Tradeoffs

Pros:

- grounded answers from the provided FAQ set
- simple runtime model
- no external API dependency in the core path

Cons:

- threshold tuning is heuristic
- local retrieval will eventually struggle as the dataset grows and overlaps more
- this version returns one stored answer rather than synthesising across sources

With more time, I would tune thresholds against a slightly larger paraphrase set and capture a few failure examples to guide future improvements.

## How I'd Scale This

Once the dataset grows beyond a small FAQ file, I would keep retrieval first and add an LLM only after retrieval.

### Trigger To Scale Beyond Local-Only Retrieval

- the FAQ set grows materially beyond 20 entries
- multiple answers become semantically similar
- answers need synthesis across several documents
- content starts changing frequently and needs better analytics or evaluation

### Recommended Retrieval-First LLM Architecture

1. Embed the full FAQ or knowledge base.
2. Retrieve the top `k` candidates for the user query.
3. If one result is clearly dominant, return its stored answer directly.
4. If the query is ambiguous, send only the top candidates to an LLM.
5. If the evidence is weak, fall back instead of generating.

### What The LLM Version Should Return

The future `LlmMatcher` should keep the same matcher contract and return structured output such as:

- `faq_id`
- `confidence`
- `no_match`
- optional internal rationale for logs only

There are a few realistic scale-up options:

- retrieval + LLM reranker: best when canonical FAQ answers should remain the final output
- retrieval-augmented generation: best when answers need light synthesis across multiple sources
- hybrid routing: let the local matcher answer easy queries and call the LLM only for ambiguous ones

I would not use LangGraph for this task. I also would not add LangChain to the main implementation. If the LLM path becomes real later, the next production concern would be observability and evals, where a tool like Langfuse could help.
