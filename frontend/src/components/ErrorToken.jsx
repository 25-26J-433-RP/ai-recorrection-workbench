/**
 * Akura AI - Error Token Component
 *
 * Child-friendly interactive clickable token for error words.
 * Shows fun popover with correction suggestions and emojis.
 */

import React, { useState, useRef, useEffect } from "react";
import { Check, X, Edit3, ChevronDown, Sparkles, Star, Lightbulb } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { WORD_STATES, PATTERN_KEYS, PATTERN_COLORS } from "../constants";

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

  // Get pattern info with emoji
  const getPatternInfo = () => {
    const pattern = token.pattern?.toLowerCase() || "";
    if (pattern.includes("visual") || pattern.includes("scrambl")) {
      return { emoji: "👀", label: "Letters got mixed up!", color: "blue" };
    }
    if (
      pattern.includes("phonetic") ||
      pattern.includes("dental") ||
      pattern.includes("retroflex")
    ) {
      return { emoji: "👂", label: "Sounds similar!", color: "amber" };
    }
    if (pattern.includes("grammar") || pattern.includes("spoken")) {
      return { emoji: "💬", label: "Speaking vs writing!", color: "purple" };
    }
    return { emoji: "✏️", label: "Spelling check!", color: "red" };
  };

  // Get CSS classes based on state - child-friendly colors
  const getTokenClasses = () => {
    const baseClasses =
      "inline-block cursor-pointer rounded-xl px-2 py-1 transition-all duration-300 relative font-bold";

    switch (token.state) {
      case WORD_STATES.CORRECTED:
        return `${baseClasses} bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 border-2 border-green-300 shadow-sm`;
      case WORD_STATES.IGNORED:
        return `${baseClasses} bg-gray-100 text-gray-400 line-through border-2 border-gray-200`;
      case WORD_STATES.FLAGGED:
      default: {
        return `${baseClasses} bg-gradient-to-r from-red-100 to-orange-100 text-red-700 border-2 border-red-300 shadow-md hover:shadow-lg hover:scale-105 animate-pulse-soft`;
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

  const patternInfo = getPatternInfo();

  return (
    <span className="relative inline">
      {/* Token */}
      <span
        ref={tokenRef}
        onClick={handleClick}
        className={getTokenClasses()}
        title={
          token.state === WORD_STATES.FLAGGED ? "Click to see the fix! 🔍" : undefined
        }
      >
        {token.displayWord}
        {token.state === WORD_STATES.FLAGGED && (
          <ChevronDown className="inline w-3 h-3 ml-0.5 opacity-60" />
        )}
        {token.state === WORD_STATES.CORRECTED && (
          <span className="absolute -top-1 -right-1 text-xs">✅</span>
        )}
      </span>

      {/* Fun Popover */}
      {isOpen && token.state === WORD_STATES.FLAGGED && (
        <div
          ref={popoverRef}
          className="absolute z-50 top-full left-0 mt-2 w-80 bg-white rounded-3xl shadow-2xl border-2 border-primary-200 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200"
        >
          {/* Fun Header */}
          <div className="px-5 py-4 bg-gradient-to-r from-primary-100 via-primary-50 to-accent-yellow/20 border-b-2 border-primary-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{patternInfo.emoji}</span>
                <div>
                  <span className="text-sm font-bold text-primary-700">
                    Oops! Found Something!
                  </span>
                  <p className="text-xs text-primary-500">{patternInfo.label}</p>
                </div>
              </div>
              <span className="text-xs px-3 py-1 bg-white rounded-full text-primary-600 font-bold shadow-sm">
                {Math.round((token.confidence || 0.85) * 100)}% sure
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="p-5">
            {/* Original → Suggested - Big and fun */}
            <div className="flex items-center justify-center gap-3 mb-5 p-4 bg-gradient-to-r from-primary-50 to-white rounded-2xl">
              <div className="text-center">
                <span className="block text-xs text-red-500 font-bold mb-1">❌ This</span>
                <span className="px-4 py-2 bg-red-100 text-red-700 rounded-xl font-bold text-lg sinhala-text shadow-sm inline-block">
                  {token.originalWord}
                </span>
              </div>
              <Sparkles className="w-6 h-6 text-accent-yellow animate-pulse" />
              <div className="text-center">
                <span className="block text-xs text-green-500 font-bold mb-1">✅ Should be</span>
                <span className="px-4 py-2 bg-green-100 text-green-700 rounded-xl font-bold text-lg sinhala-text shadow-sm inline-block">
                  {token.correctedWord}
                </span>
              </div>
            </div>

            {/* Pattern Explanation - Kid Friendly */}
            <div className="mb-5 p-4 bg-accent-yellow/10 rounded-2xl border-2 border-accent-yellow/30">
              <div className="flex items-start gap-2">
                <Lightbulb className="w-5 h-5 text-accent-yellow shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs text-amber-600 font-bold mb-1">💡 Why did this happen?</p>
                  <p className="text-sm text-amber-700">
                    {token.pattern || "Sometimes letters get jumbled up. It's okay - everyone makes mistakes!"}
                  </p>
                </div>
              </div>
            </div>

            {/* Edit Mode */}
            {isEditing ? (
              <form onSubmit={handleEditSubmit} className="mb-4">
                <input
                  ref={inputRef}
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-primary-300 rounded-xl text-lg sinhala-text focus:outline-none focus:ring-4 focus:ring-primary-200 focus:border-primary-400"
                  placeholder="Type the correct word..."
                />
                <div className="flex gap-2 mt-3">
                  <button
                    type="submit"
                    className="flex-1 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl text-sm font-bold hover:from-primary-600 hover:to-primary-700 shadow-lg"
                  >
                    ✓ Save
                  </button>
                  <button
                    type="button"
                    onClick={handleEditCancel}
                    className="flex-1 py-3 bg-gray-100 text-gray-600 rounded-xl text-sm font-bold hover:bg-gray-200"
                  >
                    ✗ Cancel
                  </button>
                </div>
              </form>
            ) : (
              /* Action Buttons - Big and Fun */
              <div className="flex gap-2">
                <button
                  onClick={handleAccept}
                  className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-gradient-to-r from-green-400 to-green-500 text-white rounded-xl font-bold text-sm hover:from-green-500 hover:to-green-600 transition-all shadow-lg shadow-green-500/30 hover:shadow-xl active:scale-95"
                >
                  <Check className="w-5 h-5" />
                  Yes, Fix It! 🎉
                </button>
                <button
                  onClick={handleReject}
                  className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-gradient-to-r from-gray-200 to-gray-300 text-gray-600 rounded-xl font-bold text-sm hover:from-gray-300 hover:to-gray-400 transition-all active:scale-95"
                >
                  <X className="w-5 h-5" />
                  Keep It
                </button>
                <button
                  onClick={handleEdit}
                  className="px-4 py-3.5 bg-accent-yellow/20 text-amber-600 rounded-xl hover:bg-accent-yellow/30 transition-all"
                  title="I know the right answer!"
                >
                  <Edit3 className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>

          {/* Fun Footer */}
          <div className="px-5 py-3 bg-primary-50 border-t-2 border-primary-100">
            <p className="text-xs text-primary-500 text-center font-medium">
              🌟 Great learners always check their work! 🌟
            </p>
          </div>
        </div>
      )}
    </span>
  );
}

export default ErrorToken;
