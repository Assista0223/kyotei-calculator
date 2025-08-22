# Google AdMob統合用のヘルパーファイル

"""
実際のAdMob統合手順:

1. Google AdMobアカウント作成
   - https://admob.google.com/ でアカウント作成
   - アプリを登録してApp IDを取得

2. テスト広告ユニットID（開発用）
   - バナー広告: ca-app-pub-3940256099942544/6300978111
   - インタースティシャル: ca-app-pub-3940256099942544/1033173712
   - リワード動画: ca-app-pub-3940256099942544/5224354917

3. Fletでの実装方法
   - WebViewを使用してHTML5広告を表示
   - または外部ブラウザで広告ページを開く

4. 実装例:
"""

import flet as ft

def create_admob_banner(ad_unit_id="ca-app-pub-3940256099942544/6300978111"):
    """
    AdMob風バナー広告コンポーネント
    実際の実装では、WebViewやiframeを使用
    """
    
    admob_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3940256099942544"
                crossorigin="anonymous"></script>
    </head>
    <body style="margin:0; background-color:#0f172a;">
        <!-- TEST AD BANNER -->
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-3940256099942544"
             data-ad-slot="6300978111"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
    </body>
    </html>
    """
    
    # Fletでは実際のWebViewコンポーネントを使用
    return ft.Container(
        content=ft.Text(
            "📱 AdMob広告領域\n（実装時はWebViewコンポーネント使用）",
            text_align=ft.TextAlign.CENTER,
            size=12,
            color="#9ca3af"
        ),
        height=60,
        bgcolor="#1a1a1a",
        border=ft.border.all(1, "#374151"),
        border_radius=8,
        padding=10,
    )

def create_interstitial_ad():
    """
    インタースティシャル広告（全画面広告）
    """
    pass

def create_rewarded_ad():
    """
    リワード動画広告
    """
    pass

# 実際のFlutterアプリでの統合例
FLUTTER_ADMOB_EXAMPLE = """
dependencies:
  google_mobile_ads: ^3.0.0

// main.dart
import 'package:google_mobile_ads/google_mobile_ads.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  MobileAds.instance.initialize();
  runApp(MyApp());
}

class BannerAdWidget extends StatefulWidget {
  @override
  _BannerAdWidgetState createState() => _BannerAdWidgetState();
}

class _BannerAdWidgetState extends State<BannerAdWidget> {
  BannerAd? _bannerAd;
  bool _isBannerAdReady = false;

  @override
  void initState() {
    super.initState();
    _bannerAd = BannerAd(
      adUnitId: 'ca-app-pub-3940256099942544/6300978111', // テスト用ID
      request: AdRequest(),
      size: AdSize.banner,
      listener: BannerAdListener(
        onAdLoaded: (_) {
          setState(() {
            _isBannerAdReady = true;
          });
        },
        onAdFailedToLoad: (ad, err) {
          print('Failed to load a banner ad: ${err.message}');
          _isBannerAdReady = false;
          ad.dispose();
        },
      ),
    );
    _bannerAd!.load();
  }

  @override
  Widget build(BuildContext context) {
    return _isBannerAdReady
        ? Container(
            width: _bannerAd!.size.width.toDouble(),
            height: _bannerAd!.size.height.toDouble(),
            child: AdWidget(ad: _bannerAd!),
          )
        : Container();
  }

  @override
  void dispose() {
    _bannerAd?.dispose();
    super.dispose();
  }
}
"""