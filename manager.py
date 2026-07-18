import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, json
from intelligence import ask_jarvis_architect
from vault import get_json_memory, update_json_memory

# --- CONFIG ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("REPO_NAME")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    async with message.channel.typing():
        # 1. READ: GitHub se memory lana
        current_mem, sha = get_json_memory(REPO, GITHUB_TOKEN)
        
        # 2. THINK: Brain se jawab mangna
        response = ask_jarvis_architect(message.content, current_mem, GROQ_KEY)
        
        # 3. WRITE: Agar naya data save karna ho
        if "###JSON_UPDATE###" in response:
            parts = response.split("###JSON_UPDATE###")
            reply_text = parts[0].strip()
            try:
                new_facts = json.loads(parts[1].strip())
                current_mem["facts"].update(new_facts) # Memory update
                update_json_memory(REPO, GITHUB_TOKEN, current_mem, sha)
                await message.channel.send(f"{reply_text}\n\n✅ *Vault Updated*")
            except:
                await message.channel.send(parts[0])
        else:
            await message.channel.send(response)

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run, daemon=True).start()

st.title("🤖 J.A.R.V.I.S. Modular Brain")
st.write("Memory Mode: **GitHub JSON Vault**")
