# AI Chat Bot with Voice Synthesis

音声合成機能付きAIチャットボットのサンプル実装ナリ。Gemini AIによるチャット機能とAivis Speechによる音声合成を組み合わせているナリ。

## 機能

- 💬 Gemini AIによる自然な会話
- 🎤 Aivis Speechによる音声合成
- 🔊 ブラウザでの音声再生（安定性向上）
- 👥 複数の音声キャラクター
- 🎯 キャラクターごとの性格設定
- 🔄 自動再生機能
- 📱 モバイルファーストデザイン
- ⌨️ エンターキーでの送信対応
- 🌐 Tailscale経由でのアクセス対応

## デモ画面

![デモ画面](docs/images/demo.png)

## 必要なもの

- Python 3.8以上
- Aivis Speech サーバー
- Gemini AI API キー
- Tailscale（リモートアクセス用・オプション）

## セットアップ

1. リポジトリをクローン：
```bash
git clone https://github.com/keiichimochi/ai-bot_aivis.git
cd ai-bot_aivis
```

2. 仮想環境を作成して有効化：
```bash
uv venv
source .venv/bin/activate  # Linuxの場合
```

3. 必要なパッケージをインストール：
```bash
uv pip install -r requirements.txt
```

4. 環境変数の設定：
`.env.sample`をコピーして`.env`を作成し、必要な環境変数を設定：
```env
GEMINI_API_KEY=your_api_key_here
```

## 使い方

1. Aivis Speechサーバーを起動（デフォルトポート: 10101）

2. アプリケーションを起動：
```bash
python main.py
```

3. ブラウザでアクセス：
   - ローカル: `http://localhost:8000`
   - Tailscale経由: `http://[Tailscaleアドレス]:8000`

## 実装済み機能

- ✅ 基本的なチャット機能
  - ユーザー入力
  - AI応答表示
  - 音声モデル選択
  - システムプロンプト

- ✅ 音声合成機能
  - テキストの文節分割
  - WAVヘッダーの検証
  - Base64エンコード/デコード
  - エラーハンドリング
  - 音声パラメータの最適化
  - 音声の前後に無音時間を追加

- ✅ 音声再生機能
  - 自動再生トグル
  - ピコ音によるユーザーインタラクション
  - 個別再生ボタン
  - 音声キュー管理
  - 安定した音声再生
  - リソースの適切な解放

- ✅ UI/UX
  - レスポンシブデザイン
  - 音声モデルのドロップダウン
  - 再生状態の視覚的フィードバック
  - スクロール自動調整
  - モバイルファースト対応
  - エンターキー送信

## 最近の更新

- 🔊 音声再生の安定性を大幅に向上
- ⚡ 音声合成パラメータの最適化
- 🛠️ エラーハンドリングの改善
- 📝 環境変数の設定を簡素化（.env.sampleの追加）
- 🔧 ポート番号を8000に変更

## 今後の予定

- 🎤 音声認識（STT）機能
- 🌙 ダークモード
- ⚡ 音声の再生速度調整
- 🔊 音量調整
- 💾 チャット履歴の保存
- 🌐 多言語対応

## 技術スタック

- バックエンド
  - FastAPI
  - Gemini AI API
  - Aivis Speech API
  - uvicorn

- フロントエンド
  - HTML/CSS/JavaScript
  - Web Audio API
  - Web Speech API (予定)

## ライセンス

MITライセンス

## 詳細な仕様

詳細な仕様については[spec.md](spec.md)を参照してくださいナリ。

## 貢献

1. このリポジトリをフォーク
2. 新しいブランチを作成：`git checkout -b feature/your-feature`
3. 変更をコミット：`git commit -am 'Add new feature'`
4. ブランチをプッシュ：`git push origin feature/your-feature`
5. プルリクエストを作成

## 注意事項

- APIキーは必ず`.env`ファイルで管理し、Gitにコミットしないでください
- 音声合成には多くのメモリを使用する可能性があります
- ブラウザの自動再生ポリシーにより、初回の音声再生には必ずユーザーインタラクションが必要です
- 音声再生の安定性は、ブラウザやデバイスの性能に依存する場合があります 