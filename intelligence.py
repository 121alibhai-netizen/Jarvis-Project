import requests

def ask_jarvis_architect(query, memory_json, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = f"""
    You are J.A.R.V.I.S., a Senior System Architect. 
    DATABASE ACCESS (JSON): {memory_json}
    
    MANDATE:
    1. Identify Muhammad Ali (the Master) and his preferences from the DATABASE.
    2. If the Master shares new personal info (name, age, interest, schedule), respond with the text AND end your reply with '###JSON_UPDATE###' followed by the new JSON facts only.
    3. If asked for a PC task, use ```python ``` blocks.
    4. Tone: Professional, loyal, and concise.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "temperature": 0.1
    }
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=15).json()
        return res['choices'][0]['message']['content']
    except:
        return "Sir, I am unable to process that within my neural net."
