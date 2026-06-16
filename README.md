# Riverside Books Chatbot

An AI-powered FAQ chatbot for a fictional independent bookshop, with a backend structured for AWS deployment and a frontend structured for Vercel.

## CLI

<p align="center">
  <img src="assets/demo-cli.gif" alt="CLI demo" />
</p>

## Frontend website

![Frontend demo](assets/demo-frontend.gif)

## Get started

> **Note**
> Start with the backend CLI for the quickest local run. The frontend is the presentation layer, and the backend is the runtime path that powers the chatbot logic.

1. Clone, install, and run the backend:

   **Windows:**

   ```powershell
   git clone https://github.com/Micha12344f/Riverside-chatbot.git
   cd Riverside-chatbot/backend
   pip install -r app/requirements.txt
   python main.py
   ```

   **macOS:**

   ```bash
   git clone https://github.com/Micha12344f/Riverside-chatbot.git
   cd Riverside-chatbot/backend
   pip3 install -r app/requirements.txt
   python3 main.py
   ```

   **Linux:**

   ```bash
   git clone https://github.com/Micha12344f/Riverside-chatbot.git
   cd Riverside-chatbot/backend
   pip3 install -r app/requirements.txt
   python3 main.py
   ```

   > **Note** — If `pip`/`pip3` isn't available, install Python first:
   > - Windows: [python.org installer](https://www.python.org/downloads/) or `winget install Python.Python.3.11`
   > - macOS: `brew install python` (also makes `pip3` and `python3` available)
   > - Linux: `sudo apt install python3-pip` (or your distro's package manager)

2. TUI experience:

   For the standalone Riverside terminal UI:

   **Windows:**

   ```powershell
   cd Riverside-chatbot/Riverside-books-CLI
   pip install -r requirements.txt
   python main.py
   ```

3. Frontend experience:

   For more information, check [frontend/README.md](<C:/Users/sossi/OneDrive/Desktop/agent builder workspace/Riverside Chatbot solution/frontend/README.md>) for the frontend walkthrough and deployment notes.

4. Backend structure and deployment notes:

   For more information, check [backend/README.md](<C:/Users/sossi/OneDrive/Desktop/agent builder workspace/Riverside Chatbot solution/backend/README.md>) for the backend entrypoints, AWS-facing structure, and runtime layout.

## Why This Approach Was Chosen

![Why this approach](assets/demo-why-this-approach.gif)

This project uses semantic retrieval as the main matching strategy because the FAQ set is fixed, small, and best answered from grounded source content rather than free-form generation.

That gives a strong balance of quality and control:

- better paraphrase handling than keyword-only matching
- far lower hallucination risk than an LLM-first chatbot
- lower operational cost than calling a model for every question
- easier testing and clearer failure behavior

For more information on the decision-making behind the project, check [backend/Project-explained/README.md](<C:/Users/sossi/OneDrive/Desktop/agent builder workspace/Riverside Chatbot solution/backend/Project-explained/README.md>).

## How Our Matching Works

![Matching flow](assets/demo-matching-flow.gif)

The matching flow is intentionally simple:

1. Load the FAQ data from the backend runtime assets.
2. Turn each FAQ into a searchable text block using both question and answer text.
3. Compare the user query against the FAQ set using semantic similarity.
4. Apply confidence rules so weak or ambiguous matches are rejected.
5. Fall back to a lexical matcher if the embedding path is unavailable.

For more information on the runtime code behind this flow, check [backend/app/README.md](<C:/Users/sossi/OneDrive/Desktop/agent builder workspace/Riverside Chatbot solution/backend/app/README.md>). For the broader project explanation, check [backend/Project-explained/README.md](<C:/Users/sossi/OneDrive/Desktop/agent builder workspace/Riverside Chatbot solution/backend/Project-explained/README.md>).

## Trade-Offs

![Trade-offs visual](assets/demo-tradeoffs.gif)

| Approach | Accuracy | Latency | Cost | Hallucination |
| --- | --- | --- | --- | --- |
| LLM as the chat engine | High | Medium-High | High | High |
| Embeddings / semantic matching | Medium-High | Medium | Low-Medium | Low |
| Keyword overlap / fuzzy matching | Low-Medium | Low | Low | Very low |

For this project, semantic matching is the best fit because it handles paraphrased questions well without paying the cost and hallucination risk of an LLM-first design.

For more information on the longer reasoning behind these trade-offs, check [backend/Project-explained/README.md](<C:/Users/sossi/OneDrive/Desktop/agent builder workspace/Riverside Chatbot solution/backend/Project-explained/README.md>).

## What's Next For Scale

![Scale path](assets/demo-scale-path.gif)

The next step is to expose the backend as an AWS-hosted API that the Vercel frontend can call directly.

After that, the scaling path is:

1. add a clean HTTP API layer in the backend
2. introduce better evaluation and monitoring
3. add deployment and environment separation across dev, preview, and production
4. use LLM routing only where retrieval alone is not enough

For more information on backend evolution, check [backend/README.md](<C:/Users/sossi/OneDrive/Desktop/agent builder workspace/Riverside Chatbot solution/backend/README.md>). For frontend delivery details, check [frontend/README.md](<C:/Users/sossi/OneDrive/Desktop/agent builder workspace/Riverside Chatbot solution/frontend/README.md>).
