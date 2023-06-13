import disnake
import disnake.ext.commands as commands


class Utilss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vip-tutorial", aliases=['vp', 'vipt'])
    async def troll(self, ctx):
        url = "https://bit.ly/NikitonzsVipTutorial"
        import webbrowser
        await ctx.message.delete()
        webbrowser.open(url, new=2)
        print("rickrolled!")
        await ctx.send("вот, " + ctx.author.name + ", ваша ссылка на источник... Как и заказывали",
                       delete_after=50, tts=True)

    @commands.slash_command(name="role", description="Assign, add or remove a role")
    async def role_command(self, inter):
        pass

    @role_command.sub_command(name = "assign")
    async def assign(self, inter,  role:disnake.Role):
        member = inter.author
        await member.add_roles(role)
        await inter.send(content = "here you go!")

def setup(bot):
    bot.add_cog(Utilss(bot))
