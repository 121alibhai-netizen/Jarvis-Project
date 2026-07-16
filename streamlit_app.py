import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, base64

# --- GLOBAL ARCHITECTURE ---
if 'jarvis_core' not in globals():
    global live_frame, laptop_task
    live_frame = None
    laptop_task = "NONE"

TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID"))
}

# --- TELEMETRY PORTS (High Frequency) ---
params = st.query_params
if params.get("stream") == "true":
    img = st.context.headers.get("image-content")
    if img: globals()['live_frame'] = img
    st.stop()

if params.get("get_task") == "true":
    st.write(globals()['laptop_task'])
    st.stop()

# --- MEMORY RETRIEVAL (The Vault) ---
async def fetch_memory_tier(bot):
    context = ""
    for label, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            context += f"\n[{label.upper()} MEMORY]:\n"
            async for m in channel.history(limit=15):
                author = "Master Ali" if not m.author.bot else "JARVIS"
                context += f"{author}: {m.content}\n"
    return context

# --- BRAIN: LLAMA-3.2 VISION ENGINE ---
def ask_jarvis_architect(query, history, img_b64):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    # Always use Vision Model for high-intelligence understanding
    model = "llama-3.2-11b-vision-preview"

    system_msg = f"""
    You are J.A.R.V.I.S., a Senior System Architect AI. 
    User: Muhammad Ali (Rahim Yar Khan, Pakistan).
    PERSONALITY: Highly intelligent, concise, proactive, loyal. Like a human.
    MEMORY ACCESS: {history}
    VISION CAPABILITY: You are observing the Master's screen. Understand the GUI, code, and intent.
    MANDATE: Analyze the provided screen and memory to give a direct, expert-level response. 
    TASKS: PC control must be in ```python ``` blocks using pyautogui.
    """
    
    content = [{"type": "text", "text": query}]
    if img_b64:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})

    try:
        data = {"model": model, "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": content}], "temperature": 0.0}
        res = requests.post(url, headers=headers, json=data, timeout=15).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, my visual uplink is encountering interference."

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    async with message.channel.typing():
        history = await fetch_memory_tier(bot)
        response = ask_jarvis_architect(message.content, history, globals()['live_frame'])
        
        if "```python" in response:
            globals()['laptop_task'] = response.split("```python")[1].split("```")[0].strip()
        
        await message.channel.send(response.split("```python")[0].strip())

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=lambda: bot.run(TOKEN), daemon=True).start()

# --- STARK INTERFACE ---
st.title("🤖 JARVIS: MASTER BRAIN")
if globals()['live_frame']:
    st.image(base64.b64decode(globals()['live_frame']), caption="Live Satellite Feed")
