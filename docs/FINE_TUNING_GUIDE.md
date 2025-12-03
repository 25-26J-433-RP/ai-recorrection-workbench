# Akura AI - Fine-Tuning Guide

## Overview

This guide explains how to fine-tune the base LLM (llama3.2:1b) on your custom Sinhala dyslexia correction dataset.

## Step 1: Generate Training Data

```bash
cd scripts

# Generate 5000 training examples in instruction format
python generate_training_data.py --output ../data/training_data.jsonl --count 5000 --format instruction

# Or generate in chat format for conversational fine-tuning
python generate_training_data.py --output ../data/training_chat.jsonl --count 5000 --format chat
```

### Output Format (Instruction)

```json
{
  "instruction": "Correct the following Sinhala text for dyslexic writing errors. Output only the corrected text.",
  "input": "මම ගෙරද යනව",
  "output": "මම ගෙදර යනවා",
  "metadata": {
    "error_type": "visual_scrambling",
    "errors": [{"original": "ගෙදර", "error": "ගෙරද", "type": "visual_scrambling"}]
  }
}
```

## Step 2: Expand Vocabulary (Optional)

Edit `scripts/sinhala_vocabulary.py` to add more:
- Nouns (people, animals, objects, places)
- Verbs (different tenses and forms)
- Adjectives and adverbs
- Common misspellings

## Step 3: Fine-Tune with Ollama

### Option A: Using Ollama Modelfile

1. Create a Modelfile:

```dockerfile
# Modelfile
FROM llama3.2:1b

# Set parameters
PARAMETER temperature 0.3
PARAMETER num_predict 256

# System prompt
SYSTEM """You are an expert Sinhala language teacher specializing in helping dyslexic students.
Your task is to correct Sinhala text that may contain dyslexic writing errors.

Types of errors to look for and correct:
1. Visual Scrambling: Letters in wrong order (e.g., ගෙරද → ගෙදර)
2. Phonetic Confusion: Dental/Retroflex swaps (e.g., න/ණ, ල/ළ)
3. Visual Reversal: Shape confusion (e.g., බ/ඩ)
4. Grammar Issues: Colloquial to written form (e.g., යනව → යනවා)

Output ONLY the corrected text, nothing else."""
```

2. Create custom model:

```bash
ollama create akura-sinhala -f Modelfile
```

### Option B: Using Hugging Face + PEFT (LoRA)

For proper fine-tuning with your dataset:

```bash
pip install transformers peft datasets accelerate bitsandbytes
```

```python
# finetune.py
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer

# Load base model
model_name = "meta-llama/Llama-3.2-1B"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# LoRA config for efficient fine-tuning
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Load your dataset
dataset = load_dataset("json", data_files="data/training_data.jsonl")

# Training arguments
training_args = TrainingArguments(
    output_dir="./akura-sinhala-lora",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    save_steps=100,
    logging_steps=10,
)

# Train
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    peft_config=lora_config,
    args=training_args,
    tokenizer=tokenizer,
)

trainer.train()
trainer.save_model("./akura-sinhala-final")
```

### Option C: Using Unsloth (Faster)

```bash
pip install unsloth
```

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-1B",
    max_seq_length=512,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
)

# ... training code similar to above
```

## Step 4: Convert to Ollama Format

After fine-tuning, convert to GGUF for Ollama:

```bash
# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Convert to GGUF
python convert.py ../akura-sinhala-final --outtype f16 --outfile akura-sinhala.gguf

# Quantize (optional, for smaller size)
./quantize akura-sinhala.gguf akura-sinhala-q4.gguf q4_k_m
```

Create Ollama model from GGUF:

```dockerfile
# Modelfile
FROM ./akura-sinhala-q4.gguf

PARAMETER temperature 0.3
PARAMETER num_predict 256

SYSTEM """You are an expert Sinhala language teacher..."""
```

```bash
ollama create akura-sinhala -f Modelfile
```

## Step 5: Update Backend Configuration

Update `.env` to use your fine-tuned model:

```env
OLLAMA_MODEL=akura-sinhala
```

## Expected Results After Fine-Tuning

| Metric | Before | After |
|--------|--------|-------|
| Visual Scrambling Accuracy | ~60% | ~95% |
| Phonetic Confusion Accuracy | ~50% | ~90% |
| Grammar Correction Accuracy | ~70% | ~95% |
| Unknown Word Handling | Poor | Good |

## Tips for Better Results

1. **More Data**: Generate 10,000+ examples for better coverage
2. **Diverse Sentences**: Add more vocabulary to `sinhala_vocabulary.py`
3. **Real Data**: If available, add real student writing samples
4. **Balanced Distribution**: Keep the 30/30/20/20 error distribution
5. **Validation Set**: Keep 10% of data for validation

## Troubleshooting

### Model not learning Sinhala characters
- Ensure base model supports Sinhala (Llama 3.2 does)
- Check tokenizer handles Sinhala properly

### Overfitting
- Reduce epochs
- Increase dropout
- Add more diverse training data

### Slow inference
- Use quantized model (q4_k_m)
- Reduce max_tokens
- Use GPU if available
