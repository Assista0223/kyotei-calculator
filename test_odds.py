"""
オッズ取得のテストスクリプト
実際のHTML構造を分析して正しいパース方法を見つける
"""

from odds_scraper import BoatRaceOddsScraper
import sys

def test_fetch_odds():
    scraper = BoatRaceOddsScraper()
    
    # テストパラメータ
    stadium_name = "平和島"  # テスト用競艇場
    race_no = 1  # 第1レース
    
    print(f"テスト開始: {stadium_name} 第{race_no}レース")
    print("-" * 50)
    
    # 競艇場コードを取得
    stadium_code = scraper.get_stadium_code(stadium_name)
    if not stadium_code:
        print(f"エラー: '{stadium_name}' の競艇場コードが見つかりません")
        return
    
    print(f"競艇場コード: {stadium_code}")
    
    # デバッグモードでオッズ取得
    print("\n2連単オッズを取得中...")
    odds_data = scraper.fetch_odds_2tan(stadium_code, race_no, debug=True)
    
    if odds_data:
        print(f"\n成功! {len(odds_data)}件のオッズを取得しました")
        print("\n取得したオッズ（上位10件）:")
        sorted_odds = sorted(odds_data.items(), key=lambda x: x[1])
        for i, (ticket, odds) in enumerate(sorted_odds[:10], 1):
            print(f"  {i:2d}. {ticket}: {odds:6.1f}倍")
    else:
        print("\nオッズの取得に失敗しました")
        print("以下の点を確認してください:")
        print("1. インターネット接続が正常か")
        print("2. 指定した競艇場で本日レースが開催されているか")
        print("3. レース時間が適切か（締切前のレースか）")
        
        # HTMLを保存してデバッグ
        print("\n詳細なデバッグのため、HTMLを保存します...")
        import requests
        from datetime import datetime
        
        url = "https://www.boatrace.jp/owpc/pc/race/odds2tf"
        params = {
            'rno': race_no,
            'jcd': stadium_code,
            'hd': datetime.now().strftime("%Y%m%d")
        }
        
        try:
            response = requests.get(url, params=params)
            with open("debug_odds.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("HTMLを 'debug_odds.html' に保存しました")
            print("このファイルを開いて実際のHTML構造を確認してください")
            
            # 簡易的な構造分析
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print("\nHTML構造の簡易分析:")
            print(f"- タイトル: {soup.title.string if soup.title else '不明'}")
            print(f"- テーブル数: {len(soup.find_all('table'))}")
            print(f"- クラス 'oddslist' を持つ要素: {len(soup.find_all(class_='oddslist'))}")
            print(f"- クラス 'is-fs14' を持つ要素: {len(soup.find_all(class_='is-fs14'))}")
            
            # エラーメッセージがないか確認
            error_messages = soup.find_all(text=lambda text: 'エラー' in text or 'メンテナンス' in text if text else False)
            if error_messages:
                print("\nエラーメッセージが見つかりました:")
                for msg in error_messages[:3]:
                    print(f"  - {msg.strip()[:50]}...")
                    
        except Exception as e:
            print(f"デバッグ中にエラー: {e}")

if __name__ == "__main__":
    test_fetch_odds()