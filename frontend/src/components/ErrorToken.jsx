/**
 * Akura AI - Error Token Component
 *
 * Interactive word token displaying dyslexia errors.
 * Implements the state machine: FLAGGED → CORRECTED/IGNORED
 */

import React, { useState, useRef, useEffect } from "react";
import { Check, X, Edit3, AlertCircle, Sparkles } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { WORD_STATES, PATTERN_KEYS, PATTERN_COLORS } from "../constants";

function ErrorToken({ token }) {
  const {
    acceptCorrection,
    rejectCorrection,
    editCorrection,
    selectToken,
    selectedTokenId,
  } = useAnalysis();

  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(token.correctedWord);
  const [showPopover, setShowPopover] = useState(false);
  const popoverRef = useRef(null);
  const tokenRef = useRef(null);

  const isSelected = selectedTokenId === token.id;
  const patternKey = PATTERN_KEYS[token.pattern] || "unknown";
  const colors = PATTERN_COLORS[patternKey] || PATTERN_COLORS.unknown;

  // Close popover when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (
        popoverRef.current &&
        !popoverRef.current.contains(event.target) &&
        tokenRef.current &&
        !tokenRef.current.contains(event.target)
      ) {
        setShowPopover(false);
        setIsEditing(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleClick = () => {
    // Allow re-correction: FLAGGED, CORRECTED, or IGNORED words can be clicked
    if (
      token.state === WORD_STATES.FLAGGED ||
      token.state === WORD_STATES.CORRECTED ||
      token.state === WORD_STATES.IGNORED
    ) {
      setShowPopover(!showPopover);
      selectToken(token.id);
    }
  };

  const handleAccept = () => {
    acceptCorrection(token.id);
    setShowPopover(false);
  };

  const handleReject = () => {
    rejectCorrection(token.id);
    setShowPopover(false);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleEditSubmit = (e) => {
    e.preventDefault();
    if (editValue.trim()) {
      editCorrection(token.id, editValue.trim());
      setIsEditing(false);
      setShowPopover(false);
    }
  };

  const handleEditCancel = () => {
    setEditValue(token.correctedWord);
    setIsEditing(false);
  };

  // Get class based on state
  const getStateClass = () => {
    switch (token.state) {
      case WORD_STATES.FLAGGED:
        return "error-token--flagged";
      case WORD_STATES.CORRECTED:
        return "error-token--corrected";
      case WORD_STATES.IGNORED:
        return "error-token--ignored";
      default:
        return "";
    }
  };

  return (
    <span className="relative inline">
      {/* The Token */}
      <span
        ref={tokenRef}
        onClick={handleClick}
        className={`error-token ${getStateClass()} ${
          token.state === WORD_STATES.FLAGGED ||
          token.state === WORD_STATES.CORRECTED ||
          token.state === WORD_STATES.IGNORED
            ? "cursor-pointer"
            : ""
        } sinhala-text`}
        title={
          token.state === WORD_STATES.FLAGGED
            ? `Click to review: ${token.pattern}`
            : token.state === WORD_STATES.CORRECTED || token.state === WORD_STATES.IGNORED
            ? "Click to change correction"
            : undefined
        }
      >
        {token.displayWord}
      </span>

      {/* Popover - uses fixed positioning to avoid overflow clipping */}
      {/* Popover - show for FLAGGED, CORRECTED, or IGNORED states for re-correction */}
      {showPopover &&
        (token.state === WORD_STATES.FLAGGED ||
          token.state === WORD_STATES.CORRECTED ||
          token.state === WORD_STATES.IGNORED) &&
        (() => {
        const rect = tokenRef.current?.getBoundingClientRect();
        const popoverStyle = rect ? {
          top: `${rect.top - 8}px`,
          left: `${rect.left + rect.width / 2}px`,
          transform: 'translate(-50%, -100%)',
        } : {};
        
        return (
          <div
            ref={popoverRef}
            className="popover"
            style={popoverStyle}
          >
          {!isEditing ? (
            <>
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`${colors.icon}`}>
                      <AlertCircle className="w-4 h-4" />
                    </span>
                    <span className="text-sm font-medium text-slate-800">
                      Suggested Correction
                    </span>
                  </div>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${colors.bg} ${colors.text}`}
                  >
                    {token.pattern}
                  </span>
                </div>
                <button
                  onClick={() => setShowPopover(false)}
                  className="p-1 hover:bg-slate-100 rounded"
                >
                  <X className="w-4 h-4 text-slate-400" />
                </button>
              </div>

              {/* Correction Display */}
              <div className="bg-slate-50 rounded-lg p-3 mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-lg sinhala-text text-red-500 line-through">
                    {token.originalWord}
                  </span>
                  <span className="text-slate-400">→</span>
                  <span className="text-lg sinhala-text text-green-600 font-medium">
                    {token.correctedWord}
                  </span>
                </div>
                {token.explanation && (
                  <p className="text-xs text-slate-500 mt-2">
                    {token.explanation}
                  </p>
                )}
              </div>

              {/* Confidence */}
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-3 h-3 text-amber-500" />
                <span className="text-xs text-slate-500">
                  Confidence: {Math.round(token.confidence * 100)}%
                </span>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={handleAccept}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-green-500 text-white text-sm font-medium rounded-lg hover:bg-green-600 transition-colors"
                >
                  <Check className="w-4 h-4" />
                  Accept
                </button>
                <button
                  onClick={handleEdit}
                  className="flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-100 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-200 transition-colors"
                >
                  <Edit3 className="w-4 h-4" />
                </button>
                <button
                  onClick={handleReject}
                  className="flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-100 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-200 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            /* Edit Mode */
            <form onSubmit={handleEditSubmit}>
              <div className="mb-3">
                <label className="text-sm font-medium text-slate-700 block mb-1">
                  Edit Correction
                </label>
                <input
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent sinhala-text text-lg"
                  autoFocus
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-indigo-500 text-white text-sm font-medium rounded-lg hover:bg-indigo-600 transition-colors"
                >
                  <Check className="w-4 h-4" />
                  Save
                </button>
                <button
                  type="button"
                  onClick={handleEditCancel}
                  className="flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-100 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
        );
      })()}
    </span>
  );
}

export default ErrorToken;
