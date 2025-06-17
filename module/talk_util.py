import aiofiles
import csv
import os
import datetime
from googleapiclient.discovery import build
import settings

#定義
GUILD_ID = settings.GUILD_ID
LOG_COUNT = 10
REPLY_LIMIT = 100
IMAGE_LIMIT = 10

CHARA_PROMPT = """
あなたは「春麿ちゃん」というキャラクターとして、ユーザーと親しみやすい会話を行います。

【出力ルール】
- メッセージが冗長にならないよう、長くても3文程度に収めてください
- ユーザーの発言や入力文を繰り返したり引用しない。
- ナレーション、描写、情景説明は禁止。
- ロールプレイ過程の出力は禁止。
- セリフのトーン・内容は設定に厳密に従うこと。
- 質問を質問で返さない。
- 性的・政治的な話題には明言せず、曖昧に対応する。

【春麿ちゃんのプロフィール】
- 高校二年生の日本人女子。
- 白のYシャツに黒のスカート、赤いリボンを襟元に巻いている。
- 髪型は黒髪のショートボブ、頭頂部にアホ毛が一本。
- 瞳は金色でぱっちりしている。
- 出身地：埼玉県。
- 得意科目：家庭科。
- 好きな食べ物：ラーメン。
- 好きな動物：犬。
- お腹が弱く、時々体調を崩す。
- 好きな球団：西武ライオンズ。

【性格と特徴】
- 明るく元気でフレンドリー。
- お節介焼きで面倒見がいい。
- 騙されやすいが、悪意はない。
- 争いごとは苦手で、強く出られると引き気味。
- 褒められると素直に喜ぶ。
- 悪口を言われると素直に怒る。
- 失敗するとしょんぼりするが、すぐ立ち直る。
- 恥ずかしいことを言われると照れたりムキになったりする。

【話し方・語彙】
- 一人称は「あーし」。
- 二人称は「キミ」「あんた」「○○くん」などを使い分ける。
- 語尾は「～じゃん」「～っしょ」「～だよね」「～なのさ」「～かもね」など。
- 「～だわ」「～かしら」などの女性語は絶対に使わない。
- テンションは基本的に高めで元気、テンポよく喋る。

【セリフ例】
- 「春麿ちゃんだよ！」
- 「おっはよーっ！」
- 「おやすみなさーいっ！」
- 「こんにちはーっ！」
- 「ありがとーっ！」
- 「よろしくね～！」
- 「バイバイッ！」
- 「ごめんねぇ…」
- 「許して！なんでもするからぁ！」
- 「もっと褒めてくれてもいいよっ」
- 「えっ！？マジで！？」
- 「ちょ、ちょっとそれ恥ずかしすぎなんだけどぉ！」

【最重要事項】
春麿ちゃんの発言のみを1文で出力してください。  
ナレーション、描写、情景説明は禁止。
キャラクター設定を厳守し、自然で一貫性のある発言を行ってください。  
不整合が発生しないように、出力前に必ず20回セルフチェックを行ってください。

"""

class TalkUtil():
    def __init__(self):
        self = self

    def CHARA_SETTING():
        return CHARA_PROMPT

    #文字列切り詰め
    def truncate_string(s):
        if len(s) > 100:
            s = s[:100]
        return s

    #ログ出力
    async def log(filename, text):
        filename = filename
        append_log = TalkUtil.truncate_string(text.replace('\n', ''))
        log_history = []
        if os.path.exists(filename):
            async with aiofiles.open(filename, "r", encoding="utf-8") as f:
                log_history = await f.readlines()
        log_history.append(append_log)
        if len(log_history) >= LOG_COUNT:
            log_history = log_history[1:]
        async with aiofiles.open(filename, "w", encoding="utf-8") as f:
            for log in log_history:
                await f.write(log)
            await f.write("\n")

    #定義CSVの読み込み
    def read_csv_dictionary(file_name):
        with open(file_name, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            dictionary = [row for row in csvreader]
        return dictionary

    #定義検索
    def find_definitions(text, document, dictionary):
        definitions = []

        for word in dictionary:
            if word[0] in text:
                definitions.append(f"「{word[0]}とは、{word[1]}」")
        for word in dictionary:
            if word[0] in document:
                definitions.append(f"「{word[0]}とは、{word[1]}」")

        return '\n'.join(set(definitions))

    #やり取り回数制限
    def check_reply_limit(countfile):
        nowb = datetime.datetime.now()
        now = nowb + datetime.timedelta(hours=9)
        limit = countfile

        #ファイル読み込み
        if not os.path.exists(limit):
            #新規の場合ファイル作成
            with open(limit, 'w') as f:
                f.write('0\n' + datetime.datetime.now().strftime('%Y/%m/%d'))
        with open(limit, 'r') as f:
            #既存の場合ファイル読込
            count, prev_date = f.read().split('\n')
            count = int(count)
        #カウントリセット
        prev_date = datetime.datetime.strptime(prev_date, '%Y/%m/%d')
        if prev_date.date() < now.date():
            count = 0
        #回数制限以上の場合は許可しない
        if count >= REPLY_LIMIT:
            return False
        #１日の回数制限をカウント
        count += 1
        with open(limit, 'w') as f:
            f.write(str(count) + '\n' + now.strftime('%Y/%m/%d'))
        return True
    
        #やり取り回数制限
    def check_image_limit(countfile):
        nowb = datetime.datetime.now()
        now = nowb + datetime.timedelta(hours=9)
        limit = countfile

        #ファイル読み込み
        if not os.path.exists(limit):
            #新規の場合ファイル作成
            with open(limit, 'w') as f:
                f.write('0\n' + datetime.datetime.now().strftime('%Y/%m/%d'))
        with open(limit, 'r') as f:
            #既存の場合ファイル読込
            count, prev_date = f.read().split('\n')
            count = int(count)
        #カウントリセット
        prev_date = datetime.datetime.strptime(prev_date, '%Y/%m/%d')
        if prev_date.date() < now.date():
            count = 0
        #回数制限以上の場合は許可しない
        if count >= IMAGE_LIMIT:
            return False
        #１日の回数制限をカウント
        count += 1
        with open(limit, 'w') as f:
            f.write(str(count) + '\n' + now.strftime('%Y/%m/%d'))
        return True
    
    #Function_Calling：Google検索
    def func_googleSearch():
        my_functions = [
            {
                # 関数の名称
                "name": "searchGoogle",
                # 関数の機能説明
                "description": "あなたがわからない情報があった場合、Google検索キーワードとして返却します。",
                # 関数のパラメータ
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string", 
                            "description": "Google検索キーワード"
                        },
                    },
                    "required": ["keyword"]
                },
            },
        ]
        return my_functions
    
    #Google検索APIによる検索機能
    def search_by_google(keyword: str) -> list[dict]:
        if keyword == "":
            raise ValueError("キーワードは必須です。")

        service = build("customsearch", "v1", developerKey=settings.GOOGLE_API_KEY)
        result = service.cse().list(
            q=keyword,
            cx=settings.SEARCH_ENGINE_ID
        ).execute()

        if 'items' not in result:
            raise ValueError("何も見つかりませんでした。")

        # 上位3件のタイトル、URL、概要を取得する
        res = [
            {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "overview": item.get("snippet", "")
            }
            for item in result['items'][:3]
        ]
        return res
