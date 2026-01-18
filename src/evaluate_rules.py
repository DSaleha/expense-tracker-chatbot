import json
from pathlib import Path
from collections import Counter

base_dir = Path(__file__).resolve().parent
dataset_dir = base_dir / "datasets"
rules_file = dataset_dir / "decision_rules.json"
data_file = dataset_dir / "manual_label.json"

# --- Load rules & evaluation order ---
with open(rules_file, "r", encoding="utf-8") as f:
    rules_data = json.load(f)

rules = rules_data["rules"]
evaluation_order = rules_data["evaluation_order"]
rule_index = {rule["rule_id"]: rule for rule in rules}

# --- Function: evaluate a single rule set ---
def evaluate_rules(status: str, flags: list[str]) -> dict:
    decorative_flags = {"typo", "round_trip"}
    flags_set = set(flags) - decorative_flags

    for rule_id in evaluation_order:
        rule = rule_index[rule_id]
        rule_status = rule["condition"]["status"]
        rule_flags = set(rule["condition"]["flags"])

        # Match status first
        if rule_status != status:
            continue

        # Match flags (OR logic)
        if rule_flags:
            if flags_set.isdisjoint(rule_flags):
                continue
        else:
            if flags_set:
                continue

        return {
            "rule_id": rule["rule_id"],
            "action": rule["action"],
            "final_status": rule["final_status"],
            "bot_response": rule["bot_response"],
        }

    raise RuntimeError(f"No rule matched for status='{status}', flags={flags}")

# --- Function: batch evaluate dataset ---
def batch_evaluate(dataset: list[dict]) -> tuple[dict, Counter]:
    results = {"matched": 0, "unmatched": 0, "details": []}

    for row in dataset:
        status = row["condition"]["status"]
        flags = row["condition"]["flags"]
        try:
            match = evaluate_rules(status, flags)
            results["matched"] += 1
            results["details"].append({"id": row["id"], "rule_id": match["rule_id"]})
        except RuntimeError:
            results["unmatched"] += 1
            results["details"].append({"id": row["id"], "rule_id": None})

    counter = Counter(d["rule_id"] for d in results["details"] if d["rule_id"])
    return results, counter

# --- Main execution ---
if __name__ == "__main__":
    # Load dataset
    with open(data_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Batch evaluation
    results, counter = batch_evaluate(dataset)

    # Print summary
    print(f"Total records: {len(dataset)}")
    print(f"Matched: {results['matched']}, Unmatched: {results['unmatched']}")
    print("Rule match frequency:")
    for rule_id, freq in counter.most_common():
        print(f"  {rule_id}: {freq}x")

    # Optional: list records without matching rules
    unmatched_ids = [d["id"] for d in results["details"] if d["rule_id"] is None]
    if unmatched_ids:
        print(f"Records with no matching rule: {unmatched_ids}")
