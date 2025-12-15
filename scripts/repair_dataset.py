"""
Repair script for akura_dataset.json
Fixes:
1. Line 3720: Wrong message structure (missing role for assistant)
2. Line 5542: Extra backslash in JSON
3. Line 6494: Wrong message structure (missing role for assistant)
4. Line 8309: Extra period and quote in JSON
"""

import json
import shutil
from datetime import datetime

input_file = 'data/akura_dataset.json'
backup_file = f'data/akura_dataset_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

print(f"Creating backup: {backup_file}")
shutil.copy(input_file, backup_file)

print(f"Reading and repairing {input_file}...")

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
fixes_made = []

for i, line in enumerate(lines, 1):
    original_line = line
    line = line.strip()
    
    if not line:
        fixed_lines.append(original_line)
        continue
    
    try:
        obj = json.loads(line)
        
        # Check and fix message structure issues
        if 'messages' in obj:
            messages = obj['messages']
            needs_fix = False
            
            # Check for malformed messages (line 3720 and 6494 pattern)
            for msg in messages:
                if 'assistant' in msg and msg.get('role') == 'user':
                    # Found the pattern: user message has assistant key inside it
                    needs_fix = True
                    break
            
            if needs_fix:
                new_messages = []
                for msg in messages:
                    if 'assistant' in msg and msg.get('role') == 'user':
                        # Split into two messages
                        user_msg = {'role': 'user', 'content': msg.get('content', '')}
                        assistant_msg = {'role': 'assistant', 'content': msg.get('assistant', '')}
                        new_messages.append(user_msg)
                        new_messages.append(assistant_msg)
                    else:
                        new_messages.append(msg)
                obj['messages'] = new_messages
                fixes_made.append(f"Line {i}: Fixed malformed message structure")
            
            # Check assistant content is valid JSON
            for msg in obj['messages']:
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '')
                    try:
                        json.loads(content)
                    except json.JSONDecodeError:
                        # Try to fix common issues
                        original_content = content
                        
                        # Fix: extra backslash (line 5542 pattern: \\\" at end instead of \")
                        if '\\\\"' in content:
                            content = content.replace('\\\\"', '\\"')
                        
                        # Fix: extra period and quote (line 8309 pattern: ?"." instead of ?")
                        if '?"."' in content:
                            content = content.replace('?"."', '?"')
                        
                        # Try parsing again
                        try:
                            json.loads(content)
                            msg['content'] = content
                            fixes_made.append(f"Line {i}: Fixed invalid JSON in assistant content")
                        except json.JSONDecodeError:
                            fixes_made.append(f"Line {i}: WARNING - Could not fix invalid JSON: {content[:50]}...")
        
        fixed_lines.append(json.dumps(obj, ensure_ascii=False) + '\n')
        
    except json.JSONDecodeError as e:
        # Keep original line if we can't parse it
        fixes_made.append(f"Line {i}: WARNING - Could not parse line: {str(e)}")
        fixed_lines.append(original_line)

print(f"\nFixes made:")
for fix in fixes_made:
    print(f"  {fix}")

if not fixes_made:
    print("  No fixes needed!")

# Write fixed content
print(f"\nWriting fixed dataset...")
with open(input_file, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"Done! Backup saved to: {backup_file}")
print(f"   Total lines: {len(fixed_lines)}")

# Validate the fixed file
print("\nValidating fixed file...")
errors = []
with open(input_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            # Check structure
            if 'messages' not in obj or len(obj['messages']) != 3:
                errors.append(f"Line {i}: Missing messages or wrong count")
            else:
                for msg in obj['messages']:
                    if msg.get('role') == 'assistant':
                        try:
                            json.loads(msg['content'])
                        except:
                            errors.append(f"Line {i}: Invalid assistant JSON")
        except json.JSONDecodeError as e:
            errors.append(f"Line {i}: {e}")

if errors:
    print(f"Still have {len(errors)} issues:")
    for err in errors[:20]:
        print(f"  {err}")
else:
    print("All lines valid!")
