/**
 * Akura AI - Constants and Configuration
 */

// Word states in the correction state machine
export const WORD_STATES = {
  RAW: "raw", // Original text, no error detected
  FLAGGED: "flagged", // AI identified as error (highlighted red)
  CORRECTED: "corrected", // Teacher accepted suggestion (highlighted green)
  IGNORED: "ignored", // Teacher rejected suggestion (underlined grey)
};

// Dyslexia pattern types
export const PATTERN_TYPES = {
  VISUAL_SCRAMBLING: "Visual Sequencing (Scrambled)",
  PHONETIC_CONFUSION: "Phonetic Confusion (Dental/Retroflex)",
  VISUAL_REVERSAL: "Visual Reversal (Shape Confusion)",
  GRAMMAR: "Grammar (Spoken vs Written)",
  UNKNOWN: "Unknown Pattern",
};

// Pattern type to simple key mapping
export const PATTERN_KEYS = {
  "Visual Sequencing (Scrambled)": "visual",
  "Phonetic Confusion (Dental/Retroflex)": "phonetic",
  "Visual Reversal (Shape Confusion)": "visual",
  "Grammar (Spoken vs Written)": "grammar",
  "Unknown Pattern": "unknown",
};

// Pattern colors
export const PATTERN_COLORS = {
  visual: {
    bg: "bg-akura-visual-50",
    border: "border-akura-visual-500",
    text: "text-akura-visual-600",
    icon: "text-akura-visual-500",
  },
  phonetic: {
    bg: "bg-akura-phonetic-50",
    border: "border-akura-phonetic-500",
    text: "text-akura-phonetic-600",
    icon: "text-akura-phonetic-500",
  },
  grammar: {
    bg: "bg-akura-grammar-50",
    border: "border-akura-grammar-500",
    text: "text-akura-grammar-600",
    icon: "text-akura-grammar-500",
  },
  unknown: {
    bg: "bg-gray-50",
    border: "border-gray-400",
    text: "text-gray-600",
    icon: "text-gray-500",
  },
};

// Error Types (simplified)
export const ERROR_TYPES = {
  VISUAL: "visual",
  PHONETIC: "phonetic",
  GRAMMAR: "grammar",
  REVERSAL: "reversal",
  OTHER: "other",
};

// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  TIMEOUT: 30000, // 30 seconds
  ENDPOINTS: {
    ANALYZE: "/api/v1/analyze",
    HEALTH: "/api/v1/health",
    PATTERNS: "/api/v1/patterns",
    OCR: "/api/v1/ocr",
    OCR_STATUS: "/api/v1/ocr/status",
  },
};

// Demo mode fallback data
export const DEMO_DATA = {
  success: true,
  data: [
    {
      word: "ගෙරද",
      type: "error",
      dyslexiaPattern: "Visual Sequencing (Scrambled)",
      suggestion: "ගෙදර",
      explanation:
        "Letters appear scrambled. Common visual sequencing error in dyslexia.",
      confidence: 0.95,
      source: "hybrid",
    },
    {
      word: "යනව",
      type: "error",
      dyslexiaPattern: "Grammar (Spoken vs Written)",
      suggestion: "යනවා",
      explanation:
        "Incomplete verb ending. Colloquial form used instead of written form.",
      confidence: 0.9,
      source: "rule-based",
    },
  ],
  correctedText: "මම ගෙදර යනවා",
  originalText: "මම ගෙරද යනව",
  processingTimeMs: 245.5,
  modelUsed: "demo-mode",
};

// Sample text for demo
export const SAMPLE_TEXTS = [
  "මම ගෙරද යනව",
  "ළමයා පාසලට යනවා",
  "අම්මා කෑම උයනව",
  "බල්ලා දුවනව",
  "මම පොත කියවනව",
];
