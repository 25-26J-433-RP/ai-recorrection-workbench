/**
 * Akura AI - Right Panel Component (Interactive Editor)
 *
 * Displays tokenized text with interactive error tokens.
 * Shows analysis results with clickable correction UI.
 */

import React from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Sparkles,
  Copy,
  Check,
  Save,
  Cloud,
  Loader2,
} from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { WORD_STATES } from "../constants";
import ErrorToken from "./ErrorToken";
import apiService from "../services/api";

function RightPanel() {
  const {
    tokens,
    isAnalyzing,
    analysisComplete,
    totalErrors,
    correctedCount,
    ignoredCount,
    pendingCount,
    processingTime,
    modelUsed,
    getFinalText,
    originalText,
    isDemoMode,
  } = useAnalysis();

  const [copied, setCopied] = React.useState(false);
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);
  const [saveError, setSaveError] = React.useState(null);

  // Copy final text to clipboard
  const handleCopy = async () => {
    const finalText = getFinalText();
    await navigator.clipboard.writeText(finalText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Save session to database
  const handleSave = async () => {
    setSaving(true);
    setSaveError(null);
    
    const sessionData = {
      original_text: originalText,
      final_text: getFinalText(),
      model_used: modelUsed,
      is_demo_mode: isDemoMode,
      actions: tokens
        .filter((t) => t.type === "error" && t.state !== WORD_STATES.FLAGGED)
        .map((t) => ({
          original_word: t.originalWord,
          suggestion: t.correctedWord,
          final_word: t.displayWord,
          action: t.state === WORD_STATES.CORRECTED ? "accept" : "reject",
          pattern: t.pattern,
          confidence: t.confidence,
        })),
    };

    const result = await apiService.saveSession(sessionData);
    setSaving(false);
    
    if (result.success) {
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } else {
      setSaveError(result.error || "Failed to save");
      setTimeout(() => setSaveError(null), 5000);
    }
  };

  // Render placeholder when no analysis
  if (!analysisComplete && !isAnalyzing) {
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col h-[calc(100vh-200px)] min-h-[500px]">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
              <Sparkles className="w-10 h-10 text-indigo-500" />
            </div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">
              Ready to Analyze
            </h3>
            <p className="text-sm text-slate-500 max-w-xs mx-auto">
              Enter text in the left panel and click "Analyze" to see AI-powered
              dyslexia pattern detection.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Render loading state
  if (isAnalyzing) {
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col h-[calc(100vh-200px)] min-h-[500px]">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
              <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            </div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">
              Analyzing Patterns...
            </h3>
            <p className="text-sm text-slate-500">
              Our AI is detecting dyslexia patterns in the text
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-200 flex flex-col h-[calc(100vh-200px)] min-h-[500px]">
      {/* Panel Header */}
      <div className="px-6 py-4 border-b border-slate-100">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-500" />
              විශ්ලේෂණ ප්‍රතිඵල
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Click on highlighted words to review corrections
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Save to Cloud Button */}
            <button
              onClick={handleSave}
              disabled={saving || pendingCount > 0}
              className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg transition-colors ${
                saved
                  ? "bg-green-100 text-green-700"
                  : saveError
                  ? "bg-red-100 text-red-700"
                  : "bg-indigo-100 hover:bg-indigo-200 text-indigo-700"
              } ${(saving || pendingCount > 0) ? "opacity-50 cursor-not-allowed" : ""}`}
              title={pendingCount > 0 ? "Review all errors before saving" : "Save to cloud database"}
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : saved ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Saved!</span>
                </>
              ) : saveError ? (
                <>
                  <XCircle className="w-4 h-4" />
                  <span>Error</span>
                </>
              ) : (
                <>
                  <Cloud className="w-4 h-4" />
                  <span>Save to Cloud</span>
                </>
              )}
            </button>

            {/* Copy Button */}
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-3 py-1.5 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-500" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Copy Result</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="flex items-center gap-4 mt-3 text-sm">
          <div className="flex items-center gap-1.5 text-red-600">
            <AlertTriangle className="w-4 h-4" />
            <span>{totalErrors} errors</span>
          </div>
          <div className="flex items-center gap-1.5 text-green-600">
            <CheckCircle2 className="w-4 h-4" />
            <span>{correctedCount} corrected</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-500">
            <XCircle className="w-4 h-4" />
            <span>{ignoredCount} ignored</span>
          </div>
          {pendingCount > 0 && (
            <div className="flex items-center gap-1.5 text-amber-600">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span>{pendingCount} pending</span>
            </div>
          )}
        </div>
      </div>

      {/* Interactive Text Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="text-xl leading-relaxed sinhala-text" dir="auto">
          {tokens.map((token) => {
            if (token.type === "whitespace") {
              return <span key={token.id}>{token.displayWord}</span>;
            }

            if (token.type === "error") {
              return <ErrorToken key={token.id} token={token} />;
            }

            // Normal word
            return (
              <span key={token.id} className="text-slate-800">
                {token.displayWord}
              </span>
            );
          })}
        </div>
      </div>

      {/* Footer Info */}
      <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 rounded-b-2xl">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>Model: {modelUsed}</span>
          <span>Processing time: {processingTime?.toFixed(0)}ms</span>
        </div>
      </div>
    </div>
  );
}

export default RightPanel;
