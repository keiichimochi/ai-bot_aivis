from flask import Flask, render_template, request, jsonify
from litellm import completion # LiteLLMをインポート
import requests
import json
from dotenv import load_dotenv
import os
import base64
import re
import psutil
import socket
import time

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
        try:
            response = requests.post(
                "http://localhost:10101/audio_query", # Aivis Speech のエンドポイント
                params=query_params,
                timeout=10 # タイムアウトを設定
            )
            response.raise_for_status() # HTTPエラーがあれば例外を発生
        except requests.exceptions.RequestException as e:
            raise ValueError(f"audio_query failed: {e}")

        print(f"audio_query response status: {response.status_code}")
        query_data = response.json()
        print("audio_queryのレスポンス:", json.dumps(query_data, ensure_ascii=False, indent=2)[:200])

        # 音声合成を実行
        print("synthesisを実行中...")
        try:
            audio_response = requests.post(
                "http://localhost:10101/synthesis", # Aivis Speech のエンドポイント
                params={
                    "speaker": speaker_id,
                    "style_id": speaker_id,
                },
                json=query_data,
                timeout=20 # タイムアウトを設定
            )
            audio_response.raise_for_status() # HTTPエラーがあれば例外を発生
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Synthesis failed: {e}")

        print(f"synthesis response status: {audio_response.status_code}")

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

    # fmtチャンク (24 bytes) - 最初のファイルのフォーマット情報をそのままコピー
    # (all_audio_data[0][12:36] は fmt チャンク全体を指します)
    result.extend(all_audio_data[0][12:36])

    # dataチャンクヘッダー
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
    selected_ai_model = data.get('ai_model', 'gemini') # フロントエンドからAIモデル名を受け取る

    print(f"受信したメッセージ: {user_message}")
    print(f"選択された音声ID: {voice_id}")
    print(f"選択されたAIモデル: {selected_ai_model}")

    try:
        # システムプロンプトを取得
        system_prompt = SPEAKER_PROMPTS.get(voice_id, "あなたは親切なアシスタントです。")
        print(f"使用するシステムプロンプト: {system_prompt}")

        print(f"{selected_ai_model}で応答を生成中...")

        model_name = ""
        # LiteLLMのモデル名指定 (2025年5月時点での推奨/一般的なモデル名)
        if selected_ai_model == "gemini":
            model_name = "gemini/gemini-1.5-flash-latest"
        elif selected_ai_model == "claude-sonnet": # "claude-sonnet-3.7" の代わりに一般的なSonnetを指定
            model_name = "claude-3-5-sonnet-20240620" # Claude 3.5 Sonnet (最新のSonnetを確認してください)
        elif selected_ai_model == "openai-gpt-4o":
            model_name = "gpt-4o"
        else:
            raise ValueError("無効なAIモデルが選択されました。")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # LiteLLM呼び出し
        # APIキーはLiteLLMが環境変数から自動で読み込みます
        # (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY)
        response = completion(
            model=model_name,
            messages=messages,
            # 必要に応じて他のパラメータ (temperature, max_tokensなど) を追加
            # temperature=0.7,
            # max_tokens=500,
        )

        # LiteLLMのレスポンス構造に合わせてメッセージを取得
        ai_message = ""
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            ai_message = response.choices[0].message.content.strip()
        else:
            raise ValueError("AIからの応答が予期した形式ではありません。")

        print(f"{selected_ai_model}の応答: {ai_message}")

        # 音声生成用のテキスト (AIの応答をそのまま使用)
        speech_text = ai_message
        print(f"音声生成用のテキスト: {speech_text}")

        if not speech_text.strip():
            raise ValueError("AIの応答が空です")

        # 音声を生成
        print("音声を生成中...")
        audio_data = generate_speech(speech_text, voice_id)

        if len(audio_data) < 44:
            raise ValueError("生成された音声データが無効です (サイズが小さすぎます)")

        # Base64エンコード
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        print(f"生成した音声データのBase64エンコード後のサイズ: {len(audio_base64)} bytes")

        return jsonify({
            'message': ai_message,
            'audio': audio_base64,
            'content_type': 'audio/wav'
        })

    except Exception as e:
        error_message = f"エラーが発生しました: {str(e)}"
        print(error_message)
        # LiteLLMは詳細なエラー情報を含むことがあるので、ログで確認すると良いでしょう。
        # 例: print(f"LiteLLM raw response: {response}")
        return jsonify({
            'message': error_message, # ユーザーに表示するメッセージ
            'error': str(e)    # 詳細なエラー (デバッグ用)
        }), 500

def kill_process_on_port(port):
    """指定されたポートを使用しているプロセスを終了する"""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.info.get('connections', []):
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    print(f"ポート {port} を使用しているプロセス {proc.info['name']} (PID: {proc.info['pid']}) を終了します。")
                    proc.kill()
                    proc.wait(timeout=3) # プロセスの終了を待つ
                    print(f"プロセス {proc.info['pid']} を終了しました。")
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print(f"プロセス {proc.info.get('pid', 'N/A')} の情報取得または終了に失敗しました。")
            pass
        except Exception as e:
            print(f"ポート確認中に予期せぬエラー: {e}")
    print(f"ポート {port} を使用しているプロセスは見つかりませんでした。")
    return False

def is_port_in_use(port):
    """指定されたポートが使用中かどうかを確認する"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return False # バインドできれば使用されていない
        except socket.error:
            return True # バインドできなければ使用中

if __name__ == '__main__':
    port = 5050 # デフォルトポートを5050に変更 (元は5000だったため)
    max_retries = 3
    retry_delay = 2 # seconds

    for i in range(max_retries):
        if is_port_in_use(port):
            print(f"ポート {port} が使用中です。(試行 {i+1}/{max_retries})")
            if kill_process_on_port(port):
                print(f"ポート {port} を解放しました。サーバーを起動します。")
                time.sleep(retry_delay) # ポートが完全に解放されるのを待つ
                break
            else:
                print(f"ポート {port} の解放に失敗しました。")
                if i == max_retries - 1:
                    print(f"ポート {port} を解放できませんでした。手動でポートを解放するか、別のポートを使用してください。")
                    exit(1) # 終了
                time.sleep(retry_delay) # リトライ前に待機
        else:
            print(f"ポート {port} は空いています。サーバーを起動します。")
            break
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)