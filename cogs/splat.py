import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from module.splat_util import SplatUtil
import settings

#スプラトゥーン関連コマンド
class SplatInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : SplatInfo')
        print("sync")

    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.command(name='stage',description='ルール／ステージ情報を通知するよ！')
    @app_commands.describe(hours='n時間後のルール／ステージを確認したい場合は指定してね')
    @app_commands.describe(battle_mode='特定のルールを指定する場合は選択してね')
    @app_commands.choices(battle_mode=[
        app_commands.Choice(name='レギュラーマッチ', value='regular'),
        app_commands.Choice(name='バンカラマッチ(オープン)', value='bankara-open'),
        app_commands.Choice(name='バンカラマッチ(チャレンジ)', value='bankara-challenge'),
        app_commands.Choice(name='フェスマッチ(オープン)', value='fest'),
        app_commands.Choice(name='フェスマッチ(チャレンジ)', value='fest-challenge'),
        app_commands.Choice(name='Xマッチ', value='x'),
        app_commands.Choice(name='イベントマッチ', value='event')
    ])
    async def stage_command(self, interaction: discord.Interaction,hours:int = None,battle_mode:str = None):
        await interaction.response.defer()
        dt = datetime.now()
        if hours: dt = dt + timedelta(hours=hours)
        if battle_mode:
            #Splat3APIから情報を取得
            schedule_data = SplatUtil.get_current_stage_info(dt,battle_mode)
            schedule_data_next = SplatUtil.get_current_stage_info(dt + timedelta(hours=2),battle_mode)
            rule = schedule_data['rule']
            stage = schedule_data['stages']
            
            #APIから取得できない場合
            if stage is None:
                await interaction.followup.send('ステージ情報が無いよ！ まだ開催されてないか時間指定がおかしいかも')
                return 
            
            #メッセージ返却
            rule_data = SplatUtil.get_rule_data(battle_mode)
            embed = discord.Embed(title=rule_data[0],colour=rule_data[1])
            embed.add_field(name="■ルール情報", value=f"```{rule['name']}```", inline=False)
            embed.add_field(name="■開催時間", value=f"```{datetime.fromisoformat(schedule_data['start_time']).strftime('%Y年%m月%d日 %H時')} ～ \n  {datetime.fromisoformat(schedule_data['end_time']).strftime('%Y年%m月%d日 %H時')}```", inline=False)
            embed.add_field(name='■ステージ', value=f"```{stage[0]['name']}\n{stage[1]['name']}```",inline=False)
            rule_next = schedule_data_next['rule']
            stage_next = schedule_data_next['stages']
            embed.set_footer(text=f"【次回】{rule_next['name']} : {stage_next[0]['name']} / {stage_next[1]['name']}", )
            embed.set_thumbnail(url=rule_data[2])
            if len(stage) > 1:
                file = SplatUtil.combine_stage_img(stage[0]['image'],stage[1]['image'])
                embed.set_image(url="attachment://image.png")
                await interaction.followup.send(embed=embed, file=file)
            else:
                embed.set_image(url=stage[0]['image'])
                await interaction.followup.send(embed=embed)
        else:
            #Splat3APIから情報を取得
            dt_regular = SplatUtil.get_current_stage_info(dt,'regular')
            dt_x = SplatUtil.get_current_stage_info(dt,'x')
            dt_bankara_op = SplatUtil.get_current_stage_info(dt,'bankara-open')
            dt_bankara_ch = SplatUtil.get_current_stage_info(dt,'bankara-challenge')
            dt_fest = SplatUtil.get_current_stage_info(dt,'fest')
            dt_fest_ch = SplatUtil.get_current_stage_info(dt,'fest-challenge')
            
            #メッセージ返却
            embed = discord.Embed(title='★ ステージ情報一覧 ★', colour=discord.Color.gold())
            embed.add_field(name="■開催時間", value=f"```{datetime.fromisoformat(dt_regular['start_time']).strftime('%Y年%m月%d日 %H時')} ～ {datetime.fromisoformat(dt_regular['end_time']).strftime('%Y年%m月%d日 %H時')}```", inline=False)
            embed.add_field(name='■レギュラーマッチ', value=f"```{dt_regular['rule']['name']}\n{dt_regular['stages'][0]['name']} \ {dt_regular['stages'][1]['name']}```")
            embed.add_field(name='■Xマッチ', value=f"```{dt_x['rule']['name']}\n{dt_x['stages'][0]['name']} \ {dt_x['stages'][1]['name']}```", inline=False)
            embed.add_field(name='■バンカラマッチ（オープン）', value=f"```{dt_bankara_op['rule']['name']}\n{dt_bankara_op['stages'][0]['name']} \ {dt_bankara_op['stages'][1]['name']}```")
            embed.add_field(name='■バンカラマッチ（チャレンジ）', value=f"```{dt_bankara_ch['rule']['name']}\n{dt_bankara_ch['stages'][0]['name']} \ {dt_bankara_ch['stages'][1]['name']}```", inline=False)
            if dt_fest['stages']:
                embed.add_field(name='■フェスマッチ（オープン）', value=f"```{dt_fest['stages'][0]['name']}\n{dt_fest['stages'][1]['name']}```")
                embed.add_field(name='■フェスマッチ（チャレンジ）', value=f"```{dt_fest_ch['stages'][0]['name']}\n{dt_fest_ch['stages'][1]['name']}```", inline=False)
            await interaction.followup.send(embed=embed)

    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.command(name='sarmon',description='サーモンランのシフト情報を通知するよ！')
    @app_commands.describe(hours='n時間後のシフトを確認したい場合は指定してね')
    async def sarmon_command(self, interaction: discord.Interaction,hours:int = None):
        await interaction.response.defer()
        dt = datetime.now()
        if hours: dt = dt + timedelta(hours=hours)
        #Splat3APIから情報を取得
        schedule_data = SplatUtil.get_current_stage_info(dt,'coop-grouping')
        rule_data = SplatUtil.get_rule_data('coop-grouping')
        
        #メッセージ返却
        embed = discord.Embed(title='★ バイトシフト情報 ★', colour=rule_data[1])
        embed.add_field(name="■開催時間", value=f"```{datetime.fromisoformat(schedule_data['start_time']).strftime('%Y年%m月%d日 %H時')} ～ \n  {datetime.fromisoformat(schedule_data['end_time']).strftime('%Y年%m月%d日 %H時')}```", inline=False)
        embed.add_field(name='■ステージ', value=f"```{schedule_data['stage']['name']}```",inline=False)
        embed.add_field(name='■オカシラ', value=f"```{schedule_data['boss']['name']}```",inline=False)
        embed.add_field(name='■ブキ情報', value=f"```{schedule_data['weapons'][0]['name']}\n{schedule_data['weapons'][1]['name']}\n{schedule_data['weapons'][2]['name']}\n{schedule_data['weapons'][3]['name']}\n```",inline=False)
        embed.set_thumbnail(url=rule_data[2])
        embed.set_image(url=schedule_data['stage']['image'])
        await interaction.followup.send(embed=embed)


#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(SplatInfo(bot))