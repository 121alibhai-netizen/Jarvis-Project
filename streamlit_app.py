import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

st.title("🤖 Jarvis Senior Terminal")

TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

if 'task_bridge' not in st.session_state: st.session_state.task_bridge = "NONE"

def ask_groq(query):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are JARVIS. For PC tasks, use ```python ``` blocks with pyautogui. For info, be brief."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.1
        }
        res = requests.post(url, headers=headers, json=data).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, connection error."

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    msg = message.content.lower().strip()
    
    # Direct Screenshot Command
    if msg == "screen" or msg == "screenshot":
        st.session_state.task_bridge = "SCREEN_CMD"
        await message.channel.send("📸 **Capturing laptop screen for you, Sir...**")
        return

    async with message.channel.typing():
        response = ask_groq(message.content)
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
            st.session_state.task_bridge = code
            await message.channel.send(f"🛠️ {response.split('```python')[0]}")
        else:
            await message.channel.send(response)

st.code(st.session_state.task_bridge)

# Double reply fix: check if bot is already in memory
if "bot" not in st.session_state:
    st.session_state.bot = True
    threading.Thread(target=lambda: bot.run(TOKEN), daemon=True).start()
