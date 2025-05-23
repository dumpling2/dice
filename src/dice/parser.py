"""
ダイス表記のパース機能を提供するモジュール
"""
import re
from typing import List, Tuple, Dict, Any, Optional

# 複雑なダイス表記をパースするための正規表現
complex_dice_pattern = re.compile(r'([+-]?\d*d\d+|[+-]?\d+)', re.IGNORECASE)
# 基本的なダイス表記をパースするための正規表現
basic_dice_pattern = re.compile(r"^(?:(\d+)d)?(\d+)(?:([+-])(\d+))?$", re.IGNORECASE)

def parse_complex_dice_notation(dice_str: str) -> List[Tuple[int, int, int]]:
    """
    複雑なダイス表記をパースする
    
    例:
        "1d20+2d6+3" -> [(1, 20, 0), (2, 6, 0), (0, 0, 3)]
        
    引数:
        dice_str: ダイス表記文字列
        
    戻り値:
        (ダイス数, 面数, 修正値) のタプルのリスト
    """
    # 文字列から空白を削除
    dice_str = dice_str.replace(" ", "")
    
    # 加算と減算で分割
    components = complex_dice_pattern.findall(dice_str)
    if not components:
        return []
    
    # 最初の要素が+で始まっていない場合、+を追加
    if not components[0].startswith('+') and not components[0].startswith('-'):
        components[0] = '+' + components[0]
    
    result = []
    for comp in components:
        sign = 1
        if comp.startswith('-'):
            sign = -1
            comp = comp[1:]
        elif comp.startswith('+'):
            comp = comp[1:]
        
        if 'd' in comp.lower():
            # ダイス表記の処理
            parts = comp.lower().split('d')
            num_dice = int(parts[0]) if parts[0] else 1
            num_sides = int(parts[1])
            result.append((sign * num_dice, num_sides, 0))
        else:
            # 単純な数値の処理
            result.append((0, 0, sign * int(comp)))
    
    return result

def validate_dice_notation(dice_str: str) -> Tuple[bool, Optional[str]]:
    """
    ダイス表記が有効かどうかを検証する
    
    引数:
        dice_str: ダイス表記文字列
        
    戻り値:
        (有効かどうか, エラーメッセージ)
    """
    try:
        dice_str = dice_str.strip()
        if not dice_str:
            return False, "ダイス表記が空です"
            
        components = parse_complex_dice_notation(dice_str)
        if not components:
            return False, "無効なダイス表記です"
            
        from ..utils.logger import get_logger
        logger = get_logger()
        logger.debug(f"ダイス表記パース結果: {components}")
        
        return True, None
    except Exception as e:
        from ..utils.logger import get_logger
        logger = get_logger()
        logger.error(f"ダイス表記の検証中にエラー: {e}")
        return False, f"ダイス表記のパース中にエラーが発生しました: {str(e)}" 