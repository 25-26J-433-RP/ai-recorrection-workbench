/**
 * Akura AI - API Service Layer
 * 
 * Handles all communication with the backend API.
 * Includes fallback to demo mode if backend is unavailable.
 */

import { API_CONFIG, DEMO_DATA } from '../constants';

class ApiService {
  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
    this.isOnline = true;
    this.demoMode = false;
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
        { method: 'GET' }
      );
      
      if (response.ok) {
        const data = await response.json();
        this.isOnline = true;
        this.demoMode = false;
        return {
          online: true,
          status: data.status,
          modelStatus: data.modelStatus || data.model_status,
          ollamaConnected: data.ollamaConnected || data.ollama_connected,
        };
      }
      throw new Error('Health check failed');
    } catch (error) {
      console.warn('Backend unavailable, switching to demo mode:', error.message);
      this.isOnline = false;
      this.demoMode = true;
      return {
        online: false,
        status: 'offline',
        modelStatus: 'Demo mode active',
        ollamaConnected: false,
      };
    }
  }

  /**
   * Analyze text for dyslexia errors
   */
  async analyzeText(text, includeCorrectWords = false) {
    // If in demo mode, return demo data
    if (this.demoMode) {
      return this.getDemoResponse(text);
    }

    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}${API_CONFIG.ENDPOINTS.ANALYZE}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text,
            include_correct_words: includeCorrectWords,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      return this.normalizeResponse(data);
    } catch (error) {
      console.warn('Analysis failed, falling back to demo mode:', error.message);
      this.demoMode = true;
      return this.getDemoResponse(text);
    }
  }

  /**
   * Generate demo response based on input text
   */
  getDemoResponse(text) {
    const words = text.split(/\s+/);
    const errors = [];
    const correctedWords = [];

    // Demo corrections dictionary
    const demoCorrections = {
      'ගෙරද': { correct: 'ගෙදර', pattern: 'Visual Sequencing (Scrambled)' },
      'යනව': { correct: 'යනවා', pattern: 'Grammar (Spoken vs Written)' },
      'එනව': { correct: 'එනවා', pattern: 'Grammar (Spoken vs Written)' },
      'කනව': { correct: 'කනවා', pattern: 'Grammar (Spoken vs Written)' },
      'බොනව': { correct: 'බොනවා', pattern: 'Grammar (Spoken vs Written)' },
      'කරනව': { correct: 'කරනවා', pattern: 'Grammar (Spoken vs Written)' },
      'මං': { correct: 'මම', pattern: 'Grammar (Spoken vs Written)' },
      'පාලස': { correct: 'පාසල', pattern: 'Visual Sequencing (Scrambled)' },
    };

    words.forEach((word) => {
      const correction = demoCorrections[word];
      if (correction) {
        errors.push({
          word,
          type: 'error',
          dyslexiaPattern: correction.pattern,
          suggestion: correction.correct,
          explanation: `Demo mode: "${word}" corrected to "${correction.correct}"`,
          confidence: 0.85,
          source: 'demo',
        });
        correctedWords.push(correction.correct);
      } else {
        correctedWords.push(word);
      }
    });

    return {
      success: true,
      data: errors,
      correctedText: correctedWords.join(' '),
      originalText: text,
      processingTimeMs: Math.random() * 100 + 50,
      modelUsed: 'demo-mode',
      isDemoMode: true,
    };
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
      isDemoMode: false,
    };
  }

  /**
   * Get available patterns
   */
  async getPatterns() {
    if (this.demoMode) {
      return {
        success: true,
        patterns: [
          { name: 'Visual Sequencing (Scrambled)', description: 'Letters in wrong order' },
          { name: 'Phonetic Confusion (Dental/Retroflex)', description: 'Similar sounding consonants' },
          { name: 'Grammar (Spoken vs Written)', description: 'Colloquial vs written forms' },
        ],
      };
    }

    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}${API_CONFIG.ENDPOINTS.PATTERNS}`,
        { method: 'GET' }
      );
      return await response.json();
    } catch (error) {
      console.warn('Failed to fetch patterns:', error.message);
      return { success: false, patterns: [] };
    }
  }

  /**
   * Enable demo mode manually
   */
  enableDemoMode() {
    this.demoMode = true;
    this.isOnline = false;
  }

  /**
   * Disable demo mode
   */
  disableDemoMode() {
    this.demoMode = false;
  }

  /**
   * Check if currently in demo mode
   */
  isDemoMode() {
    return this.demoMode;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
