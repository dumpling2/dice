"""
Discord.pyのCogを使用したモジュール化されたダイスボットの例
"""

import discord
from discord.ext import commands
import random
import re
import logging

class DiceCog(commands.Cog):
    """ダイスロール機能を提供するCog"""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('dice_bot.dice_cog')
        
        # ユーザーごとのロール履歴を保存する辞書
        self.roll_history = {}
        
        # ダイス表記をパースするための正規表現パターン
        self.dice_pattern = re.compile(r"^(?:(\d+)d)?(\d+)(?:([+-])(\d+))?$", re.IGNORECASE)
    
    @commands.command(name='roll', help='ダイスを振ります。\n例: !roll 1d6, !roll 2d10+3, !roll d20-1')
    async def roll_dice(self, ctx, dice_str: str = None):
        """
        基本的なダイスロールコマンド
        """
        if dice_str == "help":
            await self._send_help_message(ctx)
            return
            
        if not dice_str:
            await ctx.send(f"ダイスの指定がありません。\n"
                        f"正しい形式: `{ctx.prefix}roll NdS[+/-M]` (例: `{ctx.prefix}roll 2d6`)\n"
                        f"`{ctx.prefix}roll help` で詳細を確認できます。")
            return
            
        self.logger.info(f"ロールコマンド受信: {ctx.author.name} が {dice_str} を実行")
        
        # ダイス表記のパース
        match = self.dice_pattern.match(dice_str)
        
        if not match:
            await ctx.send(f"'{dice_str}' は無効なダイス指定です。\n"
                        f"正しい形式: `NdS[+/-M]` (例: `2d6`, `d20+3`, `1d10-1`)\n"
                        f"`{ctx.prefix}roll help` で詳細を確認できます。")
            return
            
        num_dice_str, num_sides_str, modifier_sign, modifier_val_str = match.groups()
        
        # パラメータの解析
        try:
            num_dice = int(num_dice_str) if num_dice_str else 1
            num_sides = int(num_sides_str)
            modifier = 0
            if modifier_sign and modifier_val_str:
                modifier = int(modifier_val_str)
                if modifier_sign == '-':
                    modifier *= -1
                    
            # パラメータのバリデーション
            if not (1 <= num_dice <= 100):
                await ctx.send("ダイスの数は1から100の間で指定してください。")
                return
            if not (2 <= num_sides <= 1000):
                await ctx.send("ダイスの面は2から1000の間で指定してください。")
                return
            if not (-1000 <= modifier <= 1000):
                await ctx.send("修正値は-1000から1000の間で指定してください。")
                return
                
        except ValueError:
            await ctx.send("ダイス指定の解析中にエラーが発生しました。正しい形式か確認してください。")
            self.logger.error(f"ダイス解析エラー: {dice_str}")
            return
            
        # ダイスロール実行
        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total_roll = sum(rolls)
        final_result = total_roll + modifier
        
        # ロール履歴に追加
        user_id = ctx.author.id
        if user_id not in self.roll_history:
            self.roll_history[user_id] = []
            
        # 最大10件まで保存
        self.roll_history[user_id].append({
            "dice_str": dice_str,
            "rolls": rolls,
            "total": total_roll,
            "modifier": modifier,
            "result": final_result
        })
        
        if len(self.roll_history[user_id]) > 10:
            self.roll_history[user_id].pop(0)
            
        # 結果メッセージ作成
        result_message = f"{ctx.author.mention} が `{dice_str}` を振りました！\n"
        
        # クリティカルとファンブルの判定
        is_critical = all(roll == num_sides for roll in rolls)
        is_fumble = all(roll == 1 for roll in rolls)
        
        if is_critical:
            result_message += "🎉 **クリティカル！** 🎉\n"
        elif is_fumble:
            result_message += "💥 **ファンブル！** 💥\n"
            
        result_message += f"出目: `{' + '.join(map(str, rolls))}` = `{total_roll}`\n"
        
        if modifier != 0:
            result_message += f"修正値: `{modifier:+}`\n"
            result_message += f"**最終結果**: `{total_roll} ({modifier:+})` = **`{final_result}`**"
        else:
            result_message += f"**最終結果**: **`{final_result}`**"
            
        # 結果が長すぎる場合の対処
        if len(result_message) > 1900:
            result_message = f"{ctx.author.mention} が `{dice_str}` を振りました！\n"
            result_message += f"多数のダイスを振ったため、合計のみ表示します。\n"
            if modifier != 0:
                result_message += f"合計(修正前): `{total_roll}`\n"
                result_message += f"修正値: `{modifier:+}`\n"
                result_message += f"**最終結果**: **`{final_result}`**"
            else:
                result_message += f"**最終結果**: **`{final_result}`**"
                
        self.logger.info(f"ロール結果: {rolls} -> 合計 {total_roll} -> 修正後 {final_result}")
        await ctx.send(result_message)
    
    @commands.command(name='history', help='あなたの過去10回分のロール履歴を表示します。')
    async def show_history(self, ctx):
        """ユーザーのロール履歴を表示するコマンド"""
        user_id = ctx.author.id
        
        if user_id not in self.roll_history or not self.roll_history[user_id]:
            await ctx.send("ロール履歴がありません。")
            return
            
        embed = discord.Embed(
            title=f"{ctx.author.display_name}さんのロール履歴",
            description="最新10件のダイスロール結果",
            color=discord.Color.blue()
        )
        
        for i, roll_data in enumerate(reversed(self.roll_history[user_id])):
            dice_str = roll_data["dice_str"]
            rolls = roll_data["rolls"]
            total = roll_data["total"]
            modifier = roll_data["modifier"]
            result = roll_data["result"]
            
            value = f"出目: {', '.join(map(str, rolls))} = {total}\n"
            if modifier != 0:
                value += f"修正値: {modifier:+}\n"
            value += f"結果: **{result}**"
            
            embed.add_field(
                name=f"{i+1}. {dice_str}",
                value=value,
                inline=False
            )
            
        await ctx.send(embed=embed)
    
    async def _send_help_message(self, ctx):
        """ヘルプメッセージを送信"""
        embed = discord.Embed(
            title="🎲 ダイスボットのヘルプ",
            description="このボットでは以下のダイス記法を使用できます",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="基本的な記法",
            value="`NdS[+/-M]`\n"
                "- N: ダイスの数 (省略時は1)\n"
                "- S: ダイスの面数\n"
                "- M: 修正値 (省略可能)",
            inline=False
        )
        
        embed.add_field(
            name="例",
            value="`d20` - 20面ダイスを1個振る\n"
                "`2d6` - 6面ダイスを2個振る\n"
                "`1d10+5` - 10面ダイスを1個振り、結果に5を加える\n"
                "`3d8-2` - 8面ダイスを3個振り、結果から2を引く",
            inline=False
        )
        
        embed.add_field(
            name="コマンド一覧",
            value=f"`{ctx.prefix}roll [ダイス表記]` - ダイスを振る\n"
                f"`{ctx.prefix}history` - あなたの過去10回分のロール履歴を表示",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    @roll_dice.error
    async def roll_dice_error(self, ctx, error):
        """roll_diceコマンドのエラーハンドリング"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"ダイスの指定がありません。\n"
                        f"正しい形式: `{ctx.prefix}roll NdS[+/-M]` (例: `{ctx.prefix}roll 2d6`)\n"
                        f"`{ctx.prefix}roll help` で詳細を確認できます。")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"ダイスの指定形式が正しくありません。\n"
                        f"正しい形式: `{ctx.prefix}roll NdS[+/-M]` (例: `{ctx.prefix}roll 2d6`)\n"
                        f"`{ctx.prefix}roll help` で詳細を確認できます。")
        else:
            self.logger.error(f"コマンドエラー: {error}")
            await ctx.send("コマンドの実行中にエラーが発生しました。")

async def setup(bot):
    """Cogを登録する関数"""
    await bot.add_cog(DiceCog(bot))
    logging.getLogger('dice_bot.dice_cog').info("DiceCogが読み込まれました") 