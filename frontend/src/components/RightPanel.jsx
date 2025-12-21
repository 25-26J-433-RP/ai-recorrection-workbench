/**
 * Akura AI - Right Panel Component
 *
 * Grammarly-style editor with sidebar scores
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
  FileText,
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

  // Score calculation
  const score = totalErrors > 0 ? Math.round(((totalErrors - pendingCount) / totalErrors) * 100) : 100;

  // Placeholder
  if (!analysisComplete && !isAnalyzing) {
    return (
      <Card className="flex flex-col h-full min-h-[400px]">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-sm">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-grammarly-green-light flex items-center justify-center">
              <FileText className="w-8 h-8 text-grammarly-green" />
            </div>
            <h3 className="text-lg font-medium text-neutral-800 mb-2">
              Ready to check your writing
            </h3>
            <p className="text-sm text-neutral-500">
              Enter Sinhala text on the left and click Analyze to find and fix errors.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  // Loading
  if (isAnalyzing) {
    return (
      <Card className="flex flex-col h-full min-h-[400px]">
        <CardHeader className="border-b border-neutral-100">
          <Skeleton className="h-5 w-24" />
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center">
          <Loader2 className="w-8 h-8 text-grammarly-green animate-spin mb-4" />
          <p className="text-sm text-neutral-500">Checking your writing...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row gap-4 h-full">
      {/* Main Editor */}
      <Card className="flex-1 flex flex-col min-h-[400px]">
        <CardHeader className="border-b border-neutral-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CardTitle>Editor</CardTitle>
              {pendingCount > 0 && (
                <Badge variant="error">
                  {pendingCount} to review
                </Badge>
              )}
            </div>
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
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-5 scrollbar-thin">
          <div className="text-base leading-[2] sinhala-text" dir="auto">
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
      </Card>

      {/* Sidebar Stats - Grammarly style */}
      <div className="lg:w-48 space-y-4">
        {/* Score Circle */}
        <Card className="p-4 text-center">
          <div className="relative w-20 h-20 mx-auto mb-3">
            <svg className="w-20 h-20 transform -rotate-90">
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke="#EEEEEE"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke="#15C39A"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${score * 2.26} 226`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl font-bold text-neutral-800">{score}</span>
            </div>
          </div>
          <p className="text-sm font-medium text-neutral-600">
            {score >= 80 ? "Great!" : score >= 50 ? "Good" : "Needs work"}
          </p>
        </Card>

        {/* Stats */}
        <Card className="p-4 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-neutral-600">
              <AlertCircle className="w-4 h-4 text-grammarly-red" />
              Found
            </span>
            <span className="font-medium text-neutral-800">{totalErrors}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-neutral-600">
              <CheckCircle2 className="w-4 h-4 text-grammarly-green" />
              Fixed
            </span>
            <span className="font-medium text-neutral-800">{correctedCount}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-neutral-600">
              <XCircle className="w-4 h-4 text-neutral-400" />
              Ignored
            </span>
            <span className="font-medium text-neutral-800">{ignoredCount}</span>
          </div>
        </Card>

        {/* Processing info */}
        <div className="text-xs text-neutral-400 text-center">
          {processingTime?.toFixed(0)}ms
        </div>
      </div>
    </div>
  );
}

export default RightPanel;
