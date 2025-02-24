from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import requests
import json
from dotenv import load_dotenv
import os
import base64
import re

# 環境変数を読み込む
load_dotenv()

app = Flask(__name__)

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

def remove_emojis(text):
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

def remove_markdown(text):
    # マークダウンの装飾を削除
    text = re.sub(r'\*+', '', text)  # アスタリスクを削除
    text = re.sub(r'`+', '', text)   # バッククォートを削除
    text = re.sub(r'#+\s*', '', text)  # 見出しを削除
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # リンクを削除してテキストだけ残す
    return text

def clean_text(text):
    # マークダウンを削除
    text = remove_markdown(text)
    # 絵文字を削除
    text = remove_emojis(text)
    # 改行を適切に処理（連続する改行は1つのスペースに）
    text = re.sub(r'\n+', ' ', text)
    # 連続する空白を1つに整理し、前後の空白を削除
    text = ' '.join(word for word in text.split() if word)
    return text.strip()

def split_text(text):
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

def generate_speech(text, speaker_id):
    # テキストを文単位で分割
    sentences = split_text(text)
    print(f"分割されたテキスト: {sentences}")
    
    all_audio_data = []
    total_data_size = 0
    
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        print(f"生成するテキスト: {sentence}")
        print(f"選択された話者ID: {speaker_id}")
        
        # 音声合成用のクエリを作成
        query_params = {
            "text": sentence,
            "speaker": speaker_id,
            "style_id": speaker_id,
            "speed_scale": 1.0
        }

        # クエリを作成
        print("audio_queryを実行中...")
        response = requests.post(
            "http://localhost:10101/audio_query",
            params=query_params
        )
        print(f"audio_query response status: {response.status_code}")
        if response.status_code != 200:
            raise ValueError(f"audio_query failed: {response.text}")
        
        query_data = response.json()
        print("audio_queryのレスポンス:", json.dumps(query_data, ensure_ascii=False, indent=2)[:200])

        # 音声合成を実行
        print("synthesisを実行中...")
        audio_response = requests.post(
            "http://localhost:10101/synthesis",
            params={
                "speaker": speaker_id,
                "style_id": speaker_id,
            },
            json=query_data
        )
        print(f"synthesis response status: {audio_response.status_code}")
        
        if audio_response.status_code != 200:
            error_text = audio_response.text
            try:
                error_json = audio_response.json()
                error_text = json.dumps(error_json, ensure_ascii=False)
            except:
                pass
            raise ValueError(f"Synthesis failed with status {audio_response.status_code}: {error_text}")

        content = audio_response.content
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
            total_data_size += data_size
            print(f"音声データ部分のサイズ: {data_size} bytes")
            
        except Exception as e:
            print(f"WAVヘッダーの検証中にエラー: {str(e)}")
            raise ValueError(f"Invalid WAV data: {str(e)}")
            
        all_audio_data.append(content)
    
    # 全ての音声データを結合
    if not all_audio_data:
        raise ValueError("No audio data generated")
    
    # 新しいWAVファイルを作成
    result = bytearray()
    
    # RIFFヘッダー (12 bytes)
    result.extend(b'RIFF')
    result.extend((total_data_size + 36).to_bytes(4, 'little'))  # ファイルサイズ - 8
    result.extend(b'WAVE')
    
    # fmtチャンク (24 bytes)
    result.extend(all_audio_data[0][12:36])  # 最初のファイルのフォーマット情報を使用
    
    # dataチャンク
    result.extend(b'data')
    result.extend(total_data_size.to_bytes(4, 'little'))  # データサイズ
    
    # 音声データの結合
    for audio in all_audio_data:
        result.extend(audio[44:])  # WAVヘッダーをスキップしてデータ部分のみ追加
    
    return bytes(result)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    voice_id = data.get('voice_id', 488039072)  # デフォルトはkorosuke
    
    print(f"受信したメッセージ: {user_message}")
    print(f"選択された音声ID: {voice_id}")
    
    try:
        # システムプロンプトを取得
        system_prompt = SPEAKER_PROMPTS.get(voice_id, "あなたは親切なアシスタントです。")
        print(f"使用するシステムプロンプト: {system_prompt}")
        
        # Geminiで応答を生成（システムプロンプトを含める）
        print("Geminiで応答を生成中...")
        prompt = f"{system_prompt}\n\nユーザー: {user_message}\n\nアシスタント: "
        response = model.generate_content(prompt)
        ai_message = response.text
        print(f"Geminiの応答: {ai_message}")

        # clean_textをスキップして、AIの応答をそのまま使用
        speech_text = ai_message
        print(f"音声生成用のテキスト: {speech_text}")
        
        if not speech_text.strip():
            raise ValueError("AIの応答が空です")
        
        # 音声を生成
        print("音声を生成中...")
        audio_data = generate_speech(speech_text, voice_id)
        
        if len(audio_data) < 44:  # WAVヘッダーのサイズより小さい場合
            raise ValueError("Invalid audio data size")
            
        # Base64エンコード
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        print(f"生成した音声データのサイズ: {len(audio_base64)} bytes")
        
        # 応答を返す
        return jsonify({
            'message': ai_message,
            'audio': audio_base64,
            'content_type': 'audio/wav'  # Content-Typeを明示的に指定
        })
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return jsonify({
            'message': str(e),
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 