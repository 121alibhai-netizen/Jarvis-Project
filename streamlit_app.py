import streamlit as st
import discord
from discord.ext import commands
import os
from threading import Thread
import asyncio

# 1. Streamlit UI
st.set_page_config(page_title="Jarvis Soul", page_icon="🤖")
st.title("🤖 Jarvis Cloud Soul")
st.write("Status: **ONLINE**")

# 2. Jarvis Discord Logic
TOKEN = os.environ.get("DISCORD_TOKEN")

# Setup Bot with "!" instead of "/"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    st.success(f"✅ Jarvis is ONLINE as {bot.user}")
    print(f"Jarvis Soul is online.")

# This part ensures he "hears" everything
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Debug: This will show in your Streamlit logs when you type something
    print(f"Message received: {message.content}")
    
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send("Hello Sir! I am your Cloud Soul. I am awake and ready!")

@bot.command()
async def status(ctx):
    await ctx.send("Cloud Systems: **Operational**\nLaptop Connection: **Awaiting Local Agent**")

# 3. Running the Bot
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error: {e}")

if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    Thread(target=run_bot).start()
    st.info("System: Booting Jarvis Soul...") 
