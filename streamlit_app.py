import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

st.set_page_config(page_title="Jarvis Senior Terminal", page_icon="🤖")
st.title("🤖 Jarvis Master Soul")

TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID"))
}

# Task Bridge
if 'task' not in st.session_state: st.session_state.task = "NONE"

# --- MEMORY RETRIEVAL ---
async def get_all_memory(bot):
    logs = "--- SYSTEM MEMORY START ---\n"
    for name, cid in CH_IDS.items():
        ch = bot.get_channel(cid)
        if ch:
            logs += f"\n[{name.upper()}]:\n"
            async for m in ch.history(limit=15):
                logs += f"{'Master' if not m.author.bot else 'Jarvis'}: {m.content}\n"
    return logs

# --- BRAIN LOGIC ---
def ask_brain(query, history):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    system_prompt = f"""You are JARVIS. Use the memory below to remember EVERYTHING about Muhammad Ali. 
    If his name is in the history, address him as 'Sir' or 'Ali Bhai'.
    Memory Banks: {history}
    Rules: 1. PC tasks = python code in ```python ``` blocks. 2. Chat = professional & brief. 3. 'save' = start with 'SAVING:'."""
    
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}], "temperature": 0.2}
    try:
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, connection to core brain is flickering."

# --- DISCORD SETUP ---
if "bot_instance" not in st.session_state: st.session_state.bot_instance = None

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    msg_clean = message.content.lower().strip()
    
    if msg_clean == "screen":
        st.session_state.task = "SCREEN_CMD"
        await message.channel.send("📸 **Sir, capturing laptop screen now...**")
        return

    async with message.channel.typing():
        history = await get_all_memory(bot)
        response = ask_brain(message.content, history)
        
        if "```python" in response:
            st.session_state.task = response.split("```python")[1].split("```")[0].strip()
            await message.channel.send(f"🛠️ {response.split('```python')[0]}")
        else:
            await message.channel.send(response)

# --- RUNNER (DOUBLE REPLY FIX) ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "started" not in st.session_state:
    st.session_state.started = True
    threading.Thread(target=run_bot, daemon=True).start()

st.subheader("Current Order for Laptop:")
st.code(st.session_state.task)
if st.button("Reset Bridge"): 
    st.session_state.task = "NONE"
    st.rerun()
