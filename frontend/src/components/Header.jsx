/**
 * Akura AI - Header Component
 *
 * Application header with logo, title, and navigation
 */

import React from "react";
import { Brain, FileText, RefreshCw, Moon, Sun } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";

function Header() {
  const { toggleReport, reset, analysisComplete, isDemoMode, apiStatus } =
    useAnalysis();

  return (
    <header className="bg-white shadow-sm border-b border-slate-200">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-800 sinhala-text">
                Akura AI
              </h1>
              <p className="text-xs text-slate-500">
                Intelligent Dyslexia Correction Engine
              </p>
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center gap-2">
            <div
              className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 ${
                apiStatus === "online"
                  ? "bg-green-100 text-green-700"
                  : apiStatus === "offline"
                  ? "bg-amber-100 text-amber-700"
                  : "bg-slate-100 text-slate-500"
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  apiStatus === "online"
                    ? "bg-green-500 animate-pulse"
                    : apiStatus === "offline"
                    ? "bg-amber-500"
                    : "bg-slate-400"
                }`}
              />
              {apiStatus === "online"
                ? "AI Online"
                : apiStatus === "offline"
                ? "Demo Mode"
                : "Connecting..."}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {/* Report Button */}
            {analysisComplete && (
              <button
                onClick={toggleReport}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors"
              >
                <FileText className="w-4 h-4" />
                <span className="text-sm font-medium">View Report</span>
              </button>
            )}

            {/* Reset Button */}
            <button
              onClick={reset}
              className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
              title="Start over"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm">Reset</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
