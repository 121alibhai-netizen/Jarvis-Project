import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

# --- SYSTEM CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID"))
}

# Task Bridge for Laptop
if 'task_bridge' not in st.session_state: st.session_state.task_bridge = "NONE"

# --- THE REAL MEMORY ENGINE (Deep Retrieval) ---
async def get_deep_memory(bot):
    # Jarvis teeno tier channels se data khinch kar layega
    memory_context = "--- START OF ACCESSED MEMORY BANKS ---\n"
    for label, cid in CH_IDS.items():
        channel = bot.get_channel(cid)
        if channel:
            memory_context += f"\n[DATABASE: {label.upper()}]\n"
            # Pechli 30 baatein har channel se (Total 90 messages context)
            async for m in channel.history(limit=30):
                author = "USER" if not m.author.bot else "JARVIS"
                memory_context += f"{author}: {m.content}\n"
    memory_context += "\n--- END OF MEMORY BANKS ---"
    return memory_context

# --- BRAIN: AGENTIC REASONING ---
def ask_jarvis_pro(query, full_memory):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    # Is prompt mein koi naam nahi hai. Jarvis memory se dhoondega.
    system_instruction = f"""
    You are J.A.R.V.I.S., a high-intelligence autonomous AI system.
    Your knowledge of the user, their name, and their preferences is stored in the MEMORY below.
    
    MEMORY LOGS:
    {full_memory}
    
    OPERATIONAL RULES:
    1. Identify the user using the provided MEMORY. If the name is there, use it.
    2. Be concise, professional, and loyal. Do not explain your internal systems.
    3. If a task requires PC control (open apps, files, browser), write Python code in ```python ``` blocks.
    4. Never say 'I am an AI' or 'As per logs'. Just speak naturally.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": query}
        ],
        "temperature": 0.1 # Sabse zyada accuracy ke liye
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=15).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, my neural link is experiencing a momentary lapse."

# --- DISCORD SOUL ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # Jarvis pehle apne dimaag ki files (History) kholta hai
        memory_banks = await get_deep_memory(bot)
        
        # Phir jawab soochta hai
        response = ask_jarvis_pro(message.content, memory_banks)
        
        # Code extraction for laptop
        if "```python" in response:
            st.session_state.task_bridge = response.split("```python")[1].split("```")[0].strip()
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
    st.write(st.session_state.task_bridge)
    st.stop()

st.title("🤖 J.A.R.V.I.S. Core Terminal")
st.write("System: **100% OPERATIONAL**")
