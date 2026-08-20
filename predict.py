import json

def generate_prediction(entries):
    if not entries or len(entries) < 6:
        return "1-2-3"
    
    # 級別（A1優先）と全国勝率でランク付け
    sorted_entries = sorted(
        entries,
        key=lambda x: (1 if x.get('class') == 'A1' else 0, x.get('national_win_rate', 0)),
        reverse=True
    )
    
    b1 = sorted_entries[0]['boat']
    b2 = sorted_entries[1]['boat']
    b3 = sorted_entries[2]['boat']
    
    return f"{b1}-{b2}-{b3}, {b1}-{b3}-{b2}"

if __name__ == "__main__":
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for venue in data.get("venues", []):
            for race in venue.get("races", []):
                race["prediction"] = generate_prediction(race.get("entries", []))
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print("✅ AI予想買い目の計算が正常に完了しました！")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
