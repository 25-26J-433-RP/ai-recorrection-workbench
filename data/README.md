# Training Data Directory

This directory stores generated training data for fine-tuning the model.

## Generate Training Data

```bash
cd scripts
python generate_training_data.py --output ../data/training_data.jsonl --count 5000
```

## Files

- `training_data.jsonl` - Instruction format training data
- `training_chat.jsonl` - Chat format training data
- `validation_data.jsonl` - Validation set (10% of data)
