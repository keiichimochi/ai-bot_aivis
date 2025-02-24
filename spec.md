# VOICEVOX OpenAI TTS API サンプルコード

VOICEVOXエンジンをOpenAIの音声合成APIフォーマットで利用するためのサンプルコードナリ。

## VOICEVOX 使い方

1. VOICEVOXのOpenAI互換APIサーバーを起動（デフォルトポート:8000）
2. 以下のコードを実行

```python
from openai import OpenAI

# カスタムベースURLを持つOpenAIクライアントを作成
client = OpenAI(base_url="http://localhost:8000/v1", api_key="your_api_key_here")

# 音声を生成
response = client.audio.speech.create(
    model="voicevox-v1",
    voice="1",
    input="こんにちは、音声合成のテストです。",
    speed=1.5
)

# 音声ファイルを保存
response.stream_to_file("output.mp3")
```

### VOICEVOX パラメータ説明

- `model`: "voicevox-v1" を指定
- `voice`: 話者ID（1: 四国めたん）
- `input`: 音声合成するテキスト
- `speed`: 話速（1.0がデフォルト、1.5で1.5倍速）

出力ファイルは `output.mp3` として保存されるナリ。

## Aivis Speech

Aivis SpeechのAPIエンドポイントは `http://localhost:10101/` ナリ。

### 話者一覧

#### Anneli (UUID: e756b8e4-b606-4e15-99b1-3f9c6a1b2317)
- ノーマル (ID: 888753760)
- 通常 (ID: 888753761)
- テンション高め (ID: 888753762)
- 落ち着き (ID: 888753763)
- 上機嫌 (ID: 888753764)
- 怒り・悲しみ (ID: 888753765)

#### korosuke (UUID: 40e5743b-a55b-4703-9cd7-221e3e5696a5)
- ノーマル (ID: 488039072)

#### sakuragi (UUID: e4dbb14f-6b40-4a00-a674-c6043b1412a5)
- ノーマル (ID: 269244800)

#### yamaoka (UUID: 67539f0d-f0ee-4770-8309-e0c4c08e4be1)
- ノーマル (ID: 1342155808)

### Aivis Speech API使用方法

Aivis SpeechのAPIは2段階のプロセスで音声を生成するナリ：

1. `/audio_query` で音声合成用のクエリを作成
2. `/synthesis` で実際の音声を生成

以下のコードで音声を生成できるナリ：

```python
import requests
import json

# 音声合成用のクエリを作成
query_params = {
    "text": "こんにちは、音声合成のテストです。",
    "speaker": 488039072,  # korosuke ノーマル
    "style_id": 488039072,  # korosuke ノーマル
    "speed_scale": 1.0
}

# クエリを作成
response = requests.post(
    "http://localhost:10101/audio_query",
    params=query_params
)
query_data = response.json()

# 音声合成を実行
audio_response = requests.post(
    "http://localhost:10101/synthesis",
    params={
        "speaker": 488039072,  # korosuke ノーマル
        "style_id": 488039072,
    },
    json=query_data
)

# 音声ファイルを保存
with open("korosuke_output.wav", "wb") as f:
    f.write(audio_response.content)
```

### Aivis Speech パラメータ説明

- `text`: 音声合成するテキスト
- `speaker`: 話者ID（整数値で指定。UUIDではないナリ！）
- `style_id`: 話者のスタイルID（整数値）
- `speed_scale`: 話速（1.0がデフォルト）

### 注意点

1. `speaker`パラメータには整数値のIDを使用する必要があるナリ（UUIDは使えないナリ）
2. 出力フォーマットは`.wav`ナリ
3. APIは2段階のプロセス（クエリ作成→音声合成）を必要とするナリ
4. requestsライブラリが必要ナリ（`uv pip install requests`でインストール）

### トラブルシューティング

1. 404エラーが出る場合：
   - APIエンドポイントが正しいか確認（`http://localhost:10101/`）
   - Aivis Speechのサーバーが起動しているか確認

2. 422エラーが出る場合：
   - `speaker`パラメータがUUIDではなく整数値（ID）になっているか確認
   - 必要なパラメータが全て含まれているか確認

3. 音声ファイルが小さすぎて再生できない場合：
   - レスポンスのステータスコードとサイズを確認
   - エラーメッセージを確認して、パラメータを修正

## Gemini AI + Aivis Speech チャットボットの実装

### 必要なライブラリ

```bash
uv pip install flask python-dotenv google-generativeai requests
```

### 環境変数の設定

`.env`ファイルを作成し、以下の内容を設定するナリ：

```env
GEMINI_API_KEY=your_api_key_here
```

### セキュリティ対策

1. `.gitignore`ファイルに以下を追加するナリ：
```
.env
__pycache__/
*.pyc
.venv/
```

### 実装のポイント

1. WAVファイルの結合処理：
   - 複数の音声データを結合する際は、WAVヘッダーを適切に処理する
   - データチャンクのサイズを正確に計算する
   - フォーマット情報は最初のファイルから取得する

2. 音声再生の制御：
   - 音声データをキューで管理し、順番に再生
   - Base64エンコードされたデータをBlobに変換して再生
   - 再生完了後にURLを解放してメモリリークを防ぐ

3. エラー処理：
   - APIレスポンスのステータスコードを確認
   - WAVヘッダーの検証を実施
   - エラーメッセージを適切にユーザーに表示

4. UI/UX改善：
   - favicon.icoの404エラーを防ぐ（空のデータURIを使用）
   - レスポンシブなデザイン
   - 音声モデル選択のドロップダウンメニュー

### デバッグのポイント

1. 音声合成のデバッグ：
   - 各文節のサイズと合成状況をログ出力
   - WAVヘッダーの整合性チェック
   - 音声データのサイズを確認

2. 音声再生のデバッグ：
   - 音声データの長さとContent-Typeを確認
   - 再生状態の変化をコンソールに出力
   - エラー発生時の詳細情報を記録 