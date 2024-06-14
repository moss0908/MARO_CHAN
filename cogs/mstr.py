import discord
from discord import app_commands
from discord.ext import commands
import random
import requests
import settings

#定数
FLICKR_ENDPOINT_URI = 'https://api.flickr.com/services/rest/'
NUM_OF_PHOTOS = 20
MESHI_TERO_WORDS = [
  'カレー',
  '焼きおにぎり',
  'ラーメン',
  'チャーハン',
  'アジフライ',
  '天ぷら',
  'とんかつ',
  'メンチカツ',
  'フォンダンショコラ',
  'ブリュレ',
  'パフェ',
  'エクレア',
  'シュークリーム',
  'パンケーキ',
  'ハンバーグ',
  'オムライス'
  'ローストビーフ',
  '寿司',
  'pizza',
  '焼鳥',
  '豚汁',
  '麻婆豆腐',
  'からあげ',
  '手羽先',
  'カルパッチョ',
  'カツ丼',
  'ドーナツ'
]

#飯テロコマンド
class MeshiTero(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : ImgText')
        print("sync")

    def get_image():
        params = {
            'method': 'flickr.photos.search',
            'api_key': settings.FLICKR_API_KEY,
            'text': random.choice(MESHI_TERO_WORDS),
            'license': '1,2,3,4,5,6', # Creative Commons Lisense
            'per_page': NUM_OF_PHOTOS,
            'format': 'json',
            'nojsoncallback': '1',
            'privacy_filter': '1', # 1 public photos
            'content_type': '1', # 1 for photos only
            'sort': 'relevance'
        }

        resp = requests.get(FLICKR_ENDPOINT_URI, params=params)
        resp_json = resp.json()

        photo_info = random.choice(resp_json['photos']['photo'])
        tmp_url = 'https://farm%s.staticflickr.com/%s/%s_%s' % (photo_info['farm'], photo_info['server'], photo_info['id'], photo_info['secret'])
        image_url = tmp_url + '.jpg'
        return image_url


    @app_commands.command(name='mstr',description='飯の画像をリプライするよ！　※自動取得の為、飯の画像じゃない場合もあります')
    @app_commands.guilds(int(settings.GUILD_ID))
    async def mstr_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        #Flickr APIを使って飯テロ画像を取得する
        image_url = MeshiTero.get_image()
        await interaction.followup.send(image_url)
        

#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(MeshiTero(bot))