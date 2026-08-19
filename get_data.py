import json
import os
import re
import urllib.request
from datetime import datetime

ALL_VENUES = [
    "桐生", "戸田", "江戸川", "平和島", "多摩川", "浜名湖", "蒲郡", "常滑",
    "津", "三国", "びわこ", "住之江", "尼崎", "鳴門", "丸亀", "児島",
    "宮島", "徳山", "下関", "若松", "芦屋", "福岡", "唐津", "大村"
]

now = datetime.now()
date_str_jp = now.strftime("%Y年%m月%d日")
yy = now.strftime("%y")
mm = now.strftime("%m")
dd = now.strftime("%d")

file_name = f"k{yy}{mm}{dd}.txt"
download_url = f"https://www.boatrace.jp/owpc/pc/extra/data/download/{file_name}"

print(f"[{now.strftime('%H:%M:%S')}] データの取得と全場解析を実行中... ({file_name})")

venues_data = []

try:
    req = urllib.request.Request(
        download_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response:
        raw_text = response.read().decode('cp932', errors='ignore')

    lines = raw_text.splitlines()
    current_venue = None
    current_race = None

    for line in lines:
        clean_line = re.sub(r'[\s \t]+', '', line)

        for v_name in ALL_VENUES:
            if f"◆◆◆{v_name}◆◆◆" in clean_line or f"［{v_name}］" in clean_line or f"[{v_name}]" in clean_line:
                existing = next((v for v in venues_data if v["name"] == v_name), None)
                if not existing:
                    current_venue = {"name": v_name, "races": []}
                    venues_data.append(current_venue)
                else:
                    current_venue = existing
                break

        race_match = re.search(r'^\s*(\d{1,2})R', line)
        if race_match and current_venue:
            r_num = int(race_match.group(1))
            current_race = {
                "race_no": r_num,
                "status": "確定",
                "payout": "-",
                "prediction": "1-2-3"
            }
            current_venue["races"].append(current_race)

        payout_match = re.search(r'３連単\s+([\d-]+)\s+([\d,]+)', line)
        if payout_match and current_race:
            combo = payout_match.group(1)
            price = payout_match.group(2)
            current_race["payout"] = f"{combo} {price}円"

    print(f"→ 本日掲載されている {len(venues_data)} 場のデータを取得しました。")

except Exception as e:
    print(f"⚠️ 公式データの取得に失敗/まだ公開されていません: {e}")

if not venues_data:
    print("→ データ未公開時間帯のため、全24場の表示テスト用データを生成します。")
    venues_data = [
        {
            "name": v_name, 
            "races": [{"race_no": r, "status": "受付中", "payout": "-", "prediction": "1-2-3"} for r in range(1, 13)]
        }
        for v_name in ALL_VENUES
    ]

output_data = {
    "date": date_str_jp,
    "last_updated": now.strftime("%H:%M:%S"),
    "venues": venues_data,
    "stats": {
        "hit_rate": "--%",
        "recovery_rate": "--%"
    }
}

with open("./data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"[{now.strftime('%H:%M:%S')}] data.json の更新が完了しました！")