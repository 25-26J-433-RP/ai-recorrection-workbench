/**
 * Akura AI - Editable Word Component
 *
 * Allows teachers to edit ANY word in the text, not just error words.
 * Useful for marking words the AI missed as errors or fixing other issues.
 */

import React, { useState, useRef, useEffect } from "react";
import { Edit2, Check, X } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";

function EditableWord({ token }) {
  const { editWord } = useAnalysis();
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(token.displayWord);
  const [showHover, setShowHover] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleDoubleClick = () => {
    setEditValue(token.displayWord);
    setIsEditing(true);
  };

  const handleSave = () => {
    if (editValue.trim() && editValue !== token.displayWord) {
      // Call context to update the word
      if (editWord) {
        editWord(token.id, editValue.trim());
      }
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(token.displayWord);
    setIsEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSave();
    } else if (e.key === "Escape") {
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <span className="inline-flex items-center gap-1 mx-0.5">
        <input
          ref={inputRef}
          type="text"
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={handleSave}
          className="px-1 py-0.5 text-lg border border-indigo-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 sinhala-text"
          style={{ width: `${Math.max(editValue.length * 12, 40)}px` }}
          dir="auto"
        />
        <button
          onClick={handleSave}
          className="p-0.5 text-green-600 hover:bg-green-100 rounded"
        >
          <Check className="w-3 h-3" />
        </button>
        <button
          onClick={handleCancel}
          className="p-0.5 text-red-600 hover:bg-red-100 rounded"
        >
          <X className="w-3 h-3" />
        </button>
      </span>
    );
  }

  return (
    <span
      className="text-slate-800 cursor-pointer hover:bg-slate-100 rounded px-0.5 transition-colors relative"
      onDoubleClick={handleDoubleClick}
      onMouseEnter={() => setShowHover(true)}
      onMouseLeave={() => setShowHover(false)}
      title="Double-click to edit"
    >
      {token.displayWord}
      {showHover && (
        <Edit2 className="inline w-3 h-3 ml-0.5 text-slate-400" />
      )}
    </span>
  );
}

export default EditableWord;
