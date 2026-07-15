import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, datetime

st.set_page_config(page_title="Jarvis Master Brain", page_icon="🤖")

# --- CONFIG (Get IDs from Secrets) ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
TEMP_CH_ID = int(os.environ.get("TEMP_CH_ID"))
BUILD_CH_ID = int(os.environ.get("BUILD_CH_ID"))
WORKFLOW_CH_ID = int(os.environ.get("WORKFLOW_CH_ID"))

if 'task' not in st.session_state: st.session_state.task = "NONE"

# --- THE TRIPLE MEMORY ENGINE ---
async def get_unified_memory(bot):
    memory_text = "--- SYSTEM MEMORY START ---\n"
    channels = [
        {"id": TEMP_CH_ID, "name": "Temporary"},
        {"id": BUILD_CH_ID, "name": "Build/Test"},
        {"id": WORKFLOW_CH_ID, "name": "Permanent Workflow"}
    ]
    
    for ch_info in channels:
        channel = bot.get_channel(ch_info['id'])
        if channel:
            memory_text += f"\n[{ch_info['name']} Memory]:\n"
            async for msg in channel.history(limit=10): # Last 10 msgs from each
                if msg.content and not msg.author.bot:
                    memory_text += f"- {msg.author.name}: {msg.content}\n"
    
    memory_text += "\n--- SYSTEM MEMORY END ---"
    return memory_text

def ask_senior_brain(query, full_memory):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    system_instruction = f"""
    You are JARVIS, a Senior AI Architect. You have 3 memory tiers:
    1. Temporary: Daily casual talk.
    2. Build: Development/Testing info.
    3. Workflow: PERMANENT instructions and personal info.
    
    CONTEXT DATA:
    {full_memory}
    
    RULES:
    - If the user says 'save this' or 'remember this', generate a response starting with 'MEM_SAVE:'.
    - If user says 'delete' or 'forget', generate a response starting with 'MEM_DELETE:'.
    - For PC tasks, use ```python ``` blocks.
    """
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": query}
        ],
        "temperature": 0.2
    }
    res = requests.post(url, headers=headers, json=data).json()
    return res['choices'][0]['message']['content']

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # 1. Memory Fetching
    memory_context = await get_unified_memory(bot)
    
    async with message.channel.typing():
        response = ask_senior_brain(message.content, memory_context)
        
        # 2. Memory Management Logic
        if response.startswith("MEM_SAVE:"):
            target_ch = bot.get_channel(WORKFLOW_CH_ID)
            clean_info = response.replace("MEM_SAVE:", "").strip()
            await target_ch.send(f"📌 **LOGGED TO WORKFLOW:**\n{clean_info}")
            await message.channel.send("✅ Sir, I have permanently moved that information to your Workflow Memory.")
            return

        # 3. Action Logic (Laptop)
        if "```python" in response:
            st.session_state.task = response.split("```python")[1].split("```")[0].strip()
            await message.channel.send(f"🛠️ **Executing Order:** {response.split('```python')[0]}")
        else:
            await message.channel.send(response)

# --- STREAMLIT UI ---
st.title("🤖 Jarvis Master Terminal")
st.subheader("Cloud-to-Laptop Bridge")
st.code(st.session_state.task)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run_bot, daemon=True).start()
