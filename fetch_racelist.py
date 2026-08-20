import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def fetch_racelist(jcd, rno, date_str):
    url = f"https://www.boatrace.jp/owpc/pc/race/racelist?rno={rno}&jcd={jcd}&hd={date_str}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200: return None
        
        soup = BeautifulSoup(res.content, "html.parser")
        tbodies = soup.select("div.table1 table.is-w1050 tbody")
        entries = []

        for boat_num, tbody in enumerate(tbodies, start=1):
            if boat_num > 6: break
            
            # 選手名取得
            name_tag = tbody.select_one("div.is-fs18 a") or tbody.select_one("div.is-fs18")
            racer_name = name_tag.get_text(strip=True).replace(" ", "").replace(" ", "") if name_tag else f"{boat_num}号艇"
            
            text_block = tbody.get_text()
            id_match = re.search(r"(\d{4})\s*/\s*([AB][12])", text_block)
            racer_id = id_match.group(1) if id_match else ""
            racer_class = id_match.group(2) if id_match else "B1"
            
            # 各種数値の抽出
            numbers = re.findall(r"\d+\.\d+", text_block)
            
            entries.append({
                "boat": boat_num,
                "racer_id": racer_id,
                "name": racer_name,
                "class": racer_class,
                "national_win_rate": float(numbers[0]) if len(numbers) > 0 else 5.0,
                "local_win_rate": float(numbers[1]) if len(numbers) > 1 else 5.0,
                "motor_2rate": float(numbers[2]) if len(numbers) > 2 else 30.0,
                "boat_2rate": float(numbers[3]) if len(numbers) > 3 else 30.0,
                "exhibition_time": 0.0
            })
            
        if not entries:
            return None

        return {"race_no": int(rno), "status": "受付中", "entries": entries}
    except Exception as e:
        print(f"Error fetching race {rno}: {e}")
        return None

if __name__ == "__main__":
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    
    # 桐生（01）の 1R 〜 12R を順番に取得
    races = []
    print("データ取得中...")
    for rno in range(1, 13):
        race_info = fetch_racelist("01", rno, date_str)
        if race_info:
            races.append(race_info)
            print(f"  └ 桐生 {rno}R 取得成功")
    
    base_data = {
        "date": now.strftime("%Y-%m-%d"),
        "last_updated": now.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {"hit_rate": "--%", "recovery_rate": "--%"},
        "venues": [
            {
                "venue_code": "01",
                "venue_name": "桐生",
                "races": races
            }
        ]
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)
    print("✅ 全出走表の取得が完了しました。")
