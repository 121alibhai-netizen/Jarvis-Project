import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID"))
}

if 'task' not in st.session_state: st.session_state.task = "NONE"

# --- DEEP MEMORY RETRIEVAL (20 messages from each tier) ---
async def fetch_deep_memory(bot):
    memory_bank = "CRITICAL DATA & HISTORY:\n"
    for name, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            memory_bank += f"--- {name.upper()} CHANNEL ---\n"
            # Limit barha kar 20 kar di hai takay naam miss na ho
            async for m in channel.history(limit=20):
                sender = "User" if not m.author.bot else "Jarvis"
                memory_bank += f"{sender}: {m.content}\n"
    return memory_bank

def ask_senior_brain(query, context):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    # Ye prompt Jarvis ko majboor karega ke woh history check kare
    system_instruction = f"""
    You are JARVIS, a professional AI Agent. 
    IMPORTANT: Look into the MEMORY below to find the User's name and details. 
    If the name is mentioned anywhere in history, ALWAYS address him as 'Sir' or by his name.
    Never say you don't know the name if it is in the logs.

    MEMORY LOGS:
    {context}
    
    TASK RULES:
    1. PC Tasks (apps, screen) -> Python code in ```python ``` blocks.
    2. Info/Chat -> Professional, senior tone.
    3. To save permanently -> Start reply with 'PERMANENT_LOG:'.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": query}],
        "temperature": 0.1 # Accuracy ke liye low temp
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=12).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, connection to memory cores is unstable."

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. Fetch deep memory from all 3 channels
        context = await fetch_deep_memory(bot)
        
        # 2. Get AI Response
        response = ask_senior_brain(message.content, context)
        
        # 3. Memory Saving Logic
        if "PERMANENT_LOG:" in response:
            wf_ch = bot.get_channel(CH_IDS["workflow"])
            info = response.replace("PERMANENT_LOG:", "").strip()
            await wf_ch.send(f"📂 **MASTER DATA LOGGED:** {info}")
            await message.channel.send("✅ Information secured in Workflow memory, Sir.")
        
        # 4. Action/Chat logic
        elif "```python" in response:
            st.session_state.task = response.split("```python")[1].split("```")[0].strip()
            await message.channel.send(f"🛠️ {response.split('```python')[0]}")
        else:
            await message.channel.send(response)

# --- WEB UI & BOT RUNNER ---
st.title("🤖 Jarvis Senior Terminal")
st.subheader("Last Task Bridge:")
st.code(st.session_state.task)

if "started" not in st.session_state:
    st.session_state.started = True
    threading.Thread(target=lambda: bot.run(TOKEN), daemon=True).start()
