"""
Akura AI - Synthetic Training Data Generator

This script generates synthetic training data for fine-tuning the model
on Sinhala dyslexia correction. It uses the "Targeted Chaos" strategy:

1. Generate correct Sinhala sentences
2. Inject dyslexia-specific errors (30% visual, 30% phonetic, 20% grammar, 20% control)
3. Create input-output pairs for supervised fine-tuning

Usage:
    python generate_training_data.py --output training_data.jsonl --count 5000
"""

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple


# =============================================================================
# SINHALA VOCABULARY DATABASE
# =============================================================================

# Common subjects (pronouns)
SUBJECTS = [
    "මම", "අපි", "ඔහු", "ඇය", "ඔවුන්", "ඔබ", "ඔබලා",
    "ළමයා", "ගුරුවරයා", "අම්මා", "තාත්තා", "අක්කා", "මල්ලි",
    "නංගි", "අයියා", "සිසුවා", "ගොවියා", "වෛද්‍යවරයා",
]

# Common objects
OBJECTS = [
    "පොත", "පැන්සල", "බෝලය", "ගෙදර", "පාසල", "කෑම",
    "වතුර", "බත්", "පාන්", "අඹ", "කෙසෙල්", "මල",
    "ගස", "කුරුල්ලා", "බල්ලා", "පූසා", "මාළුවා",
    "රථය", "බස්රථය", "දුම්රිය", "යතුරුපැදිය",
    "පරිගණකය", "දුරකථනය", "රූපවාහිනිය",
]

# Common verbs (base form - we'll add endings)
VERBS = [
    ("යනවා", "යනව", "යයි"),      # go
    ("එනවා", "එනව", "එයි"),      # come
    ("කනවා", "කනව", "කයි"),      # eat
    ("බොනවා", "බොනව", "බොයි"),    # drink
    ("ලියනවා", "ලියනව", "ලියයි"),  # write
    ("කියවනවා", "කියවනව", "කියයි"), # read
    ("බලනවා", "බලනව", "බලයි"),    # look/watch
    ("අරිනවා", "අරිනව", "අරියි"),  # open
    ("වහනවා", "වහනව", "වහයි"),    # close
    ("දුවනවා", "දුවනව", "දුවයි"),  # run
    ("ඇවිදිනවා", "ඇවිදිනව", "ඇවිදියි"), # walk
    ("නිදනවා", "නිදනව", "නිදයි"),  # sleep
    ("නැගිටිනවා", "නැගිටිනව", "නැගිටියි"), # wake up
    ("සෝදනවා", "සෝදනව", "සෝදයි"),  # wash
    ("උයනවා", "උයනව", "උයයි"),    # cook
    ("ගනිනවා", "ගනිනව", "ගනියි"),  # buy/take
    ("දෙනවා", "දෙනව", "දෙයි"),    # give
    ("කරනවා", "කරනව", "කරයි"),    # do
    ("සෙල්ලම් කරනවා", "සෙල්ලම් කරනව", "සෙල්ලම් කරයි"), # play
]

# Locations
LOCATIONS = [
    "ගෙදර", "පාසලට", "වෙළඳසැලට", "ගමට", "නගරයට",
    "උද්‍යානයට", "පන්සලට", "රෝහලට", "කාර්යාලයට",
]

# Time expressions
TIME_EXPRESSIONS = [
    "අද", "හෙට", "ඊයේ", "දැන්", "පසුව", "උදේ", "හවස",
    "රාත්‍රියේ", "සෑම දිනම", "සතියකට වරක්",
]

# =============================================================================
# DYSLEXIA ERROR PATTERNS
# =============================================================================

# Dental vs Retroflex pairs for phonetic confusion
PHONETIC_PAIRS = [
    ("න", "ණ"),
    ("ල", "ළ"),
    ("ද", "ඩ"),
    ("ත", "ට"),
]

# Visual confusion pairs (similar looking characters)
VISUAL_PAIRS = [
    ("බ", "ඩ"),
    ("ප", "ඵ"),
    ("ක", "ඛ"),
    ("ග", "ඝ"),
    ("ය", "ර"),
]


class DyslexiaErrorInjector:
    """Injects realistic dyslexia errors into Sinhala text."""
    
    def __init__(self):
        self.phonetic_pairs = PHONETIC_PAIRS
        self.visual_pairs = VISUAL_PAIRS
    
    def inject_visual_scrambling(self, word: str) -> Tuple[str, bool]:
        """
        Scramble letters in a word (visual sequencing error).
        
        Returns: (scrambled_word, was_modified)
        """
        if len(word) < 3:
            return word, False
        
        chars = list(word)
        
        # Find positions that can be swapped (avoid vowel signs)
        swappable = []
        for i, char in enumerate(chars):
            # Check if it's a base consonant (not a vowel sign)
            if '\u0D80' <= char <= '\u0DFF' and char not in 'ාැෑිීුූෙේොෝෛෞංඃ්':
                swappable.append(i)
        
        if len(swappable) < 2:
            return word, False
        
        # Swap two adjacent swappable positions
        idx = random.choice(range(len(swappable) - 1))
        i, j = swappable[idx], swappable[idx + 1]
        chars[i], chars[j] = chars[j], chars[i]
        
        result = ''.join(chars)
        return result, result != word
    
    def inject_phonetic_confusion(self, word: str) -> Tuple[str, bool]:
        """
        Swap dental/retroflex consonants (phonetic confusion).
        
        Returns: (confused_word, was_modified)
        """
        result = word
        modified = False
        
        for dental, retroflex in self.phonetic_pairs:
            if dental in result and random.random() < 0.5:
                result = result.replace(dental, retroflex, 1)
                modified = True
                break
            elif retroflex in result and random.random() < 0.5:
                result = result.replace(retroflex, dental, 1)
                modified = True
                break
        
        return result, modified
    
    def inject_visual_reversal(self, word: str) -> Tuple[str, bool]:
        """
        Swap visually similar characters (shape confusion).
        
        Returns: (confused_word, was_modified)
        """
        result = word
        modified = False
        
        for char1, char2 in self.visual_pairs:
            if char1 in result and random.random() < 0.5:
                result = result.replace(char1, char2, 1)
                modified = True
                break
            elif char2 in result and random.random() < 0.5:
                result = result.replace(char2, char1, 1)
                modified = True
                break
        
        return result, modified
    
    def inject_grammar_error(self, word: str) -> Tuple[str, bool]:
        """
        Convert written form to colloquial (grammar error).
        
        Returns: (colloquial_word, was_modified)
        """
        # Remove final ā vowel sign from verbs
        if word.endswith("වා"):
            return word[:-1], True
        if word.endswith("යි"):
            return word[:-1], True
        
        return word, False


class SentenceGenerator:
    """Generates Sinhala sentences with various structures."""
    
    def __init__(self):
        self.subjects = SUBJECTS
        self.objects = OBJECTS
        self.verbs = VERBS
        self.locations = LOCATIONS
        self.times = TIME_EXPRESSIONS
    
    def generate_simple_sentence(self) -> str:
        """Generate: Subject + Verb"""
        subject = random.choice(self.subjects)
        verb = random.choice(self.verbs)[0]  # Written form
        return f"{subject} {verb}"
    
    def generate_sov_sentence(self) -> str:
        """Generate: Subject + Object + Verb"""
        subject = random.choice(self.subjects)
        obj = random.choice(self.objects)
        verb = random.choice(self.verbs)[0]
        return f"{subject} {obj} {verb}"
    
    def generate_location_sentence(self) -> str:
        """Generate: Subject + Location + Verb"""
        subject = random.choice(self.subjects)
        location = random.choice(self.locations)
        # Use motion verbs
        verb = random.choice([v[0] for v in self.verbs[:2]])  # යනවා, එනවා
        return f"{subject} {location} {verb}"
    
    def generate_time_sentence(self) -> str:
        """Generate: Time + Subject + Verb"""
        time = random.choice(self.times)
        subject = random.choice(self.subjects)
        verb = random.choice(self.verbs)[0]
        return f"{time} {subject} {verb}"
    
    def generate_complex_sentence(self) -> str:
        """Generate: Time + Subject + Object + Location + Verb"""
        time = random.choice(self.times)
        subject = random.choice(self.subjects)
        obj = random.choice(self.objects)
        location = random.choice(self.locations)
        verb = random.choice(self.verbs)[0]
        return f"{time} {subject} {obj} {location} {verb}"
    
    def generate_random_sentence(self) -> str:
        """Generate a random sentence structure."""
        generators = [
            self.generate_simple_sentence,
            self.generate_sov_sentence,
            self.generate_location_sentence,
            self.generate_time_sentence,
            self.generate_complex_sentence,
        ]
        return random.choice(generators)()


class TrainingDataGenerator:
    """
    Generates training data using the "Targeted Chaos" strategy.
    
    Distribution:
    - 30% Visual Scrambling
    - 30% Phonetic Confusion  
    - 20% Grammar (Colloquialisms)
    - 20% Control Group (No errors)
    """
    
    def __init__(self):
        self.sentence_gen = SentenceGenerator()
        self.error_injector = DyslexiaErrorInjector()
        
        # Error type distribution
        self.error_distribution = [
            ("visual_scrambling", 0.30),
            ("phonetic_confusion", 0.30),
            ("grammar", 0.20),
            ("control", 0.20),
        ]
    
    def _select_error_type(self) -> str:
        """Select error type based on distribution."""
        r = random.random()
        cumulative = 0
        for error_type, prob in self.error_distribution:
            cumulative += prob
            if r <= cumulative:
                return error_type
        return "control"
    
    def _inject_error(
        self, 
        sentence: str, 
        error_type: str
    ) -> Tuple[str, str, List[Dict]]:
        """
        Inject errors into a sentence.
        
        Returns: (error_sentence, correct_sentence, error_details)
        """
        words = sentence.split()
        error_words = []
        error_details = []
        
        for word in words:
            if error_type == "control":
                error_words.append(word)
                continue
            
            modified = False
            error_word = word
            
            if error_type == "visual_scrambling":
                error_word, modified = self.error_injector.inject_visual_scrambling(word)
            elif error_type == "phonetic_confusion":
                error_word, modified = self.error_injector.inject_phonetic_confusion(word)
            elif error_type == "grammar":
                error_word, modified = self.error_injector.inject_grammar_error(word)
            
            if modified:
                error_details.append({
                    "original": word,
                    "error": error_word,
                    "type": error_type
                })
            
            error_words.append(error_word)
        
        return " ".join(error_words), sentence, error_details
    
    def generate_training_example(self) -> Dict:
        """Generate a single training example."""
        # Generate correct sentence
        correct_sentence = self.sentence_gen.generate_random_sentence()
        
        # Select and inject error
        error_type = self._select_error_type()
        error_sentence, _, error_details = self._inject_error(
            correct_sentence, error_type
        )
        
        return {
            "input": error_sentence,
            "output": correct_sentence,
            "error_type": error_type,
            "errors": error_details,
            "has_error": error_sentence != correct_sentence
        }
    
    def generate_dataset(self, count: int) -> List[Dict]:
        """Generate a dataset of training examples."""
        dataset = []
        
        for i in range(count):
            example = self.generate_training_example()
            dataset.append(example)
            
            if (i + 1) % 500 == 0:
                print(f"Generated {i + 1}/{count} examples...")
        
        return dataset
    
    def generate_instruction_format(self, example: Dict) -> Dict:
        """
        Convert to instruction-following format for fine-tuning.
        
        Format suitable for Llama/Alpaca style fine-tuning.
        """
        instruction = "Correct the following Sinhala text for dyslexic writing errors. Output only the corrected text."
        
        return {
            "instruction": instruction,
            "input": example["input"],
            "output": example["output"],
            "metadata": {
                "error_type": example["error_type"],
                "errors": example["errors"]
            }
        }
    
    def generate_chat_format(self, example: Dict) -> Dict:
        """
        Convert to chat format for conversational fine-tuning.
        """
        system_prompt = """You are an expert Sinhala language teacher specializing in helping dyslexic students. 
Your task is to correct Sinhala text that may contain dyslexic writing errors including visual scrambling, 
phonetic confusion (dental/retroflex swaps), and grammar issues. Output only the corrected text."""
        
        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Correct this: {example['input']}"},
                {"role": "assistant", "content": example["output"]}
            ],
            "metadata": {
                "error_type": example["error_type"],
                "errors": example["errors"]
            }
        }


def save_jsonl(data: List[Dict], filepath: str):
    """Save data to JSONL format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def save_json(data: List[Dict], filepath: str):
    """Save data to JSON format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic training data for Sinhala dyslexia correction"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="training_data.jsonl",
        help="Output file path"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=5000,
        help="Number of training examples to generate"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["jsonl", "json", "instruction", "chat"],
        default="instruction",
        help="Output format"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    print(f"🚀 Generating {args.count} training examples...")
    print(f"📁 Output: {args.output}")
    print(f"📋 Format: {args.format}")
    print()
    
    # Generate data
    generator = TrainingDataGenerator()
    raw_data = generator.generate_dataset(args.count)
    
    # Convert to specified format
    if args.format == "instruction":
        data = [generator.generate_instruction_format(ex) for ex in raw_data]
    elif args.format == "chat":
        data = [generator.generate_chat_format(ex) for ex in raw_data]
    else:
        data = raw_data
    
    # Save
    if args.format in ["jsonl", "instruction"]:
        save_jsonl(data, args.output)
    else:
        save_json(data, args.output)
    
    # Print statistics
    print()
    print("📊 Statistics:")
    error_counts = {}
    for ex in raw_data:
        et = ex["error_type"]
        error_counts[et] = error_counts.get(et, 0) + 1
    
    for error_type, count in sorted(error_counts.items()):
        percentage = (count / len(raw_data)) * 100
        print(f"   {error_type}: {count} ({percentage:.1f}%)")
    
    print()
    print(f"✅ Successfully generated {len(data)} training examples!")
    print()
    print("📝 Sample output:")
    sample = data[0]
    if args.format == "instruction":
        print(f"   Input: {sample['input']}")
        print(f"   Output: {sample['output']}")
    elif args.format == "chat":
        print(f"   User: {sample['messages'][1]['content']}")
        print(f"   Assistant: {sample['messages'][2]['content']}")
    else:
        print(f"   Input: {sample['input']}")
        print(f"   Output: {sample['output']}")


if __name__ == "__main__":
    main()
