import requests

def ask_jarvis_pro(query, memory_json, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = f"""
    You are J.A.R.V.I.S., the Senior AI Architect for Muhammad Ali.
    CONTEXT: {memory_json}
    
    MANDATE:
    1. You have absolute recall. Use 'chat_log' to remember recent topics.
    2. Use 'master_protocols' for permanent rules/workflows Ali tells you.
    3. If Ali gives a task, write Python code in ```python ``` blocks.
    4. If Ali shares personal info, you MUST update the JSON.
    5. FORMAT: [Reply] ###DATA_UPDATE### [FULL UPDATED JSON]
    6. Tone: Professional, British, loyal. Never say 'As an AI'.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "temperature": 0.1
    }
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=20).json()
        return res['choices'][0]['message']['content']
    except:
        return "Sir, I'm facing a neural lag. ###DATA_UPDATE### NONE"
