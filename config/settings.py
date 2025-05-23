"""
設定管理モジュール
"""
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# ボット設定
BOT_CONFIG: Dict[str, Any] = {
    # Discord API関連
    'BOT_TOKEN': os.getenv('DISCORD_BOT_TOKEN', ''),
    'COMMAND_PREFIX': os.getenv('COMMAND_PREFIX', '!'),
    
    # ロギング設定
    'LOG_LEVEL': getattr(logging, os.getenv('LOG_LEVEL', 'INFO'), logging.INFO),
    
    # ダイス設定
    'MAX_DICE_COUNT': 100,
    'MIN_DICE_COUNT': 1,
    'MAX_DICE_SIDES': 1000,
    'MIN_DICE_SIDES': 2,
    'MAX_MODIFIER': 1000,
    'MIN_MODIFIER': -1000,
    
    # ロール履歴
    'MAX_HISTORY_SIZE': 10,
    
    # ボタン設定
    'BUTTON_TIMEOUT': 60,  # 秒
}

def get_config(key: str, default: Any = None) -> Any:
    """
    設定値を取得する
    
    引数:
        key: 取得する設定キー
        default: キーが存在しない場合のデフォルト値
        
    戻り値:
        設定値
    """
    return BOT_CONFIG.get(key, default) 