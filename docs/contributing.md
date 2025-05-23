# Discord ダイスボット 貢献ガイドライン

このプロジェクトへの貢献を検討していただき、ありがとうございます。このドキュメントでは、ダイスボットプロジェクトへの貢献方法について説明します。

## 開発環境のセットアップ

1. リポジトリをクローン
   ```
   git clone <repository-url>
   cd dice
   ```

2. 仮想環境の作成と有効化
   ```
   python -m venv env
   # Windows
   env\Scripts\activate
   # macOS/Linux
   source env/bin/activate
   ```

3. 必要なパッケージのインストール
   ```
   pip install -r requirements.txt
   ```

4. 環境変数の設定
   ```
   cp .env.example .env
   # .envファイルを編集してDiscord Botトークンを設定
   ```

## コーディング規約

このプロジェクトでは、以下のコーディング規約に従ってください：

1. **Python スタイルガイド**：[PEP 8](https://pep8.org/) に準拠したコードを記述してください。

2. **ファイル構造**：`dice/docs/development/guidelines.md` のファイル構造を遵守してください。

3. **モジュール責任**：各モジュールの責任範囲を明確に保ってください。
   - `dice`: ダイス処理ロジック
   - `commands`: コマンドハンドラー
   - `utils`: 共通ユーティリティ
   - `views`: UI表示ロジック

4. **ドキュメンテーション**：すべての公開関数、クラス、メソッドには適切なdocstringを記述してください。

5. **型ヒント**：可能な限り型ヒント（Type Hints）を使用してください。

## 開発ワークフロー

1. **Issue の作成**：新機能の追加やバグ修正を行う前に、まずIssueを作成してください。

2. **ブランチの作成**：作業を始める前に、新しいブランチを作成してください。
   ```
   git checkout -b feature/your-feature-name
   ```
   
   ブランチ名の規則：
   - `feature/`: 新機能の追加
   - `fix/`: バグ修正
   - `refactor/`: リファクタリング
   - `docs/`: ドキュメントの更新

3. **コミットメッセージ**：明確で具体的なコミットメッセージを記述してください。
   ```
   feat: ダイスロール履歴機能を追加
   fix: クリティカル判定のバグを修正
   docs: READMEを更新
   ```

4. **プルリクエスト**：作業が完了したら、プルリクエストを作成してください。PRには以下を含めてください：
   - 変更内容の説明
   - 関連するIssueへの参照
   - テスト方法の説明

## テスト

新機能を追加する場合や既存機能を変更する場合は、必ず適切なテストを追加してください。

1. **テストの実行**：
   ```
   python -m unittest discover -s tests
   ```

2. **テストカバレッジ**：新しいコードには可能な限り高いテストカバレッジを維持してください。

## ドキュメント

コードの変更に伴い、必要に応じて以下のドキュメントを更新してください：

- `README.md`：プロジェクト概要
- `docs/usage.md`：使用方法
- 各モジュールのdocstring

## 提出前のチェックリスト

プルリクエストを提出する前に、以下の項目を確認してください：

- [ ] すべてのテストがパスしている
- [ ] コードがPEP 8スタイルガイドに準拠している
- [ ] 適切なドキュメントが追加または更新されている
- [ ] 新しい依存関係がある場合は`requirements.txt`に追加されている
- [ ] コミットメッセージが明確で具体的である

## 質問やサポート

質問やサポートが必要な場合は、Issueを作成するか、プロジェクトのメンテナーに連絡してください。

ご協力ありがとうございます！ 