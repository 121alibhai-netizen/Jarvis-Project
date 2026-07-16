import requests

def ask_groq(query, memory_context, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    system_prompt = f"""
    You are J.A.R.V.I.S., a high-intelligence AI. 
    Use the following MEMORY to understand the Master's workflows and identity:
    {memory_context}
    
    RULES:
    1. If the Master says 'remember' or 'save to workflow', start response with 'MEM_SAVE:'.
    2. Use permanent memory to repeat previous successful workflows.
    3. PC tasks must be in ```python ``` blocks.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "temperature": 0.2
    }
    res = requests.post(url, headers=headers, json=data, timeout=15).json()
    return res['choices'][0]['message']['content']
    
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        return res['choices'][0]['message']['content']
    except:
        return "Sir, my cognitive core is not responding."
