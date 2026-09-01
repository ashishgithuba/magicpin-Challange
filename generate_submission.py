import json
from pathlib import Path
import composer

def load_data():
    base_dir = Path("dataset/expanded")
    
    categories = {}
    for f in (base_dir / "categories").glob("*.json"):
        with open(f) as fp:
            data = json.load(fp)
            categories[data["slug"]] = data
            
    merchants = {}
    for f in (base_dir / "merchants").glob("*.json"):
        with open(f) as fp:
            data = json.load(fp)
            merchants[data["merchant_id"]] = data
            
    customers = {}
    for f in (base_dir / "customers").glob("*.json"):
        with open(f) as fp:
            data = json.load(fp)
            customers[data["customer_id"]] = data
            
    triggers = {}
    for f in (base_dir / "triggers").glob("*.json"):
        with open(f) as fp:
            data = json.load(fp)
            triggers[data["id"]] = data
            
    with open(base_dir / "test_pairs.json") as fp:
        test_pairs = json.load(fp)["pairs"]
        
    return categories, merchants, customers, triggers, test_pairs

def generate():
    categories, merchants, customers, triggers, test_pairs = load_data()
    
    print(f"Generating submission for {len(test_pairs)} test pairs...")
    
    with open("submission.jsonl", "w") as out:
        for pair in test_pairs:
            test_id = pair["test_id"]
            trigger_id = pair["trigger_id"]
            merchant_id = pair["merchant_id"]
            customer_id = pair.get("customer_id")
            
            trigger = triggers.get(trigger_id, {"id": trigger_id, "kind": "unknown"})
            merchant = merchants.get(merchant_id, {})
            category_slug = merchant.get("category_slug")
            category = categories.get(category_slug, {})
            customer = customers.get(customer_id) if customer_id else None
            
            try:
                composed = composer.compose(category, merchant, trigger, customer)
                
                # Verify required fields
                result = {
                    "test_id": test_id,
                    "body": composed.get("body", ""),
                    "cta": composed.get("cta", "open_ended"),
                    "send_as": composed.get("send_as", "vera"),
                    "suppression_key": composed.get("suppression_key", trigger.get("suppression_key", "")),
                    "rationale": composed.get("rationale", "")
                }
                
                out.write(json.dumps(result) + "\n")
            except Exception as e:
                print(f"Error composing for {test_id}: {e}")
                
    print("Done generating submission.jsonl")

if __name__ == "__main__":
    generate()
