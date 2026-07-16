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

# Discord Setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    # Rozana ki safayi (Auto-clean)
    try:
        await auto_clean_temp(bot, TEMP_ID)
    except:
        pass
    st.success("✅ Jarvis Soul & Vault are synchronized.")

@bot.event
async def on_message(message):
    # Bot apne aap ko reply na kare
    if message.author == bot.user:
        return
    
    # Typing indicator aur response logic
    async with message.channel.typing():
        # 1. Vault se memory nikalna
        context = await get_memories(bot, WF_ID, TEMP_ID)
        
        # 2. Intelligence ko bhej kar faisla karwana
        response = ask_groq(message.content, context, GROQ_KEY)
        
        # 3. Agar kuch save karna hai permanent
        if response.startswith("MEM_SAVE:"):
            wf_ch = bot.get_channel(WF_ID)
            info = response.replace("MEM_SAVE:", "").strip()
            await wf_ch.send(info)
            await message.channel.send("✅ Sir, that workflow has been committed to permanent memory.")
        else:
            await message.channel.send(response)

# Background Bot Runner
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "bot_active" not in st.session_state:
    st.session_state.bot_active = True
    threading.Thread(target=run_bot, daemon=True).start()

st.title("🤖 Jarvis Modular OS")
st.write("System Status: **100% Operational**")
