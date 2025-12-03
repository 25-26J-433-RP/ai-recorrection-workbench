/**
 * Akura AI - Error Token Component
 *
 * Interactive clickable token for error words.
 * Shows popover with correction suggestions.
 */

import React, { useState, useRef, useEffect } from 'react';
import { Check, X, Edit3, ChevronDown } from 'lucide-react';
import { useAnalysis } from '../context/AnalysisContext';
import { WORD_STATES, PATTERN_KEYS, PATTERN_COLORS } from '../constants';

function ErrorToken({ token }) {
  const {
    acceptCorrection,
    rejectCorrection,
    editCorrection,
    selectedTokenId,
    selectToken,
  } = useAnalysis();
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(token.correctedWord || "");
  const tokenRef = useRef(null);
  const popoverRef = useRef(null);
  const inputRef = useRef(null);

  // Get pattern color
  const getPatternColor = () => {
    const pattern = token.pattern?.toLowerCase() || "";
    if (pattern.includes("visual") || pattern.includes("scrambl")) {
      return PATTERN_COLORS.VISUAL;
    }
    if (
      pattern.includes("phonetic") ||
      pattern.includes("dental") ||
      pattern.includes("retroflex")
    ) {
      return PATTERN_COLORS.PHONETIC;
    }
    if (pattern.includes("grammar") || pattern.includes("spoken")) {
      return PATTERN_COLORS.GRAMMAR;
    }
    return PATTERN_COLORS.ERROR;
  };

  // Get CSS classes based on state
  const getTokenClasses = () => {
    const baseClasses =
      "inline-block cursor-pointer rounded px-1 py-0.5 transition-all relative";

    switch (token.state) {
      case WORD_STATES.CORRECTED:
        return `${baseClasses} bg-green-100 text-green-800 border-b-2 border-green-400`;
      case WORD_STATES.IGNORED:
        return `${baseClasses} bg-slate-100 text-slate-500 line-through`;
      case WORD_STATES.FLAGGED:
      default: {
        const color = getPatternColor();
        return `${baseClasses} bg-red-100 text-red-800 border-b-2 border-red-400 hover:bg-red-200 error-token`;
      }
    }
  };

  // Handle click outside to close popover
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        popoverRef.current &&
        !popoverRef.current.contains(event.target) &&
        tokenRef.current &&
        !tokenRef.current.contains(event.target)
      ) {
        setIsOpen(false);
        setIsEditing(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Focus input when editing
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleClick = () => {
    if (token.state === WORD_STATES.FLAGGED) {
      setIsOpen(!isOpen);
      selectToken(token.id);
    }
  };

  const handleAccept = () => {
    acceptCorrection(token.id);
    setIsOpen(false);
  };

  const handleReject = () => {
    rejectCorrection(token.id);
    setIsOpen(false);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleEditSubmit = (e) => {
    e.preventDefault();
    if (editValue.trim()) {
      editCorrection(token.id, editValue.trim());
      setIsEditing(false);
      setIsOpen(false);
    }
  };

  const handleEditCancel = () => {
    setEditValue(token.correctedWord || "");
    setIsEditing(false);
  };

  return (
    <span className="relative inline">
      {/* Token */}
      <span
        ref={tokenRef}
        onClick={handleClick}
        className={getTokenClasses()}
        title={
          token.state === WORD_STATES.FLAGGED ? "Click to review" : undefined
        }
      >
        {token.displayWord}
        {token.state === WORD_STATES.FLAGGED && (
          <ChevronDown className="inline w-3 h-3 ml-0.5 opacity-50" />
        )}
      </span>

      {/* Popover */}
      {isOpen && token.state === WORD_STATES.FLAGGED && (
        <div
          ref={popoverRef}
          className="popover-card absolute z-50 top-full left-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200"
        >
          {/* Header */}
          <div className="px-4 py-3 bg-gradient-to-r from-red-50 to-orange-50 border-b border-red-100">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-red-800">
                Detected Error
              </span>
              <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full">
                {Math.round((token.confidence || 0.85) * 100)}% confidence
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="p-4">
            {/* Original → Suggested */}
            <div className="flex items-center gap-3 mb-4">
              <span className="px-3 py-2 bg-red-100 text-red-800 rounded-lg font-medium sinhala-text">
                {token.originalWord}
              </span>
              <span className="text-slate-400">→</span>
              <span className="px-3 py-2 bg-green-100 text-green-800 rounded-lg font-medium sinhala-text">
                {token.correctedWord}
              </span>
            </div>

            {/* Pattern */}
            <div className="mb-4">
              <p className="text-xs text-slate-500 mb-1">Pattern Detected:</p>
              <p className="text-sm font-medium text-slate-700">
                {token.pattern}
              </p>
            </div>

            {/* Explanation */}
            {token.explanation && (
              <div className="mb-4 p-3 bg-slate-50 rounded-lg">
                <p className="text-xs text-slate-600">{token.explanation}</p>
              </div>
            )}

            {/* Edit Mode */}
            {isEditing ? (
              <form onSubmit={handleEditSubmit} className="mb-4">
                <input
                  ref={inputRef}
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-lg sinhala-text focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Enter correction..."
                />
                <div className="flex gap-2 mt-2">
                  <button
                    type="submit"
                    className="flex-1 py-2 bg-indigo-500 text-white rounded-lg text-sm font-medium hover:bg-indigo-600"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={handleEditCancel}
                    className="flex-1 py-2 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-200"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              /* Action Buttons */
              <div className="flex gap-2">
                <button
                  onClick={handleAccept}
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition-colors"
                >
                  <Check className="w-4 h-4" />
                  Accept
                </button>
                <button
                  onClick={handleReject}
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors"
                >
                  <X className="w-4 h-4" />
                  Ignore
                </button>
                <button
                  onClick={handleEdit}
                  className="px-3 py-2.5 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
                  title="Edit manually"
                >
                  <Edit3 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </span>
  );
}

export default ErrorToken;
