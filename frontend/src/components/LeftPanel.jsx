/**
 * Akura AI - Left Panel Component (Input Module)
 *
 * Text input area with character count and analyze button.
 * Shows helpful tips for teachers.
 */

import React from "react";
import { Send, AlertCircle, Lightbulb, FileText } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";

// Sample texts for quick testing
const SAMPLE_TEXTS = [
  {
    title: "නියැදිය 1",
    text: "මම ගෙරද යනව",
    description: "Visual scrambling + grammar",
  },
  {
    title: "නියැදිය 2",
    text: "මං පාලස යනව",
    description: "Spoken form + scrambling",
  },
];

function LeftPanel() {
  const {
    inputText,
    setInputText,
    analyzeText,
    isAnalyzing,
    analysisComplete,
  } = useAnalysis();

  const characterCount = inputText.length;
  const wordCount = inputText.trim() ? inputText.trim().split(/\s+/).length : 0;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && !isAnalyzing) {
      analyzeText();
    }
  };

  const loadSample = (text) => {
    setInputText(text);
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col h-[calc(100vh-200px)] min-h-[500px]">
      {/* Panel Header */}
      <div className="px-6 py-4 border-b border-slate-100">
        <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-500" />
          පෙළ ඇතුළත් කරන්න
        </h2>
        <p className="text-sm text-slate-500 mt-1">
          Enter student's text for dyslexia pattern analysis
        </p>
      </div>

      {/* Text Input Area */}
      <form onSubmit={handleSubmit} className="flex-1 flex flex-col p-6">
        <div className="relative flex-1">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="ශිෂ්‍යයාගේ පෙළ මෙහි ඇතුළත් කරන්න..."
            className="w-full h-full p-4 text-lg sinhala-text bg-slate-50 border border-slate-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all placeholder-slate-400"
            dir="auto"
            disabled={isAnalyzing}
          />

          {/* Character/Word Count */}
          <div className="absolute bottom-3 right-3 flex items-center gap-3 text-xs text-slate-400">
            <span>{wordCount} words</span>
            <span>•</span>
            <span>{characterCount} chars</span>
          </div>
        </div>

        {/* Sample Texts */}
        <div className="mt-4">
          <p className="text-xs text-slate-500 mb-2 flex items-center gap-1">
            <Lightbulb className="w-3 h-3" />
            Quick samples:
          </p>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_TEXTS.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => loadSample(sample.text)}
                className="px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors sinhala-text"
                title={sample.description}
              >
                {sample.title}
              </button>
            ))}
          </div>
        </div>

        {/* Analyze Button */}
        <button
          type="submit"
          disabled={!inputText.trim() || isAnalyzing}
          className={`mt-4 w-full py-3 px-6 rounded-xl font-medium text-white flex items-center justify-center gap-2 transition-all ${
            !inputText.trim() || isAnalyzing
              ? "bg-slate-300 cursor-not-allowed"
              : "bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          }`}
        >
          {isAnalyzing ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>විශ්ලේෂණය කරමින්...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>විශ්ලේෂණය කරන්න</span>
            </>
          )}
        </button>
      </form>

      {/* Tips Section */}
      <div className="px-6 py-4 bg-gradient-to-r from-amber-50 to-orange-50 border-t border-amber-100 rounded-b-2xl">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-800">Teacher Tip</p>
            <p className="text-xs text-amber-700 mt-1">
              Copy text directly from student's work. The AI will identify
              dyslexia-related patterns like letter reversals, phonetic
              confusions, and grammar variations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LeftPanel;
