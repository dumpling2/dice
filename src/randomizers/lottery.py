"""
抽選モジュール - 各種抽選機能を提供します
"""
import random
from typing import List, Dict, Any, Union, Optional, Tuple
import os
import sys
from collections import defaultdict

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from dice.src.utils.logger import get_logger
from dice.src.randomizers.selector import shuffle_list

logger = get_logger()

def draw_lottery(participants: List[str], winners_count: int) -> List[str]:
    """
    参加者リストから指定数の当選者をランダムに抽選します
    
    引数:
        participants: 参加者リスト
        winners_count: 当選者数
        
    戻り値:
        当選者リスト
    """
    if not participants:
        logger.warning("空の参加者リストから抽選しようとしました")
        return []
        
    # 当選者数が参加者数を超えないようにする
    actual_count = min(winners_count, len(participants))
    
    # 重複なしでランダムに選択
    winners = random.sample(participants, actual_count)
    
    logger.info(f"{len(participants)}人の参加者から{actual_count}人を抽選しました")
    return winners

def draw_tiered_lottery(participants: List[str], prize_tiers: Dict[str, int]) -> Dict[str, List[str]]:
    """
    参加者リストから複数の賞品に対して当選者を抽選します
    
    引数:
        participants: 参加者リスト
        prize_tiers: 賞品名と当選者数の辞書（例: {"一等賞": 1, "二等賞": 3, "三等賞": 5}）
        
    戻り値:
        賞品ごとの当選者リストの辞書
    """
    if not participants:
        logger.warning("空の参加者リストから抽選しようとしました")
        return {prize: [] for prize in prize_tiers}
        
    if not prize_tiers:
        logger.warning("賞品リストが指定されていません")
        return {}
        
    # 参加者リストをシャッフル
    remaining = participants.copy()
    random.shuffle(remaining)
    
    # 賞品ごとに当選者を抽選
    result = {}
    
    # 賞品を優先度順にソート（辞書順）
    sorted_prizes = sorted(prize_tiers.keys())
    
    for prize in sorted_prizes:
        count = prize_tiers[prize]
        # 残りの参加者から抽選
        winners_count = min(count, len(remaining))
        
        if winners_count > 0:
            # 当選者を選択
            winners = remaining[:winners_count]
            result[prize] = winners
            
            # 当選者を残りのリストから削除
            remaining = remaining[winners_count:]
        else:
            result[prize] = []
    
    return result

def draw_weighted_lottery(participants: List[str], weights: List[float], winners_count: int) -> List[str]:
    """
    重み付けされた参加者リストから当選者を抽選します
    
    引数:
        participants: 参加者リスト
        weights: 各参加者の当選確率の重み
        winners_count: 当選者数
        
    戻り値:
        当選者リスト
    """
    if not participants:
        logger.warning("空の参加者リストから抽選しようとしました")
        return []
        
    if len(participants) != len(weights):
        logger.error("参加者リストと重みリストの長さが一致しません")
        # 等確率で抽選
        weights = [1] * len(participants)
    
    # 負の重みを0に変換
    weights = [max(0, w) for w in weights]
    
    # 当選者数が参加者数を超えないようにする
    actual_count = min(winners_count, len(participants))
    
    winners = []
    remaining_participants = participants.copy()
    remaining_weights = weights.copy()
    
    for _ in range(actual_count):
        if not remaining_participants:
            break
            
        # 重みに基づいて1人選択
        if sum(remaining_weights) == 0:  # すべての重みが0の場合
            idx = random.randrange(len(remaining_participants))
        else:
            idx = random.choices(range(len(remaining_participants)), 
                                weights=remaining_weights, k=1)[0]
        
        # 当選者を追加
        winners.append(remaining_participants[idx])
        
        # 当選者を削除
        remaining_participants.pop(idx)
        remaining_weights.pop(idx)
    
    return winners

def tournament_draw(participants: List[str], rounds: int) -> Dict[int, List[Tuple[str, str]]]:
    """
    トーナメント表を生成します
    
    引数:
        participants: 参加者リスト
        rounds: トーナメントのラウンド数
        
    戻り値:
        ラウンドごとの対戦カードの辞書
    """
    if not participants:
        logger.warning("空の参加者リストからトーナメントを作成しようとしました")
        return {}
    
    # 参加者をシャッフル
    shuffled = shuffle_list(participants)
    
    # 必要な参加者数（2のべき乗）を計算
    required_count = 2 ** rounds
    
    # 参加者が足りない場合はバイを追加
    while len(shuffled) < required_count:
        shuffled.append("BYE")  # バイ（不戦勝）
    
    # 参加者が多すぎる場合は切り捨て
    if len(shuffled) > required_count:
        shuffled = shuffled[:required_count]
    
    # トーナメント表を構築
    tournament = {}
    current_round = shuffled
    
    for r in range(1, rounds + 1):
        matches = []
        for i in range(0, len(current_round), 2):
            if i + 1 < len(current_round):
                matches.append((current_round[i], current_round[i+1]))
            else:
                # 奇数の場合、最後の参加者はバイ
                matches.append((current_round[i], "BYE"))
        
        tournament[r] = matches
        
        # 次のラウンドの参加者を準備（仮の勝者として最初の参加者を選択）
        current_round = [match[0] for match in matches]
    
    return tournament 