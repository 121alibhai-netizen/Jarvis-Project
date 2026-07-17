import discord

async def get_permanent_metadata(bot, workflow_id):
    metadata = "# --- USER METADATA ---\n"
    wf_channel = bot.get_channel(workflow_id)
    if wf_channel:
        # Hum channel ki history mein sirf wo messages dhoondenge jo code blocks mein hain
        async for m in wf_channel.history(limit=50):
            if "```python" in m.content:
                # Extracting just the code from the block
                code = m.content.split("```python")[1].split("```")[0].strip()
                metadata += code + "\n"
    return metadata

async def get_recent_chat(bot, temp_id):
    chat = "\n# --- RECENT CONVERSATION ---\n"
    temp_channel = bot.get_channel(temp_id)
    if temp_channel:
        async for m in temp_channel.history(limit=10):
            sender = "Master" if not m.author.bot else "JARVIS"
            chat += f"{sender}: {m.content}\n"
    return chat
