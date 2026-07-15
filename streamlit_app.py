import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

# --- SENIOR SYSTEM CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
# Memory Channel IDs
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID"))
}

# Task Bridge (Laptop ke liye rasta)
if 'task' not in st.session_state: st.session_state.task = "NONE"
if 'bot_running' not in st.session_state: st.session_state.bot_running = False

# --- ARCHITECT REASONING ENGINE (MEMORY) ---
async def gather_memory(bot):
    all_context = "SYSTEM CONTEXT:\n"
    for name, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            all_context += f"--- {name.upper()} MEMORY ---\n"
            async for m in channel.history(limit=10):
                sender = "Master" if not m.author.bot else "Jarvis"
                all_context += f"{sender}: {m.content}\n"
    return all_context

def ask_brain(query, context):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    system_prompt = f"""
    You are JARVIS. Senior AI Agent. 
    CURRENT MEMORY:
    {context}
    
    LOGIC RULES:
    1. For laptop tasks, write code in ```python ``` blocks using pyautogui.
    2. For info/chat, respond briefly but professionally.
    3. If user says 'save', start reply with 'SAVING:'.
    4. Always check memory for the user's name/details.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
        "temperature": 0.2
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, my neural link is flickering."

# --- DISCORD SOUL ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    msg_clean = message.content.lower().strip()

    # Feature 1: ALWAYS-ON REPLIES (Cloud Brain)
    async with message.channel.typing():
        # Feature 2: MEMORY RECALL (Fetch from 3 channels)
        context = await gather_memory(bot)
        response = ask_brain(message.content, context)
        
        # Feature 3: SCREEN CAPTURE (Direct Trigger)
        if msg_clean == "screen" or msg_clean == "screenshot":
            st.session_state.task = "SCREEN_CMD"
            await message.channel.send("📸 **Capturing laptop screen, Sir...**")
            return

        # Feature 4: MEMORY SAVING (Auto-move to Workflow)
        if response.startswith("SAVING:"):
            wf_ch = bot.get_channel(CH_IDS["workflow"])
            info = response.replace("SAVING:", "").strip()
            await wf_ch.send(f"📂 **LOGGED:** {info}")
            await message.channel.send("✅ System: Logged to Permanent Workflow.")
            return

        # Check if response has code for Laptop
        if "```python" in response:
            st.session_state.task = response.split("```python")[1].split("```")[0].strip()
            await message.channel.send(f"🛠️ {response.split('```python')[0]}")
        else:
            await message.channel.send(response)

# --- WEB UI & RUNNER ---
st.title("🤖 Jarvis Senior Master")
st.subheader("Task Bridge Output:")
st.code(st.session_state.task) # Laptop parses this block

if not st.session_state.bot_running:
    st.session_state.bot_running = True
    threading.Thread(target=lambda: bot.run(TOKEN), daemon=True).start()

if st.sidebar.button("Hard Reset"):
    st.session_state.task = "NONE"; st.rerun()
