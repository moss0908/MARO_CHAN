from discord.ext import commands
from module.talk_util import TalkUtil
import os
import openai
import aiohttp
import tiktoken
import json
from tiktoken.core import Encoding
import settings

#コンフィグ設定
DATA_DIR = './talkdata/'
openai.api_key = settings.OPENAI_APIKEY
OPENAI_MODEL = "gpt-4o-search-preview"
MAX_TOKENS = 2000  # 最大トークン数

encoding: Encoding = tiktoken.encoding_for_model("gpt-4o")

#AIクライアント
class AsyncOpenAIClient:
  def __init__(self, api_key):
    self.api_key = api_key
    self.endpoint = "https://api.openai.com/v1/chat/completions"

  #不要かも
  def _format_messages(self, messages):
    formatted_messages = []
    for message in messages:
      role = message["role"]
      content = message["content"]
      formatted_messages.append(f"{role}: {content}")
    return "\n".join(formatted_messages)

  #返信作成
  async def chat_completion(self, messages, temperature):
    headers = {
      "Authorization": f"Bearer {self.api_key}",
      "Content-Type": "application/json",
    }
    data = {
      "model": OPENAI_MODEL,
      "messages": messages,
      "temperature": temperature,
      "max_completion_tokens": MAX_TOKENS,
      "top_p": 0.95,
      "frequency_penalty": 0.3,
      "presence_penalty": 0.3,
    }
    async with aiohttp.ClientSession(headers=headers) as session:
      async with session.post(self.endpoint, json=data) as response:
        result = await response.json()
        if "error" in result:
          raise Exception(f"API Error: {result['error']}")
        return result

#マロトーク(会話機能)
class MARO_Talk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    #AIクライアント呼び出し
    async_openai_client = AsyncOpenAIClient(openai.api_key)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : MARO_Talk')
        print("sync")

    @commands.Cog.listener(name='on_message')
    async def maro_talk(self, message):
        if message.author.bot:
            return
        
        #会話
        if self.bot.user.id in [member.id for member in message.mentions]:
            countfile = DATA_DIR + str(message.author.id) + '.txt' 
            if not TalkUtil.check_reply_limit(countfile):
              await message.reply(f'･･･疲れたから寝ていい？ (※今日の回数制限を超えました。明日話しかけてね)')
              return
          
            #定義設定
            yourfile = DATA_DIR + str(message.author.id) + "_summary.txt"
            document = ""
            if os.path.exists(yourfile):
                with open(yourfile, 'r', encoding='utf-8') as f:
                    document = f.read()
            dictionary = TalkUtil.read_csv_dictionary(DATA_DIR + 'dictionary.csv')
            messagelog = TalkUtil.truncate_string(message.content)
            definitions_str = TalkUtil.find_definitions(messagelog, document, dictionary)
            if (definitions_str != ""):
                definitions_str2 = "なお、以下に追加情報を示す。\n" + definitions_str
            else:
                definitions_str2 = ""
            history_settings = "\n\nまた、彼女は過去に以下の内容の会話をしている。\n\n" + document
            naming_settings = "\n\nまた、彼女はUserの事を『" + message.author.display_name + "』と呼び、名前の後に「くん」や「さん」をつける。\n"
            system_settings = TalkUtil.CHARA_SETTING() + definitions_str2 + history_settings + naming_settings + "\n上記の注意点を守り、上記の発言例と資料を参考にして、春麿ちゃんの性格や口調、言葉の作り方を模倣し、回答を構築せよ。"
            
            #メッセージ生成
            if len(message.attachments) > 0:
              response = await self.async_openai_client.chat_completion(
                messages=[
                  {
                        "role": "system",
                        "content": system_settings
                    },
                    {
                        "role": "user",
                        'content': [
                            {
                                'type': 'text',
                                'text': "ユーザーが「" + messagelog + "」と言うと、春麿ちゃんはこう返した。"
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': message.attachments[0].url
                                }
                            },
                        ]
                    },
                ],
                temperature=1.0,
                web_search_options={
                    "search_context_size": "low",  # 検索深度
                    "user_location": {
                        "type": "approximate",
                        "approximate": {
                            "country": "JP",  # 地域
                        },
                    },
                }
              )
            else:
              response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                  {
                    "role": "system",
                    "content": system_settings
                  },
                  {
                    "role": "user",
                    'content': "ユーザーが「" + messagelog + "」と言うと、春麿ちゃんはこう返した。"
                  },
                ],
                temperature=1.0,
                web_search_options={
                    "search_context_size": "low",  # 検索深度
                    "user_location": {
                        "type": "approximate",
                        "approximate": {
                            "country": "JP",  # 地域
                        },
                    },
                }
              )

            reply = response['choices'][0]['message']['content'].replace('「', '').replace('」', '')
            await message.reply(reply)
            reply_tokens = encoding.encode(reply)
            reply_tokens_count = len(reply_tokens)
            print(f"返信:{reply} ／トークン数:{reply_tokens_count}")

            #ログ出力
            response2 = await self.async_openai_client.chat_completion(
                messages=[
                    {
                        "role":
                        "user",
                        "content":
                        "以下の要点を100字以内でまとめろ。[ユーザー「" + messagelog + "」春麿ちゃん「" + reply + "」]"
                    },
                ],
                temperature=1.0
            )
            logstr = response2['choices'][0]['message']['content'].replace('\n', '').replace('」', '').replace('「', '')
            await TalkUtil.log(yourfile,TalkUtil.truncate_string(logstr))
            
            #ログ
            log_tokens = encoding.encode(logstr)
            log_tokens_count = len(log_tokens)
            print(f"ログ:{logstr} ／トークン数:{log_tokens_count}")
            
#セットアップ処理
async def setup(bot: commands.Bot):
    await bot.add_cog(MARO_Talk(bot))