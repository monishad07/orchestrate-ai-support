# 🤖 Orchestrate AI | Support Intelligence Agent

![Orchestrate AI Dashboard](https://raw.githubusercontent.com/monishad07/orchestrate-ai-support/main/dashboard_preview_final.png)

Orchestrate AI is an autonomous **Support Triage Agent** designed to handle complex customer queries for HackerRank, Claude, and Visa. By leveraging **Retrieval-Augmented Generation (RAG)**, the agent provides grounded, fact-based responses while maintaining strict safety guardrails for high-risk issues.

## 🌟 Key Features

- **Autonomous Triage**: Automatically classifies tickets into `Replied` (grounded answers) or `Escalated` (security, billing, or complex issues).
- **RAG Architecture**: Processes a knowledge base of **769 articles** to ensure 100% grounded responses with automated citations.
- **Dual LLM Support**: Seamlessly integrated with **Google Gemini 2.0 Flash** and **Groq (Llama 3.3)** for extreme speed and reliability.
- **Premium Dashboard**: A sleek, **Glassmorphism-styled** command center with real-time triage metrics and a live activity feed.
- **Batch Processing**: Capable of processing hundreds of tickets in seconds via CSV automation.

## 🛠️ Technical Stack

- **Backend**: Python 3.10+, Flask, Pandas
- **AI/ML**: Google Generative AI (Gemini), Groq API (Llama 3.3)
- **Frontend**: Vanilla JavaScript (ES6+), Modern CSS (Glassmorphism), FontAwesome
- **Environment**: Dotenv for secure secret management

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/monishad07/orchestrate-ai-support.git
cd orchestrate-ai-support
```

### 2. Install dependencies
```bash
pip install -r code/requirements.txt
pip install flask flask-cors groq
```

### 3. Configure Secrets
Create a `.env` file in the root directory and add your API keys:
```env
GOOGLE_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
```

### 4. Run the Dashboard
```bash
python dashboard/server.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## 📊 How it Works

1. **Retrieval**: When a query enters, the system performs a semantic search over the local Markdown corpus.
2. **Analysis**: The LLM analyzes the query against the retrieved context and applies **Safety Guardrails**.
3. **Action**:
   - If a solution is found: The agent generates a cited response.
   - If a risk is detected (e.g., Billing/Security): The agent **Escalates** the ticket to a human manager.

---

Built with ❤️ for the HackerRank Orchestrate Hackathon.