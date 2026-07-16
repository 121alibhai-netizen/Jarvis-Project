import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, base64

# --- GLOBAL CORE (Storage for Image Data) ---
if 'visual_memory' not in globals():
    global current_eyes, last_order
    current_eyes = None
    last_order = "NONE"

TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID"))
}

# --- THE STARK TELEMETRY PORT ---
params = st.query_params
if params.get("stream") == "true":
    # Laptop se aane wali asli photo ka data pakarna
    raw_img = st.context.headers.get("x-image-data")
    if raw_img:
        globals()['current_eyes'] = raw_img
        st.write("EYES_SYNCED")
        st.stop()

if params.get("get_task") == "true":
    st.write(globals()['last_order'])
    st.stop()

# --- BRAIN: MULTI-MODAL VISION ENGINE ---
def ask_jarvis_vision(query, history, b64_image):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    
    # System Instruction: Is se Jarvis mere jaisa behave karega
    system_prompt = f"""
    You are J.A.R.V.I.S., a Senior System Architect. 
    Your Master is Muhammad Ali. 
    VISION: You are looking at the Master's screen. analyze pixels directly. 
    RULES: 
    1. Do NOT guess. If you see code, analyze the code. If you see a browser, name the site.
    2. Be concise, professional, and loyal. No filler talk.
    3. Memory Access: {history}
    4. For PC tasks, use ```python ``` blocks.
    """

    # Multi-modal Content structure
    content_list = [{"type": "text", "text": query}]
    if b64_image:
        content_list.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}
        })

    payload = {
        "model": "llama-3.2-11b-vision-preview", # Asli Vision Model
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_list}
        ],
        "temperature": 0.0, # Zero temperature = No Hallucination (Strict Facts)
        "max_tokens": 500
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15).json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"Sir, my visual core is offline. Error: {e}"

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    async with message.channel.typing():
        # Memory retrieval
        history = ""
        async for m in message.channel.history(limit=5):
            history += f"{m.author.name}: {m.content}\n"
            
        # Analysis using raw photo and history
        response = ask_jarvis_vision(message.content, history, globals()['current_eyes'])
        
        if "```python" in response:
            globals()['last_order'] = response.split("```python")[1].split("```")[0].strip()
        
        await message.channel.send(response.split("```python")[0].strip())

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run, daemon=True).start()

# --- HUD DISPLAY ---
st.title("🤖 J.A.R.V.I.S. Visual Core")
if globals()['current_eyes']:
    st.image(base64.b64decode(globals()['current_eyes']), caption="Live Satellite Feed")
