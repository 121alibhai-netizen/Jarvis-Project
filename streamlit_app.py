import streamlit as st
import discord
from discord.ext import commands
import os
from threading import Thread
import asyncio

# 1. Streamlit UI (This keeps the cloud happy)
st.set_page_config(page_title="Jarvis Soul", page_icon="🤖")
st.title("🤖 Jarvis Cloud Soul")
st.write("Status: **ONLINE**")
st.info("Jarvis is watching your commands on Discord 24/7.")

# 2. Jarvis Discord Logic
TOKEN = os.environ.get("DISCORD_TOKEN")

# Setup Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    st.success(f"Connected to Discord as: {bot.user}")
    print(f"Jarvis Soul is online.")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello Sir! I am your Cloud Soul. I am awake and ready, even if your laptop is off.")

@bot.command()
async def status(ctx):
    await ctx.send("Cloud Systems: **Operational**\nLaptop Connection: **Awaiting Local Agent**")

# 3. Running the Bot in the background
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    Thread(target=run_bot).start()
