# AI Chat Bot with Voice Synthesis

音声合成機能付きAIチャットボットのサンプル実装ナリ。Gemini 2.0 Flash AIによるチャット機能とAivis Speechによる音声合成を組み合わせているナリ。

## 🎯 特徴

- 💬 Gemini 2.0 Flash AIによるチャット機能
- 🎤 Aivis Speechによる音声合成
- 🔊 ブラウザでの音声再生（iPhone対応）
- 📸 画像アップロード・解析機能（カメラ/ライブラリ対応）
- 🖼️ 画像のみ送信対応（テキストなしでも画像について説明）
- 👥 複数の音声キャラクター
- 🎯 キャラクターごとの性格設定
- 🔄 自動再生機能
- 📱 レスポンシブデザイン

## 📁 ファイル構成

プロジェクトは機能ごとに分割されています：

```
ai-bot_aivis/
├── app.py                      # Flaskサーバー（バックエンド）
├── templates/
│   └── index.html              # メインHTMLファイル
├── static/
│   ├── css/
│   │   └── style.css          # スタイルシート
│   └── js/
│       ├── audio.js           # 音声再生機能（iPhone対応）
│       ├── chat.js            # チャット機能
│       └── app.js             # メイン制御・初期化
├── .env                       # 環境変数（APIキー）
├── requirements.txt           # Python依存関係
└── README.md                  # このファイル
```

### 各ファイルの役割

- **`app.py`**: Flaskサーバー、API処理、音声合成
- **`templates/index.html`**: 基本的なHTML構造
- **`static/css/style.css`**: UI/UXスタイリング、レスポンシブデザイン
- **`static/js/audio.js`**: iPhone対応音声再生、HTMLAudioElement使用
- **`static/js/chat.js`**: チャット機能、メッセージ管理
- **`static/js/app.js`**: アプリ全体の初期化と制御

## 🚀 セットアップ

1. リポジトリをクローン：
```bash
git clone https://github.com/keiichimochi/ai-bot_aivis.git
cd ai-bot_aivis
```

2. 仮想環境を作成して有効化：
```bash
uv venv
.venv\Scripts\activate  # Windows
# または
source .venv/bin/activate  # macOS/Linux
```

3. 必要なパッケージをインストール：
```bash
uv pip install flask python-dotenv google-generativeai requests litellm psutil
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

## 🎮 使い方

1. Aivis Speechサーバーを起動（デフォルトポート: 10101）

2. アプリケーションを起動：
```bash
python app.py
```

3. ブラウザでアクセス：
http://localhost:5050

### 💬 基本的な使い方
- テキストメッセージを入力して「送信」ボタンをクリック
- 音声、AIモデルを選択可能
- 音声自動再生のON/OFF切り替え

### 📸 画像機能の使い方
1. **画像アップロード**: 📷ボタンをクリック
2. **撮影方法選択**: 
   - 📷 写真を撮る（カメラ起動）
   - 🖼️ ライブラリから選択（フォトライブラリ）
3. **送信方法**:
   - **テキスト + 画像**: 通常通りメッセージを入力して送信
   - **画像のみ**: テキストを入力せず「画像送信」ボタンをクリック
4. **画像圧縮**: 5MB制限に自動で圧縮（WebP/JPEG対応）

### 🔍 画像解析機能
- **画像のみ送信**: AIが画像の内容を自動で詳しく説明
- **対応フォーマット**: JPEG, PNG, WebP
- **自動圧縮**: 大きな画像も自動で最適化
- **プレビュー機能**: 送信前に画像確認可能

## 📱 iPhone/iPad対応

iPhoneやiPadでの音声再生のために以下の対応を実装しています：

### 技術的な対応
- **HTMLAudioElement使用**: Web Audio APIではなくHTMLAudioElementを使用
- **ユーザーインタラクション検知**: タップ、クリック、キー入力で音声制限を解除
- **サイレント音声再生**: iOS音声制限を事前に解除
- **手動再生ボタン**: 自動再生が失敗した場合のフォールバック

### 使用方法（iPhone）
1. ページを開いたら画面をタップ
2. 「音声自動再生」トグルを有効にする
3. メッセージを送信すると音声が自動再生される
4. 自動再生が失敗した場合は各メッセージの▶ボタンで手動再生

## 🎭 音声キャラクター

- **コロ助**: ロボットアシスタント（語尾に「ナリ」）
- **アンネリ**: 女性アシスタント（複数の感情表現）
- **桜木**: 熱血教師（東大専門予備校）
- **山岡**: 美食家（美味しんぼ風）

## 🛠️ 開発者向け情報

### デバッグモード
URLに`?debug=true`を追加するとデバッグモードが有効になり、コンソールで以下が利用可能：

```javascript
// デバッグ関数
debug.clearChat()         // チャット履歴をクリア
debug.getSettings()       // 現在の設定を取得
debug.testAudio()         // 音声テスト
getAppStatus()            // アプリケーション状態を取得
```

### カスタマイズ

各ファイルが独立しているため、個別にカスタマイズ可能：

- **UI変更**: `static/css/style.css`を編集
- **音声機能**: `static/js/audio.js`を編集
- **チャット機能**: `static/js/chat.js`を編集
- **キャラクター追加**: `app.py`の`SPEAKER_PROMPTS`を編集

## 🎵 音声合成仕様

### Aivis Speech API
- エンドポイント: `http://localhost:10101/`
- 2段階プロセス: `audio_query` → `synthesis`
- 出力フォーマット: WAV
- 文節分割機能: 長いテキストを自動で分割

### 対応音声ID
```python
VOICE_IDS = {
    488039072: "コロ助",
    888753760: "アンネリ（ノーマル）",
    888753761: "アンネリ（通常）",
    888753762: "アンネリ（テンション高め）",
    # ...他多数
}
```

## 🔧 トラブルシューティング

### よくある問題

1. **音声が再生されない（iPhone）**
   - 画面をタップしてユーザーインタラクションを有効化
   - 自動再生トグルを確認
   - 手動再生ボタン（▶）を使用

2. **Aivis Speechに接続できない**
   - ポート10101が開いているか確認
   - Aivis Speechサーバーが起動しているか確認

3. **Gemini APIエラー**
   - `.env`ファイルにAPIキーが正しく設定されているか確認
   - APIキーが有効か確認

### エラーログ確認
ブラウザの開発者ツール（F12）のコンソールタブでエラー詳細を確認できます。

## 🚀 今後の予定

- 🎤 音声認識（STT）機能
- 🌙 ダークモード完全対応
- ⚡ 音声の再生速度調整
- 🔊 音量調整
- 💾 チャット履歴の保存
- 🌐 多言語対応
- 🎨 テーマカスタマイズ

## 💡 技術スタック

### フロントエンド
- **HTML5**: セマンティックな構造
- **CSS3**: モダンなスタイリング、Flexbox
- **JavaScript ES6+**: モジュラー設計、クラスベース

### バックエンド
- **Flask**: Webフレームワーク
- **LiteLLM**: 複数AI API統合
- **Gemini 2.0 Flash**: メイン言語モデル
- **Aivis Speech**: 音声合成

### 音声技術
- **HTMLAudioElement**: iOS対応音声再生
- **WAVファイル処理**: Base64エンコード/デコード
- **音声キュー管理**: 順次再生制御

## 📄 ライセンス

MITライセンス

## 🤝 貢献

1. このリポジトリをフォーク
2. 新しいブランチを作成：`git checkout -b feature/your-feature`
3. 変更をコミット：`git commit -am 'Add new feature'`
4. ブランチをプッシュ：`git push origin feature/your-feature`
5. プルリクエストを作成

## ⚠️ 注意事項

- APIキーは必ず`.env`ファイルで管理し、Gitにコミットしないでください
- 音声合成には多くのメモリを使用する可能性があります
- iPhoneブラウザでは必ずユーザーインタラクション後に音声再生が可能になります
- 大量のリクエストはAPI制限に注意してください

## 📞 サポート

問題が発生した場合は、GitHubのIssuesでお気軽にお問い合わせください。

---

**Happy Chatting! 🎤✨** 