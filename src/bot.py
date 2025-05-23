"""
Discord ダイスボット メインアプリケーション
"""
import discord
from discord import app_commands
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
from dice.src.commands.choose import setup_choose_command
from dice.src.commands.lottery import setup_lottery_command

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
    
    # スラッシュコマンド対応のため、command_prefixは不要に
    bot = commands.Bot(command_prefix='/', intents=intents)
    
    # コマンドの設定
    @bot.event
    async def on_ready():
        """ボット起動完了時のイベントハンドラ"""
        logger.info(f"{bot.user} としてログインしました")
        logger.info("スラッシュコマンドを準備しています...")
        
        # 全てのコマンドを表示（デバッグ用）
        all_commands = []
        for cmd in bot.tree.get_commands():
            all_commands.append(f"{cmd.name} ({type(cmd).__name__})")
        
        logger.info(f"登録されているコマンド: {', '.join(all_commands)}")
        
        # スラッシュコマンドをサーバーに同期
        try:
            # グローバルコマンドを同期
            synced = await bot.tree.sync()
            logger.info(f"{len(synced)}個のグローバルスラッシュコマンドを同期しました")
            
            # 念のため特定のギルドにも同期（必要に応じてIDを変更）
            # guild = discord.Object(id=123456789012345678)  # 実際のギルドIDを指定
            # guild_synced = await bot.tree.sync(guild=guild)
            # logger.info(f"{len(guild_synced)}個のギルドスラッシュコマンドを同期しました")
        except Exception as e:
            logger.error(f"スラッシュコマンドの同期中にエラーが発生しました: {e}")
        
        logger.info("ダイスボットの準備が完了しました")
    
    # コマンドのセットアップ
    setup_roll_command(bot)
    setup_history_command(bot)
    setup_choose_command(bot)  # ランダム選択コマンドを追加
    setup_lottery_command(bot)  # 抽選コマンドを追加
    
    # エラーハンドリング（スラッシュコマンドのエラーは各コマンドで捕捉）
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