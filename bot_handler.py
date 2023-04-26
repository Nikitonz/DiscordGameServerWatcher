import discord
from discord.ext import commands
from mcstatus import JavaServer

import main

bot_token = ""
channel_ids = []

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), test_guilds=channel_ids)
server = JavaServer.lookup(f"{main.getIP()}")

@bot.event
async def on_ready():
    pass


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.command(name="online", aliases=["get", "o"])
async def online(ctx):
    try:
        print("number online called")
        status = server.status()
        message = f"На сервере сейчас играют {status.players.online} игроков."
    except:
        message = "Сервер не отвечает."

    await ctx.send(message)


@bot.command(name="who_online", aliases = ["getplrlist", "who"])
async def whoonline(ctx):
    try:

        print("playerlist called")
        query = server.query()
        message = f"На сервере сейчас играют:\n{', '.join(query.players.names)}"
    except:
        message = "Сервер не отвечает."
    await ctx.send(message)

@bot.command(name="ping")
async def ping(ctx):
    latency = server.ping()
    try:
        await ctx.send(f"Задержка составляет {latency} мс.")
    except:
        await ctx.send("Сервер не отвечает.")

bot.run(bot_token)
