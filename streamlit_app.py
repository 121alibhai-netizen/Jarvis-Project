import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, base64

# --- GLOBAL STORAGE ---
if 'jarvis_core' not in globals():
    global live_eyes, laptop_task
    live_eyes = None
    laptop_task = "NONE"

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID"))
}

# --- TELEMETRY PORTS ---
params = st.query_params
if params.get("stream") == "true":
    img = st.context.headers.get("image-content")
    if img:
        globals()['live_eyes'] = img
        st.write("EYES_SYNCED")
        st.stop()

if params.get("get_task") == "true":
    st.write(globals()['laptop_task'])
    st.stop()

# --- THE MEMORY ENGINE ---
async def fetch_memory(bot):
    memory_summary = "--- SYSTEM MEMORY HISTORY ---\n"
    for label, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            memory_summary += f"\n[{label.upper()}]:\n"
            async for m in channel.history(limit=15):
                author = "Master Ali" if not m.author.bot else "JARVIS"
                memory_summary += f"{author}: {m.content}\n"
    return memory_summary

# --- THE SENIOR BRAIN ---
def ask_jarvis_pro(query, history, screenshot):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    model = "llama-3.2-11b-vision-preview" if screenshot else "llama-3.3-70b-versatile"
    
    system_prompt = f"""
    You are J.A.R.V.I.S., the loyal AI of Muhammad Ali. Professional, Senior Architect.
    MEMORY: {history}
    VISION: You see the Master's screen. Describe exactly what you see. No boxing talk.
    RULES: If task is for PC, write Python code in ```python ``` blocks using pyautogui.
    """
    
    msg_content = [{"type": "text", "text": query}]
    if screenshot:
        msg_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot}"}})

    try:
        data = {"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": msg_content}], "temperature": 0.1}
        res = requests.post(url, headers=headers, json=data, timeout=12).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, my neural link is flickering."

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # Jab bhi message aaye, laptop ko 'SCREEN_CMD' bhej do takay taaza photo aaye
    globals()['laptop_task'] = "SCREEN_CMD"
    
    async with message.channel.typing():
        await asyncio.sleep(2) # 2 sec wait takay laptop photo bhej de
        history = await fetch_memory(bot)
        response = ask_jarvis_pro(message.content, history, globals()['live_eyes'])
        
        if "```python" in response:
            globals()['laptop_task'] = response.split("```python")[1].split("```")[0].strip()
        
        await message.channel.send(response.split("```python")[0].strip())

# --- RUNNER ---
if not st.session_state.get('started', False):
    st.session_state.started = True
    threading.Thread(target=lambda: bot.run(TOKEN), daemon=True).start()

st.title("🤖 J.A.R.V.I.S. Final Core")
if globals()['live_eyes']:
    st.image(base64.b64decode(globals()['live_eyes']), caption="Last Known Visual")
