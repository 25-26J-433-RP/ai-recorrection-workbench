/**
 * Akura AI - Status Bar Component
 *
 * Bottom status bar showing connection status and quick stats
 */

import React from "react";
import { Wifi, WifiOff, Activity, Cpu } from "lucide-react";
import { useAnalysis } from "../context/AnalysisContext";

function StatusBar() {
  const { apiStatus, isDemoMode, modelUsed, totalErrors, correctedCount } =
    useAnalysis();

  // Format model name for display
  const getModelDisplayName = () => {
    if (!modelUsed) return null;
    if (modelUsed.includes("akura") || modelUsed.includes("llama")) {
      return "Akura LLaMA 8B";
    }

    if (modelUsed.includes("gemini")) return "Gemini";
    return modelUsed;
  };

  return (
    <footer className="bg-slate-900 text-slate-300 text-xs py-2 px-4">
      <div className="container mx-auto">
        {/* Mobile: Stack layout */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
          {/* Left - Connection Status */}
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="flex items-center gap-1.5">
              {apiStatus === "online" ? (
                <Wifi className="w-3.5 h-3.5 text-green-400" />
              ) : (
                <WifiOff className="w-3.5 h-3.5 text-amber-400" />
              )}
              <span className={apiStatus === "online" ? "text-green-400" : "text-amber-400"}>
                {apiStatus === "online"
                  ? "Connected"
                  : apiStatus === "offline"
                  ? "Offline"
                  : "Connecting..."}
              </span>
            </div>

            {modelUsed && (
              <div className="flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-purple-400" />
                <span className="text-purple-400">{getModelDisplayName()}</span>
              </div>
            )}
          </div>

          {/* Center - Brand (hidden on mobile) */}
          <div className="hidden md:block text-slate-500">
            Akura AI v1.0 • Intelligent Dyslexia Correction Engine
          </div>

          {/* Right - Quick Stats */}
          <div className="flex items-center gap-3 sm:gap-4">
            {totalErrors > 0 && (
              <div className="flex items-center gap-1.5 text-indigo-400">
                <Activity className="w-3.5 h-3.5" />
                <span>
                  {correctedCount}/{totalErrors} corrected
                </span>
              </div>
            )}
            <span className="text-slate-600">© 2024</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default StatusBar;
