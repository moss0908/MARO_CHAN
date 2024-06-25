import discord
import sqlite3
import re
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from module.splat_util import SplatUtil

#SQL設定
dbname = './db/MARO_DATA.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

#モーダル作成
class RecruitModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="募集要項を記入してね！",
            timeout=None
        )
        
        self.game = RecrUtil.modal_game_title()
        self.add_item(self.game)

        self.date = RecrUtil.modal_date()
        self.add_item(self.date)

        self.time = RecrUtil.modal_time()
        self.add_item(self.time)

        self.notice = RecrUtil.modal_notice()
        self.add_item(self.notice)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            date = int(self.date.value)
        except:
            date = None
        time = int(self.time.value)
        #事前チェック
        errMsg = RecrUtil.check_time(date,time)
        if errMsg:
            await interaction.response.send_message(f'{interaction.user.mention} \n{errMsg}', ephemeral=True)
            return
        
        await interaction.response.defer()
        #時間設定
        starttime = RecrUtil.int_to_datetime(date,time)
        
        #チャンネル作成
        ch_name = self.game.value+starttime.strftime('%Y_%m%d_%H%M')
        voice_ch = await interaction.guild.create_voice_channel(f'🎫'+ch_name)
        #ロール作成／付与
        owner_role = await interaction.guild.create_role(name='募集主'+ch_name, mentionable=True, color=discord.Colour.red())
        guest_role = await interaction.guild.create_role(name='参加者'+ch_name, mentionable=True, color=discord.Colour.green())
        await interaction.user.add_roles(owner_role,guest_role)
        #権限編集（TODO：遅すぎなので考える）
        #for member in interaction.guild.members:
        #    if member == interaction.user:
        #        continue
        #    await voice_ch.set_permissions(member, speak=False)
        await voice_ch.set_permissions(owner_role, speak=True,move_members=True,mute_members=True)
        await voice_ch.set_permissions(guest_role, speak=True)
        await voice_ch.set_permissions(interaction.user, speak=True)

        #部屋情報をDBに登録
        sql = """INSERT INTO p_recruit_tbl(title,notice,roll_owner_id,roll_guest_id,voice_ch_id,start_date,expiry_date,message_url) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"""
        data = ((self.game.value, self.notice.value, owner_role.id, guest_role.id, voice_ch.id,starttime,'',''))
        cur.execute(sql, data)
        recruit_id = cur.lastrowid
        #主催者情報をDB情報を更新
        sql = """INSERT INTO p_recruit_member_tbl(recruit_id,member_id,disp_name,is_owner) VALUES(?, ?, ?, ?)"""
        data = ((recruit_id, interaction.user.id,interaction.user.display_name,1))
        cur.execute(sql, data)

        #メッセージ作成
        embed = discord.Embed(title='★参加者募集中！★')
        embed.set_thumbnail(url='https://1.bp.blogspot.com/-0LJSR56tXL8/VVGVS2PQRsI/AAAAAAAAtkA/9EI2ZHrT5w8/s550/text_sankasya_bosyu.png')
        embed.add_field(name='■ゲーム',value=f'{self.game.value}',inline=False)
        embed.add_field(name='■使用チャンネル',value=f'{voice_ch.mention}',inline=False)
        embed.add_field(name='■開始時間',value=f"{starttime.strftime('%Y年%m月%d日 %H時%M分')}",inline=False)
        embed.add_field(name='■備考欄',value=f'{self.notice.value}',inline=False)
        embed.add_field(name=f'■参加者 現在：{len(guest_role.members)}人',value=f'{interaction.user.mention}',inline=False)
        embed.set_footer(text=f'募集主 : {interaction.user.global_name} ',icon_url=f'{interaction.user.display_avatar.url}')
        view = discord.ui.View()
        
        view.add_item(discord.ui.Button(label='募集内容編集', style=discord.ButtonStyle.primary, row=3, custom_id="Setting"+str(recruit_id)))
        view.add_item(discord.ui.Button(label='参加', style=discord.ButtonStyle.green, row=4, custom_id="Join"+str(recruit_id)))
        view.add_item(discord.ui.Button(label='退出', style=discord.ButtonStyle.grey, row=4, custom_id="Exit"+str(recruit_id)))
        view.add_item(discord.ui.Button(label='破棄(募集主用)', style=discord.ButtonStyle.danger, row=4, custom_id="Break"+str(recruit_id)))
        msg = await interaction.followup.send(embed=embed,view=view)
        await msg.pin()

        #メッセージ情報を追加
        sql = """UPDATE p_recruit_tbl SET message_url = ? WHERE recruit_id = ?"""
        cur.execute(sql, (msg.jump_url,recruit_id))
        conn.commit()

#編集用モーダル
class RecruitEditModal(discord.ui.Modal):
    def __init__(self,embed):
        super().__init__(
            title="募集要項を編集",
            timeout=None 
        )
        self.embed = embed

        time = re.findall(r"\d+", embed.fields[2].value) #年、月、日、時、分を抽出
        self.dt = datetime(year=int(time[0]), month=int(time[1]), day=int(time[2]), hour=int(time[3]), minute=int(time[4]), second=0, microsecond=0, tzinfo=None)

        self.game = RecrUtil.modal_game_title()
        self.game.default = embed.fields[0].value
        self.add_item(self.game)

        self.date = RecrUtil.modal_date()
        self.date.default = time[1]+time[2]
        self.add_item(self.date)

        self.time = RecrUtil.modal_time()
        self.time.default = time[3]+time[4]
        self.add_item(self.time)

        self.notice = RecrUtil.modal_notice()
        self.notice.default = embed.fields[3].value
        self.add_item(self.notice)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            date = int(self.date.value)
        except:
            date = None
        time = int(self.time.value)

        #事前チェック
        errMsg = RecrUtil.check_time(date,time)
        if errMsg:
            await interaction.response.send_message(f'{interaction.user.mention} \n{errMsg}', ephemeral=True)
            return
        
        await interaction.response.defer()
        #時間設定
        starttime = RecrUtil.int_to_datetime(date,time)
        t = f"{starttime.strftime('%Y年%m月%d日 %H時%M分')}"

        #メッセージ更新
        new_embed = self.embed
        new_embed.title = "★参加者募集中！★ 🔧"
        new_embed.color=discord.Colour.red()
        if self.game.value != new_embed.fields[0].value:
            new_embed.set_field_at(0, name='■ゲーム',value=f'{self.game.value}',inline=False)

        if t != new_embed.fields[2].value:
            new_embed.set_field_at(2, name='■開始時間',value=f'{t}',inline=False)

        if self.notice.value != new_embed.fields[3].value:
            new_embed.set_field_at(3, name='■備考欄',value=f'{self.notice.value}',inline=False)
        
        await interaction.message.edit(embed=new_embed)
        #メッセージ更新
        member_text = new_embed.fields[4].value
        await interaction.followup.send(f'{member_text} \n 募集内容を編集したよ！内容を確認してね～')

#Recruitコマンド用Utilクラス
class RecrUtil():
    def __init__(self):
        self = self

    #モーダル情報
    def modal_game_title():
        return discord.ui.TextInput(label="募集ゲーム",style=discord.TextStyle.short,placeholder="例:スプラ３プラべ",required=True)
    def modal_date():
        return discord.ui.TextInput(label="開始日時(MMDD) ※省略時は募集日当日",max_length=4,min_length=4,style=discord.TextStyle.short,placeholder="例:12/3開始 ⇒ [1203]",required=False)
    def modal_time():
        return discord.ui.TextInput(label="開始時刻(24H/HHmm)",max_length=4,min_length=4,style=discord.TextStyle.short,placeholder="例:21:30開始 ⇒ [2130]",required=True)
    def modal_notice():
        return discord.ui.TextInput(label="備考",style=discord.TextStyle.long,placeholder="なにかあれば(自由入力)",default='挑戦者募集中！',required=False)

    #入力時間の整合性チェック
    def check_time(date,time):
        DATE_MAX = 1231 #指定日付の最大
        DATE_MIN = 101  #指定時間の最小
        TIME_MAX = 2359 #指定時間の最大
        errMsg = None

        #事前チェック
        if date != None and (date > DATE_MAX or time < DATE_MIN):
            #時間入力が不正な場合
            errMsg = 'ん？日付設定がおかしいんだけど！0101～1231の間で入力して！'
        if time > TIME_MAX or time < 0:
            #時間入力が不正な場合
            errMsg = 'ん？時間設定がおかしいんだけど！0000～2359の間で入力して！'
        return errMsg

    #int時間をdatetimeに変換
    def int_to_datetime(date,time):
        strtime = f'{time:04}'#datetime変換の関係で一度文字列に戻す
        starttime = datetime.now().replace(hour=int(strtime[0:2]), minute=int(strtime[2:4]), second=0)
        if date != None:
            strdate = f'{date:04}'#datetime変換の関係で一度文字列に戻す
            starttime = starttime.replace(month=int(strdate[0:2]), day=int(strdate[2:4]))
        return starttime
    
