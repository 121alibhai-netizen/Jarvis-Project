import discord
from datetime import datetime, timedelta

async def get_memories(bot, workflow_id, temp_id):
    memory_context = "=== JARVIS MULTI-TIER MEMORY BANKS ===\n"
    
    # 1. Workflow Channel (Permanent Rules & Info) - Last 50 messages
    wf_channel = bot.get_channel(workflow_id)
    if wf_channel:
        memory_context += "\n[CORE WORKFLOW & MASTER IDENTITY]:\n"
        async for m in wf_channel.history(limit=50):
            if not m.author.bot:
                memory_context += f"Master Order: {m.content}\n"
            else:
                memory_context += f"Jarvis Log: {m.content}\n"
            
    # 2. Temporary Channel (Recent Chat) - Last 30 messages
    temp_channel = bot.get_channel(temp_id)
    if temp_channel:
        memory_context += "\n[RECENT CONVERSATION LOGS]:\n"
        async for m in temp_channel.history(limit=30):
            sender = "Master Ali" if not m.author.bot else "JARVIS"
            memory_context += f"{sender}: {m.content}\n"
            
    memory_context += "\n=== END OF MEMORY BANKS ===\n"
    return memory_context

async def auto_clean_temp(bot, temp_id):
    channel = bot.get_channel(temp_id)
    if channel:
        cutoff = datetime.utcnow() - timedelta(days=7)
        try:
            await channel.purge(before=cutoff)
        except:
            pass # Permission issues ke liye safety
