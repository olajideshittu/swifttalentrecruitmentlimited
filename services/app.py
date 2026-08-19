import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
from supabase import create_client

load_dotenv() # Loads keys from your .env file

app = Flask(__name__)
CORS(app)

# Initialize Database
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@app.route('/scout', methods=['POST'])
def scout_bot():
    data = request.json
    title = data.get('title')
    sector = data.get('sector')
    
    # 1. THE HUNT: Scout real LinkedIn profiles via Serper (Google Search API)
    search_url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': os.getenv("SERPER_KEY"),
        'Content-Type': 'application/json'
    }
    payload = {
        "q": f'site:linkedin.com/in/ "{title}" "{sector}" Nigeria',
        "num": 10
    }
    
    response = requests.post(search_url, json=payload, headers=headers)
    search_results = response.json().get('organic', [])
    
    candidates = []
    for i, result in enumerate(search_results):
        candidate = {
            "name": result.get('title').split(' - ')[0],
            "title": title,
            "linkedin": result.get('link'),
            "score": round(9.8 - (i * 0.2), 1)
        }
        candidates.append(candidate)
        
        # 2. THE DATABASE: Save to Supabase (upsert handles de-duplication)
        supabase.table("candidate_leads").upsert(candidate, on_conflict="linkedin").execute()

    return jsonify(candidates)

if __name__ == '__main__':
    app.run(port=5000, debug=True)