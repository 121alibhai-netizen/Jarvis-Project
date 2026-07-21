import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, json
from intelligence import ask_jarvis_pro
from vault import get_json_memory, update_json_memory

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("REPO_NAME")

# --- SINGLETON LOCK ---
if "bot_active" not in st.session_state:
    st.session_state.bot_active = False

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. READ
        current_mem, _ = get_json_memory(REPO, GITHUB_TOKEN)
        
        # 2. THINK
        response = ask_jarvis_pro(message.content, current_mem, GROQ_KEY)
        
        # 3. SYNC & REPLY
        if "###DATA_UPDATE###" in response:
            parts = response.split("###DATA_UPDATE###")
            answer = parts[0].strip()
            new_data = parts[1].strip()
            
            if new_data != "NONE":
                try:
                    updated_mem = json.loads(new_data)
                    # Update Chat Logs
                    updated_mem["chat_log"] = updated_mem.get("chat_log", []) + [f"U: {message.content}", f"J: {answer}"]
                    updated_mem["chat_log"] = updated_mem["chat_log"][-20:] # Keep it clean
                    update_json_memory(REPO, GITHUB_TOKEN, updated_mem)
                except: pass
            await message.channel.send(answer)
        else:
            await message.channel.send(response)

# --- BOOT ENGINE ---
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

st.title("🤖 J.A.R.V.I.S. Senior OS")

if not st.session_state.bot_active:
    st.session_state.bot_active = True
    threading.Thread(target=run, daemon=True).start()
    st.success("✅ J.A.R.V.I.S. Core Synchronized.")

if st.sidebar.button("System Hard Reset"):
    st.session_state.bot_active = False
    st.rerun()
