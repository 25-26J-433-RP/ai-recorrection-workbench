/**
 * Akura AI - Right Panel Component
 *
 * Clean, minimal display of analysis results
 */

import React, { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Copy,
  Check,
  Cloud,
  Loader2,
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

  const [copied, setCopied] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(getFinalText());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = async () => {
    setSaving(true);
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
    }
  };

  // Placeholder state
  if (!analysisComplete && !isAnalyzing) {
    return (
      <Card className="flex flex-col h-full min-h-[400px]">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-neutral-100 flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-neutral-400" />
            </div>
            <h3 className="text-base font-medium text-neutral-600 mb-1">
              No analysis yet
            </h3>
            <p className="text-sm text-neutral-400">
              Enter text on the left and click Analyze
            </p>
          </div>
        </div>
      </Card>
    );
  }

  // Loading state
  if (isAnalyzing) {
    return (
      <Card className="flex flex-col h-full min-h-[400px]">
        <CardHeader className="border-b border-neutral-100">
          <Skeleton className="h-5 w-32" />
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center">
          <Loader2 className="w-8 h-8 text-neutral-400 animate-spin mb-4" />
          <p className="text-sm text-neutral-500">Analyzing text...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col h-full min-h-[400px]">
      <CardHeader className="border-b border-neutral-100">
        <div className="flex items-center justify-between">
          <CardTitle>Results</CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant={saved ? "success" : "outline"}
              size="sm"
              onClick={handleSave}
              disabled={saving || pendingCount > 0}
            >
              {saving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : saved ? (
                <Check className="w-4 h-4" />
              ) : (
                <Cloud className="w-4 h-4" />
              )}
              <span className="hidden sm:inline">{saved ? "Saved" : "Save"}</span>
            </Button>
            <Button variant="outline" size="sm" onClick={handleCopy}>
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              <span className="hidden sm:inline">{copied ? "Copied" : "Copy"}</span>
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-3 mt-3 text-xs">
          <Badge variant="error">
            <AlertCircle className="w-3 h-3" />
            {totalErrors} errors
          </Badge>
          <Badge variant="success">
            <CheckCircle2 className="w-3 h-3" />
            {correctedCount} fixed
          </Badge>
          {pendingCount > 0 && (
            <Badge variant="warning">
              {pendingCount} pending
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-5 scrollbar-thin">
        <div className="text-base leading-relaxed sinhala-text" dir="auto">
          {tokens.map((token) => {
            if (token.type === "whitespace") {
              return <span key={token.id}>{token.displayWord}</span>;
            }
            if (token.type === "error") {
              return <ErrorToken key={token.id} token={token} />;
            }
            return <span key={token.id}>{token.displayWord}</span>;
          })}
        </div>
      </CardContent>

      <div className="px-5 py-3 border-t border-neutral-100 text-xs text-neutral-400 flex justify-between">
        <span>{modelUsed}</span>
        <span>{processingTime?.toFixed(0)}ms</span>
      </div>
    </Card>
  );
}

export default RightPanel;
