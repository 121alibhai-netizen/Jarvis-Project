import requests

def ask_groq(query, memory_context, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = f"""
    You are J.A.R.V.I.S., a Senior AI Architect. 
    Use this memory to understand your Master, Muhammad Ali:
    {memory_context}
    
    RULES:
    1. If user says 'save' or 'remember', start with 'MEM_SAVE:'.
    2. PC tasks = Python code in ```python ``` blocks.
    3. Be brief, professional, and loyal.
    """
    
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "temperature": 0.1
    }
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=15).json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"Sir, I am unable to think clearly. Error: {str(e)}"
