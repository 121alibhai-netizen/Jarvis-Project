import requests

def ask_groq(query, api_key):
    # Filhal ye sirf baat karega, memory hum baad mein add karenge
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    system_prompt = "You are J.A.R.V.I.S., a professional AI. Be brief and smart."
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "temperature": 0.5
    }
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        return res['choices'][0]['message']['content']
    except:
        return "Sir, my cognitive core is not responding."
