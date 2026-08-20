import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

VENUE_NAMES = {
    "01":"桐生", "02":"戸田", "03":"江戸川", "04":"平和島", "05":"多摩川", "06":"浜名湖",
    "07":"蒲郡", "08":"常滑", "09":"津", "10":"三国", "11":"びわこ", "12":"住之江",
    "13":"尼崎", "14":"鳴門", "15":"丸亀", "16":"児島", "17":"宮島", "18":"徳山",
    "19":"下関", "20":"若松", "21":"芦屋", "22":"福岡", "23":"唐津", "24":"大村"
}

def check_active_venues(date_str):
    url = f"https://www.boatrace.jp/owpc/pc/race/index?hd={date_str}"
    active_venues = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, "html.parser")
            for link in soup.select("a[href*='jcd=']"):
                m = re.search(r"jcd=(\d{2})", link["href"])
                if m and m.group(1) not in active_venues:
                    active_venues.append(m.group(1))
    except Exception as e:
        print(f"会場取得エラー: {e}")
    return active_venues

def fetch_racelist(jcd, rno, date_str):
    url = f"https://www.boatrace.jp/owpc/pc/race/racelist?rno={rno}&jcd={jcd}&hd={date_str}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.content, "html.parser")
        tbodies = soup.select("div.table1 table.is-w1050 tbody") or soup.select("div.table1 table tbody")
        if not tbodies:
            return None
        
        entries = []
        for boat_num, tbody in enumerate(tbodies, start=1):
            if boat_num > 6:
                break
            name_tag = tbody.select_one("div.is-fs18 a") or tbody.select_one("div.is-fs18")
            racer_name = name_tag.get_text(strip=True).replace(" ", "").replace(" ", "") if name_tag else f"{boat_num}号艇"
            
            text_block = tbody.get_text()
            class_match = re.search(r"([AB][12])", text_block)
            racer_class = class_match.group(1) if class_match else "B1"
            
            rates = re.findall(r"\d+\.\d+", text_block)
            
            entries.append({
                "boat": boat_num,
                "name": racer_name,
                "class": racer_class,
                "national_win_rate": float(rates[0]) if len(rates) > 0 else 5.00,
                "motor_2rate": float(rates[2]) if len(rates) > 2 else 30.0
            })
            
        return {
            "race_no": int(rno),
            "deadline": "発売終了",
            "entries": entries,
            "prediction": "計算中..."
        }
    except Exception:
        return None

def fetch_venue_all_races(jcd, date_str):
    results = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_racelist, jcd, rno, date_str): rno for rno in range(1, 13)}
        for future in as_completed(futures):
            rno = futures[future]
            res = future.result()
            if res:
                results[rno] = res
    return [results[rno] for rno in sorted(results.keys())]

if __name__ == "__main__":
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    
    print("本日の開催会場を確認中...")
    active_venues = check_active_venues(date_str)
    print(f"検出された会場: {active_venues}")
    
    venues_data = []
    for jcd in active_venues:
        v_name = VENUE_NAMES.get(jcd, f"会場{jcd}")
        print(f"[{v_name}] 全12レース取得中...")
        races = fetch_venue_all_races(jcd, date_str)
        if races:
            venues_data.append({
                "venue_code": jcd,
                "venue_name": v_name,
                "races": races
            })
    
    base_data = {
        "date": now.strftime("%Y-%m-%d"),
        "last_updated": now.strftime("%Y-%m-%d %H:%M:%S"),
        "news": [
            {"id": 1, "title": "全場出走表・AI予想データを更新完了", "date": now.strftime("%Y-%m-%d")}
        ],
        "venues": venues_data
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)
        
    print("\n✅ data.json の生成が正常に完了しました！")
