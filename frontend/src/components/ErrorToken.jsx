/**
 * Akura AI - Error Token Component
 *
 * Clean, minimal interactive error word with popover
 */

import React, { useState, useRef, useEffect } from "react";
import { Check, X, Edit3, ChevronDown } from "lucide-react";
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

  const getTokenClasses = () => {
    const base = "inline-block cursor-pointer rounded px-1 py-0.5 transition-colors text-sm";
    switch (token.state) {
      case WORD_STATES.CORRECTED:
        return `${base} bg-green-50 text-green-700`;
      case WORD_STATES.IGNORED:
        return `${base} bg-neutral-100 text-neutral-400 line-through`;
      default:
        return `${base} bg-red-50 text-red-700 hover:bg-red-100`;
    }
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
        className={getTokenClasses()}
      >
        {token.displayWord}
        {token.state === WORD_STATES.FLAGGED && (
          <ChevronDown className="inline w-3 h-3 ml-0.5 opacity-50" />
        )}
      </span>

      {isOpen && token.state === WORD_STATES.FLAGGED && (
        <div
          ref={popoverRef}
          className="absolute z-50 top-full left-0 mt-1 w-64 bg-white rounded-lg shadow-lg border border-neutral-200 overflow-hidden animate-in fade-in-0 slide-in-from-top-2"
        >
          {/* Header */}
          <div className="px-3 py-2 bg-neutral-50 border-b border-neutral-100">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-neutral-600">
                Suggested correction
              </span>
              <span className="text-xs text-neutral-400">
                {Math.round((token.confidence || 0.85) * 100)}%
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="p-3">
            {/* Original → Suggested */}
            <div className="flex items-center gap-2 mb-3">
              <span className="px-2 py-1 bg-red-50 text-red-700 rounded text-sm sinhala-text">
                {token.originalWord}
              </span>
              <span className="text-neutral-300">→</span>
              <span className="px-2 py-1 bg-green-50 text-green-700 rounded text-sm sinhala-text">
                {token.correctedWord}
              </span>
            </div>

            {/* Pattern */}
            <p className="text-xs text-neutral-500 mb-3">{token.pattern}</p>

            {/* Edit mode */}
            {isEditing ? (
              <form onSubmit={handleEditSubmit}>
                <input
                  ref={inputRef}
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="w-full px-2 py-1.5 border border-neutral-300 rounded text-sm sinhala-text focus:outline-none focus:ring-1 focus:ring-neutral-400 mb-2"
                />
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 py-1.5 bg-neutral-900 text-white rounded text-xs font-medium"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsEditing(false)}
                    className="flex-1 py-1.5 bg-neutral-100 text-neutral-600 rounded text-xs font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleAccept}
                  className="flex-1 flex items-center justify-center gap-1 py-1.5 bg-green-600 text-white rounded text-xs font-medium hover:bg-green-700 transition-colors"
                >
                  <Check className="w-3 h-3" />
                  Accept
                </button>
                <button
                  onClick={handleReject}
                  className="flex-1 flex items-center justify-center gap-1 py-1.5 bg-neutral-100 text-neutral-600 rounded text-xs font-medium hover:bg-neutral-200 transition-colors"
                >
                  <X className="w-3 h-3" />
                  Ignore
                </button>
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-2 py-1.5 bg-neutral-100 text-neutral-600 rounded hover:bg-neutral-200 transition-colors"
                >
                  <Edit3 className="w-3 h-3" />
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
