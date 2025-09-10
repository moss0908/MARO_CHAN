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
    @app_commands.command(name='ytdl', description='YouTubeのURLからmp3を生成して返します')
    @app_commands.describe(url='YouTubeの動画URL')
    async def ytdl(self, interaction: discord.Interaction, url: str):
        """使い方: /ytdl url: 指定のURLからmp3を作成して返す"""
        await interaction.response.defer()

        # 一時ディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            out_template = os.path.join(tmpdir, '%(title)s.%(ext)s')
            # ffmpegの場所をsettingsから取れるようにする（任意）
            ffmpeg_loc = getattr(settings, 'FFMPEG_PATH', None)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': out_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }

            if ffmpeg_loc:
                # yt-dlp に ffmpeg の場所を教える
                ydl_opts['ffmpeg_location'] = ffmpeg_loc

            try:
                loop = asyncio.get_event_loop()
                # yt_dlpはブロッキングなのでスレッドで実行
                await loop.run_in_executor(None, lambda: YoutubeDL(ydl_opts).download([url]))

                # 出力ファイルを探す
                files = [f for f in os.listdir(tmpdir) if f.lower().endswith('.mp3')]
                if not files:
                    await interaction.followup.send('mp3の生成に失敗しました。')
                    return

                file_path = os.path.join(tmpdir, files[0])
                file_size = os.path.getsize(file_path)

                # Discordのアップロード上限チェック（標準は8MB、サーバーによっては100MB等）
                if file_size > 8 * 1024 * 1024:
                    await interaction.followup.send('生成されたmp3が大きすぎます（>8MB）。サーバーのアップロード上限を確認してください。')
                    return

                await interaction.followup.send(file=discord.File(file_path))

            except Exception as e:
                await interaction.followup.send(f'エラーが発生しました: {e}')


async def setup(bot: commands.Bot):
    await bot.add_cog(YouTube(bot))
