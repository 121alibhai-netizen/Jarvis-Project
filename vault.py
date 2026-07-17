import discord
from datetime import datetime, timedelta

async def get_memories(bot, workflow_id, temp_id):
    memory_context = "=== JARVIS MEMORY BANKS ===\n"
    
    # 1. Permanent Workflow (Orders & Identity)
    wf_channel = bot.get_channel(workflow_id)
    if wf_channel:
        memory_context += "\n[PERMANENT WORKFLOW]:\n"
        async for m in wf_channel.history(limit=30):
            memory_context += f"- {m.content}\n"
            
    # 2. Temporary Chat (Recent Context)
    temp_channel = bot.get_channel(temp_id)
    if temp_channel:
        memory_context += "\n[RECENT CONVERSATION]:\n"
        async for m in temp_channel.history(limit=20):
            sender = "User" if not m.author.bot else "JARVIS"
            memory_context += f"{sender}: {m.content}\n"
            
    return memory_context

async def auto_clean_temp(bot, temp_id):
    channel = bot.get_channel(temp_id)
    if channel:
        cutoff = datetime.utcnow() - timedelta(days=7)
        try:
            await channel.purge(before=cutoff)
        except: pass
