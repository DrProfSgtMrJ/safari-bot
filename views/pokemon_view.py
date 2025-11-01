import asyncio
import discord
from discord.ui import View

from data_models import action
from data_models.pokemon import Rarity
from data_models.action import UserAction, ActionType
from db.helpers import UseBallResult, use_bait, UseBaitResult, use_ball

class PokemonView(View):
    pokemon_name: str
    rarity: Rarity
    catch_chance: float
    flee_chance: float
    bait_thrown: int
    fled: bool
    caught: bool
    action_queue: asyncio.Queue

    def __init__(self, pokemon_name: str, rarity: Rarity, timeout: float | None = 180.0):
        super().__init__(timeout=timeout)
        self.pokemon_name = pokemon_name
        self.rarity = rarity
        self.action_queue = asyncio.Queue()
        self.bait_thrown = 0

        self.catch_chance = {
            Rarity.COMMON: 0.6,
            Rarity.UNCOMMON: 0.45,
            Rarity.RARE: 0.3,
            Rarity.LEGENDARY: 0.1
        }[rarity]
        
        self.flee_chance = {
            Rarity.COMMON: 0.05,
            Rarity.UNCOMMON: 0.1,
            Rarity.RARE: 0.2,
            Rarity.LEGENDARY: 0.5
        }[rarity]

        self.fled = False
        self.caught = False

        asyncio.create_task(self._process_actions())

    async def _process_actions(self):
        """Continously process queued user actions"""
        while not self.fled:
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
        if self.fled:
            return
        await self.action_queue.put(UserAction(discord_user_id=inter.user.id, interaction=inter, action_type=ActionType.BAIT))

    @discord.ui.button(label="Throw Ball", style=discord.ButtonStyle.blurple)
    async def throw_ball(self, inter:discord.Interaction, button: discord.ui.Button):
        if self.fled:
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
            await inter.response.send_message(f"{inter.user.mention} threw bait at {self.pokemon_name}")

    async def handle_use_ball(self, discord_user_id: int, inter: discord.Interaction):
        use_ball_result = await use_ball(discord_id=discord_user_id)
        if use_ball_result == UseBallResult.NoInventoryFound:
            await inter.response.send_message(f"{inter.user.mention} has no safari inventory. Make sure you are registered")
            return
        elif use_ball_result == UseBallResult.NoBallsLeft:
            await inter.response.send_message(f"{inter.user.mention} has no more pokeballs left")
            return

        print("throw ball")
        await inter.response.send_message(f"{inter.user.mention} threw a ball at {self.pokemon_name}")

    def apply_bait(self):
        """Apply bait effects: Increase catch chance, reduce flee chance."""
        self.bait_thrown += 1
        self.catch_chance = min(self.catch_chance + 0.05, 0.95)
        self.flee_chance = max(self.flee_chance - 0.05, 0.05)
        print(f"Applying bait: catch chance now: {self.catch_chance}, Flee chance now: {self.flee_chance}")
