import discord
from discord.ui import View

from data_models.pokemon import Rarity

class PokemonView(View):
    pokemon_name: str
    rarity: Rarity
    base_catch_chance: float
    base_flee_chance: float
    fled: bool

    def __init__(self, pokemon_name: str, rarity: Rarity, timeout: float | None = 180.0):
        super().__init__(timeout=timeout)
        self.pokemon_name = pokemon_name
        self.rarity = rarity

        self.base_catch_chance = {
            Rarity.COMMON: 0.6,
            Rarity.UNCOMMON: 0.45,
            Rarity.RARE: 0.3,
            Rarity.LEGENDARY: 0.1
        }[rarity]
        
        self.base_flee_chance = {
            Rarity.COMMON: 0.05,
            Rarity.UNCOMMON: 0.1,
            Rarity.RARE: 0.2,
            Rarity.LEGENDARY: 0.5
        }[rarity]

        self.fled = False


    @discord.ui.button(label="Throw Bait", style=discord.ButtonStyle.green)
    async def throw_bait(self, inter: discord.Interaction, button: discord.ui.Button):
        if self.fled:
            return
        print("throw bait")
        await inter.response.send_message(f"{inter.user.mention} threw bait at {self.pokemon_name}")

    @discord.ui.button(label="Throw Ball", style=discord.ButtonStyle.blurple)
    async def throw_ball(self, inter:discord.Interaction, button: discord.ui.Button):
        if self.fled:
            return
        print("throw ball")
        await inter.response.send_message(f"{inter.user.mention} threw a ball at {self.pokemon_name}")

