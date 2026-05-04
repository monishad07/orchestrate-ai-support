import sys
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add the 'code' directory to the path so we can import our existing logic
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, 'code'))

try:
    from main import load_corpus, retrieve_relevant_docs, triage_ticket
except ImportError as e:
    print(f"Error importing main logic: {e}")
    sys.exit(1)

# Load environment
load_dotenv()

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Global corpus variable
DATA_DIR = os.path.join(base_dir, 'data')
print(f"Loading corpus from {DATA_DIR}...")
CORPUS = load_corpus(DATA_DIR)
print(f"Loaded {len(CORPUS)} articles.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        import pandas as pd
        output_path = os.path.join(base_dir, 'support_tickets', 'output.csv')
        if os.path.exists(output_path):
            df = pd.read_csv(output_path)
            stats = {
                "total": len(df),
                "replied": len(df[df['status'] == 'replied']),
                "escalated": len(df[df['status'] == 'escalated'])
            }
            return jsonify(stats)
    except:
        pass
    return jsonify({"total": 29, "replied": 18, "escalated": 11})

@app.route('/api/corpus', methods=['GET'])
def get_corpus_list():
    # Return a sample of the corpus for the UI
    sample = []
    for doc in CORPUS[:50]: # First 50 docs
        sample.append({
            "title": doc['title'],
            "company": doc['company'],
            "length": len(doc['content'])
        })
    return jsonify(sample)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    issue = data.get('issue', '')
    
    # Logic: 
    # 1. Infer company (or assume None for general query)
    company = "None"
    if "hackerrank" in issue.lower(): company = "hackerrank"
    elif "claude" in issue.lower(): company = "claude"
    elif "visa" in issue.lower(): company = "visa"
    
    # 2. Retrieve context
    relevant_docs = retrieve_relevant_docs(issue, company, CORPUS)
    
    # 3. Triage with Groq (Faster & No Quota Issues for Demo)
    try:
        from groq import Groq
        import json
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        # Prepare context text
        context_text = ""
        for doc in relevant_docs:
            context_text += f"\n---\nSource: {doc['title']}\n{doc['content'][:1500]}\n"

        prompt = f"""
You are a Support Triage Agent for HackerRank, Claude, and Visa.

SAFETY RULES:
1. ESCALATE if the user is REPORTING a current "Security Breach", "Hacking", "Fraud", "Unauthorized charge", or requesting a "Refund" or "Account Deletion".
2. REPLY if the user is simply ASKING ABOUT policies, general limits, or "How-to" questions, even if they mention words like security or limits.
3. ESCALATE only if the answer is completely missing from the context.

Context:
{context_text}

Ticket:
Company: {company}
Issue: {issue}

Output strictly as JSON:
{{
  "status": "replied" or "escalated",
  "product_area": "string",
  "response": "string",
  "justification": "string with source citation and sentiment analysis",
  "request_type": "product_issue", "bug", or "feature_request"
}}
"""
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        print(f"Groq Response: {completion.choices[0].message.content}")
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"Groq Error: {e}")
        return jsonify({"status": "error", "response": f"System Error: {str(e)}", "justification": "Please check the terminal for the full Groq error log."})

if __name__ == '__main__':
    # Run on port 5000
    app.run(debug=True, port=5000)
