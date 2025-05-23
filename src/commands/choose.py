"""
ランダム選択コマンドを提供するモジュール
"""
import discord
from discord import app_commands
from discord.ext import commands
import os
import sys
from typing import List, Optional

# パスを追加して必要なモジュールをインポートできるようにする
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from dice.src.utils.logger import get_logger
from dice.src.randomizers.selector import (
    select_random_item,
    select_random_multiple,
    shuffle_list,
    create_teams
)

logger = get_logger()

def setup_choose_command(bot: commands.Bot):
    """
    ランダム選択コマンドをボットに登録する
    
    引数:
        bot: コマンドを登録するBot
    """
    logger.info("ランダム選択コマンドを設定中...")
    
    # グループコマンドの作成
    choose_group = app_commands.Group(
        name="choose", 
        description="ランダム選択コマンド",
    )
    
    @choose_group.command(name="one", description="リストからランダムに1つの項目を選択します")
    async def choose_one(
        interaction: discord.Interaction, 
        items: str
    ):
        """リストからランダムに1つの項目を選択するコマンド"""
        # 項目を分割
        item_list = [item.strip() for item in items.split(',') if item.strip()]
        
        if not item_list:
            await interaction.response.send_message("選択肢を入力してください。カンマ区切りで複数指定できます。", ephemeral=True)
            return
            
        # ランダム選択
        selected, index = select_random_item(item_list)
        
        # 結果の表示
        embed = discord.Embed(
            title="🎲 ランダム選択",
            description=f"**{len(item_list)}個**の選択肢から選びました",
            color=0x3498db
        )
        embed.add_field(name="選ばれたのは...", value=f"**{selected}**", inline=False)
        
        await interaction.response.send_message(embed=embed)
        
    @choose_group.command(name="multiple", description="リストからランダムに複数の項目を選択します")
    async def choose_multiple(
        interaction: discord.Interaction, 
        items: str,
        count: int = 1,
        unique: bool = True
    ):
        """リストからランダムに複数の項目を選択するコマンド"""
        # 項目を分割
        item_list = [item.strip() for item in items.split(',') if item.strip()]
        
        if not item_list:
            await interaction.response.send_message("選択肢を入力してください。カンマ区切りで複数指定できます。", ephemeral=True)
            return
            
        if count < 1:
            await interaction.response.send_message("選択数は1以上を指定してください。", ephemeral=True)
            return
            
        # 重複なしの場合、選択数が項目数を超えないようにする
        if unique and count > len(item_list):
            count = len(item_list)
            
        # ランダム選択
        selected = select_random_multiple(item_list, count, unique)
        
        # 結果の表示
        embed = discord.Embed(
            title="🎲 複数ランダム選択",
            description=f"**{len(item_list)}個**の選択肢から**{count}個**選びました",
            color=0x3498db
        )
        
        result_text = "\n".join([f"• {item}" for item in selected])
        embed.add_field(name="選ばれたのは...", value=result_text if result_text else "なし", inline=False)
        
        await interaction.response.send_message(embed=embed)
        
    @choose_group.command(name="shuffle", description="リストの項目をランダムに並べ替えます")
    async def shuffle(
        interaction: discord.Interaction, 
        items: str
    ):
        """リストの項目をランダムに並べ替えるコマンド"""
        # 項目を分割
        item_list = [item.strip() for item in items.split(',') if item.strip()]
        
        if not item_list:
            await interaction.response.send_message("シャッフルする項目を入力してください。カンマ区切りで複数指定できます。", ephemeral=True)
            return
            
        # シャッフル
        shuffled = shuffle_list(item_list)
        
        # 結果の表示
        embed = discord.Embed(
            title="🔀 シャッフル結果",
            description=f"**{len(item_list)}個**の項目をシャッフルしました",
            color=0x3498db
        )
        
        result_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(shuffled)])
        embed.add_field(name="シャッフル後の順序", value=result_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
    @choose_group.command(name="teams", description="メンバーをランダムにチームに分けます")
    async def teams(
        interaction: discord.Interaction, 
        members: str,
        num_teams: int = 2
    ):
        """メンバーをランダムにチームに分けるコマンド"""
        # メンバーを分割
        member_list = [member.strip() for member in members.split(',') if member.strip()]
        
        if not member_list:
            await interaction.response.send_message("メンバーを入力してください。カンマ区切りで複数指定できます。", ephemeral=True)
            return
            
        if num_teams < 1:
            await interaction.response.send_message("チーム数は1以上を指定してください。", ephemeral=True)
            return
            
        # チーム分け
        teams = create_teams(member_list, num_teams)
        
        # 結果の表示
        embed = discord.Embed(
            title="👥 チーム分け結果",
            description=f"**{len(member_list)}人**を**{num_teams}チーム**に分けました",
            color=0x3498db
        )
        
        for i, team in enumerate(teams):
            team_members = "\n".join([f"• {member}" for member in team]) if team else "なし"
            embed.add_field(name=f"チーム {i+1}", value=team_members, inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    # コマンドグループをボットツリーに追加
    bot.tree.add_command(choose_group)
    logger.info("ランダム選択コマンドを設定しました") 