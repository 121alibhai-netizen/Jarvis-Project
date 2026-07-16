import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

# --- SENIOR CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID"))
}

# Task Bridge storage for laptop
if 'task_bridge' not in st.session_state: st.session_state.task_bridge = "NONE"

# --- THE MEMORY ENGINE (3 Tiers) ---
async def get_jarvis_memory(bot):
    memory_data = "--- SYSTEM CORE MEMORY ---\n"
    for label, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            memory_data += f"\n[{label.upper()}]:\n"
            async for m in channel.history(limit=15):
                author = "Master Ali" if not m.author.bot else "JARVIS"
                memory_data += f"{author}: {m.content}\n"
    return memory_data

# --- SENIOR BRAIN LOGIC ---
def ask_jarvis_senior(query, full_history):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    system_message = f"""
    You are J.A.R.V.I.S., the senior AI assistant to Muhammad Ali.
    TONE: Professional, concise, loyal.
    MEMORY: {full_history}
    RULES:
    1. PC tasks (open apps, type, files) must be in ```python ``` blocks using pyautogui.
    2. Answer factual questions directly using your memory.
    3. Never mention 'accessing memory'. You just know everything.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_message}, {"role": "user", "content": query}],
        "temperature": 0.2
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=12).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, my neural link is experiencing instability."

# --- DISCORD SOUL ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        history = await get_jarvis_memory(bot)
        response = ask_jarvis_senior(message.content, history)
        
        if "```python" in response:
            st.session_state.task_bridge = response.split("```python")[1].split("```")[0].strip()
        
        await message.channel.send(response.split("```python")[0].strip())

# --- RUNNER (No Double Replies) ---
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run, daemon=True).start()

# --- WEB TERMINAL ---
st.title("🤖 JARVIS: Master Control")
st.subheader("Task Bridge (Laptop Order):")
st.code(st.session_state.task_bridge)

if st.button("Reset Task"):
    st.session_state.task_bridge = "NONE"
    st.rerun()
