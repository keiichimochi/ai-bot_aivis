// チャット機能を管理するモジュール
class ChatManager {
    constructor() {
        this.chatContainer = null;
        this.userInput = null;
        this.sendButton = null;
        this.voiceSelect = null;
        this.aiModelSelect = null;
        this.autoPlayToggle = null;
        this.isLoading = false;
        
        this.initializeElements();
        this.setupEventListeners();
        
        // 初期状態の送信ボタンを設定
        setTimeout(() => {
            this.updateSendButton();
            // 初回のみヘルプメッセージを表示
            if (this.chatContainer.children.length === 0) {
                this.showSystemMessage('📸 画像のみでも送信できます！📷ボタンで写真を選択して「画像送信」ボタンを押してください。');
            }
        }, 100);
    }

    // DOM要素を初期化
    initializeElements() {
        this.chatContainer = document.getElementById('chat-container');
        this.userInput = document.getElementById('user-input');
        this.sendButton = document.getElementById('send-button');
        this.voiceSelect = document.getElementById('voice-select');
        this.aiModelSelect = document.getElementById('ai-model-select');
        this.autoPlayToggle = document.getElementById('auto-play-toggle');

        if (!this.chatContainer || !this.userInput || !this.sendButton) {
            console.error("必要なDOM要素が見つかりません");
            return false;
        }
        return true;
    }

    // イベントリスナーを設定
    setupEventListeners() {
        // 送信ボタンのクリック
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Enterキーでメッセージ送信
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 入力フィールドの変更時に送信ボタンを更新
        this.userInput.addEventListener('input', () => {
            this.updateSendButton();
        });

        // 自動再生トグルの変更
        if (this.autoPlayToggle) {
            this.autoPlayToggle.addEventListener('change', (e) => {
                window.audioManager.setAutoPlay(e.target.checked);
            });
        }

        // チャットコンテナクリックでフォーカス
        this.chatContainer.addEventListener('click', () => {
            this.userInput.focus();
        });

        // 画像状態変更の監視（定期的にチェック）
        setInterval(() => {
            this.updateSendButton();
        }, 500);
    }

    // メッセージを送信
    async sendMessage() {
        const userMessage = this.userInput.value.trim();
        const selectedVoiceId = parseInt(this.voiceSelect.value);
        const selectedAiModel = this.aiModelSelect.value;
        
        // 画像データを取得
        const imageData = window.imageManager ? window.imageManager.getCurrentImage() : null;
        
        // メッセージか画像のどちらかが必要
        if (userMessage === "" && !imageData) return;

        // ローディング状態に設定
        this.setLoading(true);

        // ユーザーメッセージを表示（画像がある場合は画像も表示）
        this.appendUserMessage(userMessage, imageData);

        // 入力フィールドをクリア
        this.userInput.value = "";
        
        // 画像をクリア
        if (window.imageManager) {
            window.imageManager.clearAfterSend();
        }
        
        // 送信ボタンの状態を更新
        this.updateSendButton();

        try {
            console.log(`メッセージ送信: "${userMessage}"`);
            console.log(`選択された音声ID: ${selectedVoiceId}`);
            console.log(`選択されたAIモデル: ${selectedAiModel}`);
            if (imageData) {
                console.log('画像データも送信します');
                console.log(`画像データサイズ: ${imageData.length} bytes`);
                console.log(`画像データタイプ: ${imageData.substring(0, 30)}...`);
            }

            // 送信データを構築
            const requestData = {
                message: userMessage,
                voice_id: selectedVoiceId,
                ai_model: selectedAiModel
            };
            
            // 画像データがある場合は追加
            if (imageData) {
                requestData.image = imageData;
                console.log('リクエストデータに画像を追加しました');
            }

            console.log('fetch開始...');
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            console.log(`fetch応答ステータス: ${response.status}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`HTTPエラー! status: ${response.status}, body: ${errorText}`);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("サーバーレスポンス:", data);

            if (data.error) {
                console.error('サーバーエラー:', data.error);
                this.appendMessage(`エラー: ${data.error}`, 'error-message');
                return;
            }

            // AIメッセージを表示
            const messageElement = this.appendMessage(data.message, 'ai-message');

            // 音声データが存在する場合の処理
            if (data.audio) {
                console.log('音声データを受信しました');
                // 手動再生ボタンを追加
                const playButton = window.audioManager.createPlayButton(data.audio, messageElement);
                messageElement.appendChild(playButton);

                // 自動再生を試行
                const autoPlaySuccess = await window.audioManager.tryAutoPlay(data.audio);
                
                // 自動再生に失敗した場合の処理
                if (!autoPlaySuccess && this.autoPlayToggle.checked) {
                    console.log("自動再生に失敗しました。手動再生ボタンをご利用ください。");
                }
            } else {
                console.warn('音声データが存在しません');
            }

        } catch (error) {
            console.error("送信エラー:", error);
            console.error("エラースタック:", error.stack);
            this.appendMessage(`通信エラーが発生しました: ${error.message}`, 'error-message');
        } finally {
            this.setLoading(false);
            console.log('送信処理完了');
        }
    }

    // メッセージをチャットコンテナに追加
    appendMessage(message, className) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', className);
        messageElement.textContent = message;
        this.chatContainer.appendChild(messageElement);
        
        // 自動スクロール
        this.scrollToBottom();
        
        return messageElement;
    }

    // ユーザーメッセージを追加（画像対応）
    appendUserMessage(message, imageData) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'user-message');
        
        // 画像がある場合は画像を先に表示
        if (imageData) {
            messageElement.classList.add('message-with-image');
            
            const img = document.createElement('img');
            img.src = imageData;
            img.className = 'message-image';
            img.alt = '送信された画像';
            messageElement.appendChild(img);
        }
        
        // テキストメッセージの処理
        if (message.trim()) {
            // ユーザーがテキストを入力した場合
            const textDiv = document.createElement('div');
            textDiv.textContent = message;
            messageElement.appendChild(textDiv);
        } else if (imageData) {
            // 画像のみで、テキストが空の場合
            const textDiv = document.createElement('div');
            textDiv.textContent = '[画像について説明を求めました]';
            textDiv.style.fontStyle = 'italic';
            textDiv.style.opacity = '0.8';
            messageElement.appendChild(textDiv);
        }
        
        this.chatContainer.appendChild(messageElement);
        
        // 自動スクロール
        this.scrollToBottom();
        
        return messageElement;
    }

    // チャットコンテナを最下部にスクロール
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    // ローディング状態を設定
    setLoading(loading) {
        this.isLoading = loading;
        
        if (loading) {
            this.sendButton.disabled = true;
            this.sendButton.textContent = "送信中...";
            this.sendButton.classList.add('loading');
        } else {
            this.sendButton.disabled = false;
            this.sendButton.textContent = "送信";
            this.sendButton.classList.remove('loading');
        }
    }

    // チャット履歴をクリア
    clearChat() {
        this.chatContainer.innerHTML = '';
        console.log("チャット履歴をクリアしました");
    }

    // 現在の設定を取得
    getCurrentSettings() {
        return {
            voiceId: parseInt(this.voiceSelect.value),
            aiModel: this.aiModelSelect.value,
            autoPlay: this.autoPlayToggle.checked
        };
    }

    // エラーメッセージを表示
    showError(message) {
        this.appendMessage(message, 'error-message');
    }

    // システムメッセージを表示
    showSystemMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'system-message');
        messageElement.textContent = message;
        messageElement.style.textAlign = 'center';
        messageElement.style.opacity = '0.7';
        messageElement.style.fontStyle = 'italic';
        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
        
        return messageElement;
    }

    // 送信ボタンのテキストを更新
    updateSendButton() {
        if (this.isLoading) return; // ローディング中は変更しない
        
        const userMessage = this.userInput.value.trim();
        const hasImage = window.imageManager && window.imageManager.hasImage();
        
        // CSSクラスをリセット
        this.sendButton.classList.remove('image-send');
        
        if (hasImage && userMessage === "") {
            this.sendButton.textContent = "画像送信";
            this.sendButton.classList.add('image-send');
        } else if (hasImage && userMessage !== "") {
            this.sendButton.textContent = "送信";
        } else {
            this.sendButton.textContent = "送信";
        }
        
        // 送信可能かどうかの状態更新
        this.sendButton.disabled = (userMessage === "" && !hasImage) || this.isLoading;
    }
}

// グローバルにチャットマネージャーを作成
window.chatManager = new ChatManager();

console.log("チャットモジュール初期化完了"); 