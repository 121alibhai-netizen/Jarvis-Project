import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading
from intelligence import ask_groq
from vault import get_memories, auto_clean_temp

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
WF_ID = int(os.environ.get("WORKFLOW_CH_ID"))
TEMP_ID = int(os.environ.get("TEMP_CH_ID"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    await auto_clean_temp(bot, TEMP_ID)
    st.success("✅ Jarvis Soul & 2-Tier Vault Synced.")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        context = await get_memories(bot, WF_ID, TEMP_ID)
        response = ask_groq(message.content, context, GROQ_KEY)
        
        if response.startswith("MEM_SAVE:"):
            wf_ch = bot.get_channel(WF_ID)
            await wf_ch.send(f"📂 **MASTER LOG:** {response.replace('MEM_SAVE:', '').strip()}")
            await message.channel.send("✅ Information saved to Workflow Memory, Sir.")
        else:
            await message.channel.send(response)

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "active" not in st.session_state:
    st.session_state.active = True
    threading.Thread(target=run, daemon=True).start()

st.title("🤖 Modular Jarvis: 2-Tier Memory")
