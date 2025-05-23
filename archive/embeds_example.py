"""
Discord Embedsを活用したダイスロール結果表示の改善例
"""

import discord
from discord.ext import commands
import random
import datetime

# Embedsを使用したダイスロール結果の表示関数
async def send_dice_result_embed(ctx, dice_str, rolls, total_roll, modifier, final_result):
    """
    Embedsを使用してダイスロール結果を表示する
    
    引数:
        ctx: コマンドコンテキスト
        dice_str: ダイス表記 (例: "2d6+3")
        rolls: ダイスの出目リスト
        total_roll: ダイスの合計値
        modifier: 修正値
        final_result: 最終結果
    """
    # 出目の最大値と最小値をチェック
    num_sides = int(dice_str.split('d')[1].split('+')[0].split('-')[0])
    is_critical = all(roll == num_sides for roll in rolls)
    is_fumble = all(roll == 1 for roll in rolls)
    
    # Embedの色を決定
    if is_critical:
        color = discord.Color.gold()  # クリティカルの場合は金色
    elif is_fumble:
        color = discord.Color.dark_red()  # ファンブルの場合は暗い赤
    else:
        color = discord.Color.blue()  # 通常は青
    
    # Embedを作成
    embed = discord.Embed(
        title=f"🎲 ダイスロール: {dice_str}",
        description=f"{ctx.author.display_name}さんのロール結果",
        color=color,
        timestamp=datetime.datetime.now()
    )
    
    # アイコンを設定
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    # フィールドを追加
    # 出目の詳細
    rolls_str = " + ".join([f"**{roll}**" for roll in rolls])
    embed.add_field(name="出目", value=rolls_str, inline=False)
    
    # 合計
    embed.add_field(name="出目の合計", value=f"**{total_roll}**", inline=True)
    
    # 修正値（存在する場合）
    if modifier != 0:
        embed.add_field(name="修正値", value=f"{modifier:+}", inline=True)
    
    # 最終結果
    embed.add_field(name="最終結果", value=f"**{final_result}**", inline=True)
    
    # クリティカル/ファンブルの場合のフッター
    if is_critical:
        embed.set_footer(text="🎉 クリティカル！ 大成功です！")
    elif is_fumble:
        embed.set_footer(text="💥 ファンブル！ 大失敗です！")
    else:
        embed.set_footer(text=f"ダイスボット | {ctx.bot.user.name}")
    
    # Embedを送信
    await ctx.send(embed=embed)

# ボタン付きのダイスロール結果表示の例
class DiceRollView(discord.ui.View):
    def __init__(self, dice_str, ctx):
        super().__init__(timeout=60)  # ボタンは60秒後に無効化
        self.dice_str = dice_str
        self.ctx = ctx
    
    @discord.ui.button(label="再ロール", style=discord.ButtonStyle.primary, emoji="🎲")
    async def reroll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """再ロールボタンが押された時の処理"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("他の人のロールは再ロールできません", ephemeral=True)
            return
        
        # パース処理（簡略化）
        parts = self.dice_str.split('d')
        num_dice = int(parts[0]) if parts[0] else 1
        
        if '+' in parts[1]:
            num_sides_str, modifier_str = parts[1].split('+')
            num_sides = int(num_sides_str)
            modifier = int(modifier_str)
        elif '-' in parts[1]:
            num_sides_str, modifier_str = parts[1].split('-')
            num_sides = int(num_sides_str)
            modifier = -int(modifier_str)
        else:
            num_sides = int(parts[1])
            modifier = 0
        
        # ダイスを振る
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total_roll = sum(rolls)
        final_result = total_roll + modifier
        
        # 結果を表示
        embed = interaction.message.embeds[0]
        embed.title = f"🎲 ダイスロール（再）: {self.dice_str}"
        
        # 色の更新
        is_critical = all(roll == num_sides for roll in rolls)
        is_fumble = all(roll == 1 for roll in rolls)
        
        if is_critical:
            embed.color = discord.Color.gold()
            embed.set_footer(text="🎉 クリティカル！ 大成功です！")
        elif is_fumble:
            embed.color = discord.Color.dark_red()
            embed.set_footer(text="💥 ファンブル！ 大失敗です！")
        else:
            embed.color = discord.Color.blue()
            embed.set_footer(text=f"ダイスボット | {self.ctx.bot.user.name}")
        
        # フィールドの更新
        rolls_str = " + ".join([f"**{roll}**" for roll in rolls])
        embed.set_field_at(0, name="出目", value=rolls_str, inline=False)
        embed.set_field_at(1, name="出目の合計", value=f"**{total_roll}**", inline=True)
        
        if modifier != 0:
            embed.set_field_at(2, name="修正値", value=f"{modifier:+}", inline=True)
            embed.set_field_at(3, name="最終結果", value=f"**{final_result}**", inline=True)
        else:
            embed.set_field_at(2, name="最終結果", value=f"**{final_result}**", inline=True)
        
        # 結果を更新
        await interaction.response.edit_message(embed=embed, view=self)

# 実際のコマンド実装例
@commands.command(name='roll_embed')
async def roll_dice_embed(ctx, dice_str: str):
    """Embedsを使用してダイスロール結果を表示するコマンド例"""
    # ダイス表記をパース（簡略化）
    parts = dice_str.split('d')
    num_dice = int(parts[0]) if parts[0] else 1
    
    if '+' in parts[1]:
        num_sides_str, modifier_str = parts[1].split('+')
        num_sides = int(num_sides_str)
        modifier = int(modifier_str)
    elif '-' in parts[1]:
        num_sides_str, modifier_str = parts[1].split('-')
        num_sides = int(num_sides_str)
        modifier = -int(modifier_str)
    else:
        num_sides = int(parts[1])
        modifier = 0
    
    # ダイスを振る
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    total_roll = sum(rolls)
    final_result = total_roll + modifier
    
    # Embedsで結果を表示
    embed = create_dice_embed(ctx, dice_str, rolls, total_roll, modifier, final_result)
    
    # ボタン付きで表示
    view = DiceRollView(dice_str, ctx)
    await ctx.send(embed=embed, view=view)

def create_dice_embed(ctx, dice_str, rolls, total_roll, modifier, final_result):
    """Embedsを作成する関数（ボタン表示用に分離）"""
    # 出目の最大値と最小値をチェック
    num_sides = int(dice_str.split('d')[1].split('+')[0].split('-')[0])
    is_critical = all(roll == num_sides for roll in rolls)
    is_fumble = all(roll == 1 for roll in rolls)
    
    # Embedの色を決定
    if is_critical:
        color = discord.Color.gold()
    elif is_fumble:
        color = discord.Color.dark_red()
    else:
        color = discord.Color.blue()
    
    # Embedを作成
    embed = discord.Embed(
        title=f"🎲 ダイスロール: {dice_str}",
        description=f"{ctx.author.display_name}さんのロール結果",
        color=color,
        timestamp=datetime.datetime.now()
    )
    
    # アイコンを設定
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    # フィールドを追加
    rolls_str = " + ".join([f"**{roll}**" for roll in rolls])
    embed.add_field(name="出目", value=rolls_str, inline=False)
    embed.add_field(name="出目の合計", value=f"**{total_roll}**", inline=True)
    
    if modifier != 0:
        embed.add_field(name="修正値", value=f"{modifier:+}", inline=True)
    
    embed.add_field(name="最終結果", value=f"**{final_result}**", inline=True)
    
    if is_critical:
        embed.set_footer(text="🎉 クリティカル！ 大成功です！")
    elif is_fumble:
        embed.set_footer(text="💥 ファンブル！ 大失敗です！")
    else:
        embed.set_footer(text=f"ダイスボット | {ctx.bot.user.name}")
    
    return embed 