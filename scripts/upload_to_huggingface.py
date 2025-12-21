"""
Upload Akura AI Dyslexia Correction Dataset to Hugging Face Hub
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi, login

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# Configuration
DATA_DIR = project_root / "data"
SYNTHETIC_FILE = DATA_DIR / "akura_dataset_synthetic.json"
MAIN_DATASET_FILE = DATA_DIR / "akura_dataset.json"

# Hugging Face Configuration
HF_TOKEN = os.getenv("HF_TOKEN")
REPO_NAME = "akura-sinhala-dyslexia-dataset"  # Will create under your username


def load_jsonl(filepath: Path) -> list:
    """Load JSON Lines file."""
    data = []
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return data


def load_json_array(filepath: Path) -> list:
    """Load JSON array file."""
    data = []
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    return data


def flatten_messages(entry: dict) -> dict:
    """Flatten the messages structure for easier use."""
    messages = entry.get("messages", [])
    
    system_msg = ""
    user_msg = ""
    assistant_msg = ""
    
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "system":
            system_msg = content
        elif role == "user":
            user_msg = content
        elif role == "assistant":
            assistant_msg = content
    
    # Parse assistant response
    correction = ""
    analysis = []
    try:
        if assistant_msg:
            parsed = json.loads(assistant_msg)
            correction = parsed.get("correction", "")
            analysis = parsed.get("analysis", [])
    except json.JSONDecodeError:
        correction = assistant_msg
    
    return {
        "system_prompt": system_msg,
        "input_text": user_msg,
        "corrected_text": correction,
        "analysis": json.dumps(analysis, ensure_ascii=False) if analysis else "[]",
        "raw_assistant_response": assistant_msg,
        "messages": json.dumps(messages, ensure_ascii=False)
    }


def main():
    print("🚀 Akura AI Dataset - Hugging Face Uploader")
    print("=" * 50)
    
    # Check token
    if not HF_TOKEN:
        print("❌ HF_TOKEN not found in .env file")
        return
    
    print(f"✅ Using HF Token: {HF_TOKEN[:10]}...")
    
    # Login to Hugging Face
    print("\n📡 Logging in to Hugging Face...")
    login(token=HF_TOKEN)
    
    # Load datasets
    print("\n📂 Loading datasets...")
    
    # Load synthetic data (JSONL format)
    synthetic_data = load_jsonl(SYNTHETIC_FILE)
    print(f"   - Synthetic data: {len(synthetic_data)} samples")
    
    # Load main dataset (JSON array format)
    main_data = load_json_array(MAIN_DATASET_FILE)
    print(f"   - Main dataset: {len(main_data)} samples")
    
    # Combine datasets
    all_data = main_data + synthetic_data
    print(f"   - Total combined: {len(all_data)} samples")
    
    # Remove duplicates based on user input
    seen_inputs = set()
    unique_data = []
    for entry in all_data:
        messages = entry.get("messages", [])
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        if user_msg and user_msg not in seen_inputs:
            seen_inputs.add(user_msg)
            unique_data.append(entry)
    
    print(f"   - After deduplication: {len(unique_data)} samples")
    
    # Flatten for easier use
    print("\n🔄 Processing data...")
    processed_data = [flatten_messages(entry) for entry in unique_data]
    
    # Create Hugging Face Dataset
    print("\n📦 Creating Hugging Face Dataset...")
    dataset = Dataset.from_list(processed_data)
    
    # Split into train/test
    split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
    dataset_dict = DatasetDict({
        "train": split_dataset["train"],
        "test": split_dataset["test"]
    })
    
    print(f"   - Train samples: {len(dataset_dict['train'])}")
    print(f"   - Test samples: {len(dataset_dict['test'])}")
    
    # Get username
    api = HfApi()
    user_info = api.whoami()
    username = user_info["name"]
    full_repo_name = f"{username}/{REPO_NAME}"
    
    print(f"\n☁️  Uploading to: {full_repo_name}")
    
    # Push to Hub
    dataset_dict.push_to_hub(
        full_repo_name,
        private=False,  # Make it public
        token=HF_TOKEN
    )
    
    print(f"\n🎉 Success! Dataset uploaded to: https://huggingface.co/datasets/{full_repo_name}")
    
    # Print sample
    print("\n📋 Sample entry:")
    sample = processed_data[0]
    print(f"   Input: {sample['input_text']}")
    print(f"   Corrected: {sample['corrected_text']}")
    print(f"   Analysis: {sample['analysis'][:100]}...")


if __name__ == "__main__":
    main()
