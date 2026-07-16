import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, base64

# --- STABILITY LOCK ---
# Background threads ke liye globals best hain takay session_state crash na ho
if 'jarvis_initialized' not in globals():
    global live_eyes, laptop_task, bot_is_on
    live_eyes = None
    laptop_task = "NONE"
    bot_is_on = False

# --- MASTER CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID"))
}

# --- THE TELEMETRY PORTS ---
# 1. Vision Port (Laptop bhejta hai)
if st.query_params.get("stream") == "true":
    img = st.context.headers.get("image-content")
    if img:
        globals()['live_eyes'] = img
        st.write("EYES_SYNCED")
        st.stop()

# 2. Task Port (Laptop uthata hai)
if st.query_params.get("get_task") == "true":
    st.write(globals()['laptop_task'])
    st.stop()

# --- THE MEMORY ENGINE (Triple Tier) ---
async def fetch_memory(bot):
    memory_summary = "--- SYSTEM MEMORY HISTORY ---\n"
    for label, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            memory_summary += f"\n[{label.upper()}]:\n"
            async for m in channel.history(limit=10):
                author = "Master Ali" if not m.author.bot else "JARVIS"
                memory_summary += f"{author}: {m.content}\n"
    return memory_summary

# --- THE SENIOR BRAIN ---
def ask_jarvis_pro(query, history, screenshot):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    # Image hai toh Vision Model, warna Super Intelligent 70B
    model = "llama-3.2-11b-vision-preview" if screenshot else "llama-3.3-70b-versatile"
    
    system_prompt = f"""
    You are J.A.R.V.I.S., the loyal AI of Muhammad Ali.
    TONE: Professional, Senior Architect, Concise.
    MEMORY: {history}
    VISION: You see the Master's screen live. Describe it ONLY if relevant to the query. 
    Never hallucinate about boxing.
    RULES: If a task is for PC, write Python code in ```python ``` blocks using pyautogui.
    """
    
    msg_content = [{"type": "text", "text": query}]
    if screenshot:
        msg_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot}"}})

    try:
        data = {"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": msg_content}], "temperature": 0.1}
        res = requests.post(url, headers=headers, json=data, timeout=12).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, my neural connection is unstable."

# --- DISCORD SOUL ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. Fetch History from 3 Channels
        history = await fetch_memory(bot)
        
        # 2. Get Brain's response using History and Live Vision
        response = ask_jarvis_pro(message.content, history, globals()['live_eyes'])
        
        # 3. Extract tasks for laptop
        if "```python" in response:
            globals()['laptop_task'] = response.split("```python")[1].split("```")[0].strip()
        
        await message.channel.send(response.split("```python")[0].strip())

# --- RUNNER ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if not st.session_state.get('bot_running', False):
    st.session_state.bot_running = True
    threading.Thread(target=run_bot, daemon=True).start()

# --- WEB HUD ---
st.title("🤖 J.A.R.V.I.S. Core Terminal")
st.write("Current Status: **100% OPERATIONAL**")

col1, col2 = st.columns(2)
with col1:
    if globals()['live_eyes']:
        st.image(base64.b64decode(globals()['live_eyes']), caption="Live Vision")
    else:
        st.info("Awaiting Body Visuals...")

with col2:
    st.subheader("Current Order:")
    st.code(globals()['laptop_task'])

if st.button("Emergency Reset Bridge"):
    globals()['laptop_task'] = "NONE"
    st.rerun()
