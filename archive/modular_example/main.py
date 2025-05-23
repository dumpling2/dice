"""
モジュール化されたダイスボットのメインエントリーポイント
"""

import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ログ設定
def setup_logging():
    """ログ設定を行う"""
    # ログディレクトリの作成
    os.makedirs('logs', exist_ok=True)
    
    # ロガーの設定
    logger = logging.getLogger('dice_bot')
    logger.setLevel(logging.INFO)
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    # ファイルハンドラ（ローテーション付き）
    file_handler = RotatingFileHandler(
        filename='logs/dice_bot.log',
        maxBytes=5242880,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # ロガーにハンドラを追加
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

async def main():
    """メイン関数"""
    # 環境変数のロード
    load_dotenv()
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    # トークンのチェック
    if not token:
        logger.critical("DISCORD_BOT_TOKENが設定されていません。.envファイルを確認してください。")
        return
    
    # インテントの設定
    intents = discord.Intents.default()
    intents.message_content = True  # メッセージ内容の読み取りを許可
    
    # コマンドプレフィックスの設定
    command_prefix = os.getenv('COMMAND_PREFIX', '!')
    
    # Botの作成
    bot = commands.Bot(command_prefix=command_prefix, intents=intents)
    
    @bot.event
    async def on_ready():
        """ボットの準備完了時に呼び出されるイベント"""
        logger.info(f'{bot.user.name} ({bot.user.id}) がDiscordに接続しました')
        logger.info(f'コマンドプレフィックス: {command_prefix}')
        
        # アクティビティを設定
        activity = discord.Game(name=f"{command_prefix}roll help")
        await bot.change_presence(activity=activity)
    
    @bot.event
    async def on_command_error(ctx, error):
        """グローバルなコマンドエラーハンドラ"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"コマンドが見つかりません。`{command_prefix}roll help` でヘルプを表示できます。")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"コマンドに必要な引数が不足しています。`{command_prefix}roll help` でヘルプを表示できます。")
        else:
            logger.error(f"未処理のエラー: {error}")
            await ctx.send("コマンドの実行中にエラーが発生しました。")
    
    # Cogの読み込み
    try:
        await bot.load_extension('dice_cog')
        logger.info("Cogの読み込みが完了しました")
    except Exception as e:
        logger.error(f"Cogの読み込み中にエラーが発生しました: {e}")
    
    # ボット起動
    try:
        logger.info("ボットを起動します...")
        await bot.start(token)
    except discord.errors.LoginFailure:
        logger.critical("無効なトークンです。トークンが正しいか確認してください。")
    except Exception as e:
        logger.critical(f"ボットの起動中に予期せぬエラーが発生しました: {e}")

if __name__ == '__main__':
    # ログ設定
    logger = setup_logging()
    logger.info("ダイスボットを起動します")
    
    # 非同期メイン関数の実行
    asyncio.run(main()) 