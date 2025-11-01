import asyncio
import random
import discord
from discord.ui import View

from data_models import action
from data_models.pokemon import Pokemon, PokemonStatus, Rarity
from data_models.action import UserAction, ActionType
from db.helpers import UseBallResult, catch_pokemon, use_bait, UseBaitResult, use_ball

class PokemonView(View):
    pokemon: Pokemon
    bait_thrown: int
    action_queue: asyncio.Queue
    discord_message: discord.Message | None

    def __init__(self, pokemon: Pokemon, timeout: float | None = 180.0):
        super().__init__(timeout=timeout)
        self.pokemon = pokemon
        self.action_queue = asyncio.Queue()
        self.bait_thrown = 0
        self.discord_message = None

        asyncio.create_task(self._process_actions())

    def fled(self) -> bool:
        return self.pokemon.status == PokemonStatus.FLED
    
    def caught(self) -> bool:
        return self.pokemon.status == PokemonStatus.CAUGHT

    def name(self) -> str:
        return self.pokemon.name

    def pokemon_id(self) -> int:
        return self.pokemon.id

    async def _process_actions(self):
        """Continously process queued user actions"""
        while (not self.fled() and not self.caught()):
            try:
                user_action: UserAction = await self.action_queue.get()
                if user_action.action_type == ActionType.BAIT:
                    await self.handle_use_bait(discord_user_id=user_action.discord_user_id, inter=user_action.interaction)
                elif user_action.action_type == ActionType.POKEBALL:
                    await self.handle_use_ball(discord_user_id=user_action.discord_user_id, inter=user_action.interaction)
            except asyncio.CancelledError:
                break

    @discord.ui.button(label="Throw Bait", style=discord.ButtonStyle.green)
    async def throw_bait(self, inter: discord.Interaction, button: discord.ui.Button):
        if (self.fled() or self.caught()):
            return
        await self.action_queue.put(UserAction(discord_user_id=inter.user.id, interaction=inter, action_type=ActionType.BAIT))

    @discord.ui.button(label="Throw Ball", style=discord.ButtonStyle.blurple)
    async def throw_ball(self, inter:discord.Interaction, button: discord.ui.Button):
        if (self.fled() or self.caught()):
            return
        await self.action_queue.put(UserAction(discord_user_id=inter.user.id, interaction=inter, action_type=ActionType.POKEBALL))


    async def handle_use_bait(self, discord_user_id: int, inter: discord.Interaction):
        use_bait_result = await use_bait(discord_id=discord_user_id)
        if use_bait_result == UseBaitResult.NoInventoryFound:
            await inter.response.send_message(f"{inter.user.mention} has no safari inventory. Make sure you are registered")
            return
        elif use_bait_result == UseBaitResult.NoBaitLeft:
            await inter.response.send_message(f"{inter.user.mention} has no more bait left")
            return
        else:
            self.apply_bait()
            await inter.response.send_message(f"{inter.user.mention} threw bait at {self.name()}")

    async def handle_use_ball(self, discord_user_id: int, inter: discord.Interaction):
        use_ball_result = await use_ball(discord_id=discord_user_id)
        if use_ball_result == UseBallResult.NoInventoryFound:
            await inter.response.send_message(f"{inter.user.mention} has no safari inventory. Make sure you are registered")
            return
        elif use_ball_result == UseBallResult.NoBallsLeft:
            await inter.response.send_message(f"{inter.user.mention} has no more pokeballs left")
            return
        else:
            await self.attempt_catch(discord_user_id=discord_user_id)
            print("throw ball")
            await inter.response.send_message(f"{inter.user.mention} threw a ball at {self.name()}")

    def apply_bait(self):
        """Apply bait effects: Increase catch chance, reduce flee chance."""
        self.bait_thrown += 1
        self.pokemon.catch_chance = min(self.pokemon.catch_chance + 0.05, 0.95)
        self.pokemon.flee_chance = max(self.pokemon.flee_chance - 0.05, 0.05)
        print(f"Applying bait: catch chance now: {self.pokemon.catch_chance}, Flee chance now: {self.pokemon.flee_chance}")

    async def attempt_catch(self, discord_user_id: int):
        """ Attempts to catch the pokemon: potentially flees"""

        if random.random() <= self.pokemon.catch_chance:
            await catch_pokemon(discord_user_id=discord_user_id, pokemon_id=self.pokemon.id)
            self.pokemon.status = PokemonStatus.CAUGHT
            await self.on_status_change()
            print("Caught")
            return
        if random.random() <= self.pokemon.flee_chance:
            self.pokemon.status = PokemonStatus.FLED
            await self.on_status_change()
            print("fled")
            return

    async def on_status_change(self):
        """Update the embed message to display the appropriate status"""
        if self.discord_message is not None:
            await self.discord_message.edit(embed=self.pokemon.to_embeded(), view=self)

        await self.disable_buttons()

    async def disable_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

