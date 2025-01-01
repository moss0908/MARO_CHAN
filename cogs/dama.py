import math
import discord
import numpy
from discord import app_commands
from discord.ext import commands
import settings


#定数定義
LOC = 10000   #平均
SCALE = 10000 #標準偏差
SIZE = 1000000 #サイズ
SR_RATE = 15  #SR確率
SSR_RATE = 5  #SSR確率
COEF_RATE = 999999 #大当たり倍率
DIGITS = ['', '万', '億', '兆', '京', '垓']

#お年玉コマンド
class Dama(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : Dama')
        print("sync")

    def yenFormat(_val):
        val = str(math.ceil(_val))
        length = len(val)
        keta_length = math.ceil(length / 4)
        result = ''
        results = [''] * keta_length

        for i in range(keta_length):
            results[i] = val[-4:]
            val = val[:-4]
            if(results[i] == '-'):
                result = results[i] + result
            elif(results[i] != '0000'):
                result = str(int(results[i])) + DIGITS[i] + result
        return result + '円'

    @app_commands.command(name='dama',description='お年玉が貰えるよ！いくらかな？')
    @app_commands.guilds(int(settings.GUILD_ID))
    async def dama_command(self, interaction: discord.Interaction):
        #お年玉抽選
        r = numpy.random.normal(LOC, SCALE,SIZE)
        dama = numpy.random.choice(r)
        
        #確率で数字が大きくなる
        rng = numpy.random.default_rng()
        w_rate = rng.integers(100)
        if SSR_RATE > w_rate:
            coef = rng.integers(COEF_RATE)
            dama = dama * coef
        if SR_RATE > w_rate:
            coef = rng.integers(50)
            dama = dama * coef
        #変換
        damastr = Dama.yenFormat(dama)
        #メッセージ作成
        await interaction.response.send_message(f'今年のお年玉はいくらかな～～～？⇒『{damastr}』')
        
#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(Dama(bot))