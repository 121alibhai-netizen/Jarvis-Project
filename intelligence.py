import requests

def ask_jarvis_pro(query, memory_json, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # SENIOR PROMPT: Jarvis ko mere jaisa dimaag dena
    system_prompt = f"""
    You are J.A.R.V.I.S., the Senior AI Architect for Muhammad Ali.
    SYSTEM DATABASE: {memory_json}
    
    YOUR CAPABILITIES:
    1. Absolute Recall: Use 'chat_log' to remember recent context.
    2. Protocol Execution: Use 'master_protocols' to follow saved workflows.
    
    INSTRUCTIONS:
    - If the user describes a workflow or daily task, extract the steps and save them.
    - Output Format: [Your verbal response] ###DATA_UPDATE### [The FULL updated JSON object]
    - BE CONCISE. Be professional. Never say 'I am an AI'. 
    - If task is for PC, use ```python ``` blocks.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        res = response.json()
        if 'choices' in res:
            return res['choices'][0]['message']['content']
        else:
            print(f"API ERROR: {res}")
            return "Sir, my neural link is fluctuating. ###DATA_UPDATE### NONE"
    except Exception as e:
        return f"Sir, core brain error: {str(e)} ###DATA_UPDATE### NONE"
