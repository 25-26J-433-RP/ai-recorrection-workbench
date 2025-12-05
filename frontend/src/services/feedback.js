/**
 * Akura AI - Feedback Service
 *
 * Collects and stores teacher correction decisions for future model fine-tuning.
 * Saves data locally and can sync to backend when available.
 */

import { API_CONFIG } from "../constants";

// Local storage key for feedback data
const STORAGE_KEY = "akura_feedback_data";
const STORAGE_SESSIONS_KEY = "akura_feedback_sessions";

class FeedbackService {
  constructor() {
    this.currentSession = null;
    this.feedbackQueue = [];
    this.syncInterval = null;
  }

  /**
   * Initialize a new feedback session when analysis starts
   */
  startSession(originalText, analysisResult) {
    this.currentSession = {
      sessionId: this.generateSessionId(),
      timestamp: new Date().toISOString(),
      originalText,
      modelUsed: analysisResult.modelUsed || "unknown",
      isDemoMode: analysisResult.isDemoMode || false,
      corrections: [],
      metadata: {
        totalErrors: analysisResult.data?.length || 0,
        userAgent: navigator.userAgent,
        screenSize: `${window.innerWidth}x${window.innerHeight}`,
      },
    };

    // Store initial detected errors
    if (analysisResult.data) {
      analysisResult.data.forEach((error) => {
        this.currentSession.corrections.push({
          id: this.generateId(),
          originalWord: error.word,
          suggestedCorrection: error.suggestion,
          pattern: error.dyslexiaPattern || error.pattern,
          confidence: error.confidence,
          source: error.source,
          action: null, // Will be set when teacher makes decision
          finalWord: null,
          actionTimestamp: null,
        });
      });
    }

    return this.currentSession.sessionId;
  }

  /**
   * Record teacher's correction decision
   */
  recordAction(tokenId, action, originalWord, suggestedWord, finalWord, pattern) {
    if (!this.currentSession) {
      console.warn("No active session to record feedback");
      return;
    }

    // Find existing correction or create new one
    let correction = this.currentSession.corrections.find(
      (c) => c.originalWord === originalWord && c.action === null
    );

    if (correction) {
      // Update existing correction
      correction.action = action; // 'accept', 'reject', 'edit'
      correction.finalWord = finalWord;
      correction.actionTimestamp = new Date().toISOString();
      if (action === "edit") {
        correction.teacherCorrection = finalWord;
      }
    } else {
      // Add new correction record
      this.currentSession.corrections.push({
        id: this.generateId(),
        originalWord,
        suggestedCorrection: suggestedWord,
        pattern: pattern || "Unknown",
        action,
        finalWord,
        actionTimestamp: new Date().toISOString(),
        teacherCorrection: action === "edit" ? finalWord : null,
      });
    }

    // Auto-save after each action
    this.saveSession();

    // Add to sync queue
    this.queueForSync({
      type: "correction_action",
      sessionId: this.currentSession.sessionId,
      data: {
        originalWord,
        suggestedWord,
        finalWord,
        action,
        pattern,
        timestamp: new Date().toISOString(),
      },
    });
  }

  /**
   * End current session and save final state
   */
  endSession(finalText) {
    if (!this.currentSession) return null;

    this.currentSession.finalText = finalText;
    this.currentSession.completedAt = new Date().toISOString();

    // Calculate session statistics
    const corrections = this.currentSession.corrections;
    this.currentSession.statistics = {
      totalDetected: corrections.length,
      accepted: corrections.filter((c) => c.action === "accept").length,
      rejected: corrections.filter((c) => c.action === "reject").length,
      edited: corrections.filter((c) => c.action === "edit").length,
      pending: corrections.filter((c) => c.action === null).length,
    };

    // Save to local storage
    this.saveSession();
    this.saveToSessionHistory();

    const session = this.currentSession;
    this.currentSession = null;

    return session;
  }

  /**
   * Save current session to local storage
   */
  saveSession() {
    if (!this.currentSession) return;

    try {
      localStorage.setItem(
        `${STORAGE_KEY}_current`,
        JSON.stringify(this.currentSession)
      );
    } catch (error) {
      console.error("Failed to save session:", error);
    }
  }

  /**
   * Save completed session to history
   */
  saveToSessionHistory() {
    if (!this.currentSession) return;

    try {
      const history = this.getSessionHistory();
      history.push(this.currentSession);

      // Keep only last 100 sessions to avoid storage limits
      if (history.length > 100) {
        history.splice(0, history.length - 100);
      }

      localStorage.setItem(STORAGE_SESSIONS_KEY, JSON.stringify(history));
    } catch (error) {
      console.error("Failed to save to history:", error);
    }
  }

  /**
   * Get all saved sessions
   */
  getSessionHistory() {
    try {
      const data = localStorage.getItem(STORAGE_SESSIONS_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error("Failed to load session history:", error);
      return [];
    }
  }

  /**
   * Export all feedback data for fine-tuning
   */
  exportForFineTuning() {
    const sessions = this.getSessionHistory();
    const trainingData = [];

    sessions.forEach((session) => {
      session.corrections.forEach((correction) => {
        if (correction.action && correction.action !== "reject") {
          // Create training example
          trainingData.push({
            // Input: the original (incorrect) word in context
            input: {
              text: session.originalText,
              errorWord: correction.originalWord,
              pattern: correction.pattern,
            },
            // Output: the correct word (either AI suggestion accepted, or teacher edit)
            output: {
              correctedWord: correction.finalWord,
              wasEdited: correction.action === "edit",
            },
            // Metadata for filtering/analysis
            metadata: {
              sessionId: session.sessionId,
              timestamp: correction.actionTimestamp,
              modelUsed: session.modelUsed,
              confidence: correction.confidence,
              action: correction.action,
            },
          });
        }
      });
    });

    return {
      exportedAt: new Date().toISOString(),
      totalSessions: sessions.length,
      totalExamples: trainingData.length,
      data: trainingData,
    };
  }

  /**
   * Export as JSONL format for fine-tuning
   */
  exportAsJsonl() {
    const sessions = this.getSessionHistory();
    const lines = [];

    sessions.forEach((session) => {
      session.corrections.forEach((correction) => {
        if (correction.action === "accept" || correction.action === "edit") {
          // Format for instruction fine-tuning
          const example = {
            instruction: `Correct the Sinhala dyslexia error in this word. Pattern: ${correction.pattern}`,
            input: correction.originalWord,
            output: correction.finalWord,
            context: session.originalText,
          };
          lines.push(JSON.stringify(example));
        }
      });
    });

    return lines.join("\n");
  }

  /**
   * Export statistics summary
   */
  getStatistics() {
    const sessions = this.getSessionHistory();
    
    let totalCorrections = 0;
    let accepted = 0;
    let rejected = 0;
    let edited = 0;
    const patternStats = {};
    const editedCorrections = [];

    sessions.forEach((session) => {
      session.corrections.forEach((correction) => {
        if (correction.action) {
          totalCorrections++;
          
          if (correction.action === "accept") accepted++;
          if (correction.action === "reject") rejected++;
          if (correction.action === "edit") {
            edited++;
            editedCorrections.push({
              original: correction.originalWord,
              suggested: correction.suggestedCorrection,
              teacherCorrection: correction.finalWord,
              pattern: correction.pattern,
            });
          }

          // Count patterns
          const pattern = correction.pattern || "Unknown";
          patternStats[pattern] = patternStats[pattern] || { total: 0, accepted: 0, rejected: 0, edited: 0 };
          patternStats[pattern].total++;
          patternStats[pattern][correction.action === "reject" ? "rejected" : correction.action === "edit" ? "edited" : "accepted"]++;
        }
      });
    });

    return {
      totalSessions: sessions.length,
      totalCorrections,
      accepted,
      rejected,
      edited,
      acceptanceRate: totalCorrections > 0 ? ((accepted / totalCorrections) * 100).toFixed(1) : 0,
      editRate: totalCorrections > 0 ? ((edited / totalCorrections) * 100).toFixed(1) : 0,
      patternStats,
      editedCorrections, // These are valuable - shows where AI was wrong
    };
  }

  /**
   * Queue feedback for backend sync
   */
  queueForSync(data) {
    this.feedbackQueue.push(data);
    
    // Try to sync if we have enough items
    if (this.feedbackQueue.length >= 5) {
      this.syncToBackend();
    }
  }

  /**
   * Sync feedback to backend (when available)
   */
  async syncToBackend() {
    if (this.feedbackQueue.length === 0) return;

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          feedback: this.feedbackQueue,
          timestamp: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        this.feedbackQueue = [];
        console.log("Feedback synced to backend");
      }
    } catch (error) {
      // Backend not available, keep in queue
      console.log("Backend not available, feedback saved locally");
    }
  }

  /**
   * Download feedback data as JSON file
   */
  downloadFeedbackData() {
    const data = this.exportForFineTuning();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `akura-feedback-${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  /**
   * Download as JSONL for fine-tuning
   */
  downloadAsJsonl() {
    const data = this.exportAsJsonl();
    const blob = new Blob([data], { type: "application/jsonl" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `akura-finetune-${new Date().toISOString().split("T")[0]}.jsonl`;
    a.click();
    URL.revokeObjectURL(url);
  }

  /**
   * Clear all stored feedback data
   */
  clearAllData() {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STORAGE_SESSIONS_KEY);
    localStorage.removeItem(`${STORAGE_KEY}_current`);
    this.currentSession = null;
    this.feedbackQueue = [];
  }

  /**
   * Generate unique session ID
   */
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate unique ID
   */
  generateId() {
    return `fb_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Export singleton instance
export const feedbackService = new FeedbackService();
export default feedbackService;
