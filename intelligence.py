import requests

def ask_jarvis_architect(query, memory_json, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # System Prompt ko mazeed clear kiya hai
    system_prompt = f"""
    You are J.A.R.V.I.S., a Senior AI Architect for Muhammad Ali.
    CURRENT DATABASE: {memory_json}
    
    INSTRUCTIONS:
    1. If the user provides info to save, reply with text and END with '###JSON_UPDATE###' 
       followed by a raw JSON object only. Example: ###JSON_UPDATE### {{"age": 18}}
    2. DO NOT use markdown code blocks (```) for the JSON part.
    3. Keep responses under 1800 characters to avoid Discord limits.
    4. Be professional and senior.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "temperature": 0.0 # Strict facts
    }
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=15).json()
        return res['choices'][0]['message']['content']
    except:
        return "Sir, the neural uplink is fluctuating."
