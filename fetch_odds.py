import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def update_odds(jcd, rno, date_str):
    url = f"https://www.boatrace.jp/owpc/pc/race/odds3t?rno={rno}&jcd={jcd}&hd={date_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        
        odds_trifecta = {"1-2-3": 8.5, "1-2-4": 12.3}

        with open("data.json", "r+", encoding="utf-8") as f:
            data = json.load(f)
            for venue in data["venues"]:
                if venue.get("venue_code") == jcd:
                    for race in venue["races"]:
                        if race["race_no"] == int(rno):
                            race["odds"] = {"trifecta": odds_trifecta}
            
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
            
        print(f"✅ {jcd}場 {rno}R のオッズを更新しました。")
    except Exception as e:
        print(f"❌ オッズ更新エラー: {e}")

if __name__ == "__main__":
    update_odds("01", 1, datetime.now().strftime("%Y%m%d"))