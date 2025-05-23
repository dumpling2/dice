"""
抽選コマンドを提供するモジュール
"""
import discord
from discord import app_commands
from discord.ext import commands
import os
import sys
from typing import List, Optional
import asyncio

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from dice.src.utils.logger import get_logger
from dice.src.randomizers.lottery import (
    draw_lottery,
    draw_tiered_lottery,
    tournament_draw
)

logger = get_logger()

def setup_lottery_command(bot: commands.Bot):
    """
    抽選コマンドをボットに登録する
    
    引数:
        bot: コマンドを登録するBot
    """
    logger.info("抽選コマンドを設定中...")
    
    # グループコマンドの作成
    lottery_group = app_commands.Group(
        name="lottery", 
        description="抽選コマンド",
    )
    
    @lottery_group.command(name="draw", description="参加者から当選者を抽選します")
    async def lottery_draw(
        interaction: discord.Interaction, 
        participants: str,
        winners_count: int = 1,
        announce_delay: int = 3
    ):
        """参加者リストから当選者を抽選するコマンド"""
        # 参加者を分割
        participant_list = [p.strip() for p in participants.split(',') if p.strip()]
        
        if not participant_list:
            await interaction.response.send_message("参加者リストを入力してください。カンマ区切りで複数指定できます。", ephemeral=True)
            return
            
        if winners_count < 1:
            await interaction.response.send_message("当選者数は1以上を指定してください。", ephemeral=True)
            return
            
        # 抽選を実行
        winners = draw_lottery(participant_list, winners_count)
        
        # 結果表示の準備
        embed = discord.Embed(
            title="🎉 抽選結果",
            description=f"**{len(participant_list)}人**の参加者から**{len(winners)}人**を抽選しました",
            color=0xf1c40f
        )
        
        # 抽選演出（遅延表示）
        if announce_delay > 0 and announce_delay <= 10:
            await interaction.response.send_message("🥁 抽選中...", ephemeral=False)
            await asyncio.sleep(announce_delay)
            
            # 結果の表示
            result_text = "\n".join([f"🏆 **{winner}**" for winner in winners])
            embed.add_field(name="当選者", value=result_text if result_text else "該当者なし", inline=False)
            
            await interaction.edit_original_response(content="", embed=embed)
        else:
            # 演出なしですぐに結果表示
            result_text = "\n".join([f"🏆 **{winner}**" for winner in winners])
            embed.add_field(name="当選者", value=result_text if result_text else "該当者なし", inline=False)
            
            await interaction.response.send_message(embed=embed)
        
    @lottery_group.command(name="tiered", description="複数の賞品に対して当選者を抽選します")
    async def tiered_lottery(
        interaction: discord.Interaction, 
        participants: str,
        first_prize_count: int = 1,
        second_prize_count: int = 2,
        third_prize_count: int = 3,
        announce_delay: int = 3
    ):
        """複数賞品の当選者を抽選するコマンド"""
        # 参加者を分割
        participant_list = [p.strip() for p in participants.split(',') if p.strip()]
        
        if not participant_list:
            await interaction.response.send_message("参加者リストを入力してください。カンマ区切りで複数指定できます。", ephemeral=True)
            return
            
        # 賞品と当選者数の設定
        prize_tiers = {
            "一等賞": max(0, first_prize_count),
            "二等賞": max(0, second_prize_count),
            "三等賞": max(0, third_prize_count)
        }
        
        # 賞品が全て0の場合はエラー
        if all(count == 0 for count in prize_tiers.values()):
            await interaction.response.send_message("少なくとも1つの賞品に1人以上の当選者数を設定してください。", ephemeral=True)
            return
            
        # 抽選を実行
        results = draw_tiered_lottery(participant_list, prize_tiers)
        
        # 結果表示の準備
        embed = discord.Embed(
            title="🎊 階層的抽選結果",
            description=f"**{len(participant_list)}人**の参加者から抽選しました",
            color=0xf1c40f
        )
        
        # 抽選演出（遅延表示）
        if announce_delay > 0 and announce_delay <= 10:
            await interaction.response.send_message("🥁 抽選中...", ephemeral=False)
            await asyncio.sleep(announce_delay)
            
            # 結果の表示（逆順で表示 - 三等賞→一等賞）
            for prize in reversed(list(results.keys())):
                winners = results[prize]
                result_text = "\n".join([f"• **{winner}**" for winner in winners])
                embed.add_field(name=f"🏆 {prize} ({len(winners)}名)", 
                               value=result_text if result_text else "該当者なし", 
                               inline=False)
            
            await interaction.edit_original_response(content="", embed=embed)
        else:
            # 演出なしですぐに結果表示
            for prize in reversed(list(results.keys())):
                winners = results[prize]
                result_text = "\n".join([f"• **{winner}**" for winner in winners])
                embed.add_field(name=f"🏆 {prize} ({len(winners)}名)", 
                               value=result_text if result_text else "該当者なし", 
                               inline=False)
            
            await interaction.response.send_message(embed=embed)
        
    @lottery_group.command(name="tournament", description="トーナメント表を生成します")
    async def tournament(
        interaction: discord.Interaction, 
        participants: str,
        rounds: int = 2
    ):
        """トーナメント表を生成するコマンド"""
        # 参加者を分割
        participant_list = [p.strip() for p in participants.split(',') if p.strip()]
        
        if not participant_list:
            await interaction.response.send_message("参加者リストを入力してください。カンマ区切りで複数指定できます。", ephemeral=True)
            return
            
        if rounds < 1 or rounds > 6:
            await interaction.response.send_message("ラウンド数は1〜6の範囲で指定してください。", ephemeral=True)
            return
            
        # トーナメント表を生成
        tournament = tournament_draw(participant_list, rounds)
        
        # 結果表示の準備
        embed = discord.Embed(
            title="🏆 トーナメント表",
            description=f"**{len(participant_list)}人**の参加者でトーナメントを作成しました",
            color=0xf1c40f
        )
        
        # トーナメント表の表示
        for round_num, matches in tournament.items():
            round_text = []
            for i, (player1, player2) in enumerate(matches):
                round_text.append(f"試合{i+1}: **{player1}** vs **{player2}**")
            
            embed.add_field(
                name=f"ラウンド {round_num} ({len(matches)}試合)",
                value="\n".join(round_text),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # コマンドグループをボットツリーに追加
    bot.tree.add_command(lottery_group)
    logger.info("抽選コマンドを設定しました") 