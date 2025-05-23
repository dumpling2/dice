"""
ランダム選択モジュール - ランダムな選択機能を提供します
"""
import random
from typing import List, Dict, Any, Union, Optional, Tuple
import os
import sys

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from dice.src.utils.logger import get_logger

logger = get_logger()

def select_random_item(items: List[Any]) -> Tuple[Any, int]:
    """
    リストからランダムに1つの項目を選択します
    
    引数:
        items: 選択対象のリスト
        
    戻り値:
        選択された項目と選択されたインデックスのタプル
    """
    if not items:
        logger.warning("空のリストから選択しようとしました")
        return None, -1
        
    index = random.randint(0, len(items) - 1)
    return items[index], index

def select_random_multiple(items: List[Any], count: int, unique: bool = True) -> List[Any]:
    """
    リストからランダムに複数の項目を選択します
    
    引数:
        items: 選択対象のリスト
        count: 選択する項目数
        unique: True=重複なしで選択, False=重複ありで選択
        
    戻り値:
        選択された項目のリスト
    """
    if not items:
        logger.warning("空のリストから選択しようとしました")
        return []
        
    if unique:
        # 重複なしの選択（選択数が元のリストより多い場合は全て選択）
        count = min(count, len(items))
        return random.sample(items, count)
    else:
        # 重複ありの選択
        return [random.choice(items) for _ in range(count)]

def weighted_select(items: List[Any], weights: List[float]) -> Any:
    """
    重み付けされたリストからランダムに1つの項目を選択します
    
    引数:
        items: 選択対象のリスト
        weights: 各項目の重み（確率）のリスト
        
    戻り値:
        選択された項目
    """
    if len(items) != len(weights):
        logger.error("項目リストと重みリストの長さが一致しません")
        return None
        
    if not items:
        logger.warning("空のリストから選択しようとしました")
        return None
        
    # 負の重みを0に変換
    weights = [max(0, w) for w in weights]
    
    # 全ての重みが0の場合、等確率で選択
    if sum(weights) == 0:
        logger.warning("すべての重みが0です。等確率で選択します。")
        return random.choice(items)
        
    return random.choices(items, weights=weights, k=1)[0]

def shuffle_list(items: List[Any]) -> List[Any]:
    """
    リストの項目をランダムに並べ替えます
    
    引数:
        items: 並べ替えるリスト
        
    戻り値:
        並べ替えられたリストのコピー
    """
    if not items:
        logger.warning("空のリストをシャッフルしようとしました")
        return []
        
    shuffled = items.copy()
    random.shuffle(shuffled)
    return shuffled

def create_teams(members: List[Any], num_teams: int) -> List[List[Any]]:
    """
    メンバーをランダムにチームに分けます
    
    引数:
        members: チーム分けするメンバーのリスト
        num_teams: 作成するチーム数
        
    戻り値:
        チームのリスト（各チームはメンバーのリスト）
    """
    if not members:
        logger.warning("空のメンバーリストからチームを作成しようとしました")
        return [[] for _ in range(num_teams)]
        
    if num_teams <= 0:
        logger.error("チーム数は1以上である必要があります")
        return [members]  # 全員1チーム
        
    # メンバーをシャッフル
    shuffled_members = shuffle_list(members)
    
    # チームを初期化
    teams = [[] for _ in range(num_teams)]
    
    # メンバーを各チームに分配
    for i, member in enumerate(shuffled_members):
        team_index = i % num_teams
        teams[team_index].append(member)
        
    return teams

def assign_roles(members: List[Any], roles: List[str]) -> Dict[Any, str]:
    """
    メンバーにランダムに役割を割り当てます
    
    引数:
        members: 役割を割り当てるメンバーのリスト
        roles: 割り当てる役割のリスト
        
    戻り値:
        メンバーと割り当てられた役割の辞書
    """
    if not members:
        logger.warning("空のメンバーリストに役割を割り当てようとしました")
        return {}
        
    if not roles:
        logger.warning("空の役割リストを割り当てようとしました")
        return {}
        
    # 各メンバーに役割を割り当て（役割が足りない場合は繰り返し使用）
    assignments = {}
    random_roles = roles.copy()
    
    for i, member in enumerate(members):
        # 役割リストが尽きたら再度シャッフルして使用
        if i % len(roles) == 0:
            random_roles = shuffle_list(roles)
            
        role_index = i % len(roles)
        assignments[member] = random_roles[role_index]
        
    return assignments 