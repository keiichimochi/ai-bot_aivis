// 画像機能を管理するモジュール
class ImageManager {
    constructor() {
        this.currentImage = null;
        this.imagePreview = null;
        this.cameraButton = null;
        this.imageInput = null;
        
        this.initializeElements();
        this.setupEventListeners();
    }

    // DOM要素を初期化
    initializeElements() {
        this.cameraButton = document.getElementById('camera-button');
        this.imageInput = document.getElementById('image-input');

        if (!this.cameraButton || !this.imageInput) {
            console.error("画像関連のDOM要素が見つかりません");
            return false;
        }
        return true;
    }

    // イベントリスナーを設定
    setupEventListeners() {
        // カメラボタンのクリック
        this.cameraButton.addEventListener('click', () => {
            if (this.currentImage) {
                // 画像がある場合は削除
                this.removeImage();
            } else {
                // 画像がない場合は選択メニューを表示
                this.showImageSourceMenu();
            }
        });

        // ファイル選択時の処理
        this.imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.handleImageFile(file);
            }
        });
    }

    // 画像ファイルを処理
    async handleImageFile(file) {
        try {
            console.log(`元画像サイズ: ${(file.size / 1024 / 1024).toFixed(2)}MB`);
            
            // 画像タイプチェック
            if (!file.type.startsWith('image/')) {
                alert('画像ファイルを選択してください。');
                return;
            }

            // 圧縮中の表示
            this.showCompressionMessage('画像を処理中...');

            // ファイルをBase64に変換
            const base64 = await this.fileToBase64(file);
            
            // 圧縮処理を実行
            const compressedBase64 = await this.compressImage(base64, file.size);
            
            // 画像を設定
            this.setImage(compressedBase64);
            
            // 成功メッセージ
            this.hideCompressionMessage();
            
            console.log('画像アップロード完了');
            
        } catch (error) {
            console.error('画像処理エラー:', error);
            this.hideCompressionMessage();
            alert(error.message || '画像の処理中にエラーが発生しました。');
        } finally {
            // ファイル入力をリセット
            this.imageInput.value = '';
        }
    }

    // 圧縮メッセージを表示
    showCompressionMessage(message) {
        this.hideCompressionMessage(); // 既存のメッセージを削除
        
        const messageDiv = document.createElement('div');
        messageDiv.id = 'compression-message';
        messageDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 123, 255, 0.9);
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            font-size: 16px;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        messageDiv.textContent = message;
        
        document.body.appendChild(messageDiv);
    }

    // 圧縮メッセージを隠す
    hideCompressionMessage() {
        const existingMessage = document.getElementById('compression-message');
        if (existingMessage) {
            existingMessage.remove();
        }
    }

    // 画像圧縮の統合処理
    async compressImage(base64, originalSize) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const webpSupported = this.isWebPSupported();
        
        // 最初のリサイズ（サイズに応じて解像度を調整）
        let maxWidth, maxHeight;
        if (originalSize > 20 * 1024 * 1024) { // 20MB以上
            maxWidth = 600;
            maxHeight = 400;
        } else if (originalSize > 10 * 1024 * 1024) { // 10MB以上
            maxWidth = 800;
            maxHeight = 600;
        } else {
            maxWidth = 1200;
            maxHeight = 900;
        }
        
        console.log(`初期リサイズ: ${maxWidth}x${maxHeight}`);
        this.showCompressionMessage(`画像を${maxWidth}x${maxHeight}にリサイズ中...`);
        
        // WebP対応ブラウザの場合はWebPで試行
        let format = webpSupported ? 'webp' : 'jpeg';
        let compressed = await this.resizeImage(base64, maxWidth, maxHeight, 0.8, format);
        
        // サイズチェックとループ圧縮
        let currentSize = this.getBase64Size(compressed);
        let quality = 0.7;
        let attempt = 1;
        
        console.log(`リサイズ後のサイズ: ${(currentSize / 1024 / 1024).toFixed(2)}MB (フォーマット: ${format})`);
        
        while (currentSize > maxSize && quality > 0.1 && attempt <= 5) {
            console.log(`圧縮試行 ${attempt}: 品質${quality}, 現在のサイズ${(currentSize / 1024 / 1024).toFixed(2)}MB`);
            
            this.showCompressionMessage(`画像を圧縮中... (試行${attempt}/5, 品質${Math.round(quality * 100)}%, ${format})`);
            
            // より強い圧縮を適用
            if (attempt >= 3) {
                // 3回目以降はさらに解像度を下げる
                maxWidth = Math.floor(maxWidth * 0.8);
                maxHeight = Math.floor(maxHeight * 0.8);
                
                // WebPで失敗した場合はJPEGに切り替え
                if (attempt === 4 && format === 'webp') {
                    format = 'jpeg';
                    this.showCompressionMessage(`JPEG形式で再圧縮中...`);
                }
            }
            
            compressed = await this.resizeImage(base64, maxWidth, maxHeight, quality, format);
            currentSize = this.getBase64Size(compressed);
            quality -= 0.15; // 品質を段階的に下げる
            attempt++;
        }
        
        // 最終チェック
        const finalSize = this.getBase64Size(compressed);
        console.log(`最終画像サイズ: ${(finalSize / 1024 / 1024).toFixed(2)}MB`);
        
        if (finalSize > maxSize) {
            throw new Error(`画像サイズが${(finalSize / 1024 / 1024).toFixed(2)}MBで制限を超えています。より小さな画像を選択してください。`);
        }
        
        this.showCompressionMessage(`圧縮完了！ ${(originalSize / 1024 / 1024).toFixed(2)}MB → ${(finalSize / 1024 / 1024).toFixed(2)}MB (${format})`);
        
        // 完了メッセージを少し表示してから消す
        setTimeout(() => {
            this.hideCompressionMessage();
        }, 1500);
        
        return compressed;
    }

    // Base64データのサイズを計算
    getBase64Size(base64String) {
        // data:image/jpeg;base64, の部分を除去してサイズ計算
        const base64Data = base64String.split(',')[1];
        return Math.ceil(base64Data.length * 0.75); // Base64は約4/3倍になるので逆算
    }

    // ファイルをBase64に変換
    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    // 画像をリサイズ
    resizeImage(base64, maxWidth, maxHeight, quality = 0.8, format = 'jpeg') {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');

                // アスペクト比を保持してリサイズ
                let { width, height } = img;
                
                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width = width * ratio;
                    height = height * ratio;
                }

                canvas.width = width;
                canvas.height = height;

                // 画像を描画（アンチエイリアシングを無効にして高速化）
                ctx.imageSmoothingEnabled = true;
                ctx.imageSmoothingQuality = 'medium';
                ctx.drawImage(img, 0, 0, width, height);

                // フォーマットに応じてBase64出力
                const mimeType = format === 'webp' ? 'image/webp' : 'image/jpeg';
                resolve(canvas.toDataURL(mimeType, quality));
            };
            img.src = base64;
        });
    }

    // WebP対応チェック
    isWebPSupported() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }

    // 画像を設定
    setImage(base64Data) {
        this.currentImage = base64Data;
        
        // プレビューを作成/更新
        this.createImagePreview();
        
        // カメラボタンの状態を更新
        this.updateCameraButton();
    }

    // 画像プレビューを作成
    createImagePreview() {
        // 既存のプレビューを削除
        this.removeImagePreview();
        
        // プレビュー要素を作成
        this.imagePreview = document.createElement('div');
        this.imagePreview.className = 'image-preview';
        
        const img = document.createElement('img');
        img.src = this.currentImage;
        img.alt = '選択された画像';
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-image';
        removeBtn.innerHTML = '×';
        removeBtn.title = '画像を削除';
        removeBtn.onclick = () => this.removeImage();
        
        this.imagePreview.appendChild(img);
        this.imagePreview.appendChild(removeBtn);
        
        // 入力コンテナの前に挿入
        const inputContainer = document.querySelector('.input-container');
        inputContainer.parentNode.insertBefore(this.imagePreview, inputContainer);
    }

    // 画像プレビューを削除
    removeImagePreview() {
        if (this.imagePreview) {
            this.imagePreview.remove();
            this.imagePreview = null;
        }
    }

    // 画像を削除
    removeImage() {
        this.currentImage = null;
        this.removeImagePreview();
        this.updateCameraButton();
        console.log('画像を削除しました');
    }

    // カメラボタンの状態を更新
    updateCameraButton() {
        if (this.currentImage) {
            this.cameraButton.innerHTML = '🗑️';
            this.cameraButton.title = '画像を削除';
            this.cameraButton.classList.add('has-image');
        } else {
            this.cameraButton.innerHTML = '📷';
            this.cameraButton.title = '写真を撮る/選択';
            this.cameraButton.classList.remove('has-image');
        }
    }

    // 現在の画像を取得
    getCurrentImage() {
        return this.currentImage;
    }

    // 画像があるかチェック
    hasImage() {
        return this.currentImage !== null;
    }

    // 送信後の画像クリア
    clearAfterSend() {
        this.removeImage();
    }

    // 画像ソース選択メニューを表示
    showImageSourceMenu() {
        // 既存のメニューがあれば削除
        this.hideImageSourceMenu();
        
        // メニューを作成
        const menu = document.createElement('div');
        menu.id = 'image-source-menu';
        menu.style.cssText = `
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            padding: 8px;
            z-index: 1000;
            min-width: 200px;
            border: 1px solid #e0e0e0;
        `;
        
        // カメラオプション
        const cameraOption = document.createElement('button');
        cameraOption.style.cssText = `
            width: 100%;
            padding: 12px 16px;
            border: none;
            background: transparent;
            text-align: left;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.2s;
            display: flex;
            align-items: center;
            gap: 12px;
        `;
        cameraOption.innerHTML = '📷 写真を撮る';
        cameraOption.onmouseover = () => cameraOption.style.backgroundColor = '#f0f0f0';
        cameraOption.onmouseout = () => cameraOption.style.backgroundColor = 'transparent';
        cameraOption.onclick = () => {
            this.hideImageSourceMenu();
            this.openCamera();
        };
        
        // ライブラリオプション
        const libraryOption = document.createElement('button');
        libraryOption.style.cssText = cameraOption.style.cssText;
        libraryOption.innerHTML = '🖼️ ライブラリから選択';
        libraryOption.onmouseover = () => libraryOption.style.backgroundColor = '#f0f0f0';
        libraryOption.onmouseout = () => libraryOption.style.backgroundColor = 'transparent';
        libraryOption.onclick = () => {
            this.hideImageSourceMenu();
            this.openLibrary();
        };
        
        // キャンセルオプション
        const cancelOption = document.createElement('button');
        cancelOption.style.cssText = cameraOption.style.cssText;
        cancelOption.innerHTML = '❌ キャンセル';
        cancelOption.onmouseover = () => cancelOption.style.backgroundColor = '#f0f0f0';
        cancelOption.onmouseout = () => cancelOption.style.backgroundColor = 'transparent';
        cancelOption.onclick = () => {
            this.hideImageSourceMenu();
        };
        
        // セパレーター
        const separator = document.createElement('div');
        separator.style.cssText = `
            height: 1px;
            background: #e0e0e0;
            margin: 4px 8px;
        `;
        
        menu.appendChild(cameraOption);
        menu.appendChild(libraryOption);
        menu.appendChild(separator);
        menu.appendChild(cancelOption);
        
        document.body.appendChild(menu);
        
        // 背景クリックで閉じる
        setTimeout(() => {
            document.addEventListener('click', this.handleOutsideClick.bind(this), { once: true });
        }, 100);
    }

    // メニュー外クリックの処理
    handleOutsideClick(event) {
        const menu = document.getElementById('image-source-menu');
        if (menu && !menu.contains(event.target)) {
            this.hideImageSourceMenu();
        }
    }

    // 画像ソースメニューを隠す
    hideImageSourceMenu() {
        const existingMenu = document.getElementById('image-source-menu');
        if (existingMenu) {
            existingMenu.remove();
        }
    }

    // カメラを開く（環境カメラ優先）
    openCamera() {
        // 一時的に capture 属性を設定
        this.imageInput.setAttribute('capture', 'environment');
        this.imageInput.click();
        // クリック後に capture 属性を削除
        setTimeout(() => {
            this.imageInput.removeAttribute('capture');
        }, 100);
    }

    // ライブラリを開く
    openLibrary() {
        // capture 属性が無いことを確認
        this.imageInput.removeAttribute('capture');
        this.imageInput.click();
    }
}

// グローバルに画像マネージャーを作成
window.imageManager = new ImageManager();

console.log("画像モジュール初期化完了"); 