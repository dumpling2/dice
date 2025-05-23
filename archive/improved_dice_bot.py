"""
改善版 Discord ダイスボット
複数の機能改善を統合したバージョン
"""

import os
import re
import random
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from typing import List, Tuple, Dict, Any, Optional

# 環境変数のロード
load_dotenv()
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dice_bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('dice_bot')

# ボットの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# ユーザーごとのロール履歴
roll_history = {}

# 複雑なダイス表記をパースするための正規表現
complex_dice_pattern = re.compile(r'([+-]?\d*d\d+|[+-]?\d+)', re.IGNORECASE)
# 基本的なダイス表記をパースするための正規表現
basic_dice_pattern = re.compile(r"^(?:(\d+)d)?(\d+)(?:([+-])(\d+))?$", re.IGNORECASE)

class DiceRollView(discord.ui.View):
    """ダイスロール結果に付けるボタン付きビュー"""
    def __init__(self, dice_str: str, ctx: commands.Context):
        super().__init__(timeout=60)  # 60秒後にボタンを無効化
        self.dice_str = dice_str
        self.ctx = ctx

    @discord.ui.button(label="再ロール", style=discord.ButtonStyle.primary, emoji="🎲")
    async def reroll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """再ロールボタンが押された時の処理"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("他の人のロールは再ロールできません", ephemeral=True)
            return

        # 複雑なダイス表記の処理
        result = roll_complex_dice(self.dice_str)
        
        if "error" in result:
            await interaction.response.send_message(f"エラー: {result['error']}", ephemeral=True)
            return
            
        # Embedの作成
        embed = create_dice_embed(self.ctx, result)
        
        # 結果を更新
        await interaction.response.edit_message(embed=embed, view=self)

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
    components = complex_dice_pattern.findall(dice_str)
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
        
        if 'd' in comp.lower():
            # ダイス表記の処理
            parts = comp.lower().split('d')
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

def roll_complex_dice(dice_str: str) -> Dict[str, Any]:
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
            
            # バリデーション
            abs_num_dice = abs(num_dice)
            if not (1 <= abs_num_dice <= 100):
                return {"error": "ダイスの数は1から100の間で指定してください"}
            if not (2 <= num_sides <= 1000):
                return {"error": "ダイスの面は2から1000の間で指定してください"}
                
            rolls = roll_dice(num_dice, num_sides)
            
            # 負のダイス数の場合は結果を反転
            roll_sum = sum(rolls)
            if is_negative:
                roll_sum = -roll_sum
            
            # 出目の最大値と最小値をチェック
            is_critical = all(roll == num_sides for roll in rolls)
            is_fumble = all(roll == 1 for roll in rolls)
            
            rolls_detail.append({
                "type": "dice",
                "notation": f"{'-' if is_negative else ''}{abs_num_dice}d{num_sides}",
                "rolls": rolls,
                "sum": roll_sum,
                "negative": is_negative,
                "is_critical": is_critical,
                "is_fumble": is_fumble,
                "sides": num_sides
            })
            
            final_result += roll_sum
        else:  # 修正値
            if not (-1000 <= modifier <= 1000):
                return {"error": "修正値は-1000から1000の間で指定してください"}
                
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

def create_dice_embed(ctx: commands.Context, result: Dict[str, Any]) -> discord.Embed:
    """Embedsを作成する関数"""
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
    else:
        embed.set_footer(text=f"ダイスボット | {bot.user.name if bot.user else 'ダイスボット'}")
    
    return embed

def format_roll_result(result: Dict[str, Any]) -> str:
    """ロール結果を整形された文字列に変換する（テキスト表示用）"""
    if "error" in result:
        return f"エラー: {result['error']}"
    
    output = f"入力: `{result['input']}`\n"
    
    # クリティカルとファンブルの判定
    is_critical = any(detail.get("is_critical", False) for detail in result["details"] if detail["type"] == "dice")
    is_fumble = any(detail.get("is_fumble", False) for detail in result["details"] if detail["type"] == "dice")
    
    if is_critical:
        output += "🎉 **クリティカル！** 🎉\n"
    elif is_fumble:
        output += "💥 **ファンブル！** 💥\n"
    
    output += "詳細:\n"
    
    for detail in result["details"]:
        if detail["type"] == "dice":
            rolls_str = ", ".join(map(str, detail["rolls"]))
            output += f"・`{detail['notation']}`: [{rolls_str}] = {detail['sum']}\n"
        else:
            output += f"・修正値: {detail['value']:+}\n"
    
    output += f"**最終結果**: **`{result['result']}`**"
    
    return output

@bot.event
async def on_ready():
    """ボットの準備完了時に呼び出されるイベント"""
    logger.info(f'{bot.user.name} がDiscordに接続しました！')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'コマンドプレフィックス: {COMMAND_PREFIX}')
    logger.info('------')
    await bot.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}roll help"))

@bot.command(name='roll', help='ダイスを振ります。\n例: !roll 1d6, !roll 2d10+3, !roll d20-1')
async def roll_dice(ctx, *, dice_str: str = None):
    """
    ダイスを振るコマンド。複雑なダイス表記にも対応。
    例: !roll 1d20+2d6+3
    """
    if dice_str == "help" or dice_str is None:
        await _send_help_message(ctx)
        return
        
    logger.info(f"コマンド受信: {ctx.author.name} が {COMMAND_PREFIX}roll {dice_str} を実行")
    
    # ダイスロール実行
    result = roll_complex_dice(dice_str)
    
    if "error" in result:
        await ctx.send(f"エラー: {result['error']}\n"
                    f"正しい形式については `{COMMAND_PREFIX}roll help` で確認できます。")
        return
    
    # ロール履歴に追加
    user_id = ctx.author.id
    if user_id not in roll_history:
        roll_history[user_id] = []
        
    # 最大10件まで保存
    roll_history[user_id].append(result)
    if len(roll_history[user_id]) > 10:
        roll_history[user_id].pop(0)
    
    # 結果のEmbedを作成
    embed = create_dice_embed(ctx, result)
    
    # ボタン付きで表示
    view = DiceRollView(dice_str, ctx)
    await ctx.send(embed=embed, view=view)

@bot.command(name='history', help='あなたの過去10回分のロール履歴を表示します。')
async def show_history(ctx):
    """ユーザーのロール履歴を表示するコマンド"""
    user_id = ctx.author.id
    
    if user_id not in roll_history or not roll_history[user_id]:
        await ctx.send("ロール履歴がありません。")
        return
        
    embed = discord.Embed(
        title=f"{ctx.author.display_name}さんのロール履歴",
        description="最新10件のダイスロール結果",
        color=discord.Color.blue()
    )
    
    for i, roll_data in enumerate(reversed(roll_history[user_id])):
        dice_str = roll_data["input"]
        result = roll_data["result"]
        
        # 詳細情報を構築
        details = []
        for detail in roll_data["details"]:
            if detail["type"] == "dice":
                details.append(f"{detail['notation']}: {detail['sum']}")
            else:
                details.append(f"修正値: {detail['value']:+}")
        
        details_str = ", ".join(details)
        
        embed.add_field(
            name=f"{i+1}. {dice_str}",
            value=f"{details_str}\n結果: **{result}**",
            inline=False
        )
        
    await ctx.send(embed=embed)

async def _send_help_message(ctx):
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
        name="複数ダイス記法",
        value="`NdS+MdL[+/-X]`\n"
            "例: `1d20+2d6+3` - 1個の20面ダイスと2個の6面ダイスを振り、結果に3を加える",
        inline=False
    )
    
    embed.add_field(
        name="例",
        value=f"`{COMMAND_PREFIX}roll d20` - 20面ダイスを1個振る\n"
            f"`{COMMAND_PREFIX}roll 2d6` - 6面ダイスを2個振る\n"
            f"`{COMMAND_PREFIX}roll 1d10+5` - 10面ダイスを1個振り、結果に5を加える\n"
            f"`{COMMAND_PREFIX}roll 1d20+2d4-1` - 1個の20面ダイスと2個の4面ダイスを振り、結果から1を引く",
        inline=False
    )
    
    embed.add_field(
        name="コマンド一覧",
        value=f"`{COMMAND_PREFIX}roll [ダイス表記]` - ダイスを振る\n"
            f"`{COMMAND_PREFIX}history` - あなたの過去10回分のロール履歴を表示",
        inline=False
    )
    
    await ctx.send(embed=embed)

@roll_dice.error
async def roll_dice_error(ctx, error):
    """roll_diceコマンドでエラーが発生した際のエラーハンドリング"""
    if isinstance(error, commands.MissingRequiredArgument):
        await _send_help_message(ctx)
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"ダイスの指定形式が正しくありません。\n"
                    f"`{COMMAND_PREFIX}roll help` で詳細を確認できます。")
    else:
        logger.error(f"エラー発生: {error}")
        await ctx.send("コマンドの実行中にエラーが発生しました。")

# ボットを実行
if __name__ == '__main__':
    if BOT_TOKEN is None:
        logger.critical("エラー: DISCORD_BOT_TOKENが設定されていません。")
        logger.critical(".envファイルを作成し、DISCORD_BOT_TOKENを設定してください。")
        exit(1)
    
    try:
        bot.run(BOT_TOKEN)
    except discord.errors.LoginFailure:
        logger.critical("エラー: 無効なBOTトークンです。トークンが正しいか確認してください。")
    except Exception as e:
        logger.critical(f"ボットの起動中に予期せぬエラーが発生しました: {e}") 