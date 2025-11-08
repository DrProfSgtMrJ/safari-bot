import asyncio
import datetime
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
                    await self._process_bait(action=user_action)
                elif user_action.action_type == ActionType.POKEBALL:
                    await self._process_ball(action=user_action)
            except asyncio.CancelledError:
                break

    async def _process_bait(self, action: UserAction):
        inter = action.interaction
        use_bait_result = await use_bait(discord_id=action.discord_user_id)
        if use_bait_result == UseBallResult.NoInventoryFound:
            await self._send_message(inter, f"{inter.user.mention} has no safari inventory. Make sure you are registered")
            return
        elif use_bait_result == UseBaitResult.NoBaitLeft:
            await self._send_message(inter, f"{inter.user.mention} has no more bait left")
            return
        else:
            # apply bait
            self.bait_thrown += 1
            self.pokemon.bait_modifier += 0.05
            await self._send_message(inter, f"{inter.user.mention} threw bait at {self.name()}")

    async def _process_ball(self, action: UserAction):
        inter = action.interaction
        use_ball_result = await use_ball(discord_id=action.discord_user_id)
        if use_ball_result == UseBallResult.NoInventoryFound:
            await self._send_message(inter, f"{inter.user.mention} has no safari inventory. Make sure you are registered")
            return
        elif use_ball_result == UseBallResult.NoBallsLeft:
            await self._send_message(inter, f"{inter.user.mention} has no more pokeballs left")
            return
        else:
            await self._send_message(inter, f"{inter.user.mention} threw a ball at {self.name()}")
            roll = random.random()
            catch_threshold = self.pokemon.effective_catch_chance
            flee_threshold = min(catch_threshold + self.pokemon.effective_flee_chance, 1.0)
            if roll <= catch_threshold:
                await catch_pokemon(discord_user_id=action.discord_user_id, pokemon_id=self.pokemon.id)
                self.pokemon.catch(caught_at=datetime.datetime.now(datetime.timezone.utc))
                await self._send_message(inter, f"{inter.user.mention} CAUGHT {self.name()}")
                await self.on_status_change()
            elif roll <= flee_threshold: 
                self.pokemon.flee(fled_at=datetime.datetime.now(datetime.timezone.utc))
                await self._send_message(inter, f"{self.name()} fled...")
                await self.on_status_change()
            else:
                # Will increase flee chance if you miss
                self.pokemon.flee_modifier += 0.05
                await self._send_message(inter, f"{inter.user.mention}'s Pokeball missed!")

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

    
    async def _send_message(self, inter: discord.Interaction, content: str):
        """ Send message safely (handles one-response-per-interaction"""
        if not inter.response.is_done():
            await inter.response.send_message(content)
        else:
            await inter.followup.send(content)

    async def on_status_change(self):
        """Update the embed message to display the appropriate status"""
        if self.discord_message is not None:
            await self.discord_message.edit(embed=self.pokemon.to_wild_embeded(), view=self)


