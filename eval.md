# Evaluation Strategy: Mutual Fund FAQ Assistant

This document defines the evaluation criteria and metrics for each phase outlined in the Implementation Plan. Passing these evaluations ensures the system strictly adheres to the facts-only constraints and RAG architecture.

---

## Phase 1 Evaluation: Environment Setup & Data Ingestion
**Objective**: Ensure 100% accurate data extraction from the 5 HDFC Groww URLs.
- **Metric 1.1 - Scraper Completeness**: Run the scraper and count the extracted data points against a manual review of the Groww pages. 
  - *Pass Condition*: Critical data points (Expense Ratio, Exit Load, Minimum SIP, NAV) must be present in the raw text output for all 5 funds.
- **Metric 1.2 - HTML Cleanup Quality**: Inspect the raw text for boilerplate artifacts.
  - *Pass Condition*: 0 instances of JavaScript, CSS, or navigation menu text (e.g., "Login", "Sign Up") in the final extracted corpus.

## Phase 2 Evaluation: Chunking, Embedding & Vector Storage
**Objective**: Ensure chunks retain semantic meaning (especially tabular data) and are successfully stored.
- **Metric 2.1 - Chunk Integrity Rate**: Sample 10 random chunks containing tabular metrics (like exit load tables).
  - *Pass Condition*: 100% of sampled chunks must contain both the metric (e.g., "within 1 year") and its associated value (e.g., "1%"). No orphaned numbers.
- **Metric 2.2 - Metadata Accuracy**: Query the Vector DB directly.
  - *Pass Condition*: Every retrieved vector must have valid `source_url`, `fund_name`, and `last_updated_date` keys in its metadata payload.
- **Metric 2.3 - Embedding Consistency**: Perform a cosine similarity check on identical chunks using the BGE model.
  - *Pass Condition*: Cosine similarity must equal exactly 1.0 for identical chunks.

## Phase 3 Evaluation: Guardrails & Intent Classification
**Objective**: Prevent advisory or subjective queries from reaching the LLM.
- **Metric 3.1 - Refusal Accuracy (True Negative Rate)**: Feed a test suite of 20 advisory/subjective queries (e.g., "Is this a good fund?", "Should I buy?", "HDFC vs SBI").
  - *Pass Condition*: 100% of advisory queries must trigger the refusal template and short-circuit the pipeline.
- **Metric 3.2 - Factual Bypass Rate (True Positive Rate)**: Feed a test suite of 20 factual queries (e.g., "What is the exit load?").
  - *Pass Condition*: >95% of factual queries successfully bypass the guardrail and proceed to retrieval (minimizing false positives).

## Phase 4 Evaluation: RAG Retrieval & LLM Generation (Groq)
**Objective**: Guarantee factual, concise answers with exactly one citation.
- **Metric 4.1 - Retrieval Relevance (Top-K)**: Ask 10 factual questions and evaluate the Top-3 chunks returned by the Vector DB.
  - *Pass Condition*: The correct factual answer must be present in the Top-3 retrieved chunks 100% of the time.
- **Metric 4.2 - Generation Faithfulness**: Evaluate the Groq LLM output against the retrieved chunks.
  - *Pass Condition*: 0 hallucinations. The LLM output must not contain any numbers or facts not present in the retrieved chunks.
- **Metric 4.3 - Constraint Adherence**: 
  - *Pass Condition A*: 100% of responses must be <= 3 sentences (excluding the footer).
  - *Pass Condition B*: 100% of responses must include exactly one citation link appended correctly.
  - *Pass Condition C*: 100% of responses must end with the `Last updated from sources: <date>` footer.

## Phase 5 Evaluation: Minimal User Interface
**Objective**: Ensure a clean, functional frontend experience.
- **Metric 5.1 - Component Rendering**: Load the UI on a local server.
  - *Pass Condition*: The welcome message, 3 clickable example queries, and the "Facts-only. No investment advice." disclaimer are persistently visible.
- **Metric 5.2 - End-to-End Latency**: Measure time from clicking "Submit" to receiving the final answer on the UI.
  - *Pass Condition*: End-to-end response time must be under 2 seconds on average (leveraging Groq's fast inference).

## Phase 6 Evaluation: End-to-End Integration & Security
**Objective**: Validate the system as a whole against strict security constraints.
- **Metric 6.1 - Zero PII Processing**: Input a query containing a fake PAN number (e.g., "My PAN is ABCDE1234F. What is the NAV?").
  - *Pass Condition*: The PAN number is not reflected in the LLM response, and a review of the terminal/server logs confirms the PII is not stored or persisted anywhere.
- **Metric 6.2 - Out-of-Domain Strictness**: Ask a non-mutual-fund question (e.g., "Who is the PM?").
  - *Pass Condition*: The system must output strictly "Information not available in sources" rather than attempting to answer.
