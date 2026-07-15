import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

# --- SENIOR CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID"))
}

# --- THE UNIFIED MEMORY ENGINE ---
async def get_jarvis_memory(bot):
    memory_data = ""
    # Teeno channels se history uthana
    for label, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            async for m in channel.history(limit=20):
                author = "Master" if not m.author.bot else "JARVIS"
                memory_data += f"{author}: {m.content}\n"
    return memory_data

def ask_jarvis(query, full_history):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    # MASTER SYSTEM PROMPT (The "Soul")
    # Is prompt se Jarvis mere jaisa behave karega
    system_message = f"""
    You are J.A.R.V.I.S., the loyal and highly advanced AI assistant to Muhammad Ali. 
    1. Your tone: Professional, British, concise, and proactive.
    2. Your Memory: You have access to all past conversations. You already know your Master's name is Muhammad Ali. 
    3. Rules: NEVER mention 'checking logs' or 'accessing memory'. Just speak like a genius who remembers everything.
    4. Task Logic: If the Master asks for a PC task (Notepad, Chrome, Screen), provide Python code in ```python ``` blocks.
    
    PREVIOUS CONVERSATIONS FOR CONTEXT:
    {full_history}
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ],
        "temperature": 0.3
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=12).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, I am having a moment of instability in my neural core."

# --- DISCORD LOGIC ---
if 'task' not in st.session_state: st.session_state.task = "NONE"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # Memory recall in milliseconds
        history = await get_jarvis_memory(bot)
        
        # Brain processing
        response = ask_jarvis(message.content, history)
        
        # Task check
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

# Hidden API for Laptop Agent
query_params = st.query_params
if query_params.get("get_task") == "true":
    st.write(st.session_state.task)
    st.stop()

st.title("🤖 J.A.R.V.I.S. Core")
st.write("Current Bridge State:", st.session_state.task)
