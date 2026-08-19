import json

def calculate_ai_predictions():
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for venue in data.get("venues", []):
        for race in venue.get("races", []):
            entries = race.get("entries", [])
            if not entries: continue

            scored = []
            for entry in entries:
                score = (entry.get("national_win_rate", 0) * 0.4) + \
                        (entry.get("motor_2rate", 0) * 0.3) + \
                        ((7.0 - entry.get("exhibition_time", 6.8)) * 30)
                if entry.get("boat") == 1:
                    score += 15.0
                scored.append({"boat": entry["boat"], "score": score})

            scored.sort(key=lambda x: x["score"], reverse=True)
            
            top1, top2, top3, top4 = scored[0]["boat"], scored[1]["boat"], scored[2]["boat"], scored[3]["boat"]
            
            race["prediction"] = {
                "ai_score_order": [s["boat"] for s in scored],
                "recommendations": [f"{top1}-{top2}-{top3}", f"{top1}-{top2}-{top4}", f"{top1}-{top3}-{top2}"]
            }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("✅ AI予想買い目の再計算が完了しました。")

if __name__ == "__main__":
    calculate_ai_predictions()