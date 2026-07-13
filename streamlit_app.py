import streamlit as st
import discord
from discord.ext import commands
import os
from threading import Thread
import asyncio

st.set_page_config(page_title="Jarvis Soul", page_icon="🤖")
st.title("🤖 Jarvis Cloud Soul")

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    st.balloons()
    st.success(f"✅ Jarvis Soul is ONLINE as {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello Sir! I am your Cloud Soul. I am awake and ready!")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    Thread(target=run_bot).start()
    st.info("System: Booting Jarvis Soul...")
