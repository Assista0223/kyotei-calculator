"""
競艇オッズ自動取得モジュール
BOAT RACEオフィシャルサイトからオッズ情報をスクレイピング
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class BoatRaceOddsScraper:
    """競艇オッズスクレイピングクラス"""
    
    # 競艇場コード
    STADIUMS = {
        "桐生": "01", "戸田": "02", "江戸川": "03", "平和島": "04",
        "多摩川": "05", "浜名湖": "06", "蒲郡": "07", "常滑": "08",
        "津": "09", "三国": "10", "びわこ": "11", "住之江": "12",
        "尼崎": "13", "鳴門": "14", "丸亀": "15", "児島": "16",
        "宮島": "17", "徳山": "18", "下関": "19", "若松": "20",
        "芦屋": "21", "福岡": "22", "唐津": "23", "大村": "24"
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 最小リクエスト間隔（秒）
    
    def _rate_limit(self):
        """レート制限: リクエスト間隔を制御"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def get_stadium_code(self, stadium_name: str) -> Optional[str]:
        """競艇場名からコードを取得"""
        return self.STADIUMS.get(stadium_name)
    
    def fetch_odds_2tan(self, stadium_code: str, race_no: int, date: str = None) -> Dict[str, float]:
        """2連単オッズを取得
        
        Args:
            stadium_code: 競艇場コード（01-24）
            race_no: レース番号（1-12）
            date: 日付（YYYYMMDD形式）、Noneの場合は当日
        
        Returns:
            Dict[舟券番号, オッズ] 例: {"1-2": 5.4, "1-3": 12.3, ...}
        """
        self._rate_limit()
        
        # 日付が指定されていない場合は当日
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        # 2連単オッズURL
        url = f"https://www.boatrace.jp/owpc/pc/race/odds2tf"
        params = {
            'rno': race_no,
            'jcd': stadium_code,
            'hd': date
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            odds_data = {}
            
            # オッズテーブルを解析（実際のHTML構造に合わせて調整が必要）
            odds_tables = soup.find_all('table', class_='oddsTable')
            for table in odds_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # 舟券番号とオッズを抽出
                        ticket_text = cells[0].get_text(strip=True)
                        odds_text = cells[1].get_text(strip=True)
                        
                        # 舟券番号を整形（例: "1-2"）
                        ticket_match = re.match(r'(\d)-(\d)', ticket_text)
                        if ticket_match:
                            ticket = f"{ticket_match.group(1)}-{ticket_match.group(2)}"
                            try:
                                odds = float(odds_text)
                                odds_data[ticket] = odds
                            except ValueError:
                                continue
            
            return odds_data
            
        except requests.RequestException as e:
            print(f"オッズ取得エラー: {e}")
            return {}
        except Exception as e:
            print(f"解析エラー: {e}")
            return {}
    
    def fetch_odds_3tan(self, stadium_code: str, race_no: int, date: str = None) -> Dict[str, float]:
        """3連単オッズを取得
        
        Args:
            stadium_code: 競艇場コード（01-24）
            race_no: レース番号（1-12）
            date: 日付（YYYYMMDD形式）、Noneの場合は当日
        
        Returns:
            Dict[舟券番号, オッズ] 例: {"1-2-3": 15.4, "1-2-4": 25.3, ...}
        """
        self._rate_limit()
        
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        # 3連単オッズURL
        url = f"https://www.boatrace.jp/owpc/pc/race/odds3t"
        params = {
            'rno': race_no,
            'jcd': stadium_code,
            'hd': date
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            odds_data = {}
            
            # 3連単オッズの解析（実際のHTML構造に合わせて調整が必要）
            odds_tables = soup.find_all('table', class_='oddsTable')
            for table in odds_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        ticket_text = cells[0].get_text(strip=True)
                        odds_text = cells[1].get_text(strip=True)
                        
                        # 舟券番号を整形（例: "1-2-3"）
                        ticket_match = re.match(r'(\d)-(\d)-(\d)', ticket_text)
                        if ticket_match:
                            ticket = f"{ticket_match.group(1)}-{ticket_match.group(2)}-{ticket_match.group(3)}"
                            try:
                                odds = float(odds_text)
                                odds_data[ticket] = odds
                            except ValueError:
                                continue
            
            return odds_data
            
        except requests.RequestException as e:
            print(f"オッズ取得エラー: {e}")
            return {}
        except Exception as e:
            print(f"解析エラー: {e}")
            return {}
    
    def get_race_info(self, stadium_code: str, race_no: int, date: str = None) -> Dict:
        """レース情報を取得（レース名、締切時刻など）"""
        self._rate_limit()
        
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        url = f"https://www.boatrace.jp/owpc/pc/race/racelist"
        params = {
            'rno': race_no,
            'jcd': stadium_code,
            'hd': date
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # レース情報を抽出（実際のHTML構造に合わせて調整が必要）
            race_info = {
                'stadium_code': stadium_code,
                'race_no': race_no,
                'date': date,
                'race_name': '',
                'deadline': '',
                'status': 'unknown'
            }
            
            # レース名を取得
            race_name_elem = soup.find('h3', class_='race_name')
            if race_name_elem:
                race_info['race_name'] = race_name_elem.get_text(strip=True)
            
            return race_info
            
        except requests.RequestException as e:
            print(f"レース情報取得エラー: {e}")
            return {}


# 使用例
if __name__ == "__main__":
    scraper = BoatRaceOddsScraper()
    
    # 例: 平和島第1レースの2連単オッズを取得
    stadium_code = scraper.get_stadium_code("平和島")
    if stadium_code:
        odds_2tan = scraper.fetch_odds_2tan(stadium_code, 1)
        print(f"2連単オッズ: {odds_2tan}")
        
        # 3連単オッズも取得
        odds_3tan = scraper.fetch_odds_3tan(stadium_code, 1)
        print(f"3連単オッズ: {odds_3tan}")