"""
Akura AI - Text Chunker

Splits Sinhala text into sentence-level chunks for processing.
Supports Sinhala full stop (។) and Latin period (.) as sentence delimiters.
"""

import re
from typing import List

from loguru import logger


def chunk_by_sentences(text: str, max_words_per_chunk: int = 100) -> List[str]:
    """
    Split Sinhala text into sentence-level chunks.
    
    Splits on Sinhala full stop (។) and Latin period (.).
    If a single sentence exceeds max_words_per_chunk, it is further
    split by word count.
    
    Args:
        text: The Sinhala text to chunk
        max_words_per_chunk: Maximum words allowed in a single chunk
            before sub-splitting (default: 100)
    
    Returns:
        List of sentence strings (non-empty, stripped)
    """
    if not text or not text.strip():
        return []
    
    text = text.strip()
    
    # Split on Sinhala full stop (។) or Latin period (.)
    # Keep the delimiter with the sentence for context
    sentences = re.split(r'(?<=[.។])\s*', text)
    
    chunks = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        words = sentence.split()
        
        if len(words) <= max_words_per_chunk:
            chunks.append(sentence)
        else:
            # Sub-split large sentences by word count
            for i in range(0, len(words), max_words_per_chunk):
                sub_chunk = " ".join(words[i:i + max_words_per_chunk])
                if sub_chunk.strip():
                    chunks.append(sub_chunk.strip())
    
    logger.debug(f"Chunked text into {len(chunks)} chunk(s)")
    return chunks
