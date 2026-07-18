import streamlit as st
import discord
from discord.ext import commands
import os, asyncio, threading, json, re
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
        # 1. READ
        current_mem, sha = get_json_memory(REPO, GITHUB_TOKEN)
        
        # 2. THINK
        response = ask_jarvis_architect(message.content, current_mem, GROQ_KEY)
        
        # 3. WRITE & CLEANING
        if "###JSON_UPDATE###" in response:
            parts = response.split("###JSON_UPDATE###")
            reply_text = parts[0][:1900] # Discord limit safety
            
            try:
                # Cleaning the JSON string (removing markdown ``` json etc)
                raw_json = re.sub(r'```json|```', '', parts[1]).strip()
                new_facts = json.loads(raw_json)
                
                # Update facts in local memory
                current_mem["facts"].update(new_facts)
                
                # Push to GitHub
                status = update_json_memory(REPO, GITHUB_TOKEN, current_mem, sha)
                if status == 200 or status == 201:
                    await message.channel.send(f"{reply_text}\n\n✅ *Memory Core Updated Successfully*")
                else:
                    await message.channel.send(f"{reply_text}\n\n⚠️ *Memory Write Failed (Status {status})*")
            except Exception as e:
                print(f"DEBUG: JSON error {e}")
                await message.channel.send(f"{reply_text}\n\n❌ *Logic Error: Memory string was corrupted*")
        else:
            # Discord length safety
            await message.channel.send(response[:1990])

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run(TOKEN)

if "init" not in st.session_state:
    st.session_state.init = True
    threading.Thread(target=run, daemon=True).start()

st.title("🤖 Jarvis Professional Hub")
