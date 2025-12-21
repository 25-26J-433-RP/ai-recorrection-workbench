/**
 * Akura AI - Error Token Component
 *
 * Grammarly-style underlined error with clean popover
 */

import React, { useState, useRef, useEffect } from "react";
import { Check, X, Edit3 } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { WORD_STATES } from "../constants";

function ErrorToken({ token }) {
  const {
    acceptCorrection,
    rejectCorrection,
    editCorrection,
    selectToken,
  } = useAnalysis();
  
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(token.correctedWord || "");
  const tokenRef = useRef(null);
  const popoverRef = useRef(null);
  const inputRef = useRef(null);

  // Get pattern type for underline color
  const getPatternType = () => {
    const pattern = token.pattern?.toLowerCase() || "";
    if (pattern.includes("visual") || pattern.includes("scrambl")) return "spelling";
    if (pattern.includes("phonetic") || pattern.includes("dental")) return "spelling";
    if (pattern.includes("grammar") || pattern.includes("spoken")) return "grammar";
    return "spelling";
  };

  const getUnderlineClass = () => {
    if (token.state === WORD_STATES.CORRECTED) return "error-corrected";
    if (token.state === WORD_STATES.IGNORED) return "error-ignored";
    const type = getPatternType();
    return `error-underline error-underline--${type}`;
  };

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
    if (isOpen) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

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

  const handleEditSubmit = (e) => {
    e.preventDefault();
    if (editValue.trim()) {
      editCorrection(token.id, editValue.trim());
      setIsEditing(false);
      setIsOpen(false);
    }
  };

  return (
    <span className="relative inline">
      <span
        ref={tokenRef}
        onClick={handleClick}
        className={`${getUnderlineClass()} px-0.5 cursor-pointer`}
      >
        {token.displayWord}
      </span>

      {isOpen && token.state === WORD_STATES.FLAGGED && (
        <div
          ref={popoverRef}
          className="popover absolute z-50 top-full left-0 mt-2 w-72"
        >
          {/* Suggestion Card */}
          <div className="p-4">
            {/* Original → Suggested */}
            <div className="flex items-center gap-3 mb-3">
              <span className="text-grammarly-red line-through text-sm sinhala-text">
                {token.originalWord}
              </span>
              <span className="text-neutral-300">→</span>
              <span className="text-grammarly-green font-medium sinhala-text">
                {token.correctedWord}
              </span>
            </div>

            {/* Pattern info */}
            <p className="text-xs text-neutral-500 mb-4 leading-relaxed">
              {token.pattern}
            </p>

            {/* Edit mode */}
            {isEditing ? (
              <form onSubmit={handleEditSubmit}>
                <input
                  ref={inputRef}
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm sinhala-text focus:outline-none focus:ring-2 focus:ring-grammarly-green focus:border-grammarly-green mb-3"
                />
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 py-2 bg-grammarly-green text-white rounded-md text-sm font-medium hover:bg-grammarly-green-dark transition-colors"
                  >
                    Apply
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsEditing(false)}
                    className="flex-1 py-2 bg-neutral-100 text-neutral-600 rounded-md text-sm font-medium hover:bg-neutral-200 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleAccept}
                  className="flex-1 flex items-center justify-center gap-1.5 py-2 bg-grammarly-green text-white rounded-md text-sm font-medium hover:bg-grammarly-green-dark transition-colors"
                >
                  <Check className="w-4 h-4" />
                  Accept
                </button>
                <button
                  onClick={handleReject}
                  className="flex-1 flex items-center justify-center gap-1.5 py-2 bg-neutral-100 text-neutral-600 rounded-md text-sm font-medium hover:bg-neutral-200 transition-colors"
                >
                  <X className="w-4 h-4" />
                  Dismiss
                </button>
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-3 py-2 bg-neutral-100 text-neutral-600 rounded-md hover:bg-neutral-200 transition-colors"
                  title="Edit"
                >
                  <Edit3 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Confidence footer */}
          <div className="px-4 py-2 bg-neutral-50 border-t border-neutral-100">
            <div className="flex items-center justify-between text-xs text-neutral-400">
              <span>Confidence</span>
              <span className="font-medium text-neutral-600">
                {Math.round((token.confidence || 0.85) * 100)}%
              </span>
            </div>
          </div>
        </div>
      )}
    </span>
  );
}

export default ErrorToken;
