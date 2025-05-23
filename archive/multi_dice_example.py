"""
複数種類のダイスをサポートするロール機能の実装例
例: !roll 1d20+2d6+3
"""

import re
import random
from typing import List, Tuple

def parse_complex_dice_notation(dice_str: str) -> List[Tuple[int, int, int]]:
    """
    複雑なダイス表記をパースする
    
    例:
        "1d20+2d6+3" -> [(1, 20, 0), (2, 6, 0), (0, 0, 3)]
        
    戻り値:
        (ダイス数, 面数, 修正値) のタプルのリスト
    """
    # 文字列から空白を削除
    dice_str = dice_str.replace(" ", "")
    
    # 加算と減算で分割
    components = re.findall(r'([+-]?\d*d\d+|[+-]?\d+)', dice_str)
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
        
        if 'd' in comp:
            # ダイス表記の処理
            parts = comp.split('d')
            num_dice = int(parts[0]) if parts[0] else 1
            num_sides = int(parts[1])
            result.append((sign * num_dice, num_sides, 0))
        else:
            # 単純な数値の処理
            result.append((0, 0, sign * int(comp)))
    
    return result

def roll_dice(num_dice: int, num_sides: int) -> List[int]:
    """指定された数と面数のダイスを振る"""
    return [random.randint(1, num_sides) for _ in range(abs(num_dice))]

def roll_complex_dice(dice_str: str) -> dict:
    """
    複雑なダイス表記に基づいてダイスを振る
    
    戻り値:
        ダイスの結果を含む辞書
    """
    components = parse_complex_dice_notation(dice_str)
    if not components:
        return {"error": "無効なダイス表記です"}
    
    rolls_detail = []
    final_result = 0
    
    for num_dice, num_sides, modifier in components:
        if num_sides > 0:  # ダイスロール
            is_negative = num_dice < 0
            rolls = roll_dice(num_dice, num_sides)
            
            # 負のダイス数の場合は結果を反転
            roll_sum = sum(rolls)
            if is_negative:
                roll_sum = -roll_sum
            
            rolls_detail.append({
                "type": "dice",
                "notation": f"{'-' if is_negative else ''}{abs(num_dice)}d{num_sides}",
                "rolls": rolls,
                "sum": roll_sum,
                "negative": is_negative
            })
            
            final_result += roll_sum
        else:  # 修正値
            rolls_detail.append({
                "type": "modifier",
                "value": modifier
            })
            final_result += modifier
    
    return {
        "input": dice_str,
        "details": rolls_detail,
        "result": final_result
    }

def format_roll_result(result: dict) -> str:
    """ロール結果を整形された文字列に変換する"""
    if "error" in result:
        return f"エラー: {result['error']}"
    
    output = f"入力: `{result['input']}`\n結果: **{result['result']}**\n\n詳細:\n"
    
    for detail in result["details"]:
        if detail["type"] == "dice":
            rolls_str = ", ".join(map(str, detail["rolls"]))
            output += f"・`{detail['notation']}`: [{rolls_str}] = {detail['sum']}\n"
        else:
            output += f"・修正値: {detail['value']}\n"
    
    return output

# 使用例
if __name__ == "__main__":
    test_notations = [
        "1d20+5",
        "2d6-1",
        "d20+2d4+3",
        "1d20+2d6+1d8-3",
        "3"
    ]
    
    for notation in test_notations:
        print(f"\n===== {notation} =====")
        result = roll_complex_dice(notation)
        print(format_roll_result(result)) 