import json

filepath = 'data/akura_dataset.json'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Fix line 5542 (index 5541)
line_idx = 5541
original = lines[line_idx]

obj = json.loads(original)
old_content = obj['messages'][2]['content']

# The problem is extra backslash - correction ends with .\\" but should be ."
# Replace the malformed ending
new_content = old_content.replace('කෑව.\\', 'කෑවා.')
obj['messages'][2]['content'] = new_content
lines[line_idx] = json.dumps(obj, ensure_ascii=False) + '\n'

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed line 5542!")

# Validate
errors = []
for i, line in enumerate(lines, 1):
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
        if 'messages' in obj:
            for msg in obj['messages']:
                if msg.get('role') == 'assistant':
                    try:
                        json.loads(msg['content'])
                    except json.JSONDecodeError:
                        errors.append(f"Line {i}: Invalid assistant JSON")
    except json.JSONDecodeError as e:
        errors.append(f"Line {i}: JSON error - {e}")

if errors:
    print(f"Still have {len(errors)} errors:")
    for e in errors[:10]:
        print(f"  {e}")
else:
    print("ALL lines valid! Dataset repaired successfully!")
