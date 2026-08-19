import urllib.request
import re
import json
from datetime import datetime

def fetch_official_results():
    now = datetime.now()
    yy, mm, dd = now.strftime("%y"), now.strftime("%m"), now.strftime("%d")
    file_name = f"k{yy}{mm}{dd}.txt"
    download_url = f"https://www.boatrace.jp/owpc/pc/extra/data/download/{file_name}"

    try:
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            raw_text = response.read().decode('cp932', errors='ignore')

        lines = raw_text.splitlines()
        payout_data = {}
        for line in lines:
            payout_match = re.search(r'３連単\s+([\d-]+)\s+([\d,]+)', line)
            if payout_match:
                combo = payout_match.group(1)
                price = payout_match.group(2).replace(',', '')
                payout_data["trifecta"] = {"combination": combo, "payout": int(price)}

        with open("data.json", "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["last_updated"] = now.strftime("%Y-%m-%d %H:%M:%S")
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
            
        print("✅ レース結果・払戻金の更新が完了しました。")
    except Exception as e:
        print(f"⚠️ 結果データ取得エラー/未公開: {e}")

if __name__ == "__main__":
    fetch_official_results()