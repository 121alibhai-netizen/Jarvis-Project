import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading
from intelligence import ask_groq
from vault import get_permanent_metadata, get_recent_chat

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
WF_ID = int(os.environ.get("WORKFLOW_CH_ID"))
TEMP_ID = int(os.environ.get("TEMP_CH_ID"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. READ: Cloud se structured memory nikalna
        metadata = await get_permanent_metadata(bot, WF_ID)
        recent_chat = await get_recent_chat(bot, TEMP_ID)
        full_context = metadata + recent_chat
        
        # 2. THINK: Brain ko history bhenjna
        response = ask_groq(message.content, full_context, GROQ_KEY)
        
        # 3. SAVE: Agar info save karni ho
        if response.startswith("UPDATE_MEMORY:"):
            info_to_save = response.replace("UPDATE_MEMORY:", "").strip()
            wf_ch = bot.get_channel(WF_ID)
            await wf_ch.send(f"```python\n{info_to_save}\n```")
            await message.channel.send(f"✅ Master, I have updated your identity files with: `{info_to_save}`")
        else:
            await message.channel.send(response)

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "active" not in st.session_state:
    st.session_state.active = True
    threading.Thread(target=run, daemon=True).start()

st.title("🤖 J.A.R.V.I.S. Modular OS")
st.write("Memory Mode: **Metadata-Structured**")
