import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# 1. Keep-Alive Server (To make Jarvis 24/7 on Render)
server = Flask('')
@server.route('/')
def home():
    return "Jarvis System Status: ONLINE"

def run_server():
    server.run(host='0.0.0.0', port=8080)

# 2. Jarvis Bot Logic
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f'SYSTEM: Jarvis is now online in the Cloud.')
    # Jarvis sends a status update to the console
    await bot.change_presence(activity=discord.Game(name="Ready for your command, Sir"))

@bot.command()
async def hello(ctx):
    await ctx.send("Hello Sir! I am connected to the Render Cloud. My systems are fully operational.")

@bot.command()
async def check(ctx):
    await ctx.send("Status Report: \n- Brain: Cloud Active \n- Eyes: Awaiting Laptop Connection \n- Hands: Ready")

# Start the 'Keep-Alive' and 'Bot'
def start_jarvis():
    Thread(target=run_server).start()
    bot.run(TOKEN)

if __name__ == "__main__":
    start_jarvis()
