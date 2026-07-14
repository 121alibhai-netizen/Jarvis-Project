import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, re

# --- MASTER CONFIG ---
TOKEN = os.environ.get("MTUyNTcyMDIwMDYxNDUxNDcyOA.GigZFG.VuSKnOZCLSe29AY4kKKrdFOKNBKwpZRefN4TZQ")
GROQ_KEY = os.environ.get("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")

# --- SENIOR ARCHITECT PROMPT ---
SENIOR_PROMPT = """
You are JARVIS, a Senior System Architect AI. 
Tone: Professional, proactive, concise. 
Capabilities: You control a Windows 10 laptop via a Remote Agent.

LOGIC RULES:
1. IDENTIFY: Is this a 'Question' or a 'Task'?
2. IF QUESTION: Answer with senior-level accuracy. No yapping.
3. IF TASK: Plan the steps. Write robust Python code using:
   - pyautogui (for UI control)
   - os / subprocess (for system/files)
   - webbrowser (for web)
4. STANDARDS: 
   - Always include 'time.sleep()' between actions.
   - Use 'pyautogui.FAILSAFE = True'.
   - If opening an app, use 'os.startfile()' for speed if possible.
FORMAT: Verbal response first, then code block if needed.
"""

if 'tasks' not in st.session_state: st.session_state.tasks = []

# --- THE BRAIN ---
def ask_senior_brain(query):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SENIOR_PROMPT},
                {"role": "user", "content": query}
            ],
            "temperature": 0.1 # High precision
        }
        res = requests.post(url, headers=headers, json=data, timeout=10).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, my cognitive processors are lagging. Please check the link."

# --- DISCORD SOUL ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        full_res = ask_senior_brain(message.content)
        
        # Extract code to send to Laptop
        if "```python" in full_res:
            code = full_res.split("```python")[1].split("```")[0].strip()
            st.session_state.tasks.append(code)
            verbal = full_res.split("```python")[0].strip()
            await message.channel.send(f"⚡ **Task Routed:** {verbal}")
        else:
            await message.channel.send(full_res)

# --- TASK API (For Laptop to read) ---
st.title("🤖 Jarvis Senior Terminal")
if st.session_state.tasks:
    st.warning(f"Pending Tasks: {len(st.session_state.tasks)}")
    if st.button("Manual Clear"): st.session_state.tasks = []
    # This hidden text is what the laptop reads
    st.text_area("Current Queue", value=st.session_state.tasks[-1] if st.session_state.tasks else "NONE", height=100)

def start_soul():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=start_soul, daemon=True).start()
