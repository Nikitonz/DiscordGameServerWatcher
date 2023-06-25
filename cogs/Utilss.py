import disnake
import disnake.ext.commands as commands


class Utilss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vip-tutorial", aliases=['vt', 'vipt'])
    async def troll(self, ctx):
        url = "https://bit.ly/NikitonzsVipTutorial"
        await ctx.message.delete()
        print("rickrolled!")

        # Создаем Embed сообщение с кликабельной ссылкой
        embed = disnake.Embed(description=f"[Эксклюзивная помощь доступна здесь и сейчас! (**тык**)]({url})", color=0x00ff00)

        await ctx.send(content="вот, " + ctx.author.name + ", ваша ссылка на источник... Как и заказывали", embed=embed, delete_after=50, tts=True)

    @commands.slash_command(name="role", description="Assign, add or remove a role")
    async def role_command(self, inter):
        pass

    @role_command.sub_command(name = "assign", help= 'assigns or removes role to yourself', description='assigns or removes role to yourself')
    async def assign(self, inter, role:disnake.Role):
        member = inter.author
        try:
            if role in member.roles:
                await member.remove_roles(role)
                await inter.send(content = f"Вы выписаны из интеллигентов. Бывшая роль: {role.mention}")
            else:
                await member.add_roles(role)
                await inter.send(content = f"Назначили вам роль {role.mention}")
        except Exception:
            await inter.send("у тебя нет прав", tts=True)

    @commands.slash_command(name='clear',
                            description="чистит n сообщений. Если больше 10, спроси одобрения у администрации. Должны быть нужные права")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, inter: disnake.ApplicationCommandInteraction, count: int):
        try:
            async def delete_final(inter: disnake.ApplicationCommandInteraction, count):
                deleted_count = 0
                is_first_iteration = True

                async for message in inter.channel.history(limit=count + 1):
                    if is_first_iteration:
                        is_first_iteration = False
                        continue

                    await message.delete()
                    deleted_count += 1

                msg = f"`{deleted_count}`/`{count}` сообщений удалено."
                return msg

            class Warn(disnake.ui.View):
                def __init__(self):
                    super().__init__(timeout=600)

                @disnake.ui.button(label="Confirm deletion", style=disnake.ButtonStyle.red,
                                   custom_id="confirm_deletion")
                @commands.has_permissions(administrator=True)
                async def deletemsg(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
                    member = interaction.author
                    if not member.guild_permissions.administrator and member.id != member.guild.owner_id:
                        await interaction.send(f"У вас нет прав для выполнения этого действия.", ephemeral = True)
                        return
                    button.disabled = True
                    button.style = disnake.ButtonStyle.green
                    button.label = "Удаляем..."
                    await interaction.response.edit_message(view=self)
                    msg = await delete_final(inter, count)
                    await inter.edit_original_response(content=f"{msg}\nДействие одобрено администратором {interaction.author.mention}",view=None)



            if count <= 10:
                await inter.response.defer()
                msg = await delete_final(inter, count)
                await inter.followup.send(content=msg)
            else:
                view = Warn()
                await inter.send(
                    content=f"Пользователь {inter.author.mention} запрашивает удалить `{count}` сообщений. Подтвердите действие",
                    view=view
                )
        except disnake.errors.InteractionResponded as er:
            print(er)
        except Exception as e:
            print(e)


    @clear.error
    async def clear_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.MissingPermissions):
            await inter.response.send_message('У вас недостаточно прав для выполнения этой команды.', ephemeral=True, tts = True)
        elif isinstance(error, commands.CommandError):
            await inter.response.send_message("Ошибка при выполнении команды.", ephemeral=True, delete_after=20)


def setup(bot):
    bot.add_cog(Utilss(bot))
