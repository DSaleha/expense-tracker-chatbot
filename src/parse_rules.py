import csv
import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent
dataset_dir = base_dir / "datasets"

input_csv = dataset_dir / "decision_rules.csv"
output_json = dataset_dir / "decision_rules.json"

def normalize_flags(raw):
    if raw is None:
        return []
    
    if isinstance(raw, str):
        return [f.strip() for f in raw.split(",") if f.strip()]
    
    return []

rules = []

with open(input_csv, "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        rule = {
            "rule_id": row["rule_id"],
            "condition": {
                "status": row["condition_status"],
                "flags": normalize_flags(row["condition_flags"])
            },
            "action": row["action"],
            "final_status": row["final_status"],
            "bot_response": row["bot_response"],
            "notes": row["notes"]
        }

        rules.append(rule)

evaluation_order = [rule["rule_id"] for rule in rules]
output = {
    "rules": rules,
    "evaluation_order": evaluation_order
}

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Saved {len(rules)} rules to {output_json}")