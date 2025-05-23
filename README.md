# Discord ダイスボット

Discord用の多目的ボットです。TRPGのダイスロール機能に加え、ボードゲーム支援、ランダム選択、抽選機能などを提供します。様々なゲームやイベントで活用できます。

## 主な機能

### TRPG向け機能
- 基本的なダイスロール (`/roll 2d6`, `/roll d20+5` など)
- クリティカル/ファンブル判定
- ロール履歴の保存と表示
- 複数種類のダイスサポート (例: `/roll 1d20+2d6+3`)
- 見やすいUI (Discord Embedsの活用)
- インタラクティブな再ロール機能

### ボードゲーム・イベント向け機能
- 多彩なランダム選択機能 (`/choose`)
- 抽選機能 (`/lottery`)
- チーム分け機能
- トーナメント表作成

## インストール方法

1. このリポジトリをクローンします:
   ```
   git clone https://github.com/dumpling2/dice.git
   cd dice
   ```

2. 必要なパッケージをインストールします:
   ```
   pip install -r requirements.txt
   ```

3. `.env` ファイルを作成し、Discord Bot Tokenを設定します:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```

## 使い方

### 基本的なダイスロール (TRPG向け)

```
/roll NdS[+/-M]
```

- `N`: ダイスの数 (省略時は1)
- `S`: ダイスの面数
- `M`: 修正値 (省略可能)

例:
- `/roll d20` - 20面ダイスを1個振る
- `/roll 2d6` - 6面ダイスを2個振る
- `/roll 1d10+5` - 10面ダイスを1個振り、結果に5を加える
- `/roll 3d8-2` - 8面ダイスを3個振り、結果から2を引く

### ランダム選択 (一般用途向け)

```
/choose one [items]
```
カンマ区切りのリストから1つをランダムに選択します。

```
/choose multiple [items] [count] [unique]
```
リストから複数のアイテムをランダムに選択します。

```
/choose shuffle [items]
```
リストをランダムに並べ替えます。

```
/choose teams [members] [num_teams]
```
メンバーをランダムにチームに分けます。

### 抽選機能

```
/lottery draw [participants] [winners_count] [announce_delay]
```
参加者リストから当選者を抽選します。

```
/lottery tiered [participants] [first_prize_count] [second_prize_count] [third_prize_count]
```
複数の賞品に対して当選者を抽選します。

```
/lottery tournament [participants] [rounds]
```
参加者のトーナメント表を生成します。

### ヘルプの表示

```
/dice_help
```

または

```
/roll help
```

### ロール履歴の表示

```
/history
```

過去10回分のダイスロール結果を表示します。

## スラッシュコマンドの利点

このボットはDiscordのスラッシュコマンドに対応しています。スラッシュコマンドには以下の利点があります：

- コマンドの自動補完
- パラメーターの説明表示
- 他のボットコマンドとの衝突防止
- コマンドの発見性向上
- Discordの公式APIポリシーへの準拠

## 改善予定の機能

詳細な改善予定リストは `docs/planning/implementation_roadmap.md` と `docs/planning/expansion_plan.md` ファイルに記載されています。主な改善予定項目:

- カスタムダイスフェイスの実装
- キャラクターシート連携
- データベース統合
- インタラクティブコンポーネントの強化
- 多言語サポート
- 外部ゲームAPIとの連携

## モジュール化構造

`src` ディレクトリにはモジュール化されたボット構造が実装されています。この構造はより大規模なプロジェクトや機能拡張に適しています。

## ライセンス

MIT

## 貢献

プルリクエスト歓迎です。大きな変更をする場合は、まずissueを開いて変更内容について議論してください。