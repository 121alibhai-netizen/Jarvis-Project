import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, json
from intelligence import ask_jarvis_pro
from vault import get_json_memory, update_json_memory

# --- CONFIG FETCH ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("REPO_NAME")

# --- UI ---
st.title("🤖 J.A.R.V.I.S. Core OS")

if not TOKEN or not GROQ_KEY:
    st.error("❌ ERROR: Tokens missing in Streamlit Secrets!")
    st.stop()

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. READ: GitHub JSON Memory
        current_mem, sha = get_json_memory(REPO, GITHUB_TOKEN)
        
        # 2. THINK: Brain processing
        response = ask_jarvis_pro(message.content, current_mem, GROQ_KEY)
        
        # 3. WRITE: Silent Memory Sync
        if "###DATA_UPDATE###" in response:
            parts = response.split("###DATA_UPDATE###")
            answer = parts[0].strip()
            try:
                new_json = json.loads(parts[1].strip())
                new_json["history"] = new_json.get("history", []) + [{"u": message.content, "j": answer}]
                new_json["history"] = new_json["history"][-20:]
                update_json_memory(REPO, GITHUB_TOKEN, new_json)
            except: pass
            await message.channel.send(answer)
        else:
            await message.channel.send(response)

# --- SINGLETON RUNNER (Prevents Double Replies) ---
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Bot failed: {e}")

if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run, daemon=True).start()
    st.success("✅ Neural Soul Initialized.")
else:
    st.info("System is already running in background.")

if st.sidebar.button("Hard Reboot"):
    st.session_state.clear()
    st.rerun()
