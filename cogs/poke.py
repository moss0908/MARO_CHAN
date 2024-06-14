import discord
from discord import app_commands
from discord.ext import commands
import requests
import random
import csv
import settings

#定数定義
NETABARE_CH_ID = 1152949812774314084
BASE_URL = "https://pokeapi.co/api/v2/"
MAX_POKE = 1024
NETABARE_IDX = 1018

#ポケモン図鑑コマンド
class Poke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_ch = bot

    #ランダムにポケモン情報を取得
    def get_pokemon_random():
        p_idx = random.randint(1, MAX_POKE)
        #日本語情報の取得
        response_ja = requests.get(BASE_URL + f'pokemon-species/{p_idx}')
        if response_ja.ok:
            data_ja = response_ja.json()
            for name_info in data_ja['names']:
                if name_info['language']['name'] == 'ja-Hrkt':
                    #英語情報の取得
                    response_en = requests.get(BASE_URL + f'pokemon/{p_idx}')
                    if response_en.ok:
                        data_en = response_en.json()
                        return name_info['name'],data_en, data_ja
                    
        #取得不可
        return None, None

    #ポケモン情報を取得
    def get_pokemon_data(poke_name):
        #英語情報の取得
        response_en = requests.get(BASE_URL + f'pokemon/{poke_name.lower()}')
        if response_en.ok:
            data_en = response_en.json()
            #日本語情報の取得
            response_ja = requests.get(BASE_URL + f'pokemon-species/{poke_name.lower()}')
            if response_ja.ok:
                data_ja = response_ja.json()
                return data_en, data_ja
                
        #取得不可
        return None, None
    
    #タイプ情報を取得
    def get_ja_types(data):
        typelist = []
        res_list = data['types']
        for res_type in res_list:
            type_response = requests.get(res_type['type']['url'])
            if type_response.ok:
                type = type_response.json()
                for type_info in type['names']:
                    if type_info['language']['name'] == 'ja-Hrkt':
                        typelist.append(type_info['name'])
        return "/".join(typelist)
    
    #特性情報を取得
    def get_ja_abilities(data):
        abilities_list = []
        res_list = data['abilities']
        for res_ab in res_list:
            ab_response = requests.get(res_ab['ability']['url'])
            if ab_response.ok:
                ab = ab_response.json()
                for ab_info in ab['names']:
                    if ab_info['language']['name'] == 'ja':
                        ab_name = ab_info['name']
                        if res_ab['is_hidden']:
                            ab_name = ab_name + '(夢特性)'
                        abilities_list.append(ab_name)
        return "/".join(abilities_list)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : Poke')
        print("sync")

    @app_commands.command(name='poke',description='入力したポケモンの情報を検索するよ！')
    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.describe(poke_name='ポケモン名(完全一致/ランダムにしたい場合は「ランダム」と入れてね)')
    @app_commands.describe(ephemeral='本人にのみ表示します(デフォルトは公開メッセージ)')
    async def poke_command(self, interaction: discord.Interaction,poke_name:str,ephemeral:bool=False):
        await interaction.response.defer(ephemeral=ephemeral)

        #ポケモン情報取得
        data = None
        if poke_name == 'ランダム':
            poke_name, data, ja_data = Poke.get_pokemon_random()
        else:
            with open('./assets/poke_name.csv', encoding='utf8', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[1] == poke_name:
                        data, ja_data = Poke.get_pokemon_data(row[0])

        #チェック処理
        if data == None:
            await interaction.followup.send('そんなポケモンは知らないなあ･･･')
            return
        if interaction.channel_id != NETABARE_CH_ID and data['id'] >= NETABARE_IDX:
            await interaction.followup.send('あー！あー！聞こえない～！！　※ココでは表示できません！ネタバレ板で書いてね')
            return
        
        #要素情報の取得
        img_url = data['sprites']['front_default']
        height = data['height']
        weight = data['weight']
        stats = data['stats']
        stats_dict = {stat['stat']['name']: stat['base_stat'] for stat in stats}      

        #メッセージ作成
        embed = discord.Embed(title=poke_name)
        embed.set_thumbnail(url=img_url)
        embed.add_field(name='タイプ',value=Poke.get_ja_types(data))
        embed.add_field(name='高さ',value=f'{height/10}m')
        embed.add_field(name='重さ',value=f'{weight/10}kg')
        
        #HADCBS
        embed.add_field(name='HP',value=stats_dict['hp'])
        embed.add_field(name='攻撃',value=stats_dict['attack'])
        embed.add_field(name='防御',value=stats_dict['defense'])
        embed.add_field(name='特攻',value=stats_dict['special-attack'])
        embed.add_field(name='特防',value=stats_dict['special-defense'])
        embed.add_field(name='素早さ',value=stats_dict['speed'])
        embed.add_field(name='特性',value=Poke.get_ja_abilities(data),inline=False)
        await interaction.followup.send(embed=embed)
        
#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(Poke(bot))