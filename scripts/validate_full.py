import json

filepath = 'data/akura_dataset.json'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

results = []
results.append('=' * 60)
results.append('COMPREHENSIVE DATASET VALIDATION')
results.append('=' * 60)
results.append(f'Total lines: {len(lines)}')

# 1. JSON Parse Errors
results.append('\n--- 1. JSON Parse Errors ---')
parse_errors = []
valid_entries = []
for i, line in enumerate(lines, 1):
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
        valid_entries.append((i, obj))
    except json.JSONDecodeError as e:
        parse_errors.append((i, str(e)))

if parse_errors:
    results.append(f'FOUND {len(parse_errors)} parse error(s):')
    for ln, err in parse_errors[:10]:
        results.append(f'  Line {ln}: {err}')
else:
    results.append('OK: No JSON parse errors found.')

# 2. Schema Validation (OpenAI format)
results.append('\n--- 2. Schema Validation (OpenAI Chat Format) ---')
schema_errors = []
for i, obj in valid_entries:
    issues = []
    if 'messages' not in obj:
        issues.append('missing messages key')
    elif not isinstance(obj['messages'], list):
        issues.append('messages is not a list')
    else:
        for j, msg in enumerate(obj['messages']):
            if 'role' not in msg:
                issues.append(f'message[{j}] missing role')
            elif msg['role'] not in ['system', 'user', 'assistant']:
                issues.append(f'message[{j}] has invalid role: {msg["role"]}')
            if 'content' not in msg:
                issues.append(f'message[{j}] missing content')
            elif not isinstance(msg['content'], str):
                issues.append(f'message[{j}] content is not a string')
    if issues:
        schema_errors.append((i, issues))

if schema_errors:
    results.append(f'FOUND {len(schema_errors)} schema error(s):')
    for ln, issues in schema_errors[:10]:
        results.append(f'  Line {ln}: {issues}')
else:
    results.append('OK: All entries have valid OpenAI chat format schema.')

# 3. Content Issues
results.append('\n--- 3. Content Issues ---')
content_issues = []
for i, obj in valid_entries:
    msgs = obj.get('messages', [])
    issues = []
    
    for j, msg in enumerate(msgs):
        content = msg.get('content', '')
        if not content or content.strip() == '':
            issues.append(f'message[{j}] has empty content')
        if msg.get('role') == 'assistant':
            try:
                parsed = json.loads(content)
                if 'correction' not in parsed:
                    issues.append('assistant response missing correction key')
                if 'analysis' not in parsed:
                    issues.append('assistant response missing analysis key')
            except json.JSONDecodeError:
                issues.append('assistant content is not valid JSON')
    
    if len(msgs) != 3:
        issues.append(f'expected 3 messages, found {len(msgs)}')
    
    if issues:
        content_issues.append((i, issues))

if content_issues:
    results.append(f'FOUND {len(content_issues)} content issue(s):')
    for ln, issues in content_issues[:15]:
        results.append(f'  Line {ln}: {issues}')
    if len(content_issues) > 15:
        results.append(f'  ... and {len(content_issues) - 15} more')
else:
    results.append('OK: All entries have valid content structure.')

# 4. Check for duplicates
results.append('\n--- 4. Duplicate Check ---')
user_inputs = {}
for i, obj in valid_entries:
    msgs = obj.get('messages', [])
    for msg in msgs:
        if msg.get('role') == 'user':
            content = msg.get('content', '')
            if content in user_inputs:
                user_inputs[content].append(i)
            else:
                user_inputs[content] = [i]

duplicates = {k: v for k, v in user_inputs.items() if len(v) > 1}
if duplicates:
    results.append(f'WARNING: Found {len(duplicates)} duplicate user inputs')
    count = 0
    for content, lns in duplicates.items():
        if count < 10:
            results.append(f'  Lines {lns[:5]} have same input (showing first 5)')
        count += 1
    if len(duplicates) > 10:
        results.append(f'  ... and {len(duplicates) - 10} more duplicates')
else:
    results.append('OK: No duplicate user inputs found.')

results.append('\n' + '=' * 60)
results.append('VALIDATION COMPLETE')
results.append('=' * 60)

# Write to file
with open('validation_output.txt', 'w', encoding='ascii', errors='replace') as f:
    f.write('\n'.join(results))

print('Results written to validation_output.txt')
