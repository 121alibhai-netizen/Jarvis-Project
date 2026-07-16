import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, base64

# --- GLOBAL STORAGE (To prevent st.session_state crashes) ---
# Ye variables background threads mein bhi kaam karenge
if 'live_vision_data' not in globals():
    global live_vision_data, current_task
    live_vision_data = None
    current_task = "NONE"

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID"))
}

# --- THE GHOST EYES & TASK PORT ---
params = st.query_params
if params.get("stream") == "true":
    img_data = st.context.headers.get("image-content")
    if img_data:
        globals()['live_vision_data'] = img_data
        st.write("EYES_ACTIVE")
        st.stop()

if params.get("get_task") == "true":
    st.write(globals()['current_task'])
    st.stop()

# --- MEMORY ENGINE ---
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
    model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
    
    system_prompt = f"""
    You are J.A.R.V.I.S., the loyal AI of Muhammad Ali. Professional, Senior Architect, Concise.
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
        # Memory recall + Vision from Global variable
        history = await get_full_memory(bot)
        response = ask_jarvis_ultra(message.content, history, globals()['live_vision_data'])
        
        if "```python" in response:
            globals()['current_task'] = response.split("```python")[1].split("```")[0].strip()
        
        await message.channel.send(response.split("```python")[0].strip())

# --- RUNNER ---
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run, daemon=True).start()

# --- WEB UI ---
st.title("🤖 J.A.R.V.I.S. Ultra Terminal")
st.write("System Status: **ACTIVE**")

if globals()['live_vision_data']:
    st.image(base64.b64decode(globals()['live_vision_data']), caption="Live Telemetry")
    if st.button("Reset Vision"):
        globals()['live_vision_data'] = None
        st.rerun()
else:
    st.info("Awaiting video feed from laptop body...")

st.subheader("Current Task in Bridge:")
st.code(globals()['current_task'])
