import io
import re
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageOps
import settings


class Reverse(commands.Cog):
    """入力された文章や画像を反転して返すコマンド群"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # URLを逆転から除外して文字列を逆にする
    # 例: 'hello https://example.com world' -> 'olleh https://example.com dlrow'
    def _reverse_preserve_urls(self, s: str) -> str:
        url_re = re.compile(r"https?://\S+|www\.\S+")
        parts = []
        last = 0
        for m in url_re.finditer(s):
            if m.start() > last:
                parts.append(s[last:m.start()][::-1])
            parts.append(m.group(0))
            last = m.end()
        if last < len(s):
            parts.append(s[last:][::-1])
        return ''.join(parts)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : Reverse')

    # テキストまたは画像を逆転
    @app_commands.guilds(int(settings.GUILD_ID))
    @app_commands.command(name='reverse', description='文章や画像を逆転して返すよ（画像は左右/上下を選べる）')
    @app_commands.describe(text='反転したい文章（任意）', image='反転したい画像（任意）', mode='画像の反転方向（画像指定時のみ有効）')
    @app_commands.choices(mode=[
        app_commands.Choice(name='flip_lr (左右反転)', value='flip_lr'),
    app_commands.Choice(name='flip_ud (上下反転)', value='flip_ud'),
    app_commands.Choice(name='both (上下左右反転)', value='both'),
    ])
    async def reverse_all(
        self,
        interaction: discord.Interaction,
        text: Optional[str] = None,
        image: Optional[discord.Attachment] = None,
        mode: Optional[app_commands.Choice[str]] = None,
    ):
        content_parts = []
        file_to_send = None

        # テキスト処理
        if text is not None and text != '':
            content_parts.append(self._reverse_preserve_urls(text))

        # 画像処理
        if image is not None:
            if not image.content_type or not image.content_type.startswith('image/'):
                await interaction.response.send_message('画像ファイルを添付してね。', ephemeral=True)
                return

            img_bytes = await image.read()
            with Image.open(io.BytesIO(img_bytes)) as im:
                im = im.convert('RGBA')
                flip_mode = (mode.value if mode is not None else 'both')
                if flip_mode == 'flip_lr':
                    flipped = ImageOps.mirror(im)
                elif flip_mode == 'flip_ud':
                    flipped = ImageOps.flip(im)
                else:  # both
                    flipped = ImageOps.mirror(ImageOps.flip(im))

                output = io.BytesIO()
                flipped.save(output, format='PNG')
                output.seek(0)
                file_to_send = discord.File(fp=output, filename='reversed.png')

        if not content_parts and file_to_send is None:
            await interaction.response.send_message('文章か画像のどちらかを指定してね。', ephemeral=True)
            return

        content = '\n'.join(content_parts) if content_parts else None
        if file_to_send:
            await interaction.response.send_message(content=content, file=file_to_send)
        else:
            await interaction.response.send_message(content)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reverse(bot))

    
    
    
    
