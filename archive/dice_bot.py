# discord.pyライブラリをインポートします
import discord
from discord.ext import commands
import random
import re # 正規表現モジュール
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# トークンが設定されていない場合のエラーハンドリング
if not BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKENが設定されていません。.envファイルを確認してください。")

# Botのプレフィックス（コマンドの前に付ける記号）
COMMAND_PREFIX = '!'

# インテントの設定 (メッセージ内容の読み取りを許可)
intents = discord.Intents.default()
intents.message_content = True # メッセージコンテントのインテントを有効にする

# Botオブジェクトを作成
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    """ボットがDiscordに接続し、準備ができたときに呼び出されるイベントハンドラ"""
    print(f'{bot.user.name} がDiscordに接続しました！')
    print(f'Bot ID: {bot.user.id}')
    print('------')
    await bot.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}roll help"))

@bot.command(name='roll', help='ダイスを振ります。\n例: !roll 1d6, !roll 2d10+3, !roll d20-1')
async def roll_dice(ctx, dice_str: str):
    """
    指定された形式のダイスを振るコマンド。
    形式: NdS[+/-M]
    N: ダイスの数 (省略時は1)
    S: ダイスの面数
    M: 修正値 (省略時は0)
    例: !roll 1d6 -> 1つの6面ダイスを振る
        !roll 2d10+3 -> 2つの10面ダイスを振り、結果に3を加える
        !roll d20-1 -> 1つの20面ダイスを振り、結果から1を引く
    """
    print(f"コマンド受信: {ctx.author.name} が {COMMAND_PREFIX}roll {dice_str} を実行")

    # ダイス文字列をパースするための正規表現パターン
    # (?:(\d+)d)? : オプションのダイス数 (例: "2d")
    # (\d+)       : ダイスの面数 (必須)
    # (?:([+-])(\d+))? : オプションの修正値 (例: "+5", "-2")
    pattern = re.compile(r"^(?:(\d+)d)?(\d+)(?:([+-])(\d+))?$", re.IGNORECASE)
    match = pattern.match(dice_str)

    if not match:
        await ctx.send(f"'{dice_str}' は無効なダイス指定です。\n"
                       f"正しい形式: `NdS[+/-M]` (例: `2d6`, `d20+3`, `1d10-1`)\n"
                       f"`{COMMAND_PREFIX}roll help` で詳細を確認できます。")
        return

    num_dice_str, num_sides_str, modifier_sign, modifier_val_str = match.groups()

    # デフォルト値の設定
    num_dice = int(num_dice_str) if num_dice_str else 1
    num_sides = int(num_sides_str)
    modifier = 0
    if modifier_sign and modifier_val_str:
        modifier = int(modifier_val_str)
        if modifier_sign == '-':
            modifier *= -1

    # パラメータのバリデーション
    if not (1 <= num_dice <= 100): # ダイスの数は1から100まで
        await ctx.send("ダイスの数は1から100の間で指定してください。")
        return
    if not (2 <= num_sides <= 1000): # ダイスの面は2から1000まで
        await ctx.send("ダイスの面は2から1000の間で指定してください。")
        return
    if not (-1000 <= modifier <= 1000): # 修正値は-1000から1000まで
        await ctx.send("修正値は-1000から1000の間で指定してください。")
        return


    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    total_roll = sum(rolls)
    final_result = total_roll + modifier

    # 結果メッセージの作成
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
        result_message += f"修正値: `{modifier:+}`\n" # +記号も表示
        result_message += f"**最終結果**: `{total_roll} ({modifier:+})` = **`{final_result}`**"
    else:
        result_message += f"**最終結果**: **`{final_result}`**"

    # 結果が長すぎる場合の対処 (Discordのメッセージ長制限は2000文字)
    if len(result_message) > 1900: # 少し余裕を持たせる
        result_message = f"{ctx.author.mention} が `{dice_str}` を振りました！\n"
        result_message += f"多数のダイスを振ったため、合計のみ表示します。\n"
        if modifier != 0:
            result_message += f"合計(修正前): `{total_roll}`\n"
            result_message += f"修正値: `{modifier:+}`\n"
            result_message += f"**最終結果**: **`{final_result}`**"
        else:
            result_message += f"**最終結果**: **`{final_result}`**"


    print(f"結果: {rolls} -> 合計 {total_roll} -> 修正後 {final_result}")
    await ctx.send(result_message)

@roll_dice.error
async def roll_dice_error(ctx, error):
    """roll_diceコマンドでエラーが発生した際のエラーハンドリング"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"ダイスの指定がありません。\n"
                       f"正しい形式: `{COMMAND_PREFIX}roll NdS[+/-M]` (例: `{COMMAND_PREFIX}roll 2d6`)\n"
                       f"`{COMMAND_PREFIX}roll help` で詳細を確認できます。")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"ダイスの指定形式が正しくありません。\n"
                       f"正しい形式: `{COMMAND_PREFIX}roll NdS[+/-M]` (例: `{COMMAND_PREFIX}roll 2d6`)\n"
                       f"`{COMMAND_PREFIX}roll help` で詳細を確認できます。")
    else:
        print(f"エラー発生: {error}")
        await ctx.send("コマンドの実行中にエラーが発生しました。")


# ボットを実行
if __name__ == '__main__':
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("エラー: BOT_TOKENが設定されていません。")
        print("コード内の 'YOUR_BOT_TOKEN_HERE' を実際のDiscord Botトークンに置き換えてください。")
    else:
        try:
            bot.run(BOT_TOKEN)
        except discord.errors.LoginFailure:
            print("エラー: 無効なBOTトークンです。トークンが正しいか確認してください。")
        except Exception as e:
            print(f"ボットの起動中に予期せぬエラーが発生しました: {e}")

