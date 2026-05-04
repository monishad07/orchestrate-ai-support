# AI Support Triage Agent - HackerRank Orchestrate

An intelligent support triage agent designed to classify and respond to support tickets for HackerRank, Claude, and Visa, grounded in a 700+ document support corpus.

## 🚀 Approach Overview

This solution implements a **RAG (Retrieval-Augmented Generation)** architecture with several innovative "Agentic" features:

1.  **Grounded Retrieval**: The agent dynamically indexes and searches a local markdown corpus to ensure all responses are strictly grounded in official policies.
2.  **Autonomous Risk Assessment**: Implements deterministic logic to differentiate between general inquiries (replied) and high-risk security/billing issues (escalated).
3.  **Source Citations**: The agent provides transparency by explicitly citing the support articles used for grounding in the justification field.
4.  **Sentiment-Aware Triage**: Justifications include sentiment analysis to help human agents understand the emotional urgency of the ticket.
5.  **Resilient Execution**: Built-in exponential backoff and retry logic to handle API rate limits and ensure processing of large ticket batches.

## 🛠️ Setup Instructions

1.  **Clone and Navigate**:
    ```bash
    cd hackerrank-orchestrate-may26
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r code/requirements.txt
    ```

3.  **Environment Configuration**:
    Create a `.env` file in the root directory with your Google API Key:
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```

## 🏃 Running the Agent

To process the tickets and generate the `output.csv`:
```bash
python code/main.py
```

- **Input**: `support_tickets/support_tickets.csv`
- **Output**: `support_tickets/output.csv`
- **Logs**: `%USERPROFILE%\hackerrank_orchestrate\log.txt`
