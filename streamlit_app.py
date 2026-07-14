import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

st.set_page_config(page_title="Jarvis Brain", page_icon="🤖")
st.title("🤖 Jarvis Senior Terminal")

TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

# Task storage for laptop
if 'task_bridge' not in st.session_state:
    st.session_state.task_bridge = "NONE"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

def ask_groq(query):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are Jarvis, a professional AI. If asked for a PC task, write Python code in ```python ``` blocks. Otherwise, answer briefly."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.2
        }
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"Brain Error: {str(e)}"

@bot.event
async def on_ready():
    print(f"Jarvis is logged in as {bot.user}")
    st.success(f"✅ Bot Online: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # Debug: See message in Streamlit logs
    print(f"Message received: {message.content}")

    # Fix for 'Screen' vs 'screen'
    content = message.content.lower().strip()

    if content == "screen":
        st.session_state.task_bridge = "SCREEN_CAPTURE"
        await message.channel.send("⚡ **Requesting visual from Laptop...**")
        return

    async with message.channel.typing():
        response = ask_groq(message.content)
        
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
            st.session_state.task_bridge = code
            verbal = response.split("```python")[0].strip()
            await message.channel.send(f"🛠️ **Executing:** {verbal}")
        else:
            await message.channel.send(response)

# --- WEB UI FOR LAPTOP ---
st.subheader("Current Order for Laptop:")
st.code(st.session_state.task_bridge)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    threading.Thread(target=run_bot, daemon=True).start()
