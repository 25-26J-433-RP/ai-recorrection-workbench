/**
 * Akura AI - API Service Layer
 *
 * Handles all communication with the backend API.
 * Uses Ollama for text correction (no Gemini dependency).
 */

import { API_CONFIG } from "../constants";

class ApiService {
  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
    this.isOnline = true;
  }

  /**
   * Make a fetch request with timeout
   */
  async fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * Check if backend is available
   */
  async checkHealth() {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}${API_CONFIG.ENDPOINTS.HEALTH}`,
        { method: "GET" }
      );

      if (response.ok) {
        const data = await response.json();
        this.isOnline = true;
        return {
          online: true,
          status: data.status,
          modelStatus: data.modelStatus || data.model_status,
          ollamaConnected: data.ollamaConnected || data.ollama_connected,
        };
      }
      throw new Error("Health check failed");
    } catch (error) {
      console.error("Backend unavailable:", error.message);
      this.isOnline = false;
      return {
        online: false,
        status: "offline",
        modelStatus: "Backend unavailable",
        ollamaConnected: false,
      };
    }
  }

  /**
   * Analyze text for dyslexia errors
   */
  async analyzeText(text, includeCorrectWords = false) {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}${API_CONFIG.ENDPOINTS.ANALYZE}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text,
            include_correct_words: includeCorrectWords,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      const data = await response.json();
      return this.normalizeResponse(data);
    } catch (error) {
      console.error("Analysis failed:", error.message);
      throw error;
    }
  }

  /**
   * Normalize API response to consistent format
   */
  normalizeResponse(data) {
    return {
      success: data.success,
      data: data.data || [],
      correctedText: data.correctedText || data.corrected_text,
      originalText: data.originalText || data.original_text,
      processingTimeMs: data.processingTimeMs || data.processing_time_ms,
      modelUsed: data.modelUsed || data.model_used,
    };
  }

  /**
   * Get available patterns
   */
  async getPatterns() {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}${API_CONFIG.ENDPOINTS.PATTERNS}`,
        { method: "GET" }
      );
      return await response.json();
    } catch (error) {
      console.warn("Failed to fetch patterns:", error.message);
      return { success: false, patterns: [] };
    }
  }

  /**
   * Save session to database
   */
  async saveSession(sessionData) {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/api/v1/sessions`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(sessionData),
        }
      );

      if (response.ok) {
        return await response.json();
      }
      throw new Error("Failed to save session");
    } catch (error) {
      console.error("Save session failed:", error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get all saved sessions from database
   */
  async getSessions(limit = 50, offset = 0) {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}/api/v1/sessions?limit=${limit}&offset=${offset}`,
        { method: "GET" }
      );

      if (response.ok) {
        return await response.json();
      }
      throw new Error("Failed to get sessions");
    } catch (error) {
      console.error("Get sessions failed:", error.message);
      return { success: false, error: error.message };
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
