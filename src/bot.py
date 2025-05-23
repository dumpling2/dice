"""
Discord ダイスボット メインアプリケーション
"""
import discord
from discord.ext import commands
import logging
import os
import sys

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)

from dice.src.utils.logger import get_logger, setup_logger
from dice.config.settings import get_config
from dice.src.commands.roll import setup_roll_command
from dice.src.commands.history import setup_history_command

def start_bot(log_level: int = logging.INFO):
    """
    ボットを起動する
    
    引数:
        log_level: ログレベル
    """
    # ロガーの設定
    logger = setup_logger(log_level)
    logger.info("ダイスボットを起動しています...")
    
    # ボットの設定
    intents = discord.Intents.default()
    intents.message_content = True
    
    command_prefix = get_config('COMMAND_PREFIX', '!')
    bot = commands.Bot(command_prefix=command_prefix, intents=intents)
    
    # コマンドの設定
    @bot.event
    async def on_ready():
        """ボット起動完了時のイベントハンドラ"""
        logger.info(f"{bot.user} としてログインしました")
        logger.info(f"コマンドプレフィックス: {command_prefix}")
        logger.info("ダイスボットの準備が完了しました")
    
    # コマンドのセットアップ
    setup_roll_command(bot)
    setup_history_command(bot)
    
    # エラーハンドリング
    @bot.event
    async def on_command_error(ctx, error):
        """グローバルコマンドエラーハンドラ"""
        if isinstance(error, commands.CommandNotFound):
            # コマンドが見つからない場合は無視
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"引数が不足しています: {error}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"無効な引数です: {error}")
        else:
            logger.error(f"コマンド実行中のエラー: {error}")
            await ctx.send(f"エラーが発生しました: {error}")
    
    # ボットの起動
    token = get_config('BOT_TOKEN', '')
    if not token:
        logger.error("BOT_TOKENが設定されていません。.envファイルを確認してください。")
        return
    
    try:
        logger.info("ボットを起動しています...")
        bot.run(token)
    except discord.errors.LoginFailure:
        logger.error("BOT_TOKENが無効です。正しいトークンを設定してください。")
    except Exception as e:
        logger.error(f"ボット起動中にエラーが発生しました: {e}")

if __name__ == "__main__":
    # 直接実行された場合は起動
    start_bot() 