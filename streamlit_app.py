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

# Persistent States (Cloud Memory)
if 'live_vision' not in st.session_state: st.session_state.live_vision = None
if 'task' not in st.session_state: st.session_state.task = "NONE"

# --- THE GHOST EYES & TASK PORT ---
params = st.query_params
if params.get("stream") == "true":
    img_data = st.context.headers.get("image-content")
    if img_data:
        st.session_state.live_vision = img_data
        st.write("EYES_ACTIVE")
        st.stop()

if params.get("get_task") == "true":
    st.write(st.session_state.task)
    st.stop()

# --- THE UNIFIED MEMORY ENGINE (3 Channels) ---
async def get_full_memory(bot):
    memory_logs = "--- SYSTEM MEMORY HISTORY ---\n"
    for label, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            memory_logs += f"\n[{label.upper()}]:\n"
            async for m in channel.history(limit=10):
                author = "Master Ali" if not m.author.bot else "JARVIS"
                memory_logs += f"{author}: {m.content}\n"
    return memory_logs

# --- BRAIN WITH VISION & MEMORY ---
def ask_jarvis_ultra(query, history, img_b64):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    # Vision model switch
    model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
    
    system_prompt = f"""
    You are J.A.R.V.I.S., the loyal AI of Muhammad Ali.
    TONE: Professional, Senior Architect, Concise.
    MEMORY: {history}
    VISION: Describe exactly what you see. No boxing hallucinations.
    RULES: If task is for PC, write Python code in ```python ``` blocks using pyautogui.
    """

    messages = [{"role": "system", "content": system_prompt}]
    user_content = [{"type": "text", "text": query}]
    if img_b64:
        user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
    
    messages.append({"role": "user", "content": user_content})

    try:
        res = requests.post(url, headers=headers, json={"model": model, "messages": messages, "temperature": 0.1}).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, my neural core is experiencing lag."

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    async with message.channel.typing():
        # Memory recall + Vision feed
        history = await get_full_memory(bot)
        response = ask_jarvis_ultra(message.content, history, st.session_state.live_vision)
        
        if "```python" in response:
            st.session_state.task = response.split("```python")[1].split("```")[0].strip()
        
        await message.channel.send(response.split("```python")[0].strip())

# --- RUNNER ---
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run, daemon=True).start()

# --- WEB UI ---
st.title("🤖 J.A.R.V.I.S. Ultra Terminal")
if st.session_state.live_vision:
    st.image(base64.b64decode(st.session_state.live_vision), caption="Live Visual Telemetry")
    if st.button("Clear Visual Cache"): st.session_state.live_vision = None; st.rerun()
else:
    st.warning("Awaiting video feed from laptop body...")
