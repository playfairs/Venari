from discord.ext import commands
from discord.ext.commands import (
    Cog,
    command,
    group,
    has_permissions,
    is_owner,
    BucketType,
    cooldown,
    MaxConcurrency,
    
)


class General(Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send("Pong!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))