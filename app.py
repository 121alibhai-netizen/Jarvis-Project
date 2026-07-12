import streamlit as st
import discord
from discord.ext import commands
import os
from threading import Thread
import asyncio

st.title("Jarvis Soul Control Panel")
st.write("Status: Running 24/7 Cloud Brain")

# Discord Bot Logic
TOKEN = os.environ.get("DISCORD_TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    st.success(f"Jarvis Soul connected as {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("Sir, I am alive on Streamlit Cloud!")

# Function to run the bot in a background thread
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "bot_running" not in st.session_state:
    st.session_state.bot_running = True
    Thread(target=run_bot).start()
