import os
import random
from discord.ext import commands, tasks
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from cogs.utils import get_random_pokemon
from data_models.pokemon import Pokemon
from views.pokemon_view import PokemonView
from db.db import AsyncSessionLocal
from db.models import SafariInventory, Users



class SafariCog(commands.Cog):
    bot: commands.Bot
    safari_active: bool
    safari_channel_ids: list[int]

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.safari_active = False
        self.safari_channel_ids = []

    @commands.command(name="start-safari")
    @commands.has_permissions(administrator=True)
    async def start_safari(self, ctx: commands.Context):
        """Starts the safari task in the set channel"""
        if self.safari_active:
            await ctx.send("Safari is already active.")
            return

        if len(self.safari_channel_ids) == 0:
            await ctx.send("No Safari channels set. Please set with `!set-safari-channels`.")
            return

        self.safari_active = True

        channel_ids = ""
        for id in self.safari_channel_ids:
            safari_channel = self.bot.get_channel(int(id))
            if safari_channel is None:
                await ctx.send(f"The specified safari channel with id {id} could not be found.")
            channel_ids += f"{id}," 
        self.safari_task.start()
        await ctx.send(f"Safari started in {channel_ids}!")

    @commands.command(name="stop-safari")
    @commands.has_permissions(administrator=True)
    async def stop_safari(self, ctx: commands.Context):
        """Stops the safari task"""
        if not self.safari_active:
            await ctx.send("Safari is not active.")
            return

        self.safari_active = False
        self.safari_task.cancel()
        await ctx.send("Safari has been stopped.")
    
    @commands.command(name="set-safari-channels", help="Provide channel ids separated by '/'.")
    @commands.has_permissions(administrator=True)
    async def set_safari_channels(self, ctx: commands.Context, ids: str):
        """Sets the desired safari channels - / seperated"""
        print(f"ids: {ids}")
        channel_ids = [int(ch.strip()) for ch in ids.split('/') if ch.strip()]
        self.safari_channel_ids = channel_ids
        await ctx.send(f"Setting Safari Channels to: {self.safari_channel_ids}")

    @commands.command(name="register-user")
    @commands.has_permissions(administrator=True)
    async def register_user(self, ctx: commands.Context, discord_id: int):
        async with AsyncSessionLocal() as session:
            # check if user is already registered
            result = await session.execute(select(Users).where(Users.discord_id == discord_id))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                await ctx.send(f"User with ID `{discord_id}` is already registered!")
                await session.close()
                return
            
            member = await ctx.guild.fetch_member(discord_id)
            if member:
                discord_name = member.name

                new_user = Users(discord_id=discord_id, discord_display_name=discord_name)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)

                inventory = SafariInventory(user_id=new_user.id)
                session.add(inventory)
                await session.commit()

                await ctx.send(f"User `{discord_name}` with ID `{discord_id}` has been registered")

    @commands.command(name="unregister-user")
    @commands.has_permissions(administrator=True)
    async def unregister_user(self, ctx: commands.Context, discord_id: int):
        async with AsyncSessionLocal() as session:
            
           # Check if user exists (therefore is registered)
            result = await session.execute(select(Users).where(Users.discord_id == discord_id))
            existing_user = result.scalar_one_or_none()

            if existing_user is None:
                await ctx.send(f"User with ID `{discord_id}` is not registered")
                await session.close()
                return
            
            await session.delete(existing_user)
            await session.commit()

            await ctx.send(f"User with ID `{discord_id}` has been unregistered!")

    @commands.command(name="inventory")
    async def inventory(self, ctx: commands.Context):
        """ Will display the user's current inventory (number of pokeballs and bait  left)"""
        async with AsyncSessionLocal() as session:
            discord_user_id = ctx.author.id

            # Fetch user + inventory 
            result = await session.execute(
                select(Users)
                .options(selectinload(Users.inventory))
                .where(Users.discord_id == discord_user_id))
            user = result.scalar_one_or_none()

            if user is None:
                await ctx.send(f"User with id: {discord_user_id} is not registered")
                await session.close()
                return

            inventory = user.inventory

            if inventory is None:
                await ctx.send("No inventory found")
            
            await ctx.send(f"Remaining Bait: {inventory.bait}\nRemaining Pokeballs: {inventory.pokeballs}") 


    @tasks.loop(minutes=2)
    async def safari_task(self):
        if not self.safari_active or len(self.safari_channel_ids) == 0:
            return
        print(f"Selecting from : {self.safari_channel_ids}") 
        channel_id = random.choice(self.safari_channel_ids)
        safari_channel = self.bot.get_channel(channel_id)
        if safari_channel is None:
            print(f"Could not find channel with ID {channel_id}")
            return

        pokemon: Pokemon = await get_random_pokemon()
        print(f"Got: {pokemon.name}")
        pokemon_view = PokemonView(pokemon=pokemon)
        message = await safari_channel.send(view=pokemon_view, embed=pokemon.to_embeded())
        pokemon_view.discord_message = message

    @start_safari.error
    @set_safari_channels.error
    @stop_safari.error
    @register_user.error
    @unregister_user.error
    @inventory.error
    async def safari_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
        else:
            await ctx.send(f"An error occurred: {error}")

     


