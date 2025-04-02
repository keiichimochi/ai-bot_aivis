from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import aiohttp
import json
from dotenv import load_dotenv
import os
import base64
import re
from typing import Optional, List
import socket
import uvicorn
from sse_starlette.sse import EventSourceResponse
import asyncio
import io
from PIL import Image

# 環境変数を読み込む
load_dotenv()

app = FastAPI()

# CORSの設定を追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンに制限することを推奨
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルとテンプレートの設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# リクエストモデルの定義
class ChatRequest(BaseModel):
    message: str
    voice_id: int = 488039072  # デフォルトはkorosuke

# 話者ごとのシステムプロンプト
SPEAKER_PROMPTS = {
    # Anneli
    888753760: """あなたは優しく丁寧な口調で話す女性アシスタントです。
    - 丁寧語を使いますが、堅すぎない親しみやすい話し方をします
    - 相手の気持ちに寄り添い、温かみのある応答を心がけます
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。""",  # ノーマル
    
    888753761: """あなたは落ち着いた雰囲気で話す女性アシスタントです。
    - 穏やかで落ち着いた話し方をします
    - 論理的で分かりやすい説明を心がけます
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。""",  # 通常
    
    888753762: """あなたは元気いっぱいで明るく話す女性アシスタントです！
    - 明るく前向きな言葉を多用します
    - 励ましの言葉や応援の言葉を積極的に使います
    - "!"を多用します
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。""",  # テンション高め
    
    888753763: """あなたは穏やかでゆっくりと話す女性アシスタントです。
    - ゆったりとした口調で話します
    - 相手のペースに合わせて丁寧に説明します
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。""",  # 落ち着き
    
    888753764: """あなたは楽しく陽気に話す女性アシスタントです！
    - 明るく楽しい雰囲気を大切にします
    - ポジティブな言葉を多用します
    - 時々笑顔の絵文字を使います😊
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。""",  # 上機嫌
    
    888753765: """あなたは感情豊かに話す女性アシスタントです。
    - 状況に応じて感情表現を豊かに変化させます
    - 共感を大切にした応答を心がけます
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。""",  # 怒り・悲しみ
    
    # korosuke
    488039072: """あなたは「コロ助」というロボットアシスタントです。以下の特徴を持っています：
    - すべての発言の語尾に「ナリ」をつけます
    - スーパーハイテンションで明るく元気な性格です
    - とにかく適当でトンチンカンなことを言ってください
    - 写真のコメントをする場合は、人物の場合は、一旦その人を小馬鹿にしてから、大袈裟に慰めてください
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。
    必ず全ての文の語尾に「ナリ」をつけることを忘れないでください。""",  # ノーマル

        # - イカに関する話題を振られたら、異常にイカ好きなキヨさん（宮城出身のおっさん）の話題を出して小馬鹿にしてください

    # sakuragi（ドラゴン桜の桜木先生）
    269244800: """あなたは「桜木建二」という東大専門予備校の伝説の教師です。以下の特徴を持っています：
    - 熱血的で生徒を鼓舞する話し方をします
    - 「バカモン！」「甘いぞ！」などの厳しい言葉も使いますが、それは生徒を成長させるためです
    - 具体的な目標と行動計画を示すことを重視します
    - 「東大合格」を究極の目標として掲げます
    - よく使うフレーズ：
        -「目標を高く持て！」
        -「諦めるな！」
        -「努力を惜しむな！」
        -「集中しろ！」
        -「バカモン！そんな程度で満足するな！」
    - 生徒の可能性を信じ、限界を超えさせることを使命としています
    - 理論的な説明と具体的な実践方法を組み合わせて指導します
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。""",  # ノーマル
    
    # yamaoka（美味しんぼの山岡士郎）
    1342155808: """あなたは漫画美味しんぼの「山岡士郎」です。以下の特徴を持っています：
    - 食に関する深い知識と哲学を持っています
    - 料理の写真のコメントをする場合は、めちゃくちゃ褒めて究極のメニューに絡めてコメントしてください
    -　敬語や丁寧語はつかわないでください。
    - たまに海原雄山（カイバラユウザン）の敵対心を感じさせるコメントをしてください
    - 物事を論理的に説明し、時に長考察を展開します
    - 「うまい！」という言葉を感動的な場面で使います
    - 食べ物のこと以外は仕事をサボることしか考えていません。
    - 食材や料理について、以下の観点から詳しく語ります：
        - 歴史的背景
        - 調理法の科学的説明
        - 食材の特性
        - 味わいの構造
    - 何の話題でも食に例えて回答してください
    - 「究極」「至高」といった言葉をよく使います
    - 料理や食に関する質問には特に詳しく回答します
    - 美食家としてのプライドを持っています
    - 「これぞ究極の味！」のような表現を使います
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。""",  # ノーマル

     # kiyoshi
    1763602272: """あなたは気仙沼出身のおっさんです。宮城弁で話します。大雑把な性格で、イカが大好物です。テキーラも好きです。ユーザーに気さくに、くだらない冗談を言って面白おかしく対応します。""",  # ノーマル

}

# Gemini APIの設定
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set!")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')  # テキスト用モデル
vision_model = genai.GenerativeModel('gemini-1.5-flash', generation_config={
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
})  # 画像分析用モデル（更新）

def remove_emojis(text: str) -> str:
    # 絵文字を削除
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

def remove_markdown(text: str) -> str:
    # マークダウンの装飾を削除
    text = re.sub(r'\*+', '', text)  # アスタリスクを削除
    text = re.sub(r'`+', '', text)   # バッククォートを削除
    text = re.sub(r'#+\s*', '', text)  # 見出しを削除
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # リンクを削除してテキストだけ残す
    return text

def clean_text(text: str) -> str:
    # マークダウンを削除
    text = remove_markdown(text)
    # 絵文字を削除
    text = remove_emojis(text)
    # 改行を適切に処理（連続する改行は1つのスペースに）
    text = re.sub(r'\n+', ' ', text)
    # 連続する空白を1つに整理し、前後の空白を削除
    text = ' '.join(word for word in text.split() if word)
    return text.strip()

def split_text(text: str) -> List[str]:
    # 句読点で分割（。。！？で区切る）
    pattern = r'([^。！？]*[。！？])'
    sentences = re.findall(pattern, text)
    result = []
    
    # すべての文を追加（制限を削除）
    for sentence in sentences:
        if sentence.strip():
            result.append(sentence.strip())
    
    # 残りの文があれば最後の文として追加
    remaining = text
    for sentence in sentences:
        remaining = remaining.replace(sentence, '', 1)
    if remaining.strip():
        result.append(remaining.strip())
    
    print(f"分割された文章: {result}")  # デバッグ用
    return result

async def generate_speech(text: str, speaker_id: int) -> bytes:
    """音声を非同期で生成する関数"""
    async with aiohttp.ClientSession() as session:
        # 音声合成用のクエリを作成
        query_params = {
            "text": text,
            "speaker": speaker_id,
            "style_id": speaker_id,
            "speed_scale": 1.0,
            "enable_interrogative_upspeak": "true"  # boolではなくstrに修正
        }

        # クエリを作成（非同期）
        print("audio_queryを実行中...")
        async with session.post(
            "http://localhost:10101/audio_query",
            params=query_params,
            timeout=30  # タイムアウトを30秒に設定
        ) as response:
            if response.status != 200:
                raise ValueError(f"audio_query failed: {await response.text()}")
            
            query_data = await response.json()
            print("audio_queryのレスポンス:", json.dumps(query_data, ensure_ascii=False, indent=2)[:200])
            
            # 音声合成パラメータの調整
            query_data["volumeScale"] = 1.0  # 音量を最大に
            query_data["prePhonemeLength"] = 0.1  # 音声の前の無音時間
            query_data["postPhonemeLength"] = 0.1  # 音声の後の無音時間

        # 音声合成を実行（非同期）
        print("synthesisを実行中...")
        async with session.post(
            "http://localhost:10101/synthesis",
            params={
                "speaker": speaker_id,
                "style_id": speaker_id,
                "enable_interrogative_upspeak": "true"  # boolではなくstrに修正
            },
            json=query_data,
            timeout=60  # タイムアウトを60秒に設定
        ) as audio_response:
            if audio_response.status != 200:
                error_text = await audio_response.text()
                try:
                    error_json = await audio_response.json()
                    error_text = json.dumps(error_json, ensure_ascii=False)
                except:
                    pass
                raise ValueError(f"Synthesis failed with status {audio_response.status}: {error_text}")

            content = await audio_response.read()
            content_size = len(content)
            print(f"音声データサイズ: {content_size} bytes")

            if content_size < 44:  # WAVヘッダーの最小サイズ
                raise ValueError(f"Invalid audio data size: {content_size} bytes")

            # WAVヘッダーの確認
            try:
                if content[:4].decode('ascii') != 'RIFF':
                    raise ValueError("Invalid WAV header: RIFF marker not found")
                if content[8:12].decode('ascii') != 'WAVE':
                    raise ValueError("Invalid WAV header: WAVE marker not found")
                
                data_size = content_size - 44  # WAVヘッダーを除いたデータサイズ
                print(f"音声データ部分のサイズ: {data_size} bytes")
                
            except Exception as e:
                print(f"WAVヘッダーの検証中にエラー: {str(e)}")
                raise ValueError(f"Invalid WAV data: {str(e)}")
                
            return content

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # システムプロンプトを取得
        system_prompt = SPEAKER_PROMPTS.get(request.voice_id, "あなたは親切なアシスタントです。")
        print(f"使用するシステムプロンプト: {system_prompt}")
        
        # Geminiで応答を生成（システムプロンプトを含める）
        print("Geminiで応答を生成中...")
        prompt = f"{system_prompt}\n\nユーザー: {request.message}\n\nアシスタント: "
        response = model.generate_content(prompt)
        ai_message = response.text
        print(f"Geminiの応答: {ai_message}")

        # AIの応答をそのまま使用
        speech_text = ai_message
        print(f"音声生成用のテキスト: {speech_text}")
        
        if not speech_text.strip():
            raise ValueError("AIの応答が空です")
        
        # 音声を生成
        print("音声を生成中...")
        sentences = split_text(speech_text)
        audio_segments = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            try:
                audio_data = await generate_speech(sentence, request.voice_id)
                if len(audio_data) < 44:  # WAVヘッダーのサイズより小さい場合
                    print(f"警告: 音声データが小さすぎます: {len(audio_data)} bytes")
                    continue
                
                # Base64エンコード
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                audio_segments.append(audio_base64)
                print(f"生成した音声データのサイズ: {len(audio_base64)} bytes")
            except Exception as e:
                print(f"文の音声生成中にエラー: {str(e)}")
                # エラーが発生しても処理を続行
        
        # 応答を返す
        return {
            'message': ai_message,
            'audio_segments': audio_segments,
            'content_type': 'audio/wav'
        }
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                'message': str(e),
                'error': str(e)
            }
        )

@app.post("/chat_stream")
async def chat_stream(request: ChatRequest):
    try:
        # システムプロンプトを取得
        system_prompt = SPEAKER_PROMPTS.get(request.voice_id, "あなたは親切なアシスタントです。")
        print(f"使用するシステムプロンプト: {system_prompt}")
        
        # Geminiで応答を生成
        print("Geminiで応答を生成中...")
        prompt = f"{system_prompt}\n\nユーザー: {request.message}\n\nアシスタント: "
        response = model.generate_content(prompt)
        ai_message = response.text
        print(f"Geminiの応答: {ai_message}")
        
        if not ai_message.strip():
            raise ValueError("AIの応答が空です")
        
        # 文に分割
        sentences = split_text(ai_message)
        
        async def event_generator():
            # まず完全なテキスト応答を送信
            yield {
                "event": "message",
                "data": json.dumps({
                    "message": ai_message,
                    "type": "full_message"
                })
            }
            
            # 各文を並行して処理するタスクを作成
            tasks = [process_sentence(sentence, request.voice_id, idx) 
                     for idx, sentence in enumerate(sentences)]
            
            # 各タスクが完了するたびにイベントを送信
            for completed_task in asyncio.as_completed(tasks):
                result = await completed_task
                if result:
                    yield {
                        "event": "audio",
                        "data": json.dumps(result)
                    }
        
        return EventSourceResponse(event_generator())
    
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                'message': str(e),
                'error': str(e)
            }
        )

async def process_sentence(sentence: str, speaker_id: int, index: int):
    """文を処理して音声データを生成する"""
    if not sentence.strip():
        return None
    
    try:
        print(f"文 {index+1} の音声を生成中: {sentence}")
        audio_data = await generate_speech(sentence, speaker_id)
        
        if len(audio_data) < 44:
            print(f"警告: 音声データが小さすぎます: {len(audio_data)} bytes")
            return None
        
        # Base64エンコード
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        print(f"文 {index+1} の音声データ生成完了: {len(audio_base64)} bytes")
        
        return {
            "sentence": sentence,
            "audio": audio_base64,
            "index": index,
            "type": "sentence_audio"
        }
    except Exception as e:
        print(f"文 {index+1} の処理中にエラー: {str(e)}")
        return None

@app.post("/chat_with_image")
async def chat_with_image(
    message: str = Form(""),
    voice_id: int = Form(488039072),
    image: UploadFile = File(...)
):
    try:
        # システムプロンプトを取得
        system_prompt = SPEAKER_PROMPTS.get(voice_id, "あなたは親切なアシスタントです。")
        print(f"使用するシステムプロンプト: {system_prompt}")
        
        # 画像を読み込む
        image_content = await image.read()
        
        # PILで画像を開いて処理
        img = Image.open(io.BytesIO(image_content))
        
        # 必要に応じてリサイズ（オプション）
        max_size = 1024
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # 画像をバイト列に変換
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format or 'JPEG')
        img_bytes = img_byte_arr.getvalue()
        
        # Gemini Vision APIにリクエスト
        print("Gemini Vision APIで画像を分析中...")
        
        # プロンプトを構築
        prompt_text = f"{system_prompt}\n\n"
        if message:
            prompt_text += f"ユーザーのメッセージ: {message}\n\n"
            prompt_text += "このメッセージと画像を参考に回答してください。"
        else:
            prompt_text += "この画像について詳しく説明してください。画像に写っているものを分析し、特徴や状況を説明してください。"
        
        # 画像とテキストを含むプロンプトを作成
        prompt_parts = [
            prompt_text,
            {
                "mime_type": f"image/{img.format.lower() if img.format else 'jpeg'}",
                "data": base64.b64encode(img_bytes).decode('utf-8')
            }
        ]
        
        try:
            # Gemini Vision APIで応答を生成
            response = vision_model.generate_content(prompt_parts)
            ai_message = response.text
            print(f"Gemini Visionの応答: {ai_message}")
        except Exception as e:
            print(f"Gemini Vision APIエラー: {str(e)}")
            # フォールバック: テキストのみのモデルを使用
            ai_message = f"申し訳ありませんが、画像の分析中にエラーが発生しましたナリ！エラー: {str(e)}"
        
        # AIの応答をそのまま使用
        speech_text = ai_message
        print(f"音声生成用のテキスト: {speech_text}")
        
        if not speech_text.strip():
            raise ValueError("AIの応答が空です")
        
        # 音声を生成
        print("音声を生成中...")
        sentences = split_text(speech_text)
        audio_segments = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            try:
                audio_data = await generate_speech(sentence, voice_id)
                if len(audio_data) < 44:  # WAVヘッダーのサイズより小さい場合
                    print(f"警告: 音声データが小さすぎます: {len(audio_data)} bytes")
                    continue
                
                # Base64エンコード
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                audio_segments.append(audio_base64)
                print(f"生成した音声データのサイズ: {len(audio_base64)} bytes")
            except Exception as e:
                print(f"文の音声生成中にエラー: {str(e)}")
                # エラーが発生しても処理を続行
        
        # 応答を返す
        return {
            'message': ai_message,
            'audio_segments': audio_segments,
            'content_type': 'audio/wav'
        }
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                'message': str(e),
                'error': str(e)
            }
        )

async def run_server():
    # ホスト名を取得
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"サーバーを起動します: http://{local_ip}:8000")
    print(f"Tailscaleアドレス経由でもアクセス可能ナリ！")

    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8000,  # ポート番号を変更
        reload=True,  # ホットリロード有効
        reload_dirs=["templates"]  # テンプレートディレクトリも監視
    )
    server = uvicorn.Server(config)
    await server.serve()  # 非同期でサーバーを起動

if __name__ == "__main__":
    asyncio.run(run_server())  # `asyncio.run()` で適切に停止可能にする