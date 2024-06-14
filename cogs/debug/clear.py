import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
import settings

#定数定義
OWNER_TEXT = '募集主' #募集ロール名
GUEST_TEXT = '参加者' #参加ロール名
TEMP_CH_NM = f'🎫'  #一時ボイスチャンネル識別符号

#SQL設定
dbname = './db/MARO_DATA.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

#募集作成コマンド
class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_ch = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : Clear')
        print("sync")

    @app_commands.command(name='clear',description='【デバッグコマンド】全ての募集部屋、ロールをクリアします。')
    @app_commands.guilds(int(settings.GUILD_ID))
    #@app_commands.checks.has_permissions(administrator=True)
    async def clear_command(self, interaction: discord.Interaction):
        #部屋情報をDBから削除
        sql = """DELETE FROM p_recruit_tbl"""
        cur.execute(sql)
        sql = """DELETE FROM p_recruit_member_tbl"""
        cur.execute(sql)
        conn.commit()

        #チャンネル
        for channel in interaction.guild.voice_channels:
            if TEMP_CH_NM in channel.name:
                print(f'チャンネル削除： {channel.name}')
                await channel.delete()
        #ロール
        for role in interaction.guild.roles:
            if OWNER_TEXT in role.name or GUEST_TEXT in role.name :
                print(f'ロール削除：{role.name}')
                await role.delete()
        await interaction.response.send_message(f'{interaction.user.mention} \n[全ての募集部屋、ロールをクリアしました。]', ephemeral=True)
        
#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(Clear(bot))