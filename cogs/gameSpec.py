import json

import disnake
import disnake.ext.commands as commands
from disnake import  SelectOption
import requests
import asyncio
import subprocess

from disnake.ui import Select

from datetime import datetime, date, timedelta

from bot_handler import load


class GameSpec(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config, self.params = load("config.json")

    def load(fileP):
        with open(fileP, 'r') as file:
            data = json.load(file)
        config = data.get('config', [])
        params_all = data.get('params', [])
        params = [param for param in params_all if param.get('isEnabled', True)]
        return (config, params)

    def getIP(self):
        response = requests.get("https://httpbin.org/ip")
        data = response.json()
        ip = data["origin"]
        return ip

    def start(self):
        time_launched = datetime.now().time()
        print("started")
        ip = self.getIP()

        data = {
            "username": f"{self.params[0]['name']} Server alert",
            "avatar_url": self.params[0]['iconURL'],
            "embeds": [
                {
                    "title": f"{self.params[0]['name']} server status",
                    "description": f"\nСервер запущен!\nIP: {ip}, Port: 25565\n```{ip}:25565```\nВремя запуска: {time_launched.strftime('%H:%M:%S')}",
                    "color": 0x00FF00
                }
            ]
        }
        for url in self.config['webhookurls']:
            requests.post(url, json=data)
        with open("time.txt", 'w') as inp:
            inp.write(str(time_launched))

    def stop(self):
        with open("time.txt", 'r') as gettime:
            time_launched = datetime.strptime(gettime.readline(), '%H:%M:%S.%f').time()
        print("finishing...")

        time_stopped = datetime.now().time()
        seconds_elapsed = (datetime.combine(date.today(), time_stopped) - datetime.combine(date.today(),
                                                                                           time_launched)).total_seconds()

        data = {
            "username": f"{self.params[0]['name']} Server alert",
            "avatar_url": self.params[0]['iconURL'],
            "embeds": [
                {
                    "title": f"{self.params[0]['name']} server status",
                    "description": f"\nСервер был остановлен. Время остановки: {time_stopped.strftime('%H:%M:%S')}\nСервер проработал={timedelta(seconds=seconds_elapsed)}",
                    "color": 0x8B0000
                }
            ]
        }
        for url in self.config['webhookurls']:
            requests.post(url, json=data)

    async def put_reaction_routine(self):
        channel = self.bot.get_channel(self.config['GuildID'])
        message = await channel.fetch_message(self.config['ControlMessageID'])
        await message.clear_reactions()
        for param in self.params:
            emoji_id = param['emojiID']
            if emoji_id != "" and emoji_id != 0:
                emoji = self.bot.get_emoji(emoji_id)
                await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.config['ControlMessageID']:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            reaction = disnake.utils.find(lambda r: r.emoji.name == payload.emoji.name, message.reactions)
            user = self.bot.get_user(payload.user_id)

            if reaction and user and reaction.count > 2 and user != self.bot.user:
                await message.clear_reactions()
                subprocess.Popen(
                    ["C:\\Windows\\System32\\cmd.exe", "/c", r"D:\\GAMES\\MinecraftServerVanilla\\START.bat", "1"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.start()
                await asyncio.sleep(7200)
                await self.put_reaction_routine()

    @commands.slash_command(name='managegame', help="allows you to change add custom game to spectrate",
                            description="allows you to change add custom game to spectrate")
    async def managegm(self, inter, gamename: str, icon_url: str, ip: str, port: int):
        self.params.append((gamename, icon_url, ip, port))
        await inter.response.edit_message(content=f"Игра {gamename} добавлена в список", view=None)

    @commands.slash_command(name='online', help="1", description="displays some infos")
    async def online(self, inter):
        try:
            options_list = [param['name'] for param in self.params]
            options = [SelectOption(label=option, value=option, default=0) for option in options_list]
            select = Select(options=options, placeholder="Игра", custom_id="gamePicker")

            await inter.response.send_message("Выберите игру:", components=[select], ephemeral=True, delete_after=40)

        except asyncio.TimeoutError as er:
            await inter.send("Превышено время ожидания выбора игры." + str(er), ephemeral=True)
        except Exception as error:
            await inter.send(str(error), ephemeral=True)

    @commands.Cog.listener()
    async def on_message_interaction(self, inter):
        message = ''
        try:
            if inter.type == disnake.InteractionType.component and inter.data.get("custom_id") == 'gamePicker':
                await inter.response.defer()
                selected_option = inter.data.get("values")[0]
                inter.send(content=selected_option)
                for param in self.params:
                    if param['name'] == selected_option:
                        if selected_option == "Minecraft":
                            if param['isStaticIP']:
                                current_ip = param['ip']
                            else:
                                current_ip = self.getIP()
                            from mcstatus import JavaServer
                            server = JavaServer.lookup(f"{current_ip}:{str(param['port'])}")
                            status = server.status()
                            message = f"На сервере {param['name']} сейчас играют {status.players.online} игроков."
                        if selected_option == "Unturned":
                            server_url = 'https://api.battlemetrics.com/servers/20497498'
                            response = requests.get(server_url)
                            data = response.json()

                            if 'data' in data:
                                server_info = data['data']
                                server_name = server_info['attributes']['name']
                                player_count = server_info['attributes']['players']

                                if 'players' in server_info['relationships']:
                                    player_names = [player['attributes']['name'] for player in
                                                    server_info['relationships']['players']['data']]
                                    player_names_str = ', '.join(player_names)
                                else:
                                    player_names_str = 'Нет доступных данных о игроках'

                                message = f'На сервере {server_name} играет {player_count} игроков'
                            else:
                                print("Сервер не найден или произошла ошибка при запросе информации")

                        if inter.message and inter.message.components:
                            await inter.send(content=message, ephemeral=False, delete_after=9999)
                        else:
                            await inter.edit_original_message(content=message, view=None)
                        break
        except Exception as error:
            message = str(error)
            if '[WinError 10061]' in str(error):
                message = 'Не удалось проверить. Сервер точно запущен 🤨?'
            await inter.send(message, ephemeral=False)


def setup(bot):
    bot.add_cog(GameSpec(bot))

