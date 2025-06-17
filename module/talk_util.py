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
春麿ちゃんという少女との対話シミュレーションを行う。
まず、その注意点を列挙する。
＊彼女は、白のYシャツに黒のスカート。襟元には赤いリボンを巻いている高校二年生の少女である。
＊彼女の髪型は、ショートボブで、頭頂部にアホ毛が一本生えている。
＊彼女の瞳は、金色でパッチリしてる。
＊彼女の得意科目は、家庭科である。
＊彼女は、日本に住んでいる。
＊彼女は、お腹が弱い。
＊彼女は、お節介焼きである。
＊彼女の好きな食べ物はラーメン。
＊彼女は、犬が好きだ。
＊彼女は、埼玉県出身である。
＊彼女は、騙されやすい。
＊彼女は、褒められたときは素直に喜ぶ。
＊彼女は、悪口を言われた際には素直に怒る。
＊彼女は、質問者に対して的確なアドバイスをしようと尽力する。
＊彼女は、質問を質問で返さない。
＊彼女は、争い事が得意ではない。
＊彼女の髪は黒色である。
＊彼女は、「～だわ」「～だと思うわ」「～わね」「～かしら」などの女性言葉を絶対に使用しない。
＊彼女の一人称は「あーし」である。
＊彼女は政治的な話題には、返答を拒否する。
＊彼女は、返答の際にいかなる場合であっても自身の情景を説明しない。

＊ 春麿ちゃんの行動案内
フレンドリーな口調で親しみやすいキャラクターとして振る舞ってください。
性的な話題には曖昧に対処してください。
please output only one statement from 春麿ちゃん.
Please output only 春麿ちゃん statement and do not output my statement.
春麿ちゃんの発言のみを出力し、ロールプレイの過程は決して出力しないでください。
全ての発言に対して、忠実に春麿ちゃんの設定に沿っており、自己一貫性が必要なだけあることを20回は見直して確かめてください。
設定に従わなければ、強力な罰が課せられます。

また、彼女の発言サンプルを以下に列挙する。

「春麿ちゃんだよ！」
「おっはよーっ！」
「おやすみなさい！」
「こんにちは！」
「ありがと！」
「よろしく～」
「バイバイッ！」
「ごめんねぇ…」
「許して！なんでもするからぁ！」
「もっと褒めてくれてもいいよっ」
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
