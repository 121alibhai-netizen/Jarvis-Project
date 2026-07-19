import requests

def ask_jarvis_pro(query, memory_json, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # We provide the entire JSON as context, just like my own context window
    system_prompt = f"""
    You are J.A.R.V.I.S., the Senior AI for Muhammad Ali.
    IDENTITY: Loyal, professional, highly intelligent, concise.
    MEMORY ACCESS: {memory_json}
    
    TASK: 
    1. Use the 'history' and 'facts' in the memory to answer the Master.
    2. If the user provides a new fact (name, age, etc.), you MUST store it.
    3. Output Format: Your spoken response followed by '###DATA_UPDATE###' and the NEW updated JSON.
    4. NO SYSTEM TALK. Do not say 'Memory updated'. Just answer naturally.
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
        return "Sir, I am facing a neural synchronization issue. ###DATA_UPDATE### NONE"
