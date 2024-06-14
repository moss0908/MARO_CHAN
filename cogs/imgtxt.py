import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw
import settings

#定数
IMG_WIDTH = 520 #画像幅
IMG_ROW = 70   #1行あたりのサイズ
FONT_SIZE = 50  #フォントサイズ

#文字画像作成コマンド
class ImgText(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : ImgText')
        print("sync")

    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.command(name='imgtxt',description='文字画像を作るよ')
    @app_commands.describe(txt='文字列の内容を入れてね　※だいたい1行全角10文字を超えると縮小します『@』で改行')
    @app_commands.describe(txtfont='テキストのフォントだよ！※未指定だとNotoSansになるよ')
    @app_commands.choices(txtfont=[
        app_commands.Choice(name='NotoSansJP-Bold', value='./assets/fonts/NotoSansJP-Bold.ttf'),
        app_commands.Choice(name='赤薔薇シンデレラ', value='./assets/fonts/Akabara-Cinderella.ttf'),
        app_commands.Choice(name='g_コミックホラー', value='./assets/fonts/g_comickoin_freeB.ttf'),
        app_commands.Choice(name='HG創英角ポップ体', value='./assets/fonts/HGRPP1001.ttf'),
        app_commands.Choice(name='太甘書道フォント', value='./assets/fonts/kssweetheavycalligraphy.ttf'),
        app_commands.Choice(name='ドカベンフォント', value='./assets/fonts/NewDokabenFont_.otf'),
        app_commands.Choice(name='デラゴシック', value='./assets/fonts/DelaGothicOne-Regular.ttf')
    ])
    @app_commands.describe(txtcol='テキストカラーだよ！※未指定だと赤になるよ')
    @app_commands.choices(txtcol=[
        app_commands.Choice(name='赤', value='#FF5555'),
        app_commands.Choice(name='黄', value='#FFFF00'),
        app_commands.Choice(name='緑', value='#00FF00'),
        app_commands.Choice(name='紫', value='#800080'),
        app_commands.Choice(name='青', value='#0000FF'),
        app_commands.Choice(name='白', value='#FFFFFF'),
        app_commands.Choice(name='黒', value='#000000')
    ])
    async def imgtxt_command(self, interaction: discord.Interaction,txt:str,txtfont:str = None,txtcol:str = None):
        #文字列編集(改行&必要行数の特定)
        msgtxt = txt.replace('@','\n')
        rowCnt = msgtxt.count('\n')+1

        #画像を作成
        #フォント指定
        if txtcol == None:
            fontcolor = '#FF5555' #指定なしの場合は赤
        else:
            fontcolor = txtcol

        #フォント指定
        if txtfont == None:
            font_path = './assets/fonts/NotoSansJP-Bold.ttf' #指定なしの場合はNotoSans
        else:
            font_path = txtfont

        #背景画像
        x_pos = 0 #始点X
        y_pos = 0 #始点Y
        x_end_pos = IMG_WIDTH #終点X
        y_end_pos = IMG_ROW*rowCnt #終点Y
        bg = Image.new("RGBA", (x_end_pos,y_end_pos), (0,0,0,0))
        draw = ImageDraw.Draw(bg)
        
        #幅取得
        length = x_end_pos - x_pos
        height = y_end_pos - y_pos
        out_text_size = (length + 1, height + 1)
        font_size_offset = 0
        fontcustom = ImageFont.truetype(font_path, IMG_WIDTH, 0, encoding='utf-8') 
        bbox = draw.textbbox((x_pos, y_pos), msgtxt, font=fontcustom)

        #サイズ調整
        while length < out_text_size[0] or height < out_text_size[1]:
            fontcustom = ImageFont.truetype(font_path, IMG_WIDTH - font_size_offset, 0, encoding='utf-8') 
            bbox = draw.textbbox((x_pos, y_pos), msgtxt, font=fontcustom)
            out_text_size = (bbox[2], bbox[3])
            font_size_offset += 1

        #描画
        draw.text((x_pos, y_pos), msgtxt, font=fontcustom, fill=fontcolor)
        bg_crop = bg.crop(bg.getbbox())
        bg_crop.save("./assets/images/result.png")
        await interaction.response.send_message(file=discord.File("./assets/images/result.png"))

#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(ImgText(bot))