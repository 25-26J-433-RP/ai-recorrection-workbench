/**
 * Akura AI - Analysis Context Provider
 *
 * Global state management for text analysis and correction workflow.
 * Implements the word state machine: RAW → FLAGGED → CORRECTED/IGNORED
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useCallback,
} from "react";
import { WORD_STATES, ERROR_TYPES } from "../constants";
import apiService from "../services/api";
import feedbackService from "../services/feedback";

// Initial State
const initialState = {
  // Input state
  inputText: "",

  // Analysis state
  isAnalyzing: false,
  analysisComplete: false,

  // Tokenized data
  tokens: [], // Array of word objects with state machine

  // Results
  originalText: "",
  correctedText: "",
  processingTime: 0,
  modelUsed: "",

  // Stats
  totalErrors: 0,
  correctedCount: 0,
  ignoredCount: 0,
  pendingCount: 0,

  // Pattern distribution
  patternDistribution: {},

  // API state
  isDemoMode: false,
  apiStatus: "checking", // 'checking' | 'online' | 'offline'

  // UI state
  selectedTokenId: null,
  showReport: false,

  // Feedback state
  feedbackSessionId: null,

  // Error state
  error: null,
};

// Action Types
const ACTIONS = {
  SET_INPUT_TEXT: "SET_INPUT_TEXT",
  START_ANALYSIS: "START_ANALYSIS",
  ANALYSIS_SUCCESS: "ANALYSIS_SUCCESS",
  ANALYSIS_ERROR: "ANALYSIS_ERROR",
  SET_TOKEN_STATE: "SET_TOKEN_STATE",
  ACCEPT_CORRECTION: "ACCEPT_CORRECTION",
  REJECT_CORRECTION: "REJECT_CORRECTION",
  EDIT_CORRECTION: "EDIT_CORRECTION",
  SELECT_TOKEN: "SELECT_TOKEN",
  TOGGLE_REPORT: "TOGGLE_REPORT",
  SET_API_STATUS: "SET_API_STATUS",
  RESET: "RESET",
};

// Helper: Generate unique ID
const generateId = () =>
  `token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

// Helper: Tokenize text and merge with API results
function tokenizeWithResults(text, apiErrors) {
  const words = text.split(/(\s+)/); // Keep whitespace
  const errorMap = new Map();

  // Build error lookup
  apiErrors.forEach((err) => {
    errorMap.set(err.word, err);
  });

  let errorIndex = 0;
  return words.map((word, index) => {
    // Skip whitespace tokens
    if (/^\s+$/.test(word)) {
      return {
        id: generateId(),
        type: "whitespace",
        originalWord: word,
        displayWord: word,
        state: WORD_STATES.RAW,
      };
    }

    // Check if this word has an error
    const error = errorMap.get(word);

    if (error) {
      errorMap.delete(word); // Use each error only once
      return {
        id: generateId(),
        type: "error",
        originalWord: word,
        displayWord: word,
        correctedWord: error.suggestion,
        state: WORD_STATES.FLAGGED,
        errorType: error.type || ERROR_TYPES.VISUAL,
        pattern: error.dyslexiaPattern || error.pattern,
        explanation: error.explanation,
        confidence: error.confidence || 0.85,
        source: error.source || "ai",
      };
    }

    // Normal word
    return {
      id: generateId(),
      type: "word",
      originalWord: word,
      displayWord: word,
      state: WORD_STATES.RAW,
    };
  });
}

// Helper: Calculate stats from tokens
function calculateStats(tokens) {
  const errors = tokens.filter((t) => t.type === "error");
  const patternDistribution = {};

  errors.forEach((err) => {
    const pattern = err.pattern || "Unknown";
    patternDistribution[pattern] = (patternDistribution[pattern] || 0) + 1;
  });

  return {
    totalErrors: errors.length,
    correctedCount: errors.filter((e) => e.state === WORD_STATES.CORRECTED)
      .length,
    ignoredCount: errors.filter((e) => e.state === WORD_STATES.IGNORED).length,
    pendingCount: errors.filter((e) => e.state === WORD_STATES.FLAGGED).length,
    patternDistribution,
  };
}

// Reducer
function analysisReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_INPUT_TEXT:
      return {
        ...state,
        inputText: action.payload,
        error: null,
      };

    case ACTIONS.START_ANALYSIS:
      return {
        ...state,
        isAnalyzing: true,
        analysisComplete: false,
        error: null,
        tokens: [],
        selectedTokenId: null,
      };

    case ACTIONS.ANALYSIS_SUCCESS: {
      const {
        data,
        correctedText,
        originalText,
        processingTimeMs,
        modelUsed,
        isDemoMode,
        feedbackSessionId,
      } = action.payload;
      const tokens = tokenizeWithResults(originalText, data);
      const stats = calculateStats(tokens);

      return {
        ...state,
        isAnalyzing: false,
        analysisComplete: true,
        tokens,
        originalText,
        correctedText,
        processingTime: processingTimeMs,
        modelUsed,
        isDemoMode,
        feedbackSessionId,
        ...stats,
      };
    }

    case ACTIONS.ANALYSIS_ERROR:
      return {
        ...state,
        isAnalyzing: false,
        error: action.payload,
      };

    case ACTIONS.ACCEPT_CORRECTION: {
      const tokens = state.tokens.map((token) => {
        if (token.id === action.payload) {
          return {
            ...token,
            state: WORD_STATES.CORRECTED,
            displayWord: token.correctedWord,
          };
        }
        return token;
      });
      return {
        ...state,
        tokens,
        ...calculateStats(tokens),
      };
    }

    case ACTIONS.REJECT_CORRECTION: {
      const tokens = state.tokens.map((token) => {
        if (token.id === action.payload) {
          return {
            ...token,
            state: WORD_STATES.IGNORED,
            displayWord: token.originalWord,
          };
        }
        return token;
      });
      return {
        ...state,
        tokens,
        ...calculateStats(tokens),
      };
    }

    case ACTIONS.EDIT_CORRECTION: {
      const { tokenId, newWord } = action.payload;
      const tokens = state.tokens.map((token) => {
        if (token.id === tokenId) {
          return {
            ...token,
            state: WORD_STATES.CORRECTED,
            displayWord: newWord,
            correctedWord: newWord,
          };
        }
        return token;
      });
      return {
        ...state,
        tokens,
        ...calculateStats(tokens),
      };
    }

    case ACTIONS.SELECT_TOKEN:
      return {
        ...state,
        selectedTokenId: action.payload,
      };

    case ACTIONS.TOGGLE_REPORT:
      return {
        ...state,
        showReport: !state.showReport,
      };

    case ACTIONS.SET_API_STATUS:
      return {
        ...state,
        apiStatus: action.payload.online ? "online" : "offline",
        isDemoMode: !action.payload.online,
      };

    case ACTIONS.RESET:
      return {
        ...initialState,
        apiStatus: state.apiStatus,
        isDemoMode: state.isDemoMode,
      };

    default:
      return state;
  }
}

// Context
const AnalysisContext = createContext(null);

// Provider Component
export function AnalysisProvider({ children }) {
  const [state, dispatch] = useReducer(analysisReducer, initialState);

  // Actions
  const setInputText = useCallback((text) => {
    dispatch({ type: ACTIONS.SET_INPUT_TEXT, payload: text });
  }, []);

  const analyzeText = useCallback(async () => {
    if (!state.inputText.trim()) return;

    dispatch({ type: ACTIONS.START_ANALYSIS });

    try {
      const result = await apiService.analyzeText(state.inputText);

      if (result.success) {
        // Start feedback session for collecting teacher corrections
        const feedbackSessionId = feedbackService.startSession(
          state.inputText,
          result
        );

        dispatch({
          type: ACTIONS.ANALYSIS_SUCCESS,
          payload: { ...result, feedbackSessionId },
        });
      } else {
        dispatch({ type: ACTIONS.ANALYSIS_ERROR, payload: "Analysis failed" });
      }
    } catch (error) {
      dispatch({ type: ACTIONS.ANALYSIS_ERROR, payload: error.message });
    }
  }, [state.inputText]);

  const acceptCorrection = useCallback(
    (tokenId) => {
      // Find the token to get its details for feedback
      const token = state.tokens.find((t) => t.id === tokenId);
      if (token) {
        feedbackService.recordAction(
          tokenId,
          "accept",
          token.originalWord,
          token.correctedWord,
          token.correctedWord,
          token.pattern
        );
      }
      dispatch({ type: ACTIONS.ACCEPT_CORRECTION, payload: tokenId });
    },
    [state.tokens]
  );

  const rejectCorrection = useCallback(
    (tokenId) => {
      // Find the token to get its details for feedback
      const token = state.tokens.find((t) => t.id === tokenId);
      if (token) {
        feedbackService.recordAction(
          tokenId,
          "reject",
          token.originalWord,
          token.correctedWord,
          token.originalWord, // Keep original when rejected
          token.pattern
        );
      }
      dispatch({ type: ACTIONS.REJECT_CORRECTION, payload: tokenId });
    },
    [state.tokens]
  );

  const editCorrection = useCallback(
    (tokenId, newWord) => {
      // Find the token to get its details for feedback
      const token = state.tokens.find((t) => t.id === tokenId);
      if (token) {
        feedbackService.recordAction(
          tokenId,
          "edit",
          token.originalWord,
          token.correctedWord,
          newWord, // Teacher's manual correction
          token.pattern
        );
      }
      dispatch({
        type: ACTIONS.EDIT_CORRECTION,
        payload: { tokenId, newWord },
      });
    },
    [state.tokens]
  );

  const selectToken = useCallback((tokenId) => {
    dispatch({ type: ACTIONS.SELECT_TOKEN, payload: tokenId });
  }, []);

  const toggleReport = useCallback(() => {
    dispatch({ type: ACTIONS.TOGGLE_REPORT });
  }, []);

  const checkApiStatus = useCallback(async () => {
    const status = await apiService.checkHealth();
    dispatch({ type: ACTIONS.SET_API_STATUS, payload: status });
    return status;
  }, []);

  const reset = useCallback(() => {
    // End feedback session and save final text
    if (state.analysisComplete) {
      const finalText = state.tokens.map((t) => t.displayWord).join("");
      feedbackService.endSession(finalText);
    }
    dispatch({ type: ACTIONS.RESET });
  }, [state.analysisComplete, state.tokens]);

  // Get final corrected text
  const getFinalText = useCallback(() => {
    return state.tokens.map((t) => t.displayWord).join("");
  }, [state.tokens]);

  // Get feedback statistics
  const getFeedbackStats = useCallback(() => {
    return feedbackService.getStatistics();
  }, []);

  // Export feedback data for fine-tuning
  const exportFeedbackData = useCallback(() => {
    feedbackService.downloadFeedbackData();
  }, []);

  // Export as JSONL for fine-tuning
  const exportFeedbackJsonl = useCallback(() => {
    feedbackService.downloadAsJsonl();
  }, []);

  const value = {
    // State
    ...state,

    // Actions
    setInputText,
    analyzeText,
    acceptCorrection,
    rejectCorrection,
    editCorrection,
    selectToken,
    toggleReport,
    checkApiStatus,
    reset,
    getFinalText,

    // Feedback actions
    getFeedbackStats,
    exportFeedbackData,
    exportFeedbackJsonl,
  };

  return (
    <AnalysisContext.Provider value={value}>
      {children}
    </AnalysisContext.Provider>
  );
}

// Custom Hook
export function useAnalysis() {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error("useAnalysis must be used within AnalysisProvider");
  }
  return context;
}

export default AnalysisContext;
