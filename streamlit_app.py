import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- MEMORY RETRIEVAL ---
async def get_history(channel):
    logs = ""
    async for msg in channel.history(limit=10):
        name = "User" if msg.author != bot.user else "Jarvis"
        logs += f"{name}: {msg.content}\n"
    return logs

# --- BRAIN ---
def ask_brain(query, history):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    messages = [
        {"role": "system", "content": f"You are JARVIS. Use the following history to remember the user: \n{history}"},
        {"role": "user", "content": query}
    ]
    res = requests.post(url, headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": messages}).json()
    return res['choices'][0]['message']['content']

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        history = await get_history(message.channel)
        response = ask_brain(message.content, history)
        await message.channel.send(response)

# --- RUNNER ---
if "started" not in st.session_state:
    st.session_state.started = True
    threading.Thread(target=lambda: bot.run(TOKEN), daemon=True).start()

st.title("🤖 Jarvis Senior Terminal")
