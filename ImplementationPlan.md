# Phase-wise Implementation Plan: Mutual Fund FAQ Assistant

This document outlines the granular, step-by-step implementation phases required to build the Mutual Fund FAQ Assistant based on the approved architecture.

## Phase 1: Environment Setup
**Goal:** Initialize the project workspace.
1. **Virtual Environment**: Set up a Python virtual environment.
2. **Dependencies**: Install required libraries (`requests`, `beautifulsoup4`, `langchain`, `groq`, `sentence-transformers`, vector db client) via `requirements.txt`.

## Phase 2: Web Scraping
**Goal:** Extract raw HTML data from the specified HDFC Groww URLs.
1. **Target Identification**: Define the 5 provided HDFC Mutual Fund Groww URLs.
2. **Data Fetching**: Implement an HTTP request module (using `requests`) with appropriate headers to fetch the raw HTML payload for each fund.

## Phase 3: Data Cleaning
**Goal:** Remove noise and extract linear, readable text.
1. **HTML Stripping**: Use `BeautifulSoup` to strip out all non-essential HTML tags (`<script>`, `<style>`, `<nav>`, `<footer>`, `<svg>`, etc.).
2. **Text Extraction**: Pull the remaining visible text, ensuring that tabular layouts (like expense ratios and exit loads) are separated by newlines to preserve context.
3. **Storage**: Save the cleaned text into local `.txt` files in a dedicated `data/` directory.

## Phase 4: Text Chunking
**Goal:** Prepare the data for embedding by leveraging the pre-parsed semantic text blocks.
1. **Semantic Block Pass-Through**: Because our data cleaning pipeline (Phase 3) now outputs perfectly structured `text_blocks` in JSON format, we no longer need a sliding-window text splitter! We will iterate over the JSON array and treat every single `text` block (e.g., "Exit load", "Key fund facts") as exactly 1 distinct chunk.
2. **Context Enrichment Validation**: We will ensure that the top-level metadata (`scheme_name`, `source_url`, `nav_date`) is injected into the payload or metadata of every single semantic chunk so the LLM retains full context during retrieval.
3. **Metadata Tagging**: Attach crucial structured metadata (`source_url`, `scheme_id`) to the chunk object for vector filtering and citations.

## Phase 5: Embedding & Vector Storage
**Goal:** Convert text chunks into searchable vector representations.
1. **BGE Embedding**: Integrate the **BAAI/bge-small-en-v1.5** model via HuggingFace locally. Because our semantic blocks (from Phase 4) are highly concise (typically 50-100 words), the `small` model is perfectly optimized to capture this context. The `large` model would introduce unnecessary latency and RAM overhead without any tangible gain in accuracy for chunks of this size.
2. **Database Initialization**: Set up a lightweight vector database (e.g., ChromaDB).
3. **Data Indexing**: Ingest the embedded semantic chunks and their associated metadata into the vector store for fast retrieval.

## Phase 6: Guardrails & Intent Classification
**Goal:** Prevent advisory responses before they reach the LLM.
1. **Intent Classifier**: Implement routing logic (via zero-shot prompt or heuristics) to classify user queries as either **Factual** or **Advisory**.
2. **Refusal Handler**: If a query is advisory, short-circuit the pipeline and return a refusal template (with a SEBI/AMFI educational link).

## Phase 7: RAG Retrieval & Generation (Groq)
**Goal:** Answer factual queries using the Vector DB and a highly constrained LLM.
1. **Semantic Block Top-K Retrieval**: Because our chunks are mapped 1-to-1 with logical concepts (e.g., an entire chunk dedicated solely to "Exit Load"), we will use a simple Top-K Semantic Search (k=2). The vector space distance alone will be highly accurate, bypassing the need for complex retrieval algorithms (like Multi-Query or Parent-Document).
2. **Strict Prompt Engineering**: Instruct the LLM to use *only* the provided context, adhere to a strict maximum of 3 sentences, and provide exactly one citation link.
3. **Groq Engine**: Use the **Groq API** (running `llama3-8b-8192`) configured at `temperature=0.0` for rapid, deterministic generation.
4. **Post-Processing**: Append the required footer (`Last updated from sources: <date>`) to the LLM response.

## Phase 8: User Interface Development
**Goal:** Provide a minimal frontend for user interaction.
1. **UI Framework**: Build a simple web interface (e.g., using Streamlit).
2. **Component Integration**: Include a welcome message, 3 example queries, and a visible disclaimer: `"Facts-only. No investment advice."`
3. **Backend Wiring**: Connect the UI inputs directly to the RAG pipeline.

## Phase 9: Testing & Validation
**Goal:** Ensure the system meets strict compliance and constraint rules.
1. **Accuracy & Formatting**: Test factual queries to ensure the <= 3 sentence limit and citation rules are strictly followed.
2. **Refusal Auditing**: Test advisory queries to guarantee a 100% refusal rate.
3. **Privacy Checks**: Ensure PII (like PAN numbers) is completely ignored and not logged by the system.

## Phase 10: Automated Data Scheduler (Fresh Data)
**Goal:** Ensure the assistant always pulls the most recent daily NAVs and mutual fund metrics without manual intervention.
1. **GitHub Actions Workflow**: Create a `.github/workflows/data_ingestion.yml` workflow file.
2. **Cron Trigger**: Configure the workflow to trigger on a daily cron schedule (`schedule: - cron: '0 5 * * *'`) which corresponds to 10:30 AM IST.
3. **Pipeline Execution**: The workflow will set up Python, install dependencies, and sequentially run `scraper.py`, `parse_data.py`, and `build_index.py`.
4. **Automated Commits**: The workflow will automatically commit the newly generated JSON files and updated Chroma DB back to the repository.
