import requests

def ask_groq(query, memory_context, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # SENIOR INSTRUCTIONS
    system_prompt = f"""
    You are J.A.R.V.I.S., a Senior AI Architect. 
    Memory: {memory_context}
    Rules: PC tasks in ```python ``` blocks. Be brief and professional.
    """
    
    data = {
        # --- NEWEST STABLE MODEL ---
        "model": "llama-3.3-70b-versatile", 
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        res = response.json()
        
        # Check if the brain actually sent an answer
        if 'choices' in res:
            return res['choices'][0]['message']['content']
        else:
            # Ye line aapko asli wajah bataye gi ke Groq ne kyun mana kiya
            error_msg = res.get('error', {}).get('message', 'Unknown Error')
            return f"Sir, my brain core sent an error: {error_msg}. Please check your Groq Dashboard."
            
    except Exception as e:
        return f"Sir, I am unable to connect to the cloud. {str(e)}"
