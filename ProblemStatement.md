# Project Context: Mutual Fund FAQ Assistant

## Overview
The project is a **facts-only FAQ assistant** for mutual fund schemes (inspired by Groww). It utilizes a Retrieval-Augmented Generation (RAG) approach to answer objective, verifiable user queries by fetching information exclusively from official public sources like AMC, AMFI, and SEBI websites.

## Core Objective
To provide trustworthy, transparent, and compliant financial information without any advisory bias, speculative content, or investment recommendations. The system prioritizes accuracy and factuality over general intelligence.

## Target Audience
- Retail investors comparing mutual fund schemes.
- Customer support and content teams handling repetitive mutual fund queries.

## Key Features & Requirements
1. **Facts-Only Responses**: Answers objective queries (e.g., expense ratios, exit loads, SIP amounts, lock-in periods).
2. **Response Constraints**: 
   - Maximum of 3 sentences per response.
   - Exactly one citation link per response.
   - A mandatory footer: `Last updated from sources: <date>`.
3. **Refusal Handling**: Politely refuses non-factual or advisory queries (e.g., "Which fund is better?"), reinforcing the facts-only limitation and providing an educational link (AMFI/SEBI).
4. **User Interface**: A minimal, clean UI with a welcome message, 3 example questions, and a visible disclaimer: `"Facts-only. No investment advice."`

## Corpus Definition
- **Primary Asset Management Company (AMC)**: HDFC Mutual Funds.
- **Corpus URLs**: The RAG chatbot will extract its knowledge from the following provided URLs:
  1. [HDFC Gold ETF Fund of Fund Direct Plan Growth](https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth)
  2. [HDFC Large Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth)
  3. [HDFC Small Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth)
  4. [HDFC Silver ETF FoF Direct Growth](https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth)
  5. [HDFC Mid-Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)
- Additional official documents (like Scheme factsheets, KIM, SID, AMFI/SEBI guidance) linked from these pages may be utilized as supplementary factual sources.

## Strict Constraints
- **Data Sources**: Strictly official public sources; no third-party blogs or aggregators.
- **Privacy & Security**: Zero collection, storage, or processing of PII (PAN, Aadhaar, account numbers, OTPs, emails, phone numbers).
- **Content**: Absolute prohibition of investment advice, recommendations, performance comparisons, or return calculations (for performance queries, only provide a link to the official factsheet).
