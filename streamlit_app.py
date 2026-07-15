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

# Instance Lock to prevent double replies
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False

# --- THE MEMORY SCANNER ---
async def gather_all_memories(bot):
    full_context = "--- JARVIS MULTI-TIER MEMORY ---\n"
    for name, ch_id in CH_IDS.items():
        channel = bot.get_channel(ch_id)
        if channel:
            full_context += f"\n[{name.upper()} CHANNEL]:\n"
            async for msg in channel.history(limit=10): # Last 10 msgs from each
                sender = "User" if not msg.author.bot else "Jarvis"
                full_context += f"{sender}: {msg.content}\n"
    return full_context

# --- SENIOR BRAIN ---
def ask_jarvis(query, memory):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    system_msg = f"""
    You are JARVIS. Senior Architect.
    MEMORY ACCESS:
    {memory}
    
    RULES:
    1. Check all memory tiers before answering. 
    2. If user says 'save' or 'remember', start response with 'MEM_SAVE:'.
    3. If user says 'forget' or 'delete', start with 'MEM_DELETE:'.
    4. Use professional language.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": query}],
        "temperature": 0.2
    }
    try:
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, memory sync failed."

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. Scrape all 3 channels for memory
        memory = await gather_all_memories(bot)
        
        # 2. Get smart response
        response = ask_jarvis(message.content, memory)
        
        # 3. Handle Memory Management
        if response.startswith("MEM_SAVE:"):
            wf_ch = bot.get_channel(CH_IDS["workflow"])
            clean_info = response.replace("MEM_SAVE:", "").strip()
            await wf_ch.send(f"📂 **PERMANENT LOG:** {clean_info}")
            await message.channel.send("✅ Sir, that has been moved to your Permanent Workflow memory.")
        
        elif response.startswith("MEM_DELETE:"):
            await message.channel.send("⚠️ Sir, please delete the specific message in the memory channel manually for safety.")
        
        else:
            await message.channel.send(response)

# --- RUNNER ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

st.title("🤖 Jarvis Senior Terminal")
if not st.session_state.bot_running:
    st.session_state.bot_running = True
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("✅ Unified Memory Brain Active.")

if st.sidebar.button("Hard Reset"):
    st.session_state.bot_running = False
    st.rerun()
