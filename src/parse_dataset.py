import csv
import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent
dataset_dir = base_dir / "datasets"

input_csv = dataset_dir / "manual_label.csv"
output_json = dataset_dir / "manual_label.json"

def normalize_flags(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        flags = raw
    elif isinstance(raw, str):
        flags = raw.split(",")
    else:
        return[]
    return [f.strip() for f in flags if f.strip()]

dataset = []

def validate_condition(status, flags):
        if status == "ok" and flags:
            raise ValueError(f"Invalid condition: status 'ok' harus flags kosong. Ditemukan: {flags}")
        if status != "ok" and not flags:
            raise ValueError(f"Invalid condition: status '{status}' harus memiliki flags, tapi kosong.")
        
with open(input_csv, 'r', newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        status = row["condition_status"].strip() if row["condition_status"] else None
        flags = normalize_flags(row["condition_flags"])

        if status is None:
            raise ValueError(f"Row {row['id']} kosong condition_status, perbaiki CSV dulu.")

        validate_condition(status, flags)

        item = {
            "id": int(row["id"]),
            "text": row["text"],
            "parsed": {
                "amount": int(row["amount"]) if row["amount"] else None,
                "category": row["category"] or None,
                "time": row["time"] or None,
            },
            "condition": {
                "status": row["condition_status"],
                "flags": flags
            }
        }

        dataset.append(item)   

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"Saved {len(dataset)} records to {output_json}")