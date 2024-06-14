import discord
import random
import sqlite3
from enum import Enum
from discord import app_commands
from discord.ext import commands
import settings

#定数定義
MEMBER_RANGE = [[1],[1],[2],[3,4]]

#SQL設定
dbname = './db/MARO_DATA.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

#初期検索
cur.execute('SELECT * FROM m_spla_wp_type_tbl')
docs = cur.fetchall()
wptype_list = [ app_commands.Choice(value=doc[0], name=doc[1]) for doc in docs]
cur.execute('SELECT * FROM m_spla_wp_range_tbl')
docs = cur.fetchall()
wprange_list = [ app_commands.Choice(value=doc[0], name=doc[1]) for doc in docs]
cur.execute('SELECT * FROM m_spla_wp_roll_tbl')
docs = cur.fetchall()
wproll_list = [ app_commands.Choice(value=doc[0], name=doc[1]) for doc in docs]

#ブキおみくじコマンド
class WeaponOmikuji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : WeaponOmikuji')
        print("sync")

    @app_commands.command(name='buki',description='ランダムなブキを選ぶよ！')
    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.describe(wptype='抽選対象のブキ種',wprange='抽選対象のレンジ',wproll='抽選対象のロール')
    @app_commands.choices(wptype=wptype_list,wprange=wprange_list,wproll=wproll_list)
    async def omikuji_command(self, interaction: discord.Interaction,wptype:int = None,wprange:int = None,wproll:int = None):
        await interaction.response.defer(ephemeral=True)
        #取得SQL作成
        sql = 'SELECT * FROM m_spla_wp_tbl'
        if wptype != None or wprange != None or wproll != None:
            where = []
            if wptype != None:
                where.append('wp_type_id = ' + str(wptype))
            if wprange != None:
                where.append('wp_range_id = ' + str(wprange))
            if wproll != None:
                where.append('wp_roll_id = ' + str(wproll))
            sql = sql + ' WHERE ' + ' AND '.join(where)
        cur.execute(sql)
        wpList = cur.fetchall()

        #チェック処理
        if len(wpList) == 0:
            await interaction.followup.send('そんなブキねーよ！　※条件に一致するブキが無いよ')
            return
        
        choice_wp = random.choice(wpList)
        embed = discord.Embed(title=choice_wp[1])
        embed.set_image(url=choice_wp[5])
        await interaction.followup.send(embed=embed)

    @app_commands.command(name='hensei',description='自分＋仲間3人でランダム編成を作成するよ！')
    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.describe(p1='仲間1人目',p2='仲間2人目',p3='仲間3人目')
    async def hensei_command(self, interaction: discord.Interaction,p1:discord.Member,p2:discord.Member,p3:discord.Member):
        await interaction.response.defer(ephemeral=True)

        #チェック処理
        if p1.bot or p2.bot or p3.bot:
            await interaction.followup.send('入ろうとしたけどBOT認証で弾かれた…　※BOTはメンバーに入れられません！')
            return
        if p1 == interaction.user or p2 == interaction.user or p3 == interaction.user:
            await interaction.followup.send('チーム内に自分が入っているよ！')
            return
        if p1 == p2 or p1 == p3:
            await interaction.followup.send('チーム内で人がカブってるよ！')
            return
        if interaction.user.voice == None or p1.voice == None or p2.voice == None or p3.voice == None:
            await interaction.followup.send('全員が同じボイスチャットに入ってない場合は編成出来ないよ！')
            return
        vch = interaction.user.voice.channel
        if p1.voice.channel != vch or p2.voice.channel != vch or p3.voice.channel != vch:
            await interaction.followup.send('全員が同じボイスチャットに入ってない場合は編成出来ないよ！')
            return

        #取得SQL作成
        wpList = []
        rollList = []
        for num in range(4):
            sql = 'SELECT WP.* FROM m_spla_wp_tbl WP \
                   WHERE WP.wp_range_id IN (' + ', '.join(map(str, MEMBER_RANGE[num])) + ') '
            if len(rollList) > 0:
                sql = sql + ' AND NOT WP.wp_roll_id IN (' + ', '.join(rollList) + ') '
            cur.execute(sql + 'ORDER BY RANDOM() LIMIT 1')
            wp = cur.fetchone()
            wpList.append(wp)
            rollList.append(str(wp[4]))

        #編成情報をDM送信
        embed = discord.Embed(title='★チーム結成！★')
        embed.add_field(name='■１人目',value=f'{interaction.user.display_name} / {wpList[0][1]}',inline=False)
        embed.add_field(name='■２人目',value=f'{p1.display_name} / {wpList[1][1]}',inline=False)
        embed.add_field(name='■３人目',value=f'{p2.display_name} / {wpList[2][1]}',inline=False)
        embed.add_field(name='■４人目',value=f'{p3.display_name} / {wpList[3][1]}',inline=False)
        await interaction.user.send(embed=embed)
        await p1.send(embed=embed)
        await p2.send(embed=embed)
        await p3.send(embed=embed)
        await interaction.followup.send('編成を作成したよ！')

    @app_commands.command(name='group',description='通話に入っている人でチーム分けを作成するよ！')
    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.describe(p1='観戦1人目',p2='観戦2人目')
    async def group_command(self, interaction: discord.Interaction,p1:discord.Member=None,p2:discord.Member=None):
        await interaction.response.defer()

        #チェック処理
        if interaction.user.voice == None:
            await interaction.followup.send('ボイスチャットに入ってない場合は使用出来ないよ！')
            return
        
        #メンバー抽出
        a_team = []
        b_team = []
        vch_menbers = interaction.user.voice.channel.members
        if p1 in vch_menbers:
            vch_menbers.remove(p1)
        if p2 in vch_menbers:
            vch_menbers.remove(p2)
        random.shuffle(vch_menbers)

        middle_index = len(vch_menbers) // 2
        a_team = vch_menbers[:middle_index]
        b_team = vch_menbers[middle_index:]
        a_team_name = ''
        b_team_name = ''
        for mem in a_team:
            a_team_name = a_team_name + " / " + mem.display_name
        for mem in b_team:
            b_team_name = b_team_name + " / " + mem.display_name

        #編成情報を送信
        embed = discord.Embed(title='★チーム結成！★')
        embed.add_field(name='■Aチーム',value=f'{a_team_name}',inline=False)
        embed.add_field(name='■Bチーム',value=f'{b_team_name}',inline=False)
        await interaction.followup.send(embed=embed)

#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(WeaponOmikuji(bot))