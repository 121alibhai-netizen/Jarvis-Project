import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, time

st.set_page_config(page_title="Jarvis Senior Terminal", page_icon="🤖")
st.title("🤖 Jarvis Senior Terminal")

# --- SECRETS ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

# Task Bridge
if 'task_bridge' not in st.session_state: st.session_state.task_bridge = "NONE"

# --- BRAIN LOGIC ---
def ask_senior_brain(query):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are JARVIS, a Senior AI. If user wants a task (open apps, type), write Python code in ```python ``` blocks. Use pyautogui and time.sleep(2). If just talking, be brief."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.1
        }
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, connection to brain lost."

# --- DISCORD ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        response = ask_senior_brain(message.content)
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
            st.session_state.task_bridge = code
            await message.channel.send(f"⚡ **Tasking Body:** {response.split('```python')[0]}")
        else:
            await message.channel.send(response)

# --- WEB INTERFACE ---
st.subheader("Current Order for Laptop:")
st.code(st.session_state.task_bridge)

if st.button("Test Connection"):
    st.session_state.task_bridge = "import pyautogui; pyautogui.alert('Jarvis Body is Connected!')"
    st.rerun()

if st.button("Clear Tasks"):
    st.session_state.task_bridge = "NONE"
    st.rerun()

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run_bot, daemon=True).start()
