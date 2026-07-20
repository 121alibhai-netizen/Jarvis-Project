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

if "bot_active" not in st.session_state:
    st.session_state.bot_active = False

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. READ: Latest Memory from GitHub
        current_mem, _ = get_json_memory(REPO, GITHUB_TOKEN)
        
        # 2. THINK: Brain processes query + memory
        response = ask_jarvis_pro(message.content, current_mem, GROQ_KEY)
        
        # 3. SYNC: Update GitHub if needed
        if "###DATA_UPDATE###" in response:
            parts = response.split("###DATA_UPDATE###")
            answer = parts[0].strip()
            new_json_str = parts[1].strip()
            
            if new_json_str != "NONE":
                try:
                    updated_mem = json.loads(new_json_str)
                    # Add current chat to log (keeping only last 15)
                    updated_mem["chat_log"] = updated_mem.get("chat_log", []) + [f"U: {message.content}", f"J: {answer}"]
                    updated_mem["chat_log"] = updated_mem["chat_log"][-30:] # Limit history
                    
                    # Push to GitHub
                    update_json_memory(REPO, GITHUB_TOKEN, updated_mem)
                except: pass
            
            await message.channel.send(answer)
        else:
            await message.channel.send(response)

# --- BOOT ENGINE ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

st.title("🤖 J.A.R.V.I.S. Senior OS")

if not st.session_state.bot_active:
    st.session_state.bot_active = True
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("✅ Neural Bridge Synchronized.")

if st.sidebar.button("Hard System Reboot"):
    st.session_state.clear()
    st.rerun()
