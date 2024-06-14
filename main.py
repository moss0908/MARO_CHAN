import discord
import settings
from discord.ext import commands

# cogsリスト
EXTENSIONS = [
    'cogs.recruit',
    'cogs.buki',
    'cogs.imgtxt',
    'cogs.talk',
    'cogs.teach',
    'cogs.poke',
    'cogs.mstr',
    'cogs.splat'
]
EXTENSIONS_DEBUG = [
    'cogs.debug.clear'
]
 
#BOT設定
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            intents=discord.Intents.all(),
            help_command=None,
            command_prefix='$'
        )

    async def setup_hook(self):
        for cog in EXTENSIONS:
            await bot.load_extension(cog)
        for cog in EXTENSIONS_DEBUG:
            await bot.load_extension(cog)
        await bot.tree.sync(guild=discord.Object(id=int(settings.GUILD_ID)))

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        print("Connected!")
        await bot.change_presence(activity=discord.Game(name="テング ビーフジャーキー", type=1))
        return

#BOT実行
bot = MyBot()
bot.run(settings.TOKEN)