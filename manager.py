import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, json, re
from intelligence import ask_jarvis_pro
from vault import get_json_memory, update_json_memory

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("REPO_NAME")

# --- SINGLETON LOCK (Stops Double Replies) ---
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. Fetch latest memory from GitHub
        current_mem, _ = get_json_memory(REPO, GITHUB_TOKEN)
        
        # 2. Get AI Response
        response = ask_jarvis_pro(message.content, current_mem, GROQ_KEY)
        
        # 3. Silent Memory Management
        if "###DATA_UPDATE###" in response:
            parts = response.split("###DATA_UPDATE###")
            answer = parts[0].strip()
            
            # Extract and update JSON secretly
            try:
                new_json_str = parts[1].strip()
                if new_json_str != "NONE":
                    updated_mem = json.loads(new_json_str)
                    # Add current chat to history list
                    updated_mem["history"] = updated_mem.get("history", []) + [{"u": message.content, "j": answer}]
                    # Keep history manageable (last 20 entries)
                    updated_mem["history"] = updated_mem["history"][-20:]
                    update_json_memory(REPO, GITHUB_TOKEN, updated_mem)
            except: pass
            
            await message.channel.send(answer)
        else:
            await message.channel.send(response)

# --- THE BOOTLOADER ---
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

st.title("🤖 J.A.R.V.I.S. Core OS")

if not st.session_state.bot_running:
    st.session_state.bot_running = True
    threading.Thread(target=run, daemon=True).start()
    st.success("✅ Neural Soul Initialized.")

if st.sidebar.button("System Reboot (Hard Reset)"):
    st.session_state.bot_running = False
    st.rerun()
