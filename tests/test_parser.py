"""
ダイス表記パーサーのテスト
"""
import unittest
import sys
import os

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from src.dice.parser import parse_complex_dice_notation, validate_dice_notation

class TestDiceParser(unittest.TestCase):
    """ダイス表記パーサーのテストクラス"""
    
    def test_basic_dice_notation(self):
        """基本的なダイス表記のテスト"""
        # 単一ダイス
        result = parse_complex_dice_notation("d20")
        self.assertEqual(result, [(1, 20, 0)])
        
        # 複数ダイス
        result = parse_complex_dice_notation("2d6")
        self.assertEqual(result, [(2, 6, 0)])
        
        # 負のダイス
        result = parse_complex_dice_notation("-1d4")
        self.assertEqual(result, [(-1, 4, 0)])
    
    def test_dice_with_modifier(self):
        """修正値付きダイス表記のテスト"""
        # 修正値のみ
        result = parse_complex_dice_notation("5")
        self.assertEqual(result, [(0, 0, 5)])
        
        # ダイス+修正値
        result = parse_complex_dice_notation("1d20+5")
        self.assertEqual(result, [(1, 20, 0), (0, 0, 5)])
        
        # ダイス-修正値
        result = parse_complex_dice_notation("2d6-3")
        self.assertEqual(result, [(2, 6, 0), (0, 0, -3)])
    
    def test_complex_dice_notation(self):
        """複雑なダイス表記のテスト"""
        # 複数ダイス+修正値
        result = parse_complex_dice_notation("1d20+2d4+3")
        self.assertEqual(result, [(1, 20, 0), (2, 4, 0), (0, 0, 3)])
        
        # 複数の修正値
        result = parse_complex_dice_notation("1d8+2-1")
        self.assertEqual(result, [(1, 8, 0), (0, 0, 2), (0, 0, -1)])
        
        # 複数の負のダイス
        result = parse_complex_dice_notation("2d10-1d4")
        self.assertEqual(result, [(2, 10, 0), (-1, 4, 0)])
    
    def test_validate_dice_notation(self):
        """ダイス表記の検証テスト"""
        # 有効なダイス表記
        is_valid, error = validate_dice_notation("2d6")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # 空のダイス表記
        is_valid, error = validate_dice_notation("")
        self.assertFalse(is_valid)
        self.assertEqual(error, "ダイス表記が空です")
        
        # 無効なダイス表記
        is_valid, error = validate_dice_notation("invalid")
        self.assertFalse(is_valid)
        self.assertEqual(error, "無効なダイス表記です")

if __name__ == "__main__":
    unittest.main() 