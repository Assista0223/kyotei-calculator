# 🚀 Google AdMobアカウント設定ガイド

## ✅ 完成したファイル
- **KyoteiCalculatorPro.exe** - AdMob統合済み実行ファイル (83.6MB)
- 本物のGoogle AdMob広告コード統合済み
- テストIDで動作確認可能

## 📱 Google AdMobアカウント設定手順

### ステップ1: AdMobアカウント作成
1. **AdMob公式サイトにアクセス**
   - URL: https://admob.google.com/
   - Googleアカウントでログイン

2. **アカウント情報入力**
   - 国: 日本
   - タイムゾーン: (GMT+09:00) 東京
   - 通貨: 日本円 (JPY)

### ステップ2: アプリ登録
1. **「アプリを追加」をクリック**
   - プラットフォーム: Android
   - アプリ名: KYOTEI Calculator Pro
   - パッケージ名: com.yourcompany.kyoteicalculator

2. **アプリIDを取得**
   ```
   ca-app-pub-XXXXXXXXXX~YYYYYYYYYY
   ```

### ステップ3: 広告ユニット作成
1. **「広告ユニットを作成」**
   - 広告フォーマット: バナー
   - 広告ユニット名: Main Banner
   
2. **広告ユニットIDを取得**
   ```
   ca-app-pub-XXXXXXXXXX/ZZZZZZZZZZ
   ```

### ステップ4: コード更新
`main_with_admob.py`の186-187行目を更新:
```javascript
data-ad-client="ca-app-pub-XXXXXXXXXX"  // あなたのパブリッシャーID
data-ad-slot="ZZZZZZZZZZ"              // あなたの広告ユニットID
```

### ステップ5: 本番用ビルド
```bash
# 更新後に再ビルド
flet pack main_with_admob.py --name "KyoteiCalculatorPro"
```

## 💰 収益化の仕組み

### 広告収益の目安
- **バナー広告**: 1000表示あたり $0.50-2.00
- **日本市場**: 比較的高単価
- **競艇関連**: ギャンブル系は高収益カテゴリ

### 収益シミュレーション
| ユーザー数 | 日次表示数 | 月間収益目安 |
|-----------|-----------|-------------|
| 100人/日   | 3,000回   | ¥1,500-6,000 |
| 500人/日   | 15,000回  | ¥7,500-30,000 |
| 1000人/日  | 30,000回  | ¥15,000-60,000 |

## 🎯 次のステップ

### 1. Play Storeリリース準備
- Google Play Console登録（$25）
- アプリ説明文作成
- スクリーンショット準備
- プライバシーポリシー作成

### 2. マーケティング戦略
- 競艇関連フォーラムで紹介
- SNSでの拡散
- YouTubeレビュー依頼

### 3. 機能追加案
- [ ] レース結果自動取得
- [ ] 過去データ分析機能
- [ ] ユーザー間での予想共有
- [ ] プレミアム版（広告なし）

## ⚠️ 注意事項

### AdMobポリシー
- 自己クリック禁止
- 不正なトラフィック禁止
- コンテンツポリシー遵守

### 税務関連
- 収益が発生したら確定申告必要
- 年間20万円以上で申告義務

## 📞 サポート
- AdMobヘルプ: https://support.google.com/admob
- Fletドキュメント: https://flet.dev/docs

---

**準備完了！** あとはAdMobアカウントを作成して、広告IDを設定するだけです！