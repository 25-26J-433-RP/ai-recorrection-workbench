import json

filepath = "data/akura_dataset.json"
errors = []

print(f"🔍 Validating {filepath}...")
try:
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip(): continue # Skip empty lines
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: {e}")
                if len(errors) > 5: break

    if errors:
        print("❌ Syntax Errors Found:")
        for err in errors:
            print(err)
        exit(1)
    else:
        print("✅ Dataset is valid JSONL.")

except Exception as e:
    print(f"❌ Error reading file: {e}")
    exit(1)
