import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

# --- SENIOR CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

# Memory IDs
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID"))
}

# Laptop Task Bridge
if 'task_bridge' not in st.session_state: st.session_state.task_bridge = "NONE"

# --- SMART BRAIN WITH HISTORY ---
async def get_history(bot):
    memory = ""
    for name, cid in CH_IDS.items():
        ch = bot.get_channel(cid)
        if ch:
            async for m in ch.history(limit=10):
                memory += f"{m.author.name}: {m.content}\n"
    return memory

def ask_senior_brain(query, history):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    system_msg = f"You are JARVIS. Use this history to remember the user: {history}. If a task is for PC, write Python code in ```python ``` blocks."
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": query}],
        "temperature": 0.2
    }
    res = requests.post(url, headers=headers, json=data, timeout=10).json()
    return res['choices'][0]['message']['content']

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # Memory retrieval
        history = await get_history(bot)
        response = ask_senior_brain(message.content, history)
        
        # Check for Action Code
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
            st.session_state.task_bridge = code # Bhej diya laptop ke liye
            await message.channel.send(f"⚡ **Task Routed:** {response.split('```python')[0]}")
        else:
            await message.channel.send(response)

# --- WEB UI FOR LAPTOP ---
st.title("🤖 Jarvis Master Soul")
st.subheader("Current Bridge Task:")
st.code(st.session_state.task_bridge) # Laptop isay parhega

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "started" not in st.session_state:
    st.session_state.started = True
    threading.Thread(target=run_bot, daemon=True).start()
