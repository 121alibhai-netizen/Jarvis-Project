import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, datetime

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
TEMP_ID = int(os.environ.get("TEMP_CH_ID"))
BUILD_ID = int(os.environ.get("BUILD_CH_ID"))
WORKFLOW_ID = int(os.environ.get("WORKFLOW_CH_ID"))

if 'task' not in st.session_state: st.session_state.task = "NONE"

# --- TASK API FOR LAPTOP ---
query_params = st.query_params
if query_params.get("get_task") == "true":
    st.write(st.session_state.task)
    st.stop()

# --- AUTO-CLEAN LOGIC (7 Days) ---
async def clean_old_memory(bot):
    now = datetime.datetime.utcnow()
    for ch_id in [TEMP_ID, BUILD_ID]:
        channel = bot.get_channel(ch_id)
        if channel:
            # 7 din purane messages delete karna
            deleted = await channel.purge(before=now - datetime.timedelta(days=7))
            if len(deleted) > 0:
                print(f"Cleaned {len(deleted)} old logs from {channel.name}")

# --- BRAIN WITH TRIPLE MEMORY ---
async def get_memory_context(bot):
    context = ""
    for ch_id in [TEMP_ID, BUILD_ID, WORKFLOW_ID]:
        ch = bot.get_channel(ch_id)
        if ch:
            context += f"\n[{ch.name.upper()}]:\n"
            async for m in ch.history(limit=10):
                context += f"{'User' if not m.author.bot else 'Jarvis'}: {m.content}\n"
    return context

def ask_brain(query, context):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    prompt = f"You are JARVIS. Use this memory: {context}. Rules: 1. PC tasks in ```python ``` blocks. 2. If saving info, start with 'PERMANENT_LOG:'"
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": query}]}
    res = requests.post(url, headers=headers, json=data).json()
    return res['choices'][0]['message']['content']

# --- DISCORD SOUL ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    await clean_old_memory(bot) # Start hotay hi safayi
    st.success(f"Jarvis Soul Active: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        context = await get_memory_context(bot)
        response = ask_brain(message.content, context)

        # 1. Permanent Memory Routing
        if "PERMANENT_LOG:" in response:
            wf_ch = bot.get_channel(WORKFLOW_ID)
            await wf_ch.send(f"📂 **LOGGED:** {response.replace('PERMANENT_LOG:', '').strip()}")
            await message.channel.send("✅ Sir, that info is now permanent in Workflow Memory.")
        
        # 2. Action Routing
        elif "```python" in response:
            st.session_state.task = response.split("```python")[1].split("```")[0].strip()
            await message.channel.send(f"🛠️ {response.split('```python')[0]}")
        
        else:
            await message.channel.send(response)

# --- RUNNER ---
if "started" not in st.session_state:
    st.session_state.started = True
    threading.Thread(target=lambda: bot.run(TOKEN), daemon=True).start()

st.title("🤖 Jarvis Senior Terminal")
st.code(st.session_state.task)
