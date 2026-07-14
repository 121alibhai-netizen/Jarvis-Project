import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

# --- BRAIN CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

if 'task' not in st.session_state: st.session_state.task = "NONE"

# --- THE SECRET API FOR LAPTOP ---
# Agar URL ke aakhir mein ?get_task=true ho toh sirf code dikhao
query_params = st.query_params
if query_params.get("get_task") == "true":
    st.write(st.session_state.task)
    st.stop() # Baki page load mat karo

# --- AI LOGIC ---
def ask_brain(query):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "You are JARVIS. For tasks, use ```python ``` blocks."}, {"role": "user", "content": query}]}
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        return res['choices'][0]['message']['content']
    except: return "Connection error, Sir."

# --- DISCORD ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    msg = message.content.lower().strip()

    if msg == "screen":
        st.session_state.task = "SCREEN_CMD"
        await message.channel.send("📸 **Capturing screen for you, Sir...**")
        return

    async with message.channel.typing():
        res = ask_brain(message.content)
        if "```python" in res:
            st.session_state.task = res.split("```python")[1].split("```")[0].strip()
            await message.channel.send(f"🛠️ {res.split('```python')[0]}")
        else:
            await message.channel.send(res)

# --- UI ---
st.title("🤖 Jarvis Senior Terminal")
st.subheader("Current Order:")
st.code(st.session_state.task)

if st.button("Reset"):
    st.session_state.task = "NONE"
    st.rerun()

if "started" not in st.session_state:
    st.session_state.started = True
    threading.Thread(target=lambda: bot.run(TOKEN), daemon=True).start()
