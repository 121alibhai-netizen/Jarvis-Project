import discord
from datetime import datetime, timedelta

async def get_memories(bot, workflow_id, temp_id):
    # 1. Permanent Workflow parhna
    memory_context = "--- PERMANENT WORKFLOW MEMORY ---\n"
    wf_channel = bot.get_channel(workflow_id)
    if wf_channel:
        async for m in wf_channel.history(limit=20):
            memory_context += f"Rule/Task: {m.content}\n"
            
    # 2. Temporary conversation parhna
    memory_context += "\n--- RECENT CHAT HISTORY (TEMPORARY) ---\n"
    temp_channel = bot.get_channel(temp_id)
    if temp_channel:
        async for m in temp_channel.history(limit=15):
            sender = "User" if not m.author.bot else "JARVIS"
            memory_context += f"{sender}: {m.content}\n"
            
    return memory_context

async def auto_clean_temp(bot, temp_id):
    # 7 din purani chat mita dena
    channel = bot.get_channel(temp_id)
    if channel:
        cutoff = datetime.utcnow() - timedelta(days=7)
        await channel.purge(before=cutoff)
