"""
Convert akura_dataset.json from JSONL format to JSON array format
"""

import json

input_file = 'data/akura_dataset.json'
output_file = 'data/akura_dataset.json'

print(f"Reading {input_file}...")

# Read JSONL and convert to list
entries = []
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            obj = json.loads(line)
            entries.append(obj)

print(f"Total entries: {len(entries)}")

# Write as JSON array with pretty formatting
print(f"Writing as JSON array to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print("Done! Dataset converted to JSON array format.")
