/**
 * Akura AI - Report Modal Component
 *
 * Grammarly-style detailed report
 */

import React, { useMemo } from "react";
import {
  X,
  BarChart3,
  FileText,
  Download,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Brain,
} from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";
import { Button } from "./ui";

function ReportModal() {
  const {
    toggleReport,
    totalErrors,
    correctedCount,
    ignoredCount,
    pendingCount,
    patternDistribution,
    originalText,
    getFinalText,
    processingTime,
    modelUsed,
    tokens,
    exportFeedbackJsonl,
  } = useAnalysis();

  const totalPatterns = Object.values(patternDistribution).reduce((a, b) => a + b, 0);
  const patternPercentages = Object.entries(patternDistribution).map(
    ([pattern, count]) => ({
      pattern,
      count,
      percentage: totalPatterns > 0 ? Math.round((count / totalPatterns) * 100) : 0,
    })
  );

  const errorTokens = tokens.filter((t) => t.type === "error");
  const score = totalErrors > 0 ? Math.round(((totalErrors - pendingCount) / totalErrors) * 100) : 100;

  const getModelDisplayName = () => {
    if (!modelUsed) return modelUsed;
    if (modelUsed.includes("akura") || modelUsed.includes("llama")) {
      return "Akura LLaMA 8B";
    }
    if (modelUsed === "demo-mode") return "Demo Mode";
    return modelUsed;
  };

  const handleExport = () => {
    const report = `
AKURA AI - Writing Analysis Report
===================================
Date: ${new Date().toLocaleString()}
Model: ${getModelDisplayName()}
Processing Time: ${processingTime?.toFixed(0)}ms

Original Text:
${originalText}

Corrected Text:
${getFinalText()}

Statistics:
- Total Issues: ${totalErrors}
- Corrected: ${correctedCount}
- Dismissed: ${ignoredCount}
- Score: ${score}%

Pattern Distribution:
${patternPercentages.map((p) => `- ${p.pattern}: ${p.count} (${p.percentage}%)`).join("\n")}
    `.trim();

    const blob = new Blob([report], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `akura-report-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-2xl max-h-[85vh] bg-white rounded-lg shadow-xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-5 py-4 border-b border-neutral-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-neutral-800">Writing Report</h2>
          <button
            onClick={toggleReport}
            className="p-1.5 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Score Header */}
          <div className="flex items-center gap-6 p-4 bg-grammarly-green-light rounded-lg">
            <div className="relative w-16 h-16">
              <svg className="w-16 h-16 transform -rotate-90">
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="#E8FAF5"
                  strokeWidth="6"
                  fill="none"
                />
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="#15C39A"
                  strokeWidth="6"
                  fill="none"
                  strokeDasharray={`${score * 1.76} 176`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold text-grammarly-green-dark">{score}</span>
              </div>
            </div>
            <div>
              <p className="text-lg font-semibold text-grammarly-green-dark">
                {score >= 80 ? "Great work!" : score >= 50 ? "Good progress" : "Keep improving"}
              </p>
              <p className="text-sm text-grammarly-green">
                {correctedCount} of {totalErrors} issues addressed
              </p>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-neutral-50 rounded-lg text-center">
              <AlertCircle className="w-5 h-5 text-grammarly-red mx-auto mb-2" />
              <p className="text-2xl font-bold text-neutral-800">{totalErrors}</p>
              <p className="text-xs text-neutral-500">Issues found</p>
            </div>
            <div className="p-4 bg-neutral-50 rounded-lg text-center">
              <CheckCircle2 className="w-5 h-5 text-grammarly-green mx-auto mb-2" />
              <p className="text-2xl font-bold text-neutral-800">{correctedCount}</p>
              <p className="text-xs text-neutral-500">Corrected</p>
            </div>
            <div className="p-4 bg-neutral-50 rounded-lg text-center">
              <XCircle className="w-5 h-5 text-neutral-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-neutral-800">{ignoredCount}</p>
              <p className="text-xs text-neutral-500">Dismissed</p>
            </div>
          </div>

          {/* Pattern Distribution */}
          <div>
            <h3 className="text-sm font-medium text-neutral-700 mb-3">Issue Types</h3>
            <div className="space-y-3">
              {patternPercentages.map(({ pattern, count, percentage }) => (
                <div key={pattern}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-neutral-600">{pattern}</span>
                    <span className="text-neutral-400">{count}</span>
                  </div>
                  <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-grammarly-green rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Text Comparison */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-grammarly-red-light rounded-lg">
              <p className="text-xs font-medium text-grammarly-red mb-2">Original</p>
              <p className="text-sm text-neutral-700 sinhala-text">{originalText}</p>
            </div>
            <div className="p-4 bg-grammarly-green-light rounded-lg">
              <p className="text-xs font-medium text-grammarly-green-dark mb-2">Corrected</p>
              <p className="text-sm text-neutral-700 sinhala-text">{getFinalText()}</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-neutral-200 flex items-center justify-between bg-neutral-50">
          <span className="text-xs text-neutral-400">
            {getModelDisplayName()} • {processingTime?.toFixed(0)}ms
          </span>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="w-4 h-4" />
              Export
            </Button>
            <Button size="sm" onClick={exportFeedbackJsonl}>
              <Brain className="w-4 h-4" />
              Training Data
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportModal;
