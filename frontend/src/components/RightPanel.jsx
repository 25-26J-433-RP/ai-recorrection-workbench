/**
 * Akura AI - Right Panel Component (Interactive Editor)
 *
 * Child-friendly display of analysis results with encouraging feedback
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
  Trophy,
  Star,
  Rocket,
} from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { WORD_STATES } from "../constants";
import ErrorToken from "./ErrorToken";
import { Button, Card, CardHeader, CardTitle, CardContent, Badge, Skeleton } from "./ui";
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

  const getModelDisplayName = () => {
    if (!modelUsed) return "";
    if (modelUsed.includes("akura") || modelUsed.includes("llama")) {
      return "🤖 Akura AI";
    }
    if (modelUsed === "demo-mode") return "🎮 Demo Mode";
    if (modelUsed.includes("gemini")) return "✨ Gemini";
    return modelUsed;
  };

  const handleCopy = async () => {
    const finalText = getFinalText();
    await navigator.clipboard.writeText(finalText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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
      setSaveError(result.error || "Oops! Couldn't save 😅");
      setTimeout(() => setSaveError(null), 5000);
    }
  };

  // Render placeholder when no analysis
  if (!analysisComplete && !isAnalyzing) {
    return (
      <Card className="flex flex-col h-full min-h-[400px] lg:h-[calc(100vh-200px)]">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-primary-200 to-primary-300 flex items-center justify-center animate-float">
              <Rocket className="w-12 h-12 text-primary-600" />
            </div>
            <h3 className="text-2xl font-bold text-primary-700 mb-2">
              🚀 Ready for Adventure!
            </h3>
            <p className="text-base text-primary-500 max-w-xs mx-auto">
              Type something on the left and click the big button. 
              I'll help you find and fix any mixed-up letters! ✨
            </p>
          </div>
        </div>
      </Card>
    );
  }

  // Render loading state with fun animation
  if (isAnalyzing) {
    return (
      <Card className="flex flex-col h-full min-h-[400px] lg:h-[calc(100vh-200px)]">
        <CardHeader className="border-b-2 border-primary-100">
          <Skeleton className="h-6 w-48 bg-primary-200" />
          <Skeleton className="h-4 w-64 mt-2 bg-primary-100" />
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center p-8">
          <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-primary-200 to-primary-300 flex items-center justify-center">
            <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
          </div>
          <h3 className="text-2xl font-bold text-primary-700 mb-2">
            🔍 Checking Your Writing...
          </h3>
          <p className="text-base text-primary-500">
            Hold on! My AI brain is working hard! 🧠✨
          </p>
        </CardContent>
      </Card>
    );
  }

  // Calculate score for encouragement
  const totalToReview = totalErrors;
  const reviewed = correctedCount + ignoredCount;
  const progressPercent = totalToReview > 0 ? Math.round((reviewed / totalToReview) * 100) : 0;

  return (
    <Card className="flex flex-col h-full min-h-[400px] lg:h-[calc(100vh-200px)]">
      {/* Panel Header */}
      <CardHeader className="border-b-2 border-primary-100 bg-gradient-to-r from-primary-50 to-white">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2">
              <div className="p-2 bg-primary-100 rounded-xl">
                <Sparkles className="w-5 h-5 text-primary-600" />
              </div>
              <span className="sinhala-text">🎯 ප්‍රතිඵල</span>
            </CardTitle>
            <p className="text-sm text-primary-500 mt-2 font-medium">
              Click the colored words to fix them! 👆
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <Button
              variant={saved ? "success" : saveError ? "destructive" : "outline"}
              size="sm"
              onClick={handleSave}
              disabled={saving || pendingCount > 0}
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="hidden sm:inline">💾 Saving...</span>
                </>
              ) : saved ? (
                <>
                  <Check className="w-4 h-4" />
                  <span className="hidden sm:inline">✅ Saved!</span>
                </>
              ) : saveError ? (
                <>
                  <XCircle className="w-4 h-4" />
                  <span className="hidden sm:inline">❌ Error</span>
                </>
              ) : (
                <>
                  <Cloud className="w-4 h-4" />
                  <span className="hidden sm:inline">☁️ Save</span>
                </>
              )}
            </Button>

            <Button variant="secondary" size="sm" onClick={handleCopy}>
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-green-500" />
                  <span className="hidden sm:inline">📋 Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span className="hidden sm:inline">📋 Copy</span>
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Stats Bar - Fun badges */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 mt-3">
          <Badge variant="error" className="gap-1">
            <AlertTriangle className="w-3 h-3" />
            <span>🔴 {totalErrors} found</span>
          </Badge>
          <Badge variant="success" className="gap-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>✅ {correctedCount} fixed</span>
          </Badge>
          <Badge variant="default" className="gap-1">
            <XCircle className="w-3 h-3" />
            <span>⏭️ {ignoredCount} skipped</span>
          </Badge>
          {pendingCount > 0 && (
            <Badge variant="warning" className="gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span>⏳ {pendingCount} left</span>
            </Badge>
          )}
        </div>

        {/* Progress encouragement */}
        {totalErrors > 0 && (
          <div className="mt-3 bg-primary-50 rounded-xl p-3 border-2 border-primary-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-bold text-primary-600">
                {progressPercent === 100 ? "🎉 All done!" : "🌟 Progress"}
              </span>
              <span className="text-sm font-bold text-primary-700">{progressPercent}%</span>
            </div>
            <div className="h-3 bg-primary-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-primary-400 to-primary-500 rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            {progressPercent === 100 && (
              <p className="text-sm text-primary-600 mt-2 flex items-center gap-1">
                <Trophy className="w-4 h-4 text-accent-yellow" />
                Great job! You reviewed everything! 🏆
              </p>
            )}
          </div>
        )}
      </CardHeader>

      {/* Interactive Text Area */}
      <CardContent className="flex-1 overflow-y-auto p-4 sm:p-6 scrollbar-thin">
        <div className="text-lg sm:text-xl leading-relaxed sinhala-text" dir="auto">
          {tokens.map((token) => {
            if (token.type === "whitespace") {
              return <span key={token.id}>{token.displayWord}</span>;
            }

            if (token.type === "error") {
              return <ErrorToken key={token.id} token={token} />;
            }

            return (
              <span key={token.id} className="text-gray-800">
                {token.displayWord}
              </span>
            );
          })}
        </div>
      </CardContent>

      {/* Footer Info */}
      <div className="px-4 sm:px-6 py-3 bg-gradient-to-r from-primary-50 to-white border-t-2 border-primary-100 rounded-b-3xl">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between text-sm text-primary-500 gap-1 font-medium">
          <span>{getModelDisplayName()}</span>
          <span>⚡ {processingTime?.toFixed(0)}ms</span>
        </div>
      </div>
    </Card>
  );
}

export default RightPanel;
