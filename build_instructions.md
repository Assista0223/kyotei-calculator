# 📱 競艇資金配分アプリ - 本格収益化ガイド

## 🚀 現在の状態
✅ **AdMob統合準備完了**
- テスト用パブリッシャーID: `ca-pub-3940256099942544`
- 広告スロット: `6300978111` (バナー広告)
- HTMLコード準備済み（`main.py`の176-224行目）

## 📱 APK化とAdMob収益化手順

### 1. APK作成
```bash
# Fletアプリをパッケージ化
flet pack main.py --name "KYOTEI Calculator" --description "競艇資金配分計算ツール"

# または新しい構文
flet build apk
```

### 2. AdMob実装 (APK化後)
```python
# WebViewを別パッケージでインストール
pip install flet-webview

# main.pyのWebView部分を有効化
from flet_webview import WebView
```

### 3. 本番AdMob設定
1. **Google AdMobアカウント作成**
   - https://admob.google.com/
   
2. **アプリ登録**
   - App ID取得: `ca-app-pub-XXXXXXXXXX~YYYYYYYYYY`
   
3. **広告ユニット作成**
   - バナー広告ユニット作成
   - 広告ユニットID取得: `ca-app-pub-XXXXXXXXXX/ZZZZZZZZZZ`

4. **コード更新**
```javascript
// main.pyの182行目を更新
data-ad-client="ca-pub-XXXXXXXXXX"  // 自分のパブリッシャーID
data-ad-slot="ZZZZZZZZZZ"          // 自分の広告ユニットID
```

### 4. 本格リリース手順
1. **Google Play Console登録**
   - デベロッパーアカウント作成（$25）
   
2. **APKアップロード**
   - Play Store審査提出
   
3. **収益化開始**
   - 実際のAdMob広告配信開始
   - 収益レポート確認

## 💰 収益予測
- **バナー広告**: $0.50-2.00 per 1000 impressions
- **インタースティシャル**: $3-5 per 1000 impressions  
- **ユーザー数1000人/日**: 月額$50-200程度

## 🔧 開発継続
```bash
# 現在はデスクトップ版として動作
python main.py

# Web版テスト
flet run main.py --web
```

## 📝 追加機能案
- [ ] インタースティシャル広告（計算完了時）
- [ ] リワード動画広告（プレミアム機能解放）
- [ ] 有料版（広告なし）
- [ ] クラウド保存機能
- [ ] ソーシャル共有機能