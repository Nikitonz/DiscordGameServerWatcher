import disnake
import disnake.ext.commands as commands

GAMES = ["очко", "willbemoresoon"]


async def autocomp_games(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [games for games in GAMES if user_input.lower() in games]





class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    """
    @commands.command(name="test")
    async def test(self, ctx: disnake.MessageInteraction):
        view = Minigames.Confirm()
        view.add_item(disnake.ui.Button(label="Button 1", custom_id="test1"))
        msg = await ctx.send(content="1", view=view)
    """

    @commands.slash_command(name="minigame", description="Play the game")
    async def minigames(self, inter):
        pass
    @minigames.sub_command(name = "play", help= 'begin playing something...', description='begin playing something...')
    async def play_minigame(self, inter, gamename: str = commands.Param(autocomplete=autocomp_games)):
        if gamename == "очко":
            gameo = Cards21Game(inter=inter)
            await gameo.start_game()

        elif gamename == "willbemoresoon":
            embed = disnake.Embed(title="ты, наверное, шутишь",color=disnake.Color(16), description="сказано же, потом добавлю..." )
            await inter.send(embed=embed)

        else:
            await inter.send("Неправильная игра. Доступна только игра '21game'.")

    @minigames.sub_command(name="rules_help", help='читать правила...', description='читать правила...')
    async def help_minigame(self, inter: disnake.ApplicationCommandInteraction, gamename: str = commands.Param(autocomplete=autocomp_games)):
        if gamename == "очко":
            embed= disnake.Embed(title="Правила игры в очко", description="https://ru.wikipedia.org/wiki/Очко_(игра)")
            await inter.send(embed=embed)
        elif gamename == "willbemoresoon":
            await inter.send(content="единственное решение - ждать")
class Cards21Game:
    class ControlButtons(disnake.ui.View):
        def __init__(self, game):
            super().__init__(timeout=40)
            self.game = game

        @disnake.ui.button(style=disnake.ButtonStyle.green, label="Взять ещё", custom_id="hit")
        async def hit_cb(self, button: disnake.Button, interaction: disnake.MessageInteraction):
            await Cards21Game.hit_button(self.game, interaction)
        @disnake.ui.button(style=disnake.ButtonStyle.grey, label="Остановиться", custom_id="stop")
        async def stand_cb(self, button: disnake.Button, interaction: disnake.MessageInteraction):
            await Cards21Game.stand_button(self.game, interaction)
            self.stop()




    def __init__(self, inter):
        self.inter = inter
        self.user_hand = []  # Рука игрока
        self.bot_hand = []  # Рука бота
        self.user_sum = 0  # Сумма очков игрока
        self.bot_sum = 0  # Сумма очков бота
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        import random
        random.shuffle(self.deck)

    def is_bust(self, hand):
        return sum(hand) > 21

    def show_cards(self, hand):
        return ", ".join(str(card) for card in hand)

    async def hit_button(self, inter):
        card = self.deck.pop()  # Берем случайную карту из колоды
        self.user_hand.append(card)  # Добавляем карту в руку игрока
        self.user_sum += card  # Добавляем значение карты к сумме очков игрока

        await inter.response.edit_message(
            content=f"Ваши карты: {self.show_cards(self.user_hand)}\nСумма очков: {self.user_sum}",
            view=self.ControlButtons(self) if not self.is_bust(self.user_hand) else None,
        )

        if self.is_bust(self.user_hand):
            await self.inter.followup.send("Перебор! Вы проиграли.", ephemeral=True)


    async def stand_button(self, inter):
        while self.bot_sum < 17:
            card = self.deck.pop()
            self.bot_hand.append(card)
            self.bot_sum += card

        await inter.response.edit_message(
            content=f"Ваши карты: {self.show_cards(self.user_hand)}\nСумма ваших очков: {self.user_sum}\n\n"
                    f"Карты бота: {self.show_cards(self.bot_hand)}\nСумма очков бота: {self.bot_sum}",
            view=None,
        )

        if self.is_bust(self.bot_hand) or self.user_sum > self.bot_sum:
            await self.inter.followup.send("Вы выиграли!", ephemeral=True)
        elif self.user_sum < self.bot_sum:
            await self.inter.followup.send("Вы проиграли!", ephemeral=True)
        else:
            await self.inter.followup.send("Ничья!", ephemeral=True)

    async def start_game(self):
        try:
            await self.inter.response.send_message(
                content="Игра началась! Ваша первая карта:",
                view=self.ControlButtons(self)
            )
        except disnake.NotFound:
            pass






def setup(bot):
    bot.add_cog(Minigames(bot))
