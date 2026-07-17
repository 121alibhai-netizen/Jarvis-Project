import requests

def ask_groq(query, memory_context, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Senior Architect Strict Instructions
    system_prompt = f"""
    You are J.A.R.V.I.S., the Senior AI for Muhammad Ali. 
    MANDATORY: You MUST read the MEMORY BANKS provided below before answering.
    Your Master's name, location, and past instructions are stored there.
    
    {memory_context}
    
    PROTOCOL:
    1. If the Master's name is in memory, address him as 'Sir' or 'Ali bhai'.
    2. If the user says 'remember this' or 'save to workflow', reply with 'MEM_SAVE:' followed by the info.
    3. If asked 'Who am I?', search the 'Master Identity' section in the memory text above.
    4. PC Tasks must be in ```python ``` blocks.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "temperature": 0.1 # Sabse zyada accuracy ke liye temperature low rakha hai
    }
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=15).json()
        return res['choices'][0]['message']['content']
    except:
        return "Sir, I'm having trouble accessing my cognitive memory centers."
