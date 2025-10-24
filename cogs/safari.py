import os
from discord.ext import commands, tasks
from dataclasses import dataclass

from views.pokemon_view import PokemonView



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

    @tasks.loop(minutes=2)
    async def safari_task(self):
        if not self.safari_active or self.safari_channel_id is None:
            return

        safari_channel = self.bot.get_channel(int(self.safari_channel_id))
        if safari_channel is None:
            return
        
        pokemon_view = PokemonView("Pikachu")
        # Example message, replace with actual safari logic
        await safari_channel.send("A wild Pokémon has appeared in the safari!", view=pokemon_view)

    @start_safari.error
    @stop_safari.error
    @set_safari_channel.error
    @unset_safari_channel.error
    async def safari_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
        else:
            await ctx.send("An error occurred.")

     


