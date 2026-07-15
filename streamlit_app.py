import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
# IDs check kar len ke Streamlit Secrets mein sahi hain
TEMP_ID = int(os.environ.get("TEMP_CH_ID"))
BUILD_ID = int(os.environ.get("BUILD_CH_ID"))
WORKFLOW_ID = int(os.environ.get("WORKFLOW_CH_ID"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

# --- MEMORY RETRIEVAL ENGINE ---
async def fetch_memory_banks(current_channel):
    memory = "--- SYSTEM SHARED MEMORY ---\n"
    # Teeno channels se aakhri 10-10 baatein uthana
    channel_ids = [TEMP_ID, BUILD_ID, WORKFLOW_ID]
    
    for ch_id in channel_ids:
        channel = bot.get_channel(ch_id)
        if channel:
            memory += f"\n[{channel.name}]:\n"
            async for msg in channel.history(limit=10):
                if not msg.author.bot:
                    memory += f"User: {msg.content}\n"
                else:
                    # Bot ki apni purani baatein bhi yaad rakhna
                    memory += f"Jarvis: {msg.content}\n"
    return memory

# --- BRAIN WITH LONG-TERM REASONING ---
def ask_senior_brain(query, full_history):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    system_prompt = f"""
    You are JARVIS. You have access to three memory tiers.
    Before answering, look at the shared history provided below to remember names, preferences, and past tasks.
    
    {full_history}
    
    RULES:
    1. If you find the user's name in history, use it.
    2. If user says 'save' or 'remember', start response with 'MEM_SAVE:'.
    3. Be professional and senior level.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        "temperature": 0.2
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=15).json()
        return res['choices'][0]['message']['content']
    except:
        return "Sir, I am unable to access my memory banks at this moment."

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. Sare channels se yaaddasht ikatthi karna
        all_memories = await fetch_memory_banks(message.channel)
        
        # 2. Brain ko batana
        response = ask_senior_brain(message.content, all_memories)
        
        # 3. Agar kuch permanent save karna ho
        if "MEM_SAVE:" in response:
            wf_channel = bot.get_channel(WORKFLOW_ID)
            clean_info = response.replace("MEM_SAVE:", "").strip()
            await wf_channel.send(f"✅ **Permanent Memory Logged:** {clean_info}")
            await message.channel.send("Sir, I have updated my permanent workflow memory.")
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

st.title("🤖 Jarvis Unified Memory Brain")
st.write("Status: 24/7 Memory Sync Active")
