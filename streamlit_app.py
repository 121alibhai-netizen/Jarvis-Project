import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

# Memory Channel IDs
TEMP_ID = int(os.environ.get("TEMP_CH_ID"))
WORKFLOW_ID = int(os.environ.get("WORKFLOW_CH_ID"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

def ask_jarvis(query, memory):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    system_msg = f"You are JARVIS. Memory Tier: {memory}. If user says 'save', start reply with 'SAVE:'"
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": query}]
    }
    return requests.post(url, headers=headers, json=data).json()['choices'][0]['message']['content']

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # Brain Processing
    response = ask_jarvis(message.content, "Active")
    
    if response.startswith("SAVE:"):
        # Workflow memory mein bhej do
        wf_channel = bot.get_channel(WORKFLOW_ID)
        await wf_channel.send(f"📌 **New Memory Logged:**\n{response.replace('SAVE:', '')}")
        await message.channel.send("✅ Sir, information has been stored in Workflow Memory.")
    else:
        await message.channel.send(response)

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "started" not in st.session_state:
    st.session_state.started = True
    threading.Thread(target=run, daemon=True).start()

st.title("🤖 Jarvis Multi-Server Brain")
