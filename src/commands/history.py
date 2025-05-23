"""
ダイスロール履歴に関するコマンド処理
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict, Any, List

import sys
import os

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from dice.src.utils.logger import get_logger
from dice.src.commands.roll import get_roll_history

logger = get_logger()

def setup_history_command(bot: commands.Bot):
    """
    履歴コマンドをボットに設定する
    
    引数:
        bot: コマンドを追加するBotインスタンス
    """
    @bot.tree.command(name='history', description='あなたの過去10回分のロール履歴を表示します。')
    async def show_history(interaction: discord.Interaction):
        """ロール履歴表示コマンド"""
        try:
            user_id = interaction.user.id
            history = get_roll_history(user_id)
            
            if not history:
                await interaction.response.send_message("ロール履歴がありません。`/roll`コマンドでダイスを振ってみましょう！", ephemeral=True)
                return
                
            # 履歴の概要Embedを作成
            embed = discord.Embed(
                title=f"🎲 {interaction.user.display_name}さんのロール履歴",
                description=f"最近の{len(history)}回分のロール履歴です",
                color=discord.Color.blue()
            )
            
            # 各ロールの詳細を追加
            for i, roll in enumerate(reversed(history), 1):
                # 各ロールの概要を表示
                notation = roll['input']
                result = roll['result']
                
                # クリティカル/ファンブルの判定
                is_critical = any(detail.get("is_critical", False) for detail in roll["details"] if detail["type"] == "dice")
                is_fumble = any(detail.get("is_fumble", False) for detail in roll["details"] if detail["type"] == "dice")
                
                # 特殊結果の表示
                status = ""
                if is_critical:
                    status = " 🎉 クリティカル!"
                elif is_fumble:
                    status = " 💥 ファンブル!"
                
                embed.add_field(
                    name=f"{i}. {notation}",
                    value=f"結果: **{result}**{status}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
                
        except Exception as e:
            logger.error(f"履歴コマンド処理中にエラー: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f"コマンド処理中にエラーが発生しました: {str(e)}", ephemeral=True)
            else:
                await interaction.followup.send(f"コマンド処理中にエラーが発生しました: {str(e)}", ephemeral=True) 