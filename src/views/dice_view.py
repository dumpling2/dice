"""
ダイスロール用のDiscord UI要素
"""
import discord
from discord.ext import commands
from typing import Dict, Any, Optional

import sys
import os

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from dice.src.utils.logger import get_logger
from dice.config.settings import get_config
from dice.src.dice.roller import roll_complex_dice
from dice.src.dice.renderer import create_dice_embed

logger = get_logger()

class DiceRollView(discord.ui.View):
    """ダイスロール結果に付けるボタン付きビュー"""
    def __init__(self, dice_str: str, ctx: commands.Context):
        timeout = get_config('BUTTON_TIMEOUT', 60)
        super().__init__(timeout=timeout)  # 設定された秒数後にボタンを無効化
        self.dice_str = dice_str
        self.ctx = ctx
        self.roll_history_callback = None

    def set_history_callback(self, callback):
        """
        ロール履歴更新用のコールバック関数を設定
        
        引数:
            callback: 呼び出す関数（ユーザーID、結果を引数に取る）
        """
        self.roll_history_callback = callback

    @discord.ui.button(label="再ロール", style=discord.ButtonStyle.primary, emoji="🎲")
    async def reroll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """再ロールボタンが押された時の処理"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("他の人のロールは再ロールできません", ephemeral=True)
            return

        try:
            # 複雑なダイス表記の処理
            result = roll_complex_dice(self.dice_str)
            
            if "error" in result:
                await interaction.response.send_message(f"エラー: {result['error']}", ephemeral=True)
                return
                
            # Embedの作成
            embed = create_dice_embed(self.ctx, result)
            
            # 結果を更新
            await interaction.response.edit_message(embed=embed, view=self)
            
            # ロール履歴に追加
            if self.roll_history_callback:
                self.roll_history_callback(self.ctx.author.id, result)
                
        except Exception as e:
            logger.error(f"再ロール中にエラーが発生: {e}")
            await interaction.response.send_message("ダイスの振り直し中にエラーが発生しました。", ephemeral=True) 