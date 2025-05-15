# AI Chat Bot with Voice Synthesis

音声合成機能付きAIチャットボットのサンプル実装ナリ。Gemini AIによるチャット機能とAivis Speechによる音声合成を組み合わせているナリ。

## 機能

- 💬 Gemini AIによるチャット機能
- 🎤 Aivis Speechによる音声合成
- 🔊 ブラウザでの音声再生
- 👥 複数の音声キャラクター
- 🎯 キャラクターごとの性格設定
- 🔄 自動再生機能

## デモ画面

![デモ画面](docs/images/demo.png)

## 必要なもの

- Python 3.8以上
- Aivis Speech サーバー
- Gemini AI API キー

## セットアップ

1. リポジトリをクローン：
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

2. 仮想環境を作成して有効化：
```bash
uv venv
.venv\Scripts\activate
```

3. 必要なパッケージをインストール：
```bash
uv pip install flask python-dotenv google-generativeai requests
```

4. Gemini APIキーの取得と設定：
   - [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
   - Googleアカウントでログイン
   - 「Create API Key」をクリック
   - 生成されたAPIキーをコピー
   - プロジェクトのルートディレクトリに`.env`ファイルを作成
   - 以下の内容を`.env`ファイルに記述：
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
   - `your_api_key_here`の部分をコピーしたAPIキーに置き換え

## 使い方

1. Aivis Speechサーバーを起動（デフォルトポート: 10101）

2. アプリケーションを起動：
```bash
python app.py
```

3. ブラウザでアクセス：
http://localhost:5000

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

- ✅ 音声再生機能
  - 自動再生トグル
  - ピコ音によるユーザーインタラクション
  - 個別再生ボタン
  - 音声キュー管理

- ✅ UI/UX
  - レスポンシブデザイン
  - 音声モデルのドロップダウン
  - 再生状態の視覚的フィードバック
  - スクロール自動調整

## 今後の予定

- 🎤 音声認識（STT）機能
- 🌙 ダークモード
- ⚡ 音声の再生速度調整
- 🔊 音量調整
- 💾 チャット履歴の保存
- 🌐 多言語対応

## 技術スタック

- バックエンド
  - Flask
  - Gemini AI API
  - Aivis Speech API

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