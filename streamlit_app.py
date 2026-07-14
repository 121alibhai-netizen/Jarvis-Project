import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, time

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

st.title("🤖 Jarvis Master Control")

# Ye system check karega ke laptop online hai ya nahi
if 'last_seen' not in st.session_state: st.session_state.last_seen = 0
if 'task' not in st.session_state: st.session_state.task = "NONE"

def ask_groq(query):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are JARVIS. If the user wants a PC task (apps, typing), reply with text then Python code in ```python ``` blocks. If it's a question, just answer. Be senior and professional."},
            {"role": "user", "content": query}
        ],
        "temperature": 0.1
    }
    return requests.post(url, headers=headers, json=data).json()['choices'][0]['message']['content']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # Laptop status check
    is_laptop_alive = (time.time() - st.session_state.last_seen) < 15
    
    async with message.channel.typing():
        response = ask_groq(message.content)
        
        if "```python" in response:
            if is_laptop_alive:
                code = response.split("```python")[1].split("```")[0].strip()
                st.session_state.task = code
                await message.channel.send(f"✅ **Laptop Online.** Executing task, Sir...")
            else:
                await message.channel.send(f"⚠️ **Laptop Offline.** Sir, I can't move the mouse, but here is the information: \n{response.split('```python')[0]}")
        else:
            await message.channel.send(response)

# --- LAPTOP BRIDGE ---
# Laptop yahan se orders uthayega
st.sidebar.write("System Status:")
if (time.time() - st.session_state.last_seen) < 15:
    st.sidebar.success("💻 Laptop: CONNECTED")
else:
    st.sidebar.error("💻 Laptop: DISCONNECTED")

# Hidden route for laptop to ping
task_box = st.empty()
task_box.code(st.session_state.task)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run_bot, daemon=True).start()
