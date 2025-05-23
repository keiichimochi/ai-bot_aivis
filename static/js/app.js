// アプリケーションのメイン制御
class App {
    constructor() {
        this.version = '1.0.0';
        this.isReady = false;
        
        this.initialize();
    }

    // アプリケーションの初期化
    async initialize() {
        console.log(`AIチャットボット v${this.version} 初期化中...`);
        
        try {
            // DOM読み込み完了を待つ
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // 各モジュールの初期化確認
            this.checkModules();
            
            // 初期設定を適用
            this.applyInitialSettings();
            
            // 開発者向けのデバッグ情報
            this.setupDebugMode();
            
            // ユーザーへの初期案内
            this.showWelcomeMessage();
            
            this.isReady = true;
            console.log("アプリケーション初期化完了");
            
        } catch (error) {
            console.error("アプリケーション初期化エラー:", error);
            this.showError("アプリケーションの初期化に失敗しました。ページを再読み込みしてください。");
        }
    }

    // 各モジュールの初期化確認
    checkModules() {
        const requiredModules = ['audioManager', 'chatManager', 'imageManager'];
        const missingModules = [];

        requiredModules.forEach(module => {
            if (!window[module]) {
                missingModules.push(module);
            }
        });

        if (missingModules.length > 0) {
            throw new Error(`必要なモジュールが見つかりません: ${missingModules.join(', ')}`);
        }

        console.log("全モジュールの初期化を確認しました");
    }

    // 初期設定を適用
    applyInitialSettings() {
        // 自動再生の初期状態を設定
        const autoPlayToggle = document.getElementById('auto-play-toggle');
        if (autoPlayToggle) {
            // デフォルトは無効にしておく（ユーザーが明示的に有効にする必要がある）
            autoPlayToggle.checked = false;
            window.audioManager.setAutoPlay(false);
        }

        // 初期フォーカスを入力欄に
        const userInput = document.getElementById('user-input');
        if (userInput) {
            userInput.focus();
        }

        console.log("初期設定を適用しました");
    }

    // デバッグモードの設定
    setupDebugMode() {
        // URLパラメータでデバッグモードを有効化
        const urlParams = new URLSearchParams(window.location.search);
        const debugMode = urlParams.get('debug') === 'true';

        if (debugMode) {
            console.log("デバッグモード有効");
            
            // グローバルなデバッグ関数を追加
            window.debug = {
                app: this,
                audioManager: window.audioManager,
                chatManager: window.chatManager,
                clearChat: () => window.chatManager.clearChat(),
                testAudio: (text = "テスト音声です") => {
                    console.log("音声テスト実行中...");
                    // テスト用音声データ（実際にはサーバーから取得）
                    return "テスト音声機能は開発中です";
                },
                getSettings: () => window.chatManager.getCurrentSettings(),
                version: this.version
            };
            
            console.log("デバッグ関数が利用可能です:", Object.keys(window.debug));
        }
    }

    // ウェルカムメッセージを表示
    showWelcomeMessage() {
        const welcomeMsg = "🎤 AIチャットボットへようこそ！音声付きチャットをお楽しみください。";
        
        setTimeout(() => {
            if (window.chatManager) {
                window.chatManager.showSystemMessage(welcomeMsg);
                
                // iPhone/iPadユーザーへの特別案内
                if (this.isiOS()) {
                    setTimeout(() => {
                        const iosMsg = "📱 iPhoneをご利用の場合は、音声を聞くために画面をタップしてから自動再生を有効にしてください。";
                        window.chatManager.showSystemMessage(iosMsg);
                    }, 1000);
                }
            }
        }, 500);
    }

    // iOS端末かどうかを判定
    isiOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    }

    // エラーメッセージを表示
    showError(message) {
        if (window.chatManager) {
            window.chatManager.showError(message);
        } else {
            alert(message);
        }
    }

    // アプリケーションの状態を取得
    getStatus() {
        return {
            ready: this.isReady,
            version: this.version,
            userAgent: navigator.userAgent,
            iOS: this.isiOS(),
            modules: {
                audio: !!window.audioManager,
                chat: !!window.chatManager
            }
        };
    }

    // 設定をローカルストレージに保存
    saveSettings() {
        try {
            const settings = window.chatManager.getCurrentSettings();
            localStorage.setItem('aibot-settings', JSON.stringify(settings));
            console.log("設定を保存しました", settings);
        } catch (error) {
            console.error("設定保存エラー:", error);
        }
    }

    // 設定をローカルストレージから読み込み
    loadSettings() {
        try {
            const saved = localStorage.getItem('aibot-settings');
            if (saved) {
                const settings = JSON.parse(saved);
                console.log("保存された設定を読み込みました", settings);
                
                // 設定を適用
                if (settings.voiceId) {
                    const voiceSelect = document.getElementById('voice-select');
                    if (voiceSelect) voiceSelect.value = settings.voiceId;
                }
                
                if (settings.aiModel) {
                    const aiModelSelect = document.getElementById('ai-model-select');
                    if (aiModelSelect) aiModelSelect.value = settings.aiModel;
                }
                
                if (settings.autoPlay !== undefined) {
                    const autoPlayToggle = document.getElementById('auto-play-toggle');
                    if (autoPlayToggle) {
                        autoPlayToggle.checked = settings.autoPlay;
                        window.audioManager.setAutoPlay(settings.autoPlay);
                    }
                }
                
                return settings;
            }
        } catch (error) {
            console.error("設定読み込みエラー:", error);
        }
        return null;
    }
}

// ページ離脱時に設定を保存
window.addEventListener('beforeunload', () => {
    if (window.app) {
        window.app.saveSettings();
    }
});

// アプリケーションのインスタンスを作成
window.app = new App();

// グローバル関数として公開（デバッグ用）
window.getAppStatus = () => window.app.getStatus();

console.log("メインアプリケーション初期化完了"); 