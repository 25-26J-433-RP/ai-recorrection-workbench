"""
Akura AI - Training Data Generator using Gemini Flash

This script generates training data for fine-tuning the Akura model by
sending dyslexic Sinhala text to Google Gemini Flash for correction.

Usage:
    python scripts/generate_training_data.py --input input_texts.txt --output data/new_training.jsonl
"""

import json
import os
import sys
import time
import argparse
from typing import Optional, Tuple
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai package not installed.")
    print("Install it with: pip install google-generativeai")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# System prompt for Gemini Flash
SYSTEM_PROMPT = """You are an expert Sinhala language tutor specializing in Special Education. Your task is to correct Sinhala text written by a child with dyslexia.

The input text will contain specific types of errors:
1. Visual Confusion: Confusing similar letters (e.g., ට/ර, ක/ග).
2. Phonological Errors: Missing double consonants/Hal kireema (e.g., writing 'බලෙක්' instead of 'බල්ලෙක්').
3. Vowel Modifier (Pilla) Errors: Short vs. Long vowels (e.g., 'ටොමි' instead of 'ටොමී').
4. Phonetic Spelling: Writing exactly as spoken (e.g., 'යනව' instead of 'යනවා').

Here are examples of how you should correct the text:

Input: මකෙ ගෙදට බලෙක් ඉනවා.
Output: මගේ ගෙදර බල්ලෙක් ඉන්නවා.

Input: එයාගෙ මන ටොමි.
Output: එයාගේ නම ටොමී.

Input: මම ඉස්කොලෙට යනවා.
Output: මම ඉස්කෝලෙට යනවා.

Input: අම්මා බත් ඉවුවා.
Output: අම්මා බත් ඉව්වා.

Input: මල් වත ලසනයි.
Output: මල් වත්ත ලස්සනයි.

Input: ගහ කොල හරි ලසනයි.
Output: ගහ කොළ හරි ලස්සනයි.

Input: නන්ගි අඩනවා.
Output: නංගි අඬනවා.

---
Current Task:
Please correct the following text while preserving the original meaning. Do not change the vocabulary, only fix the spelling and grammar.
Return ONLY the corrected text, nothing else - no explanations, no prefixes like "Output:"."""


def setup_gemini(api_key: str, model_name: str = "gemini-2.0-flash") -> genai.GenerativeModel:
    """Initialize Gemini API client."""
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    }
    
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )
    
    return model


def correct_text_with_gemini(model: genai.GenerativeModel, text: str) -> Tuple[bool, str]:
    """
    Send text to Gemini for correction.
    
    Args:
        model: Gemini model instance
        text: Dyslexic text to correct
        
    Returns:
        Tuple of (success, corrected_text or error_message)
    """
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nInput: {text}\nOutput:"
        
        response = model.generate_content(prompt)
        
        if response.text:
            corrected = response.text.strip()
            # Remove any "Output:" prefix if Gemini adds it
            if corrected.lower().startswith("output:"):
                corrected = corrected[7:].strip()
            return True, corrected
        else:
            return False, "Empty response from Gemini"
            
    except Exception as e:
        return False, str(e)


def detect_error_types(original: str, corrected: str) -> list:
    """
    Detect the types of corrections made.
    
    Args:
        original: Original dyslexic text
        corrected: Corrected text
        
    Returns:
        List of error analysis dictionaries
    """
    analysis = []
    
    orig_words = original.split()
    corr_words = corrected.split()
    
    # Simple word-level comparison
    for i, orig_word in enumerate(orig_words):
        if i < len(corr_words):
            corr_word = corr_words[i]
            if orig_word != corr_word:
                error_type = detect_pattern(orig_word, corr_word)
                analysis.append({
                    "word": orig_word,
                    "type": error_type,
                    "suggestion": corr_word
                })
    
    return analysis


def detect_pattern(original: str, corrected: str) -> str:
    """Detect the type of dyslexia pattern."""
    # Check for phonetic L/L confusion (ල/ළ)
    if 'ල' in original and 'ළ' in corrected:
        return "Phonetic (L/L)"
    if 'ළ' in original and 'ල' in corrected:
        return "Phonetic (L/L)"
    
    # Check for phonetic N/N confusion (න/ණ)
    if 'න' in original and 'ණ' in corrected:
        return "Phonetic (N/N)"
    
    # Check for visual reversal (b/d confusion - ඩ/බ)
    if 'ඩ' in original and 'බ' in corrected:
        return "Visual Reversal (B/D)"
    if 'බ' in original and 'ඩ' in corrected:
        return "Visual Reversal (B/D)"
    
    # Check for vowel ending (යනව → යනවා)
    if original.endswith('ව') and corrected.endswith('වා'):
        return "Grammar (Spoken vs Written)"
    
    # Check for phonetic D/DH confusion (ද/ඳ)
    if 'ද' in original and 'ඳ' in corrected:
        return "Phonetic (D/DH)"
    
    # Check for hal kirima missing
    if len(corrected) > len(original):
        return "Phonological (Missing Hal Kireema)"
    
    # Check for visual scrambling (same letters, different order)
    if sorted(original) == sorted(corrected):
        return "Visual Scrambling"
    
    return "Spelling"


def create_training_example(original: str, corrected: str, analysis: list) -> dict:
    """
    Create a training example in the Akura format.
    
    Args:
        original: Original dyslexic text
        corrected: Corrected text
        analysis: Error analysis list
        
    Returns:
        Training example dictionary
    """
    return {
        "messages": [
            {
                "role": "system",
                "content": "You are Akura AI, a Sinhala Dyslexia Correction model."
            },
            {
                "role": "user",
                "content": original
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "correction": corrected,
                    "analysis": analysis
                }, ensure_ascii=False)
            }
        ]
    }


def process_input_file(
    model: genai.GenerativeModel,
    input_path: str,
    output_path: str,
    delay: float = 0.5
) -> Tuple[int, int]:
    """
    Process an input file and generate training data.
    
    Args:
        model: Gemini model instance
        input_path: Path to input file (one text per line)
        output_path: Path to output JSONL file
        delay: Delay between API calls in seconds
        
    Returns:
        Tuple of (successful_count, failed_count)
    """
    successful = 0
    failed = 0
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            text = line.strip()
            if not text:
                continue
            
            print(f"[{line_num}] Processing: {text[:50]}...")
            
            success, result = correct_text_with_gemini(model, text)
            
            if success:
                analysis = detect_error_types(text, result)
                example = create_training_example(text, result, analysis)
                outfile.write(json.dumps(example, ensure_ascii=False) + '\n')
                successful += 1
                print(f"  ✓ Corrected: {result[:50]}...")
            else:
                failed += 1
                print(f"  ✗ Error: {result}")
            
            # Rate limiting
            time.sleep(delay)
    
    return successful, failed


def main():
    parser = argparse.ArgumentParser(
        description="Generate Akura training data using Gemini Flash"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input file with one dyslexic text per line"
    )
    parser.add_argument(
        "--output", "-o",
        default="data/generated_training.jsonl",
        help="Output JSONL file for training data"
    )
    parser.add_argument(
        "--model", "-m",
        default="gemini-2.0-flash",
        help="Gemini model to use"
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=0.5,
        help="Delay between API calls in seconds"
    )
    parser.add_argument(
        "--api-key", "-k",
        default=None,
        help="Gemini API key (or set GEMINI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Gemini API key not provided.")
        print("Set GEMINI_API_KEY environment variable or use --api-key flag.")
        sys.exit(1)
    
    # Check input file exists
    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)
    
    print(f"=== Akura Training Data Generator ===")
    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print(f"Model:  {args.model}")
    print(f"Delay:  {args.delay}s")
    print()
    
    # Initialize Gemini
    print("Initializing Gemini...")
    model = setup_gemini(api_key, args.model)
    
    # Process file
    print("Processing input file...")
    print("-" * 50)
    
    successful, failed = process_input_file(
        model,
        args.input,
        args.output,
        args.delay
    )
    
    print("-" * 50)
    print(f"Complete! Successful: {successful}, Failed: {failed}")
    print(f"Training data saved to: {args.output}")


if __name__ == "__main__":
    main()
