"""
Akura AI - Sinhala Character Mappings

This module contains all the character mappings and dictionaries
used for dyslexia pattern detection in Sinhala text.
"""

from typing import Dict, List, Set, Tuple


# =============================================================================
# PHONETIC CONFUSION MAPPINGS
# =============================================================================

# Dental vs Retroflex consonant pairs (commonly confused by dyslexic students)
DENTAL_RETROFLEX_PAIRS: List[Tuple[str, str]] = [
    ("න", "ණ"),  # na (dental) vs Na (retroflex)
    ("ල", "ළ"),  # la (dental) vs La (retroflex)
    ("ද", "ඩ"),  # da (dental) vs Da (retroflex)
    ("ත", "ට"),  # ta (dental) vs Ta (retroflex)
]

# Create bidirectional mapping for quick lookup
PHONETIC_CONFUSION_MAP: Dict[str, str] = {}
for dental, retroflex in DENTAL_RETROFLEX_PAIRS:
    PHONETIC_CONFUSION_MAP[dental] = retroflex
    PHONETIC_CONFUSION_MAP[retroflex] = dental

# All phonetically confusable characters
PHONETIC_CONFUSABLE_CHARS: Set[str] = set(PHONETIC_CONFUSION_MAP.keys())


# =============================================================================
# VISUAL CONFUSION MAPPINGS
# =============================================================================

# Shape-based visual confusion pairs (similar looking characters)
VISUAL_CONFUSION_PAIRS: List[Tuple[str, str]] = [
    ("බ", "ඩ"),  # ba vs Da - similar shapes
    ("ප", "ඵ"),  # pa vs pha - similar base
    ("ක", "ඛ"),  # ka vs kha - similar base
    ("ග", "ඝ"),  # ga vs gha - similar base
    ("ච", "ඡ"),  # ca vs cha - similar base
    ("ජ", "ඣ"),  # ja vs jha - similar base
    ("ට", "ඨ"),  # Ta vs Tha - similar base
    ("ඩ", "ඪ"),  # Da vs Dha - similar base
    ("ත", "ථ"),  # ta vs tha - similar base
    ("ද", "ධ"),  # da vs dha - similar base
    ("ප", "ඵ"),  # pa vs pha - similar base
    ("බ", "භ"),  # ba vs bha - similar base
    ("ම", "භ"),  # ma vs bha - can look similar
    ("ය", "ර"),  # ya vs ra - cursive similarity
    ("ව", "හ"),  # va vs ha - can look similar
]

# Create bidirectional mapping for visual confusion
VISUAL_CONFUSION_MAP: Dict[str, str] = {}
for char1, char2 in VISUAL_CONFUSION_PAIRS:
    VISUAL_CONFUSION_MAP[char1] = char2
    VISUAL_CONFUSION_MAP[char2] = char1

# All visually confusable characters
VISUAL_CONFUSABLE_CHARS: Set[str] = set(VISUAL_CONFUSION_MAP.keys())


# =============================================================================
# COMMON SINHALA WORD CORRECTIONS
# =============================================================================

# Dictionary of commonly misspelled words with their corrections
# Format: {incorrect: correct}
COMMON_CORRECTIONS: Dict[str, str] = {
    # Visual Scrambling Examples
    "ගෙරද": "ගෙදර",
    "වරදා": "වාරදා",
    "පතාර": "පාතර",
    "මකුළුවා": "මකුළුවා",
    
    # Grammar/Colloquial to Written
    "යනව": "යනවා",
    "එනව": "එනවා",
    "කනව": "කනවා",
    "බොනව": "බොනවා",
    "කරනව": "කරනවා",
    "දකිනව": "දකිනවා",
    "ලියනව": "ලියනවා",
    "කියනව": "කියනවා",
    "ගන්නව": "ගන්නවා",
    "දෙනව": "දෙනවා",
    "බලනව": "බලනවා",
    "හිතනව": "හිතනවා",
    "ඉන්නව": "ඉන්නවා",
    "යනව්": "යනවා",
    "එනව්": "එනවා",
    
    # Phonetic Confusion Examples (ණ/න)
    "පාසැල": "පාසල",
    "ගුරුවරයා": "ගුරුවරයා",
    "විදුහල": "විදුහල",
    
    # Common spelling errors
    "මං": "මම",
    "උඹ": "ඔබ",
    "එයා": "ඔහු",
    "ඕනා": "ඕනෑ",
    "ඕන": "ඕනෑ",
    "ඉතින්": "ඉතිං",
}


# =============================================================================
# VOWEL SIGN MAPPINGS
# =============================================================================

# Sinhala vowel signs (pili) that attach to consonants
VOWEL_SIGNS: Dict[str, str] = {
    "ා": "aa",   # aela-pilla
    "ැ": "ae",   # aeda-pilla
    "ෑ": "aee",  # diga aeda-pilla
    "ි": "i",    # is-pilla
    "ී": "ii",   # diga is-pilla
    "ු": "u",    # paa-pilla
    "ූ": "uu",   # diga paa-pilla
    "ෙ": "e",    # kombuva
    "ේ": "ee",   # kombu deka
    "ො": "o",    # kombuva + aela-pilla
    "ෝ": "oo",   # kombu deka + aela-pilla
    "ෛ": "ai",   # gayanukitta
    "ෞ": "au",   # gayanukitta + aela-pilla
    "ං": "ng",   # anusvara (binduva)
    "ඃ": "h",    # visarga
    "්": "",     # hal-kirima (virama)
}


# =============================================================================
# BASE CONSONANTS
# =============================================================================

# All Sinhala base consonants
SINHALA_CONSONANTS: List[str] = [
    "ක", "ඛ", "ග", "ඝ", "ඞ",  # velar
    "ච", "ඡ", "ජ", "ඣ", "ඤ",  # palatal
    "ට", "ඨ", "ඩ", "ඪ", "ණ",  # retroflex
    "ත", "ථ", "ද", "ධ", "න",  # dental
    "ප", "ඵ", "බ", "භ", "ම",  # labial
    "ය", "ර", "ල", "ව",       # semi-vowels
    "ශ", "ෂ", "ස", "හ",       # sibilants
    "ළ", "ෆ",                 # additional
]


# =============================================================================
# VOWELS
# =============================================================================

# Sinhala independent vowels
SINHALA_VOWELS: List[str] = [
    "අ", "ආ", "ඇ", "ඈ",
    "ඉ", "ඊ", "උ", "ඌ",
    "ඍ", "ඎ", "ඏ", "ඐ",
    "එ", "ඒ", "ඓ", "ඔ", "ඕ", "ඖ",
]


# =============================================================================
# ERROR PATTERN EXPLANATIONS
# =============================================================================

PATTERN_EXPLANATIONS: Dict[str, str] = {
    "Visual Sequencing (Scrambled)": "Letters appear scrambled or in wrong order. Common visual sequencing error in dyslexia.",
    "Phonetic Confusion (Dental/Retroflex)": "Confusion between similar sounding consonants (dental vs retroflex). Example: න/ණ or ල/ළ.",
    "Visual Reversal (Shape Confusion)": "Confusion between visually similar characters. Common in dyslexia due to shape recognition difficulties.",
    "Grammar (Spoken vs Written)": "Colloquial/spoken form used instead of formal written form. Common in informal writing.",
    "Unknown Pattern": "Error pattern could not be definitively categorized.",
}


def get_explanation(pattern: str) -> str:
    """Get the explanation for a given error pattern."""
    return PATTERN_EXPLANATIONS.get(pattern, PATTERN_EXPLANATIONS["Unknown Pattern"])


def is_sinhala_char(char: str) -> bool:
    """Check if a character is a Sinhala character."""
    # Sinhala Unicode range: 0D80-0DFF
    if len(char) != 1:
        return False
    code = ord(char)
    return 0x0D80 <= code <= 0x0DFF


def get_sinhala_chars(text: str) -> List[str]:
    """Extract only Sinhala characters from text."""
    return [c for c in text if is_sinhala_char(c)]
