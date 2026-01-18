import csv
from pathlib import Path
from collections import Counter
from evaluate_rules import evaluate_rules
from edge_flagger import edge_flagger
from amount_normalizer import normalize_amount

base_dir = Path(__file__).resolve().parent
dataset_dir = base_dir / "datasets"

raw_file = dataset_dir / "raw_data.csv"
output_file = dataset_dir / "edge_test_result_v2.csv"

data = []
with open(raw_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

results = []
rule_counter = Counter()
unmatched = []

for row in data:
    status, flags = edge_flagger(row["text"])
    amount_info = normalize_amount(row["text"])

    try:
        decision = evaluate_rules(status, flags)
        rule_counter[decision["rule_id"]] += 1

        results.append({
            "id": row["id"],
            "text": row["text"],
            "status": status,
            "flags": "|".join(flags),
            "rule": decision["rule_id"],
            "amount": amount_info.get("amount"),
            "currency": amount_info.get("currency"),
            "normalized": amount_info.get("normalized"),
        })

    except RuntimeError as e:
        unmatched.append({
            "id": row["id"],
            "text": row["text"],
            "status": status,
            "flags": "|".join(flags),
            "rule": None,
            "error": str(e)
        })

# --- SAVE RESULT ---
with open(output_file, "w", newline="", encoding="utf-8") as f:
    fieldnames = results[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Saved edge test result to {output_file}")