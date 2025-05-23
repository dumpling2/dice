"""
ロギングユーティリティモジュール
"""
import logging
import os
from typing import Optional

_logger: Optional[logging.Logger] = None

def setup_logger(level: int = logging.INFO) -> logging.Logger:
    """ロギングの設定"""
    global _logger
    
    if _logger is not None:
        return _logger
        
    # ログディレクトリの確認と作成
    logs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # ロギング設定
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(logs_dir, 'dice_bot.log'), 
                               encoding='utf-8')
        ]
    )
    _logger = logging.getLogger('dice_bot')
    return _logger

def get_logger() -> logging.Logger:
    """ロガーオブジェクトを取得"""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger 