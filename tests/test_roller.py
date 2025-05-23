"""
ダイスロール機能のテスト
"""
import unittest
import sys
import os
from unittest.mock import patch

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from src.dice.roller import roll_dice, roll_complex_dice

class TestDiceRoller(unittest.TestCase):
    """ダイスローラーのテストクラス"""
    
    def test_roll_dice(self):
        """基本的なダイスロールのテスト"""
        # 1個のダイス
        result = roll_dice(1, 6)
        self.assertEqual(len(result), 1)
        self.assertTrue(1 <= result[0] <= 6)
        
        # 複数のダイス
        result = roll_dice(3, 20)
        self.assertEqual(len(result), 3)
        for value in result:
            self.assertTrue(1 <= value <= 20)
        
        # 負の数のダイス（絶対値が使われる）
        result = roll_dice(-2, 4)
        self.assertEqual(len(result), 2)
        for value in result:
            self.assertTrue(1 <= value <= 4)
    
    @patch('src.dice.roller.roll_dice')
    def test_roll_complex_dice_basic(self, mock_roll_dice):
        """基本的な複合ダイスロールのテスト（モック使用）"""
        # モックの設定
        mock_roll_dice.return_value = [3]
        
        # 基本的なダイスロール
        result = roll_complex_dice("1d6")
        self.assertEqual(result["input"], "1d6")
        self.assertEqual(result["result"], 3)
        self.assertEqual(len(result["details"]), 1)
        self.assertEqual(result["details"][0]["type"], "dice")
        self.assertEqual(result["details"][0]["rolls"], [3])
        
        # モックの呼び出し確認
        mock_roll_dice.assert_called_with(1, 6)
    
    @patch('src.dice.roller.roll_dice')
    def test_roll_complex_dice_with_modifier(self, mock_roll_dice):
        """修正値付きの複合ダイスロールのテスト（モック使用）"""
        # モックの設定
        mock_roll_dice.return_value = [15]
        
        # 修正値付きダイスロール
        result = roll_complex_dice("1d20+5")
        self.assertEqual(result["input"], "1d20+5")
        self.assertEqual(result["result"], 20)  # 15 + 5
        self.assertEqual(len(result["details"]), 2)
        
        # ダイス部分の確認
        self.assertEqual(result["details"][0]["type"], "dice")
        self.assertEqual(result["details"][0]["rolls"], [15])
        
        # 修正値部分の確認
        self.assertEqual(result["details"][1]["type"], "modifier")
        self.assertEqual(result["details"][1]["value"], 5)
        
        # モックの呼び出し確認
        mock_roll_dice.assert_called_with(1, 20)
    
    def test_roll_complex_dice_validation(self):
        """複合ダイスロールの検証テスト"""
        # 無効なダイス表記
        result = roll_complex_dice("invalid")
        self.assertIn("error", result)
        
        # ダイス数の制限チェック
        result = roll_complex_dice("1000d6")  # 最大100個
        self.assertIn("error", result)
        
        # ダイス面の制限チェック
        result = roll_complex_dice("1d1")  # 最小2面
        self.assertIn("error", result)
        result = roll_complex_dice("1d2000")  # 最大1000面
        self.assertIn("error", result)
        
        # 修正値の制限チェック
        result = roll_complex_dice("1d6+2000")  # 最大1000
        self.assertIn("error", result)
    
    @patch('src.dice.roller.roll_dice')
    def test_critical_fumble_detection(self, mock_roll_dice):
        """クリティカル/ファンブル判定のテスト"""
        # クリティカル（最大値）
        mock_roll_dice.return_value = [20]
        result = roll_complex_dice("1d20")
        self.assertTrue(result["details"][0]["is_critical"])
        self.assertFalse(result["details"][0]["is_fumble"])
        
        # ファンブル（最小値）
        mock_roll_dice.return_value = [1]
        result = roll_complex_dice("1d20")
        self.assertFalse(result["details"][0]["is_critical"])
        self.assertTrue(result["details"][0]["is_fumble"])
        
        # 複数ダイスのクリティカル
        mock_roll_dice.return_value = [6, 6]
        result = roll_complex_dice("2d6")
        self.assertTrue(result["details"][0]["is_critical"])
        
        # 複数ダイスのファンブル
        mock_roll_dice.return_value = [1, 1]
        result = roll_complex_dice("2d6")
        self.assertTrue(result["details"][0]["is_fumble"])
        
        # クリティカルでもファンブルでもない
        mock_roll_dice.return_value = [2, 5]
        result = roll_complex_dice("2d6")
        self.assertFalse(result["details"][0]["is_critical"])
        self.assertFalse(result["details"][0]["is_fumble"])

if __name__ == "__main__":
    unittest.main() 