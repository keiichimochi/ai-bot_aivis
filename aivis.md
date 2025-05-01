# Aivis Speech API 使用ガイド

このドキュメントではAivis Speech APIの使い方と利用可能なspeaker IDについて説明するナリ！

## Aivis Speech APIの基本情報

- **ベースURL**: `http://localhost:10101/`
- **ドキュメント**: `http://localhost:10101/docs`（Swagger UI）

## API エンドポイント

Aivis Speech APIは主に2つのエンドポイントで音声合成を行うナリ：

### 1. `/audio_query` - 音声合成クエリの作成

音声合成のパラメータを含むJSONクエリを作成するナリ。

```http
POST /audio_query
```

**パラメータ**:
- `text`: 音声合成するテキスト (必須)
- `speaker`: 話者ID (必須)
- `style_id`: スタイルID (必須、通常は話者IDと同じ)
- `speed_scale`: 話速 (デフォルト: 1.0)
- `enable_interrogative_upspeak`: 疑問文の語尾を上げる (デフォルト: true)

**レスポンス**:
音声合成パラメータを含むJSONナリ。

### 2. `/synthesis` - 音声合成の実行

`/audio_query`で取得したパラメータを使用して実際の音声を生成するナリ。

```http
POST /synthesis
```

**パラメータ**:
- `speaker`: 話者ID (必須)
- `style_id`: スタイルID (必須、通常は話者IDと同じ)
- `enable_interrogative_upspeak`: 疑問文の語尾を上げる (デフォルト: true)

**リクエストボディ**:
`/audio_query`のレスポンスJSON

**レスポンス**:
WAVフォーマットの音声データ

## 利用可能な話者ID (Speaker IDs)

現在のAivis Speech APIでは以下の話者が利用可能ナリ：

### 1. Anneli (UUID: e756b8e4-b606-4e15-99b1-3f9c6a1b2317)
- ノーマル (ID: 888753760)
- 通常 (ID: 888753761)
- テンション高め (ID: 888753762)
- 落ち着き (ID: 888753763)
- 上機嫌 (ID: 888753764)
- 怒り・悲しみ (ID: 888753765)

### 2. kiyoshi (UUID: 694f5443-eed1-4a36-9ab2-0b0bc3997d1c)
- ノーマル (ID: 1763602272)
  * 特徴: 宮城県出身、現在千葉県旭市在住の53歳、IKAのキャラクター。宮城弁で話し、イカとテキーラをこよなく愛する。
  * 声のピッチ調整: 0.10（通常より少し高め）

### 3. korosuke (UUID: 40e5743b-a55b-4703-9cd7-221e3e5696a5)
- ノーマル (ID: 488039072)
  * 特徴: 語尾に「ナリ」をつける元気なロボットアシスタント。

### 4. sakuragi (UUID: e4dbb14f-6b40-4a00-a674-c6043b1412a5)
- ノーマル (ID: 269244800)
  * 特徴: 「ドラゴン桜」の桜木建二をモチーフにした熱血教師。

### 5. yamaoka (UUID: 67539f0d-f0ee-4770-8309-e0c4c08e4be1)
- ノーマル (ID: 1342155808)
  * 特徴: 「美味しんぼ」の山岡士郎をモチーフにした美食家。

## Python コード例

以下はPythonを使った音声合成の例ナリ：

```python
import aiohttp
import json
import base64
import asyncio

async def generate_speech(text: str, speaker_id: int) -> bytes:
    """音声を非同期で生成する関数"""
    async with aiohttp.ClientSession() as session:
        # 音声合成用のクエリを作成
        query_params = {
            "text": text,
            "speaker": speaker_id,
            "style_id": speaker_id,
            "speed_scale": 1.0,
            "enable_interrogative_upspeak": "true"
        }

        # クエリを作成（非同期）
        async with session.post(
            "http://localhost:10101/audio_query",
            params=query_params,
            timeout=30
        ) as response:
            if response.status != 200:
                raise ValueError(f"audio_query failed: {await response.text()}")
            
            query_data = await response.json()
            
            # 音声合成パラメータの調整
            query_data["volumeScale"] = 1.0  # 音量を最大に
            query_data["prePhonemeLength"] = 0.1  # 音声の前の無音時間
            query_data["postPhonemeLength"] = 0.1  # 音声の後の無音時間
            
            # kiyoshiの声の高さを調整
            if speaker_id == 1763602272:  # kiyoshiのID
                query_data["pitchScale"] = 0.10  # ピッチを上げる

        # 音声合成を実行（非同期）
        async with session.post(
            "http://localhost:10101/synthesis",
            params={
                "speaker": speaker_id,
                "style_id": speaker_id,
                "enable_interrogative_upspeak": "true"
            },
            json=query_data,
            timeout=60
        ) as audio_response:
            if audio_response.status != 200:
                raise ValueError(f"Synthesis failed")

            content = await audio_response.read()
            return content

# 使用例
async def main():
    # コロ助の声で音声合成
    korosuke_audio = await generate_speech("こんにちはナリ！元気かナリ？", 488039072)
    
    # 音声ファイルを保存
    with open("korosuke_greeting.wav", "wb") as f:
        f.write(korosuke_audio)
    
    # キヨシの声で音声合成
    kiyoshi_audio = await generate_speech("おっとぉ〜い！イカした質問だべさ！", 1763602272)
    
    # 音声ファイルを保存
    with open("kiyoshi_greeting.wav", "wb") as f:
        f.write(kiyoshi_audio)

if __name__ == "__main__":
    asyncio.run(main())
```

## 音声パラメータのカスタマイズ

音声合成時に以下のパラメータを調整できるナリ：

- `pitchScale`: ピッチ（声の高さ）の調整（-0.15〜0.15）
  - 正の値で高く、負の値で低くなる
  - kiyoshiのデフォルト値: 0.10（少し高め）

- `volumeScale`: 音量の調整（0.0〜2.0）
  - デフォルト: 1.0

- `intonationScale`: イントネーションの強さ（0.0〜2.0）
  - デフォルト: 1.0

- `prePhonemeLength`: 音声前の無音時間（秒）
  - デフォルト: 0.1

- `postPhonemeLength`: 音声後の無音時間（秒）
  - デフォルト: 0.1

- `speed_scale`: 話速（0.5〜2.0）
  - デフォルト: 1.0

## トラブルシューティング

1. **API接続エラー**
   - Aivis Speech Engine（localhost:10101）が起動しているか確認
   - ファイアウォール設定を確認

2. **音声生成エラー**
   - 存在する話者IDを使用しているか確認
   - テキストが空でないか確認
   - 長すぎるテキストは複数に分割して処理

3. **音質問題**
   - パラメータ調整（pitchScale, volumeScale）で改善できる場合がある
   - WAVヘッダーを確認（最小44バイト必要）

## 注意事項

- リクエスト制限: 長文は複数の短い文に分割して処理するのが効果的
- エラーハンドリング: API呼び出しは常にtry-exceptで囲む
- メモリ管理: 大量の音声データを扱う場合はメモリ使用に注意
- ブラウザでの再生: iOSの場合はユーザーインタラクション後に音声再生を開始する

---

*この文書は2023年3月時点の情報に基づいています。APIの仕様は変更される可能性があるナリ！*
