// 音声関連の機能を管理するモジュール
class AudioManager {
    constructor() {
        this.audioQueue = [];
        this.isProcessingQueue = false;
        this.hasUserInteracted = false;
        this.currentAudio = null;
        this.isAutoPlayEnabled = false;
        
        this.initializeUserInteraction();
    }

    // iOS対応のユーザーインタラクション初期化
    initializeUserInteraction() {
        const initAudio = () => {
            if (!this.hasUserInteracted) {
                this.hasUserInteracted = true;
                console.log("ユーザーインタラクション検知。音声再生が可能になりました。");
                
                // iOS対応のためのサイレント音声再生
                const silentAudio = new Audio();
                // 短いサイレント音声のBase64データ
                silentAudio.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAAAQAEAAAAAAAAAABAAAQAIAAgAZGF0YQQAAAAAAA==';
                silentAudio.volume = 0;
                silentAudio.play().then(() => {
                    console.log("サイレント音声再生成功。iOSの音声制限を解除しました。");
                }).catch(e => {
                    console.log("サイレント音声再生失敗:", e);
                });
            }
        };

        // 複数のイベントでユーザーインタラクションを検知（一度だけ実行）
        document.addEventListener('click', initAudio, { once: true });
        document.addEventListener('touchstart', initAudio, { once: true });
        document.addEventListener('keydown', initAudio, { once: true });
    }

    // Base64音声データから再生する（iPhone対応版）
    async playAudioFromBase64(base64Data) {
        return new Promise((resolve, reject) => {
            try {
                const audio = new Audio();
                const dataUrl = `data:audio/wav;base64,${base64Data}`;
                
                // イベントリスナーを設定
                const onEnded = () => {
                    console.log("音声再生完了");
                    this.cleanup(audio);
                    resolve();
                };
                
                const onError = (e) => {
                    console.error("音声再生エラー:", e);
                    this.cleanup(audio);
                    reject(e);
                };

                audio.addEventListener('ended', onEnded);
                audio.addEventListener('error', onError);
                
                // iOS対応: データURLを設定
                audio.src = dataUrl;
                
                // iOS対応: 明示的にloadを呼び出し
                audio.load();
                
                // 再生開始
                audio.play().then(() => {
                    console.log("音声再生開始");
                    this.currentAudio = audio;
                }).catch(e => {
                    console.error("音声再生失敗:", e);
                    this.cleanup(audio);
                    reject(e);
                });
                
            } catch (error) {
                console.error("音声再生準備エラー:", error);
                reject(error);
            }
        });
    }

    // 音声オブジェクトのクリーンアップ
    cleanup(audio) {
        if (audio) {
            audio.removeEventListener('ended', () => {});
            audio.removeEventListener('error', () => {});
            audio.src = '';
            if (this.currentAudio === audio) {
                this.currentAudio = null;
            }
        }
    }

    // 現在の音声を停止
    stopCurrentAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.cleanup(this.currentAudio);
        }
        this.audioQueue = [];
        this.isProcessingQueue = false;
    }

    // 音声キューを処理
    async processAudioQueue() {
        if (this.isProcessingQueue || this.audioQueue.length === 0) {
            return;
        }
        
        this.isProcessingQueue = true;
        
        while (this.audioQueue.length > 0) {
            const audioData = this.audioQueue.shift();
            try {
                await this.playAudioFromBase64(audioData);
                // 音声間の短い間隔
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (error) {
                console.error("キュー音声再生中にエラー:", error);
            }
        }
        
        this.isProcessingQueue = false;
    }

    // 音声をキューに追加
    addToQueue(base64Data) {
        this.audioQueue.push(base64Data);
        this.processAudioQueue();
    }

    // 手動再生ボタンを作成
    createPlayButton(audioData, messageElement) {
        const playButton = document.createElement('button');
        playButton.className = 'play-button';
        playButton.innerHTML = '▶';
        playButton.title = '音声を再生';
        
        playButton.onclick = async (e) => {
            e.stopPropagation();
            
            // 現在の音声を停止
            this.stopCurrentAudio();
            
            // ボタンの状態を更新
            playButton.disabled = true;
            playButton.innerHTML = '⏸';
            playButton.classList.add('playing');
            messageElement.classList.add('playing');
            
            try {
                await this.playAudioFromBase64(audioData);
            } catch (error) {
                console.error("手動音声再生エラー:", error);
            } finally {
                // ボタンの状態をリセット
                playButton.disabled = false;
                playButton.innerHTML = '▶';
                playButton.classList.remove('playing');
                messageElement.classList.remove('playing');
            }
        };
        
        return playButton;
    }

    // 自動再生の有効/無効を設定
    setAutoPlay(enabled) {
        this.isAutoPlayEnabled = enabled;
        if (!enabled) {
            this.stopCurrentAudio();
        }
        console.log(`自動再生: ${enabled ? '有効' : '無効'}`);
    }

    // 自動再生を試行
    async tryAutoPlay(audioData) {
        if (this.isAutoPlayEnabled && this.hasUserInteracted) {
            try {
                await this.playAudioFromBase64(audioData);
                return true; // 自動再生成功
            } catch (error) {
                console.error("自動音声再生エラー:", error);
                return false; // 自動再生失敗
            }
        }
        return false; // 自動再生無効または未インタラクション
    }
}

// グローバルに音声マネージャーを作成
window.audioManager = new AudioManager();

console.log("音声モジュール初期化完了"); 