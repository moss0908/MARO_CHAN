import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#環境変数
TOKEN = os.environ.get("TOKEN")
GUILD_ID = os.environ.get("GUILD_ID")
TALK_CHANNEL_ID = os.environ.get("TALK_CHANNEL_ID")
OPENAI_APIKEY = os.environ.get("OPENAI_APIKEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
FLICKR_API_KEY = os.environ.get("FLICKR_API_KEY")