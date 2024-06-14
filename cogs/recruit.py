import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
import settings
from module.recr_util import RecruitModal, RecruitEditModal

#SQL設定
dbname = './db/MARO_DATA.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

#募集作成コマンド
class Recruit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : Recruit')
        print("sync")

    #全てのインタラクションを取得
    @commands.Cog.listener()
    async def on_interaction(self, inter:discord.Interaction):
        try:
            if inter.data['component_type'] == 2:
                #データ取得
                sql = """SELECT * FROM p_recruit_tbl"""
                cur.execute(sql)
                recList = cur.fetchall()
                await Recruit.on_button_click(recList, inter)
        except KeyError:
            pass

    ## Buttonの処理
    async def on_button_click(recList, inter:discord.Interaction):
        custom_id = inter.data["custom_id"]
        for rec in recList:
            if custom_id == "Setting" + str(rec[0]): #募集内容編集ボタン
                #事前チェック
                owner_role = inter.guild.get_role(rec[3])
                if not discord.utils.get(inter.user.roles, name=owner_role.name): #ロール所持者以外が編集しようとした場合は無視
                    await inter.response.send_message(f'{inter.user.mention} \n人の部屋勝手に編集すな～～～！', ephemeral=True)
                    return
                #編集モーダルを起動
                modal = RecruitEditModal(inter.message.embeds[0])
                await inter.response.send_modal(modal)

            if custom_id == "Join" + str(rec[0]):#参加ボタン
                await inter.response.defer()
                guest_role = inter.guild.get_role(rec[4])
                voice_ch = inter.client.get_channel(rec[5])
                #事前チェック
                if discord.utils.get(inter.user.roles, name=guest_role.name): #既に付与されている場合は無視
                    await inter.followup.send(f'{inter.user.mention} \n既に参加済みの募集だよコレ！', ephemeral=True)
                    return
                #ロール付与
                await inter.followup.send(f'{inter.user.mention}  \n参加したよ！', ephemeral=True)
                await inter.user.add_roles(guest_role)
                await voice_ch.set_permissions(inter.user, speak=True)
                if inter.user.voice is not None and inter.user.voice.channel is voice_ch:
                    await inter.user.edit(mute=False)
                #参加者情報のDB情報を更新
                sql = """INSERT INTO p_recruit_member_tbl(recruit_id,member_id,disp_name,is_owner) VALUES(?, ?, ?, ?)"""
                data = ((rec[0], inter.user.id,inter.user.display_name,0))
                cur.execute(sql, data)
                conn.commit()
                #メッセージ更新
                new_embed = inter.message.embeds[0]
                new_member = inter.message.embeds[0].fields[4].value + f'{inter.user.mention}'
                new_embed.set_field_at(4, name=f"■参加者 現在：{len(guest_role.members)}人", value=new_member, inline=False)
                await inter.message.edit(embed=new_embed)

            elif custom_id == "Exit" + str(rec[0]): #退出ボタン
                await inter.response.defer()
                owner_role = inter.guild.get_role(rec[3])
                guest_role = inter.guild.get_role(rec[4])
                voice_ch = inter.client.get_channel(rec[5])
                #事前チェック
                if discord.utils.get(inter.user.roles, name=owner_role.name):#募集主が退出しようとした場合は無視
                    await inter.followup.send(f'{inter.user.mention} \n募集主が退出してどうするの！', ephemeral=True)
                    return
                #ロール削除
                await inter.followup.send(f'{inter.user.mention}  \n退出したよ！', ephemeral=True)
                await inter.user.remove_roles(guest_role)
                await voice_ch.set_permissions(inter.user, speak=False)
                #参加者情報のDB情報を更新
                sql = """DELETE FROM p_recruit_member_tbl WHERE recruit_id = ? and member_id = ?"""
                data = ((rec[0], inter.user.id))
                cur.execute(sql, data)
                conn.commit()
                #メッセージ更新
                new_embed = inter.message.embeds[0]
                new_member = inter.message.embeds[0].fields[4].value.replace(f'{inter.user.mention}','')
                new_embed.set_field_at(4, name=f"■参加者 現在：{len(guest_role.members)}人", value=new_member, inline=False)
                await inter.message.edit(embed=new_embed)

            elif custom_id == "Break" + str(rec[0]): #破棄ボタン
                await inter.response.defer()
                owner_role = inter.guild.get_role(rec[3])
                guest_role = inter.guild.get_role(rec[4])
                voice_ch = inter.client.get_channel(rec[5])
                #事前チェック
                if not discord.utils.get(inter.user.roles, name=owner_role.name): #ロール所持者以外が破棄しようとした場合は無視
                    await inter.followup.send(f'{inter.user.mention} \n人の部屋勝手に爆破すな～～～！', ephemeral=True)
                    return
                #部屋情報を削除
                sql = """DELETE FROM p_recruit_tbl WHERE recruit_id = ?"""
                cur.execute(sql, (rec[0],))
                sql = """DELETE FROM p_recruit_member_tbl WHERE recruit_id = ?"""
                cur.execute(sql, (rec[0],))
                conn.commit()
                #募集部屋削除
                for member in guest_role.members:
                    if member.voice is not None and member.voice.channel is voice_ch:
                        channel = inter.client.get_channel(int(settings.TALK_CHANNEL_ID))
                        await member.move_to(channel) 
                await owner_role.delete()
                await guest_role.delete()
                await voice_ch.delete()
                await inter.message.delete()
                await inter.followup.send('募集を取り消したよ！')
            
    @app_commands.command(name='recruit',description='部屋募集コマンドだよ！')
    @app_commands.guilds(int(settings.GUILD_ID))
    async def recruit_command(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RecruitModal())

    @app_commands.command(name='heyalist',description='部屋情報一覧の取得コマンドだよ！')
    @app_commands.guilds(int(settings.GUILD_ID))
    async def heyalist_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        #データ取得
        sql = """SELECT * FROM p_recruit_tbl"""
        cur.execute(sql)
        recList = cur.fetchall()

        #メッセージ作成
        embed = discord.Embed(title='★現在募集中の部屋一覧★')
        for rec in recList:
            embed.add_field(name=rec[1],value=rec[8],inline=False)
        await interaction.followup.send(embed=embed)

#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(Recruit(bot))