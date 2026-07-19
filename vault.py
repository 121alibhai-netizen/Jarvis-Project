import requests
import base64
import json

def get_json_memory(repo, token):
    url = f"https://api.github.com/repos/{repo}/contents/memory.json"
    headers = {"Authorization": f"token {token}"}
    try:
        r = requests.get(url, headers=headers).json()
        if 'content' in r:
            content = base64.b64decode(r['content']).decode('utf-8')
            return json.loads(content), r['sha']
        return {"facts": {}, "history": []}, None
    except:
        return {"facts": {}, "history": []}, None

def update_json_memory(repo, token, updated_data):
    url = f"https://api.github.com/repos/{repo}/contents/memory.json"
    headers = {"Authorization": f"token {token}"}
    
    # SENIOR MOVE: Always get the latest SHA before saving to prevent 409 errors
    r_check = requests.get(url, headers=headers).json()
    sha = r_check.get('sha')
    
    encoded_content = base64.b64encode(json.dumps(updated_data, indent=4).encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": "Jarvis Memory Auto-Sync",
        "content": encoded_content,
        "sha": sha
    }
    requests.put(url, headers=headers, json=payload)
