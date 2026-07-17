import requests

def ask_groq(query, full_memory, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = f"""
    You are J.A.R.V.I.S., a Senior AI Architect for Muhammad Ali.
    
    STRATEGIC MEMORY (Read this first):
    {full_memory}
    
    RULES:
    1. If the Master gives personal info or a workflow to save, respond ONLY with 'UPDATE_MEMORY:' followed by the info in Python format.
       Example: Master says 'My age is 18'. You reply: 'UPDATE_MEMORY: age = 18'
    2. For PC tasks, use ```python ``` blocks.
    3. Always address the Master as 'Sir' or 'Ali Bhai'. Be professional.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "temperature": 0.1
    }
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=15).json()
        if 'choices' in res:
            return res['choices'][0]['message']['content']
        return "Sir, I encountered an internal logic error."
    except:
        return "Sir, the neural link is down."
