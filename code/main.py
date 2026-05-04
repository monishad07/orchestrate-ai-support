import os
import pandas as pd
import glob
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re

# Load environment variables
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GOOGLE_API_KEY not found in environment. Please set it in a .env file.", flush=True)

def load_corpus(data_dir):
    """
    Loads the support corpus from the data directory.
    Returns a list of dictionaries containing company, filepath, title, and content.
    """
    corpus = []
    companies = ['hackerrank', 'claude', 'visa']
    for company in companies:
        company_dir = os.path.join(data_dir, company)
        if not os.path.exists(company_dir):
            continue
        
        # Find all markdown files, excluding index.md
        md_files = glob.glob(os.path.join(company_dir, '**', '*.md'), recursive=True)
        for filepath in md_files:
            if filepath.endswith('index.md'):
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract title from front matter if present
                    title_match = re.search(r'^title:\s*"(.*)"', content, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1)
                    else:
                        title = os.path.basename(filepath)
                    
                    corpus.append({
                        'company': company,
                        'filepath': filepath,
                        'title': title,
                        'content': content
                    })
            except Exception as e:
                print(f"Error loading {filepath}: {e}", flush=True)
    return corpus

def retrieve_relevant_docs(issue, company, corpus, top_n=2):
    """
    Retrieves the most relevant documents based on keyword overlap.
    """
    # Filter by company if known
    if company and company.lower() != 'none':
        relevant_corpus = [doc for doc in corpus if doc['company'].lower() == company.lower()]
    else:
        relevant_corpus = corpus
    
    # Simple scoring based on word overlap
    scores = []
    # Tokenize and clean issue text
    issue_tokens = set(re.findall(r'\w+', issue.lower()))
    
    for doc in relevant_corpus:
        content_tokens = set(re.findall(r'\w+', doc['content'].lower()))
        title_tokens = set(re.findall(r'\w+', doc['title'].lower()))
        
        # Calculate score: title matches weigh more
        score = len(issue_tokens.intersection(title_tokens)) * 3
        score += len(issue_tokens.intersection(content_tokens))
        
        scores.append((doc, score))
    
    # Sort by score and filter out zero scores
    scores.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, score in scores[:top_n] if score > 0]

def triage_ticket(issue, subject, company, relevant_docs):
    """
    Uses Gemini to triage the ticket based on the provided documents.
    """
    if not api_key:
        return {
            "status": "escalated",
            "product_area": "system",
            "response": "Agent configuration error: Missing API Key.",
            "justification": "The agent was unable to process the request because the GOOGLE_API_KEY is not set.",
            "request_type": "invalid"
        }

    # Prepare context
    context_parts = []
    for doc in relevant_docs:
        content_snippet = doc['content'][:2000] # Cap content to save tokens
        context_parts.append(f"ARTICLE: {doc['title']}\nCONTENT:\n{content_snippet}")
    
    context = "\n\n---\n\n".join(context_parts)
    
    prompt = f"""
You are an expert support triage agent for HackerRank, Claude, and Visa. 
Your goal is to accurately classify and respond to support tickets using ONLY the provided support corpus context.

TICKET INFORMATION:
- Company: {company}
- Subject: {subject}
- Issue: {issue}

SUPPORT CORPUS CONTEXT:
{context if context else "No relevant articles found in the corpus."}

TASK:
Generate a structured triage response for this ticket.

REQUIRED FIELDS:
1. status: Must be either 'replied' or 'escalated'. 
   - Use 'replied' ONLY if the provided context contains a direct answer to the user's issue.
   - Use 'escalated' if the issue involves billing, bugs, fraud, security, sensitive account access, or if no clear answer is found in the corpus.
2. product_area: A concise category (e.g., 'billing', 'account_access', 'technical_issue', 'general_info').
3. response: A professional, helpful response grounded in the corpus. 
   - If 'replied', provide the solution.
   - If 'escalated', explain that a human agent will help soon.
   - If the issue is completely out of scope (unrelated to the companies), state that it is out of scope.
4. justification: A 1-2 sentence internal reasoning for your choice of status and response.
   - INNOVATION: Explicitly cite the support article(s) used (e.g., "Based on 'Password Reset' and 'Security Policy' articles...").
   - Mention the user's sentiment (e.g., "The user seems frustrated, so I've prioritized...") to justify the tone.
5. request_type: Must be one of: 'product_issue', 'feature_request', 'bug', 'invalid'.

IMPORTANT RULES:
- DO NOT use any knowledge outside of the provided context.
- DO NOT hallucinate URLs, phone numbers, or policies.
- If the company is 'None', infer the company from the content.
- If multiple requests exist, address the most urgent one or handle them collectively if possible.
- Output MUST be a single JSON object.

JSON OUTPUT:
"""
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        # Fallback for parsing errors or API issues
        print(f"Error in LLM processing: {e}", flush=True)
        return {
            "status": "escalated",
            "product_area": "unknown",
            "response": "We've received your request and are escalating it to a human specialist for further assistance.",
            "justification": f"Internal error during automated triage: {str(e)}",
            "request_type": "product_issue"
        }

def main():
    # File paths relative to the 'code' directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    input_file = os.path.join(base_dir, 'support_tickets', 'support_tickets.csv')
    output_file = os.path.join(base_dir, 'support_tickets', 'output.csv')
    
    print(f"Starting Triage Agent...", flush=True)
    print(f"Loading support corpus from {data_dir}...", flush=True)
    corpus = load_corpus(data_dir)
    print(f"Successfully loaded {len(corpus)} support articles.", flush=True)
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.", flush=True)
        return

    print(f"Reading input tickets from {input_file}...", flush=True)
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV: {e}", flush=True)
        return

    import time

    results = []
    
    for i, row in df.iterrows():
        issue = str(row.get('Issue', ''))
        subject = str(row.get('Subject', ''))
        company = str(row.get('Company', 'None'))
        
        print(f"[{i+1}/{len(df)}] Triaging ticket for {company}...", flush=True)
        
        # Step 1: Retrieve relevant documentation
        relevant_docs = retrieve_relevant_docs(issue, company, corpus)
        
        # Step 2: Triage with LLM (with retry logic)
        max_retries = 10
        result = None
        for attempt in range(max_retries):
            result = triage_ticket(issue, subject, company, relevant_docs)
            if "quota" not in result.get('justification', '').lower():
                break
            print(f"   Rate limited. Waiting 60 seconds (Attempt {attempt+1}/{max_retries})...", flush=True)
            time.sleep(60)
        
        # Step 3: Collect results
        results.append({
            'status': result.get('status', 'escalated'),
            'product_area': result.get('product_area', 'unknown'),
            'response': result.get('response', 'Our team is reviewing your request.'),
            'justification': result.get('justification', 'Automated escalation.'),
            'request_type': result.get('request_type', 'product_issue')
        })
        
        # Add a small delay to stay within free tier limits (15 RPM -> 4s per request)
        time.sleep(4)

    # Create output DataFrame and save to CSV
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_file, index=False)
    print(f"\nTriage complete! {len(results)} tickets processed.", flush=True)
    print(f"Output saved to: {output_file}", flush=True)

if __name__ == "__main__":
    main()
