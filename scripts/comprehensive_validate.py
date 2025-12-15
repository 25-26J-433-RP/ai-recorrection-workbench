import json
import sys

# Redirect output to file AND console
class TeeOutput:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = TeeOutput('validation_report.txt')

filepath = 'data/akura_dataset.json'
print('=' * 60)
print('COMPREHENSIVE DATASET VALIDATION')
print('=' * 60)

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'\n📊 Total lines: {len(lines)}')

# 1. JSON Parse Errors
print('\n--- 1. JSON Parse Errors ---')
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
        parse_errors.append((i, str(e), line[:80]))

if parse_errors:
    print(f'❌ Found {len(parse_errors)} parse error(s):')
    for ln, err, preview in parse_errors[:10]:
        print(f'  Line {ln}: {err}')
        print(f'    Preview: {preview}...')
else:
    print('✅ No JSON parse errors found.')

# 2. Schema Validation (OpenAI format)
print('\n--- 2. Schema Validation (OpenAI Chat Format) ---')
schema_errors = []
for i, obj in valid_entries:
    issues = []
    if 'messages' not in obj:
        issues.append('missing "messages" key')
    elif not isinstance(obj['messages'], list):
        issues.append('"messages" is not a list')
    else:
        for j, msg in enumerate(obj['messages']):
            if 'role' not in msg:
                issues.append(f'message[{j}] missing "role"')
            elif msg['role'] not in ['system', 'user', 'assistant']:
                issues.append(f'message[{j}] has invalid role: {msg["role"]}')
            if 'content' not in msg:
                issues.append(f'message[{j}] missing "content"')
            elif not isinstance(msg['content'], str):
                issues.append(f'message[{j}] content is not a string')
    if issues:
        schema_errors.append((i, issues))

if schema_errors:
    print(f'❌ Found {len(schema_errors)} schema error(s):')
    for ln, issues in schema_errors[:10]:
        print(f'  Line {ln}: {issues}')
else:
    print('✅ All entries have valid OpenAI chat format schema.')

# 3. Content Issues
print('\n--- 3. Content Issues ---')
content_issues = []
for i, obj in valid_entries:
    msgs = obj.get('messages', [])
    issues = []
    
    # Check for empty content
    for j, msg in enumerate(msgs):
        content = msg.get('content', '')
        if not content or content.strip() == '':
            issues.append(f'message[{j}] has empty content')
        # Check assistant response is valid JSON
        if msg.get('role') == 'assistant':
            try:
                parsed = json.loads(content)
                if 'correction' not in parsed:
                    issues.append('assistant response missing "correction" key')
                if 'analysis' not in parsed:
                    issues.append('assistant response missing "analysis" key')
            except json.JSONDecodeError:
                issues.append('assistant content is not valid JSON')
    
    # Check for expected message structure (system, user, assistant)
    if len(msgs) != 3:
        issues.append(f'expected 3 messages, found {len(msgs)}')
    
    if issues:
        content_issues.append((i, issues))

if content_issues:
    print(f'❌ Found {len(content_issues)} content issue(s):')
    for ln, issues in content_issues[:10]:
        print(f'  Line {ln}: {issues}')
    if len(content_issues) > 10:
        print(f'  ... and {len(content_issues) - 10} more')
else:
    print('✅ All entries have valid content structure.')

# 4. Check for duplicates
print('\n--- 4. Duplicate Check ---')
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
    print(f'⚠️ Found {len(duplicates)} duplicate user inputs:')
    for content, lns in list(duplicates.items())[:5]:
        print(f'  "{content[:50]}..." appears on lines: {lns[:5]}')
    if len(duplicates) > 5:
        print(f'  ... and {len(duplicates) - 5} more duplicates')
else:
    print('✅ No duplicate user inputs found.')

print('\n' + '=' * 60)
print('VALIDATION COMPLETE')
print('=' * 60)
