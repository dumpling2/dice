#!/usr/bin/env python
"""
Discord ダイスボット ランチャー
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

def check_env_file():
    """環境変数ファイルをチェック"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print(".envファイルが見つかりません。新しく作成します。")
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Discord Bot Token - 実際のトークンに置き換えてください\n")
            f.write("DISCORD_BOT_TOKEN=your_bot_token_here\n\n")
            f.write("# コマンドプレフィックス設定（デフォルト: !）\n")
            f.write("COMMAND_PREFIX=!\n")
            f.write("\n# ロギングレベル（INFO/DEBUG/WARNING/ERROR）\n")
            f.write("LOG_LEVEL=INFO\n")
        print(f".envファイルが作成されました: {env_path}")
        print("DISCORD_BOT_TOKENを設定してください。")
    return True

if __name__ == "__main__":
    # 実行環境のチェック
    if sys.version_info < (3, 8):
        print("Python 3.8以上が必要です")
        sys.exit(1)
        
    # 環境変数ファイルをチェック
    check_env_file()
    
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(description="Discord ダイスボット")
    parser.add_argument('--debug', action='store_true', 
                        help="デバッグモードで実行")
    
    args = parser.parse_args()
    
    # ログレベルの設定
    log_level = logging.DEBUG if args.debug else logging.INFO
    
    try:
        from src.bot import start_bot
        start_bot(log_level)
    except ImportError:
        print("srcディレクトリが見つかりません。正しいディレクトリで実行してください。")
        sys.exit(1)
    except Exception as e:
        print(f"起動エラー: {e}")
        sys.exit(1) 