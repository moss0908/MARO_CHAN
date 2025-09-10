import os
import tempfile
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from yt_dlp import YoutubeDL
import settings


class YouTube(commands.Cog):
    """YouTube URLから音声をmp3で抽出して返すコマンド"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.command(name='ytdl', description='YouTubeのURLからmp3を生成して返すよ！(※8MB以下で出力)')
    @app_commands.describe(url='YouTubeの動画URL', public='Trueにすると全体に送信（デフォルトは自分だけに見える）')
    async def ytdl(self, interaction: discord.Interaction, url: str, public: bool = False):
        """使い方: /ytdl url: 指定のURLからmp3を作成して返す。public=Trueで全体に公開"""
        await interaction.response.defer(ephemeral=not public)

        # 一時ディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            out_template = os.path.join(tmpdir, '%(title)s.%(ext)s')
            # ffmpegの場所をsettingsから取れるようにする（任意）
            ffmpeg_loc = getattr(settings, 'FFMPEG_PATH', None)

            
            preferred_quality = '192'
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': out_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': preferred_quality,
                }],
                'quiet': True,
                'no_warnings': True,
            }

            if ffmpeg_loc:
                # yt-dlp に ffmpeg の場所を教える
                ydl_opts['ffmpeg_location'] = ffmpeg_loc

            try:
                loop = asyncio.get_event_loop()

                # ビットレートの候補（高->低）
                qualities = ['192', '128', '96', '64', '32']
                initial_q = preferred_quality
                if initial_q in qualities:
                    qualities.remove(initial_q)
                qualities.insert(0, initial_q)

                MAX_BYTES = 8 * 1024 * 1024
                selected_path = None

                for q in qualities:
                    # 古いmp3を削除
                    for f in os.listdir(tmpdir):
                        if f.lower().endswith('.mp3'):
                            try:
                                os.remove(os.path.join(tmpdir, f))
                            except Exception:
                                pass

                    attempt_opts = dict(ydl_opts)
                    attempt_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': q,
                    }]

                    # 実行
                    await loop.run_in_executor(None, lambda: YoutubeDL(attempt_opts).download([url]))

                    files = [f for f in os.listdir(tmpdir) if f.lower().endswith('.mp3')]
                    if not files:
                        # ダウンロード失敗なら次へ
                        continue

                    file_path = os.path.join(tmpdir, files[0])
                    file_size = os.path.getsize(file_path)

                    if file_size <= MAX_BYTES:
                        selected_path = file_path
                        break
                    # 収まらなければ次のqualityで再試行

                if selected_path is None:
                    await interaction.followup.send('生成されたmp3が大きすぎるよ！（>8MB）', ephemeral=not public)
                    return

                await interaction.followup.send(file=discord.File(selected_path), ephemeral=not public)

            except Exception as e:
                await interaction.followup.send(f'エラーが発生しました: {e}', ephemeral=not public)


async def setup(bot: commands.Bot):
    await bot.add_cog(YouTube(bot))
