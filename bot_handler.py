import os

import disnake.ext.commands as commands
import json

import disnake

config = None
params = None


def load(fileP):
    with open(fileP, 'r') as file:
        data = json.load(file)
    config = data.get('config', [])
    params_all = data.get('params', [])
    params = [param for param in params_all if param.get('isEnabled', True)]
    return config, params


config, params = load("config.json")

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")



async def load_cog():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")
            print(f"The cog {file[:-3]} has been loaded.")


@bot.command(name='unload_cog')
@commands.is_owner()
async def unload_cog(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f"Cog '{extension}' unloaded.")
    except Exception as e:
        await ctx.send(f"Error unloading cog '{extension}': {e}")


@bot.command(name='reload_cog')
@commands.is_owner()
async def reload_cog(ctx, extension):
    try:
        bot.reload_extension(f'cogs.{extension}')
        await ctx.send(f"Cog '{extension}' reloaded.")
    except Exception as e:
        await ctx.send(f"Error reloading cog '{extension}': {e}")


if __name__ == '__main__':
    bot.loop.run_until_complete(load_cog())


    bot.run(config['token'])

