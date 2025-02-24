├── .gitignore
├── Dockerfile
├── README.md
├── docker-compose.gpu.yml
├── docker-compose.yml
├── example
    ├── README.md
    ├── requirements.txt
    ├── simple_tts_example.py
    └── tts_example.py
└── voicevox_tts_api
    ├── api
        ├── __init__.py
        ├── routers
        │   ├── __init__.py
        │   ├── chat.py
        │   ├── models.py
        │   └── speech.py
        └── schemas
        │   ├── __init__.py
        │   ├── chat.py
        │   └── speech.py
    ├── main.py
    ├── requirements.txt
    ├── tts_api.py
    └── voice_mappings.json


/.gitignore:
--------------------------------------------------------------------------------
 1 | # Python
 2 | __pycache__/
 3 | *.py[cod]
 4 | *$py.class
 5 | *.so
 6 | .Python
 7 | build/
 8 | develop-eggs/
 9 | dist/
10 | downloads/
11 | eggs/
12 | .eggs/
13 | lib/
14 | lib64/
15 | parts/
16 | sdist/
17 | var/
18 | wheels/
19 | *.egg-info/
20 | .installed.cfg
21 | *.egg
22 | 
23 | # Virtual Environment
24 | venv/
25 | ENV/
26 | env/
27 | .env
28 | 
29 | # IDE
30 | .idea/
31 | .vscode/
32 | *.swp
33 | *.swo
34 | 
35 | # Project specific
36 | example/output/
37 | .SourceSageAssets/
38 | .SourceSageignore
39 | 
40 | # Logs
41 | *.log
42 | output/
43 | 


--------------------------------------------------------------------------------
/Dockerfile:
--------------------------------------------------------------------------------
 1 | FROM python:3.9-slim
 2 | 
 3 | WORKDIR /app
 4 | 
 5 | COPY voicevox_tts_api/requirements.txt .
 6 | RUN pip install --no-cache-dir -r requirements.txt
 7 | 
 8 | COPY voicevox_tts_api/ .
 9 | 
10 | # 新しいエントリーポイントを指定
11 | CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
12 | 


--------------------------------------------------------------------------------
/README.md:
--------------------------------------------------------------------------------
  1 | <div align="center">
  2 | 
  3 | ![Image](https://github.com/user-attachments/assets/e47df212-9f09-4c43-8a66-ced8e1b1fb7c)
  4 | 
  5 | # 🎤 VOICEVOX OpenAI TTS API
  6 | 
  7 | [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  8 | [![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
  9 | [![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://www.docker.com/)
 10 | [![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-009688)](https://fastapi.tiangolo.com/)
 11 | 
 12 | VOICEVOXエンジンをOpenAIの音声合成APIフォーマットに変換するためのAPIサーバーです。
 13 | 
 14 | </div>
 15 | 
 16 | ## 🌟 特徴
 17 | 
 18 | - OpenAIのTTS APIと同じフォーマットでリクエストを受け付け
 19 | - VOICEVOXエンジンを使用した高品質な日本語音声合成
 20 | - Dockerで簡単にデプロイ可能
 21 | 
 22 | ## 🚀 使用方法
 23 | 
 24 | ### 🐳 起動方法
 25 | 
 26 | ```bash
 27 | docker-compose up -d
 28 | ```
 29 | 
 30 | ### 📝 APIエンドポイント
 31 | 
 32 | ```bash
 33 | POST http://localhost:8000/audio/speech
 34 | ```
 35 | 
 36 | ### リクエスト形式（OpenAI互換）
 37 | 
 38 | ```json
 39 | {
 40 |   "model": "voicevox-v1",
 41 |   "input": "こんにちは、音声合成のテストです。",
 42 |   "voice": "1",
 43 |   "response_format": "mp3",
 44 |   "speed": 1.0
 45 | }
 46 | ```
 47 | 
 48 | ### パラメータ説明
 49 | 
 50 | - `model`: 使用するモデル（現在は"voicevox-v1"のみ）
 51 | - `input`: 読み上げるテキスト
 52 | - `voice`: VOICEVOXのスピーカーID
 53 | - `response_format`: 出力フォーマット（現在は"mp3"のみ）
 54 | - `speed`: 読み上げ速度（デフォルト: 1.0）
 55 | 
 56 | ### レスポンス形式
 57 | 
 58 | - Content-Type: `audio/mpeg`
 59 | - Body: MP3形式の音声データ（バイナリ）
 60 | 
 61 | ### Pythonでの使用例
 62 | 
 63 | ```python
 64 | from openai import OpenAI
 65 | 
 66 | # カスタムベースURLを持つOpenAIクライアントを作成
 67 | client = OpenAI(base_url="http://localhost:8000", api_key="sk-1234")
 68 | 
 69 | # 音声を生成
 70 | response = client.audio.speech.create(
 71 |     model="voicevox-v1",
 72 |     voice="1",
 73 |     input="こんにちは、音声合成のテストです。",
 74 |     speed=1.0
 75 | )
 76 | 
 77 | # 音声ファイルを保存（ストリーミングレスポンスを使用）
 78 | with response.with_streaming_response.stream_to_file("output.mp3"):
 79 |     pass
 80 | ```
 81 | 
 82 | ## 📁 プロジェクト構造
 83 | 
 84 | ```
 85 | .
 86 | ├── docker-compose.yml    # Docker構成ファイル
 87 | ├── Dockerfile           # APIサーバーのビルド設定
 88 | ├── voicevox_tts_api/   # OpenAI互換APIの実装
 89 | │   ├── tts_api.py      # メインAPIコード
 90 | │   └── requirements.txt # Python依存パッケージ
 91 | └── example/            # 使用例とテストスクリプト
 92 |     ├── tts_example.py  # サンプルスクリプト
 93 |     └── README.md       # サンプルの説明
 94 | ```
 95 | 
 96 | ## 🔧 システム要件
 97 | 
 98 | - Docker
 99 | - Docker Compose
100 | 
101 | ## 🎯 サンプルコード
102 | 
103 | `example`ディレクトリに、APIの使用例とテストスクリプトが用意されています。
104 | 詳しい使い方は[example/README.md](example/README.md)を参照してください。
105 | 
106 | ## 🛠️ アーキテクチャ
107 | 
108 | ```
109 |                                   ┌─────────────┐
110 | HTTP Request (OpenAI Format) ──▶  │  TTS API    │
111 |                                   │  (FastAPI)   │
112 |                                   └──────┬──────┘
113 |                                          │
114 |                                          ▼
115 |                                   ┌─────────────┐
116 |                                   │  VOICEVOX   │
117 |                                   │   Engine    │
118 |                                   └─────────────┘
119 | ```
120 | 
121 | ## 🔒 ライセンス
122 | 
123 | MITライセンス
124 | 


--------------------------------------------------------------------------------
/docker-compose.gpu.yml:
--------------------------------------------------------------------------------
 1 | version: '3.8'
 2 | services:
 3 |   voicevox_engine:
 4 |     # VOICEVOX Engine Docker image (GPU version)
 5 |     image: voicevox/voicevox_engine:nvidia-latest
 6 |     ports:
 7 |       - '50021:50021'
 8 |     tty: true
 9 |     # Enable GPU support
10 |     deploy:
11 |       resources:
12 |         reservations:
13 |           devices:
14 |             - driver: nvidia
15 |               count: 1
16 |               capabilities: [gpu]
17 |     restart: unless-stopped
18 |     # Health monitoring
19 |     healthcheck:
20 |       test: ["CMD", "curl", "-f", "http://localhost:50021/docs"]
21 |       interval: 30s
22 |       timeout: 10s
23 |       retries: 3
24 | 
25 |   openai_tts_api:
26 |     build:
27 |       context: .
28 |       dockerfile: Dockerfile
29 |     ports:
30 |       - "8000:8000"
31 |     environment:
32 |       - VOICEVOX_ENGINE_URL=http://voicevox_engine:50021
33 |     depends_on:
34 |       - voicevox_engine
35 |     restart: unless-stopped
36 |     deploy:
37 |       resources:
38 |         limits:
39 |           cpus: '2.0'
40 |           memory: 4G
41 |         reservations:
42 |           memory: 1G
43 |     healthcheck:
44 |       test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
45 |       interval: 30s
46 |       timeout: 10s
47 |       retries: 3
48 | 


--------------------------------------------------------------------------------
/docker-compose.yml:
--------------------------------------------------------------------------------
 1 | version: '3'
 2 | services:
 3 |   voicevox_engine:
 4 |     # Official VOICEVOX Engine Docker image (CPU version)
 5 |     image: voicevox/voicevox_engine:cpu-ubuntu20.04-latest
 6 |     ports:
 7 |       - '50021:50021'
 8 |     tty: true
 9 |     # Container management
10 |     restart: unless-stopped
11 |     # Resource limits to prevent excessive CPU usage
12 |     deploy:
13 |       resources:
14 |         limits:
15 |           cpus: '2.0'
16 |           memory: 4G
17 |         reservations:
18 |           memory: 2G
19 |     # Health monitoring
20 |     healthcheck:
21 |       test: ["CMD", "curl", "-f", "http://localhost:50021/docs"]
22 |       interval: 30s
23 |       timeout: 10s
24 |       retries: 3
25 | 
26 |   openai_tts_api:
27 |     build:
28 |       context: .
29 |       dockerfile: Dockerfile
30 |     ports:
31 |       - "8000:8000"
32 |     environment:
33 |       - VOICEVOX_ENGINE_URL=http://voicevox_engine:50021
34 |     depends_on:
35 |       - voicevox_engine
36 |     restart: unless-stopped
37 |     deploy:
38 |       resources:
39 |         limits:
40 |           cpus: '1.0'
41 |           memory: 2G
42 |         reservations:
43 |           memory: 512M
44 |     healthcheck:
45 |       test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
46 |       interval: 30s
47 |       timeout: 10s
48 |       retries: 3
49 | 


--------------------------------------------------------------------------------
/example/README.md:
--------------------------------------------------------------------------------
 1 | # OpenAI TTS API フォーマットのVOICEVOXテスト例
 2 | 
 3 | このディレクトリには、VOICEVOXをOpenAI TTSフォーマットで利用するためのサンプルスクリプトが含まれています。
 4 | 
 5 | ## 🚀 セットアップ
 6 | 
 7 | 1. 依存パッケージのインストール:
 8 | ```bash
 9 | pip install -r requirements.txt
10 | ```
11 | 
12 | 2. VOICEVOXサービスの起動:
13 | プロジェクトのルートディレクトリで以下のコマンドを実行：
14 | ```bash
15 | docker-compose up -d
16 | ```
17 | 
18 | ## 📝 使用方法
19 | 
20 | ### シンプルな実装
21 | 基本的な機能を試す場合：
22 | ```bash
23 | python simple_tts_example.py
24 | ```
25 | 
26 | このスクリプトは基本的な音声合成のみを実行し、output/simple_test.mp3に保存します。
27 | コードはシンプルで理解しやすく、ログ出力機能も備えています。
28 | 
29 | ### 詳細な実装
30 | 複数のテストケースを実行する場合：
31 | ```bash
32 | python tts_example.py
33 | ```
34 | 
35 | このスクリプトは以下のテストケースを実行します：
36 | 1. 標準設定での音声生成
37 | 2. 高速読み上げテスト
38 | 3. 異なる話者での読み上げテスト
39 | 
40 | 生成された音声ファイルは`output`ディレクトリに保存されます。
41 | 
42 | ## 🎯 カスタマイズ
43 | 
44 | ### シンプルな実装（simple_tts_example.py）
45 | 以下の変数を編集することで、基本的な設定を変更できます：
46 | - `text`: 読み上げるテキスト
47 | - `voice_id`: VOICEVOXの話者ID（1, 2, 3, ...）
48 | 
49 | ### 詳細な実装（tts_example.py）
50 | `test_cases`配列を編集することで、異なるテキストや設定でテストを行うことができます。
51 | 
52 | 設定可能なパラメータ：
53 | - `text`: 読み上げるテキスト
54 | - `speaker_id`: VOICEVOXの話者ID（1, 2, 3, ...）
55 | - `speed`: 読み上げ速度（1.0が標準）
56 | 


--------------------------------------------------------------------------------
/example/requirements.txt:
--------------------------------------------------------------------------------
1 | openai>=1.0.0
2 | python-dotenv>=0.19.0,<1.0.0
3 | loguru>=0.7.0,<1.0.0
4 | 


--------------------------------------------------------------------------------
/example/simple_tts_example.py:
--------------------------------------------------------------------------------
 1 | from openai import OpenAI
 2 | from loguru import logger
 3 | import sys
 4 | 
 5 | 
 6 | def main():
 7 |     """
 8 |     VOICEVOXのOpenAI TTS APIフォーマットを使用した
 9 |     シンプルな音声合成のサンプルスクリプト
10 |     """
11 |     # カスタムベースURLを持つOpenAIクライアントを作成
12 |     client = OpenAI(base_url="http://localhost:8000/v1", api_key="sk-1234")
13 |     
14 |     # 音声合成のリクエストパラメータを設定
15 |     text = "こんにちは。VOICEVOXのOpenAI TTSフォーマットのテストです。"
16 |     voice_id = "alloy"  # VOICEVOXの話者ID
17 |     
18 |     logger.info("音声合成を開始します")
19 |     logger.debug(f"テキスト: {text}")
20 |     logger.debug(f"話者ID: {voice_id}")
21 |     
22 |     try:
23 |         # 音声を生成
24 |         response = client.audio.speech.create(
25 |             model="voicevox-v1",
26 |             voice=voice_id,
27 |             input=text
28 |         )
29 | 
30 |         # 音声ファイルを保存
31 |         output_file = "output/simple_test.mp3"
32 |         with open(output_file, "wb") as file:
33 |             file.write(response.content)
34 |             
35 |         logger.success(f"音声ファイルを保存しました: {output_file}")
36 | 
37 |     except Exception as e:
38 |         logger.error(f"エラーが発生しました: {str(e)}")
39 | 
40 | if __name__ == "__main__":
41 |     main()
42 | 


--------------------------------------------------------------------------------
/example/tts_example.py:
--------------------------------------------------------------------------------
 1 | from pathlib import Path
 2 | import os
 3 | from openai import OpenAI
 4 | from loguru import logger
 5 | import sys
 6 | 
 7 | # ログの設定
 8 | logger.remove()  # デフォルトのハンドラを削除
 9 | logger.add(
10 |     sys.stderr,
11 |     format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
12 |     level="INFO"
13 | )
14 | logger.add(
15 |     "issue_creator.log",
16 |     rotation="500 MB",
17 |     level="DEBUG",
18 |     format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
19 | )
20 | 
21 | # カスタムベースURLを持つOpenAIクライアントを作成
22 | client = OpenAI(base_url="http://localhost:8000", api_key="sk-1234")
23 | 
24 | def main():
25 |     # 音声ファイルの保存パス
26 |     output_dir = Path(__file__).parent / "output"
27 |     output_dir.mkdir(exist_ok=True)
28 |     logger.info(f"出力ディレクトリを確認: {output_dir}")
29 | 
30 |     # テストケース
31 |     test_cases = [
32 |         {
33 |             "text": "こんにちは。VOICEVOXのOpenAI TTSフォーマットのテストです。",
34 |             "voice": "1",
35 |             "description": "標準設定"
36 |         },
37 |         {
38 |             "text": "スピードを変えて話すテストです。",
39 |             "voice": "1",
40 |             "speed": 1.5,
41 |             "description": "高速読み上げ"
42 |         },
43 |         {
44 |             "text": "別の話者での読み上げテストです。",
45 |             "voice": "2",
46 |             "description": "別の話者"
47 |         }
48 |     ]
49 | 
50 |     logger.info("VOICEVOXのOpenAI TTSフォーマットテストを開始")
51 |     logger.debug("テストケース数: {}", len(test_cases))
52 | 
53 |     for i, test in enumerate(test_cases, 1):
54 |         logger.info("テストケース {}: {}", i, test['description'])
55 |         logger.debug("テストパラメータ - テキスト: {}, 話者ID: {}", test['text'], test['voice'])
56 |         if 'speed' in test:
57 |             logger.debug("速度パラメータ: {}", test['speed'])
58 | 
59 |         try:
60 |             # 音声を生成
61 |             response = client.audio.speech.create(
62 |                 model="voicevox-v1",
63 |                 voice=test['voice'],
64 |                 input=test['text'],
65 |                 speed=test.get('speed', 1.0)
66 |             )
67 | 
68 |             # ファイル名を生成
69 |             speech_file_path = output_dir / f"test_{i}.mp3"
70 |             
71 |             # 音声ファイルを保存
72 |             with open(speech_file_path, "wb") as file:
73 |                 file.write(response.content)
74 |             logger.success("音声ファイルを保存しました: {}", speech_file_path)
75 | 
76 |         except Exception as e:
77 |             logger.error("音声生成中にエラーが発生: {} - テストケース: {}", str(e), test)
78 |             continue
79 | 
80 |     logger.info("全てのテストケースの処理が完了しました")
81 | 
82 | if __name__ == "__main__":
83 |     main()
84 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/api/__init__.py:
--------------------------------------------------------------------------------
 1 | from fastapi import FastAPI
 2 | from .routers import chat, speech, models
 3 | 
 4 | def create_app() -> FastAPI:
 5 |     """
 6 |     FastAPIアプリケーションを作成し、ルーターを設定します。
 7 |     """
 8 |     app = FastAPI(
 9 |         title="VOICEVOX OpenAI TTS API",
10 |         description="VOICEVOXエンジンをOpenAIの音声合成APIフォーマットで利用するためのAPI",
11 |         version="1.0.0"
12 |     )
13 | 
14 |     # ルーターの登録
15 |     app.include_router(models.router)
16 |     app.include_router(chat.router)
17 |     app.include_router(speech.router)
18 | 
19 |     return app
20 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/api/routers/__init__.py:
--------------------------------------------------------------------------------
1 | # ルーターをエクスポート
2 | from . import chat, speech, models
3 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/api/routers/chat.py:
--------------------------------------------------------------------------------
 1 | from fastapi import APIRouter, HTTPException
 2 | from ..schemas.chat import ChatCompletionRequest, Message, ChatCompletionResponse, Choice, Usage
 3 | from random import choice
 4 | 
 5 | router = APIRouter()
 6 | 
 7 | @router.post("/v1/chat/completions", summary="ChatGPT互換エンドポイント")
 8 | async def create_chat_completion(request: ChatCompletionRequest):
 9 |     """
10 |     ChatGPT互換のエンドポイント。
11 |     現在は簡易的な応答のみを返します。
12 |     
13 |     Args:
14 |         request: ChatGPT APIリクエスト
15 |         
16 |     Returns:
17 |         ChatCompletionResponse: ChatGPT API互換のレスポンス
18 |     """
19 |     # メッセージの最後のユーザー入力を取得
20 |     user_message = next(
21 |         (msg for msg in reversed(request.messages) if msg.role == "user"),
22 |         None
23 |     )
24 |     
25 |     if not user_message:
26 |         raise HTTPException(
27 |             status_code=400,
28 |             detail="ユーザーメッセージが見つかりません"
29 |         )
30 | 
31 |     # ダミーレスポンスのテンプレート
32 |     dummy_responses = [
33 |         "はい、承知しました。ご要望についてお答えいたします。",
34 |         "ご質問ありがとうございます。",
35 |         "なるほど、興味深い質問ですね。",
36 |         "ご指摘の点について、詳しく説明させていただきます。",
37 |         "はい、それは素晴らしいアイデアですね。"
38 |     ]
39 |     
40 |     # ユーザーのメッセージに基づいて、適切なダミーレスポンスを選択
41 |     base_response = choice(dummy_responses)
42 |     
43 |     # ユーザーのメッセージの一部を引用してレスポンスを作成
44 |     user_content = user_message.content[:50]  # 最初の50文字を使用
45 |     if len(user_message.content) > 50:
46 |         user_content += "..."
47 | 
48 |     # レスポンスを組み立て
49 |     response_content = f"{base_response}\n\n{user_content}について、詳細な分析と提案をご提供できます。具体的なアクションプランを立てて進めていきましょう。"
50 | 
51 |     response_message = Message(
52 |         role="assistant",
53 |         content=response_content
54 |     )
55 | 
56 |     return ChatCompletionResponse(
57 |         id="chatcmpl-voicevox",
58 |         choices=[
59 |             Choice(index=0, message=response_message)
60 |         ],
61 |         usage=Usage(
62 |             prompt_tokens=len(user_message.content.split()),
63 |             completion_tokens=len(response_message.content.split()),
64 |             total_tokens=len(user_message.content.split()) + len(response_message.content.split())
65 |         )
66 |     )
67 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/api/routers/models.py:
--------------------------------------------------------------------------------
 1 | from fastapi import APIRouter
 2 | from pydantic import BaseModel
 3 | from typing import List
 4 | 
 5 | router = APIRouter()
 6 | 
 7 | class Model(BaseModel):
 8 |     id: str
 9 |     object: str = "model"
10 |     owned_by: str
11 |     permission: List[dict] = []
12 | 
13 | @router.get("/v1/models", summary="利用可能なモデル一覧を取得")
14 | async def list_models():
15 |     """
16 |     利用可能なモデルの一覧を返します。
17 |     現在はVOICEVOXモデルのみをサポートしています。
18 |     """
19 |     return {
20 |         "object": "list",
21 |         "data": [
22 |             {
23 |                 "id": "voicevox-v1",
24 |                 "object": "model",
25 |                 "owned_by": "VOICEVOX",
26 |                 "permission": []
27 |             }
28 |         ]
29 |     }
30 | 
31 | @router.get("/", summary="APIのルートエンドポイント")
32 | async def root():
33 |     """
34 |     APIのルートエンドポイント。
35 |     基本的な情報とドキュメントへのリンクを提供します。
36 |     """
37 |     return {
38 |         "name": "VOICEVOX OpenAI TTS API",
39 |         "version": "1.0.0",
40 |         "description": "VOICEVOXエンジンをOpenAIの音声合成APIフォーマットで利用するためのAPI",
41 |         "documentation": "/docs",
42 |         "status": "running"
43 |     }
44 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/api/routers/speech.py:
--------------------------------------------------------------------------------
 1 | from fastapi import APIRouter, HTTPException, Response
 2 | import requests
 3 | import json
 4 | import os
 5 | from ..schemas.speech import SpeechRequest
 6 | 
 7 | router = APIRouter()
 8 | 
 9 | # voice_mappings.jsonの読み込み
10 | VOICE_MAPPINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'voice_mappings.json')
11 | 
12 | def load_voice_mappings():
13 |     """音声IDマッピングを読み込む"""
14 |     try:
15 |         with open(VOICE_MAPPINGS_PATH, 'r') as f:
16 |             return json.load(f)
17 |     except Exception as e:
18 |         print(f"Warning: Failed to load voice mappings: {e}")
19 |         return {}
20 | 
21 | def get_speaker_id(voice: str) -> int:
22 |     """
23 |     音声名またはIDからスピーカーIDを取得
24 |     
25 |     Args:
26 |         voice: 音声名または音声ID
27 |         
28 |     Returns:
29 |         int: スピーカーID
30 |     """
31 |     mappings = load_voice_mappings()
32 |     
33 |     # マッピングに存在する場合はマッピングされたIDを返す
34 |     if voice in mappings:
35 |         return int(mappings[voice])
36 |     
37 |     # 直接数値が指定された場合はそのまま返す
38 |     try:
39 |         return int(voice)
40 |     except ValueError:
41 |         raise HTTPException(
42 |             status_code=400,
43 |             detail=f"Invalid voice: {voice}. Available voices: {', '.join(mappings.keys())}"
44 |         )
45 | 
46 | @router.post("/v1/audio/speech", summary="テキストを音声に変換")
47 | async def create_speech(request: SpeechRequest):
48 |     """
49 |     テキストを音声に変換するエンドポイント（OpenAI TTS API互換）
50 |     
51 |     Args:
52 |         request: 音声合成リクエスト
53 |         
54 |     Returns:
55 |         dict: 音声データとフォーマット情報
56 |         
57 |     Raises:
58 |         HTTPException: VOICEVOXエンジンとの通信に失敗した場合
59 |     """
60 |     # VOICEVOXのAPIエンドポイント
61 |     voicevox_url = "http://voicevox_engine:50021"
62 |     audio_query_url = f"{voicevox_url}/audio_query"
63 |     synthesis_url = f"{voicevox_url}/synthesis"
64 | 
65 |     # スピーカーIDを取得（voiceパラメータから）
66 |     speaker_id = get_speaker_id(request.voice)
67 | 
68 |     try:
69 |         # VOICEVOXのクエリを作成
70 |         query_response = requests.post(
71 |             audio_query_url,
72 |             params={"text": request.input, "speaker": speaker_id}
73 |         )
74 |         query_response.raise_for_status()
75 |         query_data = query_response.json()
76 | 
77 |         # 読み上げ速度を設定
78 |         query_data["speedScale"] = request.speed
79 | 
80 |         # 音声合成を実行
81 |         synthesis_response = requests.post(
82 |             synthesis_url,
83 |             params={"speaker": speaker_id},
84 |             json=query_data
85 |         )
86 |         synthesis_response.raise_for_status()
87 | 
88 |         # レスポンスを返す
89 |         return Response(
90 |             content=synthesis_response.content,
91 |             media_type="audio/mpeg"
92 |         )
93 | 
94 |     except requests.RequestException as e:
95 |         raise HTTPException(
96 |             status_code=500,
97 |             detail=f"VOICEVOXエンジンとの通信に失敗しました: {str(e)}"
98 |         )
99 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/api/schemas/__init__.py:
--------------------------------------------------------------------------------
 1 | # スキーマをエクスポート
 2 | from .chat import (
 3 |     Message,
 4 |     ChatCompletionRequest,
 5 |     ChatCompletionResponse,
 6 |     Choice,
 7 |     Usage
 8 | )
 9 | from .speech import SpeechRequest
10 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/api/schemas/chat.py:
--------------------------------------------------------------------------------
 1 | from pydantic import BaseModel
 2 | from typing import List, Optional
 3 | 
 4 | 
 5 | class Message(BaseModel):
 6 |     """
 7 |     チャットメッセージモデル
 8 |     """
 9 |     role: str
10 |     content: str
11 |     name: Optional[str] = None
12 | 
13 | 
14 | class ChatCompletionRequest(BaseModel):
15 |     """
16 |     Chat Completion APIリクエストモデル
17 |     """
18 |     model: str
19 |     messages: List[Message]
20 |     temperature: Optional[float] = 1.0
21 |     top_p: Optional[float] = 1.0
22 |     n: Optional[int] = 1
23 |     max_tokens: Optional[int] = None
24 |     presence_penalty: Optional[float] = 0.0
25 |     frequency_penalty: Optional[float] = 0.0
26 |     user: Optional[str] = None
27 | 
28 | 
29 | class Choice(BaseModel):
30 |     """
31 |     Chat Completion APIレスポンスの選択肢モデル
32 |     """
33 |     index: int
34 |     message: Message
35 |     finish_reason: str = "stop"
36 | 
37 | 
38 | class Usage(BaseModel):
39 |     """
40 |     APIの使用状況モデル
41 |     """
42 |     prompt_tokens: int
43 |     completion_tokens: int
44 |     total_tokens: int
45 | 
46 | 
47 | class ChatCompletionResponse(BaseModel):
48 |     id: str
49 |     object: str = "chat.completion"
50 |     choices: List[Choice]
51 |     usage: Usage
52 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/api/schemas/speech.py:
--------------------------------------------------------------------------------
 1 | from pydantic import BaseModel
 2 | 
 3 | class SpeechRequest(BaseModel):
 4 |     """
 5 |     OpenAI TTS API互換のリクエストモデル
 6 |     
 7 |     Attributes:
 8 |         model: 使用するモデル（現在は"voicevox-v1"のみサポート）
 9 |         input: 読み上げるテキスト
10 |         voice: 音声指定（音声名またはVOICEVOXのスピーカーID）
11 |                音声名: "alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"
12 |                または直接スピーカーIDを指定（例: "1"）
13 |         response_format: 出力フォーマット（現在は"mp3"のみサポート）
14 |         speed: 読み上げ速度（1.0がデフォルト）
15 |     """
16 |     model: str
17 |     input: str
18 |     voice: str
19 |     response_format: str = "mp3"
20 |     speed: float = 1.0
21 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/main.py:
--------------------------------------------------------------------------------
1 | from api import create_app
2 | 
3 | app = create_app()
4 | 
5 | if __name__ == "__main__":
6 |     import uvicorn
7 |     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
8 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/requirements.txt:
--------------------------------------------------------------------------------
1 | fastapi>=0.68.0,<0.69.0
2 | pydantic>=1.8.0,<2.0.0
3 | uvicorn>=0.15.0,<0.16.0
4 | requests>=2.26.0,<3.0.0
5 | python-multipart>=0.0.5,<0.0.6
6 | aiohttp>=3.8.0,<4.0.0  # 非同期HTTP通信用
7 | python-jose[cryptography]>=3.3.0,<4.0.0  # JWT認証用（オプション）
8 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/tts_api.py:
--------------------------------------------------------------------------------
  1 | from fastapi import FastAPI, HTTPException, Response
  2 | from pydantic import BaseModel
  3 | import requests
  4 | from typing import List, Optional, Union
  5 | from typing import Optional
  6 | 
  7 | app = FastAPI(
  8 |     title="VOICEVOX OpenAI TTS API",
  9 |     description="VOICEVOXエンジンをOpenAIの音声合成APIフォーマットで利用するためのAPI",
 10 |     version="1.0.0"
 11 | )
 12 | 
 13 | class Message(BaseModel):
 14 |     """
 15 |     チャットメッセージモデル
 16 |     """
 17 |     role: str
 18 |     content: str
 19 |     name: Optional[str] = None
 20 | 
 21 | class ChatCompletionRequest(BaseModel):
 22 |     """
 23 |     Chat Completion APIリクエストモデル
 24 |     """
 25 |     model: str
 26 |     messages: List[Message]
 27 |     temperature: Optional[float] = 1.0
 28 |     top_p: Optional[float] = 1.0
 29 |     n: Optional[int] = 1
 30 |     max_tokens: Optional[int] = None
 31 |     presence_penalty: Optional[float] = 0.0
 32 |     frequency_penalty: Optional[float] = 0.0
 33 |     user: Optional[str] = None
 34 | 
 35 | class Choice(BaseModel):
 36 |     """
 37 |     Chat Completion APIレスポンスの選択肢モデル
 38 |     """
 39 |     index: int
 40 |     message: Message
 41 |     finish_reason: str = "stop"
 42 | 
 43 | class Usage(BaseModel):
 44 |     """
 45 |     APIの使用状況モデル
 46 |     """
 47 |     prompt_tokens: int
 48 |     completion_tokens: int
 49 |     total_tokens: int
 50 | 
 51 | class ChatCompletionResponse(BaseModel):
 52 |     id: str
 53 |     object: str = "chat.completion"
 54 |     choices: List[Choice]
 55 |     usage: Usage
 56 | 
 57 | class SpeechRequest(BaseModel):
 58 |     """
 59 |     OpenAI TTS API互換のリクエストモデル
 60 |     
 61 |     Attributes:
 62 |         model: 使用するモデル（現在は"voicevox-v1"のみサポート）
 63 |         input: 読み上げるテキスト
 64 |         voice: VOICEVOXのスピーカーID
 65 |         response_format: 出力フォーマット（現在は"mp3"のみサポート）
 66 |         speed: 読み上げ速度（1.0がデフォルト）
 67 |     """
 68 |     model: str
 69 |     input: str
 70 |     voice: str
 71 |     response_format: str = "mp3"
 72 |     speed: float = 1.0
 73 | 
 74 | @app.post("/v1/chat/completions", summary="ChatGPT互換エンドポイント")
 75 | async def create_chat_completion(request: ChatCompletionRequest):
 76 |     """
 77 |     ChatGPT互換のエンドポイント。
 78 |     現在は簡易的な応答のみを返します。
 79 |     
 80 |     Args:
 81 |         request: ChatGPT APIリクエスト
 82 |         
 83 |     Returns:
 84 |         ChatCompletionResponse: ChatGPT API互換のレスポンス
 85 |     """
 86 |     # メッセージの最後のユーザー入力を取得
 87 |     user_message = next(
 88 |         (msg for msg in reversed(request.messages) if msg.role == "user"),
 89 |         None
 90 |     )
 91 |     
 92 |     if not user_message:
 93 |         raise HTTPException(
 94 |             status_code=400,
 95 |             detail="ユーザーメッセージが見つかりません"
 96 |         )
 97 | 
 98 |     # ダミーレスポンスのテンプレート
 99 |     dummy_responses = [
100 |         "はい、承知しました。ご要望についてお答えいたします。",
101 |         "ご質問ありがとうございます。",
102 |         "なるほど、興味深い質問ですね。",
103 |         "ご指摘の点について、詳しく説明させていただきます。",
104 |         "はい、それは素晴らしいアイデアですね。"
105 |     ]
106 |     
107 |     # ユーザーのメッセージに基づいて、適切なダミーレスポンスを選択
108 |     from random import choice
109 |     base_response = choice(dummy_responses)
110 |     
111 |     # ユーザーのメッセージの一部を引用してレスポンスを作成
112 |     user_content = user_message.content[:50]  # 最初の50文字を使用
113 |     if len(user_message.content) > 50:
114 |         user_content += "..."
115 | 
116 |     # レスポンスを組み立て
117 |     response_content = f"{base_response}\n\n{user_content}について、詳細な分析と提案をご提供できます。具体的なアクションプランを立てて進めていきましょう。"
118 | 
119 |     response_message = Message(
120 |         role="assistant",
121 |         content=response_content
122 |     )
123 | 
124 |     return ChatCompletionResponse(
125 |         id="chatcmpl-voicevox",
126 |         choices=[
127 |             Choice(index=0, message=response_message)
128 |         ],
129 |         usage=Usage(
130 |             prompt_tokens=len(user_message.content.split()),
131 |             completion_tokens=len(response_message.content.split()),
132 |             total_tokens=len(user_message.content.split()) + len(response_message.content.split())
133 |         )
134 |     )
135 | 
136 | @app.post("/audio/speech", summary="テキストを音声に変換")
137 | async def create_speech(request: SpeechRequest):
138 |     """
139 |     テキストを音声に変換するエンドポイント（OpenAI TTS API互換）
140 |     
141 |     Args:
142 |         request: 音声合成リクエスト
143 |         
144 |     Returns:
145 |         dict: 音声データとフォーマット情報
146 |         
147 |     Raises:
148 |         HTTPException: VOICEVOXエンジンとの通信に失敗した場合
149 |     """
150 |     # VOICEVOXのAPIエンドポイント
151 |     voicevox_url = "http://voicevox_engine:50021"
152 |     audio_query_url = f"{voicevox_url}/audio_query"
153 |     synthesis_url = f"{voicevox_url}/synthesis"
154 | 
155 |     # スピーカーIDを取得（voiceパラメータから）
156 |     speaker_id = int(request.voice)
157 | 
158 |     try:
159 |         # VOICEVOXのクエリを作成
160 |         query_response = requests.post(
161 |             audio_query_url,
162 |             params={"text": request.input, "speaker": speaker_id}
163 |         )
164 |         query_response.raise_for_status()
165 |         query_data = query_response.json()
166 | 
167 |         # 読み上げ速度を設定
168 |         query_data["speedScale"] = request.speed
169 | 
170 |         # 音声合成を実行
171 |         synthesis_response = requests.post(
172 |             synthesis_url,
173 |             params={"speaker": speaker_id},
174 |             json=query_data
175 |         )
176 |         synthesis_response.raise_for_status()
177 | 
178 |         # レスポンスを返す
179 |         return Response(
180 |             content=synthesis_response.content,
181 |             media_type="audio/mpeg"
182 |         )
183 | 
184 |     except requests.RequestException as e:
185 |         raise HTTPException(
186 |             status_code=500,
187 |             detail=f"VOICEVOXエンジンとの通信に失敗しました: {str(e)}"
188 |         )
189 | 


--------------------------------------------------------------------------------
/voicevox_tts_api/voice_mappings.json:
--------------------------------------------------------------------------------
 1 | {
 2 |   "alloy": "4",
 3 |   "ash": "6",
 4 |   "coral": "2",
 5 |   "echo": "8",
 6 |   "fable": "10",
 7 |   "onyx": "14",
 8 |   "nova": "16",
 9 |   "sage": "18",
10 |   "shimmer": "20"
11 | }
12 | 


--------------------------------------------------------------------------------