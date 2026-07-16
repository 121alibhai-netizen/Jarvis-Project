import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, requests, base64

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
CH_IDS = {
    "temp": int(os.environ.get("TEMP_CH_ID")),
    "workflow": int(os.environ.get("WORKFLOW_CH_ID")),
    "build": int(os.environ.get("BUILD_CH_ID"))
}

if 'live_vision' not in st.session_state: st.session_state.live_vision = None
if 'task' not in st.session_state: st.session_state.task = "NONE"

# --- THE VISION RECEIVER (Improved) ---
params = st.query_params
if params.get("stream") == "true":
    img_data = st.context.headers.get("x-image-data")
    if img_data:
        st.session_state.live_vision = img_data
        st.write("EYES_UPDATED")
        st.stop()

if params.get("get_task") == "true":
    st.write(st.session_state.task)
    st.stop()

# --- BRAIN WITH LITERAL VISION ---
def ask_jarvis_pro(query, history, img_b64):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    
    model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
    
    # SAKHT SYSTEM PROMPT (Anti-Boxing/Anti-Hallucination)
    system_prompt = f"""
    You are J.A.R.V.I.S., a high-tech AI. 
    CURRENT MASTER: Muhammad Ali.
    RULES:
    1. If an image is provided, describe EXACTLY what you see. 
    2. DO NOT assume boxing or anything else based on the Master's name.
    3. If you see a website, name it. If you see code, describe the code.
    4. Be literal, technical, and professional. 
    5. Access Memory: {history}
    """

    messages = [{"role": "system", "content": system_prompt}]
    user_content = [{"type": "text", "text": query}]
    
    if img_b64:
        user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
    
    messages.append({"role": "user", "content": user_content})

    try:
        res = requests.post(url, headers=headers, json={"model": model, "messages": messages, "temperature": 0.0}).json()
        return res['choices'][0]['message']['content']
    except: return "Sir, the visual uplink is failing."

# --- DISCORD LOGIC ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    async with message.channel.typing():
        # Memory recall
        history = ""
        async for m in message.channel.history(limit=5):
            history += f"{m.author.name}: {m.content}\n"
            
        response = ask_jarvis_pro(message.content, history, st.session_state.live_vision)
        
        if "```python" in response:
            st.session_state.task = response.split("```python")[1].split("```")[0].strip()
            await message.channel.send(response.split("```python")[0].strip())
        else:
            await message.channel.send(response)

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run, daemon=True).start()

# --- VISUAL FEED (UI) ---
st.title("🤖 J.A.R.V.I.S. Visual Center")
if st.session_state.live_vision:
    st.image(base64.b64decode(st.session_state.live_vision), caption="LIVE FEED")
    if st.button("Clear Cache"): st.session_state.live_vision = None; st.rerun()
else:
    st.warning("Awaiting video feed from laptop...")
