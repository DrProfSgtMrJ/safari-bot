import discord
from discord import Embed
from discord.ui import View

class PokemonView(View):
    embed: Embed
    pokemon_name: str

    def __init__(self, pokemon_name: str, sprite_url: str | None, timeout: float | None = 180.0):
        super().__init__(timeout=timeout)

        self.pokemon_name = pokemon_name
        self.embed = Embed(
            title=f"A wild {pokemon_name} appeared!",
            description="What will you do?",
            color=discord.Color.ash_embed()
        )
        self.embed.set_image(url=sprite_url)

        
    def get_embeded(self) -> Embed:
        return self.embed

    @discord.ui.button(label="Throw Bait", style=discord.ButtonStyle.green)
    async def throw_bait(self, inter: discord.Interaction, button: discord.ui.Button):
        print("throw bait")
        await inter.response.send_message(f"{inter.user.mention} threw bait at {self.pokemon_name}")

    @discord.ui.button(label="Throw Ball", style=discord.ButtonStyle.blurple)
    async def throw_ball(self, inter:discord.Interaction, button: discord.ui.Button):
        print("throw ball")
        await inter.response.send_message(f"{inter.user.mention} threw a ball at {self.pokemon_name}")

