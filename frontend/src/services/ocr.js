/**
 * Akura AI - OCR Service Layer
 *
 * Handles image upload and text extraction using Google Gemini Vision API.
 * Optimized for Sinhala text recognition from student essays.
 */

import { API_CONFIG } from "../constants";

class OcrService {
  constructor() {
    this.apiKey = import.meta.env.VITE_GEMINI_API_KEY || "";
    this.apiUrl =
      "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent";
  }

  /**
   * Convert file to base64
   */
  async fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        // Remove data URL prefix to get pure base64
        const base64 = reader.result.split(",")[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  /**
   * Get MIME type from file
   */
  getMimeType(file) {
    return file.type || "image/jpeg";
  }

  /**
   * Extract Sinhala text from image using Google Gemini Vision
   */
  async extractTextFromImage(imageFile) {
    // Check if API key is configured
    if (!this.apiKey) {
      console.warn("Gemini API key not configured, using demo mode");
      return this.getDemoOcrResponse();
    }

    try {
      const base64Image = await this.fileToBase64(imageFile);
      const mimeType = this.getMimeType(imageFile);

      const requestBody = {
        contents: [
          {
            parts: [
              {
                text: `You are an expert OCR system specialized in reading Sinhala (සිංහල) handwritten text from student essays. 

Your task:
1. Carefully examine this image of a student's handwritten essay
2. Extract ALL the Sinhala text exactly as written (including any spelling mistakes or errors)
3. Preserve the original writing - do NOT correct any mistakes
4. If there are multiple lines, preserve line breaks
5. If you cannot read certain characters, use [?] to indicate unclear text

Important: Extract the EXACT text as written by the student, including any dyslexia-related errors like:
- Scrambled letters (e.g., "ගෙරද" instead of "ගෙදර")
- Missing vowel signs
- Phonetic confusions
- Grammar errors

Respond ONLY with the extracted Sinhala text, nothing else. No explanations, no translations, just the raw text.`,
              },
              {
                inline_data: {
                  mime_type: mimeType,
                  data: base64Image,
                },
              },
            ],
          },
        ],
        generationConfig: {
          temperature: 0.1, // Low temperature for accurate extraction
          topK: 1,
          topP: 1,
          maxOutputTokens: 2048,
        },
      };

      const response = await fetch(`${this.apiUrl}?key=${this.apiKey}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error?.message || `API error: ${response.status}`
        );
      }

      const data = await response.json();

      // Extract text from response
      const extractedText =
        data.candidates?.[0]?.content?.parts?.[0]?.text || "";

      if (!extractedText.trim()) {
        throw new Error("No text could be extracted from the image");
      }

      return {
        success: true,
        text: extractedText.trim(),
        confidence: 0.9,
        source: "gemini-vision",
      };
    } catch (error) {
      console.error("OCR extraction failed:", error);

      // Return demo data on error
      if (error.message.includes("API key")) {
        return this.getDemoOcrResponse();
      }

      return {
        success: false,
        error: error.message,
        text: "",
      };
    }
  }

  /**
   * Demo OCR response for testing without API key
   */
  getDemoOcrResponse() {
    // Simulate OCR delay
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          text: "මම ගෙරද යනව\nමං පාලස යනව",
          confidence: 0.85,
          source: "demo-ocr",
          isDemoMode: true,
        });
      }, 1500);
    });
  }

  /**
   * Validate image file
   */
  validateImage(file) {
    const validTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];
    const maxSize = 20 * 1024 * 1024; // 20MB

    if (!validTypes.includes(file.type)) {
      return {
        valid: false,
        error: "Invalid file type. Please upload JPEG, PNG, WebP, or GIF.",
      };
    }

    if (file.size > maxSize) {
      return {
        valid: false,
        error: "File too large. Maximum size is 20MB.",
      };
    }

    return { valid: true };
  }

  /**
   * Check if API key is configured
   */
  isConfigured() {
    return !!this.apiKey;
  }
}

// Export singleton instance
export const ocrService = new OcrService();
export default ocrService;
