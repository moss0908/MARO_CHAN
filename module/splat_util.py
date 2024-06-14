import io
import requests
import discord
from datetime import datetime
from PIL import Image

#定数定義
SPLAT3API_ENDPOINT = "https://spla3.yuu26.com/api/"

#スプラトゥーン用Utilクラス
class SplatUtil():
    def __init__(self):
        self = self

    #API形式のモード名から情報（ルール名：カラー：アイコン）を取得
    def get_rule_data(p1):
        rule_data = {
            "regular": ["レギュラーマッチ", discord.Colour.brand_green(),"https://cdn.wikiwiki.jp/to/w/splatoon3mix/icon/::ref/%E3%83%AC%E3%82%AE%E3%83%A5%E3%83%A9%E3%83%BC%E3%83%9E%E3%83%83%E3%83%81.png?rev=731982e7d109cbdf5d68cfc5b1055363&t=20230804102358"],
            "bankara-open": ["バンカラマッチ(オープン)",discord.Colour.orange(),"https://cdn.wikiwiki.jp/to/w/splatoon3mix/icon/::ref/%E3%83%90%E3%83%B3%E3%82%AB%E3%83%A9%E3%83%9E%E3%83%83%E3%83%81.png.webp?rev=7f660441a805e1e3ac6e0825fac69584&t=20230804101054"],
            "bankara-challenge": ["バンカラマッチ(チャレンジ)",discord.Colour.orange(),"https://cdn.wikiwiki.jp/to/w/splatoon3mix/icon/::ref/%E3%83%90%E3%83%B3%E3%82%AB%E3%83%A9%E3%83%9E%E3%83%83%E3%83%81.png.webp?rev=7f660441a805e1e3ac6e0825fac69584&t=20230804101054"],
            "fest": ["フェスマッチ(オープン)",discord.Colour.blue(),"https://cdn.wikiwiki.jp/to/w/splatoon3mix/icon/::ref/%E3%83%95%E3%82%A7%E3%82%B9.png.webp?rev=f25948ce192ea0351191ea1fac2dc82c&t=20230804112333"],
            "fest-challenge": ["フェスマッチ(チャレンジ)",discord.Colour.blue(),"https://cdn.wikiwiki.jp/to/w/splatoon3mix/icon/::ref/%E3%83%95%E3%82%A7%E3%82%B9.png.webp?rev=f25948ce192ea0351191ea1fac2dc82c&t=20230804112333"],
            "x": ["Xマッチ",discord.Colour.green(),"https://cdn.wikiwiki.jp/to/w/splatoon3mix/icon/::ref/X%E3%83%9E%E3%83%83%E3%83%81.png?rev=3656b315904861a19627550dff03d637&t=20230804101032"],
            "event": ["イベントマッチ",discord.Colour.pink(),"https://cdn.wikiwiki.jp/to/w/splatoon3mix/icon/::ref/%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88%E3%83%9E%E3%83%83%E3%83%81.png.webp?rev=d8ed2397fe57c00e9b127de393046c1b&t=20230804101047"],
            "coop-grouping": ["サーモンラン",discord.Colour.purple(),"https://cdn.wikiwiki.jp/to/w/splatoon3mix/icon/::ref/%E3%82%B5%E3%83%BC%E3%83%A2%E3%83%B3%E3%83%A9%E3%83%B3.png?rev=a99a16e8ad08ee77444e7c3e7fe04f7f&t=20230804101118"]
        }
        return rule_data.get(p1)

    #指定時間・指定モードのルール／ステージ情報を返す
    def get_current_stage_info(dt, battle_mode):
        ret = None
        #ステージ情報の取得
        response = requests.get(SPLAT3API_ENDPOINT + f'{battle_mode}/schedule')
        if response.ok:
            schedule_list = response.json()
            for schedule_data in schedule_list['results']:
                #一致する時間帯のデータのみ取得する
                if datetime.fromisoformat(schedule_data['start_time']) <= dt.astimezone() \
                   and datetime.fromisoformat(schedule_data['end_time']) > dt.astimezone():
                    ret = schedule_data
                    break
        return ret
    
    #指定時間・指定モードのルール／ステージ情報を返す
    def get_current_stage_info(dt, battle_mode):
        ret = None
        #ステージ情報の取得
        response = requests.get(SPLAT3API_ENDPOINT + f'{battle_mode}/schedule')
        if response.ok:
            schedule_list = response.json()
            for schedule_data in schedule_list['results']:
                #一致する時間帯のデータのみ取得する
                if datetime.fromisoformat(schedule_data['start_time']) <= dt.astimezone() \
                   and datetime.fromisoformat(schedule_data['end_time']) > dt.astimezone():
                    ret = schedule_data
                    break
        return ret
    
    #ステージ画像を結合
    def combine_stage_img(url1, url2):
        response1 = requests.get(url1, stream=True)
        response2 = requests.get(url2, stream=True)
        response1.raw.decode_content = True
        response2.raw.decode_content = True
        img1 = Image.open(response1.raw)
        img2 = Image.open(response2.raw)
        dst = Image.new('RGB', (img1.width + img2.width, min(img1.height, img2.height)))
        dst.paste(img1, (0, 0))
        dst.paste(img2, (img1.width, 0))
        img_binary = io.BytesIO()
        dst.save(img_binary, format='PNG')
        img_binary.seek(0)
        file = discord.File(img_binary, filename='image.png')
        return file