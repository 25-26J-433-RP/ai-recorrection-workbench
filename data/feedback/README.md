# Feedback Data Directory

This directory stores teacher correction feedback collected through the Akura AI frontend.

## Purpose

The feedback data is used for:
1. **Model Fine-tuning** - Improve the AI's correction accuracy
2. **Pattern Analysis** - Understand common dyslexia patterns
3. **Teacher Behavior Analysis** - Learn from expert corrections

## File Types

### `feedback_YYYYMMDD_HHMMSS.json`
Individual feedback session files containing:
- Session metadata (timestamp, model used)
- All correction decisions (accept/reject/edit)
- Original and corrected words
- Detected patterns

### `training_data.jsonl`
Cumulative file in JSONL format, ready for fine-tuning:
```json
{"instruction": "Correct the Sinhala dyslexia error. Pattern: Visual Sequencing", "input": "ගෙරද", "output": "ගෙදර", "action": "accept"}
```

## Data Value

**Most Valuable Data**: Teacher edits (action="edit")
- These show where the AI was wrong
- Contains the teacher's manual correction
- Perfect for supervised fine-tuning

**Standard Data**: Accepted corrections (action="accept")
- Confirms AI was correct
- Good for reinforcement

**Negative Examples**: Rejected corrections (action="reject")
- Shows false positives
- Useful for improving precision

## Usage for Fine-tuning

```python
# Load training data
import json

training_examples = []
with open('training_data.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        example = json.loads(line)
        training_examples.append(example)

# Format for your fine-tuning framework
# (Unsloth, Hugging Face, etc.)
```

## Privacy Note

This data contains student writing samples. Handle with care and ensure compliance with data protection regulations.
