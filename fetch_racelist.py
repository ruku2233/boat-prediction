import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def fetch_racelist(jcd, rno, date_str):
    url = f"https://www.boatrace.jp/owpc/pc/race/racelist?rno={rno}&jcd={jcd}&hd={date_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200: return None
        
        soup = BeautifulSoup(res.content, "html.parser")
        tbodies = soup.select("div.table1 table.is-w1050 tbody")
        entries = []

        for boat_num, tbody in enumerate(tbodies, start=1):
            if boat_num > 6: break
            
            name_tag = tbody.select_one("div.is-fs18 a") or tbody.select_one("div.is-fs18")
            racer_name = name_tag.get_text(strip=True).replace(" ", "") if name_tag else "不明"
            
            text_block = tbody.get_text()
            id_match = re.search(r"(\d{4})\s*/\s*([AB][12])", text_block)
            racer_id = id_match.group(1) if id_match else ""
            racer_class = id_match.group(2) if id_match else ""
            
            numbers = re.findall(r"\d+\.\d+", text_block)
            
            entries.append({
                "boat": boat_num,
                "racer_id": racer_id,
                "name": racer_name,
                "class": racer_class,
                "national_win_rate": float(numbers[0]) if len(numbers) > 0 else 0.0,
                "local_win_rate": float(numbers[2]) if len(numbers) > 2 else 0.0,
                "motor_2rate": float(numbers[4]) if len(numbers) > 4 else 0.0,
                "boat_2rate": float(numbers[6]) if len(numbers) > 6 else 0.0,
                "exhibition_time": 0.0
            })
            
        return {"race_no": int(rno), "status": "受付中", "entries": entries}
    except Exception as e:
        print(f"Error fetching racelist: {e}")
        return None

if __name__ == "__main__":
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    
    race_info = fetch_racelist("01", 1, date_str)
    
    base_data = {
        "date": now.strftime("%Y-%m-%d"),
        "last_updated": now.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {"hit_rate": "--%", "recovery_rate": "--%"},
        "venues": [
            {
                "venue_code": "01",
                "venue_name": "桐生",
                "races": [race_info] if race_info else []
            }
        ]
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)
    print("✅ 出走表の取得が完了しました。")