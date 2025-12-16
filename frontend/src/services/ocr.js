/**
 * Akura AI - OCR Service Layer (Thin Client)
 *
 * Handles image upload and text extraction by calling the backend API.
 * All OCR processing is done server-side - no Gemini API calls from frontend.
 */

import { API_CONFIG } from "../constants";

class OcrService {
  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
  }

  /**
   * Get MIME type from file
   */
  getMimeType(file) {
    return file.type || "image/jpeg";
  }

  /**
   * Extract Sinhala text from image by calling backend OCR endpoint
   */
  async extractTextFromImage(imageFile) {
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append("image", imageFile);

      // Call backend OCR endpoint
      const response = await fetch(
        `${this.baseUrl}${API_CONFIG.ENDPOINTS.OCR || "/api/v1/ocr"}`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || errorData.error || `API error: ${response.status}`
        );
      }

      const data = await response.json();

      if (!data.success) {
        return {
          success: false,
          error: data.error || "OCR extraction failed",
          text: "",
        };
      }

      return {
        success: true,
        text: data.text,
        confidence: data.confidence || 0.9,
        source: data.source || "gemini-vision",
      };
    } catch (error) {
      console.error("OCR extraction failed:", error);

      return {
        success: false,
        error: error.message || "Failed to connect to OCR service",
        text: "",
      };
    }
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
   * Check if OCR service is available (always true since backend handles it)
   */
  isConfigured() {
    return true; // Backend handles configuration
  }

  /**
   * Check OCR service status from backend
   */
  async checkStatus() {
    try {
      const response = await fetch(
        `${this.baseUrl}${API_CONFIG.ENDPOINTS.OCR_STATUS || "/api/v1/ocr/status"}`,
        { method: "GET" }
      );

      if (!response.ok) {
        return { configured: false, status: "OCR service unavailable" };
      }

      return await response.json();
    } catch (error) {
      return { configured: false, status: error.message };
    }
  }
}

// Export singleton instance
export const ocrService = new OcrService();
export default ocrService;
