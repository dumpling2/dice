"""
ダイス結果の表示ロジックを提供するモジュール
"""
import discord
import datetime
from typing import Dict, Any
from discord.ext import commands

import sys
import os

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from dice.src.utils.logger import get_logger

logger = get_logger()

def create_dice_embed(ctx: commands.Context, result: Dict[str, Any]) -> discord.Embed:
    """
    ダイスロール結果用のEmbedsを作成する
    
    引数:
        ctx: コマンドコンテキスト
        result: ダイスロール結果
        
    戻り値:
        Embedオブジェクト
    """
    try:
        # ロール結果から色を決定
        is_critical = any(detail.get("is_critical", False) for detail in result["details"] if detail["type"] == "dice")
        is_fumble = any(detail.get("is_fumble", False) for detail in result["details"] if detail["type"] == "dice")
        
        # Embedの色を決定
        if is_critical:
            color = discord.Color.gold()
        elif is_fumble:
            color = discord.Color.dark_red()
        else:
            color = discord.Color.blue()
        
        # Embedを作成
        embed = discord.Embed(
            title=f"🎲 ダイスロール: {result['input']}",
            description=f"{ctx.author.display_name}さんのロール結果",
            color=color,
            timestamp=datetime.datetime.now()
        )
        
        # アイコンを設定
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        # 各ダイスの詳細を表示
        for detail in result["details"]:
            if detail["type"] == "dice":
                rolls_str = ", ".join(map(str, detail["rolls"]))
                embed.add_field(
                    name=f"{detail['notation']}",
                    value=f"[{rolls_str}] = **{detail['sum']}**",
                    inline=False
                )
            else:
                embed.add_field(
                    name="修正値",
                    value=f"{detail['value']:+}",
                    inline=False
                )
        
        # 最終結果
        embed.add_field(name="最終結果", value=f"**{result['result']}**", inline=False)
        
        # クリティカル/ファンブルの場合のフッター
        if is_critical:
            embed.set_footer(text="🎉 クリティカル！ 大成功です！")
        elif is_fumble:
            embed.set_footer(text="💥 ファンブル！ 大失敗です！")
        
        return embed
    except Exception as e:
        logger.error(f"Embed作成中にエラー: {e}")
        
        # エラー時の簡易Embed
        embed = discord.Embed(
            title="ダイスロールエラー",
            description="結果の表示中にエラーが発生しました",
            color=discord.Color.red()
        )
        return embed 