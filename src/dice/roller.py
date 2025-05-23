"""
ダイスロールの実行ロジックを提供するモジュール
"""
import random
import sys
import os
from typing import List, Dict, Any, Tuple

# パスを追加して設定モジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from dice.src.utils.logger import get_logger
from dice.config.settings import get_config
from .parser import parse_complex_dice_notation

logger = get_logger()

def roll_dice(num_dice: int, num_sides: int) -> List[int]:
    """
    指定された数と面数のダイスを振る
    
    引数:
        num_dice: ダイスの数
        num_sides: ダイスの面数
        
    戻り値:
        各ダイスの出目のリスト
    """
    return [random.randint(1, num_sides) for _ in range(abs(num_dice))]

def roll_complex_dice(dice_str: str) -> Dict[str, Any]:
    """
    複雑なダイス表記に基づいてダイスを振る
    
    引数:
        dice_str: ダイス表記文字列
    
    戻り値:
        ダイスの結果を含む辞書
    """
    try:
        components = parse_complex_dice_notation(dice_str)
        if not components:
            return {"error": "無効なダイス表記です"}
        
        rolls_detail = []
        final_result = 0
        
        for num_dice, num_sides, modifier in components:
            if num_sides > 0:  # ダイスロール
                is_negative = num_dice < 0
                
                # バリデーション
                abs_num_dice = abs(num_dice)
                min_dice = get_config('MIN_DICE_COUNT', 1)
                max_dice = get_config('MAX_DICE_COUNT', 100)
                min_sides = get_config('MIN_DICE_SIDES', 2)
                max_sides = get_config('MAX_DICE_SIDES', 1000)
                
                if not (min_dice <= abs_num_dice <= max_dice):
                    return {"error": f"ダイスの数は{min_dice}から{max_dice}の間で指定してください"}
                if not (min_sides <= num_sides <= max_sides):
                    return {"error": f"ダイスの面は{min_sides}から{max_sides}の間で指定してください"}
                    
                rolls = roll_dice(num_dice, num_sides)
                
                # 負のダイス数の場合は結果を反転
                roll_sum = sum(rolls)
                if is_negative:
                    roll_sum = -roll_sum
                
                # 出目の最大値と最小値をチェック
                is_critical = all(roll == num_sides for roll in rolls) and len(rolls) > 0
                is_fumble = all(roll == 1 for roll in rolls) and len(rolls) > 0
                
                rolls_detail.append({
                    "type": "dice",
                    "notation": f"{'-' if is_negative else ''}{abs_num_dice}d{num_sides}",
                    "rolls": rolls,
                    "sum": roll_sum,
                    "negative": is_negative,
                    "is_critical": is_critical,
                    "is_fumble": is_fumble,
                    "sides": num_sides
                })
                
                final_result += roll_sum
            else:  # 修正値
                min_mod = get_config('MIN_MODIFIER', -1000)
                max_mod = get_config('MAX_MODIFIER', 1000)
                
                if not (min_mod <= modifier <= max_mod):
                    return {"error": f"修正値は{min_mod}から{max_mod}の間で指定してください"}
                    
                rolls_detail.append({
                    "type": "modifier",
                    "value": modifier
                })
                final_result += modifier
        
        result = {
            "input": dice_str,
            "details": rolls_detail,
            "result": final_result
        }
        
        logger.debug(f"ダイスロール結果: {result}")
        return result
    except Exception as e:
        logger.error(f"ダイスロール中にエラー発生: {e}")
        return {"error": f"ダイスロール処理中にエラーが発生しました: {str(e)}"} 