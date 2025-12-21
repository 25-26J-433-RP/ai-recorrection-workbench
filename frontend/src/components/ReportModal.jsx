/**
 * Akura AI - Report Modal Component
 *
 * Displays a detailed analysis report with statistics and feedback export.
 */

import React from "react";
import {
  X,
  Download,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileJson,
  BarChart3,
  Clock,
  Cpu,
} from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";

function ReportModal() {
  const {
    toggleReport,
    totalErrors,
    correctedCount,
    ignoredCount,
    processingTime,
    modelUsed,
    tokens,
    originalText,
    getFinalText,
    getFeedbackStats,
    exportFeedbackData,
    exportFeedbackJsonl,
  } = useAnalysis();

  const stats = getFeedbackStats();
  const finalText = getFinalText();

  // Calculate pattern distribution
  const patternCounts = tokens
    .filter((t) => t.type === "error")
    .reduce((acc, t) => {
      const pattern = t.pattern || "Unknown";
      acc[pattern] = (acc[pattern] || 0) + 1;
      return acc;
    }, {});

  // Format model name
  const getModelDisplayName = () => {
    if (!modelUsed) return "Unknown";
    if (modelUsed.includes("akura") || modelUsed.includes("llama")) {
      return "Akura LLaMA 8B (Fine-tuned)";
    }
    if (modelUsed.includes("gemini")) return "Gemini";
    return modelUsed;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-800">
                Analysis Report
              </h2>
              <p className="text-sm text-slate-500">
                Summary of corrections and patterns
              </p>
            </div>
          </div>
          <button
            onClick={toggleReport}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-red-50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-red-600 mb-1">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm font-medium">Errors</span>
              </div>
              <span className="text-2xl font-bold text-red-700">
                {totalErrors}
              </span>
            </div>
            <div className="bg-green-50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-green-600 mb-1">
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-sm font-medium">Corrected</span>
              </div>
              <span className="text-2xl font-bold text-green-700">
                {correctedCount}
              </span>
            </div>
            <div className="bg-slate-50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-slate-600 mb-1">
                <XCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Ignored</span>
              </div>
              <span className="text-2xl font-bold text-slate-700">
                {ignoredCount}
              </span>
            </div>
            <div className="bg-indigo-50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-indigo-600 mb-1">
                <Clock className="w-4 h-4" />
                <span className="text-sm font-medium">Time</span>
              </div>
              <span className="text-2xl font-bold text-indigo-700">
                {processingTime?.toFixed(0)}ms
              </span>
            </div>
          </div>

          {/* Model Info */}
          <div className="bg-purple-50 rounded-xl p-4 flex items-center gap-3">
            <Cpu className="w-5 h-5 text-purple-600" />
            <div>
              <span className="text-sm text-purple-600 font-medium">
                Model Used
              </span>
              <p className="text-purple-800 font-semibold">
                {getModelDisplayName()}
              </p>
            </div>
          </div>

          {/* Pattern Distribution */}
          {Object.keys(patternCounts).length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-700 mb-3">
                Pattern Distribution
              </h3>
              <div className="space-y-2">
                {Object.entries(patternCounts).map(([pattern, count]) => (
                  <div key={pattern} className="flex items-center gap-3">
                    <span className="text-sm text-slate-600 flex-1 truncate">
                      {pattern}
                    </span>
                    <div className="flex-1 bg-slate-100 rounded-full h-2">
                      <div
                        className="bg-indigo-500 rounded-full h-2"
                        style={{
                          width: `${(count / totalErrors) * 100}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium text-slate-700 w-8 text-right">
                      {count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Text Comparison */}
          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-3">
              Text Comparison
            </h3>
            <div className="grid gap-4">
              <div className="bg-red-50 rounded-xl p-4">
                <span className="text-xs font-medium text-red-600 uppercase tracking-wider">
                  Original
                </span>
                <p className="text-slate-800 mt-1 sinhala-text">
                  {originalText}
                </p>
              </div>
              <div className="bg-green-50 rounded-xl p-4">
                <span className="text-xs font-medium text-green-600 uppercase tracking-wider">
                  Corrected
                </span>
                <p className="text-slate-800 mt-1 sinhala-text">{finalText}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-100 flex flex-col sm:flex-row gap-2 sm:justify-end">
          <button
            onClick={exportFeedbackData}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors text-sm font-medium"
          >
            <Download className="w-4 h-4" />
            Export JSON
          </button>
          <button
            onClick={exportFeedbackJsonl}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors text-sm font-medium"
          >
            <FileJson className="w-4 h-4" />
            Export JSONL (Fine-tuning)
          </button>
        </div>
      </div>
    </div>
  );
}

export default ReportModal;
