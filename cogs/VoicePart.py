import disnake
import disnake.ext.commands as commands


class VoicePart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #here goes main part
    # using @commands decorator instead @bot

def setup(bot):
    bot.add_cog(VoicePart(bot))