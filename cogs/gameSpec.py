import json
import os
from json import JSONDecodeError

import disnake
import disnake.ext.commands as commands
from disnake import SelectOption, RawReactionActionEvent
import requests
import asyncio
import subprocess

from disnake.ui import Select

from datetime import datetime, date, timedelta

from bot_handler import load
AtCapacity = None

class GameSpec(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config, self.params = load("config.json")

    def getIP(self):
        ip = None
        try:
            response = requests.get("https://httpbin.org/ip")
            data = response.json()
            ip = data["origin"]
            return ip
        except JSONDecodeError as e:
            print('error getting ip')
            return 0

    async def start(self, gamename,servname, avatarurl, ip, port):
        time_launched = datetime.now().time()
        print("started ", {gamename})
        ip = self.getIP()

        data = {
            "username": f"{gamename} Server alert",
            "avatar_url": avatarurl,
            "embeds": [
                {
                    "title": f"{servname} server status",
                    "description": f"\nСервер включён!\nIP: {ip}, Port: {port}\n```{ip}:{port}```\nВремя запуска: {time_launched.strftime('%H:%M:%S') }\n Некоторые сервера могут запускаться до 10 минут, дождитесь загрузки!",
                    "color": 0x00FF00
                }
            ]
        }
        for url in self.config['webhookurls']:
            requests.post(url, json=data)
        global AtCapacity
        AtCapacity =gamename
        with open("time.txt", 'w') as inp:
            inp.write(str(time_launched))

    def stop(self, gamename, iconurl):
        with open("time.txt", 'r') as gettime:
            time_launched = datetime.strptime(gettime.readline(), '%H:%M:%S.%f').time()
        print("finishing...", {gamename},"========================")

        time_stopped = datetime.now().time()
        seconds_elapsed = (datetime.combine(date.today(), time_stopped) - datetime.combine(date.today(),
                                                                                           time_launched)).total_seconds()

        data = {
            "username": f"{gamename} Server alert",
            "avatar_url": iconurl,
            "embeds": [
                {
                    "title": f"{gamename} server status",
                    "description": f"\nСервер был остановлен. Время остановки: {time_stopped.strftime('%H:%M:%S')}\nСервер проработал={timedelta(seconds=seconds_elapsed)}",
                    "color": 0x8B0000
                }
            ]
        }
        for url in self.config['webhookurls']:
            requests.post(url, json=data)
        global AtCapacity
        AtCapacity = None

    @commands.Cog.listener()
    async def on_ready(self):
        await self.put_reaction_routine()

    @commands.slash_command(name="myip")
    @commands.is_owner()
    async def myip(self, inter: disnake.ApplicationCommandInteraction):
        await inter.send(content=str(self.getIP()), ephemeral = True, delete_after = 30)




    async def put_reaction_routine(self):
        try:
            guilds_dep = self.config["guildsDep"]
            for guild_id, control_message_id in guilds_dep.items():

                channel = self.bot.get_channel(int(guild_id))
                message = await channel.fetch_message(control_message_id)
                await message.clear_reactions()
                for param in self.params:
                    emoji_id = param['emojiID']
                    if emoji_id != "" and emoji_id != 0:
                        emoji = self.bot.get_emoji(emoji_id)
                        await message.add_reaction(emoji)
        except Exception as e:
            pass

    @commands.command(name="enforce_poll", aliases=['ep'])
    @commands.is_owner()
    async def enforce_startup(self, ctx):
        await self.put_reaction_routine()


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        async def delayed_reaction_routine():
            await asyncio.sleep(7200)
            await self.put_reaction_routine()

        guilds_dep = self.config["guildsDep"]
        for guild_id, control_message_id in guilds_dep.items():
            if payload.message_id == control_message_id:
                channel = self.bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                reaction = disnake.utils.find(lambda r: r.emoji.name == payload.emoji.name, message.reactions)
                for param in self.params:
                    if param['emojiID']==reaction.emoji.id:
                        user = self.bot.get_user(payload.user_id)

                        if reaction and user and reaction.count > param['requiredReactions'] and user != self.bot.user:
                            global AtCapacity
                            if AtCapacity is not None:
                                print("busy by ", AtCapacity)
                                break
                            await message.clear_reactions()
                            asyncio.create_task(delayed_reaction_routine())
                            for param in self.params:
                                if str(reaction.emoji.id) == str(param['emojiID']):
                                    if param['isStaticIP']:
                                        ip = param['ip']
                                    else:
                                        ip = self.getIP()
                                    await self.start(param['game'], param['name'], param['iconURL'], ip, param['port'])
                                    print('launched')
                                    abs_path = os.path.abspath(param['pathToExecutorScript'])
                                    directory = os.path.dirname(abs_path)

                                    proc = None
                                    if abs_path.endswith('.exe'):
                                        command = ['cd', '/d', directory, '&&', 'start', '', abs_path] + [
                                            str(param['port'])]
                                        proc = subprocess.Popen(command, shell=True,
                                                                creationflags=subprocess.CREATE_NEW_CONSOLE)
                                        return_code = proc.wait()
                                        if return_code == 0:
                                            self.stop(param['game'], param['iconURL'])
                                    elif abs_path.endswith('.bat'):
                                        proc = subprocess.Popen(
                                            ['C:\Windows\System32\cmd.exe', '/c', 'start', '/wait', '', f'{abs_path}',
                                             str(param['port'])],
                                            shell=True,
                                            creationflags=subprocess.CREATE_NEW_CONSOLE,
                                            cwd=directory
                                        )
                                        return_code = proc.wait()
                                        if return_code == 0:
                                            self.stop(param['game'], param['iconURL'])
                                    else:
                                        print('Unsupported file type')
                                    break
                    else:
                        continue


    @commands.slash_command(name='managegame', help="allows you to change add custom game to spectrate",
                            description="allows you to change add custom game to spectrate")
    async def managegm(self, inter, gamename: str, icon_url: str, ip: str, port: int):
        self.params.append((gamename, icon_url, ip, port))
        await inter.response.edit_message(content=f"Игра {gamename} добавлена в список", view=None)

    @commands.slash_command(name='online', help="1", description="displays some infos")
    async def online(self, inter):
        try:
            options_list = [param['game'] for param in self.params]
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
                # await inter.send(content=selected_option)
                for param in self.params:
                    if param['game'] == selected_option:
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
            await inter.followup.send(content=message)


def setup(bot):
    bot.add_cog(GameSpec(bot))
