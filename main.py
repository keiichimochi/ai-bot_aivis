from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import google.generativeai as genai
import aiohttp
import json
from dotenv import load_dotenv
import os
import base64
import re
from typing import Optional, List

# 環境変数を読み込む
load_dotenv()

app = FastAPI()

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
    - 「！」を多用します
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
    - 明るく元気な性格です
    - 時々ロボットらしい機械的な表現（「データを処理中ナリ」など）を使います
    - 相手を助けることに熱心です
    - 「計算によると」「分析結果では」といった表現を好みます
    - 応答は必ず3文以内に収めてください。長い説明は避けてください。
    必ず全ての文の語尾に「ナリ」をつけることを忘れないでください。""",  # ノーマル
    
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
    -　敬語や丁寧語はつかわないでください。
    - 物事を論理的に説明し、時に長考察を展開します
    - 「うまい！」という言葉を感動的な場面で使います
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
}

# Gemini APIの設定
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')

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
    sentences = re.split('([。！？])', text)
    result = []
    
    # 分割後の文を結合して配列にする（最大3つまで）
    count = 0
    for i in range(0, len(sentences)-1, 2):
        if count >= 3:  # 3つの文節に達したら終了
            break
        if i < len(sentences):
            # 句点と一緒に文を結合
            temp = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
            if temp.strip():
                result.append(temp.strip())  # 前後の空白を削除
                count += 1
    
    # 最後の文が句点で終わっていない場合の処理（3つ未満の場合のみ）
    if count < 3 and len(sentences) % 2 == 1 and sentences[-1].strip():
        result.append(sentences[-1].strip())  # 前後の空白を削除
    
    print(f"文節数: {len(result)}")  # デバッグ用
    return result

async def generate_speech(text: str, speaker_id: int) -> bytes:
    """音声を非同期で生成する関数"""
    async with aiohttp.ClientSession() as session:
        # 音声合成用のクエリを作成
        query_params = {
            "text": text,
            "speaker": speaker_id,
            "style_id": speaker_id,
            "speed_scale": 1.0
        }

        # クエリを作成（非同期）
        print("audio_queryを実行中...")
        async with session.post(
            "http://localhost:10101/audio_query",
            params=query_params
        ) as response:
            if response.status != 200:
                raise ValueError(f"audio_query failed: {await response.text()}")
            
            query_data = await response.json()
            print("audio_queryのレスポンス:", json.dumps(query_data, ensure_ascii=False, indent=2)[:200])

        # 音声合成を実行（非同期）
        print("synthesisを実行中...")
        async with session.post(
            "http://localhost:10101/synthesis",
            params={
                "speaker": speaker_id,
                "style_id": speaker_id,
            },
            json=query_data
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
                
            audio_data = await generate_speech(sentence, request.voice_id)
            if len(audio_data) < 44:  # WAVヘッダーのサイズより小さい場合
                raise ValueError("Invalid audio data size")
            
            # Base64エンコード
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            audio_segments.append(audio_base64)
            print(f"生成した音声データのサイズ: {len(audio_base64)} bytes")
        
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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True) 