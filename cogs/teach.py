import discord
import csv
from discord import app_commands
from discord.ext import commands
import settings

#定数定義
DATA_DIR = './talkdata/dictionary.csv'

#単語学習コマンド
class Teach(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_ch = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : Teach')
        print("sync")

    @app_commands.command(name='teach',description='BOTに単語を教えます。会話時に使えるよ')
    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.describe(word='単語名(20文字以内)')
    @app_commands.describe(meaning='単語の意味(最低20文字以上は書いてください。)')
    async def teach_command(self, interaction: discord.Interaction,word:str,meaning:str):
        await interaction.response.defer()

        #事前チェック
        if len(word) > 20:
            await interaction.response.send_message(f'単語名が長すぎ！(20文字以内にしてください。)', ephemeral=True)
            return 
        if len(meaning) > 200:
            await interaction.response.send_message(f'意味が長すぎ！(200文字以内にしてください。)', ephemeral=True)        
            return 
        
        #CSV書き込み
        with open(DATA_DIR, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([word, meaning])

        #メッセージ作成
        embed = discord.Embed(title='下記の内容を覚えたよ！')
        embed.add_field(name='■単語名',value=f'{word}',inline=False)
        embed.add_field(name='■意味',value=f'{meaning}',inline=False)
        await interaction.followup.send(embed=embed)
        
#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(Teach(bot))