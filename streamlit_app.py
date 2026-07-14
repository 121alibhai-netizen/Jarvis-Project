import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests

# --- UI Setup ---
st.set_page_config(page_title="Jarvis Brain", page_icon="🤖")
st.title("🤖 Jarvis 24/7 Online Soul")

# --- Secrets Check ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

if not TOKEN or not GROQ_KEY:
    st.error("Secrets missing! Please add DISCORD_TOKEN and GROQ_API_KEY.")
    st.stop()

# --- Jarvis Brain Logic ---
def ask_groq(query):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are JARVIS, a highly advanced 24/7 AI. Be professional, smart, and concise like me."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.5
        }
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"Sir, I am facing a connection issue with my central core: {e}"

# --- Discord Bot Setup ---
if "bot_instance" not in st.session_state:
    st.session_state.bot_instance = None

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    print(f"Jarvis Soul is online as {bot.user}")
    st.success(f"✅ Soul is Active: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # Simple reply logic (No double replies)
    async with message.channel.typing():
        response = ask_groq(message.content)
        await message.channel.send(response)

# --- Background Runner ---
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

# Is block ki wajah se 4x replies nahi aayengi
if "started" not in st.session_state:
    st.session_state.started = True
    threading.Thread(target=run_bot, daemon=True).start()
    st.info("System Booting... Please wait.")

st.sidebar.write("System Status: 🟢 24/7 Awake")
st.sidebar.info("This is the Cloud Brain. It works even if your laptop is OFF.")
