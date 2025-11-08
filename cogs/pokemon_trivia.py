import asyncio
from discord.abc import Messageable 
from discord.ext import commands, tasks

from db.helpers import get_random_trivia_question




class PokemonTriviaCog(commands.Cog):
    bot: commands.Bot
    trivia_active: bool

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.trivia_active = False


    @commands.command(name="start-trivia")
    @commands.has_permissions(administrator=True)
    async def start_trivia(self, ctx: commands.Context):
        """Starts the trivia task"""
        if self.trivia_active:
            await ctx.send("Safari is already active.")
        else:
            self.trivia_active = True
            channel = ctx.channel
            await ctx.send("Trivia will start in 10 minutes!")
            await asyncio.sleep(600) # 10 minutes
            self.trivia_task.start(channel)

    
    @tasks.loop(minutes=30.0)
    async def trivia_task(self, channel: Messageable):
        if not self.trivia_active:
            return
        
        question = await get_random_trivia_question(mark_used=True)
        if question is None:
            await channel.send("Unable to obtain a new question")
        else:
            await channel.send(question)

    @start_trivia.error
    async def pokemon_trivia_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
        else:
            await ctx.send(f"An error occurred: {error}")
