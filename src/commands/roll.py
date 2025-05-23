"""
ダイスロール関連のコマンド処理
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Dict, Any, List, Optional

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
from dice.src.views.dice_view import DiceRollView

logger = get_logger()

# ユーザーごとのロール履歴
roll_history: Dict[int, List[Dict[str, Any]]] = {}

def setup_roll_command(bot: commands.Bot):
    """
    ロールコマンドをボットに設定する
    
    引数:
        bot: コマンドを追加するBotインスタンス
    """
    # スラッシュコマンドとして定義
    @bot.tree.command(name='roll', description='ダイスを振ります。例: 1d6, 2d10+3, d20-1')
    @app_commands.describe(dice_str='振りたいダイス (例: 1d6, 2d10+3, d20-1)')
    async def roll_dice_command(interaction: discord.Interaction, dice_str: str = None):
        """ダイスロールコマンド"""
        try:
            if not dice_str:
                await send_help_message(interaction)
                return
                
            if dice_str.lower() == 'help':
                await send_help_message(interaction)
                return
            
            # ダイスロール実行
            result = roll_complex_dice(dice_str)
            
            if "error" in result:
                await interaction.response.send_message(f"エラー: {result['error']}", ephemeral=True)
                return
                
            # Embedの作成
            embed = create_dice_embed(interaction, result)
            
            # ビューの作成と設定
            view = DiceRollView(dice_str, interaction)
            view.set_history_callback(update_roll_history)
            
            # 結果を送信
            await interaction.response.send_message(embed=embed, view=view)
            
            # ロール履歴に追加
            update_roll_history(interaction.user.id, result)
                
        except Exception as e:
            logger.error(f"ロールコマンド処理中にエラー: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f"コマンド処理中にエラーが発生しました: {str(e)}", ephemeral=True)
            else:
                await interaction.followup.send(f"コマンド処理中にエラーが発生しました: {str(e)}", ephemeral=True)
    
    # ヘルプコマンド
    @bot.tree.command(name='dice_help', description='ダイスボットの使い方を表示します')
    async def roll_help_command(interaction: discord.Interaction):
        """ダイスボットのヘルプを表示"""
        await send_help_message(interaction)

async def send_help_message(interaction: discord.Interaction):
    """
    ヘルプメッセージを送信する
    
    引数:
        interaction: インタラクション
    """
    help_embed = discord.Embed(
        title="ダイスボットの使い方",
        description="TRPGセッション用のダイスを振るためのコマンドです",
        color=discord.Color.blue()
    )
    
    help_embed.add_field(
        name="基本的な使い方",
        value=(
            "`/roll NdS` - N個のS面ダイスを振る\n"
            "`/roll d20` - 20面ダイスを1個振る\n"
            "`/roll 2d6` - 6面ダイスを2個振る"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="修正値を追加",
        value=(
            "`/roll 1d20+5` - 20面ダイスを振り、結果に5を加える\n"
            "`/roll 2d6-1` - 6面ダイスを2個振り、結果から1を引く"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="複数のダイス",
        value=(
            "`/roll 1d20+2d4` - 20面ダイス1個と4面ダイス2個を振る\n"
            "`/roll 2d8+1d6+3` - 8面ダイス2個と6面ダイス1個を振り、3を加える"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="履歴の表示",
        value="`/history` - あなたの過去10回分のダイスロール履歴を表示します",
        inline=False
    )
    
    help_embed.add_field(
        name="制限事項",
        value=(
            f"ダイスの数: {get_config('MIN_DICE_COUNT', 1)}～{get_config('MAX_DICE_COUNT', 100)}個\n"
            f"ダイスの面数: {get_config('MIN_DICE_SIDES', 2)}～{get_config('MAX_DICE_SIDES', 1000)}面\n"
            f"修正値: {get_config('MIN_MODIFIER', -1000)}～{get_config('MAX_MODIFIER', 1000)}"
        ),
        inline=False
    )
    
    await interaction.response.send_message(embed=help_embed, ephemeral=True)

def update_roll_history(user_id: int, result: Dict[str, Any]):
    """
    ユーザーのロール履歴を更新する
    
    引数:
        user_id: ユーザーID
        result: ロール結果
    """
    global roll_history
    
    if user_id not in roll_history:
        roll_history[user_id] = []
        
    # 最大履歴数に制限
    max_history = get_config('MAX_HISTORY_SIZE', 10)
    roll_history[user_id].append(result)
    if len(roll_history[user_id]) > max_history:
        roll_history[user_id].pop(0)
        
    logger.debug(f"ユーザー {user_id} の履歴を更新: {len(roll_history[user_id])}件")

def get_roll_history(user_id: int) -> List[Dict[str, Any]]:
    """
    ユーザーのロール履歴を取得する
    
    引数:
        user_id: ユーザーID
        
    戻り値:
        ロール履歴のリスト
    """
    global roll_history
    return roll_history.get(user_id, []) 