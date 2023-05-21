import argparse
import asyncio
from datetime import datetime, date, timedelta

import disnake
from disnake.ui import Select
from disnake.ext import commands

import requests
import json
from discord.ext import commands
from disnake import ApplicationCommandInteraction, SelectOption
from mcstatus import JavaServer

config = []
params = [[]]


def load(fileP):
    with open(fileP, 'r') as file:
        data = json.load(file)
    config = data.get('config', [])
    params = data.get('params', [])
    return (config, params)


def add_data(self, param1: str, param2: str, param3: str, param4: int):
    self.params.append((param1, param2, param3, param4))


def getIP():
    response = requests.get("https://httpbin.org/ip")
    data = response.json()
    ip = data["origin"]
    return ip


bot = disnake.ext.commands.Bot(command_prefix="!", intents=disnake.Intents.all())


@bot.event
async def on_ready():
    print(f"bot {bot.user} started")


@bot.event
async def on_disconnect():
    print(f"bot {bot.user} откис")


# ---------------------------------------
@bot.slash_command(name='managegame', help="allows you to change add custom game to spectrate",
                   description="allows you to change add custom game to spectrate")
async def managegm(inter, gamename: str, icon_url: str, ip: str, port: int):
    params.append((gamename, icon_url, ip, port))
    await inter.response.edit_message(content=f"Игра {gamename} добавлена в список", view=None)


# ---------------------------------------
@bot.slash_command(name='online', help="1", description="displays some infos")
async def online(inter):

    try:
        selected_option = None
        options_list = [param['name'] for param in params]
        options = [SelectOption(label=option, value=option, default=0) for option in options_list]
        select = Select(options=options, placeholder="Игра", custom_id="gamePicker")

        await inter.response.send_message("Выберите игру:", components=[select], ephemeral=True, delete_after=40)

        @bot.event
        async def on_message_interaction(interaction):
            nonlocal selected_option
            if interaction.data.custom_id == 'gamePicker':
                try:
                    print("passed #1")
                    selected_option = interaction.data.values[0]
                    #await interaction.response.edit_message(content=selected_option, view=None)
                except Exception as error:
                    await interaction.send(str(error), ephemeral=True)

        print("passed #2")
        await bot.wait_for("message_interaction", check=lambda i: i.component.custom_id == 'gamePicker')
        print("passed #3")
        print(f"{selected_option}")
        for param in params:
            if param['name'] == selected_option:
                server = JavaServer.lookup(f"{param['ip']}:" + str(param['port']))
                status = server.status()
                message = f"На сервере {param['name']} сейчас играют {status.players.online} игроков."
                await inter.send(str(message), ephemeral=True)
                print("passed #4")
                break
        print("passed #final")
    except asyncio.TimeoutError as er:
        await inter.send("Превышено время ожидания выбора игры." + str(er), ephemeral=True)
    except Exception as error:
        await inter.send(str(error), ephemeral=True)


@bot.command(name="who_online", aliases=["getplrlist", "who"])
async def whoonline(ctx):
    try:
        server = JavaServer.lookup(f"{params[0]['ip'] + params[0]['port']}")
        print("playerlist called")
        query = server.query()
        message = f"На сервере сейчас играют:\n{', '.join(query.players.names)}"
    except:
        message = "Сервер не отвечает."
    await ctx.send(message)


"""
def start():
    global time_launched
    print("started")
    time_launched = datetime.now().time()
    ip = getIP()

    data = {
        "username": f"{gamename} Server alert",
        "avatar_url": picture_url,
        "embeds": [
            {
                "title": f"{gamename} server status",
                "description": f"\nСервер запущен!\nIP: {ip}, Port: 25565\n```{ip}:25565```\nВремя запуска: {time_launched.strftime('%H:%M:%S')}",
                "color": 0x00FF00
            }
        ]
    }
    for url in webhook_urls:
        requests.post(url, json=data)
    with open("time.txt", 'w') as inp:
        inp.write(str(time_launched))


def stop():
    with open("time.txt", 'r') as gettime:
        time_launched = datetime.strptime(gettime.readline(), '%H:%M:%S.%f').time()
    print("finishing...")

    time_stopped = datetime.now().time()
    seconds_elapsed = (datetime.combine(date.today(), time_stopped) - datetime.combine(date.today(),
                                                                                       time_launched)).total_seconds()

    data = {
        "username": f"{gamename} Server alert",
        "avatar_url": picture_url,
        "embeds": [
            {
                "title": f"{gamename} server status",
                "description": f"\nСервер был остановлен. Время остановки: {time_stopped.strftime('%H:%M:%S')}\nСервер проработал={timedelta(seconds=seconds_elapsed)}",
                "color": 0x8B0000
            }
        ]
    }
    for url in webhook_urls:
        requests.post(url, json=data)

"""
if __name__ == '__main__':
    (config, params) = load("config.json")

bot.run(config[0]["token"])
