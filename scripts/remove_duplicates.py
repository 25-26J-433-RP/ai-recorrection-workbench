"""
Remove duplicate entries from akura_dataset.json
Keeps only the first occurrence of each unique user input.
"""

import json
import shutil
from datetime import datetime

input_file = 'data/akura_dataset.json'
backup_file = f'data/akura_dataset_before_dedup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

print(f"Creating backup: {backup_file}")
shutil.copy(input_file, backup_file)

print(f"Reading {input_file}...")
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original entries: {len(lines)}")

# Track unique user inputs
seen_inputs = set()
unique_lines = []
duplicates_removed = 0

for i, line in enumerate(lines, 1):
    line_stripped = line.strip()
    if not line_stripped:
        continue
    
    try:
        obj = json.loads(line_stripped)
        
        # Get user input content
        user_input = None
        for msg in obj.get('messages', []):
            if msg.get('role') == 'user':
                user_input = msg.get('content', '')
                break
        
        if user_input is None:
            # Keep entries without user input (shouldn't happen but just in case)
            unique_lines.append(line)
        elif user_input not in seen_inputs:
            # First time seeing this input - keep it
            seen_inputs.add(user_input)
            unique_lines.append(line)
        else:
            # Duplicate - skip
            duplicates_removed += 1
            
    except json.JSONDecodeError:
        # Keep malformed lines (shouldn't happen after previous fixes)
        unique_lines.append(line)

print(f"Duplicates removed: {duplicates_removed}")
print(f"Unique entries remaining: {len(unique_lines)}")

# Write deduplicated dataset
print(f"Writing deduplicated dataset...")
with open(input_file, 'w', encoding='utf-8') as f:
    f.writelines(unique_lines)

print(f"\nDone!")
print(f"  Original: {len(lines)} entries")
print(f"  After dedup: {len(unique_lines)} entries")
print(f"  Removed: {duplicates_removed} duplicates")
print(f"  Backup: {backup_file}")
