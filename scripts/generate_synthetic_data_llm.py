import os
import json
import random
import time
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv

# LangChain Imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# --- Configuration ---
DATA_FILE = project_root / "data" / "akura_dataset.json"
OUTPUT_FILE = project_root / "data" / "akura_dataset_synthetic.json"
BATCH_SIZE = 10  # Generate this many conversation turns per request
TOTAL_SAMPLES = 50   # Total samples to generate (Demo limit)

def load_existing_data(filepath: Path) -> List[Dict]:
    """Load existing dataset to use as few-shot examples."""
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

def get_llm():
    """Initialize LLM based on available API keys."""
    if os.getenv("OPENAI_API_KEY"):
        print("🤖 Using OpenAI (GPT-4o/Turbo)...")
        return ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7)
    elif os.getenv("GOOGLE_API_KEY"):
        print("🤖 Using Google Gemini (2.0 Flash)...")
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
    else:
        raise ValueError("❌ No API Key found! Please set OPENAI_API_KEY or GOOGLE_API_KEY in .env")

def create_prompt(examples: List[Dict]) -> ChatPromptTemplate:
    """Create the prompt with few-shot examples."""
    
    # Select a few random examples for context
    few_shot_samples = random.sample(examples, min(len(examples), 5))
    
    few_shot_text = ""
    for sample in few_shot_samples:
        user_msg = next((m["content"] for m in sample["messages"] if m["role"] == "user"), "")
        ai_msg = next((m["content"] for m in sample["messages"] if m["role"] == "assistant"), "")
        few_shot_text += f"USER: {user_msg}\nASSISTANT: {ai_msg}\n---\n"
    
    # Escape curly braces in few_shot_text because LangChain treats them as variables
    few_shot_text = few_shot_text.replace("{", "{{").replace("}", "}}")

    system_instruction = """You are an expert data generator for the 'Akura AI' project. 
Your task is to generate synthetic training data for a Sinhala Dyslexia Correction model.

## Dyslexia Patterns to Simulate:
1. **Visual Scrambling**: Letters in wrong order (e.g., ගෙරද -> ගෙදර).
2. **Phonetic Confusion**: Mixing up similar sounds (e.g., න/ණ, ල/ළ, බ/ඩ).
3. **Visual Reversal**: Confusing shapes (e.g., බ/ඩ).
4. **Grammar Examples**: Spoken vs Written confusion (e.g., යනව -> යනවා).

## Output Format:
You must output a VALID JSON List of Objects.
Do NOT output markdown code blocks. Just the raw JSON.

## Example Output Structure:
[
  {{
    "messages": [
      {{"role": "system", "content": "You are Akura AI..."}},
      {{"role": "user", "content": "SAMPLE_USER_TEXT"}},
      {{"role": "assistant", "content": "{{\\"correction\\": \\"CORRECT_TEXT\\", \\"analysis\\": [...]}}"}}
    ]
  }},
  ...
]

IMPORTANT: The 'content' of the assistant message MUST be a JSON stringified object (containing 'correction' and 'analysis'). The top-level structure is a normal JSON object.
"""
    
    return ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("system", f"Here are some examples of the data:\n{few_shot_text}"),
        ("user", "Generate {batch_size} NEW, UNIQUE synthetic examples. Return ONLY the JSON list.")
    ])

def main():
    print("🚀 Akura AI - Synthetic Data Generator")
    print("=======================================")

    # 1. Load Data
    print(f"📂 Loading existing data from {DATA_FILE.name}...")
    existing_data = load_existing_data(DATA_FILE)
    print(f"✅ Loaded {len(existing_data)} examples.")

    # 2. Setup LLM
    try:
        llm = get_llm()
    except ValueError as e:
        print(e)
        return

    # 3. Generate Loop
    generated_count = 0
    generated_data = []

    prompt = create_prompt(existing_data)
    chain = prompt | llm | StrOutputParser()

    print(f"\n🔄 Generating {TOTAL_SAMPLES} samples in batches of {BATCH_SIZE}...")
    
    while generated_count < TOTAL_SAMPLES:
        print(f"   - Batch {generated_count // BATCH_SIZE + 1}...")
        try:
            result = chain.invoke({"batch_size": BATCH_SIZE})
            
            # Clean up result if it contains markdown
            result = result.replace("```json", "").replace("```", "").strip()
            
            # Parse the list
            batch_list = json.loads(result)
            
            generated_data.extend(batch_list)
            generated_count += len(batch_list)
            print(f"     ✅ +{len(batch_list)} samples generated.")

        except Exception as e:
            print(f"     ❌ Error in batch: {e}")
            time.sleep(2)
            continue

    # 4. Save
    print(f"\n💾 Saving to {OUTPUT_FILE.name}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for entry in generated_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print("🎉 Done! Synthetic dataset created.")

if __name__ == "__main__":
    main()
