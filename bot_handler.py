import os
import datetime
import disnake.ext.commands as commands
import json
import disnake
import sys

from disnake import Embed

config = None
params = None


def load(fileP):
    with open(fileP, 'r') as file:
        data = json.load(file)
    config = data.get('config', [])
    params_all = data.get('params', [])
    params = [param for param in params_all if param.get('isEnabled', True)]
    return config, params


(config, params) = load("config.json")

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

logs_directory = 'logs'
os.makedirs(logs_directory, exist_ok=True)
current_time = datetime.datetime.now()
log_file_path = os.path.join(logs_directory, f'{current_time:%d.%m.%Y}.txt')

log_file = open(log_file_path, 'a')


@bot.event
async def on_ready():
    log_message(f"Logged in as {bot.user.name} ({bot.user.id})\n\n")
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening, name='/help'))
    #await bot.change_presence(activity=disnake.Game(name='Играет в /play'))




async def load_cog():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")
            log_message(f"The cog {file[:-3]} has been loaded.")
@bot.command(name='unload_cog')
@commands.is_owner()
async def unload_cog(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f"Cog '{extension}' unloaded.")
        log_message(f"Cog '{extension}' unloaded.")
    except Exception as e:
        await ctx.send(f"Error unloading cog '{extension}': {e}")
        log_message(f"Error unloading cog '{extension}': {e}")


@bot.command(name='reload_cog')
@commands.is_owner()
async def reload_cog(ctx, extension):
    try:
        bot.reload_extension(f'cogs.{extension}')
        await ctx.send(f"Cog '{extension}' reloaded.")
        log_message(f"Cog '{extension}' reloaded.")
    except Exception as e:
        await ctx.send(f"Error reloading cog '{extension}': {e}")
        log_message(f"Error reloading cog '{extension}': {e}")


@bot.command(name='shutdown', aliases=['sd'])
@commands.is_owner()
async def perform_shutting_down(ctx, time):
    try:
        import subprocess
        if time == '-a' or time == 'a':
            subprocess.run(f"shutdown -a")
            log_message("Shutdown command aborted.")
        elif int(time):
            subprocess.run(f"shutdown -s -t {time}")
            log_message(f"System will shutdown in {time} seconds.")
    except Exception as e:
        await ctx.send(f"{e} fuck...")
        log_message(f"Error performing shutdown: {e}")

@bot.command(name='logoff')
@commands.is_owner()
async def perform_logoff(ctx):
    try:
       log_file.write('\n')
       log_file.flush()
       await bot.close()
    except Exception as e:
       pass
def log_message(message):
    current_time = datetime.datetime.now()
    log_entry = f"[{current_time:%d.%m.%Y %H:%M:%S}] {message}"
    print(log_entry)
    log_file.write(log_entry + '\n')
    log_file.flush()



#sys.stdout = log_file
bot.remove_command('help')


@bot.slash_command(name="help")
async def help_command(ctx):
    import random
    emb1: Embed = disnake.Embed(title=str("Информация о командах").center(100), color=random.randint(1, 16777216),
                                type='rich', timestamp=datetime.datetime.now())

    emb1.add_field(name=f"`{config['prefix']}vip-tutorial (vt)` : ", value="Эксклюзивная помощь", inline=True)
    emb1.add_field(name=f"`{config['prefix']}help` : ", value="Вызовет это меню", inline=True)
    emb1.add_field(name=f"`{config['prefix']}unload_cog <cogName>` : ", value="Отключить дополнение (только владелец)", inline=False)
    emb1.add_field(name=f"`{config['prefix']}reload_cog <cogName>` : ", value="Перегружает дополнение (только владелец)", inline=True)
    emb1.add_field(name=f"`{config['prefix']}shutdown [a|int]` : ", value="Выключить ПК (только владелец)", inline=False)
    emb1.add_field(name=f"`{config['prefix']}logoff` : ", value="Выключает бота (только владелец)", inline=True)
    emb1.add_field(name=f"`{config['prefix']}enforce_poll (ep)` : ", value="Принудительные реакции (только владелец)", inline=True)
    emb1.add_field(name=f"`{config['prefix']}myip` : ", value="IP сервера (только владелец)", inline=False)
    emb1.add_field(name=f"`/managegm <*args>` : ", value="Добавление своей игры (только владелец)(в разработке)", inline=False)
    emb1.add_field(name=f"`/online` : ", value="Узнать число игроков онлайн", inline=True)
    emb1.add_field(name=f"`/role` : ", value="Управление ролями (доступ к контенту)", inline=False)

    message = await ctx.send(embed = emb1)

if __name__ == '__main__':
    bot.loop.run_until_complete(load_cog())

    bot.run(config['token'])
    log_file.close()
