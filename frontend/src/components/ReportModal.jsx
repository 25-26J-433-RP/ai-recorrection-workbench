/**
 * Akura AI - Report Modal Component
 *
 * Clean, minimal insights dashboard
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
  const correctionRate = totalErrors > 0 ? Math.round((correctedCount / totalErrors) * 100) : 0;

  const handleExport = () => {
    const report = `
AKURA AI - Analysis Report
===========================
Date: ${new Date().toLocaleString()}
Model: ${modelUsed}
Processing Time: ${processingTime?.toFixed(0)}ms

ORIGINAL TEXT:
${originalText}

CORRECTED TEXT:
${getFinalText()}

STATISTICS:
- Total Errors: ${totalErrors}
- Corrected: ${correctedCount}
- Ignored: ${ignoredCount}
- Pending: ${pendingCount}

PATTERN DISTRIBUTION:
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
          <div className="flex items-center gap-3">
            <BarChart3 className="w-5 h-5 text-neutral-600" />
            <h2 className="text-base font-semibold text-neutral-900">Analysis Report</h2>
          </div>
          <button
            onClick={toggleReport}
            className="p-1.5 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* Stats */}
          <div className="grid grid-cols-4 gap-3">
            <div className="p-3 bg-red-50 rounded-lg text-center">
              <AlertCircle className="w-5 h-5 text-red-500 mx-auto mb-1" />
              <p className="text-lg font-semibold text-red-700">{totalErrors}</p>
              <p className="text-xs text-red-600">Errors</p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg text-center">
              <CheckCircle2 className="w-5 h-5 text-green-500 mx-auto mb-1" />
              <p className="text-lg font-semibold text-green-700">{correctedCount}</p>
              <p className="text-xs text-green-600">Corrected</p>
            </div>
            <div className="p-3 bg-neutral-50 rounded-lg text-center">
              <XCircle className="w-5 h-5 text-neutral-400 mx-auto mb-1" />
              <p className="text-lg font-semibold text-neutral-600">{ignoredCount}</p>
              <p className="text-xs text-neutral-500">Ignored</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg text-center">
              <BarChart3 className="w-5 h-5 text-blue-500 mx-auto mb-1" />
              <p className="text-lg font-semibold text-blue-700">{correctionRate}%</p>
              <p className="text-xs text-blue-600">Rate</p>
            </div>
          </div>

          {/* Pattern Distribution */}
          <div>
            <h3 className="text-sm font-medium text-neutral-700 mb-3">Pattern Distribution</h3>
            <div className="space-y-2">
              {patternPercentages.map(({ pattern, count, percentage }) => (
                <div key={pattern}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-neutral-600">{pattern}</span>
                    <span className="text-neutral-400">{count} ({percentage}%)</span>
                  </div>
                  <div className="h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-neutral-400 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Error Table */}
          <div>
            <h3 className="text-sm font-medium text-neutral-700 mb-3">Error Details</h3>
            <div className="border border-neutral-200 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-neutral-50">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium text-neutral-500">Original</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-neutral-500">Correction</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-neutral-500">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100">
                  {errorTokens.slice(0, 10).map((token) => (
                    <tr key={token.id}>
                      <td className="px-3 py-2 text-red-600 sinhala-text">{token.originalWord}</td>
                      <td className="px-3 py-2 text-green-600 sinhala-text">{token.correctedWord}</td>
                      <td className="px-3 py-2">
                        <span
                          className={`px-2 py-0.5 rounded text-xs ${
                            token.state === "corrected"
                              ? "bg-green-100 text-green-700"
                              : token.state === "ignored"
                              ? "bg-neutral-100 text-neutral-500"
                              : "bg-amber-100 text-amber-700"
                          }`}
                        >
                          {token.state}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Text Comparison */}
          <div>
            <h3 className="text-sm font-medium text-neutral-700 mb-3">Text Comparison</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-red-50 rounded-lg">
                <p className="text-xs text-red-600 font-medium mb-1">Original</p>
                <p className="text-sm text-red-800 sinhala-text">{originalText}</p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <p className="text-xs text-green-600 font-medium mb-1">Corrected</p>
                <p className="text-sm text-green-800 sinhala-text">{getFinalText()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-neutral-200 flex items-center justify-between bg-neutral-50">
          <span className="text-xs text-neutral-400">
            {modelUsed} • {processingTime?.toFixed(0)}ms
          </span>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="w-4 h-4" />
              Export
            </Button>
            <Button variant="secondary" size="sm" onClick={exportFeedbackJsonl}>
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
