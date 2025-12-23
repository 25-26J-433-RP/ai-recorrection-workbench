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
  Cloud,
  Loader2,
} from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { WORD_STATES } from "../constants";
import ErrorToken from "./ErrorToken";
import EditableWord from "./EditableWord";
import { Button, Card, CardHeader, CardTitle, CardContent, Badge, Skeleton } from "./ui";
import apiService from "../services/api";
import { Edit2 } from "lucide-react";

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

  // Format model name for display
  const getModelDisplayName = () => {
    if (!modelUsed) return "";
    if (modelUsed.includes("akura") || modelUsed.includes("llama")) {
      return "Akura LLaMA 8B (Fine-tuned)";
    }
    if (modelUsed.includes("gemini")) return "Gemini";
    return modelUsed;
  };

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
      <Card className="flex flex-col h-full min-h-[400px] lg:h-[calc(100vh-200px)]">
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
      </Card>
    );
  }

  // Render loading state with skeleton
  if (isAnalyzing) {
    return (
      <Card className="flex flex-col h-full min-h-[400px] lg:h-[calc(100vh-200px)]">
        <CardHeader className="border-b border-slate-100">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center p-8">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
          <h3 className="text-lg font-semibold text-slate-700 mb-2">
            Analyzing Patterns...
          </h3>
          <p className="text-sm text-slate-500">
            Our AI is detecting dyslexia patterns in the text
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col h-full min-h-[400px] lg:h-[calc(100vh-200px)]">
      {/* Panel Header */}
      <CardHeader className="border-b border-slate-100">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-500" />
              <span className="sinhala-text">විශ්ලේෂණ ප්‍රතිඵල</span>
            </CardTitle>
            <p className="text-sm text-slate-500 mt-1">
              Click on highlighted words to review corrections
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Save to Cloud Button */}
            <Button
              variant={saved ? "success" : saveError ? "destructive" : "outline"}
              size="sm"
              onClick={handleSave}
              disabled={saving}
              title={
                pendingCount > 0
                  ? "Review all errors before saving"
                  : "Save to cloud database"
              }
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="hidden sm:inline">Saving...</span>
                </>
              ) : saved ? (
                <>
                  <Check className="w-4 h-4" />
                  <span className="hidden sm:inline">Saved!</span>
                </>
              ) : saveError ? (
                <>
                  <XCircle className="w-4 h-4" />
                  <span className="hidden sm:inline">Error</span>
                </>
              ) : (
                <>
                  <Cloud className="w-4 h-4" />
                  <span className="hidden sm:inline">Save</span>
                </>
              )}
            </Button>

            {/* Copy Button */}
            <Button variant="secondary" size="sm" onClick={handleCopy}>
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-500" />
                  <span className="hidden sm:inline">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span className="hidden sm:inline">Copy</span>
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-4 mt-3">
          <Badge variant="error" className="gap-1">
            <AlertTriangle className="w-3 h-3" />
            <span>{totalErrors} errors</span>
          </Badge>
          <Badge variant="success" className="gap-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>{correctedCount} corrected</span>
          </Badge>
          <Badge variant="default" className="gap-1">
            <XCircle className="w-3 h-3" />
            <span>{ignoredCount} ignored</span>
          </Badge>
          {pendingCount > 0 && (
            <Badge variant="warning" className="gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span>{pendingCount} pending</span>
            </Badge>
          )}
        </div>
      </CardHeader>

      {/* Interactive Text Area */}
      <CardContent className="flex-1 overflow-y-auto p-4 sm:p-6">
        <div className="text-lg sm:text-xl leading-relaxed sinhala-text" dir="auto">
          {tokens.map((token) => {
            if (token.type === "whitespace") {
              return <span key={token.id}>{token.displayWord}</span>;
            }

            if (token.type === "error") {
              return <ErrorToken key={token.id} token={token} />;
            }

            // Normal word - make it editable too
            return (
              <EditableWord key={token.id} token={token} />
            );
          })}
        </div>
      </CardContent>

      {/* Footer Info */}
      <div className="px-4 sm:px-6 py-3 bg-slate-50 border-t border-slate-100 rounded-b-2xl">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs text-slate-500 gap-1">
          <span>Model: {getModelDisplayName()}</span>
          <span>Processing time: {processingTime?.toFixed(0)}ms</span>
        </div>
      </div>
    </Card>
  );
}

export default RightPanel;
