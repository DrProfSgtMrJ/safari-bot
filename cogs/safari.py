import os
from discord.ext import commands, tasks
from dataclasses import dataclass

from cogs.utils import get_random_pokemon
from views.pokemon_view import PokemonView
from db.db import SessionLocal
from db.models import Users



@dataclass
class SafariCog(commands.Cog):
    bot: commands.Bot
    safari_active: bool = False
    safari_channel_id: str | None = None

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.safari_active = False
        self.safari_channel_id = os.getenv("SAFARI_CHANNEL_ID")

    @commands.command(name="start-safari")
    @commands.has_permissions(administrator=True)
    async def start_safari(self, ctx: commands.Context):
        """Starts the safari task in the set channel"""
        if self.safari_active:
            await ctx.send("Safari is already active.")
            return

        if self.safari_channel_id is None:
            await ctx.send("Safari channel is not set. Please set it first with `!set-safari-channel`.")
            return

        self.safari_active = True

        safari_channel = self.bot.get_channel(int(self.safari_channel_id))
        if safari_channel is None:
            await ctx.send("The specified safari channel could not be found.")
            self.safari_active = False
            return
        self.safari_task.start()
        await ctx.send(f"Safari started in {safari_channel.mention}!")

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
    
    @commands.command(name="set-safari-channel")
    @commands.has_permissions(administrator=True)
    async def set_safari_channel(self, ctx: commands.Context, id: str):
        """Sets the desired safari channel"""
        print(f"Setting channel to: {id}")
        self.safari_channel_id = id
        await ctx.send(f"Setting Safari Channel to: {id}")
    
    @commands.command(name="unset-safari-channel")
    @commands.has_permissions(administrator=True)
    async def unset_safari_channel(self, ctx: commands.Context):
        """Unsets the safari channel"""
        if self.safari_channel_id is None:
            await ctx.send("Safari channel already unset")
            return

        self.safari_channel_id = None
        await ctx.send(f"Unsetting Safari Channel")

    @commands.command(name="register-user")
    @commands.has_permissions(administrator=True)
    async def register_user(self, ctx: commands.Context, discord_id: int):
        session = SessionLocal()

        # check if user is already registered
        existing_user = session.query(Users).filter(Users.discord_id == discord_id).first()
        if existing_user:
            await ctx.send(f"User with ID `{discord_id}` is already registered!")
            session.close()
            return
        
        member = await ctx.guild.fetch_member(discord_id)
        if member:
            discord_name = member.name

            new_user = Users(discord_id=discord_id, discord_display_name=discord_name)
            session.add(new_user)
            session.commit()
            session.close()

            await ctx.send(f"User `{discord_name}` with ID `{discord_id}` has been registered")

    @commands.command(name="unregister-user")
    @commands.has_permissions(administrator=True)
    async def unregister_user(self, ctx: commands.Context, discord_id: int):
        session = SessionLocal()

        # check if user is already registered
        existing_user = session.query(Users).filter(Users.discord_id == discord_id).first()
        if existing_user is None:
            await ctx.send(f"User with ID `{discord_id}` is not registered already!")
            session.close()
            return
        
        discord_name = existing_user.discord_display_name
        session.delete(existing_user)
        session.commit()
        session.close()
        await ctx.send(f"User `{discord_name}` with ID `{discord_id}` has been unregistered!")


    @tasks.loop(minutes=2)
    async def safari_task(self):
        if not self.safari_active or self.safari_channel_id is None:
            return

        safari_channel = self.bot.get_channel(int(self.safari_channel_id))
        if safari_channel is None:
            return
        
        pokemon_name, sprite_url = get_random_pokemon()
        pokemon_view = PokemonView(pokemon_name=pokemon_name, sprite_url=sprite_url)
        # Example message, replace with actual safari logic
        await safari_channel.send(view=pokemon_view, embed=pokemon_view.get_embeded())

    @start_safari.error
    @stop_safari.error
    @set_safari_channel.error
    @unset_safari_channel.error
    @register_user.error
    @unregister_user.error
    async def safari_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
        else:
            await ctx.send("An error occurred.")

     


