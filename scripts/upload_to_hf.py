import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo, login
from dotenv import load_dotenv

# Add the project root to the python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

def upload_dataset():
    print("🚀 Akura AI - Dataset Uploader to Hugging Face")
    print("==============================================")

    # 1. Get HF Token
    token = os.getenv("HF_TOKEN")
    if not token:
        print("\n⚠️  HF_TOKEN not found in .env file.")
        token = input("🔑 Please enter your Hugging Face Write Token: ").strip()
    
    if not token:
        print("❌ Error: Token is required.")
        return

    try:
        login(token=token)
        print("✅ Successfully logged in to Hugging Face!")
    except Exception as e:
        print(f"❌ Error logging in: {e}")
        return

    # 2. Get Repository Name
    default_repo_name = "akura-dyslexia-sinhala"
    repo_name = input(f"\n📦 Enter Repository Name (default: {default_repo_name}): ").strip() or default_repo_name
    
    # If user didn't provide 'username/', we might need to ask or let HF handle it (it usually defaults to user's namespace)
    # But explicitly asking is safer if they want to put it in an org
    full_repo_id = repo_name
    if "/" not in repo_name:
        username = HfApi().whoami(token=token)["name"]
        full_repo_id = f"{username}/{repo_name}"
        print(f"ℹ️  Targeting repository: {full_repo_id}")

    # 3. Create Repository
    try:
        create_repo(full_repo_id, repo_type="dataset", exist_ok=True, private=False)
        print(f"✅ Repository ensured: https://huggingface.co/datasets/{full_repo_id}")
    except Exception as e:
        print(f"❌ Error creating repository: {e}")
        return

    # 4. Upload File
    dataset_path = project_root / "data" / "akura_dataset.json"
    if not dataset_path.exists():
        print(f"❌ Error: Dataset file not found at {dataset_path}")
        return

    api = HfApi()
    
    print(f"\n📤 Uploading {dataset_path.name}...")
    try:
        api.upload_file(
            path_or_fileobj=dataset_path,
            path_in_repo="akura_dataset.json",
            repo_id=full_repo_id,
            repo_type="dataset",
            commit_message="Upload Akura Sinhala Dyslexia Dataset"
        )
        print("✅ Dataset uploaded successfully!")
    except Exception as e:
        print(f"❌ Error uploading dataset: {e}")
        return

    # 5. Create and Upload Dataset Card (README.md)
    readme_content = f"""---
language:
- si
license: mit
task_categories:
- text-generation
- text-correction
tags:
- dyslexia
- sinhala
- education
- akura-ai
dataset_info:
  features:
  - name: messages
    list:
    - name: role
      dtype: string
    - name: content
      dtype: string
pretty_name: Akura Dyslexia Correction (Sinhala)
size_categories:
- n<1K
---

# 🧠 Akura AI - Sinhala Dyslexia Correction Dataset

This dataset contains examples of Sinhala text with common dyslexic writing errors and their corrections. It is designed for fine-tuning LLMs (like Llama 3) to detect and correct these specific patterns.

## Dataset Structure

The dataset is in **JSONL** format, suitable for chat-based model fine-tuning.

### Example Entry

```json
{{
  "messages": [
    {{"role": "system", "content": "You are Akura AI. Analyze the Sinhala text for dyslexia errors (Phonetic, Visual, Grammar) and provide the correction."}}, 
    {{"role": "user", "content": "මම ගෙරද යනව"}}, 
    {{"role": "assistant", "content": "{{\\"correction\\": \\"මම ගෙදර යනවා.\\", \\"analysis\\": [{{\\"word\\": \\"ගෙරද\\", \\"type\\": \\"Visual Scrambling\\", \\"suggestion\\": \\"ගෙදර\\"}}, {{\\"word\\": \\"යනව\\", \\"type\\": \\"Grammar\\", \\"suggestion\\": \\"යනවා\\"}}]}}"}}
  ]
}}
```

## Error Patterns

The dataset covers 4 main types of errors:

1. **Visual Scrambling**: `ගෙරද` → `ගෙදර`
2. **Phonetic Confusion**: `න` vs `ණ`, `ල` vs `ළ`
3. **Visual Reversal**: `බ` vs `ඩ`
4. **Grammar/Colloquial**: `යනව` → `යනවා`

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{full_repo_id}")
print(dataset['train'][0])
```

## License

MIT License. Part of the SLIIT Research Project (25-26J-433-RP).
"""
    
    # Write temp README
    readme_path = project_root / "data" / "README_HF.md"
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print("\n📝 Uploading Dataset Card...")
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=full_repo_id,
            repo_type="dataset",
            commit_message="Add Dataset Card"
        )
        print("✅ Dataset Card uploaded!")
        
        # Cleanup temp file
        os.remove(readme_path)
        
    except Exception as e:
        print(f"⚠️  Warning: Could not upload README: {e}")

    print("\n🎉 All Done! View your dataset here:")
    print(f"👉 https://huggingface.co/datasets/{full_repo_id}")

if __name__ == "__main__":
    upload_dataset()
