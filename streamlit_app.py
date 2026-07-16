import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, base64

# --- SENIOR CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID"))
}

# Persistent States
if 'live_vision' not in st.session_state: st.session_state.live_vision = None
if 'task' not in st.session_state: st.session_state.task = "NONE"

# --- THE GHOST EYES & TASK PORT ---
params = st.query_params
if params.get("stream") == "true":
    img_data = st.context.headers.get("x-image-data")
    if img_data:
        st.session_state.live_vision = img_data
        st.write("EYES_RECIEVED")
        st.stop()

if params.get("get_task") == "true":
    st.write(st.session_state.task)
    st.stop()

# --- THE UNIFIED MEMORY ENGINE ---
async def get_jarvis_memory(bot):
    memory_data = ""
    for label, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            async for m in channel.history(limit=15):
                author = "Master" if not m.author.bot else "JARVIS"
                memory_data += f"{author}: {m.content}\n"
    return memory_data

# --- BRAIN WITH VISION & MEMORY ---
def ask_jarvis_pro(query, history, img_b64):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    # Use Vision model if screen is available, otherwise use 70B
    model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
    
    system_prompt = f"""
    You are J.A.R.V.I.S., the loyal and highly advanced AI assistant to Muhammad Ali.
    TONE: Professional, British, concise, and proactive.
    MEMORY ACCESS: {history}
    VISION: You are currently looking at the Master's laptop screen via a live stream.
    RULES: 
    1. Use memory to address the Master correctly.
    2. If a task is for the PC, provide Python code in ```python ``` blocks.
    3. Never mention 'accessing logs'. Just know everything.
    """

    messages = [{"role": "system", "content": system_prompt}]
    
    user_content = [{"type": "text", "text": query}]
    if img_b64:
        user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
    
    messages.append({"role": "user", "content": user_content})

    try:
        res = requests.post(url, headers=headers, json={"model": model, "messages": messages, "temperature": 0.2}).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, I am having a moment of instability in my neural core."

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    async with message.channel.typing():
        history = await get_jarvis_memory(bot)
        response = ask_jarvis_pro(message.content, history, st.session_state.live_vision)
        
        if "```python" in response:
            st.session_state.task = response.split("```python")[1].split("```")[0].strip()
            await message.channel.send(response.split("```python")[0].strip())
        else:
            await message.channel.send(response)

# --- RUNNER ---
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run, daemon=True).start()

st.title("🤖 J.A.R.V.I.S. Visual & Memory Core")
if st.session_state.live_vision:
    st.image(base64.b64decode(st.session_state.live_vision), caption="Live Telemetry")
