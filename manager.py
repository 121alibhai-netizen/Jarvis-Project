import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading
# Hamare naye module se 'ask_groq' function import kar rahay hain
from intelligence import ask_groq
from vault import get_memories, auto_clean_temp
# IDs define karna
WF_ID = int(os.environ.get("WORKFLOW_CH_ID"))
TEMP_ID = int(os.environ.get("TEMP_CH_ID"))

st.set_page_config(page_title="Jarvis OS", page_icon="🤖")
st.title("🤖 J.A.R.V.I.S. Modular OS")

TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

# Discord Setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async with message.channel.typing():
        # 1. Fetch memory first
        context = await get_memories(bot, WF_ID, TEMP_ID)
        
        # 2. Get AI response with memory
        response = ask_groq(message.content, context, GROQ_KEY)
        
        # 3. Handle saving to Workflow channel
        if response.startswith("MEM_SAVE:"):
            wf_ch = bot.get_channel(WF_ID)
            await wf_ch.send(response.replace("MEM_SAVE:", "").strip())
            await message.channel.send("✅ Sir, that workflow has been saved to your Permanent Memory.")
        else:
            await message.channel.send(response)

@bot.event
async def on_ready():
    await auto_clean_temp(bot, TEMP_ID) # 7 days cleanup
    st.success("✅ Jarvis Soul & Vault Synced.")

# Background Bot Runner
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "bot_active" not in st.session_state:
    st.session_state.bot_active = True
    threading.Thread(target=run_bot, daemon=True).start()

st.success("✅ Jarvis Core is Online & Listening...")
